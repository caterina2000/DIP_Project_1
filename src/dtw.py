"""
Separabilita' delle grandezze con Dynamic Time Warping, misurata per camera.

A cosa serve
------------
Costruito il bacino di 34 candidate, resta da stabilire QUALI diano davvero
una firma distinguibile fra caduta e attivita' quotidiana. Il DTW confronta
la FORMA di due serie temporali anche quando non sono allineate: due cadute
possono avere la stessa struttura e durate diverse, oppure presentare il picco
qualche fotogramma prima o dopo. Un confronto punto per punto le giudicherebbe
diverse; il DTW deforma l'asse dei tempi e cerca l'allineamento migliore.

La differenza rispetto alla versione precedente
-----------------------------------------------
Quella analisi mescolava le due camere e classificava dieci grandezze, quasi
tutte del bacino A2. Ma il divario piu' grande misurato in tutto il lavoro e'
proprio quello fra i due punti di vista, e una grandezza che separa benissimo
di profilo puo' non separare nulla dall'alto: sulla vista frontale rialzata
l'angolo del tronco nel piano immagine ha appena 3 gradi di escursione fra
eretto e disteso, contro gli 84 della vista laterale.

Qui il punteggio si calcola SEPARATAMENTE per camera, e la scelta usa il
MINIMO fra i due:

    punteggio_robusto = min(punteggio_cam1, punteggio_cam2)

Il minimo e non la media, perche' una grandezza ottima da una vista e inutile
dall'altra e' esattamente quella da escludere -- e la media la premierebbe.

Le tre scelte metodologiche
---------------------------
Ricampionamento a lunghezza comune prima del confronto: senza di esso il
vincolo di warping si allarga da solo sulle coppie di lunghezza molto diversa,
che qui sono proprio quelle fra caduta e attivita' quotidiana (180 fotogrammi
contro 820). Dettaglio nella docstring di `punteggio`.


z-score per curva, prima del confronto: le grandezze hanno scale eterogenee
(gradi, velocita', rapporti adimensionali) e sui valori grezzi la distanza
sarebbe dominata da quelle di ampiezza maggiore. Si perde l'informazione di
ampiezza assoluta, accettabile perche' qui interessa la forma.

Vincolo sul cammino di allineamento, |i - j| <= w: un DTW libero puo'
deformare l'asse dei tempi al punto da far somigliare una curva di attivita'
normale a una di caduta. Il vincolo ammette piccoli sfasamenti e impedisce
deformazioni prive di senso fisico.
"""

from typing import Dict, List, Optional, Sequence

import numpy as np

FINESTRA_WARPING = 10          # |i - j| <= 10 fotogrammi
LUNGHEZZA_COMUNE = 200         # ricampionamento per le sovrapposizioni


# ============================================================
# DISTANZA
# ============================================================
def zscore(x: np.ndarray) -> Optional[np.ndarray]:
    x = np.asarray(x, dtype=np.float64)
    s = x.std()
    if not np.isfinite(s) or s < 1e-9:
        return None                      # curva piatta: non confrontabile
    return (x - x.mean()) / s


# dtaidistance e' l'implementazione compilata in C: e' presente solo
# nell'ambiente fallqt_clean. Se manca si usa la versione pura Python, che da'
# lo stesso risultato ma e' due ordini di grandezza piu' lenta -- su 34
# grandezze per due camere la differenza e' fra minuti e ore.
try:
    from dtaidistance import dtw as _dtai
    _HA_DTAI = True
except ImportError:
    _HA_DTAI = False


def _dtw_python(a, b, w):
    """Riferimento leggibile, e ricaduta quando dtaidistance non c'e'."""
    n, m = len(a), len(b)
    w = max(w, abs(n - m))
    prec = np.full(m + 1, np.inf)
    prec[0] = 0.0
    for i in range(1, n + 1):
        cur = np.full(m + 1, np.inf)
        j0, j1 = max(1, i - w), min(m, i + w)
        for j in range(j0, j1 + 1):
            c = abs(a[i - 1] - b[j - 1])
            cur[j] = c + min(prec[j], cur[j - 1], prec[j - 1])
        prec = cur
    return float(prec[m])


