# -*- coding: utf-8 -*-
"""
Le tre tabelle descrittive del Capitolo 3, ricalcolate dal CSV delle feature.

Perche' esiste
--------------
Tre tabelle del Capitolo 3 -- la durata delle fasi, l'autocorrelazione a un
passo, il rapporto fra le mediane -- riportavano numeri che **non comparivano
in alcun file di risultato** ([ISS-126](../docs/ISSUES.md)). Erano stati
calcolati una volta e trascritti. Non c'era ragione di dubitarne, ma non erano
rifacibili, ed e' la stessa forma di difetto di ISS-113.

Questo script li riproduce tutti e tre da `feature_v2.csv` e li salva, con la
provenienza, in `risultati/laboratorio/statistiche_cap3.json`.

    python pipeline/statistiche_cap3.py

Le tre definizioni, dichiarate
------------------------------
1. DURATA DELLE FASI. Per ogni ripresa di caduta della camera indicata si
   contano i fotogrammi consecutivi di ciascuna etichetta e si divide per
   `FPS_DATASET`. Si riportano mediana e decili 10 e 90 **sulle riprese**, non
   sui fotogrammi: la domanda e' quanto dura una caduta, non quanti fotogrammi
   di caduta esistono.

2. AUTOCORRELAZIONE A UN PASSO. Calcolata DENTRO ciascuna ripresa, sui soli
   fotogrammi con posa valida, e poi mediata pesando per il numero di
   fotogrammi. Calcolarla sull'intera colonna concatenata darebbe un valore
   diverso e privo di senso, perche' fra la fine di una ripresa e l'inizio
   della successiva non c'e' continuita' temporale.

3. RAPPORTO FRA LE MEDIANE. Per ogni grandezza dinamica, la mediana del valore
   assoluto sui fotogrammi di transizione (etichetta 1) divisa per quella sui
   fotogrammi di attivita' ordinaria (etichetta 0); e la stessa cosa per lo
   stato a terra (etichetta 2). Il valore assoluto perche' la direzione del
   movimento non e' la grandezza di interesse.
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if QUI not in sys.path:
    sys.path.insert(0, QUI)

import config                                              # noqa: E402
from src.provenienza import scrivi_json                    # noqa: E402

DINAMICHE = ['A3_d_angolo_tronco', 'A2_vel_ang_tronco', 'A3_hip_vel',
             'A2_testa_vel', 'A3_testa_vel_rel', 'A1_d_inclinazione']
INTEGRALI = ['A3_escursione', 'A3_percorso', 'A3_discesa',
             'A1_escursione', 'A2_percorso']
FASI = {0: 'in piedi / attivita ordinaria', 1: 'transizione (caduta in corso)',
        2: 'stato post-caduta (a terra)'}


def durate_fasi(d, fps):
    """Durata di ciascuna fase, ripresa per ripresa."""
    fuori = {}
    for etichetta, nome in FASI.items():
        durate = []
        for _, g in d.groupby(['soggetto', 'ripresa']):
            g = g.sort_values('fotogramma')
            m = (g['label'] == etichetta).to_numpy()
            if not m.any():
                continue
            # la fase puo' essere spezzata: si prende la corsa piu' lunga,
            # che e' l'evento, non la somma dei frammenti
            corsa = massima = 0
            for v in m:
                corsa = corsa + 1 if v else 0
                massima = max(massima, corsa)
            durate.append(massima / fps)
        if not durate:
            continue
        a = np.asarray(durate)
        fuori[nome] = {
            'n_riprese': int(a.size),
            'mediana_s': float(np.median(a)),
            'decile_10_s': float(np.percentile(a, 10)),
            'decile_90_s': float(np.percentile(a, 90)),
        }
    return fuori


def autocorrelazione(d, colonne):
    """Autocorrelazione a un passo, dentro ciascuna ripresa, media pesata."""
    fuori = {}
    for c in colonne:
        if c not in d.columns:
            continue
        num, den = 0.0, 0
        for _, g in d.groupby(['soggetto', 'ripresa']):
            v = g.sort_values('fotogramma')[c].to_numpy(float)
            v = v[np.isfinite(v)]
            if v.size < 3 or np.std(v) < 1e-12:
                continue
            r = float(np.corrcoef(v[:-1], v[1:])[0, 1])
            if not np.isfinite(r):
                continue
            num += r * v.size
            den += v.size
        if den:
            fuori[c] = round(num / den, 4)
    return fuori


def rapporti_mediane(d, colonne):
    """
    Mediana del valore assoluto per fase, e il rapporto su le attivita' ADL.

    LA BASE E' LA CATEGORIA `adl`, non i fotogrammi di etichetta 0. I due
    insiemi non coincidono: l'etichetta 0 comprende anche i fotogrammi che
    precedono la caduta dentro una ripresa di caduta, che sono una persona in
    piedi in attesa e non un'attivita' quotidiana.

    QUELLO CHE QUESTO CONFRONTO NON PUO' FARE. Il Capitolo 3 confrontava la
    transizione con lo SDRAIARSI VOLONTARIO, che e' il negativo che conta.
    `feature_v2.csv` non lo permette: porta due sole categorie, `adl` e
    `fall`, e gli identificativi delle undici attivita' di UP-Fall non sono
    stati conservati in estrazione. Quel confronto piu' fine era stato fatto
    sull'impianto precedente e non e' rifacibile da qui (ISS-128).
    """
    fuori = {}
    ordinarie = d[d['categoria'] == 'adl'] if 'categoria' in d.columns else \
        d[d['label'] == 0]
    for c in colonne:
        if c not in d.columns:
            continue
        base_v = ordinarie[c].abs()
        base_v = base_v[np.isfinite(base_v)]
        base = float(base_v.median()) if len(base_v) else float('nan')
        med = {}
        for etichetta in (1, 2):
            v = d.loc[d['label'] == etichetta, c].abs()
            v = v[np.isfinite(v)]
            med[etichetta] = float(v.median()) if len(v) else float('nan')
        utile = base if base > 1e-12 else float('nan')
        fuori[c] = {
            'mediana_adl': base,
            'mediana_transizione': med[1],
            'mediana_a_terra': med[2],
            'rapporto_transizione': round(med[1] / utile, 2),
            'rapporto_a_terra': round(med[2] / utile, 2),
        }
    return fuori


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default=os.path.join(
        config.FEATURE_DIR, 'feature_v2.csv'))
    ap.add_argument('--camera', type=int, default=1)
    ap.add_argument('--out', default=os.path.join(
        config.RISULTATI_DIR, 'laboratorio', 'statistiche_cap3.json'))
    a = ap.parse_args()

    d = pd.read_csv(a.csv)
    d = d[d['camera'] == a.camera]
    valide = d[d['ha_posa'] == 1] if 'ha_posa' in d.columns else d

    # le durate si misurano sulle riprese che contengono una caduta
    con_caduta = d.groupby(['soggetto', 'ripresa'])['label'].transform(
        lambda s: (s == 1).any())
    cadute = d[con_caduta]

    fuori = {
        'csv': os.path.basename(a.csv),
        'camera': a.camera,
        'fps_dataset': config.FPS_DATASET,
        'fotogrammi': int(len(d)),
        'fotogrammi_posa_valida': int(len(valide)),
        'quota_posa_valida': round(len(valide) / max(len(d), 1), 4),
        'riprese': int(d.groupby(['soggetto', 'ripresa']).ngroups),
        'riprese_con_caduta': int(cadute.groupby(['soggetto', 'ripresa']).ngroups),
        'soggetti': int(d['soggetto'].nunique()),
        'durate_fasi': durate_fasi(cadute, config.FPS_DATASET),
        'autocorrelazione_1_passo': {
            'dinamiche': autocorrelazione(valide, DINAMICHE),
            'integrali': autocorrelazione(valide, INTEGRALI)},
        'rapporti_mediane': rapporti_mediane(valide, DINAMICHE + INTEGRALI),
        'nota': ('Le tre definizioni sono nella docstring dello script. La '
                 'durata e la CORSA PIU LUNGA della fase dentro la ripresa, '
                 'non la somma dei frammenti; l autocorrelazione e calcolata '
                 'dentro ciascuna ripresa e mediata pesando per i fotogrammi.'),
    }

    dec = lambda v, n=3: f'{v:.{n}f}'.replace('.', ',')

    print('=' * 74)
    print('STATISTICHE DESCRITTIVE DEL CAPITOLO 3')
    print('=' * 74)
    print(f"  {fuori['fotogrammi']:,} fotogrammi, {fuori['riprese']} riprese, "
          f"{fuori['soggetti']} soggetti, camera {a.camera}")
    print(f"  pose valide {100 * fuori['quota_posa_valida']:.2f}%")
    print()
    print('  DURATA DELLE FASI (riprese con caduta: '
          f"{fuori['riprese_con_caduta']})")
    print(f"    {'fase':<34}{'mediana':>10}{'d10':>9}{'d90':>9}")
    for nome, v in fuori['durate_fasi'].items():
        print(f"    {nome:<34}{dec(v['mediana_s'],2):>10}"
              f"{dec(v['decile_10_s'],2):>9}{dec(v['decile_90_s'],2):>9}")
    print()
    print('  AUTOCORRELAZIONE A UN PASSO')
    for gruppo, valori in fuori['autocorrelazione_1_passo'].items():
        print(f'    {gruppo}:')
        for c, v in valori.items():
            print(f'      {c:<26}{dec(v):>9}')
    print()
    print('  RAPPORTO FRA LE MEDIANE (base: categoria adl)')
    print(f"    {'grandezza':<26}{'transizione':>14}{'a terra':>11}")
    for c, v in fuori['rapporti_mediane'].items():
        print(f"    {c:<26}{dec(v['rapporto_transizione'],1)+'x':>14}"
              f"{dec(v['rapporto_a_terra'],1)+'x':>11}")

    scrivi_json(a.out, fuori)
    print()
    print('salvato: ' + os.path.relpath(a.out, QUI))


if __name__ == '__main__':
    main()
