# Guida alla stesura del Capitolo 4

Per ogni sezione: **che cosa è stato fatto** (codice, dati, misura), **quali
tabelle e figure**, **quali promesse dei capitoli precedenti si pagano qui**, e
**che cosa dire**. Scritta il 2026-09-23.

La struttura segue la richiesta del relatore: le prime sezioni sono
**protocollo** — deciso prima di vedere i risultati — e tutto il resto sono
**risultati**. Fra le due c'è una riga di transizione esplicita.

---

## Inventario: che cosa c'è e che cosa manca

**Figure già citate in Cap4 (10):** `fig_due_camere`, `fig_dtw`,
`fig_architetture`, `fig_dimensione`, `fig_finestra`, `fig_occlusioni`,
`fig_rumore`, `fig_compiti`, `fig_viewpoint_dist`, `fig_esterno`.

**Figure pronte e NON citate, che vanno aggiunte:**

| figura | dove | perché
|---|---|---
| `fig_viste` | 4.7.1 geometria di ripresa | è il risultato di classificazione del cambio vista; oggi la sezione ha solo la figura della geometria. Riparata il 2026-09-23: prima non veniva generata.
| `fig_dominio` | 4.7.2 ricalibrazione | scompone il divario fra archivio di addestramento e archivio mai visto: è esattamente la figura dei due esperimenti che il relatore chiede di separare.

**Figura da NON mettere qui:** `fig_configurazioni` mostra A3 / A3h / A3i con e
senza controesempi — sono le cinque configurazioni del **Capitolo 5**, non le
tre di 4.3.1. Va accanto a `fig_errori`, in Cap5.

**Tabelle nuove da costruire:** `tab:leakage` (4.1.5), `tab:dtw_fold` e
`tab:k_fold` (4.6), `tab:dinamica` (4.5, arriva dal Cap3).

**Tabella che NON va spostata qui:** `tab:kappa` resta in **Cap5**. Ha una
colonna di laboratorio e una domestica, e il suo punto — il banco dice 45, la
casa dice 31 — è la tesi del Capitolo 5. In Cap4 se ne parla solo in 4.6, con
la misura annidata, che è un'altra cosa.

---

# 4.1 Protocollo sperimentale · `sec:protocollo`

**Cappello, quattro righe.** Le cinque scelte che seguono sono state fissate
prima di osservare qualunque risultato e non sono state riviste dopo. Perché la
distinzione conta: una scelta compiuta guardando il proprio esito non è un
protocollo, è un risultato travestito.

---

## 4.1.1 Sbilanciamento e metrica · `sec:metriche`

### Che cosa è stato fatto

Il sottoinsieme valutato è **Camera 1** di UP-Fall: 58.359 fotogrammi, 110
riprese, dieci soggetti. Verificato su `feature_v5.csv` il 2026-09-23 — tutti i
valori del paragrafo e della tabella coincidono con il dato.

La finestratura (`src/dati.py`) produce **11.719 finestre**, di cui **1.491
positive**, cioè il **12,72 %**. Fra i fold le positive vanno da **104 a 171**.

I pesi di classe sono inversamente proporzionali alla frequenza e calcolati
**sul solo training del fold** (`pipeline/addestra.py`). Non c'è
sottocampionamento.

### Tabelle e figure

`tab:etichette_valutazione` — distribuzione per fotogramma. **Rinominata**: si
chiamava `tab:etichette` come quella del Cap3, che però copre le 220 riprese
mentre questa copre le 110 di Camera 1.

**Nessuna figura.** Qui bastano una tabella e le definizioni.

### Coerenza da rispettare

- Cap1 `tab:criteri_valutazione` promette *Reliability → event recall*: la
  metrica per finestra di questa sezione **non** è quella, e va detto che la
  contabilità per evento arriva nel Cap5.
- Cap2 §2.4.2 dice che UP-Fall è quasi bilanciato a livello di riprese (255
  contro 306) e che lo sbilanciamento vero compare con la finestratura. **Qui
  si paga quella promessa** con 12,72 %.
- Cap3 riga 164 rimanda a questo capitolo per la ragione per cui l'accuratezza
  non basta.

### Che cosa dire

1. Il sottoinsieme, con i numeri sopra.
2. Perché l'accuratezza non serve: un classificatore che negasse sempre
   otterrebbe **87,3 %**.
