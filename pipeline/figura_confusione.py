# -*- coding: utf-8 -*-
"""
Le matrici di confusione delle sei architetture, a parita' di protocollo.

Perche' esiste
--------------
La tabella del confronto fra architetture riporta $F_2$, recall, falsi
negativi e falsi positivi. Sono quattro numeri per riga e sei righe: il
lettore deve tenerne ventiquattro in testa per capire in che cosa i modelli
differiscono davvero. Le matrici mostrano la stessa cosa in un colpo d'occhio,
e soprattutto mostrano DOVE ciascun modello sbaglia.

Perche' normalizzate per riga
-----------------------------
Sui fold di prova le finestre negative sono circa venti volte le positive. Con
i conteggi assoluti la cella in alto a sinistra --- i veri negativi --- vale
decine di migliaia, mentre le altre tre valgono centinaia: una scala di colore
che copra quell'intervallo rende bianche tutte le celle tranne una, e la
figura non mostra piu' niente.

La normalizzazione per riga divide ciascuna riga per il proprio totale, cioe'
per il numero di finestre che appartengono davvero a quella classe. Ogni riga
somma a 100, e le due righe rispondono alle due domande che contano:

  riga 'non caduta' -> quanta parte del normale il modello lascia in pace,
                       e quanta ne trasforma in allarme;
  riga 'caduta'     -> quanta parte delle cadute il modello prende,
                       e quanta ne perde. E' la recall.

E' anche l'unico modo per confrontare i sei modelli fra loro: i dieci fold
hanno dimensioni diverse, e le percentuali sono comparabili dove i conteggi
non lo sono.

La normalizzazione per colonna darebbe invece la precision. Si e' scelta la
riga perche' la metrica di riferimento del lavoro e' $F_2$, che pesa la recall
quattro volte la precision: cio' che conta e' quante cadute si perdono.

Uso:
    python pipeline/figura_confusione.py
    python pipeline/figura_confusione.py --punteggi risultati/addestramento/v2
"""

import argparse
import os
import sys

import math

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from sklearn.metrics import confusion_matrix

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# i sei modelli, nell'ordine in cui compaiono nella tabella del confronto
MODELLI = [('lstm', 'LSTM'), ('gru', 'GRU'), ('transformer', 'Transformer'),
           ('cnn', 'CNN 1D'), ('foresta', 'Random Forest'), ('grafo', 'Grafo')]

SOGLIA = 0.50
LINGUA = 'it'
TITOLI = False


def T(it, en):
    return it if LINGUA == 'it' else en


def classi():
    return T(['non caduta', 'caduta'], ['no fall', 'fall'])


CLASSI = ['non caduta', 'caduta']


def carica(dove, chiave):
    """I dieci fold di prova di una run, tenuti separati."""
    for nome in ('punteggi_%s_tre_classi_DTW_cam1_L22.npz' % chiave,
                 'punteggi_%s_tre_classi_DTW_cam1.npz' % chiave):
        p = os.path.join(dove, nome)
        if os.path.exists(p):
            z = np.load(p, allow_pickle=True)
            fold, k = [], 0
            while 'p_test_%d' % k in z:
                fold.append((np.asarray(z['y_test_%d' % k]).ravel(),
                             np.asarray(z['p_test_%d' % k]).ravel()))
                k += 1
            if fold:
                return fold
    return None


def f2(mc):
    tn, fp, fn, tp = mc.ravel()
    pr = tp / (tp + fp) if tp + fp else 0.0
    rc = tp / (tp + fn) if tp + fn else 0.0
    return 5 * pr * rc / (4 * pr + rc) if (4 * pr + rc) else 0.0


def f2_medio(fold):
    """La media degli F2 per fold: e' il valore riportato nella tabella
    del confronto fra architetture. Non coincide con l'F2 calcolato sui
    dieci fold messi insieme, perche' i fold hanno dimensioni diverse e la
    media di rapporti non e' il rapporto delle somme."""
    v = [f2(confusion_matrix(y, (s >= SOGLIA).astype(int), labels=[0, 1]))
         for y, s in fold]
    return float(np.mean(v)), float(np.std(v))


