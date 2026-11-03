# Panoramica — che cosa è stato fatto, in ordine, e perché

Questo è il primo di otto documenti. Servono a rispondere, per ogni capitolo
della tesi, a quattro domande insieme:

1. **che cosa dice il testo** (la tesi);
2. **che cosa lo produce nel codice** (quale file, quale funzione, quale riga);
3. **quali esperimenti lo sostengono** (EXP-xxx) e con quali numeri;
4. **quali problemi sono stati trovati per strada** (ISS-xxx) e come sono stati
   risolti — o perché non lo sono.

| file | copre |
|---|---|
| `00_PANORAMICA.md` | questo: il punto di partenza, l'obiettivo, la mappa generale |
| `01_CAP1_contesto.md` | Capitolo 1 — contesto applicativo e formulazione del problema |
| `02_CAP2_stato_arte.md` | Capitolo 2 — stato dell'arte |
| `03_CAP3_metodologia.md` | Capitolo 3 — dal video alle feature (il capitolo tecnico) |
| `04_CAP4_protocollo_risultati.md` | Capitolo 4 — protocollo di valutazione e risultati di laboratorio |
| `05_CAP5_edge_e_campo.md` | Capitolo 5 — dispositivo edge e validazione in casa |
| `06_CONCLUSIONI.md` | Conclusioni — contributi, limiti, sviluppi |
| `07_MAPPA_CODICE.md` | tabella di corrispondenza codice ↔ capitolo ↔ esperimento ↔ difetto |

---

## 1. Da dove si parte davvero

Il lavoro **non** è nato da zero. C'era un prototipo, ed è importante saperlo
perché metà delle decisioni prese sono *correzioni* di quel prototipo, non
invenzioni.

Il prototipo confrontava due approcci:

- una **GRU** addestrata su feature cinematiche ricavate dallo scheletro che
  MediaPipe Pose estrae da ogni fotogramma;
- un **autoencoder seguito da random forest**, che imparava da solo una
  rappresentazione compatta dello scheletro grezzo.

Il primo dichiarava **recall 95% e F1 = 0,93 su UR-Fall**.

Il relatore, partendo dall'osservazione che i sistemi di fall detection
dichiarano numeri eccellenti sulla carta e falliscono nella pratica, ha chiesto
**quattro cose**:

1. quanto il sistema regge al **cambio di telecamera e di ambiente**;
2. quanto resiste alle **occlusioni**;
3. se l'intera catena può girare su un **dispositivo edge**;
4. di provarlo con una **sessione lunga in una casa vera**.

Tutto ciò che segue è la risposta a quelle quattro domande — più una quinta
cosa che non era stata chiesta e che è diventata il risultato principale.

### Il primo numero, quello che ha cambiato tutto

Rimisurando il prototipo con un protocollo corretto, l'**F1 passa da 0,93
dichiarato a 0,0000 misurato**. Non 0,3, non 0,5: zero esatto, cioè *nessun
vero positivo su nessun fold*. Un modello che non ha mai predetto la classe
positiva.

Le cause erano tre, tutte nel protocollo e nessuna nel modello.

### Che cosa vuol dire «protocollo corretto», per esteso

Sono tre correzioni, e vanno applicate **insieme**: presa una alla volta,
nessuna delle tre porta il modello fuori dalla degenerazione.

| | correzione | dove sta nel codice |
|---|---|---|
| 1 | **divisione per soggetto** (*leave-one-subject-out*): in ogni fold un soggetto in verifica, un secondo in validazione, gli altri otto in addestramento | `src/dati.py:274-307` |
| 2 | **normalizzazione stimata sul solo addestramento**, e **sui fotogrammi e non sulle finestre** --- con passo 2 su finestre da 22 ogni fotogramma compare in circa undici finestre, e stimare sulle finestre lo peserebbe undici volte | `src/dati.py:149-175`, `:301` |
| 3 | **validation separato dal test**: la soglia si sceglie sul validation e si applica al test **una volta sola** | `src/valutazione.py:88-104` |

Prima c'era il contrario di tutte e tre: split per *ripresa* --- che con dieci
soggetti mette tutte e dieci le persone da entrambe le parti della barriera ---
nessuna normalizzazione, con scale che differivano di un fattore **646**, e la
soglia scelta guardando lo stesso insieme su cui poi si misurava.

Applicando le tre insieme, agli stessi dati e con lo stesso modello:
**F1 = 0,234, con 144 veri positivi contro zero**.