3. Definire precision, recall, $F_\beta$ con $\beta = 2$, e dichiarare che
   **$\beta$ è stato fissato prima** e non scelto sui risultati.
4. $F_2$ non sostituisce il conteggio degli errori: due configurazioni con lo
   stesso $F_2$ possono sbagliare in modi opposti. Nei confronti successivi si
   riportano sempre anche recall, FN e FP.
5. Pesi di classe sul solo training. Niente sottocampionamento, **e la
   ragione**: con 1.491 positive su 11.719 un riequilibrio toglierebbe tre
   quarti delle negative, cioè proprio la varietà di attività quotidiane che il
   modello deve imparare a non confondere.

---

## 4.1.2 Partizionamento LOSO · `sec:loso`

### Che cosa è stato fatto

`fold_loso` in `src/dati.py`: dieci fold, un soggetto in test, **uno in
validation — il successivo in ordine circolare**, regola deterministica — otto
in training. Nessun soggetto compare in due insiemi.

Prima si divideva **per registrazione** su cinque soggetti: le riprese erano
disgiunte, le persone no.

### Tabelle e figure

`tab:fold` — composizione dei dieci fold. **Nessuna figura.**

### Coerenza da rispettare

- **Cap1 `tab:domain_shift` punta qui** per *subject shift*. La sezione deve
  quindi leggersi anche come la prima delle quattro prove di generalizzazione,
  non solo come una regola di partizionamento.
- Cap2 §2.4.3 introduce subject-dependent contro subject-independent e cita
  Scheurer: **qui si paga**, e la citazione è verificata.

### Che cosa dire

1. Il problema: stesso soggetto in più riprese, finestre correlate.
2. Che cosa si faceva prima, e perché è una stima ottimistica — il modello usa
   corporatura e stile individuale.
3. La regola adottata, con il criterio circolare dichiarato deterministico.
4. `tab:fold`.
5. **Il punto che serve in tutto il resto del capitolo:** la dispersione fra
   soggetti vale **0,05–0,14** di $F_2$, confrontabile con molte differenze fra
   configurazioni. Da qui la regola: **confronto appaiato fold per fold, mai
   medie nude.**

---

## 4.1.3 Normalizzazione · `sec:normalizzazione`

### Che cosa è stato fatto

`Scaler` in `src/dati.py`. Due passaggi: `log1p` con segno su **quattordici**
colonne asimmetriche, poi `StandardScaler`. Media e deviazione sono stimate
**sui soli fotogrammi di training del fold** e applicate senza ricalcolo a
validation e test. I parametri sono salvati col modello perché servono in
inferenza.

**Correzione obbligatoria.** Il testo dice che la trasformazione si applica
«alle grandezze che soddisfano il criterio previsto nella fase di
preprocessing». **Un criterio non esiste**: `ASIMMETRICHE` è un elenco fisso di
quattordici nomi — le nove integrali più velocità angolare del tronco, velocità
della testa, velocità del bacino, velocità della testa relativa e larghezza
normalizzata — compilato guardando le distribuzioni.

### Tabelle e figure

Nessuna delle due.

### Che cosa dire

1. Il problema: rapporto fra le scale pari a **646**.
2. La standardizzazione, e che è stimata **per fold sul solo training**.
3. Perché sui **fotogrammi** e non sulle finestre: le finestre si sovrappongono
   di 20 campioni su 22, quindi contare dopo la finestratura significherebbe
   pesare lo stesso campione più volte.
4. Il `log1p` con segno, e l'elenco fisso dei quattordici nomi — **non** un
   criterio automatico.
5. Dopo: rapporto fra le scale **1,05–1,35**. Parametri salvati col modello.

---

## 4.1.4 Soglia decisionale · `sec:soglia`

È la sezione su cui il relatore insiste di più.

### Che cosa è stato fatto

`pipeline/soglia.py` riusa le probabilità già prodotte dai dieci fold e
confronta sei regole senza riaddestrare. La procedura provata per prima —
soglia scelta sul validation di ciascun fold — dà dieci valori fra **0,01 e
0,99**, deviazione **0,37**.

Decisione adottata (DEC-105): **$\theta = 0{,}50$ fissa**, uguale per tutti i
fold e tutte le configurazioni.

### Tabelle e figure

`tab:soglie` — le sei regole. **Nessuna figura.**