def dtw(a: np.ndarray, b: np.ndarray, finestra: int = FINESTRA_WARPING) -> float:
    """
    Distanza DTW vincolata, normalizzata sulla lunghezza del cammino.

    La normalizzazione serve perche' senza di essa una coppia di curve lunghe
    risulterebbe piu' distante di una coppia corta a parita' di forma, e il
    confronto fra riprese di durata diversa non sarebbe interpretabile.
    """
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return float('inf')
    if _HA_DTAI:
        # use_pruning=False, e NON e' una scelta di prestazione.
        #
        # Con use_pruning=True dtaidistance ricava il limite di potatura dalla
        # distanza euclidea, che pero' e' un maggiorante del DTW *libero* e non
        # di quello *vincolato da una finestra*: un cammino costretto in una
        # banda stretta puo' costare PIU' dell'allineamento uno-a-uno. Quando
        # succede, la funzione pota l'intera matrice e restituisce `inf`.
        #
        # L'infinito non arriva mai a chi legge, ed e' questo il punto. Se
        # cade fra le distanze intra-classe, `intra.mean()` diventa infinita e
        # il punteggio della grandezza collassa a ESATTAMENTE 0: la grandezza
        # sparisce dalla selezione. Se cade fra quelle incrociate, il punteggio
        # diventa `inf` e la grandezza schizza in testa. Nessuno dei due casi
        # produce un errore o un avviso.
        #
        # Misurato su feature_v5.csv con dtaidistance 2.5.1: tre grandezze su
        # 33 ne erano colpite --- A3_angolo_tronco, A3_testa_rel_y,
        # A3_larghezza --- e la selezione che ne risultava non era quella
        # adottata. Su una coppia reale di curve, tutte finite, use_pruning=True
        # da' `inf` dove use_pruning=False da' 27,54.
        d = _dtai.distance_fast(np.ascontiguousarray(a, dtype=np.double),
                                np.ascontiguousarray(b, dtype=np.double),
                                window=max(finestra, abs(n - m)),
                                use_pruning=False)
        # dtaidistance restituisce la radice della somma dei quadrati; la
        # versione Python somma i valori assoluti. Si normalizzano entrambe
        # sulla lunghezza, quindi la classifica non cambia -- ma il valore
        # assoluto non e' confrontabile fra le due, e va dichiarato.
        return float(d / (n + m))
    return _dtw_python(a, b, finestra) / (n + m)


def _distanze(gruppo_a: List[np.ndarray], gruppo_b: Optional[List[np.ndarray]],
              finestra: int) -> np.ndarray:
    """Distanze fra tutte le coppie; se gruppo_b e' None, dentro gruppo_a."""
    v = []
    if gruppo_b is None:
        for i in range(len(gruppo_a)):
            for j in range(i + 1, len(gruppo_a)):
                v.append(dtw(gruppo_a[i], gruppo_a[j], finestra))
    else:
        for x in gruppo_a:
            for y in gruppo_b:
                v.append(dtw(x, y, finestra))
    return np.asarray(v, dtype=np.float64)


