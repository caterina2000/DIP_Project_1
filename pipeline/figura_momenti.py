# -*- coding: utf-8 -*-
"""
La stessa rappresentazione in due momenti: in piedi e a terra.

Perche' esiste
--------------
Le figure dei landmark dicono QUALI punti usa ciascuna rappresentazione. Non
dicono a che serva: su una persona ferma e in piedi l'ellisse di A1 e' un
ovale verticale, e uno non vede perche' quel numero dovrebbe distinguere una
caduta. Queste figure mostrano la stessa costruzione in due istanti della
stessa ripresa --- prima e dopo --- dove la grandezza cambia.

E' quello che A1, A2 e A3 misurano davvero: non la posa, ma il suo cambiare.

Quali due istanti
-----------------
Dalla stessa ripresa di caduta, stessa telecamera, scelti dal programma: il
fotogramma in cui l'ingombro della persona e' piu' verticale, e quello in cui
e' piu' orizzontale. Non "uno all'inizio e uno alla fine": una caduta puo'
avere una coda in cui la persona si muove ancora, e il fotogramma finale non
e' detto sia il piu' disteso. I valori calcolati nei due istanti finiscono
nella scheda .txt, cosi' la didascalia puo' citarli.

Uso:
    python pipeline/figura_momenti.py
    python pipeline/figura_momenti.py --lingua en
    python pipeline/figura_momenti.py --solo a1 --sfondo bianco
"""

import argparse
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, QUI)

import cv2
import mediapipe as mp

from pipeline.figura_landmark import (scheletro, ellisse_a1, tronco_a2,
                                      riferimento_a3, stima_pavimento,
                                      BLU, ROSSO, VERDE,
                                      PUNTI_ELLISSE, PUNTI_A2, PUNTI_A3)

FALL = os.path.join('dataset', 'up_fall', 'raw', 'fall', 'Subject_09')
RIPRESA = os.path.join(FALL, 'sub09_act04_trial01_cam01')
ADL = os.path.join('dataset', 'up_fall', 'raw', 'adl', 'Subject_09')
PAVIMENTO = [os.path.join(ADL, 'sub09_act06_trial01_cam01'),
             os.path.join(ADL, 'sub09_act07_trial01_cam01')]

TESTI = {
    'it': {'su': 'in piedi', 'giu': 'a terra',
           'x': '$x$ [pixel]', 'y': '$y$ [pixel]'},
    'en': {'su': 'upright', 'giu': 'on the ground',
           'x': '$x$ [pixel]', 'y': '$y$ [pixel]'},
}


def istanti(cartella, tetto=400):
    """I due fotogrammi: ingombro piu' verticale e piu' orizzontale.

    L'ingombro si misura sui punti che le rappresentazioni usano, non su tutti
    e 33: le dita e i contorni del viso ballano e sposterebbero il rapporto
    senza che il corpo sia cambiato."""
    usati = sorted(set(PUNTI_ELLISSE) | set(PUNTI_A3))
    nomi = sorted(n for n in os.listdir(cartella)
                  if n.lower().endswith(('.png', '.jpg', '.jpeg')))[:tetto]
    su = giu = None
    with mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1,
                                min_detection_confidence=0.5,
                                min_tracking_confidence=0.5) as pose:
        for k, nome in enumerate(nomi):
            perc = os.path.join(cartella, nome)
            img = cv2.imread(perc)
            if img is None:
                continue
            h, w = img.shape[:2]
            r = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            if not r.pose_landmarks:
                continue
            lm = r.pose_landmarks.landmark
            P = np.array([[l.x * w, l.y * h] for l in lm], np.float64)
            vis = np.array([l.visibility for l in lm], np.float64)
            larg = float(P[usati, 0].max() - P[usati, 0].min())
            alt = float(P[usati, 1].max() - P[usati, 1].min())
            if larg <= 1 or alt <= 1:
                continue
            rapporto = alt / larg
            dato = (rapporto, k, nome, img, P, vis)
            if su is None or rapporto > su[0]:
                su = dato
            if giu is None or rapporto < giu[0]:
                giu = dato
    return su, giu