### Che cosa dire

1. Definire la soglia e il suo effetto: recall contro falsi allarmi.
2. La procedura provata per prima, **con i dieci valori**: sono la prova.
3. `tab:soglie`.
4. La conclusione: si adotta 0,50 fissa.
5. **La cautela, che va scritta e non sottintesa.** Le sei regole sono state
   confrontate sui fold di *test*: adottare 0,50 «perché vince» sarebbe
   selezione sul test. Ciò che l'esperimento stabilisce legittimamente è che
   **stimare la soglia su un solo soggetto di validation è una procedura
   instabile** — conclusione sulla procedura, non sui dati di prova.
6. **La frase che il relatore chiede, adattata.** La sua descrive la procedura
   che abbiamo *scartato*. La garanzia qui è più forte e va formulata per
   quello che è: *la soglia non vede il soggetto di prova perché non vede alcun
   dato.* Nominare l'unica eccezione — la soglia **oracolo** del trasferimento
   a UR-Fall — e dire che è diagnostica e dichiarata dove compare.

---

## 4.1.5 Che cosa viene stimato dentro il fold · `sec:leakage_protocollo`

**Sezione nuova.** Cap3 la promette in due punti (righe 89 e 1178): senza,
restano promesse scoperte.

### Che cosa dire

1. Il procedimento corretto **come sequenza numerata**, nella forma che il
   relatore ha scritto: metti da parte $s$ · calcola il criterio di selezione
   sui rimasti · stima la normalizzazione sui rimasti · addestra e tara sui
   rimasti · congela tutto · valuta su $s$ una volta sola. E accanto l'ordine
   sbagliato: selezionare le grandezze su tutti i soggetti e fare il LOSO dopo.
2. `tab:leakage` **nuova**, cinque righe:

| operazione | calcolata su | vede il test?
|---|---|---
| normalizzazione | training del fold | no
| soglia | nessun dato | no
| iperparametri del modello | nessun dato | no
| parametro $K$ della rappresentazione | scansione su dati poi valutati | **sì**
| selezione DTW | tutti i soggetti | **sì**

3. Annunciare che le due violazioni sono **misurate** in §4.6.

**Nessuna figura.** Il risultato sta più avanti.

---

> ### Riga di transizione
> Quanto precede è stato deciso prima di guardare i dati; quanto segue è ciò
> che i dati hanno mostrato.

---

# 4.2 Effetto congiunto delle correzioni · `sec:baseline`

### Che cosa è stato fatto

Confronto fra la configurazione iniziale e quella corretta, a parità di dati e
modello. Le correzioni sono tre: normalizzazione assente, split per
registrazione invece che per soggetto, stesso insieme usato per scelte di
modello e verifica finale.

### Tabelle e figure

`tab:correzioni`. **Nessuna figura.**

### Che cosa dire

Il punto: **il fallimento iniziale non era del classificatore.** Da 0 a 144 veri
positivi. Ma $F_1 = 0{,}234$ resta basso: le correzioni rendono la valutazione
significativa, non risolvono il problema. È questo che apre le sezioni seguenti.

---

# 4.3 Confronto fra rappresentazioni e architetture

## 4.3.1 Confronto fra rappresentazioni · `sec:featureset`

### Che cosa è stato fatto

Due misure distinte, e **vanno tenute distinte**:

- `tab:rappresentazioni5` — A1, A2, A3 a **cinque** soggetti. È una verifica
  preliminare, e **non è una classifica**: due grandezze di A2 erano definite
  sulla traslazione del bacino nei world landmark, che è l'origine del
  riferimento e quindi quasi degenere. Sono state rimosse. Dichiararlo.
- `tab:rappresentazioni10` — a **dieci** soggetti: A3 senza integrali 0,874,
  con integrali 0,858, sottoinsieme DTW 0,857.

### Che cosa dire

Escursione **0,017** contro dispersione fra soggetti **0,08**. Il risultato
**non** dice che integrali e selezione peggiorino: dice che dentro UP-Fall, con
questa numerosità, le tre configurazioni **non sono distinguibili**. Rimandare
al trasferimento esterno (§4.7.2), dove le differenze si vedono — lì il
sottoinsieme DTW arriva a PR-AUC 0,660 contro 0,440 di A3 senza integrali.

**Nessuna figura.** (`fig_configurazioni` mostra altro: è di Cap5.)

