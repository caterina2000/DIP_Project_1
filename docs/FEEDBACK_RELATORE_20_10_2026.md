# Correzioni del relatore — prova del 20 ottobre 2026

Discussione il 22 ottobre 2026 (v. [SIMULAZIONE_ORALE.md](SIMULAZIONE_ORALE.md)).
Mecocci ha ascoltato la prova sulle 16 slide della versione corrente
(`Presentazione_Tesi_Magistrale_Caterina_Cerretani (9).pdf`) e ha chiesto un
intervento soprattutto sulla chiusura. Il contenuto tecnico non cambia: va
ricapitolato meglio e spiegato più lentamente in due punti.

---

## 1. Che cosa ha detto, in sintesi

- La presentazione va bene nel contenuto ("ben fatta, pulita"), ma la
  conclusione non ricapitola: chi segue con attenzione ricostruisce il
  percorso, chi segue meno ne ricava solo un elenco di risultati slegati.
  **Manca una slide finale che riassuma in una manciata di frasi che cosa è
  stato fatto, perché, e con quale esito.**
- Il messaggio operativo della tesi — *il benchmark non basta a prevedere il
  comportamento in ambiente reale* — c'è nei dati ma non è mai detto in una
  frase sola. Va reso esplicito nella chiusura.
- In tre slide (RQ2, casa, RQ3) passano tre argomenti importanti uno via
  l'altro e il ritmo è troppo veloce: chi ascolta perde il filo prima
  dell'ultimo. Rallentare in particolare sul passaggio benchmark → casa →
  scheda, spiegando ogni volta *che cosa è stato trovato* prima di passare
  oltre.
- **F2-score non va mai detto senza spiegarlo.** Non tutta la commissione ha
  presente che cos'è: va introdotta la prima volta che compare (slide
  "Dati e protocollo sperimentale") con una riga che dica che cosa misura, non
  solo il nome.
- Spiegare il *perché* delle scelte, non solo il *cosa*: in particolare, il
  motivo per cui si è fatto feature engineering invece di usare
  un'architettura di grandi dimensioni va detto esplicitamente, perché la
  domanda "perché non un Transformer, o un modello visione-linguaggio" può
  arrivare da chiunque in commissione.
- Citare, quando si parla di prestazioni sulla scheda, che il numero (7,3
  fps) va messo in relazione a un termine di paragone — un confronto con la
  letteratura o almeno un giudizio esplicito su cosa serve per riconoscere un
  evento che dura secondi — invece di lasciarlo come cifra isolata.
- Sulla privacy: va precisato che il sistema non elimina il rischio, lo
  sposta. Nessuna analisi di attacco è stata fatta sul nodo; se il nodo non è
  esposto in rete e comunica solo allarmi protetti verso un server, il rischio
  resta ma è ridotto. Non va presentato come "privacy garantita".
- Video/demo dal vivo: facoltativo, non obbligatorio. Se funziona, farlo
  partire *dopo* "Grazie per l'attenzione", non incastrato nella sequenza
  principale — se si inceppa non deve portarsi dietro il resto della
  presentazione. Portare la ROCK con la telecamera in aula, se possibile,
  dà più concretezza di qualunque slide.
- Da controllare prima della discussione: una rapida verifica bibliografica
  sull'uso recente di Transformer/modelli visione-linguaggio per il
  riconoscimento di cadute o attività, perché è il tipo di domanda che Barni
  in particolare potrebbe fare. Il Cap. 2 copre già Transformer e reti a
  grafo *come classificatori* (§2, righe 134, 165-168 di `Cap2.tex`); non
  copre l'uso di un modello visione-linguaggio end-to-end al posto della
  pipeline feature-based — è il buco da coprire prima di rispondere a
  quella domanda specifica.

---

## 2. Azioni concrete, in ordine di urgenza

1. **Scrivere e provare a voce la slide/chiusura ricapitolativa** (testo
   proposto sotto, §3). È l'intervento che il relatore ha chiesto con più
   insistenza.
2. **Aggiungere la riga di spiegazione dell'F2** sulla slide "Dati e
   protocollo sperimentale", dove la metrica compare per la prima volta
   (testo proposto in §6).
3. **Rallentare consapevolmente** nel tratto RQ2 → casa → RQ3: dire
   esplicitamente, prima di passare slide, "questo è quello che succede sul
   benchmark, questo è quello che succede in casa" invece di lasciarlo
   implicito nei numeri.
4. **Preparare la risposta sul perché del feature engineering** (vs.
   Transformer/VLM end-to-end) — testo in §7, da dire a braccio se arriva la
   domanda, o da anticipare nella chiusura stessa.
5. **Preparare la precisazione sulla privacy** (§8) da tenere pronta, non da
   mettere in slide.
6. **Verifica bibliografica rapida** su VLM/foundation model per
   riconoscimento di attività/cadute (15-20 minuti bastano per non arrivare
   impreparata — non serve una review, basta sapere se esiste lavoro recente
   da citare o da escludere esplicitamente).
7. Decidere su video/ROCK fisica in aula — non urgente, ma va deciso prima
   del 22.

---

## 3. Testo proposto per la chiusura ricapitolativa

Da dire prima o al posto dell'attuale passaggio diretto a "Grazie per
l'attenzione". Tempo stimato alla lettura naturale: 45-55 secondi; da
accorciare se il tempo stringe, tagliando dal terzo paragrafo.

