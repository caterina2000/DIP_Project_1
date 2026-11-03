# B4 — Metriche di campo a livello di evento

**Che cosa è stato chiesto:** riportare i numeri di campo come li vivrebbe una
persona che ha il sistema installato in casa — **eventi**, non finestre — e con
quattro grandezze: quota di cadute rilevate, falsi allarmi per ora, tempo medio
fra falsi allarmi, **latenza** dall'inizio della caduta alla segnalazione.

**La risposta in una riga:** **tutte e quattro sono ora calcolate**, ma non
tutte sullo stesso dato: le prime tre in casa, la quarta **in laboratorio**,
perché in casa non è misurabile e questo è dimostrato.

> **Aggiornato il 7 settembre 2026.** Fino a ieri la risposta era «tre grandezze
> su quattro». La latenza è stata misurata su cinquanta cadute
> ([EXP-028](../EXPERIMENTS.md)), e nel farlo è emerso che il limite inferiore
> analitico dichiarato nel Capitolo 5 **non era un limite inferiore**
> ([ISS-145](../ISSUES.md)).

---

## Le quattro grandezze, con i numeri

### 1 e 2 — Falsi allarmi per ora, e tempo medio fra falsi allarmi

Nove sessioni domestiche, **14,98 ore**, due abitazioni:

| sessione | ore | eventi | eventi/ora | tempo medio fra allarmi | tempo sopra soglia |
|---|---:|---:|---:|---:|---:|
| multi 3 persone, 13/08 | 0,66 | 66 | **100,5** | 0,6 min | **70,1%** |
| nonni, 12/08 | 1,20 | 41 | 34,2 | 1,6 min | 12,4% |
| cadute nonni, 12/08 | 0,75 | 19 | 25,4 | 2,4 min | 10,7% |
| multipersona, 10/08 | 0,35 | 4 | 11,5 | 1,5 min | 2,6% |
| solo, 10/08 | 0,38 | 4 | 10,4 | 1,7 min | 4,3% |
| cadute sola, 13/08 | 0,58 | 4 | 6,9 | 8,0 min | 0,6% |
| **notte, 06/09** *(board)* | 4,59 | 14 | **3,1** | 14,6 min | 0,3% |
| durata 5 h, 11/08 | 6,11 | 14 | 2,3 | 24,6 min | 0,4% |
| due persone, 10/08 | 0,35 | 0 | 0,0 | — | 0,0% |
| **totale** | **14,98** | **166** | **11,1** | | |

**Il riferimento di letteratura per un'installazione funzionante è 0,049
eventi/ora**, cioè uno ogni venti ore. Siamo a 11,1: due ordini di grandezza
sopra. La sessione migliore, quella notturna sulla board, sta a 3,1.

**La dispersione fra sessioni è essa stessa il risultato**: da 0 a 100 eventi
all'ora. Il fattore che le separa non è il modello — è **quante persone ci sono
in scena e che cosa fanno**: la sessione peggiore ha tre persone che si
siedono e si distendono, la migliore è una stanza quasi sempre vuota.

### 3 — Quota di cadute rilevate

Qui la risposta **non è un numero, è un intervallo con i parametri esposti**, ed
è il punto di [C6](C6_parametri_del_recall.md):

| tolleranza di accoppiamento | persistenza 1 | persistenza 5 |
|---|---|---|
| ±10 s | 0 su 4 | 0 su 4 |
| ±30 s | 2 su 5 | 1 su 5 |
| ±60 s | 3 su 5 | 1 su 5 |
| ±90 s | **4 su 5** | 1 su 5 |

**Lo stesso sistema, sugli stessi dati, va da 0/4 a 4/5.** Il «quattro su
cinque» che circolava sta nell'angolo più permissivo: tre minuti di banda
attorno alla caduta e un allarme che scatta su una finestra isolata. Con
parametri clinicamente difendibili — allarme entro mezzo minuto, non su una
finestra sola — il richiamo è **una caduta su cinque**.

E cinque cadute non stimano un richiamo: l'intervallo di confidenza va da 0,28 a
0,99.

### 4 — La latenza

