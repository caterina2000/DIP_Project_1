# CHANGELOG — DIP_Project_1

Registro cronologico delle modifiche al codice. Piu' recente in alto.

Formato:

```
## 2026-10-01 --- Numeri a quattro o piu' cifre scritti a mano senza \num{}, trovati anche fuori dalle tabelle gia' corrette

### Il contesto

Dopo la sostituzione di `\num{}` (voce precedente), scansione dell'intera
tesi per numeri a quattro o piu' cifre scritti a mano senza separatore delle
migliaia, per verificare che non ne restassero fuori da quelle 48 occorrenze.

### Trovati 21 casi, tutti in tabelle di Cap4.tex e Cap5.tex

- `tab:loso` (Cap4.tex, righe 90-99): le dieci righe "Training windows" del
  prospetto LOSO (`9318`..`9300`) non erano mai state scritte con `\num{}`.
- `tab:confronto_architetture` (Cap4.tex, riga 297) e il paragrafo di commento
  subito sotto (riga 304): le colonne FP `1134` e `1266` (quest'ultima citata
  due volte).
- `tab:viste` (Cap4.tex, righe 792-807): le colonne "False positives" `3252`
  (due volte) e `1067`.
- Cap5.tex, riga 61: `1315~fps`, una misura descritta come viziata da un
  difetto di esecuzione (vedi il paragrafo "Some faulty measurements").
- Cap5.tex, riga 284: `4767` finestre negative, protocollo delle sessioni
  domestiche.
- `tab:falsi_positivi_giorno` (Cap5.tex, righe 296-297): `$\sim35345$`,
  `$\sim388800$`, `$\sim3751$` dentro modalita' matematica — non intercettati
  dalla prima scansione perche' preceduti da `\sim` senza spazio. Corretti
  con `{.}` dentro il `$...$`, come gia' si fa con `{,}` per i decimali
  altrove in tesi, per evitare la spaziatura che LaTeX darebbe a un punto
  trattato come punteggiatura in modalita' matematica.

**Non toccato:** `RK3576` (Cap5.tex, tre occorrenze) — e' il nome del SoC
Rockchip montato sulla scheda, non un numero da formattare.

### File toccati

`tesi/Cap4.tex` (16 sostituzioni), `tesi/Cap5.tex` (5, di cui 2 a mano per la
modalita' matematica).

**Verificato con:** scansione `[0-9]{4,}` su tutti i capitoli, esclusi anni e
`RK3576` — zero residui; `python tesi/controlla.py` -> nessun problema, 0
figure da produrre.

## 2026-10-01 --- \num{} sostituito da numeri separati a punto in tutti i capitoli inglesi

### Il contesto

Durante la ripresa della traduzione in inglese britannico, avevo inizialmente
segnalato come difetto l'uso della virgola decimale nel testo dei capitoli
(`0,874`, `0{,}04`...), confondendola con l'errore gia' corretto il 25
settembre nelle figure generate da `figure_tesi.py`. La candidata ha chiarito:
la virgola decimale resta corretta per i numeri decimali anche in inglese in
questa tesi; il problema vero e' un altro, cioe' l'uso del comando LaTeX
`\num{}` (pacchetto siunitx, non caricato/non verificato in questo progetto)
per i numeri a quattro o piu' cifre, da scrivere invece a mano con il punto
come separatore delle migliaia (`\num{234567}` -> `234.567`).

### Cosa cambia

Tutte le 48 occorrenze di `\num{...}` in `tesi/Cap1.tex`, `Cap3.tex`,
`Cap4.tex` e `Cap5.tex` sostituite con il numero scritto a mano, separatore
delle migliaia a punto, raggruppato a gruppi di tre cifre da destra (es.
`\num{116362}` -> `116.362`, `\num{1491}` -> `1.491`). Nessuna occorrenza in
Cap2.tex, Cap6.tex o Introduzione.tex. La virgola decimale non e' stata
toccata.

### File toccati

`tesi/Cap1.tex` (1 sostituzione), `tesi/Cap3.tex` (19), `tesi/Cap4.tex` (21),
`tesi/Cap5.tex` (7).

**Verificato con:** `grep -c '\\num{' tesi/*.tex` -> zero in tutti i file;
`python tesi/controlla.py` -> nessun problema, 0 figure da produrre.

## 2026-09-30 --- I tre compiti del Cap4 non sono i tre trattamenti del Cap3: due sistemi di etichette diversi

### La domanda

La candidata ha chiesto se le tre formulazioni elencate in `sec:compito`
(Cap3) e i tre compiti `evento` / `stato` / `allarme` di
`sec:compito-risultati` (Cap4) siano la stessa cosa, chiedendo di
verificarlo nel codice.

### La risposta, verificata nel codice: no

Sono **due assi distinti, costruiti su due sistemi di etichette diversi**.

- `src/etichettatura.py` definisce `MODI = ('scarta', 'caduta',
  'tre_classi')`, che operano sulle etichette **0/1/2 annotate a mano** con
  il criterio **K-su-M** (`_blocco_k_su_m`, `config.K_CADUTA=5`,
  `M_BLOCCO=8`, `K_TERRA=10`, `M_TERRA=15`). Sono quelli usati
  dall'esperimento principale, via `src/dati.py:282-287` -- cioe' tutte le
  tabelle su rappresentazioni, architetture e lunghezza della finestra. Il
  meccanismo `y_train = -1` descritto in Cap3 e' a `src/dati.py:284`.
- `pipeline/confronto_compiti.py` -- lo script che produce
  `risultati/compiti/foresta_DTW_cam1.json`, cioe' **`tab:compiti` del
  Cap4** -- definisce `COMPITI = {'evento': (FALL,), 'stato': (FALLEN,),
  'allarme': (FALL, FALLEN)}` sulle **classi OmniFall**
  (`g['classe_omnifall']`, riga 96) e con una regola diversa: una finestra
  e' positiva quando `np.isin(f, positive).sum() >= k_min` con `k_min=5`,
  cioe' un **conteggio totale**, senza blocco locale. E' esattamente la
  regola che Cap3 dichiara superata argomentando contro di essa.

### Le corrispondenze, una per una

| Cap3 (`etichettatura.MODI`) | Cap4 (`confronto_compiti.COMPITI`) |
|---|---|
| `scarta` | `evento` **solo concettualmente**: stesso positivo, ma `evento` NON esclude dall'addestramento le finestre di solo stato (valgono 0), mentre `scarta` le esclude (`y_train=-1`) |
| `caduta` | `allarme` (stesso positivo: transizione O stato) |
| `tre_classi` | **nessuno** |
| **nessuno** | `stato` (sola fase post-caduta) |

### Un errore mio, corretto

In un intervento precedente di questa serie avevo gia' toccato questa lista,
aggiungendo a Cap3 le corrispondenze "scarta = evento" e "caduta = allarme"
come se fossero identita'. Quella correzione era fondata sul commento di
`src/etichettatura.py` e **non** su `pipeline/confronto_compiti.py`, che e'
lo script che produce davvero la tabella del Cap4: le due mappature sono
concettuali, non operative, e presentarle come identita' era sbagliato.

### Corretto

- `tesi/Cap3.tex`, `sec:compito`: tolte dalle tre voci le corrispondenze
  presentate come identita'; aggiunto un paragrafo che dichiara
  esplicitamente che i tre trattamenti **non** sono i tre compiti del Cap4,
  con la mappatura corretta voce per voce e la differenza di base (etichette
  manuali + K-su-M contro classi OmniFall + conteggio totale).
- `tesi/Cap4.tex`, `sec:compito-risultati`: dichiarato, dove i tre compiti
  vengono introdotti, che i positivi sono definiti sulle annotazioni
  OmniFall e non sulle etichette annotate a mano, con la regola dei cinque
  fotogrammi e senza blocco locale; dichiarato che i negativi difficili
  (`lie_down`, `lying`) vengono dalla stessa base.

### Altro emerso, gia' coerente e non modificato

`pipeline/occlusioni.py` e `pipeline/rumore.py` leggono anch'essi
`classe_omnifall`: anche `tab:occlusioni` e `tab:rumore` del Cap4 poggiano
sulle annotazioni OmniFall. `pipeline/esporta_board.py` usa lo stesso schema
`COMPITI`, e il pacchetto installato dichiara infatti
`"compito": "evento"` -- coerente con quanto Cap5 riporta.

### File toccati

`tesi/Cap3.tex`, `tesi/Cap4.tex`.

**Verificato con:** lettura diretta di `src/etichettatura.py`,
`src/dati.py:265-293`, `pipeline/confronto_compiti.py:61-107`,
`pipeline/esporta_board.py:84`, `config.py:75-96`;
`grep -rn COMPITI\|classe_omnifall\|etichetta_finestra --include=*.py`;
`python tesi/controlla.py` -> nessun problema.

## 2026-09-30 --- DTWH nel codice, non in tesi: verificato che il tredicesimo assetto e sul dispositivo davvero installato

### La domanda della candidata

Un allegato con una riscrittura di `sec:ridondanza` (Cap3.tex) usava
`DTWH` come sigla formale con una `tab:sigle`, in un punto che alla
candidata non convinceva rispetto alla versione in repo. Richiesta:
controllare nel codice che cosa e' stato davvero fatto prima di riscrivere.

### Verificato nel codice

- `src/dati.py:colonne_di()`: `DTW` legge `risultati/dtw/scelte.txt` (dodici
  nomi); `DTWH` vi aggiunge `A3_h_pavimento` (tredici). La sigla `DTWH`
  esiste **solo nel codice e nei nomi dei file** (`pipeline/addestra.py`,
  `pipeline/esporta_board.py`, i `run_*_DTWH_*.json`, i pacchetti in
  `deploy_board/`) -- **non compare mai** in Cap3.tex, Cap4.tex o Cap5.tex,
  che descrivono lo stesso concetto in prosa piana ("dodici grandezze" /
  "tredici", "quello schierato" / "quello rivisto"). L'allegato della
  candidata avrebbe quindi reintrodotto un'incoerenza (un termine che
  Cap4/Cap5 non usano), non risolta una gia' esistente: non ripreso.
- `deploy_board/metadata.json` (il pacchetto live, creato 2026-09-09T19:40,
  606.409 byte): `"feature_set": "DTWH"`, tredici colonne, le stesse dodici
  di `scelte.txt` piu' `A3_h_pavimento`. **Confermato**: l'assetto a
  tredici grandezze, non quello a dodici, e' quello davvero installato
  sulla board per la sessione del 9 settembre che il Capitolo~5 descrive.
  Cap3.tex prima lo presentava solo come "una revisione... non mai stata
  la scelta di una procedura automatica", vero ma isolato dal resto della
  tesi: aggiunta una frase che rimanda esplicitamente al
  Capitolo edge.

### Un problema trovato per strada, non ancora risolto

Esistono DUE pacchetti datati 9 settembre: `deploy_board/
pacchetto_installato_20260909_1018/` (le 10:18, con `A2_angolo_tronco` e
`A3_ginocchia_rel_y` -- le due grandezze che la sezione sulla ridondanza
esclude per ridondanza) e `deploy_board/modello.pkl` attuale (le 19:40,
corretto: usa `A2_testa_rel_y` e `A3_caviglie\_rel_y` come `scelte.txt`).
Il CHANGELOG storico (voce del 2026-09-09, ISS-161) conferma che il primo
e' stato sostituito la sera stessa dopo un controllo di parita' fallito.

Cap5.tex, `tab:risorse`, dichiara il classificatore "592 kB". Il pacchetto
delle 10:18 pesa 592.329 byte (592 kB in base 1000); il pacchetto corretto
delle 19:40 pesa 606.409 byte, che sono **592 KiB in base 1024** -- lo
stesso numero "592", per due file diversi, con due convenzioni diverse.
Non e' stato possibile stabilire con certezza a quale dei due si riferisse
la cifra gia' in tesi: **segnalato alla candidata, non corretto da solo**,
perche' richiede sapere quale pacchetto sia stato pesato quando la riga e'
stata scritta.

### File toccati

`tesi/Cap3.tex`.

**Verificato con:** lettura diretta di `src/dati.py`, `deploy_board/
metadata.json`, `deploy_board/pacchetto_installato_20260909_1018/
metadata.json`, `risultati/dtw/scelte.txt`, `docs/CHANGELOG.md` (voce
2026-09-09); `grep -n DTWH tesi/Cap4.tex tesi/Cap5.tex` -> nessuna
occorrenza; `python tesi/controlla.py` -> nessun problema.

## 2026-09-29 --- Il divario di viewpoint era rimasto a 0,422 (cinque soggetti) in tre capitoli su quattro

### Segnalato dalla candidata

Riportando l'analisi di una revisione fatta con un altro assistente sulle
bozze di Cap6, la candidata ha chiesto di risolvere una discordanza sul
divario di $F_2$ fra le due telecamere prima di qualunque altro intervento
sul capitolo di discussione.

### Verificato

`tab:viste` in Cap4.tex (dieci soggetti, gia' riscontrata piu' volte in
questa sessione contro i dati) dice $0{,}822 \to 0{,}488$, divario
$0{,}334$. Cercando `0{,}422` nel resto della tesi (il valore va cercato con
la graffa LaTeX, non come "0,422" letterale) sono risultate TRE citazioni
del vecchio numero, tutte provenienti dall'impianto preliminare a cinque
soggetti ($0{,}857 \to 0{,}434$) e mai aggiornate quando Cap4 e' stato
rifatto a dieci:

- `Introduzione.tex`: citava anche **26,5 fps / 88,4% / 5,8%** come
  prestazioni del sistema installato -- lo stesso valore che Cap5.tex aveva
  gia' ritirato esplicitamente in un intervento precedente di questa
  sessione (paragrafo "Il vecchio valore, e perche' non viene usato"), ma
  che l'Introduzione non aveva mai recepito. Corretto in **7,3 fps /
  85,2% / 14,3%**.
- `Cap6.tex`: usava $0{,}422$ nella risposta "Quanto pesa il punto di
  vista?" e nella sezione Conclusione.
- `Conclusioni.tex`: usava $0{,}422$ due volte, una delle quali con un
  commento che lo dichiarava esplicitamente "misura a cinque soggetti, non
  ripetuta su dieci" -- corretto, perche' nel frattempo la ripetizione a
  dieci soggetti (Cap4) e' stata fatta, e il commento non serve piu'.

### Corretto

Sostituito $0{,}422$ / $0{,}857$ / $0{,}434$ con $0{,}334$ / $0{,}822$ /
$0{,}488$ in `Introduzione.tex`, `Cap6.tex`, `Conclusioni.tex` (incluso il
"più di cinque/sei volte tanto" ricalcolato: $0{,}334/0{,}079 \approx 4{,}2$,
non 5 o 6). Aggiornata anche la nota interna in testa a `Conclusioni.tex`
che indicava ancora 0,422 come valore da citare.

### Altre due correzioni di stile chieste nella stessa revisione

- Rimossa da `Cap6.tex` la frase "anche un classificatore istantaneo
  lascerebbe il sistema dove si trova": una formulazione piu' retorica che
  informativa, secondo la candidata.
- Riscritta la sezione Conclusione di `Cap6.tex`: tolto il riferimento a un
  "criterio clinico di uno o due allarmi alla settimana" mai definito ne'
  fondato su una fonte in nessun punto della tesi (non citare soglie
  cliniche senza un riferimento verificato), e ammorbidita la formulazione
  assoluta "l'ipotesi tecnica non e' verificata" in una lettura ancorata
  ai numeri (0,079 contro 0,334). Aggiunta la chiusura "il benchmark resta
  necessario ma non basta a prevedere il comportamento in esercizio",
  richiesta esplicitamente.

### File toccati

`tesi/Introduzione.tex`, `tesi/Cap6.tex`, `tesi/Conclusioni.tex`.

**Verificato con:** `grep` per `0{,}422` e per `26,5` su tutta `tesi/*.tex`
-> zero residui; `python tesi/controlla.py` -> nessun problema.

## 2026-09-29 --- fig_compiti_casa_en: le etichette sulle barre erano in italiano

### Il difetto

Segnalato dalla candidata: `fig_compiti_casa_en.png` mostrava "1,6 eventi/h"
e "3 cadute su 5" invece delle etichette inglesi, mentre assi e titolo erano
gia' tradotti correttamente.

### La causa

In `pipeline/figure_tesi.py`, `fig_compiti_casa()`, le due stringhe di testo
sopra le barre erano scritte come letterali italiani fissi
(`'  eventi/h'`, `'\n{} cadute su 5'`) invece di passare per `T(it, en)`
come fa il resto della funzione (assi, titolo) e come fa la funzione gemella
`fig_compiti()` per il grafico di laboratorio, che non aveva questo difetto.

### Corretto

`pipeline/figure_tesi.py`: le due stringhe ora usano `T('  eventi/h',
'  events/h')` e `T('\n{} cadute su 5', '\n{} falls out of 5')`.
Rigenerate `fig_compiti_casa.png` e `fig_compiti_casa_en.png` con
`python pipeline/figure_tesi.py --lingua en` (e la corrispondente passata
`it`, gia' allineata prima del fix -- rigenerata comunque per verifica).
Controllate anche le altre occorrenze di testo con l'aspetto di
un'etichetta grafica nel file (`grep` per "falsi allarmi", "eventi/h",
"cadute su"): le uniche altre trovate erano gia' dentro `T(...)` o dentro
le schede di provenienza `.txt`, che restano in italiano per costruzione.

### File toccati

`pipeline/figure_tesi.py`, `tesi/figure/fig_compiti_casa.png`,
`tesi/figure/fig_compiti_casa_en.png` (e le figure sorelle rigenerate dalla
stessa passata `--lingua en`, invariate nel contenuto).

**Verificato con:** ispezione visiva di entrambe le lingue;
`python tesi/controlla.py` -> nessun problema.

## 2026-09-29 --- tab:costo_installato: la riga "altre operazioni" resa esplicita, con la percentuale giusta

### Il confronto

La candidata ha riproposto `tab:costo_installato` con una terza riga
esplicita, "Altre operazioni" (0,76 ms), al posto di lasciare lo scarto
spiegato solo in prosa come faceva la repo. L'idea e' buona: rende la
tabella la fonte primaria e la prosa un commento, non il contrario.

### Che cosa non tornava

La sua riga riportava **0,5\%** per 0,76/136,65 ms. Calcolato:
0,76/136,65 = 0,556%, che arrotonda a **0,6\%** -- lo stesso valore che la
prosa della repo gia' dichiarava correttamente. Errore di arrotondamento
nella sua tabella, non nella repo.

Anche la colonna "catena accelerata" per quella riga (lei: 2,16 ms) e'
stata ricontrollata: e' la somma di pre-elaborazione e post-elaborazione
di `tab:costo` (1,21+0,94), che fa 2,15 ms e non 2,16. Non e' stato
possibile verificare oltre i due decimali gia' pubblicati: la didascalia
di `tab:costo` dichiara gia' che quei valori vengono trascritti a mano dal
terminale di un banco di prova, senza file sorgente con precisione
maggiore (verificato: nessun log o JSON contiene la ripartizione
pre/percezione/post/classificatore di quella catena).

### Applicato

`tesi/Cap5.tex`, `tab:costo_installato`: aggiunta la riga "Altre
operazioni" con 0,76 ms / **0,6\%** / 2,15 ms. Il paragrafo che prima
si intitolava "Perche' le due voci non sommano al totale" e' stato
riscritto in "Che cosa sono le 'altre operazioni'", perche' ora la somma
torna gia' in tabella e il paragrafo serve a spiegare la composizione
della voce, non piu' a giustificarne l'assenza.

### File toccati

`tesi/Cap5.tex`.

**Verificato con:** calcolo diretto (0,76/136,65 -> 0,6%; 1,21+0,94 ->
2,15); `python tesi/controlla.py` -> nessun problema.

## 2026-09-28 --- Le sette voci proposte dalla candidata, verificate e citate

### Su richiesta esplicita

Dopo la rinomina delle chiavi bibliografiche, la candidata ha chiesto di
riguardare tutte le voci del suo elenco: spiegare perche' alcune non erano
state inserite, dire per ognuna DOVE andrebbe citata nel testo, e tenere
quelle che non erano ancora state aggiunte.

### Risolto lo scambio di chiave LI/RL

Il file della candidata conteneva due `\bibitem{LI}` diversi (Liu et al. sui
sensori indossabili; R. Li et al. sul riconoscimento di azioni da
scheletro). Assegnata `RL` al secondo. Nessuno dei due, verificato di nuovo,
sostiene la frase di Cap2.tex riga 23 sui sensori AMBIENTALI per cui `LI`
era stato originariamente scritto: quella frase ora non ha citazione,
dichiarata apertamente come buco nella nota finale del file.

### Le sette citate, e dove

- **HO** (gia' aggiunta in precedenza) resta dov'era.
- **LI** (Liu et al., sensori indossabili): Cap2.tex, sez. "Dispositivi
  indossabili", che non aveva alcuna citazione.
- **RL** (R. Li et al., descrittore per segmenti chiave): Cap2.tex riga 93,
  come esempio concreto di feature costruite a mano su scheletro, accanto
  a `\cite{HO}`.
- **MP** (Lugaresi et al., rinominata da LU su richiesta della candidata):
  Cap3.tex, dove i tre stimatori di posa confrontati vengono elencati per
  la prima volta.
- **NIE3D** (Nie, Wei, Zhu): Cap2.tex riga 87, sulla stima di profondita'
  da una singola vista. ATTENZIONE: le pagine fornite dalla candidata
  (3447-3455) non coincidono con quelle trovate in ricerca (3467-3475);
  corrette con riserva, da controllare su IEEE Xplore prima della
  consegna.
- **DILL2024** (Dill et al.): Cap3.tex, sez. A2, dove si introduce la
  profondita' dei *world landmark* di MediaPipe -- e' lo stesso strumento
  che quel lavoro valuta.
- **RA** (Rahmani, Bennamoun): Cap2.tex riga 101, sul limite di
  invarianza al punto di vista delle normalizzazioni usuali.
- **SK** (Feng, Meunier): Cap2.tex riga 147, dove le Graph Convolutional
  Network sono introdotte senza un riferimento dedicato.
- **ZH** (Zhang, Wang, Fan, 2026): Introduzione.tex, aggiunta come quarta
  causa del divario laboratorio/realta', accanto a protocollo, cadute
  simulate e ambiente. Pubblicazione molto recente (2026): da
  ricontrollare piu' vicino alla consegna.
- **AM** (Scheurer et al., AIDE-MOI; gia' presente ma mai citata):
  Cap1.tex, subito dopo la cifra di Kangas sui falsi allarmi, come esempio
  di riduzione del tasso ottenuta per intervento sull'algoritmo.

### File toccati

`tesi/Bibliografia.tex`, `tesi/Cap1.tex`, `tesi/Cap2.tex`, `tesi/Cap3.tex`,
`tesi/Introduzione.tex`.

**Verificato con:** `python tesi/controlla.py` -> **nessun problema**
(prima volta in questa serie di interventi: zero citazioni non definite,
zero figure mancanti); `grep` per chiavi duplicate -> nessuna voce attiva
ripetuta.

## 2026-09-28 --- Bibliografia: chiavi a due lettere, ordine alfabetico, verifica delle fonti della candidata

### Su richiesta esplicita

Rinominare tutte le chiavi \bibitem/\cite dalla forma descrittiva attuale
(`mediapipe`, `scheurer`, `kangasreali`...) a due lettere maiuscole,
iniziali del cognome del primo autore (esempio dato: `PI`), e riordinare
`Bibliografia.tex` alfabeticamente per autore invece che per tema.

### Verifica delle fonti fornite dalla candidata

Sette voci nuove (allegate dalla candidata in chat, chiavi FN/IS/PA/KA/GU/
MU/LI/HO/LIN/SC/SA/BL/MP/NIE3D/DILL2024/RA/SK/ZH) confrontate con l'uso
reale di `\cite{}` nel testo e verificate via ricerca web dove il
contenuto non era gia' marcato VERIFICATO in repo:

- **HO** (Hoang et al., IEEE Access 2023): esiste, titolo/autori/pagine
  confermati (IEEE Xplore, doc. 10225507). Aggiunta.
- **LI**: la candidata ha fornito DUE voci diverse con la stessa chiave
  (Liu et al. sui sensori indossabili; R. Li et al. sul riconoscimento di
  azioni da scheletro) -- un bug nel suo file, la seconda `\bibitem`
  avrebbe zittito la prima. Entrambe le voci ESISTONO (verificate via
  ricerca web), ma **nessuna delle due corrisponde al punto in cui
  `\cite{LI}` viene davvero usato**: Cap2.tex, sezione "Sensori
  ambientali" (pressione, vibrazione, acustica, infrarossi), non
  indossabili ne' skeleton-based. Resta non definita; serve un riferimento
  sui sistemi ambientali, annotato come tale in fondo a Bibliografia.tex.
- **PA**: la pagina che la candidata ha allegato esiste (ISS, titolo
  identico a quello gia' in repo), ma e' l'edizione **precedente**
  (comunicato del 31 ottobre 2024, biennio 2022-2023, 21%/16%/33%/25%/16%)
  gia' scartata da questo progetto il 2026-08-31 (ISS-123) a favore di
  quella corretta (31 ottobre 2025, biennio 2023-2024, 20%/15%/31%/24%/15%,
  gia' `\bibitem{PA}` in repo). Non sostituita: verificato via WebFetch
  sulla pagina ISS che i due comunicati condividono lo stesso titolo e
  differiscono solo nei numeri -- un rischio di errore concreto se si cita
  "PASSI d'Argento" senza l'anno del comunicato.
- FN/IS/GU/MU/SC/SA/BL gia' presenti in repo con contenuto identico sotto
  altra chiave: nessuna voce nuova, solo la rinomina.
  NIE3D/DILL2024/RA/SK/ZH: riferimenti reali (verificati via ricerca web:
  Nie et al. ICCV 2017, Dill et al. Sensors 2024 DOI 10.3390/s24237772,
  Rahmani & Bennamoun ICCV 2017, Feng & Meunier Sensors 2022, Zhang et al.
  Frontiers in Medicine 2026) ma **non citati da nessuna parte nel testo
  attuale**: non aggiunti, segnalati alla candidata come candidati.

### La rinomina

Script ad-hoc: sostituzione esatta di ogni `\cite{vecchia-chiave}` nei
file inclusi da `tesi.tex` (Cap1-5, Introduzione; esclusi i `da_incorporare/`
e `fig_pipeline.tex`, non inclusi nel documento), poi riscrittura completa
di `Bibliografia.tex` in ordine alfabetico. Le due collisioni fra cognomi
uguali (Ho / Hoang / Hochreiter; Kangas 2012 e 2015; Scheurer 2019 e 2020)
sono risolte con chiavi distinte (`TH`/`HO`/`HS`; `KR`/`KA`;
`AM`/`SC`) e un commento incrociato in ciascuna voce che spiega la
differenza, perche' due lettere sole non bastano a distinguerle da sole.
Le note di provenienza/verifica di ogni voce sono state conservate
verbatim; le sole rimosse sono due commenti ormai obsoleti (un'etichetta
"SEGNAPOSTO" che non descriveva piu' nessuna voce reale, la vecchia nota
di raggruppamento tematico superata dall'ordine alfabetico).

### File toccati

`tesi/Bibliografia.tex` (riscritto), `tesi/Cap1.tex`, `tesi/Cap2.tex`,
`tesi/Cap3.tex`, `tesi/Cap4.tex`, `tesi/Cap5.tex`, `tesi/Introduzione.tex`.

**Verificato con:** `python tesi/controlla.py` -> stesso singolo problema
di prima (`LI` non definita), nessuna citazione rotta dalla rinomina;
`grep` per chiavi duplicate in Bibliografia.tex -> 32 voci attive, tutte
uniche; ricerca web per le sette fonti nuove elencate sopra.

## 2026-09-28 --- Confronto dato per dato fra Cap3-4-5 e la bozza della candidata

### Il metodo

Su richiesta esplicita della candidata: ignorare titoli e prosa dei suoi
allegati Cap3/Cap4/Cap5.tex (gia' un adattamento del testo di repository) e
confrontare **solo dati** -- tabelle, numeri, cio' che i numeri descrivono --
capitolo per capitolo, correggendo dove i due non tornano.

### Cap3 -- tre punti, due confermati un dato aggiunto

- Visibilita' naso/spalle/anche: l'allegato diceva "superiori a 0,99", la
  repo "sopra 0,98". Verificato contro `docs/CHANGELOG.md` (EXP-052,
  `scripts/occlusioni_mediapipe.py`, 26.548 fotogrammi): **0,98 e' il valore
  giusto**. Nessuna modifica, l'allegato ha un refuso.
- Punteggio DTW di $h_{\text{pav}}$: l'allegato riporta 1,541 (cam1, secondo
  punteggio piu' alto delle 33), 1,124 (cam2), divario 0,417 -- assenti dalla
  repo, che si limitava a "ventunesima su 33". Verificato riga per riga
  contro `risultati/dtw/log_dtw_v5_top12.txt`: **esatti**. Aggiunti al
  paragrafo "Che cosa il criterio non puo' vedere" di `sec:ridondanza`.
- La contraddizione gia' nota su $L=22$ ("non avendo riscontrato un
  miglioramento sistematico...") e' presente nell'allegato ma gia' corretta
  in repo da un intervento precedente di questa stessa sessione: nessuna
  azione nuova.

### Cap4 -- due punti

- "Un riequilibrio completo richiederebbe di eliminare circa tre quarti delle
  finestre negative": con 1.491 positive su 11.719 (10.228 negative), il
  conto esatto e' $(10228-1491)/10228=85{,}4\%$, non 75\%. **Corretto**
  (`Cap4.tex`, `sec:metriche`).
- `tab:compiti` (evento/stato/allarme): i valori dell'allegato ($F_2$
  0,831/0,704/0,810) non corrispondono in alcun modo a
  `risultati/compiti/foresta_DTW_cam1.json`, che la repo riproduce
  esattamente (0,415/0,587/0,830, con recall/precision/negativi-difficili
  tutti verificati). Nessuna modifica alla repo: la tabella dell'allegato
  va sostituita per intero, non e' un refuso isolato.

### Cap5 -- due dati verificati e aggiunti

- "Su 56 clip, 55 hanno prodotto la stessa decisione finale [...] in una sola
  registrazione contenente una caduta la decisione e' risultata diversa":
  assente dalla repo (che passava dal test sulle 200 finestre precalcolate
  direttamente ai tre aneddoti sui banchi di prova falliti). Verificato
  confrontando riga per riga `risultati/board/scansione_56clip_board.txt` e
  `scansione_56clip_pc.txt` sulla colonna della decisione finale: **su 56
  righe ne differisce esattamente una**, `evt_0067_155044` (punteggio
  0,560 sul PC contro 1,000 sulla board, entrambi con finestre sopra
  soglia). Aggiunto a `sec:parita`.
- Il richiamo 4/5 ($0{,}80$) ottenuto con tolleranza $\pm90$s e persistenza 1
  non aveva un intervallo di confidenza dichiarato. Calcolato l'intervallo
  esatto di Clopper--Pearson al 95\%: $[0{,}28,\ 0{,}99]$, che conferma il
  valore dell'allegato. Aggiunto a `sec:recall-campo`.
- `tab:risorse`: l'allegato riporta 578~kB/1,2~kB/816~kB per
  classificatore/scaler/pacchetto e "memoria occupata: non misurata". La
  repo riporta 592~kB/1,1~kB/623~kB e un picco di memoria misurato
  (297~MB). Verificato contro i file realmente installati in
  `deploy_board/pacchetto_installato_20260909_1018/`: `modello.pkl` pesa
  592.329 byte, `scaler.pkl` 1.178 byte -- **la repo e' quella corretta e
  aggiornata**, l'allegato e' una bozza precedente alla misura di memoria.
  Nessuna modifica alla repo.

### File toccati

`tesi/Cap3.tex`, `tesi/Cap4.tex`, `tesi/Cap5.tex`.

**Verificato con:** `python tesi/controlla.py` -> restano solo le 2
citazioni non definite (`HO`, `LI`); riscontro numerico diretto (script
Python ad-hoc) contro `risultati/dtw/log_dtw_v5_top12.txt`,
`risultati/compiti/foresta_DTW_cam1.json`,
`risultati/board/scansione_56clip_{board,pc}.txt`,
`deploy_board/pacchetto_installato_20260909_1018/{modello,scaler}.pkl`;
calcolo diretto per l'85,4\% e per l'intervallo di Clopper--Pearson.

## 2026-09-28 --- fig_dtw_spiegazione: legenda fuori dal grafico e uno zoom per capire il pannello (b)

### Il problema

Due difetti segnalati dalla candidata dopo la prima revisione della figura:
la legenda del pannello (b) stava sovrapposta alla matrice, sopra i dati; e
il pannello (b) da solo non si capiva, perche' la banda del DTW e' larga solo
10 campioni su una matrice 200x200 e a quella scala si confonde visivamente
col cammino stesso.

### Corretto

- `pipeline/figura_dtw.py`: rimosse le due legende interne (`ax1.legend`,
  `ax2.legend`) e sostituite con un'unica `fig.legend` sotto l'intera figura,
  fuori dagli assi.
- Aggiunto un terzo pannello (c), uno zoom sul tratto in cui il cammino del
  DTW si allontana di piu' dalla diagonale mantenendosi dentro la banda: alla
  scala ingrandita banda, diagonale e cammino sono nettamente distinti. Il
  riquadro che delimita la zona ingrandita e' disegnato anche sul pannello
  (b), con un'etichetta, per non lasciare lo zoom scollegato dal resto.
  La ricerca della zona da ingrandire esclude i 20 campioni ai due bordi
  della sequenza (fase pressoche' costante precedente alla caduta): li' il
  costo e' quasi zero ovunque e lo scostamento dalla diagonale e' un
  artefatto del pareggio fra cammini equivalenti, non la deformazione dovuta
  allo sfasamento del picco che la figura vuole mostrare.
- `tesi/Cap3.tex`, didascalia di `fig:dtw_allineamento`: riscritta per
  descrivere i tre pannelli invece di due.
- Rigenerata in entrambe le lingue.

### File toccati

`pipeline/figura_dtw.py`, `tesi/figure/fig_dtw_spiegazione.png`,
`tesi/figure/fig_dtw_spiegazione_en.png` (e le rispettive schede `.txt`),
`tesi/Cap3.tex`.

**Verificato con:** ispezione visiva di entrambe le figure rigenerate;
`python tesi/controlla.py` -> restano solo le 2 citazioni non definite
(`HO`, `LI`); lo script conferma ancora, a ogni esecuzione, che la distanza
della matrice intera disegnata coincide con quella di `src.dtw` a meno di
1e-9.

## 2026-09-28 --- Cap5: due frasi tagliate a meta' e una figura mai inserita

### La verifica

Su richiesta esplicita della candidata ("voglio la certezza 100%"), rilettura
integrale e fresca di tesi/Cap5.tex (1465 righe prima di questo intervento),
con riscontro numerico diretto delle tabelle contro i file sorgente in
risultati/campo/ e risultati/cinque_soggetti/ dove identificabili.

### Trovato e corretto

- Riga 5: la frase di apertura del capitolo era un frammento senza verbo
  principale ("Una volta stabilito ... difendibile." seguito da un punto e
  poi una nuova frase): riscritta come periodo unico e completo.
- sec:rovesciamento, apertura della sottosezione "Confronto delle
  configurazioni nei due domini": la frase "Sono considerate cinque
  configurazioni costruite progressivamente a partire" si interrompeva a
  meta' e non aveva seguito. Rimossa: il contenuto che avrebbe dovuto
  completarla era gia' presente, per intero, due paragrafi sotto ("Le cinque
  configurazioni confrontate partono tutte dalla rappresentazione A3...").
- La figura della foto reale della caduta sulla board (fig_caduta_board,
  gia' generata da pipeline/figura_caduta_board.py con il volto pixelato)
  non era mai stata effettivamente inserita nel corpo di Cap5.tex, nonostante
  fosse gia' citata da tesi/Cap6.tex (`\ref{fig:caduta_board}` senza alcuna
  label corrispondente in tutta la tesi: `python tesi/controlla.py` lo
  segnalava). Inserita nella sec:campo subito dopo la descrizione della
  prima caduta della sessione del 9 settembre.

### Riscontro numerico (tutto combacia)

Valori di tab:compiti_casa, tab:configurazioni, tab:controesempi_cross e
tab:kappa confrontati cifra per cifra con risultati/campo/compiti_in_casa.json,
risultati/campo/valutazione_10sog_k31.json,
risultati/campo/valutazione_incrociata_10sog.json e
risultati/cinque_soggetti/scansione_k_cinque_soggetti.json: corrispondenza
esatta su tutte le celle. Stesso esito per il fattore di sovrastima 44,8, le
14,98 ore totali e gli 11,1 eventi/ora (risultati/campo/eventi_sessioni.json)
e per la scomposizione della latenza in tab:latenza
(risultati/campo/latenza.json).

### File toccati

`tesi/Cap5.tex`.

**Verificato con:** lettura integrale di tesi/Cap5.tex (tutte le 1481 righe
dopo l'intervento); `python tesi/controlla.py` -> restano solo le 2 citazioni
non definite (`HO`, `LI`), che richiedono un riferimento bibliografico reale
dalla candidata; riscontro numerico via script Python ad-hoc contro i 5 file
JSON elencati sopra.

## 2026-09-28 --- Il commento del codice era sbagliato quanto la tesi: 'caduta' non e' 'stato'

### La scoperta

Confrontando i nomi dei tre compiti fra Cap3 (metodologia) e Cap4/Cap5
(risultati): Cap3 chiamava le tre strategie di etichettatura `scarta` /
`caduta` / `tre classi`, Cap4 e Cap5 chiamano i tre compiti valutati `evento`
/ `stato` / `allarme`. Andando a cercare la corrispondenza nel codice
(`src/etichettatura.py`) e' emerso che il DOCSTRING stesso e' fuorviante: per
`modo == 'caduta'` dice *"il sistema rileva lo STATO invece dell'EVENTO"*, ma
la riga di codice due sotto fa `1 if (terra or caduta) else 0` --- riconosce
l'uno O l'altro, non sostituisce l'uno con l'altro. Corrisponde quindi al
compito che Cap4/Cap5 chiamano **allarme**, non **stato**. Il compito
**stato** (solo la fase post-caduta) non e' fra i tre `MODI` di
`etichettatura.py`: e' costruito a parte in `pipeline/esporta_board.py`
(`COMPITI = {'evento': (1,), 'stato': (2,), 'allarme': (1, 2)}`), per
l'esperimento di confronto fra compiti.

### Corretto

- `src/etichettatura.py`: il commento del modo `'caduta'` non dice piu' che
  "riconosce lo stato invece dell'evento" (falso, la riga sotto lo
  smentisce); dice che riconosce l'uno O l'altro, ed e' annotato come
  corrispondente al compito "allarme" della tesi. Aggiunta la corrispondenza
  anche per `'scarta'` (= "evento").
- `tesi/Cap3.tex`, `sec:compito`: la voce `caduta` non dice piu' che il
  sistema "riconosce lo stato invece dell'evento" (stesso errore, ricalcato
  dal commento del codice). Aggiunta la corrispondenza esplicita con i nomi
  usati nel Capitolo~4: scarta=evento, caduta=allarme, e una frase che
  dichiara che tre classi e' un asse diverso (numero di classi, non
  definizione del positivo) e che il compito "stato" non e' fra questi tre
  trattamenti.

### File toccati

`src/etichettatura.py`, `tesi/Cap3.tex`.

**Verificato con:** lettura diretta di `src/etichettatura.py:89-155`
(`etichetta_finestra`, `MODI`) e `pipeline/esporta_board.py:84`
(`COMPITI`); `python tesi/controlla.py` -> gli stessi 2 problemi (`HO`, `LI`).

## 2026-09-28 --- fig_dtw_spiegazione: titolo e legenda non piu' a ridosso, e una scansione di prosa

### fig_dtw_spiegazione

Il titolo del pannello (b) e la sua legenda, posizionata `upper left` subito
sotto, avevano poco margine fra loro (`pad=9`). Aumentato il margine dei due
titoli (`pad=16`), spostata la legenda del pannello (b) di un margine
esplicito dal bordo (`bbox_to_anchor`), e aggiunto `subplots_adjust(top=0.87)`
dopo `tight_layout()` per garantire aria anche se la resa cambia. Rigenerata
in entrambe le lingue.

### Confermato: 2.4.3 anticipa gia' il leakage da finestre sovrapposte

Era l'unico punto della lettera del relatore non ancora riverificato di
persona. C'e' gia', con tanto di commento `[RELATORE 2026-09-14]` che lo
conferma. Nessun intervento necessario.

### Scansione automatica di Cap3/Cap4/Cap5 per ripetizioni e frasi lunghe

Nessuna frase quasi duplicata trovata in nessuno dei tre capitoli, e i
connettivi meccanici segnalati dal relatore («va detto che», ecc.) compaiono
una sola volta ciascuno: la prosa non risulta ripetitiva in modo sistematico.
Accorciate le poche frasi genuinamente lunghe trovate (non gli artefatti di
tabelle/elenchi che lo script confondeva con prosa): in Cap4 il paragrafo
sulla cadenza dichiarata/misurata, in Cap5 tre frasi della Discussione appena
scritta, compresa quella sul caso della sospensione.

### File toccati

`pipeline/figura_dtw.py`; `tesi/Cap4.tex`, `tesi/Cap5.tex` (accorciamenti).

**Verificato con:** `python tesi/controlla.py` -> gli stessi 2 problemi
(`HO`, `LI`).

## 2026-09-28 --- La Discussione risponde alle otto domande, una foto reale con la faccia oscurata

### La Discussione riscritta

La versione precedente (25/9) rispondeva a RQ1/RQ2/RQ3, che coprono solo in
parte le otto domande esplicite della lettera del relatore. Riscritta con un
paragrafo per domanda, nell'ordine della lettera:

1. architettura vs rappresentazione --- entrambe piccole SUL BENCHMARK
   (0,079 e 0,007), il divario vero (fattore 52) si vede solo fuori; il
   confronto fra architetture non e' mai stato ripetuto li', ed e' dichiarato
   come limite invece che esteso implicitamente;
2. costo di un soggetto mai visto --- dispersione fra fold 0,08-0,14, piu' un
   riscontro indipendente (89% -> 76% k-fold vs per-soggetto, gia' nei
   Contributi);
3. punto di vista --- 0,422 di F2, gia' in discussione;
4. dataset esterno --- **prima mancante**: PR-AUC 5,1x contro 3,4x, F2
   0,825 -> 0,630 con il sottoinsieme DTW, contro il crollo a 0,034 della
   configurazione precedente; la scomposizione calibrazione/capacita' non e'
   stata rifatta sull'assetto adottato, dichiarato come limite;
5. finestre contro allarmi --- fattore 44,8, gia' in discussione;
6. collo di bottiglia edge --- percezione 85,2% contro 14,3%, gia' in
   discussione;
7. *failure mode* residui --- **prima non enumerati come risposta a se'**:
   la sospensione che sopprime una caduta vera (9 settembre), la stima del
   pavimento che non converge sotto i 15 s, le cinque cadute come indizio e
   non stima;
8. generalizzazione da due abitazioni --- gia' aggiunta il 26/9.

### fig_caduta_board: la sola fotografia di una persona reale nella tesi

Inserita su richiesta esplicita della candidata, con la faccia oscurata.
Fonte: `deploy_board/sessioni/20260909_v5/clip/f00856.0.jpg`, il fotogramma
annotato dalla board un istante prima del primo allarme della sessione del
9 settembre (punteggio 0,760, raffica 4/5). La faccia e' **pixelata a blocchi
di 12 px**, non sfocata: la pixelazione distrugge l'informazione, uno
sfocamento gaussiano e' in alcuni casi parzialmente invertibile. Nuovo script
`pipeline/figura_caduta_board.py`. Citata in Cap5 subito dopo la frase sulla
prima caduta.

### fig_stanza: sorgente sostituita

La foto usata finora (`~/rileva/inquadratura.jpg`, ritagliata di 170 px per
togliere un oggetto personale sul bordo) e' sostituita da un fotogramma reale
della sessione `20260909_diretta` (nessuna persona in scena): risoluzione
migliore, l'oggetto non compare perche' l'inquadratura e' diversa, nessun
ritaglio arbitrario. I due riquadri (superficie rialzata, area di caduta)
sono stati ricalibrati sulla nuova immagine, verificati disegnandoli e
riguardandoli prima di scrivere il file definitivo.

### Un difetto trovato per caso

`fig_popolazione_en.png` risultava mancante su disco (probabile effetto di
una pulizia precedente), e `controlla.py` lo ha segnalato appena toccato un
file vicino. Rigenerata con `figura_popolazione.py --lingua en`.

### File toccati

`tesi/Cap5.tex` (Discussione riscritta, due figure nuove citate);
`pipeline/figura_caduta_board.py` (nuovo); `pipeline/figura_stanza.py`
(sorgente e coordinate); `tesi/figure/sorgenti/inquadratura_board.jpg`
(sostituita).

**Verificato con:** `python tesi/controlla.py` -> restano i soliti 2
problemi (`HO`, `LI`); ogni nuova citazione incrociata (`sec:featureset`,
`sec:loso`, `cap:conclusioni`, `sec:domainshift`, `sec:finestre-eventi`,
`sec:costo-computazionale`, `sec:limiti-operativi`, `sec:rovesciamento`)
verificata esistere prima di scriverla; la faccia oscurata riverificata a
occhio con un ritaglio ingrandito, nessun tratto riconoscibile residuo.

## 2026-09-26 --- Due sottosezioni vuote in Cap5, la premessa v2-v5 verificata, e una guida alla difesa

### Cap5: due `\subsection` erano vuote

Riguardando il capitolo dall'inizio alla fine: `\subsection{Costo
computazionale e frequenza di elaborazione}` non aveva una riga di testo
prima che si aprisse `\subsection{Stabilita' termica...}` subito dopo. Tutto
il confronto fra catena accelerata e catena installata --- che parla di
COSTO, non di temperatura --- finiva quindi sotto l'intestazione sbagliata.
Stessa cosa fra `Motivazione della valutazione in campo` (vuota) e
`Protocollo delle sessioni domestiche`: il discorso sul perche' le metriche
di laboratorio non bastano finiva sotto l'intestazione del protocollo vero.

Corretto spostando ciascuna intestazione al punto in cui il suo tema comincia
davvero. Trovata e saldata anche una frase spezzata in due chiusure diverse
(sulla ripartizione 88,4%/5,8% della catena accelerata, mai adottata). Aggiunta
una frase che mancava: perche' il conteggio di campo passa da dodici blocchi
iniziali a nove sessioni aggregate (quattro erano prove di pochi minuti, sotto
`--min-ore` di `eventi_sessioni.py`).

### La premessa "da v2 a v5 e' cambiato solo il dt" era incompleta

Verificato sui changelog e sui file delle feature. Non e' cambiato solo il
tempo:

- **v2 -> v3 (6 settembre):** `A3_h_pavimento` non esisteva nel motore
  (32 grandezze, non 33); lo stimatore di posa era UNICO per tutte le 220
  riprese invece che uno per ripresa; **218 -> 220 registrazioni**. Effetto
  misurato: la classifica delle sei architetture si rimescola per intero
  (Spearman v2 vs v3 = **-0,03**, la LSTM passa da prima a quinta). Non
  riguarda il dt.
- **v3 -> v4 (8 settembre):** il dt istantaneo delle derivate, corretto per
  primo perche' muove un solo parametro. Effetto **non distinguibile dal
  caso** (t=-1,15 contro critico 2,262): la selezione DTW aveva gia' scelto
  soprattutto integrali, che non dipendono da dt.
- **v4 -> v5 (9 settembre):** QUESTO e' il cambio di dt che conta --- il
  buffer degli integrali diventa una durata in secondi invece di un conteggio
  di fotogrammi. A 18 fps il motore produce valori identici bit per bit; a
  9 e 7,26 fps cambiano solo le 9 colonne integrali su 33.

In sintesi: il cambio di RAPPRESENTAZIONE (v2->v3) ha spostato la classifica
delle architetture piu' di quanto l'abbia mai spostata un cambio di
architettura; il cambio di TEMPO (v3->v4->v5) non ha contato in laboratorio e
conta solo alla cadenza reale della board.

### `docs/GUIDA_DIFESA.md`

Nuovo file: riferimento esaustivo di tutta la tesi (pipeline, sei
architetture, cinque forme di domain shift, sette contributi, dispositivo
edge, limiti, sviluppi, la cronologia v2->v5 di cui sopra) piu' una scaletta
per una presentazione di 15 minuti con i dieci numeri da tenere a mente e le
risposte pronte alle domande piu' probabili.

### File toccati

`tesi/Cap5.tex`, `tesi/Cap3.tex` (due frasi accorciate); nuovo
`docs/GUIDA_DIFESA.md`.

**Verificato con:** `python tesi/controlla.py` -> restano i soliti 2 problemi
(`HO`, `LI`); tutte le intestazioni di Cap5 rilette a mano dopo lo spostamento.

## 2026-09-25 --- La virgola decimale nelle figure inglesi, e la Discussione

### Il difetto che riguardava tutte le figure inglesi

`dec()` e `virgola()` in `figure_tesi.py` mettevano la virgola decimale
**sempre**, qualunque fosse la lingua. Tutte le figure `_en` prodotte da quel
modulo portavano quindi «0,953» e «0,2», che in inglese sono scorretti: li' il
punto e' il separatore decimale e la virgola separa le migliaia. Corretto alla
radice, in `figure_tesi.py` e in `figura_dispositivo.py`, e tutte le figure
rigenerate nelle due lingue.

### fig_configurazioni rifatta

Era un grafico a barre di cinque valori di F2 fra 0,898 e 0,953 su un asse che
partiva da zero: le barre erano indistinguibili. I dati contengono pero' una
storia che l'F2 comprime, perche' le due aggiunte agiscono su errori diversi:

| | F2 | cadute mancate | falsi allarmi |
|---|---|---|---|
| A3 | 0,898 | 45 | 172 |
| A3h | 0,931 | 22 | 137 |
| A3i | 0,943 | 14 | 150 |
| A3h + contro | 0,942 | 22 | 129 |
| A3i + contro | 0,953 | 14 | 124 |

Altezza dal pavimento e integrali tolgono cadute MANCATE (45 -> 22 -> 14); i
controesempi tolgono falsi ALLARMI (150 -> 124) e non cambiano di una sola
unita' le mancate. Rifatta come piano mancate-contro-falsi allarmi, con le
frecce delle due aggiunte: scendono le une, arretrano le altre. Il testo subito
sotto la figura gia' citava 45 -> 14 e 172 -> 124, quindi ora figura e testo
dicono la stessa cosa.

### Verifica dei numeri di campo

Ricalcolati dai punteggi, senza leggere `eventi.csv` ne' il campo `allarmi` di
`riepilogo.json`, che contano FINESTRE e non eventi:

- **14,9 confermato esattamente**: la sessione di `fig_sessione` (durata 5h
  dell'11 agosto) ha 208 finestre sopra soglia e 14 eventi.
- **44,8 e 14,98 ore su 9 sessioni confermati**: sono cio' che
  `pipeline/eventi_sessioni.py` produce. Lo scarto con le «9,6 ore, dodici
  sessioni» di `risultati/sessioni/LEGGIMI.md` e' di ambito: quello e' il
  totale della raccolta PRIMA della notte del 6 settembre, che da sola vale
  4,59 ore.
- **fig_sessione non e' disegnata a mano**: viene da `punteggi.csv` di una
  sessione vera, con gli allarmi ricalcolati applicando la regola.

### La soglia di campo non era uniforme

Quattro delle nove sessioni aggregate sono state registrate con soglia 0,45 e
cinque con 0,50, e la tesi presentava la regola come «0,50». Ricalcolando tutto
a 0,50 il fattore passa da 47,8 a 47,4: l'uno per cento, nessuna conclusione
toccata. Dichiarato in `sec:protocollo-campo` lo stesso, perche' costa una
frase.

### Due figure che esistevano e nessuno citava

- **fig_ema** in `sec:robustezza` del Capitolo 3. Il Capitolo 3 scriveva gia'
  «la' si misura che cosa costerebbe AGGIUNGERE una media mobile», e quella
  misura non c'era: la sezione rimandava al rumore gaussiano, che e' un altro
  esperimento. Chiusa una promessa che il testo faceva e non manteneva. Nella
  stessa sezione una frase era scritta due volte di seguito.
- **fig_termica** nella sezione sulla stabilita' termica del Capitolo 5, che
  cita gia' «79,5 gradi» e «regime dopo quaranta minuti». In didascalia si
  dichiara anche cio' che il testo taceva: la cadenza non ha cali improvvisi ma
  **scende lentamente**, da circa otto a circa sei fotogrammi al secondo.

Entrambe erano gia' in inglese: rinominate `_en` come `fig_pipeline`.

### fig_stanza

L'inquadratura e' ritagliata di 170 pixel a sinistra, dove c'era un cesto
azzurro sul bracciolo del divano. Il taglio e' dichiarato in didascalia e nella
scheda, perche' la figura afferma di mostrare quello che la telecamera vede.

### La Discussione, e due numeri ritirati

`Conclusioni.tex` aveva Contributi, «Il risultato che non era atteso», Limiti,
Sviluppi e Conclusione: elencava e chiudeva, ma non tornava sulle domande di
ricerca. Aggiunta `\section{Discussione}` fra i contributi e i limiti, che
risponde a RQ1, RQ2 e RQ3 una per una e poi mostra che cosa le lega.

Due numeri della Conclusione erano superati dal resto dello stesso capitolo:

- **5,8%** per il classificatore. Il Contributo 4, quattro paragrafi sopra, lo
  dichiara **ritirato il 6 settembre** e riporta 14,3%. Le due cifre
  convivevano nella stessa pagina.
- **«i suoi 14 falsi allarmi all'ora»** non e' una misura: e' l'estremo basso
  della PREVISIONE 14--125 del Contributo 5, usata come se fosse il valore
  osservato. Il misurato e' 11,1 eventi all'ora.

### Board

Spenta su richiesta. La telecamera USB non era collegata (`/dev/video*`
assente), quindi non e' stato possibile riprendere una nuova inquadratura.

### File toccati

`pipeline/figure_tesi.py`, `figura_dispositivo.py`, `figura_ema.py`,
`figura_stanza.py`; `tesi/Cap3.tex`, `Cap5.tex`, `Conclusioni.tex`.

**Verificato con** `python tesi/controlla.py`: restano i due `\cite` non
definiti, `HO` e `LI`, che richiedono un riferimento che non esiste in
bibliografia. Ogni figura citata esiste su disco. `pipeline/eventi_sessioni.py`
riproduce 44,8 e 14,98 ore.

## 2026-09-25 --- Tutte le figure citate in inglese, e cinque citazioni riparate

La tesi citava trentuno figure, ventotto delle quali gia' con il suffisso
`_en`. Le tre rimaste erano il motivo per cui la candidata vedeva italiano
sparso nelle immagini.

### Che cosa c'era davvero da tradurre

Meno di quanto sembrasse. Aperti i tre script, due non avevano nulla da
tradurre:

| figura | testo che conteneva | intervento |
|---|---|---|
| `fig_popolazione` | italiano vero | tradotta |
| `fig_pipeline` | gia' tutto inglese | solo il nome |
| `fig_rappresentazioni` | nessun testo: solo geometria | solo il nome |
| `fig_landmark_mediapipe` | nomi ufficiali MediaPipe | solo il nome |
| `fig_sessione_v5_*` | italiano vero | tradotte |

Per le tre che non contengono italiano non si e' creata una seconda copia
identica: il nome in uscita degli script e' diventato `_en` e i file sono
stati rinominati. Esiste una variante sola, ed e' inglese; il nome lo dichiara,
cosi' in tesi ogni `\includegraphics` finisce allo stesso modo e la verifica
si fa a vista.

`figura_popolazione.py` e `figura_sessione_v5b.py` hanno ricevuto il
meccanismo di `figure_tesi.py`: `LINGUA`, `T(it, en)`, `--lingua {it,en}`.

### Due difetti trovati strada facendo

**Un accento combinante in `figura_popolazione.py`.** La legenda scriveva
«piu'» come `u` seguita da U+0300, mentre l'etichetta diretta usava il
carattere precomposto: due stringhe diverse per il calcolatore, e in matplotlib
la prima rischia di stampare l'accento staccato dalla lettera. Il file e' stato
normalizzato in NFC.

**Il separatore delle migliaia.** In inglese il punto e' il separatore
DECIMALE: «13.330» si sarebbe letto tredici virgola trecentotrenta. La variante
inglese usa la virgola.

**L'etichetta della soglia** in `fig_sessione_v5_andamento` cadeva sopra i punti
sopra soglia; spostata nella fascia grigia.

### Cinque citazioni riparate, due no

Sette chiavi `\cite` non erano definite e sarebbero uscite come `[?]`. Cinque
erano abbozzi delle chiavi vere, e la corrispondenza e' accertata dal testo
stesso: `IS` -> `istat2026`, `PA` -> `passi`, `MU` -> `mubashir`,
`GU` -> `gutierrez`, `LIN` -> `lin`. In due casi il testo nomina l'autore per
esteso e le cifre citate coincidono parola per parola con il commento della
voce.

Restano due, e vanno decise dalla candidata perche' indovinarle sarebbe
falsificare un riferimento:

- **`HO`**, tredici occorrenze, e' la rassegna portante del Capitolo 2
  («Hoang et al.»). In bibliografia **non esiste alcuna voce Hoang**: manca il
  riferimento, non la chiave.
- **`LI`**, una occorrenza, sui limiti di copertura dei sensori ambientali.
  Nessuna voce «Li» in bibliografia. Il paragrafo intorno e' di `mubashir`, ma
  «probabile» non basta.

### Due figure entrate nella tesi

`fig_sessione_v5_andamento` e `fig_sessione_v5_cadute` sono entrate in
`sec:recall-campo` del Capitolo 5, che dichiarava un problema aperto: le cadute
annotate al solo minuto, il richiamo dipendente da una tolleranza di
accoppiamento. La sessione del 9 settembre e' la prima con i fotogrammi salvati
attorno a ogni finestra, quindi le cadute sono note al secondo e la tolleranza
non serve. Con essa entra un risultato che nel capitolo non c'era: **la
sospensione di 30 s perde una caduta vera** (ISS-162), quella in cui la persona
cade, prova a rialzarsi e ricade sei secondi dopo. Il classificatore la vede
benissimo; e' la regola a perderla.

`fig_landmark_mediapipe` e' entrata in `sec:pose` del Capitolo 3, prima del
primo uso degli indici.

### File toccati

`pipeline/figura_popolazione.py`, `figura_pipeline.py`,
`figura_rappresentazioni.py`, `figura_landmark_mediapipe.py`,
`figura_sessione_v5b.py`, `figura_stanza.py`; `tesi/Cap1.tex`, `Cap2.tex`,
`Cap3.tex`, `Cap5.tex`.

**Verificato con** `python tesi/controlla.py`: i problemi passano da 7 a 2, e i
due che restano sono `HO` e `LI` di cui sopra. Ogni figura citata esiste su
disco (trentadue su trentadue). `python pipeline/figura_sessione_v5b.py` in
entrambe le lingue supera il proprio controllo interno: la regola applicata al
registro ritrova, caduta per caduta, quanto il LEGGIMI della sessione dichiara.

Se una modifica non e' stata provata, si scrive «non verificato»: e'
un'informazione utile, fingere non lo e'.

---

## 2026-09-25 --- Due formulazioni che promettevano piu della misura, e tre autoriferimenti

Chiude la revisione esterna. Nessuno dei due punti era un errore di calcolo:
erano affermazioni piu forti di quanto i dati sostengano, e convivevano nella
stessa pagina con la loro versione prudente.

### La soglia

Il paragrafo diceva insieme che la soglia «non vede alcun dato» e che e stata
«dichiarata prima degli esperimenti». La prima meta e vera per costruzione, la
seconda no: 0,50 e stato ADOTTATO dopo il confronto delle sei regole sui fold
di prova, come la sezione dichiara poche righe sopra.

Riscritto distinguendo **applicazione** e **scelta**. Sull applicazione la
garanzia resta netta e piu forte di quella che il relatore chiede: la soglia
non e tarata su alcun insieme, quindi il rischio che la sua formulazione
intende escludere non si pone. Sulla scelta il limite e dichiarato: il valore
e il punto naturale per un uscita a due classi, ma la decisione di adottarlo ha
guardato i risultati, e presentarla come compiuta al buio sarebbe scorretto.

### Il leakage sulla selezione

«Spinge le prestazioni verso l alto, ed e la ragione per cui i valori vanno
letti come un limite superiore» afferma come fatto la direzione dell effetto.
La misura non la stabilisce: mostra che la selezione adottata non e quella che
un protocollo corretto avrebbe prodotto, non di quanto le metriche ne
risentano. Lo stesso capoverso, quattro righe dopo, scriveva «plausibile, non
dimostrato».

Riscritto separando le due misure per natura: su K il confronto e fra due
prestazioni e il risultato e una differenza; sulla selezione il confronto e fra
due insiemi di grandezze e il risultato e una sovrapposizione. La direzione
attesa resta dichiarata come attesa.

Cap3 gia scriveva «la sua conseguenza ATTESA e una sopravvalutazione»: era
Cap4 a essere piu assertivo del capitolo che lo promette.

### Tre autoriferimenti

Cap4 portava due volte «il Capitolo~ef{cap:risultati}», che e se stesso:
avrebbe stampato «il Capitolo 4» dentro il Capitolo 4. Sono residui dei
capoversi spostati dal Capitolo 3 il 23 settembre. Cap5 ne aveva uno analogo
verso `cap:edge`. Sostituiti con rimandi a sezione.

L ultimo ha fatto emergere che `sec:fallimenti` non esiste: la sezione si
chiama `sec:modi-fallire`.

**Verificato con:** `python tesi/controlla.py` -> PROBLEMI 7;
`python tesi/controlla_ritirati.py` -> due segnalazioni, entrambe confronti
espliciti fra 7,3 e 26,5 fps.

## 2026-09-25 --- Revisione esterna: tre tabelle su basi diverse, riportate a una sola

Una revisione esterna ha confrontato due versioni del capitolo e trovato che la
tabella della numerosita' non era compatibile con le tabelle accanto a cui
stava. **L obiezione era corretta, e l incoerenza l avevo introdotta io.**

### Il difetto

`tab:finestra` e `tab:rappresentazioni10` venivano dalla campagna GRU del
20 agosto su feature_v2; `pipeline/numerosita.py` calcolava le differenze
appaiate con la foresta su feature_v5. La riga «finestra 44 contro 22» dava
quindi **+0,091 accanto a una tabella da cui si legge +0,034**: due modelli e
due dataset diversi presentati come se fossero lo stesso esperimento.

### La correzione

`pipeline/tabelle_v5.py` ricalcola entrambe le tabelle sulla stessa base
delle differenze: foresta a 50 alberi, feature_v5, dieci fold, soglia 0,50,
valutazione sull etichetta di allarme.

| L | prima (GRU, v2) | **ora (foresta, v5)** | FN / FP |
|---|---|---|---|
| 22 | 0,847 | **0,825** | 232 / 468 |
| 28 | 0,838 | **0,851** | 164 / 414 |
| 36 | 0,817 | **0,871** | 113 / 341 |
| 44 | 0,881 | **0,915** | 53 / 249 |

**La scansione e monotona**, e 0,915 - 0,825 = 0,090 coincide con il +0,091
appaiato. Il testo diceva che l ipotesi «piu lunga e meglio» non era
confermata: era confermata, ed era la campagna a essere vecchia. Riscritto.
I due errori migliorano inoltre INSIEME, FN da 232 a 53 e FP da 468 a 249.

Configurazioni di grandezze: 0,831 / 0,832 / 0,825 invece di 0,874 / 0,858 /
0,857. La conclusione non cambia --- non distinguibili --- ma ora lo scarto
vale 0,007 e coincide con le differenze appaiate.

`fig_finestra` leggeva ancora i quattro run GRU: ricollegata a
`tabelle_v5.json`, altrimenti la figura contraddiceva la tabella.

### Gli altri residui trovati dalla revisione

- **i conteggi erano di v2**: 49.691 / 11.510 / 1.423, che per di piu non
  sommano a 58.359. Corretti in 50.264 / 11.719 / 1.491, verificati sul CSV.
  La revisione lo ha trovato con una somma, che e il controllo piu semplice
  e il piu efficace;
- **la tabella dei fold era di v2**: 9.120 / 121 invece di 9.318 / 129;
- **la normalizzazione** diceva ancora «le grandezze che soddisfano il criterio
  previsto nella fase di preprocessing». Un criterio non esiste: e un elenco
  fisso di quattordici nomi, ora scritto per esteso;
- **«cinque soggetti»** era rimasto in fondo alla sezione sulla foresta, che e
  a dieci: tolto;
- **«i due valori positivi»** della tabella delle occlusioni: sono quattro,
  fino a +0,015 per le anche.

### Che cosa la revisione ha sbagliato

Un punto solo. Su h_pav suggerisce di «scegliere una sola estrazione» fra
+1,43/-0,18 e +1,510/+0,060, come se fossero due misure alternative. Il primo
valore **non ha sorgente riproducibile**: nessuno script lo calcola e non
compare in NUMERI_PER_LA_TESI.txt. Il secondo e prodotto da
`pipeline/altezza_pavimento_viste.py` su feature_v5. Non c e una scelta da
fare.

**Verificato con:** `python pipeline/tabelle_v5.py`;
`python tesi/controlla.py` -> PROBLEMI 7.

## 2026-09-25 --- Capitolo 5: la latenza sui valori correnti, e un controllo permanente

### Che cosa era gia' a posto

Il Capitolo 5 su disco era in parte gia' corretto: la tabella del costo per
fotogramma porta 136,65 ms e 7,3 fps accanto ai valori ritirati, il fattore
finestre/eventi vale 44,8 con la sua base dichiarata (14,98 ore, nove
sessioni), e l'intervallo delle finestre positive e' 14--156 e non 14--125.

### `tab:latenza` era rimasta indietro

Riportava la scomposizione vecchia: calcolo per fotogramma 0,038 s (1,0%),
totale 3,778 s, e «il rapporto e' superiore a settanta». La misura che
`pipeline/latenza.py` produce oggi e':

| componente | tempo | quota |
|---|---:|---:|
| calcolo per fotogramma | 0,125 s | 3,2% |
| riempimento della finestra | 2,743 s | 71,0% |
| persistenza | 0,997 s | 25,8% |
| caso conservativo | 3,865 s | 100% |

La conclusione regge --- la latenza e' dominata dalla finestra e non dal
calcolo --- ma con un margine di **ventidue volte** e non di settanta. La
didascalia ora spiega anche perche' si chiami «caso conservativo» e non
«limite inferiore»: riempimento e persistenza sono i minimi, il calcolo e'
quello misurato.

### I 4,47 ms

Erano ancora nel testo come costo del classificatore. Sono nell'elenco dei
numeri ritirati: una misura del calcolatore attribuita alla board. Il
paragrafo ora tiene distinte le due macchine --- 4,85 ms sul calcolatore,
39,04 sul dispositivo --- e collega il valore alla scansione della dimensione
della foresta del Capitolo 4, che per 50 alberi misura 6,1 ms per finestra
classificata una alla volta. I due valori sono coerenti, e il 4,47 e'
dichiarato come ritirato dove compariva.

### `tesi/controlla_ritirati.py`

Controllo permanente, come `controlla.py`. Cerca nei sorgenti gli otto valori
che `NUMERI_PER_LA_TESI.txt` elenca come da non usare piu'.

Distingue due casi, perche' senza la distinzione sarebbe inutilizzabile: un
numero ritirato e' **legittimo** quando il testo lo dichiara superato, e anche
quando e' vero ma riferito a un altro oggetto. I 26,5 fps sono la frequenza
reale della catena accelerata su banco: sono sbagliati solo se attribuiti al
sistema installato. Lo script stampa separatamente le occorrenze dichiarate e
quelle da correggere.

Stato attuale: **sette occorrenze, tutte legittime**. Due restano fra quelle
«da correggere» perche' sono confronti espliciti fra 7,3 e 26,5 che l'euristica
non riconosce; sono false segnalazioni che chi legge risolve a colpo d'occhio.

**Verificato con:** `python pipeline/latenza.py`;
`python tesi/controlla_ritirati.py`; `python tesi/controlla.py` -> PROBLEMI 7.

## 2026-09-25 --- I tre compiti valutati sulla stessa etichetta: la sezione si rovescia

Le ultime quattro delle undici correzioni. La prima ha cambiato il risultato di
una sezione intera.

### `tab:compiti`: ogni compito era giudicato con il proprio metro

`confronto_compiti.py` addestrava E valutava ciascun compito sulla propria
definizione di positivo: evento su `fall`, stato su `fallen`, allarme su
`fall OR fallen`. Le tre prevalenze erano percio' 0,047 / 0,089 / 0,115 e i
tre F2 non confrontabili, perche' la precision di riferimento dipende dalla
quota di positivi. Il Capitolo 4 dichiarava pero' che i tre sono «valutati
tutti sulla stessa etichetta di allarme»: falso per quella tabella.

E' stata la candidata a trovarlo, dalla sola colonna delle prevalenze.

`finestre()` costruisce ora due etichette --- quella del compito, per
addestrare, e quella di allarme, per valutare --- come `dati.fold_loso` fa da
sempre nella pipeline principale. Con `--valuta-sul-compito` si riproduce il
comportamento precedente.

| compito | prev. addestr. | F2 prima | **F2 ora** | recall | precision | difficili |
|---|---:|---:|---:|---:|---:|---:|
| evento | 0,047 | 0,831 | **0,415** | 0,364 | 0,990 | 0,0% |
| stato | 0,089 | 0,704 | **0,587** | 0,552 | 0,874 | 8,4% |
| allarme | 0,115 | 0,810 | **0,830** | 0,836 | 0,841 | 11,7% |

La prevalenza di valutazione e' ora 0,115 per tutti e tre.

### Che cosa cambia nella lettura

Il compito evento **non** e' piu' il migliore: giudicato su cio' che il sistema
deve davvero segnalare, ne riconosce poco piu' di un terzo, perche' un modello
addestrato sulla sola transizione non ha mai visto la fase in cui la persona e'
gia' a terra.

Resta pero' l'unico che **non produce un solo falso allarme** sulle 2.234
finestre di persone sdraiate volontariamente, con precision 0,990. I tre
compiti realizzano quindi compromessi diversi fra i due errori, e la scelta non
si decide su una metrica sola: dipende da quanto costa un falso allarme
rispetto a una caduta non vista, e quel costo non e' misurabile su UP-Fall.

La sezione ora lo dice, e anticipa che nel Capitolo 5 il confronto si rovescia:
1,6 allarmi all'ora contro 36,4, tre cadute su cinque invece di quattro. Venti
volte meno segnalazioni al prezzo di una caduta. E' uno degli esempi piu' netti
di una differenza che il benchmark comprime e l'ambiente reale amplifica.

### Le altre tre

- **`tab:kappa`**, didascalia: foresta casuale, camera 1, soglia 0,50; colonna
  di laboratorio a cinque soggetti; e la dichiarazione che la tabella non e'
  una verifica indipendente della scelta di K ma **la misura da cui quella
  scelta e' stata compiuta**.
- **Confronto delle pose**: UR-Fall 81,0% va confrontato con il **92,3%** della
  camera 1, non con il 95,9% dell'archivio intero, che include la camera 2 e
  userebbe come metro dati che il modello non ha mai visto.
- **`tab:esterno`**: la riga «configurazione schierata precedente» viene dalla
  modalita' `scarta` e ha prevalenza 0,094, le altre tre da `caduta` e hanno
  0,130. Poiche' il guadagno e' PR-AUC diviso prevalenza, **non erano
  confrontabili**. Aggiunta la colonna della prevalenza, la riga spostata sotto
  un `midrule` e la didascalia dichiara le due modalita'.

**Verificato con:** `python pipeline/confronto_compiti.py`;
`python tesi/controlla.py` -> PROBLEMI 7.

## 2026-09-25 --- `tab:numerosita` rifatta su feature_v5, e una conclusione che cambia

Undici difetti segnalati dalla candidata, tutti verificati. Tre erano di
sostanza.

### Il difetto peggiore: due esperimenti sotto lo stesso nome

La riga «Definizione del compito, -0,309, t -6,85» **non veniva dal confronto
fra evento, stato e allarme** di `tab:compiti`, come il nome suggeriva. Viene
da `EXPERIMENTS.md:486`, campagna del 20 agosto: e' il confronto fra
MODALITA' DI ETICHETTATURA, `scarta` (F2 0,538) contro `tre_classi` (0,847).
La differenza 0,309 e' quella. Nessuna coppia di `tab:compiti` --- 0,831 /
0,704 / 0,810 --- differisce di 0,309, ed e' stata la candidata ad accorgersene.

Stesso problema sulla riga «effetto delle grandezze integrali, -0,022»: era la
variante «foresta con estremi», mentre quella senza estremi dava **+0,039**,
segno opposto, e `tab:rappresentazioni10` mostra -0,016. Tre misure diverse.

E «finestra 22 contro 44» confrontava L22 su feature_v5 con L44 su feature_v2.

### La soluzione: `pipeline/numerosita.py`

Tutte le righe ricalcolate sullo stesso dataset, con lo stesso modello e lo
stesso protocollo. Foresta casuale a 50 alberi per protocollo e
rappresentazione; i confronti fra architetture dai punteggi per fold gia'
salvati.

**La valutazione e' sempre sull'etichetta di allarme.** `dati.fold_loso`
restituisce per il test `y_allarme`, comune a tutte le modalita': il confronto
fra `scarta`, `caduta` e `tre_classi` e' quindi sullo stesso insieme di
finestre e sulla stessa verita'.

| confronto | differenza | t | soggetti |
|---|---:|---:|---:|
| Etichettatura: scartare le finestre di solo stato | -0,361 | -7,19 | **2** |
| Finestra di 44 campioni invece di 22 | **+0,091** | **+3,62** | **6** |
| Architettura: rete a grafo invece di GRU | -0,063 | -3,14 | 8 |
| Architettura: LSTM invece di GRU | -0,027 | -2,98 | 9 |
| Architettura: foresta invece di GRU | -0,032 | -1,24 | 52 |
| Architettura: Transformer invece di GRU | -0,020 | -1,22 | 54 |
| Architettura: CNN 1D invece di GRU | -0,019 | -1,16 | 58 |
| Etichettatura: tre classi invece di due | +0,014 | +0,92 | 94 |
| Selezione DTW invece di tutto A3 | -0,007 | -0,21 | 1833 |
| Grandezze integrali aggiunte ad A3base | +0,001 | +0,18 | 2373 |

### La conclusione che cambia

**La finestra da 44 campioni batte quella da 22 di 0,091 con t = 3,62**, e
bastano sei soggetti per dichiararlo. Il testo diceva che L = 22 veniva tenuto
«a parita' di prestazione distinguibile»: quella parita' non esiste.

La scelta resta valida ma la ragione e' un'altra, ed e' stata riscritta come
**compromesso dichiarato**: 4,9 s di storia contro 2,44 prima della prima
decisione, su una latenza che il Capitolo 5 misura dominata proprio dal
riempimento della finestra. Si rinuncia a 0,091 di F2 per dimezzare il ritardo.
E' il caso opposto a quello della dimensione della foresta, dove il valore
ereditato e' stato tenuto perche' la misura non mostrava differenze.

### Un difetto mio, trovato e corretto durante la misura

`per_fold_foresta` binarizzava le etichette con `(y_train > 0)` anche in modo
`tre_classi`, rendendo `caduta` e `tre_classi` **identici per costruzione**:
la prima esecuzione dava differenza esattamente 0,000 con t = nan. Corretto
addestrando su tre classi e riducendo a probabilita' di allarme come
1 - p(normale). Il confronto ora vale +0,014.

### Perche' non si possono mescolare v2 e v5

Richiesta della candidata: usare per ogni riga il risultato migliore fra le due
campagne. Non e' praticabile, e le ragioni sono due. **Non sono le stesse
feature**: v2 ha 218 riprese e 39 colonne, v5 ne ha 220 e 40, e venti colonne
differiscono numericamente --- undici derivate e nove integrali. E scegliere
per riga l'esito migliore sarebbe selezione sull'esito, cioe' esattamente cio'
che `sec:leakage` dichiara di non fare.

### Le altre correzioni

- `tab:soglie`: la didascalia ora dichiara da dove vengono i punteggi --- GRU,
  sottoinsieme DTW, camera 1, dieci fold, nessun riaddestramento;
- `tab:correzioni`: aggiunta la ragione per cui quel confronto usa F1 e non F2,
  con l'osservazione che con zero veri positivi ogni F-beta vale zero;
- `sec:metriche` **non aveva label**, e il rimando che l'ha citata l'ha
  scoperto: aggiunta.

**Verificato con:** `python pipeline/numerosita.py`; `python tesi/controlla.py`
-> PROBLEMI 7.

## 2026-09-24 --- Tre blocchi fuori posto, fig_dominio rifatta, h_pav ricalcolata

**Tre blocchi stavano nel cappello di «Confronto fra rappresentazioni e
architetture», prima della prima sottosezione, e nessuno dei tre riguardava il
confronto fra rappresentazioni.**

| blocco | dove e' andato |
|---|---|
| i numeri sull'altezza dal pavimento nelle due viste | `sec:viewpoint` |
| «Che cosa vede una vista e non vede l'altra» + `fig_due_camere` | `sec:viewpoint` |
| la regola di ridondanza del DTW | **eliminata**: era gia' in Cap3 `sec:dtw` |
| `fig_dtw` | Cap3, in fondo a `sec:dtw` |

`fig_dtw` illustra il criterio del minimo fra le due viste, cioe' la
selezione: appartiene al capitolo che la definisce.

**Il numero sull'altezza dal pavimento non si riproduceva.** Il testo diceva
+1,43 in un punto e +1,45 in un altro per la vista laterale, e -0,18 per la
rialzata; nessuno script del progetto lo calcolava e non compare in
`docs/NUMERI_PER_LA_TESI.txt`. Scritto
`pipeline/altezza_pavimento_viste.py`. Su `feature_v5`, soli fotogrammi con
posa valida, mediana(non caduta) - mediana(caduta):

| vista | caduta | non caduta | separazione |
|---|---|---|---|
| Camera 1, laterale | 0,082 | 1,592 | **+1,510** |
| Camera 2, frontale rialzata | 1,366 | 1,426 | **+0,060** |

Venticinque volte meno dalla vista rialzata. La conclusione del testo regge ed
e' anzi piu' netta, ma i numeri vanno sostituiti. Il segno va dichiarato,
perche' e' la sorgente dell'ambiguita' fra le due versioni.

Una trappola trovata scrivendo lo script: `dati.carica()` **filtra gia' alla
camera 1**, quindi una misura che confronta le due viste non puo' usarla.

**`fig_dominio` rifatta.** Era una sola barra orizzontale con tre segmenti, e
non si capiva: i tre valori non erano tre misure affiancate ma un valore e due
differenze, mostrati tutti e tre come lunghezze sullo stesso asse. Ora sono
tre barre nell'ordine in cui la sezione le racconta --- archivio di
addestramento, archivio nuovo come schierato, archivio nuovo con la soglia
oracolo --- con i due passi annotati: divario complessivo -0,937, recuperabile
spostando la soglia +0,457, non recuperabile -0,480.

**`Quanto pesa il leakage` rinominata `Le due violazioni del protocollo,
misurate`**: dice che e' una misura e non una discussione, e resta collegata
alla dichiarazione del Capitolo 3.

**Verificato con:** `python tesi/controlla.py` -> PROBLEMI 7. Durante lo
spostamento era salito a 8 per un `fig:dtw` rimasto senza label: la figura era
stata tolta da Cap4 prima di essere messa in Cap3.

## 2026-09-24 --- Matrici su due righe, e la dimensione della foresta misurata a dieci soggetti

**1. `fig_confusione` su due righe.** Su una riga sola i sei riquadri erano
larghi 3 cm su una figura di 18 e le percentuali diventavano illeggibili nel
PDF. Ora 3 sopra e 3 sotto, riquadri di lato doppio, numeri a corpo 17 invece
di 13, e le etichette degli assi stampate solo dove servono: asse y sulla
colonna di sinistra, asse x sulla riga in basso. `tight_layout` non vedeva la
sovrapposizione fra i titoli della seconda riga e le matrici della prima,
perche' queste sono disegnate con `imshow`: aggiunto `hspace` esplicito.

**2. `fig_dimensione` rifatta a DIECI soggetti.** Leggeva
`risultati/cinque_soggetti/exp017_rf_size.json`, prodotto dall'impianto
precedente, e **nessuno script del progetto attuale lo rigenerava**. Scritto
`pipeline/dimensione_foresta.py`: sei dimensioni per dieci fold di
`feature_v5`, camera 1, dodici grandezze DTW, soglia 0,50.

| alberi | nodi | F2 | ms/finestra |
|---|---|---|---|
| 10 | 1.881 | **0,850 ± 0,074** | 1,8 |
| 25 | 4.782 | 0,839 ± 0,063 | 3,7 |
| 50 | 9.535 | 0,838 ± 0,072 | 6,1 |
| 100 | 19.079 | 0,839 ± 0,066 | 12,1 |
| 200 | 37.889 | 0,835 ± 0,069 | 24,7 |
| 400 | 76.065 | 0,836 ± 0,072 | 43,7 |

**La conclusione regge ma cambia forma.** A cinque soggetti la scansione
sembrava avere un massimo a 50 alberi (F2 0,906); a dieci l'andamento e'
piatto e il valore piu' alto e' a DIECI alberi. L'escursione complessiva vale
0,015 contro una dispersione fra soggetti di 0,07. Il testo non puo' piu'
giustificare i 50 alberi come ottimo di accuratezza: sono il valore ereditato
dalla configurazione precedente, che la scansione ha verificato e non ha avuto
ragione di cambiare --- la stessa distinzione gia' fatta per la lunghezza
della finestra.

**Due errori nella misura della latenza, entrambi trovati e corretti.**
Il primo: cronometravo un lotto intero diviso per il numero di finestre,
mentre il sistema installato classifica una finestra alla volta; il lotto
ammortizza e dava valori di due ordini di grandezza troppo bassi (0,03 ms).
Il secondo, piu' insidioso: con `n_jobs=-1` ogni chiamata singola paga
l'avvio del pool di thread, che domina e produce una latenza **costante a
31 ms indipendente dalla dimensione** --- un numero che sembrava plausibile e
non lo era. Con `n_jobs=1`, come sulla board, la latenza scala in proporzione
agli alberi, e a 50 alberi da' 6,1 ms: coerente con i 4,85 ms che il
Capitolo 5 riporta per il calcolatore.

**Ritirati dal testo** i valori a cinque soggetti (F2 0,906 e 0,888) e la
latenza di 4,47 ms, che `NUMERI_PER_LA_TESI.txt` elenca fra quelli da non
usare piu'.

**Verificato con:** `python pipeline/dimensione_foresta.py`;
`python tesi/controlla.py` -> PROBLEMI 7. Durante la stesura era salito a 8
per un riferimento a `sec:finestra`, etichetta inesistente: la sottosezione
si chiama `sec:lunghezza_finestra`.

## 2026-09-24 --- Il confronto fra architetture passa a feature_v5

La tabella e la prosa erano sulla campagna del 20 agosto su `feature_v2`
(218 riprese); la figura era gia' stata riportata su v5 il 23 settembre.
Tabella e figura si contraddicevano a venti righe di distanza. Il Capitolo 3
descrive v5, quindi v5.

| | v2 | v5 |
|---|---|---|
| GRU | 0,847 | **0,857** |
| CNN 1D | 0,833 | 0,838 |
| Transformer | 0,846 | 0,837 |
| LSTM | 0,858 | 0,829 |
| Random Forest | 0,792 | 0,825 |
| Grafo | 0,779 | 0,794 |

**Che cosa cambia nella sostanza.** L'escursione fra le cinque architetture
non a grafo scende da 0,066 a **0,032**, contro una dispersione fra soggetti
di 0,089. La conclusione della sezione si rafforza: la differenza fra due
architetture e' ora poco piu' di un terzo della differenza fra due persone.

**Che cosa cambia nei test, e va dichiarato.** Su v2 solo la rete a grafo
superava il valore critico non corretto. Su v5 lo superano il grafo
(t = -3,14) e la LSTM (t = -2,98), entrambi con segno negativo, e nessuno dei
due arriva al critico corretto per cinque confronti (circa 3,25).

Il confronto GRU/LSTM **cambia natura**: su v2 la differenza era +0,011 con
t = +0,84 e sarebbero serviti 113 soggetti; su v5 e' -0,027 con t = -2,98 e ne
bastano 9, perche' il segno e' costante fra i fold. La prosa che usava
GRU/LSTM come esempio di differenza non rilevabile non regge piu' ed e' stata
riscritta: l'esempio ora e' GRU contro foresta casuale, e il capoverso spiega
il punto che ne esce --- non e' l'ampiezza della differenza a renderla
rilevabile, ma la sua costanza fra le persone.

**figura_confusione.py leggeva la campagna sbagliata.** Il difetto non era la
lingua: il valore per difetto di `--punteggi` era
`risultati/addestramento/v2/`. I punteggi per fold di v5 esistono --- sono i
file `_L22` del 9 settembre, che `carica()` cerca gia' per primi --- e bastava
non puntare alla sottocartella. Aggiunti `--lingua en`, 400 dpi e il titolo
fuori dall'immagine.

**`fig_confusione` entra in Cap4**, dopo `fig_architetture`. Mostra cio' che il
valore sintetico nasconde: la LSTM perde 82 cadute e ne segnala 1266
inesistenti, la foresta ne perde 232 e ne segnala 468. F2 a tre centesimi di
distanza, errori opposti. E' la figura che regge l'affermazione, promessa in
`sec:metriche`, che due configurazioni con lo stesso F2 possono sbagliare in
modi opposti.

**Un difetto introdotto e riparato nella stessa sessione.** Il blocco della
figura e' stato inserito con un heredoc di bash, che ha interpretato le
sequenze di escape: la sequenza per `begin` e' diventata BACKSPACE + "egin" e
quella per `textwidth` TAB + "extwidth". E' la terza volta in questa sessione:
gli script che contengono LaTeX vanno scritti su file con lo strumento di
scrittura, mai passati per heredoc.

**Verificato con:** `python tesi/controlla.py` -> PROBLEMI 7, lo stesso valore
di prima delle modifiche; durante il difetto era salito a 8. Cap4 risulta a
1441 righe e 13 figure.

## 2026-09-23 --- Strategia A: la dichiarazione del leakage resta in Cap3, le misure vanno in Cap4

Il relatore separa metodologia e risultati, e chiede la dichiarazione del
leakage nel Capitolo 3. Il Capitolo 3 conteneva pero anche le DUE MISURE, che
sono risultati sperimentali a tutti gli effetti.

**Restano in Cap3** (`sec:leakage`, metodologia): il principio del
leave-one-subject-out, il procedimento corretto come sequenza numerata,
l ordine sbagliato, `tab:leakage` con le cinque operazioni, e le due
dichiarazioni --- K non fissato a priori, selezione DTW eseguita una volta
sola --- ciascuna seguita dalla promessa della misura.

**Spostate in Cap4** (`sec:misura_leakage`, risultati): `tab:k_misura` e
`tab:leakage_misura`, la prosa che le interpreta, il paragrafo
« Perché il risultato non sorprende » e quello sul difetto ISS-168.
Sono 72 righe, in due sottosezioni.

**Cap4 NON ha una sottosezione 4.1.5 sul leakage.** Duplicherebbe
`tab:leakage`, che il Capitolo 3 gia porta: il relatore chiede la
dichiarazione li, e nel protocollo del Capitolo 4 chiede quattro voci
--- metriche, LOSO, normalizzazione, soglia --- non cinque.

**Un difetto introdotto e corretto nella stessa sessione.** Il testo di
raccordo che ho inserito usava ' come apostrofo: in LaTeX e il comando di
accento acuto, quindi `puo'` non stampa l apostrofo ma accenta il
carattere seguente. Sei occorrenze, sostituite con le lettere accentate.

**Verificato con:** `python tesi/controlla.py` -> PROBLEMI 7, invariato prima
e dopo lo spostamento: nessun riferimento rotto, nessuna etichetta duplicata.
Cap3 da 1260 a 1191 righe, Cap4 da 1326 a 1410.

## 2026-09-23 --- figura_due_camere in inglese, e le tre figure che non erano citate

**1. `figura_due_camere.py`: `--lingua en` e 400 dpi.** Stessa impostazione di
`figure_tesi.py`: LINGUA e' stato di modulo, il nome prende il suffisso `_en`,
la virgola decimale resta. Tradotte anche le etichette che vengono dai dati
(`Dieci soggetti` -> `Ten subjects`), che alla prima passata erano rimaste in
italiano dentro una figura per il resto inglese.

**2. Cap4 e Cap5 passano alle varianti inglesi:** 14 riferimenti aggiornati,
10 in Cap4 e 4 in Cap5. Il Capitolo 3 lo aveva gia' fatto per le sue sette.
Restano in italiano `fig_popolazione`, `fig_pipeline` e `fig_rappresentazioni`,
che non hanno ancora una variante inglese.

**3. Tre figure pronte non comparivano in nessun capitolo.**

| figura | dove e' andata | perche' mancava
|---|---|---
| `fig_viste` | Cap4, dopo `tab:viste` | non veniva nemmeno generata: il file di risultato ha quattro righe e l'elenco dei nomi ne aveva tre
| `fig_dominio` | Cap4, in `Calibrazione e capacita' discriminativa` | e' la figura dei due esperimenti che il relatore chiede di tenere distinti
| `fig_configurazioni` | Cap5, accanto a `fig_errori` | mostra le cinque configurazioni di Cap5, non le tre del confronto fra rappresentazioni di Cap4

**Verificato con:** `python tesi/controlla.py` -> PROBLEMI 7, invariato: nessun
riferimento rotto e nessuna etichetta duplicata introdotta. Le sette restanti
sono le citazioni con chiave corta, che questo intervento non tocca.
## 2026-09-23 --- docs/GUIDA_CAP4.md: guida alla stesura, sezione per sezione

Per ciascuna sezione del Capitolo 4: che cosa e' stato fatto (codice, dati,
misura), quali tabelle e figure, quali promesse dei Capitoli 1--3 si pagano li,
e che cosa dire. Segue la richiesta del relatore di separare protocollo e
risultati.

**Tre cose emerse costruendola.**

1. **Due figure pronte non erano citate in Cap4.** `fig_viste` --- il risultato
   di classificazione del cambio vista, riparata oggi --- e `fig_dominio`, che
   scompone il divario fra archivio di addestramento e archivio mai visto ed e'
   esattamente la figura dei due esperimenti che il relatore chiede di separare.

2. **`fig_configurazioni` NON va in Cap4.** Mostra A3/A3h/A3i con e senza
   controesempi, cioe' le cinque configurazioni del Capitolo 5, non le tre del
   confronto fra rappresentazioni. Va accanto a `fig_errori`.

3. **`tab:kappa` resta in Cap5.** Ha una colonna di laboratorio e una
   domestica, e il suo punto --- il banco dice 45, la casa dice 31 --- e' la
   tesi del Capitolo 5. In Cap4 la scansione compare solo in `sec:misura_leakage`,
   con la misura annidata, che e' un'altra cosa. Rettifica una indicazione
   precedente che la spostava in Cap4.
## 2026-09-23 --- figure_tesi.py: le quattordici figure in inglese, 400 dpi, e fig_viste riparata

**La traduzione precedente era incompleta e il difetto era mio.** La prima
versione aggiungeva l'infrastruttura di lingua ma convertiva le stringhe di
UNA sola figura: le altre tredici prendevano il suffisso `_en` restando in
italiano. Un nome che mente e' peggio di nessuna traduzione. Ora sono
convertite tutte: 79 stringhe visibili in 14 funzioni.

**Le etichette che vengono dai dati** --- nomi dei compiti, dei gruppi di
landmark occlusi, delle configurazioni --- sono scritte in italiano dentro i
file di risultato. Si traducono alla resa con `D()`, come gia' si faceva per
gli accenti con `ACCENTI`, per non toccare i risultati.

**Risoluzione** da 220 a 400 dpi.

**La virgola decimale resta** anche in inglese: i numeri nella figura devono
coincidere con quelli della didascalia, che e' in italiano.

**fig_viste non veniva prodotta, e non per via della lingua.** Falliva da
prima, con `FixedLocator (4) does not match the number of labels (3)`. Il file
`viste_incrociate_10sog.json` ha QUATTRO righe --- le stesse quattro di
`tab:viste` --- e l'elenco dei nomi ne aveva tre: mancava
`Camera2 -> Camera2`, la riga che nella tabella sta separata dalle altre.
`nomi[:len(righe)]` non poteva accorgersene perche' tronca e non allunga.
Aggiunta la quarta etichetta. La figura ora riproduce la tabella esattamente:
0,822 / 0,488 / 0,731 / 0,753 e FP 722 / 3252 / 751 / 1067.

**Verificato con:** `python pipeline/figure_tesi.py --lingua en` --- 14 figure
su 14, nessuna fallita (prima: 11 su 14).

### Verifica dei dati del Capitolo 3 contro feature_v5.csv

Tutto confermato tranne due valori:

| affermazione del Cap3 | misurato | esito |
|---|---|---|
| 220 riprese, 116.362 fotogrammi | 220, 116.362 | ok |
| etichette 100.296 / 5.542 / 10.524 | identiche | ok |
| quote 86,2% / 4,8% / 9,0% | identiche | ok |
| «posa valida nel 95,5%» | **95,88%** | ERRATO |
| tabella: «con posa valida 111.591» | **111.570** | ERRATO |
| «nel 4,1% non restituisce posa» | 4,12% | ok |
| 12 grandezze su 33, e il loro ordine | identici a `scelte.txt` | ok |
| correlazione media fra le 12 = 0,435 | 0,435 | ok |
| otto delle dodici sono integrali | 8 | ok |
| h_pav: 1,541 cam1, secondo su 33 | 1,541, rango 2 | ok |
| h_pav: 1,124 cam2, divario 0,417 massimo | 1,124, 0,417, massimo | ok |
| il minimo la colloca ventunesima | rango 21 | ok |
| `tab:ridondanti`: 0,97 / 0,98 / 0,86 / 0,93 | 0,972 / 0,978 / 0,856 / 0,934 | ok |

## 2026-09-23 --- figure_tesi.py: lingua, titoli fuori dall'immagine, e la campagna giusta

**Tre modifiche, la terza e' una correzione di difetto.**

**1. `--lingua en`.** Le quattordici figure generate da questo script erano
rimaste in italiano mentre il Capitolo 3 usa gia' le varianti inglesi delle
figure con testo sovrapposto. `LINGUA` e `TITOLI` sono stato di modulo e non
parametri: le funzioni hanno firme diverse e passarli a mano avrebbe richiesto
di toccare ogni chiamata. Il nome del file prende il suffisso `_en`.
La virgola decimale NON cambia: i numeri nella figura devono coincidere con
quelli della didascalia, che e' in italiano.

**2. `--titoli`.** Il titolo dentro l'immagine si duplica con la didascalia,
non compare nell'indice delle figure e non si corregge senza rigenerare il PNG.
Ora e' soppresso per difetto. I titoli dei PANNELLI restano: senza, una figura
a due riquadri non si legge.

**3. LA CORREZIONE: `fig_architetture` leggeva due campagne diverse.**
Il ripiego provava `run_<arch>_tre_classi_DTW_cam1.json` e poi `..._L22.json`.
Le due forme non sono varianti dello stesso esperimento, sono **due campagne**:

| | data | dataset | riprese |
|---|---|---|---|
| forma nuda | 2026-08-20 | `feature_v2.csv` | 218 |
| `_L22` | 2026-09-09 | `feature_v5.csv` | 220 |

Cinque architetture venivano quindi da v2 e il grafo da v5. Il Capitolo 3
descrive v5 --- 220 riprese, 116.362 fotogrammi, Delta t reale, integrali
ricalcolate --- quindi l'ordine e' stato invertito e la figura legge v5.

**Il dato che ne esce, e che vale per il Capitolo 4.** L'escursione fra le
cinque architetture non a grafo vale **0,066 su v2, 0,045 su v3 e 0,032 su
v5**: correggendo l'estrazione le architetture convergono. E la classifica si
rimescola --- Spearman fra v2 e v3 vale **-0,03**, cioe' correlazione nulla,
con la LSTM che passa da prima a quinta e la foresta da ultima a terza. Stessi
soggetti, stesso protocollo, stessa soglia: cambia solo come sono calcolate le
feature.

**Verificato con:** `python pipeline/figure_tesi.py --lingua en` e senza, le
sei run lette sono tutte `_L22`. `feature_v6_220.csv` risulta identica a v5 su
tutte le colonne numeriche: e' una riestrazione di controllo, non una versione
nuova.

## [AAAA-MM-GG] — titolo
**Tipo:** fix | feature | refactor | docs | config
**File:** percorso:riga
**Perche':** ...
**Cosa cambia:** ...
**Verificato con:** comando eseguito -> esito reale
**Collegamenti:** ISS-xxx / EXP-xxx / DEC-xxx
```


## [2026-09-22] — Capitolo 4 riordinato: vista e dataset esterno sotto «Generalizzazione»

**Tipo:** docs
**File:** `tesi/Cap4.tex`

**Perche'.** Il relatore indica come filo della tesi «quanto delle prestazioni
sopravvive quando si rimuovono progressivamente le semplificazioni del
benchmark». Soggetto, vista e dataset sono quelle tre semplificazioni, ma il
punto di vista stava subito dopo il baseline, separato dal trasferimento
esterno da cinque sezioni: la progressione restava implicita.

**Cosa cambia.**
- Nuova sezione **«Generalizzazione: soggetto, vista, dataset»**, che raccoglie
  il cambio di punto di vista e il trasferimento a UR-Fall. Il cappello dichiara
  che il soggetto e' gia' stato tolto dal LOSO, e che restano vista e dataset.
- `Effetto della geometria di ripresa` diventa `\subsection{Cambio di punto di
  vista}`; `Trasferimento a un dataset esterno` scende a sottosezione e le sue
  due sottosezioni a `\subsubsection`.
- **Le etichette non cambiano**: `sec:viewpoint` e `sec:domainshift` restano,
  perche' i Capitoli 3 e 5 vi puntano.
- Riscritte le due transizioni che l'ordine precedente rendeva false: quella in
  fondo al baseline («il primo riguarda la geometria con cui il movimento viene
  osservato») e l'attacco del confronto fra rappresentazioni («una volta
  evidenziato l'effetto della geometria di ripresa»).

**Due difetti chiusi nello stesso giro.**
- `tab:etichette` era **duplicata** fra Cap3 e Cap4 con contenuti diversi ---
  220 riprese contro le 110 di camera 1. Quella di Cap4 e' ora
  `tab:etichette_valutazione`.
- La prima etichetta della sezione nuova era `sec:generalizzazione`, che
  **esisteva gia'** in `Cap2.tex:223` (lo stato dell'arte sulla
  generalizzazione). Rinominata `sec:generalizza`.

**Verificato con:** `python tesi/controlla.py` -> da **8 a 7 problemi**; restano
soltanto le sette citazioni con chiave corta non definita. Nessun CR orfano nei
sorgenti.
**Non compilato:** non c'e' un compilatore LaTeX su questa macchina.

---

## [2026-09-22] — Audit del Capitolo 3: il codice contro il capitolo

**Tipo:** docs
**File:** `docs/AUDIT_CAP3.md` (nuovo)

**Perche'.** Prima di impostare i Capitoli 4 e 5 serve sapere se il Capitolo 3
descrive per intero il metodo di cui quelli riportano i risultati. La domanda
e' una sola: ogni scelta che sta nel codice e' dichiarata nel capitolo, e ogni
cosa dichiarata corrisponde al codice?

**Cosa dice l'audit.**
- **Esistono due Capitoli 3 divergenti** --- la stesura della candidata e
  `tesi/Cap3.tex` --- e nessuna delle due contiene tutto. La base giusta e' la
  stesura; cinque blocchi vanno portati dentro.
- **Mancano alla stesura** le due sezioni chieste dal relatore (classificatori
  e regola di allarme), la dichiarazione completa del leakage a cinque
  operazioni con le due misure, il filtro di ridondanza del DTW, e le due
  tabelle riassuntive.
- **Copertura codice -> metodologia** voce per voce: estrazione, selezione,
  finestre, etichette, modelli, decisione.
- **Un'imprecisione nel Capitolo 4:** `sec:normalizzazione` dice che il
  logaritmo si applica «per le grandezze che soddisfano il criterio previsto
  nella fase di preprocessing». **Un criterio non esiste**: `src/dati.py:170`
  ha un elenco fisso di 14 nomi, compilato guardando le distribuzioni.
- **Figure:** nessuna figura di risultati e' finita in Cap3, non c'e' niente da
  spostare. Restano due segnaposto e un disallineamento di lingua (il capitolo
  usa le varianti `_en`).
- **Testo:** tre errori di fatto, `
um{}` con le virgole che rompe i numeri,
  le citazioni con chiave corta che non esistono (7 degli 8 problemi di
  `controlla.py` si chiudono rinominandole), quattro `\ref{sec}` segnaposto,
  una duplicazione e una dozzina di refusi.

**Verificato con:** lettura di `src/modelli.py`, `src/dati.py`, `src/dtw.py`,
`src/geometry.py`, `pipeline/estrai_feature.py`, `deploy_board/rileva.py`;
conteggi ricontati su `feature_v5.csv`; chiavi di bibliografia confrontate con
`tesi/Bibliografia.tex`.

**Limite dichiarato:** il testo esaminato si interrompe a meta' di «Robustezza
e limiti». Pavimento, DTW, finestre e definizione del compito **non sono stati
controllati**.

---

## [2026-09-22] — Il DTW in figura: l'allineamento e la banda

**Tipo:** feature
**File:** `pipeline/figura_dtw.py` (nuovo), `tesi/Cap3.tex` (sez. `sec:dtw`),
`tesi/figure/fig_dtw_spiegazione[_en].png`

**Perche'.** `sec:dtw` spiega a parole tre cose che si capiscono guardandole:
perche' una distanza punto per punto non basta, che cosa vuol dire deformare
l'asse dei tempi, e che cosa cambia imponendo `|i-j| <= 10`. Sono un
allineamento e una matrice.

**Cosa cambia.** Una figura a due pannelli, inserita subito dopo
l'introduzione al DTW e prima della sottosezione sulla normalizzazione:
- **(a)** due riprese di caduta con lo stesso andamento e il picco sfasato di
  undici campioni, con le corrispondenze del cammino;
- **(b)** la matrice dei costi cumulati, con la diagonale --- cioe' il
  confronto uno-a-uno che una distanza euclidea imporrebbe --- la regione che
  la banda esclude, e il cammino di costo minimo.

**E' metodologica, non sperimentale**, ma i dati sono veri: curve vere,
z-scored e ricampionate a 200 come fa la selezione, e cammino vero.

**Due cose che lo script fa invece di assumere.**
1. `src/dtw.py` non conserva la matrice --- tiene due righe, perche' su 33
   grandezze per due camere una 200x200 per coppia costerebbe memoria senza
   servire. Qui la ricorsione e' ripetuta per intero e lo script **verifica che
   la distanza coincida con quella di `src.dtw`**, fermandosi altrimenti: senza,
   la figura mostrerebbe un allineamento diverso da quello che decide la
   selezione. Coincide (0,030633).
2. **La coppia e' scelta sulla forma, non sullo scarto fra i picchi.** La prima
   versione prendeva la coppia con i picchi distanti ~12 campioni e accoppiava
   una curva con un plateau a una con un picco stretto: due forme diverse, che
   non illustrano la deformazione. Ora si filtra sullo scarto e si massimizza
   la correlazione dopo il riallineamento: **r = 0,995**.

**Un dato che la figura rende visibile:** 69 dei 251 passi del cammino stanno
sul bordo della banda. Il vincolo non e' decorativo, morde.

**Difetto introdotto e corretto in corsa:** la prima etichetta era `fig:dtw`,
che **esisteva gia'** in `Cap4.tex:483` (i punteggi sulle due viste).
`controlla.py` e' passato da 8 a 9 problemi; rinominata `fig:dtw_allineamento`,
torna a 8.

**Verificato con:** `python pipeline/figura_dtw.py [--lingua it]`; `python
tesi/controlla.py` -> Cap3 a **11 figure**, `PROBLEMI: 8`, i preesistenti.
**Non compilato:** non c'e' un compilatore LaTeX su questa macchina.

---

## [2026-09-22] — La retta del pavimento in figura: da fotografia annotata a diagramma

**Aggiornamento in giornata.** La prima versione disegnava sopra il fotogramma.
Il fondo di UP-Fall e' una hall con vetrate, manifesti e tavoli: la retta e le
osservazioni ci finivano sopra, e **la cosa che la figura deve mostrare era
quella che si vedeva peggio**. Rifatta come **diagramma**: fondo pulito,
coordinate vere dei landmark, retta vera del motore. Cambia il fondo, non i
numeri. Il fotogramma resta con `--sfondo foto`, perche' serve a controllare
che lo scheletro sia della persona e non una posa inventata.

**Legenda con una voce per ogni oggetto, $L$ compreso** --- prima era una
freccia verde che il lettore doveva indovinare. La didascalia dichiara ora
anche che $L$ e' la stessa grandezza che normalizza le distanze di A3, e quanto
misura in pixel.

---

## [2026-09-22] — La retta del pavimento in figura, e uno scheletro senza indici

**Tipo:** feature
**File:** `pipeline/figura_pavimento.py` (nuovo), `pipeline/figura_landmark.py`,
`tesi/Cap3.tex` (sez. `sec:pavimento`), `tesi/figure/fig_pavimento.png`

**Perche'.** `sec:pavimento` descrive a parole una costruzione geometrica fatta
di quattro oggetti --- ingombro, osservazioni, retta, segmento --- che il
lettore deve tenere a mente uno per uno. In figura si vedono insieme.

**Cosa cambia.**
- **`figura_pavimento.py`**, una figura su un pannello solo: il fotogramma con
  lo scheletro, l'ingombro dei 33 landmark con il bordo inferiore marcato, le
  osservazioni $(x_{bacino}, y_{bordo})$ raccolte su altri fotogrammi, la retta
  adattata, e $h_{pav}$ quotata di lato come in un disegno tecnico --- dentro
  le gambe il segmento non si leggeva.
- **Niente e' disegnato a mano.** Le osservazioni sono `_pav_oss` del motore,
  la retta e' `_pav_retta` (il `polyfit` vero), `h_pav` e' cio' che
  `altezza_su_pavimento` restituisce. La scheda `.txt` riporta i valori di
  quella esecuzione: 423 osservazioni su 600 fotogrammi, retta
  `y = +0,0400x + 425,3`, `h_pav = +1,645`.
- **Il problema dei landmark fuori dal bordo NON e' disegnato**, deliberatamente:
  servirebbe un secondo pannello e toglierebbe leggibilita' a cio' che la figura
  deve spiegare. Resta dichiarato nel testo.
- **`figura_landmark.scheletro` accetta `indici=False`.** Gli indici MediaPipe
  dicono QUALI punti una rappresentazione usa; in una figura che spiega una
  costruzione geometrica sono rumore, e coprivano la quota. Il valore
  predefinito lascia invariato il comportamento per gli altri script.

**Da dichiarare, ed e' nella didascalia:** qui le osservazioni vengono da due
riprese, nel dataset da tutte quelle di una telecamera. Il tipo di stima e' lo
stesso, i coefficienti no.

**Lingua e leggibilita' (stessa giornata).** Il capitolo usa le varianti
**inglesi** delle figure con testo sovrapposto (`fig_landmark_en`,
`fig_momenti_a*_en`, `fig_tracciatore_en`, `fig_spostamento_en`): questa era
l'unica in italiano, ed e' stata rifatta con `--lingua en`. Cap3 punta ora a
`fig_pavimento_en.png`; la variante italiana resta prodotta.

Sulla leggibilita' sono stati corretti tre difetti trovati guardando il
risultato:
- le osservazioni arancioni al 35% di opacita' sparivano sul pavimento grigio.
  La fotografia viene ora **schiarita del 30%** (`--chiaro`) e i punti portati
  all'80%: e' la cosa che la figura deve mostrare, e non si vedeva;
- l'alone bianco era fisso a 4,2 e su un tratto sottile lo **sbianca** invece
  di staccarlo: l'ingombro tratteggiato sembrava bianco. Ora ci sono due
  livelli, commisurati allo spessore;
- l'etichetta `$L$` finiva sotto la freccia verde, ed e' stata spostata.
  Si usa `$L$` e non `$L_{tronco}$`, come gia' fa `riferimento_a3`.

**Verificato con:** `python pipeline/figura_pavimento.py [--lingua en]` ->
figure e schede prodotte; `python tesi/controlla.py` -> Cap3 passa da 9 a
**10 figure**, `PROBLEMI: 8`, gli stessi preesistenti, nessuna figura senza
immagine.
**Non compilato:** non c'e' un compilatore LaTeX su questa macchina.

---

## [2026-09-22] — La scelta di K misurata dentro il fold, e la direzione del leakage era sbagliata

**Tipo:** feature + docs
**File:** `pipeline/estrai_k_multiplo.py` (nuovo), `pipeline/k_per_fold.py`
(nuovo), `tesi/Cap3.tex` (`sec:leakage`), `tesi/Cap5.tex` (`sec:finestra-k`)

**Perche'.** [ISS-178](ISSUES.md#iss-178) aveva accertato che `K_INTEGRALI = 31`
non e' fissato a priori ma scelto per scansione, e che la scansione guarda i
fold di prova. Dichiararlo non bastava a dirne l'entita'.

**Cosa cambia.**
- **`estrai_k_multiplo.py`**: estrae le grandezze a piu' valori di K in **una
  sola passata di stima di posa**, alimentando N motori geometrici con gli
  stessi landmark. Cinque estrazioni costerebbero 103 minuti l'una; questa ne
  costa 66 per tutte e cinque, su camera 1. Verifica che K tocchi soltanto le
  nove colonne integrali e si ferma se non e' cosi'.
- **`k_per_fold.py`**: il protocollo annidato --- K scelto con un LOSO interno
  sui soli soggetti rimasti --- con il controllo di riproduzione contro
  `feature_v5.csv` prima di qualunque confronto.
- **Cap3 `sec:leakage`**: nuova `tab:k_misura` e il risultato. **Il paragrafo
  scritto stamattina dichiarava «la direzione dell'errore e' la stessa degli
  altri casi --- prestazioni sopravvalutate»: e' smentito.** Nove fold su dieci
  scelgono K=45 e l'F2 medio sale da 0,825 a 0,851.
- **Cap5 `sec:finestra-k`**: tolto il «limite superiore», che per K e' falso;
  aggiunto il richiamo alla misura.

**Verificato con:** `python pipeline/k_per_fold.py --controlla` -> «riproduce
esattamente feature_v5 sulle colonne adottate», scarto 0,000e+00 su 12 colonne e
58.359 fotogrammi. Estrazione: «nessuna divergenza sulle colonne non
integrali»; retta del pavimento identica all'estrazione di settembre.
`python tesi/controlla.py` -> `PROBLEMI: 8`, gli stessi preesistenti.
**Non compilato:** non c'e' un compilatore LaTeX su questa macchina.

**Collegamenti:** [EXP-045](EXPERIMENTS.md#exp-045),
[ISS-178](ISSUES.md#iss-178)

---

## [2026-09-22] — Il leakage dichiarato per intero: cinque operazioni, non quattro

**Tipo:** docs
**File:** `tesi/Cap3.tex` (`sec:leakage`), `tesi/Cap5.tex` (`sec:finestra-k`)

**Perche'.** Il relatore chiede che il punto sul data leakage sia dichiarato
esplicitamente, e che l'elenco comprenda **hyperparameter tuning** accanto a
normalizzazione, feature selection e threshold. Controllando quella voce e'
emerso che non reggeva: `K_INTEGRALI = 31` non e' fissato a priori, e' il
risultato di una scansione ([ISS-178](ISSUES.md#iss-178)).

**Cosa cambia.**
- **Il procedimento corretto e' scritto per intero**, come sequenza numerata,
  nelle parole del relatore: si mette s da parte, si calcola il criterio di
  selezione sui rimasti, si stima la normalizzazione sui rimasti, si addestra e
  si tara sui rimasti, si congela tutto, si valuta su s una volta sola. E
  accanto, l'ordine che non e' corretto.
- **Le operazioni diventano cinque.** Gli iperparametri del modello (a priori,
  corretti) sono separati dai parametri della rappresentazione (K, scelto per
  scansione). Due su cinque non rispettano il procedimento: K e la selezione
  DTW.
- **K dichiarato.** La colonna di laboratorio della scansione viene dai fold di
  prova; il pareggio 31 contro 45 e' stato rotto sul richiamo di campo, che il
  Capitolo 5 riporta poi come risultato. La scansione e' a cinque soggetti e non
  e' stata ripetuta. Direzione dell'errore: prestazioni sopravvalutate, come per
  il DTW.
- **Il contrasto utile:** anche la lunghezza della finestra di classificazione
  e' stata sottoposta a scansione, ma li' si e' tenuto il valore a priori.
  Misurare e cambiare non e' come misurare e tenere, e il testo lo dice.
- `Cap5.tex`: `tab:kappa` dichiarata per quello che e'.

**Verificato con:** `python tesi/controlla.py` -> `PROBLEMI: 8`, gli stessi
preesistenti. Scansione ricontrollata su
`risultati/cinque_soggetti/scansione_k_cinque_soggetti.json`. Controllo dei CR
orfani su tutti i `.tex` e i `.md` dopo un'iniezione difettosa riparata in
corsa: **0 file guasti**.
**Non compilato:** non c'e' un compilatore LaTeX su questa macchina.

**Collegamenti:** [ISS-178](ISSUES.md#iss-178),
[EXP-053](../../DIP_PROJECT/docs/EXPERIMENTS.md#exp-053)

---

## [2026-09-22] — La regola di allarme diceva il contrario del codice, e il protocollo di campo si chiude

**Tipo:** docs
**File:** `tesi/Cap3.tex` (`sec:allarme`), `tesi/Cap5.tex` (`tab:campo`),
`tesi/Conclusioni.tex`, `risultati/sessioni/LEGGIMI.md`

**Perche'.** Verifica voce per voce dei due elenchi del relatore --- quello sui
classificatori e quello sulla regola di allarme. Il primo risultava coperto; il
secondo no, e controllando le voci mancanti e' emerso che la sezione
descriveva la regola al contrario di come la calcolano la board e l'analisi.

**Cosa cambia.**
- **`sec:allarme` riscritta** ([ISS-175](ISSUES.md#iss-175)). L'allarme scatta
  alla **quinta** finestra e non alla prima --- il testo diceva il contrario, e
  sottostimava la latenza del termine di persistenza, che il Capitolo 5 conta
  invece come il 26,4% del totale. L'intervallo refrattario si conta
  dall'**ultimo allarme**, non dall'ultima finestra positiva. Nuova
  `tab:allarme` con le sei voci chieste dal relatore, e i paragrafi sulle due
  contabilita'.
- **`tab:campo` completata** ([ISS-176](ISSUES.md#iss-176)). Partecipanti e
  dimensioni degli ambienti: **non rilevati**, dichiarati tali. Ore di presenza
  sostituite da **ore con posa valida, 7,45 su 9,58**, calcolate dai dodici
  riepiloghi e dichiarate come limite inferiore.
- **Coerenza sulla soglia completata.** `Conclusioni.tex` descriveva la terza
  correzione del protocollo come «soglia scelta su un terzo insieme»; Cap4
  `sec:baseline` la descrive correttamente come «un insieme di validation
  distinto dal soggetto di test». Allineata.
- **[ISS-177](ISSUES.md#iss-177):** il LEGGIMI delle sessioni diceva 47,8 dove
  il valore calcolato e' 44,8.

**Verificato con:** `python tesi/controlla.py` -> `PROBLEMI: 8`, gli stessi
preesistenti, nessuno nuovo. Ore con posa ricalcolate dai `riepilogo.json`
(totale 9,58 h, coincide con le «circa 9,6 ore» del capitolo). Semantica della
regola letta in `deploy_board/rileva.py:1016`,
`pipeline/eventi_sessioni.py:114-130` e `pipeline/latenza.py:96-135`.
**Non compilato:** non c'e' un compilatore LaTeX su questa macchina.

**Collegamenti:** [ISS-175](ISSUES.md#iss-175), [ISS-176](ISSUES.md#iss-176),
[ISS-177](ISSUES.md#iss-177), [DEC-105](DECISIONS.md#dec-105),
[DEC-108](DECISIONS.md#dec-108)

---

## [2026-09-22] — Capitolo 3: le due sezioni chieste dal relatore, e una soglia dichiarata al contrario

**Tipo:** docs
**File:** `tesi/Cap3.tex`, `tesi/Cap4.tex`, `tesi/Cap2.tex`

**Perche'.** Ripresa del lavoro sulle richieste del relatore del 14 settembre.
Delle sue richieste sul Capitolo 3 ne restavano aperte due --- la descrizione
dei classificatori e la regola che porta dalla finestra all'evento --- e la
seconda era gia' stata scritta. Cercando la prima e' emerso che le sei
architetture non erano descritte in nessun punto della tesi, e da li' altri due
difetti.

**Cosa cambia.**
- **`sec:modelli`, nuova** ([ISS-173](ISSUES.md#iss-173)). `tab:modelli` con
  struttura e parametri delle sei architetture, piu' i paragrafi su uscita,
  arresto anticipato, rete a grafo, foresta e iperparametri non cercati. La
  descrizione del grafo viene dal Capitolo 4, dove stava in mezzo ai risultati;
  `Cap2.tex` ora rimanda qui e ha l'etichetta `sec:famiglie`.
- **`sec:ridondanza`, nuova** ([ISS-174](ISSUES.md#iss-174)). Il filtro di
  correlazione a 0,85, le quattro grandezze escluse, l'elenco delle dodici
  adottate, e il limite del criterio con `A3_h_pavimento` **21ª su 33** --- non
  19ª, che e' il rango nella classifica v3 e non in quella adottata.
- **La soglia** ([ISS-172](ISSUES.md#iss-172)). Il Capitolo 3 la dichiarava
  scelta sul validation; e' **fissa a 0,50, dichiarata a priori**
  ([DEC-105](DECISIONS.md#dec-105)). Corretti `tab:addestramento`,
  `tab:leakage`, la prosa di `sec:leakage`, `sec:modelli` e `sec:allarme`, e il
  paragrafo del Capitolo 4 che citava la frase del relatore descrivendo cosi'
  la procedura scartata.

**Verificato con:** `python tesi/controlla.py` -> `PROBLEMI: 8`, gli stessi
preesistenti (label `tab:etichette` duplicata, sette citazioni non definite),
nessuno nuovo, nessun riferimento orfano. Conteggi dei parametri ricontati sui
`risultati/addestramento/run_*.json` e coincidenti con `tab:architetture` del
Capitolo 4. Rango di `A3_h_pavimento` ricontato su entrambe le classifiche.
**Non compilato:** non c'e' un compilatore LaTeX su questa macchina.

**Collegamenti:** [ISS-172](ISSUES.md#iss-172), [ISS-173](ISSUES.md#iss-173),
[ISS-174](ISSUES.md#iss-174), [DEC-105](DECISIONS.md#dec-105),
[EXP-010](EXPERIMENTS.md#exp-010), [EXP-023](EXPERIMENTS.md#exp-023)

---

## [2026-09-21] — `dtw.py`: il pruning restituiva `inf`, e tre grandezze sparivano

**Tipo:** fix
**File:** `src/dtw.py:106` (`use_pruning`), `pipeline/dtw_per_fold.py` (nuovo),
`tesi/Cap3.tex` (sez. `sec:leakage`)
**Perche':** `distance_fast` veniva chiamata con `window=` e
`use_pruning=True` insieme. Il limite di potatura viene dalla distanza
euclidea, che non e' un maggiorante del DTW vincolato: per certe coppie la
funzione pota tutto e torna `inf`. L'infinito azzera il punteggio della
grandezza (se cade nelle distanze intra) oppure lo manda a `inf` (se cade nelle
incrociate), sempre in silenzio. Tre grandezze su 33 ne erano colpite e la
selezione che ne usciva non era quella adottata.
**Cosa cambia:** `use_pruning=False`, con il commento che spiega perche' non e'
una scelta di prestazione. Aggiunto `pipeline/dtw_per_fold.py`, che rifa' la
selezione dentro ogni fold LOSO e si ferma se non sa riprodurre quella adottata
sull'intero insieme. La sezione `sec:leakage` del Capitolo 3 passa da «verifica
non eseguita» al risultato misurato.
**Verificato con:** `python pipeline/dtw_per_fold.py --csv feature_v5.csv --top 12`
-> controllo «riproduce esattamente scelte.txt»; 0 fold su 10 riproducono la
selezione adottata, Jaccard medio 0,769. `python tesi/controlla.py` -> gli
stessi 8 problemi preesistenti, nessuno nuovo.
**Collegamenti:** [ISS-168](ISSUES.md#iss-168), [EXP-044](EXPERIMENTS.md#exp-044)

---

## [2026-09-15] — `figura_landmark.py`: quali punti usa ciascuna rappresentazione

**Tipo:** feature
**File:** `pipeline/figura_landmark.py` (nuovo), `tesi/Cap3.tex` (sez. Landmark
utilizzati, sez. `sec:tracciatore`)

**Perche'.** La tabella dei landmark elencava quattro righe di indici. Dice
quanti punti servono a A1, A2, A3 e B, non dove stiano sul corpo ne' a quale
costruzione geometrica servano. Serviva la stessa informazione su una posa
vera.

**Cosa cambia.**
- **A1 formalizzata** (richiesta della candidata). La sottosezione diceva
  «si calcola la matrice di covarianza, gli autovettori danno le direzioni»
  senza scriverlo. Ora ci sono tre equazioni fedeli a
  `MotoreGeometrico._ellisse`: `eq:covarianza` (baricentro e covarianza
  campionaria sui sette punti, denominatore $|J|-1$ come `np.cov`),
  `eq:autovalori` (decomposizione spettrale, $\lambda_1 \ge \lambda_2 \ge 0$,
  autovettori ortogonali perche' $S$ e' simmetrica semidefinita positiva) e
  `eq:ellisse` ($a=\sqrt{\lambda_1}$, $b=\sqrt{\lambda_2}$, $\theta$ da
  `atan2`). L'elenco delle grandezze rimanda ora ai simboli invece di
  nominarli a parole.
  Il passaggio chiave, che giustifica anche la figura: **le radici degli
  autovalori sono le deviazioni standard della nuvola lungo gli assi
  principali**, quindi i semiassi dell'ellisse di dispersione --- ed e' il
  motivo per cui `fig_landmark` la disegna a due sigma dichiarandolo.
  **Citazione**: `\cite{HO}` per la famiglia di feature. Verificato sul PDF:
  Hoang et al. classificano fra le handcrafted i «parameters of external
  ellipse enclosing the human body (PEE)» (Figura 4 e tabella comparativa).
  Il testo dichiara pero' la differenza: quella e' un'ellisse che **racchiude**
  la persona, A1 usa i **momenti secondi** della nuvola. Nessuna citazione
  aggiunta per la PCA in se': non c'e' in bibliografia e non e' stata
  verificata --- se serve, va scelta e controllata.
- **La giustificazione del «niente filtro» spostata dove sta la prova**
  (2026-09-16, rilievo della candidata: non ha senso dare peso a una
  sottosezione che parla di una cosa non usata, e il dato sul rumore sta
  altrove). `sec:filtraggio` ora si ferma a enunciare la scelta e rimanda; le
  tre ragioni stanno in `sec:robustezza`, subito dopo `tab:rumore`, sotto il
  paragrafo «Perche' la pipeline non filtra le coordinate»:
  1. **misurata**: iniettando rumore fino a 0,04 lunghezze di torso il calo
     massimo di $F_2$ e' 0,031, sotto la dispersione fra soggetti (+-0,08);
     se aggiungere rumore non fa danno, toglierlo non fa granche' bene;
  2. una regolarizzazione c'e' gia', **su scala maggiore**: le integrali
     accumulano su 1,72 s contro i ~0,5 s di memoria efficace di un EMA a
     alpha=0,10, e il DTW ne tiene 8 su 12 contro 2 derivate;
  3. un filtro ricorsivo ha **stato**, da azzerare identico in estrazione e
     sul dispositivo: e' esattamente la divergenza gia' capitata (GUI
     filtrata, addestramento no, ISS-009).
  **Nota per chi legge**: non esiste una DEC che registri questa scelta. Sono
  ragioni che sostengono la configurazione adottata, non una decisione presa
  in anticipo, e il testo e' formulato di conseguenza.
  Aggiunte le label `sec:filtraggio` e `sec:robustezza`.
- **`fig:ema` e `tab:ema` TOLTE da Cap3, e il paragrafo riformulato**
  (2026-09-16). Presentavano come difetto una cosa che difetto non e'.
  Verificato: la selezione delle grandezze (`pipeline/analisi_dtw.py`) legge
  il **CSV estratto**, cioe' le stesse coordinate non filtrate su cui il
  modello si addestra, viene valutato e gira sul dispositivo. Le curve
  lisciate della GUI (`DIP_PROJECT/src/dataset_live_reader.py`, EMA su
  posizioni e velocita' piu' un secondo EMA di display a 0,3 regolabile da
  `ema_spin`) erano uno strumento di ispezione e **non hanno mai deciso
  nulla**; la tesi non nomina la GUI. Non c'e' quindi incoerenza fra cio' che
  e' stato guardato e cio' su cui il modello ha imparato, in nessun punto
  riportato.
  Il testo dice ora la cosa in positivo --- «la configurazione adottata non
  applica alcun filtraggio temporale», con la ragione (niente ritardo) e il
  prezzo (le derivate restano esposte) --- invece di confessare un parametro
  inerte. `pipeline/figura_ema.py` e `fig_ema.png` restano: i numeri
  (oscillazione -76%, ampiezza -6%, ritardo 167 ms a alpha=0,10) servono come
  sviluppo futuro quantificato, non come metodo.
- **`figura_ema.py`: il filtro va applicato alle COORDINATE, non alle
  grandezze.** Rilievo della candidata, ed era giusto. La prima versione
  filtrava `A3_angolo_tronco`, cioe' una grandezza gia' calcolata. I due
  parametri del progetto precedente sono pero' argomenti del **costruttore**
  di `GeometryEngine` (`DIP_PROJECT/src/geometry.py:52`), uno per le posizioni
  e uno per le velocita': dovevano agire dentro il motore, sui landmark. Un
  terzo, `EMA_ALPHA_FEAT`, destinato alle grandezze, era scritto e
  **commentato** (`extract_video_features_curves.py:29, 190`).
  Lo script ora fa la cosa fedele: una sola passata dello stimatore, poi le
  coordinate filtrate e le grandezze **ricalcolate con `MotoreGeometrico`**,
  una volta per ciascun alpha. Numeri aggiornati di conseguenza (oscillazione
  a $\alpha=0{,}10$: 78% -> **76%**).
- **Nuovo `pipeline/figura_ema.py` e `fig:ema` + `tab:ema` in Cap3.** La
  sezione sul filtraggio affermava il compromesso di $\alpha$ senza un numero.
  La figura lo misura su due riprese dello stesso archivio, scelte dal
  programma: quella a escursione minima (persona quasi ferma) e quella a
  escursione massima (caduta), prese sul **tratto continuo di posa valida piu'
  lungo**.
  Risultato: a $\alpha=0{,}10$ l'oscillazione su persona ferma cala del
  **78%** e l'ampiezza della caduta perde solo il **6%**, con **167 ms** di
  ritardo. Il compromesso e' quindi meno severo di quanto la formulazione
  qualitativa lasciasse temere.
  **I valori di $\alpha$ non sono inventati**: 0,05 e 0,10 sono
  `EMA_ALPHA_POS` e `EMA_ALPHA_VEL` in
  `DIP_PROJECT/src/extract_video_features_curves.py:27-28`. Verificato inoltre
  che in `DIP_PROJECT/src/geometry.py` `alpha_pos` e `alpha_vel` compaiono
  **solo** nella firma di `__init__` e nelle due assegnazioni (righe 52-54):
  il filtro era dichiarato e mai applicato, come il capitolo diceva. Ora il
  testo cita i valori veri e dice dove stavano.
  La didascalia dichiara che il filtro **non** e' stato applicato ai dati:
  la figura e' una ricostruzione a posteriori.
- **Corretto un difetto della prima versione della figura**: tracciava
  attraverso le interruzioni di posa, cioe' proprio cio' che il capitolo
  vieta. Verificato al passaggio che gli **8** salti superiori a 180 gradi
  presenti in `feature_v2_omnifall.csv` stanno **tutti** a cavallo di una
  perdita di posa: lo srotolamento di `_srotola` funziona, il salto e' il
  passaggio dallo zero segnaposto al primo valore vero.
- **Rappresentazione B tolta dal capitolo** (decisione della candidata,
  2026-09-15): la tesi confronta tre rappresentazioni feature-based
  supervisionate, e basta. Rimossi la riga B dalla tabella dei landmark, il
  paragrafo «Rappresentazione scheletrica grezza» e i due rimandi incrociati.
  Il rilievo sulla rumorosita' di polsi e gomiti resta, riscritto in positivo:
  dice perche' le tre rappresentazioni **non** usino gli arti superiori,
  senza appoggiarsi a una rappresentazione che non c'e' piu'.
  `\cite{lstm}` sarebbe tornato orfano: spostato in Cap4 dove le architetture
  vengono introdotte, insieme a `\cite{gru}` e `\cite{randomforest}`, che
  erano orfani anche loro. Orfane scese da 16 a 13.
- **Il ricordo del confronto A/B era comunque capovolto**, e si registra qui
  perche' non torni fuori.
  La candidata ricordava che il confronto iniziale avesse mostrato le
  grandezze progettate superiori a quelle apprese dallo scheletro. I file del
  progetto precedente dicono l'opposto:
  `DIP_PROJECT/results_comparison/final_comparison.txt` riporta
  **Method A (fisiche + GRU) F1 = 0,0000** contro **Method B (autoencoder +
  RF) F1 = 0,3509**, e conclude «the best performing model is METHOD B».
  `DIP_PROJECT/docs/EXPERIMENTS.md` EXP-001 lo marca **non valido** e scrive
  esplicitamente che quella conclusione «non va usata in relazione», per tre
  ragioni: nessuno scaler (ISS-008, rapporto di scala **646x**, causa
  principale dell'F1 = 0), Method B etichettato con `label_mode='last'`
  invece di `assign_window_label` (ISS-020, quindi verita' di riferimento
  diverse), split per video (ISS-007).
  Il paragrafo di Cap3 su B ora riporta l'esito vero e dice perche' non sia
  usabile in **nessuna** delle due direzioni, invece di lasciar intendere che
  l'esito sia semplicemente ignoto. Aggiunto il collegamento verificato: la
  grandezza che dominava le scale era `energy`
  (`DIP_PROJECT/src/geometry.py:163`), cioe' la stessa `eq:energia` eliminata
  poco sopra per incoerenza dimensionale.
  B **resta in tabella e nel testo** come percorso esplorato e abbandonato;
  la scelta di proseguire con grandezze progettate e' ora ancorata alle
  ragioni di `sec:pose` e non a quel confronto.
- **Nuovo `pipeline/campi_landmark.py`: che cosa contengono davvero x, y, z e
  visibility.** Misurato su 2.524 fotogrammi con posa, 20 riprese, dieci
  soggetti. Quattro risultati, due dei quali correggono il testo:
  - **«normalizzate fra 0 e 1» era sbagliato.** Quando un punto cade fuori
    dall'inquadratura il modello lo estrapola: x esce da [0,1] nel 2,1% dei
    casi, **y nel 12,7%**, con massimo 1,46. Il testo dice ora «normalizzate
    su larghezza e altezza» e riporta il fatto;
  - **l'origine di z e' il bacino**: sul punto medio delle anche z vale zero
    nel 100% dei fotogrammi. La documentazione dice solo «profondita'
    relativa»;
  - **i world landmark sono in metri**: tronco mediano 0,486 m (0,389-0,523).
    Convalida l'affermazione gia' in tesi sui $3\cdot10^{-5}$ m del bacino,
    che non era mai stata controllata;
  - **la visibilita' crolla sugli arti inferiori, in modo asimmetrico**:
    spalle e anche sopra 0,99, ma ginocchio e caviglia del lato lontano dalla
    telecamera hanno mediana 0,43 e 0,49 e stanno sotto 0,5 nel 61% e 52% dei
    fotogrammi. Sono **i punti con cui A3 arricchisce A2**. Il passaggio sulla
    visibilita' non usata ora porta questi numeri.
- **Polarizzamento della stima del pavimento, quantificato.** La stima usa il
  bordo inferiore del riquadro di tutti e 33 i punti, e le estremita' sono
  spesso estrapolate sotto l'immagine (punta del piede 48% dei fotogrammi,
  polso 32%). Su una ripresa di controllo il 17,8% delle osservazioni viene da
  riquadri che sporgono sotto il bordo, eccesso mediano 60 px su 480;
  riadattando la retta sulle stesse osservazioni con le ordinate limitate
  all'altezza dell'immagine, la stima si sposta di **12 pixel**, circa un
  sesto di lunghezza di tronco. Dichiarato in `sec:pavimento`.
  *(Lo scarto e' misurato fra due adattamenti sullo stesso insieme di
  osservazioni; i coefficienti assoluti non coincidono con quelli di
  `_pavimento`, che riadatta ogni 50 osservazioni e filtra anche
  sull'angolo del tronco.)*
- **La sottosezione «Landmark utilizzati» e' stata sciolta.** Conteneva una
  tabella di indici e nient'altro. Si era provato a riempirla spiegando come
  MediaPipe produce i landmark, ma non c'e' abbastanza materiale: la rete li
  regredisce e non esiste una formula da riportare. Il contenuto e' quindi
  stato ridistribuito dove serve, e ogni pezzo e' verificato su
  arXiv:2006.10204:
  - in `sec:pose`, una frase su che cosa sia un landmark come numeri ---
    coordinate **normalizzate in [0,1]** riportate in pixel dalla pipeline,
    piu' profondita' e visibilita';
  - in «Assenza della posa e instabilita'», il rilievo che **la visibilita'
    esiste e la pipeline non la legge**. Verificato: `grep -c visibility
    src/geometry.py pipeline/estrai_feature.py` -> 0 e 0. Sta li' perche' e'
    la sezione sull'inaffidabilita' dei punti, e i due presidi descritti
    subito dopo agiscono sul fotogramma e non sul singolo punto;
    **RISCRITTO il 2026-09-16**: la prima stesura lo presentava come una
    semplificazione non giustificata. Non lo e'. `DIP_PROJECT/docs/
    EXPERIMENTS.md` EXP-052 (2026-08-17, `scripts/occlusioni_mediapipe.py`,
    26.548 fotogrammi) aveva gia' misurato la cosa: naso, spalle e anche
    restano sopra 0,98 in tutte le fasi, i gomiti scendono da 0,813 a 0,521 a
    terra, ginocchia e caviglie perdono ~20%. **Con soglia 0,50 il 100% dei
    fotogrammi supera il filtro in tutte e tre le fasi**, perche' a decidere
    sono i punti del tronco, saturi: il filtro non fa alcun lavoro. Non e'
    quindi un'omissione, e' una verifica con esito negativo.
    Il residuo vero --- un uso **per punto** sugli arti --- e' ora dichiarato
    come tale, con accanto il costo stimato: `tab:occlusioni` di Cap4 mostra
    che congelare ginocchia e caviglie sposta $F_2$ di **+0,001**, cioe' i
    punti su cui la visibilita' sarebbe informativa non spostano il
    risultato. Aggiunto il rimando a `sec:occlusioni`.
  - in `sec:rappresentazioni`, la tabella dei punti per rappresentazione, la
    `fig:landmark` e la nota sui 33 punti usati da A3 per il pavimento;
  - in `sec:rappresentazioni`, sottosezione A3, l'osservazione che lo
    stimatore compie **internamente le stesse tre operazioni** di A3 (bacino
    al centro, rotazione sulla congiungente anche-spalle, scala su riquadro
    quadrato, §2.3 del paper), con la precisazione che quella agisce
    sull'ingresso della rete e la `eq:normalizzazione` sull'uscita.
- **Una figura sola invece di tre** (`--insieme`, `fig_landmark_en.png`):
  fotografia a sinistra, poi A1, A2 e A3 su fondo chiaro, senza la persona
  sotto. La posa e' la stessa per tutte e tre, quindi ripeterla tre volte non
  aggiungeva niente; il primo pannello dimostra che la posa e' vera, gli altri
  tre lasciano leggere la geometria senza nulla intorno. Cap3 usa questa;
  le tre separate restano generabili senza `--insieme`.
- Le tre figure separate, una per rappresentazione --- `fig_landmark_a1.png`, `_a2`, `_a3`
  (+ `_en`, flag `--lingua`). Ciascuna ha due pannelli: lo stesso fotogramma
  RGB due volte, e a destra **lo scheletro sovrapposto alla persona**, non
  accanto. Una prima stesura lo disegnava su fondo bianco e sembrava un
  omino di fantasia; sopra la fotografia si vede che e' la posa di quel
  fotogramma. Le ossa portano un alone bianco (`patheffects.withStroke`),
  senza il quale il grigio sparisce nel pavimento scuro e il rosso nella
  maglietta. Dentro la figura non c'e' testo descrittivo, solo il titolo dei
  pannelli: le didascalie stanno nel capitolo.
- Prova visiva del pavimento: sovrapposta all'immagine, la retta stimata cade
  ai piedi della persona. Non era verificabile finche' il pannello era bianco.
- Gli indici sono **importati** da `src/geometry.py` (`PUNTI_ELLISSE`, `NASO`,
  `SPALLA_*`, `ANCA_*`, `GINOCCHIO_*`, `CAVIGLIA_*`), non ricopiati: se il
  codice cambiasse i punti, cambierebbe la figura. B non ha figura --- e' la
  rappresentazione abbandonata nella fase preliminare.
- **Il pavimento e' quello vero.** In una prima stesura era una riga tracciata
  al bordo inferiore dell'ingombro del fotogramma, cioe' un'approssimazione di
  chi disegnava. Ora `stima_pavimento()` fa girare `MotoreGeometrico.a3` sui
  fotogrammi, lascia che `_pavimento` accumuli le osservazioni erette e adatti
  la retta ai minimi quadrati, e legge `_pav_retta`. La retta disegnata esce
  dal codice di produzione. Differenza dichiarata nella scheda `.txt`: nel
  dataset la retta e' stimata su tutte le riprese di una telecamera, qui sulle
  riprese passate a `--pavimento`.
- **L'ellisse di A1 a due deviazioni standard**, cosi' avvolge la persona: a
  una sola copriva il solo tronco e non si leggeva come sagoma. Il fattore e'
  di sola resa e non tocca le grandezze --- allungamento e inclinazione sono
  un rapporto e una direzione, invarianti per scala. La freccia resta a 1
  sigma, cioe' la sua semilunghezza **e'** `A1_asse_mag`: nella stessa figura
  si leggono la misura e l'ingombro. Dichiarato in didascalia e nella scheda.
- **Assi in pixel** su entrambi i pannelli, origine in alto a sinistra e $y$
  crescente verso il basso --- la convenzione in cui MediaPipe restituisce le
  coordinate. Senza, non si legge a che quota cada la retta del pavimento.
- Nuovo flag `--sfondo foto|bianco`: `foto` sovrappone lo scheletro alla
  persona (predefinito), `bianco` lo lascia su fondo chiaro. I file del
  secondo portano il suffisso `_bianco`.
- Il fotogramma si sceglie da solo fra i candidati di una ripresa in piedi,
  massimizzando visibilita' dei punti x verticalita' dell'ingombro.
- Tabella dei landmark in Cap3: aggiunta la colonna del numero di punti e
  sostituito «12 punti» con gli indici veri di B (11--16, 23--28), presi da
  `DIP_PROJECT/src/geometry.py:437` (`key_indices`).
- Aggiunto in Cap3 il rilievo che A3, per la sola stima del pavimento, usa
  l'ingombro di tutti e 33 i landmark e non i suoi nove.
- `sec:tracciatore` riscritta. Aggiunte `eq:tracciatore` (lo stimatore con
  stato) e `eq:azzeramento` ($s_0^{(r)} = \varnothing$). **Tolta del tutto la
  dichiarazione del difetto**: la sezione ora enuncia soltanto che cosa fa la
  pipeline, senza raccontare la versione precedente. Decisione della
  candidata, 2026-09-15.
- La `eq:tracciatore` e' ancorata a `\cite{blazepose}`, verificato alla fonte
  (arXiv:2006.10204, §2.1 «Inference pipeline»): «Our pipeline consists of a
  lightweight body pose detector followed by a pose tracker network. The
  tracker predicts keypoint coordinates, the presence of the person on the
  current frame, and the refined region of interest for the current frame.
  When the tracker indicates that there is no human present, we re-run the
  detector network on the next frame.» Era un bibitem orfano: ora e' citato.
- Aggiunto `\bibitem{samanta}` (Samanta e Chanda, arXiv:1608.00199, 2016) e
  citato in `sec:tracciatore` per la formulazione **generale**: la loro Eq. (1)
  cerca le posizioni delle parti al fotogramma $t$ minimizzando una funzione
  condizionata alle posizioni al fotogramma $t-1$, e la §II dice in chiaro che
  e' quel condizionamento a separare tracciamento e stima su immagine singola
  («If information from previous frame is not utilized, resultant algorithm
  can estimate human pose from a single image»). Verificato alla fonte, pp.
  1-2. Cosi' la sezione ha la formulazione generale e l'istanza usata.
  **Attenzione:** licenza `arXiv perpetual non-exclusive`, non Creative
  Commons --- le figure di quel lavoro non sono riutilizzabili senza permesso.
- Nuovo `pipeline/spostamento_landmark.py` e nuova `fig:spostamento` nella
  sezione «Assenza della posa e instabilita' delle coordinate», che finora
  affermava l'instabilita' senza misurarla. Per ogni landmark, distribuzione
  dello spostamento fra fotogrammi consecutivi su 20 riprese ADL e 20 di
  caduta, un soggetto alla volta su tutti e dieci (6.943 e 3.544 coppie per
  punto).
  **Prima versione sbagliata, e va detto perche'.** Misurando nel piano
  immagine le ADL uscivano piu' mosse delle cadute (naso 0,0080 contro 0,0051)
  e il terzo quartile valeva ~0,055 per tutti e 33 i punti, identico per il
  naso e per il mignolo: la misura era dominata dalla **traslazione** della
  persona --- camminare sposta tutti i punti allo stesso modo, e una caduta e'
  quasi tutta statica, quindi la mediana la facevano i fotogrammi fermi.
  Ora si sottrae lo spostamento del bacino e resta il moto rispetto al corpo.
  Risultato: punti impiegati (anche escluse) 0,0045 su ADL contro 0,0113 di
  polsi e dita, **2,5 volte**; sulle cadute 0,0067 contro 0,0177, 2,6 volte.
  Le anche sono il riferimento da cui si sottrae, quindi il loro 0,0014 non e'
  comparabile: dichiarato in didascalia e nella scheda.
  Flag `--da-json` per ridisegnare senza rimisurare (la misura costa ~11 min).
- Nuovo `pipeline/figura_momenti.py`: `fig_momenti_a1/a2/a3` (+ `_en`,
  `_bianco`), una per sezione di rappresentazione. La stessa costruzione in
  due istanti della stessa caduta --- in piedi e a terra --- scelti dal
  programma come ingombro piu' verticale e piu' orizzontale
  (`sub09_act04_trial01_cam01`, fotogrammi 17 e 53). Le due finestre hanno lo
  **stesso lato in pixel**: con riquadri diversi sembrerebbe che la persona
  cambi dimensione invece che orientamento.
  Valori misurati, citati nelle didascalie: `A1_allungamento` 4,31 -> 8,82,
  `A1_inclinazione` 90,1 -> -175,9 (che per la periodicita' di 180 gradi vale
  4,1: una rotazione di 86 gradi, ed e' l'esempio dello srotolamento gia'
  descritto in quella sezione), `A2_angolo_tronco` 8,96 -> -79,13,
  `A3_h_pavimento` 1,02 -> -0,12.
  `sec:pavimento` ora rimanda a `fig:momenti_a3` con quei due numeri: era una
  sezione senza figure.
  `figura_landmark.etichette` ricentrata: la passata greedy spingeva solo in
  giu' e su un corpo orizzontale la colonna sfondava il bordo.
- **Resa delle figure**, su richiesta della candidata (2026-09-15):
  - colori rifatti per stare sopra la fotografia e non sulla carta bianca. Il
    rosso mattone spariva sul giubbotto rosso del soggetto e il verde scuro sul
    pavimento: ora `BLU #1565c0`, `ROSSO #d81b60` (magenta), `VERDE #00897b`,
    `GRIGIO #90a4ae`. Luminosita' diverse fra loro, quindi restano
    distinguibili anche in scala di grigi;
  - **tolto il velo bianco** sopra le fotografie: l'immagine resta a colori
    pieni, a staccare le linee ci pensa l'alone bianco di `osso`;
  - linee piu' sottili (ossa 1,1 e 1,8 invece di 1,9 e 2,6), punti piu'
    piccoli, `interpolation='lanczos'`, **400 dpi** invece di 200;
  - **aggiunto il collo**: `POSE_CONNECTIONS` non ha alcun arco fra i punti
    del viso e le spalle, quindi la testa risultava staccata dal busto. La
    nuova `collo()` disegna il segmento naso -> punto medio delle spalle. E'
    l'unica linea che non venga da MediaPipe e il docstring lo dichiara; non
    introduce nulla di inventato, perche' quel punto medio e' lo stesso che A2
    e A3 usano come estremo superiore del tronco.
- **Figure in inglese.** `spostamento_landmark.py` ha ora `--lingua` come gli
  altri (nomi dei 33 punti secondo MediaPipe). `Cap3.tex` punta alle varianti
  `_en` delle sette figure prodotte da questi script. Restano in italiano
  `fig_rappresentazioni`, `fig_striscia`, `fig_rumore`, `fig_due_camere`,
  `fig_dtw` (Cap3) e le figure di Cap4-Cap5, prodotte da altri script.
- `fig:tracciatore` resta nel capitolo, nella variante inglese
  (`fig_tracciatore_en.png`, titoli «frame $i-1$» e «frame $i$»), col collo
  collegato e i colori nuovi.
- `Cap1.tex`: `\includegraphics{fig_popolazione.png}` non aveva il prefisso
  `figure/` ed era l'unico riferimento a un file inesistente in tutta la tesi.
- Nuovo `pipeline/figura_tracciatore.py` (non piu' usato nella tesi)
  (+ varianti `_en` e `_bianco`). Due fotogrammi consecutivi di una caduta,
  posa al fotogramma $i-1$ in trasparenza sopra quella al fotogramma $i$, una
  freccia per punto. La coppia non e' scelta a occhio: si elabora la ripresa
  con lo stimatore in modalita' tracciamento e si prende quella a spostamento
  medio massimo sui nove punti di A3. E' la controparte dei dati della
  Figura 1 di Samanta e Chanda, **rifatta e non ricopiata** per via della
  licenza. Le primitive di disegno sono importate da `figura_landmark.py`,
  cosi' le due figure non divergono nello stile.

**Verificato con:**
`python pipeline/figura_landmark.py` (env `fall_processing`) -> tre PNG,
fotogramma 405 di `sub09_act07_trial01_cam01`; pavimento
`y = 0,02828 x + 433,66` su **394 osservazioni** raccolte in 500 fotogrammi.
`--lingua en` -> stessa retta, stesse osservazioni: deterministico.
La scheda `.txt` riporta A1 7 punti / A2 5 / A3 9, coerenti con la tabella del
capitolo, e i valori calcolati sul fotogramma (`A1_asse_mag` 87,75,
`A1_allungamento` 4,77, `A2_angolo_tronco` 2,16, `A3_h_pavimento` 1,72).
Struttura di `Cap3.tex`: ambienti bilanciati, graffe +0, `$` pari, nessun
`\ref` senza `\label`. **Non compilato**: non c'e' un LaTeX su questa
macchina.

**Collegamenti:** ISS-138 (lo stimatore unico fuori dal ciclo)

---

## [2026-09-10] — `regole_allarme.py` sa leggere anche le run archiviate

**Tipo:** feature
**File:** `pipeline/regole_allarme.py` (`main`, nuovo `--punteggi`)

**Perche'.** Lo script cercava i punteggi per fold sempre in
`risultati/addestramento/`. Le run su `feature_v2.csv` --- quelle su cui poggia
il Capitolo 4 --- stanno in `risultati/addestramento/v2/`, messe da parte il
7 settembre prima del riaddestramento. Senza un modo di indicarle, il confronto
fra regole si poteva fare solo sulla versione piu' recente del dataset, e non
su quella che regge il testo.

**Cosa cambia.** `--punteggi <cartella>` sceglie da dove leggere. Il controllo
di allineamento gia' presente --- «disallineamento su Subject_xx: N contro M»
--- **rifiuta la combinazione sbagliata di CSV e punteggi** invece di produrre
numeri privi di senso, quindi l'opzione non apre la porta a un errore nuovo.

**Cosa NON cambia.** Il comportamento predefinito: senza l'opzione lo script
legge dove leggeva prima.

**Verificato con:**
`python pipeline/regole_allarme.py --csv feature_v2.csv --run foresta_tre_classi_DTW_cam1 --punteggi risultati/addestramento/v2`
-> ventuno regole confrontate su 49 cadute e 13 sessioni; `consecutive 5`
richiamo 0,90 e 10,8 allarmi/ora, `isteresi 0,80/0,45/3` richiamo 0,92 e 5,1.
Ripetuto con `--sospensione` 5, 10, 15, 30, 60.

**Collegamenti:** [EXP-043](EXPERIMENTS.md#exp-043), [EXP-029](EXPERIMENTS.md#exp-029)

---

## [2026-09-10] — Pulizia: 149 MB di copie e di riferimenti difettosi

**Tipo:** refactor + docs
**File:** `dataset/processed/features/` (5 CSV, rimossi dalla candidata),
`_ripiego_20260908/feature_v3.csv`, `_ripiego_20260908/LEGGIMI.md`,
`board.npz`, `pc.npz`, `pc09.npz`

**Il criterio.** La mail al relatore del 7 settembre e la sua risposta dell'8
sono la versione considerata corretta: **tutto cio' che regge quei numeri
resta**. I numeri delle architetture della mail --- LSTM 0,858, GRU 0,847 ---
vengono da [EXP-018](EXPERIMENTS.md#exp-018), che dichiara `feature_v2.csv`:
quel file e `feature_v2_omnifall.csv` sono quindi intoccabili, insieme a
`feature_v3`, `feature_urfall` e a tutto il lavoro nuovo (v3_omnifall, v4, v5,
v5_omnifall).

**Cosa e' stato tolto.**

| | MB | perche' |
|---|---:|---|
| `feature_v1_A2_degenere.csv` | 75,7 | citato due volte, ed entrambe dicono che fu rinominato «degenere» perche' A2 lo era |
| `feature_prova.csv` | 15,4 | prova su due soggetti del 19 agosto |
| `feature_pav.csv` | 1,8 | zero riferimenti |
| `feature_nuovi.csv` | 1,5 | citato una volta, e ISSUES dice che quelle colonne non furono mai unite |
| `feature_prova_oggi.csv` | 0,7 | zero riferimenti |
| `_ripiego_20260908/feature_v3.csv` | 75,7 | **duplicato bit per bit** del file vivo, md5 `a0158c4bc13c...` |
| `board.npz` `pc.npz` `pc09.npz` | 0,08 | difettosi, [ISS-164](ISSUES.md#iss-164) |

**Il LEGGIMI del ripiego e' stato corretto**, perche' diceva il falso: *«questa
e' l'unica copia»* riferito al CSV, e dava un comando di ripristino che ora non
funziona e che non serviva gia' allora. Nello stesso file e' stato scritto che
i `.npz` dei punteggi per fold, invece, **non sono duplicati** --- differiscono
dai vivi, che il riaddestramento v3/v4/v5 ha sovrascritto --- e vista
[ISS-159](ISSUES.md#iss-159) possono essere l'ultima traccia delle run di
EXP-023. Non si cancellano.

**Cosa NON e' stato tolto, e perche'.** `risultati/sessioni/2026081[0-3]` e'
un duplicato verificato (60 file, 60 md5 identici, 0 assenti), ma cancellarlo
farebbe passare `eventi_sessioni.py` da **13 sessioni a 1** senza sollevare
nulla: [ISS-165](ISSUES.md#iss-165). Va prima corretta la risoluzione della
cartella.

**Verificato con:** `md5sum` fra le due copie di `feature_v3.csv` -> identiche
prima della rimozione, e la copia viva presente dopo; confronto md5 ricorsivo
delle quattro cartelle di agosto -> 60/60 identici;
`grep -rn 'board\.npz|pc\.npz|pc09\.npz' --include=*.py` -> solo righe di
docstring in `parita_frame.py`, **nessun caricamento a runtime**;
`elenco_punteggi(SESSIONI)` -> 13 sessioni, invariato.

**Collegamenti:** [ISS-164](ISSUES.md#iss-164), [ISS-165](ISSUES.md#iss-165),
[ISS-159](ISSUES.md#iss-159), [EXP-018](EXPERIMENTS.md#exp-018)

---

## [2026-09-10] — Il `.gitignore` non difende piu' per elenco, ma per estensione

**Tipo:** fix
**File:** `.gitignore`

**Perche'.** `deploy_board/riletture/`, creata la notte fra il 9 e il 10
settembre, conteneva **2.842 fotogrammi annotati** di persone identificabili
che **nessuna regola copriva**: `git status` li proponeva tutti
([ISS-163](ISSUES.md#iss-163)).

Il difetto e' lo stesso del 9 settembre, a ventiquattro ore di distanza. Quel
giorno erano state aggiunte due righe --- `deploy_board/resa_clip*/` e
`deploy_board/sessioni/**/clip/` --- perche' le cartelle dei fotogrammi
annotati non si chiamano `clip`. **Difendere per elenco di cartelle e' una
difesa che invecchia**: copre quelle che esistono il giorno in cui la si
scrive, e ogni cartella nuova ricomincia da zero.

**Cosa cambia.** La difesa e' ora `*.jpg` e `*.jpeg`, che non dipende da come
si chiama la cartella ne' da chi si ricorda di aggiornare l'elenco. Le righe
per cartella restano: non fanno danno, e dicono dove stanno le clip note.

**L'invariante che lo rende sicuro e' stato verificato, non supposto:** in
questo repository **non esiste un solo JPEG che sia un risultato**. I
fotogrammi di telecamera sono sempre JPEG, le figure e le curve DTW sempre
PNG, e i PNG restano tracciati.

**Verificato con:**

```
git ls-files | grep -ci 'jpe\?g$'                              -> 0   (prima)
git ls-files --others --exclude-standard | grep -ci 'jpe\?g$'  -> 2842 (prima)
                                                                -> 0    (dopo)
