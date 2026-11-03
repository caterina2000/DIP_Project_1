# Capitolo 3 — che cosa il codice decide, e che cosa il capitolo dice

Scritto il **2026-09-22**, prima di passare ai Capitoli 4 e 5.

La domanda a cui questo documento risponde è una sola: **ogni scelta di metodo
che sta nel codice è dichiarata nel capitolo, e ogni cosa dichiarata nel
capitolo corrisponde al codice?** Finché la risposta non è sì, i Capitoli 4 e 5
non sono impostabili, perché riportano i risultati di un metodo che non è
descritto per intero.

---

## 0. Il blocco da sciogliere per primo: ci sono due Capitoli 3

Esistono **due versioni divergenti**, e nessuna contiene tutto.

| | la stesura della candidata | `tesi/Cap3.tex` su disco |
|---|---|---|
| prosa | riscritta, voce propria, più scorrevole | più vecchia in alcune sezioni |
| sezioni sul classificatore e sull'allarme | **assenti** | presenti |
| dichiarazione del leakage | due righe | sezione con due misure |
| figure | 6, due con segnaposto | 11, tutte prodotte da codice |

**Le due vanno unite, e la base giusta è la stesura della candidata**: la prosa
è sua ed è migliore. Ciò che va portato dentro è elencato al § 1.

> **Nota sulla completezza di questo audit.** Il testo incollato si interrompe
> a metà di «Robustezza e limiti». Le sezioni su **pavimento, DTW, finestre e
> definizione del compito** non sono state viste e **non sono state
> controllate**: quanto segue le riguarda solo dove il codice le tocca.

---

## 1. Che cosa manca alla stesura, e non è opzionale

Cinque blocchi, in ordine di quanto pesano.

### 1.1 I classificatori e il protocollo di addestramento — **richiesta esplicita del professore**

> «nell'indice non vedo una sezione esplicita sui classificatori e sul
> training. Dal momento che confronti sei architetture, devi descrivere almeno:
> input dimensionality, architettura, numero di parametri, hyperparameters,
> loss, optimizer, stopping criterion, random seed, numero di run.»

Nella stesura le sei architetture compaiono **in una riga sola**, nella
panoramica: «Random Forest, LSTM, GRU, convoluzione temporale 1D, Transformer e
GNN». Struttura, costo e iperparametri non ci sono da nessuna parte.

Nel codice ci sono tutti, in `src/modelli.py`:

| modello | struttura | parametri |
|---|---|---:|
| GRU | due strati ricorrenti, 64 e 32 unità, dropout 0,3 | 24.483 |
| LSTM | identica, cambia la cella | 32.227 |
| CNN 1D | due blocchi conv. nucleo 5 (64, 128), BN, pooling 2, dropout | 46.147 |
| Transformer | proiezione a 64, codifica posizionale appresa, 1 blocco a 4 teste | 34.499 |
| Grafo | due blocchi spazio-temporali, adiacenza appresa fra 12 nodi | 12.323 |
| Foresta | 50 alberi, profondità libera, su 72 numeri per finestra | 12.760 nodi |

E il protocollo: entropia incrociata categorica, Adam a $10^{-3}$, 40 epoche,
lotto 16, seme 42, **una run per fold**, arresto anticipato sull'area sotto la
curva di allarme con pazienza 8 e ripristino dei pesi migliori, riduzione del
passo di 0,5 dopo 4 epoche.

**Quattro cose che solo il codice sa, e che vanno dette:**

1. **L'uscita è sempre softmax**, anche nel caso binario dove basterebbe un
   valore. Serve perché la riduzione a probabilità di allarme
   ($1 - p(\text{normale})$) sia la stessa operazione per tutti i modelli e per
   tutte le formulazioni del compito.
2. **Fra due e tre classi cambia solo l'ultimo strato**: il confronto fra
   formulazioni non misura anche una differenza di capacità.
3. **L'arresto anticipato sorveglia l'ordinamento, non la decisione.** Con la
   soglia fissata a priori, dall'addestramento non serve un modello tarato su
   0,50 ma uno che ordini bene le finestre.
4. **La rete a grafo ha per nodi le dodici grandezze, non i giunti.** È una
   scelta obbligata dal confronto, con un limite che ne segue: senza topologia
   anatomica, il vantaggio tipico di una rete a grafo non c'è.
   **Il professore ha chiesto di spostare qui questo punto dal Capitolo 2.**

### 1.2 Dalla finestra all'evento di allarme — **richiesta esplicita del professore**

