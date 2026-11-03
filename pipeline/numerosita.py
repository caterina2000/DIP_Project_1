# -*- coding: utf-8 -*-
"""
La tabella della numerosita' campionaria, rifatta su feature_v5 a dieci soggetti.

Perche' esiste
--------------
`tab:numerosita` raccoglieva righe da campagne diverse. Tre problemi accertati
il 2026-09-25:

  1. la riga «definizione del compito, -0,309» veniva dal confronto fra
     MODALITA' DI ETICHETTATURA (`scarta` contro `tre_classi`) del 20 agosto,
     non dal confronto fra evento, stato e allarme di `tab:compiti`. Due
     esperimenti diversi sotto lo stesso nome;
  2. la riga «effetto delle grandezze integrali, -0,022» era la variante
     «foresta con estremi» della stessa campagna; la variante senza estremi
     dava +0,039, cioe' segno opposto, e `tab:rappresentazioni10` mostra
     -0,016, che e' una terza misura;
  3. la riga «finestra 22 contro 44» confrontava L22 su feature_v5 con L44 su
     feature_v2: due dataset diversi.

Qui tutte le righe sono ricalcolate sullo stesso dataset, con lo stesso
modello e lo stesso protocollo, e ciascuna dichiara che cosa confronta.

Il modello
----------
Foresta casuale per i confronti di protocollo e rappresentazione: e' l'unico
dei sei che si riaddestra in frazioni di secondo, e qui serve riaddestrare
molte volte. I confronti fra ARCHITETTURE vengono invece dai punteggi per fold
gia' salvati, perche' quelli richiedono le reti.

La valutazione e' sempre sull'etichetta di allarme
--------------------------------------------------
`dati.fold_loso` restituisce per il test `y_allarme`, cioe' la stessa verita'
per tutte le modalita' di etichettatura. Il confronto fra `scarta`, `caduta` e
`tre_classi` e' quindi fatto sullo stesso insieme di finestre e sulla stessa
etichetta: cambia che cosa il modello vede in addestramento, non come viene
giudicato.

Uso
---
    python pipeline/numerosita.py
"""
import argparse
import json
import os
import sys

import numpy as np

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, QUI)

from src import dati                                        # noqa: E402

FUORI = os.path.join(QUI, 'risultati', 'laboratorio', 'numerosita.json')
PUNTEGGI = os.path.join(QUI, 'risultati', 'addestramento')
SOGLIA = 0.50
POTENZA_Z = 0.84          # z per potenza 80%
ALFA_Z = 1.96             # z per alfa 5% a due code


def f2(y, p, soglia=SOGLIA):
    q = (p >= soglia).astype(int)
    tp = int(((q == 1) & (y == 1)).sum())
    fp = int(((q == 1) & (y == 0)).sum())
    fn = int(((q == 0) & (y == 1)).sum())
    if tp == 0:
        return 0.0
    pr, rc = tp / float(tp + fp), tp / float(tp + fn)
    return 5 * pr * rc / (4 * pr + rc)


def riassumi(X):
    """Le sei statistiche per colonna che la foresta riceve al posto della
    sequenza, come in addestra.py."""
    return np.concatenate([X.mean(1), X.std(1), X.min(1), X.max(1),
                           X[:, 0, :], X[:, -1, :]], axis=1)


def per_fold_foresta(df, colonne, modo, seme=42, **kw):
    """F2 su ciascun fold, valutato sull'etichetta di allarme."""
    from sklearn.ensemble import RandomForestClassifier
    fuori = []
    for f in dati.fold_loso(df, colonne, modo, **kw):
        m = RandomForestClassifier(n_estimators=50, class_weight='balanced',
                                   random_state=seme, n_jobs=-1)
        # In tre_classi il modello vede TRE etichette, e la probabilita di
        # allarme e 1 - p(normale). Binarizzare qui renderebbe tre_classi
        # identico a caduta per costruzione, e il confronto non misurerebbe
        # nulla: e un difetto che questo script ha avuto per mezz ora.
        y = np.asarray(f.y_train).astype(int)
        m.fit(riassumi(f.X_train), y)
        prob = m.predict_proba(riassumi(f.X_test))
        i0 = list(m.classes_).index(0)
        p = 1.0 - prob[:, i0]
        fuori.append(f2((np.asarray(f.y_test) > 0).astype(int), p))
    return np.array(fuori)


