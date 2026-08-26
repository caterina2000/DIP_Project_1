# CHANGELOG — DIP_Project_1

Registro cronologico delle modifiche al codice. Piu' recente in alto.

Formato:

```
## [AAAA-MM-GG] — titolo
**Tipo:** fix | feature | refactor | docs | config
**File:** percorso:riga
**Perche':** ...
**Cosa cambia:** ...
**Verificato con:** comando eseguito -> esito reale
**Collegamenti:** ISS-xxx / EXP-xxx / DEC-xxx
```


Se una modifica non e' stata provata, si scrive «non verificato»: e'
un'informazione utile, fingere non lo e'.

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