**In casa non è misurabile, e non è una rinuncia: è un fatto dimostrato.** Le
cadute sono annotate **al minuto**, la grandezza da misurare vale **pochi
secondi**: l'incertezza sull'istante vero è fino a sessanta volte la quantità
cercata. Il dato che lo rende evidente: la prima finestra sopra soglia cade a
+11,8, +19,4, +27,7 e +32,3 secondi dal minuto annotato, e quegli scarti non
sono ritardi del sistema — sono il punto del minuto in cui la persona è caduta.

**In laboratorio invece si misura**, e questa è la novità: in UP-Fall
l'etichetta è **per fotogramma**, quindi l'istante di inizio è noto a 1/18 di
secondo, e le cadute sono **cinquanta** invece di cinque.

| persistenza | riprese con allarme | richiamo | latenza mediana | p90 | peggiore |
|---:|---:|---:|---:|---:|---:|
| 1 | 50 su 50 | **1,00** | **1,44 s** | 3,39 s | 4,00 s |
| 3 | 47 su 50 | 0,94 | 2,00 s | 4,04 s | 4,56 s |
| **5** *(installata)* | **45 su 50** | **0,90** | **2,44 s** | 4,51 s | 5,00 s |
| 10 | 44 su 50 | 0,88 | 3,56 s | 5,52 s | 6,11 s |

Sulla board, che gira a 7,3 fps invece di 9, la stessa mediana varrebbe circa
**3,0 s** — è una proporzione, non una misura.

---

## Perché cinque finestre consecutive, e da cosa si dice che vada bene

**Fino al 7 settembre: da niente.** Il valore 5 sta in
`deploy_board/metadata.json`, è scritto come costante in `esporta_board.py` e
applicato da `rileva.py`, e **in nessun punto del progetto era giustificato**.
La soglia 0,50 ha una provenienza dichiarata nel metadato stesso; la persistenza
no. Era un parametro ereditato da uno script all'altro
([ISS-145](../ISSUES.md)).

Non è un dettaglio: è il parametro che porta il richiamo di campo da quattro
cadute su cinque a una.

**Ora il prezzo è misurato, ed è preciso:** ogni passo di persistenza costa
**0,222 secondi** — esattamente il passo con cui la finestra avanza — e una
frazione di richiamo.

| | k = 1 | **k = 5** |
|---|---:|---:|
| richiamo in laboratorio | 1,00 (50 su 50) | 0,90 (45 su 50) |
| latenza mediana | 1,44 s | 2,44 s |
| eventi di falso allarme in casa | 16,0/ora | **11,1/ora** |

**Passare da 1 a 5 costa un secondo di latenza e dieci punti di richiamo, e
compra il 31% di falsi allarmi in meno.**

È la prima volta che i due lati del compromesso stanno nello stesso posto.
**Se cinque sia la scelta giusta resta discutibile** — con 11 eventi/ora contro
lo 0,049 della letteratura, il guadagno del 31% non risolve il problema, mentre
i dieci punti di richiamo si pagano su una caduta vera. Ma ora è discutibile
**con i numeri** invece che per omissione, e la curva completa è in
[EXP-028](../EXPERIMENTS.md).

## Perché esiste un periodo di sospensione

Perché **il falso positivo dominante di questo progetto non è un evento: è uno
stato che dura.**

Una persona che si distende sul divano e ci resta un'ora non produce un allarme
che si ripete: produce una condizione. Senza sospensione, la regola delle cinque
finestre consecutive scatterebbe di nuovo ogni 1,1 secondi per tutta l'ora —
oltre tremila allarmi per un solo fatto. La sospensione di trenta secondi
riconosce che, dopo un allarme, il sistema sta guardando **lo stesso fatto**.

**Ma va detto il suo limite, e il testo lo dichiara.** La sospensione ritaglia
uno stato in eventi periodici, e così **il numero di eventi diventa una funzione
del periodo di sospensione invece che del fenomeno**:

| persistenza | sosp. 10 s | **sosp. 30 s** | sosp. 60 s | sosp. 300 s |
|---:|---:|---:|---:|---:|
| 1 | 32,5 | 16,0 | 10,5 | 4,1 |
| 3 | 24,0 | 12,3 | 8,2 | 3,5 |
| **5** | 21,6 | **11,1** | 7,5 | 3,3 |
| 10 | 18,6 | 8,7 | 5,9 | 2,7 |