# ============================================================
# PUNTEGGIO
# ============================================================
def punteggio(curve_caduta: List[np.ndarray], curve_adl: List[np.ndarray],
              finestra: int = FINESTRA_WARPING,
              lunghezza: int = LUNGHEZZA_COMUNE) -> Dict[str, float]:
    """
    Confronta tre popolazioni di distanze e ne ricava due punteggi.

        D_FF  fra cadute        deve essere BASSA (le cadute si somigliano)
        D_AA  fra attivita'     deve essere BASSA
        D_FA  incrociate        deve essere ALTA (le classi si distinguono)

    punteggio      = mu_FA / mu_intra
    punteggio_rob  = (mu_FA - mu_intra) / (sigma_FA + sigma_intra)

    Il secondo tiene conto anche della dispersione: un punteggio alto puo'
    derivare da valori anomali o da forte variabilita' invece che da una vera
    separazione, e il robusto lo smaschera.

    Perche' si ricampiona a lunghezza comune
    ----------------------------------------
    Il vincolo di warping |i - j| <= w non si puo' applicare a due curve di
    lunghezza diversa senza allargarlo ad almeno |n - m|, altrimenti nessun
    cammino di allineamento arriva in fondo. Su questo dataset le riprese di
    caduta durano circa 180 fotogrammi e quelle di attivita' quotidiana circa
    820: le coppie interne alle due classi hanno lunghezze simili e mantengono
    la banda stretta, mentre le coppie INCROCIATE -- proprio quelle che devono
    risultare distanti -- se la vedono allargare a oltre 600 e si allineano
    quasi senza vincolo. La loro distanza risulta percio' piu' bassa del dovuto,
    mu_FA si abbassa e mu_intra resta alta: tutti i punteggi vengono schiacciati
    verso 1 e le grandezze non sono piu' confrontabili fra loro.

    Portando ogni curva alla stessa lunghezza il problema sparisce: n = m per
    ogni coppia, la banda vale 10 per tutte. Si perde l'informazione di durata,
    ed e' accettabile perche' la durata di una ripresa e' identica per tutte e
    34 le grandezze -- non puo' contribuire a distinguerle, mentre il rumore
    che introduce si'.
    """
    cf = [ricampiona(z, lunghezza)
          for z in (zscore(c) for c in curve_caduta) if z is not None]
    ca = [ricampiona(z, lunghezza)
          for z in (zscore(c) for c in curve_adl) if z is not None]
    if len(cf) < 2 or len(ca) < 2:
        return {'punteggio': 0.0, 'punteggio_rob': 0.0, 'n_caduta': len(cf),
                'n_adl': len(ca), 'mu_FF': 0.0, 'mu_AA': 0.0, 'mu_FA': 0.0}

    ff = _distanze(cf, None, finestra)
    aa = _distanze(ca, None, finestra)
    fa = _distanze(cf, ca, finestra)
    intra = np.concatenate([ff, aa])
    eps = 1e-9

    return {
        'n_caduta': len(cf), 'n_adl': len(ca),
        'mu_FF': float(ff.mean()), 'mu_AA': float(aa.mean()),
        'mu_FA': float(fa.mean()),
        'punteggio': float(fa.mean() / (intra.mean() + eps)),
        'punteggio_rob': float((fa.mean() - intra.mean()) /
                               (fa.std() + intra.std() + eps)),
    }


def ricampiona(x: np.ndarray, n: int = LUNGHEZZA_COMUNE) -> np.ndarray:
    """Porta una curva a lunghezza fissa, per le sovrapposizioni."""
    x = np.asarray(x, dtype=np.float64)
    if len(x) < 2:
        return np.zeros(n)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)


def curve_per_ripresa(df, colonna: str, camera: int,
                      solo_pose: bool = True) -> Dict[str, List[np.ndarray]]:
    """
    Estrae una curva per ripresa, divisa fra cadute e attivita' quotidiane.

    Una ripresa e' di caduta se contiene almeno un fotogramma di classe 1.
    """
    d = df[df.camera == camera]
    if solo_pose and 'ha_posa' in d.columns:
        d = d[d.ha_posa == 1]
    cadute, adl = [], []
    for _, g in d.groupby('ripresa'):
        g = g.sort_values('fotogramma')
        v = g[colonna].to_numpy(dtype=np.float64)
        if len(v) < 10:
            continue
        (cadute if (g.label == 1).any() else adl).append(v)
    return {'caduta': cadute, 'adl': adl}


def classifica(df, colonne: Sequence[str], camere=(1, 2),
               finestra: int = FINESTRA_WARPING) -> 'pd.DataFrame':
    """
    Punteggio per grandezza e per camera, piu' il minimo fra le due.

    La colonna `robusto` e' quella su cui si sceglie: e' il minimo, quindi
    premia solo cio' che regge da entrambi i punti di vista.
    """
    import pandas as pd
    righe = []
    for c in colonne:
        r = {'grandezza': c}
        p = []
        for cam in camere:
            g = curve_per_ripresa(df, c, cam)
            s = punteggio(g['caduta'], g['adl'], finestra)
            r[f'punteggio_cam{cam}'] = s['punteggio']
            r[f'rob_cam{cam}'] = s['punteggio_rob']
            r[f'n_caduta_cam{cam}'] = s['n_caduta']
            p.append(s['punteggio'])
        r['robusto'] = min(p) if p else 0.0
        r['divario'] = (max(p) - min(p)) if p else 0.0
        righe.append(r)
    return pd.DataFrame(righe).sort_values('robusto', ascending=False)
