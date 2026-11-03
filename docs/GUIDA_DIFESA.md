# Guida alla difesa — tutta la tesi, per filo per segno

Scritta il 26 settembre 2026. Serve a due cose: **spiegare il lavoro dall'inizio
alla fine** senza dover riaprire i cinque capitoli, e **preparare una
presentazione di 15 minuti**. La Parte A è il riferimento completo; la Parte B
è la scaletta per parlare, con solo i numeri che contano davvero.

Ogni numero qui dentro è stato verificato contro i file del progetto il giorno
in cui è stato scritto. Se qualcosa cambia nel codice o nei risultati, questo
file va riallineato — non è un documento che si scrive una volta e si dimentica.

---

## PARTE A — Il lavoro, per filo per segno

### A.1 — Il problema, in tre frasi

Le cadute sono la prima causa di trauma grave negli anziani, avvengono per il
54% in casa, e il tempo di soccorso conta quanto l'evento stesso. I sistemi
esistenti sono o indossabili (l'anziano deve ricordarsi di metterli) o basati
su telecamere che mandano immagini fuori casa (un problema di riservatezza).
Questo lavoro costruisce un sistema che vede da una telecamera RGB, **non manda
mai un'immagine fuori dall'abitazione**, e gira su un dispositivo da un centinaio
di euro.

### A.2 — Le tre domande di ricerca

Il lavoro è organizzato attorno a tre domande (Cap1, §Domande di ricerca):

- **RQ1.** A parità di rappresentazione e di protocollo, quanto conta
  l'architettura del classificatore?
- **RQ2.** Quanto delle prestazioni ottenute in condizioni controllate
  sopravvive quando cambiano soggetto, punto di vista, dataset e ambiente?
- **RQ3.** La pipeline completa può girare in continuo su un dispositivo edge
  a basso costo, con latenza e carico di allarmi accettabili?

Le risposte sono nella sezione «Discussione e conclusione» in coda a `Cap5.tex` e
riassunte qui in A.9.

### A.3 — Le cinque forme di *domain shift*

Il filo che lega Cap2, Cap4 e Cap5 (Tabella `tab:domainshift`, Cap1):

| Forma | Che cosa cambia | Dove si misura |
|---|---|---|
| *subject shift* | la persona non è nell'addestramento | LOSO, dieci fold |
| *viewpoint shift* | la telecamera cambia posizione | Cap4, sezione vista |
| *frame-rate shift* | la cadenza non è quella dei dati | Cap4, sezione frame rate |
| *dataset shift* | i dati vengono da un archivio diverso | Cap4, dataset esterno |
| *environment shift* | la scena è una casa, non un laboratorio | Cap5, validazione domestica |

Ogni riga toglie una condizione favorevole del dataset di sviluppo. È la
struttura che spiega perché il lavoro non si ferma al laboratorio.

### A.4 — Il dataset

**UP-Fall**, pubblico: 10 soggetti, **220 registrazioni** disponibili (218 più
due rientrate dopo una correzione, v. A.10), due viste RGB (laterale e
frontale rialzata), **116.362 fotogrammi**, posa valida nel **92,3%**
(111.570 fotogrammi). Etichette a livello di fotogramma: 100.296 "non caduta",
5.542 "caduta in corso", 10.524 "a terra". Nessun ricampionamento: le 220
registrazioni restano tutte, il DTW ricampiona internamente le curve a 200
punti solo per il confronto di forma, non per l'estrazione.

### A.5 — La pipeline, passo per passo

1. **Stima della posa.** MediaPipe Pose (`solutions`), 33 landmark per
   fotogramma, coordinate 2D in pixel più *world landmark* 3D centrati sul
   bacino. Confrontato con YOLOv8-pose (17 punti COCO, più persone,
   solo 2D): MediaPipe vince nettamente (Cap5, `tab:catene`).
2. **Tre rappresentazioni geometriche**, tutte derivate dagli stessi
   landmark:
   - **A1** — ellisse di covarianza su sette punti (naso, spalle, anche,
     caviglie): allungamento e inclinazione della nuvola di punti.
   - **A2** — vettore del tronco nello spazio (world landmark 3D):
     angolo con la verticale, velocità angolare.
   - **A3** — riferimento centrato sul bacino, normalizzato sulla lunghezza
     del tronco: nove grandezze corporee più l'altezza dal pavimento
     (`A3_h_pavimento`, stimata causalmente osservando i fotogrammi in cui
     la persona è in piedi).
3. **Grandezze integrali.** Non derivate istantanee (rumorose: autocorrelazione
   a un fotogramma 0,33–0,47) ma accumulate su una finestra mobile —
   escursione, percorso, discesa — con autocorrelazione 0,95–0,98 e
   separazione fra le classi 7–90× contro 5–26× delle derivate. **L'unico
   intervento che migliora sia in laboratorio sia sul campo** (Contributo 6).
4. **Selezione DTW.** Da 33 candidate (23 grandezze + 9 integrali + 1 altezza
   dal pavimento) si sceglie un sottoinsieme con un punteggio robusto per
   camera (`S_robusto = min(S_cam1, S_cam2)`) e un filtro di ridondanza
   (|ρ| < 0,85). Due configurazioni adottate: **DTW a 12 colonne** (quella
   con cui sono state condotte le sessioni domestiche di agosto) e **DTWH a
   13 colonne** (la stessa più `A3_h_pavimento`, installata la sera del
   9 settembre).
5. **Finestre**, L=22 campioni, passo 2. Compito a tre classi
   (normale / caduta in corso / a terra) e a due classi (caduta / non caduta)
   secondo la sezione.
6. **Classificatore.** Sei architetture confrontate a parità di tutto il
   resto (A.6); quella installata sul dispositivo è una **Random Forest**
   (50 alberi), scelta per costo di deployment, tempo di addestramento e
   assenza di dipendenza da TensorFlow sul dispositivo — non per essere la
   più veloce (non lo è: 39 ms/finestra sulla board contro i 6,1 ms di un
   'altra architettura sullo stesso calcolatore usato per lo sviluppo).
7. **Regola di allarme.** Soglia 0,50, persistenza di 5 finestre consecutive,
   sospensione di 30 s dopo un allarme.

### A.6 — Il confronto fra architetture (RQ1)

LOSO su dieci soggetti, stessa rappresentazione (DTW-12), stesse finestre,
stessa soglia (Cap4, `tab:architetture`):

| Modello | F2 | Recall | FN | FP | Parametri |
|---|---|---|---|---|---|
| GRU | **0,857 ± 0,089** | 0,940 | 89 | 938 | 24.483 |
| CNN 1D | 0,838 ± 0,100 | 0,938 | 93 | 1.134 | 46.147 |
| Transformer | 0,837 ± 0,082 | 0,920 | 119 | 969 | 34.499 |
| LSTM | 0,829 ± 0,084 | 0,945 | 82 | 1.266 | 32.227 |
| Random Forest | 0,825 ± 0,076 | 0,844 | 232 | 468 | 12.928 nodi |
| Grafo (GNN) | 0,794 ± 0,087 | 0,860 | 209 | 934 | 12.323 |

Escursione fra le cinque non a grafo: **0,032** — meno di metà della
dispersione fra soggetti della migliore (0,089). **Nessuna architettura batte
sensibilmente le altre.** È la risposta a RQ1: l'architettura pesa poco.

### A.7 — Il *viewpoint shift* (RQ2, la parte più grave)

A parità di soggetto, caduta e istante, passare dalla vista laterale a quella
frontale rialzata costa **0,422 di F2** (da 0,857 a 0,434). La causa è
geometrica: una telecamera dall'alto comprime la rotazione del tronco lungo
il proprio asse ottico. Addestrando su entrambe le viste si recupera il
**58%** del divario, con i falsi positivi in calo del **59%**.

### A.8 — Il risultato principale: laboratorio contro casa

Fra la configurazione di riferimento (A3) e quella adottata (A3i + controesempi)
corrono **0,055 di F2 in laboratorio** — dentro la dispersione fra soggetti,
quindi non dichiarabile — ma **un fattore 52 sui falsi allarmi in una casa
vera**. Il benchmark di laboratorio non solo non distingue le due
configurazioni: le ordina nel verso sbagliato. È il Contributo 7, ed è il
risultato che la tesi considera principale.

Le due aggiunte (vedi `fig_configurazioni`, rifatta il 25/9) correggono errori
diversi:

| Configurazione | F2 | Cadute mancate | Falsi allarmi |
|---|---|---|---|
| A3 | 0,898 | 45 | 172 |
| A3h (+ altezza pavimento) | 0,931 | 22 | 137 |
| A3i (+ integrali) | 0,943 | 14 | 150 |
| A3h + controesempi | 0,942 | 22 | 129 |
| **A3i + controesempi (adottata)** | **0,953** | **14** | **124** |

Altezza dal pavimento e integrali abbattono le **cadute mancate**
(45→22→14); i controesempi domestici abbattono i **falsi allarmi**
(150→124) senza toccare le mancate. Due assi indipendenti — per questo la
configurazione finale li tiene entrambi.

### A.9 — Il dispositivo edge (RQ3)

**Radxa ROCK 4D** (RK3576, NPU 6 TOPS), circa 100 €. Catena installata:
MediaPipe su CPU a 9 fps dichiarati, **7,3 fps** misurati in esercizio.

- Costo per fotogramma (misurato su 4,59 h continue): percezione **85,2%**,
  classificatore **14,3%** (il classificatore consuma un settimo del tempo:
  la variabile che conta è la stima di posa, non l'architettura — coerente
  con RQ1).
- Memoria: **297 MB** di picco su 5.923 MB disponibili (**5%**).
- Modello installato: 592 kB il classificatore, 1,1 kB lo scaler,
  623 kB tutto ciò che serve a girare.
- Temperatura: regime a **79,5 °C** dopo circa 40 minuti, nessun calo di
  frequenza per protezione termica osservato.
- Prova di durata più lunga: **4,59 ore continue**, due interruzioni della
  telecamera USB (~5 s totali), nessuna sospensione del sistema operativo.
- **Alternativa NPU scartata:** MediaPipe sottocampionato a 9 fps batte
  YOLOv8 a piena velocità (26,5 fps) di 0,175 di F2 su ogni voce. Cambiare
  stimatore di posa costa 5,3× più che dimezzare il frame rate.

**Sul campo (9 sessioni, 14,98 ore, due abitazioni):** rapporto finestre
sopra soglia / eventi = **44,8** — la ragione per cui il lavoro conta sempre
eventi e mai finestre. **11,1 eventi/ora** (12,2 sul solo tempo di decisione
effettiva), contro un riferimento di letteratura di 0,049/ora: restano due
ordini di grandezza, dichiarati esplicitamente come limite, non nascosti.

**La sessione del 9 settembre** (prima prova con fotogrammi annotati al
secondo, non solo al minuto): il classificatore vede **3 cadute su 4**, la
regola ne segnala **2 su 4**. La caduta persa non è persa dal modello: la
seconda di due cadute ravvicinate (6 secondi) viene vista benissimo (picco
0,800) ma **soppressa dalla sospensione di 30 s** aperta dalla prima. È il
rovescio del risultato di A.8: un meccanismo che riduce i falsi allarmi può
sopprimere un vero allarme, ed è un limite di progetto, non del classificatore.

### A.10 — I contributi (sette, da `Conclusioni.tex`, ora intitolato «Contributi, limiti e sviluppi»)

1. **Protocollo di valutazione corretto e misura del suo costo.** Con dieci
   soggetti, split casuale invece che per soggetto porta l'F1 a **0,0000**
   (mai predetta la classe positiva). Le tre correzioni insieme (split per
   soggetto, scaler fit-on-train, validation separato dal test) portano
   l'F1 a 0,234.
2. **Quantificazione del *viewpoint shift*** — A.7.
3. **Confronto fra architetture a parità di protocollo** — A.6, esito
   contrario all'ipotesi di partenza (la GRU non vince nettamente).
4. **Caratterizzazione end-to-end su hardware edge reale** — A.9. La
   percezione è il collo di bottiglia (85,2%), non il classificatore (14,3%).
5. **Scarto fra precision di laboratorio e falsi allarmi reali.** Precision
   di 0,819 su un insieme bilanciato proiettava 14–125 falsi allarmi/ora;
   misurati **2.735** (finestre) — un ordine di grandezza oltre la previsione,
   costruita apposta per essere scomoda.
6. **Grandezze integrali al posto delle derivate istantanee** — A.5 punto 3.
   L'unico intervento che migliora sia in laboratorio sia sul campo.
7. **Misura di ciò che il dataset di riferimento non distingue** — A.8, il
   contributo che la tesi considera principale.

### A.11 — Il risultato non atteso, i limiti, gli sviluppi

Sezione `Il risultato che non era atteso` (Conclusioni): un domain shift atteso
(cross-dataset) si scompone in 49% taratura di soglia e 51% perdita reale di
capacità discriminativa; solo la seconda parte non si corregge con una soglia.

**Limiti dichiarati esplicitamente:**
- Il carico di allarmi resta due-tre ordini di grandezza sopra il criterio
  clinico (1–2/settimana).
- Cinque cadute simulate non bastano per un richiamo statisticamente solido.
- Consumo elettrico non misurato (serve uno strumento fra alimentatore e
  dispositivo).
- La stima del pavimento non converge su sequenze brevi (< 15 s): limite di
  disponibilità, non di qualità.
- La sospensione di 30 s può sopprimere una seconda caduta ravvicinata (A.9).

**Sviluppi indicati:** taratura della soglia senza etichette da un periodo
iniziale assunto senza cadute; mappa del contesto tramite rilevamento oggetti
(a costo quasi nullo, eseguito solo all'avvio); sessioni più lunghe e in più
abitazioni con partecipanti anziani; sintesi di punti di vista per
riproiezione dello scheletro; ensemble di architetture; ricerca di
iperparametri.

### A.12 — Come si è arrivati a questo: v2 → v5, e perché **non è stato solo il dt**

Questa è la domanda che hai posto, ed è una premessa da correggere: **non è
vero che da v2 a v5 sia cambiato solo il ∆t**. Sono cambiate tre cose
distinte, in tre momenti distinti, verificate sui file del progetto:

**v2 → v3 (6 settembre) — non riguarda il tempo, riguarda le grandezze e il
dataset.**
- `A3_h_pavimento` **non esisteva** nel motore geometrico (32 grandezze, non
  33): il DTW non poteva sceglierla nemmeno volendo, mentre la tesi già
  dichiarava installata una configurazione che la conteneva. Corretto: la
  grandezza torna, con stima **causale** (non più adattata sull'intero
  archivio a posteriori, che sul dispositivo sarebbe stato impossibile).
- Lo stimatore di posa era **unico per tutte e 220 le riprese** invece che
  uno per ripresa: le feature dipendevano dall'ordine di estrazione.
- **218 → 220 registrazioni**: due riprese mancavano per un errore nel nome
  del file originale, non per un problema di dati.
- Effetto misurato: l'escursione fra le cinque architetture non a grafo passa
  da 0,066 (v2) a 0,045 (v3); la correlazione di Spearman fra la classifica
  v2 e quella v3 vale **−0,03** (nulla) — la LSTM passa da prima a quinta, la
  foresta da ultima a terza. **Stessi soggetti, stesso protocollo, stessa
  soglia: cambia solo come sono calcolate le feature**, e la classifica si
  rimescola per intero.

**v3 → v4 (8 settembre) — il dt istantaneo, e non ha contato.**
Le derivate istantanee sono state ricalcolate con il ∆t vero per fotogramma
invece che assunto. L'effetto **non è distinguibile dal caso** (t = −1,15
contro un critico di 2,262): delle 12 colonne selezionate, 8 sono integrali
(non si dividono per dt), 2 statiche, solo 2 derivate — e il DTW le aveva già
relegate in fondo alla classifica. Il fold che la correzione avrebbe dovuto
aiutare di più **peggiora**.

**v4 → v5 (9 settembre) — il buffer degli integrali diventa una durata, e qui
sì, è "il dt".**
`K_INTEGRALI=31` è un conteggio di fotogrammi: 31 fotogrammi durano 1,72 s a
18 fps ma **4,27 s** alla cadenza reale della board (7,26 fps). Il buffer ora
conserva secondi, non campioni. A 18 fps il motore produce valori **identici
bit per bit** (scarto 0,000e+00): il fix non tocca nulla di ciò che il
Capitolo 3 già raccontava sui dati di sviluppo. A 9 e 7,26 fps cambiano solo
le **9 colonne integrali** su 33.

**v5 = v6_220**, verificato identico su tutte le colonne numeriche: è una
riestrazione di controllo, non una sesta versione.

**In sintesi:** un cambiamento nella *rappresentazione* (v2→v3, altezza dal
pavimento + dataset completo) ha spostato la classifica delle architetture
più di quanto l'abbia mai spostata un cambio di architettura; un cambiamento
nel *tempo* (v3→v4→v5) non ha contato in laboratorio e conta solo quando la
cadenza reale si allontana molto da quella nominale — che è esattamente il
caso della board, non quello dei dati di sviluppo.

**Un difetto di coerenza reale, trovato e già corretto (23/9):** per un po' il
confronto fra le sei architetture leggeva **cinque risultati da v2 e uno
(il grafo) da v5** — due campagne diverse mescolate nella stessa tabella. La
tabella di A.6 legge oggi v5 per tutte e sei.

### A.13 — Difetti strutturali trovati e corretti in questa sessione

Riguardando tutto il Cap5 dall'inizio alla fine sono emersi due difetti di
struttura, non di contenuto: due `\subsection` erano vuote perché
l'intestazione successiva era stata scritta subito dopo senza spostare il
testo — «Costo computazionale» seguiva da «Stabilità termica» senza una riga
in mezzo, e tutto il paragrafo sul costo per fotogramma finiva sotto
l'intestazione sbagliata; stessa cosa fra «Motivazione della valutazione in
campo» e «Protocollo delle sessioni domestiche». Corretti spostando ciascuna
intestazione al punto in cui il suo tema comincia davvero. Trovata e saldata
anche una frase spezzata in due chiusure diverse (sulla ripartizione
88,4%/5,8% della catena accelerata). Aggiunta una frase che mancava: perché il
conteggio di campo passa da dodici blocchi iniziali a nove sessioni aggregate
(quattro erano prove di pochi minuti, sotto la soglia utile per una stima
oraria).

### A.14 — Che cosa resta aperto

- **Titolo della tesi**: `Frontespizio.tex` ha ancora il titolo di lavoro
  ("Fall detection su edge device: analisi sperimentale del compromesso fra
  accuratezza e costo computazionale"). Proposta più coerente con quanto
  effettivamente fatto, mai confermata: *"Rilevamento di cadute da posa su
  dispositivo edge: che cosa sopravvive dal laboratorio all'ambiente
  domestico"*.
- **Due citazioni bibliografiche mancanti**: `HO` (tredici occorrenze, la
  rassegna portante del Capitolo 2, "Hoang et al." — nessuna voce Hoang
  esiste in bibliografia) e `LI` (una occorrenza, Cap2). Servono i riferimenti
  veri: indovinarli sarebbe falsificarli.
- **Consumo elettrico**: mai misurato, serve uno strumento fra alimentatore
  e dispositivo.
- **`parita_frame_pc.npz`** non confrontato con le due colonne installate più
  di recente (`A2_testa_rel_y`, `A3_caviglie_rel_y`).

---

## PARTE B — Presentazione di 15 minuti

Quindici minuti = circa 10-12 slide, un minuto e mezzo l'una salvo le due
centrali. La regola guida: **un'idea per slide, un numero per idea**. Non
leggere le tabelle intere: dai il numero che decide, il resto sta ai lucidi.

### Scaletta con tempi

| # | Minuti | Slide | Che cosa dire (l'essenziale, non il copione) |
|---|---|---|---|
| 1 | 0:00–1:00 | Titolo | Nome, relatore, una frase: «rilevamento di cadute da video su un dispositivo da 100€, senza mandare immagini fuori casa». |
| 2 | 1:00–2:30 | Il problema | 54% delle cadute in casa; sistemi indossabili o telecamere che mandano dati fuori. La scelta: video locale su edge. |
| 3 | 2:30–4:00 | Le tre domande | RQ1 architettura, RQ2 generalizzazione, RQ3 dispositivo reale. Questa slide è la mappa di tutto il resto — tornaci alla fine. |
| 4 | 4:00–6:00 | La pipeline | Un disegno solo: video → MediaPipe (33 landmark) → tre rappresentazioni geometriche → grandezze integrali → selezione → classificatore → regola d'allarme. Usa `fig_pipeline_en.png`. |
| 5 | 6:00–7:30 | RQ1: le architetture | La tabella di A.6, ma di' solo: «sei architetture, scarto 0,032, meno della metà della variabilità fra due persone: **l'architettura non è la variabile che conta**». |
| 6 | 7:30–9:30 | RQ2: che cosa non sopravvive | Il numero del *viewpoint shift* (0,422 di F2 perso) e la ragione geometrica in una frase. Poi il risultato principale: **0,055 in laboratorio, un fattore 52 in casa** — usa `fig_configurazioni_en.png`. |
| 7 | 9:30–11:30 | RQ3: sul dispositivo | 100€, 7,3 fps, 297 MB su 5.923 (5%), 79,5°C stabile. Poi il numero onesto: **11,1 eventi/ora contro 0,049 di letteratura** — dillo senza attenuarlo, è un limite dichiarato e la tesi ne spiega la causa (percezione all'85% del tempo). |
| 8 | 11:30–12:30 | Il caso della sospensione | Una slide sola, la sessione del 9 settembre: il classificatore vede 3 cadute su 4, la regola ne segnala 2. Motivo: la sospensione anti-doppio-allarme sopprime una caduta vera che arriva 6 secondi dopo la prima. Buona domanda-trappola, arriva sempre: preparati a spiegarla in 20 secondi. |
| 9 | 12:30–14:00 | Conclusione | Le tre risposte in tre frasi: l'architettura pesa poco; ciò che si guadagna in laboratorio può non guadagnare nulla in casa (o peggio); le risorse bastano, il carico di allarmi no ancora. Il filo che le lega: quasi tutto ciò che determina il comportamento sta *fuori* dal classificatore. |
| 10 | 14:00–15:00 | Sviluppi e chiusura | Due righe sugli sviluppi (taratura senza etichette, rilevamento del contesto) e ringraziamenti. |

### I dieci numeri da avere a mente, senza guardare gli appunti

1. **220** registrazioni, 10 soggetti, UP-Fall.
2. **33** grandezze candidate → **12 o 13** selezionate dal DTW.
3. **0,857 ± 0,089** F2 della GRU (migliore), scarto fra architetture **0,032**.
4. **0,422** di F2 perso passando alla vista frontale rialzata.
5. **0,055** in laboratorio contro **un fattore 52** in casa (il risultato
   principale).
6. **100 €**, **7,3 fps**, **297 MB / 5.923 MB (5%)**, **79,5 °C**.
7. **11,1 eventi/ora** misurati contro **0,049/ora** di letteratura.
8. **44,8×**: perché si contano eventi e non finestre.
9. **3 cadute su 4 viste, 2 su 4 segnalate** (sessione del 9 settembre).
10. **14,3%** il costo del classificatore sul tempo totale — la percezione
    (MediaPipe) è il collo di bottiglia, non il modello.

### Le domande più probabili, e la risposta in due frasi

**«Perché la Random Forest e non un modello neurale, se le differenze sono
piccole?»**
Perché a parità di prestazione conta il costo di deployment: niente
TensorFlow sul dispositivo, addestramento più rapido, e le differenze fra
architetture (0,032) sono comunque sotto la variabilità fra soggetti.

**«11 falsi allarmi l'ora non sono troppi per un uso reale?»**
Sì, e lo dichiariamo: restano due-tre ordini di grandezza dal criterio
clinico. Il contributo non è aver risolto il problema, è averlo **misurato
onestamente** — il benchmark di laboratorio lo avrebbe nascosto.

**«Perché il modello vede la caduta e il sistema non segnala l'allarme?»**
È il caso della sospensione (slide 8): la regola anti-doppio-allarme, pensata
per non ripetere la notifica sullo stesso evento, tratta due cadute vicine nel
tempo come una sola. È un limite della *regola*, non del *modello* — e lo si
vede solo perché lo si è misurato su una sessione con fotogrammi annotati al
secondo.

**«Il dataset UP-Fall non è troppo diverso da una casa vera?»**
Esattamente il punto della tesi: le prestazioni di laboratorio non prevedono
quelle in casa (0,055 contro un fattore 52), ed è per questo che il lavoro
include nove sessioni domestiche vere, non solo il benchmark.

**«Quanto è costato il passaggio dal laboratorio al dispositivo?»**
Non nell'architettura (RQ1: poco), ma nella stima di posa: MediaPipe
sottocampionato a 9 fps batte YOLOv8 a piena velocità di 0,175 di F2. La
scelta dello stimatore conta 5,3 volte più del frame rate.

**«Che cosa fareste con più tempo?»**
Tarare la soglia senza etichette da un periodo iniziale assunto senza cadute,
e un rilevamento del contesto (mobili) quasi gratuito perché eseguito solo
all'avvio — risponderebbe al falso positivo dominante, la persona sdraiata su
un divano.

### Errori da non fare in presentazione

- Non dire "26,5 fps": è il valore della catena **accelerata mai adottata**,
  ritirato. Il valore vero e installato è **7,3 fps**.
- Non dire "5,8% il costo del classificatore": stesso motivo, il valore
  corretto misurato in esercizio è **14,3%**.
- Non presentare l'F2 di laboratorio come garanzia di funzionamento in casa:
  è precisamente il punto che il lavoro smentisce.
- Non confondere DTW-12 (configurazione delle sessioni di agosto) con
  DTWH-13 (installata la sera del 9 settembre, con l'altezza dal pavimento):
  se una domanda chiede "quante grandezze usa il sistema", la risposta onesta
  è "dipende da quale sessione — la versione con l'altezza dal pavimento è
  quella più recente e quella raccomandata".

---

## PARTE C — Spiegazione a voce, ~20 minuti (tesi + progetto + codice)

Scritta il 2 ottobre 2026, su richiesta esplicita: raccontare tutto il lavoro
— non solo i risultati, anche il percorso e le scelte — in una forma che si
possa dire a voce in circa venti minuti, prima di ridurlo alla presentazione
a slide della Parte D. Incorpora le indicazioni della lettera del relatore
del 14/9 (`Risposta alla mail del 14_09_2026.md`): le domande di ricerca
vanno anticipate, i requisiti vanno legati a una metrica misurabile, e il filo
conduttore è **quanto delle prestazioni da benchmark sopravvive quando si
tolgono, una alla volta, le semplificazioni del laboratorio**.

Diviso in sei blocchi, con il tempo indicativo di ciascuno. Non è un copione
da leggere parola per parola — è la sostanza, nell'ordine in cui va detta.

### C.1 — Il problema e perché (≈2 min)

Si parte dal fatto clinico: le cadute sono la prima causa di trauma grave
negli anziani, la maggior parte avviene in casa, e il tempo che passa fra la
caduta e il soccorso conta quanto l'evento stesso — più tempo a terra,
peggiore l'esito. Da qui il bisogno di rilevazione automatica.

I sistemi esistenti hanno due famiglie di limiti opposti: gli **indossabili**
richiedono che la persona se li ricordi (un anziano con decadimento cognitivo
può dimenticarli o rifiutarli), i **sensori ambientali o le telecamere
RGB classiche** o coprono poco o pongono un problema di riservatezza enorme
— mandare in rete il video di una persona a casa propria, in un momento di
vulnerabilità.

Questa tesi costruisce una terza via: un sistema che **vede** da una
telecamera RGB economica, ma non manda **mai** un fotogramma fuori
dall'abitazione — estrae la posa del corpo con MediaPipe e lavora da quel
momento in poi solo su numeri (coordinate di landmark, angoli, velocità), mai
più sui pixel. E lo fa girare su un dispositivo edge da un centinaio di euro,
non su un server.

Questo è già un punto da dire esplicitamente, perché il relatore lo ha
sottolineato: **non si dichiara il problema risolto** ("privacy-preserving"
come se i dati di posa fossero automaticamente anonimi — non lo sono, una
sequenza di movimento può ancora essere identificativa). Si dichiara che si
**riduce la quantità di informazione visuale identificabile disponibile agli
stadi successivi**. È una formulazione più onesta e più difendibile.

### C.2 — Le domande di ricerca (≈2 min)

Il lavoro non è "ho costruito un classificatore di cadute e funziona".
È organizzato attorno a tre domande precise, e va detto subito, perché è la
mappa di tutto quello che segue:

- **RQ1** — a parità di rappresentazione del movimento e di protocollo di
  valutazione, quanto conta davvero l'architettura del classificatore?
- **RQ2** — quanto delle prestazioni ottenute in condizioni controllate
  (stesso soggetto visto in training, stessa geometria di ripresa, stesso
  dataset) sopravvive quando queste condizioni cambiano una alla volta?
- **RQ3** — la pipeline completa può girare in continuo su un dispositivo
  edge a basso costo, con una latenza e un carico di falsi allarmi
  accettabili?

La seconda domanda in particolare si scompone in cinque forme concrete di
**domain shift**, ognuna misurata in un punto diverso della tesi: cambio di
**soggetto** (LOSO), cambio di **punto di vista** della telecamera, cambio di
**frame rate**, cambio di **dataset** (trasferimento esterno), cambio di
**ambiente** (dal laboratorio alla casa vera). Ogni forma toglie una
condizione favorevole tipica del benchmark. È lo scheletro concettuale che
tiene insieme i Capitoli 4 e 5.

### C.3 — Come funziona il sistema: la pipeline (≈5 min)

Si parte dal dataset: **UP-Fall**, pubblico, dieci soggetti, 220
registrazioni, due telecamere (laterale e frontale rialzata), 116.362
fotogrammi, posa valida nel 92,3% dei casi. Si useranno tutte le
registrazioni disponibili, niente scartato.

Poi la pipeline, passo per passo — qui conviene disegnarla mentre si parla,
non solo elencarla:

1. **Stima della posa.** MediaPipe Pose estrae 33 punti del corpo per
   fotogramma. È stato confrontato con un'alternativa (YOLOv8-pose, più
   persone contemporaneamente, ma solo 2D): MediaPipe vince nettamente sulla
   qualità della posa, e questo risultato torna più avanti quando si parla
   del dispositivo.
2. **Tre rappresentazioni geometriche**, tutte calcolate dagli stessi
   landmark ma con logiche diverse: una basata su un'ellisse di covarianza
   (quanto è "allungata" e inclinata la nuvola di punti del corpo), una sul
   vettore tridimensionale del tronco nello spazio, una centrata sul bacino
   e normalizzata sulla lunghezza del tronco — quest'ultima è quella più
   ricca, con nove grandezze corporee più la stima dell'altezza dal
   pavimento.
3. **Grandezze integrali.** Qui c'è una scelta metodologica importante: le
   derivate istantanee (velocità, variazioni frame-a-frame) sono rumorose.
   Si è quindi introdotta una famiglia di grandezze accumulate su una
   finestra mobile — quanto il tronco si è spostato, quanta strada ha fatto
   il bacino, di quanto è sceso — molto più stabili nel tempo. È l'unico
   intervento della tesi che migliora **sia** in laboratorio **sia** sul
   campo, e va detto con questa enfasi.
4. **Selezione delle feature con DTW.** Da 33 grandezze candidate si sceglie
   un sottoinsieme usando il *dynamic time warping* per misurare quanto bene
   ogni grandezza separa una caduta da un'attività normale, con un criterio
   robusto che richiede che la separazione tenga su entrambe le telecamere,
   e un filtro che toglie le grandezze troppo correlate fra loro. Si arriva
   così a 12 o 13 grandezze finali.
5. **Finestre temporali** di 22 campioni, con un passo di 2, date in pasto al
   classificatore.
6. **Classificatore.** Qui si inserisce la prima research question: sei
   architetture diverse sono state confrontate a parità di tutto il resto —
   rappresentazione, finestre, soglia, protocollo di split.
7. **Regola di allarme.** L'uscita del classificatore è una probabilità per
   finestra, non un allarme. Serve una regola che trasformi quella sequenza
   di probabilità in un evento: soglia di decisione, un numero minimo di
   finestre consecutive sopra soglia prima di dichiarare l'allarme
   (persistenza), e un periodo di sospensione dopo un allarme per non
   ripetere la stessa notifica. Questa regola torna, in modo inatteso, anche
   nei limiti del sistema (si vedrà in C.5).

### C.4 — Il protocollo sperimentale e i risultati in condizioni controllate (≈5 min)

Prima di mostrare risultati, va detto **come** sono stati ottenuti, perché è
un punto che il relatore ha chiesto di rendere esplicito: tutto ciò che
"impara qualcosa dai dati" — normalizzazione, selezione delle feature, scelta
della soglia — è calcolato **solo** sui soggetti di training/validation,
**mai** sul soggetto lasciato fuori per il test (LOSO, leave-one-subject-out,
dieci fold). Mescolare le due cose produrrebbe un risultato falsamente
ottimistico, ed è un errore facile da fare per chi non ci fa attenzione.

Con questo protocollo:

- **RQ1 — il confronto fra architetture.** GRU, LSTM, CNN 1D, Transformer,
  Random Forest, rete su grafo: lo scarto tra le cinque architetture non a
  grafo è di 0,032 di F2 — meno della metà della variabilità naturale che si
  osserva passando da un soggetto all'altro con la stessa identica
  architettura (0,089). Conclusione: **l'architettura del classificatore non
  è la variabile che decide le prestazioni del sistema**. È un risultato che
  va controcorrente rispetto all'aspettativa iniziale, ed è onesto dirlo
  così.
- **RQ2 — il cambio di punto di vista.** A parità di soggetto, caduta e
  istante, passare dalla vista laterale a quella frontale rialzata costa
  0,422 di F2 — una perdita enorme, con una causa geometrica precisa: una
  telecamera dall'alto comprime la rotazione del tronco attorno al proprio
  asse ottico, quindi il segnale che il sistema usa per riconoscere la
  caduta si appiattisce. Allenando il modello su entrambe le viste insieme si
  recupera il 58% del divario.
- **Il risultato che la tesi considera il più importante.** Confrontando la
  rappresentazione di partenza con quella finale (con le grandezze integrali
  e dei controesempi raccolti in ambiente domestico), in laboratorio la
  differenza è di soli 0,055 di F2 — dentro la variabilità tra soggetti,
  quindi non dichiarabile come miglioramento reale. Ma sui dati di campo, la
  stessa differenza produce un **fattore 52 sui falsi allarmi**. Il benchmark
  da laboratorio non solo non distingue le due configurazioni: le mette
  **nell'ordine sbagliato**. Questo è il punto centrale da trasmettere:
  un buon numero su un benchmark pubblico non garantisce nulla sul
  comportamento reale.
- **Il trasferimento a un dataset esterno** (UR-Fall) mostra un calo di
  prestazioni che si scompone in due parti quasi uguali: metà è semplice
  scaratura della soglia di decisione (si corregge ricalibrando), metà è
  perdita reale di capacità discriminativa (non si corregge con una soglia).
  È importante separarle, perché solo la seconda è un problema di
  generalizzazione vero.

### C.5 — Il dispositivo edge e la validazione in ambiente domestico (≈4 min)

Qui si risponde a RQ3. Il dispositivo è una **Radxa ROCK 4D** (circa 100 €),
con MediaPipe sulla CPU a una cadenza misurata di 7,3 fotogrammi al secondo
in esercizio. Numeri chiave: il costo per fotogramma si ripartisce
all'85,2% sulla stima della posa e solo al 14,3% sul classificatore — cioè
**il collo di bottiglia è la percezione, non il modello**, coerente con la
risposta a RQ1 (l'architettura conta poco, quindi anche il suo costo conta
poco). Memoria: il picco d'uso è il 5% di quella disponibile. Temperatura:
si stabilizza, nessun calo di prestazioni per surriscaldamento osservato in
una prova di 4,59 ore continue.

È stata anche scartata un'alternativa più veloce (YOLOv8-pose sulla NPU, a
piena velocità): nonostante sia più rapida, perde 0,175 di F2 rispetto a
MediaPipe anche sottocampionato — cambiare stimatore di posa costa più che
dimezzare il frame rate.

Poi la parte più scomoda e più onesta: la validazione in **nove sessioni
domestiche reali**, quasi 15 ore, due abitazioni diverse. Il sistema misura
11,1 eventi (falsi allarmi) all'ora, contro un riferimento di letteratura di
0,049 all'ora per un sistema indossabile — due ordini di grandezza di
differenza. Questo **non viene nascosto**: viene dichiarato esplicitamente
come limite, e se ne spiega la causa (l'89% del tempo di elaborazione va alla
percezione, non c'è margine per renderla più accurata senza cambiare
hardware).

Infine un caso specifico, perché è il tipo di domanda che arriva sempre in
discussione: nella sessione del 9 settembre, l'unica con fotogrammi annotati
al secondo (non solo al minuto), il **classificatore** riconosce 3 cadute su
4, ma la **regola di allarme** ne segnala solo 2. La causa: due cadute
simulate a 6 secondi di distanza, e la sospensione di 30 secondi aperta dalla
prima impedisce alla regola di generare un secondo allarme per la seconda —
anche se il classificatore l'ha vista perfettamente. È un limite della
**regola**, non del modello, ed è il rovescio esatto del risultato di prima:
un meccanismo pensato per ridurre i falsi allarmi può, in certi casi,
sopprimere un allarme vero.

### C.6 — Discussione, contributi, limiti, sviluppi (≈2 min)

Si chiude tornando alle tre domande di partenza, in tre frasi:

- L'architettura del classificatore **pesa poco**, a parità del resto.
- Ciò che si guadagna in laboratorio **può non guadagnare nulla, o addirittura
  peggiorare**, quando si passa a un ambiente reale — ed è per questo che la
  tesi non si ferma al benchmark.
- Le risorse del dispositivo edge **bastano**; il carico di falsi allarmi
  **non ancora**, ed è dichiarato come tale.

Il filo che le lega tutte e tre è lo stesso: **quasi tutto ciò che determina
il comportamento reale del sistema sta fuori dal classificatore** — nella
stima della posa, nel punto di vista della telecamera, nell'ambiente, nella
regola di aggregazione degli allarmi. È il messaggio scientifico complessivo
che il relatore ha chiesto di rendere esplicito, e non lasciare che il
lettore (o la commissione) debba ricostruirlo da solo.

Si chiude con i limiti dichiarati (il carico di allarmi resta lontano dal
criterio clinico; solo cinque cadute simulate annotate con precisione,
insufficienti per un richiamo statisticamente solido; il consumo elettrico
non è stato misurato) e due sviluppi concreti: una taratura della soglia
senza etichette, usando un periodo iniziale assunto privo di cadute, e un
riconoscimento del contesto (es. la presenza di un divano) quasi gratuito
perché eseguito solo all'avvio, per attaccare il falso positivo più frequente
osservato sul campo.

---

## PARTE D — Presentazione di 12 minuti, 18 slide (modello "Petrilli")

Scritta il 2 ottobre 2026. Ricalca la struttura della presentazione allegata
come modello (`Presentazione_Tesi_Magistrale_Niccolò_Petrilli.pdf`) —
motivazione → bisogno → obiettivo → requisiti di design → panoramica del
sistema → sottosistemi → validazione → conclusioni — non il suo contenuto
(quella tesi è su una patch aptica per il melanoma, completamente estranea).
La forma viene mantenuta: **una slide, un'idea, una frase a effetto in corsivo
in fondo**, come nel modello.

**Lingua: italiano** (deciso il 2 ottobre). Il mazzo esiste già, costruito e
pubblicato: <https://claude.ai/artifact/6jPzTbLobAuYv18HiaJJdj> — 18 slide
16:9, con le note del relatore in ogni slide (tempo, che cosa dire, che cosa
NON dire, domande probabili). Da lì si scarica in PowerPoint o PDF.

**Scelte grafiche:** fondo chiaro `#FAF8F5` (variante `#F0EDE7` per le slide
di respiro), testo `#1C2430`, accento cremisi `#9B1B30` (richiama il rosso
UNISI del modello), secondario foglia di tè `#2E7D8C`. Due caratteri: Rubik
per i titoli, IBM Plex Sans per il testo. Due sole slide a fondo pieno: la 2
(aggancio, fondo scuro) e la 18 (chiusura). Numero di pagina in basso a
destra, frase a effetto in corsivo in basso a sinistra, come nel modello.

### Scaletta definitiva, con le immagini decise

| # | Tempo | Slide | Immagine | Che cosa deve restare |
|---|---|---|---|---|
| 1 | 0:15 | Copertina | — | Titolo, candidata, relatore, data. Non si commenta. |
| 2 | 0:45 | Le cadute, e perché contano | — (tre riquadri numerici su fondo scuro) | 1ª causa di trauma grave · 54% in casa · **il tempo a terra** |
| 3 | 0:40 | Tre famiglie di soluzioni, tre limiti diversi | **3 illustrazioni 3D isometriche** (rifatte 2/10): pendente su laccio · sensore a soffitto con cono di rilevamento · angolo di stanza con telecamera, omino e lucchetto | Indossabile = compliance; ambientale = non distingue cadere da sdraiarsi; la terza via |
| 4 | 1:00 | Obiettivo e domande di ricerca | — (tre schede RQ1/RQ2/RQ3) | **La mappa di tutto il resto.** Richiesta esplicita del relatore |
| 5 | 1:00 | Requisiti, e la grandezza che li misura | — (tabella requisito → metrica → dove) | Falsi positivi per finestra ≠ allarmi all'ora |
| 6 | 1:00 | La pipeline | `fig_pipeline_en.png` | Dopo il 2° stadio non esistono più immagini nel sistema |
| 7 | 0:35 | Dal video alla posa | `fig_landmark_mediapipe_en.png` | 33 landmark; il pixel si ferma qui |
| 8 | 0:45 | Tre modi di descrivere la stessa posa | `fig_rappresentazioni_en.png` (A1+A2+A3 affiancate) | A3 normalizza sulla lunghezza del tronco |
| 9 | 0:40 | Dalle derivate alle grandezze integrali | `fig_striscia_en.png` | ρ₁ da 0,22–0,54 a 0,82–0,99; l'unico intervento che migliora ovunque |
| 10 | 0:35 | Dalla finestra all'allarme | `fig_sessione_en.png` | Soglia 0,50 → 5 finestre → 30 s; **44,8 finestre per evento** |
| 11 | 0:45 | Il dispositivo | **1 illustrazione 3D isometrica** (rifatta 2/10): webcam e scheda Radxa ROCK 4D già collegate dal cavo | ~100 € · 7,3 fps · 5% memoria · 79,5 °C. NPU scartata di proposito |
| 12 | 0:35 | Come si valuta: un soggetto fuori alla volta | — (schema LOSO a chip colorati) | Nulla di ciò che impara dai dati tocca il soggetto di test |
| 13 | 1:00 | **RQ1** — Sei architetture | `fig_architetture_en.png` | 0,032 fra modelli contro 0,089 fra persone |
| 14 | 1:10 | **RQ2** — Dal laboratorio alla casa | — (tabella 5 configurazioni + due numeri giganti) | **0,055 in laboratorio → 52× in casa.** Striscia in fondo: −0,422 di vista |
| 15 | 1:10 | **RQ3** — Quindici ore in due case | `fig_sessione_v5_andamento_en.png` | 85,2/14,3% · 11,1 eventi/ora contro 0,049 · 3 viste, 2 segnalate |
| 16 | 0:45 | Che cosa questo lavoro non dimostra | — (cinque limiti, barra cremisi) | Si dice senza scusarsi: è una slide di forza |
| 17 | 0:45 | Conclusioni e sviluppi | — (tre risposte + elenco sviluppi) | Quasi tutto sta **fuori dal classificatore** |
| 18 | 0:10 | Grazie | — | Poi fermarsi. Le domande probabili sono nelle note |

### Il conto dei tempi è onesto: 13:35, non 12:00

Sommati, i tempi delle note fanno **13 minuti e 35 secondi**. Per rientrare nei
dodici servono 95 secondi, e vanno tolti dalle slide di metodo, non dai
risultati:

| Slide | Da | A | Risparmio |
|---|---|---|---|
| 5 · Requisiti | 1:00 | 0:30 | 30 s |
| 6 · Pipeline | 1:00 | 0:45 | 15 s |
| 8 · Rappresentazioni | 0:45 | 0:30 | 15 s |
| 7 · Posa | 0:35 | 0:25 | 10 s |
| 12 · Protocollo | 0:35 | 0:25 | 10 s |
| 9 · Integrali | 0:40 | 0:30 | 10 s |

Totale risparmiato 90 s → **12:05**. Le slide 13, 14 e 15 (i tre risultati) e
la 16 (i limiti) **non si toccano**: sono il contenuto scientifico.

### Le immagini, nel dettaglio

**Rifatte il 2 ottobre in 3D isometrico ombreggiato** (tre facce colorate per
solido + ombra sfocata, lo stile "flat 3D" di Icons8/Streamline — non un
render CAD vero, per quello serve un modellatore come Spline o Blender).
Prima erano icone piatte disegnate a mano in SVG; quella versione resta in
`presentazione_tesi/sorgenti_svg/` e `immagini/versione_precedente_2d/` per
chi vuole ancora modificarla in Inkscape (installato e verificato funzionante
da riga di comando, `inkscape --version` → 1.4.4).

- *Slide 3*, ora **tre vie** invece di due (tassonomia del Cap. 2: wearable /
  ambientale / visione, non più "wearable / telecamera-che-manda-tutto-al-
  cloud"): un **pendente da collo su laccio** (non più uno smartwatch — i
  dispositivi commerciali di rilevamento cadute sono quasi sempre pendenti),
  un **sensore a soffitto** con cono di rilevamento verso il basso montato
  nell'angolo di una stanza, e lo stesso angolo di stanza con **telecamera,
  omino stilizzato e lucchetto**.
- *Slide 11*, non più due immagini affiancate ma **una sola scena**: webcam e
  Radxa ROCK 4D appoggiate sullo stesso piano, collegate da un cavo disegnato
  — risponde a "insieme in 3D" così come richiesto. La Radxa è un
  parallelepipedo verde con header a 40 pin dorati, SoC con dissipatore
  rialzato, moduli di memoria e porte USB/Ethernet sporgenti sul lato destro.

**Due video nuovi, con un omino stilizzato** (nessuna persona reale,
`presentazione_tesi/video/`):

- `omino_caduta.mp4` (2,6 s) — l'omino perde l'equilibrio e cade, con un
  lampeggio cremisi all'impatto. Sostituisce, per la slide 15, le clip vere
  delle sessioni domestiche: quelle restano riservate per la clausola del
  progetto su `sessioni_reali/` (persone identificabili, non da copiare né
  mostrare oltre il repository) — **decisione confermata il 2 ottobre** dopo
  aver posto esplicitamente la domanda.
- `omino_seduto_divano.mp4` (3 s, loop) — illustra il falso positivo più
  frequente sul campo (persona ferma su un divano, escursione del tronco
  93,5° contro 60,7° di una caduta vera). Extra per la slide 9, non nel
  copione a tempo.

Entrambi disegnati frame-per-frame con PIL e assemblati in MP4 con `ffmpeg`
(entrambi già installati sulla macchina, verificati funzionanti).

**Dalla tesi** (già caricate nel mazzo): `fig_pipeline`, `fig_landmark_mediapipe`,
`fig_rappresentazioni`, `fig_striscia`, `fig_sessione`, `fig_architetture`,
`fig_sessione_v5_andamento`. Caricate ma non usate, pronte come **slide di
riserva** per le domande: `fig_viste`, `fig_configurazioni`, `fig_termica`.

**NON caricate nel mazzo online di proposito:** `fig_caduta_board_en.png`
(fotogramma reale con una persona, volto pixelato) e
`sorgenti/inquadratura_board.jpg` (interno di un'abitazione privata).
Restano in locale, già copiate in `presentazione_tesi/immagini/` per chi
preferisce comunque usare la foto reale nella slide 15 invece del video.

**Manca:** una foto della Radxa vera. Nel progetto non esiste. O la scatti tu
alla scheda, o prendi l'immagine prodotto dal sito Radxa; l'illustrazione 3D
della slide 11 funziona comunque da sola.

### Che cosa è nuovo e non sta nella tesi

Nella slide 17 quattro dei sei sviluppi **non sono scritti in nessun
capitolo**: fusione con un sensore audio d'impatto, notifica al caregiver con
escalation, misura del consumo con batteria tampone, studio pilota con
partecipanti anziani. Vanno presentati come proposte, mai come lavoro svolto.
I primi due (taratura della soglia senza etichette, riconoscimento del
contesto) sono invece già nelle conclusioni della tesi.

---

*Fonti: `tesi/Cap1.tex`–`Cap5.tex`, `tesi/Conclusioni.tex`,
`docs/CHANGELOG.md`, `docs/ISSUES.md` (ISS-139, ISS-148, ISS-169),
`docs/EXPERIMENTS.md` (EXP-021, EXP-022, EXP-033, EXP-035),
`pipeline/eventi_sessioni.py`, `deploy_board/sessioni/20260909_v5/LEGGIMI.md`,
`Risposta alla mail del 14_09_2026.md` (lettera del relatore, 14/9/2026),
`Presentazione_Tesi_Magistrale_Niccolò_Petrilli.pdf` (modello di struttura per
la Parte D).*
