"""
Sceglie il sottoinsieme di grandezze da dare alla rete.

Produce
-------
    classifica_dtw.csv           punteggio per grandezza e per camera
    dtw_cam1_vs_cam2.png         il grafico che decide: chi sta sulla
                                 diagonale regge da entrambi i punti di vista
    curve/<grandezza>.png        sovrapposizione caduta contro ADL, per camera

Il grafico cam1 contro cam2 e' la novita' rispetto all'analisi precedente, ed
e' quello che risponde alla domanda posta: non «quale grandezza separa meglio»
ma «quale separa da entrambe le viste». Una grandezza sulla diagonale in alto
a destra funziona sempre; una lontana dalla diagonale funziona da una vista
sola, ed e' quella che in installazione produce il crollo misurato al
cambio di inquadratura.

Uso:
    python pipeline/analisi_dtw.py --csv feature_prova.csv
    python pipeline/analisi_dtw.py --csv feature.csv --top 12
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import config
from src.dtw import classifica, curve_per_ripresa, ricampiona
from src.geometry import NOMI

ACC, ROSSO, VERDE, GRIGIO = '#0E6E7E', '#A0303C', '#1D6B4F', '#5A6773'
plt.rcParams.update({'font.size': 9, 'axes.spines.top': False,
                     'axes.spines.right': False, 'figure.facecolor': 'white',
                     'savefig.facecolor': 'white'})


def virgola(ax, asse='both'):
    f = matplotlib.ticker.FuncFormatter(lambda v, _: f'{v:g}'.replace('.', ','))
    if asse in ('x', 'both'):
        ax.xaxis.set_major_formatter(f)
    if asse in ('y', 'both'):
        ax.yaxis.set_major_formatter(f)


def seleziona(cl: pd.DataFrame, df: pd.DataFrame, k: int, soglia: float):
    """
    Scorre la classifica dall'alto e tiene una grandezza solo se porta
    informazione che le gia' scelte non hanno.

    Perche' non basta prendere le prime k
    -------------------------------------
    Il DTW valuta ogni grandezza da sola: non sa nulla delle altre, quindi se
    lo stesso fenomeno fisico e' misurato in tre modi diversi lo premia tre
    volte. Su questi dati le prime tre della classifica -- A2_testa_rel_y,
    A2_angolo_tronco, A3_testa_rel_y -- sono correlate fra loro sopra 0,94:
    sono tutte «quanto e' verticale il tronco». Prendere le prime dodici
    significherebbe dare alla rete circa otto segnali distinti travestiti da
    dodici, e sprecare quattro posti che potrebbero portare informazione nuova.

    Il criterio e' quello classico della selezione avida: si aggiunge la
    prossima in classifica solo se la sua correlazione assoluta con TUTTE le
    gia' scelte sta sotto soglia. Chi viene escluso non e' inutile -- e'
    ridondante rispetto a una migliore di lui, e lo si dichiara.
    """
    corr = df[[c for c in cl.grandezza if c in df.columns]].corr().abs()
    scelte, scartate = [], []
    for g in cl.grandezza:
        if g not in corr.columns:
            continue
        blocco = [(s, corr.at[g, s]) for s in scelte if corr.at[g, s] > soglia]
        if blocco:
            s, r = max(blocco, key=lambda t: t[1])
            scartate.append((g, s, r))
        else:
            scelte.append(g)
            if len(scelte) == k:
                break
    return scelte, scartate


def grafico_camere(cl: pd.DataFrame, dst: str, scelte: 'set[str]'):
    """Punteggio cam1 contro cam2. La diagonale e' la robustezza."""
    fig, ax = plt.subplots(figsize=(8.6, 8.0))
    x, y = cl.punteggio_cam1.to_numpy(), cl.punteggio_cam2.to_numpy()
    lim = [min(x.min(), y.min()) * .95, max(x.max(), y.max()) * 1.05]

    ax.plot(lim, lim, ls='--', lw=1.2, color=GRIGIO, zorder=0)
    for _, r in cl.iterrows():
        buona = r.grandezza in scelte
        ax.scatter(r.punteggio_cam1, r.punteggio_cam2, s=70 if buona else 34,
                   color=VERDE if buona else ROSSO, alpha=.85,
                   edgecolor='white', linewidth=.8, zorder=3)
        ax.annotate(r.grandezza, (r.punteggio_cam1, r.punteggio_cam2),
                    textcoords='offset points', xytext=(6, 4),
                    fontsize=7.4 if buona else 6.6,
                    color='#20262D' if buona else GRIGIO)

    ax.set_xlim(lim); ax.set_ylim(lim); virgola(ax)
    ax.set_xlabel('separazione sulla Camera 1 (laterale)')
    ax.set_ylabel('separazione sulla Camera 2 (frontale rialzata)')
    ax.set_title('Quali grandezze reggono da entrambi i punti di vista',
                 fontsize=12.5, fontweight='bold', pad=12)
    fig.text(.5, .015,
             'Sulla diagonale: la grandezza separa allo stesso modo dalle due viste. '
             'Sotto la diagonale:\nfunziona di profilo e non dall\'alto, ed e\' il caso che '
             'produce il crollo al cambio di inquadratura.\n'
             f'In verde le {len(scelte)} scelte: punteggio minimo alto fra le due '
             f'camere, e non ridondanti fra loro.',
             ha='center', fontsize=8.4, color=GRIGIO)
    fig.tight_layout(rect=(0, .06, 1, 1))
    fig.savefig(dst, dpi=200, bbox_inches='tight')
    plt.close(fig)


