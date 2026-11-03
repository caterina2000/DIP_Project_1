# -*- coding: utf-8 -*-
"""
Le tre rappresentazioni geometriche, una figura per ciascuna, su fotogrammi veri.

Perche' esiste
--------------
Il Capitolo 3 descrive tre costruzioni geometriche --- un'ellisse adattata a
una nuvola di punti, un vettore del tronco nello spazio, un riferimento
centrato sul bacino --- in tre pagine di prosa. Questo script le disegna sui
dati veri, cosi' che il lettore veda che cosa ciascuna guarda e che cosa
ignora.

DUE SCELTE CHE RENDONO LA FIGURA ONESTA

1. Lo scheletro e' disegnato da `mediapipe.solutions.drawing_utils`, cioe'
   dallo stesso codice che lo disegnerebbe in una demo della libreria. La
   prima versione lo ridisegnava a mano, e si vedeva: sembrava
   un'illustrazione invece dell'uscita di uno stimatore.

2. La ripresa e' elaborata IN SEQUENZA. Lo stimatore e' un tracciatore, e la
   sua uscita su un'immagine isolata non e' quella che ottiene seguendo il
   movimento; su un fotogramma singolo la posa sarebbe diversa da quella che
   il sistema vede in esercizio.

Le costruzioni sovrapposte sono sottili di proposito: la figura deve mostrare
la posa stimata, non coprirla.

Ambiente
--------
Serve MediaPipe, quindi `fall_processing`:

    conda activate fall_processing
    python pipeline/figura_rappresentazioni.py

Uscita: tesi/figure/fig_rappr_a1.png, _a2.png, _a3.png, piu' la figura unica
con i tre pannelli affiancati.
"""

import argparse
import os
import sys

import numpy as np

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if QUI not in sys.path:
    sys.path.insert(0, QUI)

import config                                                # noqa: E402
from src.geometry import (MotoreGeometrico, PUNTI_ELLISSE,    # noqa: E402
                          NASO, SPALLA_SX, SPALLA_DX, ANCA_SX, ANCA_DX,
                          GINOCCHIO_SX, GINOCCHIO_DX, CAVIGLIA_SX,
                          CAVIGLIA_DX)
from src.provenienza import provenienza                       # noqa: E402

import matplotlib                                             # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt                               # noqa: E402

INK, GRIGIO, BLU = '#1A1F23', '#8A949B', '#2B5D7D'
TEAL, ROSSO, SABBIA = '#2E8B8B', '#9C3B45', '#C4A55C'
# I punti che ciascuna rappresentazione impiega. Giallo saturo con contorno
# scuro: deve staccarsi dal rosso della maglia, dal grigio del pavimento e dal
# bianco del tratto dello scheletro, e non coincidere con nessuno dei colori
# usati dalle costruzioni geometriche.
GIALLO = '#FFC61A'

# La ripresa e il fotogramma di riferimento, scelti confrontando un candidato
# per ripresa su sei soggetti: qui il soggetto occupa il 55% dell'altezza del
# fotogramma, il corpo e' in diagonale a meta' caduta, e la maglia si stacca
# dal pavimento. Le riprese in cui la persona e' piu' lontana davano
# costruzioni corrette e illeggibili.
RIPRESA = os.path.join('dataset', 'up_fall', 'raw', 'fall', 'Subject_06',
                       'sub06_act04_trial01_cam01')
FOTOGRAMMA = 21

USATI = {
    'A1': list(PUNTI_ELLISSE),
    'A2': [NASO, SPALLA_SX, SPALLA_DX, ANCA_SX, ANCA_DX],
    'A3': [NASO, SPALLA_SX, SPALLA_DX, ANCA_SX, ANCA_DX,
           GINOCCHIO_SX, GINOCCHIO_DX, CAVIGLIA_SX, CAVIGLIA_DX],
}


def dec(v, n=1):
    return ('{:.' + str(n) + 'f}').format(v).replace('.', ',')


