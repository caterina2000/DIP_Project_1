# -*- coding: utf-8 -*-
"""
Che cosa fa il DTW, e che cosa fa il vincolo |i-j| <= 10.

Perche' esiste
--------------
La Sezione `sec:dtw` spiega a parole tre cose che si capiscono guardandole:
perche' una distanza punto per punto non basta, che cosa significa deformare
localmente l'asse dei tempi, e che cosa cambia imponendo una banda attorno
alla diagonale. Sono un allineamento e una matrice: in figura si vedono.

E' una figura METODOLOGICA: spiega il criterio, non riporta un risultato. La
classifica delle grandezze e il confronto fra le due telecamere stanno altrove.

Concettuale nello scopo, non nei dati
-------------------------------------
Le curve non sono inventate: sono due riprese di caduta vere, la stessa
grandezza, z-scored e ricampionate a 200 campioni esattamente come fa la
procedura di selezione. Il cammino e' quello che la ricorsione del DTW
produce con la banda dichiarata in `src/dtw.py`.

La matrice cumulata serve solo a disegnare
------------------------------------------
`src/dtw.py` non conserva la matrice: tiene due righe, perche' su 33 grandezze
per due camere conservare 200x200 per ogni coppia costerebbe memoria senza
servire a nulla. Qui la ricorsione e' ripetuta per intero, e lo script
VERIFICA che la distanza che ne ricava coincida con quella di `src.dtw`. Se non
coincidesse, la figura mostrerebbe un allineamento diverso da quello che decide
la selezione.

Uso:
    python pipeline/figura_dtw.py
    python pipeline/figura_dtw.py --lingua it --grandezza A3_discesa
"""

import argparse
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, QUI)

import src.dtw as D
from src.dati import carica

BLU = '#1565c0'
ROSSO = '#d81b60'
VERDE = '#00897b'
ARANCIO = '#ef6c00'
GRIGIO = '#90a4ae'

TESTI = {
    'it': {
        'a': '(a) due riprese di caduta, stessa grandezza',
        'b': '(b) matrice dei costi cumulati',
        'c': '(c) dettaglio ingrandito',
        'r1': 'ripresa 1', 'r2': 'ripresa 2',
        'corr': 'corrispondenze trovate dal DTW',
        'diag': 'confronto uno-a-uno (diagonale)',
        'cam': 'cammino del DTW',
        'banda': r'banda ammessa $|i-j|\leq %d$',
        'escluso': 'escluso dalla banda',
        'xt': 'campione (dopo il ricampionamento a 200)',
        'yt': 'valore normalizzato',
        'xi': '$i$ — ripresa 1', 'yj': '$j$ — ripresa 2',
        'costo': 'costo cumulato',
        'zoom': 'zona ingrandita in (c)',
    },
    'en': {
        'a': '(a) two fall recordings, same quantity',
        'b': '(b) accumulated cost matrix',
        'c': '(c) zoomed detail',
        'r1': 'recording 1', 'r2': 'recording 2',
        'corr': 'correspondences found by DTW',
        'diag': 'one-to-one comparison (diagonal)',
        'cam': 'DTW warping path',
        'banda': r'allowed band $|i-j|\leq %d$',
        'escluso': 'excluded by the band',
        'xt': 'sample (after resampling to 200)',
        'yt': 'normalised value',
        'xi': '$i$ — recording 1', 'yj': '$j$ — recording 2',
        'costo': 'accumulated cost',
        'zoom': 'area zoomed in (c)',
    },
}


