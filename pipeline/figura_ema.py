# -*- coding: utf-8 -*-
"""
Che cosa farebbe la media mobile esponenziale sui landmark, e a che prezzo.

Il livello a cui si filtra
--------------------------
Questo conta, ed e' facile sbagliarlo. Nel progetto precedente i due parametri
del filtro erano argomenti del COSTRUTTORE del motore geometrico ---
`GeometryEngine(alpha_pos=0.05, alpha_vel=0.10)` --- quindi dovevano agire
dentro il motore, sulle posizioni dei landmark e sulle velocita' che se ne
ricavano. Un terzo parametro per le grandezze gia' calcolate, `EMA_ALPHA_FEAT`,
esisteva ed era commentato.

Filtrare le coordinate non e' come filtrare una grandezza. Le coordinate
entrano in TUTTE le grandezze: liscarle cambia l'angolo del tronco, le altezze
relative, la lunghezza del tronco e, a cascata, le derivate e gli integrali.
Questo script fa percio' la cosa fedele: elabora la ripresa una volta sola con
lo stimatore, poi filtra le COORDINATE e ricalcola le grandezze con lo stesso
motore geometrico usato in produzione, una volta per ciascun $\\alpha$.

ATTENZIONE, e va detto in didascalia: il filtro **non e' stato applicato** ai
dati di questo lavoro. I parametri erano nell'implementazione e il motore non
li usava --- in `DIP_PROJECT/src/geometry.py` compaiono solo nella firma di
`__init__` e nelle due assegnazioni. Quello che si vede qui e' percio' una
ricostruzione a posteriori.

Che cosa misura
---------------
Due condizioni dello stesso archivio:

  persona quasi ferma   la variazione fra fotogrammi consecutivi e' in gran
                        parte oscillazione della stima: si misura quanto il
                        filtro la riduce.

  caduta                la variazione e' movimento vero: si misura di quanto
                        il filtro ne schiaccia e ritarda l'escursione.

Il rapporto fra le due e' il compromesso.

Uso:
    python pipeline/figura_ema.py
    python pipeline/figura_ema.py --grandezza A3_angolo_tronco
"""

import argparse
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, QUI)

import cv2
import mediapipe as mp

from src.geometry import MotoreGeometrico

FPS = 18.0
ADL = os.path.join('dataset', 'up_fall', 'raw', 'adl', 'Subject_04',
                   'sub04_act11_trial01_cam01')
FALL = os.path.join('dataset', 'up_fall', 'raw', 'fall', 'Subject_10',
                    'sub10_act04_trial01_cam01')

BLU = '#1565c0'
ROSSO = '#d81b60'
VERDE = '#00897b'
GRIGIO = '#90a4ae'


class Punto:
    """Il minimo che il motore geometrico si aspetta da un landmark."""
    __slots__ = ('x', 'y', 'z', 'visibility')

    def __init__(self, x, y, z=0.0, visibility=1.0):
        self.x, self.y, self.z, self.visibility = x, y, z, visibility


def leggi(cartella, tetto=320):
    """La ripresa elaborata UNA VOLTA sola con lo stimatore.

    Restituisce, per ogni fotogramma, le coordinate normalizzate dei 33 punti
    oppure None se la posa manca. Filtrare e ricalcolare avviene dopo, cosi'
    che i quattro valori di alpha vedano esattamente la stessa stima di posa e
    la differenza sia tutta del filtro."""
    nomi = sorted(n for n in os.listdir(cartella)
                  if n.lower().endswith(('.png', '.jpg', '.jpeg')))[:tetto]
    fuori, dim = [], None
    with mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1,
                                min_detection_confidence=0.5,
                                min_tracking_confidence=0.5) as pose:
        for nome in nomi:
            img = cv2.imread(os.path.join(cartella, nome))
            if img is None:
                fuori.append(None)
                continue
            dim = img.shape[:2]
            r = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            if not r.pose_landmarks:
                fuori.append(None)
                continue
            lm = r.pose_landmarks.landmark
            fuori.append(np.array([[l.x, l.y, l.z] for l in lm], np.float64))
    return fuori, dim


def grandezza_filtrata(seq, dim, alpha, nome):
    """Filtra le COORDINATE con l'EMA e ricalcola la grandezza col motore.

    Lo stato del filtro si azzera alla perdita della posa, come si azzera
    quello del motore: un filtro ricorsivo che attraversasse un buco
    porterebbe dentro la nuova sequenza un valore vecchio di chissa' quanti
    fotogrammi."""
    h, w = dim
    motore = MotoreGeometrico()
    motore.reset()
    prec = None
    fuori = []
    for P in seq:
        if P is None:
            motore.reset()
            prec = None
            fuori.append(np.nan)
            continue
        Q = P if (alpha >= 1.0 or prec is None) \
            else alpha * P + (1.0 - alpha) * prec
        prec = Q
        punti = [Punto(float(q[0]), float(q[1]), float(q[2])) for q in Q]
        f = motore.fotogramma(punti, None, float(w), float(h), FPS)
        fuori.append(float(f.get(nome, np.nan)))
    return np.asarray(fuori, np.float64)


def tratto_piu_lungo(x):
    """Gli indici del tratto continuo piu' lungo senza NaN."""
    ok = np.isfinite(x)
    migliore = (0, 0)
    i = 0
    while i < len(ok):
        if not ok[i]:
            i += 1
            continue
        j = i
        while j + 1 < len(ok) and ok[j + 1]:
            j += 1
        if j - i > migliore[1] - migliore[0]:
            migliore = (i, j)
        i = j + 1
    return migliore


