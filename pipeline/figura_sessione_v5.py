# -*- coding: utf-8 -*-
"""
La sessione del 9 settembre sera, in una figura sola.

Perche' esiste
--------------
Il registro `sess_20260909_v5.csv` contiene 624 righe e la verita' di
riferimento sta in un LEGGIMI. Messi insieme rispondono a una domanda che il
Capitolo 5 pone e non mostra mai: **quando il classificatore vede una caduta e
quando invece e' la REGOLA a perderla.**

Le quattro cadute sono dichiarate dalla candidata sui fotogrammi annotati.

Che cosa si legge, nell'ordine in cui salta all'occhio:

  1. per 697 secondi su 900 il sistema **non decide**, in attesa del piano del
     pavimento (ISS-156);
  2. la caduta 2 supera la soglia quanto la 1 e **non produce allarme**, perche'
     cade dentro i 30 secondi di sospensione della prima (ISS-162);
  3. la caduta 3 il modello quasi non la vede: una finestra sopra soglia;
  4. il picco a 881 s **non e' una caduta**: e' una persona seduta sul divano,
     con `A3_h_pavimento` installata.

Tinte: quelle di `figure_tesi.py`, verificate per dicromazia --- separazione
peggiore 10,0 in OKLab x100. Nessuna identita' e' affidata al solo colore:
ogni banda porta la sua etichetta scritta.

Uso:
    python pipeline/figura_sessione_v5.py
    python pipeline/figura_sessione_v5.py --out /altro/percorso
"""
import argparse
import csv
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)

# Una sola fonte per le tinte e per l'aspetto: se cambiano li', cambiano qui.
from pipeline.figure_tesi import INK, GRIGIO, BLU, ROSSO, SABBIA, CHIARO  # noqa: E402

REGISTRO = os.path.join(RADICE, 'deploy_board', 'sessioni', '20260909_v5',
                        'sess_20260909_v5.csv')
SOGLIA = 0.50
DURATA = 900.0

# Verita' di riferimento: dichiarata sui fotogrammi annotati, non dedotta dai
# punteggi. Vedi deploy_board/sessioni/20260909_v5/LEGGIMI.md
CADUTE = [
    (742.0, 746.5, '1', 'allarme', True),
    (748.0, 751.5, '2', 'soppressa dai 30 s', False),
    (803.0, 807.5, '3', 'il modello non la vede', False),
    (855.0, 857.5, '4', 'allarme', True),
]
FALSO_POSITIVO = (880.5, 883.5, 'divano, non una caduta')
ALLARMI = [743.5, 856.3]


def leggi(percorso):
    with open(percorso, encoding='utf-8') as f:
        r = list(csv.DictReader(f))
    return ([float(x['t_s']) for x in r], [float(x['punteggio']) for x in r])


