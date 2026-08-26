"""
Addestra su UP-Fall, misura su UR-Fall. Con e senza le grandezze dinamiche.

La domanda
----------
Sul modello schierato -- A3 a dieci colonne, senza integrali -- UR-Fall da'
PR-AUC 0,169 contro una prevalenza di 0,094: un guadagno di 1,8x, cioe' quasi
nulla. E tutti i suoi falsi allarmi si concentrano su un tipo solo di negativo:
l'11,6% delle finestre di persona distesa VOLONTARIAMENTE, contro lo 0,0% di
tutto il resto.

L'ipotesi da verificare e' che quel modello non abbia modo di distinguerle,
perche' cio' che le separa e' la DINAMICA e lui non ce l'ha. Misurato su
UP-Fall, fra caduta e sdraiarsi volontario il rapporto delle mediane e':

    velocita' del bacino   30x       escursione del tronco   42x
    percorso                33x       discesa                139x

ma quelle grandezze sono integrali, e A3 ha solo derivate istantanee, la cui
autocorrelazione fra fotogrammi consecutivi e' 0,14 -- rumore.

Se l'ipotesi e' giusta, aggiungere gli integrali deve abbattere quell'11,6% e
alzare il guadagno su UR-Fall. Se e' sbagliata, non cambia nulla e il problema
sta altrove.

Il confronto e' quindi fra rappresentazioni, a parita' di tutto il resto:
stesso modello, stesso addestramento, stesso insieme di verifica.

Cosa NON si fa
--------------
Non si tara nessuna soglia su UR-Fall. La soglia resta quella dichiarata a
priori, 0,5. Il valore ottenibile ritarando sul dominio di arrivo si riporta
separatamente e si chiama **soglia oracolo**: richiede le etichette del dominio
target, che in esercizio non si hanno.

Uso:
    python pipeline/valuta_esterno.py
    python pipeline/valuta_esterno.py --modello gru
"""

import argparse
import json
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

os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '3')

import config
from src.dati import (FEATURE, COL_LABEL, COL_POSA, COL_RIPRESA,
                      COL_FOTOGRAMMA, Scaler, carica, costruisci_finestre,
                      feature_dtw)
from src.etichettatura import etichetta_finestra
from src.modelli import costruisci
from src.valutazione import metriche, probabilita_allarme

dec = lambda v, n=3: f'{v:.{n}f}'.replace('.', ',')


def pr_auc(y, p):
    y = np.asarray(y).astype(int)[np.argsort(-np.asarray(p, float))]
    tp, fp = np.cumsum(y), np.cumsum(1 - y)
    prec = tp / np.maximum(tp + fp, 1)
    rec = tp / max(y.sum(), 1)
    return float((prec * np.diff(np.concatenate([[0.0], rec]))).sum())


