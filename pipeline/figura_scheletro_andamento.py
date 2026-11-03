# -*- coding: utf-8 -*-
"""
La quarta caduta della sessione del 9 settembre, con lo scheletro sopra e
l'andamento del punteggio sotto, sullo stesso asse dei secondi.

Perche' esiste
--------------
Lo scheletro da solo mostra la posa ma non il momento della decisione. Sotto,
la stessa caduta sul punteggio: soglia, finestre sopra soglia, la raffica che
diventa allarme. Il fotogramma dello scheletro e' quello del picco (t = 855,96
s, punteggio 0,760), preso da sess_20260909_v5.csv: stessa sorgente della
figura dell'andamento, nessun valore scritto a mano.

Privacy: la figura in alto usa solo lo scheletro (landmark 11-32 di MediaPipe
Pose). I landmark del volto (0-10) non vengono disegnati.

Uso
---
    python pipeline/figura_scheletro_andamento.py --lingua it
    python pipeline/figura_scheletro_andamento.py --lingua en
"""
import argparse
import csv
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)

SESSIONE = os.path.join(RADICE, 'deploy_board', 'sessioni', '20260909_v5')
REGISTRO = os.path.join(SESSIONE, 'sess_20260909_v5.csv')
VERITA = os.path.join(SESSIONE, 'cadute.csv')
SCHELETRO = os.path.join(RADICE, 'tesi', 'figure', 'fig_scheletro_caduta_board.png')
USCITA = os.path.join(RADICE, 'tesi', 'figure')

SOGLIA = 0.50
FINESTRA = (835.0, 875.0)
ISTANTE_FOTOGRAMMA = 855.964          # f00856.0.jpg, punteggio 0,760
CORSA_ALLARME = 5                     # raffica di cinque finestre sopra soglia

INK = '#1C2430'
GRIGIO = '#8A929B'
BLU = '#2B5C7E'
ROSSO = '#9B1B30'
SABBIA = '#EBE0C8'

TESTI = {
    'it': {
        'titolo': 'La quarta caduta: lo scheletro e il punteggio',
        'y': 'punteggio',
        'x': 'secondi dall\'avvio della sessione',
        'soglia': 'soglia 0,50',
        'caduta': 'caduta dichiarata',
        'allarme': 'raffica che diventa allarme',
        'fotogramma': 'fotogramma mostrato sopra',
        'finestre': 'finestre sopra soglia',
        'allarme_val': 'allarme',
    },
    'en': {
        'titolo': 'The fourth fall: skeleton and score',
        'y': 'score',
        'x': 'seconds since session start',
        'soglia': 'threshold 0.50',
        'caduta': 'declared fall',
        'allarme': 'burst that raises the alarm',
        'fotogramma': 'frame shown above',
        'finestre': 'windows above threshold',
        'allarme_val': 'alarm',
    },
}


def leggi_registro():
    t, p, corsa = [], [], []
    with open(REGISTRO, encoding='utf-8') as f:
        for r in csv.DictReader(l for l in f if not l.startswith('#')):
            t.append(float(r['t_s']))
            p.append(float(r['punteggio']))
            corsa.append(int(r['corsa']))
    return np.array(t), np.array(p), np.array(corsa)


def leggi_cadute():
    out = []
    with open(VERITA, encoding='utf-8') as f:
        for r in csv.DictReader(l for l in f if not l.startswith('#')):
            if r['tipo'] == 'caduta' and r['etichetta'] == '4':
                out.append((float(r['inizio_s']), float(r['fine_s'])))
    return out


def costruisci(lingua):
    T = TESTI[lingua]
    t, p, corsa = leggi_registro()
    m = (t >= FINESTRA[0]) & (t <= FINESTRA[1])
    t, p, corsa = t[m], p[m], corsa[m]

    # istante in cui la raffica raggiunge le cinque finestre
    idx = np.where(corsa >= CORSA_ALLARME)[0]
    t_allarme = t[idx[0]] if len(idx) else None

    scheletro = np.array(Image.open(SCHELETRO).convert('RGB'))

    fig = plt.figure(figsize=(9.6, 8.2), dpi=200)
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.25], hspace=0.12)

    ax_img = fig.add_subplot(gs[0])
    ax_img.imshow(scheletro)
    ax_img.set_xticks([])
    ax_img.set_yticks([])
    for s in ax_img.spines.values():
        s.set_visible(False)

    ax = fig.add_subplot(gs[1])
    for a, b in leggi_cadute():
        ax.axvspan(a, b, color=SABBIA, zorder=0)
    ax.plot(t, p, color=BLU, lw=1.8, zorder=3)
    ax.axhline(SOGLIA, color=GRIGIO, ls='--', lw=1.2, zorder=2)
    ax.text(FINESTRA[0] + 0.5, SOGLIA + 0.02, T['soglia'], color=GRIGIO, fontsize=9)
    if t_allarme is not None:
        v_allarme = p[idx[0]]
        ax.scatter([t_allarme], [v_allarme], marker='v', s=110, color=ROSSO,
                   edgecolor='white', zorder=4, label=T['allarme'])
        ax.annotate('%s %s' % (T['allarme_val'], f'{v_allarme:.2f}'.replace('.', ',')),
                    xy=(t_allarme, v_allarme), xytext=(t_allarme + 4.5, v_allarme - 0.16),
                    color=ROSSO, fontsize=10, fontweight='bold',
                    arrowprops=dict(arrowstyle='-', color=ROSSO, lw=1))
    ax.axvline(ISTANTE_FOTOGRAMMA, color=INK, lw=0.9, ls=':', zorder=2)
    ax.text(ISTANTE_FOTOGRAMMA + 0.4, 0.93, T['fotogramma'], fontsize=9, color=INK)

    ax.set_xlim(*FINESTRA)
    ax.set_ylim(-0.03, 1.02)
    ax.set_xlabel(T['x'], color=INK)
    ax.set_ylabel(T['y'], color=INK)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.grid(axis='y', color='#E2E4E8', lw=0.8, zorder=0)
    ax.legend(loc='upper left', frameon=False, fontsize=9)

    fig.tight_layout()
    return fig, t_allarme


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lingua', default='it', choices=['it', 'en'])
    args = ap.parse_args()
    fig, t_allarme = costruisci(args.lingua)
    nome = 'fig_scheletro_andamento%s.png' % ('' if args.lingua == 'it' else '_en')
    out = os.path.join(USCITA, nome)
    fig.savefig(out, dpi=200)
    print('salvato', out)
    print('istante in cui la raffica raggiunge cinque finestre: %s s' % t_allarme)


if __name__ == '__main__':
    main()
