"""
Fino a che rumore reggono le grandezze integrali?

La domanda
----------
La sezione sugli integrali del capitolo metodologico afferma che accumulare
cancella il rumore, perche' il rumore a media nulla si somma a zero mentre il
movimento vero si somma. **L'affermazione e' falsa per queste tre grandezze**,
e la misura sul campo l'ha smentita:

    escursione del tronco, mediana su una finestra mobile di 31 fotogrammi
        persona FERMA su un divano (casa reale)   max 93,5 gradi
        CADUTA vera (altra casa)                  max 60,7 gradi

Il motivo e' che tutte e tre sono funzioni MONOTONE del rumore:

    percorso    = somma dei |delta posizione|   i valori assoluti non si
                                                cancellano mai
    escursione  = max - min                     il rumore allarga l'intervallo
    discesa     = y - min(y)                    il rumore abbassa il minimo

L'argomento della cancellazione vale per una somma di incrementi CON SEGNO,
non per queste. Cio' che le rende migliori delle derivate e' che sono
REGOLARI -- variano lentamente, quindi hanno autocorrelazione alta per
costruzione -- non che siano robuste.

Cosa misura questo script
-------------------------
Si inietta rumore gaussiano crescente sulle coordinate dei landmark di
UP-Fall, si ricalcolano le grandezze e si rimisura la prestazione. Serve a
distinguere due letture che oggi danno lo stesso risultato in laboratorio:

  A. gli integrali funzionano perche' catturano la dinamica della caduta;
  B. gli integrali funzionano su UP-Fall perche' li' il rumore e' basso, e
     altrove no.

Se il confronto fra grandezze integrali e derivate si mantiene al crescere del
rumore, vale A. Se si annulla o si inverte, vale B -- e la conclusione della
tesi va ridimensionata di conseguenza.

L'ampiezza del rumore e' espressa in frazione della lunghezza del torso, cosi'
da essere confrontabile fra riprese e indipendente dalla distanza dalla
telecamera.

Uso:
    python pipeline/rumore.py
    python pipeline/rumore.py --modello gru
"""

import argparse
import json
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
from src.dati import COL_SOGGETTO, FEATURE, Scaler, feature_dtw
from src.geometry import MotoreGeometrico, NOMI
from src.modelli import costruisci
from src.valutazione import aggrega, metriche, probabilita_allarme

dec = lambda v, n=3: f'{v:.{n}f}'.replace('.', ',')

# Ampiezze provate, in frazione della lunghezza del torso. Il jitter misurato
# sulle riprese domestiche corrisponde grossolanamente a 0,01-0,02.
AMPIEZZE = (0.0, 0.005, 0.01, 0.02, 0.04)

# I due insiemi da confrontare: con e senza la terna integrale.
INSIEMI = {
    'A3   senza integrali': 'A3base',
    'A3   con integrali': 'A3',
    'DTW  sottoinsieme': 'DTW',
}


class Punto:
    __slots__ = ('x', 'y', 'z', 'visibility')

    def __init__(self, x, y, z, v=1.0):
        self.x, self.y, self.z, self.visibility = x, y, z, v


def ricalcola(z, sigma, sel, seme=42):
    """
    Rigenera le grandezze con rumore gaussiano sulle coordinate.

    Il rumore e' applicato ai landmark NORMALIZZATI (coordinate in [0,1]), con
    deviazione `sigma` espressa in frazione della lunghezza del torso: si
    stima il torso per fotogramma e si scala il rumore di conseguenza,
    altrimenti la stessa ampiezza assoluta avrebbe effetti diversi a seconda
    della distanza dalla telecamera.
    """
    img, wld = z['image_landmarks'][sel], z['world_landmarks'][sel]
    vid, has = z['video_id'][sel], z['has_pose'][sel]
    rng = np.random.default_rng(seme)
    motore = MotoreGeometrico(k_integrali=config.K_INTEGRALI)

    righe, corrente = [], None
    for k in range(len(vid)):
        if vid[k] != corrente:
            corrente = vid[k]
            motore.reset()
        if not has[k]:
            righe.append({c: 0.0 for c in NOMI})
            continue
        a, b = img[k].copy(), wld[k].copy()
        if sigma > 0:
            # lunghezza del torso nel piano immagine, in coordinate normalizzate
            sh = (a[11, :2] + a[12, :2]) / 2
            hip = (a[23, :2] + a[24, :2]) / 2
            L = max(float(np.hypot(*(sh - hip))), 1e-3)
            a[:, :2] += rng.normal(0, sigma * L, a[:, :2].shape)
            b[:, :3] += rng.normal(0, sigma, b[:, :3].shape)
        righe.append(motore.fotogramma([Punto(*p[:3]) for p in a],
                                       [Punto(*p[:3]) for p in b],
                                       config.W_IMMAGINE, config.H_IMMAGINE,
                                       config.FPS_DATASET))
    return pd.DataFrame(righe)


