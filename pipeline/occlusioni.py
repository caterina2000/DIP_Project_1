"""
Occlusione controllata: quali punti servono davvero, e quanto costa perderli.

Perche'
-------
Il progetto ha gia' misurato una occlusione REALE e dipendente dalla posa: la
confidenza del naso passa da 0,938 con la persona in piedi a 0,240 quando e' a
terra, perche' il viso e' girato di lato o coperto dal braccio. Ma da quel dato
non si puo' concludere che il sistema sia «robusto alle occlusioni»: si e'
individuata e corretta UNA specifica modalita' di guasto dello stimatore.

Il relatore chiede la verifica complementare, ed e' quella giusta: un test
artificiale controllato che mascheri gruppi di punti e misuri la degradazione,
producendo una curva «quali e quanti punti mancano -> F2 e recall».

Come si simula un punto non disponibile
---------------------------------------
Non azzerandolo: uno zero in coordinate immagine e' l'angolo in alto a
sinistra, cioe' una posizione PLAUSIBILE e sbagliata, e produrrebbe velocita'
enormi verso quell'angolo. Non e' cio' che succede.

Sotto occlusione MediaPipe continua a emettere una posizione, con confidenza
bassa: il tracciatore la propaga dal fotogramma precedente finche' non ritrova
il punto. Qui si fa la stessa cosa -- il punto mascherato viene CONGELATO
all'ultima posizione nota -- perche' e' il comportamento reale dello stimatore
ed e' anche il piu' benevolo: le derivate vanno a zero invece che esplodere.
Il risultato e' quindi un limite superiore alla robustezza.

I gruppi
--------
Scelti perche' corrispondono a occlusioni che avvengono davvero in una casa:

    naso                il viso girato o coperto -- l'occlusione gia' misurata
    caviglie            i piedi dietro un mobile basso
    gambe               ginocchia e caviglie: divano, tavolo, letto
    spalle              busto coperto da una persona davanti
    anche               il riferimento di A3: e' il caso peggiore per costruzione
    meta sinistra       occlusione laterale, stipite o parete
    casuale 10/25/50%   degradazione progressiva senza struttura

Uso:
    python pipeline/occlusioni.py
    python pipeline/occlusioni.py --modello gru --feature DTW
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

NASO = 0
SPALLE = (11, 12)
ANCHE = (23, 24)
GINOCCHIA = (25, 26)
CAVIGLIE = (27, 28)
SINISTRA = (11, 13, 15, 23, 25, 27)

# I punti che le nostre grandezze usano DAVVERO: A1 adatta l'ellisse su sette
# punti, A2 e A3 usano naso, spalle, anche, ginocchia e caviglie. Sono nove su
# trentatre. Un mascheramento casuale che peschi da tutti e 33 colpisce quasi
# sempre gomiti, polsi e punti del viso che il sistema non guarda, e misura
# quindi molto meno di quanto dichiari: la quota va applicata a QUESTI.
USATI = (0, 11, 12, 23, 24, 25, 26, 27, 28)

GRUPPI = [
    ('nessuna occlusione', ()),
    ('naso', (NASO,)),
    ('caviglie', CAVIGLIE),
    ('gambe (ginocchia+caviglie)', GINOCCHIA + CAVIGLIE),
    ('spalle', SPALLE),
    ('anche  (riferimento di A3)', ANCHE),
    ('meta sinistra', SINISTRA),
]
CASUALI = (0.11, 0.22, 0.33, 0.55)     # 1, 2, 3, 5 punti dei nove usati


class Punto:
    """Adattatore: il motore geometrico vuole oggetti con .x .y .z."""
    __slots__ = ('x', 'y', 'z', 'visibility')

    def __init__(self, x, y, z, v=1.0):
        self.x, self.y, self.z, self.visibility = x, y, z, v


def maschera(lm, mask_idx, prec, rng=None, quota=0.0):
    """
    Congela i punti mascherati all'ultima posizione nota.

    `prec` e' lo stato del fotogramma precedente e viene aggiornato in luogo:
    i punti non mascherati lo rinfrescano, quelli mascherati lo leggono. E'
    il comportamento del tracciatore sotto occlusione.
    """
    out = lm.copy()
    idx = set(mask_idx)
    if quota > 0 and rng is not None:
        n = int(round(quota * len(USATI)))
        idx |= set(np.asarray(USATI)[
            rng.choice(len(USATI), n, replace=False)].tolist())
    for i in range(len(lm)):
        if i in idx and prec[i] is not None:
            out[i] = prec[i]
        else:
            prec[i] = lm[i].copy()
    return out


def ricalcola(z, mask_idx, quota=0.0, seme=42, sel=None):
    """
    Rigenera le 32 grandezze dai landmark, con i punti mascherati.

    `sel` seleziona un sottoinsieme di righe PRIMA del ricalcolo: filtrare la
    camera qui invece che dopo dimezza il lavoro, e il motore non attraversa
    comunque il confine fra riprese perche' si azzera a ogni cambio.
    """
    img, wld = z['image_landmarks'], z['world_landmarks']
    vid, has = z['video_id'], z['has_pose']
    if sel is not None:
        img, wld, vid, has = img[sel], wld[sel], vid[sel], has[sel]
    rng = np.random.default_rng(seme)
    motore = MotoreGeometrico(k_integrali=config.K_INTEGRALI)

    righe, ripresa_corr = [], None
    prec_i = [None] * img.shape[1]
    prec_w = [None] * wld.shape[1]
    for k in range(len(vid)):
        if vid[k] != ripresa_corr:
            ripresa_corr = vid[k]
            motore.reset()
            prec_i = [None] * img.shape[1]
            prec_w = [None] * wld.shape[1]
        if not has[k]:
            righe.append({c: 0.0 for c in NOMI})
            continue
        a = maschera(img[k], mask_idx, prec_i, rng, quota)
        b = maschera(wld[k], mask_idx, prec_w, rng, quota)
        lm = [Punto(*p[:3]) for p in a]
        wl = [Punto(*p[:3]) for p in b]
        righe.append(motore.fotogramma(lm, wl, config.W_IMMAGINE,
                                       config.H_IMMAGINE, config.FPS_DATASET))
    return pd.DataFrame(righe)


def valuta(df, colonne, modello, soglia):
    """LOSO sulle finestre, positivo = evento (classe OmniFall `fall`)."""
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
    ap.add_argument('--meta', default='feature_v2_omnifall.csv',
                    help='CSV con soggetto/ripresa/fotogramma/classe_omnifall')
    ap.add_argument('--modello', default='foresta')
    ap.add_argument('--feature', default='DTW')
    ap.add_argument('--camera', type=int, default=1)
    ap.add_argument('--soglia', type=float, default=0.5)
    a = ap.parse_args()

    colonne = (feature_dtw() if a.feature.upper() == 'DTW'
               else FEATURE[a.feature if a.feature in FEATURE else a.feature.upper()])
    z = np.load(a.npz, allow_pickle=True)
    meta = pd.read_csv(os.path.join(config.FEATURE_DIR, a.meta),
                       usecols=['ripresa', 'fotogramma', 'classe_omnifall'])
    cls_map = meta.drop_duplicates(['ripresa', 'fotogramma'])

    # identita' ricavata dal npz: `up_fall_Subject_01_sub01_act06_...` ->
    # `sub01_act06_...`, che e' il nome che usa il CSV.
    import re as _re
    _pat = _re.compile(r'(sub\d+_act\d+_trial\d+_cam(\d+))')
    _m = [_pat.search(str(v)) for v in z['video_id']]
    ident = pd.DataFrame({
        'ripresa': [x.group(1) if x else '' for x in _m],
        'camera': [int(x.group(2)) if x else 0 for x in _m],
        'fotogramma': z['frame'].astype(int),
        'soggetto': [str(s_) for s_ in z['subject']],
        'ha_posa': z['has_pose'].astype(int),
    })

    print('=' * 92)
    print(f'OCCLUSIONE CONTROLLATA — {a.modello}, {a.feature} '
          f'({len(colonne)} grandezze), camera {a.camera}, '
          f'{len(z["video_id"]):,} fotogrammi')
    print('=' * 92)
    print(f"{'punti mascherati':<30}{'n':>4}{'F2':>17}{'recall':>9}"
          f"{'prec.':>8}{'perdita F2':>12}")
    print('-' * 92)

    sel_cam = (ident.camera == a.camera).to_numpy()
    ident_cam = ident[sel_cam].reset_index(drop=True)
    print(f'fotogrammi su camera {a.camera}: {int(sel_cam.sum()):,}', flush=True)

    prove = ([(n, g, 0.0) for n, g in GRUPPI]
             + [(f'casuale {int(100*q)}%', (), q) for q in CASUALI])

    base, esito = None, []
    for nome, gruppo, quota in prove:
        t0 = time.time()
        f = ricalcola(z, gruppo, quota, sel=sel_cam)
        # L'identita' viene dal npz stesso, non dalla posizione nel CSV: i due
        # file hanno ORDINI DIVERSI (il npz elenca prima le ADL) e allinearli
        # per indice mescolerebbe le riprese. Il legame e' (ripresa, fotogramma).
        for c in ('ripresa', 'fotogramma', 'camera', 'ha_posa'):
            f[c] = ident_cam[c].to_numpy()
        f[COL_SOGGETTO] = ident_cam['soggetto'].to_numpy()
        f = f.merge(cls_map, on=['ripresa', 'fotogramma'], how='left')
        f['classe_omnifall'] = f['classe_omnifall'].fillna(-1).astype(int)
        f = f[f.camera == a.camera]
        ag = valuta(f, colonne, a.modello, a.soglia)
        if base is None:
            base = ag['fbeta_media']
        perdita = ag['fbeta_media'] - base
        n_punti = (len(set(gruppo)) if quota == 0
                   else int(round(quota * len(USATI))))
        print(f"{nome:<30}{n_punti:>4}"
              f"{dec(ag['fbeta_media']):>9}{' +-' + dec(ag['fbeta_dev']):>8}"
              f"{dec(ag['recall_media']):>9}{dec(ag['precision_media']):>8}"
              f"{(dec(perdita) if perdita else '—'):>12}  ({time.time()-t0:.0f} s)",
              flush=True)
        esito.append({'occlusione': nome, 'n_punti': n_punti,
                      'quota_casuale': quota, 'perdita_f2': perdita, **ag})

    print('-' * 92)
    print('I punti mascherati sono CONGELATI all ultima posizione nota, che e')
    print('il comportamento del tracciatore sotto occlusione e anche il piu')
    print('benevolo: le derivate vanno a zero invece che esplodere. I valori')
    print('sono quindi un limite SUPERIORE alla robustezza.')

    out = os.path.join(config.RISULTATI_DIR, 'occlusioni')
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, f'{a.modello}_{a.feature}.json'), 'w',
              encoding='utf-8') as fh:
        json.dump({'modello': a.modello, 'feature': a.feature,
                   'camera': a.camera, 'soglia': a.soglia,
                   'simulazione': 'punto congelato all ultima posizione nota',
                   'prove': esito}, fh, indent=2, ensure_ascii=False)
    print(f'\nsalvato: risultati/occlusioni/{a.modello}_{a.feature}.json')


if __name__ == '__main__':
    main()
