# -*- coding: utf-8 -*-
"""
Due figure misurate sul dispositivo, dai registri di sanita' delle sessioni.

Perche' esistono
----------------
Il Capitolo 5 afferma due cose importanti e le lascia in prosa:

  1. che la temperatura raggiunge un regime e non produce `thermal throttling`
     --- 79,5 gradi al massimo, regime dopo circa quaranta minuti;
  2. che la cadenza «non e' un numero solo» ma dipende da quante persone sono
     inquadrate, dal carico e dalla scena, variando fra 1,15 e 8,20 fps.

La seconda regge un'intera conseguenza metodologica: la finestra e' definita
come CONTEGGIO di campioni, quindi a cadenze diverse copre durate diverse, e
il modello in esercizio riassume una porzione di tempo diversa da quella su
cui e' stato addestrato.

Entrambe sono misurate e nessuna delle due ha una figura. I dati stanno in
`risultati/sessioni/*/*/sanita.csv`, che la board scrive durante l'esercizio:
istante, fotogrammi, pose valide, cadenza, allarmi, disco e temperatura.

Uso
---
    python pipeline/figura_dispositivo.py
    python pipeline/figura_dispositivo.py --lingua en
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt                             # noqa: E402

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INK, GRIGIO = '#1A1F23', '#8A949B'
BLU, ROSSO, SABBIA, CHIARO = '#2B5D7D', '#9C3B45', '#C4A55C', '#C9D4DA'

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.sans-serif': ['DejaVu Sans'],
    'font.size': 9.5, 'axes.edgecolor': GRIGIO, 'axes.labelcolor': INK,
    'text.color': INK, 'xtick.color': INK, 'ytick.color': INK,
    'axes.spines.top': False, 'axes.spines.right': False,
    'figure.facecolor': 'white', 'savefig.facecolor': 'white',
    'savefig.dpi': 400,
})

LINGUA = 'it'


def T(it, en):
    return it if LINGUA == 'it' else en


def dec(v, n=1):
    # il separatore segue la lingua: in inglese il punto e' quello
    # decimale, e «79,5» in una figura inglese e' scorretto
    t = ('{:.' + str(n) + 'f}').format(v)
    return t.replace('.', ',') if LINGUA == 'it' else t


def virgola(ax, assi='y'):
    from matplotlib.ticker import FuncFormatter
    if LINGUA != 'it':
        return                      # matplotlib usa gia' il punto
    f = FuncFormatter(lambda v, _: ('{:g}'.format(v)).replace('.', ','))
    if 'x' in assi:
        ax.xaxis.set_major_formatter(f)
    if 'y' in assi:
        ax.yaxis.set_major_formatter(f)


def suffisso(nome):
    if LINGUA == 'it':
        return nome
    r, p, e = nome.rpartition('.')
    return r + '_en' + p + e


# =========================================================================
#  1. Temperatura e cadenza durante la prova prolungata
# =========================================================================
def fig_termica(dove, sessione='20260811'):
    import pandas as pd
    trovati = sorted(glob.glob(os.path.join(
        QUI, 'risultati', 'sessioni', sessione, '*', 'sanita.csv')))
    if not trovati:
        print('  fig_termica  ASSENTE: nessun sanita.csv in', sessione)
        return
    d = pd.read_csv(trovati[0])
    ore = (d.t_unix - d.t_unix.iloc[0]) / 3600.0

    # I buchi vanno SPEZZATI, non interpolati. In questa sessione il sistema
    # operativo ha sospeso la board per 68 minuti: fra due campioni corrono
    # 4118 secondi, e una linea continua li attraverserebbe disegnando una
    # discesa graduale della temperatura che non e' stata misurata.
    salto = d.t_unix.diff() > 300
    temp = d.temp_c.astype(float).copy()
    fps = d.fps.astype(float).copy()
    temp[salto] = np.nan
    fps[salto] = np.nan

    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    for i in np.flatnonzero(salto.to_numpy()):
        ax.axvspan(ore.iloc[i - 1], ore.iloc[i], color=SABBIA, alpha=.22,
                   zorder=0)
        minuti = (d.t_unix.iloc[i] - d.t_unix.iloc[i - 1]) / 60.0
        ax.text((ore.iloc[i - 1] + ore.iloc[i]) / 2, d.temp_c.max() + 1.5,
                T('sospensione\n%s min', 'suspended\n%s min') % dec(minuti, 1),
                ha='center', va='bottom', fontsize=8.5, color=INK, zorder=5)
    ax.plot(ore, temp, lw=1.6, color=ROSSO, zorder=3)
    ax.set_xlabel(T('ore dall\'avvio', 'hours from start'))
    ax.set_ylabel(T('temperatura [$^\\circ$C]', 'temperature [$^\\circ$C]'),
                  color=ROSSO)
    ax.tick_params(axis='y', colors=ROSSO)
    ax.set_ylim(min(60, d.temp_c.min() - 3), d.temp_c.max() + 9)

    # il regime: la temperatura si stabilizza dopo circa quaranta minuti
    reg = 40.0 / 60.0
    ax.axvline(reg, ls=':', lw=1.2, color=GRIGIO, zorder=2)
    ax.annotate(T('regime dopo ~40 min', 'steady state after ~40 min'),
                xy=(reg, d.temp_c.max() + 2), xytext=(reg + .18,
                                                      d.temp_c.max() + 3.4),
                fontsize=8.5, color=GRIGIO,
                arrowprops=dict(arrowstyle='->', color=GRIGIO, lw=1))
    # l'etichetta del massimo va tenuta a sinistra della sospensione, che
    # occupa la fascia centrale: prima si sovrapponevano
    ax.annotate(T('massimo %s$^\\circ$C', 'peak %s$^\\circ$C')
                % dec(d.temp_c.max()),
                xy=(ore[d.temp_c.idxmax()], d.temp_c.max()),
                xytext=(ore[d.temp_c.idxmax()] + .22, d.temp_c.max() + 5.6),
                fontsize=9, color=ROSSO, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=ROSSO, lw=1))

    bx = ax.twinx()
    bx.plot(ore, fps, lw=1.2, color=BLU, alpha=.85, zorder=3)
    bx.set_ylabel(T('cadenza [fps]', 'frame rate [fps]'), color=BLU)
    bx.tick_params(axis='y', colors=BLU)
    bx.set_ylim(0, max(10, d.fps.max() * 1.25))
    bx.spines['right'].set_visible(True)
    bx.spines['right'].set_color(GRIGIO)

    ax.grid(axis='y', color=CHIARO, lw=.7, zorder=0)
    ax.set_axisbelow(True)
    virgola(ax, 'xy')
    virgola(bx, 'y')
    fig.tight_layout()

    nome = suffisso('fig_termica.png')
    fig.savefig(os.path.join(dove, nome), bbox_inches='tight')
    plt.close(fig)
    print('  %-30s <- sessioni/%s/sanita.csv  (%.1f h, %d campioni)'
          % (nome, sessione, ore.iloc[-1], len(d)))


# =========================================================================
#  2. La cadenza non e' un numero solo
# =========================================================================
def fig_cadenza(dove):
    righe = []
    for r in sorted(glob.glob(os.path.join(
            QUI, 'risultati', 'sessioni', '*', '*', 'riepilogo.json'))):
        j = json.load(open(r, encoding='utf-8'))
        if not j.get('durata_h'):
            continue
        righe.append((j.get('blocco', '?'), float(j['fps_medio']),
                      float(j['durata_h']), float(j.get('quota_pose', 0))))
    if not righe:
        print('  fig_cadenza  ASSENTE: nessun riepilogo.json')
        return
    righe.sort(key=lambda r: r[1])

    nomi = [r[0] for r in righe]
    fps = np.array([r[1] for r in righe])
    ore = np.array([r[2] for r in righe])
    pose = np.array([r[3] for r in righe])

    fig, ax = plt.subplots(figsize=(7.8, 4.2))
    y = np.arange(len(righe))[::-1]
    # il colore dice la quota di pose valide: le registrazioni piu' lente sono
    # anche quelle in cui lo stimatore fatica, e le due cose vanno lette insieme
    colori = [ROSSO if p < .5 else BLU for p in pose]
    ax.barh(y, fps, height=.62, color=colori, zorder=3)

    for i, (v, o) in enumerate(zip(fps, ore)):
        ax.text(v + .12, y[i], dec(v, 2), va='center', fontsize=9,
                color=INK, fontweight='bold')
        ax.text(-.15, y[i], T('%s h', '%s h') % dec(o, 2), va='center',
                ha='right', fontsize=8, color=GRIGIO)

    # la cadenza di progetto
    ax.axvline(9, ls='--', lw=1.4, color=SABBIA, zorder=4)
    ax.text(9.1, y[0] + .7, T('cadenza di progetto: 9 fps',
                              'design rate: 9 fps'),
            fontsize=8.5, color=SABBIA, fontweight='bold')

    ax.set_yticks(y)
    ax.set_yticklabels(nomi, fontsize=8.5)
    ax.set_xlabel(T('cadenza media della registrazione [fps]',
                    'mean frame rate of the recording [fps]'))
    ax.set_xlim(0, 10.4)
    ax.set_ylim(-.8, len(righe) - .05)
    ax.grid(axis='x', color=CHIARO, lw=.7, zorder=0)
    ax.set_axisbelow(True)
    virgola(ax, 'x')

    from matplotlib.patches import Patch
    ax.legend(handles=[
        Patch(color=BLU, label=T('posa valida sopra il 50%',
                                 'valid pose above 50%')),
        Patch(color=ROSSO, label=T('posa valida sotto il 50%',
                                   'valid pose below 50%'))],
        frameon=False, fontsize=8.5, loc='lower right')

    fig.tight_layout()
    nome = suffisso('fig_cadenza.png')
    fig.savefig(os.path.join(dove, nome), bbox_inches='tight')
    plt.close(fig)
    print('  %-30s <- %d riepilogo.json  (da %s a %s fps)'
          % (nome, len(righe), dec(fps.min(), 2), dec(fps.max(), 2)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dove', default=os.path.join(QUI, 'tesi', 'figure'))
    ap.add_argument('--lingua', default='it', choices=('it', 'en'))
    a = ap.parse_args()

    global LINGUA
    LINGUA = a.lingua
    os.makedirs(a.dove, exist_ok=True)

    for f in (fig_termica, fig_cadenza):
        try:
            f(a.dove)
        except Exception as e:
            print('  %-30s FALLITA: %s' % (f.__name__, e))


if __name__ == '__main__':
    main()
