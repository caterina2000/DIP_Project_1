# A2 — Resilienza alle occlusioni

**Che cosa è stato chiesto:** verificare quanto il sistema regge quando parte
del corpo non è visibile.

**La risposta in una riga:** **nessun gruppo di punti del corpo è critico** — la
perdita massima è **0,037 di F2** contro una dispersione fra soggetti di
**0,071**: il danno di un'occlusione resta sotto quello che si ottiene già solo
cambiando la persona su cui si verifica.

> **Rimisurata il 7 settembre 2026** con il motore geometrico corrente e la
> selezione DTW rifatta sul dataset riestratto. Il numero peggiore è
> **raddoppiato** rispetto alla misura di agosto (era 0,020) e il margine è
> passato da un fattore quattro a un fattore due. La conclusione regge, il
> margine si è ristretto.

---

## Prima di tutto: che cosa vuol dire «critico»

Un gruppo di punti è **critico** se, togliendolo, la prestazione peggiora **più
di quanto peggiori già da sola** cambiando la persona su cui si verifica.

Il confronto è tutto lì. «Perdo 0,037 di F2» non significa niente da solo:
significa qualcosa solo accanto a un metro. Il metro di questo lavoro è la
**dispersione fra soggetti** — quanto il risultato cambia a seconda di *chi* è
la persona esclusa dall'addestramento — e vale **0,071**.

**Un gruppo critico sarebbe quello la cui assenza fa più danno di una persona
diversa in verifica.** Nessuno dei dieci provati lo è: la perdita peggiore, le
spalle, è **poco più di metà** del metro.

Il capitolo usa anche un secondo criterio, più fine, che confronta i gruppi
**anatomici** con gruppi **casuali della stessa dimensione**: se togliere due
punti scelti (le spalle) costasse più di togliere due punti a caso, quei due
punti porterebbero informazione propria. Nella misura di agosto non accadeva;
nella misura del 7 settembre **accade** — spalle $-0{,}037$ contro casuale a due
punti $+0{,}001$ — e il Passo 4-bis dice perché.

*(Un'osservazione che aiuta a capire perché non lo sono: il motore geometrico
non guarda i punti uno per uno, ma **relazioni** fra punti — l'angolo del
tronco, l'altezza della testa rispetto alle anche, l'allungamento
dell'ellisse. Congelare un punto ne degrada alcune, e le altre continuano a
descrivere lo stesso movimento.)*

---

## Come ci siamo arrivati, passo per passo

### Passo 1 — Perché l'occlusione va simulata, e non osservata

Un'occlusione vera — un divano davanti alle gambe — **non è annotata in nessuno
dei due archivi**: nessuno ha segnato quali fotogrammi hanno una parte del corpo
nascosta. Non è possibile misurarla su UP-Fall né su UR-Fall.

Il progetto aveva però già in mano un'occlusione *reale*: la confidenza del naso
che passa da 0,938 con la persona in piedi a 0,240 quando è a terra, perché il
viso si gira o è coperto dal braccio. Da quel dato **non si può concludere che
il sistema sia robusto**: si era individuata una singola modalità di guasto
dello stimatore, non misurata la resistenza del sistema.

La verifica complementare — e il relatore l'ha indicata nella forma giusta
([B3](B3_occlusioni_controllate.md)) — è **un test artificiale controllato**:
mascherare gruppi di punti e misurare la degradazione.

### Passo 2 — Come si simula un punto non disponibile, e perché non azzerandolo

Questo è il passaggio metodologico che conta.

**Non si azzera.** Uno zero, in coordinate immagine, è l'angolo in alto a
sinistra: una posizione **plausibile e sbagliata**. Il punto «occluso»
schizzerebbe verso quell'angolo, e le grandezze di velocità e percorso
esploderebbero. Misureremmo il danno di un teletrasporto, non di un'occlusione.

**Si congela.** Sotto occlusione MediaPipe non smette di emettere una
posizione: continua a produrla, con confidenza bassa, propagandola dal
fotogramma precedente finché non ritrova il punto. La simulazione fa
esattamente questo — **il punto mascherato viene tenuto all'ultima posizione
nota**, mentre i punti visibili continuano ad aggiornarsi.

Nel codice sono otto righe, e la struttura è quella: si tiene lo stato del
fotogramma precedente; i punti non mascherati lo aggiornano, quelli mascherati
lo leggono.

```python
for i in range(len(lm)):
    if i in idx and prec[i] is not None:
        out[i] = prec[i]          # mascherato: legge il passato
    else:
        prec[i] = lm[i].copy()    # visibile: aggiorna il passato
```

**È anche la simulazione più benevola possibile**, e va detto: congelando, le
derivate vanno a zero invece che esplodere. **I numeri che ne escono sono
quindi un limite superiore alla robustezza**, non una stima neutra.

### Passo 3 — Quali gruppi, e perché quelli

I gruppi **non sono uno solo**: sono **dieci condizioni**, e sono scelte perché
corrispondono a occlusioni che avvengono davvero in una casa.

