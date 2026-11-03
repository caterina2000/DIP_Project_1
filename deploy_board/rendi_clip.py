# -*- coding: utf-8 -*-
"""
Rimette in scena una clip salvata con la configurazione installata OGGI.

Perche' esiste
--------------
Le clip di `clip_demo/` sono gli eventi di **agosto**: sono state salvate
attorno agli allarmi di allora, con un modello diverso e una regola diversa, e
da allora nessuno le ha piu' guardate. Sono dati registrati, e contengono
un'informazione che non costa nulla raccogliere: **che cosa direbbe di quegli
stessi istanti il sistema di adesso.**

Ogni clip viene ricalcolata con il pacchetto corrente --- stesso motore
geometrico, stesse tredici colonne, stesso modello, stessa aggregazione --- e
produce:

    <out>/<clip>/*.jpg   i fotogrammi annotati: scheletro sopra l'immagine
                         vera, punteggio, soglia, raffica, banda d'allarme
    <out>/<clip>.csv     una riga per finestra decisa

e in fondo una tabella che confronta le regole di allarme sulle stesse clip.

**La cadenza.** Le clip sono state salvate a 10 fps dal registratore, non alla
velocita' con cui questo script le rilegge: il `dt` passato al motore e' quindi
quello dichiarato (`--fps`, predefinito 10), non un tempo di elaborazione.
Misurarlo dall'orologio darebbe derivate inventate.

Uso:
    python deploy_board/rendi_clip.py clip_demo/*            (dalla cartella)
    python deploy_board/rendi_clip.py clip_demo/evt_0001_132012 --out resa
"""

import argparse
import csv
import os
import sys
from collections import deque

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
if QUI not in sys.path:
    sys.path.insert(0, QUI)

from mostra import disegna, normalizza, pannello, riassumi
from rileva import costruisci_motore

W, H, H_PAN = 640, 480, 170


def carica_pacchetto(dove):
    """
    Il pacchetto da usare, che non e' per forza quello installato.

    Serve perche' la configurazione installata --- DTWH, tredici colonne ---
    **non e' valutabile su una clip corta**: `A3_h_pavimento` richiede
    cinquanta osservazioni di persona eretta, e in diciassette secondi
    attorno a un allarme non ce ne sono. Le clip di agosto si guardano
    quindi con un pacchetto a dodici colonne, che il pavimento non lo
    chiede, e la differenza va dichiarata invece che nascosta.
    """
    import joblib
    import json
    meta = json.load(open(os.path.join(dove, 'metadata.json'),
                          encoding='utf-8'))
    return (meta, joblib.load(os.path.join(dove, 'modello.pkl')),
            joblib.load(os.path.join(dove, 'scaler.pkl')))