> Per chiudere, riprendo in breve il percorso. L'obiettivo era costruire un
> sistema di rilevamento delle cadute il più possibile preservante della
> privacy, capace di girare interamente in locale su un dispositivo a basso
> costo — perché un sistema pensato per restare acceso in casa non può
> mandare video fuori dall'abitazione.
>
> Per arrivarci ho fatto tre cose. Primo, feature engineering: non ho dato il
> video a un modello di grandi dimensioni, perché non è compatibile con
> l'esecuzione locale su un dispositivo da 150 euro — ho definito io tre
> rappresentazioni della posa e dodici grandezze geometriche, cinematiche e
> temporali, selezionate con la DTW come le più discriminanti. Secondo, ho
> confrontato sei architetture di classificazione a parità di feature e
> protocollo: nessuna è risultata significativamente superiore alle altre.
> Terzo, e questo è il punto centrale della tesi, ho misurato cosa succede
> quando il sistema esce dal benchmark: cambiando punto di vista l'F2 scende
> da 0,82 a 0,49, su un dataset esterno scende a 0,63, e in due case vere sono
> emersi errori — persone sedute o sdraiate sul divano scambiate per cadute —
> che sul benchmark non si vedono, perché quelle situazioni lì non ci sono.
>
> Ho corretto il sistema su quegli errori specifici, portando i falsi allarmi
> da 140 a meno di 3 all'ora, e l'ho fatto girare quattro ore e mezzo di
> fila su una scheda Radxa ROCK, senza interruzioni, a 7,3 fotogrammi al
> secondo — sufficiente per un evento che dura secondi.
>
> Il messaggio che porto a casa da questo lavoro è semplice: il benchmark non
> basta. Un sistema valutato solo su un benchmark pubblico può avere
> prestazioni eccellenti sulla carta e comportarsi in modo molto diverso in un
> salotto vero. Per saperlo, va portato fuori dal laboratorio e misurato lì.
> Grazie per l'attenzione.

**Verificato con:** numeri confrontati con le slide 10-13 della presentazione
(F2 GRU 0,857 vs RF 0,825; laterale 0,822 → frontale 0,488; UR-Fall 0,630;
A3 139,9 → A3i+controesempi 2,7 finestre/ora; prova di continuità 4,59 ore,
7,3 fps) e con `docs/DISCORSO_CORRETTO.md`. Non ancora provato a voce con il
cronometro: il tempo stimato è a lettura, non misurato.

## 4. Testo per la slide (non per la voce)

La slide va letta in 10-15 secondi d'occhio, non recitata: solo le parole
chiave, i numeri restano quelli detti a voce con il testo di §3. Proposta,
nello stesso stile delle slide esistenti (titolo + bullet + riga finale in
risalto come nella slide 11):

```
IN SINTESI

Obiettivo
Rilevamento cadute privacy-preserving, interamente on-edge — niente video
fuori dall'abitazione

Come
Feature engineering invece di un modello pesante → 12 feature geometriche,
cinematiche e temporali, selezionate con DTW

RQ1 — Classificatore
6 architetture confrontate, nessun vantaggio significativo
(GRU 0,857 vs RF 0,825)

RQ2 — Generalizzazione
Il benchmark non predice il reale
laterale 0,82 → frontale 0,49 → UR-Fall 0,63 → casa: errori mai visti sul
benchmark

RQ3 — Edge
Radxa ROCK, ~150€, 7,3 fps, 4,59 ore continue senza interruzioni

———————————————————————————————
Il benchmark non basta: va validato fuori dal laboratorio.
```

Posizione: come slide a sé, subito prima di "Grazie per l'attenzione"
(quindi slide 15bis, tra l'attuale 15 "Conclusioni, limiti e sviluppi" e la
16 finale) — oppure dentro la 16 stessa, aggiungendo i bullet sopra la
scritta "Grazie". La 15 attuale resta utile com'è: è il recap per RQ di
limiti e sviluppi, questa nuova slide è il recap "cosa ho fatto e perché",
che la 15 non dà.

**Superato da §4bis: preferire quella versione.** Aggiunge la stessa
ricapitolazione **sostituendo** il contenuto della slide 15 invece di
aggiungerne una — risponde alla stessa richiesta di Mecocci senza allungare
la presentazione, che è uno dei suoi stessi rilievi (il ritmo RQ2→casa→RQ3
già troppo veloce). Questa versione resta come riferimento per il
*contenuto* dei numeri, non più per la collocazione.

### 4bis. Versione preferita — sostituisce la slide 15, non ne aggiunge una

Arrivata da una seconda revisione esterna il 20 ottobre, **verificata**: i
297 MB di picco di memoria (5% dei 6 GB disponibili) sono in
`tesi/Cap5.tex:247` parola per parola; il resto dei numeri coincide con
quanto già verificato in questo file. Due cautele da questa revisione, da
tenere:

- **non trasformare 3/4 (cadute riconosciute il 9 settembre) in un
  F2-score della board** — manca precision/recall completi su quelle
  registrazioni, sarebbe un numero costruito;
- **non dire che 7,3 fps sono "più che sufficienti"** — dire solo che
  permettono l'esecuzione continua nella configurazione provata; la
  sufficienza vera (allarmi, tempestività, cadute mancate) non è stata
  misurata.

**Discorso di chiusura proposto** (alternativo al testo di §3, stessa
funzione, impostato esplicitamente sull'ordine che Mecocci ha chiesto:
obiettivo → come → verifica → PoC → limite):

