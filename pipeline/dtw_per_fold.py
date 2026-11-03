# -*- coding: utf-8 -*-
"""
La selezione DTW rifatta dentro ogni fold LOSO, per misurare il leakage.

Perche' esiste
--------------
La selezione delle grandezze descritta nel Capitolo 3 e' stata eseguita UNA
VOLTA SOLA sull'intero insieme, prima del leave-one-subject-out, e le dodici
grandezze che ne risultano sono le stesse in tutti i fold. Il soggetto
lasciato fuori ha quindi contribuito al punteggio di separabilita' che decide
quali colonne il classificatore riceve: e' una forma di data leakage, e il
relatore ha chiesto che venga dichiarata (lettera del 14 settembre 2026).

Dichiararla non basta pero' a dirne l'entita'. Questo script la misura: per
ciascun soggetto rifa' la selezione ESCLUDENDOLO, e confronta il sottoinsieme
ottenuto con quello adottato. Se i dieci sottoinsiemi coincidono con quello
adottato, il leakage non ha cambiato nulla e si puo' dirlo con un numero. Se
differiscono, la differenza e' la misura del problema.

Il controllo che viene prima
----------------------------
Prima dei dieci fold lo script rifa' la selezione sull'INTERO insieme e la
confronta con `risultati/dtw/scelte.txt`, cioe' con quella effettivamente
adottata. Se le due non coincidono, il confronto per fold non significa nulla
--- si starebbero confrontando due cose diverse --- e lo script si ferma.

Il backend conta
----------------
`src/dtw.py` usa dtaidistance quando c'e' e una versione in puro Python
altrimenti, e le due NON restituiscono lo stesso valore: la prima e' la radice
della somma dei quadrati, la seconda la somma degli assoluti. La classifica
non dovrebbe cambiare, ma per un confronto con la selezione adottata serve lo
stesso backend con cui quella e' stata prodotta. Lo script dichiara quale sta
usando e il controllo qui sopra se ne accorgerebbe.

Uso
---
    python pipeline/dtw_per_fold.py
    python pipeline/dtw_per_fold.py --csv feature_v5.csv --top 12

Scrive `risultati/dtw/per_fold.json` e `risultati/dtw/per_fold.txt`.
"""

import argparse
import json
import os
import sys
import time

import pandas as pd

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

import config                                                 # noqa: E402
from src.dtw import classifica                                # noqa: E402
from src.geometry import NOMI                                 # noqa: E402
from pipeline.analisi_dtw import seleziona                    # noqa: E402


def scegli(df, colonne, camere, top, max_corr):
    """Classifica e seleziona, esattamente come fa analisi_dtw.py."""
    cl = classifica(df, colonne, camere=tuple(camere))
    validi = df[df.ha_posa == 1] if 'ha_posa' in df.columns else df
    scelte, _ = seleziona(cl, validi, top, max_corr)
    return list(scelte), cl


