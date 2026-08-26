"""
Prova di parita' A LIVELLO DI FOTOGRAMMA, non di finestra.

Perche' serve
-------------
`parita.npz` contiene finestre di grandezze GIA' CALCOLATE: verifica che il
modello e lo scaler si trasferiscano fra PC e board, e salta completamente lo
stimatore di posa. La catena reale invece e':

    immagine -> MediaPipe -> geometria -> scaler -> foresta
                └── punto cieco della parità sulle finestre ──┘

La verifica sulle finestre e' passata con scarto ESATTAMENTE ZERO, e le stesse
clip hanno comunque dato risultati diversi sulle due macchine: picco 1,000 con
un allarme sul PC contro 0,560 senza allarme sulla board. Il modello era
identico; a differire erano le grandezze in ingresso.

Questo script chiude quel punto cieco: elabora gli stessi fotogrammi e salva le
dodici grandezze, cosi' che le due macchine possano essere confrontate colonna
per colonna.

Uso
---
Sulla board:
    python3 parita_frame.py --video clip_demo/evt_0067_155044 --out board.npz

Sul PC, sugli stessi fotogrammi:
    python parita_frame.py --video ... --out pc.npz

Poi il confronto:
    python parita_frame.py --confronta pc.npz board.npz
"""

import argparse
import glob
import json
import os
import sys

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)


def estrai(cartella, colonne, k_integrali, fps, limite=None):
    import cv2
    import mediapipe as mp
    from geometry import MotoreGeometrico

    files = sorted(f for f in os.listdir(cartella)
                   if f.lower().endswith(('.jpg', '.png', '.jpeg')))
    if limite:
        files = files[:limite]

    pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1,
                                  min_detection_confidence=0.5,
                                  min_tracking_confidence=0.5)
    motore = MotoreGeometrico(k_integrali=k_integrali)

    V, P, LM = [], [], []
    for nome in files:
        img = cv2.imread(os.path.join(cartella, nome))
        if img is None:
            continue
        h, w = img.shape[:2]
        r = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        lm = r.pose_landmarks.landmark if r.pose_landmarks else None
        wl = r.pose_world_landmarks.landmark if r.pose_world_landmarks else None
        f = motore.fotogramma(lm, wl, w, h, fps)
        V.append([f[c] for c in colonne])
        P.append(int(lm is not None))
        # i primi punti grezzi: servono a distinguere se la differenza nasce
        # nello STIMATORE o nella geometria costruita sopra di esso
        LM.append([[p.x, p.y, p.z] for p in lm[:29]] if lm else
                  [[0.0, 0.0, 0.0]] * 29)

    import mediapipe as _mp
    return (np.asarray(V, np.float64), np.asarray(P, np.int8),
            np.asarray(LM, np.float64), np.asarray(files, dtype=object),
            _mp.__version__, cv2.__version__)


def confronta(a, b):
    A, B = np.load(a, allow_pickle=True), np.load(b, allow_pickle=True)
    dec = lambda v, n=6: f'{v:.{n}f}'.replace('.', ',')

    print('=' * 74)
    print('PARITA A LIVELLO DI FOTOGRAMMA')
    print('=' * 74)
    for et, Z in ((os.path.basename(a), A), (os.path.basename(b), B)):
        print(f"  {et:<22} mediapipe {str(Z['mediapipe'])}   "
              f"opencv {str(Z['opencv'])}   {len(Z['valori'])} fotogrammi")
    print()

    n = min(len(A['valori']), len(B['valori']))
    if len(A['valori']) != len(B['valori']):
        print(f'  ATTENZIONE: numero di fotogrammi diverso, confronto sui primi {n}')

    pa, pb = A['posa'][:n], B['posa'][:n]
    print(f"  pose valide           {int(pa.sum())} contro {int(pb.sum())}   "
          f"concordi su {int((pa == pb).sum())}/{n} fotogrammi")

    la, lb = A['landmark'][:n], B['landmark'][:n]
    m = (pa == 1) & (pb == 1)
    if m.any():
        d = np.abs(la[m] - lb[m])
        print(f"  landmark grezzi       scarto medio {dec(d.mean())}   "
              f"massimo {dec(d.max())}")
    print()

    col = list(A['colonne'])
    va, vb = A['valori'][:n], B['valori'][:n]
    print(f"{'grandezza':<24}{'scarto medio':>14}{'massimo':>12}"
          f"{'relativo':>12}")
    print('-' * 74)
    peggiore = 0.0
    for i, c in enumerate(col):
        d = np.abs(va[:, i] - vb[:, i])
        scala = max(np.abs(va[:, i]).mean(), 1e-9)
        rel = d.mean() / scala
        peggiore = max(peggiore, rel)
        print(f'{c:<24}{dec(d.mean(), 4):>14}{dec(d.max(), 4):>12}'
              f'{dec(100 * rel, 1) + "%":>12}')
    print('-' * 74)
    print(f'  scarto relativo peggiore: {dec(100 * peggiore, 1)}%')
    print()
    if peggiore < 0.01:
        print('  Le due macchine producono le stesse grandezze.')
    else:
        print('  Le grandezze DIFFERISCONO. Il confronto sui landmark grezzi')
        print('  qui sopra dice se la causa e lo stimatore di posa o la')
        print('  geometria costruita su di esso.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--video', default=None)
    ap.add_argument('--out', default='parita_frame.npz')
    ap.add_argument('--limite', type=int, default=60)
    ap.add_argument('--confronta', nargs=2, default=None,
                    metavar=('A.npz', 'B.npz'))
    a = ap.parse_args()

    if a.confronta:
        confronta(*a.confronta)
        return

    if not a.video:
        sys.exit('serve --video oppure --confronta')

    meta = json.load(open(os.path.join(QUI, 'metadata.json'), encoding='utf-8'))
    V, P, LM, files, mpv, cvv = estrai(
        a.video, meta['colonne'], meta['k_integrali'], meta['fps_assunti'],
        a.limite)
    np.savez_compressed(a.out, valori=V, posa=P, landmark=LM, nomi=files,
                        colonne=np.array(meta['colonne'], dtype=object),
                        mediapipe=mpv, opencv=cvv)
    print(f'{len(V)} fotogrammi, {int(P.sum())} con posa  ->  {a.out}')
    print(f'mediapipe {mpv}   opencv {cvv}')


if __name__ == '__main__':
    main()
