# CLAUDE.md — istruzioni per lavorare su questo repository

Progetto: **rilevamento di cadute da video RGB su dispositivo edge**.
MediaPipe Pose → grandezze geometriche → classificatore su finestre di 2,4 s.
Tesi magistrale in Ingegneria dell'Intelligenza Artificiale e
dell'Automazione, Universita' di Siena.

**Da leggere prima di toccare qualsiasi cosa:**
[docs/PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md).

---

## 1. Dove sta cosa

```
DIP_Project_1/                 <- QUESTO progetto: e' quello attivo
├── tesi/          il testo: cinque capitoli, figure, controlla.py
├── pipeline/      gli script che producono risultati e figure
├── src/           il codice di libreria (geometria, dati, modelli)
├── risultati/     tutti i numeri, compresi quelli di campo
├── dataset/       feature estratte
├── docs/          registro: contesto, changelog, esperimenti, difetti, decisioni
└── _superato/     materiale sostituito, conservato ma NON da usare

../DIP_PROJECT/                <- progetto storico
├── sessioni_reali/   la cartella di RACCOLTA delle sessioni, con le clip
├── docs/             il registro storico (ISS-001..055, EXP-001..061)
└── scripts/          gli script di campo dell'impianto precedente
```

La tesi e' stata spostata qui il **23 agosto 2026**. In `DIP_PROJECT/tesi/`
non c'e' piu' niente: se qualcuno cerca un capitolo, e' in `tesi/`.

### Il materiale superato

`_superato/` contiene tre gruppi: le sezioni `.tex` gia' incorporate nei
capitoli, le bozze `.txt` (quattro delle sette sono vuote), e cinque figure
del 7 agosto prodotte quando i soggetti erano cinque. **Nulla di quello che
sta li' va aperto per lavorarci.** Il LEGGIMI in quella cartella dice per
ciascun file dove e' finito il suo contenuto.

---

## 2. La tesi

Cinque capitoli piu' introduzione e conclusioni, in `tesi/`. Le etichette `\label{cap:...}` sono stabili: la
numerazione e' cambiata una volta e i riferimenti hanno retto perche' sono
nomi e non numeri. **Non sostituire mai un `\ref` con un numero scritto a
mano.**

| | file | titolo | etichette |
|---|---|---|---|
| | `Introduzione.tex` | prosa continua, senza titoli interni | --- |
| 1 | `Cap1.tex` | Contesto applicativo e formulazione del problema | `cap:contesto` |
| 2 | `Cap2.tex` | Stato dell'arte | `cap:stato_arte` |
| 3 | `Cap3.tex` | Metodologia: dalla stima di posa alla decisione | `cap:metodologia` |
| 4 | `Cap4.tex` | Protocollo di valutazione e risultati sperimentali | `cap:risultati` + alias `cap:protocollo`, `cap:sperimentale` |
| 5 | `Cap5.tex` | Implementazione su dispositivo edge e validazione in ambiente reale | `cap:edge` + alias `cap:campo` |
| | `Conclusioni.tex` | Discussione e conclusioni | `cap:conclusioni` |

**Erano otto fino al 26 agosto.** Protocollo e risultati sono ora il Capitolo 4,
deployment e ambiente reale il Capitolo 5, le conclusioni hanno un file proprio.
`Cap6.tex`, `Cap7.tex` e `Cap8.tex` non esistono piu': le copie di com'erano
stanno in `_superato/capitoli_pre_fusione/`.

**Le etichette dei capitoli fusi sono tenute tutte come alias**, perche' una
ventina di rimandi le usa. Togliendone una si rompono i `\ref` senza guadagnare
nulla.

**Attenzione ai rimandi nei capitoli fusi.** Dopo la fusione, un
`\ref{cap:risultati}` scritto dentro il Capitolo 4 e' un autoriferimento: dice
«nel Capitolo 4» a chi sta leggendo il Capitolo 4. Ne sono stati corretti
cinque il 26 agosto. Prima di aggiungere un rimando, controllare che non punti
al capitolo in cui si sta scrivendo.

### Prima di dichiarare finito un intervento sul testo

```
python tesi/controlla.py
```

