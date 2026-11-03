# -*- coding: utf-8 -*-
"""
La pipeline di questo lavoro, dal fotogramma all'allarme.

Perche' esiste
--------------
Il Capitolo 3 descrive sette passaggi in nove pagine. Una figura che li mette
in fila permette di tenere il filo mentre si leggono i dettagli.

L'impaginazione segue quella della Figura 1 di Hoang et al. (IEEE Access 11,
2023): flusso orizzontale, asse del tempo verticale sulle colonne di immagini,
fasi dichiarate in una banda di etichette in basso, architetture disegnate
come piccoli schemi invece che elencate. I contenuti sono pero' quelli di
QUESTO lavoro --- fotogrammi veri di UP-Fall, scheletri prodotti davvero da
MediaPipe su quei fotogrammi, e le scelte adottate nei blocchi a valle.

Le diciture sono in inglese, come la figura di riferimento.

La ripresa
----------
`sub09_act05_trial01_cam01` --- caduta da seduto su sedia vuota, camera 1
(laterale). E' l'unica act05 della camera 1 con posa valida sul 100% dei
fotogrammi: lo scheletro disegnato e' quello vero. Stessa ripresa di
`figura_due_camere.py`.

I tre istanti vengono dalle annotazioni per fotogramma, non scelti a occhio:
la caduta e' annotata dal fotogramma 19 al 71, quindi uno prima, uno dentro e
uno nello stato successivo.

Uso (ambiente fall_processing, l'unico con mediapipe):
    python pipeline/figura_pipeline.py
"""

import argparse
import os
import sys

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import (FancyBboxPatch, FancyArrowPatch, Rectangle,
                                Circle, Arc)

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RIPRESA = os.path.join('dataset', 'up_fall', 'raw', 'fall',
                       'Subject_09', 'sub09_act05_trial01_cam01')
FIGURE = os.path.join(QUI, 'tesi', 'figure')

# dalle annotazioni per fotogramma: caduta annotata 19..71 su 175 fotogrammi
ISTANTI = [8, 45, 120]

BLU = '#27496d'
ETICH = '#3c6e9f'
GRIGIO = '#333333'
VERDE = '#2f7d52'
ARANCIO = '#b9782c'
CREMA = '#fbf0dd'
CHIARO = '#eef3f8'
BORDO = '#9fb6cc'
TRATTO = '#8fa6bd'
NODO = '#5b8db8'


# ----------------------------------------------------------------- posa
def estrai(cartella, indici):
    import mediapipe as mp
    nomi = sorted(os.listdir(cartella))
    pose = mp.solutions.pose.Pose(static_image_mode=False,
                                  model_complexity=1,
                                  min_detection_confidence=0.5)
    voluti, fuori = set(indici), {}
    # si scorre dall'inizio: in modalita' video MediaPipe usa il fotogramma
    # precedente, quindi saltare all'indice darebbe una stima diversa.
    for k in range(max(voluti) + 1):
        img = cv2.imread(os.path.join(cartella, nomi[k]))
        if img is None:
            continue
        r = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if k in voluti:
            fuori[k] = (img, r.pose_landmarks)
    pose.close()
    return fuori


def ritaglia(landmark, w, h, margine=0.18):
    xs = [p.x for p in landmark.landmark]
    ys = [p.y for p in landmark.landmark]
    lato = max(max(xs) - min(xs), max(ys) - min(ys)) * (1 + 2 * margine)
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    return (int(max(0, (cx - lato / 2) * w)), int(min(w, (cx + lato / 2) * w)),
            int(max(0, (cy - lato / 2) * h)), int(min(h, (cy + lato / 2) * h)))


def scheletro(img, landmark):
    import mediapipe as mp
    h, w = img.shape[:2]
    tela = np.full((h, w, 3), 255, np.uint8)
    mp.solutions.drawing_utils.draw_landmarks(
        tela, landmark, mp.solutions.pose.POSE_CONNECTIONS,
        mp.solutions.drawing_utils.DrawingSpec(
            color=(70, 100, 45), thickness=3, circle_radius=4),
        mp.solutions.drawing_utils.DrawingSpec(
            color=(140, 95, 45), thickness=3))
    a, b, c, d = ritaglia(landmark, w, h)
    return tela[c:d, a:b]


