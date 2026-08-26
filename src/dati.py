"""
Dai CSV di feature alle finestre, con le due etichette e la divisione per soggetto.

Le due etichette
----------------
Ogni finestra ne porta DUE, e tenerle separate e' il cuore del confronto fra
regole di etichettatura:

    y_train   dipende dal MODO scelto ('scarta' | 'caduta' | 'tre_classi').
              E' cio' su cui il modello viene addestrato, ed e' la variabile
              dell'esperimento.

    y_allarme fissa per tutti i modi: 1 se la finestra contiene una caduta
              in corso OPPURE una persona a terra, 0 altrimenti. E' il metro
              con cui si misurano tutti e tre i modelli, e non dipende da
              come sono stati addestrati.

Senza questa separazione il confronto non sarebbe interpretabile: il modo
'scarta' verrebbe misurato su un insieme di verifica piu' facile, perche' le
finestre che scarta sono proprio quelle ambigue.

La divisione
------------
Leave-one-subject-out. In ogni fold tre insiemi DISGIUNTI PER PERSONA: uno in
verifica, uno in validazione, il resto in addestramento. Con finestre
sovrapposte una divisione casuale metterebbe finestre quasi identiche da
entrambe le parti, e con pochi soggetti metterebbe la stessa persona in
addestramento e in verifica.

I buchi di posa
---------------
Il 4,5% dei fotogrammi non ha una posa stimabile. Scartarli e basta creerebbe
finestre che saltano il buco: ventidue campioni presi a cavallo di
un'interruzione descrivono un movimento mai avvenuto, e la finestra
coprirebbe piu' tempo di quanto dichiara. Qui ogni ripresa viene spezzata nei
suoi TRATTI CONTINUI di posa valida, e le finestre si costruiscono dentro un
tratto solo.

Lo scaler
---------
Stimato sui soli fotogrammi di addestramento del fold, mai sull'intero
dataset, e sui FOTOGRAMMI e non sulle finestre: con passo 2 su finestre da 22
ogni fotogramma comparirebbe in undici finestre, quindi peserebbe undici
volte, con un peso che per giunta varia agli estremi di ogni ripresa.
"""

import os
from dataclasses import dataclass
from typing import Iterator, List, Optional, Sequence

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

import config
from src.etichettatura import etichetta_finestra
from src.geometry import (NOMI, NOMI_A1, NOMI_A2, NOMI_A3,
                          NOMI_INT_A1, NOMI_INT_A2, NOMI_INT_A3)

# ============================================================
# NOMI DELLE COLONNE NEL CSV
# ============================================================
# Il CSV prodotto da pipeline/estrai_feature.py usa questi nomi. Stanno qui
# come costanti e non sparsi nel codice, perche' e' esattamente il punto in
# cui il progetto precedente si e' rotto: i moduli citavano `subject` e
# `video_id` mentre l'estrattore scriveva altro, e l'errore si scopriva solo
# eseguendo.
COL_SOGGETTO = 'soggetto'
COL_RIPRESA = 'ripresa'
COL_FOTOGRAMMA = 'fotogramma'
COL_POSA = 'ha_posa'
COL_LABEL = 'label'
COL_CAMERA = 'camera'


# ============================================================
# RAPPRESENTAZIONI
# ============================================================
# Ogni bacino con la sua terna di integrali. 'TUTTE' e' il bacino completo da
# cui parte l'analisi DTW; il sottoinsieme che ne esce si legge con
# feature_dtw(), da file invece che copiato a mano -- cosi' non puo' divergere
# dall'analisi che lo ha prodotto.
FEATURE = {
    'A1': NOMI_A1 + NOMI_INT_A1,
    'A2': NOMI_A2 + NOMI_INT_A2,
    'A3': NOMI_A3 + NOMI_INT_A3,
    'TUTTE': list(NOMI),
    # Le stesse rappresentazioni SENZA la terna di integrali. Servono a
    # isolare il contributo degli integrali a parita' di tutto il resto: e'
    # il confronto che il relatore chiede, cioe' se le integrali aggiungano
    # informazione alle architetture sequenziali (che l'ordine ce l'hanno)
    # quanto ne aggiungono a un modello che riassume la finestra.
    'A1base': list(NOMI_A1),
    'A2base': list(NOMI_A2),
    'A3base': list(NOMI_A3),
}


def feature_dtw(percorso: Optional[str] = None) -> List[str]:
    """Il sottoinsieme scelto dall'analisi DTW, letto da `scelte.txt`."""
    p = percorso or os.path.join(config.RISULTATI_DIR, 'dtw', 'scelte.txt')
    if not os.path.exists(p):
        raise FileNotFoundError(
            f'{p} non esiste: eseguire prima pipeline/analisi_dtw.py')
    with open(p, encoding='utf-8') as f:
        return [r.strip() for r in f if r.strip()]


