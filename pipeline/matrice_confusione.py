# -*- coding: utf-8 -*-
"""
La matrice di confusione delle run gia' fatte, senza riaddestrare.

Perche' si puo'. `addestra.py` salva i punteggi di ogni finestra di test di
ogni fold in `risultati/addestramento/punteggi_*.npz`: 1,5 MB in tutto, ed e'
la ragione per cui questa tabella costa secondi invece di dieci
addestramenti. I punteggi sono quelli del **test** di ciascun fold, mai del
validation, quindi la matrice e' aggregata su dieci soggetti ciascuno dei
quali non era in addestramento quando e' stato valutato.

Che cosa conta, e che cosa NO. Le celle sono **finestre**, non eventi. Un
sistema installato non produce finestre ma allarmi, e le due contabilita'
differiscono di un fattore misurato in 44,8 ([DEC-017]): questa matrice
descrive il classificatore, non il sistema. Per il sistema servono le
metriche di evento, che si ottengono dalle sessioni.

Uso:
    python pipeline/matrice_confusione.py
    python pipeline/matrice_confusione.py --run foresta_tre_classi_DTWH_cam1_L22
    python pipeline/matrice_confusione.py --figura tesi/figure/fig_confusione.png
"""

import argparse
import glob
import os
import sys

import numpy as np

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RADICE not in sys.path:
    sys.path.insert(0, RADICE)

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

DIR = os.path.join(RADICE, 'risultati', 'addestramento')
dec = lambda v, n=3: f'{v:.{n}f}'.replace('.', ',')


def raccogli(percorso):
    """Tutti i fold di test messi insieme: (punteggi, etichette, per_fold)."""
    d = np.load(percorso, allow_pickle=True)
    P, Y, per_fold = [], [], []
    i = 0
    while f'p_test_{i}' in d.files:
        p, y = d[f'p_test_{i}'], d[f'y_test_{i}']
        P.append(p)
        Y.append(y)
        sog = (d['fold_test'][i] if 'fold_test' in d.files else i)
        per_fold.append((str(sog), p, y))
        i += 1
    return np.concatenate(P), np.concatenate(Y), per_fold


def conta(p, y, soglia):
    prev = p >= soglia
    vp = int(((prev == 1) & (y == 1)).sum())
    fp = int(((prev == 1) & (y == 0)).sum())
    fn = int(((prev == 0) & (y == 1)).sum())
    vn = int(((prev == 0) & (y == 0)).sum())
    return vp, fp, fn, vn


def metriche(vp, fp, fn, vn, beta=2.0):
    rec = vp / max(vp + fn, 1)
    pre = vp / max(vp + fp, 1)
    b2 = beta * beta
    f = ((1 + b2) * pre * rec / max(b2 * pre + rec, 1e-12)) if (pre + rec) else 0.0
    spec = vn / max(vn + fp, 1)
    return rec, pre, f, spec


