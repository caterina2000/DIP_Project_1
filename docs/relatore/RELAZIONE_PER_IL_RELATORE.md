# Rilevamento di cadute su dispositivo edge — che cosa è stato fatto, e che cosa regge

**Caterina Cerretani · 7 settembre 2026**

Questo documento raccoglie in un posto solo tutte le risposte alle sue
richieste. È scritto per essere letto dall'inizio alla fine: ogni numero che
compare viene da un file prodotto da un'esecuzione, mai trascritto a mano.

---

# Parte 0 — Tre nozioni, senza le quali i numeri non si leggono

Sono tre, e servono tutte e tre. Le spiego qui una volta sola.

## F2, e perché non l'accuratezza

Le cadute sono rare: in laboratorio sono il 14% delle finestre, in un soggiorno
vero praticamente zero. Un sistema che dicesse sempre «non è una caduta» avrebbe
l'86% di accuratezza e sarebbe inutile.

Si usano perciò due grandezze che guardano **solo** gli allarmi e le cadute:

- **richiamo** — delle cadute vere, quante ne prendo;
- **precisione** — dei miei allarmi, quanti erano cadute vere.

**F2** le combina pesando il richiamo **quattro volte** la precisione, perché
perdere una caduta è più grave che disturbare qualcuno. La scelta è stata
dichiarata *prima* di guardare i risultati.

## La dispersione fra soggetti: il metro di tutto

Il sistema viene verificato con la **validazione leave-one-subject-out**: si
mette da parte **una persona intera**, si addestra su quelle che restano, si
verifica su di lei, e si ripete finché ognuna è stata quella esclusa. Dieci
persone, dieci ripetizioni, con tre insiemi sempre disgiunti — otto in
addestramento, una per la taratura, una per la verifica.

L'alternativa — dividere a caso le finestre — lascerebbe la stessa persona da
entrambe le parti, e il modello imparerebbe *quel corpo*: la statura, il modo di
piegarsi. Risponderebbe alla domanda sbagliata.

Da qui esce la grandezza più importante del lavoro: **la dispersione fra
soggetti**, cioè quanto il risultato cambia a seconda di *chi* è escluso. Nel
confronto fra architetture vale **±0,085** di F2.

Si ricalcola per ogni esperimento, perché dipende dalla configurazione: in
quello sulle occlusioni, per esempio, vale 0,071. È sempre quel valore — non uno
fisso — il metro con cui va giudicata la differenza di *quell'* esperimento.

> **È il metro con cui va giudicata ogni differenza di questo documento. Una
> differenza più piccola di 0,085 non è distinguibile dall'aver pescato una
> persona invece di un'altra.**

## Evento contro finestra sopra soglia

Il sistema decide ogni 0,25 secondi. Una persona che resta a terra — o distesa
sul divano — produce una **raffica** di decisioni positive consecutive.
Contarle come altrettanti allarmi sbaglia di quasi due ordini di grandezza:
sulle registrazioni domestiche il rapporto vale **44,8**.

Un allarme è definito da due parametri dichiarati: **cinque finestre
consecutive** sopra soglia perché venga emesso, e **trenta secondi** di silenzio
dopo. **Ogni numero di campo di questo lavoro è un evento**, mai una finestra.

---

# Parte 1 — Le quattro richieste iniziali

## A1 · Il sistema regge al cambio di telecamera e di ambiente?

**No, e ora sappiamo di quanto e perché.**

UP-Fall riprende ogni caduta con due telecamere sincronizzate: **Camera 1** è
laterale, all'altezza del busto; **Camera 2** è frontale e più in alto,
inclinata verso il basso. Il confronto si fa quindi a parità di tutto il resto —
stessa persona, stessa caduta, stesso istante.