def main():
    ap = argparse.ArgumentParser()
    # la campagna v5, non la v2: `carica()` cerca i file `_L22` per primi,
    # e quelli sono del 9 settembre su feature_v5. La sottocartella v2
    # conserva la campagna del 20 agosto, che il Capitolo 3 non descrive.
    ap.add_argument('--punteggi',
                    default=os.path.join(QUI, 'risultati', 'addestramento'))
    ap.add_argument('--lingua', default='it', choices=('it', 'en'))
    ap.add_argument('--titoli', action='store_true')
    ap.add_argument('--dove', default=os.path.join(QUI, 'tesi', 'figure'))
    ap.add_argument('--nome', default='fig_confusione.png')
    a = ap.parse_args()

    global LINGUA, TITOLI
    LINGUA, TITOLI = a.lingua, a.titoli
    if LINGUA != 'it' and a.nome == 'fig_confusione.png':
        a.nome = 'fig_confusione_en.png'

    if not os.path.isdir(a.punteggi):
        sys.exit('cartella dei punteggi non trovata: ' + a.punteggi)

    dati = []
    for chiave, etichetta in MODELLI:
        etichetta = T(etichetta, {'Grafo': 'Graph'}.get(etichetta, etichetta))
        fold = carica(a.punteggi, chiave)
        if fold is None:
            print('   %-14s ASSENTE, saltato' % etichetta)
            continue
        y = np.concatenate([f[0] for f in fold])
        s = np.concatenate([f[1] for f in fold])
        p = (s >= SOGLIA).astype(int)
        mc = confusion_matrix(y, p, labels=[0, 1])
        mcn = confusion_matrix(y, p, labels=[0, 1], normalize='true')
        m, d = f2_medio(fold)
        dati.append((etichetta, mc, mcn, m, d))
        tn, fp, fn, tp = mc.ravel()
        print('   %-14s %2d fold  F2 medio=%.3f+-%.3f  FN=%4d  FP=%5d  recall=%.3f'
              % (etichetta, len(fold), m, d, fn, fp, tp / (tp + fn)))

    if not dati:
        sys.exit('nessuna run trovata in ' + a.punteggi)

    # scala di colore: bianco -> blu della tesi
    mappa = LinearSegmentedColormap.from_list(
        'tesi', ['#ffffff', '#cfe0ee', '#7fa9ca', '#27496d'])

    n = len(dati)
    # due righe quando i modelli sono piu' di quattro: su una riga sola
    # i riquadri diventano troppo stretti perche' i numeri si leggano.
    righe = 2 if n > 4 else 1
    colonne = int(math.ceil(n / float(righe)))
    fig, assi = plt.subplots(righe, colonne,
                             figsize=(4.05 * colonne, 4.35 * righe))
    assi = np.atleast_1d(assi).ravel()
    for ax in assi[n:]:
        ax.axis('off')
    fig.patch.set_facecolor('white')

    for k, (ax, (etichetta, mc, mcn, m, d)) in enumerate(
            zip(assi, dati)):
        prima_colonna = (k % colonne == 0)
        ultima_riga = (k >= n - colonne)
        ax.imshow(mcn, cmap=mappa, vmin=0, vmax=1)
        for i in range(2):
            for j in range(2):
                ax.text(j, i - 0.10, '%.1f%%' % (100 * mcn[i, j]),
                        ha='center', va='center', fontsize=17,
                        fontweight='bold',
                        color='white' if mcn[i, j] > 0.55 else '#27496d')
                ax.text(j, i + 0.22, '%d' % mc[i, j], ha='center', va='center',
                        fontsize=12,
                        color='#dce8f2' if mcn[i, j] > 0.55 else '#5a6b7a')
        ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
        ax.set_xticklabels(classi() if ultima_riga else ['', ''],
                           fontsize=10.5)
        ax.set_yticklabels(classi() if prima_colonna else ['', ''],
                           fontsize=10.5, rotation=90,
                           va='center')
        if ultima_riga:
            ax.set_xlabel(T('predetta', 'predicted'), fontsize=11)
        if prima_colonna:
            ax.set_ylabel(T('reale', 'actual'), fontsize=11)
        ax.set_title('%s\n$F_2 = %.3f \\pm %.3f$' % (etichetta, m, d),
                     fontsize=13, pad=10)
        for s in ax.spines.values():
            s.set_edgecolor('#9fb6cc')

    TITOLI and fig.suptitle(
        'Matrici di confusione normalizzate per riga, '
                 'LOSO a dieci fold, soglia $0{,}50$',
                 fontsize=12.5, y=1.02)
    fig.tight_layout()
    # su due righe i titoli della seconda toccano le matrici della prima:
    # tight_layout non lo vede perche' le matrici sono disegnate con imshow
    if righe > 1:
        fig.subplots_adjust(hspace=0.42)
    os.makedirs(a.dove, exist_ok=True)
    fuori = os.path.join(a.dove, a.nome)
    fig.savefig(fuori, dpi=400, facecolor='white', bbox_inches='tight')
    print('scritto', fuori)


if __name__ == '__main__':
    main()