def grafico_curve(df, grandezza: str, dst: str):
    """Sovrapposizione caduta contro ADL, una colonna per camera."""
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 3.8), sharey=True)
    for ax, cam in zip(axes, (1, 2)):
        g = curve_per_ripresa(df, grandezza, cam)
        for classe, colore, nome in (('caduta', ROSSO, 'caduta'),
                                     ('adl', ACC, 'attivita quotidiana')):
            C = [ricampiona((c - np.mean(c)) / (np.std(c) + 1e-9))
                 for c in g[classe]]
            if not C:
                continue
            M = np.vstack(C)
            m, s = M.mean(axis=0), M.std(axis=0)
            t = np.linspace(0, 100, len(m))
            ax.fill_between(t, m - s, m + s, color=colore, alpha=.18)
            ax.plot(t, m, color=colore, lw=2,
                    label=f'{nome} (n={len(C)})')
        ax.set_title(f'Camera {cam}', fontsize=10.5, fontweight='bold')
        ax.set_xlabel('tempo normalizzato (%)')
        ax.legend(frameon=False, fontsize=8)
        virgola(ax, 'y')
    axes[0].set_ylabel('valore normalizzato')
    fig.suptitle(grandezza, fontsize=12, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(dst, dpi=170, bbox_inches='tight')
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='feature.csv')
    ap.add_argument('--top', type=int, default=10,
                    help='quante grandezze selezionare')
    ap.add_argument('--curve', type=int, default=6,
                    help='per quante disegnare le curve')
    ap.add_argument('--max-corr', type=float, default=0.85,
                    help='correlazione massima ammessa fra due scelte')
    ap.add_argument('--escludi', default='',
                    help='grandezze da togliere dal bacino, separate da virgola')
    a = ap.parse_args()

    p = os.path.join(config.FEATURE_DIR, a.csv)
    if not os.path.exists(p):
        sys.exit(f'manca {p}: eseguire prima pipeline/estrai_feature.py')
    df = pd.read_csv(p)

    fuori = {s.strip() for s in a.escludi.split(',') if s.strip()}
    colonne = [c for c in NOMI if c in df.columns and c not in fuori]
    if fuori:
        print(f'escluse dal bacino su richiesta: {", ".join(sorted(fuori))}')
    camere = sorted(df.camera.unique())
    print('=' * 78)
    print(f'DTW — {len(colonne)} grandezze, camere {camere}, '
          f'{df.ripresa.nunique()} riprese, {df.soggetto.nunique()} soggetti')
    print('=' * 78)
    if len(camere) < 2:
        print('ATTENZIONE: una sola camera nei dati, il criterio robusto non '
              'e applicabile\n')

    cl = classifica(df, colonne, camere=tuple(camere))

    # La correlazione si misura sui soli fotogrammi con posa: sugli altri le
    # grandezze valgono zero per costruzione e sarebbero correlate fra loro
    # per un motivo che non ha nulla a che vedere con la dinamica del corpo.
    validi = df[df.ha_posa == 1] if 'ha_posa' in df.columns else df
    scelte, scartate = seleziona(cl, validi, a.top, a.max_corr)
    insieme = set(scelte)

    print(f"{'grandezza':24s}{'cam1':>9s}{'cam2':>9s}{'ROBUSTO':>10s}"
          f"{'divario':>9s}   scelta")
    print('-' * 78)
    escluse = {g: (s, r) for g, s, r in scartate}
    for _, r in cl.iterrows():
        if r.grandezza in insieme:
            nota = 'SI'
        elif r.grandezza in escluse:
            s, v = escluse[r.grandezza]
            nota = f'ridondante con {s} (r={f"{v:.2f}".replace(".", ",")})'
        else:
            nota = ''
        print(f"{r.grandezza:24s}{r.punteggio_cam1:9.3f}{r.punteggio_cam2:9.3f}"
              f"{r.robusto:10.3f}{r.divario:9.3f}   {nota}")

    out = os.path.join(config.RISULTATI_DIR, 'dtw')
    os.makedirs(os.path.join(out, 'curve'), exist_ok=True)
    cl.to_csv(os.path.join(out, 'classifica_dtw.csv'), index=False)

    if len(camere) >= 2:
        grafico_camere(cl, os.path.join(out, 'dtw_cam1_vs_cam2.png'), insieme)
        print(f'\ngrafico: {os.path.relpath(out, RADICE)}/dtw_cam1_vs_cam2.png')

    for g in scelte[:a.curve]:
        grafico_curve(df, g, os.path.join(out, 'curve', f'{g}.png'))
    print(f'curve: {a.curve} grandezze in {os.path.relpath(out, RADICE)}/curve/')

    # I numeri si formattano SEMPRE prima di entrare nella stringa: applicare
    # .replace('.', ',') a una f-string gia' composta trasforma in virgola
    # anche i punti che non sono decimali (l'indice «1.» dell'elenco, le
    # estensioni dei file). E' un errore che si nota tardi e male.
    dec = lambda v, n=3: f'{v:.{n}f}'.replace('.', ',')

    print(f'\nSOTTOINSIEME SCELTO ({len(scelte)}), '
          f'correlazione massima ammessa {dec(a.max_corr, 2)}:')
    for i, g in enumerate(scelte, 1):
        r = cl[cl.grandezza == g].iloc[0]
        print(f'  {i:2d}. {g:24s} robusto {dec(r.robusto)}')
    if scartate:
        print(f'\nescluse per ridondanza ({len(scartate)}):')
        for g, s, v in scartate:
            print(f'  {g:24s} ~ {s} (r={dec(v, 2)})')

    C = validi[scelte].corr().abs().values
    media = (C.sum() - len(scelte)) / (len(scelte) ** 2 - len(scelte))
    print(f'\ncorrelazione media fra le scelte: {dec(media)}')

    with open(os.path.join(out, 'scelte.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(scelte))


if __name__ == '__main__':
    main()
