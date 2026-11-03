# Lettera al relatore — A2, resilienza alle occlusioni

*Testo pronto da inviare. La scheda completa è in
[A2_occlusioni.md](A2_occlusioni.md).*

---

Buongiorno professore,

le scrivo sulla seconda richiesta — quanto il sistema regge quando parte del
corpo non è visibile.

**La risposta è che nessun gruppo di punti del corpo risulta critico.** La
perdita peggiore è **0,037 di F2**, contro una dispersione fra soggetti di
**0,071**: il danno di un'occlusione resta sotto quello che si ottiene già solo
cambiando la persona su cui si verifica.

Ho rifatto questa misura ieri con il motore geometrico corrente, e il numero
peggiore è raddoppiato rispetto alla versione precedente: il margine passa da un
fattore quattro a un fattore due. La conclusione regge, ma il margine si è
ristretto e la ragione è interessante — la spiego più sotto, dopo i numeri.

## Che cosa intendo per «critico»

Un gruppo è critico se, togliendolo, la prestazione peggiora **più di quanto
peggiori da sola** cambiando la persona in verifica. È il confronto che dà
significato al numero: 0,037 di F2 non vuol dire nulla in assoluto, vuol dire
qualcosa accanto a un metro, e il metro di questo lavoro è la dispersione fra
soggetti.

Una possibile spiegazione, che riporto come lettura e non come misura: il motore
geometrico non guarda i punti uno per uno, ma **relazioni** fra punti — l'angolo
del tronco, l'altezza della testa rispetto alle anche, l'allungamento
dell'ellisse. Congelarne uno degrada alcune di quelle relazioni, e le altre
continuano a descrivere lo stesso movimento.

## Perché l'occlusione è simulata

Un'occlusione vera — un divano davanti alle gambe — **non è annotata in nessuno
dei due archivi**: nessuno ha segnato quali fotogrammi abbiano una parte del
corpo nascosta, quindi su UP-Fall non è misurabile.

Avevo però già in mano un'occlusione reale: la confidenza del naso che passa da
0,938 in piedi a 0,240 a terra. Da quel dato non si può concludere che il
sistema sia robusto — avevo individuato **una** modalità di guasto dello
stimatore, non misurato la resistenza del sistema. La verifica complementare che
lei ha indicato, un test artificiale controllato, è esattamente ciò che
mancava.

## Come ho simulato un punto non disponibile

È il passaggio metodologico che conta, e vorrei esporlo per esteso.

**Non azzerando il punto.** Uno zero in coordinate immagine è l'angolo in alto a
sinistra: una posizione *plausibile e sbagliata*. Il punto occluso schizzerebbe
là, e le grandezze di velocità e percorso esploderebbero: misurerei il danno di
un teletrasporto, non di un'occlusione.

**Congelandolo.** Sotto occlusione MediaPipe non smette di emettere una
posizione: la propaga dal fotogramma precedente, con confidenza bassa, finché
non ritrova il punto. La simulazione fa la stessa cosa — il punto mascherato
resta all'ultima posizione nota mentre gli altri continuano ad aggiornarsi — ed
è quindi il comportamento reale dello stimatore.

**Va detto che è anche la simulazione più benevola possibile**: congelando, le
derivate vanno a zero invece che esplodere. **I valori che riporto sono un
limite superiore alla robustezza**, non una stima neutra.

Non c'è un video della simulazione: avviene sulle coordinate dei punti, non
sulle immagini. Le immagini non vengono modificate — si modifica ciò che lo
stimatore ha prodotto da esse.

## Quali gruppi, e perché quelli

Non un gruppo solo: **dieci condizioni**, scelte perché corrispondono a
occlusioni che avvengono davvero in una casa.

| gruppo | punti | che cosa rappresenta |
|---|---:|---|
| naso | 1 | il viso girato o coperto |
| caviglie | 2 | i piedi dietro un mobile basso |
| gambe (ginocchia + caviglie) | 4 | divano, tavolo, letto |
| spalle | 2 | busto coperto da una persona davanti |
| anche | 2 | il **riferimento** del sistema di coordinate: per costruzione il caso peggiore |
| metà sinistra | 6 | occlusione laterale — uno stipite, una parete |
| casuale 11/22/33/55% | 1/2/3/5 | degradazione progressiva, senza struttura |

Una precisazione sulle percentuali: MediaPipe produce 33 punti, ma il motore
geometrico ne usa **nove** — naso, spalle, anche, ginocchia, caviglie. Un
mascheramento casuale che pescasse fra tutti e 33 colpirebbe quasi sempre
gomiti, polsi e punti del viso che il sistema non guarda, e dichiarerebbe molto
più di quanto misura. Le quote sono quindi applicate ai nove punti usati: «55%»
significa **cinque punti su nove**.

## I numeri

Foresta casuale, camera 1, soglia 0,50 dichiarata a priori, validazione
leave-one-subject-out a dieci fold.

