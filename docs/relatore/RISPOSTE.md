# Le richieste del relatore, e la risposta a ciascuna

Aggiornato al **7 settembre 2026**. Ogni numero di questo documento viene da un
file di risultato, non da un altro documento.

Per ogni richiesta c'è una scheda a parte che racconta passo per passo come ci
si è arrivati: il collegamento sta in fondo a ciascuna sezione, e l'elenco
completo è in [INDICE.md](INDICE.md).

> **Da mandare al relatore c'è
> [RELAZIONE_PER_IL_RELATORE.md](RELAZIONE_PER_IL_RELATORE.md)**, che dice le
> stesse cose in forma discorsiva e si legge dall'inizio alla fine. Questo file
> resta come versione per richiesta, con i rimandi alle schede.

---

## In sintesi

Le richieste vengono da tre momenti distinti e sono tenute separate perché hanno
storie diverse: **A** le quattro iniziali, **B** le cinque verifiche indicate a
voce, **C** i sette punti dell'email del 20 agosto. **D** sono invece le
domande poste a lei, che attendono una risposta.

**Nessuna richiesta è rimasta senza risposta, e con il 6 settembre si è chiusa
anche l'ultima che dipendeva dall'hardware** — la prova di durata sul
dispositivo. Ma il conteggio «tutte» sarebbe generoso, e va detto perché:

- la prova di durata è stata di **4,59 ore** e non di dodici;
- i **quattordici allarmi** che ne sono usciti **non sono verificabili**, perché
  il registratore della board non salva immagini;
- restano **trentacinque numeri del testo senza un artefatto** che li produca,
  emersi il 7 settembre da un difetto dello strumento che avrebbe dovuto
  segnalarli.

I due giorni appena passati hanno prodotto sette risultati nuovi, cinque dei
quali sono difetti trovati nel lavoro stesso: sono raccontati insieme in
**[NOVITA_6_7_settembre.md](NOVITA_6_7_settembre.md)**, e vale la pena leggerli
di seguito perché tre di essi hanno la stessa causa.

---

## A — Le quattro richieste iniziali

### A1 · Resilienza al cambio di telecamera e di ambiente

**Il sistema non è resiliente, e ora sappiamo di quanto, per quale causa, e
quale delle due cause candidate pesa davvero.**

Le tre righe erano l'ultima misura del lavoro ancora ferma a cinque soggetti:
il 7 settembre sono state rieseguite a dieci sul dataset riestratto
([EXP-026](../EXPERIMENTS.md)).

| addestrata su | verificata su | F2 | falsi allarmi | cadute perse |
|---|---|---:|---:|---:|
| Camera 1 | Camera 1 | 0,822 ± 0,099 | 722 | 186 |
| Camera 1 | **Camera 2** | **0,488 ± 0,119** | **3.252** | 451 |
| Camera 1 + 2 | Camera 2 | **0,731 ± 0,188** | 751 | 335 |
| *Camera 2* | *Camera 2* | *0,753 ± 0,179* | *1.067* | *246* |

Cambiare inquadratura costa **0,334 di F2**, circa **tre volte la dispersione
fra soggetti**. Addestrare su entrambe le viste ne recupera il **73%** e riporta
i falsi allarmi da 3.252 a 751. Trasferire alla vista rialzata non peggiora un
po' tutto: **fa esplodere un errore solo**.

La spiegazione geometrica è misurata: l'escursione dell'angolo del tronco vale
**74,0° sulla vista laterale contro 33,2° su quella rialzata**, rapporto
**2,23×**, con 30 sequenze su 39 sopra i 60 gradi contro 8.

**Il 6 settembre quel numero è cambiato per la terza volta**, e la causa è
interessante: il codice di misura riusava un solo stimatore di posa per tutte le
riprese, e MediaPipe è un tracciatore. Rifatto, e su dieci soggetti invece di
cinque, il rapporto passa da 1,99× a 2,23×.

