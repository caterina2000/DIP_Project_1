# -*- coding: utf-8 -*-
"""
Due fotogrammi consecutivi: che cosa passa dall'uno all'altro.

Perche' esiste
--------------
La Sezione "Lo stimatore e' un tracciatore" scrive che la posa al fotogramma
$i$ dipende da quella al fotogramma $i-1$, e lo mette in equazione. Detta
cosi' e' un'affermazione sulla carta. Questa figura la mostra sui dati: due
fotogrammi davvero consecutivi di una caduta, con lo scheletro del primo
sovrapposto in chiaro a quello del secondo e una freccia per ogni punto, dal
dove era al dove e' finito.

E' il disegno che in Samanta e Chanda (arXiv:1608.00199) e' la Figura 1, dove
i nodi di un fotogramma e quelli del precedente stanno sullo stesso schema con
le frecce delle dipendenze. Qui non e' ricopiata --- la loro licenza e'
`arXiv perpetual non-exclusive` e non consente il riuso --- ma rifatta sui
fotogrammi di questo lavoro, il che la rende anche una misura invece che uno
schema.

Quale coppia di fotogrammi
--------------------------
Non scelta a occhio. Si elabora la ripresa con lo stimatore in modalita'
tracciamento, come in estrazione, e si prende la coppia consecutiva in cui lo
spostamento medio dei punti usati e' massimo: durante una caduta e' il momento
in cui il corpo si muove di piu', ed e' li' che la dipendenza dal fotogramma
precedente si vede senza dover ingrandire nulla. Lo spostamento misurato
finisce nella scheda .txt.

Uso:
    python pipeline/figura_tracciatore.py
    python pipeline/figura_tracciatore.py --lingua en
    python pipeline/figura_tracciatore.py --sfondo bianco
"""

import argparse
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import FancyArrowPatch

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, QUI)

import cv2
import mediapipe as mp

# le primitive di disegno stanno gia' in figura_landmark: importarle evita
# che le due figure divergano nello stile e nei colori
from src.geometry import NASO, SPALLA_SX, SPALLA_DX
from pipeline.figura_landmark import (osso, collo, BLU, GRIGIO, VERDE,
                                      PUNTI_A3)

RIPRESA = os.path.join('dataset', 'up_fall', 'raw', 'fall',
                       'Subject_09', 'sub09_act05_trial01_cam01')

TESTI = {
    'it': {'prima': 'fotogramma $i-1$', 'dopo': 'fotogramma $i$',
           'x': '$x$ [pixel]', 'y': '$y$ [pixel]'},
    'en': {'prima': 'frame $i-1$', 'dopo': 'frame $i$',
           'x': '$x$ [pixel]', 'y': '$y$ [pixel]'},
}


def traccia(cartella, tetto=400):
    """La ripresa elaborata come in estrazione: stimatore in modalita'
    tracciamento, un fotogramma dopo l'altro, stato che passa fra l'uno e
    l'altro. Restituisce per ogni fotogramma il nome del file e i 33 punti in
    pixel, oppure None se la posa manca."""
    nomi = sorted(n for n in os.listdir(cartella)
                  if n.lower().endswith(('.png', '.jpg', '.jpeg')))[:tetto]
    fuori = []
    with mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1,
                                min_detection_confidence=0.5,
                                min_tracking_confidence=0.5) as pose:
        for nome in nomi:
            perc = os.path.join(cartella, nome)
            img = cv2.imread(perc)
            if img is None:
                fuori.append((nome, None, None))
                continue
            h, w = img.shape[:2]
            r = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            if not r.pose_landmarks:
                fuori.append((nome, None, None))
                continue
            lm = r.pose_landmarks.landmark
            fuori.append((nome,
                          np.array([[l.x * w, l.y * h] for l in lm], np.float64),
                          np.array([l.visibility for l in lm], np.float64)))
    return fuori


