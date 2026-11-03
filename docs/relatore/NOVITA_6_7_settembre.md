# Che cosa è emerso il 6 e il 7 settembre

Due giornate di verifiche hanno prodotto **dodici risultati nuovi**, di cui
**otto sono difetti trovati nel lavoro stesso**. Vale la pena leggerli insieme,
perché tre di essi hanno **la stessa causa** e nessuno se n'era mai accorto.

Nessuno ribalta una conclusione. Quello che cambia è la **riproducibilità** — il
punto su cui il lavoro era più fragile — e in due casi il sistema ne esce
**migliorabile a costo zero**.

---

## Il filo che li tiene insieme: MediaPipe Pose è un tracciatore

Lo stimatore di posa **mantiene stato fra un fotogramma e il successivo**. È ciò
che lo rende buono — segue la persona che ha già trovato invece di ricominciare
da capo — ed è una proprietà che il progetto non aveva mai messo per iscritto.

In due giorni ha prodotto **tre difetti distinti**, in tre punti diversi del
lavoro:

| dove | che cosa succedeva | |
|---|---|---|
| fra riprese di una **misura** | un solo stimatore per cinquanta riprese: l'ultima immagine di una — persona a terra — condizionava la prima della successiva | [ISS-133](../ISSUES.md) |
| fra **persone** dentro una ripresa | perde chi cade e si aggancia a un astante seduto, in 11 riprese su 50 di Camera 2 | [ISS-134](../ISSUES.md) |
| fra riprese del **dataset** | un solo stimatore per tutti i 220 video: le feature dipendono dall'ordine di elaborazione | [ISS-138](../ISSUES.md) |

**Non è una svista ripetuta tre volte: è una proprietà del componente**, e la
correzione è sempre la stessa — uno stimatore che nasce e muore dentro ciascuna
ripresa.

---

## 1. Il dataset è stato rifatto da capo

Le feature su cui poggia ogni risultato del lavoro dipendevano dall'ordine in
cui i 220 video erano stati elaborati. Riestraendo una ripresa già presente,
come controllo, **nessuna delle 866 righe coincideva** con quelle del dataset.

Quanto pesa, misurato in deviazioni standard della colonna:

| fotogrammi dall'inizio della ripresa | scarto |
|---|---:|
| 0–5 | **2,32 σ** |
| 5–50 | 0,26 σ |
| oltre 300 | 0,026 σ |

Decade, perché il tracciatore converge sulla persona che ha davanti. Ma le
riprese di **caduta** durano circa duecento fotogrammi: la parte contaminata è
lì un quarto del video invece di un ventesimo, e **le prime una o due finestre
di ogni ripresa cadono dentro di essa**.

Le conclusioni qualitative non erano in discussione — poggiano su divari molto
più grandi — ma la **riproducibilità** sì: chi riestraeva il dataset non
otteneva gli stessi numeri, e non c'era modo di sapere quale ordine fosse stato
usato.

**Scelta fatta: riestrarre tutto.** `feature_v3.csv`, chiuso alle 20:57 del 6
settembre: 220 riprese invece di 218 — due video mancavano davvero e un terzo
aveva un errore di battitura nel nome originale — 116.362 fotogrammi, 95,9% di
pose valide. **Le etichette non cambiano di un fotogramma**, il che è il
controllo che serviva.

## 2. L'altezza dal pavimento, che il sistema non aveva

Il Capitolo 3 dichiara che il sistema finale poggia su una configurazione che
comprende l'altezza del bacino dal pavimento. **Sulla board quella grandezza non
c'è**, e non poteva esserci: non era fra le 32 calcolate dal motore geometrico,
quindi il criterio di selezione non avrebbe potuto sceglierla nemmeno volendo
([ISS-139](../ISSUES.md)).

È emersa da una domanda giusta: *perché il sistema confonde «sdraiarsi sul
divano» con una caduta?* Il ragionamento era che l'altezza dal pavimento
distingue il divano dal pavimento **a prescindere dalla velocità**. È corretto —
e la risposta è che quella grandezza il modello installato non ce l'ha.

