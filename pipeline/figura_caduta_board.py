# -*- coding: utf-8 -*-
"""
Una caduta reale rilevata dal sistema installato, con la faccia oscurata.

Perche' esiste
--------------
Fin qui il capitolo sul campo mostrava soltanto grafici di punteggio: nessuna
immagine reale, per la regola di riservatezza del progetto (le clip ritraggono
persone identificabili e restano escluse da git). La candidata ha chiesto
esplicitamente, per questo fotogramma solo e con la faccia oscurata, di farne
un'eccezione: e' casa sua e la persona a terra e' lei.

La sorgente e' `deploy_board/sessioni/20260909_v5/clip/f00856.0.jpg`, uno dei
2.254 fotogrammi annotati dalla board durante la sessione del 9 settembre: e'
il picco della prima caduta (Sezione~sec:campo del Cap5), punteggio 0,760,
quarta finestra di una raffica di cinque, un fotogramma prima dell'allarme.

La faccia e' pixelata, non solo sfocata: uno sfocamento gaussiano si puo'
invertire parzialmente conoscendone i parametri, la pixelazione a blocchi
grandi (12 px, su una faccia di circa 110x100) distrugge l'informazione e non
la nasconde soltanto.

Uso
---
    python pipeline/figura_caduta_board.py --lingua it
    python pipeline/figura_caduta_board.py --lingua en
"""
import argparse
import os
import sys

import numpy as np

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Rectangle

from pipeline.figure_tesi import INK, GRIGIO, ROSSO, CHIARO  # noqa: E402

SORGENTE = os.path.join(RADICE, 'deploy_board', 'sessioni', '20260909_v5',
                        'clip', 'f00856.0.jpg')
# la faccia sta qui nel fotogramma originale (640x650): individuata a vista
# ritagliando la zona della testa e verificando il risultato prima di
# pixelare, non indovinata.
RIQUADRO_FACCIA = (405, 265, 565, 385)  # sinistra, sopra, destra, sotto
USCITA = os.path.join(RADICE, 'tesi', 'figure')

LINGUA = 'it'


def T(it, en):
    return it if LINGUA == 'it' else en


def pixela(img, riquadro, blocco=12):
    """Sostituisce il riquadro con una versione a blocchi grandi: irreversibile.

    Passa per PIL con ricampionamento NEAREST, che tollera dimensioni non
    multiple del blocco senza bisogno di fare i conti a mano.
    """
    from PIL import Image
    x0, y0, x1, y1 = riquadro
    fuori = img.copy()
    if fuori.dtype != np.uint8:
        fuori = (fuori * 255).astype(np.uint8) if fuori.max() <= 1.0 \
            else fuori.astype(np.uint8)
    zona = fuori[y0:y1, x0:x1]
    h, w = zona.shape[:2]
    piccola = Image.fromarray(zona).resize(
        (max(1, w // blocco), max(1, h // blocco)), Image.NEAREST)
    grande = np.array(piccola.resize((w, h), Image.NEAREST))
    fuori[y0:y1, x0:x1] = grande
    return fuori


def disegna():
    img = mpimg.imread(SORGENTE)
    img_oscurata = pixela(img, RIQUADRO_FACCIA, blocco=12)
    h, w = img_oscurata.shape[:2]

    fig, ax = plt.subplots(figsize=(5.4, 5.6))
    ax.imshow(img_oscurata)
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.set_xticks([])
    ax.set_yticks([])
    for lato in ax.spines.values():
        lato.set_edgecolor(GRIGIO)
        lato.set_linewidth(.8)

    x0, y0, x1, y1 = RIQUADRO_FACCIA
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False,
                           edgecolor=ROSSO, lw=1.3, ls='--', zorder=5))
    ax.text(x0, y0 - 6, T('faccia oscurata', 'face redacted'),
            color=ROSSO, fontsize=8, weight='bold', va='bottom')

    ax.set_title(T('Fotogramma reale, prima caduta della sessione: '
                   'punteggio 0,760, raffica 4/5',
                   'Real frame, first fall of the session: '
                   'score 0.760, burst 4/5'),
                 fontsize=9.5, pad=8, color=INK)
    fig.subplots_adjust(left=.02, right=.98, top=.93, bottom=.02)
    return fig


def main():
    global LINGUA
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--lingua', default='it', choices=('it', 'en'))
    ap.add_argument('--out', default=USCITA)
    a = ap.parse_args()
    LINGUA = a.lingua

    if not os.path.exists(SORGENTE):
        sys.exit('manca il fotogramma sorgente: %s' % SORGENTE)

    nome = 'fig_caduta_board.png' if LINGUA == 'it' else 'fig_caduta_board_en.png'
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
            'Un fotogramma reale della sessione del 9 settembre 2026, con lo\n'
            'scheletro e il punteggio sovrapposti dal registratore della board.\n'
            'E\' il picco della prima delle quattro cadute simulate (punteggio\n'
            '0,760, quarta finestra della raffica di cinque che porta al primo\n'
            'allarme). Descritta in tesi/Cap5.tex, sec:campo.\n\n'
            'PERSONE E RISERVATEZZA\n-----------------------\n'
            'La persona a terra e\' la candidata, nella propria abitazione.\n'
            'Inserita SOLO dopo richiesta esplicita della candidata, che ha\n'
            'chiesto di oscurare la faccia. La faccia e\' pixelata a blocchi di\n'
            '12 pixel (non sfocata): la pixelazione distrugge l\'informazione,\n'
            'uno sfocamento gaussiano e\' in alcuni casi parzialmente invertibile.\n'
            'Il riquadro rosso in figura mostra dove.\n\n'
            'PROVENIENZA\n-----------\n'
            'deploy_board/sessioni/20260909_v5/clip/f00856.0.jpg\n'
            '  uno dei 2.254 fotogrammi annotati dalla board durante la sessione\n\n'
            'PRODOTTA DA\n-----------\npipeline/figura_caduta_board.py --lingua %s\n'
            % (nome, '=' * (9 + len(nome)), LINGUA))
    print('scritta %s' % scheda)
    return 0


if __name__ == '__main__':
    sys.exit(main())