# ------------------------------------------------- schemi delle architetture
def sch_ricorrente(ax):
    """Tre celle in fila, stato che scorre, ingresso dal basso."""
    for i, x in enumerate([0.22, 0.50, 0.78]):
        ax.add_patch(FancyBboxPatch((x - 0.09, 0.42), 0.18, 0.24,
                                    boxstyle='round,pad=0.01,rounding_size=0.04',
                                    linewidth=1.0, edgecolor=NODO,
                                    facecolor='white'))
        ax.annotate('', xy=(x, 0.40), xytext=(x, 0.16),
                    arrowprops=dict(arrowstyle='-|>', color=NODO, lw=1.0))
        ax.add_patch(Circle((x, 0.11), 0.045, facecolor=NODO, edgecolor='none'))
        if i < 2:
            ax.annotate('', xy=(x + 0.19, 0.54), xytext=(x + 0.10, 0.54),
                        arrowprops=dict(arrowstyle='-|>', color=NODO, lw=1.0))
    ax.annotate('', xy=(0.96, 0.54), xytext=(0.88, 0.54),
                arrowprops=dict(arrowstyle='-|>', color=NODO, lw=1.0))


def sch_convoluzione(ax):
    """Una sequenza di campioni e un nucleo che scorre."""
    for i in range(8):
        x = 0.07 + i * 0.115
        ax.add_patch(Rectangle((x, 0.12), 0.085, 0.26, linewidth=0.9,
                               edgecolor=NODO, facecolor='white'))
    ax.add_patch(Rectangle((0.295, 0.08), 0.325, 0.34, linewidth=1.5,
                           edgecolor=ARANCIO, facecolor='none'))
    for i, x in enumerate([0.36, 0.475, 0.59]):
        ax.annotate('', xy=(0.475, 0.72), xytext=(x, 0.44),
                    arrowprops=dict(arrowstyle='-', color=ARANCIO, lw=0.9))
    ax.add_patch(Circle((0.475, 0.78), 0.055, facecolor=ARANCIO,
                        edgecolor='none'))


def sch_attenzione(ax):
    """Istanti in fila e archi che collegano elementi distanti."""
    xs = [0.10, 0.28, 0.46, 0.64, 0.82]
    for x in xs:
        ax.add_patch(Rectangle((x - 0.055, 0.10), 0.11, 0.24, linewidth=0.9,
                               edgecolor=NODO, facecolor='white'))
    for a, b, alt in [(0, 4, 0.52), (1, 3, 0.34), (0, 2, 0.30)]:
        cx = (xs[a] + xs[b]) / 2
        ax.add_patch(Arc((cx, 0.34), abs(xs[b] - xs[a]), alt * 2,
                         theta1=0, theta2=180, edgecolor=ARANCIO, lw=1.0))
    ax.annotate('', xy=(0.96, 0.22), xytext=(0.89, 0.22),
                arrowprops=dict(arrowstyle='-|>', color=NODO, lw=1.0))


def sch_grafo(ax):
    """Nodi e archi: lo scheletro e' gia' un grafo."""
    nodi = [(0.50, 0.82), (0.26, 0.58), (0.74, 0.58),
            (0.20, 0.22), (0.50, 0.40), (0.80, 0.22)]
    archi = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 4), (2, 5), (3, 4), (4, 5)]
    for i, j in archi:
        ax.plot([nodi[i][0], nodi[j][0]], [nodi[i][1], nodi[j][1]],
                color=NODO, lw=1.0, zorder=1)
    for x, y in nodi:
        ax.add_patch(Circle((x, y), 0.062, facecolor=NODO, edgecolor='white',
                            linewidth=1.0, zorder=2))