**Il resto del protocollo è arrivato dopo**, e non nasce da un difetto ma da
misure successive. Vale la pena elencarlo, perché «a parità di protocollo» in
tutto il lavoro significa *questo*:

- **$F_2$ dichiarata prima** di osservare i dati di verifica (`config.py:94`),
  non scelta a posteriori fra i valori che davano il numero migliore;
- **soglia fissa a 0,50, dichiarata a priori** ([DEC-105](../DECISIONS.md#dec-105)):
  stimarla su un solo soggetto di validazione aggiunge più rumore
  dell'adattamento che porta --- deviazione **0,37 su [0, 1]**;
- **le finestre non attraversano i buchi di posa** né il confine fra due
  riprese: descriverebbero un movimento mai avvenuto;
- **due etichette per finestra** --- `y_train` cambia con la definizione del
  compito, `y_allarme` è fissa ed è il metro con cui i modelli si confrontano;
- **un `run_metadata.json` per esecuzione** con la soglia **e il criterio con
  cui è stata scelta**: una soglia registrata senza il criterio non è
  riproducibile.

Quel 0,234 è basso, e questo è il punto: era il primo numero *interpretabile*
del progetto. Tutto il resto del lavoro consiste nel farlo salire capendo
perché è basso.

---

## 2. Che cos'è il sistema, in una riga

```
telecamera USB → 640×480 → MediaPipe Pose (33 punti) → 32 grandezze geometriche
    → sottoinsieme di 12 scelto per separabilità → finestra di 22 campioni (2,44 s)
    → foresta casuale → punteggio → regola di allarme (5 finestre + 30 s)
```

Tutto su una board da ~100 €. **Nessuna immagine lascia il dispositivo.**

### Perché una finestra di 22 campioni

Il numero **è un'eredità**: 45 campioni a 18 fps nel prototipo, riportati alla
frequenza che il dispositivo regge davvero (9 fps) mantenendo la stessa
*durata*. Quel 45 non era giustificato da alcuna misura --- nel progetto
precedente valeva 45 in `config`, **75** in `demo_realtime.py` e **39** nei
metadati della run migliore.

È stato messo alla prova ([EXP-012](../EXPERIMENTS.md#exp-012)), perché
l'ipotesi ragionevole era che fosse **troppo corto**: la caduta mediana dura
3,11 s e la finestra ne copre 2,44.

| campioni | durata | $F_2$ |
|---:|---:|---:|
| **22** | **2,44 s** | **0,847 ± 0,085** |
| 28 | 3,11 s | 0,838 ± 0,077 |
| 36 | 4,00 s | 0,817 ± 0,146 |
| 44 | 4,89 s | 0,881 ± 0,090 |

**Nessuna differenza significativa, andamento non monotono, e per distinguere
22 da 44 servirebbero 52 soggetti.** L'ipotesi era sbagliata, e la spiegazione
è che *la memoria effettiva non coincide con la finestra*: ogni campione porta
gli integrali accumulati sui 31 fotogrammi precedenti, cioè 1,7 s di storia in
più --- il campo di ricezione reale è circa 5,8 s --- e due terzi dei positivi
sono lo stato «a terra», che si riconosce da una finestra corta quanto si
vuole.

C'è poi una seconda ragione, indipendente: **la finestra è il 72,6% della
latenza** (2,743 s su un limite inferiore di 3,778 s). Allungarla costa tempo
di rilevamento senza comprare accuratezza.

Quindi 22 non è più un valore ereditato: è un valore **verificato contro tre
alternative**, e sostenuto da un secondo argomento.

### Perché una foresta casuale, e non la GRU

**Non perché sia la più accurata: non lo è.**

| | $F_2$ | falsi neg. | falsi pos. | addestramento |
|---|---:|---:|---:|---:|
| GRU | 0,847 ± 0,085 | 105 | 885 | 22,7 min |
| Foresta, 50 alberi | 0,792 ± 0,080 | 271 | **421** | **0,2 min** |

Ma il confronto appaiato fold per fold dà **t = −1,74 contro un valore critico
di 2,26**: *non è distinguibile dalla GRU*. E quando l'accuratezza non decide,
decide tutto il resto:

- **dimezza i falsi allarmi** rispetto a ogni rete. Non è un modello peggiore,
  è un modello con **un altro punto di funzionamento** --- e in una casa un
  falso allarme non è una riga in una tabella, è un sistema che viene spento;
- **gira con scikit-learn su CPU.** Le reti richiederebbero TensorFlow su ARM,
  che è una dipendenza pesante, oppure la conversione per l'acceleratore
  neurale --- la stessa strada che sullo stimatore di posa costa 0,216 di $F_2$;
- **costa 4,47 ms per finestra**, cioè il **5,8%** del bilancio per fotogramma.
  È la più lenta delle cinque, ed è irrilevante;
- il pacchetto installato è **6.928 nodi, 1,4 MB**;
- si addestra in **0,2 minuti contro 22,7**, ed è ciò che ha reso possibile
  provare tutte le configurazioni in una giornata invece che in una settimana.

### Le due ipotesi di partenza, e come sono finite

| ipotesi ereditata dal prototipo | esito |
|---|---|
| l'intera catena può girare in tempo reale su hardware da cento euro | **verificata** — 26,5 fps, e il classificatore è il 5,8% del costo |
| una rete ricorrente compatta è la scelta giusta per il classificatore | **non verificata** — cinque architetture cadono entro 0,066 di F2 contro una dispersione fra soggetti di 0,08–0,12: nessuna coppia è distinguibile |

---

## 3. I dati: tre archivi, tre ruoli diversi

Questo è [DEC-106](../DECISIONS.md#dec-106), ed è una decisione, non una
comodità: **i tre non si mescolano mai**, perché ognuno risponde a una domanda
che gli altri non possono rispondere.

| archivio | che cos'è | a che cosa serve |
|---|---|---|
| **UP-Fall** | laboratorio, 10 soggetti usati, 218 riprese, 114.923 fotogrammi, 2 telecamere sincronizzate | addestrare, e misurare il **recall** |
| **sessioni domestiche** | 12 blocchi, 4 giornate, 2 abitazioni, 9,6 ore registrate sulla board | misurare i **falsi allarmi reali** e tarare |
| **UR-Fall** | altro laboratorio, 11.400 fotogrammi, 67 riprese | **test esterno**: il modello ha imparato la caduta o ha imparato UP-Fall? |

### «Perché dieci soggetti e non diciassette?»

È la domanda che arriva per prima, quindi la risposta va scritta per prima.

**UP-Fall contiene diciassette soggetti.** Il lavoro ne usa **dieci**, e la
limitazione è *nostra e non del dataset*: sono quelli scaricati ed estratti.
Cinque soggetti pesano 13,7 GB di PNG grezzi, quindi dieci ne pesano circa 27, e
l'estrazione delle feature con MediaPipe su 114.923 fotogrammi è costata **95
minuti** la prima volta ([EXP-003](../EXPERIMENTS.md#exp-003)) e **124 minuti**
la seconda, dopo la correzione di A2 ([EXP-007](../EXPERIMENTS.md#exp-007)).

Il numero **è cambiato durante il lavoro**: fino al 20 agosto i soggetti erano
**cinque**, poi sono diventati dieci, e questo raddoppio ha ribaltato o
ridimensionato quattro conclusioni già scritte. È il motivo per cui in tesi
alcune misure portano l'avvertenza «impianto a cinque soggetti».

Aggiungere i sette mancanti è stato valutato quantitativamente
([EXP-013](../EXPERIMENTS.md#exp-013)) e **non cambierebbe le conclusioni**:
porterebbe solo il confronto GRU-contro-foresta vicino alla soglia di
significatività senza raggiungerla, e l'errore standard della media passerebbe
da ±0,027 a ±0,021. Guadagno cosmetico. Per distinguere una GRU da una LSTM ne
servirebbero **113**.

### «Perché i landmark e non i pixel?»

Tre ragioni, in ordine di peso:

1. **Riservatezza per costruzione.** L'immagine viene scartata alla fonte:
   quello che raggiunge il classificatore non contiene volto, abbigliamento né
   sfondo. Non è una dichiarazione di intenti, è una proprietà della catena — il
   modello *non può* imparare l'aspetto delle persone perché l'aspetto non gli
   arriva. È la condizione perché una telecamera sia accettabile in una casa
   privata.
2. **Costo.** Poche decine di numeri invece di 640×480×3 componenti. È ciò che
   rende possibile far girare tutto su cento euro.
3. **Interpretabilità.** Ogni grandezza si riconduce a una parte del corpo,
   quindi si può misurare separatamente il contributo di ciascun gruppo di punti
   — ed è esattamente ciò che fa l'esperimento sulle occlusioni.

MediaPipe restituisce **33 punti**. Non si usano tutti allo stesso modo: ogni
rappresentazione ne seleziona un sottoinsieme scelto per significato cinematico
(naso, spalle, anche, ginocchia, caviglie). Il dettaglio è in
`03_CAP3_metodologia.md`.

---

## 4. La cronologia, in dodici passi

Serve per leggere i registri: quasi ogni numero della tesi ha una data.

| quando | che cosa | dove |
|---|---|---|
| 19 ago | motore geometrico unificato, estrazione pilota su 2 soggetti | EXP-001 |
| 19 ago | **primo difetto**: angolo dell'ellisse srotolato con periodo 360 invece di 180 | ISS-100 |
| 19 ago | estrazione completa, 10 soggetti, 114.923 fotogrammi, 95,5% pose valide | EXP-003 |
| 19 ago | **secondo difetto**: il vincolo DTW si allargava sulle coppie caduta/ADL — run annullata | ISS-101, EXP-004 |
| 19 ago | DTW corretto + selezione consapevole della ridondanza | EXP-005, EXP-006 |
| 20 ago | **terzo difetto**: quattro grandezze A2 misuravano l'origine del riferimento | ISS-104 |
| 20 ago | riestrazione (v2, 32 colonne) e nuovo DTW: le due A2 riabilitate salgono al 2° e 3° posto | EXP-007, EXP-008 |
| 20 ago | prima LOSO difendibile, e la scoperta che la soglia è instabile | EXP-009 |
| 20 ago | sei regole di soglia a confronto: **vince non scegliere** | EXP-010, DEC-105 |
| 20 ago | cinque architetture, lunghezza della finestra, analisi di numerosità | EXP-011/012/013 |
| 21 ago | UR-Fall riestratto con il motore nuovo; le tre definizioni del compito | EXP-014, EXP-015 |
| 22 ago | le stesse 56 clip su PC e su board: 55 decisioni identiche, una diversa | EXP-016, ISS-106 |
| 26 ago | scomposizione della latenza: il ritardo **non è misurabile** con annotazione al minuto | EXP-017, ISS-108 |

---

## 5. I numeri da ricordare

**In laboratorio** (UP-Fall, LOSO su 10 soggetti, camera 1):

| configurazione | F2 |
|---|---:|
| A3 — riferimento | 0,898 ± 0,075 |
| A3h — con l'altezza dal pavimento | 0,931 ± 0,051 |
| A3i — con le grandezze integrali | 0,943 ± 0,064 |
| A3i + controesempi domestici | **0,953 ± 0,055** |

**Le tre definizioni del compito** (foresta, sottoinsieme DTW):

| compito | F2 | falsi allarmi sui distesi volontari |
|---|---:|---:|
| **evento** (`fall`) | **0,831** | **0,0%** |
| stato (`fallen`) | 0,704 | 12,5% |
| allarme (`fall` O `fallen`) | 0,810 | 13,1% |

**In casa** (eventi/ora, persistenza 5, sospensione 30 s):

| compito | casa studente | casa nonni | cadute rilevate |
|---|---:|---:|---:|
| evento | 0,9 | 5,3 | 3/5 |
| stato | 15,2 | 104,2 | 0/5 |
| allarme | 23,2 | 105,1 | 4/5 |

**Il costo per fotogramma sulla board**: percezione **88,4%**, classificatore
**5,8%**, totale 37,7 ms cioè 26,5 fps.

**Il risultato principale**: fra la configurazione di riferimento e quella
adottata corrono **0,055 di F2 in laboratorio** — dentro la dispersione fra
soggetti, quindi una differenza che non si può dichiarare — e un **fattore 52**
sui falsi allarmi in una casa reale.

---

## 6. Che cosa NON è stato fatto

Dichiararlo vale quanto dichiarare il resto, ed è una delle regole di scrittura
del progetto.

- **Ricerca di iperparametri**: nessuna, in nessun esperimento.
- **Occlusioni da mobilio reali**: non misurate — né UP-Fall né UR-Fall le
  annotano. È misurata solo l'occlusione *simulata* per congelamento.
- **Multi-persona**: implementato e funzionante, ma non validabile, perché
  nessun archivio pubblico contiene più persone in scena.
- **Effetto della quantizzazione INT8**: non isolato dal cambio di rete.
- **Reti a grafo sui giunti dello scheletro**: non provate. La rete a grafo
  di [EXP-018](../EXPERIMENTS.md#exp-018) lavora sulle grandezze geometriche.
- **Prova di durata da dodici ore**: non eseguita. È l'ultima richiesta esplicita
  del relatore ancora aperta.
- **Il confronto con i dispositivi in commercio** --- prezzo, prestazioni
  dichiarate, quali dati escono dall'abitazione --- non è mai stato fatto,
  benché sia l'ipotesi economica da cui il lavoro parte. Vedi il paragrafo che
  segue.

### Le reti a grafo: provate il 27 agosto

Fino a quella data questo documento e il Capitolo 2 dichiaravano «reti a grafo:
mai provate». **Non è più vero** ([ISS-122](../ISSUES.md#iss-122)). Una rete
spazio-temporale è stata addestrata con lo stesso protocollo delle altre cinque
architetture ([EXP-018](../EXPERIMENTS.md#exp-018)). Va detto con precisione
che cosa è stato provato: **i nodi del grafo sono le dodici grandezze
geometriche in ingresso, non i giunti dello scheletro**, e l'adiacenza è
appresa. Una GCN sui giunti resta fuori, perché cambierebbe insieme
architettura e rappresentazione.

Il risultato: **F2 0,779 ± 0,122** contro 0,847 della GRU, cioè −0,068, con
$t = -2{,}37$ e vittoria su 2 fold su 10. È il primo confronto fra architetture
del lavoro che supera la soglia critica di 2,26, e la supera nel verso
sbagliato. Non sopravvive alla correzione per molteplicità: cinque confronti
contro lo stesso riferimento richiedono $|t| > 3{,}25$. La lettura difendibile
è quindi **nessuna architettura fa meglio della GRU, e la sola che si avvicina
a essere distinguibile fa peggio.**

La domanda di accuratezza resta quella che con dieci soggetti **non si può
decidere**: per separare una GRU da una LSTM ne servirebbero 113
([EXP-013](../EXPERIMENTS.md#exp-013)), e per sostenere lo scarto del grafo ne
servirebbero 16.

La domanda che invece **si può decidere** --- e che è quella da cui il lavoro
parte --- è di **fattibilità economica**: *un modello più pesante ci sta, su
cento euro, e a che prezzo in fotogrammi al secondo?* Quella non dipende dal
numero di soggetti: dipende dal dispositivo, e si misura sul dispositivo.

E la risposta, misurata ([EXP-019](../EXPERIMENTS.md#exp-019)), è che la rete a
grafo **non è affatto più pesante**: 12.323 parametri contro i 24.483 della
GRU, e 1,80 ms per finestra contro i 4,85 ms della foresta che gira sul
dispositivo. Il classificatore è il **5,8%** del costo per fotogramma, quindi
il margine c'era e c'è: un classificatore dieci volte più pesante porterebbe il
totale da 37,7 a circa 57 ms, cioè da 26,5 a **~17,5 fps**, che resta sopra i
9 fps su cui il modello è addestrato. **Il collo di bottiglia resterebbe la
percezione.**

L'obiettivo del lavoro, detto per intero, non è «classificare bene una caduta»:
è stabilire se un dispositivo da un centinaio di euro --- una Radxa o una
Raspberry con una telecamera --- possa fare il lavoro di un impianto
commerciale **a costo inferiore di ordini di grandezza e senza che alcuna
immagine esca dall'abitazione**. Su quell'obiettivo l'architettura del
classificatore conta per il costo, non per l'accuratezza, e i due vanno
misurati separatamente.

---

## 7. Le tre cose che cambiano l'interpretazione di qualunque numero

1. **`eventi.csv` nelle sessioni contiene finestre sopra soglia, non eventi.**
   Le due grandezze differiscono di un fattore misurato in **47,8**. Gli eventi
   si ricalcolano con `pipeline/eventi_sessioni.py`, ed è l'unica forma in cui i
   numeri di campo vanno riportati.
2. **I numeri misurati sul PC non sono i numeri della board.** Lo stimatore di
   posa è un *tracciatore* e diverge fra architetture ([ISS-106](../ISSUES.md#iss-106)):
   su 56 clip, 55 decisioni identiche e una diversa — ed era una caduta vera.
3. **Sei misure sono ancora a cinque soggetti** e il testo lo dichiara dove
   compaiono: effetto del punto di vista, confronto fra rappresentazioni,
   dimensione del modello, frame rate, scansione di K, confronto fra stimatori.