def una_clip(cartella, meta, modello, blob, cv2, mp, fps, out,
             salva=True, salva_csv=None):
    """Ricalcola una clip e restituisce (istanti, punteggi, quota_pose)."""
    files = sorted(f for f in os.listdir(cartella)
                   if f.lower().endswith(('.jpg', '.jpeg', '.png')))
    if not files:
        return [], [], 0.0

    colonne = meta['colonne']
    L, passo, soglia = (meta['lunghezza_finestra'], meta['passo_finestra'],
                        meta['soglia'])
    reg = meta['regola_decisione']
    persistenza, sospensione = reg['persistenza_finestre'], reg['sospensione_s']
    serve_pav = 'A3_h_pavimento' in colonne

    # Uno stimatore NUOVO per clip: MediaPipe e' un tracciatore, e riusarlo
    # farebbe dipendere una clip da quella elaborata prima (ISS-138).
    pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1,
                                  min_detection_confidence=0.5,
                                  min_tracking_confidence=0.5)
    motore = costruisci_motore(meta)
    buf, storia = deque(maxlen=L), deque(maxlen=W)

    # Il CSV e le immagini sono due cose diverse: il primo e' testo, pesa
    # nulla, ed e' quello da cui si ricalcola qualunque regola senza rifare
    # niente. `--senza-immagini` saltava anche lui, e buttava via i numeri
    # insieme alle figure.
    if salva_csv is None:
        salva_csv = salva
    dest = os.path.join(out, os.path.basename(os.path.normpath(cartella)))
    if salva:
        os.makedirs(dest, exist_ok=True)
    elif salva_csv:
        os.makedirs(out, exist_ok=True)

    righe = []
    n_pose = corsa = lampeggio = n_allarmi = 0
    ultimo_allarme = -1e18
    p_corr = 0.0

    for i, nome in enumerate(files):
        frame = cv2.imread(os.path.join(cartella, nome))
        if frame is None:
            continue
        frame = cv2.resize(frame, (W, H))
        t = i / fps

        r = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        lm = r.pose_landmarks.landmark if r.pose_landmarks else None
        wl = r.pose_world_landmarks.landmark if r.pose_world_landmarks else None
        n_pose += lm is not None

        f = motore.fotogramma(lm, wl, W, H, fps)
        buf.append([f[c] for c in colonne])

        pav_pronto, pav_oss = motore.pavimento_pronto()
        pav = pav_pronto or not serve_pav
        if len(buf) == L and i % passo == 0 and pav:
            X = np.asarray(buf, np.float32)[None]
            p_corr = float(modello.predict_proba(
                riassumi(normalizza(X, blob)))[0, 1])
            storia.append(p_corr)
            corsa = corsa + 1 if p_corr >= soglia else 0
            allarme = (corsa >= persistenza
                       and (t - ultimo_allarme) >= sospensione)
            if allarme:
                ultimo_allarme = t
                n_allarmi += 1
                lampeggio = 20
            righe.append((t, p_corr, int(p_corr >= soglia), corsa,
                          int(allarme), int(lm is not None), int(pav)))

        if not salva:
            continue

        tela = frame.copy()
        colore = ((70, 70, 240) if p_corr >= soglia
                  else (120, 230, 120) if lm is not None else (90, 90, 90))
        disegna(cv2, tela, lm, W, H, colore)
        cv2.putText(tela, f'{p_corr:.3f}', (16, 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, colore, 2, cv2.LINE_AA)
        cv2.putText(tela, f'{os.path.basename(cartella)}   t={t:5.1f}s',
                    (16, 70), cv2.FONT_HERSHEY_SIMPLEX, .5, (230, 230, 230), 1,
                    cv2.LINE_AA)
        if lm is None:
            cv2.putText(tela, 'posa non rilevata', (16, H - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, .6, (90, 90, 220), 2,
                        cv2.LINE_AA)
        if not pav:
            cv2.putText(tela, f'pavimento non stimato ({pav_oss}/50)',
                        (16, H - 48), cv2.FONT_HERSHEY_SIMPLEX, .55,
                        (60, 190, 240), 2, cv2.LINE_AA)
        if lampeggio > 0:
            lampeggio -= 1
            cv2.rectangle(tela, (0, 0), (W - 1, H - 1), (60, 60, 250), 6)
            cv2.putText(tela, 'CADUTA RILEVATA', (W // 2 - 170, H // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (70, 70, 250), 3,
                        cv2.LINE_AA)
        fuori = np.vstack([tela, pannello(cv2, storia, soglia, W, H_PAN,
                                          corsa, persistenza)])
        cv2.imwrite(os.path.join(dest, nome), fuori,
                    [int(cv2.IMWRITE_JPEG_QUALITY), 80])

    if salva_csv and righe:
        with open(dest + '.csv', 'w', newline='') as fh:
            c = csv.writer(fh)
            c.writerow(['t_s', 'punteggio', 'sopra', 'corsa', 'allarme',
                        'posa', 'pavimento'])
            c.writerows(righe)

    return ([x[0] for x in righe], [x[1] for x in righe],
            n_pose / max(len(files), 1))


def regole(t, p, soglia_reg):
    """Che cosa direbbero regole diverse sugli stessi punteggi."""
    fuori = {}
    for nome, s, K, M in [('installata 0,50 5cons', 0.50, 5, 5),
                          ('0,50 5su7', 0.50, 5, 7),
                          ('0,40 2cons', 0.40, 2, 2),
                          ('0,30 3su5', 0.30, 3, 5)]:
        fin, ult, n = [], -1e18, 0
        for ti, pi in zip(t, p):
            fin.append(pi >= s)
            fin[:] = fin[-M:]
            if sum(fin) >= K and (ti - ult) >= 30.0:
                ult = ti
                n += 1
        fuori[nome] = n
    return fuori


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cartelle', nargs='+')
    ap.add_argument('--out', default=os.path.join(QUI, 'resa_clip'))
    ap.add_argument('--fps', type=float, default=10.0,
                    help='la cadenza con cui la clip fu SALVATA (10 fps dal '
                         'registratore), non quella di rilettura')
    ap.add_argument('--senza-immagini', action='store_true',
                    dest='senza_immagini')
    ap.add_argument('--senza-csv', action='store_true', dest='senza_csv',
                    help='non scrivere nemmeno i punteggi per finestra. '
                         'Da usare solo per una prova al volo: senza il CSV '
                         'la rilettura non e piu rianalizzabile.')
    ap.add_argument('--pacchetto', default=QUI,
                    help='cartella con metadata.json, modello.pkl e '
                         'scaler.pkl. Predefinito: quello installato')
    a = ap.parse_args()

    import cv2
    import mediapipe as mp

    meta, modello, blob = carica_pacchetto(a.pacchetto)
    print('=' * 78)
    print('CLIP RICALCOLATE CON LA CONFIGURAZIONE DI OGGI')
    print('=' * 78)
    print('  pacchetto   %s a %d colonne, compito %s, soglia %.2f'
          % (meta['feature_set'], meta['n_colonne'], meta['compito'],
             meta['soglia']))
    print('  regola      %d finestre consecutive, %d s di sospensione'
          % (meta['regola_decisione']['persistenza_finestre'],
             meta['regola_decisione']['sospensione_s']))
    print('  cadenza     %.0f fps (dichiarata, non misurata sulla rilettura)'
          % a.fps)
    print()
    print('  %-22s %6s %7s %7s %7s   %s'
          % ('clip', 'pose', 'picco', '>=0,50', '>=0,40', 'allarmi per regola'))
    print('  ' + '-' * 76)

    tot = {}
    for c in a.cartelle:
        if not os.path.isdir(c):
            continue
        t, p, quota = una_clip(c, meta, modello, blob, cv2, mp, a.fps, a.out,
                               salva=not a.senza_immagini,
                               salva_csv=not a.senza_csv)
        if not p:
            print('  %-22s  (nessuna finestra decisa)'
                  % os.path.basename(os.path.normpath(c)))
            continue
        rg = regole(t, p, meta['soglia'])
        for k, v in rg.items():
            tot[k] = tot.get(k, 0) + v
        print('  %-22s %5.0f%% %7.3f %7d %7d   %s'
              % (os.path.basename(os.path.normpath(c)), 100 * quota, max(p),
                 sum(1 for x in p if x >= 0.50), sum(1 for x in p if x >= 0.40),
                 '  '.join('%s=%d' % (k.split()[0], v) for k, v in rg.items())))

    if tot:
        print()
        print('  in tutto, per regola:')
        for k, v in tot.items():
            print('    %-24s %d allarmi' % (k, v))
    if not a.senza_immagini:
        print()
        print('  fotogrammi annotati in %s/' % a.out)


if __name__ == '__main__':
    main()
