# Discorso per il controrelatore (circa 14 minuti)

Aggiornato il 6 ottobre 2026. Circa 2.000 parole, cioè 14–15 minuti a ritmo normale; per stare in 12 taglia la sezione 5.
Spiegazione di ogni scelta nel codice: [SPIEGAZIONE_CODICE.md](SPIEGAZIONE_CODICE.md).

Filo logico: parto dal bisogno, scelgo il dispositivo, pongo le domande e costruisco la pipeline in ordine, dal fotogramma
all'allarme. Ogni passo risponde a un problema lasciato aperto dal precedente.

## 1. Il problema e la scelta del dispositivo (circa 2 minuti)

Il mio lavoro riguarda il rilevamento automatico delle cadute, con attenzione alla popolazione anziana e all'ambiente domestico. La
popolazione invecchia, e cresce il bisogno di soluzioni che permettano alle persone fragili di restare autonome nella propria casa.
Secondo i dati PASSI d'Argento, circa un anziano su cinque riferisce almeno una caduta in un anno, e la frequenza sale dal 15% fra 65 e
74 anni al 31% oltre gli 85. Circa il 54% delle cadute avviene in casa. Il problema non è solo la caduta: è il tempo che la persona
resta a terra prima di essere aiutata, perché in casa non c'è un'assistenza umana continua.

Le tecnologie possibili vanno dai dispositivi indossabili ai sensori ambientali, comprese le telecamere. Io ho studiato un sistema con
una telecamera RGB collegata a una scheda Radxa ROCK 4D, che costa circa cento euro. La telecamera serve solo all'inizio della
pipeline: tutta l'elaborazione avviene sul dispositivo. Questo evita di mandare il video a un server e limita ciò che esce dal sistema
alle informazioni necessarie per segnalare un allarme. Lo presento come una riduzione della circolazione delle immagini, non come una
garanzia di privacy, perché il sistema acquisisce comunque immagini della persona.

Per essere utile deve fare tre cose: riconoscere le cadute, contenere i falsi allarmi, perché troppi lo rendono inutilizzabile, e
funzionare in continuo con risorse limitate.

## 2. Le tre domande (circa 1 minuto)

Ho organizzato il lavoro intorno a tre domande. La prima: quanto conta l'architettura del classificatore, se tengo fissi dati,
rappresentazione del movimento e protocollo? La seconda, quella che considero più importante: le prestazioni ottenute in condizioni
controllate si mantengono quando cambiano soggetto, punto di vista, dataset e ambiente? Molti lavori riportano solo il benchmark, e non
si sa se quei risultati reggano fuori dal laboratorio. La terza: la pipeline completa riesce a girare in locale e in continuo,
trasformando i punteggi del classificatore in allarmi? Il percorso della tesi segue queste domande, dal benchmark fino al
funzionamento in casa.

## 3. La pipeline e il preprocessing (circa 5 minuti)

La pipeline parte dai fotogrammi RGB. MediaPipe Pose, sviluppato da Google, restituisce 33 punti anatomici, i landmark, che descrivono
il corpo come uno scheletro. Da questi calcolo grandezze geometriche e temporali. Il classificatore quindi non analizza centinaia di
migliaia di pixel ma una descrizione compatta, e posso collegare ogni grandezza a qualcosa di osservabile: l'inclinazione del tronco,
la posizione della testa rispetto al bacino, la discesa del corpo. Questo aiuta anche a capire gli errori.

Ho confrontato tre rappresentazioni. La prima, A1, tratta i landmark in 2D come una nuvola di punti e la riassume con un'ellisse: dalla
matrice di covarianza ricavo le direzioni principali e la dispersione, quindi orientamento e allungamento della figura. La seconda, A2,
usa i landmark tridimensionali di MediaPipe, con origine nel bacino. La profondità è stimata da una sola immagine, e la posizione della
persona rispetto a stanza e pavimento non è disponibile. La terza, A3, usa i landmark 2D riferiti al corpo: centro nel bacino e scala
data dalla lunghezza del tronco. Riduce la dipendenza dalla posizione nell'immagine e dalla dimensione apparente, ma perde il
contesto: una persona sul divano e una caduta possono avere la stessa postura. Per questo ho aggiunto l'altezza del bacino rispetto a
un pavimento stimato dall'immagine stessa.