| punti mascherati | n | F2 | perdita |
|---|---:|---:|---:|
| **nessuna occlusione** | 0 | **0,853 ± 0,071** | — |
| anche | 2 | 0,868 | +0,015 |
| casuale 33% | 3 | 0,856 | +0,003 |
| gambe | 4 | 0,854 | +0,001 |
| naso | 1 | 0,851 | −0,002 |
| metà sinistra | 6 | 0,848 | −0,004 |
| caviglie | 2 | 0,841 | −0,012 |
| **casuale 55%** | 5 | 0,821 | **−0,032** |
| **spalle** | 2 | **0,816** | **−0,037** |

Nove condizioni su dieci stanno dentro ±0,015, contro una dispersione fra
soggetti di 0,071. Due si staccano: le spalle e il mascheramento casuale di
cinque punti su nove.

Alcune condizioni migliorano leggermente il valore. **Non ne concludo che
occludere aiuti**: siamo dentro il rumore, e il segno di una differenza di 0,003
non è interpretabile. Riportarle come guadagni sarebbe l'errore speculare a
quello di riportare −0,004 come un danno.

### Un risultato che non mi aspettavo, e che ho verificato

Le spalle sono **l'unico gruppo anatomico che costi più di un gruppo casuale
della stessa dimensione**: −0,037 contro +0,001 di due punti a caso. È
precisamente il criterio con cui distinguevo un gruppo critico da uno
qualunque, e nella misura precedente non accadeva.

Fra le due misure erano però cambiate **due cose insieme** — il motore
geometrico e il sottoinsieme di dodici grandezze scelto dal criterio DTW — quindi
il confronto non diceva quale delle due pesasse. Ho rifatto l'esperimento una
terza volta, con il **motore nuovo e le colonne precedenti**:

| | prima | motore nuovo, **colonne precedenti** | motore nuovo, colonne nuove |
|---|---:|---:|---:|
| naso | −0,008 | **−0,007** | −0,002 |
| **spalle** | **−0,020** | **−0,019** | **−0,037** |
| casuale 55% | −0,009 | **−0,007** | −0,032 |

**Con le colonne precedenti tornano i numeri precedenti**: la causa non è il
motore geometrico né i punti, è **la selezione delle grandezze**. E si spiega
con una colonna sola su dodici: entra l'angolo del tronco — il vettore fra
spalle e anche — al posto di una grandezza riferita al naso. Il costo delle
spalle raddoppia, quello del naso si dimezza.

Ne traggo una conclusione più precisa di quella che avevo scritto: **non è che
l'informazione sia distribuita in sé — lo è per un dato insieme di grandezze**,
e cambiare quell'insieme sposta il punto del corpo su cui il sistema è
vulnerabile. Per chi dovesse installare il sistema è un fatto utile: la
robustezza alle occlusioni si sceglie insieme alle grandezze, non si eredita dal
problema.

## Il protocollo, e perché ho scelto quello

Sulla validazione **leave-one-subject-out**: si mette da parte una persona
intera, si addestra sulle altre, si verifica su di lei, e si ripete finché
ognuna è stata quella esclusa. Dieci soggetti, dieci fold, con tre insiemi
disgiunti per persona — otto in addestramento, uno di validazione, uno di test.

L'alternativa naturale — dividere a caso le finestre, o dividere per video —
lascerebbe **la stessa persona** in addestramento e in verifica, e il modello
imparerebbe *quel corpo*: la statura, il modo di piegarsi, la lunghezza del
torso. Il numero che ne uscirebbe risponderebbe alla domanda sbagliata —
«riconosce le cadute di chi ha già visto?» — mentre quella vera è **«funziona su
una persona nuova?»**, che è la condizione in cui il sistema si trova una volta
installato.

E dà una cosa che una divisione casuale non dà: **la dispersione fra soggetti**.
Ripetendo dieci volte con dieci persone diverse escluse si misura quanto il
risultato dipenda da chi capita in verifica. Vale 0,071, ed è il metro con cui
giudico ogni differenza di questo lavoro, compresa quella delle occlusioni.

Il suo limite lo dichiaro: con dieci persone anche la dispersione è stimata su
dieci valori, quindi è essa stessa rumorosa. È la ragione per cui il capitolo
dichiara quanti soggetti servirebbero per distinguere ciascun confronto, invece
di dichiarare vincitori.

## Che cosa questa risposta non copre

- **Le occlusioni da mobilio reale non sono misurate.** Un divano non congela i
  punti: li fa sparire, e a volte ne fa comparire di sbagliati.
- **La simulazione è la più benevola possibile**, quindi i valori sono un limite
  superiore.
- **Il caso peggiore non è qui.** Non è l'occlusione di un gruppo, è lo
  stimatore che **cambia persona**: lì non manca un'informazione, ce n'è una
  falsa al suo posto, e il danno è di tutt'altro ordine. È la seconda causa del
  divario fra le due viste di cui le ho scritto nella risposta precedente.

Resto a disposizione, e la ringrazio.