> In conclusione, l'obiettivo del mio lavoro era sviluppare un sistema di
> rilevamento automatico delle cadute capace di funzionare interamente su
> un dispositivo edge, con un'architettura orientata alla tutela della
> privacy attraverso l'elaborazione locale del video.
>
> Per raggiungere questo obiettivo ho scelto un approccio basato sul
> feature engineering: a partire dalla posa stimata, ho costruito
> descrittori geometrici, cinematici e temporali per fornire al
> classificatore una rappresentazione compatta e interpretabile del
> movimento, anziché richiedergli di apprendere direttamente dal video.
>
> Ho quindi verificato sperimentalmente le prestazioni e la capacità di
> generalizzazione del sistema. L'F2-score, che attribuisce maggiore
> importanza al riconoscimento delle cadute, passa da 0,82 a 0,49
> cambiando il punto di vista della telecamera. Le prove domestiche hanno
> inoltre evidenziato errori poco rappresentati nel benchmark, soprattutto
> in presenza di persone sedute o sdraiate su superfici rialzate.
>
> Infine, ho realizzato un proof of concept funzionante sulla ROCK 4D,
> eseguendo localmente l'intera pipeline a circa 7,3 fotogrammi al secondo,
> con un impiego di memoria inferiore a 300 MB.
>
> Nelle prove domestiche, nella sessione del 9 settembre, il classificatore
> ha riconosciuto tre delle quattro cadute simulate, ma la logica di
> generazione dell'allarme ne ha segnalate soltanto due. Questo evidenzia
> che il comportamento finale dipende dall'intera pipeline, non soltanto
> dal classificatore.
>
> Il lavoro dimostra quindi la fattibilità dell'approccio su un dispositivo
> edge, ma soprattutto che ottenere buone prestazioni su un benchmark
> controllato non è sufficiente a garantire un rilevamento affidabile in un
> ambiente reale.
>
> Restano da affrontare il numero ancora elevato di allarmi e la necessità
> di verifiche indipendenti, su più abitazioni e per periodi continuativi
> più lunghi.

**Slide 15 riscritta** (sostituisce i tre blocchi RQ1/RQ2/RQ3 attuali;
limiti e sviluppi restano come sono, Mecocci li ha già giudicati adeguati):

```
Dalla progettazione al funzionamento reale

Feature engineering
Descrittori compatti e interpretabili del movimento

Generalizzazione
F2 0,82 → 0,49 cambiando vista

Proof of concept edge
7,3 fps, elaborazione interamente locale

Prove sulla board
3/4 → 2/4   cadute riconosciute → allarmi emessi

Il benchmark è necessario, ma non sufficiente a validare il sistema in
ambiente reale.

Limiti: falsi allarmi, poche cadute simulate, due abitazioni.
Sviluppi: dati indipendenti, prove più lunghe, ottimizzazione della pipeline.
```

**Risposte pronte sull'hardware**, costruite sulla tesi (non parole
testuali del relatore, la trascrizione si interrompe prima di quella
parte):

> *"Perché è significativo il risultato di 7,3 fps?"* — È la frequenza
> della pipeline completa sulla CPU della ROCK 4D, non del solo
> classificatore: comprende stima della posa, estrazione delle feature e
> decisione. Dimostra la fattibilità computazionale dell'esecuzione
> locale; la verifica di tempestività e affidabilità richiede dati
> operativi che non ho ancora.

> *"Quali prestazioni di rilevamento sulla board?"* — Nella sessione del 9
> settembre, tre cadute simulate su quattro riconosciute dal
> classificatore, due hanno generato un allarme. Mostra anche il limite
> della regola di persistenza e del tempo refrattario.

> *"La memoria della board era un limite?"* — No: picco misurato 297 MB
> sui 6 GB disponibili, il 5%. Il collo di bottiglia è computazionale, la
> stima della posa su CPU assorbe circa l'85% del tempo.

**Nota onesta su questa fonte:** la seconda revisione dichiara di non aver
potuto leggere la parte finale della registrazione (dove il relatore
comincia a parlare delle domande attese da Barni) e non inventa cosa
direbbe — coerente con quanto già raccolto in questo file da §1 a §9: quella
parte resta da ascoltare, se la registrazione completa diventa disponibile.

---

## 5. Il video che vuole Mecocci

Mecocci l'ha proposto come facoltativo ("non sarebbe malissimo"), non come
richiesta vincolante, con due indicazioni precise: farlo partire **dopo**
"Grazie per l'attenzione" (non dentro la sequenza principale, così se non
parte non si porta dietro il resto), e che l'idea di portare la ROCK vera
con la telecamera in aula gli piace più di qualunque video, perché dà "un
senso di estrema concretezza".

**Attenzione prima di scegliere il materiale — vincolo di privacy.** Il
progetto precedente (`DIP_PROJECT/CLAUDE.md`) è esplicito: le clip intorno
agli allarmi delle sessioni reali, comprese quelle in
`deploy_board/clip_demo/` di questo stesso repository (le cartelle
`evt_0001_092019` e simili), ritraggono familiari identificabili e **non
vanno copiate altrove né pubblicate**. Una proiezione in sede di discussione
— specie se la seduta viene registrata — è una forma di pubblicazione. Prima
di scegliere quale filmato mostrare, va deciso filmato per filmato chi
compare:

- `docs/demo_caduta.mp4` e `docs/demo_divani.mp4` (21 agosto, già usati per
  le miniature `_demo_caduta.png`/`_demo_divani.png`): da verificare chi vi
  compare prima di usarli — se la persona ripresa è solo la candidata, non
  c'è il problema dei familiari; se compaiono i nonni o altri familiari delle
  sessioni in casa, vale la stessa restrizione.
- Le clip in `deploy_board/clip_demo/` e in `deploy_board/riletture/`: da
  **non** usare, sono le stesse coperte dalla restrizione.
- Alternativa che evita del tutto il problema: una **demo dal vivo**, con la
  candidata stessa come soggetto — è anche l'opzione che Mecocci preferisce.
  Serve una prova di funzionamento della ROCK nel giorno/aula della
  discussione (alimentazione, rete se serve, luce sufficiente) fatta
  **prima** del 22, non il giorno stesso.
- Se si preferisce comunque un video pre-registrato e concreto senza usare
  le clip di casa: si può registrare una breve clip nuova, apposita, con la
  sola candidata come soggetto, nei giorni prima della discussione.

**Collocazione pratica:** ultima slide o subito dopo, avviata manualmente,
con un piano B pronto (uno screenshot statico, ad esempio uno dei fotogrammi
già nella slide 14) se il video o la demo dal vivo non partono — in modo da
non perdere tempo in aula a risolvere un problema tecnico.

---

## 6. Riga da aggiungere dove compare per la prima volta l'F2

Sulla slide "Dati e protocollo sperimentale", prima o subito dopo la
formula:

