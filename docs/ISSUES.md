# ISSUES — DIP_Project_1

Registro dei difetti. Nulla si cancella: cio' che viene risolto si sposta in
«Risolti» con data e intervento. La storia dei difetti serve.

Numerazione da 100 per non confondersi con le ISS-0xx del progetto storico.

---

## Aperti

<a id="iss-113"></a>
### ISS-113 — I numeri del costo edge non hanno un artefatto che li produca

**Trovata:** 2026-08-26 · **Gravita': media** · **Stato: APERTA**

La ripartizione del costo per fotogramma --- pre-elaborazione 1,21 ms,
percezione **33,34 ms (88,4%)**, post 0,94 ms, classificatore 2,20 ms,
totale **37,7 ms** cioe' **26,5 fps** --- esiste **soltanto nel testo della
tesi**. Cercando `33.34` e `33,34` in tutti i JSON, CSV, TXT e MD dei due
progetti non compare in nessun file di risultato.

`DIP_PROJECT/deploy_board/benchmark_board.py` **stampa a schermo e non
salva**: i valori sono stati trascritti da una sessione di terminale.

E' una delle quattro richieste del relatore e una delle affermazioni di
intestazione del lavoro (*«il collo di bottiglia non e' la classificazione ma
la percezione»*), quindi e' anche il numero che meno puo' permettersi di non
essere rifacibile.

**Intervento, prima meta' (2026-08-26).** Non si aggiunge un banco
separato: `deploy_board/rileva.py` misura ora le quattro fasi **dentro
l'esecuzione vera**, con `perf_counter` attorno a pre-elaborazione,
percezione, post-elaborazione e classificatore, e scrive il bilancio nel
`riepilogo.json` insieme a tutto il resto. Il numero verra' quindi dalla
stessa esecuzione che produce gli allarmi, non da una prova a parte: e' il
solo modo perche' non possa divergere dalla catena in esercizio.

Riporta anche il costo del classificatore **per finestra** accanto a quello
**per fotogramma**, che sono i due valori la cui differenza il Capitolo 5
doveva spiegare.

**Verificato con:** `rileva.py --video clip_demo/evt_0001_092019` sul
calcolatore -> bilancio prodotto, JSON scritto. I valori sono quelli del PC e
non della board.

**Resta da fare:** eseguirlo sulla board, nella stessa sessione della prova
lunga.

---

<a id="iss-111"></a>
### ISS-111 — Il fattore fra le due viste non si riproduce dal file citato

**Trovata:** 2026-08-26 · **Gravita': media** · **Stato: APERTA**

`tesi/Cap5.tex:88` dichiara che il rapporto fra l'escursione dell'angolo del
tronco osservata dalle due telecamere vale **1,90x**, e aggiunge che «una
misura indipendente, calcolata senza passare dai file di feature intermedi,
conferma 1,90x». La didascalia di `fig:viewpoint_dist` dichiara che «in **tre**
sequenze la vista rialzata osserva quanto quella laterale».

Il file che il capitolo indica come sorgente,
`risultati/cinque_soggetti/exp013_camera_viewpoint.csv`, dice altro:

| | |
|---|---|
| coppie | 25 (5 soggetti x 5 tipi di caduta, attivita' 1-5) |
| medie | cam1 71,0 gradi, cam2 35,7 gradi |
| **rapporto delle medie** | **1,99x** |
| **sequenze con cam2 >= cam1** | **2** |

Provate le varianti: media dei rapporti 2,87, mediana 2,79; il filtro sulla
quota di pose valide non sposta nulla (1,98 a qualunque soglia). **Nessuna
combinazione produce 1,90 ne' tre sequenze.**

Non si conclude che il testo sia sbagliato: 1,90 potrebbe venire dalla
«misura indipendente» citata, cioe' da una procedura diversa da questo CSV.
Si conclude che **la sorgente dichiarata non produce il numero dichiarato**.

**La figura stampa cio' che il file dice**, quindi al momento figura e testo
si contraddicono.

**Intervento previsto.** Ritrovare la procedura che produce 1,90 e dichiararla
come sorgente, oppure allineare testo e didascalia a 1,99 e a «due sequenze».
Fino ad allora la figura non va inserita nel testo.

---

<a id="iss-110"></a>
### ISS-110 — Due versioni divergenti dei capitoli, e i fatti che tornano indietro

**Trovata:** 2026-08-26 · **Gravita': alta** · **Stato: APERTA**

La candidata scrive i capitoli in Overleaf; il repository ne conserva un'altra
versione. Le due divergono, e la fusione avviene a mano.

**Il danno accertato.** La versione Overleaf del Capitolo 2 riportava per
OmniFall «circa 14 ore di registrazioni uniche, 101 soggetti e 29 viste».
Sono i numeri **gia' trovati sbagliati e corretti il 25 agosto**: l'abstract
dichiara quindicimila riprese, ottanta ore, sedici classi. La stessa versione
attribuiva la rassegna skeleton-based a una «review del 2024 con oltre cento
metodi» invece che a `nguyen` (Sensors 23(11):5121, 2023).

Un fatto verificato e corretto e' quindi tornato indietro. E' il modo di
sbagliare piu' pericoloso del progetto, perche' non lascia traccia: il testo
compila, si legge bene, e il numero e' falso.

**Danno secondario.** Dieci chiavi di citazione su dodici non esistono in
`Bibliografia.tex` (`1`, `kangas2015falsealarm`, `scheurer2019aidemoi`,
`mubashir2013survey`, `gutierrez2021vision`, `huang2024skeleton`,
`lin2021openpose`, `martinez2019upfall`, `broadley2018realworld`,
`schneider2025omnifall`). Con `thebibliography` scritto a mano non
compilano come riferimento.

**Contesto che aggrava.** Solo **7 voci su 31** portano il commento
`% VERIFICATO`: `broadley`, `gomes`, `gutierrez`, `kangasreali`, `lin`,
`nguyen`, `omnifall`. Tutte le altre non sono state controllate sulla fonte.

**Intervento previsto.** Una sola copia del testo. Finche' ne esistono due,
ogni fusione va fatta confrontando i numeri contro i commenti `% VERIFICATO`
in `Bibliografia.tex`, mai a memoria. I due numeri di OmniFall e Nguyen sono
ora protetti da un avviso in testa a `tesi/Cap2.tex`.

---

<a id="iss-109"></a>
### ISS-109 — Le rappresentazioni si chiamano A1 nella tesi e A nella lettera

**Trovata:** 2026-08-26 · **Gravita': bassa** · **Stato: APERTA**

`tesi/Cap3.tex:232` intitola la prima rappresentazione «A1 --- la sagoma come
ellisse». La lettera al relatore del 17 agosto dichiara invece: «Si chiamano
A, A2 e A3 --- non esiste un "A1", il primo e' semplicemente A.»

Il relatore ha in mano la lettera, quindi la divergenza va sanata. Il codice
usa `A1`: `src/geometry.py:92` definisce `NOMI_A1` e le dieci colonne portano
il prefisso `A1_`. Rinominare il codice costerebbe una riestrazione, quindi la
scelta economica e' tenere `A1` nella tesi e **dichiarare la rinomina** dove le
tre rappresentazioni vengono introdotte.

**Intervento previsto.** Una riga in `Cap3.tex`, sezione «Tre rappresentazioni
geometriche», che dichiari il cambio di nome rispetto alla comunicazione
precedente.

---

<a id="iss-108"></a>
### ISS-108 — Il Capitolo 1 promette una misura di ritardo che non esiste

**Trovata:** 2026-08-26 · **Gravita': media** · **Stato: APERTA**

`tesi/Cap1.tex:64` dichiara: «Per questa ragione il Capitolo~
ef{cap:campo}
misura esplicitamente il *ritardo* di rilevamento, e non soltanto se l'allarme
arrivi.» La parola «ritardo» **non compare in `Cap7.tex`**: zero occorrenze.

`pipeline/eventi_sessioni.py` calcola eventi/ora, quota di tempo sopra soglia e
tempo medio fra falsi allarmi (`mtba_min`), ma **non** la latenza fra l'istante
annotato della caduta e il primo allarme.

La latenza e' anche una delle quattro metriche operative indicate dal relatore
nell'email del 20 agosto, quindi il difetto e' doppio: una promessa non
mantenuta nel testo e una richiesta esplicita non ancora eseguita.

**Difetto secondario nello stesso passaggio.** `Cap1.tex:53` e `Cap1.tex:64`
aprono entrambi con «Questa osservazione ha una conseguenza...», a due
paragrafi di distanza. I due paragrafi vanno fusi in uno.

**Aggiornamento 2026-08-26.** Calcolata: [EXP-017](EXPERIMENTS.md#exp-017),
`pipeline/latenza.py`. **Il ritardo fra caduta e allarme non e' misurabile**
perche' l'annotazione e' al minuto e la grandezza e' di pochi secondi: gli
scarti osservati (+11,8 ... +32,3 s) misurano il punto del minuto in cui si
e' caduti. Si misura invece la scomposizione: calcolo 0,038 s, riempimento
della finestra 2,743 s, persistenza 0,997 s, limite inferiore 3,778 s.

**Resta aperta** la parte testuale: il Capitolo 1 promette ancora «misura
esplicitamente il ritardo», e va riscritto; e i due paragrafi di Cap1.tex:53
e :64 vanno ancora fusi.

**Collegamenti:** [ISS-107](#iss-107)

---

<a id="iss-107"></a>
### ISS-107 — I capitoli 3 e 4 sono suddivisi troppo

**Trovata:** 2026-08-25 · **Gravita': media** · **Stato: APERTA**

Misurato il rapporto fra parole e titoli in ciascun capitolo:

| capitolo | parole | sez. | sottosez. | parole per titolo |
|---|---:|---:|---:|---:|
| 4 Protocollo | 2.976 | 5 | 17 | **135** |
| 6 Deployment | 2.664 | 7 | 7 | 190 |
| 3 Metodologia | 9.408 | 10 | 39 | 192 |
| 1 Contesto | 3.738 | 6 | 11 | 220 |
| 7 Ambiente reale | 4.823 | 11 | 6 | 284 |
| **2 Stato dell'arte** | 2.416 | 5 | 0 | **483** |
| 8 Conclusioni | 2.418 | 5 | 0 | 484 |

Il Capitolo 3 ha **quarantanove titoli** in 9.400 parole; il Capitolo 4 ne ha
ventidue in meno di tremila, cioe' un titolo ogni mezza paginetta.

**Quattro sezioni del Capitolo 4 non hanno testo proprio**: un titolo seguito
immediatamente da un altro titolo. Sono «Sbilanciamento delle classi»,
«Dallo split per video al LOSO», «Normalizzazione stimata sul solo
addestramento» e «La soglia decisionale».

**Il criterio.** Sotto le 250 parole un blocco non giustifica una
`\subsection`: va reso `\paragraph`, che porta un nome ma non una voce
nell'indice. Il Capitolo 2, sistemato il 26 agosto, e' il modello.

**Due casi accertati nel Capitolo 3, da risolvere insieme alla suddivisione.**
La sezione «B --- coordinate scheletriche grezze» conta 90 parole e non e'
una sezione: va assorbita fra le rappresentazioni. Le sottosezioni «Cosa e'
stato rimosso, e perche'» e «Cosa sostituiscono» dicono la stessa cosa in due
punti diversi.

**Intervento previsto** Ridurre il Capitolo 3 da 49 a circa 21 titoli e il
Capitolo 4 da 22 a circa 10, senza togliere contenuto: le sezioni sono tutte
necessarie, e' la gerarchia a essere sbagliata.

---

<a id="iss-106"></a>
### ISS-106 — Lo stimatore di posa non si trasferisce fra architetture

**Trovata:** 2026-08-22 · **Gravita': media** · **Stato: APERTA (accertata, non risolvibile)**

Le stesse clip, elaborate sul PC (x86) e sulla board (ARM) con la stessa
versione di MediaPipe e lo stesso modello, producono grandezze diverse.

La parita' sulle **finestre gia' calcolate** era passata con scarto
`0,000e+00`: modello e scaler si trasferiscono esattamente. La divergenza
nasce prima, nello stimatore di posa, che e' un **tracciatore**: mantiene
stato fra fotogrammi, e uno scarto infinitesimo nella decodifica
dell'immagine si amplifica lungo la sequenza.

| fotogramma | scarto medio sui landmark |
|---:|---:|
| 1 | 0,0001 |
| 11 | 0,0755 |

**Effetto misurato** ([EXP-016](EXPERIMENTS.md#exp-016)): su 56 clip, 55
decisioni identiche e una diversa — una caduta reale che il PC segnala con
punteggio 1,000 e la board non segnala (picco 0,560, l'antirimbalzo a cinque
finestre non scatta).

**Perche' non e' risolvibile.** Non e' un difetto di versione ne' di
configurazione: e' la natura del componente. Le implementazioni delle
operazioni in virgola mobile differiscono fra le due architetture, e un
sistema con stato le amplifica.

**Cosa comporta.**

1. La verifica di trasferimento deve partire dai **fotogrammi**. La prova
   sulle finestre precalcolate e' passata con scarto esattamente zero pur
   mascherando l'unica divergenza reale: e' un punto cieco, non una prova.
2. **Le prestazioni misurate sul PC non sono le prestazioni della board.** Il
   recall va misurato sulla board.
3. L'antirimbalzo amplifica la divergenza: trasforma uno scarto continuo di
   punteggio in una decisione binaria diversa. E' un costo del meccanismo,
   accettato consapevolmente ([DEC-107](DECISIONS.md#dec-107)).

---

<a id="iss-105"></a>
### ISS-105 — La finestra e' piu' corta dell'evento da riconoscere

**Trovata:** 2026-08-20 · **Gravita': alta** · **Stato: APERTA**

`config.py`: `LUNGHEZZA_FINESTRA = 22` campioni a 9 fps = **2,44 s**.

Misurata la durata delle fasi sulle 50 riprese di caduta della camera 1:

| fase | mediana | decile 10% | decile 90% |
|---|---:|---:|---:|
| in piedi, prima | 0,92 s | | |
| **caduta in corso (classe 1)** | **3,11 s** | 2,05 s | 3,94 s |
| a terra (classe 2) | 5,97 s | 4,82 s | 6,89 s |

La finestra non puo' contenere una caduta intera: ne vede sempre un frammento,
e nella meta' dei casi al massimo il 78%.

**Da dove viene il 22.** E' 45 diviso due, dove 45 era `SEQUENCE_LENGTH` nel
`config.py` del progetto precedente — un valore che in quel progetto esisteva
in tre versioni contrastanti: 45 in config, 75 in `demo_realtime.py:23`, **39**
nei metadati della run migliore ([ISS-004](#iss-004) del vecchio registro).
Nessuna delle tre e' mai stata giustificata, e nessuna e' mai stata confrontata
con la durata dell'evento.

**Costo della correzione: basso.** I parametri di una GRU **non dipendono**
dalla lunghezza della sequenza; cresce solo il tempo di inferenza, in modo
lineare, e la memoria del buffer sulla board.

**Intervento previsto:** ablation su 22 / 28 / 36 campioni a parita' di tutto
il resto. 28 copre la caduta mediana, 36 il decile 90%.

---

## Risolti

<a id="iss-112"></a>
### ISS-112 — Le soglie di etichettatura erano dichiarate in due posti

**Trovata:** 2026-08-26 · **Risolta:** 2026-08-26 · **Gravita': media**

`config.py` dichiarava `CADUTA_MIN_FOTOGRAMMI = 5` e `TRANSIZIONE_MAX = 10`;
`src/etichettatura.py` aveva i propri default `k_caduta=5, m_blocco=8,
k_terra=10, m_terra=15`; nessuno collegava i due, e i chiamanti non passavano
nulla. `pipeline/addestra.py` scriveva pero' nel `run_metadata.json` i valori
di `config`: **il file che serve a rendere una run rifacibile dichiarava
parametri che non la governavano**. Le due ampiezze di blocco, che rendono il
criterio «K su M» invece di «K totali», non erano registrate da nessuna parte.

**Intervento.** Le quattro soglie stanno ora in `config.py` con **gli stessi
nomi dei parametri della funzione**, raccolte in `SOGLIE_ETICHETTATURA`;
`etichetta_finestra` le legge da li' quando l'argomento e' `None`, e un
valore passato esplicitamente continua a prevalere; `addestra.py` registra il
dizionario intero. Le due costanti vecchie sono state rimosse: nessun
riferimento residuo.

**Verificato con:** `etichetta_finestra` su sequenze costruite --- 5
fotogrammi consecutivi di classe 1 -> `1`; 4 -> `0`; 10 di classe 2 -> `2`;
con `k_caduta=4` esplicito, 4 -> `1`. **Comportamento identico a prima**, che
era il requisito: la correzione non doveva cambiare alcun risultato gia'
prodotto.

---


<a id="iss-114"></a>
### ISS-114 — Tre riferimenti di bibliografia non corrispondono a lavori reali

**Trovata:** 2026-08-26 · **Risolta:** 2026-08-26 · **Gravita': alta**

`asif`, `zobi` e `gazem` erano segnaposto marcati `[DA CERCARE]`, con autore e
titolo plausibili e un `TODO: recuperare titolo completo, autori e sede`.
Erano citati nel testo: `gazem` nel Capitolo 2, `asif` e `zobi` nel Capitolo 1
--- questi ultimi aggiunti lo stesso 26 agosto durante l'installazione del
Capitolo 1, per non lasciare voci orfane, senza controllare che cosa fossero.

**Intervento.** Le tre voci sono state ritirate da `Bibliografia.tex` e le
citazioni tolte dal testo. **Nessuna e' stata riattaccata a un altro
riferimento**: sostituire un riferimento non verificato con un altro scelto
in fretta produce lo stesso difetto con un nome diverso. Le tre affermazioni
sono state riscritte in modo da reggere da sole:

| voce | affermazione | come regge ora |
|---|---|---|
| `asif` | le rappresentazioni pose-based sono invarianti all'aspetto | riscritta come conseguenza dell'architettura: volto, texture e abbigliamento non raggiungono il classificatore, quindi il modello non puo' apprenderli. E' vera per costruzione |
| `zobi` | lo stimatore perde landmark sotto occlusione | rimando in avanti al capitolo che lo **misura**, senza anticipare il numero |
| `gazem` | i wearable dipendono dalla compliance | citazione tolta; la frase resta, ed e' gia' attribuita alla famiglia dalla rassegna citata a inizio sezione |

In testa a `Bibliografia.tex` c'e' ora un avviso che dice di non
reinserirle e che un eventuale riferimento va **verificato sulla fonte**.

**Verificato con:** `python tesi/controlla.py` -> «Nessun problema»; nessuna
citazione non definita; l'elenco delle voci mai citate e' invariato
(`gru`, `lstm`, `noury`, `randomforest`, `rougier`).

**Collegamenti:** [ISS-110](#iss-110)

---


<a id="iss-104"></a>
### ISS-104 — Quattro grandezze A2 misuravano l'origine del riferimento

**Trovata:** 2026-08-20 · **Risolta:** 2026-08-20 · **Gravita': alta**

`src/geometry.py`, metodo `a2()` e chiamata a `_integrali('A2', ...)`.

I world landmark di MediaPipe sono **centrati sul punto medio delle anche**: il
bacino e' l'origine del sistema di riferimento e non si muove per costruzione.
Misurato su 40 fotogrammi consecutivi:

```
bacino  dev.std   [0,000034  0,000047  0,000046]  m   <- 0,03 mm
naso    dev.std   [0,012700  0,002712  0,017535]  m   <- 400 volte tanto
```

Quattro grandezze misuravano quindi rumore numerico:

| grandezza | max misurato | destino |
|---|---:|---|
| `A2_hip_vy` | 0,000 | rimossa |
| `A2_hip_vel` | 0,1 | rimossa |
| `A2_percorso` | 7,6 | ridefinita sul naso |
| `A2_discesa` | 1,4 | ridefinita sul naso |

**Aggravante: la grandezza degenere era stata SELEZIONATA.** `A2_percorso` era
entrata fra le dodici scelte di [EXP-006](EXPERIMENTS.md#exp-006), al nono
posto, e la sua bassa correlazione con `A1_percorso` (0,25) e `A3_percorso`
(0,30) era stata interpretata come «porta la componente in profondita'». Era
indipendente perche' era rumore, e il rumore non correla con niente. E' il
modo tipico in cui una grandezza degenere supera un filtro di ridondanza.

**Intervento.** `A2_hip_vy` e `A2_hip_vel` rimosse: la traslazione assoluta del
corpo con i world landmark non e' misurabile, e la misurano gia' A1 e A3 nel
piano immagine. `A2_percorso` e `A2_discesa` ridefinite sul **naso**, la cui
posizione in coordinate world e' gia' relativa alle anche, quindi e' un
movimento vero. Verificata anche la direzione dell'asse y: cresce verso il
basso come nel piano immagine (naso y = −0,55, caviglie y = +0,68 su persona
eretta).

**Verificato con:** riestrazione completa
([EXP-007](EXPERIMENTS.md#exp-007)) — 30 colonne identiche bit per bit fra v1 e
v2, solo le due ridefinite cambiate; e nuova analisi DTW
([EXP-008](EXPERIMENTS.md#exp-008)), dove le due riabilitate entrano al secondo
e terzo posto della classifica.

---

<a id="iss-100"></a>
### ISS-100 — Periodo di srotolamento sbagliato per l'angolo dell'ellisse

**Trovata:** 2026-08-19 · **Risolta:** 2026-08-19 · **Gravita': alta**

`src/geometry.py`, funzione `_srotola`. L'angolo veniva srotolato con periodo
360 gradi per tutte le grandezze angolari, incluso l'asse maggiore
dell'ellisse.

L'asse di un'ellisse e' una **direzione, non un verso**: ha periodo 180 gradi.
Con il periodo sbagliato la serie presentava salti artificiali — misurato un
passaggio 201,9 -> 49,5 gradi fra due fotogrammi consecutivi, cioe' una
rotazione di 152 gradi in un diciottesimo di secondo, fisicamente impossibile.
Ogni salto si propagava sulla derivata e sugli integrali accumulati.

**Intervento:** `incl = _srotola(incl, p_inc, periodo=180.0)` per l'inclinazione
dell'ellisse; le grandezze vettoriali mantengono 360.

**Verificato con:** riestrazione del pilota, i salti spuri spariti dalla serie.

---

<a id="iss-101"></a>
### ISS-101 — Il vincolo di warping si allargava sulle coppie incrociate

**Trovata:** 2026-08-19 · **Risolta:** 2026-08-19 · **Gravita': alta**

`src/dtw.py`, funzione `dtw`: `window=max(finestra, abs(n - m))`.

L'allargamento e' necessario — con `|n - m|` maggiore della banda nessun
cammino di allineamento arriva in fondo — ma su questo dataset produceva un
effetto perverso. Le riprese di caduta durano ~180 fotogrammi, quelle di
attivita' quotidiana ~820:

| coppia | differenza di lunghezza | banda effettiva |
|---|---:|---:|
| caduta - caduta | piccola | 10 |
| ADL - ADL | piccola | 10 |
| **caduta - ADL** | ~640 | **630** |

Le coppie incrociate — quelle che devono risultare distanti — si allineavano
quasi senza vincolo, e la loro distanza risultava artificialmente bassa.

**Impatto misurato.** Su dati sintetici con la stessa asimmetria: punteggio
5,055 invece di 7,201, cioe' **−30% su forme volutamente diversissime**.

L'effetto non era uniforme, ed e' questa la parte grave: colpiva
**selettivamente gli integrali**, che sono curve lisce e sotto warping libero
si deformano l'una nell'altra a costo quasi nullo, mentre le grandezze
posizionali hanno un gradino netto che il warping non cancella. Cinque delle
nove integrali risultavano sotto 1,0 e venivano scartate come rumore. Il
difetto era conservativo sui valori ma **falsava l'ordine della classifica**,
che e' esattamente cio' che serviva.

**Intervento:** ricampionamento a 200 campioni prima del confronto, cosi' `n =
m` per ogni coppia e la banda vale 10 per tutte. Vedi
[DEC-102](DECISIONS.md#dec-102).

**Verificato con:** test sintetico riproducibile (8 curve da 180 con discesa
netta contro 9 da 820 oscillanti) e riesecuzione su dati reali, dove nessuna
grandezza resta sotto 1,0 e cinque integrali risalgono di oltre +0,19.

**Run annullata:** [EXP-004](EXPERIMENTS.md#exp-004).

---

<a id="iss-102"></a>
### ISS-102 — Selezione DTW cieca alla ridondanza

**Trovata:** 2026-08-19 · **Risolta:** 2026-08-19 · **Gravita': media**

`pipeline/analisi_dtw.py` selezionava `cl.head(top)`, cioe' le prime k della
classifica. Il DTW valuta ogni grandezza isolatamente, quindi lo stesso
fenomeno misurato in tre modi occupa tre posti.

Sui dati reali le prime dodici contenevano cinque coppie con |r| > 0,80:

```
A2_testa_rel_y      A2_angolo_tronco      r = 0,972
A2_testa_rel_y      A3_testa_rel_y        r = 0,981
A2_angolo_tronco    A3_testa_rel_y        r = 0,946
A3_ginocchia_rel_y  A3_caviglie_rel_y     r = 0,931
A3_escursione       A2_escursione         r = 0,852
```

Le prime tre sono la stessa cosa: quanto e' verticale il tronco. Alla rete
sarebbero arrivati circa otto segnali indipendenti travestiti da dodici.

Difetto collaterale dello stesso punto: fra il dodicesimo (1,163) e il
tredicesimo (1,162) della classifica c'era **un millesimo**. Sotto 1,16
l'ordine era un pareggio, non una graduatoria, e tagliare a dodici secchi era
arbitrario.

**Intervento:** funzione `seleziona`, selezione avida con soglia `--max-corr`
(predefinito 0,85). Le escluse vengono dichiarate con il nome di chi le blocca
e il valore di r. Correlazione media fra le scelte da 0,385 a 0,325. Vedi
[DEC-103](DECISIONS.md#dec-103) e [EXP-006](EXPERIMENTS.md#exp-006).

---

<a id="iss-103"></a>
### ISS-103 — `.replace('.', ',')` applicato a f-string gia' composte

**Trovata:** 2026-08-19 · **Risolta:** 2026-08-19 · **Gravita': bassa**

Ricorrente in tutto il progetto, storico e nuovo. Per scrivere i decimali con
la virgola si applicava `.replace('.', ',')` alla stringa finita, che
trasformava in virgola **tutti** i punti: quelli degli elenchi numerati
(`1.` diventava `1,`), quelli delle estensioni, quelli delle frasi.

**Intervento:** in `pipeline/analisi_dtw.py` i numeri si formattano prima di
entrare nella stringa, con un `dec()` locale, e il perche' e' scritto in un
commento accanto — l'errore si nota tardi e male.