> «una sezione esplicita, dove definisci threshold, persistence, minimum number
> of consecutive positives, event merging, refractory interval, inizio/fine
> dell'evento. Questo è importante ai fini di rendere ben interpretabile il
> Capitolo 5.»

Nella stesura c'è una frase nella panoramica: «genera l'allarme quando vengono
riconosciute cinque finestre positive consecutive». Le altre cinque voci non
ci sono.

Dal codice (`deploy_board/rileva.py:1016`, `pipeline/eventi_sessioni.py:127`):

| voce | valore |
|---|---|
| soglia | 0,50, fissata a priori |
| positivi consecutivi | 5; **la successione si azzera alla prima finestra sotto soglia** |
| istante dell'allarme | la **quinta** finestra, non la prima |
| fusione | le positive successive non aprono nuove segnalazioni |
| refrattario | **30 s dall'ultimo allarme emesso**, non dall'ultima finestra positiva |
| fine dell'evento | non definita: la segnalazione è un istante |

⚠ **Due di queste erano scritte al contrario nel file su disco**, e sono state
corrette il 2026-09-22 ([ISS-175](ISSUES.md#iss-175)). L'istante dell'allarme
sbagliato **sottostimava la latenza** del termine di persistenza — 0,997 s su
3,778 s, il 26,4% secondo `tab:latenza` del Capitolo 5.

E il punto che il professore chiama uno dei messaggi forti della tesi: **falsi
positivi per finestra e allarmi per ora sono due livelli diversi**, non due
modi di dire la stessa cosa. Una raffica di cinquanta finestre consecutive è
una segnalazione sola; cinquanta finestre isolate non ne producono nessuna.

### 1.3 Il leakage: cinque operazioni, non due

La stesura dice, in fondo a § dati e preprocessing, che la normalizzazione è
per fold e che la selezione DTW no. È vero ma incompleto. Il professore chiede
di dichiarare **il procedimento corretto** e di passarlo in rassegna operazione
per operazione.

| operazione | calcolata su | vede il test? |
|---|---|---|
| normalizzazione | soli soggetti di addestramento del fold | no |
| scelta della soglia | **nessun dato**: fissata a priori a 0,50 | no |
| iperparametri del modello | **nessun dato**: fissati a priori | no |
| parametri della rappresentazione | **$K$ scelto per scansione** | **sì** |
| selezione con DTW | **tutti i soggetti, una volta sola** | **sì** |

Le due violazioni sono **misurate**, e vanno in direzioni opposte:

- **DTW** ([EXP-044](EXPERIMENTS.md#exp-044)): 0 fold su 10 riproducono la
  selezione adottata, Jaccard 0,769 → prestazioni **sopravvalutate**.
- **$K$** ([EXP-045](EXPERIMENTS.md#exp-045)): 9 fold su 10 scelgono $K=45$ e
  fanno **meglio** di 0,026 → prestazioni **sottostimate** sul criterio di
  laboratorio.

### 1.4 Il filtro di ridondanza del DTW

Il criterio non è «le dodici col punteggio più alto». Si scorre la classifica e
si tiene una grandezza solo se la correlazione con **tutte** le già scelte resta
sotto 0,85, misurata sui soli fotogrammi con posa. **Quattro grandezze meglio
piazzate sono escluse per ridondanza**, e senza dirlo il lettore non capisce
perché la seconda in classifica non c'è.

### 1.5 Le tabelle riassuntive che il professore ha chiesto

- **`tab:dati`** — che cosa entra nell'esperimento, riga per riga. Lui l'ha
  chiesta con parole precise: «devi spiegare esattamente quali dati entrano nel
  tuo esperimento».
- **`tab:pipeline`** — ingresso, uscita e sezione di ogni passaggio. È il filo
  del capitolo: da centinaia di migliaia di pixel a dodici numeri per finestra.

---

## 2. Codice → metodologia: la copertura, voce per voce

✅ nella stesura · ⚠ presente ma impreciso · ❌ assente · — non controllabile
(testo troncato)

### Estrazione

| scelta nel codice | stato |
|---|---|
| MediaPipe `solutions`, complessità 1, confidenze 0,5 | ✅ |
| uno stimatore **per ripresa**, stato azzerato | ✅ ben spiegato |
| $\Delta t$ dai riferimenti temporali veri | ✅ |
| nessuna interpolazione delle coordinate | ✅ |
| `ha_posa`, feature a zero, stato temporale azzerato | ✅ |
| derivate seconde rimosse | ✅ |
| nessun filtro temporale | ✅ |
| A1 nove, A2 cinque, A3 nove → 23 | ✅ |
| tre integrali per rappresentazione → 32 | ⚠ la frase sul conteggio sembra persa nella riscrittura |
| altezza dal pavimento → 33 | — |
| retta del pavimento: ingombro più alto che largo (rapporto 1,6), 50 osservazioni minime, `polyfit`, ricalcolo a fine telecamera | — |

### Selezione

| scelta nel codice | stato |
|---|---|
| z-score per curva, ricampionamento a 200 | — |
| banda $|i-j|\leq 10$ | — |
| punteggio $S=\mu_{FA}/\mu_{\text{intra}}$ | — |
| robusto = **minimo** fra le due viste, non media | — |
| **filtro di ridondanza avido, soglia 0,85** | ❌ § 1.4 |
| `use_pruning=False` ([ISS-168](ISSUES.md#iss-168)) | ❌ vale una riga: è un difetto trovato e corretto |

### Finestre, etichette, normalizzazione

| scelta nel codice | stato |
|---|---|
| $L=22$, passo 2 | — |
| sottocampionamento uno su due | ✅ |
| finestre solo dentro tratti di posa continua | ✅ |
| $K$-su-$M$: transizione 5 su 8, a terra 10 su 15 | — |
| tre formulazioni del compito, $y_{\text{train}}=-1$, $y_{\text{allarme}}$ | — |
| `log1p` con segno su 14 colonne prima della standardizzazione | ✅ ma in Cap4, ed è il posto giusto |

### Modelli e decisione

| scelta nel codice | stato |
|---|---|
| sei architetture, struttura e parametri | ❌ § 1.1 |
| softmax sempre; solo l'ultimo strato cambia fra 2 e 3 classi | ❌ |
| pesi di classe inversi alla frequenza, media 1 | ❌ |
| arresto anticipato sull'AUC di allarme | ❌ |
| Adam $10^{-3}$, 40 epoche, lotto 16, seme 42, una run per fold | ❌ |
| foresta: riassunto a 6 statistiche × 12 = 72 numeri | ❌ |
| $p_{\text{allarme}} = 1-p(\text{normale})$ | ❌ |
| soglia 0,50 **fissa a priori** ([DEC-105](DECISIONS.md#dec-105)) | ❌ |
| regola di allarme completa | ❌ § 1.2 |

---

## 3. Un'imprecisione trovata nel Capitolo 4

`sec:normalizzazione` dice che il logaritmo si applica «per le grandezze che
soddisfano **il criterio previsto** nella fase di preprocessing».

**Un criterio non esiste.** `src/dati.py:170` definisce `ASIMMETRICHE` come un
**elenco fisso di 14 nomi**: le nove integrali più `A2_vel_ang_tronco`,
`A2_testa_vel`, `A3_hip_vel`, `A3_testa_vel_rel`, `A3_larghezza`. Sono state
scelte guardando le distribuzioni, non da una regola automatica.

Va riformulato: o si dichiara l'elenco, o si dichiara che è stato compilato a
mano. Come sta adesso promette una procedura che non c'è.

---

## 4. Le figure: quali stanno in metodologia

Il criterio della candidata — **figure che spiegano, non figure che misurano**
— è quello giusto. Sul file a disposizione la situazione è questa.

**Metodologiche, tutte da tenere:**

| figura | che cosa spiega |
|---|---|
| `fig_pipeline` | la catena intera, dal fotogramma all'allarme |
| `fig_tracciatore` | perché lo stimatore è un tracciatore e va azzerato |
| `fig_landmark` | quali punti usa ciascuna rappresentazione |
| `fig_momenti_a1/a2/a3` | che cosa misura ogni rappresentazione, in due istanti |
| `fig_rappresentazioni` | le tre letture della stessa posa, a confronto |
| `fig_striscia` | perché una grandezza accumulata è più regolare di una derivata |
| `fig_pavimento` | come si stima la retta del pavimento, e cos'è $h_{\text{pav}}$ |
| `fig_dtw_allineamento` | che cosa allinea il DTW e che cosa impedisce la banda |

Nessuna figura di risultati è finita in Cap3: non c'è niente da spostare.

**Due segnaposto da chiudere nella stesura:**
- `\caption{Caption}` con `\label{fig:placeholder}` sulla figura dei landmark;
- il blocco `\hl{}` sotto `fig:striscia`, che contiene già il testo buono.

**Attenzione alla lingua.** Il capitolo usa le varianti **inglesi** delle
figure con testo sovrapposto (`_en`). La stesura chiama `fig_momenti_a1.png` e
`fig_spostamento.png` senza suffisso: vanno allineate.

---

## 5. Il testo: che cosa correggere

### 5.1 Errori di fatto

| dove | dice | è |
|---|---|---|
| `tab:etichette` | 111.591 con posa valida | **111.570** |
| § stima della posa | «posa valida nel **95,5%**» | **95,9%** — e contraddice la tabella sopra |
| § visibilità | naso, spalle, anche «superiori a **0,99**» | **0,98** |

### 5.2 `\num{}` con le virgole — rompe i numeri

Il preambolo ha `\sisetup{output-decimal-marker={,}}`. Scrivere
`\num{116,362}` rischia di produrre **116,362** invece di 116.362. Tutto il
resto della tesi scrive `\num{116362}`.

### 5.3 Citazioni: un problema sistematico, con soluzione meccanica

`\cite{SA}`, `\cite{BL}`, `\cite{MP}` **non esistono**. Ma le voci ci sono con
il nome lungo — e questo spiega anche i 7 riferimenti rotti che `controlla.py`
segnala da settimane:

| chiave usata | voce reale |
|---|---|
| `SA` | `samanta` — Samanta & Chanda, pose tracking |
| `BL` | `blazepose` — visibility e modalità video |
| `MP` | `mediapipe` — world landmark |
| `IS` | `istat2026` |
| `PA` | `passi` |
| `MU` | `mubashir` |
| `LI`, `LIN` | `lin` |
| `GU` | `gutierrez` |
| `HO` | **nessuna**: va scritta |

Rinominando si chiudono 7 problemi su 8. `HO` è l'unico che richiede una voce
nuova — e le viene attribuito contenuto diverso in tre punti (i 18 fps di
UP-Fall, i parametri GRU/LSTM, la rassegna skeleton-based): va deciso che cosa
cita davvero.

### 5.4 Segnaposto

`\ref{sec}` in quattro punti, `\ref{cap}` in uno, `fig:placeholder`, e
`\label{sec:dati e preprocessing}` — **con gli spazi dentro**, ed è pure
referenziato. Va rinominato `sec:dati`.

### 5.5 Ripetizioni e frasi da sciogliere

- «\(K\) indica però un numero di campioni e non una durata fissa» compare
  **due volte** nella stessa sottosezione, in forma breve e in forma lunga.
- Frase rotta: «Le rappresentazioni utilizzate nel lavoro si basano non
  utilizzano i landmark delle mani e si basano principalmente su…»
- Frase rotta: «Un valore elevato di \(\rho_1\) che la grandezza tende a…»
  (manca il verbo)
- «Ragione per cui il si tiene traccia…»
- «mantenendo separati i di addestramento…»
- «e dichiarano per cascuna» → *dichiarando per ciascuna*
- «evento di allerme» · «della posae» · «l'insieme inziale» · «Nessuna
  regstrazione» · «in presenza di pù persone» · «rumore dei landamark» ·
  «si è introdotto tre grandezze» · «si è eseguito una prova» · «vengono
  confrontate tre insiemi» · «delle coordiante» · «Tale misurà»
- «la visibility 26.548 fotogrammi» → *su 26.548*
- `(F\_2)-score` → `$F_2$`
- `Figura\ref{...}` senza spazio → `Figura~\ref{...}`
- «perchè» → *perché*

### 5.6 Un'affermazione da rintracciare

> «Ginocchio e caviglia del lato più lontano dalla telecamera presentano una
> visibility al di sotto di 0,5 in più della metà dei fotogrammi»

Non l'ho trovata negli artefatti. Se viene da EXP-052 va citata; altrimenti va
tolta o misurata.

---

## 6. L'ordine in cui conviene procedere

1. **Unire le due versioni**, prendendo la stesura come base e portandoci
   dentro i cinque blocchi del § 1. È il passo che sblocca tutto il resto.
2. **Le correzioni meccaniche** del § 5.1–5.4: numeri, `\num{}`, citazioni,
   segnaposto. Chiudono anche 7 degli 8 problemi di `controlla.py`.
3. **La rilettura** del § 5.5.
4. Solo allora i Capitoli 4 e 5, che a quel punto hanno un metodo completo da
   cui riportare i risultati.

---

## 7. Che cosa resta da controllare

Le sezioni **pavimento, DTW, finestre e definizione del compito** non erano nel
testo esaminato. Vanno confrontate con il codice allo stesso modo, in
particolare su: la soglia 1,6 dell'ingombro e le 50 osservazioni minime per la
retta del pavimento; il minimo fra le due viste; la soglia 0,85 del filtro di
ridondanza; i parametri $K$-su-$M$ dell'etichettatura; le tre formulazioni del
compito con $y_{\text{train}}=-1$.
