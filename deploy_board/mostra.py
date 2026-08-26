"""
Visualizzazione per la discussione: scheletro, punteggio, allarme.

Mostra cio' che il sistema vede davvero -- lo scheletro e le dodici grandezze
che ne derivano -- invece dell'immagine. Non e' soltanto una precauzione sulla
riservatezza: e' la dimostrazione visiva del paradigma privacy-by-design, perche'
rende evidente che dal fotogramma il sistema ricava trentatre punti e poi butta
via i pixel.

    python3 mostra.py --video clip/evt_xxx           riproduce una clip
    python3 mostra.py                                dalla telecamera
    python3 mostra.py --video clip/evt_xxx --salva out.mp4

Cosa appare a schermo
---------------------
A sinistra lo scheletro su fondo scuro, a destra il punteggio nel tempo con la
soglia e le due condizioni della regola di decisione. Quando l'allarme scatta,
la banda rossa.

Il grafico del punteggio mostra anche la RAFFICA in corso, cioe' da quante
finestre consecutive il punteggio sta sopra soglia: e' la grandezza che
distingue un allarme da una finestra sopra soglia, e senza mostrarla la
differenza fra 1.636 e 34 all'ora resta invisibile.
"""

import argparse
import json
import os
import sys
import time
from collections import deque

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

# Coppie di landmark che formano lo scheletro disegnato. Sono le connessioni
# anatomiche fra i punti che le grandezze usano davvero, piu' quelle che
# rendono la figura leggibile.
OSSA = [(11, 12), (11, 23), (12, 24), (23, 24),
        (11, 13), (13, 15), (12, 14), (14, 16),
        (23, 25), (25, 27), (24, 26), (26, 28),
        (0, 11), (0, 12)]
# I nove punti da cui derivano le dodici grandezze: si disegnano piu' grandi.
USATI = {0, 11, 12, 23, 24, 25, 26, 27, 28}


def carica():
    import joblib
    meta = json.load(open(os.path.join(QUI, 'metadata.json'), encoding='utf-8'))
    return (meta, joblib.load(os.path.join(QUI, 'modello.pkl')),
            joblib.load(os.path.join(QUI, 'scaler.pkl')))


def normalizza(X, blob):
    Z = np.asarray(X, dtype=np.float64).copy()
    m = np.asarray(blob['maschera_log1p'], dtype=bool)
    if m.any():
        c = np.where(m)[0]
        Z[..., c] = np.sign(Z[..., c]) * np.log1p(np.abs(Z[..., c]))
    f = Z.shape
    return blob['scaler'].transform(Z.reshape(-1, f[-1])).reshape(f)


def riassumi(X):
    return np.concatenate([X.mean(1), X.std(1), X.min(1), X.max(1),
                           X[:, 0, :], X[:, -1, :]], axis=1)


def disegna(cv2, tela, lm, w, h, colore):
    if lm is None:
        return
    pt = [(int(p.x * w), int(p.y * h)) for p in lm]
    for a, b in OSSA:
        if a < len(pt) and b < len(pt):
            cv2.line(tela, pt[a], pt[b], colore, 2, cv2.LINE_AA)
    for i, p in enumerate(pt):
        if i in USATI:
            cv2.circle(tela, p, 5, colore, -1, cv2.LINE_AA)
        elif i > 10:
            cv2.circle(tela, p, 2, (110, 110, 110), -1, cv2.LINE_AA)