> L'F2-score pesa la recall più della precisione: conta di più trovare le
> cadute vere che evitare qualche falso allarme in più. Per un sistema di
> allarme, perdere una caduta costa più di una segnalazione in eccesso.

---

## 7. Risposta pronta — perché feature engineering e non un modello di grandi dimensioni

> Un Transformer end-to-end sul video grezzo, o un modello
> visione-linguaggio, non è compatibile con l'esecuzione locale su un
> dispositivo da 150 euro come quello che ho usato: sono modelli pensati per
> girare su GPU dedicate, non su una scheda embedded. Per questo ho scelto un
> percorso diverso — stimare la posa con MediaPipe e costruire a mano le
> feature discriminative — che è più leggero e più interpretabile, anche se
> dipende dalla qualità delle grandezze che ho scelto io. Ho comunque incluso
> un Transformer **come classificatore** nel confronto della RQ1, applicato
> alle feature già estratte, non al video: ottiene un F2 di 0,837, comparabile
> alla GRU, non lo supera.

(Nota: completare il punto 6 di §2 — verifica bibliografica — prima di dirla
con sicurezza in commissione se arriva la domanda specifica sui VLM.)

---

## 8. Precisazione da tenere pronta — privacy

> Il sistema non garantisce la privacy in modo completo: non è stata fatta
> un'analisi di attacco sul nodo. Quello che fa è ridurre l'esposizione,
> perché l'elaborazione resta sulla telecamera e dall'abitazione esce solo
> l'allarme, non il video. Se il nodo non è esposto in rete — comunica solo
> con un server tramite messaggi protetti — il rischio residuo è quello del
> server e del canale, non quello dei frame grezzi. È una riduzione della
> superficie d'attacco, non un'eliminazione del rischio.

---

## 9. Originalità delle rappresentazioni A1/A2/A3 — dove dirlo e come

In prova, alla slide "Tre modi di descrivere la stessa posa" (slide 6),
Mecocci ha chiesto esplicitamente se le tre rappresentazioni (l'ellisse di
A1, le coordinate 3D di A2, il riferimento sul bacino di A3) vengono dalla
letteratura o sono state definite dalla candidata, a partire dai soli
landmark grezzi di MediaPipe. La risposta a voce ("l'ho definita io") è
arrivata solo dopo diversi scambi — il punto non era chiaro dal discorso
preparato. Due interventi, non alternativi: uno sulla slide 6 (dove è nata
la domanda), uno in conclusione (ricapitolazione dei contributi, già in §3).

**Alla slide 6**, inserire prima di descrivere A1:

> MediaPipe mi fornisce solo i trentatré landmark grezzi: come raggrupparli
> in queste tre rappresentazioni, e quali grandezze ricavarne, l'ho definito
> io — non sono output della libreria.

**Sulla slide stessa** (non solo a voce), da mettere sotto il titolo, prima
delle tre colonne A1/A2/A3 — così la risposta resta visibile per tutta la
slide, anche se la domanda arriva mentre si è già su A2 o A3:

```
MediaPipe fornisce i 33 landmark grezzi.
Raggruppamento, ellisse (PCA) e grandezze derivate: implementazione propria.
```

Versione più compatta, come sottotitolo unico sotto il titolo della slide:

```
A partire dai soli landmark grezzi di MediaPipe — raggruppamento e
grandezze definiti in questo lavoro
```

E, arrivando ad A1 (il punto esatto della domanda in prova), a voce si
chiude la frase sull'ellisse con:

> ...attraverso un'ellisse che ne descrive la forma e l'orientamento globale
> del corpo, costruita da me con un'analisi delle componenti principali sui
> punti scelti.

Non ripetere la stessa formula per A2 e A3: la frase d'apertura copre già
tutte e tre le rappresentazioni; insistere tre volte suonerebbe ridondante.

**In conclusione**, resta valido il testo di §3 ("volevo costruire un
sistema privacy-preserving, on-edge... per farlo ho fatto feature
engineering, non un modello pesante") prima di passare a RQ1/RQ2/RQ3: lì il
livello è diverso, non la singola rappresentazione ma il disegno
complessivo del lavoro.

**Perché entrambe e non una sola.** La domanda sull'originalità può arrivare
mentre si è ancora sulla slide 6, non necessariamente in fondo: se la
risposta esiste solo nella slide conclusiva, nel momento in cui serve non
c'è.

### 9bis. Perché slide e voce dicono cose diverse, e un esempio per rappresentazione

**Slide vs voce, perché sono separate.** La slide è un'ancora visiva, resta
sullo schermo per tutta la durata della slide: deve reggersi con poche
parole, non con il ragionamento. La voce è dove si fa l'argomento vero —
più lunga, più tecnica, e capace di rispondere nel momento in cui la
domanda arriva, cosa che il testo fisso della slide non può fare. Tutto
sulla slide affolla lo schermo e distrae da quello che si sta dicendo;
tutto solo a voce rischia che, se la domanda arriva dopo essere passati
oltre, la risposta non sia più davanti agli occhi. La slide dice *che è
tua*, la voce spiega *come*.

**Frase di raccordo, a voce**, quando si introduce la slide 6:

> Dai 33 landmark che MediaPipe mi fornisce, ho implementato le tre
> rappresentazioni selezionando per ciascuna un sottoinsieme specifico di
> punti, da cui ho costruito le grandezze geometriche e cinematiche che
> ritenevo più informative per distinguere una caduta da un'attività
> quotidiana — sono le candidate su cui poi la DTW ha scelto le dodici più
> discriminanti.

**Un esempio per rappresentazione**, da `src/geometry.py`, pronto se chiedono
il dettaglio di una grandezza specifica:

- **A1 — ellisse, 7 punti (naso, spalle, anche, caviglie) → 9 grandezze.**
  Covarianza dei 7 punti, poi autovalori/autovettori (`np.cov` +
  `np.linalg.eigh`). *Asse maggiore* = radice del primo autovalore, quanto
  il corpo è disteso lungo la direzione principale. *Inclinazione* = angolo
  dell'autovettore principale, l'orientamento nel piano immagine (verticale
  in piedi, orizzontale a terra). *Allungamento* = asse maggiore su asse
  minore, alto in piedi, basso a terra o seduti. Le tre derivate e la
  velocità del baricentro misurano quanto rapidamente queste grandezze
  cambiano — è lì che si vede la transizione, non nel valore statico.
- **A2 — mondo 3D, 5 punti (naso, spalle, anche) → 5 grandezze.** Vettore
  tronco = punto medio spalle meno punto medio anche, nel riferimento world
  di MediaPipe. *Angolo_tronco* = angolo rispetto alla verticale via
  prodotto scalare: 0° tronco verticale, verso 90° orizzontale. Da lì la
  velocità angolare del tronco e la velocità della testa in metri al
  secondo — l'unica grandezza con un'unità fisica vera, perché i world
  landmark stimano una scala reale.
- **A3 — bacino, punti su spalle/anche/ginocchia/caviglie, normalizzati per
  la lunghezza del tronco.** Esempio: *testa_rel_y* = quanto la testa è più
  alta del bacino in lunghezze di tronco, vicino a 1 in piedi, vicino a 0 a
  terra. *A3_h_pavimento* (ISS-139) è l'unica che dice non "che posa ha il
  corpo" ma "a che altezza dal pavimento si trova": distingue una persona
  seduta sul divano, posa simile ma altezza diversa, da una a terra.

---

### 9ter. Verifica sul codice — cosa è davvero suo

Controllato `src/geometry.py` il 20 ottobre per rispondere con certezza, non
a memoria, alla domanda "l'hai definita tu o viene da qualcosa di
esistente". MediaPipe Pose fornisce **solo** i 33 landmark grezzi (coordinate
nel piano immagine, più una stima in un riferimento "world" centrato sulle
anche). Tutto il resto è implementato nel modulo:

- **A1 (ellisse):** sette punti scelti dalla candidata (naso, spalle, anche,
  caviglie — il codice documenta anche il bug per cui due script
  precedenti ne usavano un numero diverso, poi corretto). L'ellisse è
  calcolata come autovalori/autovettori della matrice di covarianza di quei
  punti (`np.cov` + `np.linalg.eigh`), non da una funzione di libreria.
  **Distinzione onesta da fare in aula:** la PCA come tecnica è standard,
  non è un'invenzione della candidata; la scelta dei punti, l'applicazione a
  questo problema e il codice che la implementa sono suoi.
- **A2 (mondo 3D):** angolo del tronco dal prodotto scalare col vettore
  verticale nel riferimento world. Due grandezze (velocità del bacino) sono
  state tolte dopo aver misurato che erano rumore numerico puro — deviazione
  standard di 0,00003 m, documentata nel codice con il numero esatto.
- **A3 (bacino):** coordinate centrate sul bacino, normalizzate per la
  lunghezza del tronco; l'altezza dal pavimento reintrodotta il 2026-09-06
  dopo ISS-139.
- **I tre descrittori temporali (escursione, percorso, discesa):**
  **interamente originali, nessuna funzione di libreria li calcola.** Buffer
  circolare per bacino scritto dalla candidata, finestra basata su durata e
  non su conteggio di campioni, tre formule proprie: escursione = max−min
  dell'angolo nella finestra; percorso = somma delle distanze euclidee tra
  punti consecutivi, normalizzata; discesa = scarto dal massimo recente. Il
  modulo motiva anche la scelta di accumulare invece di derivare, con numeri
  misurati (autocorrelazione 0,91-0,94 contro 0,18-0,44 delle derivate
  istantanee).

**Risposta pronta, se richiesta di nuovo:**

> Le tre rappresentazioni e le dodici feature finali sono implementate da me
> in `src/geometry.py`, a partire dai soli landmark grezzi di MediaPipe. Dove
> uso uno strumento esistente — l'analisi delle componenti principali per
> l'ellisse — lo dico esplicitamente: la tecnica è nota, l'applicazione a
> questo problema è mia. I tre descrittori temporali non derivano da nessuna
> libreria: sono una formula e un'implementazione a buffer circolare che ho
> scritto io.

### 9quater. Testo completo verificato per le slide 6-7

Bozza della candidata, controllata e corretta su due punti: "dynamic type
warping" → **dynamic time warping** (lapsus da correggere prima
dell'aula, non durante); "standardizzazione" → **normalizzazione** per il
passaggio pre-DTW, per non confonderlo con la standardizzazione
(`StandardScaler` fit-on-train) del classificatore, nominata più avanti nel
discorso — sono due passaggi distinti e in questo progetto si chiamano in
modo distinto apposta (v. `docs/DISCORSO_CORRETTO.md`, dove sono
esplicitamente separate). Per il resto la bozza è accurata, inclusa la
distinzione corretta fra ciò che stima MediaPipe (i landmark 3D di A2) e
ciò che costruisce la candidata (A1, A3, tutte le grandezze derivate).

