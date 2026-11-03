# -*- coding: utf-8 -*-
"""
La prima caduta reale della sessione, con la persona sostituita dal solo
scheletro.

Perche' esiste
--------------
`figura_caduta_board.py` mostra il fotogramma con la faccia pixelata: la
persona resta riconoscibile dal corpo. Questa versione toglie la persona
(riempiendo la sua area con lo sfondo, cv2.inpaint) e disegna al suo posto i
33 landmark di MediaPipe Pose collegati, senza volto (indici 0-10 esclusi).
Stanza, fascia del punteggio e riquadro di raffica restano identici.

Uso
---
    python pipeline/figura_caduta_scheletro.py
"""
import os
import sys

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Rectangle

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)

SORGENTE = os.path.join(RADICE, 'deploy_board', 'sessioni', '20260909_v5',
                        'clip', 'f00856.0.jpg')
MODELLO = os.path.join(RADICE, '..', 'DIP_PROJECT', 'src', 'pose_landmarker_lite.task')
USCITA = os.path.join(RADICE, 'tesi', 'figure', 'fig_caduta_scheletro.png')

INK = '#1C2430'
ROSSO = '#9B1B30'
TEAL = '#2E7D8C'

# connessioni standard MediaPipe Pose, solo corpo (11-32)
CONNESSIONI = [(11, 12), (11, 13), (13, 15), (12, 14), (14, 16), (11, 23),
               (12, 24), (23, 24), (23, 25), (25, 27), (24, 26), (26, 28),
               (27, 29), (29, 31), (28, 30), (30, 32), (15, 17), (15, 19),
               (15, 21), (16, 18), (16, 20), (16, 22), (27, 31), (28, 32)]


def landmark_in_pixel(immagine_rgb):
    """Posa del fotogramma, in coordinate pixel. None se non rilevata."""
    import mediapipe as mp
    from mediapipe.tasks import python as mpt
    from mediapipe.tasks.python import vision

    opts = vision.PoseLandmarkerOptions(
        base_options=mpt.BaseOptions(model_asset_path=MODELLO),
        running_mode=vision.RunningMode.IMAGE, num_poses=1)
    h, w = immagine_rgb.shape[:2]
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=immagine_rgb)
    with vision.PoseLandmarker.create_from_options(opts) as det:
        res = det.detect(mp_img)
    if not res.pose_landmarks:
        return None
    return [(p.x * w, p.y * h, p.visibility) for p in res.pose_landmarks[0]]


def main():
    img_bgr = cv2.imread(SORGENTE)
    img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    h, w = img.shape[:2]

    pts = landmark_in_pixel(np.ascontiguousarray(img))
    if pts is None:
        sys.exit('posa non rilevata sul fotogramma')
    visibili = [(x, y) for x, y, v in pts if v >= 0.3]

    # area della persona: involucro dei landmark visibili, allargato
    maschera = np.zeros((h, w), np.uint8)
    hull = cv2.convexHull(np.array(visibili, np.int32))
    cv2.fillConvexPoly(maschera, hull, 255)
    maschera = cv2.dilate(maschera, np.ones((21, 21), np.uint8))
    sfondo = cv2.inpaint(img_bgr, maschera, 5, cv2.INPAINT_NS)
    sfondo = cv2.cvtColor(sfondo, cv2.COLOR_BGR2RGB)

    fig, ax = plt.subplots(figsize=(5.4, 5.6))
    ax.imshow(sfondo)
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.set_xticks([])
    ax.set_yticks([])
    for lato in ax.spines.values():
        lato.set_edgecolor('#8A929B')
        lato.set_linewidth(.8)

    for a, b in CONNESSIONI:
        xa, ya, va = pts[a]
        xb, yb, vb = pts[b]
        if min(va, vb) < 0.3:
            continue
        colore = ROSSO if a in (11, 12, 23, 24) or b in (11, 12, 23, 24) else TEAL
        ax.plot([xa, xb], [ya, yb], color=colore, lw=2.6, solid_capstyle='round')
    for i, (x, y, v) in enumerate(pts):
        if i <= 10 or v < 0.3:
            continue
        ax.scatter([x], [y], s=26, color=INK, zorder=5)

    ax.set_title('Fotogramma reale, prima caduta:\n'
                 'punteggio 0,760, raffica 4/5 (persona sostituita dallo scheletro)',
                 fontsize=9, pad=8, color=INK)
    fig.subplots_adjust(left=.02, right=.98, top=.9, bottom=.02)
    fig.savefig(USCITA, dpi=200, facecolor='white')
    plt.close(fig)
    print('scritta', USCITA, '| landmark visibili', len(visibili), '/ 33')


if __name__ == '__main__':
    main()
