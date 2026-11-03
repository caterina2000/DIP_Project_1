# Capitolo 2 — Stato dell'arte nel rilevamento automatico delle cadute

**File:** `tesi/Cap2.tex` · **etichetta:** `cap:stato_arte` · **2.618 parole**,
5 sezioni, **zero sottosezioni** (i blocchi da ~150 parole sono `\paragraph`).

Questo capitolo **non esisteva** fino al 23 agosto 2026. È stato scritto da zero
e poi **riscritto quattro volte**, ogni volta su un'obiezione fondata. La storia
delle quattro stesure è più istruttiva del contenuto finale, quindi viene prima.

---

## 1. Le quattro stesure, e che cosa ha fatto fallire le prime tre

### Prima stesura — 5.271 parole. Difetto: parlava del lavoro senza mostrarlo

Misurato, non giudicato a sensazione:

- **venticinque rimandi** ai capitoli sperimentali («il Capitolo X lo misura»);
- **venti occorrenze** di «questo lavoro»;
- **diciannove paragrafi** con **una citazione su centosette**.

Un capitolo di stato dell'arte che cita se stesso invece che la letteratura non
è uno stato dell'arte: è un riassunto anticipato della tesi.

### Seconda stesura — 2.645 parole. Difetto: gerarchia

Tolti i rimandi, tolti i grassetti (da 18 a 0), introdotto l'ambiente `Domanda`
per **porre** le domande del lavoro invece di prometterne la risposta.
Restavano però otto sottosezioni, sei dentro la stessa sezione e lunghe fra 104
e 189 parole: sotto le 250 parole un blocco non giustifica una `\subsection`.

### Terza stesura — 2.416 parole, cinque sezioni, zero sottosezioni

Tolte le due parti che descrivevano **cose non impiegate nel lavoro**:

- il confronto fra elaborazione diretta dell'immagine e posa, già argomentato
  nel Capitolo 1;
- la trattazione estesa delle reti a grafo, ridotta a una menzione nell elenco
  delle famiglie. Dal 27 agosto una rete a grafo E stata provata (EXP-018), ma
  sulle grandezze geometriche e non sui giunti: vedi ISS-122.

Al loro posto una **dichiarazione esplicita** di quali famiglie il lavoro
confronti e quali no. Le sei sottosezioni sono diventate `\paragraph`: hanno un
nome, non una voce nell'indice.

### Quarta stesura — 26 agosto, 2.516 parole. Causa: il nuovo Capitolo 1

La candidata ha riscritto il Capitolo 1, che ora **assorbe tre argomenti** prima
trattati nel Capitolo 2: la scelta della visione contro gli indossabili, la
scelta della posa con la motivazione di riservatezza, e il conto sulla frequenza
di base. La sua versione del Capitolo 2 li ripeteva tutti e tre, conteneva un
blocco duplicato al proprio interno (il passaggio su Lin et al. compariva due
volte) e **reintroduceva due affermazioni già smentite**.

La quarta stesura li toglie e vi rimanda. Ha inoltre assorbito cinque citazioni
che il nuovo Capitolo 1 non porta più: `bagala`, `tcnte`, `gcn3stream`,
`scheurer`, `vira`.

---

## 2. ISS-110 — il difetto più pericoloso del progetto

**Due versioni divergenti dello stesso capitolo**, una in Overleaf e una nel
repository, fuse a mano.

Il danno accertato: la versione Overleaf del Capitolo 2 riportava per OmniFall
«circa 14 ore di registrazioni uniche, 101 soggetti e 29 viste». Sono i numeri
**già trovati sbagliati e corretti il 25 agosto**: l'abstract dichiara
**quindicimila riprese, ottanta ore, sedici classi**. La stessa versione
attribuiva la rassegna skeleton-based a una «review del 2024 con oltre cento
metodi» invece che a `nguyen` (Sensors 23(11):5121, 2023).

> **Un fatto verificato e corretto è tornato indietro.** È il modo di sbagliare
> più pericoloso del progetto, perché non lascia traccia: il testo compila, si
> legge bene, e il numero è falso.

**Difesa adottata:** un avviso in testa a `tesi/Cap2.tex` che protegge
esplicitamente i due numeri, e la regola che ogni fusione fra le due versioni va
fatta confrontando i numeri contro i commenti `% VERIFICATO` in
`Bibliografia.tex`, **mai a memoria**.

