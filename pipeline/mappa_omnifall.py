"""
Applica le etichette OmniFall ai nostri CSV di feature di UP-Fall.

Perche'
-------
Le nostre etichette per fotogramma hanno tre valori -- 0 normale, 1 caduta in
corso, 2 a terra -- e non distinguono una persona distesa DOPO UNA CADUTA da
una distesa PER SCELTA: `act11 = laying` vale 0, esattamente come camminare.
E' il negativo difficile del progetto, e finora era misurabile solo sulle
registrazioni domestiche -- che sono anche la fonte dei controesempi, quindi
contaminate -- oppure su UR-Fall.

OmniFall (2025) ha riannotato a mano otto dataset, UP-Fall compreso, con una
tassonomia a sedici classi che separa esattamente cio' che ci serviva:

    1|fall      l'atto di cadere, da qualunque stato precedente
    2|fallen    essere a terra DOPO una caduta
    5|lie_down  sdraiarsi INTENZIONALMENTE
    6|lying     essere disteso dopo esserci andato intenzionalmente

Sui soggetti 1-10 di camera 1 ci sono 1.705 secondi di `lying`: il negativo
difficile, dentro il dataset di addestramento.

Cosa NON cambia
---------------
Nulla della nostra pipeline. Le annotazioni sono etichette temporali sui video
che abbiamo gia': si applicano ai CSV di feature e basta. Continuiamo a
estrarre scheletri con MediaPipe, a lavorare su grandezze geometriche e a non
far uscire nessuna immagine. Cambia solo che le etichette diventano quelle di
un benchmark pubblicato, quindi confrontabili con i risultati di altri.

Il vincolo di allineamento
--------------------------
I segmenti OmniFall sono in SECONDI, i nostri dati in fotogrammi. La
conversione usa il frame rate del dataset (18 fps) e va verificata, non
assunta: lo script confronta la classe OmniFall con la nostra etichetta
esistente e stampa la matrice di accordo. Se l'allineamento fosse sbagliato di
mezzo secondo, `fall` e `fallen` non cadrebbero dove cadono le nostre 1 e 2.

Uso:
    python pipeline/mappa_omnifall.py --csv feature_v2.csv
    python pipeline/mappa_omnifall.py --csv ../DIP_PROJECT/dataset/processed/features/dataset_features_a3i_k31.csv --colonne-vecchie
"""

import argparse
import os
import re
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

NOMI_CLASSI = {
    0: 'walk', 1: 'fall', 2: 'fallen', 3: 'sit_down', 4: 'sitting',
    5: 'lie_down', 6: 'lying', 7: 'stand_up', 8: 'standing', 9: 'other',
}
# I due che il progetto non sapeva distinguere
DOPO_CADUTA = 2      # fallen
VOLONTARIO = {5, 6}  # lie_down, lying

_P_OMNI = re.compile(r'Subject(\d+)/Activity(\d+)/Trial(\d+)/.*Camera(\d+)',
                     re.IGNORECASE)
_P_NOSTRO = re.compile(r'sub(\d+)_act(\d+)_trial(\d+)_cam(\d+)', re.IGNORECASE)


def chiave_omni(p: str):
    m = _P_OMNI.search(str(p))
    return tuple(int(g) for g in m.groups()) if m else None