def sch_albero(ax):
    """Un albero di decisione, e la foresta come piu' alberi sovrapposti."""
    for dx, dy, alpha in [(0.10, -0.08, 0.35), (0.05, -0.04, 0.6), (0, 0, 1.0)]:
        nodi = {(0.50, 0.86): [(0.28, 0.54), (0.72, 0.54)],
                (0.28, 0.54): [(0.16, 0.20), (0.40, 0.20)],
                (0.72, 0.54): [(0.60, 0.20), (0.84, 0.20)]}
        for (px, py), figli in nodi.items():
            for fx, fy in figli:
                ax.plot([px + dx, fx + dx], [py + dy, fy + dy],
                        color=VERDE, lw=1.0, alpha=alpha, zorder=1)
        punti = set(nodi) | {p for v in nodi.values() for p in v}
        for x, y in punti:
            ax.add_patch(Circle((x + dx, y + dy), 0.055, facecolor=VERDE,
                                edgecolor='white', linewidth=0.9,
                                alpha=alpha, zorder=2))


def sch_omino(ax):
    """Sagoma con i landmark, l'icona dello stimatore di posa."""
    punti = {'testa': (0.50, 0.90), 'sx_sp': (0.34, 0.70), 'dx_sp': (0.66, 0.70),
             'sx_go': (0.22, 0.50), 'dx_go': (0.78, 0.50),
             'sx_an': (0.40, 0.44), 'dx_an': (0.60, 0.44),
             'sx_gi': (0.36, 0.24), 'dx_gi': (0.64, 0.24),
             'sx_ca': (0.34, 0.06), 'dx_ca': (0.66, 0.06)}
    ossa = [('testa', 'sx_sp'), ('testa', 'dx_sp'), ('sx_sp', 'dx_sp'),
            ('sx_sp', 'sx_go'), ('dx_sp', 'dx_go'),
            ('sx_sp', 'sx_an'), ('dx_sp', 'dx_an'), ('sx_an', 'dx_an'),
            ('sx_an', 'sx_gi'), ('dx_an', 'dx_gi'),
            ('sx_gi', 'sx_ca'), ('dx_gi', 'dx_ca')]
    for a, b in ossa:
        ax.plot([punti[a][0], punti[b][0]], [punti[a][1], punti[b][1]],
                color=ARANCIO, lw=1.6, zorder=1, solid_capstyle='round')
    for x, y in punti.values():
        ax.add_patch(Circle((x, y), 0.052, facecolor=NODO, edgecolor='white',
                            linewidth=1.0, zorder=2))


def torta3d(fig, x, y, w, h, valori, etichette, colori):
    """Torta con effetto di estrusione e linee di richiamo."""
    from matplotlib.patches import Wedge
    ax = fig.add_axes([x, y, w, h])
    ax.set_xlim(-1.75, 1.75); ax.set_ylim(-1.35, 1.25); ax.axis('off')

    def scuro(c, f=0.62):
        c = c.lstrip('#')
        r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
        return '#%02x%02x%02x' % (int(r * f), int(g * f), int(b * f))

    tot = float(sum(valori))
    bordi, a0 = [], 90.0
    for v in valori:
        a1 = a0 - 360.0 * v / tot
        bordi.append((a1, a0))
        a0 = a1
    # lo spessore: la stessa torta ripetuta piu' in basso, in tinta scura
    for dy in np.linspace(-0.34, -0.03, 9):
        for (t1, t2), c in zip(bordi, colori):
            ax.add_patch(Wedge((0, dy), 1.0, t1, t2, facecolor=scuro(c),
                               edgecolor='none', zorder=1))
    for (t1, t2), c in zip(bordi, colori):
        ax.add_patch(Wedge((0, 0), 1.0, t1, t2, facecolor=c,
                           edgecolor='white', linewidth=1.2, zorder=2))
    # linee di richiamo
    for (t1, t2), et, v in zip(bordi, etichette, valori):
        am = np.radians((t1 + t2) / 2)
        xa, ya = np.cos(am), np.sin(am)
        xb, yb = xa * 1.55, ya * 1.55
        ax.plot([xa * 0.92, xb], [ya * 0.92, yb], color=GRIGIO, lw=0.9, zorder=3)
        ax.text(xb + (0.10 if xb >= 0 else -0.10), yb,
                '%s %.0f%%' % (et, 100.0 * v / tot),
                ha='left' if xb >= 0 else 'right', va='center',
                fontsize=9.2, color=GRIGIO, zorder=3)
    return ax