Danno secondario dello stesso episodio: **dieci chiavi di citazione su dodici**
non esistevano in `Bibliografia.tex` (`1`, `kangas2015falsealarm`,
`scheurer2019aidemoi`, `mubashir2013survey`, `gutierrez2021vision`,
`huang2024skeleton`, `lin2021openpose`, `martinez2019upfall`,
`broadley2018realworld`, `schneider2025omnifall`). Con `thebibliography`
scritto a mano **non compilano come riferimento**.

### Lo stato della bibliografia, oggi

- **7 voci su 31** portano il commento `% VERIFICATO`: `broadley`, `gomes`,
  `gutierrez`, `kangasreali`, `lin`, `nguyen`, `omnifall`.
- **3 erano inventate** e sono state ritirate ([ISS-114](../ISSUES.md#iss-114)).
- **5 non sono citate** da nessuna parte: `gru`, `lstm`, `noury`,
  `randomforest`, `rougier`. Con `thebibliography` **vengono stampate lo
  stesso**, a differenza di bibtex: per ritirarle non basta togliere il `\cite`,
  va commentata la voce.
- **Le restanti 16 non sono mai state controllate sulla fonte**, e sostengono
  numeri che compaiono nell'Introduzione.

Quando le sette furono verificate, **due affermazioni su sette non ressero**:

| voce | che cosa diceva | esito |
|---|---|---|
| `omnifall` | «quattordici ore, 101 soggetti, 29 viste» | **falso** → 15k riprese, 80 ore, 16 classi |
| `nabizade` | «undici studi su 588 record» | **nessun riscontro** → sostituita da `gomes` (IEEE J. Biomed. Health Inform. 2026, 433 studi primari), che sostiene la stessa tesi con numeri verificabili |

È il punto aperto numero due del lavoro. Con un tasso di errore di 2 su 7 sul
campione verificato, le sedici non verificate sono un rischio reale.

---

## 3. Il contenuto, sezione per sezione

L'ordine seguito è **quello delle scelte da compiere**: il sensore → la
rappresentazione → il modello temporale → i dati e i protocolli. Per ciascuna si
dichiara quali alternative la letteratura offre e **quali fra esse questo lavoro
confronta**.

### 2.1 — Tecnologie: tre famiglie

| famiglia | vantaggio | limite |
|---|---|---|
| **indossabili** (accelerometri, giroscopi) | il sensore segue la persona, non dipende dal punto di vista | dipende dalla *compliance*: va indossato, caricato, usato con continuità |
| **ambientali** (pressione, acustica, IR, radar) | non chiedono nulla all'utente | il vincolo si sposta sull'ambiente: coprono solo le aree strumentate; descrizione più povera del movimento |
| **vision-based** (RGB, RGB-D, termiche) | più informazione: posizione, configurazione, dinamica, interazione | costo di calcolo, e il video contiene informazioni identificative |

Riferimento quantitativo: Gutiérrez et al. hanno analizzato **ottantuno sistemi**
pubblicati fra 2015 e 2020, documentando la transizione da descrittori
geometrici progettati a mano verso rappresentazioni apprese (`gutierrez`,
Sensors 21(3):947 — *verificato*).

### 2.2 — Rappresentazione del movimento

Il passaggio chiave: **il sensore stabilisce quale informazione esista; la
rappresentazione stabilisce quale parte di essa raggiunga il classificatore.**

Rassegna di riferimento: `nguyen` (Sensors 23(11):5121, 2023 — *verificato*),
circa duecentocinquanta risultati da oltre settanta studi fra 2019 e marzo 2023.
Distingue **caratteristiche geometriche progettate a mano** da
**rappresentazioni apprese**, ed è esattamente la biforcazione che il Capitolo 3
percorre in entrambe le direzioni (le tre rappresentazioni A1/A2/A3 contro le
coordinate grezze B).

Alla rappresentazione scheletrica vengono attribuite due proprietà utili su
hardware limitato — **compattezza** e **interpretabilità** — ma il capitolo
aggiunge subito il rovescio, che è la tesi metodologica del lavoro:

> «La posa non è però una misura ma una **stima**. Una catena basata sulla posa
> sposta parte della difficoltà dal classificatore allo stimatore e alla
> geometria costruita sopra di esso — ed è una difficoltà che questo lavoro
> **misura invece di assumere**.»

Impiego già documentato nella fall detection: Lin et al. estraggono la posa con
OpenPose e confrontano LSTM e GRU (`lin`, Applied Sciences 11(1):329 —
*verificato*).

### 2.3 — Modellazione temporale: quattro famiglie più un termine di paragone

Ricorrenti (LSTM, GRU) · convoluzioni temporali · reti a grafo · modelli ad
attenzione. Più — e questo è il punto metodologico — un **classificatore non
sequenziale**:

> «Un classificatore che non modella l'ordine dei campioni è **necessario** per
> stabilire se un modello sequenziale stia effettivamente sfruttando dipendenze
> temporali: è il controllo che rende interpretabile l'intero confronto.»

Ed è la ragione per cui la foresta casuale è nel confronto del Capitolo 4 — non
come alternativa economica ma come **strumento diagnostico**.

Dichiarazione esplicita, in grassetto nel testo: **le reti a grafo non vengono
considerate**, non sono state provate, quindi su di esse il lavoro non dice
nulla. Fuori anche optical flow, CNN 3D, SVM e k-NN.

> **Questa frase sta per cambiare.** Il 27 agosto la famiglia mancante è stata
> implementata dietro la stessa interfaccia delle altre cinque
> (`src/modelli.py`, classe `Grafo`) e messa in addestramento a parità assoluta
> di protocollo: stesse dodici grandezze, stessa finestra, stessa LOSO, stessa
> soglia dichiarata a priori. **Quando la misura sarà chiusa la dichiarazione
> di questo capitolo andrà riscritta**, qui e nella sezione di
> posizionamento — e con essa il «cinque architetture» dell'Introduzione, del
> Capitolo 4 e delle Conclusioni.
>
> Va anticipato che cosa quella misura è e che cosa non è: **i nodi del grafo
> sono le dodici grandezze in ingresso, non i giunti del corpo.** Una GCN sui
> giunti richiederebbe le coordinate grezze dei landmark, che il CSV non
> contiene, e cambierebbe insieme architettura e rappresentazione — cioè due
> variabili invece di una, che è esattamente ciò che il protocollo di questo
> lavoro esiste per impedire.

La sezione chiude con la **prima Domanda** del lavoro:

> *Quanto la scelta dell'architettura influenza il risultato, quando
> rappresentazione, dati e protocollo vengono mantenuti costanti?*

### 2.4 — Dati e protocolli: la sezione più lunga, e la più densa

Otto `\paragraph`, ciascuno con una tesi.

**Le cadute simulate sono un vincolo, non una scorciatoia.** Non si possono
provocare incidenti in persone fragili. La domanda pertinente non è «sono
simulate?» ma **che cosa, di preciso, la simulazione non conserva**. Risposta
documentata: Kangas et al. hanno confrontato cadute reali di anziani (sensori
indossati sei mesi) con cadute sperimentali — la grandezza più indicativa è la
*rapidità di crescita della decelerazione* e non il suo picco, e nelle cadute
reali compaiono **impatti multipli**, assenti negli altri movimenti
(`kangasreali`, Gait & Posture 35(3):500-505 — *verificato*).

**Quanto costa, misurato.** Bagalà et al.: tredici algoritmi pubblicati,
sensibilità dichiarata 76–100% su cadute simulate, **sensibilità media misurata
57,0% ± 27,3** su ventinove cadute reali (`bagala`). «Non è un margine di
errore: è un cambio di ordine di grandezza nella conclusione.»

**Gli archivi pubblici.** UR-Fall, Le2i, Multiple Cameras Fall Dataset, UP-Fall.
L'eterogeneità rende privo di significato il confronto diretto fra F-score
ottenuti su archivi diversi. **Perché UP-Fall**: diciassette soggetti, undici
attività, più prove per attività, e soprattutto **due telecamere sincronizzate**
— che è la condizione che rende possibile l'esperimento sul punto di vista del
Capitolo 4 — più una varietà di ADL che permette negativi più realistici.

**I valori riportati, e il protocollo che li produce.** 99,58% sulla vista
frontale di UP-Fall per un'architettura TCN+attenzione (`tcnte`); oltre 94% medio
per un modello a grafo su tre flussi (`gcn3stream`). Ma Scheurer et al. mostrano
che ottimizzare per utenti *noti* e per utenti *sconosciuti* sono problemi
distinti, con divari **oltre venti punti** sugli stessi dati (`scheurer`).
**Un valore elevato non è interpretabile senza il protocollo che lo ha prodotto.**

**Verificabilità.** Fra gli ottantuno sistemi di Gutiérrez la maggioranza è
valutata su dati propri non pubblici.

**Quali negativi, non quanti.** Il rapporto negativi/positivi non è il criterio
giusto — nessun archivio potrebbe riprodurre il rapporto reale. Il criterio è
*quali* negativi ci siano, e i **negativi difficili** (sedersi di scatto,
inginocchiarsi, chinarsi, distendersi volontariamente) sono quelli che decidono.
È la premessa concettuale del vocabolario OmniFall usato nel Capitolo 3.

**Azioni e stati.** OmniFall unifica otto archivi in sedici classi,
quindicimila riprese per ottanta ore con annotazione per fotogramma
(`omnifall`, arXiv:2505.19889 — *verificato*). Distingue le azioni
**transitorie** (`fall`, `lie_down`) dagli **stati** statici (`fallen`,
`lying`). Su video di incidenti reali i modelli confondono `fallen` con
`lying`: **non caduta contro attività, ma persona a terra contro persona
distesa.** È la stessa distinzione su cui poggia il risultato del Capitolo 4.

**Tre livelli di generalizzazione.** In ordine di severità:

1. fra **finestre** — finestre sovrapposte della stessa ripresa distribuite a
   caso: si valuta su sequenze quasi identiche a quelle viste;
2. fra **soggetti** — la divisione per persona, e il LOSO che rende visibile la
   dispersione fra individui;
3. fra **punti di vista** — specifico dei sistemi vision-based;
4. fra **archivi** — il più severo: cambiano insieme persone, ambiente,
   telecamera, frequenza, annotazione e distribuzione delle attività. Alanazi et
   al.: da 99,81% sul proprio dominio a ~50%, con $F_1$ dell'1,38%, su un
   archivio diverso (`vira`).

**Dalla finestra all'evento.** Un classificatore produce decisioni per finestra,
un sistema installato produce **eventi**. Broadley et al. rilevano che manca
accordo su come quantificare la capacità di evitare i falsi allarmi e su che
cosa costituisca un non-evento (`broadley`, Sensors 18(7):2060 — *verificato*).

**Esecuzione su dispositivo.** `gomes` (2026, 433 studi primari — *verificato*)
dedica una parte specifica a fps, latenza e piattaforma effettivamente
impiegata. «La velocità di esecuzione non è una proprietà dell'architettura, ma
una misura da compiere sul dispositivo di destinazione e sulla catena completa.»

Chiude con la **seconda Domanda**:

> *Che cosa un archivio di laboratorio non riesce a misurare, e con quali
> conseguenze per chi lo impiega per scegliere fra alternative?*

### 2.5 — Posizionamento

Le due Domande delimitano il perimetro. E la dichiarazione di ciò che resta
fuori, che nell'economia di questo lavoro vale quanto ciò che c'è dentro:

- **le reti a grafo costruite sui giunti dello scheletro**, che richiederebbero
  le coordinate dei landmark. La rete a grafo di EXP-018 lavora invece sulle
  dodici grandezze geometriche, ed e nel confronto;
- **la sintesi di punti di vista**, discussa fra gli sviluppi;
- **il rilevamento multi-persona**, realizzato ma non valutabile perché nessun
  archivio pubblico lo permette.

---

## 4. Le regole di scrittura, ricavate qui e valide per tutta la tesi

Sono state estratte dalla tesi triennale della candidata durante la riscrittura
di questo capitolo, e stanno ora in `CLAUDE.md` § 2:

1. **I capitoli di sfondo fissano i concetti che servono dopo, e si fermano.**
   Non anticipano risultati: il risultato si annuncia una volta sola,
   nell'Introduzione.
2. **Enfasi con `\emph` sui termini che si stanno definendo**, non con
   `\textbf`. Il grassetto è l'eccezione, non il ritmo.
3. **Un titolo ogni ~400 parole.** Sotto le 250 parole un blocco diventa
   `\paragraph`: ha un nome ma non una voce nell'indice.
4. **Niente formule retoriche**: «conviene», «va detto», «è la ragione per cui»,
   trattini lunghi a raffica. Frasi dichiarative, riferimento in fondo.
5. **Dichiarare cosa NON si è fatto** vale più che descriverlo come se lo si
   fosse fatto.

Il Capitolo 2, con le sue 501 parole per titolo, è stato poi usato come
**modello** per il diradamento dei capitoli 3, 4 e 5.