**Un risultato del capitolo è invece caduto.** Il testo affermava che addestrare
sulla vista buona e trasferire batte di 2,5× l'addestrare direttamente sulla
vista povera. A dieci soggetti il confronto **si rovescia**: 0,753 addestrando
su Camera 2 contro 0,488 trasferendo da Camera 1. L'affermazione è stata
ritirata dal Capitolo 4 ([ISS-143](../ISSUES.md)); al suo posto resta che
addestrare su entrambe le viste e addestrare solo su quella di esercizio **non
sono distinguibili**, quindi chi installa sceglie in base a ciò che ha.

**E il divario ha due cause, non una.** Oltre alla compressione prospettica, su
Camera 2 lo stimatore **perde chi cade e si aggancia a un astante seduto in 11
riprese su 50** — su Camera 1 in 0 su 50. Arriva anche nei dati di
addestramento: nel dodici per cento delle cadute di Camera 2 il classificatore
riceve, per la fase a terra, le grandezze di un'altra persona.

**Le due cause sono state separate il 7 settembre, e non pesano allo stesso
modo.** Rifacendo le tre righe senza le undici riprese contaminate il divario
**non si chiude**: 0,334 con tutte, 0,356 senza. Il cambio di persona falsava la
*misura geometrica*; il divario di classificazione è sostanzialmente tutto
compressione prospettica.

Il dato che ha cambiato un criterio di lavoro: su Camera 2 una posa si trova nel
97,0% dei campioni contro l'85,7% di Camera 1. **La vista che porta meno
informazione è quella in cui lo stimatore fallisce meno spesso**, perché quando
perde il soggetto trova comunque qualcuno. La quota di pose rilevate non è una
misura di qualità.

*Cambio di ambiente:* trasferendo il modello a un archivio esterno l'F2 va a
**0,034**, contro 0,971 in dominio. Ritarando la soglia sulle etichette del
dominio di destinazione — la soglia oracolo, che chi installa non possiede —
si arriva a 0,492. Il divario totale, 0,937, si scompone quindi in **49%
taratura** (recuperabile, da 0,034 a 0,492) e **51% perdita reale della
capacità di separare** (da 0,492 a 0,971), che nessuna soglia recupera. La
conferma indipendente è la PR-AUC, che non dipende dalla soglia: 1,79 volte il
caso fuori dominio contro 18,7 dentro.

→ [scheda A1](A1_cambio_di_vista_e_di_ambiente.md)

### A2 · Resilienza alle occlusioni

**Nessun gruppo di punti del corpo è critico.** Mascherando gruppi di landmark
con il punto congelato all'ultima posizione nota, la perdita massima è
**0,020 di F2** — sulle spalle — contro una dispersione fra soggetti di 0,078.
Il danno è un quarto del rumore naturale dell'esperimento.

Il fenomeno di auto-occlusione osservato all'inizio del lavoro — la confidenza
del naso da 0,938 in piedi a 0,240 a terra — è **specifico di YOLOv8**: su
MediaPipe passa da 0,997 a 0,989. Nel testo resta attribuito allo stimatore su
cui è stato misurato.

**Non misurate:** le occlusioni da mobilio reale, che nessuno dei due archivi
annota.

→ [scheda A2](A2_occlusioni.md)

### A3 · Porting su nodo edge, senza video verso l'esterno

**Fatto, e il 6 settembre finalmente misurato invece che trascritto.** La catena
completa gira su una Radxa ROCK 4D da circa cento euro.

| | dichiarato in tesi | **misurato su 4,59 h** |
|---|---:|---:|
| percezione | 33,34 ms (88,4%) | **116,38 ms (85,2%)** |
| classificatore | 2,20 ms (5,8%) | **19,51 ms (14,3%)** |
| **totale** | **37,7 ms — 26,5 fps** | **136,65 ms — 7,3 fps** |

**Il dispositivo è 3,6 volte più lento di quanto il capitolo dichiarasse.** Le
proporzioni reggono, e con esse l'affermazione portante — il collo di bottiglia
è la percezione, non la classificazione. I valori assoluti no.

Il numero sbagliato era quello in tesi, e l'indizio era nel progetto da sempre:
il file di configurazione dichiara che la board regge circa **nove** fotogrammi
al secondo, ed è su quel presupposto che il dataset viene sottocampionato. I 7,3
misurati sono coerenti; i 26,5 non lo erano mai stati.