**Lo stesso sistema, sugli stessi dati, dà da 2,7 a 32,5 eventi all'ora a
seconda di come si aggrega.** Chi volesse un numero migliore non deve cambiare
il modello: gli basta allungare la sospensione.

Per questo accanto agli eventi si riporta sempre la **quota di tempo sopra
soglia**, che non dipende da nessuno dei due parametri: sulla sessione peggiore
vale il 70%, cioè il sistema ha passato due terzi del pomeriggio convinto che
qualcuno fosse caduto. È la misura più onesta per un falso positivo che è uno
stato.

---

## L'unità di misura, che è il cuore della richiesta

Il sistema decide ogni 0,25 s. Una persona che resta a terra produce una
**raffica** di decisioni positive consecutive: contarle come altrettanti allarmi
è un errore di quasi due ordini di grandezza.

**Sulle registrazioni domestiche il rapporto fra le due contabilità vale 44,8**:
496 finestre sopra soglia all'ora diventano 11,1 eventi.

> **Correzione del 7 settembre.** Il fattore era dichiarato **47,8**. Lo script
> che lo calcola cercava i punteggi in file di nome `punteggi.csv`, che è il
> nome scritto dal registratore di agosto; il registratore della board scrive
> `<nome_sessione>.csv`. **La sessione di 4,59 ore del 6 settembre non entrava
> quindi in nessun numero di campo, e lo script non se ne lamentava**
> ([ISS-140](../ISSUES.md)). E quel numero **non aveva un artefatto**: esisteva
> solo nel testo. Ora ogni esecuzione scrive
> `risultati/campo/eventi_sessioni.json`.

---

## Il limite inferiore che non era un limite inferiore

La tabella della latenza nel Capitolo 5 dichiarava **3,778 s** come limite
inferiore: riempimento della finestra 2,743 s, persistenza 0,997 s, calcolo
0,038 s.

**La mediana misurata alla stessa regola è 2,44 s** — 2,74 s riportata alla
frequenza di quella tabella — cioè circa **un secondo sotto**.

La ragione sta in un'assunzione implicita: la scomposizione suppone che la
finestra debba riempirsi **dopo** l'inizio della caduta. Non è richiesto. Il
classificatore decide su finestre che stanno **a cavallo** dell'istante di
inizio, e il movimento iniziale della caduta basta a portarle sopra soglia: il
minimo misurato a persistenza uno è **+0,17 s**, cioè una finestra con tre
fotogrammi di caduta e quarantuno di ciò che la precede.

**3,778 s resta un numero utile — è la latenza del caso conservativo — ma non è
un limite inferiore**, e il Capitolo 5 lo chiama ora così.

Quello che la scomposizione dice, e che regge, è **dove sta il collo di
bottiglia**: la finestra di decisione, non l'hardware. 2,74 s contro 38 ms, un
fattore settantatré. Un dispositivo dieci volte più veloce sposterebbe il totale
dell'uno per cento.

---

## Che cosa questa risposta non copre

- **La latenza di campo resta non misurata**, e non è colmabile con questi dati:
  servirebbe riannotare le cadute domestiche al secondo, guardando le clip.
  Quelle esistono per le sessioni di agosto ma non per quella del 6 settembre
  ([ISS-142](../ISSUES.md)).
- **La latenza di laboratorio è misurata dall'annotazione**, non dall'inizio
  fisico della perdita di equilibrio: se l'annotatore ha segnato l'inizio in
  ritardo, la misura è sottostimata.
- Cinquanta cadute messe in scena da dieci persone giovani non sono cadute vere
  di persone anziane.

---

## Dove guardare

| | |
|---|---|
| eventi per sessione | `risultati/campo/eventi_sessioni.json` |
| latenza in laboratorio | `risultati/laboratorio/latenza_laboratorio_*.json` |
| scomposizione analitica | `risultati/campo/latenza.json` |
| script | `pipeline/eventi_sessioni.py` (con `--sensibilita`), `pipeline/latenza_laboratorio.py`, `pipeline/latenza.py` |
| registro | [EXP-028](../EXPERIMENTS.md), [ISS-145](../ISSUES.md), [ISS-140](../ISSUES.md), [ISS-115](../ISSUES.md) |
| nella tesi | Capitolo 5, `tab:latenza`, `tab:latenza_misurata`, `tab:tolleranza`, `fig:sessione` |