def valuta(df, colonne, modello, soglia):
    L, passo, step = (config.LUNGHEZZA_FINESTRA, config.PASSO_FINESTRA,
                      config.FRAME_STEP)
    X, y, sog = [], [], []
    for (s, _), g in df.groupby([COL_SOGGETTO, 'ripresa'], sort=True):
        g = g.sort_values('fotogramma')
        g = g[g.ha_posa == 1]
        if step > 1:
            g = g.iloc[::step]
        if len(g) < L:
            continue
        v = g[list(colonne)].to_numpy(np.float32)
        cls = g['classe_omnifall'].to_numpy()
        for i in range(0, len(g) - L + 1, passo):
            X.append(v[i:i + L])
            y.append(int((cls[i:i + L] == 1).sum() >= 5))
            sog.append(s)
    X, y, sog = np.stack(X), np.array(y), np.array(sog)
    ris = []
    for t in sorted(set(sog)):
        m = sog == t
        sc = Scaler(colonne).fit(df[df[COL_SOGGETTO] != t])
        mod = costruisci(modello, (X.shape[1], X.shape[2]), 2)
        mod.addestra(sc.transform(X[~m]), y[~m].astype(int))
        p = probabilita_allarme(mod.probabilita(sc.transform(X[m])))
        ris.append(metriche(y[m], p, soglia))
    return aggrega(ris)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--npz', default=os.path.join(
        os.path.dirname(RADICE), 'DIP_PROJECT', 'dataset', 'processed',
        'features', 'landmarks_raw.npz'))
    ap.add_argument('--meta', default='feature_v2_omnifall.csv')
    ap.add_argument('--modello', default='foresta')
    ap.add_argument('--camera', type=int, default=1)
    ap.add_argument('--soglia', type=float, default=0.5)
    a = ap.parse_args()

    import re
    z = np.load(a.npz, allow_pickle=True)
    meta = pd.read_csv(os.path.join(config.FEATURE_DIR, a.meta),
                       usecols=['ripresa', 'fotogramma', 'classe_omnifall'])
    cls_map = meta.drop_duplicates(['ripresa', 'fotogramma'])

    pat = re.compile(r'(sub\d+_act\d+_trial\d+_cam(\d+))')
    m = [pat.search(str(v)) for v in z['video_id']]
    ident = pd.DataFrame({
        'ripresa': [x.group(1) if x else '' for x in m],
        'camera': [int(x.group(2)) if x else 0 for x in m],
        'fotogramma': z['frame'].astype(int),
        'soggetto': [str(s_) for s_ in z['subject']],
        'ha_posa': z['has_pose'].astype(int)})
    sel = (ident.camera == a.camera).to_numpy()
    ident_cam = ident[sel].reset_index(drop=True)

    print('=' * 88)
    print(f'ROBUSTEZZA AL RUMORE — {a.modello}, camera {a.camera}, '
          f'{int(sel.sum()):,} fotogrammi')
    print('rumore gaussiano sui landmark, deviazione in frazione della '
          'lunghezza del torso')
    print('=' * 88)
    print(f"{'sigma':>7}" + ''.join(f'{n:>24}' for n in INSIEMI))
    print('-' * 88)

    base = {}
    esito = []
    for sigma in AMPIEZZE:
        t0 = time.time()
        f = ricalcola(z, sigma, sel)
        for c in ('ripresa', 'fotogramma', 'camera', 'ha_posa'):
            f[c] = ident_cam[c].to_numpy()
        f[COL_SOGGETTO] = ident_cam['soggetto'].to_numpy()
        f = f.merge(cls_map, on=['ripresa', 'fotogramma'], how='left')
        f['classe_omnifall'] = f['classe_omnifall'].fillna(-1).astype(int)

        riga = {'sigma': sigma}
        celle = ''
        for nome, chiave in INSIEMI.items():
            colonne = (feature_dtw() if chiave == 'DTW'
                       else FEATURE[chiave])
            ag = valuta(f, colonne, a.modello, a.soglia)
            if sigma == 0.0:
                base[nome] = ag['fbeta_media']
            d = ag['fbeta_media'] - base[nome]
            celle += f"{dec(ag['fbeta_media']):>10}{('  ' + dec(d, 3)) if sigma else '':>14}"
            riga[chiave] = {'f2': ag['fbeta_media'], 'dev': ag['fbeta_dev'],
                            'recall': ag['recall_media'],
                            'precisione': ag['precision_media'], 'delta': d}
        print(f'{dec(sigma, 3):>7}{celle}   ({time.time()-t0:.0f} s)',
              flush=True)
        esito.append(riga)

    print('-' * 88)
    print('A destra di ogni valore, la variazione rispetto a sigma = 0.')
    print()
    print('Se il vantaggio degli integrali si mantiene al crescere del rumore,')
    print('essi catturano la dinamica. Se si annulla o si inverte, il vantaggio')
    print('misurato in laboratorio dipende dal fatto che li il rumore e basso.')

    out = os.path.join(config.RISULTATI_DIR, 'rumore')
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, f'{a.modello}_cam{a.camera}.json'), 'w',
              encoding='utf-8') as fh:
        json.dump({'modello': a.modello, 'camera': a.camera,
                   'soglia': a.soglia, 'ampiezze': list(AMPIEZZE),
                   'unita_rumore': 'deviazione standard in frazione della '
                                   'lunghezza del torso',
                   'prove': esito}, fh, indent=2, ensure_ascii=False)
    print(f'\nsalvato: risultati/rumore/{a.modello}_cam{a.camera}.json')


if __name__ == '__main__':
    main()