def gomito(fig, punti, colore=VERDE, lw=2.2):
    """Percorso spezzato con la punta sull'ultimo tratto."""
    for i in range(len(punti) - 2):
        fig.add_artist(FancyArrowPatch(punti[i], punti[i + 1],
                                       transform=fig.transFigure,
                                       arrowstyle='-', linewidth=lw,
                                       color=colore))
    fig.add_artist(FancyArrowPatch(punti[-2], punti[-1],
                                   transform=fig.transFigure,
                                   arrowstyle='-|>', mutation_scale=17,
                                   linewidth=lw, color=colore))


def pannello(fig, x, y, w, h, disegno, titolo, colore=GRIGIO, ts=9.5):
    ax = fig.add_axes([x, y, w, h])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    disegno(ax)
    fig.text(x + w / 2, y - 0.024, titolo, ha='center', va='top',
             fontsize=ts, color=colore)
    return ax


# ----------------------------------------------------------------- disegno
def foto(fig, x, y, w, h, immagine):
    ax = fig.add_axes([x, y, w, h])
    ax.imshow(cv2.cvtColor(immagine, cv2.COLOR_BGR2RGB))
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor(BORDO); s.set_linewidth(0.9)
    return ax


def png(fig, x, y, w, h, percorso):
    ax = fig.add_axes([x, y, w, h])
    ax.imshow(mpimg.imread(percorso))
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor(BORDO); s.set_linewidth(0.7)
    return ax


def asse_tempo(fig, x, y0, y1, testo='time'):
    fig.add_artist(FancyArrowPatch((x, y1), (x, y0), transform=fig.transFigure,
                                   arrowstyle='-|>', mutation_scale=12,
                                   linewidth=1.2, color=GRIGIO))
    fig.text(x - 0.013, (y0 + y1) / 2, testo, rotation=90, va='center',
             ha='center', fontsize=10, color=GRIGIO)


def scatola(fig, x, y, w, h, colore=BLU, riempi=CHIARO, tratteggio=False):
    ax = fig.add_axes([x, y, w, h]); ax.axis('off')
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.add_patch(FancyBboxPatch(
        (0.02, 0.02), 0.96, 0.96,
        boxstyle='round,pad=0.01,rounding_size=0.05',
        linewidth=1.2, edgecolor=colore, facecolor=riempi,
        linestyle=(0, (4, 3)) if tratteggio else '-'))
    return ax


def testo_scatola(ax, titolo, righe, colore=BLU, ts=11, tr=9.4):
    if titolo:
        ax.text(0.5, 0.90, titolo, ha='center', va='top',
                fontsize=ts, fontweight='bold', color=colore)
    y, passo = (0.64 if titolo else 0.84), 0.175
    for r in righe:
        ax.text(0.5, y, r, ha='center', va='top', fontsize=tr, color=GRIGIO)
        y -= passo


def fre(fig, x0, y0, x1, y1, colore=VERDE, lw=2.2):
    fig.add_artist(FancyArrowPatch((x0, y0), (x1, y1), transform=fig.transFigure,
                                   arrowstyle='-|>', mutation_scale=17,
                                   linewidth=lw, color=colore))


def banda(fig, x, w, testo):
    fig.add_artist(Rectangle((x, 0.018), w, 0.048, transform=fig.transFigure,
                             facecolor=ETICH, edgecolor='none', zorder=5))
    fig.text(x + w / 2, 0.042, testo, ha='center', va='center',
             fontsize=10.5, color='white', fontweight='bold', zorder=6)