L'obiezione che la misura fosse a stanza vuota è stata verificata e
**falsificata**: con una persona in scena il costo *sale* da 126,0 a 144,1 ms.

L'acceleratore neurale **non viene usato**: costa 0,216 di F2, mentre dimezzare
la frequenza dei fotogrammi ne costa 0,041. Risultato negativo, tenuto nel testo.

→ [scheda A3](A3_dispositivo_edge.md)

### A4 · Prova di durata in ambiente reale

**Fatta.** Dodici blocchi domestici in agosto — due abitazioni, 10,39 ore
utilizzabili — e il **6 settembre 4,59 ore continue sulla board**, con la
telecamera collegata e nessun intervento.

| | |
|---|---:|
| durata | 4,59 ore |
| **sospensione della macchina** | **~0** (differenza fra i due orologi: 3,4 µs) |
| frequenza | 7,26 fps · pose valide 35,1% |
| interruzioni della telecamera | 2, per 5,1 s, riprese da sole |
| **eventi di allarme** | **14**, cioè 3,05/ora · tempo sopra soglia 0,3% |

**Non sono le dodici ore richieste, e i quattordici allarmi non sono
verificabili:** il registratore della board non salva immagini, mentre la sua
documentazione afferma che le clip attorno agli allarmi si possono attivare. Il
registratore usato in agosto le salvava, ed è con quelle che gli allarmi delle
sessioni domestiche sono stati guardati uno per uno.

Il numero riportabile è il **tasso di eventi**; chiamarli falsi allarmi sarebbe
un'affermazione senza prova.

→ [scheda A4](A4_prova_di_durata.md)

---

## B — Le cinque verifiche indicate

### B1 · PR-AUC nel passaggio all'archivio esterno

**È perdita vera, la meno comoda delle due possibilità.**

| | PR-AUC | rispetto alla prevalenza |
|---|---:|---:|
| archivio di addestramento | 0,990 | 18,7× |
| archivio mai visto | **0,169** | **1,79×** |

Con ROC-AUC 0,750. Nel dominio nuovo il modello è **meno di due volte meglio del
caso**: non è soltanto uno spostamento della scala dei punteggi.

→ [scheda B1](B1_pr_auc.md)

### B2 · Controesempi di una casa verificati sull'altra

**Fatta in entrambi i versi**, e indica la prima delle due ipotesi: il modello
impara una categoria trasferibile, non la stanza.

| controesempi da | verifica su | eventi/ora |
|---|---|---|
| casa dei nonni | casa dello studente | 0,342 → **0,171** |
| casa dello studente | casa dei nonni | 1,781 → **0,890** |

**Il costo va dichiarato insieme al beneficio:** in quella configurazione il
recall scende a **due cadute su cinque**.

→ [scheda B2](B2_controesempi.md)

### B3 · Verifica controllata sulle occlusioni

**Fatta nella forma suggerita**, ed è la stessa misura di A2: perdita massima
0,020 di F2 contro una dispersione fra soggetti di 0,078.

→ [scheda B3](B3_occlusioni_controllate.md)

### B4 · Metriche di campo a livello di evento

**Fatta per tre grandezze su quattro.**

Il punto centrale è l'unità di misura: una persona che resta a terra produce una
raffica di decisioni positive, e contarle come allarmi sovrastima di quasi due
ordini di grandezza. **Sulle registrazioni domestiche il rapporto vale 44,8**:
496 finestre sopra soglia all'ora diventano 11,1 eventi.

> Il 7 settembre quel numero è passato da 47,8 a 44,8. Lo script che lo calcola
> non vedeva la sessione del 6 settembre, perché il registratore della board
> scrive i punteggi con un altro nome di file — e non se ne lamentava. Il
> numero, inoltre, **non aveva un artefatto**: esisteva solo nel testo. Ora ogni
> esecuzione lo scrive in un file.

**La quarta grandezza — la latenza — non è misurabile con questi dati:** le
cadute sono annotate al minuto, mentre la grandezza da misurare è di pochi
secondi. Al suo posto c'è la scomposizione di ciò che invece si misura:

| addendo | valore | quota |
|---|---:|---:|
| calcolo per fotogramma | 0,038 s | 1,0% |
| **riempimento della finestra** | **2,743 s** | **72,6%** |
| persistenza | 0,997 s | 26,4% |
| **limite inferiore** | **3,778 s** | |

**La latenza è dominata dalla finestra di decisione, non dall'hardware:** un
fattore settantatré. Un dispositivo dieci volte più veloce sposterebbe il limite
dell'uno per cento.

→ [scheda B4](B4_eventi_e_latenza.md)

### B5 · Prova lunga con controllo della sospensione

**Fatta.** Il primo tentativo era *sembrato* riuscire: la macchina si era
sospesa e il registratore, che misurava il tempo con un orologio che durante la
sospensione non avanza, non se n'era accorto. È il modo peggiore in cui una
misura può essere sbagliata.

`rileva.py` tiene ora **due orologi** e dichiara la differenza in ogni
riepilogo. Il 6 settembre quella differenza è stata di **3,4 microsecondi**: la
macchina non ha dormito, e stavolta lo sappiamo invece di sperarlo.

→ [scheda B5](B5_prova_lunga.md)

---

## C — I punti dell'email del 20 agosto

### C1 · Gli ingressi della foresta e le grandezze integrali

**La sua lettura del meccanismo è corretta; i numeri su cui poggiava non lo
erano.** La finestra viene riassunta con sei statistiche per grandezza e non
contiene alcuna nozione di ordine: la foresta è l'unica architettura a cui
l'informazione temporale vada consegnata già calcolata.

Ma il vantaggio di 0,040 veniva da **cinque** soggetti. A dieci non è
distinguibile dal caso, e con la regola di etichettatura che include gli estremi
il segno **si rovescia** a −0,022. Per distinguerlo servirebbero fra 34 e 70
soggetti; sulla GRU ne servirebbero 274.

A dieci soggetti la foresta non è più la prima della tabella ma **l'ultima delle
cinque** — e resta comunque indistinguibile dalla GRU. L'indicazione di non
dichiarare un vincitore vale ancora, nell'altro verso.

**Il 7 settembre le sei architetture sono state riaddestrate sul dataset
riestratto**, dodici run in tre ore e mezzo. Nessuno scarto rispetto a prima
arriva alla dispersione fra soggetti, l'ordine si rimescola, e l'escursione fra
le cinque non a grafo **si stringe da 0,066 a 0,045**: metà della dispersione.
L'affermazione che porta il capitolo — *non sono distinguibili* — ne esce più
forte, non più debole.

→ [scheda C1](C1_ingressi_della_foresta.md) · e vedi [D2](D_domande_al_relatore.md)

### C2 · Chiamarlo adattamento al dominio, non generalizzazione

**Fatto.** Nel Capitolo 5: «adattamento al dominio di installazione — *domain
adaptation* nella terminologia corrente — e non generalizzazione». La
correzione non è di parole: i dati sostengono la seconda affermazione e non la
prima.

→ [scheda C2](C2_adattamento_al_dominio.md)

### C3 · Mostrare i due errori, non un solo F2

**Fatto, ed è stata la richiesta più fertile delle nove.**

Da A3 ad A3i con i controesempi i falsi negativi passano da **45 a 14** e i
falsi positivi da **172 a 124**: in laboratorio la configurazione finale non
introduce alcuno scambio, migliora entrambi gli errori.

E scomponendo i falsi allarmi **per attività**: su 419, ben **389 — il 93% —
vengono da una sola attività, sdraiarsi**. Camminare, stare in piedi e saltare
non ne producono nemmeno uno su cinquemila finestre.

**L'ipotesi che il sistema si allarmi per il movimento rapido è stata verificata
e smentita:** il picco di velocità verticale di una camminata (0,087) *supera*
quello della finestra mediana di caduta (0,055).