A queste grandezze ho aggiunto tre quantità integrali: escursione, percorso e discesa. L'escursione è la differenza fra massimo e
minimo dell'angolo del tronco, il percorso è la lunghezza accumulata dal punto che seguo, la discesa è quanto sta sotto il suo punto
più alto recente. Le calcolo su 31 campioni, circa 1,7 secondi. Servono perché appena la persona è a terra la velocità istantanea
torna piccola e non ricorda più l'evento, mentre queste tre grandezze sì.

Le grandezze candidate sono 33, e non tutte servono. Ho usato una selezione con il Dynamic Time Warping, che confronta gli andamenti nel
tempo anche se i movimenti hanno velocità diverse. Cerca grandezze coerenti dentro la stessa classe e diverse fra cadute e attività
quotidiane, le valuta su entrambe le telecamere tenendo il punteggio peggiore, ed elimina quelle troppo correlate fra loro. Ne restano
12. L'altezza dal pavimento esce da questa selezione, perché funziona molto bene sulla vista laterale ma meno sulla frontale. La
reintroduco come configurazione a 13 grandezze, perché il sistema installato usa la vista laterale.

Prima del classificatore i dati passano per un preprocessing, in cinque passi. Primo: i fotogrammi di UP-Fall sono immagini PNG, e il
nome di ogni file è l'orario dell'acquisizione. Li ordino per quell'orario e, per ciascuno, uso il tempo realmente trascorso dal
precedente, perché la cadenza dichiarata è 18 fotogrammi al secondo ma misurata va da 14,4 a 19,6, e non è regolare nemmeno dentro una
stessa ripresa. Una velocità è una differenza divisa per un tempo: se dividessi per un tempo sbagliato, ogni piccolo buco nella cattura
diventerebbe un falso picco di velocità. Secondo: reinizializzo lo stimatore di posa all'inizio di ogni registrazione. MediaPipe è un
tracciatore e tiene memoria del fotogramma precedente: se non lo riavvio, la prima posa di una registrazione parte dall'ultima di
quella prima, per esempio una persona a terra, e le feature dei primi fotogrammi risultano alterate. Terzo: la posa è valida nel 95,9%
dei fotogrammi; quando manca, azzero la memoria delle posizioni precedenti, così non calcolo mai uno spostamento fra una posa prima di
un buco e una dopo, che non è mai avvenuto, e nessuna finestra collega osservazioni separate da un buco. Quarto: alcune grandezze hanno
code lunghissime, con pochi valori enormi, fino a 900 volte la mediana, che dominerebbero la standardizzazione. Su quelle applico
`segno(x)·log(1+|x|)`, un logaritmo che comprime i valori grandi e conserva il segno. Quinto: standardizzo con media e deviazione
calcolate solo sui dati di addestramento di ogni fold, e le applico così come sono al test, in modo che il soggetto di test non
influenzi la scala.

Poi organizzo i dati in finestre. Una caduta è un evento che si evolve: in un singolo istante può avere la stessa postura di chi si
siede di colpo o raccoglie un oggetto, e ciò che le distingue è la dinamica. Per avvicinarmi ai vincoli della scheda tengo un campione
ogni due, da circa 18 a circa 9 al secondo, perché la pipeline completa non reggeva la frequenza originale. La lunghezza della finestra è
un compromesso: troppo corta, non vede l'intera dinamica; troppo lunga, include campioni estranei all'evento e richiede più tempo per
riempirsi, quindi ritarda la decisione. Ho confrontato quattro lunghezze, 22, 28, 36 e 44 campioni, cioè da 2,4 a 4,9 secondi. F2 sale
sempre con la lunghezza, da 0,825 a 0,915 con 44, e diminuiscono sia i falsi negativi sia i falsi positivi. Ho comunque mantenuto 22:
con 44 servono circa 4,9 secondi prima di poter decidere, contro 2,4. È una scelta di tempestività dichiarata come compromesso, e non
ho misurato la latenza con 44: il conto è il tempo di riempimento della finestra.

