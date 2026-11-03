# Mappa: codice ↔ capitolo ↔ esperimento ↔ difetto

Serve a rispondere a due domande che tornano di continuo: *«questo numero da dove
viene?»* e *«se tocco questo file, quale parte della tesi cambia?»*

---

## 1. I file di libreria (`src/`)

| file | che cosa fa | dove finisce nella tesi | EXP / ISS / DEC |
|---|---|---|---|
| `src/geometry.py` | le 32 grandezze, un fotogramma alla volta, con buffer circolare per gli integrali | Cap. 3 §§ rappresentazioni, integrali | ISS-100 (periodo 180°), ISS-104 (A2 degenere), EXP-001/003/007 |
| `src/dtw.py` | distanza DTW vincolata, punteggio di separabilità, classifica per camera | Cap. 3 § DTW | ISS-101 (banda), DEC-101 (minimo), DEC-102 (ricampionamento), EXP-002/004/005/008 |
| `src/etichettatura.py` | criterio K-su-M, tre modi di etichettatura | Cap. 3 § etichettatura | ISS-112 (soglie in due posti), DEC-104 |
| `src/dati.py` | finestre dentro tratti continui, doppia etichetta, LOSO, scaler | Cap. 4 §§ partizionamento, normalizzazione | ISS-106 (indirettamente), EXP-009 |
| `src/modelli.py` | GRU, LSTM, CNN 1D, Transformer, **rete a grafo**, foresta dietro un'interfaccia unica | Cap. 4 § architetture | EXP-011, EXP-018 |
| `src/valutazione.py` | $F_\beta$, scelta della soglia, aggregazione fra fold | Cap. 4 §§ metrica, soglia | DEC-105, EXP-010 |

### Le costanti — `config.py`

**Unica fonte.** Nel progetto precedente `SEQUENCE_LENGTH` valeva **45 in config,
75 in `demo_realtime.py`, 39 nei metadati della run migliore**; e `FPS` valeva 18,
30, 15 e 20 in quattro file. *Le feature dinamiche si dividono per $dt = 1/\text{FPS}$,
quindi lo stesso movimento produceva numeri diversi a seconda di quale file lo
calcolava.*

| costante | valore | dove pesa |
|---|---:|---|
| `FPS_DATASET` | 18,0 | Cap. 3 (derivate), Cap. 4 (frame rate) |
| `FPS_ESERCIZIO` / `FRAME_STEP` | 9,0 / 2 | Cap. 5 (la board regge ~9 fps) |
| `LUNGHEZZA_FINESTRA` / `PASSO_FINESTRA` | 22 / 2 | Cap. 3 § finestre, EXP-012 |
| `SOGLIE_ETICHETTATURA` | k=5/m=8, k=10/m=15 | Cap. 3 § K-su-M, ISS-112 |
| `BETA` | 2,0 | Cap. 4 § metrica |
| `N_ALBERI` | 50 | Cap. 4 § dimensione del modello |
| `K_INTEGRALI` | 31 | Cap. 3 § integrali, Cap. 5 § scansione di K |
| `SEME` | 42 | riproducibilità: due esecuzioni indipendenti danno metriche identiche fold per fold |

---

## 2. Gli script (`pipeline/`)

