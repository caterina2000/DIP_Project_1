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

Radxa ROCK 4D, `rock@192.168.1.13`, chiave SSH gia' configurata. Dopo ogni
riavvio: `sudo iw dev wlan0 set power_save off`, altrimenti l'SSH cade.
Spegnere con `sudo poweroff` e attendere il LED.

---

## 5. Tre cose che cambiano l'interpretazione di qualunque numero

1. **`eventi.csv` nelle sessioni contiene finestre sopra soglia, non
   eventi.** Le due grandezze differiscono di un fattore misurato in
   **47,8**. Gli eventi si ricalcolano con `pipeline/eventi_sessioni.py`, ed
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

In ordine di quanto blocca il resto.

1. **La prova di durata sulla board.** E' l'ultima richiesta esplicita del
   relatore ancora aperta. `deploy_board/rileva.py` ha ora il doppio orologio
   e dichiara la sospensione della macchina, quindi il difetto che aveva
   invalidato silenziosamente il primo tentativo e' rilevabile. Nella stessa
   sessione si chiude anche [ISS-113](docs/ISSUES.md): il bilancio del costo
   per fotogramma esce dal `riepilogo.json` della prova stessa.
2. **Le sedici voci di bibliografia mai verificate.** Sette portano il marchio
   `% VERIFICATO`, tre erano inventate e sono state ritirate
   ([ISS-114](docs/ISSUES.md)), cinque non sono citate. Le restanti sostengono
   numeri che compaiono nell'Introduzione e non sono mai state controllate
   sulla fonte. Quando le sette furono verificate, due affermazioni su sette
   non ressero.
3. **[ISS-111](docs/ISSUES.md)** --- il rapporto fra le due viste vale 1,99
   nel file e 1,90 nel testo. Finche' non e' risolto, `fig_viewpoint_dist.png`
   non va inserita.
4. **Tre figure mancanti** nel Capitolo 4. Due sono generate ma bloccate dal
   punto precedente e dal fatto che vengono da cinque soggetti; la terza va
   composta dai fotogrammi delle due telecamere, scegliendo l'istante.
5. **Piu' cadute reali.** Con cinque, l'intervallo di confidenza sul recall va
   da 0,28 a 0,99. E' il limite piu' serio del lavoro. La sessione da cui
   vengono tutte e cinque ha il 25,9% di pose valide, peggio di sessioni che
   sono state scartate: rifarla con l'inquadratura giusta e' l'intervento a
   costo piu' basso.
6. **`docs/INDICE_E_STRUTTURA.txt` da riscrivere** prima di mandarlo al
   relatore: contiene ancora l'indice a otto capitoli e una domanda su una
   fusione che non si fa piu'. Il relatore rientra il **2 settembre**.
