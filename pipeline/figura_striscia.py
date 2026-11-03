# -*- coding: utf-8 -*-
"""
Una caduta, quattro istanti, e le grandezze che la seguono.

Perche' esiste
--------------
La selezione con il DTW dice QUANTO una grandezza separa le classi, ma non
mostra COME. Questa figura affianca le due cose: in alto quattro fotogrammi
della stessa caduta con la posa stimata, in basso l'andamento di due grandezze
sullo stesso asse dei tempi, con i quattro istanti segnati.

Le due grandezze sono scelte per contrasto, e sono l'argomento del capitolo:

  - una DERIVATA ISTANTANEA (velocita' del bacino): quello che il sistema
    usava all'inizio;
  - una GRANDEZZA INTEGRALE (discesa del bacino sulla finestra mobile):
    quello che la sostituisce.

Se l'argomento del Capitolo 3 regge, la seconda deve avere un picco leggibile
in corrispondenza della transizione e la prima no --- non perche' la dinamica
non ci sia, ma perche' nella derivata e' sepolta nel rumore di stima.

Ambiente: `fall_processing` (serve MediaPipe).

    python pipeline/figura_striscia.py
"""

import argparse
import os
import sys

import numpy as np

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if QUI not in sys.path:
    sys.path.insert(0, QUI)

import config                                                  # noqa: E402
from src.provenienza import provenienza                        # noqa: E402
from pipeline.figura_rappresentazioni import (elabora, con_scheletro,  # noqa: E402
                                              riquadro, RIPRESA, dec)

import matplotlib                                              # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt                                # noqa: E402

INK, GRIGIO, BLU = '#1A1F23', '#8A949B', '#2B5D7D'
TEAL, ROSSO, SABBIA = '#2E8B8B', '#9C3B45', '#C4A55C'

# derivata istantanea contro grandezza integrale, sulla stessa quantita' fisica
CURVE = {
    'it': [('A3_hip_vel', 'velocità del bacino (derivata istantanea)', GRIGIO),
           ('A3_discesa', 'discesa del bacino (integrale su finestra mobile)',
            ROSSO)],
    'en': [('A3_hip_vel', 'hip velocity (instantaneous derivative)', GRIGIO),
           ('A3_discesa', 'hip descent (integral over a sliding window)',
            ROSSO)],
}

ASSI = {
    'it': ('tempo (s)', 'valore normalizzato\nal proprio massimo'),
    'en': ('time (s)', 'value normalised\nto its own maximum'),
}


def istanti(seq, quanti=4):
    """
    Quattro istanti attorno alla transizione.

    Si individua il fotogramma in cui l'angolo del tronco cambia piu' in
    fretta --- che e' la caduta --- e si prendono due istanti prima e due
    dopo. Prenderli equispaziati sull'intera ripresa darebbe tre fotogrammi
    di persona ferma e uno di caduta.
    """
    ang = np.array([d['f'].get('A3_angolo_tronco', np.nan) for d in seq],
                   dtype=float)
    validi = np.array([d['punti'] is not None for d in seq])
    ang[~validi] = np.nan
    d1 = np.abs(np.gradient(np.nan_to_num(ang, nan=np.nanmean(ang))))
    centro = int(np.nanargmax(d1))
    proposti = [centro - 14, centro - 3, centro + 6, centro + 22]
    fuori = []
    for i in proposti:
        i = int(np.clip(i, 0, len(seq) - 1))
        while i < len(seq) and seq[i]['punti'] is None:
            i += 1
        fuori.append(min(i, len(seq) - 1))
    return sorted(set(fuori))[:quanti], centro