def elabora(cartella, limite):
    """La ripresa elaborata in sequenza: immagine, posa, grandezze."""
    import cv2
    import mediapipe as mp

    files = sorted(f for f in os.listdir(cartella)
                   if f.lower().endswith(('.png', '.jpg', '.jpeg')))[:limite]
    if not files:
        sys.exit('nessuna immagine in ' + cartella)

    pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1,
                                  min_detection_confidence=.5,
                                  min_tracking_confidence=.5)
    motore = MotoreGeometrico()

    fuori = []
    for nome in files:
        img = cv2.imread(os.path.join(cartella, nome))
        if img is None:
            continue
        h, w = img.shape[:2]
        r = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        lm = r.pose_landmarks.landmark if r.pose_landmarks else None
        wl = r.pose_world_landmarks.landmark if r.pose_world_landmarks else None
        f = motore.fotogramma(lm, wl, w, h, config.FPS_DATASET)
        fuori.append({
            'nome': nome, 'bgr': img, 'posa': r.pose_landmarks,
            'punti': (np.array([[p.x * w, p.y * h] for p in lm], np.float64)
                      if lm else None),
            'f': f, 'w': w, 'h': h,
        })
    pose.close()
    return fuori


def con_scheletro(d, spessore=2, raggio=3, stile='neutro'):
    """
    Il fotogramma con la posa disegnata da MediaPipe.

    La funzione e' sempre `drawing_utils.draw_landmarks`, quella che la
    libreria usa nei propri esempi. Cambia solo lo stile:

      'nativo'  usa `get_default_pose_landmarks_style()`, cioe' i colori della
                libreria: lato sinistro arancione, destro azzurro. Oltre a
                essere riconoscibile, distingue i due lati --- utile su un
                corpo che cade, dove gli arti si sovrappongono.

      'neutro'  grigio e bianco, scelti qui. Non compete con i colori delle
                costruzioni geometriche sovrapposte.

    Nessuno dei due e' piu' «vero» dell'altro: in entrambi i casi le posizioni
    dei punti sono quelle stimate, ed e' l'unica cosa che la figura afferma.
    """
    import cv2
    import mediapipe as mp

    img = d['bgr'].copy()
    if d['posa'] is not None:
        du = mp.solutions.drawing_utils
        if stile == 'nativo':
            du.draw_landmarks(
                img, d['posa'], mp.solutions.pose.POSE_CONNECTIONS,
                landmark_drawing_spec=(
                    mp.solutions.drawing_styles
                    .get_default_pose_landmarks_style()))
        else:
            du.draw_landmarks(
                img, d['posa'], mp.solutions.pose.POSE_CONNECTIONS,
                landmark_drawing_spec=du.DrawingSpec(
                    color=(200, 200, 200), thickness=spessore,
                    circle_radius=raggio),
                connection_drawing_spec=du.DrawingSpec(
                    color=(240, 240, 240), thickness=spessore))
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def _incastra(centro, semi, limite):
    """Intervallo dentro [0, limite]: se sborda trasla, non tronca."""
    larghezza = min(2 * semi, limite)
    a = max(0.0, min(centro - larghezza / 2, limite - larghezza))
    return a, a + larghezza


def riquadro(P, w, h, margine=.34):
    x0, x1 = float(P[:, 0].min()), float(P[:, 0].max())
    y0, y1 = float(P[:, 1].min()), float(P[:, 1].max())
    lato = max(x1 - x0, y1 - y0) * (1 + margine)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx0, rx1 = _incastra(cx, lato / 2, w)
    ry0, ry1 = _incastra(cy, lato / 2, h)
    return rx0, rx1, ry0, ry1


def evidenzia(ax, P, indici, colore=GIALLO):
    """
    I punti che la rappresentazione impiega.

    Cerchio pieno con anello scuro attorno: pieno perche' si veda anche sopra
    il tratto bianco dello scheletro, anello perche' non si confonda con i
    punti che MediaPipe disegna e che la rappresentazione NON usa.
    """
    for i in indici:
        ax.plot(P[i, 0], P[i, 1], marker='o', ms=9, mfc=colore,
                mec=INK, mew=1.4, zorder=6)