def coppia(seq):
    """La coppia consecutiva con lo spostamento medio maggiore sui punti di
    A3. Entrambi i fotogrammi devono avere la posa: una coppia a cavallo di
    un buco non descrive uno spostamento, descrive un'interruzione."""
    meglio = None
    for i in range(1, len(seq)):
        a, b = seq[i - 1], seq[i]
        if a[1] is None or b[1] is None:
            continue
        d = float(np.mean(np.linalg.norm(b[1][PUNTI_A3] - a[1][PUNTI_A3],
                                         axis=1)))
        if meglio is None or d > meglio[0]:
            meglio = (d, i)
    return meglio


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ripresa', default=RIPRESA)
    ap.add_argument('--lingua', default='it', choices=('it', 'en'))
    ap.add_argument('--sfondo', default='foto', choices=('foto', 'bianco'))
    ap.add_argument('--dove', default=os.path.join(QUI, 'tesi', 'figure'))
    a = ap.parse_args()

    t = TESTI[a.lingua]
    cartella = a.ripresa if os.path.isabs(a.ripresa) \
        else os.path.join(QUI, a.ripresa)
    if not os.path.isdir(cartella):
        sys.exit('ripresa non trovata: ' + cartella)

    seq = traccia(cartella)
    valide = sum(1 for s in seq if s[1] is not None)
    print('%s: %d fotogrammi, %d con posa' % (os.path.basename(cartella),
                                              len(seq), valide))
    scelta = coppia(seq)
    if scelta is None:
        sys.exit('nessuna coppia consecutiva con posa in entrambi')
    spostamento, i = scelta
    print('coppia scelta: %d -> %d, spostamento medio %.1f pixel'
          % (i - 1, i, spostamento))

    nome_a, Pa, va = seq[i - 1]
    nome_b, Pb, vb = seq[i]
    img_a = cv2.imread(os.path.join(cartella, nome_a))
    img_b = cv2.imread(os.path.join(cartella, nome_b))
    h, w = img_b.shape[:2]

    # il riquadro comune: deve contenere entrambe le pose, se no lo
    # spostamento sembrerebbe uscire dall'inquadratura
    T = np.vstack([Pa, Pb])
    mx = 0.16 * (T[:, 0].max() - T[:, 0].min()) + 46
    my = 0.16 * (T[:, 1].max() - T[:, 1].min()) + 40
    x0, x1 = max(T[:, 0].min() - mx, 0), min(T[:, 0].max() + mx, w)
    y0, y1 = max(T[:, 1].min() - my, 0), min(T[:, 1].max() + my, h)

    larghezza = 3.7
    fig, (sx, dx) = plt.subplots(
        1, 2, figsize=(2 * larghezza, larghezza * (y1 - y0) / (x1 - x0) + 0.75))
    fig.patch.set_facecolor('white')
    for ax in (sx, dx):
        ax.set_xlim(x0, x1)
        ax.set_ylim(y1, y0)
        ax.set_aspect('equal')
        ax.tick_params(labelsize=7.5, colors='#5a6b7a', length=3, width=0.8)
        ax.set_xlabel(t['x'], fontsize=8.5, color='#5a6b7a', labelpad=2)
        for s in ax.spines.values():
            s.set_edgecolor('#b9c6d2')
            s.set_linewidth(0.9)
    sx.set_ylabel(t['y'], fontsize=8.5, color='#5a6b7a', labelpad=2)
    dx.tick_params(labelleft=False)

    if a.sfondo == 'foto':
        # nessun velo sopra la fotografia: la si lascia com'e'. Sono le linee
        # a doversi vedere sopra l'immagine, non l'immagine a doversi
        # schiarire --- e ci pensa l'alone bianco dentro `osso`.
        sx.imshow(cv2.cvtColor(img_a, cv2.COLOR_BGR2RGB), extent=(0, w, h, 0),
                  zorder=0, interpolation='lanczos')
        dx.imshow(cv2.cvtColor(img_b, cv2.COLOR_BGR2RGB), extent=(0, w, h, 0),
                  zorder=0, interpolation='lanczos')
    else:
        for ax in (sx, dx):
            ax.set_facecolor('#fbfcfd')

    # sinistra: la posa al fotogramma i-1, quella che il tracciatore ha gia'.
    # `collo` e' l'unico segmento che non venga da POSE_CONNECTIONS: MediaPipe
    # non collega il viso alle spalle, in nessun fotogramma, e senza quel
    # tratto la testa resta staccata dal busto. Vedi la sua docstring.
    for p, q in mp.solutions.pose.POSE_CONNECTIONS:
        osso(sx, Pa, p, q, GRIGIO, 1.0, 1)
    collo(sx, Pa, GRIGIO, 1.0, 1)
    sx.scatter(Pa[:, 0], Pa[:, 1], s=9, c=GRIGIO, zorder=2, linewidths=0.5,
               edgecolors='white')
    for p, q in mp.solutions.pose.POSE_CONNECTIONS:
        if p in PUNTI_A3 and q in PUNTI_A3:
            osso(sx, Pa, p, q, VERDE, 1.5, 3, alpha=0.95)
    collo(sx, Pa, VERDE, 1.5, 3, alpha=0.95)
    sx.scatter(Pa[PUNTI_A3, 0], Pa[PUNTI_A3, 1], s=52, c=VERDE, zorder=5,
               linewidths=0.9, edgecolors='white')
    sx.set_title(t['prima'], fontsize=12, color='#1d2b36', pad=7)

    # destra: la posa al fotogramma i, con quella precedente in trasparenza
    # e una freccia per punto --- e' lo spostamento, non un'ipotesi
    shA = (Pa[SPALLA_SX] + Pa[SPALLA_DX]) / 2.0
    for p, q in mp.solutions.pose.POSE_CONNECTIONS:
        if p in PUNTI_A3 and q in PUNTI_A3:
            dx.plot([Pa[p, 0], Pa[q, 0]], [Pa[p, 1], Pa[q, 1]], color=VERDE,
                    lw=1.3, alpha=0.55, zorder=2, solid_capstyle='round')
    dx.plot([Pa[NASO, 0], shA[0]], [Pa[NASO, 1], shA[1]], color=VERDE,
            lw=1.3, alpha=0.55, zorder=2, solid_capstyle='round')
    dx.scatter(Pa[PUNTI_A3, 0], Pa[PUNTI_A3, 1], s=42, c=VERDE, zorder=3,
               alpha=0.55, linewidths=0)

    for p, q in mp.solutions.pose.POSE_CONNECTIONS:
        osso(dx, Pb, p, q, GRIGIO, 1.0, 4)
    collo(dx, Pb, GRIGIO, 1.0, 4)
    dx.scatter(Pb[:, 0], Pb[:, 1], s=9, c=GRIGIO, zorder=5, linewidths=0.5,
               edgecolors='white')
    for p, q in mp.solutions.pose.POSE_CONNECTIONS:
        if p in PUNTI_A3 and q in PUNTI_A3:
            osso(dx, Pb, p, q, BLU, 1.5, 6, alpha=0.95)
    collo(dx, Pb, BLU, 1.5, 6, alpha=0.95)

    # frecce nere e sottili: sono la cosa da leggere, e il nero e' l'unico
    # colore che si stacca sia dal pavimento sia dalla maglietta
    for j in PUNTI_A3:
        if float(np.linalg.norm(Pb[j] - Pa[j])) < 1.5:
            continue          # sotto il pixel e mezzo la freccia sarebbe un punto
        dx.add_patch(FancyArrowPatch(
            tuple(Pa[j]), tuple(Pb[j]), color='black', lw=0.9,
            arrowstyle='-|>', mutation_scale=7, zorder=8, shrinkA=2, shrinkB=3,
            path_effects=[pe.withStroke(linewidth=2.4, foreground='white',
                                        alpha=0.9)]))
    dx.scatter(Pb[PUNTI_A3, 0], Pb[PUNTI_A3, 1], s=52, c=BLU, zorder=9,
               linewidths=0.9, edgecolors='white')
    # niente indici qui: questa figura parla della dipendenza temporale, non
    # di quali punti usi una rappresentazione. I numeri stanno nelle figure
    # dei landmark, e qui affollerebbero e basta.
    dx.set_title(t['dopo'], fontsize=12, color='#1d2b36', pad=7)

    fig.tight_layout()
    os.makedirs(a.dove, exist_ok=True)
    coda = '' if a.sfondo == 'foto' else '_bianco'
    suff = '' if a.lingua == 'it' else '_en'
    fuori = os.path.join(a.dove, 'fig_tracciatore%s%s.png' % (coda, suff))
    fig.savefig(fuori, dpi=400, facecolor='white', bbox_inches='tight')
    print('scritto', fuori)

    with open(os.path.splitext(fuori)[0] + '.txt', 'w', encoding='utf-8') as f:
        f.write('due fotogrammi consecutivi, la dipendenza temporale\n\n')
        f.write('ripresa            %s\n' % os.path.basename(cartella))
        f.write('fotogrammi         %d -> %d\n' % (i - 1, i))
        f.write('file               %s\n                   %s\n'
                % (nome_a, nome_b))
        f.write('spostamento medio  %.1f pixel sui 9 punti di A3\n'
                % spostamento)
        d = np.linalg.norm(Pb[PUNTI_A3] - Pa[PUNTI_A3], axis=1)
        f.write('per punto:\n')
        for j, v in zip(PUNTI_A3, d):
            f.write('    %2d  %6.1f px\n' % (j, v))
        f.write('\ncoppia scelta come quella a spostamento massimo fra i\n')
        f.write('primi %d fotogrammi, %d dei quali con posa valida.\n'
                % (len(seq), valide))
        f.write('Stimatore in modalita tracciamento, come in estrazione.\n')


if __name__ == '__main__':
    main()
