# EXPERIMENTS — DIP_Project_1

Registro delle run. Anche quelle fallite o superate: una run rifatta per
dimenticanza costa piu' che scriverla.

Scheda: data · script · dati · configurazione · esito · artefatti · validita'.

---

## Riepilogo

| ID | Data | Cosa | Esito |
|---|---|---|---|
| [EXP-001](#exp-001) | 2026-08-19 | Estrazione feature, pilota su 2 soggetti | OK |
| [EXP-002](#exp-002) | 2026-08-19 | DTW per camera sul pilota | OK, ma non generalizza |
| [EXP-003](#exp-003) | 2026-08-19 | Estrazione feature, 10 soggetti | OK |
| [EXP-004](#exp-004) | 2026-08-19 | DTW su 10 soggetti, senza ricampionamento | ANNULLATA — [ISS-101](ISSUES.md#iss-101) |
| [EXP-005](#exp-005) | 2026-08-19 | DTW su 10 soggetti, con ricampionamento | OK |
| [EXP-006](#exp-006) | 2026-08-19 | Selezione consapevole della ridondanza | OK |
| [EXP-007](#exp-007) | 2026-08-20 | Riestrazione con A2 corretto (v2) | OK |
| [EXP-008](#exp-008) | 2026-08-20 | DTW su v2 — **set definitivo** | OK |
| [EXP-009](#exp-009) | 2026-08-20 | Prima LOSO: GRU, tre classi | OK, ma soglia instabile |
| [EXP-010](#exp-010) | 2026-08-20 | Confronto fra sei regole di soglia | OK — decisivo |
| [EXP-011](#exp-011) | 2026-08-20 | Confronto fra cinque architetture | OK — nessuna distinguibile |
| [EXP-012](#exp-012) | 2026-08-20 | Ablation sulla lunghezza della finestra | OK — nessun effetto |
| [EXP-013](#exp-013) | 2026-08-20 | Numerosita necessaria per ogni confronto | OK — decisivo |
| [EXP-014](#exp-014) | 2026-08-21 | UR-Fall estratto con il motore nuovo | OK |
| [EXP-015](#exp-015) | 2026-08-21 | Le tre definizioni del compito | OK — decisivo |

---

<a id="exp-001"></a>
## EXP-001 — Estrazione pilota, 2 soggetti

**Data:** 2026-08-19 · **Script:** `pipeline/estrai_feature.py --soggetti 1,2 --out feature_prova.csv`
**Ambiente:** `fall_processing` (MediaPipe 0.10.11)

Verifica che il motore geometrico unificato produca tutte e 34 le colonne su un
campione piccolo, prima di impegnare due ore sull'intero dataset.

**Risultato:** 23.074 fotogrammi, 44 riprese, 34/34 colonne, 97,1% pose valide.

**Nota:** durante questa fase e' stato corretto il periodo di srotolamento
dell'angolo dell'ellisse, che era 360 gradi e deve essere 180 — l'asse
dell'ellisse e' una direzione, non un verso. Vedi [ISS-100](ISSUES.md#iss-100).

---

<a id="exp-002"></a>
## EXP-002 — DTW per camera, pilota

**Data:** 2026-08-19 · **Script:** `pipeline/analisi_dtw.py --csv feature_prova.csv`
**Ambiente:** `fallqt_clean` (unico con `dtaidistance`)

Prima applicazione del criterio `robusto = min(cam1, cam2)`.

**Risultato:** classifica guidata da `A2_testa_rel_y` (2,036 / 1,208),
`A1_asse_mag` (1,208 / 1,286) unico punto sopra la diagonale, `A2_discesa`
con divario 0,001.

**Validita': PARZIALE.** Con 10 cadute e 12 ADL per camera i punteggi non sono
stabili. Confrontando con [EXP-005](#exp-005): `A1_asse_mag` scende da 1,208 a
1,101 su cam1 e `A2_discesa` da 1,053 a 1,095 con l'ordine di classifica
completamente diverso. **Le conclusioni di questa run non vanno citate.**
Serviva a validare il codice, non a scegliere le grandezze.

---

<a id="exp-003"></a>
## EXP-003 — Estrazione completa, 10 soggetti

**Data:** 2026-08-19 · **Script:** `pipeline/estrai_feature.py --out feature.csv`
**Ambiente:** `fall_processing` · **Durata:** 95 minuti

**Risultato:** 114.923 fotogrammi, 218 riprese, 10 soggetti, 34/34 colonne,
**95,5% pose valide**.

Distribuzione delle etichette a livello di fotogramma:

| etichetta | fotogrammi | quota |
|---|---:|---:|
| 0 — attivita' normale | 98.857 | 86,0% |
| 1 — caduta in corso | 5.542 | 4,8% |
| 2 — a terra | 10.524 | 9,2% |

Dentro le sole riprese di caduta (17.892 fotogrammi): 1.826 in piedi prima
(10%), 5.542 la caduta (31%), 10.524 a terra dopo (59%).

**Verifica sulle etichette predefinite.** Lo script ha segnalato 47.115
fotogrammi (41%) etichettati dalla cartella invece che dal suffisso del nome
file. Controllato: stanno **tutti** nelle ADL dei soggetti 6-10, e le ADL dei
soggetti 1-5 — annotate a mano — sono 49.916 fotogrammi tutti a etichetta 0,
nessun 1 e nessun 2, sulle stesse attivita' (act06-act11). Il valore
predefinito riproduce la scelta manuale, non la aggira. Le riprese di caduta
hanno il suffisso al 100% su tutti e dieci i soggetti.

**Osservazione che pesa sul seguito.** Fra le ADL c'e' `act11 = laying`,
sdraiarsi volontariamente: 20.980 fotogrammi, il 18% dell'intero dataset,
etichettati 0. Il dataset contiene quindi ventimila fotogrammi di persona
distesa a terra etichettati 0 e diecimila etichettati 2. Lo stato finale e'
quasi identico; la differenza sta solo in come ci si e' arrivati. Vedi
[DEC-104](DECISIONS.md#dec-104).

Durata media delle riprese: cadute ~180 fotogrammi, ADL ~820.

**Artefatti:** `dataset/processed/features/feature.csv`

---

<a id="exp-004"></a>
## EXP-004 — DTW su 10 soggetti, senza ricampionamento

**Data:** 2026-08-19 · **Script:** `pipeline/analisi_dtw.py --csv feature.csv --top 12`

**Esito: ANNULLATA.** Affetta da [ISS-101](ISSUES.md#iss-101): il vincolo di
warping si allargava da solo sulle coppie di lunghezza molto diversa, che qui
sono proprio quelle fra caduta (~180 fotogrammi) e ADL (~820). Le coppie
incrociate ricevevano una banda di ~630 invece di 10, si allineavano quasi
senza vincolo e risultavano artificialmente vicine.

L'effetto era **sistematico e selettivo**: colpiva gli integrali, che sono
curve lisce e sotto warping libero si deformano l'una nell'altra a costo quasi
nullo. Cinque delle nove integrali risultavano sotto 1,0, cioe' scartate come
rumore.

Classifica conservata come `risultati/dtw/classifica_dtw_senza_ricampionamento.csv`
per rendere verificabile il confronto con [EXP-005](#exp-005).

---

<a id="exp-005"></a>
## EXP-005 — DTW su 10 soggetti, con ricampionamento

**Data:** 2026-08-19 · **Script:** `pipeline/analisi_dtw.py --csv feature.csv --top 12`
**Ambiente:** `fallqt_clean` · **Correzione:** [DEC-102](DECISIONS.md#dec-102)

Curve portate a 200 campioni dopo lo z-score e prima del confronto, cosi' la
banda vale 10 per tutte le coppie.

**Verifica della correzione, su dati sintetici** con la stessa asimmetria di
durata del dataset reale (8 curve da 180 con discesa netta contro 9 da 820
oscillanti):

| | mu_FA | mu_intra | punteggio |
|---|---:|---:|---:|
| senza ricampionamento | 0,0207 | 0,0041 | 5,055 |
| con ricampionamento | 0,0420 | 0,0058 | **7,201** |

La distanza fra le classi raddoppia. Il difetto era conservativo — deprimeva i
punteggi — ma in modo asimmetrico fra le grandezze, quindi ne falsava l'ordine.

**Effetto sui dati reali:** nessuna grandezza resta sotto 1,0 (minimo 1,046).
Gli spostamenti maggiori sono tutti integrali:

| grandezza | EXP-004 | EXP-005 | Δ |
|---|---:|---:|---:|
| `A3_percorso` | 0,937 | 1,183 | +0,246 |
| `A1_percorso` | 0,944 | 1,182 | +0,238 |
| `A2_escursione` | 0,969 | 1,197 | +0,228 |
| `A1_escursione` | 0,951 | 1,177 | +0,226 |
| `A3_escursione` | 1,006 | 1,202 | +0,196 |
| `A2_testa_rel_y` | 1,326 | 1,309 | −0,017 |
| `A1_vy` | 1,134 | 1,155 | +0,021 |

**Risultato sui bacini** (regge sia prima sia dopo la correzione):

| | cam1 | cam2 |
|---|---:|---:|
| `A2_angolo_tronco` (mondo 3D) | 1,486 | **1,284** |
| `A3_angolo_tronco` (piano immagine) | 1,270 | **1,104** |

Le coordinate world di MediaPipe riducono davvero la dipendenza dal punto di
vista. Coerente con la misura diretta di escursione angolare ottenuta per via
indipendente (84 gradi su cam1 contro 3 su cam2 per l'angolo nel piano
immagine).

`A1_asse_mag` e' l'unica grandezza nettamente sopra la diagonale
(1,101 / 1,314): l'ingombro dell'ellisse si misura meglio dall'alto che di
profilo.

**Artefatti:** `risultati/dtw/classifica_dtw.csv`, `dtw_cam1_vs_cam2.png`,
`curve/*.png`

---

<a id="exp-006"></a>
## EXP-006 — Selezione consapevole della ridondanza

**Data:** 2026-08-19 · **Script:** `pipeline/analisi_dtw.py --csv feature.csv --top 12 --max-corr 0.85`
**Motivazione:** [DEC-103](DECISIONS.md#dec-103)

Il DTW valuta ogni grandezza da sola e premia tre volte lo stesso fenomeno se
e' misurato in tre modi. Le prime dodici secche contenevano cinque coppie con
|r| > 0,80, tre delle quali sopra 0,94 e tutte riconducibili a «quanto e'
verticale il tronco».

Confronto fra soglie, correlazione media assoluta fra le scelte:

| soglia | corr. media | note |
|---|---:|---|
| prime 12 secche | 0,385 | 5 coppie sopra 0,80 |
| 0,90 | 0,393 | quasi nessun effetto |
| **0,85** | **0,325** | adottata |
| 0,75 | 0,240 | ammette grandezze piu' in basso in classifica |

### Set definitivo (12)

| # | grandezza | robusto | tipo | bacino |
|---|---|---:|---|---|
| 1 | `A2_testa_rel_y` | 1,309 | posizionale | A2 |
| 2 | `A1_discesa` | 1,203 | integrale | A1 |
| 3 | `A3_escursione` | 1,202 | integrale | A3 |
| 4 | `A3_discesa` | 1,183 | integrale | A3 |
| 5 | `A3_percorso` | 1,183 | integrale | A3 |
| 6 | `A1_percorso` | 1,182 | integrale | A1 |
| 7 | `A3_ginocchia_rel_y` | 1,179 | posizionale | A3 |
| 8 | `A1_escursione` | 1,177 | integrale | A1 |
| 9 | `A2_percorso` | 1,162 | integrale | A2 |
| 10 | `A3_hip_vel` | 1,160 | velocita' | A3 |
| 11 | `A3_testa_vel_rel` | 1,157 | velocita' | A3 |
| 12 | `A1_vy` | 1,155 | velocita' | A1 |

Composizione: **7 integrali, 3 velocita', 2 posizionali** — A3 sei, A1 quattro,
A2 due. Correlazione media fra le scelte 0,325.

### Escluse per ridondanza

| esclusa | ridondante con | r |
|---|---|---:|
| `A2_angolo_tronco` | `A2_testa_rel_y` | 0,97 |
| `A3_testa_rel_y` | `A2_testa_rel_y` | 0,98 |
| `A2_escursione` | `A3_escursione` | 0,85 |
| `A3_caviglie_rel_y` | `A3_ginocchia_rel_y` | 0,93 |

`A2_angolo_tronco` esce perche' il tronco e' un segmento rigido e
`testa_rel_y ~ L cos(theta)`: e' la stessa grandezza fisica. L'esclusione dal
set **non tocca** il risultato A2-contro-A3 di [EXP-005](#exp-005), che e'
un'affermazione sulle rappresentazioni e non sul set finale.

### Nota sui tre `percorso`

Entrano tutti e tre e non sono ridondanti fra loro:

| | A1 | A2 | A3 |
|---|---:|---:|---:|
| **A1_percorso** | 1,00 | 0,25 | 0,79 |
| **A2_percorso** | 0,25 | 1,00 | 0,30 |
| **A3_percorso** | 0,79 | 0,30 | 1,00 |

`A2_percorso` e' quasi indipendente dagli altri due (0,25 e 0,30) perche' il
percorso in coordinate world include la componente in profondita', invisibile
nel piano immagine. A1 e A3 stanno a 0,79, appena sotto la soglia: e' il caso
piu' borderline del set.

**Limite dichiarato.** Il DTW piu' la correlazione sono una preselezione
euristica. L'arbitro e' la LOSO sul modello: la scelta fra soglia 0,85 e 0,75,
e piu' in generale la dimensione del set, va decisa li'. Nessuna delle
grandezze supera 1,31 su entrambe le camere, quindi **nessuna separa da sola**;
il set va valutato insieme, non grandezza per grandezza.

**Artefatti:** `risultati/dtw/scelte.txt`, `classifica_dtw.csv`,
`dtw_cam1_vs_cam2.png`

---

<a id="exp-007"></a>
## EXP-007 — Riestrazione con A2 corretto (v2)

**Data:** 2026-08-20 · **Script:** `pipeline/estrai_feature.py --out feature_v2.csv`
**Ambiente:** `fall_processing` · **Durata:** 124 minuti
**Motivo:** [ISS-104](ISSUES.md#iss-104)

**Risultato:** 114.923 fotogrammi, 218 riprese, 10 soggetti, **32/32 colonne**
(erano 34: due rimosse), 95,5% pose valide. Etichette identiche a
[EXP-003](#exp-003).

**Verifica di chirurgia della modifica.** Confrontate v1 e v2 colonna per
colonna sulle stesse 114.923 righe:

| | esito |
|---|---|
| righe e chiavi | identiche |
| colonne solo in v1 | `A2_hip_vy`, `A2_hip_vel` (rimosse) |
| colonne solo in v2 | nessuna |
| colonne identiche bit per bit | **30** |
| colonne cambiate | `A2_percorso`, `A2_discesa` (ridefinite) |

| grandezza | v1 mediana\|·\| | v1 max | v2 mediana\|·\| | v2 max |
|---|---:|---:|---:|---:|
| `A2_percorso` | 0,000 | 7,6 | **0,185** | 17,7 |
| `A2_discesa` | 0,000 | 1,4 | **0,015** | 7,9 |

La modifica ha toccato esattamente cio' che doveva e nient'altro.

**Artefatti:** `dataset/processed/features/feature_v2.csv`.
Il file v1 e' stato **rinominato** `feature_v1_A2_degenere.csv` invece che
cancellato: 124 minuti di calcolo non si buttano, ma il nome deve rendere
impossibile usarlo per sbaglio.

---

<a id="exp-008"></a>
## EXP-008 — DTW su v2, set definitivo

**Data:** 2026-08-20 · **Script:** `pipeline/analisi_dtw.py --csv feature_v2.csv --top 12 --max-corr 0.85`

Le due grandezze A2 ridefinite entrano **al secondo e terzo posto**, mentre in
[EXP-005](#exp-005) erano in fondo alla classifica come rumore:

| grandezza | EXP-005 (bacino) | EXP-008 (naso) |
|---|---:|---:|
| `A2_discesa` | 1,095 | **1,224** |
| `A2_percorso` | 1,162 (falso) | **1,221** |

Conferma la diagnosi di [ISS-104](ISSUES.md#iss-104): il percorso e la discesa
della TESTA in coordinate world sono fra le grandezze piu' discriminanti
dell'intero bacino. Prima si misurava l'origine del riferimento.

### Set definitivo (12)

| # | grandezza | robusto | tipo |
|---|---|---:|---|
| 1 | `A2_testa_rel_y` | 1,309 | posizionale |
| 2 | `A2_discesa` | 1,224 | integrale |
| 3 | `A2_percorso` | 1,221 | integrale |
| 4 | `A1_discesa` | 1,203 | integrale |
| 5 | `A3_escursione` | 1,202 | integrale |
| 6 | `A3_discesa` | 1,183 | integrale |
| 7 | `A3_percorso` | 1,183 | integrale |
| 8 | `A1_percorso` | 1,182 | integrale |
| 9 | `A3_ginocchia_rel_y` | 1,179 | posizionale |
| 10 | `A1_escursione` | 1,177 | integrale |
| 11 | `A3_hip_vel` | 1,160 | velocita' |
| 12 | `A3_testa_vel_rel` | 1,157 | velocita' |

**Nove integrali su dodici.** Escluse per ridondanza: `A2_angolo_tronco`
(r = 0,97), `A3_testa_rel_y` (0,98), `A2_escursione` (0,85),
`A3_caviglie_rel_y` (0,93).

**Limite dichiarato.** La correlazione media fra le scelte sale da 0,323 a
0,424 rispetto a EXP-006: le due A2 riabilitate passano il filtro ma restano
parenti delle altre. E' il prezzo di tre bacini che descrivono lo stesso corpo.

---

<a id="exp-009"></a>
## EXP-009 — Prima LOSO: GRU, tre classi

**Data:** 2026-08-20 · **Script:** `pipeline/addestra.py --modello gru --modo tre_classi --feature DTW --camera 1`
**Ambiente:** `fall_training` · **Durata:** 27 minuti (1.639 s)
**Dati:** feature.csv (v1), 12 grandezze di EXP-006, camera 1, 11.510 finestre

Prima metrica di classificazione difendibile dell'intero progetto: divisione
per soggetto, scaler stimato solo sul train del fold, soglia scelta sul
validation e applicata al test una volta sola.

**Risultato:** F2 = **0,813 ± 0,110** · recall 0,909 · precisione 0,690 ·
24.483 parametri.

**Riproducibilita' verificata:** due esecuzioni indipendenti hanno dato metriche
identiche fold per fold. Il seme funziona.

**Il problema.** Le soglie scelte per fold: 0,01 · 0,02 · 0,22 · 0,43 · 0,71 ·
0,75 · 0,90 · 0,94 · 0,95 · 0,99. Coprono tutto l'intervallo. Riletti in
termini di quota di finestre su cui il sistema suona:

| quota di allarme | fold | F2 |
|---|---|---|
| vicina alla prevalenza (12-15%) | 01, 05, 06, 09, 10 | **0,88 – 0,95** |
| due volte e mezzo (25-31%) | 02, 03, 04, 08 | 0,64 – 0,80 |
| troppo bassa (10,3%) | 07 | 0,72 |

Non e' il modello a variare fra i soggetti: e' la soglia. Da qui
[EXP-010](#exp-010).

**Artefatti:** `risultati/addestramento/run_gru_tre_classi_DTW_cam1.json`,
`punteggi_gru_tre_classi_DTW_cam1.npz`

---

<a id="exp-010"></a>
## EXP-010 — Sei regole di soglia a confronto

**Data:** 2026-08-20 · **Script:** `pipeline/soglia.py --dettaglio`
**Dati:** le probabilita' per fold salvate da [EXP-009](#exp-009). Nessun
riaddestramento: l'esperimento costa secondi.

| regola | F2 media ± dev | recall | prec. | soglia media ± dev | scarto trasf. |
|---|---:|---:|---:|---:|---:|
| `fbeta` (attuale) | 0,810 ± 0,117 | 0,908 | 0,689 | 0,59 ± 0,37 | 0,094 |
| `f1` | 0,790 ± 0,120 | 0,851 | 0,747 | 0,70 ± 0,34 | **0,068** |
| `youden` | 0,808 ± 0,117 | 0,910 | 0,686 | 0,59 ± 0,37 | 0,096 |
| `prevalenza` | 0,787 ± 0,116 | 0,858 | 0,734 | 0,68 ± 0,35 | 0,076 |
| `prev15` | 0,823 ± 0,136 | **0,972** | 0,610 | 0,43 ± 0,31 | 0,106 |
| **`fissa05`** | **0,851 ± 0,078** | 0,926 | 0,721 | 0,50 ± 0,00 | 0,080 |

**Vince non scegliere.** La soglia fissa da' l'F2 piu' alto e la dispersione
piu' bassa. Tutte le regole adattive fanno peggio.

**Perche'.** Stimare la soglia da un solo soggetto di validazione aggiunge piu'
rumore di quanto adattamento porti: deviazione della soglia 0,37 su un
intervallo [0, 1]. Una soglia fissa ha deviazione zero per costruzione.

**Avvertenza metodologica, che conta piu' del risultato.** Confrontare sei
regole sui fold di test e sceglierne una e' **selezione sul test set**. Il
numero 0,851 non e' quindi una stima imparziale.

Cio' che si puo' portare avanti non e' «0,5 e' la soglia migliore», che sarebbe
una conclusione sui dati di test. E' **«scegliere la soglia su un solo soggetto
di validazione e' una procedura dannosa»**, che e' una conclusione sulla
PROCEDURA e regge. Da li' la scelta a priori difendibile e' la soglia fissa,
perche' non stima nulla e non puo' sovradattarsi. Vedi
[DEC-105](DECISIONS.md#dec-105).

**Osservazione residua che nessuna soglia risolve.** Anche a soglia fissa la
quota di allarme varia da 5,5% (Subject_04) a 34,7% (Subject_02) mentre i
positivi veri stanno fra 6,7% e 14,9%. La distribuzione dei punteggi si sposta
da persona a persona: e' il domain shift fra individui, e si affronta tarando
sulle registrazioni di esercizio, non qui.

---

<a id="exp-011"></a>
## EXP-011 — Cinque architetture a confronto

**Data:** 2026-08-20 · **Script:** `pipeline/addestra.py --soglia 0.5`
**Dati:** feature_v2.csv, 12 grandezze DTW, camera 1, modo `tre_classi`, LOSO su 10 soggetti

| modello | F2 | dispersione | recall | precisione | parametri | durata |
|---|---:|---:|---:|---:|---:|---:|
| LSTM | 0,858 | ±0,082 | 0,934 | 0,715 | 32.227 | 996 s |
| **GRU** | **0,847** | ±0,085 | 0,928 | 0,711 | **24.483** | 1.362 s |
| Transformer | 0,846 | ±0,100 | 0,939 | 0,679 | 34.499 | 689 s |
| CNN 1D | 0,833 | ±0,118 | 0,937 | 0,651 | 46.147 | 666 s |
| Foresta | 0,792 | ±0,080 | 0,807 | **0,838** | 12.760 nodi | **11 s** |

**Confronto appaiato contro la GRU, fold per fold:**

```
lstm          +0,011   vince 6/10   t = +0,84
transformer   −0,002   vince 4/10   t = −0,08
cnn           −0,014   vince 5/10   t = −0,60
foresta       −0,055   vince 3/10   t = −1,74      (serve |t| > 2,26)
```

**Nessuna architettura è statisticamente distinguibile dalla GRU**, che ottiene la stessa prestazione con il 24% dei parametri in meno della LSTM e il 47% in meno della CNN.

**Modalita di etichettatura, stesso modello:**

```
caduta      0,854 ±0,077        scarta contro tre_classi:  −0,309   t = −6,85
tre_classi  0,847 ±0,085        caduta contro tre_classi:  +0,007   t = +0,33
scarta      0,538 ±0,137
```

Una scelta di rappresentazione del problema produce un effetto **ventotto volte** più grande della scelta fra tutte le architetture messe insieme.

---

<a id="exp-012"></a>
## EXP-012 — Lunghezza della finestra: misurata, nessun effetto

**Data:** 2026-08-20 · **Script:** `pipeline/addestra.py --lunghezza {22,28,36,44}`

Ipotesi di partenza ([ISS-105](ISSUES.md#iss-105)): la finestra da 2,44 s è più corta della caduta mediana da 3,11 s, quindi allungarla dovrebbe aiutare.

| campioni | durata | F2 | dispersione |
|---:|---:|---:|---:|
| 22 | 2,44 s | 0,847 | ±0,085 |
| 28 | 3,11 s | 0,838 | ±0,077 |
| 36 | 4,00 s | 0,817 | ±0,146 |
| 44 | 4,89 s | 0,881 | ±0,090 |

```
L=28  −0,010  t = −0,51        L=36  −0,030  t = −0,56        L=44  +0,033  t = +1,23
```

**Nessuna differenza significativa, andamento non monotono. L'ipotesi era sbagliata.**

Spiegazione probabile: la memoria effettiva non è la finestra. Ogni campione porta gli integrali accumulati su 31 fotogrammi, cioè 1,7 s di storia in più; e due terzi dei positivi sono lo stato «a terra», che si riconosce da una finestra corta quanto si vuole.

**ISS-105 si chiude come «misurata, nessun effetto», non come «corretta».** Da valore ereditato, 22 campioni diventa un valore verificato contro tre alternative.

---

<a id="exp-013"></a>
## EXP-013 — Quanti soggetti servirebbero per ciascun confronto

**Data:** 2026-08-20 · Potenza 80%, alfa 5%, test appaiato

| confronto | effetto | dev. diff | t (n=10) | soggetti necessari |
|---|---:|---:|---:|---:|
| modo `scarta` contro `tre_classi` | −0,309 | 0,143 | −6,85 | **2** |
| GRU contro foresta | −0,055 | 0,100 | −1,74 | 26 |
| integrali, foresta con estremi | −0,022 | 0,045 | −1,53 | 34 |
| finestra 22 contro 44 | +0,033 | 0,086 | +1,23 | 52 |
| integrali, foresta senza estremi | +0,039 | 0,117 | +1,06 | 70 |
| **GRU contro LSTM** | +0,011 | 0,042 | +0,84 | **113** |
| integrali sulla GRU | +0,016 | 0,096 | +0,54 | 274 |

UP-Fall ne ha 17 in tutto, noi ne usiamo 10.

**La formulazione più forte della tesi centrale:** distinguere una GRU da una LSTM richiederebbe **113 soggetti**; distinguere due regole di etichettatura ne richiede **2**. Un fattore **56** fra le due domande.

Aggiungere i sette soggetti mancanti porterebbe solo «GRU contro foresta» vicino alla soglia, senza raggiungerla. Il guadagno reale sarebbe l'errore standard della media da ±0,027 a ±0,021: cosmetico.

---

<a id="exp-014"></a>
## EXP-014 — UR-Fall estratto con il motore geometrico nuovo

**Data:** 2026-08-21 · **Script:** `pipeline/estrai_urfall.py` (nuovo) · **Durata:** 9,6 minuti

**Risultato:** 11.400 fotogrammi, 67 riprese, **32/32 colonne**, **81,0% pose valide** (contro 95,8% di UP-Fall), 2.289 negativi difficili conservati.

Etichette dalle annotazioni originali degli autori, non dai nomi dei file: 0 normale (84,3%), 1 transizione (7,8%), 2 a terra (7,9%).

**Addestrando su UP-Fall e misurando su UR-Fall** (foresta, modo `caduta`, soglia 0,50 dichiarata a priori):

| rappresentazione | n | PR-AUC | guadagno | F2 | recall | difficili | facili |
|---|---:|---:|---:|---:|---:|---:|---:|
| modello schierato (vecchio) | 10 | 0,169 | 1,8× | 0,034 | — | 11,6% | 0,0% |
| A3base senza integrali | 9 | 0,440 | 3,4× | 0,404 | 0,426 | 47,1% | 0,2% |
| A3 con integrali | 12 | 0,466 | 3,6× | 0,479 | 0,504 | 41,7% | 0,2% |
| **DTW** | 12 | **0,660** | **5,1×** | 0,630 | 0,765 | 50,5% | 8,2% |

Il guadagno passa da 1,8× a 5,1× e l'F2 da 0,034 a 0,630. **Il grosso del salto non viene dagli integrali ma dal motore corretto** — angoli srotolati, derivate non esplosive — e dalla definizione corretta del positivo: già A3base, con le stesse nove grandezze del vecchio, quasi raddoppia il guadagno.

Con `modo scarta`, cioè positivo = sola transizione: DTW sale a **6,8×** e i falsi allarmi sui difficili scendono da 50,5% a **35,9%**. Entrambe le direzioni — dinamica e transizione — aiutano e si sommano.

---

<a id="exp-015"></a>
## EXP-015 — Le tre definizioni del compito

**Data:** 2026-08-21 · **Script:** `pipeline/mappa_omnifall.py`, `pipeline/confronto_compiti.py` (nuovi)

Con le etichette OmniFall applicate a UP-Fall (96,4% dei fotogrammi coperti, 21.322 distesi volontari resi misurabili):

| compito | positivo | prevalenza | F2 | recall | prec. | **difficili** | facili |
|---|---|---:|---:|---:|---:|---:|---:|
| **evento** | `fall` | 0,047 | **0,831 ±0,072** | 0,814 | 0,924 | **0,0%** | 0,4% |
| stato | `fallen` | 0,089 | 0,704 ±0,084 | 0,707 | 0,755 | 12,5% | 0,7% |
| allarme | `fall` O `fallen` | 0,115 | 0,810 ±0,068 | 0,817 | 0,833 | 13,1% | 0,4% |

**Sull'evento il sistema sbaglia sullo 0,0% delle 2.234 finestre di persona distesa volontariamente.** Ed è anche il compito con l'F2 più alto e la precisione più alta, nonostante la prevalenza più bassa.

La verifica sulle registrazioni domestiche è in `DIP_PROJECT` ([EXP-061](../../DIP_PROJECT/docs/EXPERIMENTS.md#exp-061)): i falsi allarmi dai nonni crollano da 105,1 a **5,3 eventi/ora** con recall 3/5 contro 4/5. Vedi [DEC-107](DECISIONS.md#dec-107).

---

<a id="exp-016"></a>
## EXP-016 — Le stesse 56 clip, sul PC e sulla board

**Data:** 2026-08-22 · **Script:** `deploy_board/rileva.py` in modalità scansione · **Dati:** `bloccocadute_nonni_20260812_154007`, 56 clip · **Esito:** ✅

Prima verifica end-to-end del sistema completo — immagine, stimatore di posa, geometria, scaler, classificatore, antirimbalzo — sulle due macchine, sugli **stessi fotogrammi**.

| | PC | board |
|---|---:|---:|
| clip | 56 | 56 |
| allarmi emessi | 2 | **1** |
| pose valide (media) | 96,4% | 96,3% |
| picco: scarto medio | — | 0,063 |
| picco: correlazione | — | r = 0,781 |
| clip concordi | — | **55 / 56** |

Le tre clip su cui i punteggi divergono in modo apprezzabile:

| clip | PC (picco / finestre / allarmi) | board |
|---|---|---|
| `evt_0041_154942` | 0,440 · 0 · 0 | 0,200 · 0 · 0 |
| `evt_0433_155521` | 0,600 · 2 · 0 | 0,220 · 0 · 0 |
| **`evt_0067_155044`** | **1,000 · 9 · 1** | **0,560 · 2 · 0** |

**Le due macchine concordano sul comportamento, non sui punteggi.** Su 55 clip su 56 la decisione finale è identica, e le due clip che il PC segnala sono cadute reali. La sola divergenza di comportamento è `evt_0067`: il PC la classifica con punteggio saturo, la board si ferma a 0,560 e l'antirimbalzo — che pretende cinque finestre consecutive sopra soglia — non emette l'allarme.

La causa non è il classificatore: la parità sulle finestre precalcolate è **esatta** (scarto 0,000e+00, [EXP-014](#exp-014)). È lo stimatore di posa, che è un **tracciatore**: mantiene uno stato fra fotogrammi, e differenze infinitesime nella decodifica dell'immagine si amplificano lungo la sequenza (scarto sui landmark 0,0001 al fotogramma 1, 0,0755 all'undicesimo). Vedi [ISS-106](ISSUES.md#iss-106).

**Conseguenze per la relazione.** Primo: la verifica di trasferimento deve partire dai **fotogrammi**, non dalle grandezze già calcolate — la prova sulle finestre è passata con scarto esattamente zero pur mascherando l'unica divergenza reale. Secondo: **i numeri di prestazione misurati sul PC non sono automaticamente i numeri della board**, e su un evento su cinque la differenza è la differenza fra allarme e silenzio. Terzo: l'antirimbalzo, introdotto contro i falsi allarmi ([DEC-107](DECISIONS.md#dec-107)), amplifica la divergenza — trasforma uno scarto continuo di punteggio in una decisione binaria diversa. Il recall sulla board va misurato sulla board.

---

<a id="exp-017"></a>
## EXP-017 — La latenza di rilevamento: che cosa si misura e che cosa no

**Data:** 2026-08-26 · **Script:** `pipeline/latenza.py` (nuovo)
**Dati:** `risultati/sessioni/20260813/bloccocadute_sola_.../punteggi.csv`,
8.411 finestre, 35 minuti, cinque cadute annotate
**Esito:** ✔ eseguito · **Uscita:** `risultati/campo/latenza.json`

**Domanda.** Il Capitolo 1 prometteva una misura del ritardo di rilevamento
([ISS-108](ISSUES.md#iss-108)); il relatore l'ha chiesta fra le quattro
metriche operative. E' misurabile?

**Risposta: no, non nella forma richiesta.** Le cadute sono annotate **al
minuto** (`ORARI_CADUTE = ['09:20','09:22','09:25','09:29','09:31']`), mentre
la grandezza da misurare e' di pochi secondi. L'incertezza sull'istante vero
e' fino a sessanta volte la quantita' da misurare.

Il dato che lo rende evidente: la prima finestra sopra soglia cade a **+11,8,
+19,4, +27,7 e +32,3 secondi** dal minuto annotato. Quegli scarti non sono
ritardi del sistema, sono **il punto del minuto in cui la persona e' caduta**.

**Che cosa invece si misura, esattamente.** La latenza si scompone in tre
addendi, due dei quali dipendono solo dalla configurazione:

| addendo | valore | quota |
|---|---:|---:|
| calcolo per fotogramma | 0,038 s | 1,0% |
| **riempimento della finestra** (22 campioni a 8,02 fps) | **2,743 s** | **72,6%** |
| persistenza (5 finestre, una ogni 0,249 s) | 0,997 s | 26,4% |
| **limite inferiore** | **3,778 s** | |

**La latenza e' dominata dalla finestra di decisione, non dall'hardware: 2,74 s
contro 38 ms, un fattore settantatre.** E' il complemento del risultato sul
costo per fotogramma --- li' il collo di bottiglia era la percezione, qui e'
la finestra --- e in entrambi i casi il classificatore non conta.

**Verifica empirica del terzo addendo.** E' l'unico intervallo con entrambi
gli estremi noti al centesimo. Sulle due cadute in cui l'allarme scatta:
**1,70 s e 1,28 s**, contro 1,00 s attesi. Lo scarto e' atteso a sua volta: la
regola chiede cinque finestre *consecutive*, e i punteggi hanno buchi.

**Le altre tre cadute non producono allarme** a persistenza 5, con corse
massime di 2, 0 e 3 finestre. Coerente con la tabella del capitolo di campo.

**Conseguenza per il testo.** La promessa del Capitolo 1 va sostituita: non
«si misura il ritardo», ma «si scompone la latenza e si dichiara che
l'addendo dipendente dall'evento non e' misurabile con annotazione al minuto».
Per misurarlo davvero servirebbe annotare al secondo, il che richiede di
rivedere i fotogrammi salvati --- che pero' esistono solo attorno agli allarmi.

**Collegamenti:** [ISS-108](ISSUES.md#iss-108)