# ----------------------------------------------------------------- figura
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dove', default=FIGURE)
    # Una sola variante, e la scritte sono gia' tutte inglesi: il nome lo
    # dichiara, cosi' in tesi ogni figura si cita con lo stesso suffisso.
    ap.add_argument('--nome', default='fig_pipeline_en.png')
    a = ap.parse_args()

    cartella = os.path.join(QUI, RIPRESA)
    if not os.path.isdir(cartella):
        sys.exit('ripresa non trovata: ' + cartella)
    print('estrazione della posa...')
    dati = estrai(cartella, ISTANTI)
    for k in ISTANTI:
        print('   fotogramma %3d  %s' % (k, 'posa' if dati[k][1] else 'SENZA POSA'))
    if any(dati[k][1] is None for k in ISTANTI):
        sys.exit('un istante e senza posa')

    fig = plt.figure(figsize=(17.4, 8.0))
    fig.patch.set_facecolor('white')

    YF = [0.645, 0.435, 0.225]
    HF = 0.185
    TIT = 11.6

    # ---- 1. input video ----
    X1, W1 = 0.050, 0.112
    fig.text(X1 + W1 / 2, 0.905, 'Input video', ha='center',
             fontsize=TIT, fontweight='bold', color=GRIGIO)
    asse_tempo(fig, X1 - 0.021, YF[2], YF[0] + HF)
    for j, k in enumerate(ISTANTI):
        ax = foto(fig, X1, YF[j], W1, HF, dati[k][0])
        ax.set_ylabel('frame %d' % k, fontsize=9.4, color=GRIGIO, labelpad=4)
        if j < 2:
            fig.text(X1 + W1 / 2, YF[j] - 0.017, '. . .', ha='center',
                     fontsize=11, color=GRIGIO)

    # ---- 2. pose framework ----
    X2, W2 = 0.196, 0.090
    fig.text(X2 + W2 / 2, 0.905, 'Pose framework', ha='center',
             fontsize=TIT, fontweight='bold', color=GRIGIO)
    scatola(fig, X2, 0.330, W2, 0.360, colore=BLU, riempi='white')
    # riquadro interno con il nome e l'icona, come nella figura di riferimento
    scatola(fig, X2 + 0.008, 0.470, W2 - 0.016, 0.205, colore=BORDO,
            riempi=CHIARO)
    fig.text(X2 + W2 / 2, 0.648, 'MediaPipe Pose', ha='center', va='top',
             fontsize=11.2, fontweight='bold', color=BLU)
    axo = fig.add_axes([X2 + 0.026, 0.487, 0.038, 0.130])
    axo.set_xlim(0, 1); axo.set_ylim(0, 1); axo.axis('off')
    sch_omino(axo)
    for i, r in enumerate(['33 landmarks', 'single person',
                           '2D image plane', '3D world landmarks']):
        fig.text(X2 + W2 / 2, 0.442 - i * 0.030, r, ha='center', va='center',
                 fontsize=9.0, color=GRIGIO)
    fre(fig, X1 + W1 + 0.010, 0.510, X2 - 0.010, 0.510)

    # ---- 3. skeleton data ----
    X3, W3 = 0.342, 0.112
    fig.text(X3 + W3 / 2, 0.905, 'Skeleton data', ha='center',
             fontsize=TIT, fontweight='bold', color=GRIGIO)
    asse_tempo(fig, X3 - 0.016, YF[2], YF[0] + HF)
    for j, k in enumerate(ISTANTI):
        ax = foto(fig, X3, YF[j], W3, HF, scheletro(*dati[k]))
        ax.set_ylabel('frame %d' % k, fontsize=9.4, color=GRIGIO, labelpad=4)
        if j < 2:
            fig.text(X3 + W3 / 2, YF[j] - 0.017, '. . .', ha='center',
                     fontsize=11, color=GRIGIO)
    fre(fig, X2 + W2 + 0.010, 0.510, X3 - 0.042, 0.510)

    # ---- 4. data preprocessing (impilato, dal basso verso l'alto) ----
    X4, W4, HB = 0.480, 0.096, 0.150
    fasi = [('Data cleaning', ['missing pose flagged,', 'never interpolated']),
            ('Data normalization', ['mean and variance', 'from training only']),
            ('Sample selection', ['and labeling', r'windows $L=22$, stride 2'])]
    basi = [0.115, 0.300, 0.485]
    for (tit, righe), yb in zip(fasi, basi):
        ax = scatola(fig, X4, yb, W4, HB, colore=ARANCIO, riempi=CREMA)
        testo_scatola(ax, tit, righe, colore=ARANCIO, ts=10.2, tr=8.4)
    for i in range(2):
        fre(fig, X4 + W4 / 2, basi[i] + HB + 0.004,
            X4 + W4 / 2, basi[i + 1] - 0.004, colore=VERDE, lw=2.2)
    # percorso spezzato: scende sotto la colonna degli scheletri, poi rientra
    gomito(fig, [(X3 + W3 / 2, YF[2] - 0.022),
                 (X3 + W3 / 2, 0.150),
                 (X4 - 0.008, 0.150)])

    # ---- 5. data split ----
    fig.text(X4 + W4 / 2, 0.905, 'Data split', ha='center',
             fontsize=TIT, fontweight='bold', color=GRIGIO)
    torta3d(fig, X4 - 0.024, 0.700, 0.145, 0.160,
            [8, 1, 1], ['train', 'val', 'test'],
            ['#7fa9ca', '#cfe0ee', '#27496d'])
    fig.text(X4 + W4 / 2, 0.690, 'LOSO, 10 folds', ha='center', va='top',
             fontsize=9.0, color=GRIGIO, style='italic')
    # dalla selezione dei campioni sale alla suddivisione
    fre(fig, X4 + W4 / 2, basi[2] + HB + 0.004, X4 + W4 / 2, 0.668)

    # ---- 6. feature extraction and recognition ----
    X6, W6 = 0.602, 0.278
    scatola(fig, X6, 0.098, W6, 0.580, colore=TRATTO, riempi='#fafcfe',
            tratteggio=True)
    fig.text(X6 + W6 / 2, 0.905, 'Feature extraction and recognition',
             ha='center', fontsize=TIT, fontweight='bold', color=GRIGIO)

    # 6a. handcrafted features
    ax = scatola(fig, X6 + 0.012, 0.430, W6 - 0.024, 0.235,
                 colore=BLU, riempi=CHIARO, tratteggio=True)
    ax.text(0.5, 0.95, 'Handcrafted feat.s', ha='center', va='top',
            fontsize=10.6, fontweight='bold', color=BLU)
    for i, nome in enumerate(['fig_rappr_a1.png', 'fig_rappr_a2.png',
                              'fig_rappr_a3.png']):
        p = os.path.join(FIGURE, nome)
        if os.path.exists(p):
            png(fig, X6 + 0.024 + i * 0.055, 0.512, 0.049, 0.100, p)
            fig.text(X6 + 0.0485 + i * 0.055, 0.498, ['A1', 'A2', 'A3'][i],
                     ha='center', va='top', fontsize=9.4, color=GRIGIO)
    fig.text(X6 + 0.216, 0.598, 'integral feat.s', ha='center',
             fontsize=9.6, color=GRIGIO, fontweight='bold')
    fig.text(X6 + 0.216, 0.573, 'excursion\npath, descent', ha='center',
             va='top', fontsize=9.0, color=GRIGIO)
    fig.text(X6 + W6 / 2, 0.462,
             r'33 candidates $\rightarrow$ DTW selection $\rightarrow$ 12 adopted',
             ha='center', va='center', fontsize=9.6, color=BLU)

    # 6b. recognition: gli schemi delle architetture
    ax = scatola(fig, X6 + 0.012, 0.118, W6 - 0.024, 0.292,
                 colore=BLU, riempi=CHIARO, tratteggio=True)
    ax.text(0.5, 0.96, 'Recognition', ha='center', va='top',
            fontsize=10.6, fontweight='bold', color=BLU)

    yS, hS, wS = 0.283, 0.076, 0.052
    pannello(fig, X6 + 0.026, yS, wS, hS, sch_ricorrente, 'GRU / LSTM')
    pannello(fig, X6 + 0.086, yS, wS, hS, sch_convoluzione, '1D CNN')
    pannello(fig, X6 + 0.146, yS, wS, hS, sch_attenzione, 'Transformer')
    pannello(fig, X6 + 0.206, yS, wS, hS, sch_grafo, 'GNN')

    axa = fig.add_axes([X6 + 0.026, 0.138, 0.050, 0.070])
    axa.set_xlim(0, 1); axa.set_ylim(0, 1); axa.axis('off')
    sch_albero(axa)
    fig.text(X6 + 0.086, 0.192, 'Random Forest', ha='left', va='center',
             fontsize=10.2, color=VERDE, fontweight='bold')
    fig.text(X6 + 0.086, 0.168, 'deployed on device', ha='left', va='center',
             fontsize=9.4, color=VERDE)
    fig.text(X6 + 0.086, 0.144, 'same representation, same folds, same threshold',
             ha='left', va='center', fontsize=8.6, color=GRIGIO, style='italic')

    # dalla selezione dei campioni al riquadro delle feature
    fre(fig, X4 + W4 + 0.006, 0.554, X6 - 0.004, 0.554)
    # dalle feature progettate al riconoscimento
    fre(fig, X6 + W6 / 2, 0.426, X6 + W6 / 2, 0.414)

    # ---- 7. evaluation e output ----
    X7, W7 = 0.898, 0.086
    ax = scatola(fig, X7, 0.455, W7, 0.200, colore=BLU)
    testo_scatola(ax, 'Metrics', [r'$F_2$-score', 'recall', 'precision'],
                  ts=11, tr=9.4)

    # esito: tre riquadri collegati
    scatola(fig, X7, 0.290, W7, 0.070, colore=VERDE, riempi='#eef7f1')
    fig.text(X7 + W7 / 2, 0.325, 'Fall / Not-fall', ha='center', va='center',
             fontsize=10.2, color=VERDE, fontweight='bold')
    scatola(fig, X7, 0.185, W7, 0.070, colore=VERDE, riempi='#eef7f1')
    fig.text(X7 + W7 / 2, 0.220, 'five consecutive\nwindows', ha='center',
             va='center', fontsize=9.0, color=GRIGIO)
    scatola(fig, X7, 0.080, W7, 0.070, colore=VERDE, riempi='#d9efe1')
    fig.text(X7 + W7 / 2, 0.115, 'Alarm', ha='center', va='center',
             fontsize=11, color=VERDE, fontweight='bold')
    fre(fig, X7 + W7 / 2, 0.286, X7 + W7 / 2, 0.259)
    fre(fig, X7 + W7 / 2, 0.181, X7 + W7 / 2, 0.154)

    fre(fig, X6 + W6 + 0.005, 0.325, X7 - 0.005, 0.325)

    # il ramo della valutazione parte dalla suddivisione e arriva alle metriche,
    # passando a destra della torta per non attraversarla
    yv = 0.845
    xv = X4 + 0.148
    gomito(fig, [(X4 + 0.118, 0.782), (xv, 0.782), (xv, yv),
                 (X7 + W7 / 2, yv), (X7 + W7 / 2, 0.661)],
           colore=GRIGIO, lw=1.6)
    fig.text((xv + X7 + W7 / 2) / 2, yv + 0.019, 'Evaluation', ha='center',
             fontsize=10.8, color=GRIGIO, style='italic')

    # ---- bande delle fasi ----
    banda(fig, 0.028, 0.152, 'Input')
    banda(fig, 0.192, 0.250, 'Keypoint extraction')
    banda(fig, 0.456, 0.112, 'Data preprocessing')
    banda(fig, 0.600, 0.282, 'Feature extraction and recognition')
    banda(fig, 0.892, 0.100, 'Output')

    os.makedirs(a.dove, exist_ok=True)
    fuori = os.path.join(a.dove, a.nome)
    fig.savefig(fuori, dpi=200, facecolor='white')
    print('scritto', fuori)


if __name__ == '__main__':
    main()