| addestrata su | verificata su | F2 | falsi allarmi | cadute perse |
|---|---|---:|---:|---:|
| Camera 1 | Camera 1 | 0,822 | 722 | 186 |
| Camera 1 | **Camera 2** | **0,488** | **3.252** | 451 |
| Camera 1 + 2 | Camera 2 | 0,731 | 751 | 335 |
| Camera 2 | Camera 2 | 0,753 | 1.067 | 246 |

**Cambiare inquadratura costa 0,334 di F2**, cioè tre volte la dispersione:
è un effetto vero. Addestrare su entrambe le viste ne recupera il 73%.

Il dato che si vede solo separando i due errori, come lei aveva chiesto: passare
alla vista rialzata **non peggiora un po' tutto, fa esplodere un errore solo** —
i falsi allarmi si moltiplicano per quattro e mezzo.

### Perché la vista rialzata è peggiore

L'indicatore più forte di una caduta è la rotazione del tronco dalla verticale
all'orizzontale. Una telecamera che guarda dall'alto vede quella rotazione
avvenire *verso di sé*, quindi compressa. Misurando l'escursione dell'angolo del
tronco su cinquanta cadute, **senza addestrare nulla**: **74,0° dalla vista
laterale contro 33,2° da quella rialzata**, rapporto **2,23×**.

### Due difetti trovati guardando le immagini invece dei numeri

Il rapporto era dichiarato 1,99×, e prima ancora 4,32×. La correzione più
istruttiva è l'ultima, e riguarda un componente che il progetto non aveva mai
descritto per quello che è: **MediaPipe Pose è un tracciatore** — mantiene
memoria fra un fotogramma e il successivo.

1. Il codice di misura riusava **un solo** stimatore per tutte le riprese in
   fila: l'ultima immagine di una — persona a terra — condizionava la prima
   della successiva. Su una sequenza lo scarto arriva a **68°**.
2. Componendo una figura ho visto uno scheletro corretto disegnato **addosso
   alla persona sbagliata**, con accanto un angolo che sembrava sensato. Su
   Camera 2 lo stimatore **perde chi cade e si aggancia a chi è rimasto in
   piedi, in 11 riprese su 50**; su Camera 1 in 0 su 50. Il difetto arriva anche
   nei dati di addestramento: nel 12% delle cadute di Camera 2 il classificatore
   riceve, per la fase a terra, le grandezze di un'altra persona.

**Le due cause sono state separate.** Rifacendo tutto senza le undici riprese
contaminate il divario **non si chiude** (0,334 → 0,356): il cambio di persona
falsava la *misura geometrica*, ma il divario di classificazione è
sostanzialmente tutto compressione ottica.

### Un dato che ha cambiato un criterio di lavoro

Su Camera 2 una posa viene trovata nel **97,0%** dei campioni, su Camera 1
nell'**85,7%**. **La vista che porta meno informazione è quella in cui lo
stimatore fallisce meno spesso**, perché quando perde il soggetto trova comunque
qualcun altro. La quota di pose rilevate non è una misura di qualità — e la
usavo per decidere se accettare una sessione registrata in casa.

### Un risultato del capitolo che ho dovuto ritirare

Il testo affermava che addestrare sulla vista buona e trasferire batte di
**2,5×** l'addestrare direttamente sulla vista povera. **A dieci soggetti il
confronto si rovescia**: 0,753 contro 0,488. L'ho ritirato. Al suo posto resta
un'osservazione più debole e più utile: addestrare su entrambe le viste (0,731)
e addestrare solo su quella di esercizio (0,753) **non sono distinguibili**,
quindi chi installa sceglie in base a ciò che ha.

### Il cambio di ambiente

Il modello addestrato su UP-Fall, applicato a UR-Fall — altra stanza, altre
persone, altra telecamera — senza toccare nulla:

| | F2 |
|---|---:|
| in dominio, per riferimento | 0,971 |
| archivio nuovo, con la soglia con cui è schierato | **0,034** |
| archivio nuovo, con la soglia ritarata sulle sue etichette | 0,492 |