| script | produce | capitolo | esperimento |
|---|---|---|---|
| `estrai_feature.py` | `feature_v2.csv` — 114.923 fotogrammi × 32 grandezze | 3 | EXP-001, EXP-003, EXP-007 |
| `estrai_urfall.py` | UR-Fall con lo stesso motore, 11.400 fotogrammi | 4 § esterno | EXP-014 |
| `rietichetta_urfall.py` | etichette UR-Fall nella semantica di UP-Fall + `disteso_volontario` | 4 § esterno | EXP-014 |
| `mappa_omnifall.py` | etichette OmniFall su UP-Fall, copertura 96,4% | 3 § compito | EXP-015 |
| `analisi_dtw.py` | `classifica_dtw.csv`, `scelte.txt`, `dtw_cam1_vs_cam2.png` | 3 § DTW | EXP-002/004/005/006/008 |
| `addestra.py` | LOSO completa, `run_*.json`, `punteggi_*.npz` | 4 | EXP-009/011/012 |
| `soglia.py` | confronto fra sei regole, **senza riaddestrare** | 4 § soglia | EXP-010 |
| `confronto_compiti.py` | i tre compiti + negativi difficili | 4 § compiti | EXP-015 |
| `valuta_esterno.py` | PR-AUC/prevalenza su UR-Fall | 4 § esterno | EXP-014 |
| `occlusioni.py` | mascheramento controllato per congelamento | 4 § occlusioni | — |
| `rumore.py` | iniezione di rumore gaussiano sui landmark | 3 § fin dove regge | — |
| `eventi_sessioni.py` | metriche di **evento** sulle sessioni domestiche | 5 § metriche di evento | — |
| `latenza.py` | scomposizione della latenza, e cosa non è misurabile | 5, e ISS-108 | EXP-017 |
| `esporta_board.py` | `modello.pkl`, `scaler.pkl`, `metadata.json`, `parita.npz` | 5 § parità | — |
| `figure_tesi.py` | le undici figure in `tesi/figure/` | 3, 4, 5 | — |
| `confronto_appaiato.py` | t appaiato contro la GRU e **soggetti necessari**, ricalcolati dalle run su disco | 4 § numerosità | EXP-018 |
| `costo_classificatori.py` | millisecondi per finestra delle sei architetture, stesso metro, batch 1 | 4 § architetture, 5 § costo | EXP-018 |

---

## 3. Il pacchetto sul dispositivo (`deploy_board/`)

| file | ruolo |
|---|---|
| `metadata.json` | **la dichiarazione completa della configurazione installata** |
| `modello.pkl` | foresta a 50 alberi, 6.928 nodi, addestrata su **tutti** i dieci soggetti |
| `scaler.pkl` | parametri di normalizzazione + colonne + maschera log1p |
| `parita.npz` | 200 finestre con le predizioni calcolate sul PC |
| `geometry.py` | **copia identica** di `src/geometry.py` (per questo non importa `config`) |
| `rileva.py` | il rilevatore: telecamera → posa → 12 grandezze → finestra → foresta → allarme |
| `parita_frame.py` | verifica di parità **a partire dai fotogrammi**, non dalle finestre (ISS-106) |

### Che cosa dichiara `metadata.json`, e perché ogni campo c'è

```
compito              "evento"  — il positivo è la transizione (DEC-107)
feature_set          "DTW", 12 colonne, elencate per nome
maschera_log1p       quali colonne passano per log1p, nell'ordine
lunghezza_finestra   22        passo 2        fps_assunti 9,0
k_integrali          31        riscaldamento_s 1,72
soglia               0,50      con l'origine dichiarata (EXP-010)
regola_decisione     persistenza 5 finestre, sospensione 30 s
                     + la nota sul fattore 47,8
n_soggetti           10        n_finestre_train 12.140, positive 569
stimatore_posa       mediapipe 0.10.11 solutions, una persona
nota_parita          soglia di tolleranza 1e-6, e che cosa fare se fallisce
```

> **Nota storica.** Fino al 21 agosto la board girava con A3 a dieci colonne e
> $K = 9$: **le grandezze integrali, che erano il contributo del Capitolo 3, non
> erano mai arrivate sul dispositivo**, perché nel prototipo erano calcolate a
> posteriori con `pandas.rolling()`. L'esportazione del 21 agosto è il momento in
> cui la configurazione misurata e quella installata coincidono.

---

## 4. I risultati (`risultati/`)

| cartella | contiene | usato in |
|---|---|---|
| `dtw/` | classifica, scelte, grafici delle curve | Cap. 3 |
| `addestramento/` | `run_*.json` + `punteggi_*.npz` per fold (1,5 MB, tracciati in git) | Cap. 4 |
| `compiti/` | i tre compiti | Cap. 4 § compiti |
| `esterno/` | UR-Fall | Cap. 4 § esterno |
| `occlusioni/` | gruppi anatomici e casuali | Cap. 4 § occlusioni |
| `rumore/` | iniezione di rumore | Cap. 3 |
| `laboratorio/` | metadati delle run a dieci soggetti | Cap. 4 |
| `cinque_soggetti/` | **le misure non ripetute dopo il raddoppio**, con un LEGGIMI che dichiara la provenienza | Cap. 4 §§ viewpoint, dimensione; Cap. 5 § K |
| `campo/` | `compiti_in_casa.json`, `valutazione_10sog_k31.json`, `valutazione_incrociata_10sog.json`, `pr_auc_allineato.json`, `latenza.json` | Cap. 5 |
| `sessioni/` | le dodici sessioni: `punteggi.csv`, `riepilogo.json`, `sanita.csv` | Cap. 5 |