Reintrodotta, con una stima **causale** (si accumulano le osservazioni di chi
sta in piedi e si adatta la retta del pavimento quando ne bastano, perché sul
dispositivo non esiste il futuro), e misurata a parità di tutto il resto:

| | F2 | richiamo | falsi negativi | falsi positivi |
|---|---:|---:|---:|---:|
| 12 colonne | 0,807 | 0,834 | 249 | 501 |
| **13 colonne** | **0,866** | **0,894** | **163** | 443 |

**Il 35% dei falsi negativi in meno per una colonna sola**, e i falsi allarmi
calano anch'essi.

**Il particolare metodologico che va nel testo:** la selezione automatica **non
l'avrebbe scelta** — è 19ª su 33 in classifica — perché il criterio misura ogni
grandezza **da sola**, e da sola l'altezza dal pavimento non distingue chi si
sdraia da chi cade. Serve *insieme* alla dinamica. È un limite del criterio di
selezione, non della grandezza, e va detto dove il criterio viene presentato.

## 3. La prova di durata sulla board

4,59 ore continue, telecamera collegata, **sospensione della macchina misurata
pari a zero** — la differenza fra i due orologi è di 3,4 microsecondi. È
l'ultima delle richieste che dipendeva dall'hardware
([A4](A4_prova_di_durata.md), [B5](B5_prova_lunga.md)).

Ne è uscito anche il bilancio del costo per fotogramma **prodotto dalla stessa
esecuzione che ha prodotto gli allarmi**: 136,65 ms, cioè 7,3 fps. Chiude una
riserva aperta dal 26 agosto ([A3](A3_dispositivo_edge.md)).

## 4. La sessione che spariva dai numeri di campo

Lo script che calcola gli eventi cercava i punteggi in file di nome
`punteggi.csv`; il registratore della board scrive `<sessione>.csv`. **La
sessione di 4,59 ore non entrava in nessun numero, e lo script non se ne
lamentava** ([ISS-140](../ISSUES.md)).

Il fattore di sovrastima fra finestre ed eventi passa da **47,8 a 44,8**, su
14,98 ore invece di 10,39. E quel numero **non aveva un artefatto**: esisteva
solo nel testo. Ora ogni esecuzione lo scrive in un file, e le schede delle
figure lo leggono da lì.

## 5. Trentacinque numeri della tesi erano sepolti sotto una registrazione

Questo è il più insidioso dei cinque. Lo strumento che controlla se ogni numero
del testo ha un artefatto che lo produce raccoglie i valori da tutti i file
sotto `risultati/`. Copiando lì la sessione del 6 settembre sono entrati **due
CSV per campione**, uno per finestra e uno per fotogramma da 17,8 MB: la riserva
è passata a **1,8 milioni di valori distinti**.

Con quella massa di decimali arbitrari **ogni** numero del testo trova un
riscontro per caso. Il controllo dichiarava **zero numeri ingiustificati in
tutti i capitoli** — il risultato migliore mai visto.

| | con i CSV di sessione | **senza** |
|---|---:|---:|
| valori nella riserva | 1.827.905 | **10.769** |
| Cap3 / Cap4 / Cap5 / Conclusioni | 0 / 0 / 0 / 0 | **5 / 11 / 15 / 4** |

**I due file erano il 99,4% della riserva.** Trentacinque numeri non erano
giustificati: erano sepolti ([ISS-141](../ISSUES.md)).

Il difetto **è arrivato da solo**: nessuno ha toccato lo strumento, è bastato
copiare una registrazione nella cartella dei risultati. Chi avesse eseguito il
controllo senza sapere della sessione avrebbe concluso che il testo era a posto.

## 6. Il registratore della board non salva immagini, e dice il contrario