---

## 4.3.2 Confronto fra architetture · `sec:architetture`

**È la risposta alla RQ1**, e Cap1 riga 237 e Cap3 riga 1003 ci puntano
entrambi.

### Che cosa è stato fatto

Sei architetture (`src/modelli.py`), stessa rappresentazione, stesse finestre,
stessi fold, stessa normalizzazione, stessa soglia. Varia solo il
classificatore. Struttura e numero di parametri sono nel Cap3
(`tab:architetture` della metodologia): **non ripeterli qui**.

### ⚠ Il difetto da risolvere prima di scrivere

La prosa di questa sezione cita valori di **tre campagne diverse**. Verificato
il 2026-09-23:

| architettura | v2 (20 ago) | v3 (6 set) | **v5 (9 set)** |
|---|---|---|---|
| GRU | 0,847 | 0,819 | **0,857** |
| CNN 1D | 0,833 | 0,828 | **0,838** |
| Transformer | 0,846 | 0,799 | **0,837** |
| LSTM | 0,858 | 0,783 | **0,829** |
| Random Forest | 0,792 | 0,807 | **0,825** |
| Grafo | 0,794 | 0,699 | **0,794** |

**Il Capitolo 3 descrive v5** — 220 riprese, 116.362 fotogrammi, $\Delta t$
reale, integrali ricalcolate. La tabella va rifatta su v5, e `fig_architetture`
è già stata riportata su v5 il 2026-09-23 (prima mescolava v2 e v5).

### Che cosa dire — e non è la classifica

1. Che cambia **solo** l'architettura.
2. `tab:architetture` e `fig_architetture`.
3. **Il punto:** l'escursione fra le cinque architetture non a grafo vale
   **0,032** su v5, meno di metà della dispersione fra soggetti. La differenza
   fra due architetture è più piccola della differenza fra due persone. Nella
   figura si vede direttamente: **tutte e sei cadono dentro la banda grigia.**
4. **L'argomento più forte, ed è nuovo.** Correggendo l'estrazione delle
   feature — stessi soggetti, stesso protocollo, stessa soglia — l'escursione
   **si restringe** (0,066 → 0,045 → 0,032) e la classifica **si azzera**:
   Spearman fra v2 e v3 vale **−0,03**. La LSTM passa da prima a quinta, la
   foresta da ultima a terza. Non serve cambiare dataset per rimescolare
   l'ordine: basta correggere un $\Delta t$.
5. Il numero di parametri non ordina il risultato.

---

## 4.3.3 Analisi delle differenze e numerosità · `tab:numerosita`

### Che cosa è stato fatto

`pipeline/confronto_appaiato.py`: test $t$ appaiato fold per fold, più la
numerosità necessaria per rilevare l'effetto con potenza dell'80 %.

### Che cosa dire

1. La sola architettura che supera il valore critico è la **rete a grafo**, e lo
   supera **nel verso sbagliato**; con la correzione per confronti multipli non
   resta significativa.
2. **Il dato che vale di più:** il confronto GRU/LSTM richiederebbe decine di
   soggetti, mentre la **definizione del compito** si vede con **due**.
3. Conclusione: alcune scelte metodologiche pesano molto più della scelta fra
   architetture di capacità simile.
4. Dichiarare che **non c'è stata ricerca di iperparametri**.

⚠ `tab:numerosita` va riallineata ai valori v5 insieme alla tabella sopra.

---

# 4.4 Analisi di sensibilità · `sec:sensibilita`

**Cappello:** queste verifiche non cercano un ottimo, controllano se le
conclusioni precedenti dipendano da una singola scelta.

| sottosezione | codice | tabella | figura | numerosità |
|---|---|---|---|---|
| Dimensione del modello | — | — | `fig_dimensione` | **cinque soggetti: dichiararlo** |
| Effetto del frame rate · `sec:framerate` | `pipeline/tune_framerate` | `tab:framerate` | — | **cinque soggetti** |
| Lunghezza della finestra | `finestratura_confronto.py` | `tab:finestra` | `fig_finestra` | dieci |
| Regolarità temporale · `sec:autocorrelazione` | `autocorrelazione.py` | `tab:autocorrelazione` | — | dieci |
| Sensibilità al rumore · `sec:rumore` | `rumore.py` | `tab:rumore`, `tab:ambiguita` | `fig_rumore` | dieci |
| Robustezza all'occlusione · `sec:occlusioni` | `occlusioni.py` | `tab:occlusioni` | `fig_occlusioni` | dieci |

