"""
Il divario fra le due viste, misurato addestrando invece che descrivendo.

Perche' esiste
--------------
La tabella `tab:viste` del Capitolo 4 --- tre righe, addestra su una vista e
verifica sull'altra --- veniva dall'impianto a CINQUE soggetti, mentre la
misura geometrica che la spiega e' a dieci. Le due cose stavano nello stesso
paragrafo con provenienze diverse.

E c'era un secondo problema, piu' interessante. Il divario di F2 fra le viste
ha DUE cause ([ISS-134](../docs/ISSUES.md#iss-134)):

  1. la compressione prospettica --- una telecamera rialzata proietta una
     persona in piedi e una distesa in modo simile;
  2. lo stimatore di posa che su Camera2 PERDE chi cade e si aggancia a un
     astante, in 11 riprese su 50.

Finche' le due stanno insieme, il numero misura la loro somma e il testo puo'
solo dichiararlo. Rieseguendo le stesse tre righe con e senza le riprese
contaminate, la differenza fra le due esecuzioni e' la seconda causa, e cio'
che resta e' la prima.

Il ciclo e' quello di `addestra.py`, non un altro
------------------------------------------------
Stessa costruzione delle finestre, stesso scaler stimato sui soli fotogrammi
di addestramento del fold, stessa disciplina dei tre insiemi disgiunti per
persona, stessa soglia fissa dichiarata a priori. L'unica differenza e' che le
finestre di addestramento e quelle di verifica possono venire da telecamere
diverse.

Uso:
    python pipeline/viste_incrociate.py --csv feature_v3.csv
    python pipeline/viste_incrociate.py --csv feature_v3.csv --senza-contaminate
    python pipeline/viste_incrociate.py --csv feature_v3.csv --feature A3 \
        --escludi A3_h_pavimento
"""

import argparse
import os
import sys
import time

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
from src.dati import (COL_RIPRESA, COL_SOGGETTO, FEATURE, Scaler, carica,
                      costruisci_finestre)
from src.modelli import costruisci
from src.provenienza import scrivi_json
from src.valutazione import aggrega, metriche, probabilita_allarme

dec = lambda v, n=3: f'{v:.{n}f}'.replace('.', ',')

# Le tre combinazioni della tabella del Capitolo 4, nell'ordine in cui vi
# compaiono. La terza e' l'unica che vede entrambe le viste in addestramento.
COMBINAZIONI = [
    ('Camera1', (1,), 1),
    ('Camera1 -> Camera2', (1,), 2),
    ('Camera1+2 -> Camera2', (1, 2), 2),
    # la quarta non e' nella tabella del capitolo ma ne sostiene il risultato
    # controintuitivo: addestrare sulla vista POVERA e verificare su di essa
    ('Camera2', (2,), 2),
]


def riprese_contaminate(percorso=None):
    """
    Le riprese in cui lo stimatore passa a un'altra persona (ISS-134).

    Il criterio non e' ricostruito qui: si legge la colonna `salto_a` del CSV
    prodotto da `escursione_viste.py`, che segna il campione in cui l'angolo
    del tronco fa un salto piu' grande della soglia dichiarata. Rifare il
    criterio in due posti significherebbe averne due.
    """
    p = percorso or os.path.join(config.RISULTATI_DIR, 'laboratorio',
                                 'escursione_viste_10sog.csv')
    if not os.path.exists(p):
        return []
    d = pd.read_csv(p)
    return sorted(d.loc[d['salto_a'].notna(), 'name'].astype(str).tolist())


def finestre_per_camera(csv, colonne, modo, camere, escludi_riprese=()):
    """{camera: (X, y_train, y_allarme, soggetti, riprese, fotogrammi)}."""
    fuori = {}
    for cam in camere:
        df = carica(csv, camera=cam)
        if escludi_riprese:
            df = df[~df[COL_RIPRESA].isin(escludi_riprese)].reset_index(drop=True)
        X, y_tr, y_al, sog, rip = costruisci_finestre(df, colonne, modo)
        fuori[cam] = (X, y_tr, y_al, np.asarray(sog), np.asarray(rip), df)
    return fuori


