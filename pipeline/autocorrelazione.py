# -*- coding: utf-8 -*-
"""Autocorrelazione a un passo delle grandezze, per la tabella del Capitolo 3.

Perche' esiste. La tabella `tab:autocorrelazione` riportava valori che non
corrispondevano piu' a quelli citati negli altri capitoli, e conteneva
«Energia del corpo» --- una grandezza che il capitolo stesso, tre pagine
prima, dichiara di aver eliminato perche' sommava quadrati di quantita' con
unita' diverse. Serviva un file che la producesse.

Come si calcola, e perche' non basta `np.corrcoef` sull'intera colonna.
L'autocorrelazione a un passo confronta il valore al tempo t con quello al
tempo t-1. Due campioni consecutivi appartengono allo stesso segnale solo se
appartengono alla stessa ripresa E se in mezzo non c'e' un buco di posa:
altrimenti si correla la fine di una ripresa con l'inizio di un'altra, o due
istanti separati da un intervallo in cui non si e' visto niente. Le coppie
vengono quindi raccolte dentro i tratti continui di posa valida, ripresa per
ripresa, e messe insieme solo alla fine.

Uso:
    python pipeline/autocorrelazione.py --csv feature_v4.csv
    python pipeline/autocorrelazione.py --csv feature_v4.csv --contro feature_v3.csv
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RADICE not in sys.path:
    sys.path.insert(0, RADICE)

FEATURE = os.path.join(RADICE, 'dataset', 'processed', 'features')

# Le grandezze della tabella del Capitolo 3, con il nome che vi compare.
RIGHE = [
    ('derivate', "Variazione dell'angolo del tronco", 'A2_d_angolo_tronco'),
    ('derivate', 'Velocita\' del bacino',             'A3_hip_vel'),
    ('derivate', 'Velocita\' della testa',            'A2_testa_vel'),
    ('derivate', 'Velocita\' angolare del tronco',    'A2_vel_ang_tronco'),
    ('integrali', 'Escursione del tronco',            'A3_escursione'),
    ('integrali', 'Percorso del bacino',              'A3_percorso'),
    ('integrali', 'Discesa del bacino',               'A3_discesa'),
]


def coppie(df, col):
    """(x_t, x_{t-1}) dentro i tratti continui di posa valida."""
    a, b = [], []
    for _, g in df.groupby(['soggetto', 'ripresa'], sort=False):
        v = g['ha_posa'].to_numpy() == 1
        x = g[col].to_numpy(float)
        # ogni cambio di stato apre un blocco; si tengono solo i validi
        blocchi = np.cumsum(np.concatenate(([0], np.diff(v.astype(int)) != 0)))
        for k in np.unique(blocchi):
            idx = np.where(blocchi == k)[0]
            if not v[idx[0]] or len(idx) < 3:
                continue
            t = x[idx]
            a.append(t[1:])
            b.append(t[:-1])
    if not a:
        return np.zeros(0), np.zeros(0)
    return np.concatenate(a), np.concatenate(b)


def rho1(df, col):
    x, y = coppie(df, col)
    if len(x) < 100 or np.std(x) == 0 or np.std(y) == 0:
        return float('nan'), len(x)
    return float(np.corrcoef(x, y)[0, 1]), len(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='feature_v4.csv')
    ap.add_argument('--contro', default=None,
                    help='secondo CSV, per il confronto fra due estrazioni')
    a = ap.parse_args()

    df = pd.read_csv(os.path.join(FEATURE, a.csv))
    alt = (pd.read_csv(os.path.join(FEATURE, a.contro))
           if a.contro else None)

    print('=' * 70)
    print('AUTOCORRELAZIONE A UN PASSO   ---   %s' % a.csv)
    if alt is not None:
        print('%s contro %s' % (a.csv, a.contro))
    print('=' * 70)
    print('coppie prese dentro i tratti continui di posa valida\n')

    intestazione = '%-36s %8s' % ('grandezza', 'rho_1')
    if alt is not None:
        intestazione += ' %10s %8s' % (a.contro.split('.')[0], 'delta')
    print(intestazione)
    print('-' * len(intestazione))

    famiglia = None
    for fam, nome, col in RIGHE:
        if col not in df.columns:
            print('%-36s   (colonna assente)' % nome)
            continue
        if fam != famiglia:
            famiglia = fam
            print('  %s' % ('Derivate istantanee' if fam == 'derivate'
                            else 'Grandezze integrali'))
        r, n = rho1(df, col)
        riga = '%-36s %8.3f' % ('    ' + nome, r)
        if alt is not None and col in alt.columns:
            r2, _ = rho1(alt, col)
            riga += ' %10.3f %+8.3f' % (r2, r - r2)
        print(riga)

    print()
    d = [rho1(df, c)[0] for _, _, c in RIGHE if c in df.columns
         and _ == 'derivate']
    der = [rho1(df, c)[0] for f, _, c in RIGHE if f == 'derivate'
           and c in df.columns]
    intg = [rho1(df, c)[0] for f, _, c in RIGHE if f == 'integrali'
            and c in df.columns]
    if der and intg:
        print('derivate istantanee: da %.3f a %.3f' % (min(der), max(der)))
        print('grandezze integrali: da %.3f a %.3f' % (min(intg), max(intg)))


if __name__ == '__main__':
    main()