### Promesse da pagare qui

- **Cap1 `tab:domain_shift` → `sec:framerate`** per il *frame-rate shift*.
- **Cap1 riga 174** rimanda a questo capitolo per la sensibilità alla perdita
  di landmark.
- **Cap3 riga 254 → `sec:occlusioni`**: dichiara di non aver usato la
  *visibility* per punto, e si appoggia al fatto che congelare ginocchia e
  caviglie sposta $F_2$ di **+0,001**. Verificato: `tab:occlusioni` lo riporta.
- **Cap3 riga 620 → `sec:rumore`** per il rumore gaussiano.
- **Cap3 §regolarità → `sec:autocorrelazione`**, dove Cap3 dice espressamente
  che l'autocorrelazione serve a descrivere la regolarità e **non** l'utilità.

### Le cose da dire che oggi mancano

**Lunghezza della finestra.** L'ipotesi era che una finestra più lunga aiutasse,
perché la transizione dura 3,11 s in mediana. **Guardare se l'andamento è
monotono: non lo è**, e per questo si tiene $L = 22$. Dire che si è misurato e
si è **tenuto** il valore che si aveva — è il contrasto con $K$, che invece è
stato cambiato.

**Regolarità temporale.** Derivate 0,249–0,533, integrali 0,785–0,988. Il
valore più basso fra le integrali supera il più alto fra le derivate, quindi la
separazione fra le due famiglie non dipende da quale grandezza si scelga. **La
cautela è obbligatoria:** una grandezza accumulata è più regolare *per
costruzione*; l'autocorrelazione non dimostra che sia informativa.

**Rumore, e il controesempio che è la parte migliore.** Fino a $\sigma = 0{,}04$
il calo massimo è 0,031, sotto la dispersione fra soggetti. Poi
`tab:ambiguita`: su una persona **ferma su un divano** l'escursione massima del
tronco vale **93,5°**, superiore ai **60,7°** di una caduta vera. Non è
movimento: è lo stimatore che alterna fra due configurazioni. Spiegare perché il
rumore gaussiano non cattura questo caso — è un errore **coerente nel tempo**, e
una grandezza accumulata non sa distinguerlo da un movimento reale. È il limite
che nessuna finestra temporale risolve.

**Occlusioni.** Tenere il capoverso sulle spalle: rifacendo la misura con il
sottoinsieme precedente le spalle tornano a −0,019, quindi la sensibilità non
dipende dai punti del corpo ma da **quali dodici grandezze il criterio ha
scelto**. È un'osservazione forte.
⚠ La coda di questa sottosezione parla di **rumore**, non di occlusione: va
spostata in `sec:rumore`, dove i numeri stanno già in tabella.

---

# 4.5 Effetto della definizione del compito · `sec:compito-risultati`

Etichetta verificata: `sec:compito-risultati` è quella già sul disco e
`sec:compiti` non è citata da nessuna parte.

### Che cosa è stato fatto

`pipeline/confronto_compiti.py`. Le tre formulazioni definite in Cap3
§`sec:compito` — evento, evento+stato, tre classi — valutate **tutte sulla
stessa etichetta di allarme** (`y_allarme`), altrimenti il confronto è truccato:
un modello addestrato solo sull'evento sarebbe avvantaggiato se le finestre
post-caduta sparissero anche dalla verifica. È la ragione per cui `src/dati.py`
marca quelle finestre con `y_train = -1` invece di eliminarle.

### Tabelle e figure

`tab:compiti`, `fig_compiti`, e **`tab:dinamica` che arriva dal Cap3** — va
inserita subito dopo «Queste due condizioni possono essere trattate come
un'unica classe oppure separate», perché è l'evidenza che regge tutta la
sezione: durante la transizione le due condizioni distano 30–139 volte, fra i
due stati finali 1,3–2,8. La geometria finale non le distingue; la dinamica sì.

### Che cosa dire

**È la differenza più grande di tutto il capitolo:** −0,309, $t = -6{,}85$,
bastano **due** soggetti per vederla. Contrapporla esplicitamente alla
differenza fra architetture, che ne richiederebbe decine.