Il contributo originale non è «il sistema non trasferisce», ma la
**scomposizione** di quel crollo, perché da essa dipendono due conclusioni
opposte: o il modello **ordina** ancora bene e basta ritarare la soglia, oppure
**non separa più** e nessuna soglia serve.

Il divario totale, 0,937, si divide quasi a metà: **49% è taratura**
(recuperabile, in linea di principio, da chi installa) e **51% è perdita reale**
della capacità di separare, che nessuna soglia recupera. La conferma
indipendente è la PR-AUC, che non dipende dalla soglia: 1,79 volte il caso fuori
dominio contro 18,7 dentro.

## A2 · Il sistema regge quando parte del corpo non è visibile?

**Sì: nessun gruppo di punti del corpo risulta critico.**

Un'occlusione vera — un divano davanti alle gambe — non è annotata in nessuno
dei due archivi, quindi non è misurabile direttamente. L'ho **simulata in modo
controllato**, che è la forma che lei aveva indicato.

**Come si simula un punto non disponibile.** Non azzerandolo: uno zero in
coordinate immagine è l'angolo in alto a sinistra, una posizione plausibile e
falsa, e il punto ci schizzerebbe dentro facendo esplodere velocità e percorso.
**Si congela** all'ultima posizione nota, che è ciò che MediaPipe fa davvero
sotto occlusione. Va detto che è anche la simulazione **più benevola
possibile**: i valori sono un limite superiore alla robustezza.

Dieci condizioni, scelte perché corrispondono a occlusioni domestiche vere: il
viso coperto, i piedi dietro un mobile, le gambe dietro il divano, il busto
coperto da una persona davanti, metà scena tagliata da uno stipite, più quattro
mascheramenti casuali.

**Il risultato è che non c'è un risultato**, ed è quello interessante: la
perdita peggiore è **0,037 di F2**, contro una dispersione fra soggetti di
**0,071**. Mascherare **cinque punti su nove** ne costa 0,032.

*Una precisazione: MediaPipe produce 33 punti, ma il motore geometrico ne usa
nove. Le percentuali sono calcolate su quei nove, altrimenti si dichiarerebbe
molto più di quanto si misura.*

**Un risultato che non mi aspettavo.** Le spalle sono l'unico gruppo che costi
più di un gruppo casuale della stessa dimensione. Ho verificato da dove viene, e
non è anatomia: rifacendo la misura con il sottoinsieme di grandezze precedente
le spalle tornano a −0,019. **La sensibilità dipende da quali dodici grandezze
il criterio di selezione ha scelto**, non dai punti. Ne segue una conclusione
più precisa di quella che avevo scritto: non è che l'informazione sia
distribuita *in sé* — **lo è per un dato insieme di grandezze**, e la robustezza
alle occlusioni si sceglie insieme a esse.

## A3 · Il porting su dispositivo edge, senza video verso l'esterno

**Fatto, e il 6 settembre finalmente misurato invece che trascritto.**

La catena completa gira su una Radxa ROCK 4D da circa cento euro con una
telecamera USB.

| | dichiarato in tesi | **misurato su 4,6 ore** |
|---|---:|---:|
| percezione | 33,34 ms (88,4%) | **116,38 ms (85,2%)** |
| classificatore | 2,20 ms (5,8%) | **19,51 ms (14,3%)** |
| **totale** | **37,7 ms — 26,5 fps** | **136,65 ms — 7,3 fps** |

**Il dispositivo è 3,6 volte più lento di quanto il capitolo dichiarasse.**

Il numero della tesi era stato trascritto da una sessione di terminale e non
compariva in nessun file: era l'unico numero portante del lavoro che non fosse
rifacibile. La correzione non è stata rifare il banco di prova, ma
**strumentare la catena vera**, così che il bilancio esca dalla stessa
esecuzione che produce gli allarmi.

