# Guida al lavoro: che cosa è stato chiesto, che cosa risponde, che cosa no

Verificato sui dati il **6 settembre 2026**. Ogni numero di questo documento
è stato ricontrollato sul file che lo produce, non ripreso da un altro
documento.

Serve a **me**: che cosa il relatore ha chiesto, che cosa il progetto risponde
a ciascuna richiesta, quali numeri reggono e quali no. Per lui c'è
[RISPOSTE_AL_RELATORE.md](RISPOSTE_AL_RELATORE.md), scritto per essere letto
da fuori.

---

## Parte 0 — Le tre nozioni senza cui le tabelle non si leggono

### F2, e perché non l'accuratezza

Le finestre di caduta sono il **14%** del dataset e circa lo zero per cento in
un soggiorno vero. Un modello che dicesse sempre «non è una caduta» avrebbe
l'86% di accuratezza e sarebbe inutile.

Si usano due grandezze che guardano **solo** gli allarmi e le cadute:

- **recall** — delle cadute vere, quante ne prendo;
- **precision** — dei miei allarmi, quanti erano cadute vere.

**F2** le combina pesando il recall **quattro volte** la precision. È una
scelta dichiarata *prima* di guardare i risultati, ed è giusto così — ma nella
Parte 3 diventa la chiave di tutto.

### Leave-one-subject-out, e la dispersione fra soggetti

Si addestra su otto soggetti, si sceglie la soglia su un nono, si verifica sul
decimo; si ripete dieci volte. **La persona su cui verifico non l'ha mai vista
nessun modello.**

Ne esce la grandezza più importante del progetto: la **dispersione fra
soggetti**, cioè quanto il risultato cambia a seconda di *chi* è escluso. Vale
**±0,085** di F2. È il metro di tutto: una differenza più piccola di ±0,085 non
è distinguibile dall'aver pescato una persona invece di un'altra.

### Evento contro finestra sopra soglia

Il sistema decide ogni 0,25 s. Una caduta produce una **raffica** di decisioni
positive, perché la persona resta a terra. Contarle come allarmi sovrastima di
quasi due ordini di grandezza: su **quindici ore** di registrazioni domestiche
— nove sessioni, 166 eventi — il rapporto vale **44,8**.