Controlla ambienti non chiusi, etichette duplicate, riferimenti orfani,
figure mancanti, **figure senza immagine** e citazioni non definite. Un
ambiente `figure` senza `\includegraphics` **compila**: lascia uno spazio
bianco con la didascalia sotto, ed e' cosi' che quattro figure mancanti sono
rimaste inosservate per settimane.

**Non esiste un compilatore LaTeX su questa macchina.** Il PDF si produce su
Overleaf. Non dichiarare mai «verificato» ciò che è stato solo controllato
staticamente: scrivere quale controllo è stato eseguito.

### Come si scrive, in questo lavoro

Regole ricavate dalla tesi triennale della candidata, e da applicare:

1. **I capitoli di sfondo fissano i concetti che servono dopo, e si
   fermano.** Non anticipano risultati: il risultato si annuncia una volta
   sola, nell'Introduzione.
2. **Enfasi con `\emph` sui termini che si stanno definendo**, non con
   `\textbf`. Il grassetto e' l'eccezione, non il ritmo.
3. **Un titolo ogni ~400 parole.** Sotto le 250 parole un blocco non
   giustifica una `\subsection`: si usa `\paragraph`, che ha un nome ma non
   una voce nell'indice.
4. **Niente formule retoriche**: «conviene», «va detto», «è la ragione per
   cui», trattini lunghi a raffica. Frasi dichiarative, riferimento in fondo.
5. **Dichiarare cosa NON si e' fatto** vale piu' che descriverlo come se lo
   si fosse fatto.

### Bibliografia

`thebibliography` scritto a mano: **una voce non citata viene stampata lo
stesso**, a differenza di bibtex. Per ritirare un riferimento non basta
togliere il `\cite`, va commentata la voce.

---

## 3. Regola vincolante — documentazione viva

Un task non e' concluso finche' la documentazione non e' allineata.

| Se hai fatto questo… | …aggiorna |
|---|---|
| modificato un `.py` | [docs/CHANGELOG.md](docs/CHANGELOG.md) |
| eseguito una run o un'analisi | [docs/EXPERIMENTS.md](docs/EXPERIMENTS.md) |
| trovato un difetto | [docs/ISSUES.md](docs/ISSUES.md), nuova `ISS-1xx` |
| risolto un difetto | ISSUES, sezione «Risolti», con data e intervento |
| preso una scelta metodologica | [docs/DECISIONS.md](docs/DECISIONS.md) |
| cambiato la struttura | [docs/PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md) |

**Registrare anche le run fallite.** Una run che crasha e' un dato:
ripeterla per dimenticanza costa piu' che scriverla.

**Nel campo «Verificato con» va il comando eseguito e il suo esito reale.**
Se una modifica non e' stata provata, scrivere «non verificato».

---

## 4. Vincoli operativi

### Git

`DIP_Project_1` e' un repository dal 25 agosto 2026. Fino al 26 tracciava
soltanto `tesi/`; da quel giorno traccia anche il **codice** --- `config.py`,
`src/`, `pipeline/` e gli script di `deploy_board/` --- perche' sono i file
che producono i numeri della tesi e non avevano storia.

Restano fuori: dataset, modelli, clip, e il CSV delle feature da 71 MB.

