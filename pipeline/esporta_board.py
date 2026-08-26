"""
Prepara il pacchetto da copiare sulla board.

Cosa esporta
------------
    modello.pkl        foresta addestrata su TUTTI i soggetti
    scaler.pkl         parametri di normalizzazione, colonne e maschera log1p
    metadata.json      configurazione completa, per tracciabilita'
    parita.npz         200 finestre con le predizioni calcolate sul PC

Perche' su tutti i soggetti
---------------------------
I modelli per fold della validazione incrociata servono a STIMARE la
prestazione, non a essere installati: ciascuno ha visto otto soggetti su dieci.
Il modello che si installa li vede tutti. E' la correzione di una discrepanza
gia' osservata nel progetto precedente, dove il recall fuori linea (2/5) era
piu' basso di quello di campo (4/5) sugli stessi eventi proprio perche' fuori
linea si mediavano modelli addestrati su meno dati.

La prova di parita'
-------------------
`parita.npz` contiene finestre gia' normalizzate e le probabilita' che il PC
produce su di esse. Il primo comando da eseguire sulla board le riconfronta: se
divergono oltre 1e-6, le versioni di scikit-learn non sono compatibili e
qualunque misura successiva non e' valida. E' un controllo di trenta secondi
che evita di scoprire il problema dopo dodici ore di registrazione.

Il compito
----------
Il positivo e' l'EVENTO, cioe' la transizione (`fall` nella tassonomia
OmniFall), non lo stato a terra. E' la conclusione del lavoro: sul compito
evento i falsi allarmi sulle persone distese volontariamente sono lo 0,0%,
contro il 12,5% del compito stato.

Uso:
    python pipeline/esporta_board.py
    python pipeline/esporta_board.py --feature A3 --compito allarme
"""

import argparse
import json
import os
import platform
import sys
from datetime import datetime

import numpy as np
import pandas as pd

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

import config
from src.dati import (ASIMMETRICHE, COL_FOTOGRAMMA, COL_POSA, COL_RIPRESA,
                      COL_SOGGETTO, FEATURE, Scaler, carica, feature_dtw)
from src.modelli import Foresta

dec = lambda v, n=3: f'{v:.{n}f}'.replace('.', ',')

COMPITI = {'evento': (1,), 'stato': (2,), 'allarme': (1, 2)}