*Era 47,8 fino al 7 settembre 2026: la sessione di durata del 6 settembre non
entrava nel conto, perché il registratore nuovo scrive i punteggi con un altro
nome di file ([ISS-140](ISSUES.md#iss-140)). Il valore si ricalcola con
`pipeline/eventi_sessioni.py`, che ora lo scrive anche in
`risultati/campo/eventi_sessioni.json`.*

La regola installata chiede **5 finestre consecutive** e poi tace **30 s**.
Ogni numero di campo di questo lavoro è un **evento**.

---

## Parte 1 — Il dataset, verificato

`dataset/processed/features/feature_v2.csv`, 71 MB.

| | |
|---|---:|
| soggetti | **10** (`Subject_01`…`Subject_10`) |
| attività per soggetto | **11**, tutte, per tutti |
| camere | **2** — 57.786 e 57.137 fotogrammi |
| video | **218** |
| fotogrammi | **114.923** |
| posa rilevata | **95,5%** |

**Video per categoria:** 100 di caduta, 118 di attività normale.
**Fotogrammi per categoria:** 17.892 caduta, 97.031 normale.

**Etichetta per fotogramma** — è questa che conta, non la categoria del video:

| etichetta | significato | fotogrammi | quota |
|---|---|---:|---:|
| 0 | attività normale o pre-caduta | 98.857 | 86,0% |
| 1 | **caduta in corso** | 5.542 | 4,8% |
| 2 | a terra, dopo | 10.524 | 9,2% |

Le due camere sono perfettamente bilanciate: 2.771 fotogrammi di classe 1
ciascuna, identici, perché sono sincronizzate.

### Due video mancano, e uno ha un errore di nome

Attesi 10 × 11 × 2 = **220**, presenti **218**. Mancano davvero:

- `sub06_act08_trial01_cam02`
- `sub07_act10_trial01_cam01`

E un terzo c'è ma si chiama `sub01_act08_**trail**01_cam02` — errore di
battitura **nel dataset originale**, non nostro. Va saputo, perché qualunque
script che costruisca i nomi a partire dallo schema non lo trova.

---

## Parte 2 — Dalle immagini alle grandezze, verificato

### Le tre rappresentazioni: 32 grandezze

Dallo scheletro di MediaPipe (33 punti) si ricavano **32 grandezze**, in tre
famiglie che guardano il corpo in tre modi diversi:

| | famiglia | che cosa guarda | grandezze |
|---|---|---|---:|
| **A1** | un'**ellisse** adattata alla nuvola di punti | forma complessiva del corpo | 12 |
| **A2** | il **vettore del tronco nello spazio** | inclinazione 3D anca→spalle | 8 |
| **A3** | un **riferimento centrato sul bacino** | altezze e velocità relative | 12 |

Di queste, **nove sono integrali** — `escursione`, `percorso`, `discesa`, una
terna per famiglia — accumulate su una finestra mobile di 31 fotogrammi. Non
sono derivate istantanee: sono ciò che è successo negli ultimi 1,7 secondi.
Servono perché la foresta riassume la finestra con statistiche e non ha alcuna
nozione di ordine: l'informazione temporale va consegnata già calcolata.

### La selezione con il DTW: 12 su 32

`risultati/dtw/classifica_dtw.csv` classifica tutte e 32 le grandezze su
**entrambe** le camere. Il punteggio usato per decidere è il **minimo fra le
due**, non la media — perché una grandezza che separa benissimo da un punto di
vista e per niente dall'altro è inutile a un sistema che verrà montato in una
stanza qualunque, e la media la premierebbe.

Le dodici scelte pescano da tutte e tre le famiglie: **A1: 3, A2: 3, A3: 6**.

**La selezione non è «le prime dodici», ed è la cosa che va capita.** Tre
grandezze fra le prime dodici per punteggio sono state **scartate**:

| scartata pur essendo in alto | presa al suo posto |
|---|---|
| `A2_angolo_tronco` | `A1_escursione` |
| `A3_testa_rel_y` | `A3_hip_vel` |
| `A2_escursione` | `A3_testa_vel_rel` |

Il motivo: il DTW valuta ogni grandezza **da sola**, e premia tre volte lo
stesso fenomeno se è misurato in tre modi. Le prime dodici secche contenevano
**cinque coppie con correlazione oltre 0,80**, tre delle quali sopra 0,94, e
tutte riconducibili a «quanto è verticale il tronco». Applicando un tetto di
0,85 alla correlazione, la correlazione media fra le scelte scende da 0,385 a
**0,325**.

**Quindi sì: sono state prese le più discriminative — ma non le più
discriminative in assoluto, le più discriminative *che aggiungono qualcosa*.**

---

## Parte 3 — Il confronto fra classificatori, verificato

### Il protocollo è a tre insiemi, e sono disgiunti

Ogni fold: **train ~9.100 finestre** (otto soggetti), **validation ~1.100** (un
soggetto), **test ~1.200** (un soggetto). Verificato: tutti e dieci i soggetti
usati come test esattamente una volta, e **in nessun fold validation e test
coincidono**.

**La soglia è fissa a 0,50, dichiarata a priori**, e i file di run lo scrivono:
`scelta_soglia: "fissa a 0.5, dichiarata a priori"`. Per un confronto fra
architetture è la scelta corretta — nessuna prende vantaggio dalla taratura.

### La matrice di confusione, sommata sui dieci fold

Esempio, la GRU:

| | predetto **normale** | predetto **caduta** |
|---|---:|---:|
| **reale normale** | 9.202 | **885** *(falsi positivi)* |
| **reale caduta** | **105** *(falsi negativi)* | 1.318 |

E per tutte e sei, su 1.423 finestre positive e 10.087 negative:

| modello | F2 | recall | precision | falsi negativi | falsi positivi | FP/FN |
|---|---:|---:|---:|---:|---:|---:|
| **LSTM** | **0,858** | 0,928 | 0,621 | 102 | 807 | 7,9 |
| GRU | 0,847 | 0,926 | 0,598 | 105 | 885 | 8,4 |
| Transformer | 0,846 | 0,937 | 0,565 | **89** | 1.028 | 11,6 |
| CNN 1D | 0,833 | 0,933 | 0,534 | 95 | 1.161 | 12,2 |
| **Foresta** *(installata)* | 0,792 | 0,810 | **0,732** | 271 | **421** | **1,6** |
| Grafo | 0,779 | 0,868 | 0,502 | 188 | 1.225 | 6,5 |

### La domanda: si può usare «la rete migliore»?

**La migliore per F2 è la peggiore per falsi allarmi, e viceversa.**

LSTM contro Foresta: **+0,066** di F2, **−169** falsi negativi (−62%), ma
**+386** falsi positivi (**+92%**).

Non è un pareggio: è uno **scambio**, e va deciso, non calcolato.

**Perché l'F2 mette la foresta ultima.** Perché pesa il recall quattro volte la
precision: **ordinare per F2 significa ordinare per quanto un modello è
disposto a suonare.** La foresta ha la precision più alta di tutte e il
rapporto falsi allarmi / cadute perse più basso di tutte — 1,6 contro 6,5–12,2.
L'F2 punisce la prudenza per costruzione.

**E comunque il divario non è reale.** 0,066 contro una dispersione fra
soggetti di ±0,085: **il divario è più piccolo della differenza fra due
persone**. Servirebbero 26 soggetti per dichiararlo, 113 fra GRU e LSTM.
UP-Fall ne ha 17 in tutto.

**La risposta.** Si potrebbe installare la LSTM, ma non sarebbe «meglio»:
scambierebbe meno cadute perse con quasi il doppio dei falsi allarmi, e in una
casa sono i falsi allarmi a far spegnere il sistema. La foresta è stata scelta
per ragioni che i dati **sanno** decidere: si addestra in undici secondi contro
venticinque minuti, non porta TensorFlow sul dispositivo, è riproducibile, e ha
il rapporto FP/FN più basso. **Non** perché più veloce: per finestra è la più
lenta delle sei (4,85 ms contro 1,32 della CNN).

### Che cosa sposta davvero l'ago

| intervento | effetto | soggetti per dichiararlo |
|---|---|---:|
| cambiare la **definizione del compito** | −0,309 di F2 | **2** |
| cambiare il **punto di vista** | −0,422 di F2 | — |
| cambiare **architettura** | ≤0,079 | **26–274** |

Un fattore **cinquantasei** fra la prima domanda e l'ultima.

---

## Parte 4 — Sulla board, verificato oggi

| verifica | esito |
|---|---|
| impronta di `geometry.py` PC contro board | **identica** |
| 200 finestre precalcolate | scarto **0,000e+00** |
| 56 clip elaborate dai fotogrammi | **55 su 56** identiche, una no |

La terza è quella che conta: la seconda passa con scarto **esattamente zero**
pur mascherando l'unica divergenza reale. Lo stimatore di posa è un
tracciatore, e diverge fra architetture di processore.

**Il costo per fotogramma, misurato oggi sulla telecamera vera:**

| | Capitolo 5 dichiara | misurato |
|---|---:|---:|
| percezione | 33,34 ms (88,4%) | **124,26 ms (86,2%)** |
| classificatore | 2,20 ms (5,8%) | **18,26 ms (12,7%)** |
| **totale** | **37,7 ms → 26,5 fps** | **144,1 ms → 6,9 fps** |

**La board è 3,8 volte più lenta di quanto la tesi dichiari.** Le proporzioni
reggono, e con esse la frase portante — il collo di bottiglia è la percezione.
Ma il numero sbagliato è quello in tesi: `config.py` dichiara da sempre che «la
board regge ~9 fps», e 6,9 è coerente con quello.

---

## Parte 5 — Le sessioni in casa, verificate

Dodici sessioni, **9,58 ore**, due abitazioni.

| sessione | ore | pose valide |
|---|---:|---:|
| 10 ago — sei blocchi | 0,91 in tutto | **0,6% – 39,8%** |
| 11 ago — durata 5 h | 4,99 | 83,0% |
| 12 ago — cadute due persone | 0,49 | 86,8% |
| 12 ago — cadute nonni | 0,75 | 99,3% |
| 12 ago — nonni | 1,20 | 92,0% |
| 13 ago — **cadute da sola** | 0,58 | **25,9%** |
| 13 ago — multi tre persone | 0,66 | 97,6% |

Le sei sessioni del 10 agosto non entrano in alcun risultato: la telecamera era
posizionata male, ed è il motivo per cui esiste il protocollo di ripresa. **La
sessione da cui vengono le cinque cadute ha il 25,9%**, peggio di sessioni che
sono state scartate.

### Le sessioni di casa SONO già state usate — e mi ero espresso male

Sono state usate come **controesempi negativi**, ed è uno dei risultati del
lavoro:

| configurazione | F2 | falsi negativi | falsi positivi |
|---|---:|---:|---:|
| A3 | 0,898 | 45 | 172 |
| A3h *(+ altezza dal pavimento)* | 0,931 | 22 | 137 |
| A3i *(+ integrali)* | 0,943 | 14 | 150 |
| **A3i + controesempi domestici** | **0,953** | **14** | **124** |

I controesempi tolgono 26 falsi positivi senza toccare i falsi negativi.

### E le cadute registrate in casa sono recuperabili — in parte

Le sessioni registrano dieci grandezze più `hip_x`, `hip_y` e `torso_len`.
Verificato colonna per colonna:

| dove servirebbero | recuperabili? | perché |
|---|---|---|
| set **A3** (10 grandezze) | **sì, subito** | le dieci colonne sono esattamente quelle |
| set **A3i** (A3 + 3 integrali) | **sì, ricalcolando** | gli integrali A3 vogliono angolo del tronco, posizione dell'anca e lunghezza del torso: tutti e tre registrati |
| set **A3h** | no | manca `h_pavimento`, e serve il piano del pavimento dai landmark |
| **sottoinsieme DTW a 12** | no | sei delle dodici sono integrali A1 e A2, che vogliono l'ellisse e il naso: non registrati |

**Quindi la tua idea si può fare**, su A3 e su A3i — che è la seconda
configurazione migliore, F2 0,943. Non sul modello installato.

**Resta però un limite che non si aggira:** le clip esistono **solo attorno
agli allarmi**. Le cadute che il sistema si è perso non hanno immagine, e sono
esattamente quelle che servirebbero per migliorarlo. Il file delle grandezze
invece c'è per tutta la sessione, quindi le cadute perse **hanno i numeri anche
se non hanno le immagini**: si possono etichettare a mano dagli orari annotati.

**Da oggi il problema non si ripresenta:** `rileva.py --feature` scrive tutte e
**32** le grandezze per fotogramma, con gli stessi nomi e lo stesso ordine di
`feature_v2.csv`.

---

## Parte 6 — Le richieste del relatore, una per una

### A1 — Resilienza al cambio di telecamera e di ambiente ✅

Due misure. *Cambio di inquadratura*, a parità di soggetto, caduta e istante:

| addestrata su | verificata su | F2 | falsi positivi |
|---|---|---:|---:|
| Camera 1 | Camera 1 | 0,857 | 57 |
| Camera 1 | Camera 2 | 0,434 | 1.113 |
| Camera 1 + 2 | Camera 2 | **0,678** | **460** |

Cambiare punto di vista costa **metà dell'accuratezza**; addestrare su due
viste ne recupera il 58% e taglia i falsi positivi del 59%, migliorando recall
e precision **insieme** — che è ciò che distingue un apprendimento più generale
dallo spostamento di una soglia.

*Trasferimento a UR-Fall*: F2 0,034 con la soglia installata, 0,492 ritarando.

⚠ **Il perché è cambiato il 6 settembre** — vedi Parte 7, punto 1.

### A2 — Occlusioni ✅

Perdita massima **0,020 di F2** contro una dispersione di 0,078: **nessun
gruppo di landmark è critico**. Non è il risultato atteso. Le occlusioni da
mobilio reale **non** sono misurate: quella misurata è simulata.

### A3 — Porting su edge senza video verso l'esterno ✅ / ⚠

Gira su una Radxa da ~100 €. Sulla riservatezza il risultato è pieno: si
salvano **solo posa e punteggi**, e per ottenerlo è stata tolta dal prototipo
una registrazione video continua che contraddiceva la tesi. Sui numeri di
velocità, vedi Parte 4.

### A4 / B5 — Prova di durata ⏳

Dodici blocchi, 9,58 ore, la più lunga 4,99 h continuative. **La prova da
dodici ore con controllo della sospensione è partita oggi.**

Il «controllo della sospensione»: il primo tentativo *sembrava* riuscito e non
lo era, perché la macchina si era sospesa da sola. C'era un orologio solo. Ora
ce ne sono **due** — uno da parete e un cronometro che conta solo da sveglio — e
la differenza è quanto ha dormito.

### B1 — PR-AUC nel trasferimento ✅

L'F2 dipende da dove metti la soglia; la PR-AUC guarda **tutte** le soglie e
dice se il modello *ordina* ancora le finestre.

| | PR-AUC | rispetto alla prevalenza |
|---|---:|---:|
| archivio di addestramento | 0,990 | 18,7× |
| archivio mai visto | **0,169** | **1,79×** |

**C'è perdita reale**, non solo taratura. La soglia scelta a posteriori sul
dominio di destinazione è chiamata **soglia oracolo**: chi installa il sistema
non ce l'ha.

### B2 — Controesempi di una casa verificati sull'altra ✅

0,342 → 0,171 e 1,781 → 0,890 eventi/ora: **circa un fattore due in entrambi i
versi**. Non è una dimostrazione con due case, ma indica che il modello ha
imparato una categoria trasferibile. **Il costo è dichiarato:** in quella
configurazione il recall scende a due cadute su cinque.

### B3 — Verifica controllata sulle occlusioni ✅ *(= A2)*

### B4 — Metriche di campo a livello di evento ✅ / ⚠

Fatte tre su quattro. **La latenza non è misurabile** con questi dati: le
cadute sono annotate **al minuto** e la grandezza è di pochi secondi.

Si misura invece la **scomposizione**: calcolo 0,038 s (1,0%), **riempimento
della finestra 2,743 s (72,6%)**, persistenza 0,997 s (26,4%), limite inferiore
**3,778 s**. Il ritardo è dominato dalla finestra, non dall'hardware.

### C1 — Ingressi della foresta e grandezze integrali ⚠

**Il meccanismo che descriveva è corretto; i numeri no.** Il guadagno di 0,040
veniva da cinque soggetti; a dieci **non è distinguibile dal caso**, e con
un'altra regola di etichettatura il segno si rovescia. Servirebbero 34–70
soggetti. Resta come **lettura dichiarata**, non come contributo misurato.

### C2, C4 — Terminologia ✅

«Adattamento al dominio» invece di «generalizzazione»; «soglia oracolo»
definita come valore non ottenibile da chi installa.

### C3 — Mostrare i due errori ✅

È la richiesta più fertile: da qui nasce tutta la Parte 3. Da A3 alla
configurazione finale i falsi negativi passano da 45 a 14 e i falsi positivi da
172 a 124: in laboratorio **nessuno scambio**, migliorano entrambi. Lo scambio
compare solo in casa.

### C5 — Coerenza fra 4,47 e 2,20 ms ✅ / ⚠

La spiegazione regge — il classificatore decide una volta ogni due fotogrammi,
quindi il costo per fotogramma è metà di quello per finestra. I due valori sono
però in discussione: vedi Parte 4.

### C6 — Parametri non dichiarati del recall di campo ✅

Riportato come **intervallo con i parametri esposti**, mai come numero singolo.

### C7 — Indice e struttura ✅

Rifatto il 31 agosto sulla struttura a cinque capitoli.

---

## Parte 7 — Che cosa non torna

### 1. Su Camera 2 lo stimatore perde chi cade

| | riprese con cambio di persona |
|---|---:|
| Camera 1 (laterale) | **0 su 50** |
| Camera 2 (rialzata) | **11 su 50** |

E arriva nei dati di addestramento: 3 su 25. **Nel 12% delle cadute di Camera 2
il modello riceve, per la fase a terra, le grandezze di un'altra persona.** Il
capitolo spiegava il divario con la sola compressione prospettica: le cause
sono **due**.

Peggio: provando la telecamera in soggiorno, a stanza vuota, lo stimatore ha
disegnato una persona **sopra una cyclette**, con il 72% di «pose rilevate». Il
protocollo accetta una sessione guardando quella percentuale.

### 2. La board è quasi quattro volte più lenta *(Parte 4)*

### 3. Sedici voci di bibliografia mai verificate

Su 32. Delle dodici controllate, **quattro affermazioni non hanno retto**, e
tre riferimenti non corrispondevano a lavori reali. Cinque voci inoltre non
sono citate da nessuna parte e vengono stampate lo stesso.

### 4. Cinque cadute non stimano un recall

Intervallo di confidenza da **0,28 a 0,99**. È il limite più serio del lavoro.

---

## Parte 8 — Come migliorare, in ordine di resa

1. **Rifare la sessione di cadute** con l'inquadratura verificata oggi (quattro
   criteri su quattro) e `--feature` attivo. Con 4–6 persone e ~5 cadute
   ciascuna l'intervallo passa da 0,59 a circa 0,30.
2. **Recuperare le cadute già registrate** su A3 e A3i, etichettandole dagli
   orari annotati: i numeri ci sono anche dove mancano le immagini.
3. **Non fidarsi della quota di pose valide** come criterio di accettazione.
   Serve un controllo che guardi *dove* sta la posa e *quanto si muove*.
4. **Rieseguire il confronto fra le viste** escludendo le riprese contaminate.
5. **Verificare le sedici voci di bibliografia.**
6. **Non inseguire l'architettura.** Servirebbero 26–274 soggetti, ed è il
   posto dove il lavoro *non* va speso.