git ls-files --others --exclude-standard deploy_board/riletture/ | wc -l
                                                                -> 47  (CSV + LEGGIMI, invariati)
git ls-files --others --exclude-standard | grep -ci '.png$'     -> 47  (invariati)
```

**Collegamenti:** [ISS-163](ISSUES.md#iss-163), [ISS-161](ISSUES.md#iss-161),
[ISS-142](ISSUES.md#iss-142)

---

## [2026-09-09] — La sessione di campo in una figura, e la tavolozza verificata

**Tipo:** feature
**File:** `pipeline/figura_sessione_v5.py` (nuovo), `tesi/figure/fig_sessione_v5.png`

**Perche'.** Il registro della sessione v5 ha 624 righe e la verita' di
riferimento sta in un LEGGIMI: separati non rispondono alla domanda che il
Capitolo 5 pone e non mostra mai, cioe' **quando il classificatore vede una
caduta e quando invece e' la REGOLA a perderla**.

**Cosa cambia.** Una figura con due riquadri: la sequenza dei punteggi con le
quattro cadute dichiarate sui fotogrammi, e sotto la lettura riga per riga.
Si legge a colpo d'occhio che la caduta 2 supera la soglia quanto la 1 e non
produce allarme, e che il picco a 881 s non e' una caduta ma un divano.

**Due scelte di impaginazione, e la ragione.**

1. **L'asse parte da 690 s, non da 0.** Il primo tentativo disegnava 0-900 e
   sprecava il **77% della tela** sulla zona in cui il sistema non decide,
   schiacciando tutto cio' che conta nell'ultimo quinto. Quel fatto e' un
   **numero**, non una forma: sta in una riga di testo sotto la figura.
2. **Nessuna identita' e' affidata al solo colore.** Ogni banda porta il suo
   numero, ogni esito la sua parola. Le tinte sono quelle di `figure_tesi.py`,
   importate e non ricopiate.

**La tavolozza del progetto e' stata verificata**, non giudicata a occhio:
conversione in OKLab e simulazione delle tre dicromazie (matrici di Machado
2009). Separazione peggiore fra le tinte usate **10,0** su 100 --- l'obiettivo
e' 8 --- e minimo a vista normale **19,4** contro una soglia di 15. `SABBIA` ha
contrasto **2,36:1** su bianco, quindi e' usata **solo** come fondo di banda con
etichetta scritta, mai per tratti sottili o testo.

**Verificato con:** `python pipeline/figura_sessione_v5.py` -> 624 finestre,
36 sopra soglia, picco 0,960, 4 cadute di cui 2 con allarme. Figura **aperta e
guardata**: tre collisioni di etichette corrette in due passate. **Non
compilata in LaTeX**: su questa macchina non c'e' un compilatore.

**Collegamenti:** [EXP-039](EXPERIMENTS.md#exp-039), [ISS-162](ISSUES.md#iss-162),
[ISS-156](ISSUES.md#iss-156)

---

## [2026-09-09] — Il pacchetto v5 sulla board, e la verifica che confrontava mele con pere

**Tipo:** fix + feature
**File:** `deploy_board/rileva.py` (`verifica_parita_fotogrammi`), `deploy_board/metadata.json`,
`deploy_board/modello.pkl`, `deploy_board/scaler.pkl`, `deploy_board/parita.npz`

**Perche'.** Installando sulla board la selezione v5/DTWH, la verifica di
avvio ha dichiarato `A3_escursione` divergente al **5807%**. Non era una
divergenza: era `A3_escursione` confrontata con `A3_ginocchia_rel_y`
([ISS-161](ISSUES.md#iss-161)).

**Cosa cambia.**

1. **Il pacchetto installato e' v5/DTWH**, esportato da
   `feature_v5_omnifall.csv` (12.357 finestre, 595 positive, 50 alberi, 7.322
   nodi). Rispetto a quello delle 10:18 cambiano due grandezze su tredici:
   `A2_angolo_tronco` -> `A2_testa_rel_y`, `A3_ginocchia_rel_y` ->
   `A3_caviglie_rel_y`. **Il motore non cambia**: impronta `e4c0d354...`
   identica, quindi ogni differenza viene dal modello e dalle due colonne.
   Copie di sicurezza in `deploy_board/pacchetto_installato_20260909_1018/` e,
   sulla board, `~/rileva_pacchetto_20260909_1018/`.

2. **La parita' per fotogramma allinea per nome.** `parita_frame.py` scriveva
   gia' i nomi delle colonne dentro l'npz e nessuno li leggeva. Ora le comuni
   si riordinano, quelle assenti dal riferimento si dichiarano e non si
   confrontano, e sotto le due comuni la verifica si dichiara **non eseguita**
   invece di «superata». La stampa da' lo scarto **per ciascuna grandezza**.

3. **Misurata la divergenza vera fra PC e board, ed e' lo stimatore di posa.**
   I landmark differiscono nel **99,98% delle coordinate** (media 1,21e-03,
   massimo 8,19e-02) fra MediaPipe 0.10.9 su x86 e la stessa versione su
   aarch64. Lo scarto sulle grandezze si ordina di conseguenza: statiche
   0,000%, integrali 0,4-0,6%, derivate 2,4-3,7%.

**Verificato con:** `rileva.py --parita` sulla board 192.168.1.20, sei
esecuzioni. Prima del correttivo: 5807,4% col pacchetto v5, 3,7% con quello
10:18, entrambi ripetibili. Dopo: **3,70% su `A3_hip_vel` con entrambi**, e la
parita' sulle **finestre** sempre a `0.000e+00` --- modello e scaler si
trasferiscono esatti nonostante scikit-learn 1.6.0 -> 1.9.0.

**Collegamenti:** [ISS-161](ISSUES.md#iss-161), [ISS-153](ISSUES.md#iss-153),
[ISS-106](ISSUES.md#iss-106), [ISS-159](ISSUES.md#iss-159)

---

## [2026-09-09] — Le citazioni perse nell'incorporazione delle stesure di Cap1 e Cap2

**Tipo:** fix
**File:** `tesi/Cap1.tex:63`, `tesi/Cap1.tex:93`, `tesi/Cap2.tex:53`,
`tesi/Cap2.tex:255`, `tesi/Bibliografia.tex:127`

**Perche'.** L'installazione delle stesure della candidata come Capitolo 1 e
Capitolo 2 ha portato con se' cinque difetti di citazione. Tre li segnalava
`controlla.py`, due no: **una voce mai citata non e' un errore per LaTeX**, e
con `thebibliography` scritto a mano viene stampata lo stesso. Sono quindi
sparite in silenzio.

**Cosa cambia.**

1. **`\cite{gazem}` tolto da Cap2.** Era una delle tre voci **ritirate il 26
   agosto perche' inventate** ([ISS-114](ISSUES.md#iss-114)), ed e' rientrata
   con la stesura. La frase sulla compliance dell'utente regge da sola, come
   gia' nella versione precedente del capitolo. E' il secondo episodio
   documentato del ritorno indietro che [ISS-110](ISSUES.md#iss-110) descrive.

2. **`fnopi` ed `epicentro` aggiunte a `Bibliografia.tex`**, verificate sulla
   fonte e non a memoria, con il commento `% VERIFICATO 2026-09-09` e l'URL:
   - `fnopi` -> comunicato FNOPI del 1 settembre 2026. Confermati gli 80mila
     pensionamenti fra il 2026 e il 2035, gli 1,1 milioni di caregiver
     informali e il rapporto infermieri/abitanti sotto la media UE di 8,5.
   - `epicentro` -> dossier PASSI d'Argento «Cadute tra gli anziani», sezione
     *Impatto per la salute*. La frattura del femore e' il 46,5% dei ricoveri
     maschili e il 55,3% di quelli femminili sulle SDO 2010 per incidente
     domestico: «circa la meta' dei casi» e' corretto perche' il valore unico
     non esiste, sono due popolazioni. Fonte **diversa** da `passi`, che e' il
     comunicato del 31 ottobre 2025 sul biennio 2023-2024.

3. **`fleming` rimessa in Cap1**, con i valori della fonte al posto di
   un'affermazione generica: l'82% delle cadute avviene mentre la persona e'
   sola, il 30% di chi cade resta a terra un'ora o piu'. Era l'unico
   riferimento clinico del *long lie* e la stesura l'aveva persa.

4. **`mediapipe` e `blazepose` rimesse in Cap1:93**, dove il testo dice con
   quale stimatore di posa si lavora e non lo attribuiva a nessuno.

5. **`gomes` rimessa in Cap2**, sull'affermazione che sosteneva anche prima:
   la mappatura sistematica dei 433 studi primari dedica una parte specifica a
   fotogrammi al secondo, latenza e piattaforma hardware.

**Verificato con:** `python tesi/controlla.py` -> da «PROBLEMI: 3»
(`epicentro`, `fnopi`, `gazem` non definite) a «Nessun problema»; voci mai
citate da sei a due. Le due che restano, `noury` e `rougier`, sono quelle gia'
dichiarate in testa a `Cap2.tex` come da sistemare, e sono precedenti a questo
intervento. **Non compilato**: su questa macchina non c'e' LaTeX.

**Collegamenti:** [ISS-110](ISSUES.md#iss-110), [ISS-114](ISSUES.md#iss-114)

---

## [2026-09-09] — La finestra degli integrali diventa una durata, e il pacchetto porta con se' il motore

**Tipo:** fix + feature
**File:** `src/geometry.py`, `config.py`, `deploy_board/rileva.py`,
`pipeline/esporta_board.py`, `pipeline/audit_board.py`,
`pipeline/mappa_omnifall.py`, `src/dati.py`, `deploy_board/parita_frame.py`,
`prove/prova_geometria.py`

**Perche'.** Due pratiche osservate in un prototipo pubblico di architettura
quasi identica --- MediaPipe, feature geometriche, foresta, voto temporale ---
che rispondono a tre difetti aperti di questo lavoro: le sue grandezze sono
**indipendenti dal frame rate**, e il suo pacchetto porta lo **schema delle
feature insieme al modello**. Qui il conteggio fisso di fotogrammi era
[ISS-148](ISSUES.md#iss-148) e la copia del motore tenuta a mano era
[ISS-139](ISSUES.md#iss-139).

### 1. La finestra degli integrali e' una durata

`K_INTEGRALI = 31` e' un conteggio, e trentuno fotogrammi durano 1,72 s a 18
fps ma **4,27 s alla cadenza di 7,26 fps misurata sulla board**. Nove delle
tredici colonne installate sono integrali: tre quarti del vettore di ingresso
avevano un significato fisico diverso fra addestramento ed esercizio.

Il buffer conserva ora **secondi**, non campioni, con scarto per anzianita'.
Ogni campione porta il proprio `dt`, quindi la finestra e' corretta anche
quando la cadenza salta *dentro* la stessa ripresa --- che e' il caso reale:
mediana 49,6 ms, novantanovesimo percentile 159,8 ms ([ISS-149](ISSUES.md#iss-149)).

**A 18 fps il motore produce valori identici bit per bit.** Misurato sul
motore precedente e su quello nuovo, stessa sequenza, tutte e 33 le grandezze:
scarto **0,000e+00**. `feature_v3.csv` e ogni numero della tesi che ne discende
non si muovono. A 9 e a 7,26 fps cambiano soltanto le nove integrali, ed e' la
correzione.

Il costruttore accetta ora `durata_integrali` in secondi; `k_integrali` resta
accettato e viene convertito dividendo per 18 fps, quindi i chiamanti gia'
scritti non cambiano comportamento.

**Il file d'oro delle prove e' stato rigenerato, e la ragione e' questa.** La
sua sequenza gira a **9 fps**: 105 valori su 1.320 --- il 7,95%, tutti in
sette colonne integrali --- cambiano perche' a quella cadenza la finestra e'
di 15 campioni invece di 31. Sono aggiunte due prove che il file d'oro non
puo' dare, perche' gira a una cadenza sola: che il buffer copra la durata
dichiarata a 18, 9 e 7,26 fps, e che il costruttore accetti i secondi.

### 2. Sulla board la cadenza si misura invece di assumerla

`rileva.py` passava `fps_assunti = 9,0` a `fotogramma()` mentre la board ne
faceva 7,26: le derivate uscivano **sopravvalutate del 24%**. Ora c'e' la
classe `Cadenza`, mediana degli intervalli su finestra mobile di trenta, con
gli intervalli oltre i cinque secondi scartati --- sono le riaperture della
telecamera e i risvegli, non cadenza. Su cartella di fotogrammi resta il
valore dichiarato: li' l'intervallo fra due letture e' la velocita' di
elaborazione, non la cadenza di ripresa.

Il riepilogo dichiara ora `fps_dichiarato` e `fps_usato_ultimo` accanto.

### 3. Il pacchetto porta il motore e lo schema

`esporta_board.py` **copia** `src/geometry.py` nel pacchetto invece di
lasciarlo allineare a mano, e scrive nel metadato `schema_feature`: l'elenco
ordinato delle 33 grandezze che quel motore calcola, con gli indici delle
tredici installate. `rileva.py` lo confronta all'avvio e dice **quale**
grandezza manca --- l'impronta sha256 dice solo *che* due file differiscono, e
un commento riscritto la fa fallire come una grandezza mancante.

Una colonna che il modello chiede e il motore non calcola e' ora **bloccante**:
sarebbe un `KeyError` al primo fotogramma.

### 4. `colonne_di` esce da `addestra.py`

Viveva accanto a un `import tensorflow`, quindi chi esporta non poteva
chiamarla e avrebbe dovuto riscriverla --- il difetto che questo progetto ha
gia' commesso tre volte. E' in `src/dati.py`, e addestramento ed esportazione
chiamano la stessa.

### 5. Cio' che e' saltato fuori strada facendo

- **il riferimento di parita' per fotogramma era su una clip senza pose**
  ([ISS-153](ISSUES.md#iss-153)): 60 fotogrammi, 0 con posa, cioe' un
  riferimento di soli zeri che sarebbe passato comunque. E il metadato ne
  nominava una che in `clip_demo/` non c'e' piu';
- **il modello installato e quello misurato non hanno lo stesso positivo**
  ([ISS-154](ISSUES.md#iss-154)): il pacchetto si addestra sulle classi
  OmniFall, l'F2 della tesi si misura sulle etichette manuali.

**Verificato con:**
`python prove/esegui.py` -> **33 su 33** (erano 31, piu' le due nuove);
confronto fra motore vecchio e nuovo sulla stessa sequenza -> **0,000e+00 a 18
fps**, sette colonne integrali diverse a 9 e 7,26;
`python pipeline/audit_board.py` -> **«Nessuna differenza»** (erano 2, ed erano
`A3_h_pavimento` mancante e le impronte divergenti);
`rileva.py --video clip_demo/evt_0068_142026` con l'ambiente della board
(mediapipe 0.10.9) -> quattro verifiche verdi: impronta, **schema 33
grandezze**, finestre `0,000e+00`, **fotogrammi 60 confrontati scarto 0,00%**;
171 fotogrammi elaborati, 100% di pose, 0 allarmi.

**Verificato SULLA BOARD** lo stesso giorno, dopo che il dispositivo e' stato
acceso ([EXP-035](EXPERIMENTS.md#exp-035)): quattro verifiche eseguite,
impronta e schema coincidono, parita' sulle finestre `0,000e+00` **fra
scikit-learn 1.6 e 1.9**, parita' per fotogramma eseguita per la prima volta
dal 22 agosto e divergente al 3,7% per una ragione ora isolata --- l'OpenCV
della board e' 5.0.0 contro 4.13.0 del calcolatore, e i **landmark grezzi**
divergono mentre il motore geometrico e' lo stesso file.

Nella prima sessione la cadenza misurata e' **6,469** contro i 9,0 dichiarati:
le derivate erano sopravvalutate del **39%** e il buffer copriva **4,79 s**
invece di 1,72. E' il difetto misurato mentre viene corretto.

**Non verificato:** il **recall a bordo**. Nessuna caduta e' stata messa in
scena: quella sessione e' una prova di installazione, non di rilevamento.

**Collegamenti:** [ISS-148](ISSUES.md#iss-148), [ISS-149](ISSUES.md#iss-149),
[ISS-150](ISSUES.md#iss-150), [ISS-139](ISSUES.md#iss-139),
[ISS-153](ISSUES.md#iss-153), [ISS-154](ISSUES.md#iss-154),
[EXP-034](EXPERIMENTS.md#exp-034)

---

## [2026-09-08] — Un controllo di coerenza che si esegue, e le sessioni rimpatriate

**Tipo:** feature + fix
**File:** `pipeline/coerenza.py` (nuovo), `pipeline/audit_board.py` (nuovo),
`risultati/sessioni/2026081*/`

**Perche'.** Ogni difetto serio di questo lavoro ha avuto la stessa forma: la
stessa cosa calcolata in due posti che dovevano essere d'accordo e non lo
erano. Finestratura (ISS-147), durata degli integrali (ISS-148), fps del
dataset (ISS-149), allineamento OmniFall (ISS-150), colonne installate
(ISS-139), capitoli in tre copie (ISS-110). Nessuno produceva un errore:
producevano numeri plausibili. **Un controllo che si esegue e' meglio di una
rilettura che si ricorda.**

**Cosa fa `coerenza.py`.** Cinque confronti, e stampa solo cio' che non
coincide: le funzioni scritte due volte (`riassumi`, `normalizza`), la forma
delle tracce di sessione, i risultati che dipendono da cartelle fuori dal
repository, le costanti ridefinite fuori da `config.py`, e la board contro il
progetto (via `audit_board.py`).

**Che cosa ha trovato, alla prima esecuzione: quattro incoerenze.**

- **dodici sessioni su tredici senza traccia per fotogramma.** Non erano
  perse: i `feature.csv` stavano in `DIP_PROJECT/sessioni_reali/`, e in
  `DIP_Project_1` era stato copiato tutto tranne quello. **Rimpatriate tutte
  e dodici**, 40 MB, 22 colonne ciascuna. Nessuna immagine copiata: le clip
  restano dove sono;
- **le tracce hanno due forme diverse**: 22 colonne quelle di agosto, 34
  quella del 6 settembre. Agosto salva le grandezze grezze
  (`hip_x`, `hip_y`, riquadro) da cui si ricava `h_pavimento`; settembre salva
  le 32 gia' calcolate, che `h_pavimento` non contengono. **Ciascuna delle due
  permette di valutare configurazioni che l'altra non permette**, ed e' la
  ragione tecnica di [ISS-139](ISSUES.md#iss-139): il Capitolo 5 valuta la
  famiglia A3 perche' e' l'unica che le sessioni di agosto consentivano di
  ricalcolare, non per una scelta metodologica;
- **sette punti leggono da `../DIP_PROJECT`**, fra cui `eventi_sessioni.py`,
  che produce i numeri di campo del Capitolo 5;
- **la board non esegue cio' che il progetto dichiara**: manca
  `A3_h_pavimento` nel suo `geometry.py`, e ha `A2_testa_rel_y` dove la
  selezione odierna sceglie `A2_angolo_tronco`.

**Un falso positivo, dichiarato.** Il controllo segnala `normalizza` come
divergente fra `rileva.py` e `mostra.py`: la differenza e' **il nome di una
variabile** (`forma` contro `f`). Il confronto e' sul sorgente normalizzato e
non sul comportamento, e va letto sapendolo.

**Verificato con:** `python pipeline/coerenza.py` -> 4 incoerenze prima del
rimpatrio, 3 dopo; `python pipeline/audit_board.py` -> 2 differenze;
`python tesi/controlla.py` -> «Nessun problema»; `python prove/esegui.py` ->
31 su 31.

**Collegamenti:** [ISS-139](ISSUES.md#iss-139), [ISS-147](ISSUES.md#iss-147),
[ISS-148](ISSUES.md#iss-148), [ISS-149](ISSUES.md#iss-149)

---

## [2026-09-08] — L'etichetta del confine, la latenza attribuita, e cosa vede la board

**Tipo:** feature + docs
**File:** `src/etichettatura.py`, `config.py`, `tesi/Cap3.tex`, `tesi/Cap5.tex`

**Perche'.** Confronto con un prototipo pubblico di architettura quasi
identica --- MediaPipe, feature geometriche, foresta, voto temporale --- che
adotta due pratiche assenti qui: escludere i fotogrammi ambigui invece di
indovinarli, e dichiarare lo scarto fra le finestre di addestramento e quelle
di esercizio.

**Cosa cambia.**

- **`etichetta_finestra` sa escludere le finestre di confine.** Una finestra
  che contiene l'evento sotto la soglia $K$-su-$M$ valeva 0, cioe' un negativo
  pulito, ed era un'ipotesi sul confine che cadeva sulla classe che deve
  restare pulita. Ora c'e' `escludi_incerte`, con predefinito in
  `config.ESCLUDI_FINESTRE_INCERTE`. **Sta spento**, e la ragione e' misurata:
  tocca **39 finestre su 25.130, lo 0,16%**, nessuna positiva
  ([EXP-031](EXPERIMENTS.md#exp-031)). Accenderlo richiederebbe di riaddestrare
  tutto per spostare una quantita' che non si misura; lasciarlo acceso senza
  riaddestrare renderebbe il codice non riproducibile dai numeri stampati;
- **Capitolo 3** dichiara la regola, l'alternativa e il conteggio, nella
  sezione sull'assegnazione dell'etichetta di finestra;
- **Capitolo 5**, nuova `tab:latenza_sensibilita` e il paragrafo *Da dove
  vengono i due secondi*: la persistenza cinque costa 0,997 s, la finestra
  lunga 1,243 s, il dispositivo 0,113 s. **Nessuna delle tre riguarda
  l'hardware**, ed e' la risposta alla domanda ovvia sul perche' 2,44 s.

**Il difetto trovato strada facendo, ed e' il piu' grave:**
[ISS-147](ISSUES.md#iss-147). In addestramento nessuna finestra contiene
fotogrammi senza posa, perche' `_tratti_continui` spezza sui buchi. Sulla board
`buf.append` e' incondizionato e `fotogramma(None, ...)` restituisce zeri:
**il 75,4% delle finestre di decisione contiene righe di zeri** e il 77,3% e'
deciso con gli integrali non riscaldati, contro un contratto scritto nella
docstring di `rileva.py` che promette il contrario.

**Verificato con:** `python prove/esegui.py` -> 31 su 31 con l'opzione spenta;
conteggio delle due popolazioni di finestre -> [EXP-031](EXPERIMENTS.md#exp-031);
`python tesi/controlla.py` -> «Nessun problema».

**Non verificato:** l'effetto sulle metriche di accendere l'esclusione. Non e'
stato riaddestrato nulla, ed e' dichiarato in tesi.

**Collegamenti:** [ISS-147](ISSUES.md#iss-147),
[EXP-031](EXPERIMENTS.md#exp-031)

---

## [2026-09-08] — Il Capitolo 5 ristrutturato, e due numeri che il 6 settembre aveva superato

**Tipo:** fix + docs
**File:** `tesi/Cap5.tex`, `tesi/Conclusioni.tex:33`, `pipeline/latenza.py:66`,
`docs/INDICE_E_STRUTTURA.txt`

**Perché.** La revisione della gerarchia dell'8 settembre si era fermata prima
del Capitolo 5, e la sua verifica --- «nessuna sezione sopra le mille parole
senza sottosezioni» --- **su quel capitolo non valeva**. Misurando le parole di
ogni titolo fino al successivo di pari livello:

| | parole | sottosezioni | difetto |
|---|---:|---:|---|
| 5.3 | 1.235 | 2 | 474 parole di `\paragraph` **prima** della prima sottosezione |
| 5.4 | 2.509 | 2 | tre argomenti diversi sotto un titolo solo |
| 5.5 | 1.312 | 0 | la sezione più lunga del capitolo senza una divisione |
| 5.7 | 1.378 | 4 | una sottosezione da 138 parole accanto a una da 542 |

Il capitolo aveva **66 titoli per 10.464 parole, cioè uno ogni 158**, contro la
regola dichiarata di uno ogni ~400.

**Cosa cambia nella struttura.**

Il difetto ricorrente è **il testo appeso**: blocchi lunghi fra il titolo di
una sezione e la sua prima sottosezione, che in indice non compaiono da nessuna
parte perché non sono né la sezione né una sua parte dichiarata.

- **la 5.4 aveva 764 parole appese** --- il costo per fotogramma, che è una
  delle tre misure della sezione e non aveva un titolo mentre le altre due ce
  l'avevano. Ora ha tre sottosezioni pari: costo, latenza, comportamento
  termico. **Resta una sezione sola.** Un primo tentativo l'aveva divisa in tre
  sezioni ed era sbagliato: le tre misure rispondono alla stessa domanda ---
  che cosa costa tenere acceso questo sistema --- e sono una caratterizzazione,
  non tre;
- **la 5.3 aveva lo stesso difetto con 474 parole**: sono la sottosezione
  `La strada dell'acceleratore neurale`, e `Confronto a parità di protocollo`
  vi rientra come `\paragraph`, perché era il suo esito e non un pari grado;
