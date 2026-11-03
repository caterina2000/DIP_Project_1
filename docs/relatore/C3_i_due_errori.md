# C3 — Punto 5: mostrare i due errori, non un solo F2

**Che cosa è stato chiesto:** non riassumere tutto in un F2. Mostrare
separatamente **falsi negativi** e **falsi positivi**, perché in un sistema di
sicurezza non sono intercambiabili e un indice solo li nasconde.

**La risposta in una riga:** **fatto — ed è stata la richiesta più fertile delle
nove**: ha prodotto due tabelle nuove nel Capitolo 4 e ha smentito l'ipotesi che
tutti avevano in testa su come il sistema sbaglia.

---

## Come ci siamo arrivati, passo per passo

### Passo 1 — La tabella dei due errori per configurazione

Falsi negativi e falsi positivi per ciascuna delle cinque configurazioni, più la
figura `fig_errori.png`. Il dato principale, a dieci soggetti:

| | falsi negativi | falsi positivi |
|---|---:|---:|
| A3 | 45 | 172 |
| **A3i + controesempi** | **14** | **124** |

**In laboratorio la configurazione finale non introduce alcuno scambio**:
migliora entrambi gli errori. Lo scambio compare solo in casa, che è esattamente
la tesi del Capitolo 5.

### Passo 2 — Chiedersi *da dove vengono* i falsi allarmi

Un conteggio aggregato dice quanti sono, non da dove vengono. I falsi allarmi
sono stati attribuiti all'**attività** da cui proviene ciascuna finestra,
rileggendo i punteggi già salvati — nessun nuovo addestramento — e ricostruendo
le finestre con lo stesso codice che le costruisce in addestramento. Le
numerosità coincidono su tutti e dieci i fold, quindi l'attribuzione è
verificabile e non congetturale.

| attività | finestre | falsi allarmi | quota |
|---|---:|---:|---:|
| camminare | 1.390 | 0 | 0,0% |
| stare in piedi | 2.552 | 0 | 0,0% |
| saltare | 1.079 | 0 | 0,0% |
| sedersi | 2.525 | 19 | 0,8% |
| raccogliere un oggetto | 330 | 11 | 3,3% |
| **sdraiarsi** | 2.201 | **389** | **17,7%** |

**Su 419 falsi allarmi, 389 — il 93% — vengono da una sola attività.**
Camminare, stare in piedi e saltare non ne producono nemmeno uno su cinquemila
finestre.

### Passo 3 — L'ipotesi della velocità, verificata e smentita

L'obiezione naturale è che il sistema si allarmi per il **movimento rapido**.
Misurando il picco di velocità **verticale** del corpo dentro la finestra:

| gruppo | mediana | p90 |
|---|---:|---:|
| cadute vere | 0,055 | 0,622 |
| **camminare** | **0,087** | 0,629 |
| sdraiarsi, falso allarme | 0,030 | 0,106 |
| sdraiarsi, riconosciuta | 0,005 | 0,031 |

**Camminare ha il picco di discesa più alto delle cadute**, perché in due
secondi e mezzo di passi il corpo oscilla molte volte. Se il sistema decidesse
sulla velocità istantanea, camminare sarebbe il falso allarme principale: non ne
produce nessuno. **La velocità istantanea non è il discriminante**, ed è la
conferma diretta dell'argomento del Capitolo 3 a favore delle grandezze
integrali.

*Un errore commesso e corretto nel farlo:* la prima versione dell'analisi usava
il **modulo** dello spostamento dell'anca, cioè velocità in qualunque direzione.
Con quella, camminare risultava sette volte più veloce delle cadute — vero e
privo di significato, perché quella grandezza non ha un verso. Rifatta con la
componente verticale con segno.

### Passo 4 — Scomporre anche i positivi

| tipo di caduta | finestre | richiamo |
|---|---:|---:|
| di lato | 274 | 0,934 |
| in avanti sulle mani | 329 | 0,915 |
| seduta su sedia vuota | 288 | 0,753 |
| in avanti sulle ginocchia | 302 | 0,715 |
| **all'indietro** | 230 | **0,704** |

**Ventitré punti di richiamo** fra la migliore e la peggiore: un divario più
grande di quello fra due qualunque delle sei architetture confrontate. La caduta
all'indietro è la più difficile, ed è plausibile che sia lo stesso meccanismo
che rende cieca la vista rialzata — è la direzione in cui il tronco ruota meno
nel piano dell'immagine. **È una lettura, non una misura.**

### Passo 5 — Il seguito del 6-7 settembre: perché il sistema confonde il divano

La domanda nata da questa richiesta — *perché sdraiarsi?* — ha prodotto il
risultato più importante degli ultimi due giorni.

Il ragionamento era: **l'altezza del bacino dal pavimento distingue il divano
dal pavimento a prescindere dalla velocità**, quindi il modello dovrebbe
riuscirci. È corretto, e la risposta è che quella grandezza il modello
installato **non ce l'ha** — e non poteva averla, perché non era fra le
grandezze calcolate ([ISS-139](../ISSUES.md)).

Reintrodotta, e misurata a parità di tutto il resto:

| | F2 | richiamo | FN | FP |
|---|---:|---:|---:|---:|
| 12 colonne | 0,807 | 0,834 | 249 | 501 |
| **13 colonne, con l'altezza dal pavimento** | **0,866** | **0,894** | **163** | 443 |

**I falsi negativi calano del 35% aggiungendo una sola colonna**, e i falsi
allarmi calano anch'essi: non è uno scambio fra i due errori.

Va detto però che **in UP-Fall quella grandezza non risolve i falsi allarmi**:
nell'archivio ci si sdraia sul pavimento, non su un divano, e le due quote
coincidono — 0,12 contro 0,11 lunghezze di torso. Il beneficio atteso è sui
**falsi negativi** e sul trasferimento in casa, dove il divano esiste e la
differenza misurata sul campo è +1,47 contro +0,02.

---

## Dove guardare

| | |
|---|---|
| attribuzione delle finestre | `risultati/addestramento/_mappa_finestre.npz` |
| run con e senza l'altezza dal pavimento | `risultati/addestramento/run_foresta_tre_classi_DTW*_cam1_L22.json` |
| registro | [EXP-021](../EXPERIMENTS.md), [EXP-023](../EXPERIMENTS.md), [ISS-139](../ISSUES.md) |
| nella tesi | Capitolo 4, `tab:errori_attivita`, `tab:richiamo_tipo`, `fig:errori` |
