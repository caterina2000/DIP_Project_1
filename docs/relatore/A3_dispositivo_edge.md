# A3 — Porting su nodo edge, senza video verso l'esterno

**Che cosa è stato chiesto:** portare la catena completa su un dispositivo a
basso costo, e far sì che nessuna immagine esca dal dispositivo.

**La risposta in una riga:** **fatto, e il 6 settembre finalmente misurato
invece che trascritto** — il dispositivo è **3,6 volte più lento** di quanto la
tesi dichiarasse, ma l'affermazione portante del capitolo regge.

---

## Come ci siamo arrivati, passo per passo

### Passo 1 — Il dispositivo

Radxa ROCK 4D, circa cento euro con una telecamera USB. La catena completa gira
a bordo: telecamera → 640×480 → MediaPipe Pose → 12 grandezze geometriche →
finestra di 22 campioni → foresta casuale → allarme.

### Passo 2 — Verificare che la board calcoli le stesse cose del calcolatore

Prima di ogni misura il programma esegue **tre verifiche di avvio** e le
dichiara una per una nel proprio riepilogo:

1. **impronta del motore geometrico** — il file esiste in due copie, una sul PC
   e una sulla board, tenute allineate a mano. Se divergono, la board calcola
   grandezze diverse *senza che nulla sollevi un errore*. L'impronta attesa sta
   nel `metadata.json`: coincide;
2. **parità sulle finestre** — duecento finestre già calcolate, date in pasto al
   modello sulla board: scarto **0,000e+00**;
3. **parità sui fotogrammi** — la stessa clip elaborata *dall'immagine in poi*
   sulle due macchine. È l'unica che intercetta il difetto seguente, e **non è
   stata eseguita**: vedi Passo 6.

### Passo 3 — Il difetto che le prime due verifiche non vedono

Sulle stesse 56 clip elaborate dai fotogrammi, **55 decisioni su 56 coincidono
e una no — ed è una caduta vera**. La causa non è il classificatore, che è
identico al bit, ma lo stimatore di posa: MediaPipe usa percorsi numerici
diversi su architetture diverse, e la differenza si amplifica perché è un
tracciatore ([ISS-106](../ISSUES.md)).

Conseguenza metodologica, ed è dichiarata nel testo: **il recall del sistema va
misurato a bordo**. I numeri del calcolatore non sono i numeri della board.

### Passo 4 — Il costo per fotogramma: la riserva che è rimasta aperta un mese

Il Capitolo 5 dichiarava: pre-elaborazione 1,21 ms, percezione 33,34 ms
(88,4%), post 0,94 ms, classificatore 2,20 ms, **totale 37,7 ms = 26,5 fps**.

Cercando `33,34` in tutti i file di risultato dei due progetti **non compariva
da nessuna parte** ([ISS-113](../ISSUES.md)): il numero era stato trascritto da
una sessione di terminale. Uno dei numeri portanti del lavoro non era
rifacibile.

La correzione non è stata rifare il banco di prova, ma **strumentare la catena
vera**: `rileva.py` misura ora le quattro fasi con `perf_counter` *dentro
l'esecuzione che produce gli allarmi*, e scrive il bilancio nel proprio
riepilogo. Così non può divergere dalla catena in esercizio.

### Passo 5 — La misura, e la discordanza

Eseguita sulla board con la telecamera collegata, prima su un minuto e poi
**consolidata sulle 4,59 ore** della prova di durata del 6 settembre:

| fase | dichiarato | **misurato (4,59 h)** |
|---|---:|---:|
| pre-elaborazione | 1,21 ms (3,2%) | 0,25 ms (0,2%) |
| **percezione** | 33,34 ms (88,4%) | **116,38 ms (85,2%)** |
| post-elaborazione | 0,94 ms | 0,50 ms |
| classificatore (per fotogramma) | 2,20 ms (5,8%) | **19,51 ms (14,3%)** |
| **totale** | **37,7 ms — 26,5 fps** | **136,65 ms — 7,3 fps** |

**Che cosa regge.** Le proporzioni: percezione ~85% contro ~88% dichiarato. Con
esse regge l'affermazione portante del capitolo — *il collo di bottiglia è la
percezione, non la classificazione* — e la sua conseguenza: la scelta del
classificatore non determina la frequenza di esercizio.

**Che cosa non regge, e perché il numero sbagliato era quello in tesi.** Il file
di configurazione del progetto dichiara **da sempre** che la board regge circa
nove fotogrammi al secondo, ed è su quel presupposto che il dataset viene
sottocampionato in addestramento. **I 7,3 fps misurati sono coerenti con il
progetto; i 26,5 dichiarati non lo erano mai stati**, e nessuno aveva mai
confrontato i due numeri fra loro.

**Un'obiezione verificata e falsificata.** «La misura era a stanza vuota, dove
lo stimatore lavora diversamente.» Ripetuta con un soggetto in scena il costo
**sale** da 126,0 a 144,1 ms, perché al rilevatore di persone si aggiunge il
modello dei landmark. Il divario si allarga invece di chiudersi.

### Passo 6 — La riservatezza, e il difetto che ci si è nascosto dentro

Il registratore salva in continuo **soltanto posa e punteggi**. Dal prototipo
era stata tolta una registrazione video continua che contraddiceva l'argomento
della tesi.

**Ma il 7 settembre è emerso che oggi non salva immagini affatto**
([ISS-142](../ISSUES.md)), mentre la sua documentazione afferma che le clip
attorno agli allarmi si possono attivare. Non si possono: il codice non le
scrive. Il registratore di agosto le salvava — ±10 s attorno a ogni allarme,
con un tetto giornaliero — ed è con quelle che gli allarmi delle sessioni
domestiche sono stati guardati uno per uno.

Ne segue che la terza verifica di avvio non ha potuto girare, e che i
quattordici allarmi della prova di durata **non sono verificabili**.

### Passo 7 — L'acceleratore neurale, risultato negativo tenuto nel testo

L'NPU della board **non viene usata**: farci girare il modello costa **0,216 di
F2**, mentre dimezzare la frequenza dei fotogrammi ne costa 0,041. È un
risultato negativo su un lavoro consistente, e resta nel testo perché è
un'informazione utile a chi volesse rifare la stessa scelta.

---

## Che cosa resta aperto

- **I 4,47 ms per finestra** che il Capitolo 4 attribuisce alla board. La board
  misurata ne fa **39,04**, e il costo misurato *sul calcolatore* è 4,85 ms:
  sembra un numero del PC etichettato come numero della board
  ([ISS-137](../ISSUES.md)). Va ritirato o dichiarato per quello che è.
- **Il salvataggio delle clip** va portato in `rileva.py` prima della prossima
  sessione lunga, altrimenti ogni sessione futura produrrà numeri non
  verificabili.

---

## Dove guardare

| | |
|---|---|
| bilancio misurato | `risultati/sessioni/20260906/notte_20260906_1523/notte_20260906_1523_riepilogo.json` |
| parità PC/board | `risultati/board/` |
| script | `deploy_board/rileva.py`, `pipeline/esporta_board.py`, `pipeline/latenza.py` |
| registro | [EXP-016](../EXPERIMENTS.md), [EXP-024](../EXPERIMENTS.md), [ISS-113](../ISSUES.md), [ISS-137](../ISSUES.md), [ISS-106](../ISSUES.md), [ISS-142](../ISSUES.md) |
| nella tesi | Capitolo 5, `tab:costo_misurato` |