Le etichette le ho annotate a mano, fotogramma per fotogramma, in tre fasi: 0 attività quotidiana, 1 transizione di caduta, 2 stato a
terra dopo la caduta. La transizione è meno del 5% dei fotogrammi, quindi la classe positiva è rara, e le cadute sono simulate. Tengo
separate transizione e stato a terra perché chi si sdraia volontariamente è a terra senza essere caduto, e UP-Fall contiene proprio
quell'attività, circa il 18% dei fotogrammi. Se considerassi «a terra» come caduta, il modello imparerebbe «orizzontale è caduta». Ho
confrontato tre definizioni del compito: con il solo evento la precisione è 0,990 ma la recall solo 0,364; considerando anche lo stato a
terra la recall sale a 0,836 e F2 a 0,830, ma l'11,7% delle finestre in cui la persona si sdraia volontariamente viene segnalato.
Cambiare la definizione del compito pesa più che cambiare architettura. Per la valutazione comune conto come positive sia la
transizione sia lo stato a terra.

## 4. Protocollo e architetture (circa 2 minuti)

Uso UP-Fall: dieci soggetti, 220 registrazioni da due telecamere sincronizzate. Valuto con leave-one-subject-out, e non con una
divisione per video, perché lo stesso soggetto compare in molti video: se è sia in addestramento sia in test, il modello può
riconoscere la persona e non la caduta, e il risultato è gonfiato. A ogni iterazione un soggetto intero è in test, uno in
validazione, che serve solo a fermare l'addestramento, e otto in addestramento, per dieci fold; normalizzazione e scaler sono stimati
solo sugli otto. La metrica principale è F2, che pesa di più la recall, quindi le cadute mancate, ma tengo separati falsi positivi e
falsi negativi perché anche troppi falsi allarmi compromettono l'utilità.

Per rispondere alla prima domanda ho confrontato sei architetture, a parità di rappresentazione e protocollo: Random Forest, LSTM,
GRU, CNN 1D, Transformer e una rete a grafo. La GRU ha il valore medio più alto, 0,857, la Random Forest 0,825: la differenza è 0,032,
mentre la deviazione standard fra soggetti è 0,089: cambiare persona sposta l'F2 più che cambiare architettura. Confronto i modelli
fold per fold con la GRU come riferimento, cioè sugli stessi dieci soggetti, per togliere la difficoltà del singolo soggetto. LSTM e
rete a grafo superano da soli la soglia di significatività, circa 2,26 per dieci fold, ma facendo cinque confronti la probabilità di un
falso positivo statistico cresce: con la correzione di Bonferroni la soglia sale a circa 3,25 e nessuna differenza la supera. Questo
non dimostra che i modelli siano equivalenti, ma solo che con dieci soggetti non si distinguono; per vedere la differenza fra GRU e
Random Forest ne servirebbero circa cinquanta. Fanno inoltre errori diversi, la Random
Forest meno falsi positivi della GRU ma più falsi negativi. Non ho cercato sistematicamente gli iperparametri e ho addestrato ogni
modello una volta per fold. La conclusione è che l'architettura conta, ma meno della variabilità fra persone.

## 5. Le prestazioni fuori dalle condizioni di riferimento (circa 2 minuti)

La seconda domanda ha una risposta più netta. Un modello addestrato e valutato sulla vista laterale raggiunge F2 0,822. Applicato alla
vista frontale rialzata scende a 0,488, e i falsi positivi passano da 722 a 3.252. Con entrambe le viste in addestramento risale a
0,731. La stessa postura, vista da un'altra posizione, produce grandezze diverse; lo 0,822 è la prestazione nella stessa vista, non
una prestazione trasferita. Ho poi provato UR-Fall, un dataset esterno dove cambiano soggetti, ambiente e acquisizione: uso la
sola telecamera frontale RGB a 30 fotogrammi al secondo, 67 registrazioni e 11.400 fotogrammi, rielaborate con lo stesso stimatore e
lo stesso calcolo, con la soglia fissata su UP-Fall. Il sottoinsieme DTW raggiunge F2 0,630, che è 5,1 volte la prevalenza in
PR-AUC. Il trasferimento è incompleto: in una configurazione precedente ho scomposto la perdita, e circa metà era di taratura, cioè
la soglia 0,50 non era più adatta e spostarla la recuperava, mentre circa metà era perdita di potere discriminante, che nessuna soglia
recupera. La soglia migliore a posteriori è solo diagnostica, perché usa le etichette di test.