def pannello(cv2, storia, soglia, larghezza, altezza, corsa, persistenza):
    """Il punteggio nel tempo, con soglia e raffica in corso."""
    p = np.full((altezza, larghezza, 3), 22, np.uint8)
    y_soglia = int(altezza - soglia * (altezza - 30)) - 10
    cv2.line(p, (0, y_soglia), (larghezza, y_soglia), (90, 90, 200), 1)
    cv2.putText(p, f'soglia {soglia:.2f}', (6, y_soglia - 6),
                cv2.FONT_HERSHEY_SIMPLEX, .42, (120, 120, 220), 1, cv2.LINE_AA)

    if len(storia) > 1:
        n = min(len(storia), larghezza)
        v = list(storia)[-n:]
        passo = larghezza / max(n - 1, 1)
        for i in range(1, n):
            y0 = int(altezza - v[i - 1] * (altezza - 30)) - 10
            y1 = int(altezza - v[i] * (altezza - 30)) - 10
            c = (80, 80, 235) if v[i] >= soglia else (200, 190, 90)
            cv2.line(p, (int((i - 1) * passo), y0), (int(i * passo), y1),
                     c, 2, cv2.LINE_AA)

    # la raffica in corso: quante finestre consecutive sopra soglia
    for k in range(persistenza):
        x = larghezza - 18 * (persistenza - k) - 8
        acceso = k < corsa
        cv2.rectangle(p, (x, 8), (x + 13, 21),
                      (80, 80, 235) if acceso else (60, 60, 60),
                      -1 if acceso else 1)
    cv2.putText(p, f'raffica {corsa}/{persistenza}',
                (larghezza - 18 * persistenza - 118, 20),
                cv2.FONT_HERSHEY_SIMPLEX, .42, (170, 170, 170), 1, cv2.LINE_AA)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--video', default=None)
    ap.add_argument('--camera', type=int, default=0)
    ap.add_argument('--salva', default=None, help='scrive un mp4')
    ap.add_argument('--fps-riproduzione', type=float, default=8.0)
    a = ap.parse_args()

    import cv2
    import mediapipe as mp
    from geometry import MotoreGeometrico

    meta, modello, blob = carica()
    colonne = meta['colonne']
    L, passo, soglia = (meta['lunghezza_finestra'], meta['passo_finestra'],
                        meta['soglia'])
    reg = meta['regola_decisione']
    persistenza, sospensione = reg['persistenza_finestre'], reg['sospensione_s']

    pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1,
                                  min_detection_confidence=0.5,
                                  min_tracking_confidence=0.5)
    motore = MotoreGeometrico(k_integrali=meta['k_integrali'])
    buf, storia = deque(maxlen=L), deque(maxlen=460)

    if a.video:
        files = sorted(f for f in os.listdir(a.video)
                       if f.lower().endswith(('.jpg', '.png', '.jpeg')))
        sorgente, cap = iter(files), None
    else:
        cap = cv2.VideoCapture(a.camera)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        sorgente = None

    W, H = 640, 480
    H_PAN = 190
    scrittore = None
    if a.salva:
        scrittore = cv2.VideoWriter(
            a.salva, cv2.VideoWriter_fourcc(*'mp4v'), a.fps_riproduzione,
            (W, H + H_PAN))

    t0 = time.time()
    n_frame = corsa = n_allarmi = 0
    ultimo_allarme = -1e18
    p_corr = 0.0
    lampeggio = 0

    try:
        while True:
            if cap is not None:
                ok, frame = cap.read()
                if not ok:
                    break
            else:
                try:
                    frame = cv2.imread(os.path.join(a.video, next(sorgente)))
                except StopIteration:
                    break
                if frame is None:
                    continue
            n_frame += 1
            t = time.time() - t0
            frame = cv2.resize(frame, (W, H))
            h, w = frame.shape[:2]

            r = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            lm = r.pose_landmarks.landmark if r.pose_landmarks else None
            wl = r.pose_world_landmarks.landmark if r.pose_world_landmarks else None

            f = motore.fotogramma(lm, wl, w, h, meta['fps_assunti'])
            buf.append([f[c] for c in colonne])

            if len(buf) == L and n_frame % passo == 0:
                X = np.asarray(buf, np.float32)[None]
                p_corr = float(modello.predict_proba(
                    riassumi(normalizza(X, blob)))[0, 1])
                storia.append(p_corr)
                sopra = p_corr >= soglia
                corsa = corsa + 1 if sopra else 0
                if corsa >= persistenza and (t - ultimo_allarme) >= sospensione:
                    ultimo_allarme = t
                    n_allarmi += 1
                    lampeggio = 18

            # --- lo scheletro, non l'immagine ---
            tela = np.full((H, W, 3), 26, np.uint8)
            colore = ((70, 70, 240) if p_corr >= soglia
                      else (200, 200, 200) if lm else (90, 90, 90))
            disegna(cv2, tela, lm, w, h, colore)
            if lm is None:
                cv2.putText(tela, 'posa non rilevata', (18, H - 22),
                            cv2.FONT_HERSHEY_SIMPLEX, .6, (110, 110, 110), 1,
                            cv2.LINE_AA)
            cv2.putText(tela, f'{p_corr:.3f}', (18, 44),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, colore, 2, cv2.LINE_AA)
            cv2.putText(tela, f'allarmi {n_allarmi}', (18, 74),
                        cv2.FONT_HERSHEY_SIMPLEX, .55, (170, 170, 170), 1,
                        cv2.LINE_AA)
            if lampeggio > 0:
                lampeggio -= 1
                cv2.rectangle(tela, (0, 0), (W - 1, H - 1), (60, 60, 250), 6)
                cv2.putText(tela, 'CADUTA RILEVATA', (W // 2 - 165, H // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (70, 70, 250), 3,
                            cv2.LINE_AA)

            fuori = np.vstack([tela, pannello(cv2, storia, soglia, W, H_PAN,
                                              corsa, persistenza)])
            if scrittore is not None:
                scrittore.write(fuori)
            else:
                cv2.imshow('rilevamento cadute — cio che il sistema vede', fuori)
                if cv2.waitKey(int(1000 / a.fps_riproduzione)) & 0xFF == 27:
                    break
    except KeyboardInterrupt:
        pass
    finally:
        if cap is not None:
            cap.release()
        if scrittore is not None:
            scrittore.release()
            print(f'salvato: {a.salva}')
        cv2.destroyAllWindows()

    print(f'fotogrammi {n_frame}   allarmi {n_allarmi}')


if __name__ == '__main__':
    main()