**I punteggi per fold in `.npz` sono tracciati in git** (eccezione esplicita nel
`.gitignore`) perché permettono di rifare EXP-010 **senza riaddestrare**.

**Le clip non sono tracciate e non vanno copiate**: ritraggono familiari
identificabili. Restano in `DIP_PROJECT/sessioni_reali/**/clip/` e in
`deploy_board/clip_demo/`. **Nessun numero del lavoro dipende da esse**: la regola
di decisione si applica ai punteggi.

---

## 5. I difetti, per gravità e per stato

### Risolti

| ID | difetto | come è stato trovato |
|---|---|---|
| **ISS-100** | periodo di srotolamento 360 invece di 180 per l'ellisse | un salto 201,9° → 49,5° fra fotogrammi consecutivi |
| **ISS-101** | il vincolo di warping si allargava sulle coppie incrociate | i cinque integrali sotto 1,0 non tornavano |
| **ISS-102** | selezione DTW cieca alla ridondanza | le prime tre grandezze erano correlate sopra 0,94 |
| **ISS-103** | `.replace('.', ',')` su f-string già composte | gli elenchi numerati uscivano `1,` invece di `1.` |
| **ISS-104** | quattro grandezze A2 misuravano l'origine del riferimento | dev.std del bacino 0,00003 m contro 0,0175 m del naso |
| **ISS-109** | tre nomi per la stessa rappresentazione | rilettura incrociata fra codice, Cap. 3 e Cap. 4 |
| **ISS-111** | quattro valori discordanti in due paragrafi consecutivi | ricalcolo dal CSV citato come sorgente |
| **ISS-112** | soglie di etichettatura dichiarate in due posti | il `run_metadata.json` documentava parametri che non governavano la run |
| **ISS-114** | tre riferimenti di bibliografia inventati | erano marcati `[DA CERCARE]` e sono stati citati lo stesso |
| **ISS-108** | il Cap. 1 prometteva una misura di ritardo che non esiste | la misura è stata fatta (EXP-017): **non è misurabile**; la promessa è sparita con la riscrittura del capitolo |
| **ISS-116** | il Cap. 4 dichiarava i numeri di un impianto a cinque soggetti | 12,36% di positive e 94,55% di negative nello stesso insieme |
| **ISS-117** | i numeri ritirati di OmniFall sopravvivevano nel Cap. 3 | seconda occorrenza di ISS-110: l'avviso stava solo nel Cap. 2 |
| **ISS-118** | la stessa misura con due intervalli diversi in tre capitoli | autocorrelazione 0,18–0,44 contro 0,11–0,41 |
| **ISS-119** | la docstring del motore geometrico sosteneva l'argomento smentito | terza sede della stessa affermazione già corretta altrove |
| **ISS-120** | rimandi che puntavano al posto sbagliato | controllo automatico delle ancore dei registri |
| **ISS-121** | la nota di provenienza del Cap. 4 rivendicava cinque soggetti anche per le occlusioni | `n_fold: 10` nel JSON, e la didascalia della figura lo diceva già |

### Aperti

| ID | difetto | stato |
|---|---|---|
| **ISS-105** | la finestra è più corta dell'evento | **misurata, nessun effetto** (EXP-012). Chiusa come misurata, non come corretta |
| **ISS-106** | lo stimatore di posa non si trasferisce fra architetture | **accertata, non risolvibile**: è la natura del componente |
| **ISS-107** | i capitoli 3 e 4 erano suddivisi troppo | risolta per il testo (49 → 20 titoli), la voce resta come registro |
| **ISS-115** | la scomposizione della latenza è misurata e non compare nel testo | **aperta**: EXP-017 esiste, nessun capitolo la riporta |
| **ISS-110** | due versioni divergenti dei capitoli, e fatti che tornano indietro | **il difetto più pericoloso**: mitigato con avvisi, non risolto |
| **ISS-113** | i numeri del costo edge non hanno un artefatto che li produca | metà fatto: `rileva.py` li misura ora dentro l'esecuzione. **Resta da eseguire sulla board** |

---

## 6. Come si rifà ciascun numero