| gruppo | punti | l'occlusione domestica che rappresenta |
|---|---:|---|
| naso | 1 | il viso girato o coperto — è l'occlusione già osservata |
| caviglie | 2 | i piedi dietro un mobile basso |
| gambe (ginocchia + caviglie) | 4 | divano, tavolo, letto |
| spalle | 2 | busto coperto da una persona davanti |
| **anche** | 2 | è il **riferimento** del sistema di coordinate A3: per costruzione è il caso peggiore |
| metà sinistra | 6 | occlusione laterale — uno stipite, una parete |
| casuale 11 / 22 / 33 / 55% | 1 / 2 / 3 / 5 | degradazione progressiva, senza struttura |

**Una precisazione che cambia il significato delle percentuali.** MediaPipe
produce **33** punti, ma il motore geometrico ne usa **nove**: naso, spalle,
anche, ginocchia, caviglie. Un mascheramento casuale che pescasse fra tutti e 33
colpirebbe quasi sempre gomiti, polsi e punti del viso che il sistema non
guarda, e dichiarerebbe molto più di quanto misura. **Le quote casuali sono
quindi applicate ai nove punti usati**: «55%» significa cinque punti su nove,
non su trentatré.

### Passo 4 — La misura

Foresta casuale sul sottoinsieme di dodici grandezze, camera 1, soglia 0,50
dichiarata a priori, **leave-one-subject-out a dieci fold** (Passo 6).

| punti mascherati | n | F2 | perdita | *(agosto)* |
|---|---:|---:|---:|---:|
| **nessuna occlusione** | 0 | **0,853 ± 0,071** | — | *0,857* |
| anche *(riferimento di A3)* | 2 | 0,868 | **+0,015** | *+0,012* |
| casuale 33% | 3 | 0,856 | +0,003 | *−0,001* |
| casuale 22% | 2 | 0,854 | +0,001 | *−0,006* |
| gambe (ginocchia + caviglie) | 4 | 0,854 | +0,001 | *−0,000* |
| naso | 1 | 0,851 | −0,002 | *−0,008* |
| casuale 11% | 1 | 0,851 | −0,002 | *−0,012* |
| metà sinistra | 6 | 0,848 | −0,004 | *+0,008* |
| caviglie | 2 | 0,841 | −0,012 | *−0,015* |
| **casuale 55%** | 5 | 0,821 | **−0,032** | *−0,009* |
| **spalle** | 2 | **0,816** | **−0,037** | *−0,020* |

**Nove condizioni su dieci stanno dentro ±0,015**, contro una dispersione fra
soggetti di 0,071. Due si staccano dal gruppo: le spalle e il mascheramento
casuale di cinque punti su nove.

Tre letture, tutte dichiarate come tali:

- **mascherare cinque punti su nove costa 0,032 di F2**, cioè meno della metà
  della dispersione fra soggetti. Non è che il sistema «resista» a perdere metà
  dei punti: è che l'informazione su cui decide è distribuita fra le grandezze;
- **le spalle sono l'unico gruppo anatomico che costi più di un gruppo casuale
  della stessa dimensione**, e nella misura di agosto non era così. Il Passo
  4-bis separa le due spiegazioni possibili;
- **alcune condizioni migliorano leggermente il risultato** (anche, e i due
  mascheramenti casuali piccoli). Non significa che occludere aiuti: significa
  che siamo **dentro il rumore**, e che il segno di una differenza di 0,003 non
  è interpretabile. Riportarle come guadagni sarebbe l'errore speculare a
  quello di riportare −0,004 come un danno.

### Passo 4-bis — Perché il numero peggiore è raddoppiato, misurato

Fra la misura di agosto e quella del 7 settembre sono cambiate **due cose
insieme**: il motore geometrico (32 → 33 grandezze) e la selezione DTW, rifatta
sul dataset riestratto. Il confronto fra le due esecuzioni non dice quale delle
due pesi.

Una terza esecuzione le separa: **motore nuovo, colonne di agosto**.

| | agosto | motore nuovo, **colonne di agosto** | motore nuovo, colonne nuove |
|---|---:|---:|---:|
| base | 0,857 | 0,856 | 0,853 |
| naso | −0,008 | **−0,007** | −0,002 |
| **spalle** | **−0,020** | **−0,019** | **−0,037** |
| casuale 55% | −0,009 | **−0,007** | −0,032 |

**Con le colonne di agosto tornano i numeri di agosto.** La causa non è il
motore geometrico e non sono i landmark: **è la selezione delle colonne**.

**E si spiega con una colonna sola.** Fra le due selezioni cambia un elemento su
dodici: entra `A2_angolo_tronco` — l'angolo del tronco, cioè il vettore fra il
punto medio delle **spalle** e quello delle anche — al posto di
`A2_testa_rel_y`, che dipendeva dal **naso**.

Tutto il quadro segue da lì: il costo delle spalle raddoppia, quello del naso si
dimezza, e il mascheramento casuale di cinque punti su nove — che spesso pesca
anche le spalle — passa da −0,007 a −0,032.