def pannello_a1(ax, d, colore=GIALLO):
    from matplotlib.patches import Ellipse
    P = d['punti']
    pts = P[PUNTI_ELLISSE]
    centro = pts.mean(axis=0)
    val, vec = np.linalg.eigh(np.cov((pts - centro).T))
    ordine = np.argsort(val)[::-1]
    val, vec = val[ordine], vec[:, ordine]
    semi = 1.7 * np.sqrt(np.maximum(val, 0))
    ang = np.degrees(np.arctan2(vec[1, 0], vec[0, 0]))

    ax.add_patch(Ellipse(centro, 2 * semi[0], 2 * semi[1], angle=ang,
                         fc='none', ec=BLU, lw=1.3, zorder=5))
    for i, col in enumerate((BLU, TEAL)):
        dv = vec[:, i] * semi[i]
        ax.plot([centro[0] - dv[0], centro[0] + dv[0]],
                [centro[1] - dv[1], centro[1] + dv[1]],
                color=col, lw=1.3, zorder=5)
    evidenzia(ax, P, USATI['A1'], colore)


def pannello_a2(ax, d, colore=GIALLO):
    from matplotlib.patches import FancyArrowPatch
    P = d['punti']
    msp = (P[SPALLA_SX] + P[SPALLA_DX]) / 2
    man = (P[ANCA_SX] + P[ANCA_DX]) / 2
    ax.add_patch(FancyArrowPatch(man, msp, arrowstyle='-|>',
                                 mutation_scale=13, color=INK, lw=2.1,
                                 zorder=5))
    ax.plot(man[0], man[1], marker='x', ms=9, color=INK, mew=2.0, zorder=6)
    ax.plot([man[0], man[0]],
            [man[1], man[1] - 1.25 * np.linalg.norm(msp - man)],
            color=INK, lw=1.1, ls=':', zorder=5)
    evidenzia(ax, P, USATI['A2'], colore)


def pannello_a3(ax, d, rx0, rx1, colore=GIALLO):
    P = d['punti']
    msp = (P[SPALLA_SX] + P[SPALLA_DX]) / 2
    man = (P[ANCA_SX] + P[ANCA_DX]) / 2
    ax.plot([man[0], msp[0]], [man[1], msp[1]], color=SABBIA, lw=2.2,
            zorder=5)
    ax.plot(man[0], man[1], marker='x', ms=8, color=SABBIA, mew=1.8, zorder=6)
    ax.plot([rx0, rx1], [man[1], man[1]], color=SABBIA, lw=.8, ls=':',
            zorder=4)

    passo = (rx1 - rx0) * .062
    for k, (idx, col) in enumerate(((NASO, INK), (GINOCCHIO_DX, TEAL),
                                    (CAVIGLIA_DX, BLU))):
        y = P[idx, 1]
        qx = rx0 + passo * (k + .8)
        ax.plot([qx, P[idx, 0]], [y, y], color=col, lw=.7, ls='--', alpha=.65,
                zorder=4)
        ax.annotate('', xy=(qx, y), xytext=(qx, man[1]),
                    arrowprops=dict(arrowstyle='<->', color=col, lw=.9))
    evidenzia(ax, P, USATI['A3'], colore)


def disegna(d, dove, spessore=2, raggio=3, stile='neutro'):
    P, w, h = d['punti'], d['w'], d['h']
    rx0, rx1, ry0, ry1 = riquadro(P, w, h)
    sfondo = con_scheletro(d, spessore, raggio, stile)
    # sul lato sinistro dello stile nativo il giallo si confonderebbe con
    # l'arancione: si passa al magenta, che non e' usato da nessuno dei due
    colore_punti = '#E0218A' if stile == 'nativo' else GIALLO

    def prepara(ax):
        ax.imshow(sfondo, zorder=0)
        ax.set_xlim(rx0, rx1)
        ax.set_ylim(ry1, ry0)
        ax.axis('off')

    scritti = []
    for nome, disegnatore in (
            ('a1', lambda ax: pannello_a1(ax, d, colore_punti)),
            ('a2', lambda ax: pannello_a2(ax, d, colore_punti)),
            ('a3', lambda ax: pannello_a3(ax, d, rx0, rx1, colore_punti))):
        fig, ax = plt.subplots(figsize=(3.6, 3.6))
        prepara(ax)
        disegnatore(ax)
        p = os.path.join(dove, 'fig_rappr_%s.png' % nome)
        fig.savefig(p, bbox_inches='tight', pad_inches=.02, dpi=240,
                    facecolor='white')
        plt.close(fig)
        scritti.append(p)

    # la stessa cosa affiancata, per chi preferisce una figura sola
    fig, assi = plt.subplots(1, 3, figsize=(10.2, 3.6))
    fig.subplots_adjust(wspace=.03)
    for ax in assi:
        prepara(ax)
    pannello_a1(assi[0], d, colore_punti)
    pannello_a2(assi[1], d, colore_punti)
    pannello_a3(assi[2], d, rx0, rx1, colore_punti)
    # Questa figura non porta scritte --- solo geometria sul fotogramma ---
    # quindi la variante e' una sola e si cita come le altre, con `_en`.
    p = os.path.join(dove, 'fig_rappresentazioni_en.png')
    fig.savefig(p, bbox_inches='tight', pad_inches=.02, dpi=240,
                facecolor='white')
    plt.close(fig)
    scritti.append(p)
    return scritti


