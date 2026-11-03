# -*- coding: utf-8 -*-
"""
La scelta di K rifatta dentro ogni fold LOSO, per misurare il leakage.

Perche' esiste
--------------
`K_INTEGRALI = 31` non e' stato fissato a priori. `config.py:108` rimanda a
EXP-053 del progetto storico, che si intitola «La finestra di accumulazione era
scelta, non ottimizzata»: il valore di partenza era 9, e 31 e' il risultato di
una scansione su cinque lunghezze. I numeri che hanno deciso vengono da due
insiemi, ed entrambi pongono un problema:

  1. la colonna «F2 laboratorio» della scansione e' misurata SUI FOLD DI PROVA,
     quindi la scelta di K ha visto i soggetti lasciati fuori;
  2. il pareggio fra 31 e 45 e' stato rotto sul richiamo di campo, che il
     Capitolo 5 riporta poi come risultato.

E' la stessa malattia della selezione DTW, ed e' dichiarata in `sec:leakage`
(ISS-178). Dichiararla non basta pero' a dirne l'entita'. Questo script la
misura, come `dtw_per_fold.py` ha fatto per le grandezze.

Il protocollo annidato
----------------------
Per ciascun soggetto `s` lasciato fuori:

    1. si mette `s` da parte e non lo si guarda piu';
    2. si sceglie K con un LOSO INTERNO sui soli nove soggetti rimasti,
       prendendo quello con l'F-beta medio piu' alto;
    3. si addestra sui rimasti con quel K e si valuta su `s`, una volta sola.

E' il procedimento che il Capitolo 3 enuncia. Il confronto e' contro la
procedura effettivamente seguita, cioe' K = 31 fisso in tutti i fold.

Il controllo che viene prima
----------------------------
Come in `dtw_per_fold.py`, prima dei dieci fold si verifica che il dataset a
K = 31 ricostruito dal CSV multi-K riproduca `feature_v5.csv` sulle colonne che
contano. Se non lo riproduce si starebbero confrontando due cose diverse, e lo
script si ferma.

Che cosa si puo' concludere, e che cosa no
------------------------------------------
Se i dieci fold scelgono tutti K = 31, il leakage non ha cambiato nulla e lo si
puo' dire con un numero. Se scelgono valori diversi, la differenza fra la
prestazione con il K scelto dentro il fold e quella con K = 31 e' la misura
del problema --- ed e' un limite inferiore, perche' la scelta di campo resta
comunque fuori da questo conto.

Uso
---
    python pipeline/k_per_fold.py
    python pipeline/k_per_fold.py --controlla        (solo il controllo)

Scrive `risultati/dtw/k_per_fold.json` e `.txt`.
"""

import argparse
import json
import os
import sys
import time

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RADICE not in sys.path:
    sys.path.insert(0, RADICE)

import numpy as np
import pandas as pd

import config
from src.dati import carica, feature_dtw, fold_loso
from src.modelli import costruisci
from src.valutazione import metriche, probabilita_allarme

INTEGRALI = ['A1_escursione', 'A1_percorso', 'A1_discesa',
             'A2_escursione', 'A2_percorso', 'A2_discesa',
             'A3_escursione', 'A3_percorso', 'A3_discesa']


def dec(x, n=3):
    return f'{x:.{n}f}'.replace('.', ',')


def dataset_a_k(multi: pd.DataFrame, k: int) -> pd.DataFrame:
    """
    Il dataset come se fosse stato estratto a quel K.

    Le colonne integrali `*_k{K}` prendono il nome senza suffisso; le altre
    non dipendono da K e restano come sono. Le colonne degli altri K spariscono,
    cosi' nessun passaggio successivo puo' leggerle per sbaglio.
    """
    d = multi.copy()
    for c in INTEGRALI:
        d[c] = d[f'{c}_k{k}']
    via = [c for c in d.columns
           if any(c.startswith(f'{i}_k') for i in INTEGRALI)]
    return d.drop(columns=via)