def dtw_completo(a, b, w):
    """
    La stessa ricorsione di `src.dtw._dtw_python`, ma con la matrice intera.

    Serve il cammino, e per il cammino serve poter tornare indietro. Fuori
    dalla banda resta `inf`, ed e' cosi' che la banda si vede nel disegno.
    """
    n, m = len(a), len(b)
    w = max(w, abs(n - m))
    Dm = np.full((n + 1, m + 1), np.inf)
    Dm[0, 0] = 0.0
    for i in range(1, n + 1):
        for j in range(max(1, i - w), min(m, i + w) + 1):
            c = abs(a[i - 1] - b[j - 1])
            Dm[i, j] = c + min(Dm[i - 1, j], Dm[i, j - 1], Dm[i - 1, j - 1])

    # ritorno all'indietro: a ogni passo il predecessore di costo minimo
    i, j, cammino = n, m, [(n, m)]
    while i > 1 or j > 1:
        passi = [(Dm[i - 1, j - 1], i - 1, j - 1),
                 (Dm[i - 1, j], i - 1, j),
                 (Dm[i, j - 1], i, j - 1)]
        _, i, j = min(passi, key=lambda t: t[0])
        cammino.append((i, j))
    return Dm, np.array(cammino[::-1], dtype=int)


def scegli_coppia(curve, scarto_min=6, scarto_max=18):
    """
    Due riprese con lo STESSO ANDAMENTO ma il picco spostato.

    Non sono scelte a vista, e non basta lo scarto fra i picchi: quello da solo
    accoppia volentieri una curva con un plateau e una con un picco stretto,
    cioe' due forme diverse, e la figura mostrerebbe due andamenti diversi
    invece della deformazione dell'asse dei tempi.

    Il criterio e' quindi in due passi. Si tengono le coppie il cui scarto fra
    i picchi sta fra `scarto_min` e `scarto_max` --- sotto non si vedrebbe la
    deformazione, sopra si uscirebbe dalla banda e si vedrebbe solo il vincolo
    --- e fra quelle si prende la piu' SIMILE, misurando la correlazione dopo
    aver riallineato le due curve sul loro scarto.
    """
    pronte = []
    for c in curve:
        z = D.zscore(D.ricampiona(c))
        if z is not None:
            pronte.append(z)

    meglio = None
    for p in range(len(pronte)):
        for q in range(p + 1, len(pronte)):
            u, v = pronte[p], pronte[q]
            d = int(np.argmax(u)) - int(np.argmax(v))
            if not (scarto_min <= abs(d) <= scarto_max):
                continue
            # correlazione sulla parte che si sovrappone dopo lo spostamento
            if d >= 0:
                uu, vv = u[d:], v[:len(v) - d]
            else:
                uu, vv = u[:len(u) + d], v[-d:]
            if len(uu) < 30 or uu.std() < 1e-9 or vv.std() < 1e-9:
                continue
            r = float(np.corrcoef(uu, vv)[0, 1])
            if meglio is None or r > meglio[0]:
                meglio = (r, abs(d), u, v)

    if meglio is None:
        return None
    r, d, u, v = meglio
    print(f'  somiglianza della coppia scelta: r = {r:.3f} dopo il '
          f'riallineamento')
    return (r, d, u, v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lingua', default='en', choices=('it', 'en'))
    ap.add_argument('--csv', default='feature_v5.csv')
    ap.add_argument('--grandezza', default='A3_discesa',
                    help='una delle dodici adottate, con un picco leggibile')
    ap.add_argument('--camera', type=int, default=1)
    a = ap.parse_args()
    T = TESTI[a.lingua]
    W = D.FINESTRA_WARPING

    print(f'lettura di {a.csv}...')
    df = carica(a.csv, camera=None)
    curve = D.curve_per_ripresa(df, a.grandezza, a.camera)['caduta']
    print(f'  {len(curve)} riprese di caduta sulla camera {a.camera}')

    scelta = scegli_coppia(curve)
    if scelta is None:
        sys.exit('nessuna coppia utilizzabile')
    _, scarto, x, y = scelta
    print(f'  coppia scelta: picchi distanti {scarto} campioni')

    Dm, cammino = dtw_completo(x, y, W)

    # --- il controllo che rende la figura fedele alla procedura ---
    mia = Dm[len(x), len(y)] / (len(x) + len(y))
    sua = D._dtw_python(x, y, W) / (len(x) + len(y))
    print(f'  distanza: matrice intera {mia:.6f}   src.dtw {sua:.6f}')
    if abs(mia - sua) > 1e-9:
        sys.exit('FERMATO: la matrice intera non riproduce src.dtw. '
                 'La figura mostrerebbe un allineamento diverso da quello '
                 'che decide la selezione.')
    print('  riproduce esattamente src.dtw')

    fuori = int((np.abs(cammino[:, 0] - cammino[:, 1]) >= W).sum())
    print(f'  cammino: {len(cammino)} passi, {fuori} sul bordo della banda')

    # regione da ingrandire nel pannello (c): quella in cui il cammino si
    # allontana di piu' dalla diagonale, cioe' dove il vincolo di banda lavora
    # davvero e non un tratto qualunque scelto a vista. Esclusi i bordi della
    # sequenza: li' le curve sono pressoche' costanti (fase precedente alla
    # caduta), il costo e' quasi zero ovunque e lo scostamento che ne segue e'
    # un artefatto del pareggio fra cammini equivalenti, non la deformazione
    # dovuta allo sfasamento del picco che la figura vuole mostrare.
    margine = 20
    interno = (np.arange(len(cammino)) > 0)
    interno &= (cammino[:, 0] > margine) & (cammino[:, 0] < len(x) - margine)
    interno &= (cammino[:, 1] > margine) & (cammino[:, 1] < len(y) - margine)
    scostamento = np.abs(cammino[:, 0] - cammino[:, 1]).astype(float)
    scostamento[~interno] = -1
    kmax = int(np.argmax(scostamento))
    ic, jc = cammino[kmax]
    meta = 18
    i0, i1 = max(0, ic - meta), min(len(x), ic + meta)
    j0, j1 = max(0, jc - meta), min(len(y), jc + meta)
    print(f'  zoom (c): i in [{i0},{i1}], j in [{j0},{j1}], '
          f'scostamento massimo {int(scostamento[kmax])} campioni')

    # ------------------------------------------------------------- disegno
    fig, (ax1, ax2, ax3) = plt.subplots(
        1, 3, figsize=(15.6, 5.6),
        gridspec_kw={'width_ratios': [1.5, 1.0, 0.62], 'wspace': 0.34})
    ALONE = [pe.withStroke(linewidth=2.6, foreground='white')]

    # ---------- (a) le due curve, e le corrispondenze ----------
    off = 2.7
    t = np.arange(len(x))
    for k in range(0, len(cammino), 9):
        i, j = cammino[k]
        ax1.plot([i - 1, j - 1], [x[i - 1] + off, y[j - 1] - off],
                 color=GRIGIO, lw=0.7, ls='--', zorder=2, alpha=0.9)
    ax1.plot(t, x + off, color=BLU, lw=2.2, zorder=4, path_effects=ALONE)
    ax1.plot(t, y - off, color=ARANCIO, lw=2.2, zorder=4, path_effects=ALONE)

    # le etichette in alto e in basso, fuori dalle curve
    for val, testo, col, va, dy in ((x + off, T['r1'], BLU, 'bottom', 0.45),
                                    (y - off, T['r2'], ARANCIO, 'top', -0.45)):
        ax1.annotate(testo, (2, float(val[:6].mean()) + dy), fontsize=10.5,
                     color=col, fontweight='bold', ha='left', va=va, zorder=6,
                     path_effects=[pe.withStroke(linewidth=3.4,
                                                 foreground='white')])
    ax1.set_title(T['a'], fontsize=11.5, pad=16)
    ax1.set_xlabel(T['xt'], fontsize=9.8)
    ax1.set_ylabel(T['yt'], fontsize=9.8)
    ax1.set_xlim(0, len(x) - 1)
    # margine in basso: senza, l'etichetta della seconda curva esce
    lo, hi = float((y - off).min()), float((x + off).max())
    ax1.set_ylim(lo - 0.9, hi + 0.5)
    ax1.tick_params(labelsize=8.8)
    for lato in ('top', 'right'):
        ax1.spines[lato].set_visible(False)
    corr_handle = Line2D([], [], color=GRIGIO, lw=0.9, ls='--')

    # ---------- (b) la matrice, la banda, il cammino ----------
    M = Dm[1:, 1:].copy()
    finito = np.isfinite(M)
    im = ax2.imshow(np.where(finito, M, np.nan), origin='lower',
                    cmap='Blues', aspect='equal', interpolation='nearest')
    # fuori dalla banda: grigio pieno, cosi' la banda e' la figura
    ax2.imshow(np.where(finito, np.nan, 1.0), origin='lower',
               cmap=matplotlib.colors.ListedColormap(['#eceff1']),
               aspect='equal', interpolation='nearest')

    n = len(x)
    d = np.arange(n)
    ax2.plot(d, d, color=GRIGIO, lw=1.4, ls='--', zorder=4)
    for s in (+W, -W):
        ax2.plot(d, d + s, color=VERDE, lw=1.6, zorder=5)
    ax2.plot(cammino[:, 1] - 1, cammino[:, 0] - 1, color=ROSSO, lw=2.4,
             zorder=6, path_effects=ALONE)

    ax2.set_title(T['b'], fontsize=11.5, pad=16)
    ax2.set_xlabel(T['yj'], fontsize=9.8)
    ax2.set_ylabel(T['xi'], fontsize=9.8)
    ax2.set_xlim(0, n - 1)
    ax2.set_ylim(0, n - 1)
    ax2.tick_params(labelsize=8.8)
    cb = fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.03)
    cb.set_label(T['costo'], fontsize=9)
    cb.ax.tick_params(labelsize=8)

    path_handle = Line2D([], [], color=ROSSO, lw=2.4)
    diag_handle = Line2D([], [], color=GRIGIO, lw=1.4, ls='--')
    banda_handle = Line2D([], [], color=VERDE, lw=1.6)

    # rettangolo che marca, sulla matrice intera, la zona ripresa in (c) --
    # senza questo riferimento lo zoom sarebbe uno spezzone scollegato dal
    # resto, e non si capirebbe da dove viene.
    riquadro = plt.Rectangle((j0, i0), j1 - j0, i1 - i0, fill=False,
                             edgecolor='black', lw=1.3, zorder=8)
    ax2.add_patch(riquadro)
    ax2.annotate(T['zoom'], (j0, i1), xytext=(6, 6),
                textcoords='offset points', fontsize=8.2,
                fontweight='bold', zorder=9,
                path_effects=[pe.withStroke(linewidth=3.0,
                                            foreground='white')])

    # ---------- (c) lo stesso disegno, ma solo sul riquadro ----------
    ax3.imshow(np.where(finito, M, np.nan), origin='lower', cmap='Blues',
              aspect='equal', interpolation='nearest',
              vmin=float(np.nanmin(M[np.isfinite(M)])),
              vmax=float(np.nanmax(M[np.isfinite(M)])))
    ax3.imshow(np.where(finito, np.nan, 1.0), origin='lower',
              cmap=matplotlib.colors.ListedColormap(['#eceff1']),
              aspect='equal', interpolation='nearest')
    ax3.plot(d, d, color=GRIGIO, lw=1.6, ls='--', zorder=4)
    for s in (+W, -W):
        ax3.plot(d, d + s, color=VERDE, lw=2.0, zorder=5)
    ax3.plot(cammino[:, 1] - 1, cammino[:, 0] - 1, color=ROSSO, lw=3.0,
             zorder=6, path_effects=ALONE, marker='o', markersize=3.0,
             markevery=1)
    ax3.set_xlim(j0, j1 - 1)
    ax3.set_ylim(i0, i1 - 1)
    ax3.set_title(T['c'], fontsize=11.5, pad=16)
    ax3.set_xlabel(T['yj'], fontsize=9.8)
    ax3.tick_params(labelsize=8.8)
    for spina in ax3.spines.values():
        spina.set_edgecolor('black')
        spina.set_linewidth(1.3)

    fig.legend([corr_handle, path_handle, diag_handle, banda_handle],
              [T['corr'], T['cam'], T['diag'], T['banda'] % W],
              loc='lower center', ncol=4, bbox_to_anchor=(0.5, 0.0),
              fontsize=9.6, framealpha=0.95, edgecolor='#b0bec5',
              columnspacing=1.6, handletextpad=0.7)

    fig.tight_layout()
    fig.subplots_adjust(top=0.87, bottom=0.22)
    nome = 'fig_dtw_spiegazione' + ('_en' if a.lingua == 'en' else '')
    dst = os.path.join(QUI, 'tesi', 'figure', nome + '.png')
    fig.savefig(dst, dpi=190, facecolor='white')
    plt.close(fig)
    print(f'salvata in {os.path.relpath(dst, QUI)}')

    # ------------------------------------------------------------- scheda
    with open(dst.replace('.png', '.txt'), 'w', encoding='utf-8') as f:
        f.write(f"""FIGURA — CHE COSA FA IL DTW, E CHE COSA FA LA BANDA
File: {nome}.png
Prodotta da: pipeline/figura_dtw.py
Comando:     python pipeline/figura_dtw.py --lingua {a.lingua} --grandezza {a.grandezza}

CHE COSA SI VEDE
  (a) due riprese di caduta vere, la stessa grandezza, z-scored e ricampionate
      a 200 campioni come fa la selezione. Le tratteggiate sono le
      corrispondenze del cammino DTW, una ogni sette passi.
  (b) la matrice dei costi cumulati. In grigio cio' che la banda esclude, in
      tratteggio la diagonale --- cioe' il confronto uno-a-uno che farebbe una
      distanza euclidea --- e in rosso il cammino trovato. Il riquadro nero
      segna la zona dove il cammino si allontana di piu' dalla diagonale, ed
      e' quella ripresa ingrandita in (c).
  (c) lo stesso disegno di (b), ma solo sul riquadro segnato: alla scala
      intera la banda (larga appena {W} campioni su 200) e il cammino si
      confondono con la diagonale; qui si vedono distinti.
  La legenda con tutti gli elementi dei tre pannelli sta sotto la figura,
  non sovrapposta ai dati.

E' una figura METODOLOGICA: spiega il criterio, non riporta un risultato.

NUMERI DI QUESTA ESECUZIONE
  grandezza          {a.grandezza}
  camera             {a.camera}
  riprese di caduta  {len(curve)}
  scarto fra i picchi {scarto} campioni
  banda              |i-j| <= {W}   (src/dtw.py, FINESTRA_WARPING)
  passi del cammino  {len(cammino)}, di cui {fuori} sul bordo della banda
  distanza           {mia:.6f}  (coincide con src.dtw a meno di 1e-9)

CONTROLLO ESEGUITO
  src/dtw.py non conserva la matrice: tiene due righe. Qui la ricorsione e'
  ripetuta per intero e lo script verifica che la distanza coincida con quella
  di src.dtw, altrimenti si ferma. Senza, la figura mostrerebbe un
  allineamento diverso da quello che decide la selezione.

DA METTERE IN LATEX
-------------------
\\begin{{figure}}[htbp]
\\centering
\\includegraphics[width=\\textwidth]{{figure/{nome}.png}}
\\caption{{Che cosa il \\emph{{Dynamic Time Warping}} allinea, e che cosa il
vincolo di banda impedisce. A sinistra due riprese di caduta di UP-Fall,
la stessa grandezza, normalizzate e ricampionate come fa la procedura di
selezione: hanno la stessa forma ma raggiungono il picco a {scarto} campioni
di distanza, e le tratteggiate sono le corrispondenze che il DTW stabilisce.
Al centro la matrice dei costi cumulati: la diagonale tratteggiata e' il
confronto uno-a-uno che una distanza punto per punto imporrebbe, la regione
grigia e' quella che il vincolo $|i-j|\\leq {W}$ esclude, e in rosso il cammino
di costo minimo; il riquadro nero segna dove il cammino si allontana di piu'
dalla diagonale. A destra lo stesso riquadro ingrandito, perche' alla scala
dell'intera matrice una banda larga {W} campioni su 200 e' troppo sottile per
distinguerla dal cammino. Le curve e il cammino sono quelli veri; la figura
spiega il criterio e non riporta un risultato. Prodotta da
\\texttt{{pipeline/figura\\_dtw.py}}.}}
\\label{{fig:dtw}}
\\end{{figure}}
""")
    print(f'scheda in {os.path.relpath(dst.replace(".png", ".txt"), QUI)}')


if __name__ == '__main__':
    main()