# Grandezze non negative con code lunghe: log1p prima della standardizzazione,
# altrimenti lo StandardScaler viene dominato dagli outlier.
#
# Il criterio non e' a occhio: sono le colonne non negative il cui rapporto fra
# 99,9-esimo percentile e mediana supera 10. Misurato su feature.csv, 109.746
# fotogrammi con posa valida:
#
#     A3_discesa        908x      A2_vel_ang_tronco  105x
#     A1_discesa        550x      A3_escursione       96x
#     A3_hip_vel        292x      A1_percorso         90x
#     A3_testa_vel_rel  228x      A2_testa_vel        56x
#     A3_percorso       137x      A2_escursione       30x
#     A1_escursione     111x      A3_larghezza       9,6x  (al limite)
#
# Restano fuori A1_asse_mag, A1_asse_min, A3_torso_len e A1_allungamento, che
# stanno fra 2,5x e 5,2x: sono gia' su scala compatta e il logaritmo non
# aggiunge nulla. Le grandezze con segno -- angoli, derivate, velocita'
# proiettate -- non possono passare per log1p e non ci passano.
ASIMMETRICHE = set(NOMI_INT_A1 + NOMI_INT_A2 + NOMI_INT_A3) | {
    'A2_vel_ang_tronco', 'A2_testa_vel', 'A3_hip_vel', 'A3_testa_vel_rel',
    'A3_larghezza',
}


@dataclass
class Fold:
    soggetto_test: str
    soggetto_val: str
    soggetti_train: list
    X_train: np.ndarray
    y_train: np.ndarray
    X_val: np.ndarray          # tutte le finestre del soggetto di validazione
    y_val: np.ndarray          # verita' di allarme, per scegliere la soglia
    Xv_modello: np.ndarray     # sottoinsieme etichettabile nello spazio del
    yv_modello: np.ndarray     # modello, per fermare l'addestramento
    X_test: np.ndarray
    y_test: np.ndarray         # verita' di allarme
    n_classi: int


class Scaler:
    """log1p sulle colonne asimmetriche, poi standardizzazione."""

    def __init__(self, colonne: Sequence[str]):
        self.colonne = list(colonne)
        self.maschera = np.array([c in ASIMMETRICHE for c in self.colonne])
        self._s = StandardScaler()

    def _log(self, a):
        if not self.maschera.any():
            return np.asarray(a, dtype=np.float64)
        out = np.asarray(a, dtype=np.float64).copy()
        c = np.where(self.maschera)[0]
        out[..., c] = np.sign(out[..., c]) * np.log1p(np.abs(out[..., c]))
        return out

    def fit(self, df_fotogrammi: pd.DataFrame):
        v = df_fotogrammi[self.colonne].to_numpy(np.float64)
        self._s.fit(self._log(v))
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        if len(X) == 0:
            return X.astype(np.float32)
        n, L, f = X.shape
        return self._s.transform(
            self._log(X).reshape(-1, f)).reshape(n, L, f).astype(np.float32)


# ============================================================
# FINESTRE
# ============================================================
def _tratti_continui(g: pd.DataFrame) -> List[pd.DataFrame]:
    """
    Spezza una ripresa nei tratti in cui la posa e' valida senza interruzioni.

    Se la colonna della posa non c'e', o non ci sono buchi, la ripresa resta
    un tratto solo.
    """
    if COL_POSA not in g.columns:
        return [g]
    valida = g[COL_POSA].to_numpy() == 1
    if valida.all():
        return [g]
    if not valida.any():
        return []
    # ogni cambio di stato apre un blocco; si tengono solo quelli validi
    blocchi = np.cumsum(np.concatenate(([0], np.diff(valida.astype(int)) != 0)))
    fuori = []
    for b in np.unique(blocchi):
        idx = np.where(blocchi == b)[0]
        if valida[idx[0]]:
            fuori.append(g.iloc[idx])
    return fuori


