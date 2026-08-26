"""
Ricostruisce le etichette di UR-Fall con la semantica di UP-Fall.

Il problema
-----------
Le due annotazioni sono di NATURA diversa, e finora sono state confrontate come
se fossero la stessa cosa.

    UP-Fall   fase dell'EVENTO    0 normale · 1 sta cadendo · 2 a terra dopo
    UR-Fall   POSTURA            -1 non disteso · 0 in transizione · 1 disteso

`label = 1` significa quindi cose diverse: in UP-Fall e' la caduta in corso, in
UR-Fall e' la persona distesa -- e in una ripresa di attivita' quotidiana
significa una persona che si e' sdraiata di proposito.

Cosa era andato perso
---------------------
Il CSV processato del progetto ha due sole classi. Confrontando riga per riga
con le annotazioni originali (allineate: l'originale numera da 1, il nostro da
0) la conversione risulta:

    originale -1  ->  nostro 0    99%
    originale  0  ->  nostro 1    76%   e nostro 0 il 24%
    originale +1  ->  nostro 1   100%

La classe di transizione e' stata quindi spalmata sulle altre due senza una
regola, e le 1.470 pose "disteso" delle riprese ADL -- persone che si sdraiano
di proposito, cioe' esattamente il negativo difficile del progetto -- sono
state forzate a 0 insieme a tutto il resto.

Cosa produce questo script
--------------------------
Un CSV con le stesse feature e tre colonne nuove:

    label        rietichettata nella semantica di UP-Fall
                   ripresa di caduta:  -1 -> 0 · 0 -> 1 (transizione) · 1 -> 2 (a terra)
                   ripresa ADL:        tutto -> 0, perche' nessuna e' una caduta
    postura      l'etichetta originale, conservata: -1 / 0 / 1
    disteso_volontario   1 sui fotogrammi di ADL con postura 0 o 1

L'ultima colonna e' la ragione principale per cui vale la pena fare questo
lavoro: permette di misurare il tasso di falsi allarmi SUI SOLI casi difficili,
con dati esterni al progetto invece che sulle sole registrazioni domestiche.

Uso:
    python scripts/rietichetta_urfall.py
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_STORICO = os.path.join(os.path.dirname(RADICE), 'DIP_PROJECT')
ANNOT = os.path.join(_STORICO, 'dataset', 'ur_fall', 'raw', 'annotazioni')
FEAT = os.path.join(_STORICO, 'dataset', 'ur_fall', 'processed', 'features')

dec = lambda v, n=1: f'{v:.{n}f}'.replace('.', ',')


def annotazioni() -> pd.DataFrame:
    """Le due tabelle originali, unite e con la categoria."""
    pezzi = []
    for nome, cat in (('urfall-cam0-falls.csv', 'fall'),
                      ('urfall-cam0-adls.csv', 'adl')):
        p = os.path.join(ANNOT, nome)
        if not os.path.exists(p):
            sys.exit(f'manca {p}\n'
                     f'scaricare da http://fenix.ur.edu.pl/~mkepski/ds/data/{nome}')
        d = pd.read_csv(p, header=None, usecols=[0, 1, 2],
                        names=['seq', 'frame_o', 'postura'])
        d['cat_ann'] = cat
        pezzi.append(d)
    return pd.concat(pezzi, ignore_index=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='body_features_bodycentric.csv')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()

    src = os.path.join(FEAT, a.csv)
    dst = a.out or src.replace('.csv', '_3classi.csv')
    if not os.path.exists(src):
        sys.exit(f'manca {src}')

    ann = annotazioni()
    df = pd.read_csv(src)
    df['seq'] = df.video_id.str.replace('-cam0-rgb', '', regex=False)
    # l'originale numera i fotogrammi da 1, il nostro da 0
    df['frame_o'] = df.frame + 1

    m = df.merge(ann[['seq', 'frame_o', 'postura']], on=['seq', 'frame_o'],
                 how='left')
    trovati = int(m.postura.notna().sum())
    print('=' * 78)
    print('UR-FALL — rietichettatura nella semantica di UP-Fall')
    print('=' * 78)
    print(f'righe                 {len(m):,}')
    print(f'annotazione trovata   {trovati:,}  ({dec(100*trovati/len(m))}%)')
    if trovati < len(m):
        print(f'  senza annotazione: {len(m)-trovati:,} -> restano a etichetta 0')

    vecchia = m['label'].copy()
    post = m.postura

    # Semantica di UP-Fall. Nelle riprese ADL nulla e' una caduta, qualunque
    # sia la postura: una persona distesa sul pavimento per scelta e' un
    # NEGATIVO, ed e' proprio il caso che il sistema deve non confondere.
    nuova = pd.Series(0, index=m.index, dtype=int)
    caduta = m['category'] == 'fall'
    nuova[caduta & (post == 0)] = 1      # transizione: sta cadendo
    nuova[caduta & (post == 1)] = 2      # stato: a terra dopo la caduta

    m['label'] = nuova
    m['disteso_volontario'] = ((m['category'] == 'adl') &
                               (post.isin([0, 1]))).astype(int)

    print()
    print('etichetta nuova per categoria:')
    print(pd.crosstab(m['category'], m.label).to_string())
    print()
    print('confronto con la vecchia etichetta:')
    print(pd.crosstab(vecchia.rename('vecchia'),
                      m.label.rename('nuova')).to_string())
    print()
    n_dv = int(m.disteso_volontario.sum())
    print(f'NEGATIVI DIFFICILI — persona distesa o in procinto di sdraiarsi')
    print(f'in una ripresa di attivita quotidiana: {n_dv:,} fotogrammi '
          f'({dec(100*n_dv/len(m))}% del dataset)')
    print('Sono il caso che il sistema deve non confondere con una caduta, ed')
    print('erano tutti forzati a 0 senza distinzione dalle altre attivita.')

    m = m.drop(columns=['seq', 'frame_o'])
    m.to_csv(dst, index=False)
    print()
    print(f'salvato: {os.path.relpath(dst, RADICE)}')
    print(f'colonne nuove: label (rietichettata), postura (originale), '
          f'disteso_volontario')


if __name__ == '__main__':
    main()