**Che cosa regge:** le proporzioni, e con esse l'affermazione portante — *il
collo di bottiglia è la percezione, non la classificazione*. **Che cosa non
regge:** i valori assoluti. E l'indizio era nel progetto da sempre: il file di
configurazione dichiara che la board regge circa **nove** fotogrammi al secondo,
ed è su quel presupposto che il dataset viene sottocampionato. I 7,3 misurati
sono coerenti; i 26,5 non lo erano mai stati, e nessuno aveva confrontato i due.

L'obiezione che la misura fosse a stanza vuota è stata verificata e
**falsificata**: con una persona in scena il costo *sale* da 126,0 a 144,1 ms.

**L'acceleratore neurale non viene usato:** costa 0,216 di F2, mentre dimezzare
la frequenza dei fotogrammi ne costa 0,041. È un risultato negativo su un lavoro
consistente, e resta nel testo.

**Sulla riservatezza:** il registratore salva in continuo soltanto posa e
punteggi. Ma il 7 settembre è emerso che **non salva immagini affatto**, mentre
la sua documentazione afferma che le clip attorno agli allarmi si possono
attivare. Non si possono: il codice non le scrive. Il registratore usato in
agosto le salvava, ed è con quelle che gli allarmi delle sessioni domestiche
sono stati guardati uno per uno.

## A4 · La prova di durata in ambiente reale

**Fatta**, in due tempi: dodici blocchi domestici in agosto — due abitazioni,
10,4 ore utilizzabili — e il **6 settembre 4,59 ore continue sulla board**.

| | |
|---|---:|
| durata | 4,59 ore |
| **sospensione della macchina** | **~0** (i due orologi distano 3,4 µs) |
| frequenza · pose valide | 7,26 fps · 35,1% |
| interruzioni della telecamera | 2, per 5,1 s, riprese da sole |
| **eventi di allarme** | **14**, cioè 3,05/ora · tempo sopra soglia 0,3% |

**Perché il controllo della sospensione conta.** Il primo tentativo era
*sembrato* riuscire: si era chiuso senza errori e con il registro completo. Ma i
fotogrammi non tornavano con la durata e la temperatura era scesa di tredici
gradi: **il dispositivo si era sospeso da solo**, e il registratore, che misura
il tempo con un orologio che durante la sospensione non avanza, al risveglio
riprendeva e alla fine dichiarava la durata richiesta. È il modo peggiore in cui
una misura può essere sbagliata — non fallisce, sembra riuscire. Da allora ci
sono **due orologi**, e la loro differenza è scritta in ogni riepilogo.

**Due cose vanno dette.** Non sono le dodici ore. E i **quattordici allarmi non
sono verificabili**: non esistono immagini di quei momenti, quindi il numero
riportabile è il *tasso di eventi*, non «quattordici falsi allarmi».

---

# Parte 2 — Le cinque verifiche che lei ha indicato

## B1 · La PR-AUC nel passaggio all'archivio esterno

**È perdita vera**, cioè la meno comoda delle due possibilità.

| | PR-AUC | rispetto alla prevalenza |
|---|---:|---:|
| archivio di addestramento | 0,990 | **18,7×** il caso |
| archivio mai visto | **0,169** | **1,79×** il caso |

Nel dominio nuovo il modello è **meno di due volte meglio del caso**: non è
soltanto uno spostamento della scala dei punteggi. La PR-AUC va sempre letta
contro la prevalenza, perché 0,169 significa cose diverse se i positivi sono il
10% o l'1% dei campioni.

## B2 · I controesempi di una casa, verificati sull'altra

**Fatta in entrambi i versi**, ed è l'unico disegno che distingua le due ipotesi
che lei aveva prospettato.

| controesempi da | verifica su | eventi/ora |
|---|---|---|
| casa dei nonni | casa dello studente | 0,342 → **0,171** |
| casa dello studente | casa dei nonni | 1,781 → **0,890** |

Circa un fattore due in entrambe le direzioni: ciò che il modello impara dai
controesempi **non è la stanza**. Nel testo l'effetto è chiamato **adattamento
al dominio** e non generalizzazione, come lei ha indicato — e la differenza non
è di parole: i dati sostengono la seconda affermazione, non la prima.