def roc_auc(y, p):
    y = np.asarray(y).astype(int)
    n1 = int(y.sum())
    n0 = len(y) - n1
    if n0 == 0 or n1 == 0:
        return float('nan')
    r = pd.Series(np.asarray(p, float)).rank().to_numpy()
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def finestre_esterne(df, colonne, modo, frame_step, **soglie):
    """
    Come `costruisci_finestre`, ma porta anche la quota di fotogrammi che sono
    negativi difficili. Serve a misurare i falsi allarmi separatamente su
    quelli e su tutto il resto.
    """
    L, passo = config.LUNGHEZZA_FINESTRA, config.PASSO_FINESTRA
    ha_duro = 'disteso_volontario' in df.columns
    X, y, duro = [], [], []
    for _, g in df.groupby(COL_RIPRESA, sort=True):
        g = g.sort_values(COL_FOTOGRAMMA)
        if COL_POSA in g.columns:
            g = g[g[COL_POSA] == 1]
        if frame_step > 1:
            g = g.iloc[::frame_step]
        if len(g) < L:
            continue
        v = g[list(colonne)].to_numpy(np.float32)
        lab = g[COL_LABEL].to_numpy(np.int8)
        dv = (g['disteso_volontario'].to_numpy() if ha_duro
              else np.zeros(len(g), int))
        for i in range(0, len(g) - L + 1, passo):
            fin = lab[i:i + L]
            e = etichetta_finestra(fin, modo, **soglie)
            if e is None:
                continue
            X.append(v[i:i + L])
            y.append(int(e > 0))
            duro.append(float(dv[i:i + L].mean()))
    if not X:
        raise ValueError('nessuna finestra costruita su UR-Fall')
    return np.stack(X), np.array(y, np.int8), np.array(duro)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--modello', default='foresta')
    ap.add_argument('--modo', default='caduta',
                    help='caduta = positivo se transizione O stato a terra')
    ap.add_argument('--camera', type=int, default=1)
    ap.add_argument('--frame-step-ur', type=int, default=3,
                    help='UR-Fall gira a 30 fps: 3 lo porta a 10, il piu '
                         'vicino ai 9 del modello')
    ap.add_argument('--soglia', type=float, default=0.5)
    a = ap.parse_args()

    up = carica('feature_v2.csv', camera=a.camera)
    ur = pd.read_csv(os.path.join(config.FEATURE_DIR, 'feature_urfall.csv'))

    insiemi = [('A3base  senza integrali', FEATURE['A3base']),
               ('A3      con integrali', FEATURE['A3']),
               ('DTW     sottoinsieme scelto', feature_dtw())]

    print('=' * 100)
    print(f'ADDESTRATO SU UP-FALL, MISURATO SU UR-FALL — {a.modello}, '
          f'modo {a.modo}, soglia {dec(a.soglia, 2)} dichiarata a priori')
    print('=' * 100)
    print(f"{'rappresentazione':<30}{'n':>5}{'PR-AUC':>9}{'guadagno':>10}"
          f"{'ROC-AUC':>9}{'F2':>8}{'recall':>8}"
          f"{'allarme su DIFFICILI':>22}{'su facili':>11}")
    print('-' * 100)

    esito = []
    for nome, colonne in insiemi:
        mancanti = [c for c in colonne if c not in ur.columns]
        if mancanti:
            print(f'{nome:<30}  colonne assenti in UR-Fall: {mancanti[:3]}')
            continue

        Xtr, ytr, _, _, _ = costruisci_finestre(up, colonne, a.modo)
        ok = ytr >= 0
        sc = Scaler(colonne).fit(up)
        Xtr = sc.transform(Xtr[ok])
        ytr = ytr[ok].astype(int)

        Xte, yte, duro = finestre_esterne(ur, colonne, a.modo, a.frame_step_ur)
        Xte = sc.transform(Xte)

        m = costruisci(a.modello, (Xtr.shape[1], Xtr.shape[2]), 2)
        m.addestra(Xtr, ytr)
        p = probabilita_allarme(m.probabilita(Xte))

        prev = float(yte.mean())
        pa, ra = pr_auc(yte, p), roc_auc(yte, p)
        met = metriche(yte, p, a.soglia)
        m_duro = (yte == 0) & (duro >= 0.5)
        m_fac = (yte == 0) & (duro < 0.5)
        fa_d = float((p[m_duro] >= a.soglia).mean()) if m_duro.any() else float('nan')
        fa_f = float((p[m_fac] >= a.soglia).mean()) if m_fac.any() else float('nan')

        print(f"{nome:<30}{len(colonne):>5}{dec(pa):>9}"
              f"{dec(pa/max(prev,1e-9), 1) + 'x':>10}{dec(ra):>9}"
              f"{dec(met['fbeta']):>8}{dec(met['recall']):>8}"
              f"{dec(100*fa_d, 1) + '%  (n=' + str(int(m_duro.sum())) + ')':>22}"
              f"{dec(100*fa_f, 1) + '%':>11}")

        esito.append({'rappresentazione': nome.strip(), 'n_colonne': len(colonne),
                      'finestre_ur': int(len(yte)), 'prevalenza': prev,
                      'pr_auc': pa, 'guadagno': pa / max(prev, 1e-9),
                      'roc_auc': ra, 'f2': met['fbeta'],
                      'recall': met['recall'], 'precision': met['precision'],
                      'allarme_difficili': fa_d, 'n_difficili': int(m_duro.sum()),
                      'allarme_facili': fa_f})

    print('-' * 100)
    print('guadagno = PR-AUC diviso prevalenza. 1x significa nessuna capacita '
          'discriminativa.')
    print('DIFFICILI = finestre negative di persona distesa volontariamente; '
          'facili = tutti gli altri negativi.')

    out = os.path.join(config.RISULTATI_DIR, 'esterno')
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, f'urfall_{a.modello}_{a.modo}.json'), 'w',
              encoding='utf-8') as f:
        json.dump({'modello': a.modello, 'modo': a.modo, 'soglia': a.soglia,
                   'frame_step_ur': a.frame_step_ur, 'config': esito},
                  f, indent=2, ensure_ascii=False)
    print(f"\nsalvato: risultati/esterno/urfall_{a.modello}_{a.modo}.json")


if __name__ == '__main__':
    main()