In due abitazioni sono emerse difficoltà che il dataset non mostra, soprattutto persone sdraiate su divano o letto. Ho studiato il
contributo di grandezze integrali, altezza dal pavimento e controesempi domestici, cioè attività normali che il sistema confondeva con
cadute, aggiunte all'addestramento come esempi negativi. Una finestra positiva è una finestra con punteggio sopra 0,50, non un
allarme: una caduta ne produce in media 44,8 perché le finestre si sovrappongono, e la regola d'allarme le raccoglie in eventi, 7.429
finestre in 166 eventi. In casa le finestre positive passano da circa 140 all'ora a 9,8 con le
integrali e a 2,7 con anche i controesempi. Sul benchmark F2 migliora solo di 0,055. Il costo è che le cadute riconosciute scendono da
quattro su cinque a tre su cinque. Sono pochi eventi simulati, e queste scelte le ho fatte guardando proprio quegli errori: è un
percorso di sviluppo, non una verifica indipendente.

## 6. La pipeline gira? Dispositivo e allarme (circa 2 minuti)

Sulla Radxa ho installato MediaPipe e una Random Forest, scelta per semplicità di esecuzione, addestramento rapido e assenza della
dipendenza da TensorFlow sul dispositivo, visto che nel confronto controllato il vantaggio delle reti era contenuto. La pipeline
raggiunge circa 7,3 fotogrammi al secondo: è la capacità di elaborazione misurata sulla scheda, un valore diverso dai 18 fotogrammi
del dataset e dai 9 di progetto dopo il sottocampionamento. Per fotogramma
servono circa 136 millisecondi, di cui l'85% per la stima della posa e il 14% per il classificatore. Il collo di bottiglia è la posa,
quindi cambiare classificatore cambierebbe poco. Ho provato anche YOLOv8 quantizzato sulla NPU, più veloce, ma con la persona sdraiata
conservava la posa nel 44% dei fotogrammi contro il 79% di MediaPipe. La prova continua di riferimento dura 4,59 ore, senza sospensioni
del sistema operativo e con recupero automatico di due brevi interruzioni della telecamera: documenta la fattibilità per alcune ore,
non per giorni.

Per trasformare il punteggio in allarme serve una regola: cinque finestre consecutive sopra 0,50, poi trenta secondi di silenzio. La
soglia 0,50 l'ho scelta confrontando sei regole sugli stessi fold, quindi non è indipendente dai risultati. La regola ha un costo, e
l'ho visto: il 9 settembre, con quattro cadute simulate, il classificatore ne ha riconosciute tre ed è stata emessa una segnalazione
per due, perché una caduta, sei secondi dopo la precedente, è stata soppressa dai trenta secondi. Una persona seduta sul divano ha
prodotto invece quattro finestre positive e nessun allarme, perché ne servivano cinque. Per questo classificatore e logica di allarme
vanno valutati separatamente, e il ritardo va misurato dall'inizio fisico della caduta: la pipeline introduce circa 3,9 secondi, di cui
il 71% è il riempimento della finestra.

Dichiaro i limiti: soglia, selezione DTW, parametro K, altezza e controesempi sono stati influenzati dai dati osservati; la selezione
DTW è fatta sull'intero dataset prima del LOSO; le prove domestiche sono su due abitazioni e cadute simulate, e non sono una
validazione clinica. Il contributo è aver seguito cosa cambia quando un sistema basato sulla posa passa dal benchmark controllato al
funzionamento in casa.