`rileva.py` apre la propria documentazione dicendo che le clip attorno agli
allarmi, «se attivate», restano su disco locale. **Non esiste alcun modo di
attivarle**: il codice non scrive nessun fotogramma
([ISS-142](../ISSUES.md)).

Il registratore usato in agosto le salvava — ±10 s attorno a ogni allarme, con
un tetto giornaliero — ed è con quelle che gli allarmi delle sessioni domestiche
sono stati guardati uno per uno.

Conseguenza: **i quattordici allarmi della prova di durata non sono
verificabili**, e la verifica di parità sui fotogrammi — l'unica che
intercetterebbe la divergenza fra PC e board — non ha potuto girare. Va portato
il salvataggio delle clip in `rileva.py` prima della prossima sessione lunga.

## 7. Il riaddestramento, concluso

Le sei architetture vanno rifatte sul dataset nuovo, altrimenti il confronto del
Capitolo 4 mette a fianco misure prese su archivi diversi. **Dodici run, dalle
09:22 alle 12:44 del 7 settembre.**

| architettura | F2 su v2 | **su v3, 12 colonne** | **su v3, con l'altezza dal pavimento** |
|---|---:|---:|---:|
| CNN 1D | 0,833 | 0,828 | **0,885** |
| GRU | 0,847 | 0,819 | 0,842 |
| foresta | 0,792 | 0,807 | **0,866** |
| Transformer | 0,846 | 0,799 | 0,860 |
| LSTM | 0,858 | 0,783 | **0,864** |
| rete a grafo | 0,779 | 0,699 | 0,756 |

**Due risultati distinti.**

Il primo: **nessuno scarto fra v2 e v3 arriva alla dispersione fra soggetti
(±0,085)**, il rifacimento non ribalta nulla, e l'escursione fra le cinque
architetture non a grafo **si stringe da 0,066 a 0,045** — metà della
dispersione. È la dimostrazione più forte che la tesi abbia dell'affermazione
che porta: **le architetture non sono distinguibili fra loro**.

Il secondo: **l'altezza dal pavimento migliora tutte e sei**, con un guadagno
medio di +0,056. Nessun guadagno singolo è distinguibile, ma sei segni concordi
su sei hanno probabilità $2^{-6} = 0{,}016$ se la colonna non servisse. È il
fatto che rende la decisione D5 informata invece che teorica.


## 8. Le tre righe sul punto di vista, rifatte — e un risultato ritirato

Erano l'ultima misura del lavoro ancora ferma a **cinque** soggetti, mentre la
misura geometrica che le spiega era già a dieci: due provenienze nello stesso
paragrafo. Rifatte a dieci sul dataset nuovo, il divario fra le viste passa da
0,422 a **0,334** e il rimedio — addestrare su entrambe — funziona meglio di
quanto sembrasse, dal 58% al 73%.

**Nella stessa esecuzione sono state separate le due cause** del divario:
togliendo le undici riprese in cui lo stimatore cambia persona il divario **non
si chiude**, quindi è compressione ottica e non difetto dello stimatore. Era un
limite che il testo poteva solo dichiarare.

**E un'affermazione del Capitolo 4 è caduta.** Il testo diceva che addestrare
sulla vista buona e trasferire batte di **2,5×** l'addestrare direttamente sulla
vista povera. A dieci soggetti il confronto **si rovescia**: 0,753 contro 0,488.
L'affermazione è stata ritirata ([ISS-143](../ISSUES.md)); al suo posto resta
che addestrare su due viste e addestrare su quella di esercizio **non sono
distinguibili**.

## 9. Una soglia scritta nel codice senza motivo

La tabella dell'escursione conta le «sequenze sopra 60°». Quel 60 era un
letterale nel codice, senza commento, e **in nessun punto del progetto era
giustificato** ([ISS-144](../ISSUES.md)).

La conclusione non ne dipende, ed è stato verificato: da 30° a 80° la vista
laterale supera la soglia fra 2,5 e 13 volte più spesso, senza mai cambiare
verso. La didascalia lo dichiara ora come **convenzione di lettura**, con
l'intervallo su cui è stata controllata.