**Mai `git add .` o `git add -A`.** Aggiungere sempre i percorsi
esplicitamente. Il `.gitignore` esclude gia' clip, modelli e il CSV delle
feature da 71 MB, con un'eccezione per i punteggi per fold in
`risultati/addestramento/*.npz`, che sono 1,5 MB e permettono di rifare
[EXP-010](docs/EXPERIMENTS.md#exp-010) senza riaddestrare.

**Commit e push solo se richiesti.** Nessun remote configurato.

### Le immagini di persone

Le clip attorno agli allarmi ritraggono familiari identificabili. Restano in
`DIP_PROJECT/sessioni_reali/**/clip/` e nelle sei clip di
`deploy_board/clip_demo/`, tutte escluse da git. **Non copiarle in percorsi
tracciati, non pubblicarle, non allegarle.** Nessun numero del lavoro
dipende da esse: la regola di decisione si applica ai punteggi.

### Ambienti conda

| ambiente | per | note |
|---|---|---|
| `fall_processing` | estrazione feature | MediaPipe 0.10.9 |
| `fall_training` | addestramento | TensorFlow |
| `fall_env` (sulla board) | esecuzione sul dispositivo | cv2 5.0.0, mediapipe 0.10.9 |

Gli script in `pipeline/` girano con qualunque interprete che abbia numpy,
pandas e scikit-learn; `addestra.py` richiede anche TensorFlow.

### La board

Radxa ROCK 4D, utente `rock`, chiave SSH gia' configurata. Dopo ogni
riavvio: `sudo iw dev wlan0 set power_save off`, altrimenti l'SSH cade.
Spegnere con `sudo poweroff` e attendere il LED.

**L'indirizzo non e' fisso, e il 2026-09-06 questo ha fatto danno.** La board
prende un indirizzo dal DHCP. Quel giorno era `192.168.1.13`, ma con la board
spenta il router ha dato **lo stesso indirizzo al calcolatore**: `ping` ha
risposto in 0 ms (rispondeva a se stesso) e `ssh rock@192.168.1.13` ha
prodotto `REMOTE HOST IDENTIFICATION HAS CHANGED`, che sembra un attacco e
invece era il PC che parlava con se stesso. **Non cancellare la voce da
`known_hosts` per far passare quell'errore**: e' l'unica cosa che identifica
la board, ed e' cio' che ha permesso di capire l'equivoco in due minuti.

Per trovarla, si cerca la sua chiave invece del suo indirizzo:

```bash
grep "^192.168.1.13 ssh-ed25519" ~/.ssh/known_hosts   # la chiave attesa
for i in $(seq 2 60); do ssh-keyscan -t ed25519 192.168.1.$i; done 2>/dev/null
```

L'indirizzo su cui compare quella chiave e' la board. Se non compare, la
board e' spenta: nessuna scansione la fa apparire.

---

## 5. Tre cose che cambiano l'interpretazione di qualunque numero

1. **`eventi.csv` nelle sessioni contiene finestre sopra soglia, non
   eventi.** Le due grandezze differiscono di un fattore misurato in
   **44,8**. Gli eventi si ricalcolano con `pipeline/eventi_sessioni.py`, ed
   e' l'unica forma in cui i numeri di campo vanno riportati.

2. **I numeri misurati sul calcolatore non sono i numeri della board.** Lo
   stimatore di posa e' un tracciatore e diverge fra architetture
   ([ISS-106](docs/ISSUES.md#iss-106)): su 56 clip, 55 decisioni identiche e
   una diversa, ed era una caduta vera. Il recall va misurato a bordo.

3. **Sei misure sono ancora a cinque soggetti** e il testo lo dichiara dove
   compaiono: effetto del punto di vista, confronto fra rappresentazioni,
   dimensione del modello, frame rate, scansione di $K$, confronto fra
   stimatori di posa. Non inventare numeri per quelle: dichiarare la
   provenienza.

---

## 6. Lavoro aperto

Aggiornato al **7 settembre 2026**. In ordine di quanto blocca il resto.

**Lo stato degli strumenti:** `python prove/esegui.py` passa **31 prove su 31**
(il file d'oro della geometria e' stato rigenerato il 7 settembre per la
grandezza in piu', dopo aver verificato che le altre 32 non cambiano di un
bit); `python tesi/controlla.py` dice «Nessun problema. Restano 0 figure da
produrre».

1. **Il riaddestramento su `feature_v3.csv` e' in corso**
   ([EXP-025](docs/EXPERIMENTS.md#exp-025)), avviato il 7 settembre alle 09:22:
   cinque architetture su DTW e poi le stesse su DTWH. Finche' non finisce, **le
   tabelle del Capitolo 4 confrontano architetture addestrate su v2 con una
   foresta addestrata su v3**, e non sono confrontabili fra loro. Il registro
   dell'esecuzione e' `risultati/addestramento/log_riaddestramento_v3.txt`; le
   run su v2 sono conservate in `risultati/addestramento/v2/`.

2. **Decidere che cosa gira sulla board**
   ([ISS-139](docs/ISSUES.md#iss-139)), e ora la scelta e' informata: sullo
   stesso v3, aggiungere `A3_h_pavimento` alle dodici colonne porta l'F2 da
   0,807 a **0,866** e i falsi negativi da 249 a **163**, cioe' il 35% in meno
   ([EXP-023](docs/EXPERIMENTS.md#exp-023)). Installarla significa rifare
   l'export, la prova di parita' e una sessione di controllo; non installarla
   significa correggere il Capitolo 3, che dichiara installata una
   configurazione che sul dispositivo non c'e'.

   Da scrivere comunque nel Capitolo 3: **la selezione DTW non avrebbe scelto
   quella grandezza** --- e' 19esima su 33 --- perche' il criterio misura ogni
   grandezza **da sola**. E' un limite del criterio, e va detto dove il criterio
   viene presentato.

3. **Le sedici voci di bibliografia mai verificate.** Sette portano il marchio
   `% VERIFICATO`, tre erano inventate e sono state ritirate
   ([ISS-114](docs/ISSUES.md#iss-114)), cinque non sono citate --- `gru`,
   `lstm`, `noury`, `randomforest`, `rougier` --- e con `thebibliography`
   scritto a mano **vengono stampate lo stesso**. Delle dodici verificate
   finora, quattro affermazioni non hanno retto.

4. **Piu' cadute reali.** Con cinque, l'intervallo di confidenza sul recall va
   da 0,28 a 0,99. E' il limite piu' serio del lavoro. La sessione da cui
   vengono tutte e cinque ha il 25,9% di pose valide, peggio di sessioni che
   sono state scartate: rifarla con l'inquadratura giusta e' l'intervento a
   costo piu' basso. **La prova di durata del 6 settembre non aiuta su questo**:
   e' una misura di durata e di costo, con il 35% di pose e nessuna caduta
   messa in scena.

5. **`tesi/Cap1_riordinato.tex`**, del 5 settembre: una proposta di riordino del
   Capitolo 1 che **non e' inclusa in `tesi.tex`**. Contiene blocchi marcati
   `[NUOVO]` e `[VERIFICA]`, e la figura `fig_popolazione.png`, che oggi non
   compare nel PDF perche' sta solo li'. Va adottata o archiviata:
   `controlla.py` la elenca fra i «non inclusi» a ogni esecuzione.

6. **Cinque figure generate e mai inserite**: `fig_striscia.png`,
   `fig_dtw.png`, `fig_rappr_a1/a2/a3.png`. Le schede `.txt` accanto a ciascuna
   contengono gia' il blocco LaTeX e la frase da aggiungere.

7. **Il residuo di [ISS-137](docs/ISSUES.md#iss-137):** i **4,47 ms per
   finestra** che il Capitolo 4 attribuisce alla board. La board misurata ne fa
   39,04, e [EXP-019](docs/EXPERIMENTS.md#exp-019) misura 4,85 ms **sul
   calcolatore**. Va ritirato o dichiarato come misura sul calcolatore.

**Fatte, e non piu' da fare:** la **prova di durata sulla board** --- 4,59 ore,
nessuna sospensione, 3,1 eventi/ora, 136,65 ms per fotogramma
([EXP-024](docs/EXPERIMENTS.md#exp-024)) --- che chiude
[ISS-113](docs/ISSUES.md#iss-113); la **riestrazione completa** del dataset,
che chiude [ISS-138](docs/ISSUES.md#iss-138); i numeri dell'escursione fra le
due viste, **gia' riscritti nel Capitolo 4** (74,0° contro 33,2°, rapporto
2,23×, 30 su 39 contro 8 su 39) --- il valore 2,44× che questa sezione citava
era quello a cinque soggetti, e non e' quello da usare;
`docs/INDICE_E_STRUTTURA.txt` riscritto sulla struttura a cinque capitoli il 31
agosto; [ISS-111](docs/ISSUES.md#iss-111) risolta e `fig_viewpoint_dist.png`
inserita; la scomposizione della latenza entrata nel Capitolo 5
([ISS-115](docs/ISSUES.md#iss-115)); `fig:due_camere`, l'ultima figura mancante,
composta il 6 settembre.