def costruisci_finestre(df: pd.DataFrame, colonne: Sequence[str], modo: str,
                        lunghezza=None, passo=None, frame_step=None,
                        **soglie):
    """
    Ritorna (X, y_train, y_allarme, soggetti, id_ripresa).

    Le finestre non attraversano mai il confine fra due riprese ne' un buco di
    posa: descriverebbero un movimento che non e' avvenuto.

    Le finestre che il modo 'scarta' esclude restano comunque in X, marcate
    con y_train = -1: servono in verifica, dove tutti i modelli vanno misurati
    sullo stesso insieme.
    """
    L = lunghezza or config.LUNGHEZZA_FINESTRA
    passo = passo or config.PASSO_FINESTRA
    step = frame_step if frame_step is not None else config.FRAME_STEP

    colonne = list(colonne)
    mancanti = [c for c in colonne if c not in df.columns]
    if mancanti:
        raise KeyError(f'colonne assenti dal CSV: {mancanti[:5]}'
                       f'{" ..." if len(mancanti) > 5 else ""}')

    X, y_tr, y_al, sog, rip = [], [], [], [], []
    for (s, v), g in df.groupby([COL_SOGGETTO, COL_RIPRESA], sort=True):
        g = g.sort_values(COL_FOTOGRAMMA)
        for tratto in _tratti_continui(g):
            t = tratto.iloc[::step] if step > 1 else tratto
            if len(t) < L:
                continue
            dati = t[colonne].to_numpy(np.float32)
            lab = t[COL_LABEL].to_numpy(np.int8)
            for i in range(0, len(t) - L + 1, passo):
                fin = lab[i:i + L]
                e = etichetta_finestra(fin, modo, **soglie)
                X.append(dati[i:i + L])
                y_tr.append(-1 if e is None else e)
                # verita' di allarme: la finestra contiene caduta OPPURE
                # persona a terra. Indipendente dal modo, e' il metro comune.
                y_al.append(int(etichetta_finestra(fin, 'caduta', **soglie) == 1))
                sog.append(s)
                rip.append(v)
    if not X:
        raise ValueError('nessuna finestra costruita: controllare colonne e lunghezza')
    return (np.stack(X), np.array(y_tr, np.int8), np.array(y_al, np.int8),
            np.array(sog), np.array(rip))


def conteggio(y_train: np.ndarray, y_allarme: np.ndarray) -> str:
    """
    Riepilogo delle finestre per classe. Va stampato a ogni run: senza, un
    fold con zero positivi in verifica produce metriche apparentemente valide
    e prive di significato.
    """
    n = len(y_train)
    r = [f'finestre: {n:,}']
    for c, nome in ((-1, 'scartate'), (0, 'normale'), (1, 'caduta'),
                    (2, 'a terra')):
        k = int((y_train == c).sum())
        if k:
            r.append(f'  y_train {c:2d} ({nome:9s}) {k:7,}  {100*k/n:5.1f}%')
    p = int(y_allarme.sum())
    r.append(f'  allarme atteso        {p:7,}  {100*p/n:5.1f}%')
    return '\n'.join(r)


# ============================================================
# LEAVE-ONE-SUBJECT-OUT
# ============================================================
def fold_loso(df: pd.DataFrame, colonne: Sequence[str], modo: str,
              **kw) -> Iterator[Fold]:
    """
    Un fold per soggetto. Il validation e' il soggetto successivo in ordine
    circolare, cosi' i tre insiemi restano disgiunti per persona senza dover
    scegliere a mano quale sia il validation.
    """
    X, y_tr, y_al, sog, _ = costruisci_finestre(df, colonne, modo, **kw)
    soggetti = sorted(set(sog))
    if len(soggetti) < 3:
        raise ValueError(f'servono almeno 3 soggetti, trovati {len(soggetti)}')

    n_classi = 3 if modo == 'tre_classi' else 2
    for i, test in enumerate(soggetti):
        val = soggetti[(i + 1) % len(soggetti)]
        train = [s for s in soggetti if s not in (test, val)]

        m_tr = np.isin(sog, train) & (y_tr >= 0)    # esclude le scartate
        m_te = sog == test
        # Il validation serve a DUE cose che vogliono etichette diverse:
        # fermare l'addestramento (etichette nello spazio del modello, quindi
        # senza le scartate) e scegliere la soglia (verita' di allarme, su
        # tutte le finestre). Tenerle separate evita di dover scegliere quale
        # delle due sacrificare.
        m_va_mod = (sog == val) & (y_tr >= 0)
        m_va = sog == val

        sc = Scaler(colonne).fit(df[df[COL_SOGGETTO].isin(train)])
        yield Fold(test, val, train,
                   sc.transform(X[m_tr]), y_tr[m_tr],
                   sc.transform(X[m_va]), y_al[m_va],
                   sc.transform(X[m_va_mod]), y_tr[m_va_mod],
                   sc.transform(X[m_te]), y_al[m_te],
                   n_classi)


def carica(csv: Optional[str] = None, camera: Optional[int] = 1,
           solo_posa: bool = False) -> pd.DataFrame:
    """
    CSV di feature, filtrato per camera.

    `solo_posa` NON va usato prima del finestramento: ci pensa
    `_tratti_continui`, che oltre a togliere i fotogrammi senza posa impedisce
    alle finestre di scavalcare il buco. Serve per le analisi sui fotogrammi
    -- correlazioni, scale, statistiche -- dove il buco non fa danno.
    """
    p = csv or os.path.join(config.FEATURE_DIR, 'feature.csv')
    if not os.path.isabs(p) and not os.path.exists(p):
        p = os.path.join(config.FEATURE_DIR, p)
    d = pd.read_csv(p)
    if camera is not None and COL_CAMERA in d.columns:
        d = d[d[COL_CAMERA] == camera]
    if solo_posa and COL_POSA in d.columns:
        d = d[d[COL_POSA] == 1]
    return d.reset_index(drop=True)