## 10. La robustezza alle occlusioni dipende dalle colonne, non dai punti

Rifacendo la misura con il motore corrente, il danno peggiore **raddoppia**: le
spalle passano da −0,020 a −0,037 di F2. La conclusione regge — resta sotto la
dispersione fra soggetti — ma il margine passa da un fattore quattro a un
fattore due.

**La causa è stata isolata con una terza esecuzione**, motore nuovo e colonne
precedenti: i numeri di prima tornano. Non è il motore, **sono le colonne**, e si
spiega con una sola su dodici — entra l'angolo del tronco, che dipende dalle
spalle, al posto di una grandezza riferita al naso.

Ne segue una conclusione più precisa: non è che l'informazione sia distribuita
*in sé*, **lo è per un dato insieme di grandezze**. La robustezza alle occlusioni
si sceglie insieme alle grandezze.

## 11. La latenza si misurava, e il «limite inferiore» non lo era

Il lavoro dichiarava la latenza non misurabile. È vero **per il campo**, dove
l'annotazione è al minuto; **è falso per il laboratorio**, dove l'etichetta è
per fotogramma. Misurata su cinquanta cadute invece che su cinque, la mediana è
**2,44 s**.

E il Capitolo 5 dichiarava **3,778 s** come limite inferiore. Non lo è: quel
conto assume che la finestra debba riempirsi *dopo* l'inizio della caduta, e non
è richiesto — il classificatore decide su finestre a cavallo dell'istante di
inizio. Il minimo misurato è **+0,17 s** ([ISS-145](../ISSUES.md)).

## 12. La regola di allarme è la peggiore delle quattro provate

È il risultato pratico più utile della giornata, e nasce da un'osservazione che
il Capitolo 5 conteneva senza trarne la conseguenza: tre cadute vere non
producono allarme «con corse massime di due, zero e tre finestre».

La regola chiede cinque finestre **consecutive**: **azzera l'evidenza già
accumulata ogni volta che un fotogramma va storto** — cosa che succede proprio
nelle cadute difficili, dove la persona esce dal campo o si copre.

Confrontando ventuno regole di quattro famiglie, **senza riaddestrare nulla**:

| regola | cadute prese | latenza | falsi allarmi in casa |
|---|---:|---:|---:|
| **cinque consecutive** *(installata)* | 44 su 50 | 2,47 s | 10,8/ora |
| cumulata | **49 su 50** | **1,61 s** | 9,3/ora |
| **isteresi** | 48 su 50 | 2,00 s | **5,1/ora** |

**Undici regole su venti battono quella installata su entrambi gli assi**, e il
risultato è strutturale — tutte le varianti della cumulata, quasi tutte
dell'isteresi. Cambiarla costa **quattro righe di codice sul dispositivo e
nessun riaddestramento**.

---

## Che cosa questi due giorni dicono del lavoro

Otto difetti su dodici risultati sono difetti trovati **da noi, cercandoli**, e
tre condividono una causa che ora è scritta. **Nessuno ribalta una
conclusione:** il dataset rifatto sposta l'F2 di meno della dispersione fra
persone, il divario fra le viste risulta più grande e non più piccolo, e la
robustezza alle occlusioni resta sotto il rumore.

Ciò che cambia è la **riproducibilità**, ed è il punto su cui il lavoro era più
fragile: numeri trascritti da terminali, un dataset che dipendeva dall'ordine di
elaborazione, un fattore citato quattro volte e calcolato da nessuna parte, una
soglia scelta a occhio.

**E due risultati vanno nella direzione opposta, cioè migliorano il sistema
senza costare niente:** l'altezza dal pavimento, che toglie il 35% dei falsi
negativi e migliora tutte e sei le architetture, e la regola di allarme, che
cambiata dimezza i falsi allarmi prendendo più cadute. Nessuna delle due
richiede di riaddestrare alcunché.
