# -*- coding: utf-8 -*-
"""
Popolazione italiana per fascia d'eta', 2016-2026: 0-14 contro 65 e piu'.

Perche' esiste
--------------
E' la figura di apertura del Capitolo 1. Serve a mostrare la ragione
strutturale per cui la domanda di assistenza domiciliare cresce: nello stesso
decennio le due curve si divaricano, e non e' un effetto di scala ma un
sorpasso gia' avvenuto.

Da dove vengono i numeri
------------------------
Sono LETTI DAL GRAFICO pubblicato nel Rapporto annuale ISTAT, non da una
tabella. La lettura e' accurata a circa +/- 30 mila unita': sufficiente per la
forma delle due curve e per i valori agli estremi citati nel testo (13,3 ->
14,8 milioni e 8,2 -> 6,9), non per citare un singolo anno intermedio come
dato puntuale.

**Se recuperi la tabella ISTAT, sostituisci i due dizionari qui sotto e
rigenera: non c'e' altro da toccare.** In didascalia conviene scrivere
«elaborazione su dati ISTAT», che e' quello che questa figura e'.

    conda activate fall_processing      # va bene qualunque ambiente con matplotlib
    python pipeline/figura_popolazione.py
"""

import argparse
import os
import sys

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if QUI not in sys.path:
    sys.path.insert(0, QUI)

import matplotlib                                              # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt                                # noqa: E402
from matplotlib.ticker import FuncFormatter                    # noqa: E402

LINGUA = 'it'


def T(it, en):
    """La stringa nella lingua corrente, come in `figure_tesi.py`."""
    return it if LINGUA == 'it' else en


ANNI = list(range(2016, 2027))

# migliaia di persone, al 1 gennaio -- lettura dal grafico ISTAT
GIOVANI = [8220, 8140, 8050, 7940, 7820, 7700, 7580, 7450, 7300, 7100, 6860]
ANZIANI = [13330, 13450, 13580, 13720, 13860, 13900, 13980, 14090, 14250,
           14520, 14830]

# Palette verificata sui controlli calcolabili (OKLab, simulazione
# Machado-Oliveira-Fernandes): entrambi i colori stanno nella banda di
# luminosita' 0,43-0,77, hanno croma sopra 0,10 e contrasto sopra 3:1 sul
# bianco; la separazione fra i due vale 26,2 a vista normale e 22,2 nel caso
# peggiore fra protanopia e deuteranopia, contro un obiettivo di 8.
# I colori di `figure_tesi.py` (#2B5D7D e #C4A55C) separano altrettanto bene
# ma non passano croma e contrasto: sono stati scuriti e saturati quanto basta.
BLU = '#15618F'      # 0-14
ORO = '#A8842F'      # 65 e piu'
INK = '#1A1F23'
GRIGIO = '#8A949B'
GRIGLIA = '#DCDFE2'


def migliaia(v, _pos=None):
    """13330 -> '13.330' in italiano, '13,330' in inglese.

    Il separatore non e' un dettaglio di stile: in inglese il punto e' il
    separatore DECIMALE, e «13.330» si leggerebbe tredici virgola
    trecentotrenta invece di tredicimilatrecentotrenta.
    """
    return format(int(v), ',d').replace(',', T('.', ','))


def disegna(dove, nome=None, dpi=300):
    nome = nome or ('fig_popolazione.png' if LINGUA == 'it'
                    else 'fig_popolazione_en.png')
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Griglia orizzontale soltanto: le linee verticali non aiutano a leggere
    # un valore su una serie continua, e competono con le curve.
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRIGLIA, lw=.8)
    ax.xaxis.grid(False)
    for lato in ('top', 'right'):
        ax.spines[lato].set_visible(False)
    for lato in ('left', 'bottom'):
        ax.spines[lato].set_color(GRIGIO)
        ax.spines[lato].set_linewidth(.8)

    ax.plot(ANNI, GIOVANI, color=BLU, lw=2.2, solid_capstyle='round',
            label=T('0-14 anni', '0-14 years'), zorder=3)
    ax.plot(ANNI, ANZIANI, color=ORO, lw=2.2, solid_capstyle='round',
            label=T('65 anni e più', '65 and over'), zorder=3)

    # Etichetta diretta all'estremo destro: l'identita' della serie non
    # dipende dal solo colore, e il valore finale e' quello citato nel testo.
    # Niente numeri su ogni punto -- gli estremi bastano.
    for y, colore, testo in (
            (ANZIANI[-1], ORO, T('65 anni e più', '65 and over')),
            (GIOVANI[-1], BLU, T('0-14 anni', '0-14 years'))):
        ax.annotate('%s\n%s' % (testo, migliaia(y)),
                    xy=(ANNI[-1], y), xytext=(6, 0),
                    textcoords='offset points', va='center', ha='left',
                    fontsize=9, color=INK, linespacing=1.35)

    # Valori di partenza, per rendere leggibile l'ampiezza del decennio.
    # Ancorati a destra del punto: centrati sfondavano sull'asse y e finivano
    # sotto le etichette delle tacche.
    for y in (ANZIANI[0], GIOVANI[0]):
        ax.annotate(migliaia(y), xy=(ANNI[0], y), xytext=(3, 7),
                    textcoords='offset points', ha='left', va='bottom',
                    fontsize=8.5, color=GRIGIO)

    ax.set_xlim(2015.7, 2026.0)
    ax.set_ylim(6000, 15000)
    ax.set_xticks(ANNI)
    ax.set_yticks(range(6000, 15001, 1000))
    ax.yaxis.set_major_formatter(FuncFormatter(migliaia))
    ax.tick_params(labelsize=9, colors=INK, length=0)
    ax.set_ylabel(T('migliaia di persone', 'thousands of people'),
                  fontsize=9, color=INK, labelpad=8)

    # Legenda in alto, come nell'originale ISTAT. Al centro del grafico
    # galleggiava nella fascia vuota fra le due curve.
    ax.legend(loc='lower center', bbox_to_anchor=(.5, 1.01), ncol=2,
              frameon=False, fontsize=9.5, handlelength=1.8,
              columnspacing=2.4)

    # Spazio a destra per le etichette dirette
    fig.subplots_adjust(right=.80)

    p = os.path.join(dove, nome)
    fig.savefig(p, dpi=dpi, facecolor='white', bbox_inches='tight',
                pad_inches=.15)
    plt.close(fig)
    return p


def main():
    global LINGUA
    ap = argparse.ArgumentParser()
    ap.add_argument('--dove', default=os.path.join(QUI, 'tesi', 'figure'))
    ap.add_argument('--dpi', type=int, default=300)
    ap.add_argument('--lingua', default='it', choices=('it', 'en'))
    a = ap.parse_args()
    LINGUA = a.lingua

    p = disegna(a.dove, dpi=a.dpi)
    print('scritto   ', p)
    print('65+        %s -> %s  (%+.1f%%)'
          % (migliaia(ANZIANI[0]), migliaia(ANZIANI[-1]),
             100 * (ANZIANI[-1] / ANZIANI[0] - 1)))
    print('0-14       %s -> %s  (%+.1f%%)'
          % (migliaia(GIOVANI[0]), migliaia(GIOVANI[-1]),
             100 * (GIOVANI[-1] / GIOVANI[0] - 1)))

    try:
        from src.provenienza import provenienza
        print('codice    ', provenienza()['commit_breve'])
    except Exception:
        pass


if __name__ == '__main__':
    main()
