"""
Metriche, scelta della soglia, e la regola che trasforma le probabilita' in
un allarme.

Il punto delicato: modelli diversi, stessa domanda
--------------------------------------------------
I tre modi di etichettatura producono modelli con uscite di forma diversa --
una probabilita' i binari, tre i ternari. Ma a tutti va chiesta la stessa
cosa, altrimenti il confronto non e' un confronto:

    «data questa finestra, devo suonare?»

Per un modello binario la risposta e' p(caduta). Per uno a tre classi e'
p(caduta) + p(a terra), cioe' 1 - p(attivita' normale): la probabilita' che
NON si tratti di attivita' ordinaria. Non e' una scelta di comodo -- discende
dalla motivazione clinica, per cui il danno dipende dal tempo passato a terra
e non dall'impatto: un sistema deve segnalare anche chi e' gia' a terra.

Perche' F-beta con beta = 2
---------------------------
I due errori non hanno lo stesso costo. Un falso negativo e' una caduta non
rilevata, cioe' una persona che resta a terra senza che nessuno lo sappia; un
falso positivo e' un allarme a vuoto, e il costo e' il disturbo. F1 li pesa
uguali e presuppone quindi che si equivalgano. Con beta = 2 il recall pesa il
quadruplo della precisione.

Il valore e' dichiarato in config PRIMA di guardare i dati di verifica, non
scelto a posteriori fra quelli che davano il numero migliore.
"""

from typing import Optional

import numpy as np

import config


# ============================================================
# DA PROBABILITA' A DECISIONE
# ============================================================
def probabilita_allarme(p: np.ndarray) -> np.ndarray:
    """
    Riduce l'uscita del modello a UNA probabilita' di allarme.

    p ha forma (n,) oppure (n, 1)  -> modello binario, si usa cosi' com'e'
    p ha forma (n, 2)              -> binario softmax, si prende la colonna 1
    p ha forma (n, 3)              -> ternario: 1 - p(classe 0)

    Cosi' i tre modelli restituiscono tutti un numero fra 0 e 1 che significa
    la stessa cosa, e la soglia e' confrontabile.
    """
    p = np.asarray(p, dtype=np.float64)
    if p.ndim == 1:
        return p
    if p.shape[1] == 1:
        return p[:, 0]
    if p.shape[1] == 2:
        return p[:, 1]
    if p.shape[1] == 3:
        return 1.0 - p[:, 0]
    raise ValueError(f'forma non gestita: {p.shape}')


def metriche(y_vero: np.ndarray, p_allarme: np.ndarray, soglia: float,
             beta: Optional[float] = None) -> dict:
    """Conteggi ed F-beta a una soglia data. y_vero e' la verita' di allarme."""
    beta = config.BETA if beta is None else beta
    y = np.asarray(y_vero).astype(int)
    pred = (np.asarray(p_allarme) >= soglia).astype(int)

    tp = int(((pred == 1) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    tn = int(((pred == 0) & (y == 0)).sum())

    rec = tp / (tp + fn) if tp + fn else 0.0
    prec = tp / (tp + fp) if tp + fp else 0.0
    b2 = beta * beta
    fbeta = ((1 + b2) * prec * rec / (b2 * prec + rec)) if (prec + rec) else 0.0
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0

    return {'soglia': float(soglia), 'fbeta': fbeta, 'f1': f1,
            'recall': rec, 'precision': prec,
            'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
            'n': len(y), 'quota_positivi': float(y.mean()) if len(y) else 0.0}


def scegli_soglia(y_val: np.ndarray, p_val: np.ndarray,
                  beta: Optional[float] = None, passo: float = 0.01):
    """
    Soglia che massimizza F-beta SUL VALIDATION.

    Va scelta qui e applicata al test una volta sola. Sceglierla guardando il
    test sarebbe leakage: l'insieme che deve dare una stima imparziale
    verrebbe usato per una decisione di progetto, e il numero che ne esce non
    direbbe piu' nulla su come andra' altrove.
    """
    beta = config.BETA if beta is None else beta
    migliore, best = 0.5, -1.0
    for s in np.arange(passo, 1.0, passo):
        m = metriche(y_val, p_val, s, beta)
        if m['fbeta'] > best:
            best, migliore = m['fbeta'], float(s)
    return migliore, best


def aggrega(fold: list) -> dict:
    """
    Media e dispersione fra fold, piu' i conteggi cumulati.

    Con pochi soggetti la DISPERSIONE non e' una nota a margine della media:
    e' la misura di quanto il risultato dipenda da chi capita in verifica, ed
    e' dello stesso ordine di molte differenze che si vorrebbero confrontare.
    Per questo viene sempre riportata accanto alla media.
    """
    if not fold:
        return {}
    out = {'n_fold': len(fold)}
    for k in ('fbeta', 'f1', 'recall', 'precision'):
        v = np.array([f[k] for f in fold], dtype=float)
        out[f'{k}_media'] = float(v.mean())
        out[f'{k}_dev'] = float(v.std(ddof=0))
    for k in ('tp', 'fp', 'fn', 'tn'):
        out[f'{k}_tot'] = int(sum(f[k] for f in fold))
    return out


def tabella_fold(fold: list, nomi: list) -> str:
    """Tabella per fold: la media da sola nasconde i fold anomali."""
    r = [f"{'fold (verifica)':<18}{'soglia':>8}{'F2':>8}{'recall':>8}"
         f"{'prec.':>8}{'TP':>6}{'FP':>6}{'FN':>6}",
         '-' * 68]
    for n, f in zip(nomi, fold):
        r.append(f"{n:<18}{f['soglia']:8.2f}{f['fbeta']:8.3f}{f['recall']:8.3f}"
                 f"{f['precision']:8.3f}{f['tp']:6d}{f['fp']:6d}{f['fn']:6d}")
    a = aggrega(fold)
    r.append('-' * 68)
    r.append(f"{'media +- dev':<18}{'':>8}"
             f"{a['fbeta_media']:8.3f}{a['recall_media']:8.3f}"
             f"{a['precision_media']:8.3f}"
             f"{a['tp_tot']:6d}{a['fp_tot']:6d}{a['fn_tot']:6d}")
    r.append(f"{'':<18}{'':>8}{'+-'+format(a['fbeta_dev'],'.3f'):>8}")
    return '\n'.join(r)