def per_fold_npz(chiave):
    z = np.load(os.path.join(PUNTEGGI, 'punteggi_%s_L22.npz' % chiave),
                allow_pickle=True)
    fuori, i = [], 0
    while 'p_test_%d' % i in z:
        fuori.append(f2(np.asarray(z['y_test_%d' % i]).ravel(),
                        np.asarray(z['p_test_%d' % i]).ravel()))
        i += 1
    return np.array(fuori)


def confronta(nome, a, b, che_cosa):
    """`a` contro `b`: differenza appaiata, t, e numerosita' per potenza 80%."""
    from scipy import stats
    d = a - b
    s = d.std(ddof=1)
    t, _ = stats.ttest_rel(a, b)
    dz = d.mean() / s if s > 0 else 0.0
    n = int(np.ceil(((ALFA_Z + POTENZA_Z) / abs(dz)) ** 2)) if dz else None
    return {'confronto': nome, 'che_cosa': che_cosa,
            'media_a': float(a.mean()), 'media_b': float(b.mean()),
            'differenza': float(d.mean()), 'dev_differenza': float(s),
            't': float(t), 'n_80': n, 'n_fold': len(d)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='feature_v5.csv')
    ap.add_argument('--fuori', default=FUORI)
    a = ap.parse_args()

    df = dati.carica(a.csv)
    dtw = dati.feature_dtw()
    a3 = dati.colonne_di('A3')
    a3base = dati.colonne_di('A3base')

    print('csv %s, %d soggetti, foresta casuale a 50 alberi, soglia %.2f'
          % (a.csv, df[dati.COL_SOGGETTO].nunique(), SOGLIA))
    print('valutazione sempre sull\'etichetta di allarme\n')

    righe = []

    # --- modalita' di etichettatura --------------------------------------
    tre = per_fold_foresta(df, dtw, 'tre_classi')
    scarta = per_fold_foresta(df, dtw, 'scarta')
    caduta = per_fold_foresta(df, dtw, 'caduta')
    righe.append(confronta('Etichettatura: scarta contro tre classi',
                           scarta, tre,
                           'che cosa il modello vede in addestramento'))
    righe.append(confronta('Etichettatura: caduta contro tre classi',
                           caduta, tre,
                           'che cosa il modello vede in addestramento'))

    # --- rappresentazione -------------------------------------------------
    f_a3 = per_fold_foresta(df, a3, 'tre_classi')
    f_a3b = per_fold_foresta(df, a3base, 'tre_classi')
    f_dtw = tre
    righe.append(confronta('Grandezze integrali: A3 contro A3base',
                           f_a3, f_a3b, 'nove grandezze accumulate in piu'))
    righe.append(confronta('Selezione DTW: dodici grandezze contro A3',
                           f_dtw, f_a3, 'quali grandezze il modello riceve'))

    # --- lunghezza della finestra ----------------------------------------
    l22 = tre
    l44 = per_fold_foresta(df, dtw, 'tre_classi', lunghezza=44)
    righe.append(confronta('Finestra: 44 campioni contro 22', l44, l22,
                           'quanta storia entra in una decisione'))

    # --- architetture, dai punteggi gia' salvati -------------------------
    gru = per_fold_npz('gru_tre_classi_DTW_cam1')
    for chiave, nome in (('cnn', 'CNN 1D'), ('transformer', 'Transformer'),
                         ('lstm', 'LSTM'), ('foresta', 'foresta casuale'),
                         ('grafo', 'rete a grafo')):
        v = per_fold_npz('%s_tre_classi_DTW_cam1' % chiave)
        righe.append(confronta('Architettura: %s contro GRU' % nome, v, gru,
                               'solo il classificatore'))

    righe.sort(key=lambda r: (r['n_80'] is None, r['n_80']))
    print('%-46s %10s %8s %9s' % ('confronto', 'differenza', 't', 'n 80%'))
    for r in righe:
        print('%-46s %+10.3f %8.2f %9s'
              % (r['confronto'], r['differenza'], r['t'],
                 r['n_80'] if r['n_80'] is not None else '--'))

    os.makedirs(os.path.dirname(a.fuori), exist_ok=True)
    with open(a.fuori, 'w', encoding='utf-8') as f:
        json.dump({'csv': a.csv, 'modello': 'foresta casuale, 50 alberi',
                   'soglia': SOGLIA, 'potenza': 0.80, 'alfa': 0.05,
                   'test': 'appaiato, due code',
                   'valutazione': 'etichetta di allarme, comune a tutte le '
                                  'modalita di etichettatura',
                   'righe': righe}, f, ensure_ascii=False, indent=1)
    print('\nscritto', a.fuori)


if __name__ == '__main__':
    main()
