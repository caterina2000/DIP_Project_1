# -*- coding: utf-8 -*-
"""Scompone la latenza di rilevamento, e dichiara che cosa non e' misurabile.

Perche' esiste
--------------
Il Capitolo 1 prometteva una misura del ritardo di rilevamento
([ISS-108](../docs/ISSUES.md)) e il relatore l'ha chiesta fra le quattro
metriche operative. La promessa non era mantenibile nella forma in cui era
stata scritta, e questo script mostra perche'.

Le cadute della sessione del 13 agosto sono annotate **al minuto**:
`['09:20', '09:22', '09:25', '09:29', '09:31']`. La grandezza da misurare ---
il tempo fra l'inizio della caduta e la prima segnalazione --- e' dell'ordine
di pochi secondi. **L'incertezza sull'istante vero e' fino a sessanta volte
piu' grande della quantita' da misurare**, quindi la differenza fra l'ora
annotata e l'ora dell'allarme non misura il ritardo del sistema: misura in
quale punto del minuto la persona e' caduta.

Che cosa invece si misura esattamente
-------------------------------------
La latenza si scompone in tre addendi, due dei quali si calcolano dalla sola
configurazione e non dipendono dall'annotazione:

    latenza  =  calcolo  +  riempimento della finestra  +  persistenza

    calcolo         37,7 ms per fotogramma, misurato sul dispositivo
    finestra        L campioni / fps  --- il classificatore non puo' decidere
                    prima che l'evento occupi la finestra
    persistenza     (P-1) x cadenza delle decisioni

Il terzo addendo si verifica anche empiricamente, sulle cadute in cui
l'allarme scatta: e' l'unico intervallo i cui due estremi sono entrambi noti
al centesimo di secondo.

Uso
---
    python pipeline/latenza.py
    python pipeline/latenza.py --soglia 0.5 --persistenza 5
"""

import argparse
import datetime as dt
import json
import os

import numpy as np
import pandas as pd

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSIONE = os.path.join(QUI, 'risultati', 'sessioni', '20260813',
                        'bloccocadute_sola_20260813_091641')

# Annotazione delle cadute, dal registro di campo. E' al MINUTO: e' questo il
# limite che rende non misurabile il ritardo, ed e' il punto dello script.
ORARI = ['09:20', '09:22', '09:25', '09:29', '09:31']
RISOLUZIONE_ANNOTAZIONE_S = 60.0

# Costo per fotogramma misurato sul dispositivo, Capitolo sull'edge.
CALCOLO_MS = 37.7


