# Capitolo 1 — Contesto applicativo e formulazione del problema

**File:** `tesi/Cap1.tex` · **etichetta:** `cap:contesto` · **2.912 parole**,
4 sezioni, 4 sottosezioni, 4 paragrafi (un titolo d'indice ogni ~420 parole).

Questo capitolo **non contiene misure del sistema**. È un capitolo di sfondo, e
la regola che segue è: *i capitoli di sfondo fissano i concetti che servono
dopo, e si fermano.* Il risultato viene annunciato una volta sola,
nell'Introduzione.

---

## 1. Che cosa deve fare il capitolo

Deve stabilire **quattro cose** che tutti i capitoli successivi danno per
acquisite:

1. che il problema clinico esiste e ha una forma precisa (non «le cadute sono
   brutte», ma *dove* si cade, *quanto* pesa il tempo a terra);
2. quali sono i **requisiti** rispetto ai quali il sistema andrà giudicato —
   perché la tesi si giudica su quelli, non su un F2;
3. perché il passaggio dal dato controllato all'ambiente reale è **difficile**,
   e per quali tre cause distinte;
4. che «rilevare una caduta» **non individua un compito solo** — il che è il
   seme del risultato del Capitolo 4.

---

## 2. Sezione per sezione: la tesi che sostiene, e da dove viene il numero

### 1.1 — Ambient Assisted Living e rilevanza clinica

| affermazione nel testo | fonte |
|---|---|
| gli over 65 sono il 25,1% della popolazione italiana | Rapporto Annuale ISTAT 2026 (`istat2026`) |
| circa un anziano su cinque riferisce almeno una caduta nell'ultimo anno; 16% fra 65–74, 33% oltre 85; donne 25% contro uomini 16% | PASSI d'Argento, ISS (`passi`) |
| **circa il 60% delle cadute avviene in casa**, 19% in strada, 11% in giardino, 10% altrove | `passi` |
| il 14% delle cadute richiede almeno un giorno di ricovero | `passi` |

Il 60% domestico **non è un dato di colore**: è la giustificazione dell'intero
impianto. In ospedale c'è personale, quindi il soccorso è rapido; in casa, e
soprattutto per chi vive solo, la persona può restare a terra a lungo. Da qui la
*long-lie syndrome* — disidratazione, ipotermia, danno muscolare — e la
conseguenza progettuale: **il problema non è riconoscere una caduta, è ridurre
il tempo fra l'evento e l'allarme.**

Questa frase è quella che, nel Capitolo 5, viene usata per rifiutare una
tolleranza di accoppiamento di ±90 secondi: se il danno dipende dal tempo
passato a terra, un allarme novanta secondi dopo non è un rilevamento tempestivo.
Il capitolo di sfondo, insomma, **vincola** un capitolo sperimentale.

### 1.2 — Requisiti di un sistema in esercizio continuo

Tre paragrafi, tre requisiti.

**Tempestività e sostenibilità del carico di allarmi.** Il punto è che i due non
si possono separare: un sistema continuamente attivo produce un numero enorme di
decisioni, e ogni attivazione errata costa una verifica umana. I termini di
paragone dichiarati qui sono quelli usati poi in tutto il Capitolo 5:

- Kangas et al.: ~15.500 ore di funzionamento, **0,049 falsi allarmi/ora**,
  ridotti a 0,025 con una modifica dell'algoritmo (`kangas`);
- AIDE-MOI, come esempio di riduzione ottenuta agendo sulla logica (`aidemoi`).

> **Nota storica utile all'orale.** In una versione precedente del lavoro il
> termine di paragone era **0,4 allarmi/ora**. Quel valore non ha trovato
> riscontro nella fonte ([ISS-050](../../../DIP_PROJECT/docs/ISSUES.md#iss-050)
> del registro storico) ed è stato sostituito da 0,049, che è verificato. Chi
> legge documenti vecchi del progetto troverà ancora 0,4: è sbagliato.

**Riservatezza e trattamento locale.** Qui viene introdotta la posa. La catena
è: video → landmark scheletrici (MediaPipe, costruito su BlazePose) → feature
geometriche → classificatore. La formulazione adottata nel testo è deliberata:

> «poiché volto, texture e abbigliamento non raggiungono il classificatore, il
> modello **non può** apprendere l'aspetto delle persone osservate al posto del
> movimento. È una proprietà della catena, non un'ipotesi da verificare.»

Questa frase ha una storia. Nella stesura del 26 agosto era sostenuta da una
citazione (`asif`) che si è poi rivelata un **segnaposto inventato**
([ISS-114](../ISSUES.md#iss-114)). La citazione è stata ritirata e l'affermazione
riscritta in modo che **regga da sola**, come conseguenza architetturale. È il
modo corretto di trattare un riferimento che non regge: non sostituirlo in
fretta con un altro, ma verificare se l'affermazione ne aveva davvero bisogno.

**Costo, risorse, architettura edge.** Dichiara il vincolo: la catena deve stare
su hardware a basso costo, quindi il problema non è massimizzare una metrica ma
trovare un compromesso fra accuratezza, complessità, latenza e sostenibilità del
funzionamento continuo.

### 1.3 — Criticità del trasferimento al reale

Tre sottosezioni, tre cause **di natura diversa** — e tenerle distinte è il
punto della sezione.

**Variazione del dominio e geometria di ripresa.** Una stessa dinamica appare in
modo diverso se osservata frontalmente, lateralmente o dall'alto. È
l'anticipazione del risultato più grande del Capitolo 4 (0,422 di F2 fra le due
telecamere), enunciato qui *senza il numero*: il capitolo di sfondo pone il
problema, non anticipa la risposta.

**Occlusioni e qualità della posa.** Rimando esplicito al capitolo che le
**misura** mascherando in modo controllato gruppi di punti corporei. Anche qui
c'era una citazione inventata (`zobi`), ritirata e sostituita da un rimando in
avanti al capitolo che misura il fenomeno, senza anticiparne il numero.

**Prevalenza dell'evento e frequenza di base.** È il conto che regge tutto il
Capitolo 5, ed è fatto qui:

```
4,5 decisioni/s × 60 × 60 × 24 × 365 ≈ 1,42 · 10⁸ decisioni all'anno
```

contro **una o due cadute** nello stesso periodo. E la conseguenza:

```
1,42 · 10⁸ × 10⁻⁴  ≈  1,42 · 10⁴  falsi positivi all'anno
```

cioè: **un tasso di falsi positivi dello 0,01%, che sembra trascurabile, produce
quattordicimila attivazioni errate all'anno.**

Il paragrafo si chiude con la distinzione fra i **due livelli di analisi** —
finestra e evento — che il Capitolo 5 formalizza e quantifica (fattore 47,8).

### 1.4 — Definizione dell'evento da riconoscere

È la sezione più importante del capitolo, perché contiene in nuce il risultato
del Capitolo 4.

Una caduta è un fenomeno **dinamico**: configurazione stabile → perdita di
equilibrio → variazione rapida → configurazione finale a terra. Da qui tre
formulazioni possibili del problema di classificazione:

- riconoscere l'**atto** del cadere;
- riconoscere lo **stato** successivo;
- accettare **entrambi** come rilevanti per l'allarme.

E la ragione per cui non sono equivalenti, enunciata qui in forma qualitativa:
sedersi, inginocchiarsi o sdraiarsi volontariamente producono configurazioni
simili a quelle di dopo una caduta. **La differenza non sta nella postura finale
ma nella dinamica con cui vi si arriva.**

Il Capitolo 3 la rende quantitativa (rapporti fra mediane: 30×, 42×, 139×) e il
Capitolo 4 la misura (0,0% contro 12,5% di falsi allarmi sui distesi volontari).

### 1.5 — Ipotesi di lavoro e obiettivi

Il lavoro si sviluppa lungo **quattro direzioni**, e sono le quattro che
strutturano i capitoli successivi:

1. **rappresentazione del movimento** → Capitolo 3;
2. **classificazione temporale e confronto fra modelli** → Capitolo 4, §
   architetture;
3. **definizione del compito e protocollo di valutazione** → Capitolo 4, prima
   metà e § compiti;
4. **fattibilità e trasferibilità** → Capitolo 4 § trasferimento esterno e
   Capitolo 5.

L'obiettivo dichiarato: distinguere una caduta reale da una normale attività
quotidiana **riducendo il rischio di falsi negativi senza generare un numero
eccessivo di falsi allarmi**. In un contesto *safety-critical* il falso negativo
è l'errore grave — ed è la giustificazione, dichiarata prima di guardare i dati,
della scelta di $F_\beta$ con $\beta = 2$ nel Capitolo 4.

---

## 3. Lavoro fatto su questo capitolo, e problemi trovati

### La versione della candidata sostituisce quella precedente (26 agosto)

Il capitolo esisteva in **due versioni divergenti** — una in Overleaf, scritta
dalla candidata, e una nel repository ([ISS-110](../ISSUES.md#iss-110)). Quella
della candidata è stata adottata come base perché già applicava i titoli in
forma nominale e aveva sciolto una sottosezione singola. **Il testo è suo**;
sono stati corretti soltanto:

1. **tre chiavi di citazione inesistenti**, che in compilazione sarebbero uscite
   come `[?]`:
   - `\cite{1}` → `\cite{istat2026}`
   - `\cite{kangas2015falsealarm}` → `\cite{kangas}`
   - `\cite{scheurer2019aidemoi}` → `\cite{aidemoi}`
2. **due citazioni aggiunte** dove il testo già faceva l'affermazione:
   `mediapipe` e `blazepose` sullo stimatore di posa;
3. refusi (*Analogalmente*, *duranete*, *in ambiente domestici*, *Alla luce
   considerazioni*) e decimali all'italiana (0,049 invece di 0.049).

**Gerarchia risultante:** 4 sezioni, 4 sottosezioni, 4 paragrafi → 420 parole
per titolo, contro le 192 della versione precedente.

### ISS-114 — tre riferimenti che non corrispondono a lavori reali

Lo stesso 26 agosto erano state aggiunte altre due citazioni (`asif`, `zobi`)
«per non lasciare voci di bibliografia orfane». Erano **segnaposto marcati
`[DA CERCARE]`**, con autore e titolo plausibili e un `TODO`. Insieme a `gazem`
(citato nel Capitolo 2) sono stati **ritirati**, e nessuno è stato riattaccato a
un altro riferimento — sostituire un riferimento non verificato con un altro
scelto in fretta produce lo stesso difetto con un nome diverso.

| voce | affermazione che sosteneva | come regge ora |
|---|---|---|
| `asif` | le rappresentazioni pose-based sono invarianti all'aspetto | riscritta come **conseguenza dell'architettura**: è vera per costruzione |
| `zobi` | lo stimatore perde landmark sotto occlusione | **rimando in avanti** al capitolo che lo misura, senza anticipare il numero |
| `gazem` | i wearable dipendono dalla compliance | citazione tolta; la frase resta, già attribuita dalla rassegna citata a inizio sezione |

In testa a `Bibliografia.tex` c'è ora un avviso che dice di non reinserirle.
Verificato con `python tesi/controlla.py` → «Nessun problema».

### ISS-108 — il capitolo prometteva una misura che non esiste (risolta il 27 agosto)

`Cap1.tex:64` **dichiarava**: «Per questa ragione il Capitolo~\ref{cap:campo} misura
esplicitamente il *ritardo* di rilevamento». La parola «ritardo» non compariva
nel capitolo di campo: zero occorrenze.

La misura è stata poi affrontata ([EXP-017](../EXPERIMENTS.md#exp-017),
`pipeline/latenza.py`) e la risposta è che **il ritardo fra caduta e allarme non
è misurabile con i dati disponibili**: le cadute sono annotate *al minuto*
(`['09:20','09:22','09:25','09:29','09:31']`), la grandezza da misurare è di
pochi secondi, e l'incertezza è fino a sessanta volte la quantità da misurare.
Gli scarti osservati — +11,8, +19,4, +27,7, +32,3 s — non sono ritardi del
sistema: sono il punto del minuto in cui la persona è caduta.

Ciò che si misura invece è la **scomposizione**:

| addendo | valore | quota |
|---|---:|---:|
| calcolo per fotogramma | 0,038 s | 1,0% |
| **riempimento della finestra** (22 campioni a 8,02 fps) | **2,743 s** | **72,6%** |
| persistenza (5 finestre, una ogni 0,249 s) | 0,997 s | 26,4% |
| **limite inferiore** | **3,778 s** | |

**La latenza è dominata dalla finestra di decisione, non dall'hardware: 2,74 s
contro 38 ms, un fattore settantatré.**

**Com'è finita.** Il 27 agosto la promessa è stata cercata di nuovo nel testo e
**non c'è più**: è sparita con l'installazione della versione del Capitolo 1
della candidata, il 26 agosto — insieme ai due paragrafi che aprivano entrambi
con «Questa osservazione ha una conseguenza…». Nessuno dei due interventi
previsti è stato quindi necessario, e ISS-108 è chiusa.

**Resta però un difetto residuo, con un numero proprio:** i valori della
scomposizione — 0,038 s, 2,743 s, 0,997 s, limite inferiore 3,778 s — **non
compaiono in alcun capitolo**. La misura c'è e il lettore della tesi non la
trova. È [ISS-115](../ISSUES.md#iss-115), e la sua sede naturale è il Capitolo
5, accanto al bilancio computazionale: lì il collo di bottiglia era la
percezione, qui è la finestra di decisione.

---

## 4. Come questo capitolo si collega agli altri

| ciò che il Cap. 1 fissa | dove viene ripreso |
|---|---|
| long-lie syndrome, tempestività | Cap. 5 § recall di campo: rifiuto della tolleranza a ±90 s |
| 0,049 falsi allarmi/ora | Cap. 5 § metriche di evento: 3,41/ora misurati, cioè 70× |
| conto della frequenza di base (1,42·10⁸) | Cap. 5 § frequenza di base: previsione 14–125/ora, misurati 2.735 |
| falso negativo più grave del falso positivo | Cap. 4 § metrica: $F_2$ dichiarata a priori |
| privacy-by-design | Cap. 5 § protocollo sessioni: il registratore salva solo posa e feature |
| tre formulazioni del compito | Cap. 3 § compito, Cap. 4 § compiti, Cap. 5 § compiti in casa |
| domain shift e geometria di ripresa | Cap. 4 § effetto della geometria di ripresa |
| occlusioni | Cap. 4 § robustezza all'occlusione |
