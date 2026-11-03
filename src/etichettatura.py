"""
Dall'etichetta per fotogramma a quella della finestra.

Il problema
-----------
L'annotazione e' per fotogramma e a tre classi:

    0  attivita' quotidiana, oppure la fase precedente alla caduta
    1  caduta in corso, dalla perdita di equilibrio all'arrivo a terra
    2  post-caduta, la persona e' a terra

Il classificatore pero' non decide sul fotogramma ma su una finestra di
~2,4 s, che quasi sempre contiene fotogrammi di piu' classi. Serve una regola
per riassumerli, e la regola non e' un dettaglio tecnico: cambia quali
finestre finiscono nell'addestramento e con quale etichetta.

Le due decisioni indipendenti
-----------------------------
1. COME CONTARE. La regola precedente contava i fotogrammi della classe
   ovunque fossero nella finestra: cinque fotogrammi di caduta sparpagliati
   valevano quanto cinque consecutivi. Per un evento che e' per natura una
   dinamica continua e' incoerente. Qui si conta con il criterio K-su-M:
   servono almeno K fotogrammi della classe dentro un blocco locale di M.
   Tollera un fotogramma annotato male senza spezzare l'evento.

2. COSA FARE DELLA FASE 2. E' la decisione che pesa di piu', perche' la
   fase 2 e' PIU' ABBONDANTE della fase 1 -- sui dati di questo progetto
   2.483 fotogrammi contro 1.463 -- e dura molto piu' a lungo. Un sistema
   installato ha piu' occasioni di accorgersi che qualcuno E' a terra che
   di cogliere l'attimo in cui STA cadendo, ed e' anche cio' che conta
   clinicamente: il danno della long-lie syndrome dipende dal tempo passato
   a terra, non dall'impatto.

   Tre trattamenti possibili, tutti implementati qui perche' vanno
   CONFRONTATI e non scelti a priori:

     'scarta'      la finestra con troppa fase 2 viene esclusa.
                   E' il comportamento storico; toglie il 40% dei positivi.
                   Nella tesi e' il compito chiamato "evento".
     'caduta'      la fase 2 conta positiva QUANTO la fase 1, non al posto
                   suo: il commento precedente diceva "il sistema rileva lo
                   STATO invece dell'EVENTO", ma il codice due righe sotto
                   fa `1 if (terra or caduta) else 0` -- riconosce l'uno O
                   l'altro, non sostituisce l'uno con l'altro. Nella tesi e'
                   il compito chiamato "allarme".
     'tre_classi'  la finestra puo' valere 0, 1 o 2: il modello impara a
                   distinguerle, e in esercizio si allarma su 1 oppure 2.
                   E' l'unico modo che permette di distinguere "a terra" da
                   "disteso sul divano", che sono due stati e non due eventi.

3. CHE FARE DEL CONFINE. Una finestra puo' contenere fotogrammi di classe 1 o
   2 e non averne abbastanza da superare il criterio K-su-M. Oggi vale 0: un
   negativo pulito. Ma quella finestra sta a cavallo di una transizione, e
   chiamarla negativa non e' una misura, e' un'ipotesi sul confine --- e
   l'ipotesi contamina proprio la classe che deve restare pulita, perche' i
   negativi sono il denominatore di ogni falso allarme.

   Con `escludi_incerte` quelle finestre sono escluse invece che indovinate,
   come gia' avviene per le finestre della modalita' 'scarta'. Il valore
   predefinito sta in `config.ESCLUDI_FINESTRE_INCERTE` ed e' False: accenderlo
   cambia l'insieme di addestramento, quindi va fatto insieme a un
   riaddestramento e non da solo.
"""

from typing import Optional

import numpy as np

import config


def _blocco_k_su_m(maschera: np.ndarray, k: int, m: int) -> bool:
    """
    True se esiste un blocco di `m` fotogrammi consecutivi che ne contiene
    almeno `k` della classe cercata.

    Con m == k il criterio diventa "k consecutivi stretti"; con m molto
    grande degenera nel conteggio totale sulla finestra. I due estremi sono
    quindi casi particolari di questa stessa funzione, il che rende il
    confronto fra criteri una variazione di parametro invece che di codice.
    """
    n = len(maschera)
    if k <= 0:
        return True
    if n < k:
        return False
    m = min(m, n)
    # somma mobile su finestra m, calcolata con la somma cumulata
    cum = np.concatenate(([0], np.cumsum(maschera.astype(np.int32))))
    finestre = cum[m:] - cum[:-m]
    return bool(finestre.size and finestre.max() >= k)


def etichetta_finestra(etichette,
                       modo: str = 'tre_classi',
                       k_caduta: int = None,
                       m_blocco: int = None,
                       k_terra: int = None,
                       m_terra: int = None,
                       escludi_incerte: bool = None) -> Optional[int]:
    """
    Etichetta di una finestra a partire dalle etichette dei suoi fotogrammi.

    Parametri
    ---------
    etichette : sequenza di 0/1/2, lunga quanto la finestra
    modo      : 'scarta' | 'caduta' | 'tre_classi'
    k_caduta, m_blocco : almeno k_caduta fotogrammi di classe 1 dentro un
                         blocco di m_blocco consecutivi
    k_terra, m_terra   : stesso criterio per la classe 2

    Ritorna
    -------
    0, 1, 2 oppure None se la finestra va scartata.

    La precedenza e' sempre: prima si decide sulla fase 2, poi sulla fase 1.
    Una finestra che contiene entrambe descrive il momento in cui la caduta
    si e' appena conclusa, e in quel caso lo stato finale e' l'informazione
    piu' recente.
    """
    # I valori stanno in config, non qui: un default scritto nel modulo e un
    # valore dichiarato in config sono due sorgenti di verita' per lo stesso
    # parametro, e prima o poi divergono (ISS-112).
    k_caduta = config.K_CADUTA if k_caduta is None else k_caduta
    m_blocco = config.M_BLOCCO if m_blocco is None else m_blocco
    k_terra = config.K_TERRA if k_terra is None else k_terra
    m_terra = config.M_TERRA if m_terra is None else m_terra
    escludi_incerte = (config.ESCLUDI_FINESTRE_INCERTE
                       if escludi_incerte is None else escludi_incerte)

    e = np.asarray(etichette).astype(np.int8)
    if e.size == 0:
        return None

    terra = _blocco_k_su_m(e == 2, k_terra, m_terra)
    caduta = _blocco_k_su_m(e == 1, k_caduta, m_blocco)

    # Il confine: c'e' traccia dell'evento, ma sotto la soglia che lo dichiara.
    # Non e' un negativo, e' una finestra su cui non si sa.
    if escludi_incerte and not terra and not caduta and bool((e != 0).any()):
        return None

    if modo == 'scarta':
        if terra:
            return None
        return 1 if caduta else 0

    if modo == 'caduta':
        return 1 if (terra or caduta) else 0

    if modo == 'tre_classi':
        if terra:
            return 2
        return 1 if caduta else 0

    raise ValueError(f"modo sconosciuto: {modo!r} "
                     f"(attesi 'scarta', 'caduta', 'tre_classi')")


MODI = ('scarta', 'caduta', 'tre_classi')