def confronta(adottate, ottenute):
    a, b = set(adottate), set(ottenute)
    return {
        'uguali': a == b,
        'in_comune': len(a & b),
        'mancanti': sorted(a - b),     # adottate ma non scelte senza il sogg.
        'aggiunte': sorted(b - a),     # scelte senza il sogg. ma non adottate
        'jaccard': len(a & b) / len(a | b) if a | b else 1.0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='feature_v5.csv',
                    help='il CSV che ha prodotto la selezione adottata')
    ap.add_argument('--top', type=int, default=12)
    ap.add_argument('--max-corr', type=float, default=0.85)
    a = ap.parse_args()

    from src import dtw as _dtw
    backend = 'dtaidistance' if getattr(_dtw, '_HA_DTAI', False) else 'puro Python'
    print('backend DTW: %s' % backend, flush=True)

    p = os.path.join(config.FEATURE_DIR, a.csv)
    if not os.path.exists(p):
        sys.exit('manca %s' % p)
    df = pd.read_csv(p)
    colonne = [c for c in NOMI if c in df.columns]
    camere = sorted(df.camera.unique())
    soggetti = sorted(df.soggetto.unique())
    print('%s: %d grandezze, %d riprese, %d soggetti, camere %s'
          % (a.csv, len(colonne), df.ripresa.nunique(), len(soggetti),
             list(camere)), flush=True)

    fuori = os.path.join(config.RISULTATI_DIR, 'dtw')
    with open(os.path.join(fuori, 'scelte.txt'), encoding='utf-8') as f:
        adottate = [r.strip() for r in f if r.strip()]
    print('selezione adottata: %d grandezze\n' % len(adottate), flush=True)

    # ---------------------------------------------------- controllo
    print('CONTROLLO: rifaccio la selezione sull\'intero insieme...', flush=True)
    t0 = time.time()
    intero, _ = scegli(df, colonne, camere, a.top, a.max_corr)
    dt = time.time() - t0
    c = confronta(adottate, intero)
    print('  %.1f s per passata' % dt, flush=True)
    if not c['uguali']:
        print('  NON riproduce la selezione adottata.')
        print('  mancanti: %s' % c['mancanti'])
        print('  aggiunte: %s' % c['aggiunte'])
        sys.exit('  il confronto per fold non sarebbe interpretabile: mi fermo.')
    print('  riproduce esattamente scelte.txt\n', flush=True)
    print('  stima per i %d fold: circa %.0f minuti\n'
          % (len(soggetti), len(soggetti) * dt / 60.0), flush=True)

    # ---------------------------------------------------- i fold
    esito = []
    for i, s in enumerate(soggetti, 1):
        t0 = time.time()
        sotto = df[df.soggetto != s]
        scelte, _ = scegli(sotto, colonne, camere, a.top, a.max_corr)
        c = confronta(adottate, scelte)
        c['soggetto_escluso'] = str(s)
        c['scelte'] = scelte
        c['secondi'] = round(time.time() - t0, 1)
        esito.append(c)
        print('  [%2d/%d] senza %-8s  in comune %2d/%d  %s  (%.0f s)'
              % (i, len(soggetti), s, c['in_comune'], len(adottate),
                 'identico' if c['uguali'] else
                 'DIVERSO: -%s +%s' % (c['mancanti'], c['aggiunte']),
                 c['secondi']), flush=True)

    identici = sum(1 for e in esito if e['uguali'])
    jac = sum(e['jaccard'] for e in esito) / len(esito)
    sempre = set(adottate)
    for e in esito:
        sempre &= set(e['scelte'])
    mai = set()
    for e in esito:
        mai |= set(e['aggiunte'])

    print('\n' + '=' * 70)
    print('%d fold su %d riproducono esattamente la selezione adottata'
          % (identici, len(esito)))
    print('Jaccard medio: %.3f' % jac)
    print('grandezze scelte in TUTTI i fold e anche adottate: %d su %d'
          % (len(sempre), len(adottate)))
    if mai:
        print('grandezze mai adottate ma scelte da qualche fold: %s'
              % sorted(mai))
    print('=' * 70)

    riepilogo = {
        'csv': a.csv, 'top': a.top, 'max_corr': a.max_corr,
        'backend_dtw': backend,
        'adottate': adottate,
        'controllo_intero_insieme_riproduce': True,
        'fold': esito,
        'fold_identici': identici, 'fold_totali': len(esito),
        'jaccard_medio': round(jac, 4),
        'stabili_in_tutti_i_fold': sorted(sempre),
        'mai_adottate_ma_scelte_da_qualche_fold': sorted(mai),
    }
    with open(os.path.join(fuori, 'per_fold.json'), 'w', encoding='utf-8') as f:
        json.dump(riepilogo, f, indent=1, ensure_ascii=False)

    with open(os.path.join(fuori, 'per_fold.txt'), 'w', encoding='utf-8') as f:
        f.write('selezione DTW rifatta dentro ogni fold LOSO\n\n')
        f.write('CSV        %s\n' % a.csv)
        f.write('backend    %s\n' % backend)
        f.write('controllo  la selezione sull\'intero insieme riproduce '
                'esattamente scelte.txt\n\n')
        for e in esito:
            f.write('senza %-8s  in comune %2d/%d  %s\n'
                    % (e['soggetto_escluso'], e['in_comune'], len(adottate),
                       'identico' if e['uguali']
                       else '-%s +%s' % (e['mancanti'], e['aggiunte'])))
        f.write('\n%d fold su %d identici, Jaccard medio %.3f\n'
                % (identici, len(esito), jac))
    print('\nscritti per_fold.json e per_fold.txt in risultati/dtw/')
    return 0


if __name__ == '__main__':
    sys.exit(main())
