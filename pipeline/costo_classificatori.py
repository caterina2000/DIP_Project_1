# -*- coding: utf-8 -*-
"""
Quanto costa ciascun classificatore per finestra, a parita' di condizioni.

Perche' esiste
--------------
Il confronto fra architetture del Capitolo 4 riporta l'accuratezza e il numero
di parametri, e dichiara che nessuna coppia e' distinguibile. Ma la domanda da
cui il lavoro parte non e' solo «quale classifica meglio»: e' **se un
dispositivo da un centinaio di euro basti**, e su quella domanda l'architettura
conta per il COSTO e non per l'accuratezza.

Il costo pero' non era mai stato misurato per tutte e sei le architetture con
lo stesso metro: il valore che compare nella tesi --- 4,47 ms per finestra ---
riguarda la sola foresta.

Che cosa misura, e che cosa no
------------------------------
Misura il tempo di UNA inferenza su UNA finestra, che e' la grandezza
pertinente a un sistema in streaming: la board riceve un fotogramma e decide,
non accumula un lotto. Il modello viene scaldato prima di cronometrare, e si
riporta la MEDIANA su molte ripetizioni, non la media: la coda dovuta allo
scheduler del sistema operativo altrimenti domina.

DUE PRECAUZIONI, senza le quali il banco misura sé stesso
---------------------------------------------------------
La prima versione di questo script dava alla foresta 32 ms contro i 4,47
dichiarati altrove, e alle reti ricorrenti 170-240 ms: un ordine di grandezza
fuori scala. Non erano i modelli, era il modo di chiamarli.

1. **Le reti si chiamano attraverso `tf.function`**, compilata una volta sulla
   forma dell'ingresso. Chiamare il modello in modo interpretato ripaga a ogni
   invocazione il costo di attraversare gli strati in Python, e su una rete
   ricorrente con ventidue passi quel costo si paga ventidue volte: si
   misurerebbe l'interprete, non la ricorrenza.

2. **La foresta si chiama con un solo thread.** Con `n_jobs = -1` ogni
   chiamata su una finestra sola distribuisce cinquanta alberi su un pool di
   thread e poi li raccoglie: il coordinamento costa piu' del calcolo. In
   esercizio, su una finestra alla volta, il thread singolo e' anche la
   configurazione giusta.

E' lo stesso difetto che il Capitolo 5 racconta per tre misure diverse: un
banco che non verifica di stare misurando la cosa che dichiara riporta un
numero plausibile e sbagliato.

**I tempi sono quelli di questo calcolatore, non della board.** Servono a
confrontare le architetture fra loro, non a predire i millisecondi sul
dispositivo: ISS-106 ha accertato che le due macchine non sono intercambiabili.
Il rapporto fra le architetture e' pero' la grandezza che interessa, ed e'
quella che si trasferisce meglio del valore assoluto.

I modelli NON sono addestrati, tranne la foresta, che viene caricata da
`deploy_board/modello.pkl` --- cioe' e' quella davvero installata. Per il tempo
di inferenza l'addestramento non cambia nulla in una rete: la forma del grafo
di calcolo e' la stessa. Per una foresta si', e per questo si usa quella vera.

Uso:
    python pipeline/costo_classificatori.py
    python pipeline/costo_classificatori.py --ripetizioni 500
"""

import argparse
import json
import os
import sys
import time

import numpy as np

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '3')

import config
from src.provenienza import scrivi_json


def cronometra(chiamata, ripetizioni, scaldata=20):
    for _ in range(scaldata):
        chiamata()
    t = []
    for _ in range(ripetizioni):
        a = time.perf_counter()
        chiamata()
        t.append((time.perf_counter() - a) * 1000.0)
    t = np.asarray(t)
    return float(np.median(t)), float(t.mean()), float(t.std())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ripetizioni', type=int, default=200)
    ap.add_argument('--lunghezza', type=int, default=config.LUNGHEZZA_FINESTRA)
    ap.add_argument('--grandezze', type=int, default=12)
    a = ap.parse_args()

    from src.modelli import ARCHITETTURE, Foresta, costruisci

    forma = (a.lunghezza, a.grandezze)
    X = np.random.randn(1, *forma).astype('float32')
    righe = []

    print('=' * 78)
    print(f'COSTO PER FINESTRA — finestra {forma[0]}x{forma[1]}, batch 1, '
          f'{a.ripetizioni} ripetizioni')
    print('=' * 78)
    print(f"{'architettura':<14}{'parametri':>12}{'mediana ms':>12}"
          f"{'media ms':>11}{'dev':>8}{'x foresta':>11}")
    print('-' * 78)

    riferimento = None
    for arch in ARCHITETTURE:
        if arch == 'foresta':
            import joblib
            perc = os.path.join(RADICE, 'deploy_board', 'modello.pkl')
            m = joblib.load(perc)
            m.n_jobs = 1                     # vedi la docstring: precauzione 2
            n_par = int(sum(t.tree_.node_count for t in m.estimators_))
            riassunto = Foresta.riassumi(X)
            med, mu, sd = cronometra(lambda: m.predict_proba(riassunto),
                                     a.ripetizioni)
            nota = 'installata, 50 alberi, n_jobs=1'
        else:
            import tensorflow as tf
            mod = costruisci(arch, forma, 3)
            mod.costruisci()
            n_par = mod.n_parametri
            rete = mod._m
            # vedi la docstring: precauzione 1
            passo = tf.function(lambda t: rete(t, training=False))
            T = tf.constant(X)
            med, mu, sd = cronometra(lambda: passo(T), a.ripetizioni)
            nota = 'non addestrata, tf.function'
        if arch == 'foresta':
            riferimento = med
        righe.append({'architettura': arch, 'n_parametri': n_par,
                      'ms_mediana': med, 'ms_media': mu, 'ms_dev': sd,
                      'nota': nota})

    for r in righe:
        rap = r['ms_mediana'] / riferimento if riferimento else float('nan')
        print(f"{r['architettura']:<14}{r['n_parametri']:>12,}"
              f"{r['ms_mediana']:>12.2f}{r['ms_media']:>11.2f}"
              f"{r['ms_dev']:>8.2f}{rap:>10.1f}x")

    print('-' * 78)
    print('I tempi sono di questo calcolatore, non della board. Il rapporto fra')
    print('le architetture e\' cio\' che si legge; il valore assoluto no.')

    fuori = os.path.join(config.RISULTATI_DIR, 'laboratorio',
                         'costo_classificatori.json')
    os.makedirs(os.path.dirname(fuori), exist_ok=True)
    scrivi_json(fuori, {'forma_finestra': list(forma), 'batch': 1,
                        'ripetizioni': a.ripetizioni,
                        'macchina': 'calcolatore di sviluppo, non la board',
                        'python': sys.version.split()[0],
                        'misure': righe}, indent=2)
    print(f'salvato: {os.path.relpath(fuori, RADICE)}')


if __name__ == '__main__':
    main()