> A partire dai 33 landmark che MediaPipe mi fornisce, ho definito tre
> rappresentazioni dello stesso movimento: per ciascuna ho selezionato un
> sottoinsieme di punti utile a costruire le feature più adatte a
> distinguere una caduta da un'attività quotidiana.
>
> La prima usa landmark bidimensionali nel piano immagine e sintetizza la
> distribuzione di questi punti con un'ellisse. L'ellisse deriva
> dall'analisi delle componenti principali: dagli autovalori e dagli
> autovettori della covarianza di questi punti ricavo le direzioni
> principali della dispersione, e da lì costruisco l'ellisse — mi serve per
> capire quando la persona è effettivamente eretta e quando la sua
> configurazione si sposta verso il basso. Con questa geometria, che
> dipende da come la telecamera vede la persona, ho costruito le grandezze
> geometriche e cinematiche di base per questa rappresentazione.
>
> Ho fatto lo stesso per le altre due. La seconda usa coordinate
> tridimensionali — quelle sono una stima che prendo direttamente da
> MediaPipe, non le calcolo io — da cui ricavo l'angolo del tronco rispetto
> alla verticale. La terza considera il corpo stesso come riferimento:
> prendo come origine il centro del bacino e normalizzo rispetto alla
> lunghezza del tronco, per ridurre la dipendenza dalla posizione e dalla
> scala della persona nell'immagine.
>
> Tutte queste grandezze le ho implementate io, dopo vari esperimenti, per
> capire quali, a partire da questi punti, fossero più utili a distinguere
> una caduta da un'attività quotidiana. In totale sono 32 candidate, e da
> queste ne sono state selezionate dodici tramite dynamic time warping:
> siccome ogni feature ha una scala diversa, prima le normalizzo, poi
> confronto le curve temporali permettendo una deformazione nel tempo, così
> da confrontare lo stesso movimento anche se eseguito a velocità diverse.
> Le feature più utili, secondo questo criterio, sono quelle con andamenti
> simili all'interno della stessa classe e diversi tra classi diverse.

---

## 11. Prestazioni reali sulla board — non l'offline, non il benchmark

Richiesto esplicitamente il 20 ottobre: separare le prestazioni della
configurazione **installata** (MediaPipe Pose + Random Forest, le dodici
feature DTW) misurate su **sessioni reali sulla board**, dall'esperimento
offline sulle cinque configurazioni A3/A3h/A3i (quello è sviluppo, non il
sistema installato — v. §1). Fonte: `tesi/Cap5.tex`, sezioni "Event-level
metrics" (`sec:finestre-eventi`) e "Recall and criteria for associating the
events" (`sec:recall-campo`), lette il 20 ottobre.

**Protocollo domestico** (campagna di agosto + sessione del 6 settembre):
2 abitazioni, 4 giorni, 12 blocchi, ~9,6 ore di funzionamento effettivo, 5
cadute simulate, 7,45 ore su 9,58 con posa valida (77,8%).

**Tasso di allarme — 9 sessioni, 14,98 ore in tempo di orologio** (gli 8
blocchi di agosto sopra i 9 minuti + la sessione lunga del 6 settembre):

| grandezza | valore |
|---|---:|
| rapporto finestre sopra soglia : eventi | **44,8** |
| eventi/ora sul tempo totale | **11,1** |
| eventi/ora sulle sole ore con decisioni (1,41 h di buco escluse) | **12,2** |
| esempio: sessione 11 agosto, finestre sopra soglia → eventi | 208 → 14 (rapporto 14,9) |

**Richiamo sulle 5 cadute simulate (campagna di agosto):**

| criterio | risultato |
|---|---|
| tolleranza ±60s, una finestra positiva sufficiente | **4/5**, richiamo 0,80, IC 95% 0,28–0,99 |
| regola operativa vera (soglia 0,50 + 5 finestre consecutive) | **2/5** generano un allarme |

Nota dichiarata nella tesi: un'analisi offline precedente su questi stessi
dati aveva trovato 2/5 anche nel caso a finestra singola, non 4/5 — la
differenza veniva dal modello (media dei fold in cross-validation contro il
modello finale riaddestrato su tutto, installato sulla board) più un doppio
sottocampionamento nell'analisi offline. Corrette queste due cose, l'offline
riproduce il comportamento della board — quindi non è una discrepanza
irrisolta, è stata spiegata.

**Verifica più precisa — sessione del 9 settembre** (4 cadute annotate sul
fotogramma esatto, quella già citata in §3-§9 e usata per i video):
classificatore **3/4 riconosciute**, regola di aggregazione **2/4 allarmi**
— la seconda caduta, sei secondi dopo la prima, è vista ma non genera
allarme (sospensione di 30s ancora attiva); un falso positivo sul divano
(4 finestre sopra soglia) **non genera allarme**, sotto le 5 richieste.

**Latenza introdotta dalla pipeline** (a 8,02 fps medi; non la latenza
reale caduta→allarme, perché in casa le cadute sono annotate solo al
minuto): calcolo per fotogramma 0,125s (3,2%), riempimento finestra 2,743s
(71,0%), persistenza 0,997s (25,8%) — totale **3,865s**.

**Attenzione — il «4/5» di agosto e il «3/4» del 9 settembre NON sono la
stessa configurazione, verificato il 21 ottobre.** Il DTWH (le tredici
colonne, con l'altezza dal pavimento) non esisteva ad agosto: è stato
reintrodotto il 6 settembre (ISS-139). Lo stesso K=31 fu scelto guardando un
confronto 4/5-contro-3/5 di agosto (`EXP-053`, progetto precedente) su dati
**pre-DTWH**. Il «4/5» stesso non è stabile: un controllo dell'epoca
(`EXP-055`, 18 agosto) trovò che vale solo a tolleranza ±90s e senza
persistenza, altrimenti è 1/5. **Non sommare le cadute delle due campagne
in un unico numero** ("9 cadute, 7 riconosciute") senza dichiarare questo:
vengono da due tappe diverse della pipeline. Dichiararlo come limite è più
difendibile che tacerlo — ed è coerente col messaggio centrale del lavoro.

---

## 11bis. Perché non un F2 sul campo — numeri verificati, con una correzione

Spiegazione data il 20 ottobre, **corretta dopo un controllo incrociato**
richiesto dalla candidata il 21: una prima versione citava `DEC-106` di
`docs/DECISIONS.md`, che a sua volta cita `EXP-009` (20 agosto, un GRU a tre
classi, fase acerba del progetto) — non la configurazione finale installata.
I numeri sotto sono verificati contro `tesi/Cap4.tex` e `Cap5.tex`, non contro
un record di decisione più vecchio.

**Perché non si calcola un F2 sui dati reali.** UP-Fall (il benchmark) ha una
prevalenza di finestre positive molto più alta di quella che una casa vera
produce. F2 dipende dalla prevalenza attraverso la precisione: lo stesso
classificatore, stessa soglia, dà F2 diversi a seconda di quanto è raro
l'evento. Un F2 forzato sui dati di casa (pochissimi positivi veri, milioni
di finestre negative su una giornata) non sarebbe confrontabile con quello
del benchmark, oltre a essere statisticamente instabile con 5-9 eventi.
(Nota: l'F2 sul campo **si potrebbe** calcolare in linea di principio, con
annotazioni sufficienti — il punto non è l'impossibilità, è che non sarebbe
una stima robusta né comparabile.)