**Ne esce una conclusione più precisa di quella che il capitolo dichiarava.** Non
è che l'informazione sia distribuita *in sé*: **lo è per un dato insieme di
grandezze**, e cambiare quell'insieme sposta il punto del corpo su cui il
sistema è vulnerabile. Per chi installa il sistema è un fatto utile — **la
robustezza alle occlusioni si sceglie insieme alle grandezze**, non si eredita
dal problema.

### Passo 5 — La scoperta laterale, che ha corretto un'affermazione del lavoro

L'auto-occlusione del naso — 0,938 in piedi, 0,240 a terra — sembrava una
proprietà del problema: quando una persona cade, la faccia si nasconde.

**Non lo è: è una proprietà di YOLOv8**, lo stimatore su cui quella misura era
stata fatta. Su MediaPipe la stessa confidenza passa da **0,997 a 0,989**, cioè
non cambia. Nel testo il fenomeno resta attribuito allo stimatore su cui è stato
misurato, e non presentato come caratteristica delle cadute.

### Passo 6 — Il protocollo: che cos'è la LOSO, e perché è la scelta giusta

**Leave-one-subject-out** significa: si mette da parte **una persona intera**, si
addestra su quelle che restano, si verifica su di lei; poi si ripete escludendo
la successiva, finché ognuna è stata la persona esclusa una volta. Dieci
soggetti, dieci fold.

Con dieci soggetti il ciclo di questo lavoro usa **tre insiemi disgiunti per
persona**:

| insieme | chi | a che cosa serve |
|---|---|---|
| addestramento | 8 soggetti | imparare |
| validation | 1 soggetto, il successivo in ordine circolare | fermare l'addestramento, e — dove la soglia non è fissa — sceglierla |
| test | 1 soggetto | misurare, **una volta sola** |

**Perché è la scelta giusta qui.** L'alternativa naturale — dividere a caso le
finestre, o dividere per video — lascerebbe **la stessa persona** in
addestramento e in verifica. Il modello riconoscerebbe allora *quel corpo*: la
sua statura, il suo modo di piegarsi, la lunghezza del suo torso. Il numero che
ne esce risponde alla domanda sbagliata — «riconosce le cadute di chi ha già
visto?» — mentre la domanda vera è **«funziona su una persona nuova?»**, che è
la condizione in cui il sistema lavora una volta installato in casa di qualcuno.

**E dà qualcosa che una divisione casuale non dà: la dispersione fra soggetti.**
Ripetendo dieci volte con dieci persone diverse escluse, si misura *quanto il
risultato dipende da chi capita in verifica*. Vale **0,071**, ed è il metro con
cui tutto il lavoro giudica le differenze — questa risposta compresa. Senza
LOSO non ci sarebbe metro, e ogni differenza sembrerebbe reale.

**Il costo, che va detto:** con dieci persone la dispersione è a sua volta
stimata su dieci valori, quindi è essa stessa rumorosa. È il limite più serio
del lavoro, e la ragione per cui il capitolo dichiara quanti soggetti
servirebbero per distinguere ciascun confronto invece di dichiarare vincitori.

---

## Che cosa questa risposta non copre

- **Le occlusioni da mobilio reale non sono misurate.** Ciò che è misurato è
  l'occlusione *simulata*, e la differenza è sostanziale: un divano non congela
  i punti, li fa **sparire** e a volte ne fa comparire di sbagliati.
- **La simulazione è la più benevola possibile**, quindi i valori sono un limite
  superiore alla robustezza.
- **Il caso peggiore non è qui.** Non è l'occlusione di un gruppo, è lo
  stimatore che **cambia persona** ([ISS-134](../ISSUES.md)): lì non manca
  un'informazione, ce n'è una **falsa** al suo posto, e il danno è di
  tutt'altro ordine — è la seconda causa del divario fra le due viste
  ([A1](A1_cambio_di_vista_e_di_ambiente.md)).
- **I punti di partenza vengono dall'estrazione di agosto.** Le posizioni dei
  landmark su cui la simulazione lavora furono estratte il 20 agosto, quindi
  con lo stimatore condiviso fra riprese ([ISS-138](../ISSUES.md)). I numeri
  della tabella vengono da quella misura. *(Una riesecuzione con il motore
  geometrico corrente — 33 grandezze e la selezione DTW rifatta su v3 — è stata
  avviata il 7 settembre; i landmark di partenza resterebbero comunque quelli,
  perché rifarli significa riestrarre la posa da tutti i video.)*

---

## Dove guardare

| | |
|---|---|
| artefatto | `risultati/occlusioni/foresta_DTW.json` |
| la stessa misura con le colonne di agosto | `..._colonne_agosto.json` |
| la misura di agosto, conservata | `..._agosto_v2.json` |
| registro | [EXP-027](../EXPERIMENTS.md) |
| script | `pipeline/occlusioni.py` |
| landmark di partenza | `DIP_PROJECT/dataset/processed/features/landmarks_raw.npz`, 92 MB, fuori da git |
| nella tesi | Capitolo 4, sezione sulle occlusioni, `fig:occlusioni` |
