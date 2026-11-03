"""
La latenza di rilevamento, misurata dove le etichette lo permettono.

Perche' esiste
--------------
Sulle sessioni domestiche la latenza NON e' misurabile, ed e' dimostrato: le
cadute sono annotate al minuto mentre la grandezza da misurare vale pochi
secondi, quindi l'incertezza sull'istante vero e' fino a sessanta volte la
quantita' cercata ([ISS-108](../docs/ISSUES.md)). Da li' il lavoro concludeva
che la latenza non si misura, e riportava solo il suo limite inferiore
analitico: 3,778 s, dominato per il 72,6% dal riempimento della finestra.

Ma quella conclusione vale per il CAMPO, non per il laboratorio. In UP-Fall
l'etichetta e' per fotogramma: l'istante in cui la caduta comincia e' noto a
1/18 di secondo. La latenza si misura quindi esattamente, su cinquanta cadute
invece che su cinque, e il numero che ne esce e' un limite inferiore empirico
al posto di uno analitico.

Che cosa misura, esattamente
----------------------------
Per ogni ripresa di caduta:

    inizio  = primo fotogramma etichettato «caduta in corso»
    allarme = fine della k-esima finestra consecutiva sopra soglia
    latenza = allarme - inizio

L'allarme e' collocato alla FINE della finestra perche' e' li' che la decisione
esiste: prima, il classificatore non ha ancora i 22 campioni che gli servono.

E la misura si ripete al variare della persistenza k, che e' il parametro di
cui il progetto non ha mai giustificato il valore: k=5 e' ereditato, non
derivato. La curva (k -> richiamo, latenza) e' cio' che serve per sceglierlo.

I punteggi non vengono ricalcolati: si rileggono quelli salvati dalla LOSO, e
le finestre si ricostruiscono con lo stesso codice che le ha prodotte. Le
numerosita' devono coincidere fold per fold, ed e' il controllo che rende
l'allineamento verificabile invece che congetturale.

Uso:
    python pipeline/latenza_laboratorio.py
    python pipeline/latenza_laboratorio.py --run foresta_tre_classi_DTW_cam1_L22
"""

import argparse
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

import config
from src.dati import (COL_FOTOGRAMMA, COL_LABEL, COL_RIPRESA, COL_SOGGETTO,
                      _tratti_continui, carica)
from src.etichettatura import etichetta_finestra
from src.provenienza import scrivi_json

dec = lambda v, n=2: f'{v:.{n}f}'.replace('.', ',')


def finestre_con_fotogramma(df, modo='tre_classi', lunghezza=None, passo=None,
                            frame_step=None):
    """
    Le stesse finestre di `costruisci_finestre`, ma con il FOTOGRAMMA di fine.

    Il ciclo e' replicato invece che importato perche' `costruisci_finestre`
    non restituisce gli indici temporali: sono inutili all'addestramento e qui
    sono tutto. L'ordine dei gruppi e dei tratti e' identico --- stesso
    `groupby` ordinato, stesso passo --- quindi la n-esima finestra prodotta
    qui e' la n-esima finestra usata in addestramento, e il controllo delle
    numerosita' lo verifica.
    """
    L = lunghezza or config.LUNGHEZZA_FINESTRA
    passo = passo or config.PASSO_FINESTRA
    step = frame_step if frame_step is not None else config.FRAME_STEP

    sog, rip, y_al, f_fine, f_inizio = [], [], [], [], []
    for (s, v), g in df.groupby([COL_SOGGETTO, COL_RIPRESA], sort=True):
        g = g.sort_values(COL_FOTOGRAMMA)
        for tratto in _tratti_continui(g):
            t = tratto.iloc[::step] if step > 1 else tratto
            if len(t) < L:
                continue
            lab = t[COL_LABEL].to_numpy(np.int8)
            fot = t[COL_FOTOGRAMMA].to_numpy(np.int64)
            for i in range(0, len(t) - L + 1, passo):
                fin = lab[i:i + L]
                y_al.append(int(etichetta_finestra(fin, 'caduta') == 1))
                sog.append(s)
                rip.append(v)
                f_inizio.append(fot[i])
                f_fine.append(fot[i + L - 1])
    return pd.DataFrame({'soggetto': sog, 'ripresa': rip, 'y_allarme': y_al,
                         'f_inizio': f_inizio, 'f_fine': f_fine})


def punteggi_per_soggetto(percorso):
    """{soggetto: array dei punteggi}, dai file `.npz` della LOSO."""
    z = np.load(percorso, allow_pickle=True)
    fold = [str(s) for s in z['fold_test']]
    return {s: np.asarray(z[f'p_test_{i}'], float) for i, s in enumerate(fold)}


def inizio_caduta(df):
    """{ripresa: primo fotogramma etichettato «caduta in corso»}."""
    c = df[df[COL_LABEL] == 1]
    return c.groupby(COL_RIPRESA)[COL_FOTOGRAMMA].min().to_dict()