Scomponendo i positivi per **tipo di caduta**, il richiamo va da 0,934 (di lato)
a **0,704 (all'indietro)**: ventitré punti, più del divario fra due qualunque
delle sei architetture.

→ [scheda C3](C3_i_due_errori.md)

### C4 · Chiamarla soglia oracolo

**Fatto.** Definita nel testo come «valore ottenuto usando le etichette del
dominio di destinazione, che chi installa non possiede». Serve a scomporre il
fallimento, non a dichiarare una prestazione.

→ [scheda C4](C4_soglia_oracolo.md)

### C5 · La coerenza fra 4,47 e 2,20 ms

**La spiegazione c'era e ora è scritta:** il classificatore decide una volta ogni
due fotogrammi, quindi il costo per fotogramma è metà di quello per finestra.

**Ma il 6 settembre è emerso che il numero di partenza è probabilmente
sbagliato.** La board misurata fa **39,04 ms per finestra**; il calcolatore ne
fa 4,85. I 4,47 attribuiti alla board distano l'8% dal valore del PC: sembra un
numero del calcolatore etichettato come numero della board. Va ritirato o
dichiarato per quello che è ([D6](D_domande_al_relatore.md)).

→ [scheda C5](C5_coerenza_dei_millisecondi.md)

### C6 · I parametri non dichiarati del recall di campo

**Recepito.** Il recall di campo dipende da tre scelte — l'unità (evento o
finestra), la tolleranza di accoppiamento, la persistenza — ed è riportato come
**intervallo con i parametri esposti**, mai come numero singolo.

E resta la precisazione che pesa più di tutte: **cinque cadute non stimano un
recall**, l'intervallo di confidenza va da 0,28 a 0,99.

→ [scheda C6](C6_parametri_del_recall.md)

### C7 · L'indice aggiornato e la struttura del capitolo sperimentale

**Fatto**, dopo un primo tentativo che descriveva una struttura mai applicata.
`docs/INDICE_E_STRUTTURA.txt` è stato riscritto il 31 agosto sulla struttura
effettiva a **cinque capitoli**, e riporta per ogni sezione **la tesi che
sostiene**, non il suo contenuto.

→ [scheda C7](C7_indice_e_struttura.md)

---

## D — Le domande che attendono una risposta sua

| | domanda |
|---|---|
| **D1** | La fusione fra contesto e stato dell'arte: la soluzione adottata — capitoli separati e ripetizioni tolte — risponde all'obiezione? |
| **D2** | L'interpretazione sugli ingressi della foresta va tenuta come lettura dichiarata, o tolta? |
| **D3** | La latenza: un limite inferiore scomposto al posto di una misura è accettabile? |
| **D4** | Quale dei due sistemi installabili presentare: 2,5 allarmi/ora con 3 cadute su 5, o 14,0 con 4 su 5? |
| **D5** | *(nuova)* L'altezza dal pavimento toglie il 35% dei falsi negativi: rifare l'export sulla board, o correggere il testo? |
| **D6** | *(nuova)* I 4,47 ms attribuiti alla board: ritirarli o dichiararli come misura sul calcolatore? |

→ [scheda D](D_domande_al_relatore.md)

---

## Che cosa resta aperto, in ordine

1. **I trentacinque numeri senza artefatto**, riemersi il 7 settembre. Alcuni
   sono valori di letteratura e un artefatto non possono averlo; altri sono
   statistiche derivate che dovrebbero averlo. La distinzione va fatta a mano.
2. **Il riaddestramento delle sei architetture** sul dataset riestratto, in
   corso: finché non finisce, le tabelle del Capitolo 4 confrontano modelli
   addestrati su archivi diversi.
3. **Il salvataggio delle clip** nel registratore della board, senza il quale
   ogni sessione futura produrrà allarmi non verificabili.
4. **Le sedici voci di bibliografia mai verificate** su trentadue. Delle dodici
   controllate finora, quattro affermazioni non hanno retto.
5. **Più cadute reali.** È il limite più serio del lavoro: con cinque,
   l'intervallo di confidenza sul recall va da 0,28 a 0,99. La sessione da cui
   vengono tutte e cinque ha il 25,9% di pose valide, peggio di sessioni che
   sono state scartate: **rifarla con l'inquadratura giusta è l'intervento a
   costo più basso di tutto l'elenco.**
6. **La prova da dodici ore**, ora che è ripetibile e verificabile.
