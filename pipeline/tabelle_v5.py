# -*- coding: utf-8 -*-
"""
`tab:finestra` e `tab:rappresentazioni10` rifatte sulla stessa base della
tabella della numerosita': foresta casuale, feature_v5, dieci soggetti.

Perche' esiste
--------------
Accertato il 2026-09-25, su segnalazione esterna. Le due tabelle erano
entrambe della campagna GRU del 20 agosto su feature_v2:

  - `tab:finestra` riporta L22 a 0,847, che e' `run_gru_..._DTW_cam1.json`
    del 20 agosto; il run v5 della stessa configurazione da' 0,857;
  - L28, L36 e L44 esistono solo come run del 20 agosto.

`pipeline/numerosita.py` calcolava invece le differenze con la foresta su
feature_v5, e i due insiemi non erano confrontabili: la riga «finestra 44
contro 22» dava +0,091 accanto a una tabella da cui si legge +0,034. Era una
incoerenza introdotta dal confronto stesso, non un risultato.

Qui le due tabelle sono ricalcolate con lo stesso modello e lo stesso dataset
delle differenze appaiate, cosi' che tabella e confronto si leggano insieme.

Uso
---
    python pipeline/tabelle_v5.py
"""
import argparse
import json
import os
import sys

import numpy as np

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, QUI)

from src import dati                                        # noqa: E402

FUORI = os.path.join(QUI, 'risultati', 'laboratorio', 'tabelle_v5.json')
SOGLIA = 0.50


def misura(df, colonne, modo='tre_classi', seme=42, **kw):
    """F2, recall, FN e FP per fold, valutati sull'etichetta di allarme."""
    from sklearn.ensemble import RandomForestClassifier
    f2s, rec, fn_t, fp_t = [], [], 0, 0
    for f in dati.fold_loso(df, colonne, modo, **kw):
        m = RandomForestClassifier(n_estimators=50, class_weight='balanced',
                                   random_state=seme, n_jobs=-1)
        m.fit(_riassumi(f.X_train), np.asarray(f.y_train).astype(int))
        prob = m.predict_proba(_riassumi(f.X_test))
        p = 1.0 - prob[:, list(m.classes_).index(0)]
        y = (np.asarray(f.y_test) > 0).astype(int)
        q = (p >= SOGLIA).astype(int)
        tp = int(((q == 1) & (y == 1)).sum())
        fp = int(((q == 1) & (y == 0)).sum())
        fn = int(((q == 0) & (y == 1)).sum())
        fn_t += fn
        fp_t += fp
        if tp:
            pr, rc = tp / float(tp + fp), tp / float(tp + fn)
            f2s.append(5 * pr * rc / (4 * pr + rc))
            rec.append(rc)
        else:
            f2s.append(0.0)
            rec.append(0.0)
    a = np.array(f2s)
    return {'f2': float(a.mean()), 'dev': float(a.std(ddof=1)),
            'recall': float(np.mean(rec)), 'fn': fn_t, 'fp': fp_t}


def _riassumi(X):
    return np.concatenate([X.mean(1), X.std(1), X.min(1), X.max(1),
                           X[:, 0, :], X[:, -1, :]], axis=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='feature_v5.csv')
    ap.add_argument('--fuori', default=FUORI)
    a = ap.parse_args()

    df = dati.carica(a.csv)
    dtw = dati.feature_dtw()

    print('%s, foresta a 50 alberi, soglia %.2f, dieci fold\n'
          % (a.csv, SOGLIA))

    # --- lunghezza della finestra ---------------------------------------
    print('LUNGHEZZA DELLA FINESTRA')
    print('%4s %9s %18s %9s %12s' % ('L', 'durata', 'F2', 'recall', 'FN / FP'))
    finestra = []
    for L in (22, 28, 36, 44):
        r = misura(df, dtw, lunghezza=L)
        r['L'] = L
        r['durata_s'] = round(L / 9.0, 1)
        finestra.append(r)
        print('%4d %7.1f s  %.3f +- %.3f %9.3f %6d / %4d'
              % (L, r['durata_s'], r['f2'], r['dev'], r['recall'],
                 r['fn'], r['fp']))

    # --- configurazioni di grandezze ------------------------------------
    print('\nCONFIGURAZIONI DI GRANDEZZE')
    print('%-36s %18s %9s' % ('configurazione', 'F2', 'recall'))
    config = []
    for nome, col in (('A3 senza grandezze integrali',
                       dati.colonne_di('A3base')),
                      ('A3 con grandezze integrali', dati.colonne_di('A3')),
                      ('Sottoinsieme selezionato tramite DTW', dtw)):
        r = misura(df, col)
        r['nome'] = nome
        r['n_colonne'] = len(col)
        config.append(r)
        print('%-36s  %.3f +- %.3f %9.3f'
              % (nome, r['f2'], r['dev'], r['recall']))

    os.makedirs(os.path.dirname(a.fuori), exist_ok=True)
    with open(a.fuori, 'w', encoding='utf-8') as f:
        json.dump({'csv': a.csv, 'modello': 'foresta casuale, 50 alberi',
                   'soglia': SOGLIA,
                   'valutazione': 'etichetta di allarme',
                   'finestra': finestra, 'configurazioni': config}, f,
                  ensure_ascii=False, indent=1)
    print('\nscritto', a.fuori)


if __name__ == '__main__':
    main()