def disegna(seq, scelti, dove, nome='fig_striscia.png', stile='neutro',
            lingua='it'):
    n = len(scelti)
    fig = plt.figure(figsize=(10.6, 6.0))
    griglia = fig.add_gridspec(2, n, height_ratios=[1.35, 1], hspace=.12,
                               wspace=.03)

    # --- in alto: i fotogrammi, TUTTI CON LO STESSO RITAGLIO ---------
    # Un ritaglio per fotogramma seguirebbe la persona e la mostrerebbe della
    # stessa dimensione in tutti e quattro: la caduta sparirebbe. Il riquadro
    # e' quindi calcolato sull'unione delle quattro pose.
    unione = np.vstack([seq[i]['punti'] for i in scelti])
    rx0, rx1, ry0, ry1 = riquadro(unione, seq[scelti[0]]['w'],
                                  seq[scelti[0]]['h'], margine=.16)
    for k, i in enumerate(scelti):
        ax = fig.add_subplot(griglia[0, k])
        d = seq[i]
        ax.imshow(con_scheletro(d, stile=stile))
        ax.set_xlim(rx0, rx1)
        ax.set_ylim(ry1, ry0)
        ax.set_xticks([])
        ax.set_yticks([])
        for lato in ax.spines.values():
            lato.set_color(GRIGIO)
            lato.set_linewidth(.8)
        ax.set_title('%s' % chr(ord('a') + k), fontsize=11, fontweight='bold',
                     color=INK, pad=3)

    # --- in basso: le curve ------------------------------------------
    bx = fig.add_subplot(griglia[1, :])
    t = np.arange(len(seq)) / config.FPS_DATASET

    for chiave, etichetta, colore in CURVE[lingua]:
        v = np.array([d['f'].get(chiave, np.nan) for d in seq], dtype=float)
        v = np.abs(v)
        scala = np.nanmax(v) or 1.0
        bx.plot(t, v / scala, color=colore, lw=1.6, label=etichetta)

    for k, i in enumerate(scelti):
        bx.axvline(t[i], color=INK, lw=.9, ls=':', zorder=1)
        bx.annotate(chr(ord('a') + k), xy=(t[i], 1.03),
                    xycoords=('data', 'axes fraction'), ha='center',
                    va='bottom', fontsize=10, fontweight='bold', color=INK)

    bx.set_xlim(t[0], t[-1])
    bx.set_ylim(-.04, 1.10)
    bx.set_xlabel(ASSI[lingua][0])
    bx.set_ylabel(ASSI[lingua][1])
    bx.legend(loc='lower center', bbox_to_anchor=(.5, -.42), ncol=2,
              frameon=False, fontsize=8.5, columnspacing=2.2)
    for lato in ('top', 'right'):
        bx.spines[lato].set_visible(False)

    p = os.path.join(dove, nome)
    fig.savefig(p, bbox_inches='tight', dpi=220, facecolor='white')
    plt.close(fig)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lingua', default='it', choices=('it', 'en'))
    ap.add_argument('--ripresa', default=None)
    ap.add_argument('--limite', type=int, default=70)
    ap.add_argument('--istanti', default=None,
                    help='indici separati da virgola; senza, scelti attorno '
                         'alla transizione')
    ap.add_argument('--dove', default=os.path.join(QUI, 'tesi', 'figure'))
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

    if a.istanti:
        scelti = [int(x) for x in a.istanti.split(',')]
        centro = None
    else:
        scelti, centro = istanti(seq)
    print('transizione stimata al fotogramma %s' % centro)
    print('istanti    %s' % ', '.join(str(i) for i in scelti))
    for i in scelti:
        print('  #%-4d tronco %8s°   hip_vel %8s   discesa %8s'
              % (i, dec(seq[i]['f']['A3_angolo_tronco']),
                 dec(seq[i]['f']['A3_hip_vel'], 2),
                 dec(seq[i]['f']['A3_discesa'], 2)))

    nome = 'fig_striscia' + ('_en' if a.lingua == 'en' else '') + '.png'
    print('scritto   ', disegna(seq, scelti, a.dove, nome=nome,
                                stile=a.stile, lingua=a.lingua))
    print('codice    ', provenienza()['commit_breve'])


if __name__ == '__main__':
    main()