**Il costo va dichiarato insieme al beneficio:** in quella configurazione il
richiamo scende a due cadute su cinque.

## B3 · La verifica controllata sulle occlusioni

**Fatta nella forma suggerita**, ed è la stessa misura di A2. La forma indicata
— congelare i punti all'ultima posizione nota — è esattamente ciò che fa uno
stimatore di posa quando smette di vedere una parte, ed è per questo che è una
simulazione difendibile e non una comodità.

## B4 · Le metriche di campo a livello di evento

**Tutte e quattro sono calcolate**, ma non tutte sullo stesso dato.

**Falsi allarmi per ora e tempo fra allarmi**, nove sessioni, 14,98 ore:
**11,1 eventi/ora** in aggregato, da 0 a 100 secondo la sessione. La sessione
migliore, quella notturna sulla board, sta a 3,1. Il riferimento di letteratura
per un'installazione funzionante è **0,049 eventi/ora**: siamo due ordini di
grandezza sopra, ed è il dato più severo del lavoro.

**Quota di cadute rilevate:** non è un numero, è un **intervallo con i parametri
esposti**, e lo stesso sistema sugli stessi dati va **da 0/4 a 4/5** secondo la
tolleranza di accoppiamento e la persistenza richiesta. Il «quattro su cinque»
che circolava sta nell'angolo più permissivo; con parametri clinicamente
difendibili è **una caduta su cinque**.

**La latenza**, ed è la novità del 7 settembre. In casa **non è misurabile**, e
non è una rinuncia: le cadute sono annotate **al minuto** mentre la grandezza
vale pochi secondi. È come misurare una penna con un metro che ha solo le tacche
dei metri.

**Ma in laboratorio si misura**, perché lì l'etichetta è per fotogramma. Su
cinquanta cadute invece che su cinque, la latenza mediana è **2,44 secondi**.

Nel farlo è emerso un errore nel Capitolo 5: c'era scritto che il sistema non
può metterci meno di **3,778 s**. Non è vero. Quel conto assume che la finestra
debba riempirsi **dopo** l'inizio della caduta, e non è richiesto: il
classificatore decide su finestre che stanno **a cavallo** dell'istante di
inizio. Il minimo misurato è **+0,17 s**, cioè una finestra con tre fotogrammi
di caduta e quarantuno di ciò che la precede. Il capitolo chiama ora quel valore
*caso conservativo*.

Quello che regge, e resta il risultato utile: **la latenza è dominata dalla
finestra di decisione, non dall'hardware** — 2,74 s contro 38 ms. Un dispositivo
dieci volte più veloce la migliorerebbe dell'uno per cento.

## B5 · La prova lunga con controllo della sospensione

**Fatta**, ed è descritta in A4: 4,59 ore con sospensione misurata **pari a
zero**. Restano le dodici ore, e restano le clip da salvare — senza, anche una
prova da dodici ore produrrebbe un conteggio non verificabile.

---

# Parte 3 — I sette punti della sua email del 20 agosto

## C1 · Gli ingressi della foresta e le grandezze integrali

**La sua lettura del meccanismo è corretta; i numeri su cui poggiava non lo
erano.**

Sul meccanismo l'ipotesi è esatta: la finestra viene riassunta con sei
statistiche per grandezza e non contiene alcuna nozione di ordine, quindi la
foresta è **l'unica architettura a cui l'informazione temporale vada consegnata
già calcolata**.

Ma il numero che lo sosteneva veniva da **cinque** soggetti. A dieci il
vantaggio **non è distinguibile dal caso**, e con una variante della regola di
etichettatura cambia perfino segno. Per distinguerlo servirebbero fra 34 e 70
soggetti; sulla GRU ne servirebbero 274.

