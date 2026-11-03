# -*- coding: utf-8 -*-
"""
Il posizionamento della telecamera: l'inquadratura vera, la pianta, l'alzato.

Perche' esiste
--------------
La `fig_stanza` precedente era uno schema soltanto: pianta e alzato, disegnati.
Diceva che cosa il protocollo prescrive, ma non mostrava che cosa la telecamera
vede davvero --- e la ragione per cui l'altezza dal pavimento serve sta proprio
li', in una stanza in cui il divano e il pavimento stanno nella stessa
inquadratura.

Questa versione aggiunge il fotogramma reale, ripreso dalla board
nell'abitazione in cui si sono svolte le sessioni. Lo schema resta sotto,
perche' il fotogramma mostra un caso e lo schema la regola.

La fotografia
-------------
`tesi/figure/sorgenti/inquadratura_board.jpg`, copiata da `~/rileva/` sulla
Radxa. **Non ritrae persone**: e' la stanza vuota, ripresa per verificare
l'inquadratura prima di una sessione. E' l'unica immagine di ambiente
domestico che entra nella tesi, ed entra perche' la stanza e' vuota.

Lingua
------
Come per le altre figure del progetto: `--lingua en` produce `fig_stanza_en.png`.

Uso:
    python pipeline/figura_stanza.py --lingua it
    python pipeline/figura_stanza.py --lingua en
"""

import argparse
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Polygon, Rectangle, FancyArrowPatch

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)

from pipeline.figure_tesi import INK, GRIGIO, BLU, ROSSO, SABBIA, CHIARO  # noqa: E402

FOTO = os.path.join(RADICE, 'tesi', 'figure', 'sorgenti',
                    'inquadratura_board.jpg')
USCITA = os.path.join(RADICE, 'tesi', 'figure')

LINGUA = 'it'


def T(it, en):
    return it if LINGUA == 'it' else en


# --------------------------------------------------------------- pannelli
def pannello_foto(ax):
    """L'inquadratura vera, con le due zone che devono starci dentro.

    La sorgente e' un fotogramma della board (sessione del 9 settembre,
    ripresa diretta, nessuna persona in scena), non piu' la prima foto di
    verifica: risoluzione migliore, e l'oggetto personale che compariva sul
    bordo sinistro non c'e' semplicemente perche' l'inquadratura e' diversa.
    """
    img = mpimg.imread(FOTO)
    h, w = img.shape[:2]
    ax.imshow(img)
    ax.set_xlim(0, w); ax.set_ylim(h, 0)
    ax.set_xticks([]); ax.set_yticks([])
    for lato in ax.spines.values():
        lato.set_edgecolor(GRIGIO); lato.set_linewidth(.8)

    # La superficie rialzata: il divano, a sinistra.
    ax.add_patch(Rectangle((5, 75), 345, 258, fill=False,
                           edgecolor=ROSSO, lw=1.8, zorder=3))
    ax.text(9, 69, T('superficie rialzata', 'raised surface'),
            color=ROSSO, fontsize=9.5, weight='bold', va='bottom', zorder=4)

    # l'area di caduta: il pavimento libero con il tappeto, a destra
    ax.add_patch(Polygon([(232, h), (283, 222), (w - 2, 222), (w - 2, h)],
                         closed=True, fill=False, edgecolor=BLU, lw=1.8,
                         zorder=3))
    ax.text(w - 4, 216, T('area di caduta', 'fall area'),
            color=BLU, fontsize=9.5, weight='bold', ha='right', va='bottom',
            zorder=4)

    ax.set_title(T('Quello che la telecamera vede',
                   'What the camera actually sees'),
                 fontsize=10.5, pad=8, color=INK)


def pannello_pianta(ax):
    """Vista dall'alto: il cono visivo contiene divano e area libera."""
    ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis('off')
    ax.add_patch(Rectangle((.4, .4), 9.2, 6.2, fill=False,
                           edgecolor=GRIGIO, lw=1.2))

    cam = (1.3, 3.5)
    ax.add_patch(Polygon([cam, (9.3, 6.2), (9.3, .8)], closed=True,
                         facecolor=SABBIA, alpha=.20, lw=0))
    ax.plot(*cam, marker='s', ms=9, color=INK, zorder=5)
    ax.text(cam[0], cam[1] - .45, T('telecamera', 'camera'), ha='center',
            va='top', fontsize=9, color=INK, weight='bold')

    ax.add_patch(Rectangle((3.0, 4.7), 5.6, 1.4, facecolor='none',
                           edgecolor=ROSSO, lw=1.6))
    ax.text(5.8, 5.4, T('divano', 'sofa'), ha='center', va='center',
            fontsize=9, color=ROSSO, weight='bold')

    ax.add_patch(Rectangle((3.4, 1.2), 5.2, 2.6, facecolor='none',
                           edgecolor=BLU, lw=1.6, ls='--'))
    ax.text(6.0, 2.5, T('area di caduta', 'fall area'), ha='center',
            va='center', fontsize=9, color=BLU, weight='bold')

    ax.annotate('', xy=(8.6, .95), xytext=(3.4, .95),
                arrowprops=dict(arrowstyle='<->', color=BLU, lw=1.1))
    ax.text(6.0, .72, T('lato lungo perpendicolare all' + chr(39) + 'asse',
                        'long side perpendicular to the axis'),
            ha='center', va='top', fontsize=8, color=BLU)

    ax.set_title(T('Pianta', 'Plan view'), fontsize=10, pad=6, color=INK)