- **la 5.5 riceve due sottosezioni**, motivazione e protocollo, che sono le due
  metà che il suo stesso capoverso di apertura annuncia;
- **la 5.7 scende da quattro sottosezioni a tre:** quella da 138 parole rientra
  nell'apertura come `\paragraph{Il rovesciamento che è stato ritirato}`;
- **venti `\paragraph` su quarantasei tolti.** Otto erano titoli per meno di
  centoventi parole, cioè un'intestazione ogni due frasi: quelli che nominano
  un caveat o una precisazione sono ora una frase in corsivo nel testo, che è
  la forma di un inciso. Sei erano elenchi travestiti da titoli --- i tre
  ostacoli del porting, i tre modi di fallire --- e sono `itemize`. **Due
  raccontavano una seconda volta** la sospensione del dispositivo e il crollo
  del frame rate col numero di persone, già narrati per esteso nella sezione
  sull'esercizio prolungato: la 5.9 annunciava «tre risultati» e ne elencava
  cinque.

Esito: **da 9 sezioni + 11 sottosezioni + 46 `\paragraph` a 9 + 13 + 26** ---
un titolo ogni 216 parole invece che ogni 158 --- e circa duecento parole di
ripetizione in meno.

**Cosa cambia nei numeri** --- [ISS-146](ISSUES.md#iss-146),
[EXP-030](EXPERIMENTS.md#exp-030):

- `latenza.py` portava `CALCOLO_MS = 37.7`, ritirato da
  [ISS-137](ISSUES.md#iss-137) il 6 settembre. L'addendo si ricava ora da
  1/fps della sessione: **0,125 s invece di 0,038**, totale 3,865 s invece di
  3,778, e il rapporto fra finestra e calcolo scende da **73× a 22×**. La
  conclusione --- la latenza è dominata dalla finestra --- regge;
- il capitolo riaffermava in due punti il **5,8%** del classificatore sul costo
  per fotogramma, dopo averlo dichiarato ritirato e sostituito da **14,3%**
  quattro paragrafi prima. Corretti entrambi;
- **le Conclusioni portavano il bilancio ritirato per intero** --- 26,5 fps,
  88,4%, 5,8%, «un ventesimo del problema» --- dentro uno dei cinque contributi
  elencati. Sono 7,3 fps, 85,2%, 14,3% e un settimo, con il valore vecchio
  dichiarato accanto al nuovo;
- `latenza.py` stampava ancora `LIMITE INFERIORE`, che
  [ISS-145](ISSUES.md#iss-145) aveva sostituito nel testo il 7 settembre ma non
  nello script: ora stampa `CASO CONSERVATIVO`.

**Verificato con:** `python pipeline/latenza.py` -> 0,125 s, totale 3,865 s,
3,2%; `python tesi/controlla.py` -> «Nessun problema. Restano 0 figure da
produrre»; `python tesi/indice.py` -> 9 sezioni, 13 sottosezioni, nessuna
sezione con una sottosezione sola e nessun blocco appeso, 131 titoli fuori
indice; `python prove/esegui.py` -> 31 su 31.

**Non verificato:** il PDF. Su questa macchina non c'è un compilatore LaTeX, e
il controllo è statico.

**Collegamenti:** [ISS-146](ISSUES.md#iss-146),
[ISS-137](ISSUES.md#iss-137), [ISS-145](ISSUES.md#iss-145),
[EXP-030](EXPERIMENTS.md#exp-030)

---

## [2026-09-08] — La gerarchia dei titoli, resa coerente

**Tipo:** docs
**File:** `tesi/Cap1.tex`, `Cap2.tex`, `Cap4.tex`, `Cap5.tex`,
`docs/INDICE_E_STRUTTURA.txt`

**Perché:** l'indice non sembrava quello di una tesi sperimentale, e la ragione
era misurabile. Contando le parole di ogni titolo fino al successivo di pari
livello: **4.5 valeva 2.340 parole senza una sola sottosezione**, mentre 4.3 e
4.6, della stessa taglia, ne avevano due e tre; **2.4 valeva 1.235 parole senza
sottosezioni** ed era l'unica sezione del Capitolo 2 a superare le mille;
**5.3 aveva una sottosezione sola**, che è il caso peggiore perché una
sottosezione unica non divide niente.

**Cosa cambia:**

- **undici `\paragraph` promossi a `\subsection`**: quattro in 2.4 (cadute
  simulate, archivi pubblici, attività negative, livelli di generalizzazione —
  erano sottosezioni fino all'appiattimento del 25 agosto), due in 4.5, tre in
  4.7 che sono tre esperimenti distinti, uno in 5.3;
- **«Definizione dell'evento da riconoscere» promossa da 1.3.4 a sezione 1.4.**
  Non è una criticità del trasferimento come le altre tre: è la scelta
  metodologica su che cosa il sistema debba riconoscere. È la modifica
  strutturale che proponeva `Cap1_riordinato.tex` del 5 settembre, e l'unica di
  quella proposta portata nel testo;
- **i titoli promossi sono stati riscritti nel registro della sezione.** Un
  `\paragraph` porta una frase perché vive nel flusso del testo; un titolo di
  indice è un sintagma nominale. «Le cadute simulate sono un vincolo, non una
  scorciatoia» è diventato «Cadute simulate e cadute reali»;
- corretto un refuso nel titolo di 5.4.1, `e'` invece di `è`, che finiva
  nell'indice;
- `INDICE_E_STRUTTURA.txt` riporta la struttura nuova e la ragione della
  modifica.

**Il difetto che questa verifica ha fatto emergere, ed è più grave:** i capitoli
su cui la candidata sta lavorando **non sono quelli del repository**. Il
Capitolo 1 che ha in mano non coincide né con `Cap1.tex` né con
`Cap1_riordinato.tex`, e il suo Capitolo 2 non esiste qui: non contiene neppure
le parole «Dispositivi indossabili» o «Livelli di generalizzazione». È
[ISS-110](ISSUES.md#iss-110), aperta dal 26 agosto, e la scelta presa oggi è
che **la copia buona è il repository**.

**Verificato con:** `python tesi/indice.py` -> nessuna sezione sopra le mille
parole senza sottosezioni, nessuna sezione con una sottosezione sola;
`python tesi/controlla.py` -> «Nessun problema»; `python prove/esegui.py` ->
31 su 31.

**Collegamenti:** [ISS-110](ISSUES.md#iss-110)

---

## [2026-09-08] — L'indice si ricava dai sorgenti, e i titoli che non ci sono

**Tipo:** feature + docs
**File:** `tesi/indice.py` (nuovo), `docs/INDICE_E_STRUTTURA.txt`

**Perché:** l'indice con i numeri di pagina lo produce LaTeX, e su questa
macchina non c'è un compilatore: quello in mano è sempre la fotografia
dell'ultima compilazione su Overleaf. Confrontandolo con i sorgenti è emerso
che è **di due ristrutturazioni fa** — Cap1 ha una sottosezione in meno e una
sezione assorbita, Cap2 ne ha tre tolte e una declassata, in Cap3 due sezioni
sono fuse, in Cap4 tutto scala di uno dopo la fusione di 4.3 e 4.4, e in Cap5
**la latenza si è spostata da 5.6.3 a 5.4.1**.

**Cosa cambia:**

- `tesi/indice.py` stampa la struttura **di adesso**, letta dai `.tex`
  nell'ordine in cui `tesi.tex` li include. Riconosce anche le forme stellate e
  i titoli di quarto livello, che l'indice non mostra, e li marca invece di
  ometterli in silenzio. `--titoli` li elenca tutti, `--soli-fuori` mostra solo
  quelli;
- `INDICE_E_STRUTTURA.txt` ha ora un blocco sui **161 titoli fuori indice** e
  sulla ragione: un `\paragraph` sta fuori **per scelta di struttura**
  (`tocdepth` = 2, e la regola del titolo ogni ~400 parole), una forma stellata
  **per costruzione** — non scrive nel `.toc` — ed è quindi il tipo di titolo
  che sparisce senza che nessuno se ne accorga. Nel testo attuale ne resta
  **una sola**, `L'ambiguità di posa` in 3.2;
- **sei numeri del documento erano rimasti indietro** e sono stati corretti,
  ciascuno con la sua storia dichiarata fra parentesi: il divario fra le viste
  (0,872 → 0,822 come primo valore, e 0,438 → 0,334 come divario), l'escursione
  fra architetture (0,079 → 0,045), le occlusioni (0,020 → 0,037), il costo per
  fotogramma (88,4%/5,8% → 85,2%/14,3%) e il fattore fra finestre ed eventi
  (47,8 → 44,8). Il primo, 0,872, era il valore ritirato da
  [ISS-129](ISSUES.md#iss-129): stava in un documento indirizzato al relatore;
- il conteggio delle parole passa da 35.491 a **41.525**.

**Verificato con:** `python tesi/indice.py` nelle tre modalità -> struttura
completa, 161 titoli fuori indice di cui 1 stellato; conteggi per capitolo
confrontati con `tesi/controlla.py`.

**Collegamenti:** [ISS-129](ISSUES.md#iss-129), [ISS-143](ISSUES.md#iss-143),
[ISS-145](ISSUES.md#iss-145), Capitolo 5 `tab:latenza_misurata`

---

## [2026-09-07] — Una relazione unica per il relatore, e l'indice rimesso in pari

**Tipo:** docs
**File:** `docs/relatore/RELAZIONE_PER_IL_RELATORE.md` (nuovo),
`docs/relatore/INDICE.md`, `docs/relatore/NOVITA_6_7_settembre.md`,
`docs/relatore/B3_occlusioni_controllate.md`

**Perché:** sedici schede rispondono bene a «da dove viene questo numero», ma
non si leggono di seguito. Per mandare qualcosa serviva **un documento solo**,
discorsivo, che si legga dall'inizio alla fine.

**Cosa cambia:**

- `RELAZIONE_PER_IL_RELATORE.md` — 577 righe in sei parti: le tre nozioni per
  leggere i numeri spiegate una volta sola, poi A, B, C, i risultati dei due
  giorni, ciò che resta aperto e le sette domande. Le schede restano come
  dettaglio;
- **rileggendo tutte le schede ne è emersa una rimasta indietro:** B3 riportava
  ancora i numeri delle occlusioni di prima della riesecuzione (0,020 contro
  una dispersione di 0,078). Allineata a 0,037 e 0,071;
- `NOVITA_6_7_settembre.md` **era incompleto**: elencava sette risultati e ne
  erano nati altri cinque nel pomeriggio — le viste rifatte con il risultato
  ritirato, la soglia dei 60 gradi, le occlusioni rimisurate, la latenza, le
  regole di allarme. Ora sono dodici, di cui otto difetti;
- `INDICE.md` riscritto: indicava come documento da mandare quello sbagliato,
  dichiarava sei domande invece di sette e «tre grandezze su quattro» per B4,
  che ora sono quattro.

**Verificato con:** tutti i collegamenti fra i ventitré file risolvono a un file
esistente; `python tesi/controlla.py` -> «Nessun problema»; `python
prove/esegui.py` -> 31 su 31.

**Collegamenti:** [EXP-029](EXPERIMENTS.md#exp-029),
[EXP-028](EXPERIMENTS.md#exp-028), [EXP-027](EXPERIMENTS.md#exp-027)

---

## [2026-09-07] — La regola di allarme era la peggiore delle quattro provate

**Tipo:** feature
**File:** `pipeline/regole_allarme.py` (nuovo)

**Perché:** il Capitolo 5 osservava che tre cadute vere non producono allarme
«con corse massime di due, zero e tre finestre», e non ne traeva la
conseguenza. La regola installata chiede cinque finestre **consecutive**:
azzera l'evidenza gia' accumulata a ogni fotogramma storto, e i fotogrammi
vanno storti proprio nelle cadute difficili.

**Cosa cambia:**

- `regole_allarme.py` confronta **ventuno regole di quattro famiglie** —
  consecutive, m su n, cumulata (CUSUM), isteresi — sugli stessi punteggi gia'
  salvati. Non riaddestra nulla: cambia solo l'aritmetica che trasforma i
  punteggi in un allarme, e ogni regola e' causale, quindi eseguibile a bordo
  cosi' com'e' scritta;
- il giudizio e' su **due assi che vengono da archivi diversi**: richiamo e
  latenza dalle cinquanta cadute annotate di UP-Fall, allarmi all'ora dalle nove
  sessioni domestiche dove cadute non ce ne sono;
- **undici regole su venti battono quella installata su entrambi gli assi.** La
  cumulata a 0,5 prende 49 cadute su 50 invece di 44, è 0,9 s più veloce e fa il
  14% di falsi allarmi in meno; l'isteresi 0,80/0,45/3 ne prende 48, è 0,5 s più
  veloce e **dimezza i falsi allarmi**, da 10,8 a 5,1 all'ora;
- **il risultato è strutturale**: tutte e cinque le varianti della cumulata e
  tre delle quattro dell'isteresi battono l'installata. Non è un parametro
  fortunato, è la famiglia consecutiva a essere quella sbagliata.

**Verificato con:** `regole_allarme.py` sulle configurazioni DTW e DTWH ->
stessa graduatoria, valori assoluti migliori su DTWH; allineamento fra finestre
e punteggi verificato su dieci fold.

**Collegamenti:** [EXP-029](EXPERIMENTS.md#exp-029),
[EXP-028](EXPERIMENTS.md#exp-028), [ISS-145](ISSUES.md#iss-145)

---

## [2026-09-07] — La latenza si misurava, e il limite inferiore non lo era

**Tipo:** feature + fix
**File:** `pipeline/latenza_laboratorio.py` (nuovo), `tesi/Cap5.tex`

**Perché:** rispondendo a una domanda che nessuno aveva fatto — *da che cosa si
dice che cinque finestre consecutive vadano bene?* — sono emersi due difetti
nello stesso paragrafo del Capitolo 5.

**Cosa cambia:**

- `latenza_laboratorio.py` misura la latenza di rilevamento **dove le etichette
  lo permettono**. In casa non è misurabile e resta dimostrato; in UP-Fall
  l'etichetta è per fotogramma, quindi l'istante d'inizio è noto a 1/18 di
  secondo e le cadute sono cinquanta invece di cinque. Non riaddestra nulla:
  rilegge i punteggi salvati e **si ferma** se le finestre ricostruite non
  coincidono fold per fold con essi, perché senza allineamento ogni latenza
  finirebbe sulla ripresa sbagliata;
- **[ISS-145, primo difetto] la persistenza valeva 5 e nessuno sapeva perché.**
  Ora ogni passo costa 0,222 s di latenza e una frazione di richiamo, misurati:
  da k=1 a k=5 si perdono un secondo e dieci punti di richiamo, e si guadagna il
  31% di falsi allarmi in meno. Il compromesso è esposto invece che nascosto;
- **[ISS-145, secondo difetto] i 3,778 s non erano un limite inferiore.** La
  mediana misurata alla stessa regola è 2,44 s — 2,74 riportata alla frequenza
  della tabella — perché la scomposizione suppone che la finestra debba
  riempirsi *dopo* l'inizio della caduta, e non è richiesto: il classificatore
  decide su finestre a cavallo dell'istante d'inizio. Il Capitolo 5 chiama ora
  quel valore **caso conservativo**, e gli mette accanto la misura con la curva
  della persistenza (`tab:latenza_misurata`).

**Verificato con:** `latenza_laboratorio.py` sulle configurazioni DTW e DTWH ->
allineamento verificato su dieci fold, mediana 2,44 s e 2,47 s a k=5;
`python tesi/controlla.py` -> «Nessun problema».

**Collegamenti:** [EXP-028](EXPERIMENTS.md#exp-028),
[ISS-145](ISSUES.md#iss-145), [ISS-108](ISSUES.md#iss-108)

---

## [2026-09-07] — Le occlusioni rimisurate, e la robustezza che dipende dalle colonne

**Tipo:** feature + docs
**File:** `pipeline/occlusioni.py`, `tesi/Cap4.tex`,
`tesi/figure/fig_occlusioni.png`, `risultati/occlusioni/`

**Perché:** la misura delle occlusioni era di agosto, quindi con il motore
geometrico e la selezione DTW di allora. Il resto del lavoro è stato rifatto sul
dataset riestratto: lasciarla indietro avrebbe messo nello stesso capitolo
numeri di due impianti diversi.

**Cosa cambia:**

- `occlusioni.py` accetta `--scelte`, il file della selezione DTW, e
  `--suffisso` per non sovrascrivere l'uscita. Servono a **separare l'effetto
  del motore da quello delle colonne** quando i due cambiano insieme; il JSON
  registra ora anche le colonne usate e il file da cui vengono;
- corretto il messaggio finale, che stampava il nome del file **senza** il
  suffisso: diceva di aver scritto un file diverso da quello scritto davvero;
- **il numero peggiore raddoppia**: le spalle passano da $-0{,}020$ a
  $-0{,}037$, e il mascheramento casuale di cinque punti su nove da $-0{,}009$ a
  $-0{,}032$. La conclusione regge --- 0,037 resta sotto la dispersione fra
  soggetti, 0,071 --- ma il margine passa da un fattore quattro a un fattore
  due;
- **la causa è stata isolata con una terza esecuzione**, motore nuovo e colonne
  di agosto: i numeri di agosto tornano. Non è il motore, **sono le colonne**, e
  si spiega con una sola su dodici --- entra l'angolo del tronco, che dipende
  dalle spalle, al posto di una grandezza riferita al naso;
- il Capitolo 4 riscrive di conseguenza la seconda osservazione: non è che
  l'informazione sia distribuita *in sé*, **lo è per un dato insieme di
  grandezze**.

**Verificato con:** tre esecuzioni di `occlusioni.py` --- agosto conservata,
colonne correnti, colonne di agosto --- confrontate riga per riga in
[EXP-027](EXPERIMENTS.md#exp-027); `python tesi/controlla.py` -> «Nessun
problema»; `python prove/esegui.py` -> 31 su 31.

**Collegamenti:** [EXP-027](EXPERIMENTS.md#exp-027),
[ISS-138](ISSUES.md#iss-138), Capitolo 4 `tab:occlusioni`

---

## [2026-09-07] — Le tre righe della vista, un risultato ritirato, e due figure che mancavano

**Tipo:** feature + fix
**File:** `pipeline/viste_incrociate.py` (nuovo), `pipeline/figure_tesi.py`,
`tesi/Cap4.tex`, `tesi/figure/fig_viste.png`, `fig_dominio.png`,
`fig_viewpoint_dist.png`

**Perché:** la tabella `tab:viste` era l'ultima misura del lavoro ferma a
cinque soggetti, mentre la misura geometrica che la spiega era a dieci: due
provenienze nello stesso paragrafo. E il divario fra le viste conteneva **due
cause** che il testo poteva solo dichiarare senza separarle.

**Cosa cambia:**

- `viste_incrociate.py` rifà le tre righe a dieci soggetti sul dataset
  riestratto, tutte in **una sola esecuzione** — è il rimedio strutturale a
  [ISS-129](ISSUES.md#iss-129), dove una riga veniva da un modello diverso
  dalle altre due — e aggiunge `--senza-contaminate`, che esclude le riprese in
  cui lo stimatore cambia persona. Il criterio non è riscritto: si legge la
  colonna `salto_a` prodotta da `escursione_viste.py`, perché averlo in due
  posti significherebbe averne due;
- **il divario passa da 0,422 a 0,334** e il recupero addestrando su due viste
  dal 58% al 73%;
- **le due cause sono separate:** senza le undici riprese contaminate il
  divario non si chiude, passa a 0,356. Il cambio di persona falsava la misura
  geometrica, non il divario di classificazione;
- **[ISS-143] un risultato del Capitolo 4 è stato ritirato.** La quarta riga,
  aggiunta apposta, dà 0,753 addestrando direttamente su Camera 2 contro 0,488
  trasferendo da Camera 1: il «risultato controintuitivo» si rovescia;
- `fig_viewpoint_dist.png` **rifatta**: tracce in tinta media invece che grigio
  pallido, riferimento a 60°, rapporto sulle medie, legenda sotto, e la prosa
  spostata dalla figura alla didascalia — dentro l'immagine restano solo i
  valori, come vuole la convenzione di `salva()`;
- **due figure nuove**: `fig_viste.png` (F2 con la dispersione, e i due errori
  separati) e `fig_dominio.png` (il divario fra i due archivi scomposto in 49%
  taratura e 51% perdita reale). Erano due punti del testo senza immagine.

**Verificato con:** `viste_incrociate.py --csv feature_v3.csv --feature A3
--escludi A3_h_pavimento`, con e senza `--senza-contaminate`;
`python tesi/controlla.py` -> «Nessun problema»; `python prove/esegui.py` ->
31 su 31; `python pipeline/audit_numeri.py` -> Cap4 passa da 260 a 270 numeri
con gli stessi 11 orfani, cioè **i dieci numeri nuovi hanno tutti un
artefatto**.

**Collegamenti:** [EXP-026](EXPERIMENTS.md#exp-026),
[ISS-143](ISSUES.md#iss-143), [ISS-134](ISSUES.md#iss-134),
[ISS-129](ISSUES.md#iss-129)

---

## [2026-09-07] — Le risposte al relatore, una scheda per richiesta

**Tipo:** docs
**File:** `docs/relatore/` (nuova, 20 file), `docs/RISPOSTE_AL_RELATORE.md`

**Perché:** le risposte alle sedici richieste stavano in un solo file, che
diceva *che cosa* è stato fatto ma non *come*. Per una discussione serve poter
risalire il ragionamento di ciascuna: quali ipotesi sono state verificate,
quali smentite, quali errori sono stati commessi e corretti per strada.

**Cosa cambia:**

- `docs/relatore/INDICE.md` — l'indice, con lo stato di ogni richiesta;
- `docs/relatore/RISPOSTE.md` — il testo unico, tutte le risposte in sequenza,
  aggiornato al 7 settembre;
- **sedici schede**, una per richiesta (A1-A4, B1-B5, C1-C7), ciascuna con la
  stessa forma: che cosa è stato chiesto, la risposta in una riga, il percorso
  passo per passo, **che cosa la risposta non copre**, e i file da cui i numeri
  escono;
- `docs/relatore/D_domande_al_relatore.md` — le domande rivolte a lui, ora
  **sei**: alle quattro del 26 agosto se ne aggiungono due nate in questi due
  giorni (installare o no l'altezza dal pavimento sulla board; che fare dei
  4,47 ms attribuiti alla board);
- `docs/relatore/NOVITA_6_7_settembre.md` — i sette risultati degli ultimi due
  giorni letti insieme, perché tre di essi hanno la stessa causa: MediaPipe Pose
  è un tracciatore, e il progetto non lo aveva mai messo per iscritto;
- `docs/RISPOSTE_AL_RELATORE.md` porta ora in testa il rimando alla cartella
  nuova, e resta come storia: nulla si cancella.

**Numeri aggiornati rispetto alla versione del 6 settembre:** il fattore fra
finestre ed eventi (47,8 -> **44,8**), il costo per fotogramma consolidato sulle
4,59 ore (144,1 -> **136,65 ms**, cioè 3,8x -> **3,6x**), la prova di durata da
«non fatta» a **fatta**, e tre difetti nuovi (ISS-140, ISS-141, ISS-142).

**Verificato con:** tutti i collegamenti interni fra le venti schede risolvono
a un file esistente; `python tesi/controlla.py` -> «Nessun problema»;
`python prove/esegui.py` -> 31 su 31.

**Collegamenti:** [ISS-140](ISSUES.md#iss-140), [ISS-141](ISSUES.md#iss-141),
[ISS-142](ISSUES.md#iss-142), [EXP-022](EXPERIMENTS.md#exp-022),
[EXP-023](EXPERIMENTS.md#exp-023), [EXP-024](EXPERIMENTS.md#exp-024)

---

## [2026-09-07] — La sessione che spariva dal conto, e l'archivio delle run su v2

**Tipo:** fix + feature
**File:** `pipeline/eventi_sessioni.py`,
`risultati/addestramento/v2/` (nuova), `risultati/campo/eventi_sessioni.json`
(nuovo)

**Perché.** Ripreso il lavoro dopo la sera del 6, in cui la riestrazione, la
selezione DTW, due addestramenti e una prova di durata di quattro ore e mezzo
sono arrivati **dopo** l'ultima riga di registro. Rimettendo in fila i
risultati sono venuti fuori due difetti.

**[ISS-140] La sessione del 6 settembre non entrava in nessun numero di
campo.** `eventi_sessioni.py` cercava `*/*/punteggi.csv`, che è il nome scritto
da `session_recorder.py`; `deploy_board/rileva.py` scrive invece
`<nome_sessione>.csv`, con `t_s` al posto di `t_unix` e `sopra` al posto di
`sopra_soglia`. Lo script stampava otto blocchi invece di nove **senza
segnalare nulla**, e il totale era coerente con se stesso.

**Il fattore di sovrastima cambia: da 47,8 a 44,8**, su 14,98 ore invece di
10,39 e 166 eventi invece di 152. È un numero citato nel Capitolo 5, nella
guida al lavoro, nel documento per il relatore e in due schede di figura.

**Secondo difetto, trovato mentre si sistemava il primo:** quel numero non
aveva un artefatto. Lo script stampava e non salvava, e `audit_numeri.py` lo
dava per coperto solo perché la cifra `47.8` compare per caso dentro i JSON di
addestramento — la stessa trappola di [ISS-135](ISSUES.md#iss-135).

**Cosa cambia:**

- `elenco_punteggi()` riconosce entrambi i nomi di file, esclude
  `*_feature.csv` e sostituisce il `glob` in due punti;
- `tempo_e_decisione()` legge entrambi gli schemi di colonne. Per il conteggio
  degli eventi conta solo la **differenza** fra gli istanti, quindi epoch e
  orologio monotòno sono equivalenti: il commento lo dice, perché altrimenti
  la riga sembra una scorciatoia;
- ogni esecuzione scrive `risultati/campo/eventi_sessioni.json` con la tabella
  per sessione e l'aggregato. Il percorso della sorgente è relativo: un
  artefatto viaggia fra macchine, un percorso assoluto no;
- `risultati/addestramento/v2/` conserva le venti run su `feature_v2.csv` con
  il loro LEGGIMI. Serviva prima di riaddestrare: i nomi dei file prodotti da
  `addestra.py` non contengono la versione del dataset, e le run di GRU e
  della rete a grafo sarebbero state sovrascritte senza avviso.
  `scheda_numeri.py` non le rilegge, perché tiene solo i nomi che cominciano
  per `run_`.

**[ISS-141] E lo stesso difetto di [ISS-135](ISSUES.md#iss-135) è rientrato da
un'altra porta.** I due CSV della sessione del 6 settembre — uno per finestra,
uno per fotogramma da 17,8 MB — sono finiti nella riserva di `audit_numeri.py`,
che è salita a 1,8 milioni di valori distinti. Con abbastanza decimali
arbitrari **ogni** numero del testo trova un riscontro per caso: l'audit
dichiarava **zero** numeri senza riscontro in tutti i capitoli. Togliendo quei
due soli file la riserva scende a 10.769 valori — **erano il 99,4% del totale** — e i numeri senza riscontro tornano a 5 nel Capitolo 3, 11 nel 4,
15 nel 5 e 4 nelle Conclusioni: **trentacinque in tutto**. `e_grezzo_di_sessione()` li esclude ora; il `riepilogo.json` della
sessione resta dentro, perché quello i risultati li contiene.

**Il file d'oro delle prove è stato rigenerato**, e la ragione va scritta:
senza, sarebbe indistinguibile da una regressione. Il motore produce 33
grandezze invece di 32, quindi `prova_geometria` falliva sul confronto dei
nomi. **Prima di rigenerarlo è stato verificato che le 32 grandezze vecchie
non cambiano di un bit** — scarto massimo 0,0 su tutte e 32 — cioè che la
modifica al motore è puramente additiva e non tocca nessun numero già
scritto. Dopo la rigenerazione: **31 prove su 31**.

**Verificato con:** `python pipeline/eventi_sessioni.py` → nove blocchi invece
di otto, `notte_20260906_1523` presente con 4,59 ore, 3,1 eventi/ora e fattore
12,0, aggregato 44,8 su 14,98 ore; artefatto scritto e riletto.

**Collegamenti:** [ISS-140](ISSUES.md#iss-140), [ISS-113](ISSUES.md#iss-113),
[EXP-024](EXPERIMENTS.md#exp-024), [EXP-025](EXPERIMENTS.md#exp-025)

---

## [2026-09-06] — L'altezza dal pavimento torna nel motore, e il dataset si rifa'

**Tipo:** feature + fix
**File:** `src/geometry.py`, `pipeline/estrai_feature.py`,
`dataset/processed/features/feature_v3.csv` (in produzione), `tesi/Cap4.tex`,
`tesi/Cap5.tex`

**Perche':** tre difetti distinti, trovati nello stesso pomeriggio e che si
risolvono con la stessa riestrazione.

**[ISS-139] La tesi dichiarava installata una configurazione che non c'era.**
Il Capitolo 3 dice che il sistema finale poggia su A3h --- con l'altezza del
bacino dal pavimento --- e A3i. Il dispositivo esegue il sottoinsieme DTW a
dodici colonne, che quella grandezza non la contiene. **E non poteva
contenerla: `h_pavimento` non era fra le 32 grandezze del motore**, quindi il
DTW non avrebbe potuto sceglierla nemmeno volendo. Nel primo impianto quella
grandezza dimezzava i falsi negativi, da 45 a 22.

**[ISS-138] Le feature dipendevano dall'ordine di estrazione.**
`estrai_feature.py` azzerava il motore geometrico a ogni ripresa --- con tanto
di commento che ne spiegava la ragione --- ma creava **un solo** stimatore di
posa per tutte e 220. Il ragionamento era giusto e si era fermato a meta'.

**Il dataset era a 218 video su 220.** Due mancavano davvero, un terzo aveva un
errore di battitura nel nome originale (`trail01`).

**Cosa cambia:**

- `src/geometry.py` produce **33 grandezze**: torna `A3_h_pavimento`. La stima
  e' **causale** --- si accumulano le osservazioni di chi sta in piedi e si
  adatta la retta del pavimento quando ne bastano --- perche' sul dispositivo
  non esiste il futuro. L'implementazione precedente adattava sull'intero
  archivio a posteriori;
- **il pavimento non si azzera con la ripresa.** E' una proprieta' della
  TELECAMERA: in una ripresa di caduta nessuno sta in piedi abbastanza a lungo
  per stimarlo. `reset()` azzera lo stato della ripresa, `reset_pavimento()` e'
  separata. La prima versione sbagliava proprio qui, e dava «stima non
  riuscita» su tutti i video di caduta perche' vengono elaborati per primi:
  sarebbe stata **una nuova dipendenza dall'ordine**, cioe' ISS-138 rientrato
  da un'altra porta;
- l'estrazione tiene **un motore per telecamera** e **ricalcola l'altezza alla
  fine** con la retta stimata su tutta la telecamera, cosi' il valore non
  dipende da come sono ordinate le riprese;
- lo **stimatore di posa nasce e muore dentro ciascuna ripresa** (ISS-138);
- nuovo controllo `controlla_etichette`, che ferma l'estrazione se una ripresa
  di caduta e' priva di suffissi --- verrebbe etichettata «caduta in corso» per
  intero, compresi i secondi in cui la persona cammina --- se una ripresa e'
  etichettata a meta', o se un'attivita' normale porta un suffisso diverso da
  `-0`;
- `--riprese` per riestrarre pochi video invece di un soggetto intero.

**L'asimmetria che va dichiarata, ed e' scritta nel codice:** in addestramento
il pavimento e' stimato su tutta la telecamera, in esercizio su cio' che il
dispositivo ha visto finora.

**Verificato con:** `estrai_feature.py --riprese ...` su quattro riprese ->
33 colonne, retta `y = -0,0114x + 479,8` da 1.610 fotogrammi eretti, altezza
mediana +1,37 torsi; controllo delle etichette su tutte e 220 le riprese ->
nessuna anomalia.

**Esito della riestrazione completa, chiusa alle 20:57 del 6 settembre.**
`feature_v3.csv`: **220 riprese**, **116.362 fotogrammi**, **33 grandezze**,
**95,9%** di pose valide. Le etichette non cambiano di un fotogramma (5.542
«caduta in corso», 10.524 «a terra», identici a v2), e i 1.439 fotogrammi in
piu' sono esattamente quelli dei due video aggiunti. `A3_h_pavimento` e'
definita sul **100%** dei fotogrammi con posa, con mediane 1,517 / 0,958 /
0,502 lunghezze di torso per le tre etichette. Dettagli in
[EXP-022](EXPERIMENTS.md#exp-022).

**Collegamenti:** [ISS-138](ISSUES.md#iss-138), [ISS-139](ISSUES.md#iss-139),
[EXP-021](EXPERIMENTS.md#exp-021)

---

## [2026-09-06] — Gli errori scomposti per attivita', e due tabelle nel Capitolo 4

**Tipo:** feature
**File:** `tesi/Cap4.tex`, `risultati/addestramento/_mappa_finestre.npz`

**Perche':** il punto 5 dell'email del relatore --- «mostra i due errori, non
un solo F2» --- era stato evaso con una tabella aggregata. Ma i falsi allarmi
non sono diffusi: sono concentrati, e nessuno l'aveva mai verificato.

**Non e' una run nuova.** Le sei architetture furono addestrate il 20 e il 27
agosto. Qui si rileggono i punteggi per finestra gia' salvati e si attribuisce
ogni finestra all'attivita' da cui proviene, ricostruendo le finestre con
`src/dati.py`: le numerosita' coincidono su tutti e dieci i fold, quindi
l'attribuzione e' verificabile.

**Cosa e' uscito:** su **419 falsi allarmi, 389 --- il 93% --- vengono da una
sola attivita', sdraiarsi**. Camminare, stare in piedi e saltare non ne
producono nemmeno uno su cinquemila finestre.

**L'ipotesi della velocita', verificata e smentita.** Il picco di velocita'
verticale di una camminata (mediana 0,087) **supera** quello della finestra
mediana di caduta (0,055): in due secondi e mezzo di passi il corpo oscilla
molte volte. Se il sistema decidesse sulla velocita', camminare sarebbe il
falso allarme principale.

*Un errore commesso e corretto nel farlo:* la prima versione dell'analisi
usava `A3_hip_vel`, che e' il **modulo** dello spostamento, quindi velocita' in
qualunque direzione. Con quella camminare risultava sette volte piu' veloce
delle cadute --- vero e privo di significato. Rifatta con `A1_vy`, verticale
con segno.

**E il richiamo per tipo di caduta va da 0,934 (di lato) a 0,704
(all'indietro):** ventitre punti, piu' del divario fra due qualunque delle sei
architetture.

**Verificato con:** ricostruzione delle finestre allineata ai punteggi salvati
-> stesse numerosita' su tutti i fold; `python tesi/controlla.py` ->
«Nessun problema».

**Collegamenti:** [EXP-021](EXPERIMENTS.md#exp-021), Capitolo 4
`tab:errori_attivita`, `tab:richiamo_tipo`

---

## [2026-09-06] — Il costo sul dispositivo, misurato invece che trascritto

**Tipo:** fix
**File:** `deploy_board/rileva.py`, `tesi/Cap5.tex`

**Perche':** [ISS-113](ISSUES.md#iss-113) --- la ripartizione del costo per
fotogramma esisteva solo nel testo. Il 6 settembre `rileva.py` e' stato
installato sulla board (dove c'era ancora il deployment di agosto) ed eseguito
sulla telecamera vera.

**Cosa e' uscito:** **144,1 ms per fotogramma, cioe' 6,9 fps**, contro i
37,7 ms e 26,5 fps dichiarati. **Il dispositivo e' 3,8 volte piu' lento.** Le
proporzioni reggono --- percezione 86,2%, classificatore 12,7% --- e con esse
l'affermazione portante del capitolo.

**L'obiezione della stanza vuota, verificata e falsificata:** con un soggetto
in scena il costo **sale** da 126,0 a 144,1 ms, perche' al rilevatore si
aggiunge il modello dei landmark.

**Altre due correzioni a `rileva.py` nella stessa sessione:**

- `--camera` accetta un **percorso** oltre all'indice. L'indice non e' stabile:
  la stessa telecamera e' passata da `/dev/video0` a `/dev/video1` per una
  ri-enumerazione, e una prova lunga lanciata sull'indice sbagliato non parte;
- **il registratore sopravvive alla sparizione della telecamera.** Sulla board
  l'autosuspend USB la fa ri-enumerare e la lettura fallisce con «No such
  device»: e' successo dopo 193 secondi e ha ucciso una prova di dodici ore al
  terzo minuto. Ora riprova a riaprirla, e scrive nel riepilogo **quante volte
  e per quanti secondi** --- un'ora di buco passata sotto silenzio sarebbe
  peggio della prova fallita;
- `--feature` scrive tutte e **32** le grandezze per fotogramma, con i nomi e
  l'ordine del dataset. Senza, una sessione domestica produce punteggi e da un
  punteggio non si riaddestra niente: e' il motivo per cui le cadute registrate
  in agosto non sono aggiungibili al dataset. Salvarne dodici --- quelle che il
  modello usa oggi --- sarebbe stato lo stesso errore.

**Verificato con:** `rileva.py --parita` sulla board -> impronta di
`geometry.py` identica, 200 finestre con scarto `0,000e+00`; due sessioni da
60 s, a stanza vuota e con soggetto.

**Collegamenti:** [ISS-113](ISSUES.md#iss-113), [ISS-137](ISSUES.md#iss-137)

---

## [2026-09-06] — Le figure non concludono piu' al posto del testo

**Tipo:** refactor
**File:** `pipeline/figure_tesi.py`, `tesi/figure/*.txt` (21 schede)

**Perche':** diverse figure portavano stampata dentro la propria conclusione
--- «Nessuna architettura fa meglio della GRU», «Nessun gruppo di punti e'
critico» --- e sotto una nota in prosa.

Un titolo che afferma una tesi non e' una figura, e' una diapositiva: il
lettore non puo' verificarlo guardando, gli viene detto. In una tesi la
conclusione la trae il testo. E quella prosa non e' modificabile senza
rigenerare l'immagine, non compare nell'indice delle figure, non e' cercabile.

**Cosa cambia:** i titoli sono **descrittivi**; le note in prosa sono uscite
dalle immagini; `salva()` scrive accanto a ogni PNG una **scheda `.txt`** con
quattro voci --- che cosa mostra, come si legge, i numeri, provenienza. Dentro
l'immagine restano solo i valori sui marcatori e le etichette degli schemi.

**Un numero alla deriva trovato nel farlo:** la scheda di `fig_sessione`
dichiarava il fattore 47,8, ma **quella sessione ne da' 14,9**. Ora il valore
e' calcolato dalla figura stessa, e il 47,8 e' dichiarato come valore
d'insieme.

**Verificato con:** `python pipeline/figure_tesi.py` -> 14 figure e 21 schede;
`fig_architetture.png` ispezionata a video.

## [2026-09-06] — L'audit dei numeri escludeva niente, e questo lo rendeva inutile

**Tipo:** fix
**File:** `pipeline/audit_numeri.py`, `pipeline/escursione_viste.py`

**Perche':** salvando la serie per campione di cento riprese --- circa 24.000
float, che l'audit moltiplica per sei arrotondamenti --- i numeri del
**Capitolo 5 senza riscontro sono passati da 9 a 1 senza che una sua riga
fosse toccata**. Con abbastanza decimali arbitrari nella riserva, qualunque
numero trova una corrispondenza per caso ([ISS-135](ISSUES.md#iss-135)).

**Cosa cambia:**

- `audit_numeri.py` esclude i file `*_serie.json` e `*_serie.csv`: una serie
  per campione e' il dato grezzo da cui un risultato si calcola, non un
  risultato. Il commento riporta i due conteggi, perche' la riga non si
  giustifica senza;
- `escursione_viste.py` scrive un `_riepilogo.json` con le statistiche
  **derivate** --- medie, deviazioni, rapporti, conteggi, salto massimo --- che
  nel CSV non compaiono e che prima restavano solo stampate a schermo. Con
  `--solo-riepilogo` si ricalcola dal CSV senza rifare la stima di posa.

**Verificato con:** `python pipeline/audit_numeri.py` -> Cap4 da 0 (falso) a
5, Cap5 da 1 (falso) a 8; poi, prodotto il riepilogo, Cap4 resta 5 e i due
numeri nuovi della sezione sul punto di vista sono coperti. I cinque residui
di Cap4 sono gli stessi di prima della sessione: due valori critici di test
statistico, un intervallo di rapporti, e il $4{,}32\times$ storico che il
testo cita **come valore ritirato**.

**Collegamenti:** [ISS-135](ISSUES.md#iss-135)

## [2026-09-06] — L'escursione fra le due viste, rifatta su dieci soggetti

**Tipo:** fix
**File:** `pipeline/escursione_viste.py`, `pipeline/figura_due_camere.py`,
`pipeline/figure_tesi.py`, `tesi/Cap4.tex`,
`risultati/laboratorio/escursione_viste_10sog.csv` (nuovo) e il suo
`_serie.json`, `tesi/figure/fig_due_camere.png`,
`tesi/figure/fig_viewpoint_dist.png`

**Perche':** quella misura era dichiarata «a cinque soggetti» e lo era
soltanto perche' fu eseguita allora --- i fotogrammi grezzi di **entrambe** le
telecamere esistono per tutti e dieci. Rifarla costa quaranta minuti di
calcolo e toglie al Capitolo 4 una delle sei avvertenze di provenienza.

**Cosa cambia nei numeri:**

| | prima | dopo |
|---|---:|---:|
| Camera1 / Camera2 | 71,0° / 35,7° | **74,0° / 33,2°** |
| rapporto fra le medie | 1,99× | **2,23×** |
| sopra 60° | 18 su 25 / 6 su 25 | **30 su 39 / 8 su 39** |
| sequenze con Camera2 >= Camera1 | 2 su 25 | **1 su 39** |
| cambi di persona | non misurati | **0 su 50 / 11 su 50** |

Il valore a dieci soggetti sta **fra** quello contaminato (1,99×) e quello
pulito a cinque (2,44×), che e' il comportamento atteso di una stima su un
campione doppio.

**Cosa cambia nel testo.** La sezione ha ora **due** meccanismi e non uno:
la compressione prospettica, e il cambio di persona con la sua tabella
`tab:cambio_persona`. Il paragrafo delle correzioni racconta i tre valori
successivi --- 4,32×, 1,99×, 2,23× --- e che cosa insegna ciascuno: il primo
era numerosita', il secondo stato residuo fra esecuzioni, il terzo non e' un
errore di misura ma un comportamento del sistema.

**Cosa cambia nelle figure.** `fig_due_camere` e' su `sub09_act05_trial01`,
che ha il rapporto mediano esatto delle 39 riprese pulite a dieci soggetti;
`fig_viewpoint_dist` legge il CSV nuovo, disegna tratteggiate le undici
riprese con cambio di persona escludendole dalle medie, e **non stampa piu'
l'avvertenza a cinque soggetti**.

**Due difetti di codice trovati nel farlo, entrambi corretti:** la nota in
calce alla figura riportava il nome della ripresa e la numerosita' scritti a
mano, e sono rimasti indietro a ogni cambio; ora si ricavano dal CSV con cui
la figura si e' confrontata. E `figura_due_camere.py` ricavava la cartella del
soggetto da una costante invece che da `--nome`.

**Verificato con:**
`escursione_viste.py --soggetti 1,...,10` -> 100 riprese, CSV e serie scritti;
`figura_due_camere.py` -> escursione ricalcolata uguale al CSV a **0,00°** su
entrambe le telecamere, nessun cambio di persona, PNG ispezionato a video;
`figure_tesi.fig_viewpoint_dist` -> 39 coppie valide, rapporto 2,23, 1
rovesciata, 11 escluse; `python tesi/controlla.py` -> «Nessun problema».

**Collegamenti:** [EXP-020](EXPERIMENTS.md#exp-020),
[ISS-133](ISSUES.md#iss-133), [ISS-134](ISSUES.md#iss-134)

---

## [2026-09-06] — L'indirizzo della board non e' fisso, e ha simulato un attacco

**Tipo:** docs
**File:** `CLAUDE.md`, sezione «La board»

**Perche':** con la board spenta, il router ha assegnato **al calcolatore**
l'indirizzo `192.168.1.13` che CLAUDE.md dichiarava come quello della board.
`ping` ha risposto in 0 ms --- rispondeva a se stesso --- e
`ssh rock@192.168.1.13` ha prodotto `REMOTE HOST IDENTIFICATION HAS CHANGED`,
che si legge come un attacco e invece era il PC che parlava con se stesso.

**Il rischio evitato:** la reazione ovvia a quell'errore e' cancellare la voce
da `known_hosts`. Sarebbe stato il danno vero, perche' quella voce e' **l'unica
cosa che identifica la board** su una rete dove l'indirizzo cambia.

**Cosa cambia:** la sezione non dichiara piu' un indirizzo fisso e spiega come
trovare la board per **impronta della chiave** invece che per indirizzo, con il
comando. Dice anche che se la chiave non compare su nessun indirizzo la board
e' spenta, e che nessuna scansione la fa apparire.

**Verificato con:** `ipconfig` -> il calcolatore ha 192.168.1.13;
`ssh-keyscan -t ed25519` su 192.168.1.2-40 -> la chiave della board non
compare su alcun indirizzo, la board e' spenta.

## [2026-09-06] — `controlla.py` segue `tesi.tex` invece della cartella

**Tipo:** fix
**File:** `tesi/controlla.py`

**Perche':** lo script prendeva i capitoli con `glob('Cap*.tex')`, cioe'
controllava **la cartella** invece del **documento**. Il 5 settembre e'
bastato che comparisse `Cap1_riordinato.tex` --- una proposta di riordino del
Capitolo 1, non inclusa in `tesi.tex` --- perche' il controllo segnalasse
quattro problemi (una label duplicata e tre citazioni non definite) su un
documento che compilava benissimo.

**Il danno non e' il rumore, e' l'abitudine.** Un cancello che segnala errori
su file che non entrano nel PDF si impara a scorrere, ed e' il modo in cui un
errore vero passa inosservato. E' lo stesso difetto che aveva lasciato quattro
figure senza immagine per settimane.

**Cosa cambia:**

- i file da controllare si leggono dagli `\include` e `\input` di `tesi.tex`,
  ignorando le righe commentate; senza `tesi.tex` si ricade sul comportamento
  precedente, cosi' lo script resta usabile su una cartella di soli capitoli;
- i `.tex` presenti e non inclusi finiscono in un blocco a parte, **NON
  INCLUSI DA tesi.tex**: non sono un problema, una bozza in lavorazione e'
  legittima, ma vanno detti --- altrimenti si lavora per giorni su un file che
  nel PDF non entra, che e' esattamente il rischio che corre oggi
  `Cap1_riordinato.tex` con dentro `fig_popolazione.png`;
- `Frontespizio.tex` e `Ringraziamenti.tex` rientrano nel controllo, perche'
  `tesi.tex` li include e prima la glob li escludeva.

**Verificato con:** `python tesi/controlla.py` -> «Nessun problema. Restano 0
figure da produrre», con `Cap1_riordinato.tex` elencato fra i non inclusi;
uscita 0. Prima della modifica: 4 problemi e uscita 1.

**Collegamenti:** Capitolo 1, `fig:popolazione`

## [2026-09-06] — L'ultima figura mancante, e i due difetti che ha fatto emergere

**Tipo:** feature + fix
**File:** `pipeline/figura_due_camere.py` (nuovo),
`pipeline/escursione_viste.py` (nuovo),
`tesi/figure/fig_due_camere.png` (nuova),
`risultati/cinque_soggetti/exp013_camera_viewpoint_indipendente.csv` (nuovo),
`risultati/cinque_soggetti/exp013_serie.json` (nuovo)

**Perche':** `fig:due_camere` era l'unico ambiente `figure` di tutta la tesi
senza immagine, e il commento nel Capitolo 4 lo definiva «la piu' importante
del capitolo». Diceva anche «non e' generabile da uno script: va composta e
ritagliata a mano», e non era vero: la catena per leggere i fotogrammi,
stimare la posa e ritagliare esisteva gia' in `figura_rappresentazioni.py` e
`figura_striscia.py`.

**Cosa mostra la figura:** quattro pannelli, colonne le due telecamere, righe
due istanti della stessa caduta allo stesso indice di fotogramma. **In piedi
le due viste sono indistinguibili --- 88,3° e 89,8°. A terra no: 4,2° contro
73,6°.** La vista rialzata vede una persona distesa quasi come una in piedi,
ed e' l'affermazione del capitolo, mostrata.

**I due difetti, trovati perche' la figura si controlla da sola.** Lo script
ricalcola l'escursione della ripresa che disegna e la confronta con il CSV
citato dalla tabella accanto. Il confronto e' fallito, e sotto c'erano due
cose distinte:

- **[ISS-133](ISSUES.md#iss-133)** --- `check_camera_viewpoint.py` usa **un
  solo** stimatore di posa per tutte e cinquanta le riprese. MediaPipe Pose e'
  un tracciatore: l'ultimo fotogramma di una ripresa innesca il primo della
  successiva. Rimisurato con uno stimatore per ripresa, il rapporto fra le
  medie passa da **1,99× a 2,30×**, e su una singola ripresa lo scarto arriva
  a **68°**.

- **[ISS-134](ISSUES.md#iss-134)** --- su Camera2 lo stimatore **perde chi
  cade e si aggancia a un astante seduto**, in **6 riprese su 25**; su Camera1
  in **0 su 25**. La prima resa della figura ne era un caso: lo scheletro era
  addosso alla persona in maglia rossa seduta sulla sedia, con accanto un
  angolo di 87,1° che sembrava sensato. **Quel PNG e' stato cancellato.**

**Cosa cambia nel codice:**

- `figura_due_camere.py` sceglie gli istanti dalla **sola annotazione** (il
  centro del blocco di classe 0 e quello di classe 2), non dagli estremi
  dell'angolo su una delle due viste, che gonfierebbero il divario; e ha una
  guardia che **si rifiuta di disegnare** un istante successivo a un cambio di
  persona;
- `escursione_viste.py` rifa' la misura con uno stimatore per ripresa,
  identica in tutto il resto, conta i cambi di persona con un criterio
  dichiarato, e **non tocca il CSV originale**: scrive accanto, perche' la
  differenza fra i due file e' il dato;
- salva anche `exp013_serie.json` con la serie per campione delle cinquanta
  riprese, cosi' che il criterio del salto si possa cambiare **senza
  rieseguire due ore di stima di posa**. Stessa ragione dei punteggi per fold
  in `risultati/addestramento/*.npz`.

**Verificato con:**
`fall_processing/python.exe pipeline/escursione_viste.py` -> 50 riprese, CSV e
JSON scritti, confronto stampato; il valore a stimatore condiviso riproduce il
CSV originale a **0,00°** su entrambe le telecamere di `sub01_act01_trial01`,
che e' cio' che identifica la causa di ISS-133 senza margine.
`fall_processing/python.exe pipeline/figura_due_camere.py` -> escursione
ricalcolata uguale al CSV pulito a 0,00° su entrambe, nessun cambio di
persona, PNG scritto e **ispezionato a video**.

**Non verificato:** che il cambio di persona contamini anche le **feature** di
Camera2 usate per addestrare, che passano dallo stesso stimatore a persona
singola. Se lo facesse, parte del divario di F2 fra le viste avrebbe questa
causa e non solo quella ottica.

**Collegamenti:** [ISS-133](ISSUES.md#iss-133), [ISS-134](ISSUES.md#iss-134),
[EXP-020](EXPERIMENTS.md#exp-020), Capitolo 4 `fig:due_camere`

---

## [2026-09-06] — Due voci del registro erano ferme su «APERTA» dopo essere state chiuse

**Tipo:** docs
**File:** `docs/ISSUES.md`

**Perche':** [ISS-115](ISSUES.md#iss-115) portava in testa «Stato: APERTA» e
nel corpo «Risolta il 2026-09-01», e stava nella sezione «Aperti».
[ISS-105](ISSUES.md#iss-105) e' chiusa da [EXP-012](EXPERIMENTS.md#exp-012)
dal 20 agosto --- «misurata, nessun effetto» --- e stava anch'essa fra gli
aperti. Un registro dei difetti che elenca come aperto cio' che e' chiuso
smette di essere leggibile proprio nel punto in cui serve: quando si chiede
che cosa resta.

**Cosa cambia:** entrambe spostate in «Risolti» con data e intervento; a
ISS-105 e' stata aggiunta la tabella dell'ablation (22 / 28 / 36 / 44
campioni, tutti i $|t| < 1{,}3$) e la ragione per cui si chiude come
«misurata» e non come «corretta».

**Verificato con:** rilettura delle due sezioni; l'intestazione di ciascuna
voce ora dichiara «Trovata / Risolta» come tutte le altre in quella sezione.

## [2026-09-05] — La figura demografica di apertura del Capitolo 1

**Tipo:** feature
**File:** `pipeline/figura_popolazione.py` (nuovo),
`tesi/figure/fig_popolazione.png` (nuova), `tesi/figure/fig_popolazione.txt`

**Perche':** il Capitolo 1 apriva su un'immagine ripresa dal Rapporto annuale
ISTAT. Rifarla con il codice la rende coerente con le altre figure della tesi
e, soprattutto, rende esplicito da dove vengono i numeri.

**Cosa mostra:** popolazione italiana 0-14 contro 65 e piu', 2016-2026, in
migliaia. Le due curve si divaricano: gli over 65 passano da 13.330 a 14.830
(+11,3%), la fascia 0-14 da 8.220 a 6.860 (-16,5%).

**I numeri sono letti dal grafico ISTAT, non da una tabella**, con
un'accuratezza di circa +/- 30 mila unita'. Regge per la forma delle curve e
per i valori agli estremi; non regge per citare un singolo anno intermedio.
Per questo la didascalia dice «elaborazione su dati ISTAT» e non «Fonte:
ISTAT». I due elenchi in testa allo script sono l'unico punto da toccare se si
recupera la tabella.

**Controllo indipendente:** gli estremi digitalizzati danno +11,3% sugli over
65, che e' esattamente il valore gia' scritto nel testo del capitolo e ricavato
per altra via.

**Palette verificata, non scelta a occhio.** I sei controlli calcolabili
(OKLab, simulazione Machado-Oliveira-Fernandes 2009) sono stati eseguiti: i
colori di `figure_tesi.py` --- `#2B5D7D` e `#C4A55C` --- separano benissimo
(32,3 a vista normale, 28,4 nel caso peggiore fra protanopia e deuteranopia,
contro un obiettivo di 8) ma **non passano**: entrambi hanno croma sotto la
soglia di 0,10 e il sabbia ha contrasto 2,36:1 sul bianco, sotto il minimo di
3. Scuriti e saturati quanto basta: `#15618F` e `#A8842F` passano tutto
(croma 0,102 e 0,110; contrasto 6,69:1 e 3,50:1; separazione 26,2 / 22,2).

**Verificato con:** `python pipeline/figura_popolazione.py` -> PNG 2275x1306 a
300 dpi, sfondo bianco; immagine riaperta e ispezionata. Due difetti trovati e
corretti alla prima resa: le etichette dei valori di partenza sfondavano
sull'asse y (ora ancorate a destra del punto) e la legenda galleggiava nella
fascia vuota fra le due curve (ora in alto, come nell'originale).

**Collegamenti:** Capitolo 1, `fig:popolazione`

---

## [2026-09-04] — Preambolo LaTeX: un solo posto in cui il formato e' definito

**Tipo:** fix
**File:** `tesi/tesi.tex`

**Perche':** il preambolo fissava margini e interlinea due volte, e la seconda
dichiarazione annullava la prima senza segnalare nulla. I margini effettivi
erano 4,02 cm a sinistra contro 2,98 a destra --- asimmetria di 1 cm su un
documento `oneside` --- e l'interlinea 1,3 invece di 1,5.

**Cosa cambia:**

- formato definito solo da `geometry`; tolti `\oddsidemargin`,
  `\evensidemargin` (inerte con `oneside`), `\textheight`, `\topmargin`;
- interlinea con `setspace` e `\onehalfspacing`, equivalente all'interlinea
  1,5 di Word;
- `\usepackage[latin1]{inputenc}` rimosso: i `.tex` sono UTF-8, verificato
  byte per byte su tutti e undici i file;
- `\include{Conclusione}` -> `Conclusioni`, `bibliografia` -> `Bibliografia`,
  `\input frontespizio` -> `\input{Frontespizio}`: su Overleaf, che compila su
  Linux, i primi tre non trovavano il file;
- `\pagestyle{myheadings}` tolto dal corpo, dove annullava la configurazione
  `fancyhdr` del preambolo; sintassi `fancyhdr` portata alla versione corrente;
- `\clearpage` prima di `\addcontentsline` per bibliografia e ringraziamenti:
  senza, la voce in indice prendeva il numero della pagina precedente;
- aggiunti `hyperref` (101 `\ref` e 38 `\cite` nella tesi), `microtype`,
  `lmodern`, `caption`, `\listoffigures`, `\listoftables`;
- tolti `newlfont`, `epsfig`, `ifsym`, `soul`, `tikz`, `url`, `subfig`:
  nessuno usato in alcun capitolo, verificato con `grep`.

**Verificato con:** `grep`/`python` sul contenuto dei `.tex` per codifica,
nomi dei file e uso effettivo dei pacchetti -> tutti UTF-8, tre riferimenti
sbagliati confermati, sette pacchetti inutilizzati confermati. **La
compilazione non e' stata provata**: su questa macchina non c'e' una
distribuzione LaTeX. Il layout e' calcolato, non compilato.

**Collegamenti:** [ISS-132](ISSUES.md#iss-132)

---

## [2026-09-04] — Una caduta, quattro istanti, e le due grandezze a confronto

**Tipo:** feature
**File:** `pipeline/figura_striscia.py` (nuovo),
`tesi/figure/fig_striscia.png` (nuova),
`docs/TESTO_FIGURE_RAPPRESENTAZIONI.md`

**Perche':** la selezione con il DTW dice **quanto** una grandezza separa le
classi, non **come**. Le curve gia' prodotte in `risultati/dtw/curve/`
aggregano cinquanta cadute e mostrano la forma media; mancava il legame fra il
movimento e il segnale su una caduta sola.

**Cosa mostra:** quattro fotogrammi della stessa caduta con la posa stimata da
MediaPipe --- in piedi, in caduta, a terra, ferma --- e sotto, sullo stesso
asse dei tempi, due grandezze con gli istanti segnati. Il ritaglio dei quattro
fotogrammi e' **comune**: uno per fotogramma avrebbe seguito la persona e
mostrata sempre della stessa dimensione, facendo sparire proprio la caduta.

**Le due grandezze sono scelte per contrasto**, e sono l'argomento del
Capitolo 3: la velocita' del bacino, che e' una derivata istantanea, e la
discesa del bacino, che e' un integrale su finestra mobile. La figura mostra
tre cose che il testo afferma separatamente:

1. **La derivata da' un picco spurio a 1,45 s**, mentre la persona sta ancora
   camminando --- il falso positivo che le derivate regalano.
2. **L'integrale sale con continuita'** e raggiunge il massimo alla
   transizione, senza picchi isolati.
3. **La derivata torna a zero appena il corpo si ferma; l'integrale resta
   alto** per tutto il tempo in cui la persona e' a terra, e scende solo
   quando la finestra mobile esce dall'evento.

**Il terzo punto e' quello che non mi aspettavo di vedere cosi' chiaro.**
L'argomento del capitolo e' che gli integrali sono meno rumorosi; la figura
mostra che hanno anche **memoria**. E' la ragione per cui il compito «stato» e
il compito «evento» si comportano in modo diverso, e per cui gli integrali
aiutano sul campo dove il positivo dura.

**Verificato con:**
`fall_processing/python.exe pipeline/figura_striscia.py` -> transizione
individuata al fotogramma 32, istanti 18 / 29 / 38 / 54, angolo del tronco da
$-97°$ a $-185°$; figura ispezionata a video.

---

## [2026-09-03] — La soglia oracolo, e una scomposizione che veniva da un altro esperimento

**Tipo:** fix
**File:** `tesi/Cap4.tex`, `tesi/Conclusioni.tex`,
`docs/RISPOSTE_AL_RELATORE.md`, `docs/spiegazioni/06_CONCLUSIONI.md`

**Perche':** il valore $0{,}612$ della soglia oracolo era rimasto fra gli
orfani dell'audit ([ISS-126](ISSUES.md#iss-126)) e non era stato chiuso.
Rintracciandolo si e' visto che non e' un numero isolato ma la punta di una
scomposizione intera presa dall'impianto precedente
([ISS-131](ISSUES.md#iss-131)).

**Cosa cambia:** $0{,}612 \to 0{,}492$; «due terzi taratura, un terzo perdita»
$\to$ **49% e 51%**; nel Capitolo 4 la scomposizione e' ora scritta per esteso
con tutti e tre i termini, ricalcolabile da `pr_auc_allineato.json`.

**La ragione per cui vale la pena averlo trovato** non e' la seconda cifra
decimale. «Due terzi taratura» dice che il crollo e' soprattutto un problema di
scala e si correggerebbe ritarando; «meta' e meta'» dice che c'e' tanta perdita
reale quanta taratura. Sono due conclusioni diverse, e la seconda e' quella
coerente con la PR-AUC che il capitolo gia' riportava --- $1{,}79$ volte il
caso contro $18{,}7$ in dominio. **Il capitolo si contraddiceva a due pagine di
distanza**, e la contraddizione non era visibile senza risalire ai file.

**Il difetto era doppio**: l'esperimento vecchio usava come riferimento in
dominio proprio quel $0{,}872$ che [ISS-129](ISSUES.md#iss-129) ha mostrato
appartenere a un altro modello. Due difetti indipendenti si erano composti nel
medesimo paragrafo.

**Verificato con:** `python _oracolo.py` -> i due esperimenti confrontati riga
per riga; `python tesi/controlla.py` -> «Nessun problema».

**Collegamenti:** [ISS-131](ISSUES.md#iss-131), [ISS-129](ISSUES.md#iss-129)

---

## [2026-09-02] — La figura delle rappresentazioni: fotogramma vero, e senza testo

**Tipo:** feature
**File:** `pipeline/figura_rappresentazioni.py`, `tesi/Cap3.tex`,
`tesi/figure/fig_rappresentazioni.png`

**Cosa cambia**, rispetto alla versione della mattina:

| | |
|---|---|
| ripresa | dalla caduta in avanti alla **caduta laterale** (`act04`) |
| fotogramma | il **#20**, scelto a occhio dal foglio a contatto |
| testo | **tolto dalla figura**: niente titoli, valori o note. Si scrivono in LaTeX |
| dimensione | pannelli piu' larghi, senza titoli occupano tutta la riga |
| ritaglio | la finestra **trasla** invece di troncare ai bordi |

**Perche' la caduta laterale.** Quella in avanti sulle mani passa da eretta ad
accasciata in pochi fotogrammi: o il corpo e' verticale, e le tre costruzioni
degenerano in tre segmenti paralleli, o e' gia' a terra con i landmark
accavallati. La caduta laterale attraversa l'inquadratura --- che e' anche la
geometria prescritta dal protocollo di ripresa --- e ha una transizione
leggibile.

**Perche' il fotogramma e' fissato e non scelto da un criterio.** Il criterio
automatico e' la massima inclinazione del tronco, e su ogni ripresa restituisce
la persona **gia' distesa**: l'istante piu' estremo non e' quello piu'
leggibile. E' scelto guardando il foglio a contatto (`--provini`, aggiunto) e
scritto nel codice con la ragione accanto.

**Il difetto del ritaglio.** La finestra veniva centrata sul soggetto e poi
troncata ai bordi dell'immagine: con la persona in basso il margine inferiore
spariva e **i piedi finivano sul taglio**. Ora la finestra mantiene le
dimensioni e trasla rientrando nell'immagine.

**Con `--con-valori`** si riottiene la versione annotata, che serve a
controllare a schermo che i numeri disegnati siano quelli del motore.

**Verificato con:**
`fall_processing/python.exe pipeline/figura_rappresentazioni.py` -> fotogramma
#20, inclinazione dell'ellisse 51,3°, angolo del tronco A2 48,9° e A3
$-111{,}9$°; figura ispezionata a video a ogni passaggio;
`python tesi/controlla.py` -> «Nessun problema».

---

## [2026-09-02] — La figura delle rappresentazioni su un fotogramma vero

**Tipo:** feature, fix
**File:** `pipeline/figura_rappresentazioni.py` (nuovo),
`pipeline/figure_tesi.py`, `tesi/Cap3.tex`,
`tesi/figure/fig_rappresentazioni.png`

**Perche':** la prima versione della figura usava un corpo sintetico. Di una
costruzione geometrica interessa se regge sui dati veri: uno scheletro
sintetico e' sempre pulito, e non mostra ne' i punti che lo stimatore sbaglia
ne' quanto l'ellisse sia davvero allungata su una persona che cade.

**Cosa cambia:** lo script prende una ripresa di UP-Fall, la elabora **in
sequenza** con MediaPipe --- lo stimatore e' un tracciatore, e su
un'immagine isolata non da' la stessa uscita --- sceglie l'istante di massima
inclinazione del tronco e vi disegna sopra le tre costruzioni. Il ritaglio si
calcola dal riquadro dei landmark: senza, la figura mostrava la stanza e la
persona occupava un ventesimo dell'inquadratura.

**I numeri stampati sono quelli del motore geometrico**, non ricalcolati per la
figura: se `geometry.py` cambia, cambia la figura.

**Un difetto trovato mentre si scriveva, e chiuso subito.** Per un momento
**due funzioni scrivevano lo stesso file**: la sintetica in `figure_tesi.py` e
quella vera nello script nuovo. Chi eseguiva `figure_tesi.py` per ultimo
sostituiva la figura vera con lo schema **senza alcun errore**. La sintetica e'
stata rimossa, e la docstring di `figure_tesi.py` dichiara ora che quella
figura non sta li' e perche' --- richiede MediaPipe, quindi un altro ambiente.

**Il risultato che la figura ha reso visibile.** Sullo stesso fotogramma A2
riporta un angolo del tronco di $31{,}9^\circ$ e A3 di $-114{,}0^\circ$. Non
e' una discordanza: A3 misura nel piano immagine, A2 nel riferimento dei world
landmark, che e' centrato sulle anche e non allineato alla gravita'. **Ottanta
gradi di differenza sullo stesso tronco**, ed e' la dimostrazione piu' diretta
che l'angolo di A2 non e' un'inclinazione rispetto al pavimento --- cosa che il
capitolo affermava e che ora si vede. Nel testo e' stato aggiunto il paragrafo
che lo spiega, insieme al motivo per cui i nomi portano il prefisso della
rappresentazione.

**Verificato con:**
`fall_processing/python.exe pipeline/figura_rappresentazioni.py` -> 70
fotogrammi, 70 con posa, scelto il #69; `python pipeline/figure_tesi.py` ->
tredici figure, e `fig_rappresentazioni.png` **non** sovrascritta;
`python tesi/controlla.py` -> «Nessun problema».

**Collegamenti:** [ISS-127](ISSUES.md#iss-127), [ISS-112](ISSUES.md#iss-112)

---

## [2026-09-02] — Le tre rappresentazioni geometriche, mostrate invece che descritte

**Tipo:** feature
**File:** `pipeline/figure_tesi.py` (`fig_rappresentazioni`), `tesi/Cap3.tex`,
`tesi/figure/fig_rappresentazioni.png` (nuova)

**Perche':** il Capitolo 3 descriveva tre costruzioni geometriche --- un'ellisse
adattata a una nuvola di punti, un vettore del tronco nello spazio, un
riferimento centrato sul bacino --- in tre pagine di prosa e **non ne mostrava
nessuna**. Sono le costruzioni da cui viene ogni grandezza del lavoro.

**Cosa cambia:** tre pannelli sullo stesso corpo inclinato di 30 gradi. In
grigio i landmark disponibili, in nero quelli che ciascuna rappresentazione
impiega: 7, 5, 9. A1 con l'ellisse e i due assi, A2 con il vettore del tronco e
l'origine sulle anche, A3 con la lunghezza del tronco come normalizzatore e le
tre altezze relative.

**L'ellisse di A1 non e' disegnata: e' calcolata**, dagli autovettori della
covarianza dei sette punti che A1 impiega, con la stessa procedura di
`geometry.py`. Disegnare una costruzione geometrica con numeri finti sarebbe
un'illustrazione; con i numeri veri e' una verifica --- e infatti l'angolo che
ne esce, **120 gradi su un corpo inclinato di 30**, illustra da solo la
questione della periodicita' che il capitolo discute piu' avanti: 120 e $-$60
sono lo stesso asse.

**Nel testo** e' stato aggiunto il paragrafo che dice che cosa distingue le tre
rappresentazioni, e non e' il numero di punti: A1 non sa che quei punti sono un
corpo, A2 sa che esiste un tronco, A3 sa che il corpo ha una taglia. Da li'
discende il modo diverso in cui degradano.

**Verificato con:** `python pipeline/figure_tesi.py` -> quattordici figure;
l'immagine ispezionata a video quattro volte, correggendo la sovrapposizione
delle etichette con il titolo, le tre quote di A3 che si accavallavano e gli
apostrofi al posto degli accenti; `python tesi/controlla.py` ->
«Nessun problema».

**Collegamenti:** [ISS-127](ISSUES.md#iss-127)

---

## [2026-09-02] — Lo schema del posizionamento, e una disposizione che violava il protocollo

**Tipo:** feature
**File:** `pipeline/figure_tesi.py` (`fig_stanza`), `tesi/Cap5.tex`,
`tesi/figure/fig_stanza.png` (nuova)

**Perche':** il protocollo di ripresa e' la parte del lavoro che un lettore
vorrebbe ripetere, ed era descritto solo a parole. E' anche la ragione per cui
sei sessioni su dodici sono state scartate, quindi vale la pena mostrarlo.

**Cosa cambia:** pianta e alzato con la telecamera, il cono del campo visivo
ritagliato sulle pareti, il divano, l'area di caduta con il lato lungo
perpendicolare all'asse ottico, la finestra alle spalle, e le quote --- 3-4 m
di distanza, 1,2-1,5 m di altezza. Nel testo, le tre prescrizioni che ne
discendono sono ora enunciate una per una invece di essere disperse.

**E' un'eccezione alla regola del modulo, ed e' dichiarata nella docstring.**
Tutte le altre figure leggono `risultati/`; questa non ha numeri da leggere: la
sua sorgente e' il protocollo, e viene stampata in coda come per le altre.

**Il ritrovamento, che vale piu' della figura.** La prima disposizione tracciata
**violava il protocollo che doveva illustrare**: con la telecamera a 2,15 m dal
muro corto e un obiettivo da 62 gradi, il bordo inferiore del campo visivo
tagliava il divano, e il protocollo chiede che una persona distesa sul divano
sia inquadrata per intero. Le posizioni sono state corrette finche' entrambi
--- divano e area di caduta --- non sono entrati nel cono.

Disegnare una prescrizione e' un modo di verificarla: a parole «divano e area
libera nell'inquadratura» si legge senza attrito, in pianta o ci stanno o non
ci stanno.

**Verificato con:** `python pipeline/figure_tesi.py` -> tredici figure;
l'immagine ispezionata a video tre volte, correggendo il ritaglio del cono,
la resa dei trattini e le sovrapposizioni delle etichette;
`python tesi/controlla.py` -> «Nessun problema».

**Collegamenti:** [ISS-127](ISSUES.md#iss-127)

---

## [2026-09-01] — La figura che mostra la differenza fra finestre ed eventi

**Tipo:** feature, fix
**File:** `pipeline/figure_tesi.py` (`fig_sessione`), `tesi/Cap5.tex`,
`tesi/figure/fig_sessione.png` (nuova)

**Perche':** il rapporto fra finestre sopra soglia ed eventi --- 47,8 --- e' il
numero che distingue un dato riportabile da uno che sovrastima di due ordini di
grandezza, e nel testo era \emph{soltanto} un numero. La figura lo rende
visibile: le raffiche sono raggruppate a occhio, e gli allarmi che ne escono
sono pochi triangoli.

**Cosa cambia:** sei ore della prima sessione domestica, punteggio per finestra,
soglia, finestre sopra soglia e allarmi emessi ricalcolando la regola dai
punteggi --- non leggendo `eventi.csv`, che contiene finestre. **208 finestre,
14 allarmi.**

**Il rapporto in questa sessione vale 14,9 e non 47,8**, ed e' detto nel testo:
il fattore dipende dalla lunghezza delle raffiche, quindi dalla sessione, e il
47,8 e' l'aggregato su tutte le registrazioni. E' un argomento in piu' per non
riportare mai le finestre come eventi --- sovrastimano di una quantita' che
cambia da una registrazione all'altra.

**Il ritrovamento.** Tracciando i punteggi e' comparso un buco di
**sessantotto minuti** che nessun riepilogo dichiarava
([ISS-130](ISSUES.md#iss-130)). E' la sospensione automatica gia' raccontata
nel capitolo, ma con due precisazioni nuove: il valore corretto e' 68 minuti e
non «un'ora e nove», ed e' ora ricalcolabile dagli istanti; e **il registratore
la dichiarava come uno stallo di venti secondi**, perche' contava il tempo in
cui il programma era attivo. Il testo lo dice ora, ed e' la giustificazione
concreta del doppio orologio introdotto il 26 agosto.

**Verificato con:** `python pipeline/figure_tesi.py` -> dodici figure;
`python tesi/controlla.py` -> «Nessun problema», 38.305 parole; l'immagine
ispezionata a video; l'interruzione ricalcolata dagli istanti di
`punteggi.csv` (16:03:30 -> 17:11:12) e confrontata con il `riepilogo.json`.

**Collegamenti:** [ISS-130](ISSUES.md#iss-130), [ISS-113](ISSUES.md#iss-113)

---

## [2026-09-01] — Capitolo 5: diciassette tabelle, e la latenza entra nel testo

**Tipo:** feature, fix, docs
**File:** `tesi/Cap5.tex`,
`risultati/cinque_soggetti/scansione_k_cinque_soggetti.json` (nuovo)

**Perche':** il Capitolo 5 e' quello con piu' dati tabellari della tesi e
**non aveva una sola tabella numerata** ([ISS-127](ISSUES.md#iss-127)); e la
scomposizione della latenza, misurata il 26 agosto, non compariva in alcun
capitolo ([ISS-115](ISSUES.md#iss-115)) pur essendo una delle quattro metriche
operative chieste dal relatore.

**Cosa cambia:**

| | |
|---|---|
| tabelle | **17 su 17** numerate, con etichetta e didascalia. Le didascalie dichiarano la provenienza dove non e' ovvia: cinque soggetti contro dieci, banco contro esercizio |
| `sec:latenza` | sezione nuova con `tab:latenza`: 0,038 s di calcolo, **2,743 s di riempimento della finestra**, 0,997 s di persistenza, limite inferiore **3,778 s** |
| artefatti | scansione di $K$ e confronto fra stimatori consolidati da `DIP_PROJECT` |

**La sezione sulla latenza dice per prima cosa cio' che non si puo' dire.** Il
ritardo fra caduta e allarme **non e' misurabile** con annotazione al minuto:
la prima finestra sopra soglia cade a +11,8, +19,4, +27,7 e +32,3 secondi dal
minuto annotato, e quegli scarti non sono ritardi del sistema ma il punto del
minuto in cui la persona e' caduta.

**Il risultato che la sezione porta** e' il complemento esatto del bilancio
computazionale: la' il collo di bottiglia era la percezione e il classificatore
valeva il 5,8%; qui il collo di bottiglia e' la finestra di decisione ---
2,74 s contro 38 ms, un fattore settantatre --- e il calcolo vale l'1,0%.
**In entrambi i bilanci il classificatore e' il termine che non conta.**
Con il conto che ne segue: un dispositivo dieci volte piu' veloce sposterebbe
il limite inferiore dell'uno per cento.

**Due righe restano non verificate**, ed e' registrato in
[ISS-126](ISSUES.md#iss-126): la riga $K = 9$ della scansione e la riga
«MediaPipe @ 18 fps» delle catene non corrispondono ad alcuna run trovata nel
progetto storico. Le altre quindici righe delle due tabelle corrispondono alla
terza cifra.

**Verificato con:** `python _estrai_k.py` in `DIP_PROJECT` -> scansione di $K$
(0,859 / 0,928 / 0,963 / 0,980 / 0,987) e stimatori (0,909 / 0,682 / 0,857)
coincidenti con le tabelle; `python tesi/controlla.py` -> «Nessun problema»,
37.911 parole; `python pipeline/inventario_figure.py` -> Cap. 5 a 17 tabelle
su 17 ambienti.

**Collegamenti:** [ISS-115](ISSUES.md#iss-115), [ISS-127](ISSUES.md#iss-127),
[ISS-126](ISSUES.md#iss-126), [EXP-017](EXPERIMENTS.md#exp-017)

---

## [2026-09-01] — Capitolo 4: la sesta architettura entra nel testo, e quindici tabelle

**Tipo:** fix, docs
**File:** `tesi/Cap4.tex`, `tesi/Cap5.tex`, `tesi/Conclusioni.tex`,
`tesi/Introduzione.tex`, `pipeline/figure_tesi.py`,
`tesi/figure/fig_architetture.png`

**Perche':** [ISS-122](ISSUES.md#iss-122) aveva corretto il Capitolo 2, che
dichiarava di non aver provato le reti a grafo. **Il Capitolo 4 era rimasto a
cinque architetture**: la tabella, la scansione di numerosita', la figura e le
quattro affermazioni che citano l'intervallo fra la migliore e la peggiore.
Correggere il capitolo che *dichiara* senza correggere quello che *misura*
lascia il lavoro in contraddizione con il proprio registro.

**Cosa cambia:**

| | |
|---|---|
| `tab:architetture` | sesta riga: grafo, $0{,}779 \pm 0{,}122$, 12.323 parametri --- il modello con meno parametri dei sei |
| l'intervallo | **0,066 -> 0,079**, allineato in Cap. 4, Cap. 5, Conclusioni e Introduzione |
| `tab:numerosita` | riga «GRU contro grafo», $t = -2{,}37$, 16 soggetti |
| `fig_architetture.png` | rigenerata a sei architetture; il titolo passa da «nessuna e' distinguibile» a «nessuna fa meglio della GRU» |
| l'enunciato | da «nessuna coppia e' distinguibile» a «nessuna fa meglio della GRU, e la sola che si avvicina fa peggio», con la molteplicita' dichiarata |

**La sostanza non si muove.** 0,079 resta dentro la dispersione fra soggetti
(0,08--0,12), e il divario fra due punti di vista --- 0,422 dopo
[ISS-129](ISSUES.md#iss-129) --- resta oltre cinque volte tanto. L'enunciato
nuovo e' anche piu' solido del vecchio, perche' «nessuna e' distinguibile» era
una frase che un sesto confronto poteva rompere.

**Le tabelle.** I quindici `tabular` del capitolo erano tabelle numerate in
**due** casi ([ISS-127](ISSUES.md#iss-127)). Ora sono **quindici su quindici**:
distribuzione delle etichette, composizione dei fold, sei regole di soglia,
effetto congiunto delle correzioni, escursione per punto di vista,
trasferimento fra viste, le due tabelle delle rappresentazioni, architetture,
numerosita', dimensione della foresta, frame rate, occlusioni, compiti,
trasferimento esterno. Tre hanno ricevuto anche il richiamo nel testo.

**Verificato con:** `python pipeline/figure_tesi.py` -> undici figure, quella
delle architetture ora legge sei file di run; `python tesi/controlla.py` ->
«Nessun problema»; `python pipeline/inventario_figure.py` -> Cap. 4 a 15
tabelle su 15 ambienti.

**Collegamenti:** [ISS-122](ISSUES.md#iss-122), [ISS-127](ISSUES.md#iss-127),
[ISS-129](ISSUES.md#iss-129), [EXP-018](EXPERIMENTS.md#exp-018)

---

## [2026-09-01] — Il numero piu' citato della tesi confrontava due modelli diversi

**Tipo:** fix
**File:** `tesi/Cap4.tex`, `tesi/Cap5.tex`, `tesi/Conclusioni.tex`,
`tesi/Introduzione.tex`, `docs/spiegazioni/*.md`,
`risultati/cinque_soggetti/viste_cinque_soggetti.json` (nuovo)

**Perche':** cercando l'artefatto dei numeri orfani del Capitolo 4
([ISS-126](ISSUES.md#iss-126)) e' emerso che la prima riga della tabella del
punto di vista non appartiene alla foresta con cui sono calcolate le altre due
([ISS-129](ISSUES.md#iss-129)).

**Cosa cambia:** `0{,}872 \pm 0{,}099` diventa `0{,}857 \pm 0{,}088`, e con
essa il divario fra le viste (**0,438 -> 0,422**), il recupero addestrando su
due viste (**56% -> 58%**), il divario residuo (**0,194 -> 0,178**) e il
rapporto con l'intervallo fra le architetture (**quasi sette -> piu' di sei
volte**). Venti sostituzioni in sei file, perche' quel numero e' il metro di
tutto il lavoro.

**La conclusione non si muove, si rafforza:** 0,422 resta oltre sei volte
l'intervallo entro cui cadono le sei architetture, e le due righe da cui viene
il risultato sul recupero erano gia' esatte alla quarta cifra.

**Il dettaglio che vale la pena ricordare:** il numero giusto era gia' nel
testo. Due paragrafi sopra la tabella, il capitolo scriveva «l'F2 passa da 0,29
a 0,857». La contraddizione stava in mezza pagina, e nessuna rilettura l'aveva
vista --- perche' rileggere non e' ricalcolare.

**Verificato con:** i tre `run_metadata.json` dell'impianto a cinque soggetti
riletti alla sorgente; i falsi positivi ricavati (57 / 1.113 / 460)
corrispondono ai due valori gia' presenti nel testo, il che conferma che le
righe due e tre erano quelle giuste; `python tesi/controlla.py` ->
«Nessun problema».

**Collegamenti:** [ISS-129](ISSUES.md#iss-129), [ISS-126](ISSUES.md#iss-126)

---

## [2026-09-01] — Capitolo 3: le tabelle descrittive ricalcolate alla sorgente

**Tipo:** fix, feature
**File:** `pipeline/statistiche_cap3.py` (nuovo), `tesi/Cap3.tex`,
`tesi/Cap5.tex`, `tesi/Conclusioni.tex`,
`risultati/laboratorio/statistiche_cap3.json` (nuovo)

**Perche':** l'audit ([ISS-126](ISSUES.md#iss-126)) ha mostrato che le tre
tabelle descrittive del Capitolo 3 non avevano un file che le producesse. Erano
state calcolate una volta e trascritte.

**Cosa cambia:** lo script le ricalcola tutte e tre da `feature_v2.csv` con le
definizioni dichiarate nella docstring, e le salva con la provenienza.
**Una si riproduce, due no** ([ISS-128](ISSUES.md#iss-128)): l'autocorrelazione
e il rapporto fra le mediane venivano dall'impianto precedente, e la prova sta
dentro la tabella --- elencava «Energia del corpo», una grandezza che nel
feature set attuale non esiste piu'.

Le tre tabelle sono state rifatte, insieme ai due punti del Cap. 5 e delle
Conclusioni che citavano lo stesso intervallo. **Le conclusioni non si
muovono**: i due intervalli di autocorrelazione ora non si sovrappongono
nemmeno, e la separazione fra transizione e stato resta di uno o due ordini di
grandezza.

**Nella stessa passata**, i due `tabular` inline del capitolo --- gli stimatori
di posa e i sottoinsiemi di landmark --- sono diventati tabelle vere con
didascalia, etichetta e richiamo nel testo. Il Cap. 3 passa da 6 a 8 tabelle
numerate su 8 ambienti: e' l'unico dei tre capitoli sperimentali a essere
completo ([ISS-127](ISSUES.md#iss-127)).

**Verificato con:** `python pipeline/statistiche_cap3.py` eseguito sui 57.786
fotogrammi della camera 1; `python pipeline/audit_numeri.py` -> gli orfani del
Cap. 3 scendono da 28 a quelli residui elencati nella issue;
`python tesi/controlla.py` -> «Nessun problema».

**Collegamenti:** [ISS-128](ISSUES.md#iss-128), [ISS-126](ISSUES.md#iss-126),
[ISS-127](ISSUES.md#iss-127), [ISS-118](ISSUES.md#iss-118)

---

## [2026-09-01] — Cinque interventi sul codice: le prove, le verifiche di avvio, la provenienza

**Tipo:** feature, fix
**File:** `prove/` (nuova), `src/provenienza.py` (nuovo),
`deploy_board/rileva.py`, `deploy_board/metadata.json`,
`pipeline/esporta_board.py`, `pipeline/latenza.py`,
`pipeline/costo_classificatori.py`, `pipeline/confronto_appaiato.py`,
`pipeline/addestra.py`

**Perche':** tre difetti strutturali, nessuno dei quali produce un errore.
Su settemila righe non esisteva **una** prova automatica; il riepilogo della
board si scriveva **solo alla fine**, quindi una prova di dodici ore
interrotta all'undicesima non lasciava alcun bilancio; e i file di risultato
**non dicono da quale codice vengono**, che e' la causa prima di
[ISS-113](ISSUES.md#iss-113).

**Cosa cambia:**

| | |
|---|---|
| `prove/` | **31 prove** in due secondi, solo `unittest`: motore geometrico a file d'oro, regola K-su-M, aggregazione in eventi |
| `src/provenienza.py` | ogni JSON di risultato porta commit, stato dell'albero, data, comando e versioni. Scrittura **atomica** |
| `rileva.py`, riepilogo | riscritto ogni 300 s con un campo `parziale`; scrittura atomica; scritto **anche su interruzione** |
| `rileva.py`, verifiche | tre all'avvio: impronta di `geometry.py`, parita' sulle finestre, parita' **sui fotogrammi** |
| `metadata.json` | `sha256_geometry` e il blocco `parita_fotogrammi` |

**L'intervento che vale piu' degli altri e' la terza verifica.** `geometry.py`
esiste in due copie, `src/` e `deploy_board/`, allineate a mano: oggi
coincidono (`1df79ebe...`), e il giorno in cui divergeranno la board calcolera'
grandezze diverse **senza sollevare alcun errore**. L'impronta e' ora nei
metadati e `rileva.py` si rifiuta di partire se non corrisponde.

**La verifica sui fotogrammi non e' bloccante, e la ragione va detta.** Quella
sulle finestre e' passata con scarto esattamente zero mentre le due macchine
davano decisioni diverse su una caduta vera ([ISS-106](ISSUES.md#iss-106)): e'
la verifica cieca. Quella sui fotogrammi la chiude, ma richiede MediaPipe e una
clip di riferimento, e **una prova di dodici ore non deve fermarsi perche' un
file di controllo non e' stato copiato**. Se manca, viene dichiarata non
eseguita nel riepilogo, dove resta leggibile.

**Un difetto introdotto e corretto nella stessa sessione**, che vale la pena
registrare: lo script di migrazione ha inserito
`from src.provenienza import scrivi_json` in **testa** a `latenza.py`, che e'
standalone e non tocca `sys.path`. Il file **compilava** e sarebbe esploso alla
prima esecuzione. E' lo stesso genere di difetto che le prove servono a
prendere: `py_compile` non lo vede, eseguire lo script si'.

**Verificato con:** `python prove/esegui.py` -> 31 prove, OK in 0,3 s;
`python -m py_compile` sui sette file toccati -> nessun errore;
`python pipeline/latenza.py` eseguito davvero -> JSON riscritto con la chiave
`_provenienza` (commit `34ece3b9`, `albero_pulito: false`).
**Non verificato sulla board:** le tre verifiche di avvio e il riepilogo
periodico sono stati provati solo sul calcolatore. Il primo giro sulla board
e' la prova di durata stessa.

**Collegamenti:** [ISS-113](ISSUES.md#iss-113), [ISS-106](ISSUES.md#iss-106),
[ISS-125](ISSUES.md#iss-125)

---

## [2026-08-31] — Il documento per il relatore, riscritto sulla struttura vera

**Tipo:** docs
**File:** `docs/INDICE_E_STRUTTURA.txt` (riscritto integralmente)

**Perche':** il documento era del 26 agosto e **proponeva** una struttura che poi
non e' stata applicata --- proponeva di fondere contesto e stato dell'arte, e
quella fusione non si e' fatta. Il 27 agosto gli era stata messa in testa una
toppa che avvertiva «leggere prima del resto», ma sotto la toppa restavano
l'indice a otto capitoli, i capitoli sperimentali numerati 3-4-5 secondo la
proposta, e una domanda su una fusione che non si fa piu'. Era il documento che
il relatore avrebbe letto per primo al rientro, il **2 settembre**.

**Cosa cambia:** l'indice e' quello **applicato** --- cinque capitoli, 35.491
parole, con le sezioni prese da `tesi/*.tex` e non da una proposta. I capitoli
sperimentali sono il 4 e il 5, e il 5 e' presentato nei suoi due blocchi
(5.1--5.4 dispositivo, 5.5--5.9 ambiente reale) con la ragione per cui restano
nello stesso capitolo. La parte 2 riporta per ogni sezione **la tesi che
sostiene, non il suo contenuto**, che era il criterio chiesto.

**Tre aggiunte rispetto alla versione del 26:**

1. **La rete a grafo** ([EXP-018](EXPERIMENTS.md#exp-018)) entra nella parte 4,
   con la dichiarazione di che cosa e' stato provato --- nodi le grandezze, non
   i giunti --- e la riformulazione della frase sulle architetture. E' anche la
   prima delle tre domande finali, perche' tocca un'affermazione portante.
2. **Il costo per finestra** ([EXP-019](EXPERIMENTS.md#exp-019)), che risponde
   alla domanda decidibile con dieci soggetti dove quella di accuratezza non lo
   e', e che obbliga a dire per esteso perche' e' stata scelta la foresta.
3. **Le due correzioni alle fonti** ([ISS-123](ISSUES.md#iss-123),
   [ISS-124](ISSUES.md#iss-124)), dichiarate nella parte 5. Un numero ritirato e
   cinque rifatti sono un'informazione che il relatore deve avere prima di
   leggere il Capitolo 1, non dopo.

**La verifica sulla latenza e' stata riscritta.** Nella versione del 26 diceva
«la calcolo prima di chiudere il capitolo». La misura e' stata fatta
([EXP-017](EXPERIMENTS.md#exp-017)) e dice che nella forma richiesta **non e'
misurabile**: il documento riporta ora la scomposizione e dichiara che i numeri
non sono ancora nel testo ([ISS-115](ISSUES.md#iss-115)).

**Verificato con:** `python _superato/correzioni_2026-08-31/_struttura.py` --- le sezioni dell'indice estratte
dai sorgenti `.tex`, non trascritte; i conteggi di parole da
`python tesi/controlla.py` (35.491); i numeri della parte 3 riletti contro
`risultati/campo/pr_auc_allineato.json`,
`risultati/campo/valutazione_incrociata_10sog.json`,
`risultati/occlusioni/foresta_DTW.json` e `risultati/campo/latenza.json`.
**Non inviato:** il documento e' pronto, la consegna e' una decisione della
candidata.

**Collegamenti:** [ISS-107](ISSUES.md#iss-107), [ISS-115](ISSUES.md#iss-115),
[EXP-018](EXPERIMENTS.md#exp-018), [EXP-019](EXPERIMENTS.md#exp-019)

---

## [2026-08-31] — Capitolo 1: le fonti verificate, e cinque numeri che non tornavano

**Tipo:** fix, docs
**File:** `tesi/Cap1.tex`, `tesi/Bibliografia.tex`

**Perche':** il capitolo che fissa il contesto clinico poggia interamente su
fonti esterne, ed era il capitolo con la quota piu' alta di riferimenti mai
controllati. Due voci portavano un avviso esplicito — «DA CONFERMARE», «DA
VERIFICARE» — che non era mai stato sciolto.

**Cosa cambia:**

| | |
|---|---|
| [ISS-123](ISSUES.md#iss-123) | cinque valori PASSI d'Argento su sette erano del biennio precedente, e il «60% delle cadute in casa» non corrisponde ad alcuna edizione |
| [ISS-124](ISSUES.md#iss-124) | la voce `kangas` fondeva due lavori diversi, e attribuiva a uno di essi un numero che sulla fonte non c'e' |
| voce nuova `fleming` | il *long lie* era l'unica affermazione clinica del capitolo senza riferimento |
| tre ripetizioni tolte | l'argomento sull'edge, l'elenco «precision e recall non bastano» e il requisito sui falsi allarmi comparivano due volte ciascuno |

**L'intervento che cambia la sostanza, e non la forma**, e' il ritiro di «tasso
ridotto a 0,025 dopo revisione dell'algoritmo». Non e' un riferimento
inventato: il lavoro di Kangas esiste, e il valore di 0,049 allarmi/ora e'
suo. E' l'affermazione sulla riduzione a non risultare dalla fonte, ed e'
proprio quella che il capitolo usava per sostenere che intervenire
sull'algoritmo abbassa il carico di allarmi. Al suo posto c'e' ora AIDE-MOI,
dove la riduzione e' documentata con entrambi i valori — 0,43 e 0,17 per
settimana e per soggetto — e con la sensibilita' che sale dal 27,3% all'80,0%
nello stesso passaggio.

**Sulla struttura**, il capitolo mantiene le quattro sezioni e aggiunge in
apertura un paragrafo che dichiara che cosa ciascuna sostiene. Le tre
ripetizioni tolte erano tutte dello stesso tipo: un argomento enunciato dove
serviva e poi ripetuto per intero due paragrafi dopo. Il rimando alla
Sezione~`sec:prevalenza` sostituisce la seconda occorrenza dell'argomento sui
falsi allarmi.

**Verificato con:** `python tesi/controlla.py` -> «Nessun problema», Cap. 1 a
2.861 parole con 4 sezioni e 4 sottosezioni (~400 parole per titolo d'indice);
le fonti riesaminate una per una — comunicato ISS del 31-10-2025, Rapporto
annuale ISTAT 2026, Gerontology 61:61--68 (DOI 10.1159/000362720), Sensors
19(6):1357, BMJ 337:a2227 (DOI 10.1136/bmj.a2227). **Nessun compilatore LaTeX
su questa macchina:** il controllo e' statico, il PDF non e' stato prodotto.

**Collegamenti:** [ISS-123](ISSUES.md#iss-123), [ISS-124](ISSUES.md#iss-124),
[ISS-110](ISSUES.md#iss-110)

---

## [2026-08-31] — La sessione del 27 agosto entra nel registro, e la frase che cambia

**Tipo:** docs, fix
**File:** `docs/EXPERIMENTS.md` (EXP-018, EXP-019, nota su EXP-011),
`docs/ISSUES.md` (ISS-122), `tesi/Cap2.tex`,
`docs/spiegazioni/00_PANORAMICA.md`

**Perche':** la sessione del 27 agosto si e' interrotta alle 18:02 dopo aver
prodotto tre risultati e **nessuna voce di registro**: la rete a grafo in
`src/modelli.py`, la sua run LOSO, e i due script nuovi
`pipeline/confronto_appaiato.py` e `pipeline/costo_classificatori.py`. Nel
frattempo il Capitolo 2 continuava a dichiarare che le reti a grafo non erano
state provate.

**Cosa cambia:**

| | |
|---|---|
| [EXP-018](EXPERIMENTS.md#exp-018) | la rete a grafo come sesta architettura: F2 0,779 ±0,122, 12.323 parametri, $t = -2{,}37$ contro la GRU |
| [EXP-019](EXPERIMENTS.md#exp-019) | costo per finestra delle sei architetture, 300 ripetizioni sul calcolatore |
| [ISS-122](ISSUES.md#iss-122) | il Capitolo 2 dichiarava di non aver provato la famiglia. Corretti i due punti |
| nota su [EXP-011](EXPERIMENTS.md#exp-011) | «nessuna architettura e' distinguibile dalla GRU» diventa «nessuna fa meglio, e la sola che si avvicina a essere distinguibile fa peggio» |

**I due risultati che vale la pena rileggere.**

Il primo: il grafo e' **il primo confronto fra architetture che supera la
soglia critica** di 2,26, e lo supera **nel verso sbagliato**. Non sopravvive
alla correzione per molteplicita' --- cinque confronti contro lo stesso
riferimento richiedono $|t| > 3{,}25$ --- quindi va riportato come indicativo.
La tesi centrale del lavoro non ne esce indebolita: ne esce detta meglio,
perche' «nessuna e' distinguibile» era una frase che un sesto confronto poteva
rompere, mentre «nessuna fa meglio» e' cio' che i dati sostengono davvero.

Il secondo: **la foresta installata sul dispositivo e' la piu' lenta per
finestra** delle sei, 4,85 ms contro 1,32 della CNN e 1,80 del grafo. Non e'
una contraddizione, ma obbliga a dire per esteso perche' e' stata scelta ---
undici secondi di addestramento contro venticinque minuti, nessuna dipendenza
da TensorFlow sul dispositivo, riproducibilita' --- e a non attribuirle un
vantaggio di velocita' in inferenza che non ha. I 4,85 ms sono inoltre il primo
controllo indipendente dei 4,47 ms per finestra dichiarati nel Capitolo 4.

**Verificato con:** `python _superato/correzioni_2026-08-31/_fix_cap2.py` -> tre sostituzioni applicate;
`grep -n -i grafo tesi/*.tex` -> nessuna occorrenza residua di «mai provate»;
i numeri di EXP-018 ed EXP-019 riletti da
`risultati/laboratorio/confronto_appaiato_gru.json` e
`risultati/laboratorio/costo_classificatori.json`, che sono i file che li
producono. **La run del grafo non e' stata rieseguita**: i valori vengono dal
JSON del 27 agosto.

**Collegamenti:** [EXP-018](EXPERIMENTS.md#exp-018),
[EXP-019](EXPERIMENTS.md#exp-019), [ISS-122](ISSUES.md#iss-122)

---

## [2026-08-27] — Giro di coerenza: sei affermazioni che si contraddicevano

**Tipo:** fix
**File:** `tesi/Cap3.tex`, `tesi/Cap4.tex`, `tesi/Cap5.tex`,
`tesi/Conclusioni.tex`, `src/geometry.py`, `deploy_board/geometry.py`,
`docs/EXPERIMENTS.md`, `docs/ISSUES.md`, `docs/PROJECT_CONTEXT.md`,
`docs/INDICE_E_STRUTTURA.txt`

**Perche':** scrivendo le spiegazioni per capitolo sono emerse affermazioni che
si contraddicevano fra loro. Nessuna produceva un errore, ed e' il punto: il
testo compila, il codice gira, e il numero e' sbagliato.

**Cosa cambia**, sei difetti, tutti registrati:

| | difetto | dove |
|---|---|---|
| [ISS-116](ISSUES.md#iss-116) | il Capitolo 4 dichiarava 12,36% di finestre positive e 94,55% di negative **nello stesso insieme**; la tabella delle etichette era quella a cinque soggetti | `Cap4.tex` |
| [ISS-117](ISSUES.md#iss-117) | i numeri di OmniFall ritirati il 25 agosto (101 soggetti, 29 viste) erano ancora nel Capitolo 3 | `Cap3.tex` |
| [ISS-118](ISSUES.md#iss-118) | l'autocorrelazione citata come 0,18--0,44 nel Cap. 3 e come 0,11--0,41 nel Cap. 5 e nelle Conclusioni | tre capitoli |
| [ISS-119](ISSUES.md#iss-119) | la docstring del motore geometrico sosteneva l'argomento sul rumore che il Cap. 3 dichiara falso | `src/geometry.py` |
| [ISS-120](ISSUES.md#iss-120) | tre rimandi che puntavano al posto sbagliato, piu' «otto capitoli» in un file che due paragrafi sotto ne dichiara cinque | registri |
| [ISS-108](ISSUES.md#iss-108) | chiusa: la promessa sul «ritardo» e' sparita con la riscrittura del Capitolo 1, e la misura esiste (EXP-017) | `Cap1.tex` |

**Il difetto che vale la pena rileggere e' ISS-117**, perche' e' la seconda
occorrenza dello stesso: la correzione di [ISS-110](ISSUES.md#iss-110) era stata
applicata al Capitolo 2 e l'avviso messo in testa a quel file soltanto, mentre
la stessa affermazione stava anche nel Capitolo 3. **Un numero ritirato in un
punto non e' ritirato nel lavoro.** L'avviso e' ora accanto al numero in
entrambi i file.

**Aperta [ISS-115](ISSUES.md#iss-115):** la scomposizione della latenza e'
misurata ([EXP-017](EXPERIMENTS.md#exp-017)) e **non compare in alcun
capitolo** --- ne' 3,778 s, ne' 2,743 s, ne' la parola «riempimento». E' una
delle quattro metriche operative chieste dal relatore.

**Verificato con:** ricalcolo dei numeri del Capitolo 4 da
`dataset/processed/features/feature_v2.csv` --- 57.786 fotogrammi, 109 riprese,
10 soggetti, 91,61% di pose valide, 11.510 finestre, 1.423 positive (12,36%),
che concordano con la somma della tabella dei fold riportata nello stesso
capitolo; `python tesi/controlla.py` -> «Nessun problema», resta la sola
`fig:due_camere` da comporre; `diff src/geometry.py deploy_board/geometry.py`
-> identici, e la copia della board importa (32 grandezze, K = 31); controllo
automatico delle ancore dei tre registri -> nessun rimando rotto.
**Compilazione non provata:** nessun compilatore LaTeX su questa macchina.

**Nota sui conteggi di parole.** La tabella di `PROJECT_CONTEXT.md` diceva 33.9k
ed era ferma al pomeriggio del 26 agosto: i due commit della sera hanno aggiunto
testo ai capitoli 4 e 5. Rimisurata: **35.407 parole**, stessi 39 titoli di
sezione e 33 di sottosezione.

---

## [2026-08-27] — Spiegazione integrale del lavoro, un file per capitolo

**Tipo:** docs
**File:** `docs/spiegazioni/00_PANORAMICA.md`, `01_CAP1_contesto.md`,
`02_CAP2_stato_arte.md`, `03_CAP3_metodologia.md`,
`04_CAP4_protocollo_risultati.md`, `05_CAP5_edge_e_campo.md`,
`06_CONCLUSIONI.md`, `07_MAPPA_CODICE.md` (tutti nuovi)

**Perche':** il registro e' diviso per genere --- esperimenti, difetti,
decisioni, cronologia --- e nessuno dei quattro racconta un capitolo dall'inizio
alla fine. Serviva la vista ortogonale: per ogni capitolo, che cosa dice il
testo, quale codice lo produce, quali esperimenti lo sostengono, quali difetti
sono stati trovati per strada.

**Cosa cambia:** otto documenti. Ciascuno risponde per il proprio capitolo alle
quattro domande insieme, con i riferimenti a file e riga del codice
(`geometry.py:132`, `dati.py:301`, ...) e i rimandi a EXP/ISS/DEC.
`07_MAPPA_CODICE.md` e' la tabella inversa: da un file di codice ai capitoli che
ne dipendono, piu' i comandi per rifare ogni numero.

Le sezioni piu' dense sono quelle che il registro non conteneva in forma
narrativa: perche' dieci soggetti e non diciassette; perche' i landmark e non i
pixel; perche' il minimo fra le due camere e non la media; perche' l'argomento
sulla cancellazione del rumore negli integrali e' sbagliato e che cosa regge al
suo posto; e le tre volte in cui un numero di intestazione dipendeva da un
parametro dell'analisi lasciato implicito.

**Verificato con:** i valori riletti contro `EXPERIMENTS.md`, `ISSUES.md`,
`DECISIONS.md`, i sorgenti `tesi/*.tex`, `deploy_board/metadata.json`,
`risultati/sessioni/LEGGIMI.md` e il codice citato. **Nessuna modifica ai
sorgenti della tesi ne' al codice**: e' documentazione soltanto.

---

## [2026-08-26] — Soglie di etichettatura da una sorgente sola, e due orologi sulla board

**Tipo:** fix, feature
**File:** `config.py`, `src/etichettatura.py`, `pipeline/addestra.py`,
`deploy_board/rileva.py`

**1. [ISS-112](ISSUES.md#iss-112).** Le quattro soglie del criterio K-su-M
stanno ora in `config.SOGLIE_ETICHETTATURA`, con gli stessi nomi dei
parametri della funzione che le usa. `etichetta_finestra` le legge da li';
`addestra.py` registra il dizionario intero invece di due valori su quattro.
Comportamento invariato, verificato su sequenze costruite.

**2. Doppio orologio in `rileva.py`.** `time.time()` e `time.monotonic()`
insieme: la loro differenza a fine sessione **e'** il tempo in cui la macchina
ha dormito. Se supera un secondo il riepilogo lo dichiara in rosso e marca la
sessione come non valida come prova di durata. E' il difetto del 10 agosto,
quando una prova e' sembrata riuscire mentre la board aveva dormito un'ora e
nove minuti.

**3. Bilancio del costo dentro l'esecuzione** ([ISS-113](ISSUES.md#iss-113)).
`perf_counter` attorno alle quattro fasi, e il risultato nel `riepilogo.json`.
Non un banco separato: i tempi sono quelli della stessa esecuzione che
produce gli allarmi.

**4. Una collisione di nomi corretta.** `sospensione` indicava sia il
silenzio dopo un allarme sia la sospensione della macchina. Il primo e' ora
`sospensione_regola`, con un commento accanto: e' il genere di collisione che
produce un numero plausibile e sbagliato.

**Verificato con:** `rileva.py --video clip_demo/evt_0001_092019` con
l'interprete `fall_processing` -> 175 fotogrammi, riepilogo e bilancio
prodotti, JSON scritto, sospensione 0,0 s. I valori di costo sono quelli del
calcolatore, non della board.

**Nota.** Nessuno di questi file e' sotto controllo di versione: il
repository traccia soltanto `tesi/`.

---

## [2026-08-26] — Ritirati tre riferimenti inventati

**Tipo:** fix
**File:** `tesi/Bibliografia.tex`, `tesi/Cap1.tex`, `tesi/Cap2.tex`

**Perche':** [ISS-114](ISSUES.md#iss-114). `asif`, `zobi` e `gazem` erano
segnaposto `[DA CERCARE]` con autore e titolo plausibili e nessun riscontro.

**Cosa cambia:** le tre voci sono fuori dalla bibliografia e le citazioni
fuori dal testo. **Nessuna riattaccata a un altro riferimento**: le tre
affermazioni sono state riscritte in modo da reggere da sole --- una come
conseguenza dell'architettura, una come rimando al capitolo che la misura,
una senza citazione. In testa a `Bibliografia.tex` un avviso dice di non
reinserirle.

Il commento in testa a `Cap1.tex` documentava «quattro citazioni aggiunte»:
ora ne dichiara due, e registra che le altre due erano segnaposto ritirati lo
stesso giorno. Serve a impedire che qualcuno le rimetta per far sparire una
voce orfana.

**Verificato con:** `python tesi/controlla.py` -> «Nessun problema». Le voci
mai citate restano cinque, le stesse di prima.

**Collegamenti:** [ISS-114](ISSUES.md#iss-114)

---

## [2026-08-26] — Gerarchia del Capitolo 3: da 49 titoli a 20

**Tipo:** docs
**File:** `tesi/Cap3.tex`

**Perche':** era l'ultimo capitolo fuori misura, con un titolo ogni 185 parole
--- dieci sezioni e trentanove sottosezioni in novemila parole.

**Cosa cambia:** 50 operazioni di declassamento e rinomina. **Nessun testo e'
stato cancellato**: la candidata ha chiesto che tutto cio' che e' stato
misurato resti nella tesi, quindi si e' agito solo sul livello dei titoli.

| | prima | ora |
|---|---:|---:|
| sezioni | 10 | **7** |
| sottosezioni | 39 | **13** |
| parole per titolo | 185 | **453** |

Tre accorpamenti: la sezione sul rumore dei landmark diventa sottosezione
della stima di posa; `B --- coordinate scheletriche grezze`, che contava
novanta parole, e' assorbita fra le rappresentazioni; finestratura e
definizione del compito, che erano due sezioni consecutive, diventano una
sola con tre sottosezioni.

**L'autocorrelazione resta nella metodologia**, declassata a `\paragraph`.
Era prevista in origine per il capitolo dei risultati, ma il relatore ha
chiesto esplicitamente di usarla come **spiegazione del fenomeno e non come
prova**: la sua sede naturale e' quindi accanto alla motivazione delle
grandezze integrali, non fra le misure.

**Verificato con:** `python tesi/controlla.py` -> «Nessun problema».

**Lo stato della tesi dopo questo intervento:**

| | parole | sez | sott | parole/titolo |
|---|---:|---:|---:|---:|
| Introduzione | 966 | --- | --- | --- |
| 1 Contesto | 2.858 | 4 | 4 | 357 |
| 2 Stato dell'arte | 2.507 | 5 | 0 | 501 |
| 3 Metodologia | 9.076 | 7 | 13 | 453 |
| 4 Protocollo e risultati | 7.872 | 9 | 7 | 492 |
| 5 Dispositivo e ambiente reale | 7.133 | 9 | 9 | 396 |
| Conclusioni | 2.103 | 5 | 0 | 420 |
| | **33.930** | **39** | **33** | |

**La riorganizzazione strutturale e' conclusa.** Restano contenuti: tre
figure, la prova lunga sulla board, [ISS-111](ISSUES.md#iss-111), e la
verifica delle voci di bibliografia.

---

## [2026-08-26] — Il Capitolo 1 della candidata entra nel repository

**Tipo:** docs, fix
**File:** `tesi/Cap1.tex`, `tesi/Cap5.tex`, `tesi/controlla.py`

**Perche':** il capitolo esisteva in due versioni divergenti
([ISS-110](ISSUES.md#iss-110)). Quella della candidata e' la buona: applica
gia' i titoli in forma nominale e ha sciolto la sottosezione singola che la
versione precedente aveva sotto la prima sezione.

**Cosa cambia:** il testo e' suo. Sono stati corretti soltanto:

1. **Tre chiavi di citazione inesistenti**, che sarebbero uscite come `[?]`:
   `1` -> `istat2026`, `kangas2015falsealarm` -> `kangas`,
   `scheurer2019aidemoi` -> `aidemoi`.
2. **Quattro citazioni aggiunte** dove il testo faceva gia' l'affermazione:
   `mediapipe` e `blazepose` sullo stimatore, `asif` sull'invarianza
   all'aspetto, `zobi` sulle coordinate instabili in occlusione. Erano citate
   solo nella versione precedente e senza di esse restavano voci mai citate.
3. Refusi (*Analogalmente*, *duranete*, *in ambiente domestici*, *mantenendo
   invarianti*, *Alla luce considerazioni*) e decimali all'italiana.

**Gerarchia:** 4 sezioni, 4 sottosezioni, 4 paragrafi --- **420 parole per
titolo**, contro le 192 della versione precedente.

**Due difetti trovati per strada.**

`controlla.py` non spogliava i commenti prima di cercare le `\cite`: le tre
chiavi corrette, citate nel commento di intestazione che documenta la
correzione, venivano segnalate come non definite. La stessa logica era gia'
applicata alle `ibitem` e ora vale anche per le `\cite`.

`yolopose` non era citato da nessuna parte, benche' il Capitolo 5 confronti
proprio quello stimatore su tre pagine. Citazione aggiunta alla prima
occorrenza.

**Verificato con:** `python tesi/controlla.py` -> «Nessun problema».
Totale 33.938 parole.

**Resta:** il diradamento del Capitolo 3, unico capitolo ancora fuori misura.

---

## [2026-08-26] — Gerarchia dei capitoli 4 e 5, e titoli accademici

**Tipo:** docs
**File:** `tesi/Cap4.tex`, `tesi/Cap5.tex`

**Perche':** la fusione aveva messo in fila due elenchi di sezioni di primo
livello: 14 sezioni nel Capitolo 4 e 18 nel Capitolo 5, cioe' un indice che si
legge come una lista di argomenti invece che come un ragionamento.

**Cosa cambia:** 79 operazioni di declassamento e rinomina, nessuna
riscrittura di testo.

| | prima | ora | parole per titolo |
|---|---:|---:|---:|
| Capitolo 4 | 14 sez + 30 sott | **9 sez + 7 sott** | 492 |
| Capitolo 5 | 18 sez + 9 sott | **9 sez + 9 sott** | 396 |

I titoli sono ora in forma nominale: «Effetto della geometria di ripresa» al
posto di «L'effetto del punto di vista», «Discordanza fra prestazioni di
benchmark e comportamento reale» al posto di «Che cosa il laboratorio non
riesce a misurare», «Analisi di numerosita' campionaria» al posto di «Quanti
soggetti servirebbero».

**Le regole applicate.** Una `\subsection` esiste solo se ha almeno una
sorella e se insieme esauriscono la sezione; un blocco sotto le 250 parole
diventa `\paragraph`, che ha un nome ma non una voce nell'indice. Tre gruppi
di sezioni sono stati raccolti sotto una sezione sola: rappresentazioni e
architetture, i controlli di sensibilita', motivazione e protocollo delle
sessioni domestiche.

**Verificato con:** `python tesi/controlla.py` -> «Nessun problema».
Introduzione 966, Cap1 3.337, Cap2 2.518, Cap3 9.371, Cap4 8.430, Cap5 7.573,
Conclusioni 2.182; totale **34.377**.

**Resta fuori misura:** Capitolo 1 (un titolo ogni 192 parole) e Capitolo 3
(185). Il Capitolo 3 e' il diradamento vero, e comporta spostare nei capitoli
4 e 5 cio' che e' misura e non metodo.

---

## [2026-08-26] — La tesi passa da otto capitoli a cinque

**Tipo:** docs
**File:** `tesi/Cap4.tex`, `tesi/Cap5.tex` (fusi), `tesi/Conclusioni.tex`
(rinominato), `tesi/tesi.tex`, `tesi/controlla.py`

**Perche':** la struttura concordata. Il protocollo da solo non era un
capitolo (2.976 parole, ventidue titoli, quattro sezioni senza testo proprio);
dispositivo e ambiente reale ripetevano entrambi la descrizione della board.

**Cosa cambia:**

| prima | ora |
|---|---|
| 4 protocollo + 5 risultati | **4 Protocollo di valutazione e risultati sperimentali** |
| 6 deployment + 7 ambiente reale | **5 Implementazione su dispositivo edge e validazione in ambiente reale** |
| 8 conclusioni | `Conclusioni.tex` |

Le introduzioni dei quattro capitoli fusi sono state **sostituite** da due
aperture nuove, non concatenate; nei punti di giunzione c'e' un paragrafo di
transizione. Il testo delle sezioni e' invariato.

**Le etichette sono tenute tutte come alias** --- `cap:risultati`,
`cap:protocollo`, `cap:sperimentale` sul Capitolo 4; `cap:edge` e `cap:campo`
sul Capitolo 5 --- perche' una ventina di rimandi negli altri capitoli le usa.
Nessun `
ef` e' stato riscritto a mano.

`controlla.py` non conosceva `Conclusioni.tex`, che non si chiama `Cap*`:
segnalava `cap:conclusioni` come etichetta assente e lasciava le sue 2.182
parole fuori dal totale. Corretto.

**Copia di sicurezza** in `_superato/capitoli_pre_fusione/`, con il LEGGIMI
che dice per ciascun file dove e' finito.

**Verificato con:** `python tesi/controlla.py` -> «Nessun problema».
Introduzione 966, Cap1 3.337, Cap2 2.518, Cap3 9.371, Cap4 8.409, Cap5 7.551,
Conclusioni 2.182; **totale 34.334**.

**Resta da fare:** la gerarchia interna. Il Capitolo 4 ha 14 sezioni contro le
9 previste, il Capitolo 5 ne ha 18 contro 9, il Capitolo 3 e' ancora a 9.371
parole contro 6.800. Sono declassamenti a sottosezione, non riscritture.

---

## [2026-08-26] — I quattro interventi chiesti dal relatore

**Tipo:** docs, feature
**File:** `tesi/Cap5.tex`, `tesi/Cap6.tex`, `tesi/Cap7.tex`,
`pipeline/figure_tesi.py` (`fig_errori`)

**Perche':** quattro richieste esplicite dell'email del 20 agosto non erano
ancora nel testo. Verificate una per una con `grep`: nessuna delle quattro
espressioni compariva.

| suo punto | intervento |
|---|---|
| §4 chiamarlo adattamento al dominio | `Cap7.tex`: «adattamento al dominio di installazione --- *domain adaptation* nella terminologia corrente --- e non generalizzazione» |
| §5 mostrare i due errori, non un solo F2 | `Cap7.tex`: tabella FN/FP per le cinque configurazioni + `fig_errori.png` |
| §6 chiamarla soglia oracolo | `Cap5.tex`: definita come «valore ottenuto usando le etichette del dominio di destinazione, che chi installa non possiede» |
| §8 coerenza fra 4,47 e 2,20 ms | `Cap6.tex`: il classificatore decide una volta ogni due fotogrammi (passo 2), quindi il costo ammortizzato e' meta' di quello per finestra |

**Il dato nuovo del §5**, a dieci soggetti e non a cinque: da A3 ad A3i con i
controesempi i falsi negativi passano da **45 a 14** e i falsi positivi da
**172 a 124**. In laboratorio la configurazione finale **non introduce alcuno
scambio**: migliora entrambi gli errori. Lo scambio compare solo in casa, che
e' esattamente la tesi del capitolo.

**Verificato con:** `python tesi/controlla.py` -> «Nessun problema»;
`python pipeline/figure_tesi.py` -> undici figure; `fig_errori.png` ispezionata
a video.

**Collegamenti:** [EXP-017](EXPERIMENTS.md#exp-017)

---

## [2026-08-26] — Scomposizione della latenza, e una promessa da riscrivere

**Tipo:** feature
**File:** `pipeline/latenza.py` (nuovo), `risultati/campo/latenza.json`

**Perche':** [ISS-108](ISSUES.md#iss-108) e la quarta metrica operativa
chiesta dal relatore.

**Cosa cambia:** lo script scompone la latenza nei tre addendi e dichiara
quale non e' misurabile. **Il ritardo fra caduta e allarme non lo e'**:
l'annotazione delle cadute e' al minuto, la grandezza da misurare e' di pochi
secondi. Si misurano invece calcolo 0,038 s, riempimento della finestra
2,743 s, persistenza 0,997 s, limite inferiore **3,778 s** --- dominata dalla
finestra di decisione, non dall'hardware, con un fattore settantatre.

**Verificato con:** `python pipeline/latenza.py` -> scomposizione stampata,
ritardo della regola 1,70 e 1,28 s sulle due cadute in cui l'allarme scatta
contro 1,00 s attesi, JSON scritto.

**Collegamenti:** [EXP-017](EXPERIMENTS.md#exp-017), [ISS-108](ISSUES.md#iss-108)

---

## [2026-08-26] — Due delle tre figure mancanti, e una discordanza

**Tipo:** feature
**File:** `pipeline/figure_tesi.py` (`fig_dimensione`, `fig_viewpoint_dist`),
`risultati/cinque_soggetti/` (nuova)

**Perche':** `tesi/controlla.py` segnalava tre ambienti `figure` senza
immagine nel capitolo dei risultati. Due sono ora generabili.

**Cosa cambia:** le sorgenti stavano solo in `DIP_PROJECT/scripts/out/`, cioe'
fuori dal repository: sono state copiate in `risultati/cinque_soggetti/`, con
un LEGGIMI che dichiara la provenienza. **Le due misure vengono dall'impianto
a cinque soggetti**, e le figure lo stampano dentro l'immagine.

- `fig_dimensione.png` — F2 con dispersione fra fold e latenza, doppio asse,
  sei dimensioni di foresta. Le barre d'errore si sovrappongono: la figura
  mostra che l'ottimo a 50 alberi **non e' distinguibile** dalle altre
  dimensioni, che e' lo stesso criterio applicato alle architetture.
- `fig_viewpoint_dist.png` — grafico appaiato delle 25 sequenze, una linea per
  coppia, in rosso le due che si rovesciano.

**Verificato con:** `python pipeline/figure_tesi.py` -> dieci figure prodotte,
nessun errore; entrambe le nuove ispezionate a video.

**Difetto trovato:** [ISS-111](ISSUES.md#iss-111) — il file dice 1,99x e due
sequenze rovesciate, il capitolo dichiara 1,90x e tre. Finche' non e'
risolto, `fig_viewpoint_dist` non va inserita nel testo.

**Collegamenti:** [ISS-111](ISSUES.md#iss-111)

---

## [2026-08-26] — Capitolo 2, quarta stesura sulla nuova versione del Capitolo 1

**Tipo:** docs
**File:** `tesi/Cap2.tex`

**Perche':** la candidata ha riscritto il Capitolo 1, che ora assorbe tre
argomenti prima trattati nel Capitolo 2: la scelta della visione contro gli
indossabili, la scelta della posa con la motivazione di riservatezza, e il
conto sulla frequenza di base. La sua versione del Capitolo 2 li ripeteva
tutti e tre, conteneva un blocco duplicato al proprio interno (il passaggio su
Lin et al. compariva due volte) e reintroduceva due affermazioni gia'
smentite ([ISS-110](ISSUES.md#iss-110)).

**Cosa cambia:** da 2.416 a 2.516 parole, cinque sezioni, zero sottosezioni.
Tolto cio' che il nuovo Capitolo 1 dice; rimasto cio' che la tesi impiega.
Assorbite dal vecchio Capitolo 1 cinque citazioni che la nuova versione non
porta piu': `bagala` (13 algoritmi su 29 cadute reali, sensibilita' 57,0%),
`tcnte` (99,58% su UP-Fall), `gcn3stream`, `scheurer` (utenti noti contro
sconosciuti, oltre 20 punti), `vira` (99,81% in dominio, ~50% fuori).
Aggiunta la citazione a `urfall`, che altrimenti resterebbe orfana quando il
Capitolo 1 verra' sostituito. Reti a grafo, optical flow, CNN 3D, SVM e k-NN
restano fuori, con dichiarazione esplicita di cosa il lavoro non prova.

**Verificato con:** `python tesi/controlla.py` -> «Nessun problema»; nessuna
citazione non definita, nessun riferimento orfano; Cap2 324 righe, 2.516
parole, 5 sezioni. Compilazione non provata: nessun compilatore LaTeX su
questa macchina.

**Collegamenti:** [ISS-110](ISSUES.md#iss-110), [ISS-107](ISSUES.md#iss-107)

---

## [2026-08-26] — Indice a cinque capitoli, e il documento per il relatore

**Tipo:** docs
**File:** `docs/INDICE_E_STRUTTURA.txt` (nuovo)

**Perche':** il relatore ha chiesto, nell'email del 20 agosto, «un indice
aggiornato e, soprattutto, la struttura del capitolo sperimentale», per
verificare che il lettore arrivi alle conclusioni senza doverle ricostruire
dalla successione cronologica degli esperimenti. Rientra il 2 settembre.

**Cosa cambia:** gli otto capitoli diventano cinque. Fusi *Contesto* e *Stato
dell'arte*, che ripetevano la stessa tassonomia dei sensori, lo stesso
argomento sulla posa e lo stesso difetto di protocollo; fusi *Protocollo* e
*Risultati*, perche' il primo aveva 22 titoli in 2.976 parole ed era il
preambolo del secondo. *Deployment* e *Ambiente reale* restano separati: la
prova domestica non e' la validazione finale ma lo strumento con cui il
problema e' stato riformulato. Da 33.644 a circa 30.000 parole previste.

Il documento riporta, per ogni sezione dei tre capitoli sperimentali, la tesi
che sostiene e non il suo contenuto; lo stato delle cinque verifiche chieste
dal relatore (quattro fatte, la prova di durata no); e una correzione al punto
1 della sua email, perche' a dieci soggetti il guadagno delle grandezze
integrali sulla foresta non e' distinguibile dal caso
([EXP-013](EXPERIMENTS.md#exp-013)).

**Verificato con:** i valori citati riletti contro i file che li producono
(`risultati/campo/pr_auc_allineato.json`,
`risultati/campo/valutazione_incrociata_10sog.json`,
`risultati/occlusioni/foresta_DTW.json`); `wc -w` -> 2.862 parole.
**Nessuna modifica ai sorgenti della tesi:** la riorganizzazione e' proposta,
non applicata. `tesi/controlla.py` invariato, restano 3 figure mancanti.

**Collegamenti:** [ISS-107](ISSUES.md#iss-107), [ISS-108](ISSUES.md#iss-108),
[ISS-109](ISSUES.md#iss-109)


---

## [2026-08-25/26] — Il Capitolo 2, e le regole di scrittura

**Tipo:** docs
**File:** `tesi/Cap2.tex`, `tesi/Bibliografia.tex`, `CLAUDE.md` (nuovo)

**Perche':** il capitolo sullo stato dell'arte, scritto il 23 agosto, e'
stato riscritto tre volte su altrettante obiezioni della candidata, tutte
fondate.

**Le tre stesure.**

*Prima*, 5.271 parole. Difetto misurato: venticinque rimandi ai capitoli
sperimentali («il Capitolo X lo misura»), venti occorrenze di «questo
lavoro», e diciannove paragrafi con una citazione su centosette. Un capitolo
che parlava del lavoro senza mostrarne niente.

*Seconda*, 2.645 parole. Tolti i rimandi, tolti i grassetti (da 18 a 0),
introdotto l'ambiente `Domanda` per porre le due domande del lavoro invece di
prometterne la risposta. Restavano pero' otto sottosezioni, sei dentro la
stessa sezione e lunghe fra 104 e 189 parole.

*Terza*, 2.416 parole, cinque sezioni, zero sottosezioni. Tolte le due parti
che descrivevano cose non impiegate nel lavoro — il confronto fra
elaborazione diretta dell'immagine e posa, gia' argomentato nel Capitolo 1, e
la trattazione delle reti a grafo, mai provate — con al loro posto una
dichiarazione esplicita di quali famiglie il lavoro confronti e quali no. Le
sei sottosezioni sono diventate `\paragraph`.

**Le regole di scrittura**, ricavate dalla tesi triennale della candidata e
ora in `CLAUDE.md`: i capitoli di sfondo fissano i concetti e si fermano;
l'enfasi e' `\emph` sui termini definiti; un titolo ogni ~400 parole; niente
formule retoriche; dichiarare cosa non si e' fatto.

**Riferimenti verificati sul web il 2026-08-25**, uno per uno: `gutierrez`
(Sensors 21(3):947, 81 sistemi), `broadley` (Sensors 18(7):2060, 22
articoli), `lin` (Applied Sciences 11(1):329), `omnifall` (arXiv:2505.19889,
15k riprese, 80 ore, 16 classi), `kangasreali` (Gait & Posture 35(3):500-505),
`nguyen` (Sensors 23(11):5121).

**Due affermazioni non reggevano, e sono state sostituite.** La voce
`omnifall` riportava «quattordici ore, 101 soggetti, 29 viste» contro i
numeri dichiarati nell'abstract. La voce `nabizade` sosteneva «undici studi
su 588 record» senza che ne sia stato trovato riscontro: sostituita da
`gomes` (IEEE J. Biomed. Health Inform. 2026, 433 studi primari), che
sostiene la stessa tesi con numeri verificabili.

**Verificato con:** `tesi/controlla.py` dopo ogni stesura, sempre senza
problemi. Compilazione non provata: nessun compilatore LaTeX su questa
macchina.

**Issue:** aperta [ISS-107](ISSUES.md#iss-107), sovra-suddivisione dei
capitoli 3 e 4.

---

## [2026-08-19] — Documentazione iniziale del progetto

**Tipo:** docs
**File:** `docs/EXPERIMENTS.md`, `docs/DECISIONS.md`, `docs/ISSUES.md`, `docs/CHANGELOG.md`
**Perche':** il progetto nuovo era senza registro. Le sei run gia' fatte, i tre
difetti trovati e risolti e le quattro decisioni metodologiche esistevano solo
nella conversazione.
**Cosa cambia:** quattro registri popolati retroattivamente con EXP-001..006,
ISS-100..103, DEC-100..104.
**Verificato con:** rilettura incrociata dei riferimenti; i numeri provengono
dagli output delle run, non da ricostruzione a memoria.

---

## [2026-08-19] — Selezione consapevole della ridondanza

**Tipo:** feature
**File:** `pipeline/analisi_dtw.py` — nuova `seleziona()`, opzione `--max-corr`,
`grafico_camere()` riceve l'insieme scelto invece del numero
**Perche':** [ISS-102](ISSUES.md#iss-102) — il DTW valuta ogni grandezza da
sola e premiava tre volte «quanto e' verticale il tronco».
**Cosa cambia:** selezione avida, si aggiunge una grandezza solo se la sua
correlazione con tutte le gia' scelte sta sotto soglia. Le escluse sono
dichiarate con chi le blocca e il valore di r. La correlazione si misura sui
soli fotogrammi con posa valida.
**Verificato con:** `pipeline/analisi_dtw.py --csv feature.csv --top 12 --max-corr 0.85`
-> 12 scelte, 4 escluse per ridondanza, correlazione media da 0,385 a 0,325.
Provate anche le soglie 0,75 e 0,90.
**Collegamenti:** [ISS-102](ISSUES.md#iss-102), [DEC-103](DECISIONS.md#dec-103),
[EXP-006](EXPERIMENTS.md#exp-006)

---

## [2026-08-19] — Formattazione dei decimali prima della composizione

**Tipo:** fix
**File:** `pipeline/analisi_dtw.py` — `dec()` locale
**Perche':** [ISS-103](ISSUES.md#iss-103) — `.replace('.', ',')` su f-string
gia' composte trasformava anche il punto degli elenchi numerati.
**Cosa cambia:** i numeri si formattano prima di entrare nella stringa. Il
perche' e' in un commento accanto, non solo qui.
**Verificato con:** l'elenco del sottoinsieme scelto stampa `1.`, `2.` e
`robusto 1,309`.
**Collegamenti:** [ISS-103](ISSUES.md#iss-103)

---

## [2026-08-19] — Ricampionamento a lunghezza comune prima del DTW

**Tipo:** fix
**File:** `src/dtw.py` — `punteggio()`, nuovo parametro `lunghezza`
**Perche':** [ISS-101](ISSUES.md#iss-101) — il vincolo di warping si allargava
da solo sulle coppie caduta-ADL (~180 contro ~820 fotogrammi), che sono proprio
quelle che devono risultare distanti.
**Cosa cambia:** le curve vengono portate a 200 campioni dopo lo z-score e
prima del confronto, cosi' la banda vale 10 per tutte le coppie. Venti righe di
docstring spiegano il conto delle durate e perche' perdere l'informazione di
durata e' lecito.
**Verificato con:** test sintetico con la stessa asimmetria di durata ->
punteggio da 5,055 a 7,201 sulle stesse curve; riesecuzione reale -> nessuna
grandezza sotto 1,0, cinque integrali risalgono di oltre +0,19.
**Collegamenti:** [ISS-101](ISSUES.md#iss-101), [DEC-102](DECISIONS.md#dec-102),
[EXP-004](EXPERIMENTS.md#exp-004) annullata, [EXP-005](EXPERIMENTS.md#exp-005)

---

## [2026-08-19] — Periodo di srotolamento dell'angolo dell'ellisse

**Tipo:** fix
**File:** `src/geometry.py` — `_srotola()`, chiamata sull'inclinazione
**Perche':** [ISS-100](ISSUES.md#iss-100) — l'asse di un'ellisse e' una
direzione, non un verso: periodo 180 gradi, non 360.
**Cosa cambia:** `periodo=180.0` per l'inclinazione dell'ellisse; le grandezze
vettoriali restano a 360.
**Verificato con:** riestrazione del pilota; il salto 201,9 -> 49,5 gradi fra
fotogrammi consecutivi non si ripresenta.
**Collegamenti:** [ISS-100](ISSUES.md#iss-100)

---

## [2026-08-20] — Ciclo di addestramento e confronto fra architetture

**Tipo:** feature
**File:** `src/modelli.py` (nuovo), `pipeline/addestra.py` (nuovo),
`pipeline/soglia.py` (nuovo), `src/dati.py`
**Perche':** serviva un ciclo unico per tutte le architetture: se ognuna avesse
il suo, ogni differenza misurata potrebbe venire dal ciclo invece che dal
modello.
**Cosa cambia:**
- `modelli.py` — GRU, LSTM, CNN 1D, Transformer e foresta casuale dietro
  un'interfaccia sola (`.addestra`, `.probabilita`, `.n_parametri`), a 2 o 3
  classi. Arresto anticipato sull'AUC della probabilita' di ALLARME, non sulla
  perdita: la soglia si sceglie dopo, quindi serve un modello che ORDINI bene,
  non che decida bene a 0,5.
- `addestra.py` — LOSO completa, `run_metadata.json` con tutto il necessario a
  rifarla, e le probabilita' per fold in `.npz`.
- `soglia.py` — confronto fra regole di soglia sulle probabilita' salvate,
  senza riaddestrare.
- `dati.py` — nomi di colonna allineati all'estrattore (`soggetto`, `ripresa`,
  `fotogramma`, `ha_posa`); le finestre non scavalcano piu' i buchi di posa;
  `Fold` porta ora anche il validation nello spazio di etichette del modello.
**Verificato con:** tutte e cinque le architetture a 2 e 3 classi (uscite
normalizzate, conteggio parametri: GRU 24.450 contro LSTM 32.194, cioe' il 24%
in meno come atteso da 3 porte contro 4); LOSO reale su 10 fold con soggetti
disgiunti e 76-171 positivi per fold; due esecuzioni indipendenti con metriche
identiche.
**Collegamenti:** [EXP-009](EXPERIMENTS.md#exp-009),
[EXP-010](EXPERIMENTS.md#exp-010), [DEC-105](DECISIONS.md#dec-105)

---

## [2026-08-20] — A2: rimosse due grandezze degeneri, ridefinite due integrali

**Tipo:** fix
**File:** `src/geometry.py` — `NOMI_A2`, `a2()`, chiamata a `_integrali('A2')`
**Perche':** [ISS-104](ISSUES.md#iss-104) — i world landmark sono centrati sulle
anche, quindi il bacino e' l'origine e non si muove (deviazione standard
0,00003 m contro 0,0175 m del naso).
**Cosa cambia:** `A2_hip_vy` e `A2_hip_vel` rimosse; `A2_percorso` e
`A2_discesa` ora seguono il naso, la cui posizione in coordinate world e' gia'
relativa alle anche. Il bacino passa da 34 a 32 grandezze.
**Verificato con:** riestrazione completa su `feature_v2.csv` — 30 colonne
identiche bit per bit fra v1 e v2, solo le due ridefinite cambiate; nuova DTW
dove le due riabilitate entrano al secondo e terzo posto.
**Collegamenti:** [ISS-104](ISSUES.md#iss-104), [EXP-007](EXPERIMENTS.md#exp-007),
[EXP-008](EXPERIMENTS.md#exp-008)