def corse(sopra):
    """Lunghezza della corsa di valori veri che termina in ciascun indice."""
    fuori = np.zeros(len(sopra), int)
    n = 0
    for i, v in enumerate(sopra):
        n = n + 1 if v else 0
        fuori[i] = n
    return fuori


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sessione', default=SESSIONE)
    ap.add_argument('--soglia', type=float, default=0.5)
    ap.add_argument('--persistenza', type=int, default=5)
    ap.add_argument('--finestra', type=int, default=22)
    ap.add_argument('--cerca-s', type=float, default=90.0,
                    help='quanto si cerca dopo il minuto annotato')
    a = ap.parse_args()

    d = pd.read_csv(os.path.join(a.sessione, 'punteggi.csv'))
    with open(os.path.join(a.sessione, 'riepilogo.json'), encoding='utf-8') as f:
        rie = json.load(f)

    t = d['t_unix'].to_numpy(float)
    s = d['punteggio'].to_numpy(float)
    sopra = s >= a.soglia
    run = corse(sopra)

    cadenza = float(np.diff(t).mean())
    fps = float(rie['fps_medio'])
    riempimento = a.finestra / fps
    persistenza_s = (a.persistenza - 1) * cadenza
    minima = CALCOLO_MS / 1000.0 + riempimento + persistenza_s

    print('sessione   ', os.path.basename(a.sessione))
    print('finestre   ', len(d))
    print('fps medio  ', '{:.2f}'.format(fps).replace('.', ','))
    print()
    print('SCOMPOSIZIONE, dalla sola configurazione')
    print('  calcolo per fotogramma        {:>7.3f} s'
          .format(CALCOLO_MS / 1000.0).replace('.', ','))
    print('  riempimento della finestra    {:>7.3f} s   ({} campioni a {:.2f} fps)'
          .format(riempimento, a.finestra, fps).replace('.', ','))
    print('  persistenza                   {:>7.3f} s   ({} finestre, una ogni {:.3f} s)'
          .format(persistenza_s, a.persistenza, cadenza).replace('.', ','))
    print('  ------------------------------------------')
    print('  LIMITE INFERIORE              {:>7.3f} s'
          .format(minima).replace('.', ','))
    print()
    print('  Il calcolo e\' il {:.1f}% del totale: la latenza e\' dominata dalla'
          .format(100 * (CALCOLO_MS / 1000.0) / minima).replace('.', ','))
    print('  finestra di decisione, non dall\'hardware.')

    giorno = dt.datetime.fromtimestamp(t[0]).date()
    righe = []
    print()
    print('PER CADUTA ANNOTATA   (l\'annotazione e\' al minuto: +-60 s)')
    print('  ora     finestre>=soglia  corsa max  prima sopra  allarme  regola')
    for o in ORARI:
        h, m = map(int, o.split(':'))
        t0 = dt.datetime.combine(giorno, dt.time(h, m)).timestamp()
        sel = (t >= t0) & (t < t0 + a.cerca_s)
        idx = np.where(sel & sopra)[0]
        r = {'ora': o, 'finestre_sopra': int(len(idx)),
             'corsa_massima': int(run[sel].max()) if sel.any() else 0}
        if len(idx):
            r['prima_sopra_s'] = float(t[idx[0]] - t0)
            colpo = np.where(sel & (run >= a.persistenza))[0]
            if len(colpo):
                r['allarme_s'] = float(t[colpo[0]] - t0)
                r['ritardo_regola_s'] = float(t[colpo[0]] - t[idx[0]])
        righe.append(r)
        print('  {}  {:>10d}  {:>10d}  {:>10}  {:>8}  {:>6}'.format(
            o, r['finestre_sopra'], r['corsa_massima'],
            '{:+.1f} s'.format(r['prima_sopra_s']).replace('.', ',')
            if 'prima_sopra_s' in r else '--',
            '{:+.1f} s'.format(r['allarme_s']).replace('.', ',')
            if 'allarme_s' in r else '--',
            '{:.2f} s'.format(r['ritardo_regola_s']).replace('.', ',')
            if 'ritardo_regola_s' in r else '--'))

    misurati = [r['ritardo_regola_s'] for r in righe if 'ritardo_regola_s' in r]
    print()
    if misurati:
        print('  ritardo della regola misurato su {} cadute: {} s'
              .format(len(misurati),
                      ' e '.join('{:.2f}'.format(v).replace('.', ',')
                                 for v in misurati)))
        print('  atteso dalla configurazione: {:.2f} s'
              .format(persistenza_s).replace('.', ','))

    print()
    print('CHE COSA NON SI MISURA, e perche\'')
    print('  Gli scarti «prima sopra soglia» vanno da {:+.1f} a {:+.1f} secondi.'
          .format(min(r['prima_sopra_s'] for r in righe if 'prima_sopra_s' in r),
                  max(r['prima_sopra_s'] for r in righe if 'prima_sopra_s' in r))
          .replace('.', ','))
    print('  Non sono ritardi del sistema: sono il punto del minuto annotato in')
    print('  cui la persona e\' caduta. Con annotazione al minuto il ritardo di')
    print('  rilevamento NON e\' misurabile, e va dichiarato tale.')

    fuori = {
        'sessione': os.path.basename(a.sessione),
        'configurazione': {'soglia': a.soglia, 'persistenza': a.persistenza,
                           'finestra': a.finestra, 'fps_medio': fps,
                           'cadenza_decisioni_s': cadenza},
        'risoluzione_annotazione_s': RISOLUZIONE_ANNOTAZIONE_S,
        'scomposizione_s': {'calcolo': CALCOLO_MS / 1000.0,
                            'riempimento_finestra': riempimento,
                            'persistenza': persistenza_s,
                            'limite_inferiore': minima},
        'per_caduta': righe,
        'ritardo_regola_misurato_s': misurati,
        'nota': ('Il ritardo fra caduta e allarme non e\' misurabile: '
                 'l\'annotazione ha risoluzione di un minuto, la grandezza da '
                 'misurare e\' di pochi secondi.'),
    }
    dest = os.path.join(QUI, 'risultati', 'campo', 'latenza.json')
    with open(dest, 'w', encoding='utf-8') as f:
        json.dump(fuori, f, ensure_ascii=False, indent=1)
    print()
    print('scritto', os.path.relpath(dest, QUI))


if __name__ == '__main__':
    main()
