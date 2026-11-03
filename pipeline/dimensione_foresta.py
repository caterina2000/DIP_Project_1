# -*- coding: utf-8 -*-
"""
La dimensione della foresta casuale, misurata a dieci soggetti.

Perche' esiste
--------------
La figura `fig_dimensione` leggeva `risultati/cinque_soggetti/exp017_rf_size.json`,
prodotto dall'impianto sperimentale precedente. Nessuno script del progetto
attuale lo rigenerava, e la didascalia doveva percio' dichiarare che la misura
veniva da cinque soggetti mentre tutto il resto del capitolo ne usa dieci.

La foresta e' l'unico dei sei modelli per cui rifare la scansione costa poco:
non richiede TensorFlow, si addestra in frazioni di secondo e la scansione
completa sono sei dimensioni per dieci fold, cioe' sessanta addestramenti.

Che cosa misura
---------------
Per ciascuna dimensione, sui dieci fold LOSO di `feature_v5.csv`, camera 1,
dodici grandezze DTW:

  - l'F-beta con beta = 2 alla soglia 0,50 fissata a priori, media e
    deviazione fra i fold;
  - il numero complessivo di nodi degli alberi, che e' cio' che determina
    l'occupazione in memoria del modello schierato;
  - il tempo di addestramento;
  - la latenza di classificazione per finestra, misurata SUL CALCOLATORE.

L'ultima voce va letta per quello che e'. Il Capitolo 5 riporta 39,04 ms per
finestra misurati sulla board: il valore di questo script e' dell'ordine dei
millisecondi perche' e' preso su una macchina diversa, e serve a descrivere
l'andamento rispetto alla dimensione, non il costo del sistema installato.

Uso
---
    python pipeline/dimensione_foresta.py
    python pipeline/dimensione_foresta.py --alberi 10 25 50 100 200 400
"""
import argparse
import json
import os
import sys
import time

import numpy as np

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, QUI)

from src import dati                                        # noqa: E402

FUORI = os.path.join(QUI, 'risultati', 'laboratorio', 'dimensione_foresta.json')
ALBERI = [10, 25, 50, 100, 200, 400]
SOGLIA = 0.50


def fbeta(y, p, soglia=SOGLIA, beta=2.0):
    q = (p >= soglia).astype(int)
    tp = int(((q == 1) & (y == 1)).sum())
    fp = int(((q == 1) & (y == 0)).sum())
    fn = int(((q == 0) & (y == 1)).sum())
    if tp == 0:
        return 0.0, fn, fp
    prec = tp / float(tp + fp)
    rec = tp / float(tp + fn)
    b2 = beta * beta
    return (1 + b2) * prec * rec / (b2 * prec + rec), fn, fp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='feature_v5.csv')
    ap.add_argument('--camera', type=int, default=1)
    ap.add_argument('--modo', default='tre_classi')
    ap.add_argument('--alberi', type=int, nargs='+', default=ALBERI)
    ap.add_argument('--seme', type=int, default=42)
    ap.add_argument('--fuori', default=FUORI)
    a = ap.parse_args()

    from sklearn.ensemble import RandomForestClassifier

    df = dati.carica(a.csv)
    df = df[df.camera == a.camera]
    colonne = dati.feature_dtw()
    fold = list(dati.fold_loso(df, colonne, a.modo))

    print('csv        %s, camera %d, %d grandezze' % (a.csv, a.camera,
                                                      len(colonne)))
    print('fold       %d' % len(fold))
    print('soglia     %.2f, fissata a priori' % SOGLIA)
    print()
    print('%7s %9s %17s %8s %8s %11s' % ('alberi', 'nodi', 'F2', 'FN', 'FP',
                                         'ms/finestra'))

    prove = []
    for n_alberi in a.alberi:
        f2s, fns, fps, nodi, t_fit, t_pred = [], [], [], [], [], []
        for f in fold:
            # la foresta non riceve la sequenza: la finestra viene riassunta
            # con sei statistiche per colonna, come in addestra.py
            def riassumi(X):
                return np.concatenate(
                    [X.mean(1), X.std(1), X.min(1), X.max(1),
                     X[:, 0, :], X[:, -1, :]], axis=1)

            Xtr = riassumi(f.X_train)
            Xte = riassumi(f.X_test)
            ytr = (np.asarray(f.y_train) > 0).astype(int)
            yte = (np.asarray(f.y_test) > 0).astype(int)

            m = RandomForestClassifier(n_estimators=n_alberi,
                                       class_weight='balanced',
                                       random_state=a.seme, n_jobs=-1)
            t0 = time.perf_counter()
            m.fit(Xtr, ytr)
            t_fit.append(time.perf_counter() - t0)

            p = m.predict_proba(Xte)[:, 1]
            # La latenza si misura UNA FINESTRA ALLA VOLTA, come fa il sistema
            # installato: un lotto intero ammortizza l overhead e darebbe un
            # valore ottimistico di due ordini di grandezza.
            # E si misura con n_jobs = 1: con il pool di thread attivo ogni
            # chiamata singola paga l avvio del pool, che domina e produce
            # una latenza costante indipendente dalla dimensione. Sulla board
            # la foresta gira su un solo processo.
            m.set_params(n_jobs=1)
            campione = Xte[:200]
            t0 = time.perf_counter()
            for riga in campione:
                m.predict_proba(riga.reshape(1, -1))
            t_pred.append((time.perf_counter() - t0) / len(campione) * 1000.0)

            v, fn, fp = fbeta(yte, p)
            f2s.append(v)
            fns.append(fn)
            fps.append(fp)
            nodi.append(sum(t.tree_.node_count for t in m.estimators_))

        prove.append({
            'n_trees': n_alberi,
            'n_nodes': int(np.mean(nodi)),
            'fbeta': float(np.mean(f2s)),
            'fbeta_std': float(np.std(f2s, ddof=1)),
            'fn': int(np.sum(fns)),
            'fp': int(np.sum(fps)),
            'fit_s': float(np.mean(t_fit)),
            'latency_ms_pc': float(np.mean(t_pred)),
            'n_soggetti': len(fold),
        })
        q = prove[-1]
        print('%7d %9d  %.3f +- %.3f %8d %8d %11.3f'
              % (q['n_trees'], q['n_nodes'], q['fbeta'], q['fbeta_std'],
                 q['fn'], q['fp'], q['latency_ms_pc']))

    os.makedirs(os.path.dirname(a.fuori), exist_ok=True)
    with open(a.fuori, 'w', encoding='utf-8') as f:
        json.dump(prove, f, ensure_ascii=False, indent=1)
    print()
    print('scritto', a.fuori)
    print('la latenza e\' misurata sul CALCOLATORE, non sulla board:')
    print('il Capitolo 5 riporta 39,04 ms per finestra sul dispositivo.')


if __name__ == '__main__':
    main()
