# D — Le domande che attendono una risposta sua

Queste non sono risposte: sono i punti in cui la scelta non è tecnica, e va
fatta da chi giudica il lavoro. Le prime quattro erano già poste il 26 agosto;
le ultime tre nascono dai due giorni scorsi.

---

## D1 — La fusione fra contesto e stato dell'arte

**Era la domanda:** unire il capitolo di contesto e quello sullo stato
dell'arte, come proposto, oppure tenerli separati?

**Superata dai fatti, ma la scelta va ratificata.** La struttura applicata li
tiene **separati**, e la ripetizione che la fusione doveva eliminare è stata
tolta in un altro modo: tre argomenti che comparivano in entrambi — la scelta
della visione contro gli indossabili, la motivazione di riservatezza della posa,
il conto sulla frequenza di base — stanno ora **solo nel Capitolo 1**, e il
Capitolo 2 vi rimanda.

Il risultato è cinque capitoli invece di otto ([C7](C7_indice_e_struttura.md)).
Resta da sapere se la soluzione adottata risponde all'obiezione o se la fusione
va comunque fatta.

---

## D2 — L'interpretazione sugli ingressi della foresta

**È la domanda:** l'interpretazione meccanicistica — la foresta riceve la
finestra senza ordine temporale, quindi le grandezze integrali le servono più
che alle reti — va **tenuta come lettura dichiarata**, oppure **tolta**?

**Il fatto che la rende una domanda:** la lettura è corretta come meccanismo, ma
il numero che la sosteneva non sopravvive a dieci soggetti — il vantaggio non è
distinguibile dal caso, e con una variante della regola di etichettatura cambia
segno ([C1](C1_ingressi_della_foresta.md)).

**La proposta:** tenerla accanto alla tabella della numerosità necessaria, detta
come lettura del fenomeno e **non come contributo misurato**, con scritto quanti
soggetti servirebbero per verificarla (fra 34 e 70). Toglierla del tutto
significherebbe perdere l'unica spiegazione disponibile di un comportamento
osservato.

---

## D3 — La latenza di rilevamento

**Era la domanda:** come riportare la latenza, visto che i dati non permettono
di misurarla?

**Risolta il 7 settembre, con una misura vera.** In casa non è calcolabile,
perché l'annotazione è al minuto e la grandezza vale pochi secondi. **In
laboratorio sì**: in UP-Fall l'etichetta è per fotogramma, e le cadute sono
cinquanta invece di cinque. La mediana è **2,44 s**
([B4](B4_eventi_e_latenza.md), [EXP-028](../EXPERIMENTS.md)).

Nel farlo è emerso che il «limite inferiore» di 3,778 s dichiarato nel Capitolo
5 **non era un limite inferiore**: la misura sta un secondo sotto, perché il
sistema decide su finestre a cavallo dell'istante di inizio invece di aspettare
che la finestra si riempia dopo. Il capitolo lo chiama ora *caso conservativo*.

Resta da sapere se la forma adottata — latenza misurata in laboratorio,
dichiarata non misurabile in casa, con la ragione — è accettabile in sede di
discussione.

---

## D4 — Quale dei due sistemi installabili presentare

**È la domanda che pesa di più.** Ce ne sono due, e non uno:

| | falsi allarmi | cadute rilevate |
|---|---:|---:|
| **con** i controesempi | 2,5 eventi/ora | **3 su 5** |
| **senza**, configurazione ottimizzata | 14,0 eventi/ora | **4 su 5** |

Con questi numeri la seconda sembra preferibile: in un sistema di sicurezza una
caduta persa pesa più di undici allarmi all'ora in più. Ma è una scelta di
merito, non una conclusione dei dati.

**La domanda:** presentare la scelta come **aperta**, dichiarando il criterio, o
indicare la configurazione a recall pieno come **sistema proposto** e l'altra
come variante?

> Va ripetuto che **cinque cadute non stimano un recall**: l'intervallo di
> confidenza va da 0,28 a 0,99 e non permette di distinguere alcuna
> configurazione da un'altra. Qualunque delle due si presenti, quel limite va
> dichiarato accanto.

---

## D5 — L'altezza dal pavimento: installarla o correggere il testo *(nuova)*

**Il fatto.** Il Capitolo 3 dichiara che il sistema finale poggia su una
configurazione che comprende **l'altezza del bacino dal pavimento**. Sul
dispositivo quella grandezza non c'è, e non poteva esserci: non era fra quelle
calcolate dal motore geometrico ([ISS-139](../ISSUES.md)).

Reintrodotta e misurata, **toglie il 35% dei falsi negativi**: 249 → 163, con
l'F2 che sale da 0,807 a 0,866 ([C3](C3_i_due_errori.md)).

**La domanda:** rifare l'export sulla board con la configurazione a tredici
colonne — il che richiede una nuova prova di parità e una sessione di controllo,
cioè una giornata di lavoro sul dispositivo — oppure **correggere il testo**,
dichiarando che l'installato è il sottoinsieme a dodici colonne e che la
configurazione migliore appartiene all'impianto precedente?

La prima rende vero ciò che il testo afferma. La seconda è onesta e rinuncia al
risultato migliore del lavoro.

---

## D6 — I 4,47 ms attribuiti alla board *(nuova)*

**Il fatto.** Il Capitolo 4 attribuisce alla board un costo di 4,47 ms per
finestra. La board misurata ne fa **39,04**; il calcolatore, misurato
indipendentemente, ne fa 4,85 ([C5](C5_coerenza_dei_millisecondi.md)).

**La domanda:** ritirare quel numero, o dichiararlo come misura sul calcolatore
mettendo accanto quella della board? La seconda conserva un'informazione — il
rapporto di otto fra le due macchine — che è a sua volta un risultato.

---

## D7 — Cambiare la regola di allarme *(nuova)*

**Il fatto.** La regola installata — cinque finestre consecutive sopra soglia —
è la peggiore delle quattro famiglie provate. Rileggendo gli stessi punteggi,
senza riaddestrare nulla ([EXP-029](../EXPERIMENTS.md)):

| regola | cadute prese | latenza | falsi allarmi in casa |
|---|---:|---:|---:|
| **cinque consecutive** *(installata)* | 44 su 50 | 2,47 s | 10,8/ora |
| cumulata | **49 su 50** | **1,61 s** | 9,3/ora |
| **isteresi** | 48 su 50 | 2,00 s | **5,1/ora** |

Il difetto della regola installata è la parola «consecutive»: azzera l'evidenza
accumulata a ogni fotogramma storto, ed è per questo che tre cadute vere delle
sessioni domestiche non hanno prodotto allarme pur essendo state viste.

**La domanda:** adottare una regola diversa — cioè cambiare quattro righe di
codice sul dispositivo, senza toccare il modello — o tenere quella installata e
riportare il confronto come risultato?

Adottarla significa rifare la prova di parità e una sessione di controllo.
Tenerla significa presentare un sistema che, per come si è scoperto oggi,
scarta gratuitamente una caduta su dieci.

---

## Dove guardare

| | |
|---|---|
| numerosità necessaria per ogni confronto | [EXP-013](../EXPERIMENTS.md) |
| configurazioni installabili | `risultati/campo/compiti_in_casa.json` |
| altezza dal pavimento | [EXP-023](../EXPERIMENTS.md), [ISS-139](../ISSUES.md) |
| costo del classificatore | [EXP-019](../EXPERIMENTS.md), [ISS-137](../ISSUES.md) |