def oscillazione(x):
    """Deviazione standard delle differenze fra campioni consecutivi."""
    return float(np.std(np.diff(x)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--grandezza', default='A3_angolo_tronco')
    # 0,05 e 0,10 sono i valori scritti nel codice precedente
    # (`EMA_ALPHA_POS` e `EMA_ALPHA_VEL`); 0,30 e' un termine di paragone
    # piu' reattivo.
    ap.add_argument('--alpha', nargs='*', type=float,
                    default=[0.30, 0.10, 0.05])
    ap.add_argument('--dove', default=os.path.join(QUI, 'tesi', 'figure'))
    a = ap.parse_args()

    fig, assi = plt.subplots(1, 2, figsize=(12.4, 4.4))
    fig.patch.set_facecolor('white')
    misure = {}

    for ax, rel, titolo in ((assi[0], ADL, 'nearly still person'),
                            (assi[1], FALL, 'fall')):
        cartella = os.path.join(QUI, rel)
        if not os.path.isdir(cartella):
            sys.exit('ripresa non trovata: ' + cartella)
        seq, dim = leggi(cartella)
        valide = sum(1 for s in seq if s is not None)
        print('%-20s %s: %d fotogrammi, %d con posa'
              % (titolo, os.path.basename(cartella), len(seq), valide))

        grezzo = grandezza_filtrata(seq, dim, 1.0, a.grandezza)
        i0, i1 = tratto_piu_lungo(grezzo)
        fetta = slice(i0, i1 + 1)
        t = np.arange(i1 - i0 + 1) / FPS
        ax.plot(t, grezzo[fetta], color=GRIGIO, lw=1.6,
                label=r'raw ($\alpha=1$)', zorder=2)

        misure[titolo] = {'grezzo': grezzo[fetta], 'alpha': {}}
        for al, col in zip(a.alpha, (BLU, VERDE, ROSSO)):
            y = grandezza_filtrata(seq, dim, al, a.grandezza)[fetta]
            ax.plot(t, y, color=col, lw=1.9, label=r'$\alpha=%.2f$' % al,
                    zorder=3)
            misure[titolo]['alpha'][al] = y

        ax.set_title(titolo, fontsize=12, color='#1d2b36', pad=8)
        ax.set_xlabel('time [s]', fontsize=9.5, color='#5a6b7a')
        ax.grid(color='#eef2f5', lw=0.8)
        ax.set_axisbelow(True)
        for sp in ('top', 'right'):
            ax.spines[sp].set_visible(False)
        for sp in ('left', 'bottom'):
            ax.spines[sp].set_edgecolor('#b9c6d2')
    assi[0].set_ylabel('trunk angle [deg]', fontsize=9.5, color='#5a6b7a')
    assi[1].legend(frameon=False, fontsize=9.5, loc='best')

    fig.tight_layout()
    os.makedirs(a.dove, exist_ok=True)
    fuori = os.path.join(a.dove, # Le scritte di questa figura sono gia' tutte inglesi: esiste
    # una variante sola, e il nome lo dichiara.
    'fig_ema_en.png')
    fig.savefig(fuori, dpi=400, facecolor='white', bbox_inches='tight')
    print('scritto', fuori)

    scheda = os.path.join(a.dove, 'fig_ema_en.txt')
    with open(scheda, 'w', encoding='utf-8') as f:
        f.write('media mobile esponenziale applicata alle COORDINATE dei\n')
        f.write('landmark, con le grandezze ricalcolate dal motore geometrico\n')
        f.write('ATTENZIONE: il filtro NON e stato applicato ai dati di\n')
        f.write('questo lavoro. Ricostruzione a posteriori.\n\n')
        f.write('grandezza osservata  %s\n' % a.grandezza)
        f.write('ferma   %s\n' % os.path.basename(ADL))
        f.write('caduta  %s\n\n' % os.path.basename(FALL))
        print()
        for titolo, dati in misure.items():
            g = dati['grezzo']
            r0 = oscillazione(g)
            med = float(np.median(g))
            i0 = int(np.argmax(np.abs(g - med)))
            amp0 = abs(g[i0] - med)
            f.write('%s\n' % titolo)
            f.write('  oscillazione grezza %.4f gradi\n' % r0)
            print(titolo)
            for al, y in dati['alpha'].items():
                rr = oscillazione(y)
                i1 = int(np.argmax(np.abs(y - med)))
                amp1 = abs(y[i1] - med)
                f.write('  alpha=%.2f  oscillazione %.4f (-%.0f%%)  '
                        'ampiezza -%.0f%%  ritardo %+.0f ms\n'
                        % (al, rr, 100 * (1 - rr / r0) if r0 else 0,
                           100 * (1 - amp1 / amp0) if amp0 else 0,
                           1000 * (i1 - i0) / FPS))
                print('  alpha=%.2f  oscillazione -%.0f%%   ampiezza -%.0f%%'
                      '   ritardo %+.0f ms'
                      % (al, 100 * (1 - rr / r0) if r0 else 0,
                         100 * (1 - amp1 / amp0) if amp0 else 0,
                         1000 * (i1 - i0) / FPS))
            f.write('\n')
    print('scheda    %s' % scheda)


if __name__ == '__main__':
    main()