**Il 7 settembre le sei architetture sono state riaddestrate** sul dataset
riestratto — dodici esecuzioni in tre ore e mezzo. Nessuno scarto rispetto a
prima arriva alla dispersione fra soggetti, l'ordine si rimescola, e
**l'escursione fra le cinque architetture non a grafo si stringe da 0,066 a
0,045**, cioè a metà della dispersione. È la prova più forte che il lavoro abbia
dell'affermazione che porta: **le architetture non sono distinguibili fra loro**,
e chi ne dichiarasse una vincitrice starebbe leggendo il rumore.

**Che cosa propongo di scrivere:** l'interpretazione meccanicistica resta come
**lettura dichiarata** del fenomeno, accanto alla tabella di quanti soggetti
servirebbero, e non come contributo misurato. Su questo le chiedo un parere.

## C2 · Adattamento al dominio, non generalizzazione

**Fatto.** Nel Capitolo 5: «adattamento al dominio di installazione — *domain
adaptation* nella terminologia corrente — e non generalizzazione». La conseguenza
operativa è dichiarata accanto: un sistema installato ha bisogno di raccogliere
controesempi **in quella casa**, e questo è un costo di installazione, non una
proprietà gratuita del modello.

## C3 · Mostrare i due errori, non un solo F2

**Fatto, ed è stata la richiesta più fertile delle nove.**

Da A3 ad A3i con i controesempi i falsi negativi passano da **45 a 14** e i
falsi positivi da **172 a 124**: in laboratorio la configurazione finale non
introduce alcuno scambio, migliora entrambi gli errori.

**E scomponendo i falsi allarmi per attività**, cosa che nessuno aveva mai
fatto: su 419, ben **389 — il 93% — vengono da una sola attività, sdraiarsi**.
Camminare, stare in piedi e saltare non ne producono nemmeno uno su cinquemila
finestre.

**L'ipotesi che il sistema si allarmi per il movimento rapido è stata verificata
e smentita:** il picco di velocità verticale di una camminata (0,087) *supera*
quello della finestra mediana di caduta (0,055), perché in due secondi e mezzo
di passi il corpo oscilla molte volte. Se il sistema decidesse sulla velocità,
camminare sarebbe il falso allarme principale: non ne produce nessuno.

**E scomponendo i positivi per tipo di caduta**, il richiamo va da 0,934 (di
lato) a **0,704 (all'indietro)**: ventitré punti, più del divario fra due
qualunque delle sei architetture.

**Il seguito, ed è il risultato più importante di questi due giorni.** La
domanda nata da qui — *perché proprio sdraiarsi?* — mi ha portato a
un'osservazione: l'altezza del bacino dal pavimento distingue il divano dal
pavimento **a prescindere dalla velocità**. È corretta, e la risposta è che
**quella grandezza il sistema installato non ce l'ha**, e non poteva averla:
non era fra quelle calcolate.

Reintrodotta e misurata: **i falsi negativi calano del 35%** (249 → 163) e l'F2
sale da 0,807 a 0,866. E riaddestrando tutte e sei le architetture, **migliora
tutte e sei**, con un guadagno medio di +0,056. Nessun guadagno singolo è
distinguibile, ma sei segni concordi su sei hanno probabilità 0,016 se la
colonna non servisse.

## C4 · Chiamarla soglia oracolo

**Fatto.** È definita nel testo come «valore ottenuto usando le etichette del
dominio di destinazione, che chi installa non possiede», ed è presentata come
**limite superiore** di ciò che una ritaratura potrebbe dare, non come
prestazione ottenibile.

## C5 · La coerenza fra 4,47 e 2,20 ms

**La spiegazione c'era e ora è scritta:** il classificatore decide una volta ogni
due fotogrammi, quindi il costo per fotogramma è metà di quello per finestra.
Non sono due misure in disaccordo, sono la stessa misura in due unità.

**Ma il numero di partenza è probabilmente sbagliato.** La board misurata fa
**39,04 ms** per finestra; il calcolatore ne fa 4,85. I 4,47 attribuiti alla
board distano l'8% dal valore del PC: sembra un numero del calcolatore
etichettato come numero della board. Va ritirato o dichiarato per quello che è.

## C6 · I parametri non dichiarati del richiamo di campo

**Recepito.** Il richiamo di campo dipende da tre scelte — l'unità (evento o
finestra), la tolleranza di accoppiamento, la persistenza — ed è ora riportato
come **intervallo con i parametri esposti**, mai come numero singolo.