def disegna(t, p, out):
    """Due riquadri: la sequenza sopra, la lettura delle quattro cadute sotto.

    Il primo tentativo disegnava 0-900 s e sprecava il 77% della tela sulla
    zona in cui il sistema non decide, schiacciando tutto cio' che conta
    nell'ultimo quinto. Quel fatto e' un NUMERO, non una forma: sta meglio
    scritto che disegnato.
    """
    fig, (ax, bx) = plt.subplots(
        2, 1, figsize=(9.2, 4.5), gridspec_kw={'height_ratios': [3.1, 1],
                                               'hspace': .38})

    x0, x1 = 690.0, DURATA

    # --- le quattro cadute, dichiarate sui fotogrammi -------------------
    for a, b, n, _nota, _presa in CADUTE:
        ax.axvspan(a, b, color=SABBIA, alpha=.30, lw=0, zorder=1)
        ax.text((a + b) / 2, 1.035, n, ha='center', va='bottom',
                fontsize=10, weight='bold', color=INK)

    a, b, _ = FALSO_POSITIVO
    ax.axvspan(a, b, color=CHIARO, alpha=.95, lw=0, zorder=1)
    ax.annotate('divano\nnon e\' una caduta',
                xy=((a + b) / 2, .70), xytext=(899, .97),
                ha='right', va='top', fontsize=8, color=INK, linespacing=1.3,
                arrowprops=dict(arrowstyle='-', color=GRIGIO, lw=.8))

    # --- il punteggio ---------------------------------------------------
    ax.plot(t, p, color=BLU, lw=1.5, zorder=3, solid_capstyle='round')

    ax.axhline(SOGLIA, color=GRIGIO, lw=1.0, ls='--', zorder=2)
    ax.text(x0 + 2, SOGLIA + .02, 'soglia 0,50', ha='left', va='bottom',
            fontsize=8, color=GRIGIO)

    # --- gli allarmi emessi ---------------------------------------------
    for k, ta in enumerate(ALLARMI, 1):
        pa = max(v for tt, v in zip(t, p) if abs(tt - ta) < .35)
        ax.plot([ta], [pa], marker='v', ms=9, color=ROSSO, zorder=5,
                markeredgecolor='white', markeredgewidth=1.0)
        dx = -20 if k == 1 else -22
        ax.annotate('allarme ' + str(k), xy=(ta, pa),
                    xytext=(ta + dx, min(pa + .16, .99)),
                    ha='center', fontsize=8.5, weight='bold', color=ROSSO,
                    arrowprops=dict(arrowstyle='-', color=ROSSO, lw=.8))

    ax.set_xlim(x0, x1)
    ax.set_ylim(-.02, 1.02)
    ax.set_xlabel('secondi dall' + chr(39) + 'avvio della sessione')
    ax.set_ylabel('punteggio')
    ax.set_xticks(range(700, 901, 25))
    ax.set_yticks([0, .25, .5, .75, 1.0])
    ax.set_yticklabels(['0', '0,25', '0,50', '0,75', '1'])
    ax.grid(axis='y', color=CHIARO, lw=.7, alpha=.7, zorder=0)
    ax.set_axisbelow(True)
    ax.set_title('Quattro cadute, due allarmi: il classificatore ne vede tre, '
                 'la regola ne segnala due', fontsize=10.5, pad=26)

    # --- la lettura, sotto ----------------------------------------------
    bx.axis('off')
    bx.set_xlim(0, 1)
    bx.set_ylim(0, 1)

    righe = [
        ('1', '742 s', 'picco 0,96', 'allarme emesso', True),
        ('2', '748 s', 'picco 0,80', 'nessun allarme: sei secondi dopo la 1, '
         'dentro i 30 s di sospensione', False),
        ('3', '803 s', 'picco 0,52', 'nessun allarme: una sola finestra sopra '
         'soglia, il modello quasi non la vede', False),
        ('4', '855 s', 'picco 0,80', 'allarme emesso', True),
    ]
    y = .93
    for n, quando, picco, esito, presa in righe:
        col = INK if presa else ROSSO
        bx.text(.005, y, n, fontsize=10, weight='bold', va='top', color=INK)
        bx.text(.035, y, quando, fontsize=8.2, va='top', color=INK)
        bx.text(.105, y, picco, fontsize=8.2, va='top', color=INK)
        bx.text(.195, y, ('OK  ' if presa else 'NO  ') + esito, fontsize=8.2,
                va='top', color=col, weight='bold' if not presa else 'normal')
        y -= .245

    bx.text(.005, -.10, 'Prima delle 697 s il sistema non ha deciso nulla: '
            '2.717 finestre scartate perche' + chr(39) + ' il piano del '
            'pavimento non era ancora stimato. Restano 203 s utili su 900.',
            fontsize=8, va='top', color=GRIGIO, style='italic')

    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--registro', default=REGISTRO)
    ap.add_argument('--out', default=os.path.join(RADICE, 'tesi', 'figure',
                                                  'fig_sessione_v5.png'))
    a = ap.parse_args()

    if not os.path.isfile(a.registro):
        sys.exit(f'manca il registro: {a.registro}')
    t, p = leggi(a.registro)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    disegna(t, p, a.out)

    sopra = sum(1 for v in p if v >= SOGLIA)
    print(f'registro   {len(t)} finestre decise, da {t[0]:.1f} s a {t[-1]:.1f} s')
    print(f'           {sopra} sopra soglia, picco {max(p):.3f}')
    print(f'cadute     {len(CADUTE)} dichiarate sui fotogrammi, '
          f'{sum(1 for c in CADUTE if c[4])} con allarme')
    print(f'scritto    {a.out}')


if __name__ == '__main__':
    main()