**I numeri corretti, nella configurazione finale:**

| grandezza | valore verificato | fonte |
|---|---|---|
| prevalenza benchmark (protocollo principale) | **12,72%** — 1.491 su 11.719 finestre | `Cap4.tex:36` |
| falsi positivi, configurazione installata, prima delle prove domestiche | **0,96%** — 46 su 4.767 finestre negative | `Cap5.tex:284` |
| proiezione: finestre erroneamente positive/ora | **~156** (16.200 decisioni/ora × 0,96%) — finestre, non allarmi distinti | calcolo da quanto sopra |
| allarmi veri effettivamente generati (dopo soglia + persistenza + sospensione) | **11,1–12,2 eventi/ora** | §11, già verificato |

**Sulla soglia 0,50:** non è stata calibrata formalmente sulle sessioni
domestiche — è stata scelta confrontando sei regole sui fold di test del
benchmark (v. `DISCORSO_CORRETTO.md`). Le sessioni domestiche **mostrano la
conseguenza** di quella soglia sui falsi allarmi reali, non ne sono state la
fonte. Non dire che le sessioni domestiche "hanno tarato la soglia": di' che
l'hanno **messa alla prova**.

**Risposta pronta** ("Perché non ha calcolato l'F2 sulla board?"):

> Ho distinto la valutazione sul benchmark da quella operativa in ambiente
> domestico, perché rispondono a due domande diverse. Sul benchmark ho usato
> l'F2 per confrontare i classificatori e misurare la capacità di
> riconoscere le cadute. Nelle prove domestiche la prevalenza delle cadute è
> estremamente bassa e gli eventi simulati sono pochi: un F2 calcolato su
> così pochi eventi sarebbe instabile e non direttamente confrontabile con
> quello del benchmark. Ho quindi valutato il comportamento operativo
> attraverso il numero di cadute riconosciute, gli allarmi effettivamente
> generati e il carico di eventi all'ora.

---

## 12. Hardware e architetture — Transformer, VLM, e i numeri della board

Preparato il 21 ottobre. Contiene **una correzione a una risposta che si
stava per dare sbagliata** (il Transformer scartato "perché lento": la
misura dice il contrario) e **un punto da non affermare mai** (che un VLM
non possa girare sulla board: può, ed è documentato dal produttore).

### 12.1 Prestazioni della configurazione installata (DTW + Random Forest)

| | valore |
|---|---|
| F2 benchmark, LOSO 10 soggetti | **0,825 ± 0,076**, recall 0,844, 232 FN, 468 FP (`Cap4.tex:297`) |
| Cadute, 9 settembre (4 annotate al fotogramma) | classificatore **3/4**, regola d'allarme **2/4** |
| Cadute, agosto (5 annotate al minuto) | **4/5** criterio permissivo, **2/5** regola installata |
| Carico, 9 sessioni / 14,98 h | **11,1 eventi/ora** (tempo totale), **12,2** (sole ore con decisioni) |

Asterisco obbligatorio: agosto precede l'altezza dal pavimento (6
settembre), non è la stessa configurazione di settembre — v. §11.

### 12.2 Finestre positive contro eventi d'allarme

- Una **finestra** e' una decisione: una ogni **2/9 ≈ 0,22 s**, cioe'
  **4,5 al secondo, 16.200 all'ora, 388.800 al giorno** (`Cap5.tex:285`).
  Sulla board, a 7,3 fps misurati, in esercizio sono ~**3,7 al secondo**:
  il numero del capitolo descrive la configurazione, quello della board la
  misura.
- Un **evento** e' cio' che l'utente percepisce: 5 finestre consecutive
  sopra soglia, poi 30 s di silenzio.
- Rapporto misurato fra i due: **44,8** sulle nove sessioni. Sessione
  dell'11 agosto: **208 finestre → 14 eventi** (14,9). Contare finestre
  invece di eventi **sovrastima i falsi allarmi di 44,8 volte**.
- Limite da dichiarare: il conteggio degli eventi dipende dai parametri di
  aggregazione. Per un falso positivo che e' uno **stato** (persona distesa
  sul divano) la misura onesta e' la **quota di tempo in allarme**, che non
  dipende da persistenza e sospensione.
- Il riferimento di letteratura 0,049 allarmi/ora **non e' confrontabile**:
  cambiano tecnologia, popolazione, durata, definizione di evento.

### 12.3 Prestazioni hardware

| | valore |
|---|---|
| Pipeline completa | **7,3 fps**, 136,65 ms/fotogramma |
| stima della posa | 116,38 ms — **85,2%** |
| classificatore | 19,51 ms — **14,3%** |
| pre + post | 0,75 ms |
| Memoria di picco | **297 MB** = 5% dei 6 GB (`Cap5.tex:247`) |
| Continuita' | **4,59 h**, nessuna sospensione, 2 interruzioni camera recuperate |
| Costo | ~150 € hardware |

**Perche' 7,3 fps e' significativo:** una caduta dura mediamente ~3,1 s; a
7,3 fps una finestra di 22 campioni copre ~3 s, quindi l'evento e'
descritto da ventidue osservazioni. La scomposizione della latenza lo
conferma: dei 3,865 s introdotti dalla configurazione, il **71% e' il
riempimento della finestra** e solo il **3,2% il calcolo per fotogramma** —
raddoppiare gli fps sposterebbe pochissimo. La NPU da 6 TOPS **non e'
usata**: MediaPipe gira su CPU.