def finestre(df, colonne, positive, k_min=5):
    L, passo, step = (config.LUNGHEZZA_FINESTRA, config.PASSO_FINESTRA,
                      config.FRAME_STEP)
    X, y = [], []
    for _, g in df.groupby([COL_SOGGETTO, COL_RIPRESA], sort=True):
        g = g.sort_values(COL_FOTOGRAMMA)
        if COL_POSA in g.columns:
            g = g[g[COL_POSA] == 1]
        if step > 1:
            g = g.iloc[::step]
        if len(g) < L:
            continue
        v = g[list(colonne)].to_numpy(np.float32)
        cls = g['classe_omnifall'].to_numpy()
        for i in range(0, len(g) - L + 1, passo):
            X.append(v[i:i + L])
            y.append(int(np.isin(cls[i:i + L], positive).sum() >= k_min))
    return np.stack(X), np.array(y, int)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='feature_v2_omnifall.csv')
    ap.add_argument('--feature', default='DTW')
    ap.add_argument('--compito', default='evento', choices=list(COMPITI))
    ap.add_argument('--camera', type=int, default=1)
    ap.add_argument('--soglia', type=float, default=0.5)
    ap.add_argument('--n-alberi', type=int, default=config.N_ALBERI)
    ap.add_argument('--out', default='deploy_board')
    a = ap.parse_args()

    import joblib

    colonne = (feature_dtw() if a.feature.upper() == 'DTW'
               else FEATURE[a.feature if a.feature in FEATURE else a.feature.upper()])
    df = carica(a.csv, camera=a.camera)
    if 'classe_omnifall' not in df.columns:
        sys.exit('il CSV non ha `classe_omnifall`: eseguire mappa_omnifall.py')

    print('=' * 78)
    print(f'PACCHETTO PER LA BOARD — {a.feature} ({len(colonne)} grandezze), '
          f'compito «{a.compito}»')
    print('=' * 78)

    X, y = finestre(df, colonne, COMPITI[a.compito])
    sc = Scaler(colonne).fit(df)
    Xs = sc.transform(X)

    print(f'finestre        {len(X):,}   positive {int(y.sum()):,} '
          f'({100*y.mean():.1f}%)')
    print(f'soggetti        {df[COL_SOGGETTO].nunique()}   camera {a.camera}')

    mod = Foresta(n_classi=2, n_alberi=a.n_alberi).addestra(Xs, y)
    p = mod.probabilita(Xs)[:, 1]
    print(f'alberi          {a.n_alberi}   nodi totali {mod.n_parametri:,}')
    print(f'in-sample       allarme sul {100*(p >= a.soglia).mean():.1f}% '
          f'delle finestre (atteso ~{100*y.mean():.1f}%)')

    out = os.path.join(RADICE, a.out)
    os.makedirs(out, exist_ok=True)
    joblib.dump(mod._m, os.path.join(out, 'modello.pkl'))
    joblib.dump({'scaler': sc._s, 'colonne': list(colonne),
                 'maschera_log1p': sc.maschera.tolist()},
                os.path.join(out, 'scaler.pkl'))

    # ---- campioni di parita' ----
    rng = np.random.default_rng(config.SEME)
    pos = np.where(y == 1)[0]
    neg = np.where(y == 0)[0]
    idx = np.concatenate([rng.choice(pos, min(100, len(pos)), replace=False),
                          rng.choice(neg, min(100, len(neg)), replace=False)])
    np.savez_compressed(os.path.join(out, 'parita.npz'),
                        X=Xs[idx].astype(np.float32), p_attesa=p[idx],
                        y=y[idx])

    meta = {
        'creato': datetime.now().isoformat(timespec='seconds'),
        'compito': a.compito,
        'positivo': {'evento': 'la transizione: l atto di cadere',
                     'stato': 'essere a terra dopo una caduta',
                     'allarme': 'transizione oppure stato'}[a.compito],
        'modello': 'foresta casuale su feature aggregate della finestra',
        'n_alberi': a.n_alberi, 'n_nodi': mod.n_parametri,
        'aggregazione': 'media, dev.std, min, max, primo, ultimo -> '
                        '6 statistiche per grandezza',
        'feature_set': a.feature, 'colonne': list(colonne),
        'n_colonne': len(colonne),
        'maschera_log1p': sc.maschera.tolist(),
        'lunghezza_finestra': config.LUNGHEZZA_FINESTRA,
        'passo_finestra': config.PASSO_FINESTRA,
        'frame_step_dataset': config.FRAME_STEP,
        'fps_assunti': config.FPS_ESERCIZIO,
        'durata_finestra_s': round(config.LUNGHEZZA_FINESTRA / config.FPS_ESERCIZIO, 3),
        'k_integrali': config.K_INTEGRALI,
        'riscaldamento_s': round(config.K_INTEGRALI / config.FPS_DATASET, 2),
        'soglia': a.soglia,
        'origine_soglia': 'dichiarata a priori. Il confronto fra sei regole di '
                          'selezione (EXP-010) mostra che sceglierla su un solo '
                          'soggetto di validazione aggiunge piu rumore di quanto '
                          'adattamento porti: deviazione 0,37 su [0,1].',
        'regola_decisione': {'persistenza_finestre': 5, 'sospensione_s': 30,
                             'nota': 'una raffica di finestre consecutive e UN '
                                     'allarme, non N. Fattore misurato 47,8.'},
        'camera': a.camera, 'n_soggetti': int(df[COL_SOGGETTO].nunique()),
        'n_finestre_train': int(len(X)), 'n_positive_train': int(y.sum()),
        'stimatore_posa': 'mediapipe 0.10.11, solutions, una persona',
        'risoluzione': '640x480 (ridimensionare prima di MediaPipe)',
        'versioni_pc': {'python': platform.python_version(),
                        'numpy': np.__version__,
                        'pandas': pd.__version__},
        'nota_parita': 'Le predizioni sulla board devono coincidere con '
                       'p_attesa in parita.npz entro 1e-6. Se divergono, le '
                       'versioni di scikit-learn non sono compatibili e nessuna '
                       'misura successiva e valida.',
    }
    with open(os.path.join(out, 'metadata.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print()
    print(f'riscaldamento   {meta["riscaldamento_s"]} s '
          f'(buffer degli integrali, K = {config.K_INTEGRALI})')
    print(f'finestra        {meta["durata_finestra_s"]} s '
          f'({config.LUNGHEZZA_FINESTRA} campioni a {config.FPS_ESERCIZIO:.0f} fps)')
    print()
    print(f'scritto in {a.out}/:')
    for f_ in ('modello.pkl', 'scaler.pkl', 'metadata.json', 'parita.npz'):
        p_ = os.path.join(out, f_)
        print(f'   {f_:<16} {os.path.getsize(p_)/1024:8.1f} KB')


if __name__ == '__main__':
    main()
