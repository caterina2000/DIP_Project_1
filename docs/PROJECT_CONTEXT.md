# PROJECT_CONTEXT — DIP_Project_1

Mappa di cosa sta dove, e perche'. Aggiornato al 2026-08-26.

---

## Il lavoro in due parole

Rilevare cadute da video RGB su un dispositivo edge da ~100 euro, senza che
nessuna immagine esca dal dispositivo. MediaPipe Pose estrae 33 punti del
corpo, da quelli si ricavano grandezze geometriche, e un classificatore decide
su finestre di ~2,4 secondi.

**La domanda del classificatore e' «sta cadendo?», non «e' a terra?»**
([DEC-107](DECISIONS.md#dec-107)). E' la scelta che fa la differenza fra un
sistema usabile e uno che suona per un pomeriggio intero su due persone
sedute sui divani.

---

---

## Che cosa e' cambiato fra il 22 e il 26 agosto

Sono i giorni in cui questo progetto e' diventato quello principale. Chi
riprende il lavoro trova una struttura diversa da quella descritta piu' sotto.

### La tesi e' qui

`tesi/` contiene il testo: otto capitoli, le figure, e `controlla.py`. Prima
stava in `DIP_PROJECT/tesi/`, dove non c'e' piu' nulla. Lo spostamento e'
stato verificato con `diff -rq` prima della rimozione: 43 file identici.

`pipeline/figure_tesi.py` scrive ora in `tesi/figure/` dello stesso progetto:
la destinazione non attraversa piu' il confine fra due cartelle.

### Cinque capitoli, non otto

Il 23 agosto e' stato scritto il capitolo sullo stato dell'arte, che non
esisteva, portando i capitoli a otto. Il 26 sono diventati **cinque**:
protocollo e risultati insieme, deployment e ambiente reale insieme, le
conclusioni in un file proprio. Le etichette `\label{cap:...}` sono state
tenute tutte come alias e tutti i `ef` si risolvono da soli.

La copia dei capitoli com'erano prima della fusione sta in
`_superato/capitoli_pre_fusione/`, con il LEGGIMI che dice dove e' finito
ciascuno.

### Le sessioni domestiche sono qui

`risultati/sessioni/` contiene le **dodici** sessioni registrate sulla board:
punteggi per finestra, riepiloghi, controlli di sanita'. In tutto 4,4 MB.
**Le clip non sono state copiate**: sono immagini di persone identificabili e
non servono a riprodurre alcun numero.

`pipeline/eventi_sessioni.py` preferisce ora questa copia e ripiega sulla
cartella di raccolta del progetto storico, dichiarando in testa da dove sta
leggendo.

Il LEGGIMI in quella cartella contiene l'indice delle dodici sessioni e la
tabella di quali producono quali risultati. Il dato che rende visibile: le sei
sessioni del **10 agosto** hanno pose valide fra lo 0,6% e il 39,8% e non
entrano in alcun risultato — era la telecamera posizionata male, ed e' il
motivo per cui esiste il protocollo di ripresa.

### Git

Il progetto e' un repository dal 25 agosto, e traccia soltanto `tesi/`. Il
`.gitignore` esclude clip, modelli e il CSV delle feature, con un'eccezione
per i punteggi per fold.

### `_superato/`

Materiale sostituito, conservato ma non da usare: le sezioni `.tex` gia'
incorporate nei capitoli, le bozze `.txt`, e le figure a cinque soggetti. Il
LEGGIMI dice per ciascun file dove e' finito il suo contenuto.

---

## Lo stato del testo

| | capitolo | parole | sez. | sottosez. | parole per titolo |
|---|---|---:|---:|---:|---:|
| | Introduzione | 966 | --- | --- | prosa continua |
| 1 | Contesto applicativo e formulazione del problema | 2.858 | 4 | 4 | 357 |
| 2 | Stato dell'arte | 2.507 | 5 | 0 | 501 |
| 3 | Metodologia | 9.076 | 7 | 13 | 453 |
| 4 | Protocollo di valutazione e risultati sperimentali | 7.872 | 9 | 7 | 492 |
| 5 | Implementazione su edge e validazione in ambiente reale | 7.133 | 9 | 9 | 396 |
| | Conclusioni | 2.103 | 5 | 0 | 420 |
| | | **33.9k** | **39** | **33** | |

Il criterio e' un titolo d'indice ogni ~400 parole, e dal 26 agosto **tutti i
capitoli lo rispettano**. Le regole di scrittura sono in
[../CLAUDE.md](../CLAUDE.md), sezione 2.

**Nessun testo e' stato cancellato** nella riorganizzazione: 129 declassamenti
e rinomine, zero tagli. La tesi resta a 33.9k parole invece delle 30k previste
perche' tutto cio' che e' stato misurato e' rimasto dentro. La compressione a
costo piu' basso, se servisse, e' spostare le trentadue grandezze in
appendice: ~700 parole senza perdere niente.


## Due progetti, due ruoli

| | |
|---|---|
| **DIP_Project_1** (questo) | modellazione: feature, selezione, architetture, valutazione di laboratorio ed esterna |
| **DIP_PROJECT** (`../DIP_PROJECT`) | ambiente storico e **di campo**: sessioni domestiche, board, occlusioni reali, YOLOv8, costo edge |

Non e' una divisione provvisoria da sanare: e' un **vincolo dei dati**.

Le sessioni domestiche contengono soltanto le dieci colonne A3 che il
registratore scriveva, e le immagini esistono solo attorno agli allarmi (scelta
di privacy: sono l'unico dato identificabile del progetto). Il progetto nuovo
lavora su 32 grandezze con integrali causali e sul sottoinsieme scelto dal DTW:
**su quei dati non puo' fare meglio del vecchio**, perche' le colonne che gli
servono non ci sono.

Riscrivere gli script di campo contro l'API nuova produrrebbe codice piu'
pulito che calcola gli stessi identici numeri. Si scrivera' direttamente qui
quando ci saranno sessioni registrate con il motore nuovo.

**Cosa NON si duplica:** `sessioni_reali/` (10,6 ore, 58.815 fotogrammi di
clip), i dataset grezzi, i modelli. Gli script che servono li leggono dal
progetto storico con percorso relativo, e `SESSIONI_REALI` nell'ambiente
permette di spostarli.

---

## Struttura

```
config.py                   ogni costante, una volta sola
src/
  geometry.py               32 grandezze, integrali CAUSALI (buffer circolare)
  dati.py                   finestre, LOSO, scaler, tre modi di etichettatura
  etichettatura.py          da etichetta per fotogramma a etichetta di finestra
  modelli.py                GRU, LSTM, CNN, Transformer, foresta — interfaccia unica
  valutazione.py            metriche, soglia, F-beta
  dtw.py                    separabilita' per camera, criterio del minimo
pipeline/
  estrai_feature.py         UP-Fall  -> 32 grandezze
  estrai_urfall.py          UR-Fall  -> stesse 32 grandezze
  mappa_omnifall.py         etichette OmniFall su UP-Fall
  analisi_dtw.py            selezione del sottoinsieme, per camera
  addestra.py               LOSO completa, metadati, probabilita' salvate
  soglia.py                 confronto fra regole di soglia
  confronto_compiti.py      evento / stato / allarme
  valuta_esterno.py         addestra su UP-Fall, misura su UR-Fall
  occlusioni.py             mascheramento controllato dei landmark
  eventi_sessioni.py        metriche di EVENTO sulle sessioni  (legge il storico)
  rietichetta_urfall.py     tre classi da annotazioni originali (legge il storico)
risultati/
  dtw/  addestramento/  compiti/  esterno/  occlusioni/
  campo/                    JSON importati dall'ambiente storico
  laboratorio/              metadati delle run a 10 soggetti
docs/
  figure/                   12 figure, rigenerate 2026-08-21
  EXPERIMENTS · ISSUES · DECISIONS · CHANGELOG
```

---

## I numeri di riferimento

**Laboratorio** — UP-Fall, LOSO su 10 soggetti, camera 1:

| configurazione | F2 |
|---|---:|
| A3 | 0,898 ± 0,075 |
| A3h (+ altezza dal pavimento) | 0,931 ± 0,051 |
| A3i (+ integrali) | 0,943 ± 0,064 |
| A3i + controesempi domestici | 0,953 ± 0,055 |

**Le tre definizioni del compito** — foresta, sottoinsieme DTW:

| compito | F2 | falsi allarmi sui distesi volontari |
|---|---:|---:|
| **evento** (`fall`) | **0,831** | **0,0%** |
| stato (`fallen`) | 0,704 | 12,5% |
| allarme (`fall` O `fallen`) | 0,810 | 13,1% |

**In casa** — eventi/ora, persistenza 5, sospensione 30 s:

| compito | casa studente | casa nonni | cadute |
|---|---:|---:|---:|
| evento | 0,9 | **5,3** | 3/5 |
| stato | 15,2 | 104,2 | 0/5 |
| allarme | 23,2 | 105,1 | 4/5 |

Riferimento di letteratura: **0,049 eventi/ora** (studio longitudinale, 15.500
ore, 16 anziani). Il valore 0,4/ora usato in precedenza non trova riscontro
([ISS-050](../../DIP_PROJECT/docs/ISSUES.md#iss-050)).

---

## Cosa e' stabilito, e con che forza

| affermazione | evidenza |
|---|---|
| nessuna architettura e' distinguibile dalla GRU | t-test appaiato, 10 fold, tutti \|t\| < 2,26 |
| servirebbero 113 soggetti per separare GRU da LSTM, 2 per separare due regole di etichettatura | analisi di numerosita' |
| il compito «evento» azzera i falsi allarmi sui distesi volontari | 2.234 finestre, 0,0% |
| gli integrali dividono i falsi allarmi per 14 a parita' di dati | 139,9 -> 9,8 |
| i controesempi trasferiscono fra abitazioni | ~2x in entrambe le direzioni |
| il trasferimento a UR-Fall fallisce, e non per calibrazione | PR-AUC 1,8x sopra la prevalenza |
| nessun gruppo di landmark e' critico | perdita massima 0,020 di F2, un quarto della dispersione |
| la lunghezza della finestra non conta fra 2,4 e 4,9 s | tutti \|t\| < 1,3 |

---

## Quello che manca

- riscrittura di quattro paragrafi della relazione (linguaggio, trade-off, narrazione)
- prova lunga sulla board **dopo** la correzione del debounce
  ([ISS-051](../../DIP_PROJECT/docs/ISSUES.md#iss-051))
- ~~schierare sulla board la configurazione corretta~~ **fatto il 21 agosto**:
  `deploy_board/metadata.json` dichiara compito «evento», sottoinsieme DTW a
  dodici colonne, K = 31, finestra 22, soglia 0,50, dieci soggetti. La nota
  precedente («oggi gira A3 a dieci colonne») era rimasta ferma a prima
  dell'esportazione
- piu' cadute reali: con cinque, l'intervallo di confidenza sul recall va da
  0,28 a 0,99 e non permette di distinguere nulla