```powershell
# feature (ambiente fall_processing, ~2 ore)
python pipeline/estrai_feature.py --out feature_v2.csv

# selezione DTW (ambiente con dtaidistance)
python pipeline/analisi_dtw.py --csv feature_v2.csv --top 12 --max-corr 0.85

# una LOSO completa (ambiente fall_training)
python pipeline/addestra.py --modello gru --modo tre_classi --feature DTW --camera 1

# tutte le architetture per tutti i modi
python pipeline/addestra.py --tutti

# confronto fra regole di soglia — secondi, nessun riaddestramento
python pipeline/soglia.py --dettaglio

# i tre compiti
python pipeline/confronto_compiti.py

# trasferimento esterno
python pipeline/valuta_esterno.py

# metriche di EVENTO sulle sessioni domestiche
python pipeline/eventi_sessioni.py --soglia 0.5 --persistenza 5 --sospensione 30
python pipeline/eventi_sessioni.py --sensibilita

# scomposizione della latenza
python pipeline/latenza.py

# confronto appaiato fra architetture, e numerosita' necessaria
python pipeline/confronto_appaiato.py

# costo per finestra di tutte e sei le architetture (sul PC, non sulla board)
python pipeline/costo_classificatori.py

# figure della tesi
python pipeline/figure_tesi.py

# controllo del sorgente LaTeX — SEMPRE prima di dichiarare finito un intervento
python tesi/controlla.py
```

**Sul dispositivo**, in quest'ordine e mai in un altro:

```bash
python3 rileva.py --parita                    # 30 s: se fallisce, fermarsi qui
python3 rileva.py --video clip_demo/evt_0001_092019
python3 rileva.py --durata 43200              # la prova di durata, da fare
```

---

## 7. Le sei decisioni metodologiche, in una riga ciascuna

| ID | decisione | la ragione in una riga |
|---|---|---|
| **DEC-100** | un solo CSV con tutte le grandezze, con prefisso del bacino | due colonne omonime di bacini diversi potevano collassare in un merge |
| **DEC-101** | separabilità per camera, criterio del **minimo** | una grandezza ottima da una vista e inutile dall'altra è quella da escludere, e la media la premierebbe |
| **DEC-102** | ricampionamento a lunghezza comune prima del DTW | il vincolo di warping si allargava proprio sulle coppie che devono risultare distanti |
| **DEC-103** | selezione avida con vincolo di correlazione a 0,85 | il DTW premia tre volte lo stesso fenomeno se è misurato in tre modi |
| **DEC-105** | soglia fissa a 0,5, dichiarata a priori | una soglia che non stima nulla non può sovradattarsi; stimarla su un soggetto costa 0,37 di deviazione |
| **DEC-106** | tre archivi, tre ruoli, mai mescolati | nessuno dei tre è sostituibile con un altro: recall, falsi allarmi reali, generalizzazione |
| **DEC-107** | il positivo è l'**evento**, non lo stato | 0,0% di falsi allarmi sui distesi volontari contro 12,5%, e il rapporto delle mediane è 139× sulla discesa |

---

## 8. Le regole operative che valgono sempre

- **Mai `git add .` o `git add -A`.** Il `.gitignore` esclude clip, modelli e il
  CSV delle feature da 71 MB, ma qualunque nuova cartella di dati non lo sarebbe.
- **Tre ambienti conda distinti**: `fall_processing` (estrazione, MediaPipe
  0.10.9/0.10.11), `fall_training` (TensorFlow), `fall_env` sulla board. Gli
  script di `pipeline/` girano con qualunque interprete che abbia numpy, pandas e
  scikit-learn; `addestra.py` richiede anche TensorFlow.
- **Non esiste un compilatore LaTeX su questa macchina.** Il PDF si produce su
  Overleaf. Non dichiarare mai «verificato» ciò che è stato solo controllato
  staticamente: scrivere **quale** controllo è stato eseguito.
- **`python tesi/controlla.py` prima di dichiarare finito un intervento sul
  testo.** Controlla ambienti non chiusi, etichette duplicate, riferimenti
  orfani, figure mancanti, **figure senza immagine** e citazioni non definite.
- **Non sostituire mai un `\ref` con un numero scritto a mano.** La numerazione è
  cambiata una volta e i riferimenti hanno retto perché sono nomi.
- **Registrare anche le run fallite.** Una run che crasha è un dato: ripeterla per
  dimenticanza costa più che scriverla.
- **Nel campo «Verificato con» va il comando eseguito e il suo esito reale.** Se
  una modifica non è stata provata, scrivere «non verificato».
