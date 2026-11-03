"""
Tre definizioni del compito, misurate anche sul negativo difficile.

Il punto
--------
«Rilevare una caduta» non e' un compito solo. Con le etichette OmniFall se ne
possono definire tre, e sono diversi per positivo, prevalenza e difficolta':

    EVENTO    positivo = `fall`               l'atto di cadere
    STATO     positivo = `fallen`             essere a terra dopo una caduta
    ALLARME   positivo = `fall` OR `fallen`   quando il sistema deve suonare

Il negativo che conta e' sempre lo stesso e ora e' annotato: `lying` e
`lie_down`, cioe' persona distesa VOLONTARIAMENTE. Sono 21.322 fotogrammi in
UP-Fall, il 18,6%, e nelle nostre etichette valevano 0 come camminare.

Perche' misurarlo a parte
-------------------------
Un tasso di falsi allarmi complessivo nasconde il problema: i negativi facili
-- camminare, stare in piedi -- sono la grande maggioranza e sono banali. Su
UR-Fall abbiamo misurato 0,2% di allarmi sui negativi facili contro 35-50% sui
difficili. La media dei due non descrive nessuno dei due.

Il riferimento esterno: OmniFall riporta con VideoMAE (87 milioni di parametri)
F1 65,6% sull'evento e 41,0% sullo stato, e nota che i modelli multimodali
grandi confondono `fallen` con `lying` (29-31% F1). E' il problema aperto del
campo, non un difetto di questo progetto.

Uso:
    python pipeline/confronto_compiti.py
    python pipeline/confronto_compiti.py --modello gru --feature DTW
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
from src.dati import (COL_FOTOGRAMMA, COL_POSA, COL_RIPRESA, COL_SOGGETTO,
                      FEATURE, Scaler, carica, feature_dtw)
from src.modelli import costruisci
from src.valutazione import aggrega, metriche, probabilita_allarme

dec = lambda v, n=3: f'{v:.{n}f}'.replace('.', ',')

FALL, FALLEN = 1, 2
VOLONTARIO = (5, 6)          # lie_down, lying

COMPITI = {
    'evento':  (FALL,),
    'stato':   (FALLEN,),
    'allarme': (FALL, FALLEN),
}


def finestre(df, colonne, positive, k_min=5, valuta=None):
    """
    Finestre con positivo definito dalle classi OmniFall in `positive`.

    Ritorna anche la quota di fotogrammi `lying`/`lie_down` per finestra, che
    serve a separare i negativi difficili da quelli facili.
    """
    L, passo, step = (config.LUNGHEZZA_FINESTRA, config.PASSO_FINESTRA,
                      config.FRAME_STEP)
    # `valuta` e' l'insieme di classi con cui si GIUDICA, che non e'
    # necessariamente quello con cui si addestra: i tre compiti vanno
    # confrontati sulla stessa verita', altrimenti hanno prevalenze diverse
    # e le precision non sono commensurabili.
    if valuta is None:
        valuta = positive
    X, y, y_al, duro, sog = [], [], [], [], []
    for (s, _), g in df.groupby([COL_SOGGETTO, COL_RIPRESA], sort=True):
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
            f = cls[i:i + L]
            X.append(v[i:i + L])
            y.append(int(np.isin(f, positive).sum() >= k_min))
            y_al.append(int(np.isin(f, valuta).sum() >= k_min))
            duro.append(float(np.isin(f, VOLONTARIO).mean()))
            sog.append(s)
    if not X:
        raise ValueError('nessuna finestra')
    return (np.stack(X), np.array(y, np.int8), np.array(y_al, np.int8),
            np.array(duro), np.array(sog))


def loso(df, colonne, positive, modello, soglia, k_min=5, valuta=None):
    X, y, y_al, duro, sog = finestre(df, colonne, positive, k_min, valuta)
    soggetti = sorted(set(sog))
    ris, fa_d, fa_f = [], [], []
    for test in soggetti:
        m_te = sog == test
        m_tr = ~m_te
        sc = Scaler(colonne).fit(df[df[COL_SOGGETTO] != test])
        mod = costruisci(modello, (X.shape[1], X.shape[2]), 2)
        mod.addestra(sc.transform(X[m_tr]), y[m_tr].astype(int))
        p = probabilita_allarme(mod.probabilita(sc.transform(X[m_te])))
        # si valuta sull'etichetta di allarme, non su quella del compito
        ris.append(metriche(y_al[m_te], p, soglia))
        yt, dt = y_al[m_te], duro[m_te]
        md, mf = (yt == 0) & (dt >= 0.5), (yt == 0) & (dt < 0.5)
        if md.any():
            fa_d.append(float((p[md] >= soglia).mean()))
        if mf.any():
            fa_f.append(float((p[mf] >= soglia).mean()))
    return ris, float(np.mean(fa_d)) if fa_d else float('nan'), \
        float(np.mean(fa_f)) if fa_f else float('nan'), y, y_al, duro


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='feature_v2_omnifall.csv')
    ap.add_argument('--modello', default='foresta')
    ap.add_argument('--feature', default='DTW')
    ap.add_argument('--camera', type=int, default=1)
    ap.add_argument('--soglia', type=float, default=0.5)
    ap.add_argument('--valuta-sul-compito', action='store_true',
                    help='valuta ogni compito sulla propria etichetta invece '
                         'che su quella di allarme: riproduce il '
                         'comportamento precedente, in cui le tre prevalenze '
                         'erano diverse e gli F2 non confrontabili')
    a = ap.parse_args()

    colonne = (feature_dtw() if a.feature.upper() == 'DTW'
               else FEATURE[a.feature if a.feature in FEATURE else a.feature.upper()])
    df = carica(a.csv, camera=a.camera)
    if 'classe_omnifall' not in df.columns:
        sys.exit(f'{a.csv} non ha `classe_omnifall`: '
                 f'eseguire prima pipeline/mappa_omnifall.py')

    print('=' * 96)
    print(f'TRE DEFINIZIONI DEL COMPITO — {a.modello}, {a.feature} '
          f'({len(colonne)} grandezze), camera {a.camera}, LOSO su '
          f'{df[COL_SOGGETTO].nunique()} soggetti, soglia {dec(a.soglia, 2)}')
    print('=' * 96)
    print(f"{'compito':<10}{'positivo':<22}{'prevalenza':>11}{'F2':>17}"
          f"{'recall':>8}{'prec.':>8}{'allarme DIFFICILI':>20}{'facili':>9}")
    print('-' * 96)

    esito = []
    for nome, positive in COMPITI.items():
        valuta = None if a.valuta_sul_compito else COMPITI['allarme']
        ris, fd, ff, y, y_al, duro = loso(df, colonne, positive,
                                          a.modello, a.soglia,
                                          valuta=valuta)
        ag = aggrega(ris)
        etich = {'evento': 'fall', 'stato': 'fallen',
                 'allarme': 'fall O fallen'}[nome]
        print(f"{nome:<10}{etich:<22}{dec(float(y.mean())):>11}"
              f"{dec(ag['fbeta_media']):>9}{' +-' + dec(ag['fbeta_dev']):>8}"
              f"{dec(ag['recall_media']):>8}{dec(ag['precision_media']):>8}"
              f"{dec(100*fd, 1) + '%':>20}{dec(100*ff, 1) + '%':>9}")
        esito.append({'compito': nome, 'positivo': etich,
                      'prevalenza_addestramento': float(y.mean()),
                      'prevalenza_valutazione': float(y_al.mean()),
                      'allarme_difficili': fd, 'allarme_facili': ff, **ag})

    n_duro = int((duro >= 0.5).sum())
    print('-' * 96)
    print(f'DIFFICILI = finestre negative con almeno meta dei fotogrammi '
          f'`lying`/`lie_down` ({n_duro:,} finestre).')
    print('facili = tutti gli altri negativi: camminare, stare in piedi, sedersi.')
    print()
    print('Riferimento esterno, OmniFall 2025 con VideoMAE (87 M di parametri):')
    print('   evento (fall)    F1 65,6%        stato (fallen)   F1 41,0%')
    print('   i modelli multimodali grandi confondono `fallen` con `lying`: '
          'F1 29-31%')

    out = os.path.join(config.RISULTATI_DIR, 'compiti')
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, f'{a.modello}_{a.feature}_cam{a.camera}.json'),
              'w', encoding='utf-8') as f:
        json.dump({'modello': a.modello, 'feature': a.feature,
                   'colonne': list(colonne), 'camera': a.camera,
                   'soglia': a.soglia, 'compiti': esito}, f, indent=2,
                  ensure_ascii=False)
    print(f'\nsalvato: risultati/compiti/{a.modello}_{a.feature}_cam{a.camera}.json')


if __name__ == '__main__':
    main()