def chiave_nostra(v: str):
    m = _P_NOSTRO.search(str(v))
    return tuple(int(g) for g in m.groups()) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='feature_v2.csv')
    ap.add_argument('--annotazioni', default=os.path.join(
        os.path.dirname(RADICE), 'DIP_PROJECT', 'dataset', 'omnifall',
        'up_fall.csv'))
    ap.add_argument('--fps', type=float, default=config.FPS_DATASET)
    ap.add_argument('--col-ripresa', default=None,
                    help='default: `ripresa` se esiste, altrimenti `video_id`')
    ap.add_argument('--col-fotogramma', default=None)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()

    if not os.path.exists(a.annotazioni):
        sys.exit(f'mancano le annotazioni: {a.annotazioni}')
    ann = pd.read_csv(a.annotazioni)
    ann['chiave'] = ann.path.map(chiave_omni)
    ann = ann[ann.chiave.notna()]

    src = a.csv if os.path.exists(a.csv) else os.path.join(config.FEATURE_DIR, a.csv)
    if not os.path.exists(src):
        sys.exit(f'manca {src}')
    d = pd.read_csv(src)

    c_rip = a.col_ripresa or ('ripresa' if 'ripresa' in d.columns else 'video_id')
    c_fot = a.col_fotogramma or ('fotogramma' if 'fotogramma' in d.columns else 'frame')
    d['chiave'] = d[c_rip].map(chiave_nostra)
    d['t'] = d[c_fot] / a.fps

    print('=' * 78)
    print('ETICHETTE OMNIFALL APPLICATE A UP-FALL')
    print('=' * 78)
    print(f'CSV            {os.path.basename(src)}  ({len(d):,} righe)')
    print(f'annotazioni    {len(ann):,} segmenti')
    print(f'chiavi in comune: '
          f'{len(set(d.chiave.dropna()) & set(ann.chiave)):,} riprese')

    # Per ogni ripresa si scorrono i suoi segmenti e si marcano i fotogrammi
    # che ci cadono dentro. E' un intervallo per volta: i segmenti OmniFall
    # non si sovrappongono.
    d['classe_omnifall'] = -1
    per_chiave = {k: g for k, g in ann.groupby('chiave')}
    for k, idx in d.groupby('chiave').groups.items():
        seg = per_chiave.get(k)
        if seg is None:
            continue
        t = d.loc[idx, 't'].to_numpy()
        cls = np.full(len(t), -1, dtype=int)
        for _, r in seg.iterrows():
            cls[(t >= r.start) & (t < r.end)] = int(r.label)
        d.loc[idx, 'classe_omnifall'] = cls

    coperti = int((d.classe_omnifall >= 0).sum())
    print(f'fotogrammi coperti: {coperti:,}  ({100*coperti/len(d):.1f}%)')

    d['nome_omnifall'] = d.classe_omnifall.map(NOMI_CLASSI).fillna('—')
    d['dopo_caduta'] = (d.classe_omnifall == DOPO_CADUTA).astype(int)
    d['disteso_volontario'] = d.classe_omnifall.isin(VOLONTARIO).astype(int)

    print()
    print('distribuzione delle classi OmniFall:')
    vc = d.nome_omnifall.value_counts()
    for n, v in vc.items():
        print(f'   {n:<12} {v:8,}  {100*v/len(d):5.1f}%')

    if 'label' in d.columns:
        print()
        print('VERIFICA DELL ALLINEAMENTO — nostra etichetta contro OmniFall')
        print('(se i secondi fossero disallineati, `fall` e `fallen` non')
        print(' cadrebbero dove cadono le nostre 1 e 2)')
        t = pd.crosstab(d.label, d.nome_omnifall)
        print(t.to_string())
        for nostra, atteso in ((1, 'fall'), (2, 'fallen')):
            if nostra in t.index and atteso in t.columns:
                q = t.loc[nostra, atteso] / max(t.loc[nostra].sum(), 1)
                print(f'   nostra {nostra} -> «{atteso}» nel '
                      f'{100*q:.1f}% dei casi')

    n_dv = int(d.disteso_volontario.sum())
    print()
    print(f'NEGATIVO DIFFICILE reso misurabile: {n_dv:,} fotogrammi di persona')
    print(f'distesa o che si sdraia VOLONTARIAMENTE ({100*n_dv/len(d):.1f}%).')
    print('Nelle nostre etichette valevano 0, indistinguibili da camminare.')

    dst = a.out or src.replace('.csv', '_omnifall.csv')
    d.drop(columns=['chiave', 't']).to_csv(dst, index=False)
    print(f'\nsalvato: {dst}')


if __name__ == '__main__':
    main()