def pannello_alzato(ax):
    """Vista di lato: altezza e asse orizzontale."""
    ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis('off')
    ax.plot([.4, 9.6], [1.0, 1.0], color=GRIGIO, lw=1.4)
    ax.text(.5, .75, T('pavimento', 'floor'), fontsize=8, color=GRIGIO,
            va='top')

    cx, cy = 1.4, 4.0
    ax.plot(cx, cy, marker='s', ms=9, color=INK, zorder=5)
    ax.add_patch(FancyArrowPatch((cx + .25, cy), (9.2, cy),
                                 arrowstyle='-|>', mutation_scale=12,
                                 color=INK, lw=1.2))
    ax.text(5.6, cy + .18, T('asse ottico orizzontale',
                             'horizontal optical axis'),
            ha='center', va='bottom', fontsize=8.5, color=INK)

    ax.add_patch(Polygon([(cx, cy), (9.4, 6.4), (9.4, 1.0)], closed=True,
                         facecolor=SABBIA, alpha=.18, lw=0))

    ax.annotate('', xy=(cx, 1.0), xytext=(cx, cy),
                arrowprops=dict(arrowstyle='<->', color=ROSSO, lw=1.1))
    # il trattino lungo va scritto come carattere: matplotlib non interpreta
    # il «--» di LaTeX e lo stamperebbe come due trattini
    ax.text(cx - .25, 2.5, T('1,2–1,5 m', '1.2–1.5 m'), rotation=90,
            ha='right', va='center', fontsize=9, color=ROSSO, weight='bold')

    # persona in piedi e persona a terra, entrambe dentro il cono
    ax.plot([5.2, 5.2], [1.0, 3.6], color=BLU, lw=3.0, solid_capstyle='round')
    ax.plot(5.2, 3.85, marker='o', ms=7, color=BLU)
    ax.text(5.2, .75, T('in piedi', 'standing'), ha='center', va='top',
            fontsize=8, color=BLU)

    ax.plot([7.1, 8.7], [1.18, 1.18], color=BLU, lw=3.0,
            solid_capstyle='round')
    ax.plot(7.0, 1.18, marker='o', ms=7, color=BLU)
    ax.text(7.9, .75, T('a terra', 'on the floor'), ha='center', va='top',
            fontsize=8, color=BLU)

    ax.set_title(T('Alzato', 'Side view'), fontsize=10, pad=6, color=INK)


# ------------------------------------------------------------------- main
def disegna():
    fig = plt.figure(figsize=(9.6, 6.6))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.45, 1], hspace=.30,
                          wspace=.18)
    pannello_foto(fig.add_subplot(gs[0, :]))
    pannello_pianta(fig.add_subplot(gs[1, 0]))
    pannello_alzato(fig.add_subplot(gs[1, 1]))
    fig.subplots_adjust(left=.03, right=.97, top=.93, bottom=.04)
    return fig


def main():
    global LINGUA
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--lingua', default='it', choices=('it', 'en'))
    ap.add_argument('--out', default=USCITA)
    a = ap.parse_args()
    LINGUA = a.lingua

    if not os.path.exists(FOTO):
        sys.exit('manca la fotografia: %s' % FOTO)

    nome = 'fig_stanza.png' if LINGUA == 'it' else 'fig_stanza_en.png'
    fig = disegna()
    p = os.path.join(a.out, nome)
    fig.savefig(p, dpi=200, facecolor='white')
    plt.close(fig)
    print('scritta %s' % p)

    scheda = p[:-4] + '.txt'
    with open(scheda, 'w', encoding='utf-8') as f:
        f.write(
            'FIGURA — %s\n%s\n\n'
            'CHE COSA MOSTRA\n---------------\n'
            'In alto l\'inquadratura REALE della board nell\'abitazione in cui\n'
            'si sono svolte le sessioni. Sotto, lo schema del protocollo:\n'
            'pianta a sinistra, alzato a destra.\n\n'
            'PERCHE\' LA FOTOGRAFIA\n---------------------\n'
            'Lo schema dice che l\'inquadratura deve contenere sia l\'area di\n'
            'caduta sia le superfici rialzate. La fotografia lo mostra: il\n'
            'divano e il pavimento libero stanno nello stesso fotogramma, ed e\'\n'
            'esattamente la condizione che rende necessaria l\'altezza del\n'
            'bacino dal pavimento.\n\n'
            'PERSONE\n-------\n'
            'Nessuna. Il fotogramma ritrae la stanza vuota, ripresa per\n'
            'verificare l\'inquadratura prima di una sessione. E\' l\'unica\n'
            'immagine di ambiente domestico che entra nella tesi, ed entra\n'
            'perche\' non c\'e\' nessuno dentro.\n\n'
            'PROVENIENZA\n-----------\n'
            'tesi/figure/sorgenti/inquadratura_board.jpg\n'
            '  ritagliata da deploy_board/sessioni/20260909_diretta/clip/\n'
            '  f00019.7.jpg sulla Radxa ROCK 4D: fotogramma reale, nessuna\n'
            '  persona in scena, tolte solo le fasce con il punteggio in\n'
            '  sovraimpressione sopra e sotto.\n\n'
            'NON E\' UNA MISURA\n-----------------\n'
            'Pianta e alzato sono la resa grafica del protocollo, non un\n'
            'rilievo: le dimensioni degli ambienti non sono state registrate,\n'
            'e la tabella del protocollo lo dichiara. L\'unica quota reale e\'\n'
            'l\'altezza della telecamera, 1,2-1,5 m.\n\n'
            'PRODOTTA DA\n-----------\npipeline/figura_stanza.py --lingua %s\n'
            % (nome, '=' * (9 + len(nome)), LINGUA))
    print('scritta %s' % scheda)
    return 0


if __name__ == '__main__':
    sys.exit(main())
