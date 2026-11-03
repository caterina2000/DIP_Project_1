# -*- coding: utf-8 -*-
"""
Quanto separa l'altezza del bacino dal pavimento, nelle due viste.

Perche' esiste
--------------
Il Capitolo 4 riporta che sulla vista laterale la separazione fra le mediane
di caduta e non caduta vale «+1,43 lunghezze di tronco» e sulla frontale
rialzata «-0,18». I due valori compaiono nel testo in due forme diverse
(+1,43 e +1,45) e non si riproducono da `feature_v5.csv`: nessuno script del
progetto li calcola, e non compaiono in `docs/NUMERI_PER_LA_TESI.txt`.

Questo script li ricalcola, in modo che il numero riportato sia difendibile.
Stampa la mediana di `A3_h_pavimento` per classe e per telecamera, e la loro
differenza, sui soli fotogrammi con posa valida.

La convenzione del segno va dichiarata, perche' e' la sorgente dell'ambiguita':
qui la separazione e' `mediana(non caduta) - mediana(caduta)`, cioe' positiva
quando chi non e' caduto sta piu' in alto --- che e' il verso in cui la
grandezza e' informativa.

Uso
---
    python pipeline/altezza_pavimento_viste.py
    python pipeline/altezza_pavimento_viste.py --solo-stato
"""
import argparse
import json
import os
import sys

import numpy as np

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, QUI)

from src import dati                                        # noqa: E402

FUORI = os.path.join(QUI, 'risultati', 'laboratorio',
                     'altezza_pavimento_viste.json')
VISTE = {1: 'Camera 1, laterale', 2: 'Camera 2, frontale rialzata'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='feature_v5.csv')
    ap.add_argument('--solo-stato', action='store_true',
                    help='positiva la sola etichetta 2 (persona a terra) '
                         'invece di 1 e 2 insieme')
    ap.add_argument('--fuori', default=FUORI)
    a = ap.parse_args()

    # NON si usa dati.carica(): quella funzione filtra gia' alla camera 1,
    # e qui servono entrambe le viste. Si legge il CSV cosi com e.
    import pandas as pd
    percorso = os.path.join(QUI, 'dataset', 'processed', 'features', a.csv)
    df = pd.read_csv(percorso, low_memory=False)
    df = df[df.ha_posa == 1]

    positiva = (df.label == 2) if a.solo_stato else (df.label > 0)
    quale = 'solo stato post-caduta' if a.solo_stato else 'transizione e stato'

    print('csv        %s, soli fotogrammi con posa valida' % a.csv)
    print('positiva   %s' % quale)
    print('segno      mediana(non caduta) - mediana(caduta)')
    print()
    print('%-30s %10s %10s %12s' % ('vista', 'caduta', 'non cad.', 'separaz.'))

    fuori = []
    for cam, nome in sorted(VISTE.items()):
        x = df[df.camera == cam]
        if x.empty:
            continue
        cad = float(x[positiva.reindex(x.index, fill_value=False)]
                    ['A3_h_pavimento'].median())
        non = float(x[~positiva.reindex(x.index, fill_value=False)]
                    ['A3_h_pavimento'].median())
        print('%-30s %10.3f %10.3f %+12.3f' % (nome, cad, non, non - cad))
        fuori.append({'camera': cam, 'vista': nome, 'mediana_caduta': cad,
                      'mediana_non_caduta': non, 'separazione': non - cad,
                      'n_fotogrammi': int(len(x))})

    if len(fuori) == 2:
        r = fuori[0]['separazione'] / max(abs(fuori[1]['separazione']), 1e-9)
        print()
        print('la vista laterale separa %.1f volte piu\' della rialzata' % r)

    os.makedirs(os.path.dirname(a.fuori), exist_ok=True)
    with open(a.fuori, 'w', encoding='utf-8') as f:
        json.dump({'csv': a.csv, 'positiva': quale, 'viste': fuori}, f,
                  ensure_ascii=False, indent=1)
    print('scritto', a.fuori)


if __name__ == '__main__':
    main()