Con la precisazione che pesa più di tutte: **cinque cadute non stimano un
richiamo**, l'intervallo di confidenza va da 0,28 a 0,99.

## C7 · L'indice aggiornato e la struttura del capitolo sperimentale

**Fatto**, dopo un primo tentativo che descriveva una struttura mai applicata.
L'indice è stato riscritto il 31 agosto sulla struttura effettiva a **cinque
capitoli**, e riporta per ogni sezione **la tesi che sostiene**, non il suo
contenuto.

---

# Parte 4 — Che cosa è emerso il 6 e il 7 settembre

Due giornate di verifiche hanno prodotto nove risultati nuovi, **sei dei quali
sono difetti trovati nel lavoro stesso**. Li riassumo perché tre hanno la stessa
causa.

**Il filo comune: MediaPipe Pose è un tracciatore.** Mantiene memoria fra un
fotogramma e il successivo — è ciò che lo rende buono — ed è una proprietà che
il progetto non aveva mai messo per iscritto. In due giorni ha prodotto **tre
difetti distinti**: fra riprese di una misura, fra persone dentro una ripresa, e
fra riprese del dataset di addestramento.

**1. Il dataset è stato rifatto da capo.** Le feature dipendevano dall'ordine in
cui i video erano stati elaborati: riestraendo una ripresa già presente, come
controllo, **nessuna delle 866 righe coincideva**. Le conclusioni non erano in
discussione — poggiano su divari molto più grandi — ma la **riproducibilità**
sì. Il dataset nuovo ha 220 riprese invece di 218 e 116.362 fotogrammi, e le
etichette non cambiano di un fotogramma.

**2. L'altezza dal pavimento, che il sistema non aveva** — descritta in C3.

**3. La prova di durata sulla board**, con il costo per fotogramma finalmente
misurato — descritta in A3 e A4.

**4. Una sessione spariva dai numeri di campo.** Lo script cercava i punteggi in
file con il nome scritto dal registratore di agosto; quello della board usa un
nome diverso. **La sessione di 4,6 ore non entrava in nessun numero, e lo script
non se ne lamentava.** Il fattore fra finestre ed eventi passa da 47,8 a
**44,8**.

**5. Trentacinque numeri della tesi erano sepolti sotto una registrazione.**
C'è uno strumento che verifica se ogni numero del testo ha un file che lo
produce. Copiando la sessione del 6 settembre nella cartella dei risultati sono
entrati due file per campione, e la riserva è passata a **1,8 milioni di valori
distinti**: con quella massa di decimali arbitrari **ogni** numero trova un
riscontro per caso, e lo strumento dichiarava zero numeri ingiustificati in
tutti i capitoli. Escludendo quei due file ne riemergono trentacinque. **Il
difetto è arrivato da solo**: nessuno aveva toccato lo strumento.

**6. Il registratore della board non salva immagini, e dice il contrario** —
descritto in A3.

**7. Un risultato del Capitolo 4 è stato ritirato** — il «controintuitivo» di
A1.

**8. La soglia dei 60 gradi non era giustificata** da nessuna parte: era un
numero scritto nel codice senza commento. La conclusione non dipende da esso —
da 30° a 80° la vista laterale supera la soglia fra 2,5 e 13 volte più spesso,
senza mai cambiare verso — e ora la didascalia lo dichiara come convenzione di
lettura.