def provini(sequenza, dove, quanti=12):
    """Foglio a contatto: per scegliere il fotogramma guardandolo."""
    validi = [i for i, d in enumerate(sequenza) if d['punti'] is not None]
    if not validi:
        sys.exit('nessun fotogramma con posa valida')
    passo = max(1, len(validi) // quanti)
    scelti = validi[::passo][:quanti]
    righe = (len(scelti) + 3) // 4
    fig, assi = plt.subplots(righe, 4, figsize=(13.0, 3.3 * righe))
    assi = np.atleast_1d(assi).ravel()
    for ax in assi:
        ax.axis('off')
    for ax, i in zip(assi, scelti):
        d = sequenza[i]
        ax.imshow(con_scheletro(d))
        rx0, rx1, ry0, ry1 = riquadro(d['punti'], d['w'], d['h'])
        ax.set_xlim(rx0, rx1)
        ax.set_ylim(ry1, ry0)
        ax.set_title('#{}   tronco {}°'.format(
            i, dec(d['f']['A3_angolo_tronco'])), fontsize=9)
    p = os.path.join(dove, '_provini_rappresentazioni.png')
    fig.savefig(p, bbox_inches='tight', dpi=130, facecolor='white')
    plt.close(fig)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ripresa', default=None)
    ap.add_argument('--limite', type=int, default=45)
    ap.add_argument('--fotogramma', type=int, default=None)
    ap.add_argument('--provini', action='store_true',
                    help='foglio a contatto dei candidati, poi termina')
    ap.add_argument('--dove', default=os.path.join(QUI, 'tesi', 'figure'))
    ap.add_argument('--spessore', type=int, default=2,
                    help='spessore del tratto dello scheletro, in pixel')
    ap.add_argument('--raggio', type=int, default=3,
                    help='raggio dei punti dello scheletro, in pixel')
    ap.add_argument('--stile', choices=('neutro', 'nativo'), default='neutro',
                    help="'nativo' usa i colori di MediaPipe, sinistra "
                         "arancione e destra azzurra; 'neutro' grigio e bianco")
    a = ap.parse_args()

    cartella = a.ripresa
    if cartella is None:
        for radice in (QUI, os.path.join(QUI, '..', 'DIP_PROJECT')):
            c = os.path.abspath(os.path.join(radice, RIPRESA))
            if os.path.isdir(c):
                cartella = c
                break
    if cartella is None or not os.path.isdir(cartella):
        sys.exit('ripresa non trovata: indicarla con --ripresa')

    print('ripresa   ', cartella)
    seq = elabora(cartella, a.limite)
    print('fotogrammi %d, con posa %d'
          % (len(seq), sum(1 for d in seq if d['punti'] is not None)))

    if a.provini:
        print('provini   ', provini(seq, a.dove))
        return

    i = a.fotogramma
    if i is None:
        i = FOTOGRAMMA if a.ripresa is None else 0
    d = seq[i]
    if d['punti'] is None:
        sys.exit('il fotogramma %d non ha posa valida' % i)

    print('scelto     #%d  %s' % (i, d['nome']))
    for k in ('A1_inclinazione', 'A1_allungamento', 'A2_angolo_tronco',
              'A3_angolo_tronco', 'A3_torso_len', 'A3_testa_rel_y',
              'A3_ginocchia_rel_y', 'A3_caviglie_rel_y'):
        print('  %-22s %s' % (k, dec(d['f'][k], 2)))

    for p in disegna(d, a.dove, a.spessore, a.raggio, a.stile):
        print('scritto   ', p)
    print('codice    ', provenienza()['commit_breve'])

if __name__ == '__main__':
    main()