E il risultato che conta di più: nel compito **evento**, nessuna delle 2.234
finestre di persone sdraiate volontariamente viene classificata positiva. Nel
compito stato il 12,5 %, nel compito allarme il 13,1 %.

---

# 4.6 Quanto pesa il leakage · `sec:misura_leakage`

**Sezione nuova.** Cap3 la promette due volte (righe 1172 e 1210).

### Che cosa è stato fatto

**1. Selezione DTW rifatta per fold** — `pipeline/dtw_per_fold.py`.
Prima un controllo di riproducibilità: rifare la selezione sull'intero insieme
e verificare di riprodurre **esattamente** `scelte.txt`. Senza, il confronto non
significa nulla.
Risultato: **nessuno dei dieci fold riproduce la selezione adottata**; Jaccard
medio **0,769**.

**2. Scelta di $K$ rifatta per fold** — `pipeline/k_per_fold.py`, protocollo
annidato: per ogni soggetto, $K$ scelto con un LOSO interno sui soli nove
rimasti, poi valutazione su quello escluso.
Risultato: **nove fold su dieci scelgono $K = 45$**, non 31. $F_2$ medio
**0,851** contro **0,825**.

### Che cosa dire — e le due misure vanno in direzioni opposte

**Sul DTW.** Sei grandezze su dodici compaiono in tutti e dieci i fold e formano
un nucleo stabile; cinque delle sei sono integrali. L'instabilità si concentra
sulla metà ridondante: otto scambi su sedici avvengono fra grandezze correlate
sopra 0,85. Conclusione: **il leakage esiste, i valori sono un limite
superiore, ma l'effetto è plausibilmente piccolo.** *Plausibile, non
dimostrato*: dimostrarlo richiederebbe di riaddestrare tutto con il
sottoinsieme proprio di ciascun fold.
Dichiarare anche il difetto trovato per strada: **il controllo di
riproducibilità la prima volta è fallito**, per un difetto della libreria di
distanza che restituiva infinito in silenzio. È la ragione per cui il controllo
esiste.

**Su $K$.** Il punto che ribalta l'attesa: il leakage **non ha gonfiato** le
prestazioni, **le ha ridotte** di 0,026.
Onestà statistica: $t$ appaiato **2,22** contro un critico di **2,26**, quindi
**non significativo**; un soggetto pesa 0,122, quasi cinque volte la media;
escludendolo la media scende a 0,016 ma il test sale a 2,72. Effetto **piccolo e
sistematico**, non grande e incerto.
Perché non sorprende: la scansione originale mostrava già che sul solo criterio
di laboratorio 45 batte 31, e ci si fermò a 31 **per il richiamo di campo**.
Che cosa non misura: la preferenza per 31 si fonda sul richiamo domestico, che
il Cap5 riporta come risultato. Separarli richiederebbe cadute diverse da quelle
usate per scegliere, e cinque non bastano.

**Nessuna figura.** Due tabelle nuove.

---

# 4.7 Generalizzazione: soggetto, vista, dataset · `sec:generalizza`

**È la risposta alla RQ2**, e la sezione dove il filo della tesi diventa
visibile.

**Cappello:** il LOSO ha già tolto la prima semplificazione, il soggetto noto —
ed è la ragione per cui ogni valore di questo capitolo è misurato su una persona
mai vista. Qui si tolgono le altre due, una alla volta.

---

## 4.7.1 Effetto della geometria di ripresa · `sec:viewpoint`

Cap1 `tab:domain_shift` ci punta per il *viewpoint shift*; Cap3 righe 688 e 783
per l'altezza dal pavimento e per il criterio del minimo fra le viste.

### Che cosa è stato fatto

`pipeline/escursione_viste.py` per la geometria, `pipeline/viste_incrociate.py`
per le prestazioni. Dieci soggetti, dataset riestratto.

### Tabelle e figure

`tab:escursione`, `tab:viste`, `fig_viewpoint_dist`, `fig_due_camere`, **e
`fig_viste` che va aggiunta**: è il risultato di classificazione delle quattro
configurazioni, e riproduce `tab:viste` esattamente (0,822 / 0,488 / 0,731 /
0,753; FP 722 / 3252 / 751 / 1067).

### Che cosa dire

1. La geometria: escursione media **74,0°** sulla laterale contro **33,2°**
   sulla rialzata; 30 sequenze su 39 sopra 60° contro 8 su 39.