**9. La regola di allarme è la peggiore delle quattro provate**, ed è il
risultato pratico più utile della giornata. Il Capitolo 5 osservava che tre
cadute vere non producono allarme «con corse massime di due, zero e tre
finestre», senza trarne la conseguenza: la regola chiede cinque finestre
**consecutive**, e quindi **azzera l'evidenza già accumulata ogni volta che un
fotogramma va storto** — cosa che succede proprio nelle cadute difficili.

Ho confrontato ventuno regole, **senza riaddestrare nulla**: cambia solo
l'aritmetica che trasforma i punteggi in un allarme.

| regola | cadute prese | latenza | falsi allarmi in casa |
|---|---:|---:|---:|
| **cinque consecutive** *(installata)* | 44 su 50 | 2,47 s | 10,8/ora |
| cumulata | **49 su 50** | **1,61 s** | 9,3/ora |
| **isteresi** | 48 su 50 | 2,00 s | **5,1/ora** |

**Undici regole su venti battono quella installata su entrambi gli assi**, e il
risultato è strutturale — tutte le varianti della cumulata e quasi tutte
dell'isteresi — quindi non è un parametro fortunato: **è la famiglia consecutiva
a essere quella sbagliata**.

---

# Parte 5 — Che cosa resta aperto

1. **Più cadute reali.** È il limite più serio del lavoro: con cinque,
   l'intervallo di confidenza sul richiamo va da 0,28 a 0,99. La sessione da cui
   vengono tutte e cinque ha il 25,9% di pose valide: rifarla con l'inquadratura
   giusta è l'intervento a costo più basso. **E il nostro archivio di
   laboratorio contiene una sola prova per attività**: UP-Fall ne pubblica di
   più, e scaricarne altre moltiplicherebbe le cadute disponibili senza toccare
   una riga di codice.
2. **Trentacinque numeri senza un file che li produca**, ora scesi a
   ventisette. Alcuni sono valori di letteratura e un file nostro non possono
   averlo; altri sono statistiche derivate che dovrebbero averlo. La distinzione
   va fatta a mano.
3. **Le tabelle del Capitolo 4 riportano ancora i valori del dataset
   precedente**, e vanno riscritte su quelli nuovi.
4. **Il salvataggio delle clip** nel registratore della board, senza il quale
   ogni sessione futura produrrà allarmi non verificabili.
5. **Sedici voci di bibliografia mai verificate** su trentadue. Delle dodici
   controllate finora, quattro affermazioni non hanno retto.
6. **La prova da dodici ore**, ora che è ripetibile e verificabile.

---

# Parte 6 — Le sette domande che le rivolgo

Non sono risposte: sono i punti in cui la scelta non è tecnica.

| | domanda |
|---|---|
| **D1** | La fusione fra contesto e stato dell'arte: la soluzione adottata — capitoli separati e ripetizioni tolte — risponde all'obiezione? |
| **D2** | L'interpretazione sugli ingressi della foresta va tenuta come lettura dichiarata, o tolta? |
| **D3** | La latenza: misurata in laboratorio e dichiarata non misurabile in casa, con la ragione — è una forma accettabile? |
| **D4** | Quale dei due sistemi installabili presentare: pochi falsi allarmi e tre cadute su cinque, o molti e quattro su cinque? |
| **D5** | L'altezza dal pavimento toglie il 35% dei falsi negativi e migliora tutte e sei le architetture: rifare l'installazione sul dispositivo, o correggere il testo? |
| **D6** | I 4,47 ms attribuiti alla board: ritirarli o dichiararli come misura sul calcolatore? |
| **D7** | Cambiare la regola di allarme? Costa quattro righe di codice e nessun riaddestramento, e dimezza i falsi allarmi prendendo più cadute. |

Le due che pesano di più sono **D5** e **D7**, perché entrambe migliorano il
sistema installato senza toccare il modello — e perché finché non sono decise,
il testo descrive una configurazione diversa da quella che il dispositivo
esegue.

---

*Ogni numero di questo documento è ricalcolabile dai file indicati nelle schede
di dettaglio, una per richiesta, nella stessa cartella.*