def lato_comune(pose, margine=1.22):
    """Il lato della finestra quadrata, uguale per tutti i pannelli.

    In piedi la persona occupa una striscia alta e stretta, a terra una bassa
    e larga. Con due riquadri diversi i pannelli uscirebbero di forma diversa
    e le due ellissi non sarebbero confrontabili a vista: sembrerebbe che la
    persona cambi dimensione, non orientamento. Una finestra quadrata dello
    stesso lato per entrambi tiene la scala fissa e lascia cambiare solo cio'
    che cambia davvero."""
    lato = 0.0
    for P in pose:
        lato = max(lato, float(P[:, 0].max() - P[:, 0].min()),
                   float(P[:, 1].max() - P[:, 1].min()))
    return lato * margine + 40.0


def riquadro(P, img, lato):
    """La finestra centrata sulla posa, fatta rientrare nell'immagine dove
    l'immagine e' abbastanza grande."""
    h, w = img.shape[:2]
    cx = 0.5 * (float(P[:, 0].min()) + float(P[:, 0].max()))
    cy = 0.5 * (float(P[:, 1].min()) + float(P[:, 1].max()))
    x0, x1 = cx - lato / 2, cx + lato / 2
    y0, y1 = cy - lato / 2, cy + lato / 2
    if lato <= w:
        x0 += max(0.0, -x0) - max(0.0, x1 - w)
        x1 = x0 + lato
    if lato <= h:
        y0 += max(0.0, -y0) - max(0.0, y1 - h)
        y1 = y0 + lato
    return x0, x1, y0, y1