def allarme(sopra, k):
    """Indice della finestra in cui scatta l'allarme, o None."""
    corsa = 0
    for i, s in enumerate(sopra):
        corsa = corsa + 1 if s else 0
        if corsa >= k:
            return i
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='feature_v3.csv')
    ap.add_argument('--run', default='foresta_tre_classi_DTWH_cam1_L22')
    ap.add_argument('--camera', type=int, default=1)
    ap.add_argument('--soglia', type=float, default=0.5)
    ap.add_argument('--fps', type=float, default=None,
                    help='fotogrammi al secondo del dataset (default da config)')
    ap.add_argument('--persistenze', default='1,2,3,4,5,7,10')
    a = ap.parse_args()

    fps = a.fps or config.FPS_DATASET
    ks = [int(x) for x in a.persistenze.split(',')]

    df = carica(a.csv, camera=a.camera)
    fin = finestre_con_fotogramma(df)
    p = punteggi_per_soggetto(os.path.join(
        config.RISULTATI_DIR, 'addestramento', f'punteggi_{a.run}.npz'))
    inizio = inizio_caduta(df)

    print('=' * 88)
    print(f'LATENZA DI RILEVAMENTO IN LABORATORIO — {a.run}')
    print(f'camera {a.camera} · soglia {dec(a.soglia)} · {fps:.0f} fps · '
          f'{len(inizio)} riprese con caduta annotata')
    print('=' * 88)

    # allineamento: la n-esima finestra ricostruita deve essere la n-esima
    # finestra usata in addestramento, per ogni soggetto
    for s, punteggi in p.items():
        n = int((fin.soggetto == s).sum())
        if n != len(punteggi):
            sys.exit(f'disallineamento su {s}: {n} finestre ricostruite contro '
                     f'{len(punteggi)} punteggi salvati. Senza allineamento '
                     f'ogni latenza sarebbe attribuita alla ripresa sbagliata.')
    print(f'allineamento verificato su {len(p)} soggetti\n')

    fin = fin.copy()
    fin['punteggio'] = np.nan
    for s, punteggi in p.items():
        fin.loc[fin.soggetto == s, 'punteggio'] = punteggi
    fin = fin.dropna(subset=['punteggio'])
    fin['sopra'] = fin.punteggio >= a.soglia

    righe = []
    print(f"{'k':>3}{'riprese con allarme':>22}{'richiamo':>10}"
          f"{'latenza mediana':>18}{'p90':>9}{'peggiore':>10}")
    print('-' * 88)
    for k in ks:
        lat, senza = [], 0
        for r, t0 in inizio.items():
            g = fin[fin.ripresa == r].sort_values('f_fine')
            if g.empty:
                continue
            i = allarme(g.sopra.to_numpy(), k)
            if i is None:
                senza += 1
                continue
            lat.append((g.f_fine.to_numpy()[i] - t0) / fps)
        lat = np.array(lat, float)
        n = len(lat) + senza
        righe.append({'persistenza': k, 'riprese': n, 'con_allarme': len(lat),
                      'richiamo': len(lat) / n if n else 0.0,
                      'latenza_mediana_s': float(np.median(lat)) if len(lat) else None,
                      'latenza_p90_s': float(np.percentile(lat, 90)) if len(lat) else None,
                      'latenza_max_s': float(lat.max()) if len(lat) else None,
                      'latenza_min_s': float(lat.min()) if len(lat) else None})
        print(f"{k:>3}{len(lat):>13} su {n:<6}{dec(len(lat)/n):>10}"
              f"{dec(np.median(lat)) + ' s':>18}{dec(np.percentile(lat, 90)):>9}"
              f"{dec(lat.max()):>10}")

    print('-' * 88)
    print('La latenza e\' misurata dal primo fotogramma etichettato «caduta in')
    print('corso» alla FINE della finestra che fa scattare l\'allarme: e\' li\'')
    print('che la decisione esiste. Valori negativi sono possibili e sono')
    print('informativi: l\'allarme scatta PRIMA che l\'annotazione dichiari la')
    print('caduta, perche\' la finestra vede gia\' il movimento che la precede.')

    dst = os.path.join(config.RISULTATI_DIR, 'laboratorio',
                       f'latenza_laboratorio_{a.run}.json')
    scrivi_json(dst, {
        'run': a.run, 'csv': a.csv, 'camera': a.camera, 'soglia': a.soglia,
        'fps_dataset': fps,
        'lunghezza_finestra': config.LUNGHEZZA_FINESTRA,
        'passo_finestra': config.PASSO_FINESTRA,
        'frame_step': config.FRAME_STEP,
        'definizione': 'latenza = fine della finestra che fa scattare l allarme '
                       '- primo fotogramma etichettato caduta in corso',
        'n_riprese_con_caduta': len(inizio),
        'per_persistenza': righe,
    })
    print(f'\nscritto: {os.path.relpath(dst, RADICE)}')


if __name__ == '__main__':
    main()