### 12.4 Transformer — la correzione

Il Transformer **e' stato provato**, come classificatore sulle dodici
grandezze: F2 **0,837 ± 0,082**, contro GRU 0,857 e foresta 0,825. GRU
contro Transformer: differenza 0,020, t = −1,22, servirebbero **54
soggetti** per distinguerli (`Cap4.tex:297`, `:348`).

**NON dire che la foresta e' stata scelta perche' il Transformer era troppo
lento: la misura dice il contrario.** `EXP-019`, costo per finestra:

| architettura | ms/finestra |
|---|---:|
| CNN 1D | 1,32 |
| **Transformer** | **1,61** |
| Grafo | 1,80 |
| LSTM | 3,45 |
| GRU | 3,51 |
| **Foresta (installata)** | **4,85** — la piu' lenta delle sei |

La ragione vera, e difendibile: **dipendenze software** (scikit-learn
contro TensorFlow su ARM) e semplicita' di installazione; il modello pesa
0,6 MB.

**E comunque avrebbe cambiato poco:** il classificatore e' il 14,3% del
tempo. Mantenendo sulla board il vantaggio di 3× misurato sul PC, 19,51 ms
→ ~6,5, totale 136,65 → ~124 ms, cioe' da **7,3 a ~8,1 fps**: +11%. Il
collo di bottiglia e' la percezione.

**Da ammettere per primi:** `EXP-019` e' dichiaratamente una misura **sul
calcolatore, non sulla board**. La pipeline completa a bordo con il
Transformer non e' mai stata misurata.

### 12.5 VLM — il punto da non sbagliare

**Non affermare che un VLM non puo' girare sulla ROCK 4D.** L'RK3576 e'
documentato dal produttore come capace di eseguire **Qwen2.5-VL 3B** via
RKNN-Toolkit2, e il materiale ufficiale elenca il supporto a VLM.
L'argomento corretto non e' la possibilita', e' il **regime di esercizio**:

- requisito: **una decisione ogni 0,22 s, in continuo, per ore**, su un
  dispositivo da 150 €;
- la pipeline attuale lo fa con 136 ms/fotogramma e 297 MB;
- su quella classe di hardware un LLM piccolo gira a ~34 token/s (Qwen2
  0.5B quantizzato su RK3576), un VLM da 2B decodifica a ~15 token/s, e
  Qwen2.5-VL-3B su RK3588 risulta documentato **con un acceleratore
  aggiuntivo** per l'inferenza pratica;
- **costo per una singola immagine**: InternVL3.5-2B su RK3588 (chip
  imparentato con l'RK3576 della ROCK 4D) impiega **2,1 s per l'encoder
  visivo + 1 s di prefill (265 token)**, cioe' **oltre 3 secondi** prima
  della prima risposta — contro i **136 ms a fotogramma (7,3 fps)** della
  pipeline installata. **Attenzione a come si dice questo numero**: la
  pipeline gira a 7,3 fps, cioe' 136 millisecondi *a fotogramma* — non
  "136 fps", e' l'errore piu' facile da fare qui e salta all'occhio di chi
  si occupa di hardware;
- memoria: un 3B a 4 bit sono ~2 GB di soli pesi, contro i 297 MB di tutta
  la pipeline — cambia la classe di costo del dispositivo, che era un
  vincolo del lavoro.

Distanza: **uno o due ordini di grandezza**, strutturale, non di taratura —
non "il VLM e' piu' lento", ma un regime d'uso diverso: circa 270 decisioni
al minuto richieste dal sistema contro circa 14 risposte al minuto che un
VLM di quella taglia produrrebbe, se interrogato in continuo.

**La chiusura costruttiva** (trasforma l'obiezione in progetto): un VLM
avrebbe senso come **secondo stadio**, invocato solo quando il rilevatore
economico ha gia' segnalato qualcosa. Con undici eventi l'ora, un modello
chiamato undici volte l'ora invece di 4,5 volte al secondo e' sostenibile.

**Da ammettere:** nessuna misura propria — ne' VLM ne' Transformer
end-to-end sono stati eseguiti sulla board. I numeri citati sono di
letteratura e del produttore.

**Come si verificherebbe davvero** (risposta a "come fa a sapere se
funzionerebbero meglio?"): convertire il modello con RKNN-Toolkit2,
quantizzare a INT8, misurare fps e memoria sulla board, e valutarlo con lo
stesso protocollo LOSO. E' una procedura, non un'opinione.

**Il filone esiste**: lavori su transformer alleggeriti per fall detection
su edge, uno dei quali riporta una riduzione del **99,6% dei parametri**
mantenendo l'accuratezza. Dichiararlo come non esplorato e' piu' solido che
liquidarlo.

Fonti consultate il 21 ottobre 2026:
- <https://thinkrobotics.com/products/recomputer-rk3576-20-open-rockchip-ai-box-for-ai-development>
- <https://sensecraft.seeed.cc/ai-lab/en/tutorials/rk/benchmark/llm> (InternVL3.5-2B
  su RK3588: encoder 2,1 s + prefill 1 s, 265 token)
- <https://worldscientific.com/doi/10.1142/S0129065724500266>
- <https://journals.uran.ua/tarp/article/view/329398>

---

## Collegamenti

- [SIMULAZIONE_ORALE.md](SIMULAZIONE_ORALE.md) — sedute e risposte per
  domanda, seduta del 22 ottobre 2026.
- [DOMANDE_PUNGENTI_4_DOCENTI.md](DOMANDE_PUNGENTI_4_DOCENTI.md) — le cinque
  domande da sapere a memoria, aggiornate il 19 ottobre.
- [DISCORSO_CORRETTO.md](DISCORSO_CORRETTO.md) — discorso esteso verificato,
  fonte dei numeri usati sopra.
- [GUIDA_DIFESA.md](GUIDA_DIFESA.md) — riferimento completo capitolo per
  capitolo.