def loso_foresta(df, colonne, modo, soggetti=None, soglia=0.5):
    """
    Un LOSO con la foresta, eventualmente ristretto a un sottoinsieme di
    soggetti. Ritorna l'elenco degli F-beta per fold.

    La foresta e' la stessa architettura con cui la scansione originale e'
    stata condotta (EXP-053), e costa una decina di secondi per LOSO: e' cio'
    che rende praticabile un protocollo annidato.
    """
    d = df if soggetti is None else df[df.soggetto.isin(soggetti)]
    fuori = []
    for f in fold_loso(d, colonne, modo):
        m = costruisci('foresta', (config.LUNGHEZZA_FINESTRA, len(colonne)),
                       f.n_classi)
        m.addestra(f.X_train, f.y_train)
        p = probabilita_allarme(m.probabilita(f.X_test))
        r = metriche(f.y_test, p, soglia)
        r['soggetto'] = f.soggetto_test
        fuori.append(r)
    return fuori


def controllo_riproduzione(multi, colonne, modo):
    """A K=31 il CSV multi-K deve dare le stesse colonne di feature_v5."""
    print('CONTROLLO DI RIPRODUZIONE')
    print('-' * 74)
    d31 = dataset_a_k(multi, config.K_INTEGRALI)
    v5 = carica('feature_v5.csv', camera=1)

    chiavi = ['ripresa', 'fotogramma']
    a = d31.sort_values(chiavi).reset_index(drop=True)
    b = v5[v5.ripresa.isin(set(d31.ripresa))].sort_values(chiavi).reset_index(drop=True)

    if len(a) != len(b):
        sys.exit(f'  righe diverse: multi-K {len(a)}, feature_v5 {len(b)}')

    peggio = []
    for c in colonne:
        s = float(np.abs(a[c].values - b[c].values).max())
        peggio.append((s, c))
    peggio.sort(reverse=True)

    print(f'  riprese {a.ripresa.nunique()}, fotogrammi {len(a):,}, '
          f'colonne confrontate {len(colonne)}')
    for s, c in peggio[:3]:
        print(f'  {c:<22} scarto massimo {s:.3e}')

    if peggio[0][0] > 1e-9:
        sys.exit('  FERMATO: a K=31 il dataset ricostruito non riproduce '
                 'feature_v5. Il confronto per fold non significherebbe nulla.')
    print('  riproduce esattamente feature_v5 sulle colonne adottate\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='feature_k_multiplo.csv')
    ap.add_argument('--modo', default='tre_classi')
    ap.add_argument('--soglia', type=float, default=0.5,
                    help='la soglia fissa dichiarata a priori (DEC-105)')
    ap.add_argument('--controlla', action='store_true',
                    help='esegue il solo controllo di riproduzione')
    a = ap.parse_args()

    multi = carica(a.csv, camera=1)
    kappa = sorted({int(c.split('_k')[-1]) for c in multi.columns
                    if any(c.startswith(f'{i}_k') for i in INTEGRALI)})
    colonne = feature_dtw()

    print('=' * 74)
    print(f'SCELTA DI K DENTRO IL FOLD — K provati: {kappa}')
    print('=' * 74)
    print(f'  adottato    K = {config.K_INTEGRALI}')
    print(f'  colonne     {len(colonne)} (selezione DTW)')
    print(f'  soggetti    {multi.soggetto.nunique()}')
    print(f'  modo        {a.modo}\n')

    controllo_riproduzione(multi, colonne, a.modo)
    if a.controlla:
        return

    # I dataset a ciascun K, costruiti una volta sola.
    per_k = {k: dataset_a_k(multi, k) for k in kappa}
    soggetti = sorted(multi.soggetto.unique())

    t0 = time.time()
    righe = []
    for s in soggetti:
        rimasti = [x for x in soggetti if x != s]

        # --- 2. K scelto con un LOSO interno sui soli rimasti ---
        interno = {}
        for k in kappa:
            r = loso_foresta(per_k[k], colonne, a.modo,
                             soggetti=rimasti, soglia=a.soglia)
            interno[k] = float(np.mean([x['fbeta'] for x in r]))
        k_scelto = max(interno, key=interno.get)

        # --- 3. valutazione su s, con il K scelto e con quello adottato ---
        def su_s(k, soglia=a.soglia):
            for f in fold_loso(per_k[k], colonne, a.modo):
                if f.soggetto_test != s:
                    continue
                m = costruisci('foresta',
                               (config.LUNGHEZZA_FINESTRA, len(colonne)),
                               f.n_classi)
                m.addestra(f.X_train, f.y_train)
                p = probabilita_allarme(m.probabilita(f.X_test))
                return metriche(f.y_test, p, soglia)
            raise RuntimeError(f'fold {s} non trovato')

        r_scelto = su_s(k_scelto)
        r_adottato = (r_scelto if k_scelto == config.K_INTEGRALI
                      else su_s(config.K_INTEGRALI))

        righe.append({
            'soggetto': s,
            'k_scelto': k_scelto,
            'interno': interno,
            'fbeta_k_scelto': r_scelto['fbeta'],
            'fbeta_k_adottato': r_adottato['fbeta'],
            'fn_k_scelto': r_scelto['fn'], 'fn_k_adottato': r_adottato['fn'],
            'fp_k_scelto': r_scelto['fp'], 'fp_k_adottato': r_adottato['fp'],
        })
        print(f'  {s:<12} K interno = {k_scelto:<3} '
              f'F2 su {s}: {dec(r_scelto["fbeta"])} con K scelto, '
              f'{dec(r_adottato["fbeta"])} con K=31   '
              f'({(time.time()-t0)/60:.1f} min)', flush=True)

    # ------------------------------------------------------------ riepilogo
    n_conformi = sum(1 for r in righe if r['k_scelto'] == config.K_INTEGRALI)
    med_scelto = float(np.mean([r['fbeta_k_scelto'] for r in righe]))
    med_adottato = float(np.mean([r['fbeta_k_adottato'] for r in righe]))

    print()
    print('=' * 74)
    print(f'fold che scelgono K = {config.K_INTEGRALI}: '
          f'{n_conformi} su {len(righe)}')
    print(f'F2 medio con K scelto dentro il fold : {dec(med_scelto)}')
    print(f'F2 medio con K = {config.K_INTEGRALI} fisso'
          f'{"":14}: {dec(med_adottato)}')
    print(f'differenza                           : '
          f'{dec(med_adottato - med_scelto, 4)}')
    print('=' * 74)
    print()
    print('Come si legge. Una differenza POSITIVA significa che il K adottato')
    print('rende piu\' di quello scelto senza guardare il soggetto di prova:')
    print('e\' la quota di prestazione che il leakage spiega. Una differenza')
    print('negativa o nulla significa che la scelta a posteriori non ha')
    print('aggiunto nulla, e che il valore adottato regge da solo.')

    conteggio_k = {int(k): sum(1 for r in righe if r['k_scelto'] == k)
                   for k in kappa}
    fuori = {
        'csv': a.csv, 'modo': a.modo, 'architettura': 'foresta',
        'k_adottato': config.K_INTEGRALI, 'k_provati': kappa,
        'soglia': a.soglia, 'colonne': colonne,
        'fold_conformi': n_conformi, 'n_fold': len(righe),
        'k_scelti': conteggio_k,
        'fbeta_medio_k_scelto': med_scelto,
        'fbeta_medio_k_adottato': med_adottato,
        'differenza': med_adottato - med_scelto,
        'fold': righe,
    }
    dst = os.path.join(config.RISULTATI_DIR, 'dtw')
    os.makedirs(dst, exist_ok=True)
    with open(os.path.join(dst, 'k_per_fold.json'), 'w', encoding='utf-8') as f:
        json.dump(fuori, f, ensure_ascii=False, indent=1)
    print(f'\nsalvato in {os.path.join("risultati", "dtw", "k_per_fold.json")}')


if __name__ == '__main__':
    main()