2. Le prestazioni: $F_2$ da **0,822 a 0,488** spostando solo l'inquadratura,
   cioè **−0,334**, circa **tre volte** la dispersione fra soggetti.
3. Il recupero: addestrando su entrambe le viste si arriva a **0,731**, con i
   falsi positivi da 3252 a 751. **Recall e precision migliorano insieme** —
   dirlo, perché distingue un apprendimento più generale da uno spostamento di
   soglia.
4. **I due difetti trovati rifacendo la misura**, da dichiarare: un solo
   stimatore riusato fra riprese (MediaPipe mantiene stato: su una sequenza lo
   scarto arriva a 68°); e su Camera 2 lo stimatore perde chi cade e si aggancia
   a un'altra persona in **11 riprese su 50**, contro 0 su 50 di Camera 1. Le
   undici contaminate sono escluse.
5. Dichiarare che i valori vengono da dieci soggetti e dal dataset riestratto, e
   che una versione precedente a cinque soggetti dava numeri diversi.
6. **L'altezza dal pavimento**, che arriva dal Cap3: sulla laterale la
   separazione fra le mediane vale **+1,43** lunghezze di tronco, sulla frontale
   rialzata **−0,18**, cioè nessuna separazione utile. È la ragione per cui il
   criterio del minimo fra le due viste esclude questa grandezza, e la ragione
   per cui l'insieme a tredici esiste come termine di confronto.

---

## 4.7.2 Trasferimento a un dataset esterno · `sec:domainshift`

Cap1 `tab:domain_shift` ci punta per il *dataset shift*; Cap2 riga 233 annuncia
che al quarto livello «è nuovo tutto il resto insieme».

**Il relatore chiede che i due esperimenti siano presentati come esperimenti
distinti**, perché rispondono a domande diverse. Quindi due sottosezioni.

### Cappello

UR-Fall riestratto con lo stesso motore geometrico: 11.400 fotogrammi, 67
riprese, tutte e 33 le grandezze. **Posa valida nell'81,0 %** contro il 95,9 %
di UP-Fall — e questo è già parte della risposta.

### a) Trasferimento diretto

Modello e soglia restano quelli di UP-Fall, applicati senza toccare nulla.
Risponde alla domanda che un'installazione pone davvero: **che cosa succede
portando il sistema, così com'è, dove non è stato tarato.**
Figura: `fig_esterno`. Tabella: `tab:esterno`.
Il sottoinsieme DTW raggiunge PR-AUC **0,660**, cioè 5,1 volte il caso, contro
1,8 della configurazione precedente.

### b) Ricalibrazione diagnostica

La soglia viene ricalcolata **sulle etichette di UR-Fall**: richiede di
conoscere in anticipo le cadute del nuovo ambiente, e per questo si chiama
**soglia oracolo**. Non è disponibile in esercizio.
**Figura da aggiungere: `fig_dominio`**, che scompone il divario.
A che cosa serve: separare quanta parte del crollo è **perdita di capacità
discriminativa** e quanta è **soltanto una soglia fuori scala**. Il risultato:
dei 0,937 punti di divario, circa 0,457 si recuperano con la soglia e circa
0,480 restano.
**La frase che deve esserci:** il primo esperimento misura il sistema, il
secondo lo diagnostica; riportare il secondo al posto del primo sovrastimerebbe
di molto ciò che il sistema fa su un dominio nuovo.

### c) Metriche indipendenti dalla soglia

Perché servono: la prevalenza diversa rende poco confrontabile un singolo $F_2$
fra i due dataset, perché la precision dipende dalla quota di positivi. PR-AUC e
il guadagno rispetto al caso.

⚠ La scomposizione calibrazione/discriminazione riguarda **la configurazione
precedente**, non il sottoinsieme DTW. Il testo già lo dice: mantenerlo.

---

# 4.8 Sintesi del capitolo

Mezza pagina. Gli effetti in fila **dal più grande al più piccolo**:

| | effetto su $F_2$ | soggetti per vederlo |
|---|---|---|
| definizione del compito | −0,309 | 2 |
| cambio di punto di vista | −0,334 | ~1 |
| cambio di dataset | crollo a 0,630 | — |
| architettura | 0,032 | decine |

Il messaggio: **l'architettura è l'ultima della lista.** Non anticipare il
Capitolo 5.