def una_riga(dati, colonne, camere_train, camera_test, soglia=0.5,
             verboso=False):
    """
    Un LOSO completo con addestramento e verifica su viste eventualmente
    diverse. Ritorna (metriche per fold, nomi dei fold).
    """
    soggetti = sorted(set(dati[camera_test][3]))
    risultati, nomi, dettagli = [], [], []

    for i, test in enumerate(soggetti):
        val = soggetti[(i + 1) % len(soggetti)]
        train = [s for s in soggetti if s not in (test, val)]

        # Lo scaler vede i fotogrammi delle sole telecamere e dei soli
        # soggetti di addestramento: se vedesse anche la vista di verifica,
        # una parte del trasferimento sarebbe gia' avvenuta dentro la
        # normalizzazione invece che dentro il modello.
        frames = pd.concat([dati[c][5] for c in camere_train])
        sc = Scaler(colonne).fit(frames[frames[COL_SOGGETTO].isin(train)])

        Xtr, ytr = [], []
        Xva, yva = [], []
        for c in camere_train:
            X, y_tr, y_al, sog, _, _ = dati[c]
            m = np.isin(sog, train) & (y_tr >= 0)
            Xtr.append(sc.transform(X[m]))
            ytr.append(y_tr[m])
            mv = (sog == val) & (y_tr >= 0)
            Xva.append(sc.transform(X[mv]))
            yva.append(y_tr[mv])
        Xtr = np.concatenate(Xtr)
        ytr = np.concatenate(ytr)
        Xva = np.concatenate(Xva)
        yva = np.concatenate(yva)

        X, y_tr, y_al, sog, _, _ = dati[camera_test]
        mte = sog == test
        Xte, yte = sc.transform(X[mte]), y_al[mte]

        n_classi = 3 if int(y_tr.max()) > 1 else 2
        m = costruisci('foresta', (Xtr.shape[1], Xtr.shape[2]), n_classi)
        m.addestra(Xtr, ytr, Xva, yva, verboso=0)

        r = metriche(yte, probabilita_allarme(m.probabilita(Xte)), soglia)
        risultati.append(r)
        nomi.append(test)
        dettagli.append({'test': test, 'val': val, 'n_train': int(len(Xtr)),
                         'n_test': int(len(Xte)),
                         'positivi_test': int(yte.sum()),
                         **{k: r[k] for k in ('fbeta', 'recall', 'precision',
                                              'tp', 'fp', 'fn', 'tn')}})
        if verboso:
            print(f'    {test}: F2 {dec(r["fbeta"])}  '
                  f'FP {r["fp"]}  FN {r["fn"]}', flush=True)

    return risultati, nomi, dettagli


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='feature_v3.csv')
    ap.add_argument('--feature', default='A3',
                    help='bacino di grandezze (default A3, come la tabella)')
    ap.add_argument('--escludi', default='',
                    help='colonne da togliere dal bacino, separate da virgola')
    ap.add_argument('--modo', default='tre_classi')
    ap.add_argument('--soglia', type=float, default=0.5)
    ap.add_argument('--senza-contaminate', action='store_true',
                    dest='senza_contaminate',
                    help='esclude le riprese in cui lo stimatore cambia '
                         'persona (ISS-134), in addestramento e in verifica')
    ap.add_argument('--uscita', default=None)
    ap.add_argument('--verboso', action='store_true')
    a = ap.parse_args()

    fuori_col = {c.strip() for c in a.escludi.split(',') if c.strip()}
    colonne = [c for c in FEATURE[a.feature] if c not in fuori_col]

    contaminate = riprese_contaminate() if a.senza_contaminate else []
    t0 = time.time()

    print('=' * 78)
    print(f'VISTE INCROCIATE — {a.feature}: {len(colonne)} grandezze · '
          f'{a.modo} · soglia {dec(a.soglia, 2)} dichiarata a priori')
    if fuori_col:
        print(f'escluse dal bacino: {", ".join(sorted(fuori_col))}')
    if a.senza_contaminate:
        print(f'ESCLUSE {len(contaminate)} riprese in cui lo stimatore cambia '
              f'persona (ISS-134)')
    print('=' * 78)

    dati = finestre_per_camera(a.csv, colonne, a.modo, (1, 2), contaminate)
    for cam in (1, 2):
        X, y_tr, y_al, sog, rip, _ = dati[cam]
        print(f'camera {cam}: {len(X):,} finestre · {len(set(rip))} riprese · '
              f'{int(y_al.sum()):,} positive')
    print()

    righe = []
    for etichetta, tr, te in COMBINAZIONI:
        print(f'--- {etichetta}', flush=True)
        r, nomi, dettagli = una_riga(dati, colonne, tr, te, a.soglia,
                                     a.verboso)
        ag = aggrega(r)
        print(f'    F2 {dec(ag["fbeta_media"])} ± {dec(ag["fbeta_dev"])} · '
              f'richiamo {dec(ag["recall_media"])} · '
              f'FP {ag["fp_tot"]} · FN {ag["fn_tot"]}\n', flush=True)
        righe.append({'etichetta': etichetta,
                      'addestrata_su': [f'camera{c}' for c in tr],
                      'verificata_su': f'camera{te}',
                      'aggregato': ag, 'fold': dettagli})

    divario = righe[0]['aggregato']['fbeta_media'] - righe[1]['aggregato']['fbeta_media']
    recupero = righe[2]['aggregato']['fbeta_media'] - righe[1]['aggregato']['fbeta_media']

    print('=' * 78)
    print(f'divario fra le viste          {dec(divario)} di F2')
    print(f'recuperato addestrando su due {dec(recupero)}  '
          f'({dec(100 * recupero / divario, 0)}% del divario)')
    print('=' * 78)

    dst = a.uscita or os.path.join(
        config.RISULTATI_DIR, 'laboratorio',
        'viste_incrociate_10sog'
        + ('_senza_contaminate' if a.senza_contaminate else '') + '.json')
    scrivi_json(dst, {
        'csv': a.csv,
        'feature_set': a.feature,
        'colonne': colonne,
        'n_colonne': len(colonne),
        'colonne_escluse': sorted(fuori_col),
        'modo': a.modo,
        'soglia': a.soglia,
        'lunghezza_finestra': config.LUNGHEZZA_FINESTRA,
        'split': 'leave-one-subject-out; il soggetto successivo fa da '
                 'validation ed e escluso dall addestramento, come in '
                 'addestra.py',
        'architettura': 'foresta',
        'riprese_escluse': contaminate,
        'n_riprese_escluse': len(contaminate),
        'divario_f2': divario,
        'recupero_f2': recupero,
        'durata_s': round(time.time() - t0, 1),
        'righe': righe,
    })
    print(f'scritto: {os.path.relpath(dst, RADICE)}')


if __name__ == '__main__':
    main()
