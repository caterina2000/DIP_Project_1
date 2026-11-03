# Storia del progetto — dal primo commit al 9 settembre 2026

Documento di memoria. Serve a chi riprende il lavoro dopo giorni, o a una
sessione nuova che non ha visto niente di quello che c'e' stato prima.

**Ricostruito dai registri e dai file, non dal ricordo di una conversazione.**
Ogni numero qui dentro ha un puntatore al documento che lo contiene: se un
numero e' cambiato, e' cambiato li' e questo file va aggiornato di conseguenza.

I registri veri restano [CHANGELOG.md](CHANGELOG.md),
[EXPERIMENTS.md](EXPERIMENTS.md), [ISSUES.md](ISSUES.md),
[DECISIONS.md](DECISIONS.md). Questo file **non li sostituisce**: li riassume
in ordine di tempo, che e' l'unica cosa che nessuno dei quattro fa.

---

## 0. Il lavoro in una riga

Rilevare cadute da video RGB su un dispositivo edge da circa cento euro, senza
che nessuna immagine esca dal dispositivo. MediaPipe Pose estrae 33 punti del
corpo, da quelli si ricavano grandezze geometriche, e un classificatore decide
su finestre di circa 2,4 secondi.

La domanda che il classificatore risponde e' **«sta cadendo?»**, non «e' a
terra?» ([DEC-107](DECISIONS.md#dec-107)). E' la scelta che separa un sistema
usabile da uno che suona per un pomeriggio intero su due persone sedute sul
divano.

---

## 1. Le cinque fasi

### Fase I — febbraio–luglio 2026: l'impianto che non funzionava

Primo commit **16 febbraio 2026**, «Upload iniziale Fall Detection», nel
progetto oggi chiamato `DIP_PROJECT`. Impianto: UP-Fall, MediaPipe, feature
geometriche, due strade in parallelo — una GRU (*Method A*) e un autoencoder
seguito da foresta casuale (*Method B*).

Il risultato di quella stagione, registrato come EXP-001 nel registro storico:

```
Method A (GRU)          F1 = 0,0000
Method B (AE + foresta) F1 = 0,3509
```

Le run di quel periodo sono in gran parte prive di metadati: nel registro
storico compaiono con la data «precedente a 2026-05» e con esito ⚠ o ❌.
Una sola aveva un `run_metadata.json`.

### Fase II — 3–4 agosto: l'audit, e la diagnosi dell'F1 = 0

Il **3 agosto** nasce il sistema di documentazione viva: CHANGELOG, ISSUES,
EXPERIMENTS, DECISIONS, PROJECT_CONTEXT. E' il momento in cui il progetto
smette di essere un insieme di script e diventa un lavoro tracciabile.

Il **4 agosto** la causa dell'F1 = 0 viene accertata, e non era quella che si
pensava:

| | |
|---|---|
| causa | **nessuno `StandardScaler`** (ISS-008 storica) |
| prova | le scale delle feature differiscono di **646×**: `energy` ha media 11,58 e massimo 15.499, quindi domina i gradienti e rende invisibili le altre nove |
| concausa | split **per video** e non per soggetto: tutti e 5 i soggetti in train *e* in test, con 28 sole finestre positive nel test |
| ipotesi smentita | che lo scarto delle finestre positive fosse la causa: toglieva il 40% dei positivi, non la quasi totalita' |

**La lezione che ha guidato tutto il resto del progetto e' questa:** la causa
plausibile e la causa vera non coincidono, e distinguerle costa una misura.

### Fase III — 5–18 agosto: il dispositivo

Il lavoro si sposta sull'hardware: una **Radxa ROCK 4D**. In due settimane:

- **5 agosto** — primi risultati sulla board, parita' PC/board verificata.
- **6 agosto** — YOLOv8 convertito per l'NPU e misurato end-to-end: 18,5 fps,
  guadagno reale 1,71×. Il sistema gira a 26,5 fps. *(Numero poi ritirato:
  vedi ISS-137 e il §2.)*
- **7 agosto** — il collo di bottiglia non era la rete, era `scp` file per
  file. La soglia sui keypoint diventa una decisione reversibile. Il fattore
  4,32× fra le viste **non si riproduce**: il valore corretto e' 1,99×.
- **9–10 agosto** — sopralluogo della stanza, protocollo di ripresa, prima ora
  in ambiente reale. La soglia passa da 0,38 a 0,50.
- **10 agosto** — sei sessioni con pose valide fra lo **0,6% e il 39,8%**: la
  telecamera era posizionata male. Non entrano in nessun risultato, e sono il
  motivo per cui esiste il protocollo di ripresa.
- **11 agosto** — il domain shift e la sua cura.
- **14 agosto** — grandezze **integrali** al posto delle derivate istantanee.

### Fase IV — 19–23 agosto: il secondo impianto

Nasce `DIP_Project_1` con una pipeline riscritta. Non e' una correzione della
precedente: e' un impianto diverso, con un registro che riparte da ISS-100,
EXP-001, DEC-100 per non confondersi con quello storico.

| data | passo | esito |
|---|---|---|
| 19 ago | estrazione feature, 10 soggetti, 34 colonne | 114.923 fotogrammi, 218 riprese, **95,5% pose valide** |
| 19 ago | DTW senza ricampionamento | **ANNULLATA**, [ISS-101](ISSUES.md#iss-101) |
| 19 ago | DTW con ricampionamento a lunghezza comune | OK, [DEC-102](DECISIONS.md#dec-102) |
| 20 ago | riestrazione con A2 corretto (v2), DTW definitiva | OK |
| 20 ago | prima LOSO a 10 soggetti | OK, ma soglia instabile |
| 20 ago | sei regole di soglia a confronto | **decisivo** |
| 20 ago | cinque architetture a confronto | **nessuna distinguibile dalle altre** |
| 20 ago | ablation sulla lunghezza di finestra | nessun effetto |
| 20 ago | numerosita' necessaria per ogni confronto | **decisivo** |
| 21 ago | UR-Fall rietichettato con il motore nuovo | OK |
| 21 ago | le tre definizioni del compito | **decisivo** → [DEC-107](DECISIONS.md#dec-107) |
| 22 ago | le stesse 56 clip su PC e su board | **una decisione su 56 diverge** |

Il **23 agosto** la tesi si sposta qui. In `DIP_PROJECT/tesi/` non resta nulla;
lo spostamento e' stato verificato con `diff -rq` prima della rimozione, 43
file identici.

### Fase V — 23 agosto–9 settembre: la tesi, e i numeri che non reggevano

Il progetto diventa repository git il **25 agosto**. Il **26** i capitoli
passano da otto a cinque, con tutte le etichette tenute come alias.

Da qui in avanti la storia e' quella di una **revisione sistematica dei
risultati**, e quasi ogni voce del registro e' un numero che non reggeva:

- **26 ago** — ritirati **tre riferimenti di bibliografia inventati**
  ([ISS-114](ISSUES.md#iss-114)): `asif`, `zobi`, `gazem`. Non reinseriti; le
  affermazioni che sostenevano sono state riscritte per reggere da sole.
- **31 ago** — cinque numeri epidemiologici del Capitolo 1 erano di
  un'edizione diversa della sorveglianza ([ISS-123](ISSUES.md#iss-123)); una
  voce di bibliografia fondeva due lavori ([ISS-124](ISSUES.md#iss-124)).
- **1 set** — nascono le prove automatiche: `prove/`, 31 prove, due secondi.
  Coprono i tre punti dove un errore non produce un'eccezione ma un numero.
- **1 set** — il numero piu' citato della tesi confrontava due modelli diversi.
- **6 set** — riestrazione completa **v3**, 220 riprese, 33 grandezze.
  L'altezza dal pavimento entra nel classificatore: **i falsi negativi calano
  del 35%**. L'escursione fra le viste rifatta su dieci soggetti: 2,23× e non
  1,99×, e una seconda causa — 11 riprese su 50 cambiano persona.
- **6 set** — l'indirizzo della board non e' fisso, e il router ha dato al PC
  lo stesso indirizzo: `ping` rispondeva a se stesso e l'SSH sembrava un
  attacco. Vedi [CLAUDE.md](../CLAUDE.md) §4 per la procedura corretta.
- **7 set** — la regola di allarme installata era **la peggiore delle quattro
  provate**; ventuno regole a confronto, l'isteresi dimezza i falsi allarmi e
  prende piu' cadute. Le occlusioni rimisurate: la robustezza dipende dalle
  **colonne**, non dal motore.
- **8 set** — la latenza rifatta sul costo per fotogramma misurato: il fattore
  scende da 73× a 22×, la conclusione regge. La board decide **fuori
  distribuzione nel 75,4%** dei casi.
- **9 set** — vedi §5.

---

## 2. I numeri che contano oggi, e quelli che sono stati ritirati

La cosa piu' utile da sapere non e' il valore corrente: e' **quale valore e'
stato ritirato e perche'**, perche' i numeri ritirati continuano a comparire
nei documenti vecchi.

| grandezza | valore ritirato | valore corrente | dove |
|---|---|---|---|
| costo per fotogramma sulla board | 37,7 ms (26,5 fps) | **136,65 ms** | [ISS-137](ISSUES.md#iss-137), EXP-024 |
| cadenza reale della board | 9,0 fps *assunti* | **6,47 fps** (9 set) · 7,26 fps (6 set) | EXP-035, EXP-024 |
| escursione fra le due viste | 4,32× → 1,99× | **2,23×** | EXP-020 |
| fattore della scomposizione di latenza | 73× | **22×** | EXP-030 |
| durata della finestra integrale sulla board | 1,72 s *creduti* | **4,79 s** prima della correzione | EXP-035 |

Le due cadenze **non sono una contraddizione**: sono due sessioni diverse,
6 e 9 settembre. Ma vanno citate con la loro data, perche' cambiano la durata
della finestra di esercizio (3,03 s contro 3,40 s) — e questo e' il nodo di
[ISS-158](ISSUES.md#iss-158).

**Le dodici grandezze in uso** (selezione DTW, campagna v5):

```
A2_testa_rel_y  A2_discesa  A2_percorso  A1_discesa  A3_discesa  A3_escursione
A3_caviglie_rel_y  A3_percorso  A3_hip_vel  A3_testa_vel_rel  A1_percorso  A1_escursione
```

**La popolazione di addestramento** (camera 1, 10 soggetti, 110 riprese):
11.719 finestre, di cui 87,3% normali, 4,0% caduta in corso, 8,7% a terra —
**allarme atteso sul 12,7%**.

---

## 3. Le decisioni che non si rimettono in discussione

Sono in [DECISIONS.md](DECISIONS.md), DEC-100..109. Le tre che spiegano
qualunque altra scelta:

- **[DEC-107](DECISIONS.md#dec-107)** — il classificatore risponde «sta
  cadendo?». Cambiare questa domanda cambia tutti i numeri.
- **[DEC-106](DECISIONS.md#dec-106)** — tre dataset con tre ruoli distinti, e
  nessuno dei tre fa il lavoro di un altro.
- **[DEC-105](DECISIONS.md#dec-105)** — soglia fissa, dichiarata a priori.
  Non scelta sul test.

---

## 4. I difetti aperti — 21 su 61 registrati

Elenco completo in [ISSUES.md](ISSUES.md). I quattro che pesano di piu' oggi,
e sono tutti della stessa famiglia:

1. **[ISS-158](ISSUES.md#iss-158)** — la finestra di *decisione* e' ancora un
   conteggio di fotogrammi. In addestramento dura 2,44 s, sulla board **3,40 s**.
   La correzione fatta per gli integrali qui non si puo' ripetere: a 6,47 fps
   il dispositivo non ha abbastanza fotogrammi per un passo di 0,111 s. Tre
   vie possibili, nessuna gratis, **nessuna scelta**.
2. **[ISS-160](ISSUES.md#iss-160)** — K = 5 e M = 8 sono campioni, non
   secondi, e sono calcolati sul flusso gia' sottocampionato. Cambiare
   `step` cambierebbe il criterio del 50% senza che nessuno lo decida.
3. **[ISS-159](ISSUES.md#iss-159)** — `scelte.txt` viene sovrascritto a ogni
   analisi DTW, e la foresta dipende dall'**ordine** delle colonne.
4. **[ISS-110](ISSUES.md#iss-110)** — due copie divergenti dei capitoli. Vedi §5.

---

## 5. Il 9 settembre, giorno per ora

### La finestra degli integrali diventa una durata — chiusa

`K_INTEGRALI = 31` era un conteggio: 1,72 s a 18 fps, ma **4,27 s alla cadenza
misurata sulla board**. Nove delle tredici colonne installate sono integrali:
tre quarti del vettore d'ingresso avevano un significato fisico diverso fra
addestramento ed esercizio.

Il buffer conserva ora **secondi**. A 18 fps il motore produce valori
**identici bit per bit** — scarto 0,000e+00 su tutte e 33 le grandezze — quindi
`feature_v3.csv` e ogni numero della tesi che ne discende non si muovono.

Sulla board la cadenza si **misura** invece di assumerla: `rileva.py` passava
9,0 fps mentre la board ne faceva 7,26, e le derivate uscivano sopravvalutate.

### Tre risultati di campo, e sono i piu' severi del progetto

| | |
|---|---|
| **EXP-035** | prima sessione con DTWH installata. La cadenza vera e' **6,47** e non 9,0 |
| **EXP-036** | la regola installata su **tre cadute vere** con verita' di riferimento: **recall 0 su 3**. Il tetto di qualunque regola e' 2 su 3, e una caduta il classificatore proprio non la vede |
| **EXP-037** | i sei allarmi di agosto riletti col modello di oggi: **nessuno dei sei sarebbe emesso**, il piu' alto fa 0,400 |

Sono i numeri da tenere presenti prima di scrivere qualunque frase ottimista
sul comportamento in ambiente reale.

### Le stesure della candidata entrano nel repository

Cap1 (17:33) e Cap2 (18:14) sono ora la **prosa della candidata**, corretta,
non piu' la riscrittura del repository. L'operazione ha riportato indietro
cinque citazioni, **due delle quali invisibili** — una voce mai citata non e'
un errore per LaTeX, e con `thebibliography` scritto a mano viene stampata lo
stesso:

| chiave | |
|---|---|
| `gazem` | **rientrata**, ed era una delle tre ritirate il 26 agosto perche' inventate |
| `fnopi`, `epicentro` | chiavi nuove, non definite |
| `fleming` | persa: era l'unico riferimento clinico del *long lie* |
| `mediapipe`, `blazepose` | perse: il testo diceva quale stimatore usa senza attribuirlo |
| `gomes` | persa da Cap2 |

Tutte sistemate; `fnopi` ed `epicentro` verificate sulla fonte con URL e
commento `% VERIFICATO`. `python tesi/controlla.py` → **Nessun problema**.

**Cap3, Cap4 e Cap5 sono fermi in `tesi/da_incorporare/`, per decisione.**
Installarli com'e' stato fatto per Cap1 e Cap2 cancellerebbe, in silenzio:

| | figure | tabelle | sezioni |
|---|---|---|---|
| Cap3 | `fig:finestra`, `fig:rappresentazioni` | `tab:grandezze`, `tab:landmark`, `tab:stimatori` | `sec:nomi`, `sec:metodoB`, `sec:elenco-grandezze` |
| Cap4 | `fig:viste`, `fig:dominio`, `fig:configurazioni`, `fig:due_camere` | `tab:alberi`, `tab:cambio_persona`, `tab:errori_attivita`, `tab:richiamo_tipo` | `sec:sei-regole` |
| Cap5 | --- | `tab:latenza_misurata`, `tab:costo_misurato`, `tab:fps_scena`, `tab:prima_ora`, `tab:scambio` | `sec:frequenza-base`, `sec:prima-ora` |

**In silenzio davvero:** nessuno di quei rimandi e' usato da un altro capitolo,
quindi `controlla.py` non segnalerebbe niente. Dettagli e verifica in
[ISS-110](ISSUES.md#iss-110).

### La campagna v5 — 6 run su 12 al momento della scrittura

`for F in DTW DTWH; for A in gru lstm cnn transformer grafo foresta`, su
`feature_v5.csv`, camera 1, L22, tre classi. Blocco **DTW** concluso:

| modello | F2 | ±dev | recall | precisione | TP | FP | FN | parametri | durata |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **gru** | **0,857** | 0,089 | 0,946 | 0,683 | 1.402 | 938 | 89 | 24.483 | 1.245 s |
| cnn | 0,838 | 0,100 | 0,941 | 0,639 | 1.398 | 1.134 | 93 | 46.147 | 602 s |
| transformer | 0,837 | 0,082 | 0,927 | 0,650 | 1.372 | 969 | 119 | 34.499 | 711 s |
| lstm | 0,829 | 0,084 | 0,947 | 0,627 | 1.409 | 1.266 | 82 | 32.227 | 934 s |
| **foresta** | 0,825 | 0,076 | 0,849 | **0,808** | 1.259 | **468** | 232 | 12.928 | **10 s** |
| grafo | 0,794 | 0,087 | 0,865 | 0,645 | 1.282 | 934 | 209 | 12.323 | 2.162 s |

Due letture che vanno nel Capitolo 4:

1. **L'escursione fra le sei architetture e' 0,063; la deviazione fra i fold di
   una singola architettura e' 0,076–0,100.** Lo scarto fra i modelli sta sotto
   la variabilita' interna di ciascuno. E' il sostegno diretto alla
   formulazione chiesta dal relatore: *non emerge evidenza sufficiente per
   attribuire all'architettura un ruolo dominante*.
2. **La foresta sta 0,032 sotto la GRU in F2, ma con la meta' dei falsi
   allarmi** (468 contro 938), precisione 0,808 contro 0,683, e in **10 secondi
   contro 1.245**. Per un sistema che deve girare su una board ed essere
   sopportabile in casa, il confronto non e' ovvio come l'F2 suggerisce.

La campagna copia `risultati/dtw/scelte.txt` in `scelte_usata_campagna_v5.txt`
prima di partire: e' il presidio contro [ISS-159](ISSUES.md#iss-159).

---

## 6. Dove sta cosa

```
DIP_Project_1/            <- il progetto attivo
├── tesi/                 cinque capitoli, figure, controlla.py
│   └── da_incorporare/   Cap3, Cap4, Cap5: stesure NON installate
├── pipeline/             gli script che producono risultati e figure
├── src/                  geometria, dati, etichettatura, modelli
├── prove/                31 prove automatiche, `python prove/esegui.py`
├── risultati/            tutti i numeri, compresi quelli di campo
├── deploy_board/         cio' che gira sul dispositivo
├── docs/                 questo registro
└── _superato/            sostituito, conservato, NON da usare

../DIP_PROJECT/           <- il progetto storico
├── sessioni_reali/       la RACCOLTA delle sessioni, con le clip
├── docs/                 ISS-001..055, EXP-001..061, fino al 22 agosto
└── scripts/              gli script di campo dell'impianto precedente
```

**Le clip ritraggono familiari identificabili.** Restano fuori da git, non si
copiano in percorsi tracciati, non si pubblicano. Nessun numero del lavoro
dipende da esse: la regola di decisione si applica ai punteggi.

**Non esiste un compilatore LaTeX su questa macchina.** Il PDF si produce su
Overleaf. «Verificato» si scrive solo per cio' che e' stato eseguito davvero.

---

## 7. Che cosa resta

1. **Decidere su ISS-110**: fusione, installazione secca o direzione opposta
   per Cap3, Cap4, Cap5. Finche' non e' presa, quei tre capitoli non si toccano.
2. **Decidere su ISS-158**: riaddestrare alla cadenza vera, ricampionare a
   bordo, oppure dichiarare lo scarto e misurarlo. La terza e' il minimo.
3. **ISS-160**: K e M in secondi, come gia' fatto per gli integrali.
4. Registrare la campagna v5 in `EXPERIMENTS.md` quando le 12 run finiscono.
5. `noury` e `rougier` sono in bibliografia e non sono citate da nessuna parte:
   vanno citate dove servono o commentate.

---

*Stato al 9 settembre 2026, ore 19:15. Aggiornare questo file quando cambia
una fase, non a ogni intervento: i dettagli stanno nei quattro registri.*