def stampa(nome, p, y, per_fold, soglia):
    vp, fp, fn, vn = conta(p, y, soglia)
    rec, pre, f2, spec = metriche(vp, fp, fn, vn)
    n = len(y)
    print()
    print('=' * 74)
    print(f'MATRICE DI CONFUSIONE — {nome}')
    print('=' * 74)
    print(f'  {n:,} finestre di test, {int(y.sum()):,} positive '
          f'({100*y.mean():.1f}%), soglia {dec(soglia,2)}')
    print(f'  aggregate su {len(per_fold)} fold LOSO: ogni finestra e valutata')
    print(f'  da un modello che non aveva visto il suo soggetto')
    print()
    print('                        PREVISTO')
    print('                   caduta      non caduta')
    print('               +-----------+-----------+')
    print(f'  VERO caduta  |  {vp:6,}   |  {fn:6,}   |   {vp+fn:6,}')
    print(f'       non c.  |  {fp:6,}   |  {vn:6,}   |   {fp+vn:6,}')
    print('               +-----------+-----------+')
    print(f'                  {vp+fp:6,}      {fn+vn:6,}      {n:6,}')
    print()
    print(f'  richiamo    {dec(rec)}   ({vp:,} su {vp+fn:,} cadute prese)')
    print(f'  precisione  {dec(pre)}   ({fp:,} falsi allarmi su {vp+fp:,} segnalazioni)')
    print(f'  specificita {dec(spec)}')
    print(f'  F2          {dec(f2)}   (il richiamo pesa il quadruplo)')

    print()
    print('  per fold (il soggetto tenuto fuori):')
    print('    %-10s %7s %7s %7s %7s %7s' % ('soggetto', 'fin.', 'pos.', 'rich.', 'prec.', 'F2'))
    f2s = []
    for sog, pf, yf in per_fold:
        a, b, c, dd = conta(pf, yf, soglia)
        r, pr, ff, _ = metriche(a, b, c, dd)
        f2s.append(ff)
        print('    %-10s %7d %7d %7s %7s %7s'
              % (sog, len(yf), int(yf.sum()), dec(r), dec(pr), dec(ff)))
    print('    %-10s %7s %7s %7s %7s %7s'
          % ('media', '', '', '', '', dec(float(np.mean(f2s)))))
    print('    %-10s %7s %7s %7s %7s %7s'
          % ('dev.st.', '', '', '', '', dec(float(np.std(f2s)))))
    return vp, fp, fn, vn


def figura(dati, dove, soglia):
    """Le matrici affiancate, per la tesi."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, assi = plt.subplots(1, len(dati), figsize=(5.2 * len(dati), 4.4))
    if len(dati) == 1:
        assi = [assi]
    for ax, (nome, vp, fp, fn, vn) in zip(assi, dati):
        M = np.array([[vp, fn], [fp, vn]], float)
        Mn = M / M.sum(axis=1, keepdims=True)
        ax.imshow(Mn, cmap='Blues', vmin=0, vmax=1)
        for i in range(2):
            for j in range(2):
                ax.text(j, i, f'{int(M[i, j]):,}\n{100*Mn[i, j]:.1f}%',
                        ha='center', va='center', fontsize=11,
                        color='white' if Mn[i, j] > .5 else '#222')
        ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
        ax.set_xticklabels(['caduta', 'non caduta'])
        ax.set_yticklabels(['caduta', 'non caduta'])
        ax.set_xlabel('previsto'); ax.set_ylabel('vero')
        rec, pre, f2, _ = metriche(vp, fp, fn, vn)
        ax.set_title(f'{nome}\nF2 {dec(f2)}   richiamo {dec(rec)}   '
                     f'precisione {dec(pre)}', fontsize=10)
    fig.suptitle(f'Finestre di test aggregate sui dieci fold LOSO, '
                 f'soglia {dec(soglia,2)}', fontsize=11)
    fig.tight_layout()
    os.makedirs(os.path.dirname(dove), exist_ok=True)
    fig.savefig(dove, dpi=150)
    print(f'\n  figura scritta in {dove}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', nargs='*', default=['foresta_tre_classi_DTWH_cam1_L22',
                                                 'foresta_tre_classi_DTW_cam1_L22'])
    ap.add_argument('--soglia', type=float, default=0.5)
    ap.add_argument('--figura', default=None)
    ap.add_argument('--elenco', action='store_true')
    a = ap.parse_args()

    if a.elenco:
        for f in sorted(glob.glob(os.path.join(DIR, 'punteggi_*.npz'))):
            print('  ', os.path.basename(f)[10:-4])
        return

    dati = []
    for nome in a.run:
        p = os.path.join(DIR, f'punteggi_{nome}.npz')
        if not os.path.exists(p):
            print(f'manca {p}')
            continue
        P, Y, pf = raccogli(p)
        vp, fp, fn, vn = stampa(nome, P, Y, pf, a.soglia)
        dati.append((nome.replace('_', ' '), vp, fp, fn, vn))

    if a.figura and dati:
        figura(dati, os.path.join(RADICE, a.figura), a.soglia)


if __name__ == '__main__':
    main()