def pannello(ax, nome_r, punti, colore, img, P, vis, retta, sfondo, t,
             lato):
    x0, x1, y0, y1 = riquadro(P, img, lato)
    h, w = img.shape[:2]
    ax.set_xlim(x0, x1)
    ax.set_ylim(y1, y0)
    ax.set_aspect('equal')
    ax.tick_params(labelsize=7.5, colors='#5a6b7a', length=3, width=0.8)
    ax.set_xlabel(t['x'], fontsize=8.5, color='#5a6b7a', labelpad=2)
    for s in ax.spines.values():
        s.set_edgecolor('#b9c6d2')
        s.set_linewidth(0.9)

    if sfondo == 'foto':
        # niente velo: la fotografia resta com'e', a staccare le linee
        # ci pensa l'alone bianco dentro `osso`
        ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), extent=(0, w, h, 0),
                  zorder=0, interpolation='lanczos')
    else:
        ax.set_facecolor('#fbfcfd')

    misure = {}
    if nome_r == 'a1':
        mag, minore, ang = ellisse_a1(ax, P)
        misure = {'A1_asse_mag': mag, 'A1_asse_min': minore,
                  'A1_allungamento': mag / (minore + 1e-6),
                  'A1_inclinazione': ang}
    if nome_r == 'a3':
        h_pav = riferimento_a3(ax, P, retta, x0, x1)
        if h_pav is not None:
            misure['A3_h_pavimento'] = h_pav
    scheletro(ax, P, vis, punti, colore)
    if nome_r == 'a2':
        misure = {'A2_angolo_tronco': tronco_a2(ax, P)}
    return misure


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ripresa', default=RIPRESA)
    ap.add_argument('--pavimento', nargs='*', default=PAVIMENTO)
    ap.add_argument('--lingua', default='it', choices=('it', 'en'))
    ap.add_argument('--sfondo', default='foto', choices=('foto', 'bianco'))
    ap.add_argument('--solo', default=None, choices=('a1', 'a2', 'a3'))
    ap.add_argument('--dove', default=os.path.join(QUI, 'tesi', 'figure'))
    a = ap.parse_args()

    t = TESTI[a.lingua]
    suff = '' if a.lingua == 'it' else '_en'
    coda = '' if a.sfondo == 'foto' else '_bianco'
    cartella = a.ripresa if os.path.isabs(a.ripresa) \
        else os.path.join(QUI, a.ripresa)
    if not os.path.isdir(cartella):
        sys.exit('ripresa non trovata: ' + cartella)

    su, giu = istanti(cartella)
    if su is None or giu is None:
        sys.exit('non trovo due istanti validi in ' + cartella)
    print('ripresa   %s' % os.path.basename(cartella))
    print('in piedi  fotogramma %3d, ingombro alto/largo %.2f' % (su[1], su[0]))
    print('a terra   fotogramma %3d, ingombro alto/largo %.2f' % (giu[1], giu[0]))

    lavoro = [('a1', PUNTI_ELLISSE, BLU), ('a2', PUNTI_A2, ROSSO),
              ('a3', PUNTI_A3, VERDE)]
    if a.solo:
        lavoro = [x for x in lavoro if x[0] == a.solo]

    retta = oss = nfot = None
    if any(x[0] == 'a3' for x in lavoro):
        carte = [c if os.path.isabs(c) else os.path.join(QUI, c)
                 for c in a.pavimento]
        retta, oss, nfot = stima_pavimento(carte)
        if retta is not None:
            print('pavimento y = %.5f x + %.2f su %d osservazioni'
                  % (retta[0], retta[1], oss))

    lato = lato_comune([su[4], giu[4]])
    print('finestra  %.0f x %.0f pixel, uguale per i due pannelli' % (lato, lato))

    tutte = {}
    for nome_r, punti, colore in lavoro:
        # ogni pannello ha il suo riquadro: in piedi e a terra la persona
        # occupa porzioni diverse dell'inquadratura, e un riquadro comune
        # renderebbe minuscolo il primo
        fig, assi = plt.subplots(1, 2, figsize=(9.8, 5.2))
        fig.patch.set_facecolor('white')
        m = {}
        for ax, dato, eti in ((assi[0], su, t['su']), (assi[1], giu, t['giu'])):
            _r, k, _nome, img, P, vis = dato
            m[eti] = pannello(ax, nome_r, punti, colore, img, P, vis, retta,
                              a.sfondo, t, lato)
            ax.set_title(eti, fontsize=12, color='#1d2b36', pad=7)
        assi[0].set_ylabel(t['y'], fontsize=8.5, color='#5a6b7a', labelpad=2)
        fig.tight_layout()
        os.makedirs(a.dove, exist_ok=True)
        fuori = os.path.join(a.dove,
                             'fig_momenti_%s%s%s.png' % (nome_r, coda, suff))
        fig.savefig(fuori, dpi=400, facecolor='white', bbox_inches='tight')
        plt.close(fig)
        print('scritto', fuori)
        tutte[nome_r] = (fuori, m)

    scheda = os.path.join(a.dove, 'fig_momenti%s%s.txt' % (coda, suff))
    with open(scheda, 'w', encoding='utf-8') as f:
        f.write('la stessa rappresentazione in due momenti\n\n')
        f.write('ripresa    %s\n' % os.path.basename(cartella))
        f.write('in piedi   fotogramma %d (alto/largo %.2f)\n' % (su[1], su[0]))
        f.write('a terra    fotogramma %d (alto/largo %.2f)\n\n'
                % (giu[1], giu[0]))
        for nome_r, (fuori, m) in tutte.items():
            f.write('%s  %s\n' % (nome_r.upper(), os.path.basename(fuori)))
            chiavi = sorted({k for d in m.values() for k in d})
            for c in chiavi:
                v = ['%s %.4f' % (eti, m[eti][c]) for eti in m if c in m[eti]]
                f.write('    %-18s %s\n' % (c, '   '.join(v)))
            f.write('\n')
        if retta is not None:
            f.write('pavimento y = %.6f x + %.3f, da '
                    'MotoreGeometrico._pavimento\n'
                    '          su %d osservazioni in %d fotogrammi.\n'
                    % (retta[0], retta[1], oss, nfot))
    print('scheda    %s' % scheda)


if __name__ == '__main__':
    main()
