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
| [EXP-016](#exp-016) | 2026-08-22 | Le stesse 56 clip sul PC e sulla board | OK — una decisione su 56 diverge |
| [EXP-017](#exp-017) | 2026-08-26 | Scomposizione della latenza di rilevamento | OK — un addendo non e' misurabile |
| [EXP-018](#exp-018) | 2026-08-27 | La rete a grafo, sesta architettura | OK — la sola che si avvicina a essere distinguibile, e fa peggio |
| [EXP-019](#exp-019) | 2026-08-27 | Costo per finestra delle sei architetture | OK — la foresta installata e' la piu' lenta |
| [EXP-020](#exp-020) | 2026-09-06 | Escursione per vista, rifatta su dieci soggetti | OK — 2,23× invece di 1,99×, e una seconda causa: 11 riprese su 50 cambiano persona |
| [EXP-021](#exp-021) | 2026-09-06 | Errori scomposti per attivita' e per tipo di caduta | OK — il 93% dei falsi allarmi viene da una sola attivita' |
| [EXP-022](#exp-022) | 2026-09-06 | Riestrazione completa (v3) e nuova selezione DTW | OK — 220 riprese, 33 grandezze, niente piu' dipendenza dall'ordine |
| [EXP-023](#exp-023) | 2026-09-06 | L'altezza dal pavimento nel classificatore | OK — decisivo: i falsi negativi calano del 35% |
| [EXP-024](#exp-024) | 2026-09-06 | Prova di durata sulla board, 4,6 ore | OK — 3,1 eventi/ora, 136,65 ms per fotogramma |
| [EXP-025](#exp-025) | 2026-09-07 | Le sei architetture rifatte su v3, DTW e DTWH | OK — l'altezza dal pavimento migliora **tutte e sei** |
| [EXP-026](#exp-026) | 2026-09-07 | Le tre righe della vista a dieci soggetti, e le due cause separate | OK — il divario è compressione ottica, non lo stimatore |
| [EXP-027](#exp-027) | 2026-09-07 | Occlusioni rimisurate col motore corrente | OK — la robustezza dipende dalle COLONNE, non dal motore |
| [EXP-028](#exp-028) | 2026-09-07 | Latenza misurata in laboratorio, e la curva della persistenza | OK — mediana 2,44 s, e il «limite inferiore» non lo era |
| [EXP-029](#exp-029) | 2026-09-07 | Ventuno regole di allarme a confronto | OK — **decisivo**: l'isteresi dimezza i falsi allarmi e prende più cadute |
| [EXP-030](#exp-030) | 2026-09-08 | Scomposizione della latenza rifatta sul costo per fotogramma misurato | OK — il fattore scende da 73× a 22×, la conclusione regge |
| [EXP-031](#exp-031) | 2026-09-08 | Due conteggi sulle finestre: il confine dell'etichetta, e cosa vede la board | OK — il confine vale lo 0,16%, la board decide fuori distribuzione nel 75,4% |
| [EXP-032](#exp-032) | 2026-09-08 | La sessione riclassificata con la finestratura dell'addestramento | OK — **decisivo**: 14 allarmi diventano 4, e dieci erano il difetto |
| [EXP-033](#exp-033) | 2026-09-08 | Riestrazione v4 con il dt vero fotogramma per fotogramma | OK — il difetto e' reale, l'effetto sull'F2 e' $-0{,}006$: non distinguibile |
| [EXP-034](#exp-034) | 2026-09-09 | L'allineamento OmniFall con i timestamp veri, prima e dopo | OK — la copertura sale, l'accordo su «a terra» sale di 3,6 punti, quello sulla transizione non si muove |
| [EXP-035](#exp-035) | 2026-09-09 | DTWH installata sulla board: parita', cadenza misurata, prima sessione | OK — **decisivo**: la cadenza vera e' 6,47 non 9,0, e la finestra degli integrali passa da 4,79 s a 1,72 |
| [EXP-036](#exp-036) | 2026-09-09 | La regola installata su **tre** cadute vere, con verita' di riferimento | OK — **decisivo**: recall **0 su 3**; il tetto di qualunque regola e' 2 su 3, e una caduta il classificatore non la vede |
| [EXP-037](#exp-037) | 2026-09-09 | I sei allarmi di agosto riletti con il modello di oggi | OK — **nessuno dei sei sarebbe emesso**: il piu' alto fa 0,400 |
| [EXP-038](#exp-038) | 2026-09-09 | Le sei architetture su v5, con la selezione di v5 | OK — **decisivo**: l'altezza dal pavimento NON migliora piu' tutte e sei, e il «sei segni concordi» di EXP-025 cade |
| [EXP-039](#exp-039) | 2026-09-09 | Prima sessione di campo con la selezione v5 | OK — quattro raffiche, **una persa per una finestra**, e il pavimento mangia i tre quarti della sessione |
| [EXP-040](#exp-040) | 2026-09-09 | Le 422 clip di agosto rilette con il pacchetto v5 | OK — **decisivo in negativo**: il 91,5% non produce nessuna decisione, il materiale di campo non e' rivalutabile con l'altezza dal pavimento installata |
| [EXP-044](#exp-044) | 2026-09-21 | La selezione DTW rifatta dentro ogni fold LOSO | OK — **decisivo**: 0 fold su 10 riproducono la selezione adottata, ma il nucleo di 6 grandezze non si muove |

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

> **Aggiornamento del 2026-08-27.** Questa frase vale per le cinque architetture
> qui confrontate. Con la rete a grafo aggiunta come sesta
> ([EXP-018](#exp-018)) non regge più alla lettera: il grafo dà $t = -2{,}37$
> contro un valore critico di $2{,}26$. Regge invece la sua forma corretta, che
> è anche più forte: **nessuna architettura fa meglio della GRU, e la sola che
> si avvicina a essere distinguibile fa peggio.** Il grafo non sopravvive
> comunque alla correzione per molteplicità: cinque confronti contro lo stesso
> riferimento richiedono $|t| > 3{,}25$.

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

La causa non è il classificatore: la parità sulle finestre precalcolate è **esatta** (scarto 0,000e+00, prova di parità del pacchetto esportato, `deploy_board/parita.npz`). È lo stimatore di posa, che è un **tracciatore**: mantiene uno stato fra fotogrammi, e differenze infinitesime nella decodifica dell'immagine si amplificano lungo la sequenza (scarto sui landmark 0,0001 al fotogramma 1, 0,0755 all'undicesimo). Vedi [ISS-106](ISSUES.md#iss-106).

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

---

<a id="exp-018"></a>
## EXP-018 — La rete a grafo, sesta architettura

**Data:** 2026-08-27 · **Script:** `pipeline/addestra.py --architettura grafo --lunghezza 22`, poi `pipeline/confronto_appaiato.py`
**Dati:** `feature_v2.csv`, 12 grandezze DTW, camera 1, modo `tre_classi`, LOSO su 10 soggetti
**Esito:** ✔ eseguito · **Uscite:** `risultati/addestramento/run_grafo_tre_classi_DTW_cam1_L22.json`, `punteggi_grafo_tre_classi_DTW_cam1_L22.npz`, `risultati/laboratorio/confronto_appaiato_gru.json`

**Domanda.** Il Capitolo 2 dichiarava di non aver provato le reti a grafo. La
dichiarazione era corretta e costava poco, ma lasciava scoperta l'unica
famiglia citata dalla rassegna di riferimento~(`nguyen`) che il lavoro non
toccava. Provarla costa una run.

**Che cosa è stato provato, esattamente.** Una rete spazio-temporale che
alterna un mescolamento **spaziale** dei nodi e una convoluzione **temporale**
sullo stesso nodo, due blocchi, 32 canali, nucleo temporale 5, dropout 0,3.
**I nodi sono le dodici grandezze geometriche in ingresso, non i giunti dello
scheletro**, e l'adiacenza fra essi è una matrice **appresa**, normalizzata per
riga con una softmax.

Le due scelte vanno dichiarate perché limitano la portata del risultato:

1. **Perché non i giunti.** Il CSV contiene grandezze geometriche, non le
   coordinate dei landmark: una GCN sullo scheletro richiederebbe di
   riestrarre, e cambierebbe *insieme* architettura e rappresentazione. Il
   confronto misurerebbe due variabili invece di una.
2. **Perché l'adiacenza appresa.** Su un grafo di giunti l'adiacenza è
   l'anatomia; qui non esiste un'adiacenza data. Ricavarla dalla correlazione
   misurata porrebbe la domanda di *su quali dati*, e stimarla su tutti
   sarebbe fuga d'informazione. Una matrice appresa non stima nulla fuori dal
   fold.

Ne segue il limite: con nodi privi di topologia anatomica, il vantaggio tipico
della famiglia — sfruttare una struttura nota — non è disponibile. Resta il
meccanismo, cioè mescolare esplicitamente i canali con pesi appresi prima di
guardare il tempo.

**Le sei architetture, stesso protocollo, soglia fissa 0,50 dichiarata a priori:**

| modello | F2 | dispersione | recall | precisione | parametri | durata |
|---|---:|---:|---:|---:|---:|---:|
| LSTM | 0,858 | ±0,082 | 0,934 | 0,715 | 32.227 | 996 s |
| **GRU** (riferimento) | **0,847** | ±0,085 | 0,928 | 0,711 | 24.483 | 1.517 s |
| Transformer | 0,846 | ±0,100 | 0,939 | 0,679 | 34.499 | 689 s |
| CNN 1D | 0,833 | ±0,118 | 0,937 | 0,651 | 46.147 | 667 s |
| Foresta | 0,792 | ±0,080 | 0,807 | **0,838** | 12.760 nodi | **11 s** |
| **Grafo** | **0,779** | ±0,122 | 0,876 | 0,628 | **12.323** | 2.106 s |

**Confronto appaiato contro la GRU, fold per fold** (valore critico $2{,}26$):

```
lstm          +0,011   vince 6/10   t = +0,84    soggetti necessari 114
transformer   −0,002   vince 4/10   t = −0,08
cnn           −0,014   vince 5/10   t = −0,60    soggetti necessari 217
foresta       −0,055   vince 3/10   t = −1,74    soggetti necessari  28
grafo         −0,068   vince 2/10   t = −2,37    soggetti necessari  16
```

**Il risultato, e come va detto.** Il grafo è **il primo confronto fra
architetture di questo lavoro che supera la soglia critica**. Tre precisazioni,
tutte necessarie:

- Il segno è **negativo**: il grafo fa *peggio*, non meglio.
- I confronti contro lo stesso riferimento sono ora cinque, e la molteplicità
  non è controllata. Con la correzione di Bonferroni il valore critico passa da
  $2{,}26$ a $3{,}25$, e $t = -2{,}37$ **non lo supera**. La differenza va
  quindi riportata come indicativa, non come stabilita.
- Nessuna ricerca di iperparametri è stata fatta, qui come per le altre cinque
  architetture. È un confronto a parità dichiarata, non fra modelli ottimizzati.

**Conseguenza sul testo.** La frase di [EXP-011](#exp-011) — «nessuna
architettura è statisticamente distinguibile dalla GRU» — è stata sostituita
con «nessuna fa meglio, e la sola che si avvicina a essere distinguibile fa
peggio». Il Capitolo 2 dichiarava di non aver provato la famiglia:
[ISS-122](ISSUES.md#iss-122).

**Che cosa questo *non* dice.** Che le reti a grafo siano peggiori per il
rilevamento di cadute. Dice che *questa* rete, su *queste* grandezze, con
*questa* numerosità, fa 0,068 di F2 in meno della GRU. Per sostenere quello
scarto servirebbero sedici soggetti; il lavoro ne ha dieci.

**Collegamenti:** [EXP-011](#exp-011), [EXP-013](#exp-013),
[EXP-019](#exp-019), [ISS-122](ISSUES.md#iss-122)

---

<a id="exp-019"></a>
## EXP-019 — Costo per finestra delle sei architetture

**Data:** 2026-08-27 · **Script:** `pipeline/costo_classificatori.py` (nuovo)
**Configurazione:** finestra 22×12, lotto 1, 300 ripetizioni, `tf.function`,
**sul calcolatore di sviluppo e non sulla board**
**Esito:** ✔ eseguito · **Uscita:** `risultati/laboratorio/costo_classificatori.json`

**Domanda.** [EXP-018](#exp-018) risponde a una domanda di accuratezza, che con
dieci soggetti non si decide. La domanda da cui il lavoro parte è invece di
**fattibilità economica**, e quella non dipende dal numero di soggetti: *quanto
costa per finestra ciascuna architettura?*

| architettura | parametri | mediana | media | dev. | rispetto alla foresta |
|---|---:|---:|---:|---:|---:|
| CNN 1D | 46.147 | **1,32 ms** | 1,38 | 0,18 | 0,3× |
| Transformer | 34.499 | 1,61 ms | 1,66 | 0,17 | 0,3× |
| Grafo | **12.323** | 1,80 ms | 1,88 | 0,22 | 0,4× |
| LSTM | 32.227 | 3,45 ms | 3,51 | 0,40 | 0,7× |
| GRU | 24.483 | 3,51 ms | 3,55 | 0,38 | 0,7× |
| **Foresta** (installata) | 6.928 nodi | **4,85 ms** | 5,22 | 0,89 | 1,0× |

**Il risultato che va letto per intero: la foresta è la più lenta per
finestra.** È anche quella installata sul dispositivo. Non è una
contraddizione, ed è il punto in cui la giustificazione della scelta va detta
per esteso: la foresta non è stata scelta perché più veloce in inferenza, ma
perché si addestra in undici secondi contro i venticinque minuti della GRU, non
porta TensorFlow sul dispositivo, e dà risultati riproducibili. Il costo per
finestra non era il criterio, e questa misura mostra che non avrebbe potuto
esserlo.

**Controllo di coerenza.** Il Capitolo 4 riporta 4,47 ms per finestra per il
classificatore installato; qui la stessa grandezza misurata su questo
calcolatore vale 4,85 ms. Sono due macchine diverse e i due valori sono
compatibili: è il primo controllo indipendente che quel numero abbia superato.

**Il margine, quantificato.** Il classificatore è il 5,8% del costo per
fotogramma ([ISS-113](ISSUES.md#iss-113) per la provenienza di quel dato). Un
classificatore dieci volte più pesante porterebbe il totale da 37,7 a circa
57 ms, cioè da 26,5 a ~17,5 fps, che resta sopra i 9 fps su cui il modello è
addestrato. **Il collo di bottiglia resterebbe la percezione.** E la rete a
grafo non è affatto più pesante: metà dei parametri della GRU e un terzo del
tempo per finestra della foresta.

**Validità.** Tre limiti, dichiarati: i tempi sono di **questo calcolatore, non
della board**, e solo il rapporto fra architetture è trasferibile; le cinque
reti sono misurate **non addestrate**, perché il tempo di inferenza dipende
dalla forma e non dai valori dei pesi; la foresta è invece quella installata,
50 alberi, `n_jobs=1`.

**Collegamenti:** [EXP-018](#exp-018), [ISS-113](ISSUES.md#iss-113)

---

<a id="exp-020"></a>
## EXP-020 — L'escursione per punto di vista, rimisurata senza i due difetti

**Data:** 2026-09-06 · **Script:** `pipeline/escursione_viste.py` (nuovo)
**Dati:** UP-Fall, 50 riprese di caduta × 2 telecamere, **dieci** soggetti
**Configurazione:** identica a quella originale — un fotogramma ogni tre,
immagine a metà risoluzione, `model_complexity=1`, soglie 0,5, angolo del
tronco nel piano immagine ripiegato in [0, 90] — **tranne che lo stimatore di
posa nasce e muore dentro ciascuna ripresa**
**Esito:** ✔ eseguita · **Uscita:**
`risultati/laboratorio/escursione_viste_10sog.csv`, il suo `_serie.json` con
la serie per campione e il suo `_riepilogo.json` con le statistiche derivate
(medie, deviazioni, rapporti, conteggi), che nel CSV non compaiono;
`risultati/cinque_soggetti/exp013_camera_viewpoint_indipendente.csv` per il
confronto diretto con la misura originale, che esiste solo a cinque soggetti

**Perché è stata rifatta.** Due difetti trovati lo stesso giorno, il secondo
mentre si sistemava il primo. [ISS-133](ISSUES.md#iss-133): la misura
originale usa **un solo** stimatore per tutte e cinquanta le riprese, e
MediaPipe Pose è un tracciatore, quindi l'ultimo fotogramma di una ripresa
innesca il primo della successiva. [ISS-134](ISSUES.md#iss-134): su Camera2
lo stimatore **perde chi cade e si aggancia a un astante seduto**.

### Il primo difetto: quanto pesa

| | originale | per ripresa |
|---|---:|---:|
| Camera1, media | 71,0° | **73,3°** |
| Camera2, media | 35,7° | **31,9°** |
| rapporto fra le medie | 1,99× | **2,30×** |
| sopra 60°, Camera1 | 18 su 25 | 18 su 25 |
| sopra 60°, Camera2 | 6 su 25 | **4 su 25** |

Lo scarto medio per sequenza è −0,72°, ma il massimo è **68,06°**
(`sub03_act01_trial01_cam02`, da 88,26° a 20,20°). **Non è quindi un rumore
uniforme e piccolo:** su alcune riprese lo stato ereditato cambia
completamente la stima, e su quali riprese dipende dall'ordine di
elaborazione.

### Il secondo difetto: dove si perde il soggetto

Criterio dichiarato: spostamento dell'anca fra due campioni con posa
consecutivi oltre 0,45 in coordinate normalizzate, sommando le componenti. La
serie per campione è salvata, quindi il criterio si può cambiare senza
rieseguire due ore di stima di posa.

| | riprese con cambio di persona |
|---|---:|
| Camera1, laterale | **0 su 50** |
| Camera2, frontale rialzata | **11 su 50** |

(Su cinque soggetti erano 0 su 25 e 6 su 25: la proporzione tiene.)

L'asimmetria è netta e va nella direzione della tesi del capitolo, ma per una
ragione diversa da quella scritta: **non è solo che la vista rialzata comprime
l'angolo, è che in un quarto delle cadute non vede più chi è caduto.** Chi
cade diventa piccolo e lontano, e il rilevatore riparte agganciando qualcun
altro che è rimasto in piedi o seduto nel campo.

### Rifatta su DIECI soggetti

La misura era a cinque soggetti soltanto perché fu eseguita allora: i
fotogrammi grezzi di **entrambe** le telecamere esistono per tutti e dieci.
Rieseguita su cinquanta riprese per due viste, cento sequenze in tutto.

| | Camera1 | Camera2 |
|---|---:|---:|
| escursione media, 39 riprese senza cambio di persona | **74,0° ± 24,2** | **33,2° ± 23,5** |
| sopra 60° | 30 su 39 | 8 su 39 |
| **cambi di persona** | **0 su 50** | **11 su 50** |
| posa rilevata | 85,7% | **97,0%** |

Rapporto fra le medie **2,23×**; per sequenza da **0,98×** a 7,37×, mediano
2,79×. **In una sequenza su trentanove** Camera2 osserva quanto Camera1: il
testo ne dichiarava due su venticinque, quindi il fenomeno è meno variabile di
quanto scritto ma non privo di eccezioni.

**L'ultima riga è quella che non mi aspettavo.** Su Camera2 una posa viene
trovata nel 97,0% dei campioni contro l'85,7% di Camera1: **la vista che porta
meno informazione è quella in cui lo stimatore fallisce meno spesso**, perché
quando perde il soggetto trova comunque qualcun altro. La quota di pose
rilevate non è una misura di qualità, ed è un criterio che il protocollo di
ripresa usava.

### Che cosa cambia rispetto ai cinque soggetti

| | testo prima | 5 soggetti, pulita | **10 soggetti** |
|---|---:|---:|---:|
| Camera1 | 71,0° | 74,6° | **74,0°** |
| Camera2 | 35,7° | 30,6° | **33,2°** |
| rapporto | 1,99× | 2,44× | **2,23×** |
| sequenze con Camera2 ≥ Camera1 | 2 su 25 | 0 su 19 | **1 su 39** |

Il valore a dieci soggetti sta **fra** i due, che è il comportamento atteso di
una stima su un campione doppio: i cinque soggetti in più riportano verso il
centro l'effetto che il sottoinsieme esagerava in entrambe le direzioni.

**La riga che cambia un'affermazione del Capitolo 4.** Il testo dice che *«in
2 sequenze su 25 Camera2 osserva quanto o più di Camera1»*, con il rapporto
per sequenza che scende a 0,39×. Sulle riprese in cui entrambe le viste
seguono davvero il soggetto **il rapporto minimo è 1,04: Camera2 non osserva
mai più di Camera1.** Le due eccezioni erano artefatti — una veniva dal cambio
di persona, l'altra dallo stato ereditato.

L'effetto è quindi **più grande e più regolare** di quanto la tesi dichiari:
2,44× invece di 1,99×, e senza controesempi.

**Validità.** Resta una misura a **cinque soggetti**, come l'originale.
Riguarda una grandezza **descrittiva**: non entra in alcun addestramento, e i
valori di F2 della Tabella delle viste non ne dipendono. La soglia di 0,45 sul
salto dell'anca è una scelta, calibrata fra il salto più grande osservato in
una caduta seguita correttamente (0,31) e il più piccolo dei sei cambi di
persona (0,49); le serie salvate permettono di rifare il conto con un'altra
soglia.

### Il cambio di persona arriva anche nelle feature — verificato

La domanda che questa run lasciava aperta era se il cambio di persona
riguardasse solo la misura descrittiva o anche le **feature usate per
addestrare**, che passano dallo stesso stimatore a persona singola. Si
risponde senza rieseguire nulla: `landmarks_raw_5sog_backup.npz` contiene i
landmark per fotogramma dell'impianto a cinque soggetti, cioè esattamente il
dato da cui quelle feature sono state costruite. Stesso criterio, applicato
al salto dell'anca fra fotogrammi consecutivi con posa:

| | riprese di caduta | con cambio di persona | salto massimo, mediana |
|---|---:|---:|---:|
| Camera1 | 24 | **0** | 0,10 |
| Camera2 | 25 | **3** | 0,06 |

Le tre sono `sub02_act04` (salto 0,71), `sub01_act04` (0,53) e `sub04_act03`
(0,48). Su Camera1 il salto più grande di tutte e ventiquattro le riprese vale
**0,31**, cioè sotto la soglia di 0,45: la separazione fra i due gruppi è
netta, e non è la soglia a produrla.

**Quindi sì: il divario di F2 fra le due viste ha in parte questa causa.** Nel
12% delle cadute di Camera2 il modello riceve, per la fase «a terra», le
grandezze di un'altra persona. Resta un effetto del punto di vista — è la
vista rialzata a far perdere il soggetto — ma il meccanismo non è la
compressione angolare.

**Un risultato secondario, e va detto perché riguarda il protocollo di
misura.** Sui fotogrammi interi i cambi sono **3 su 25**; nella misura di
EXP-013, che campiona un fotogramma ogni tre, sono **6 su 25**. Il
sottocampionamento raddoppia le perdite di aggancio, perché il tracciatore
deve colmare un salto tre volte più grande. La grandezza descrittiva è quindi
misurata in condizioni **peggiori** di quelle in cui il sistema lavora.

**Verificato con:** `landmarks_raw_5sog_backup.npz`, 58.823 fotogrammi, salto
dell'anca fra fotogrammi consecutivi con posa, soglia 0,45 -> tabella qui
sopra.

**Collegamenti:** [ISS-133](ISSUES.md#iss-133), [ISS-134](ISSUES.md#iss-134),
[ISS-106](ISSUES.md#iss-106), [EXP-013](#exp-013)

---

<a id="exp-021"></a>
## EXP-021 — Gli errori scomposti per attività e per tipo di caduta

**Data:** 2026-09-06 · **Natura: RILETTURA, non run nuova**
**Dati:** i punteggi per finestra già salvati in
`risultati/addestramento/punteggi_foresta_tre_classi_DTW_cam1.npz`, prodotti
il 20 agosto
**Esito:** ✔ · **Uscita:** `risultati/addestramento/_mappa_finestre.npz`

**Va detto subito che cosa NON è:** non è un addestramento nuovo. Le sei
architetture furono confrontate il 20 agosto ([EXP-011](#exp-011)) e la rete a
grafo il 27 ([EXP-018](#exp-018)). Qui si rileggono quei file e si attribuisce
ogni finestra all'attività da cui proviene, cosa che non era mai stata fatta.

**Come.** Le finestre sono state ricostruite con `src/dati.py` e allineate ai
punteggi salvati: le numerosità coincidono su tutti e dieci i fold, il che
rende l'attribuzione verificabile e non congetturale.

### I falsi allarmi non sono diffusi: sono concentrati

| attività | finestre | falsi allarmi | quota |
|---|---:|---:|---:|
| camminare | 1.390 | 0 | 0,0% |
| stare in piedi | 2.552 | 0 | 0,0% |
| saltare | 1.079 | 0 | 0,0% |
| sedersi | 2.525 | 19 | 0,8% |
| raccogliere un oggetto | 330 | 11 | 3,3% |
| **sdraiarsi** | 2.201 | **389** | **17,7%** |

**Su 419 falsi allarmi, 389 --- il 93% --- vengono da una sola attività.**
Camminare, stare in piedi e saltare non ne producono nemmeno uno su cinquemila
finestre.

### L'ipotesi della velocità, verificata e smentita

L'obiezione naturale e' che il sistema si allarmi per il movimento rapido.
Misurando il picco di velocita' **verticale** del corpo dentro la finestra:

| gruppo | mediana | p90 |
|---|---:|---:|
| cadute vere | 0,055 | 0,622 |
| **camminare** | **0,087** | 0,629 |
| sdraiarsi, falso allarme | 0,030 | 0,106 |
| sdraiarsi, riconosciuta | 0,005 | 0,031 |

**Camminare ha il picco di discesa piu' alto delle cadute**, perche' in due
secondi e mezzo di passi il corpo oscilla molte volte. Se il sistema decidesse
sulla velocita', camminare sarebbe il falso allarme principale: non ne produce
nessuno. **La velocita' istantanea non e' il discriminante**, ed e' la
conferma diretta dell'argomento del Capitolo 3 a favore degli integrali.

*(Nota su un errore commesso e corretto: la prima versione di questa analisi
usava `A3_hip_vel`, che e' il MODULO dello spostamento e quindi velocita' in
qualunque direzione. Con quella, camminare risultava sette volte piu' veloce
delle cadute --- vero ma privo di significato, perche' quella grandezza non ha
un verso. Rifatta con `A1_vy`, che e' verticale con segno.)*

### E l'altezza dal pavimento non puo' risolverlo, in questo archivio

Misurata con la grandezza reintrodotta il 6 settembre
([ISS-139](ISSUES.md#iss-139)):

| | altezza del bacino, in lunghezze di torso |
|---|---:|
| camminare | 1,69 |
| sedersi | 1,58 |
| **sdraiarsi** | **0,12** |
| **a terra dopo una caduta** | **0,11** |

**Sono la stessa quota.** In UP-Fall ci si sdraia sul pavimento, non su un
divano: nell'archivio la distinzione fra «coricato» e «caduto» **non esiste
come informazione statica**, e vive interamente nella dinamica della
transizione. E' la conferma piu' netta che il compito giusto sia riconoscere
l'evento e non lo stato ([DEC-107](DECISIONS.md#dec-107)).

Ne segue anche che il beneficio atteso da `h_pavimento` **non e' sui falsi
allarmi di laboratorio** ma sui falsi negativi e sul trasferimento in casa,
dove il divano esiste e la differenza misurata sul campo e' +1,47 contro +0,02
lunghezze di torso.

### Non tutte le cadute sono ugualmente riconoscibili

| tipo di caduta | finestre | richiamo |
|---|---:|---:|
| di lato | 274 | 0,934 |
| in avanti sulle mani | 329 | 0,915 |
| seduta su sedia vuota | 288 | 0,753 |
| in avanti sulle ginocchia | 302 | 0,715 |
| **all'indietro** | 230 | **0,704** |

**Ventitre punti di richiamo** fra la migliore e la peggiore: un divario piu'
grande di quello fra due qualunque delle sei architetture confrontate. La
caduta all'indietro e' la piu' difficile, ed e' plausibile che sia lo stesso
meccanismo che rende cieca la vista rialzata --- e' la direzione in cui il
tronco ruota meno nel piano dell'immagine. **E' una lettura, non una misura.**

**Validita'.** Dieci soggetti, camera 1, foresta sul sottoinsieme DTW, soglia
0,50 dichiarata a priori. Le attivita' sono quelle di UP-Fall e i nomi seguono
la numerazione ufficiale.

**Collegamenti:** [EXP-011](#exp-011), [EXP-015](#exp-015),
[ISS-139](ISSUES.md#iss-139), Capitolo 4 `tab:errori_attivita`,
`tab:richiamo_tipo`

---

<a id="exp-022"></a>
## EXP-022 — La riestrazione completa (v3), e la selezione DTW rifatta

**Data:** 2026-09-06, chiusa alle 20:57 · **Script:** `pipeline/estrai_feature.py`,
`src/geometry.py`, `pipeline/analisi_dtw.py`
**Dati:** UP-Fall, **220 riprese**, 10 soggetti, 2 telecamere
**Esito:** ✔ · **Uscita:** `dataset/processed/features/feature_v3.csv` (77 MB,
fuori da git), `risultati/dtw/classifica_dtw.csv`, `risultati/dtw/scelte.txt`

**Perché.** Tre difetti che si chiudevano con la stessa riestrazione:
[ISS-138](ISSUES.md#iss-138) — un solo stimatore di posa per tutte le riprese,
quindi feature dipendenti dall'ordine; [ISS-139](ISSUES.md#iss-139) —
`h_pavimento` assente dal motore; e i due video mancanti su 220.

### Il dataset, prima e dopo

| | v2 | **v3** |
|---|---:|---:|
| riprese | 218 | **220** |
| fotogrammi | 114.923 | **116.362** |
| camera 1 / camera 2 | 57.786 / 57.137 | 58.359 / 58.003 |
| pose rilevate | 95,5% | **95,9%** |
| grandezze | 32 | **33** |
| fotogrammi «caduta in corso» | 5.542 | 5.542 |
| fotogrammi «a terra» | 10.524 | 10.524 |

**Le etichette non cambiano di un fotogramma**, ed è il controllo che serviva:
i due video aggiunti sono attività normali (`sub06_act08`, `sub07_act10`), e
l'etichettatura non dipende dalla stima di posa. I 1.439 fotogrammi in più sono
esattamente quelli dei due video: 866 su camera 2 e 573 su camera 1.

### L'altezza dal pavimento, misurata

Stima **causale** — si accumulano le osservazioni di chi sta in piedi e si
adatta la retta quando ne bastano — e poi ricalcolata a fine telecamera con la
retta stimata su tutte le riprese, così il valore non dipende dall'ordine.
Copertura: **100% dei fotogrammi con posa**. Mediane, in lunghezze di torso:

| etichetta | mediana |
|---|---:|
| normale | 1,517 |
| caduta in corso | 0,958 |
| **a terra** | **0,502** |

Monotona come dev'essere, e con una separazione netta fra il primo e l'ultimo
valore.

### La selezione DTW

Rifatta sulle 33 grandezze. Rispetto alla selezione storica — quella installata
sulla board, che veniva da v2 e da 32 grandezze, conservata in
`risultati/dtw/classifica_dtw_32grandezze.csv` e `scelte_32grandezze.txt` —
**cambia una colonna su dodici**: entra `A2_angolo_tronco` (che sale al primo
posto), esce `A2_testa_rel_y`.

**`A3_h_pavimento` non viene scelta: è 19ª su 33.** Il criterio misura la
separabilità di una grandezza **da sola**, e da sola l'altezza dal pavimento non
distingue chi si sdraia da chi cade — lo mostra [EXP-021](#exp-021): in UP-Fall
ci si sdraia sul pavimento, e le due quote coincidono. Che poi il classificatore
ne tragga vantaggio lo dice [EXP-023](#exp-023): è un limite del criterio di
selezione, non della grandezza.

**Validità.** Il dataset e il bacino dei candidati sono cambiati **insieme**: il
cambio di una colonna nella selezione **non è attribuibile** all'uno o
all'altro. Per separarli servirebbe una selezione su v3 ristretta alle 32
grandezze vecchie, che non è stata fatta.

**Collegamenti:** [ISS-138](ISSUES.md#iss-138), [ISS-139](ISSUES.md#iss-139),
[EXP-008](#exp-008), [EXP-023](#exp-023)

---

<a id="exp-023"></a>
## EXP-023 — L'altezza dal pavimento nel classificatore: DTW contro DTWH

**Data:** 2026-09-06, 21:35 · **Script:** `pipeline/addestra.py --csv feature_v3.csv`
**Dati:** v3, camera 1, dieci soggetti, LOSO a dieci fold
**Configurazione:** foresta casuale, tre classi, finestra 22 campioni a passo 2,
soglia **0,50 dichiarata a priori**, scaler stimato sul solo addestramento del
fold
**Esito:** ✔ · **Uscita:**
`risultati/addestramento/run_foresta_tre_classi_DTW_cam1_L22.json` e
`..._DTWH_cam1_L22.json`, con i punteggi per fold negli `.npz`

Le due run differiscono **per una colonna sola**: DTWH è DTW più
`A3_h_pavimento`. Stesso dataset, stessi fold, stesso seme, stessa soglia.

| | colonne | F2 | richiamo | precisione | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|---:|
| DTW | 12 | 0,807 ± 0,104 | 0,834 | 0,806 | 1.242 | 501 | 249 |
| **DTWH** | 13 | **0,866 ± 0,102** | **0,894** | 0,828 | 1.328 | **443** | **163** |

**I falsi negativi calano del 35%, da 249 a 163, e i falsi allarmi calano
anch'essi**, da 501 a 443: non è uno scambio fra i due errori, è un
miglioramento su entrambi. Il guadagno di F2 è **+0,059**, cioè **sotto** la
dispersione fra soggetti (±0,085): sull'F2 aggregato non è distinguibile dal
rumore fra persone, sul conteggio degli errori sì.

**Il confronto con v2 non è pulito e va detto.** La foresta su v2 dava F2 0,792
con 271 FN e 421 FP; la stessa su v3 dà 0,807 con 249 FN e 501 FP. Fra le due
sono cambiati il dataset, i due video aggiunti e una colonna della selezione:
**il salto da 0,792 a 0,807 non è attribuibile a nessuno dei tre in
particolare.** Il confronto che regge è l'altro, DTW contro DTWH sullo stesso
v3.

**Validità.** Dieci soggetti, una sola architettura. Le altre cinque erano
ancora su v2 al momento di questa run: il confronto fra architetture su v3 è
[EXP-025](#exp-025).

**Collegamenti:** [ISS-139](ISSUES.md#iss-139), [EXP-021](#exp-021),
[EXP-022](#exp-022), [EXP-011](#exp-011)

---

<a id="exp-024"></a>
## EXP-024 — La prova di durata sulla board, 4,6 ore

**Data:** 2026-09-06, dalle 15:23 · **Script:** `deploy_board/rileva.py` sulla
Radxa ROCK 4D, telecamera USB collegata
**Configurazione:** quella installata — compito «evento», sottoinsieme DTW a 12
colonne, finestra 22 a passo 2, soglia 0,50, **cinque finestre consecutive** e
**trenta secondi** di sospensione
**Esito:** ✔ eseguita, riepilogo `parziale` — i file sono stati copiati mentre la
sessione era ancora viva
**Uscita:** `risultati/sessioni/20260906/notte_20260906_1523/`

È l'ultima delle richieste del relatore che richiedeva l'hardware.

| | |
|---|---:|
| durata | **4,59 ore** (16.508 s) |
| sospensione della macchina | **~0 s** — non si è sospesa |
| fotogrammi | 119.928 |
| frequenza | **7,26 fps** |
| pose valide | **35,1%** |
| interruzioni della telecamera | 2, per 5,1 s in tutto, riprese da sole |
| finestre sopra soglia | 168 |
| **eventi di allarme** | **14** = 3,05/ora |
| tempo in allarme | 0,3% |

**Il doppio orologio ha fatto il suo lavoro.** Orologio di sistema e cronometro
monotòno coincidono a meno di 3,4 microsecondi: la macchina non si è sospesa, e
stavolta lo sappiamo invece di sperarlo ([ISS-130](ISSUES.md#iss-130)).

**Le verifiche di avvio.** L'impronta del motore geometrico coincide con quella
dichiarata nel `metadata.json`, e la prova di parità su duecento finestre dà
scarto **0,000e+00** fra board e calcolatore. La parità per fotogramma — la
sola che intercetterebbe [ISS-106](ISSUES.md#iss-106) — si è dichiarata *non
eseguita*: mancava la cartella dei fotogrammi, e manca perché nessuna sessione
della board ne produce più ([ISS-142](ISSUES.md#iss-142)).

**Il costo per fotogramma, consolidato:** 136,65 ms in totale — percezione
116,38 (85,2%), classificatore 19,51 (14,3%), pre e post insieme 0,75. Chiude
[ISS-113](ISSUES.md#iss-113); il merito, cioè il divario con il Capitolo 5,
resta [ISS-137](ISSUES.md#iss-137).

**Che cosa questa sessione NON dice.** I quattordici allarmi **non sono
verificabili**, e la ragione è più seria di una dimenticanza: `rileva.py` non
salva immagini affatto ([ISS-142](ISSUES.md#iss-142)). Il registratore di
agosto salvava una clip di ±10 s attorno a ogni allarme ed è con quelle che
gli allarmi delle sessioni domestiche sono stati guardati uno per uno; il
registratore della board non lo fa, e la sua documentazione sostiene il
contrario. Di quei quattordici momenti non esiste alcuna immagine, né sul
dispositivo né altrove. Non risulta alcuna caduta messa in scena, ma «non risulta» non è un
riscontro annotato. Il numero riportabile è il **tasso di eventi**, 3,1 ogni
ora; chiamarli falsi allarmi richiederebbe di guardarli.

E le pose valide sono il **35%**: per gran parte delle quattro ore e mezzo la
stanza era vuota. È una prova di **durata e di costo**, non di rilevamento.

**Collegamenti:** [ISS-113](ISSUES.md#iss-113), [ISS-137](ISSUES.md#iss-137),
[ISS-140](ISSUES.md#iss-140), [EXP-016](#exp-016)

---

<a id="exp-025"></a>
## EXP-025 — Le architetture rifatte su v3

**Data:** 2026-09-07, 09:22 → 12:44 · **Esito:** ✔ **conclusa**
**Script:** `pipeline/addestra.py --csv feature_v3.csv --modello <arch> --modo
tre_classi --feature DTW|DTWH --camera 1`
**Registro dell'esecuzione:** `risultati/addestramento/log_riaddestramento_v3.txt`

Cinque architetture — GRU, LSTM, CNN 1D, Transformer, rete a grafo — prima su
DTW e poi su DTWH. La foresta è già fatta ([EXP-023](#exp-023)).

**Perché.** Dopo [EXP-022](#exp-022) ogni numero del Capitolo 4 viene da run su
v2, cioè da un dataset che dipende dall'ordine di estrazione e non contiene
l'altezza dal pavimento. Il confronto fra architetture va rifatto sullo stesso
dato, altrimenti mette a confronto misure prese su archivi diversi.

**Le run su v2 sono conservate** in `risultati/addestramento/v2/`: i nomi dei
file non contengono la versione del dataset e GRU e grafo sarebbero state
sovrascritte.

### Le sei architetture su v3

Dodici run, tre ore e mezzo. Soglia 0,50 dichiarata a priori, LOSO a dieci fold,
camera 1.

| architettura | DTW (12 col.) | **DTWH (13 col.)** | guadagno |
|---|---:|---:|---:|
| CNN 1D | 0,828 ± 0,099 | **0,885 ± 0,093** | +0,057 |
| foresta | 0,807 ± 0,104 | **0,866 ± 0,102** | +0,059 |
| LSTM | 0,783 ± 0,103 | **0,864 ± 0,067** | +0,081 |
| Transformer | 0,799 ± 0,099 | **0,860 ± 0,089** | +0,061 |
| GRU | 0,819 ± 0,096 | **0,842 ± 0,098** | +0,023 |
| rete a grafo | 0,699 ± 0,088 | 0,756 ± 0,107 | +0,057 |

**L'altezza dal pavimento migliora TUTTE e sei le architetture.** Preso da solo
nessun guadagno è distinguibile: il più grande, +0,081, sta sotto la dispersione
fra soggetti (±0,085). Ma **sei segni concordi su sei** non lo sono: sotto
l'ipotesi che la colonna non serva, la probabilità di sei miglioramenti su sei è
$2^{-6} = 0{,}016$. Il guadagno medio è **+0,056**.

È la conferma che [EXP-023](#exp-023) suggeriva su una sola architettura, e
rende la scelta di [ISS-139](ISSUES.md#iss-139) una decisione informata: la
grandezza non aiuta *un* modello, aiuta il compito.

### Il confronto fra architetture, rifatto

| | v2 (dataset vecchio) | **v3** |
|---|---:|---:|
| migliore | LSTM 0,858 | CNN 1D 0,828 |
| peggiore fra le cinque | foresta 0,792 | LSTM 0,783 |
| escursione fra le cinque | 0,066 | **0,045** |
| rete a grafo | 0,779 | 0,699 |

**L'ordine si rimescola e l'escursione si stringe.** Su v2 la LSTM era prima e
la foresta ultima; su v3 la CNN è prima e la LSTM penultima. Tutte e cinque
stanno dentro **0,045**, cioè **metà della dispersione fra soggetti**: è la
dimostrazione più forte che il capitolo abbia dell'affermazione che porta —
**le architetture non sono distinguibili fra loro**, e chi ne dichiarasse una
vincitrice starebbe leggendo il rumore.

La rete a grafo resta ultima in entrambi i dataset, ed è l'unica che si
distingua: peggiora di 0,08 rispetto alla mediana delle altre.

**Verificato con:** `risultati/addestramento/log_riaddestramento_v3.txt`, dodici
run concluse con uscita 0; ogni `run_*.json` porta il proprio `_provenienza`
con il comando che l'ha prodotta.

**Che cosa resta da fare, ed è testo:** le tabelle del Capitolo 4 riportano
ancora i valori su v2. Vanno riscritte su questi, dichiarando che il dataset è
stato riestratto.

---

<a id="exp-026"></a>
## EXP-026 — Le tre righe della vista, rifatte a dieci soggetti e con le due cause separate

**Data:** 2026-09-07 · **Script:** `pipeline/viste_incrociate.py` (nuovo)
**Dati:** `feature_v3.csv`, dieci soggetti, due telecamere
**Configurazione:** foresta casuale, tre classi, A3 **senza** `A3_h_pavimento`
— dodici colonne, la stessa composizione dell'A3 con cui la tabella fu
prodotta — finestra 22 a passo 2, soglia **0,50 dichiarata a priori**,
leave-one-subject-out con il soggetto successivo come validation ed escluso
dall'addestramento, scaler stimato sui soli fotogrammi di addestramento del
fold
**Esito:** ✔ · **Uscita:**
`risultati/laboratorio/viste_incrociate_10sog.json` e
`..._senza_contaminate.json`

**Perché.** La tabella `tab:viste` del Capitolo 4 veniva dall'impianto a
**cinque** soggetti, mentre la misura geometrica che la spiega
([EXP-020](#exp-020)) era a dieci: due provenienze diverse nello stesso
paragrafo. E il divario di F2 fra le viste conteneva **due cause** che il testo
poteva solo dichiarare senza separarle — la compressione prospettica e lo
stimatore che cambia persona ([ISS-134](ISSUES.md#iss-134)).

### Le tre righe, a dieci soggetti

| addestrata su | verificata su | F2 | falsi allarmi | cadute non viste |
|---|---|---:|---:|---:|
| Camera 1 | Camera 1 | **0,822 ± 0,099** | 722 | 186 |
| Camera 1 | Camera 2 | **0,488 ± 0,119** | **3.252** | 451 |
| Camera 1 + 2 | Camera 2 | **0,731 ± 0,188** | 751 | 335 |
| *Camera 2* | *Camera 2* | *0,753 ± 0,179* | *1.067* | *246* |

La quarta riga non fa parte della tabella del capitolo: serve al risultato
«controintuitivo» che il capitolo dichiarava, ed è quella che lo smentisce
([ISS-143](ISSUES.md#iss-143)).

**Divario fra le viste: 0,334 di F2.** Addestrare su entrambe ne recupera il
**73%** e riporta i falsi allarmi da 3.252 a 751, cioè al livello della prima
riga.

Confronto con i valori pubblicati, che erano a cinque soggetti e su v2:

| | cinque soggetti | **dieci soggetti (v3)** |
|---|---:|---:|
| Camera 1 → Camera 1 | 0,857 | 0,822 |
| Camera 1 → Camera 2 | 0,434 | 0,488 |
| Camera 1+2 → Camera 2 | 0,678 | 0,731 |
| **divario** | **0,422** | **0,334** |
| recuperato addestrando su due | 58% | **73%** |

Il divario si riduce di 0,088 ma resta **tre volte la dispersione fra
soggetti**: la conclusione del capitolo non cambia, i numeri sì.

### Le due cause, separate

Stessa cosa, escludendo dall'addestramento e dalla verifica le **11 riprese**
in cui lo stimatore passa a un'altra persona:

| | con tutte le riprese | **senza le 11 contaminate** |
|---|---:|---:|
| Camera 1 → Camera 1 | 0,822 ± 0,099 | 0,822 ± 0,099 |
| Camera 1 → Camera 2 | 0,488 ± 0,119 | **0,466 ± 0,212** |
| Camera 1+2 → Camera 2 | 0,731 ± 0,188 | 0,673 ± 0,206 |
| **divario** | 0,334 | **0,356** |

**Il divario non si chiude: semmai cresce di 0,022, che è dentro il rumore.**

**Ne segue che le due cause non pesano allo stesso modo, ed è il risultato
utile:** il cambio di persona dello stimatore falsava la **misura geometrica**
— lì il rapporto passava da 2,13× a 2,23× togliendolo — ma **non è ciò che
rende la vista rialzata peggiore per il classificatore**. Il divario di F2 è
sostanzialmente tutto compressione prospettica.

**Il confronto va letto con una cautela, ed è dichiarata nel codice:** le due
esecuzioni non hanno lo stesso insieme di verifica. Togliere 11 riprese di
caduta toglie 274 finestre positive da Camera 2, quindi la seconda colonna
misura «il divario sulle riprese pulite», non «il divario senza l'effetto
dello stimatore» su un insieme identico. È la domanda giusta comunque: se il
difetto spiegasse il divario, sulle riprese pulite il divario dovrebbe
restringersi. Non lo fa.

### Il risultato «controintuitivo» del capitolo non regge

Il Capitolo 4 affermava che un modello addestrato su Camera 1 e verificato su
Camera 2 **batte di 2,5×** un modello addestrato direttamente su Camera 2, e ne
traeva che *la qualità del punto di vista in addestramento conta più della sua
corrispondenza con quello di esercizio*.

| | cinque soggetti | **dieci soggetti** |
|---|---:|---:|
| Camera 1 → Camera 2 | 0,434 | 0,488 |
| Camera 2 → Camera 2 | ≈0,17 | **0,753** |
| rapporto | 2,5× a favore del trasferimento | **1,5× a favore dell'addestramento diretto** |

**Il confronto si rovescia**, e lo fa anche escludendo le riprese contaminate
(0,466 contro 0,747). L'affermazione è stata ritirata dal capitolo
([ISS-143](ISSUES.md#iss-143)) e sostituita da quella ordinaria: addestrare
sulla vista di esercizio è meglio che trasferirvi da un'altra.

Ciò che sopravvive è più debole e più utile: **addestrare su entrambe le viste
(0,731) e addestrare solo su quella di esercizio (0,753) non sono
distinguibili**, perché distano meno della dispersione fra soggetti.

**Validità.** Dieci soggetti, una sola architettura, camera 1 come sorgente di
addestramento nelle prime tre righe. Il numero della prima riga (0,822) non
coincide con la run canonica su DTW (0,807) perché il bacino di grandezze è A3
e non il sottoinsieme scelto dal DTW: sono due configurazioni diverse, e la
tabella confronta le **viste**, non le rappresentazioni.

**Collegamenti:** [EXP-020](#exp-020), [ISS-133](ISSUES.md#iss-133),
[ISS-134](ISSUES.md#iss-134), Capitolo 4 `tab:viste`, `fig:viste`

---

<a id="exp-027"></a>
## EXP-027 — Le occlusioni rimisurate, e la scoperta che dipendono dalle colonne

**Data:** 2026-09-07 · **Script:** `pipeline/occlusioni.py`
**Dati:** `landmarks_raw.npz` del 20 agosto — 114.923 fotogrammi, camera 1 —
con il **motore geometrico corrente** (33 grandezze)
**Configurazione:** foresta casuale, soglia 0,50 dichiarata a priori, LOSO a
dieci fold, punti mascherati **congelati** all'ultima posizione nota
**Esito:** ✔ · **Uscita:** `risultati/occlusioni/foresta_DTW.json`,
`..._colonne_agosto.json`, `..._agosto_v2.json` (la misura precedente,
conservata)

**Perché.** La misura era di agosto, quindi con il motore geometrico e la
selezione DTW di allora. Il resto del lavoro è stato rifatto sul dataset
riestratto: lasciarla indietro avrebbe messo nello stesso capitolo numeri di due
impianti diversi, che è il difetto di [ISS-129](ISSUES.md#iss-129).

### Il numero peggiore raddoppia

| gruppo congelato | agosto | **7 settembre** |
|---|---:|---:|
| anche *(riferimento di A3)* | +0,012 | +0,015 |
| gambe | −0,000 | +0,001 |
| naso | −0,008 | **−0,002** |
| metà sinistra | +0,008 | −0,004 |
| caviglie | −0,015 | −0,012 |
| **casuale 55%** (5 punti su 9) | −0,009 | **−0,032** |
| **spalle** | **−0,020** | **−0,037** |

La conclusione regge — 0,037 resta sotto la dispersione fra soggetti, 0,071 —
ma **il margine passa da un fattore quattro a un fattore due**, e una delle due
osservazioni del capitolo cade: le spalle sono ora **l'unico gruppo anatomico
che costa più di un gruppo casuale della stessa dimensione** (−0,037 contro
+0,001), che è precisamente il criterio con cui il capitolo definisce «critico».

### Che cosa lo ha causato, misurato invece che ipotizzato

Fra le due esecuzioni sono cambiate **due cose insieme** — il motore geometrico
e la selezione DTW — quindi il confronto da solo non dice quale delle due pesi.
La terza esecuzione le separa: **motore nuovo, colonne di agosto**.

| | agosto | motore nuovo, **colonne di agosto** | motore nuovo, colonne nuove |
|---|---:|---:|---:|
| base | 0,857 | 0,856 | 0,853 |
| naso | −0,008 | **−0,007** | −0,002 |
| **spalle** | **−0,020** | **−0,019** | **−0,037** |
| casuale 55% | −0,009 | **−0,007** | −0,032 |

**Con le colonne di agosto i numeri di agosto tornano.** La causa non è il
motore geometrico, non sono i landmark: **è la selezione delle colonne**.

**E si spiega con una colonna sola.** Fra le due selezioni cambia un elemento su
dodici: entra `A2_angolo_tronco` — l'angolo del tronco, cioè il vettore fra il
punto medio delle **spalle** e quello delle anche — al posto di
`A2_testa_rel_y`, che dipendeva dal **naso**. Tutto il resto del quadro segue:
il costo delle spalle raddoppia, quello del naso si dimezza, e il mascheramento
casuale di cinque punti su nove — che spesso pesca le spalle — passa da −0,007
a −0,032.

### Che cosa questo cambia nel testo

L'affermazione «l'informazione è distribuita sulla configurazione e non
concentrata in alcuni segmenti» **non è una proprietà del problema: è una
proprietà del sottoinsieme di grandezze scelto**. Con dodici colonne che non
contengono l'angolo del tronco, nessun gruppo di punti è critico; con dodici che
lo contengono, le spalle lo diventano quasi.

È un risultato utile a chi installasse il sistema: **la robustezza alle
occlusioni si può scegliere**, ed è una conseguenza della selezione delle
grandezze e non un dato di natura.

**Validità.** I landmark restano quelli estratti il 20 agosto, quindi con lo
stimatore condiviso fra riprese ([ISS-138](ISSUES.md#iss-138)): rifarli
significa riestrarre la posa da tutti i video, e le tre esecuzioni li
condividono, quindi il confronto fra loro è pulito anche se la base non lo è.

**Collegamenti:** [ISS-138](ISSUES.md#iss-138), [EXP-022](#exp-022),
Capitolo 4 `tab:occlusioni`, `fig:occlusioni`

---

<a id="exp-028"></a>
## EXP-028 — La latenza di rilevamento, misurata in laboratorio, e la persistenza finalmente giustificata

**Data:** 2026-09-07 · **Script:** `pipeline/latenza_laboratorio.py` (nuovo)
**Dati:** `feature_v3.csv`, camera 1, **50 riprese di caduta**, dieci soggetti
**Natura:** RILETTURA — i punteggi sono quelli salvati dalla LOSO, nessun
addestramento nuovo
**Esito:** ✔ · **Uscita:**
`risultati/laboratorio/latenza_laboratorio_foresta_tre_classi_DTWH_cam1_L22.json`
e la stessa per la configurazione DTW

**Perché.** Il lavoro dichiarava la latenza **non misurabile**, e per il campo è
vero: le cadute domestiche sono annotate al minuto mentre la grandezza vale
pochi secondi ([ISS-108](ISSUES.md#iss-108)). Ma quella conclusione era stata
estesa a tutto il lavoro, e **in laboratorio non vale**: in UP-Fall l'etichetta
è per fotogramma, quindi l'istante in cui la caduta comincia è noto a 1/18 di
secondo. La latenza si misura esattamente, e su **cinquanta** cadute invece che
su cinque.

**Come.** Per ogni ripresa di caduta: `inizio` = primo fotogramma etichettato
«caduta in corso»; `allarme` = fine della k-esima finestra consecutiva sopra
soglia; `latenza = allarme − inizio`. L'allarme sta alla **fine** della finestra
perché è lì che la decisione esiste.

Le finestre sono ricostruite con lo stesso codice che le ha prodotte in
addestramento e **allineate ai punteggi salvati**: lo script si ferma se le
numerosità non coincidono fold per fold, perché senza allineamento ogni latenza
sarebbe attribuita alla ripresa sbagliata.

### La latenza, e il prezzo della persistenza

Configurazione DTWH, soglia 0,50, dieci soggetti, 9 fps effettivi:

| persistenza *k* | riprese con allarme | richiamo | latenza mediana | p90 | peggiore |
|---:|---:|---:|---:|---:|---:|
| 1 | 50 su 50 | **1,00** | **1,44 s** | 3,39 | 4,00 |
| 2 | 48 su 50 | 0,96 | 1,75 s | 3,70 | 4,22 |
| 3 | 47 su 50 | 0,94 | 2,00 s | 4,04 | 4,56 |
| 4 | 47 su 50 | 0,94 | 2,22 s | 4,36 | 7,06 |
| **5** *(installata)* | **45 su 50** | **0,90** | **2,44 s** | 4,51 | 5,00 |
| 7 | 45 su 50 | 0,90 | 2,89 s | 4,96 | 5,44 |
| 10 | 44 su 50 | 0,88 | 3,56 s | 5,52 | 6,11 |

Sulla configurazione **installata** (DTW, dodici colonne) il quadro è lo stesso:
k=5 dà richiamo 0,88 e mediana 2,47 s.

**Ogni passo di persistenza costa esattamente 0,222 s** — il passo della
finestra — e una frazione di richiamo. Passare da k=1 a k=5 costa **1,0 s di
latenza e dieci punti di richiamo** (50 riprese su 50 diventano 45).

**Che cosa si compra in cambio, misurato sulle sessioni domestiche:** con la
sospensione installata di 30 s gli eventi di falso allarme passano da 16,0 a
11,1 all'ora, cioè **−31%** (a sospensione 10 s: da 32,5 a 21,6, −34%). È la prima volta che i due lati del compromesso stanno nello stesso
posto, ed è ciò che serve per scegliere *k* invece di ereditarlo.

### Il limite inferiore analitico non è un limite inferiore

La tabella `tab:latenza` del Capitolo 5 dichiara **3,778 s** come limite
inferiore, sommando riempimento della finestra (2,743 s), persistenza (0,997 s)
e calcolo (0,038 s).

**La mediana misurata alla stessa regola è 2,44 s**, e riportata alla frequenza
di quella tabella resta **2,74 s**: circa un secondo **sotto** il presunto
limite inferiore.

La ragione è nell'assunzione: la scomposizione suppone che la finestra debba
riempirsi **dopo** l'inizio della caduta. Non è richiesto. Il classificatore
decide su finestre che **stanno a cavallo** dell'istante di inizio, e il
movimento iniziale della caduta basta a portarle sopra soglia. Il minimo
misurato a k=1 è **+0,17 s**: una finestra che contiene tre fotogrammi di caduta
e quarantuno di ciò che la precede scatta comunque.

**3,778 s resta un numero utile, ma è la latenza del caso conservativo, non un
limite inferiore.** La differenza è dichiarata in [ISS-145](ISSUES.md#iss-145).

**Validità, e va detta per intero.**

- La latenza è misurata **dall'annotazione**, non dall'inizio fisico della
  perdita di equilibrio. Se l'annotatore ha segnato l'inizio in ritardo, la
  latenza misurata è **sottostimata**. È il limite di questa misura, e non è
  eliminabile senza riannotare.
- È una latenza di **laboratorio**: cadute messe in scena, telecamera fissa,
  9 fps effettivi. Sulla board la frequenza è 7,3 fps, quindi la finestra dura
  3,0 s invece di 2,44 e la stessa mediana varrebbe circa **3,0 s**. È una
  proporzione, non una misura.
- Cinquanta cadute di dieci persone non sono cadute vere di persone anziane.

**Collegamenti:** [ISS-108](ISSUES.md#iss-108), [ISS-145](ISSUES.md#iss-145),
[EXP-017](#exp-017), [EXP-021](#exp-021), Capitolo 5 `tab:latenza`

---

<a id="exp-038"></a>
## EXP-038 — Le sei architetture su v5, e il risultato di EXP-025 che non regge

**Data:** 2026-09-09, 3h05 di calcolo · **Script:** `pipeline/addestra.py`
**Dati:** `feature_v5.csv` --- il primo dataset prodotto dal motore installato,
con `dt` misurato per fotogramma e integrali a durata
**Selezione:** quella che il DTW sceglie **su v5**, conservata in
`risultati/addestramento/scelte_usata_campagna_v5.txt`
**Configurazione:** LOSO a dieci fold, camera 1, modo `tre_classi`, finestra 22
a passo 2, soglia 0,50 dichiarata a priori
**Esito:** ✔ dodici run

### Il risultato

| architettura | DTW (12 col.) | DTWH (13 col.) | guadagno |
|---|---:|---:|---:|
| **GRU** | **0,857 ± 0,089** | 0,844 ± 0,082 | **−0,012** |
| CNN 1D | 0,838 ± 0,100 | 0,830 ± 0,093 | −0,008 |
| Transformer | 0,837 ± 0,082 | 0,840 ± 0,089 | +0,003 |
| LSTM | 0,829 ± 0,084 | **0,846 ± 0,081** | +0,017 |
| foresta | 0,825 ± 0,076 | 0,844 ± 0,071 | +0,020 |
| rete a grafo | 0,794 ± 0,087 | 0,790 ± 0,090 | −0,004 |

### Il risultato di EXP-025 non sopravvive

[EXP-025](#exp-025) concludeva: *«L'altezza dal pavimento migliora TUTTE e sei
le architetture»*, con guadagno medio +0,056 e l'argomento della **concordanza
dei segni** --- sei su sei, probabilita' $2^{-6} = 0{,}016$ sotto l'ipotesi che
la colonna non serva.

Su v5 i segni sono **tre positivi e tre negativi**, e il guadagno medio e'
**+0,003**. La concordanza era l'unico argomento statistico a sostegno di
`A3_h_pavimento`, perche' nessun guadagno preso da solo era distinguibile: **con
i segni discordi non resta niente.**

**La spiegazione e' la ridondanza, ed e' coerente.** La selezione di v5 fa
entrare `A2_testa_rel_y` e `A3_caviglie_rel_y`, che sono **altezze relative**:
portano gia' parte dell'informazione che `A3_h_pavimento` aggiungeva quando la
selezione ne era priva. Il guadagno misurato sulla sola foresta lo mostra su
tre gradini: **+0,059** (v3, selezione v3), **+0,040** (a parita' d'ordine),
**+0,020** (selezione v5).

`A3_h_pavimento` non e' inutile: **e' utile quando la selezione non contiene
altre altezze.** E' una proprieta' dell'insieme, non della grandezza, e va
scritta cosi'.

### La foresta, e il prezzo che le reti fanno pagare

A parita' di F2 le sei architetture non costano la stessa cosa a chi sta nella
stanza. Su DTWH la foresta pareggia la migliore delle reti e suona **meno della
meta' delle volte**:

| | foresta DTWH | LSTM DTWH |
|---|---:|---:|
| F2 | 0,844 | 0,846 |
| **falsi positivi** | **453** | 1.003 |
| **precisione** | **0,825** | 0,674 |
| dispersione fra i fold | **±0,071**, la piu' bassa delle dodici run | ±0,081 |
| parametri | 11.946 | 32.483 |
| addestramento | **10 s** | 942 s |

E' anche l'**unica** delle sei con precisione sopra 0,8: tutte le reti stanno
fra 0,585 e 0,674. L'F2 pesa il richiamo quattro volte la precisione, quindi
nasconde questa differenza --- ma un sistema domestico la paga per intero, e la
foresta e' cio' che e' **installato sulla board**.

### Il confronto fra architetture

Le prime cinque stanno in **0,032** su DTW (da 0,825 a 0,857) e in **0,016** su
DTWH, contro dispersioni fra soggetti di **±0,07 – ±0,10**. La conclusione di
[EXP-011](#exp-011) e [EXP-018](#exp-018) regge intatta: **non emerge evidenza
sufficiente per attribuire alla scelta dell'architettura un ruolo dominante.**

Due cose cambiano rispetto a v3, e vanno dette:

- **la rete a grafo recupera molto** --- da 0,699 a 0,794 su DTW --- e non e'
  piu' la sola che si avvicina a essere distinguibile in peggio. L'affermazione
  di EXP-018 va rivista;
- **le dispersioni scendono** (±0,07–0,10 contro ±0,09–0,14 su v3): sul dataset
  corretto le architetture sono piu' stabili fra soggetti.

### Il limite di questo confronto, e va dichiarato

**Fra EXP-025 e questa campagna sono cambiate DUE cose**, non una: il dataset
(v3 → v5) **e** la selezione (12 colonne di v3 → 12 di v5, due delle quali
diverse). Il confronto **interno** fra le sei architetture e' pulito, perche'
tutte hanno ricevuto le stesse colonne. Il confronto **fra le due campagne** no:
il miglioramento generale su DTW (sei architetture su sei, da +0,010 a +0,095)
non e' attribuibile a v5 in particolare.

Isolarlo richiederebbe una terza campagna, con v5 e la selezione di v3. **Non e'
stata fatta.**

**Collegamenti:** [EXP-025](#exp-025), [EXP-023](#exp-023), [EXP-011](#exp-011),
[EXP-018](#exp-018), [ISS-156](ISSUES.md#iss-156),
[ISS-159](ISSUES.md#iss-159), [DEC-109](DECISIONS.md#dec-109)

---

<a id="exp-037"></a>
## EXP-037 — I sei allarmi di agosto, riletti con il modello di oggi

**Data:** 2026-09-09 · **Script:** `deploy_board/rendi_clip.py` (nuovo)
**Dati:** le sei clip di `deploy_board/clip_demo/`, salvate ad agosto attorno
ad altrettanti allarmi del sistema di allora
**Configurazione:** pacchetto **DTW a 12 colonne** su `feature_v3_omnifall.csv`,
compito «evento», soglia 0,50, cadenza dichiarata 10 fps (quella con cui il
registratore le salvo')
**Esito:** ✔ · **Uscite:** `deploy_board/resa_clip_dtw12/` --- fotogrammi
annotati e un CSV per clip

**La domanda.** Quelle clip esistono **perche' il sistema di agosto ci aveva
suonato sopra**. Sono dati registrati e mai riguardati: che cosa direbbe di
quegli stessi istanti il sistema di adesso?

| clip | pose valide | picco | finestre ≥ 0,50 |
|---|---:|---:|---:|
| evt_0001_092019 | 34% | 0,240 | 0 |
| evt_0001_132012 | 100% | 0,160 | 0 |
| evt_0014_092236 | **6%** | 0,100 | 0 |
| evt_0038_094621 | 66% | 0,260 | 0 |
| evt_0068_142026 | 100% | **0,400** | 0 |
| evt_0188_182734 | 97% | 0,040 | 0 |

**Nessuno dei sei allarmi di agosto sarebbe emesso oggi.** Il punteggio piu'
alto e' 0,400, sotto la soglia dichiarata, e nessuna finestra di nessuna clip
la supera. Con la regola installata gli allarmi sono zero; anche abbassando a
0,30 con 3 su 5 ne resta **uno solo**.

**Che cosa contiene la clip piu' alta.** In `resa_clip_dtw12/evt_0068_142026/`
si vede una persona **distesa sul divano con il portatile**, gambe sollevate.
E' il negativo difficile del progetto --- sdraiarsi volontariamente --- ed e'
esattamente il caso che il passaggio al compito «evento» doveva togliere:
[EXP-015](#exp-015) misurava lo **0,0%** di allarmi sui distesi volontari
contro il 12,5% del compito «stato». **Qui lo stesso risultato si vede su un
allarme vero emesso in casa**, non su finestre di laboratorio.

**Il limite di questa lettura.** Delle sei clip non e' documentato quali
fossero falsi allarmi e quali cadute recitate: sono state scelte come
dimostrazione, non annotate. Se una delle sei fosse una caduta vera, questo
esperimento starebbe misurando un **falso negativo** e non un falso positivo
soppresso. Il caso guardato --- il divano --- e' inequivocabile; gli altri
cinque no. **La conclusione difendibile e' quindi asimmetrica:** il sistema di
oggi non emetterebbe quei sei allarmi, e almeno uno dei sei era certamente da
non emettere.

**Due clip hanno pose quasi assenti** --- 6% e 34% --- e su quelle il modello
non ha di che decidere: il punteggio basso non e' un giudizio, e' un'assenza di
dati.

**Collegamenti:** [EXP-015](#exp-015), [EXP-036](#exp-036),
[ISS-156](ISSUES.md#iss-156),
[DEC-016](../../DIP_PROJECT/docs/DECISIONS.md#dec-016)

---

<a id="exp-036"></a>
## EXP-036 — La regola installata misurata su tre cadute vere

**Data:** 2026-09-09, ~08:54 · **Dispositivo:** Radxa ROCK 4D
**Script:** `deploy_board/mostra_web.py` (nuovo), configurazione **DTWH a 13
colonne** installata lo stesso giorno
**Dati:** 12,5 minuti in salotto, 2.436 finestre decise, **tre cadute messe in
scena** dalla candidata
**Uscite:** `deploy_board/sessioni/20260909_diretta/` --- registro per finestra
(tracciato) e **2.539 fotogrammi annotati** (esclusi da git)
**Esito:** ✔

### Perche' questa sessione e' diversa da tutte le precedenti

**Ha la verita' di riferimento, e ha le immagini.** Le sessioni di settembre non
avevano nessuna immagine ([ISS-142](ISSUES.md#iss-142)), ed e' il motivo per
cui i quattordici eventi di [EXP-024](#exp-024) restano non verificabili. Qui
la candidata ha dichiarato i tre intervalli in cui era a terra, leggendoli sui
fotogrammi salvati:

| | a terra | durata |
|---|---|---:|
| caduta 1 | f00431 – f00467 | 36 s |
| caduta 2 | f00503 – f00529,3 | 26 s |
| caduta 3 | f00547,0 – f00566,5 | 20 s |

### Il risultato

| regola | allarmi | **cadute prese** | falsi |
|---|---:|---:|---:|
| **installata: soglia 0,50, 5 consecutive** | 0 | **0 su 3** | 0 |
| 0,50, 5 su 7 (isteresi) | 1 | 1 su 3 | 0 |
| 0,50, 2 consecutive | 1 | 1 su 3 | 0 |
| **0,40, 2 consecutive** | 2 | **2 su 3** | **0** |
| 0,30, 3 su 5 | 3 | 2 su 3 | **1** |
| 0,25, 3 su 5 | 4 | 2 su 3 | **2** |

**La configurazione installata non rileva nessuna delle tre cadute.** Il tetto
di qualunque regola provata e' **2 su 3**, e la terza non e' raggiungibile: il
suo punteggio massimo e' **0,200**.

### Le tre cadute sono tre casi diversi, e questo e' il valore della sessione

| | picco | finestre ≥ 0,50 | senza posa | esito |
|---|---:|---:|---:|---|
| caduta 1 | 0,540 | **1** | 11% | vista, una sola finestra sopra |
| caduta 2 | **0,200** | 0 | **1%** | **mancata dal classificatore** |
| caduta 3 | 0,720 | 5 | 0% | vista, ma le cinque non consecutive |

**Caduta 1 --- vista, ma per una finestra sola.** Il profilo attorno
all'istante dichiarato: 0,000 esatto finche' e' in piedi; tocca terra a
431,2; sale 0,16 → 0,32; **picco 0,540 a 435,4**; poi ridiscende a 0,10 in due
secondi mentre e' ancora a terra. **Nessuna regola con persistenza ≥ 2 avrebbe
suonato a soglia 0,50**, nemmeno l'isteresi.

**Caduta 2 --- il classificatore non l'ha vista, e non e' colpa del
tracciamento.** Punteggio massimo **0,200** su 84 finestre, con appena **l'1%
di finestre senza posa**: lo stimatore la seguiva. Nei fotogrammi
(`clip/f00508.4.jpg`) la persona e' distesa **lungo l'asse ottico**, con il
corpo che punta verso l'obiettivo: il tronco si proietta in un segmento corto e
il suo angolo quasi non cambia. E' la **compressione ottica** misurata in
[EXP-026](#exp-026) e la ragione per cui [DEC-101](DECISIONS.md#dec-101)
seleziona col criterio del minimo fra le viste --- qui su una caduta vera,
dentro l'inquadratura prescritta.

**Caduta 3 --- il caso che insegna di piu'.** Le finestre sopra soglia sono
**cinque**, esattamente quante la regola ne chiede: 548,8 · 549,1 · 549,4 ·
**550,4** · 550,7. Ma fra la terza e la quarta due finestre valgono **0,46**,
quattro centesimi sotto la soglia, e il contatore delle consecutive **si
azzera**. La raffica piu' lunga e' 3.

> **Una regola che conta consecutive e' fragile a un avvallamento di quattro
> centesimi.** E' precisamente cio' che [EXP-029](#exp-029) aveva concluso in
> laboratorio --- «l'isteresi dimezza i falsi allarmi e prende piu' cadute» ---
> qui su una caduta vera: `5 su 7` la prende, `5 consecutive` no, **sugli
> stessi identici punteggi**.

### Tre osservazioni che valgono per il testo

1. **Il picco arriva 4,2 s dopo il contatto col pavimento** (caduta 1). Non e'
   lentezza del dispositivo: ventidue campioni a 6,06 fps sono 3,6 s, e la
   caduta deve riempire la finestra prima che il punteggio salga. E' la
   scomposizione della latenza del Capitolo 5 osservata su un evento vero.

2. **Il punteggio scende mentre la persona resta a terra**, e resta basso per
   tutti i 36 secondi. **E' il comportamento voluto** --- il positivo e'
   `fall`, la transizione, non `fallen`
   ([DEC-016](../../DIP_PROJECT/docs/DECISIONS.md#dec-016)) --- e la sessione
   lo conferma in una casa. Ma ne discende che **se l'allarme non scatta nei
   due secondi del picco non scattera' piu'**: chi e' gia' a terra e'
   invisibile a questa via. E' il caso per cui DEC-016 prevedeva una **via
   lenta** (altezza dal pavimento + immobilita' + durata) che non e' mai stata
   costruita --- e la caduta 2 e' esattamente il caso che solo quella
   prenderebbe.

3. **La cyclette e' un falso positivo documentato.** L'unico allarme non
   corrispondente a una caduta, a soglia 0,30, cade a t = 224 s. In
   `clip/f00213.6.jpg` **la stanza e' vuota** e lo stimatore ha disegnato uno
   scheletro sulla bicicletta da camera: [ISS-136](ISSUES.md#iss-136), finora
   un'osservazione, ora con un fotogramma e un'ora sopra. **Abbassare la
   soglia per prendere le cadute la fa suonare.**

### Validita', e i suoi limiti

**Tre cadute in 12,5 minuti.** Zero falsi allarmi su dodici minuti non dice
quasi nulla su un'ora, e scegliere `0,40 con 2 consecutive` **perche' funziona
su questi eventi** sarebbe adattarsi a tre eventi. Cio' che il dato sostiene e'
l'affermazione negativa, che e' piu' solida: **la regola installata non prende
cadute che il suo stesso classificatore vede.**

L'osservazione sull'orientamento --- le due cadute lungo l'asse ottico fanno
0,540 e 0,200, quella di traverso 0,720 --- e' **un'osservazione su tre casi**,
non una misura. Va nella stessa direzione di EXP-026, e questo la rende
plausibile; non la rende dimostrata.

**La soglia 0,50 non e' stata scelta oggi:** e' dichiarata a priori dal
metadato ([EXP-010](#exp-010)). La sessione non mette in discussione la soglia
--- entrambe le cadute viste l'hanno superata --- ma la **persistenza**.

**Collegamenti:** [EXP-029](#exp-029), [EXP-026](#exp-026), [EXP-024](#exp-024),
[ISS-136](ISSUES.md#iss-136), [ISS-142](ISSUES.md#iss-142),
[ISS-139](ISSUES.md#iss-139), [EXP-035](#exp-035)

---

<a id="exp-035"></a>
## EXP-035 — DTWH sulla board: parita', cadenza misurata, prima sessione

**Data:** 2026-09-09 · **Dispositivo:** Radxa ROCK 4D, `192.168.1.20`
(trovata dalla sua chiave, non da un indirizzo ricordato)
**Pacchetto:** DTWH a 13 colonne da `feature_v3_omnifall.csv`, compito
«evento», motore a durata
**Esito:** ✔ · **Uscite:** `~/rileva/sess_20260909_prova{,_feature,_riepilogo}`
sul dispositivo; pacchetto precedente conservato in `~/rileva_prima_20260909`

### Le verifiche di avvio, sul dispositivo

| verifica | esito |
|---|---|
| impronta di `geometry.py` | coincide, `e4c0d354...` |
| **schema delle grandezze** (nuovo) | 33 grandezze, nomi e ordine coincidono |
| parita' sulle finestre | 200 confrontate, scarto **0,000e+00** |
| parita' per fotogramma | **divergono**, `A3_hip_vel` al 3,7% |

**La parita' sulle finestre vale piu' di quanto sembri:** il modello e' stato
serializzato con scikit-learn **1.6** e la board ne ha **1.9**, e le duecento
finestre danno scarto esattamente zero. E' il controllo che quella differenza
di versione esiste per intercettare, e l'ha superato.

**La parita' per fotogramma e' stata eseguita per la prima volta dal 22
agosto**, perche' fino a ieri la clip di riferimento nominata dal metadato non
esisteva ([ISS-153](ISSUES.md#iss-153)).

| grandezza | scarto medio | massimo | relativo |
|---|---:|---:|---:|
| A3_hip_vel | 0,0073 | 0,0444 | **3,7%** |
| A3_discesa | 0,0021 | 0,0113 | 3,6% |
| A3_ginocchia_rel_y | 0,0066 | 0,0873 | 3,6% |
| A1_discesa | 0,0017 | 0,0079 | 3,0% |
| A3_testa_vel_rel | 0,0156 | 0,1159 | 2,4% |
| A2_angolo_tronco | 0,1932 | 1,6452 | 1,8% |
| ... le altre sei | | | 0,4-1,3% |
| **A3_h_pavimento** | **0,0000** | **0,0000** | **0,0%** |

**La causa e' isolata, ed e' a monte della geometria.** Le pose sono concordi
**60 su 60** e MediaPipe e' 0.10.9 da entrambe le parti, ma i **landmark
grezzi** divergono: scarto medio 0,001211, massimo 0,081930. Il motore
geometrico e' lo stesso file, verificato per sha256. Cio' che differisce e'
l'**OpenCV**: 4.13.0 sul calcolatore, **5.0.0** sulla board --- decodifica
JPEG e ridimensionamento diversi, quindi pixel diversi in ingresso allo
stimatore. E' [ISS-106](ISSUES.md#iss-106) con l'attribuzione piu' precisa
ottenuta finora.

`A3_h_pavimento` vale **zero esatto da entrambe le parti**: in sessanta
fotogrammi la retta del pavimento non si stima, e la colonna resta inerte. E'
la conferma che il presidio aggiunto oggi --- non decidere finche' la stima
non c'e' --- interviene esattamente dove serve.

### La prima sessione con la configurazione nuova

Due minuti sulla telecamera, 615 fotogrammi, 60,8% di pose valide.

| | dichiarato | **misurato** |
|---|---:|---:|
| cadenza data al motore | 9,0 | **6,469** |
| finestra degli integrali | 31 campioni | **1,722 s = 11,1 campioni** |

**E' il difetto di [ISS-148](ISSUES.md#iss-148) misurato mentre viene
corretto.** Prima di oggi il motore riceveva 9,0 fps mentre la board ne faceva
6,47: le derivate uscivano **sopravvalutate del 39%**, e i trentuno fotogrammi
del buffer coprivano **4,79 s** invece dei 1,72 su cui il modello e'
addestrato --- un fattore **2,8**.

**Il presidio del pavimento diceva «0 finestre non decise su 297», e quel
numero NON VALE NULLA:** il presidio non ha bloccato niente perche' era
scritto male ([ISS-155](ISSUES.md#iss-155)). `pavimento_pronto()` restituisce
la coppia `(pronto, n_osservazioni)`, e una tupla non vuota e' sempre vera:
`not motore.pavimento_pronto()` non poteva essere vero nemmeno a pavimento
ignoto. La sessione ha quindi deciso su tutte e 297 le finestre, comprese
quelle in cui `A3_h_pavimento` valeva 0,0 per assenza di stima.

**Corretto e rimisurato lo stesso giorno** col visore in diretta: a presidio
funzionante, **14 finestre** sono state effettivamente scartate prima che la
retta fosse disponibile, e poi la stima e' arrivata (95 osservazioni di
persona eretta). Il numero giusto e' quattordici, non zero.

**Costo per fotogramma:** 179,09 ms in tutto --- percezione 159,05 (88,8%),
classificatore 18,91 (10,6%). Piu' alto dei 136,65 ms di
[EXP-024](#exp-024), e la ragione e' dichiarata dal Capitolo 5: quella
sessione aveva il 35% di pose, questa il 60,8%, e lo stimatore costa di piu'
quando c'e' qualcuno.

**Tre interruzioni della telecamera in due minuti**, ciascuna recuperata in 3
s. `dmesg` le spiega: il dispositivo USB e' stato **collegato a sessione in
corso** (t = 797 s dall'avvio), quindi erano l'enumerazione. Nessun errore USB,
48-51 °C, carico 0,54.

**Nessun allarme**, punteggio massimo 0,320.

**Che cosa questa sessione NON dice.** Nessuna caduta e' stata messa in scena:
e' una prova di installazione, non di rilevamento. Il recall a bordo della
configurazione a tredici colonne **non e' stato misurato**.

**Collegamenti:** [ISS-148](ISSUES.md#iss-148), [ISS-139](ISSUES.md#iss-139),
[ISS-153](ISSUES.md#iss-153), [ISS-106](ISSUES.md#iss-106),
[EXP-024](#exp-024), [EXP-016](#exp-016)

---

<a id="exp-034"></a>
## EXP-034 — L'allineamento OmniFall con i timestamp veri

**Data:** 2026-09-09 · **Script:** `pipeline/mappa_omnifall.py --csv feature_v3.csv`
**Dati:** `feature_v3.csv`, 116.362 fotogrammi, 220 riprese; annotazioni
OmniFall `up_fall.csv`, 2.426 segmenti
**Esito:** ✔ · **Uscita:** `dataset/processed/features/feature_v3_omnifall.csv`

**Domanda.** [ISS-150](ISSUES.md#iss-150): OmniFall annota in secondi, e la
conversione in fotogrammi moltiplicava per 18 fps. La cadenza vera va da 14,43
a 19,63, quindi l'errore **cresce lungo la ripresa**. Correggerlo con i
timestamp veri --- che stanno nei nomi dei file, al microsecondo --- migliora
l'accordo con le nostre etichette manuali, oppure no?

**Copertura della correzione:** **220 riprese su 220**, 116.362 righe, il 100%.
Nessuna ripresa e' rimasta col ripiego.

**Di quanto si sposta l'etichetta:**

| | |
|---|---:|
| spostamento mediano | **0,398 s** |
| spostamento massimo | **11,890 s** |
| righe spostate di oltre 1 s | 25.888 (**22,2%**) |
| righe spostate di oltre 3,11 s, la durata mediana di una caduta | 6.523 |
| fotogrammi che **cambiano classe** OmniFall | 2.727 su 116.362 (**2,3%**) |

**L'accordo con le etichette manuali, prima e dopo:**

| conversione | coperti | nostra 1 → `fall` | nostra 2 → `fallen` | `fall` → nostra 1 |
|---|---:|---:|---:|---:|
| 18 fps fissi | 97,3% | 67,4% | 81,5% | 91,1% |
| **timestamp veri** | **98,5%** | 67,2% | **85,1%** | 90,6% |

**Il risultato e' parziale, e va riportato come tale.** La copertura sale di
1,2 punti e l'accordo sullo stato «a terra» sale di **3,6 punti**, che e' il
guadagno piu' netto. L'accordo sulla **transizione** non si muove --- 67,4%
contro 67,2% --- e il verso opposto cala di mezzo punto. La correzione e'
giusta perche' usa il dato invece di una costante falsa, non perche' produca
un salto nelle metriche.

**E dice anche un'altra cosa.** Che l'accordo sulla transizione resti al 67%
con i tempi giusti significa che **il disaccordo fra le nostre etichette e
OmniFall non era di allineamento**: un terzo dei fotogrammi che abbiamo
annotato come caduta OmniFall non li chiama `fall` nemmeno adesso. E' una
differenza di definizione dell'evento, e con il tempo sistemato non ha piu'
scuse temporali.

**Validita'.** Il confronto e' fra due conversioni della **stessa** annotazione
sullo **stesso** CSV: cambia una colonna di tempi e nient'altro.

**Collegamenti:** [ISS-150](ISSUES.md#iss-150), [ISS-149](ISSUES.md#iss-149),
[ISS-154](ISSUES.md#iss-154)

---

<a id="exp-033"></a>
## EXP-033 — La riestrazione con il $\Delta t$ vero, e perche' non cambia il risultato

**Data:** 2026-09-08 · **Script:** `pipeline/estrai_feature.py` (corretto),
`pipeline/analisi_dtw.py`, `pipeline/addestra.py`
**Dati:** UP-Fall, 220 riprese, 116.362 fotogrammi -> `feature_v4.csv`
**Durata:** 102 minuti di estrazione, 12 secondi di addestramento per configurazione
**Esito:** ✔ eseguito, ✗ **nessun miglioramento misurabile**

**Perche'.** [ISS-149](ISSUES.md#iss-149): `FPS_DATASET = 18,0` era
un'assunzione mai verificata, e la cadenza vera va da 14,43 a 19,63 fps con lo
scarto concentrato sul soggetto 6. Le derivate si dividono per quel valore.

**Che cosa e' stato cambiato.** Una cosa sola: `estrai_feature.py` ricava
l'intervallo vero fra ciascun fotogramma e il precedente dai timestamp nei nomi
dei file, e passa `1/dt` al motore geometrico invece della costante. Non e'
stata usata una media per ripresa ma il **dt per fotogramma**, perche' la
cadenza salta anche dentro la stessa ripresa --- mediana 49,6 ms, nono decile
70,2 ms, 99mo percentile 159,8 ms --- e una media trasformerebbe ogni buco di
cattura in un picco di velocita' mai avvenuto.

### Che cosa e' cambiato nel dataset

Struttura identica a v3: stesse 116.362 righe, stesse 40 colonne, 95,9% di pose
valide, **etichette identiche fotogramma per fotogramma** (5.542 «caduta in
corso», 10.524 «a terra»).

| gruppo di colonne | cambiate |
|---|---|
| le 11 derivate | **si', nel 96% delle righe** |
| le 9 integrali | no, identiche bit per bit |
| statiche, altezza dal pavimento, etichette | no |

E' esattamente cio' che doveva succedere: le integrali non si dividono per
`dt`, quindi la correzione non poteva toccarle.

**L'artefatto per soggetto e' sparito.** Ampiezza mediana della derivata di
ogni soggetto, rapportata a quella di tutti: il soggetto 6 passa da **1,110 a
0,910** (--18%), mentre gli altri si spostano dello 0,5--4% e il soggetto 10
resta a 1,87. La correzione ha tolto l'errore senza appiattire le differenze
vere fra persone, che era il rischio.

### La selezione DTW non cambia

Rifatta su v4, sceglie **le stesse 12 grandezze** di v3. Cambia solo l'ordine
fra l'ottava e la nona (`A3_hip_vel` e `A3_percorso`). E' un risultato di
robustezza: la preselezione non dipende dal difetto.

### Il risultato, e non e' quello atteso

Foresta, tre classi, DTW, camera 1, L=22, **stesso codice eseguito lo stesso
giorno sui due CSV**:

| fold | v3 | v4 | delta |
|---|---:|---:|---:|
| Subject_01 | 0,813 | 0,786 | $-0{,}027$ |
| Subject_02 | 0,726 | 0,708 | $-0{,}018$ |
| Subject_03 | 0,646 | 0,647 | $+0{,}001$ |
| Subject_04 | 0,897 | 0,897 | 0 |
| Subject_05 | 0,669 | 0,643 | $-0{,}026$ |
| **Subject_06** | **0,883** | **0,863** | $\mathbf{-0{,}020}$ |
| Subject_07 | 0,882 | 0,882 | 0 |
| Subject_08 | 0,840 | 0,843 | $+0{,}003$ |
| Subject_09 | 0,962 | 0,960 | $-0{,}002$ |
| Subject_10 | 0,874 | 0,902 | $+0{,}028$ |
| **media** | **0,819 ± 0,105** | **0,813 ± 0,112** | $-0{,}006$ |

**Confronto appaiato:** differenza media $-0{,}0061$, errore standard
$0{,}0053$, **t = $-1{,}15$** contro un valore critico di 2,262.
**Non distinguibile dal caso**, e vale il 6% della dispersione fra soggetti.

**E il fold che la correzione doveva aiutare peggiora.** Subject_06, quello a
14,43 fps le cui derivate erano gonfiate del 25%, passa da 0,883 a 0,863. E'
l'esito opposto all'ipotesi, e va riportato per intero.

### Perche' non poteva cambiare molto, ed e' la spiegazione piu' interessante

Delle **12 colonne selezionate, otto sono integrali** --- che la correzione non
tocca --- **due sono statiche**, e solo **due sono derivate** (`A3_hip_vel`,
ottava, e `A3_testa_vel_rel`, dodicesima), entrambe in fondo alla classifica.

La selezione DTW aveva gia', per conto proprio, scartato quasi tutte le
grandezze affette dal difetto. **La pipeline era gia' isolata dal problema, e
non perche' qualcuno lo avesse previsto.** E' anche la ragione per cui il
difetto era sopravvissuto: non produceva sintomi.

### Che cosa se ne ricava

Il difetto e' reale, la correzione e' giusta, e l'effetto sui numeri di
laboratorio e' **sotto la risoluzione del lavoro**. Dove la correzione conta
davvero e' sul dispositivo ([ISS-148](ISSUES.md#iss-148)), dove la cadenza
e' 7,26 fps invece dei 9 assunti e varia molto piu' che in laboratorio.

**Collegamenti:** [ISS-149](ISSUES.md#iss-149), [ISS-148](ISSUES.md#iss-148),
[EXP-022](#exp-022), Capitolo 3

---

<a id="exp-032"></a>
## EXP-032 — La sessione del 6 settembre riclassificata con la finestratura dell'addestramento

**Data:** 2026-09-08 · **Natura:** RICLASSIFICAZIONE fuori linea --- nessun
addestramento, nessuna nuova sessione: stessa traccia, stesso modello, due
regole di finestratura
**Dati:** `notte_20260906_1523_feature.csv`, 120.051 fotogrammi, 4,59 ore,
35,1% di pose valide
**Modello:** `deploy_board/modello.pkl` + `scaler.pkl`, quelli installati
**Esito:** ✔

**Perche'.** [ISS-147](ISSUES.md#iss-147) dice che la board decide su finestre
che l'addestramento non contiene. Restava da sapere se la cosa sposti un
numero o no.

**La verifica che autorizza il confronto.** Prima di ogni cosa, parita' su
`parita.npz`: **scarto massimo 0** su 200 finestre. E la ricostruzione della
regola attuale **riproduce la board esattamente**: 168 finestre sopra soglia e
14 allarmi, identici al `riepilogo.json` di quella sera. Senza questi due
controlli i numeri sotto non varrebbero niente --- e il primo tentativo era
infatti sbagliato, perche' applicava lo scaler a `parita.npz`, che contiene
finestre **gia' normalizzate**: scarto 0,94 invece di 0. La verifica ha fatto
il proprio lavoro.

**Le due regole.**

*A, com'e' oggi:* ogni fotogramma entra nel buffer, anche quello senza posa,
che vale zeri su tutte le colonne; la guardia del riscaldamento e' un tempo
dall'avvio e non viene riarmata.

*B, come `src/dati.py`:* il fotogramma senza posa non entra e azzera il
buffer; non si decide finche' non ci sono di nuovo $K = 31$ fotogrammi validi
consecutivi.

| | decisioni | sopra soglia | allarmi | eventi/ora |
|---|---:|---:|---:|---:|
| **A** --- la board | 60.015 | 168 (36,6/ora) | **14** | **3,05** |
| **B** --- corretta | 13.639 | 51 (11,1/ora) | **4** | **0,87** |

**Dieci allarmi su quattordici erano il difetto.** Il tasso scende di 3,5
volte. La mediana del punteggio sale da 0,0000 a 0,0400 --- coerente: sotto A
piu' di meta' delle decisioni sono prese su finestre interamente di zeri, che
il modello mappa su un punteggio nullo e che gonfiano il denominatore senza
dire niente.

**Che cosa questo NON misura, ed e' la meta' che conta di piu'.** La sessione
non contiene cadute: si misura il lato dei falsi allarmi e non quello del
richiamo. Le cinque cadute stanno nella sessione del 13 agosto, che ha i
punteggi ma **non** la traccia per fotogramma, e da un punteggio non si
ricostruisce una finestra. Correggere il difetto puo' costare richiamo, e con
i dati in archivio non si puo' sapere quanto. Per saperlo serve **una sessione
nuova con `--feature` acceso e cadute messe in scena**, che e' anche
l'intervento gia' in cima al lavoro aperto per un'altra ragione.

**Collegamenti:** [ISS-147](ISSUES.md#iss-147), [EXP-031](#exp-031),
[EXP-024](#exp-024), Capitolo 5

---

<a id="exp-031"></a>
## EXP-031 — Due conteggi sulle finestre: il confine dell'etichetta, e che cosa vede davvero la board

**Data:** 2026-09-08 · **Natura:** CONTEGGIO — nessun addestramento, nessuna
misura nuova: si contano finestre su dati gia' in archivio
**Esito:** ✔

Due domande diverse, la stessa unita' di misura. Entrambe nascono dal
confronto con un prototipo pubblico che adotta due pratiche che questo lavoro
non aveva: escludere i fotogrammi ambigui invece di indovinarli, e dichiarare
lo scarto fra le finestre di addestramento e quelle di esercizio.

### Primo conteggio: quanto vale il confine dell'etichetta

**Dati:** `feature_v3.csv`, telecamera 1, dieci soggetti, 25.130 finestre.

Una finestra che contiene fotogrammi di caduta o di persona a terra ma non
abbastanza da superare il criterio $K$-su-$M$ vale oggi **0**, cioe' un
negativo pulito. E' un'ipotesi sul confine, e cade sulla classe che deve
restare pulita. L'alternativa --- escluderla --- e' stata implementata
(`config.ESCLUDI_FINESTRE_INCERTE`, predefinito **spento**) e misurata.

| modo | escluse | negative | caduta | a terra | cambiano |
|---|---:|---:|---:|---:|---:|
| `tre_classi`, oggi | 0 | 21.610 | 1.262 | 2.258 | --- |
| `tre_classi`, con esclusione | **39** | 21.571 | 1.262 | 2.258 | **39 (0,16%)** |

**Trentanove finestre su 25.130**, tutte dalla classe negativa a quella
esclusa, e **nessuna finestra positiva cambia**. E' lo 0,18% della sola classe
negativa, e sta sotto la risoluzione di qualunque confronto del lavoro, dove
la dispersione fra soggetti vale $\pm 0{,}06$--$0{,}08$ di $F_2$. La pratica e'
giusta e non sposta niente: l'opzione resta spenta perche' accenderla senza
riaddestrare renderebbe il codice non riproducibile dai numeri stampati.
Scritto nel Capitolo 3, sezione sull'assegnazione dell'etichetta di finestra.

### Secondo conteggio: che cosa vede la board

**Dati:** `notte_20260906_1523_feature.csv`, 120.051 fotogrammi, 4,59 ore,
35,1% di pose valide. Finestre ricostruite con L=22 e passo 2, cioe' gli
stessi di `deploy_board/metadata.json`.

| | finestre | quota |
|---|---:|---:|
| totali | 60.015 | |
| tutte con posa, come in addestramento | 14.780 | **24,6%** |
| con almeno un fotogramma a zero | 45.235 | **75,4%** |
| con integrali non riscaldati | 46.376 | **77,3%** |

E' [ISS-147](ISSUES.md#iss-147), ed e' il conteggio piu' scomodo di questa
giornata: **tre decisioni su quattro sono prese su un ingresso che la
distribuzione di addestramento non contiene.**

**Collegamenti:** [ISS-147](ISSUES.md#iss-147), [ISS-106](ISSUES.md#iss-106),
[EXP-024](#exp-024), Capitolo 3 e Capitolo 5 `sec:parita`

---

<a id="exp-030"></a>
## EXP-030 — La scomposizione della latenza, rifatta sul costo per fotogramma misurato

**Data:** 2026-09-08 · **Script:** `pipeline/latenza.py` (corretto)
**Dati:** sessione `bloccocadute_sola_20260813_091641`, 8.411 finestre, cinque
cadute annotate al minuto
**Natura:** RICALCOLO — nessun addestramento, nessuna misura nuova sulla board:
cambia un solo addendo della somma
**Esito:** ✔ · **Uscita:** `risultati/campo/latenza.json`

**Perché.** [ISS-146](ISSUES.md#iss-146): l'addendo «calcolo per fotogramma»
valeva ancora 37,7 ms, il numero che [ISS-137](ISSUES.md#iss-137) aveva
ritirato il 6 settembre. La board misurata ne fa 136,65
([EXP-024](#exp-024)).

**Come.** La costante è stata sostituita da **1/fps della sessione**. Sulla
board il ciclo è seriale --- cattura, percezione, geometria, classificazione,
in fila --- quindi la cadenza fra due fotogrammi è il costo di un fotogramma.
La verifica che autorizza la sostituzione è nel riepilogo del 6 settembre:
136,65 ms sommando le quattro fasi strumentate contro 137,65 ms di cadenza
(1 / 7,2647 fps), **uno scarto dello 0,7%**. Ricavarlo dalla sessione evita
inoltre di sommare l'fps di una sessione con i millisecondi di un'altra.

**Risultato.**

| addendo | prima | dopo | quota |
|---|---:|---:|---:|
| calcolo per fotogramma | 0,038 s | **0,125 s** | 3,2% |
| riempimento della finestra (22 campioni a 8,02 fps) | 2,743 s | 2,743 s | 71,0% |
| persistenza (5 finestre, una ogni 0,249 s) | 0,997 s | 0,997 s | 25,8% |
| **totale, caso conservativo** | **3,778 s** | **3,865 s** | |

**Che cosa regge.** L'affermazione del capitolo --- *la latenza è dominata
dalla finestra di decisione, non dall'hardware* --- resta vera, ed è l'unica
cosa che il capitolo le fa sostenere. La finestra vale ancora ventidue volte
il calcolo.

**Che cosa non regge.** Il **fattore settantatré**, che era l'ordine di
grandezza citato accanto all'affermazione. È ventidue. E il corollario
pratico: comprare un dispositivo dieci volte più veloce toglieva l'1% della
latenza totale, ne toglie il **3%** --- resta trascurabile, ma tre volte meno
trascurabile.

**Il confronto con la misura empirica non cambia di segno.** La mediana
misurata in laboratorio a persistenza cinque è 2,44 s
([EXP-028](#exp-028)), cioè 2,74 s riportata agli 8,02 fps di questa sessione:
resta **circa un secondo sotto** il caso conservativo, che è il punto di
[ISS-145](ISSUES.md#iss-145) e non dipende da questo addendo.

**Collegamenti:** [ISS-146](ISSUES.md#iss-146), [ISS-137](ISSUES.md#iss-137),
[ISS-145](ISSUES.md#iss-145), [EXP-024](#exp-024), [EXP-028](#exp-028),
Capitolo 5 `tab:latenza`

---

<a id="exp-029"></a>
## EXP-029 — Ventuno regole di allarme a confronto: quella installata è la peggiore delle quattro famiglie

**Data:** 2026-09-07 · **Script:** `pipeline/regole_allarme.py` (nuovo)
**Natura:** RILETTURA — nessun modello riaddestrato, cambia solo l'aritmetica
che trasforma i punteggi in un allarme
**Dati:** i punteggi già salvati della LOSO (50 cadute annotate, dieci
soggetti) **e** i punteggi delle nove sessioni domestiche (14,98 ore, nessuna
caduta messa in scena)
**Esito:** ✔ · **Uscita:**
`risultati/laboratorio/regole_allarme_foresta_tre_classi_DTW_cam1_L22.json` e
la stessa per DTWH

**Perché.** La regola installata chiede **cinque finestre consecutive** sopra
soglia. Il valore cinque non era giustificato ([ISS-145](ISSUES.md#iss-145)),
ma il difetto più serio non è il valore: **è la parola «consecutive»**. Il
Capitolo 5 lo documentava senza trarne la conseguenza:

> *«Le altre tre cadute non producono allarme a persistenza cinque, con corse
> massime di due, zero e tre finestre.»*

Su tre cadute vere il punteggio era sopra soglia a tratti, ma con dei buchi: la
corsa si azzerava e ripartiva. **Una regola che chiede consecutività butta via
l'evidenza già accumulata ogni volta che un fotogramma va storto** — e i
fotogrammi vanno storti proprio nelle cadute difficili, dove la persona esce dal
campo o si copre.

### Le quattro famiglie

Tutte leggono gli stessi punteggi, tutte sono causali, tutte girerebbero sul
dispositivo così come sono scritte.

| famiglia | regola | costo |
|---|---|---|
| **consecutive k** *(installata)* | k finestre di fila sopra soglia | un contatore |
| **m su n** | m finestre sopra soglia fra le ultime n, anche non contigue | una coda di n booleani |
| **cumulata c** | si accumula (punteggio − soglia), il negativo scarica ma non azzera; allarme sopra c | un numero. È una regola CUSUM: pesa **quanto** si è sopra, non solo quante volte |
| **isteresi a/b/k** | si entra con una soglia alta, si resta con una bassa | due soglie e un contatore |

### Le due misure, che tirano in direzioni opposte

**Laboratorio:** quante delle cinquanta cadute annotate fa scattare, e dopo
quanto. **Casa:** quanti allarmi produce all'ora nelle nove sessioni domestiche,
dove non ci sono cadute e quindi sono **tutti falsi**.

Una regola è migliore se, **a parità di allarmi in casa, prende più cadute o le
prende prima**. Il confronto è su una frontiera, non su un numero.

### Il risultato, sulla configurazione installata sulla board

| regola | richiamo | latenza mediana | allarmi/ora in casa |
|---|---:|---:|---:|
| consecutive 1 | 0,98 | 1,44 s | 15,8 |
| **consecutive 5** *(installata)* | **0,88** | **2,47 s** | **10,8** |
| 3 su 6 | 0,96 | 1,97 s | 12,4 |
| 6 su 10 | 0,88 | 2,69 s | 10,7 |
| **cumulata 0,5** | **0,98** | **1,61 s** | 9,3 |
| cumulata 1,0 | 0,96 | 1,89 s | 8,5 |
| isteresi 0,70/0,40/3 | 0,96 | 1,97 s | 7,7 |
| **isteresi 0,80/0,45/3** | **0,96** | **2,00 s** | **5,1** |
| isteresi 0,90/0,50/3 | 0,84 | 1,94 s | 3,0 |

**Undici regole su venti battono quella installata su entrambi gli assi.** Due
la battono su tutti e tre:

- **cumulata 0,5** — prende **49 cadute su 50** invece di 44, è **0,9 s più
  veloce**, e fa **il 14% di falsi allarmi in meno**;
- **isteresi 0,80/0,45/3** — prende 48 su 50, è 0,5 s più veloce, e **dimezza i
  falsi allarmi**: da 10,8 a 5,1 all'ora, cioè **−53%**.

Sulla configurazione con l'altezza dal pavimento (DTWH) il quadro è identico,
con i valori assoluti migliori.

### Il risultato è strutturale, non un parametro fortunato

È il punto che conta, perché rende la conclusione difendibile:
**tutte e cinque le varianti della cumulata e tre delle quattro dell'isteresi
battono la regola installata.** Non è una combinazione trovata a furia di
provare: è che **la famiglia sbagliata è quella consecutiva**.

La ragione è la stessa che il Capitolo 5 aveva osservato senza usarla: la
consecutività **azzera la memoria** a ogni fotogramma storto. La cumulata la
scarica gradualmente; l'isteresi la conserva finché il punteggio non crolla
davvero. Entrambe sopravvivono al buco isolato, che è ciò che distingue una
caduta difficile da un falso allarme.

### Che cosa questo non dimostra

- **Le regole sono state confrontate sugli stessi dati su cui vengono
  giudicate.** Ho provato ventuno regole e riportato le migliori: parte del
  vantaggio può essere adattamento a questi dati. L'attenuante è che i due assi
  vengono da **archivi diversi** — le cadute da UP-Fall, i falsi allarmi dalle
  sessioni domestiche — quindi una regola che vince su entrambi non sta
  adattandosi a un solo insieme. Ma i parametri (0,80/0,45/3) sono stati scelti
  guardando questi risultati, e **la conclusione robusta è la famiglia, non il
  parametro**.
- **In casa non ci sono cadute annotate al secondo**, quindi il richiamo è
  misurato in laboratorio e i falsi allarmi in casa. Le due metà vengono da due
  mondi.
- Nessuna di queste regole è stata provata **sul dispositivo**: la verifica di
  parità andrebbe rifatta, perché cambia il codice che decide.

**Collegamenti:** [ISS-145](ISSUES.md#iss-145), [EXP-028](#exp-028),
[EXP-010](#exp-010), Capitolo 5 `tab:tolleranza`

---

<a id="exp-039"></a>
## EXP-039 — Prima sessione di campo con la selezione v5

**Data:** 2026-09-09, sera · **Script:** `deploy_board/mostra_web.py --durata 900 --immagini clip_20260909_v5 --registro sess_20260909_v5.csv`
**Dispositivo:** Radxa ROCK 4D, `192.168.1.20` · **Durata:** 15 minuti pieni

Pacchetto v5/DTWH esportato la sera stessa da `feature_v5_omnifall.csv`, 50
alberi, 7.322 nodi. Rispetto a quello della mattina cambiano **due grandezze su
tredici** (`A2_angolo_tronco` -> `A2_testa_rel_y`, `A3_ginocchia_rel_y` ->
`A3_caviglie_rel_y`); **il motore geometrico e' lo stesso**, impronta
`e4c0d354...`.

**Verifiche di avvio:** geometria e schema coincidono; parita' sulle **finestre**
`0,000e+00` --- modello e scaler si trasferiscono esatti nonostante
scikit-learn 1.6.0 -> 1.9.0; parita' per fotogramma **3,70%** su `A3_hip_vel`,
che e' [ISS-106](ISSUES.md#iss-106) misurata e non un guasto (vedi
[ISS-161](ISSUES.md#iss-161)).

### Risultato

**6.703 fotogrammi, 2 allarmi, 2.254 immagini annotate.**

| | |
|---|---|
| finestre **decise** | **624**, da 697,4 s a 900,0 s |
| finestre scartate per pavimento | **2.717** |
| con posa | 98,7% |
| sopra soglia 0,50 | 36 |

### La verita' di riferimento, dichiarata sui fotogrammi

Le cadute messe in scena sono **quattro**, dichiarate dalla candidata guardando
le immagini annotate. Il confronto con il registro:

| # | istante | il classificatore la vede? | l'allarme suona? | perche' |
|---|---|---|---|---|
| 1 | 742--746 s | **si**, picco 0,960, 13 finestre | **si**, allarme 1 | |
| 2 | 748--751 s | **si**, picco 0,800, 9 finestre | **no** | caduta sei secondi dopo la prima: **soppressa dai 30 s di sospensione** |
| 3 | 803--807 s | **no**, picco 0,520, **una** finestra sopra soglia | no | discesa lenta: nei fotogrammi la persona si accovaccia e rotola |
| 4 | 855--857 s | **si**, picco 0,800, 7 finestre | **si**, allarme 2 | alle 850,0 s la persona e' in piedi con punteggio 0,000: e' un evento distinto dal n. 3 |

> **Il classificatore vede 3 cadute su 4. La regola ne segnala 2 su 4.**
> **Una caduta su quattro e' persa dalla REGOLA, non dal modello.**

E' la distinzione che conta: su questa sessione il margine piu' grande non sta
nel classificatore ma nella logica di decisione ([ISS-162](ISSUES.md#iss-162)).

### Il falso positivo, ed e' quello che pesa

La raffica delle **881,6 s** --- 4 finestre, picco **0,660** --- **non e' una
caduta**: nel fotogramma `f00881.8.jpg` la persona e' **seduta sul divano con il
telefono**. La regola delle cinque finestre non ha suonato, e ha fatto bene.

**Il pacchetto installato e' DTWH, cioe' quello CON `A3_h_pavimento`** --- la
grandezza reintrodotta apposta per distinguere chi e' a terra da chi sta su una
superficie rialzata. Su un divano vero da 0,660. Lo stesso giorno in cui
[EXP-038](#exp-038) mostra che su v5 il suo vantaggio medio e' +0,003 con tre
segni positivi e tre negativi.

**Ne segue una correzione a un'analisi fatta prima di guardare i fotogrammi.**
Rivalutando il registro, abbassare la persistenza da 5 a 4 finestre sembrava
recuperare un evento. **E' falso:** la raffica da 4 finestre e' il divano.
Abbassare la regola non recupera la caduta n. 3 --- che ha **una sola** finestra
sopra soglia, e nessuna persistenza ragionevole la prende --- ma **aggiunge un
falso allarme**. La prescrizione del relatore di non toccare la regola guardando
questi dati e' confermata dai dati stessi.

### Che cosa dice

**1. Il sistema ha deciso per 203 secondi su 900.** Le prime 624 finestre utili
cominciano a **697,4 s**: per undici minuti e mezzo non ha deciso nulla, in
attesa che il piano del pavimento fosse stimato. E'
[ISS-156](ISSUES.md#iss-156) osservata dal vivo, e in una prova a tempo si
mangia i tre quarti della sessione.

**2. La sospensione di 30 secondi si e' mangiata una caduta vera.** Le cadute
1 e 2 distano **sei secondi**. La seconda e' stata vista benissimo --- nove
finestre, picco 0,800 --- e non ha prodotto allarme perche' il sistema aveva
appena suonato. E' lo scenario domestico che conta di piu': una persona cade,
prova a rialzarsi, ricade. Vedi [ISS-162](ISSUES.md#iss-162).

**3. Il confronto con la mattina NON e' pulito.** Mattina: picchi 0,540 /
0,200 / 0,720, zero allarmi su tre cadute. Sera: 0,960 / 0,800 / 0,800 / 0,660,
due allarmi. Ma la mattina il **26,7%** delle finestre era senza posa e la sera
il **98,7%** ce l'ha: parte del guadagno e' v5 e parte e' l'inquadratura. Per
separarli vanno rigirate le clip della mattina col pacchetto v5
(`deploy_board/rendi_clip.py`). **Finche' non e' fatto, il confronto e'
indicativo e non va citato come misura.**

**Artefatti:** `deploy_board/sessioni/20260909_v5/` --- `LEGGIMI.md`,
`sess_20260909_v5.csv` (624 righe, tracciato), `sess_20260909_v5.log`,
`clip/` (2.254 immagini, **escluse da git**).

**Difetto trovato:** la colonna `allarme` del registro e' `0` su tutte e 624 le
righe, mentre il log stampa i due allarmi. Chi ricalcolasse gli eventi dal CSV
ne conterebbe zero.

---

<a id="exp-045"></a>
## EXP-045 — La scelta di K rifatta dentro il fold: il leakage va nella direzione opposta

**Data:** 2026-09-22 · **Script:** `pipeline/estrai_k_multiplo.py` poi
`pipeline/k_per_fold.py`
**Dati:** camera 1, dieci soggetti, 110 riprese, 58.359 fotogrammi, estratti a
K = 5, 15, 22, 31, 45 in una sola passata di stima di posa
**Configurazione:** foresta casuale, tre classi, dodici colonne DTW, finestra
22 a passo 2, soglia 0,50 dichiarata a priori
**Esito:** ✅ · **Uscita:** `risultati/dtw/k_per_fold.json`,
`risultati/dtw/log_k_per_fold.txt`

### Perche'

`K_INTEGRALI = 31` non e' fissato a priori ([ISS-178](ISSUES.md#iss-178)):
viene da una scansione che ha confrontato prestazioni sui fold di prova. Il
relatore chiede che ogni operazione che impara dai dati sia calcolata dentro il
fold. Questa e' la misura di quanto la violazione pesi, ed e' l'analogo di
[EXP-044](#exp-044) per la selezione delle grandezze.

### Il protocollo annidato

Per ciascun soggetto `s`: lo si mette da parte; si sceglie K con un LOSO
**interno sui soli nove rimasti**; si valuta su `s` con quel K e con K=31, una
volta sola. Circa 470 addestramenti.

### Due controlli prima della misura

1. **K tocca solo le nove grandezze integrali.** L'estrazione alimenta cinque
   motori geometrici con gli stessi landmark e confronta fotogramma per
   fotogramma le altre ventiquattro colonne: **nessuna divergenza** su 58.359
   fotogrammi.
2. **A K=31 riproduce `feature_v5.csv`**: scarto **0,000e+00** su tutte e dodici
   le colonne adottate. Senza questo il confronto non significherebbe nulla.

Da segnalare anche un controllo non cercato: la retta del pavimento di camera 1
esce **identica** a quella dell'estrazione completa di settembre
(`y = +0,0507·x + 455,5`, 37.189 fotogrammi eretti).

### Il risultato

| soggetto escluso | K scelto | F2 con quel K | F2 con K=31 | differenza |
|---|---:|---:|---:|---:|
| 1  | 45 | 0,864 | 0,863 | +0,001 |
| 2  | 45 | 0,739 | 0,751 | **−0,012** |
| 3  | **31** | 0,676 | 0,676 | 0,000 |
| 4  | 45 | 0,897 | 0,873 | +0,024 |
| 5  | 45 | 0,897 | 0,874 | +0,024 |
| 6  | 45 | 0,961 | 0,952 | +0,009 |
| 7  | 45 | 0,845 | 0,819 | +0,026 |
| 8  | 45 | 0,927 | 0,882 | +0,045 |
| 9  | 45 | 0,894 | 0,773 | **+0,122** |
| 10 | 45 | 0,808 | 0,785 | +0,023 |
| **media** | | **0,851** | **0,825** | **+0,026** |

**Nove fold su dieci scelgono K = 45**, non il valore adottato.

**Il leakage non ha gonfiato le prestazioni: le ha ridotte.** E' la direzione
opposta a quella di [EXP-044](#exp-044), e va detto perche' la tesi dichiarava
il contrario prima di questa misura.

### Quanto regge

Mediana +0,023. Il test appaiato sui dieci da' **t = 2,22**, appena sotto il
critico 2,26: **non significativo**. Un soggetto pesa molto --- su `Subject_09`
la differenza vale 0,122, quasi cinque volte la media. Escludendolo la media
scende a **+0,016** ma la dispersione si dimezza e il test diventa **t = 2,72**
contro un critico di 2,31. L'effetto e' piccolo e sistematico, non grande e
incerto: positivo in 8 fold su 10, nullo in uno, negativo in uno solo per 0,012.

### Perche' non sorprende

[EXP-053 del progetto storico](../../DIP_PROJECT/docs/EXPERIMENTS.md#exp-053)
mostrava gia' che sul **solo criterio di laboratorio** K=45 batte K=31 (F2
0,987 contro 0,980), e ci si fermo' a 31 per il richiamo di campo (4/5 contro
3/5). Il LOSO interno usa soltanto il criterio di laboratorio e ritrova 45.
Questa e' quindi una conferma indipendente, **a dieci soggetti e con il
protocollo corretto**, di cio' che la scansione a cinque aveva mostrato con
quello sbagliato.

### Che cosa NON misura, e non e' un dettaglio

La ragione per cui si e' preferito 31 non e' di laboratorio ma di campo, e il
richiamo su cui quella preferenza si fonda viene poi riportato fra i risultati
del Capitolo 5. Separare le due cose richiederebbe cadute domestiche diverse da
quelle usate per scegliere, e **cinque cadute non bastano a produrne due insiemi
disgiunti**. Questa misura copre il leakage di laboratorio e non quello di
campo.

**Collegamenti:** [ISS-178](ISSUES.md#iss-178), [EXP-044](#exp-044),
[EXP-053](../../DIP_PROJECT/docs/EXPERIMENTS.md#exp-053)

---

<a id="exp-044"></a>
## EXP-044 — La selezione DTW rifatta dentro ogni fold, e il leakage misurato

**Data:** 2026-09-21 · **Script:** `pipeline/dtw_per_fold.py --csv feature_v5.csv --top 12`
**Natura:** RISELEZIONE — nessun riaddestramento: si rifa' solo la scelta delle
grandezze, dieci volte, escludendo ogni volta il soggetto di prova
**Esito:** ✔ · **Uscita:** `risultati/dtw/per_fold.json`, `risultati/dtw/per_fold.txt`

**Perche'.** La selezione descritta nel Capitolo 3 era stata eseguita una volta
sola sull'intero insieme, prima del LOSO: il soggetto lasciato fuori
contribuiva quindi a decidere quali colonne il classificatore riceve. Il
relatore ha chiesto che il punto venga dichiarato; dichiararlo non basta pero'
a dirne l'entita'.

**Controllo preliminare.** Lo script rifa' prima la selezione sull'intero
insieme e la confronta con `scelte.txt`. La prima esecuzione **e' fallita**, ed
era [ISS-168](ISSUES.md#iss-168): corretta quella, il controllo passa e
riproduce esattamente le dodici grandezze adottate. Senza questo controllo
l'esperimento avrebbe confrontato due selezioni calcolate in modo diverso.

**Esito.**

| | |
|---|---|
| fold che riproducono la selezione adottata | **0 su 10** |
| Jaccard medio | **0,769** |
| grandezze in tutti i fold e anche adottate | **6 su 12** |
| sovrapposizione per fold | fra 9/12 e 11/12 |

Il nucleo stabile e' `A1_discesa`, `A2_discesa`, `A3_discesa`, `A3_percorso`,
`A3_hip_vel`, `A3_testa_vel_rel`: **cinque delle sei sono integrali**. Le due
piu' instabili, `A1_escursione` e `A2_testa_rel_y`, sono scelte da cinque fold
su dieci.

**Come leggere gli scambi.** Sedici scambi accoppiati, correlazione fra la
grandezza che esce e quella che entra: mediana 0,793, **otto su sedici sopra
0,85**, cioe' sopra la soglia con cui la procedura stessa dichiara due
grandezze intercambiabili (`A2_testa_rel_y` contro `A2_angolo_tronco`: 0,972;
`A3_caviglie_rel_y` contro `A3_ginocchia_rel_y`: 0,934). Meta' degli scambi e'
quindi nominale. L'altra meta' no: `A2_percorso` sostituita da `A1_asse_mag`
sono correlate 0,065.

**Validita'.** Il leakage e' accertato e le metriche del Capitolo 4 restano un
limite superiore. **Non e' stato misurato l'effetto sulle metriche**: servirebbe
riaddestrare le sei architetture dieci volte con il sottoinsieme proprio di
ciascun fold. Questo esperimento misura la stabilita' della selezione, non il
costo dell'instabilita'.

---

<a id="exp-043"></a>
## EXP-043 — Le regole di allarme su v2, e la scoperta che il laboratorio non puo' misurare la sospensione

**Data:** 2026-09-10 · **Script:** `pipeline/regole_allarme.py --csv feature_v2.csv --run foresta_tre_classi_DTW_cam1 --punteggi risultati/addestramento/v2`
**Natura:** RILETTURA — nessun riaddestramento: cambia solo l'aritmetica che
trasforma i punteggi gia' salvati in allarmi
**Esito:** ✔ · **Uscita:** `risultati/laboratorio/regole_allarme_foresta_tre_classi_DTW_cam1.json`

**Perche'.** [EXP-029](#exp-029) aveva confrontato ventuno regole, ma su
`feature_v3.csv`. Portata la tesi a v2, quel confronto andava rifatto sugli
stessi punteggi che reggono il Capitolo 4, altrimenti la discussione sulla
regola di allarme poggia su un dataset diverso da tutto il resto.

### Il confronto regge, e non dipende dalla versione del dataset

| regola | richiamo | latenza mediana | allarmi/ora in casa |
|---|---:|---:|---:|
| **consecutive 5** *(installata)* | **0,90** | **2,53 s** | **10,8** |
| cumulata 0,5 | **0,98** | **1,64 s** | 9,3 |
| cumulata 1,0 | 0,92 | 1,94 s | 8,5 |
| isteresi 0,70/0,40/3 | 0,94 | 2,00 s | 7,7 |
| **isteresi 0,80/0,45/3** | 0,92 | 2,00 s | **5,1** |
| isteresi 0,90/0,50/3 | 0,84 | 2,00 s | 3,0 |

**Quattro regole su ventuno battono quella installata su entrambi gli assi**, e
sono le stesse famiglie che vincevano su v3: la conclusione di EXP-029 --- la
famiglia sbagliata e' quella *consecutiva*, non il valore di k --- **non dipende
dalla versione del dataset**. E' la verifica piu' forte che quel risultato abbia
finora ricevuto.

### E poi la scoperta, che riguarda un altro parametro

La sospensione dopo un allarme e' stata fatta variare fra 5 e 60 secondi, a
parita' di tutto il resto:

| sospensione | richiamo | latenza | allarmi/ora |
|---:|---:|---:|---:|
| 5 s | 0,90 | 2,53 s | 30,6 |
| 10 s | 0,90 | 2,53 s | 20,8 |
| 15 s | 0,90 | 2,53 s | 16,0 |
| **30 s** *(installata)* | **0,90** | **2,53 s** | **10,8** |
| 60 s | 0,90 | 2,53 s | 7,3 |

> **Il richiamo e la latenza non si muovono di un centesimo. Solo i falsi
> allarmi cambiano, e di un fattore quattro.**

Letta cosi', la sospensione sembra un parametro gratuito: allungarla riduce i
falsi allarmi e non costa nulla. **Ed e' una conclusione falsa**, prodotta da un
limite dei dati e non da una proprieta' del sistema.

### Perche' e' falsa

La sospensione puo' cancellare una caduta vera **solo se due cadute distinte
cadono vicine nel tempo**. Nel materiale di laboratorio questo non accade mai:

| | |
|---|---:|
| riprese di UP-Fall che contengono una caduta | 50 |
| riprese con **una sola** transizione | 48 |
| riprese con due transizioni | 2 --- distanti **0,39 s** e **0,11 s** |

Le due riprese con due transizioni sono **la stessa caduta annotata con una
breve interruzione**, non due cadute: a un decimo di secondo di distanza nessuna
regola le distinguerebbe. In pratica **ogni ripresa contiene esattamente una
caduta**, e una sospensione non ha nulla da sopprimere.

**Il costo dei trenta secondi e' quindi strutturalmente invisibile su questi
dati.** L'unica volta che si e' manifestato e' stato in casa, il 9 settembre:
due cadute a **sei secondi** di distanza, la seconda vista benissimo dal
classificatore (picco 0,800, nove finestre sopra soglia) e mai segnalata
([ISS-162](ISSUES.md#iss-162)).

### Che cosa se ne ricava, in concreto

1. **La regola di aggregazione si puo' studiare su v2**, e la conclusione regge.
2. **La sospensione no.** Scandirla su questi dati produce una frontiera che
   mostra solo il beneficio e mai il prezzo, e chi la leggesse senza questa
   avvertenza sceglierebbe il valore piu' alto.
3. Per misurare il prezzo servono **registrazioni con due cadute ravvicinate**,
   che oggi esistono in un solo esemplare e non annotato al secondo.

**Verificato con:** il comando in testa, e la stessa esecuzione ripetuta con
`--sospensione` 5, 10, 15, 30 e 60; conteggio delle transizioni separate per
ripresa su `feature_v2.csv`, camera 1 -> 48 riprese con una, 2 con due a 0,39 s
e 0,11 s di distanza.

**Collegamenti:** [EXP-029](#exp-029), [ISS-162](ISSUES.md#iss-162),
[DEC-108](DECISIONS.md#dec-108), [EXP-039](#exp-039)

---

<a id="exp-042"></a>
## EXP-042 — Le 422 clip di agosto rilette con la selezione a dodici grandezze

**Data:** 2026-09-10 · **Script:** `deploy_board/rendi_clip.py --pacchetto deploy_board/pacchetto_dtw12 --senza-immagini`
**Ambiente:** `fall_processing` (MediaPipe 0.10.9, la stessa della board)
**Natura:** RILETTURA — nessun riaddestramento; cambia solo il pacchetto con cui le
immagini già salvate vengono rielaborate
**Uscita:** `deploy_board/riletture/dtw12_agosto/` — 422 CSV, nessuna immagine
**Esito:** ✔

**Perché.** La rilettura del 9 settembre con il pacchetto v5/DTWH aveva prodotto
**36 CSV su 422**: il 91,5% delle clip non produceva alcuna decisione. Il LEGGIMI
di quella cartella indicava il controllo che lo avrebbe accertato --- rifare le
stesse clip con un pacchetto **senza** `A3_h_pavimento` --- e dichiarava «**non è
stato fatto**». Questo è quel controllo.

### La verifica di parità, prima della misura

Il modello del pacchetto è stato salvato con scikit-learn 1.6 e l'ambiente monta
la 1.7.2. `metadata.json` dichiara che se le versioni non sono compatibili
«nessuna misura successiva è valida», e il pacchetto porta 200 finestre di
riferimento apposta. Eseguita: **scarto massimo 0,000e+00**, sotto la soglia di
1e-6. Le due versioni producono predizioni identiche.

### Il risultato

| | pacchetto v5/DTWH (13 colonne) | **pacchetto DTW (12 colonne)** |
|---|---:|---:|
| clip elaborate | 422 | **422** |
| clip che producono una decisione | 36 --- **8,5%** | **422 --- 100,0%** |

**Nessuna clip scartata.** [ISS-156](ISSUES.md#iss-156) è accertata: era la stima
del piano del pavimento a rendere mute le riletture, non i dati. Su una clip di
una quindicina di secondi il riferimento non fa in tempo a formarsi, e senza di
esso il presidio scarta ogni finestra.

### Che cosa direbbe oggi il sistema di quegli istanti

| sessione | clip | allarmi |
|---|---:|---:|
| `bloccomultipersona_20260810_165645` | 9 | 3 |
| `bloccosolo_20260810_172124` | 8 | 2 |
| `bloccodurata5h_20260811_130411` | 30 | 1 |
| `bloccocadute_2persone_20260812_181033` | 10 | 2 |
| `bloccocadute_nonni_20260812_154007` | 56 | 2 |
| `bloccononni_20260812_142519` | 150 | 0 |
| `bloccocadute_sola_20260813_091641` | 9 | 0 |
| `bloccomulti_3persone_20260813_113943` | 150 | 3 |
| **totale** | **422** | **13** |

Picco mediano **0,180**; sopra soglia in **24 clip su 422 (5,7%)**, sopra 0,80 in
undici.

Le quattro regole a confronto, sugli stessi punteggi e con la stessa sospensione
di 30 s:

| regola | allarmi |
|---|---:|
| **installata --- 0,50 e cinque consecutive** | **13** |
| 0,50 e cinque su sette | 14 |
| 0,40 e due consecutive | 27 |
| 0,30 e tre su cinque | 41 |

### Che cosa questo NON misura, e va detto

- **Non è un tasso di falsi allarmi.** Le clip esistono soltanto dove il sistema
  di agosto aveva già suonato: sono ~422 finestre di venti secondi, non le
  14,98 ore. È un campione **sbilanciato per costruzione**.
- **Non è un richiamo.** Una caduta che il sistema di allora si era persa non ha
  lasciato immagini, e nessuna rilettura la può recuperare.
- **È** il numero di vecchi allarmi che il modello di oggi rifarebbe: **13 su
  422**. Gli altri 409 non li rifarebbe.

### Un difetto dello strumento, incontrato per strada

Alla prima esecuzione MediaPipe è andato in errore a metà delle due sessioni più
lunghe, portandosi via **169 clip**:

```
RET_CHECK failure (inference_interpreter_delegate_runner.cc:154)
  (interpreter_->Invoke())==(kTfLiteOk)
ERROR: failed to setup XNNPACK runtime
RuntimeError: CalculatorGraph::Run() failed
```

Non dipende dalla lunghezza delle clip --- quelle perse hanno fra 93 e 178
fotogrammi, nessuna sotto i 22 necessari --- ed è stato aggirato rieseguendo a
blocchi di quindici clip, così che un errore ne perda quindici e non centocinquanta.
**Chi rilancia questa analisi in un colpo solo deve aspettarsi di perdere pezzi
senza che il conteggio finale lo dichiari.**

**Verificato con:** `rendi_clip.py` su 422 cartelle di clip -> 422 CSV, tutti con
almeno una riga; prova di parità del pacchetto -> scarto massimo 0,000e+00 su 200
finestre; conteggio degli allarmi ricalcolato dai CSV con le quattro regole.

**Collegamenti:** [ISS-156](ISSUES.md#iss-156), [ISS-142](ISSUES.md#iss-142),
[EXP-029](#exp-029), [EXP-040](#exp-040)

---

<a id="exp-041"></a>
## EXP-041 — I numeri di campo della mail al relatore si riproducono, e 1,41 ore erano cieche

**Data:** 2026-09-10 · **Script:** `pipeline/eventi_sessioni.py`
**Natura:** RILETTURA — nessun modello riaddestrato, nessuna clip riletta:
solo i `punteggi.csv` gia' registrati dalla board in agosto e il 6 settembre
**Dati:** nove sessioni domestiche, 14,98 ore
**Esito:** ✔ · **Uscita:** `risultati/campo/eventi_sessioni.json`

**Perche'.** Prima di rileggere le clip con un pacchetto nuovo serviva sapere
se i numeri comunicati al relatore si ottengono ancora dal repository com'e'
oggi. E' la domanda piu' economica del lavoro: non richiede ne' clip ne'
riaddestramento.

### I numeri della mail, riprodotti

| | nella mail | oggi |
|---|---:|---:|
| finestre positive/ora | 496 | **496** |
| eventi/ora | 11,1 | **11,1** |
| **fattore fra le due contabilita'** | **44,8** | **44,8** |
| ore | --- | 14,98 |
| sessioni | «quelle attualmente incluse» | **9** |

Le nove sono quelle sopra i nove minuti: `--min-ore` vale 0,15 e scarta
quattro riprese, tre delle quali durano fra 0,03 e 0,11 ore e una non ha
nessuna finestra. **Il criterio esiste ed e' un parametro**, non una scelta
implicita, ma non e' stampato: chi legge l'uscita vede nove blocchi e non
sa che ne sono stati esclusi quattro.

### Il difetto che l'analisi ha fatto emergere

**1,41 delle 14,98 ore sono buchi**: intervalli in cui non e' stata prodotta
nessuna decisione, e che finiscono lo stesso nel denominatore di eventi/ora
([ISS-167](ISSUES.md#iss-167)).

| | arco | buco | attive |
|---|---:|---:|---:|
| `bloccodurata5h_20260811` | 6,11 h | **1,13 h** | 4,98 h |
| `bloccosolo_20260810` | 0,38 h | 0,14 h | 0,25 h |
| `bloccoduepersone_20260810` | 0,35 h | 0,14 h | 0,21 h |
| **totale** | **14,98 h** | **1,41 h** | **13,57 h** |

Il buco maggiore e' un salto unico: le finestre si fermano alle **16:03:30** e
riprendono alle **17:11:12**, contro un intervallo mediano di **0,281 s**. Il
`riepilogo.json` di quella sessione dichiara `stalli: 1` e
`stallo_totale_s: 20.0`.

| | sulle ore totali | sulle ore attive |
|---|---:|---:|
| finestre/ora | 496 | **547** |
| eventi/ora | **11,1** | **12,2** |
| fattore | **44,8** | **44,8** |

**Il fattore non si muove, ed e' il punto.** E' un rapporto: il denominatore
si semplifica. L'affermazione centrale del punto 9 della mail --- contare
finestre invece che eventi sovrastima di 44,8 volte --- **regge esattamente**.
Quello che si muove del 10% e' il tasso assoluto, e va corretto dove compare.

### Che cosa questo NON dice

- **Non dice che i numeri delle figure si riproducono.** Le figure leggono
  `risultati/addestramento/`, e quelle run sono state riscritte il 9 settembre
  su `feature_v5.csv`: rigenerando `fig_architetture.png` oggi la GRU passa in
  testa a 0,857 e la LSTM scende a 0,829. Qui e' stato verificato **solo** il
  campo, che legge i punteggi registrati e non dipende da nessun
  riaddestramento.
- **Non misura il richiamo domestico.** Le sessioni non hanno cadute annotate
  al secondo; qui si contano allarmi, non cadute prese.

**Collegamenti:** [ISS-167](ISSUES.md#iss-167), [EXP-024](#exp-024),
[EXP-029](#exp-029), Capitolo 5 `tab:eventi`

---

<a id="exp-040"></a>
## EXP-040 — Le 422 clip di agosto rilette con il pacchetto v5

**Data:** 2026-09-09 · **Script:** `deploy_board/rendi_clip.py --senza-immagini`
**Ambiente:** `fall_processing` (MediaPipe 0.10.9) · **Dati:** 58.815 fotogrammi

Tutte le clip salvate attorno agli allarmi delle sessioni domestiche di agosto,
ricalcolate con il pacchetto **v5/DTWH** installato la sera del 9 settembre.
La domanda: *che cosa direbbe oggi il sistema dei momenti che allora lo fecero
suonare?*

| sessione | casa | clip | **mute** | picco | allarmi v5 |
|---|---|---:|---:|---:|---:|
| `bloccosolo` 10/08 | studente | 8 | 5 | 0,780 | **2** |
| `bloccomultipersona` 10/08 | studente | 9 | 6 | 0,300 | 0 |
| `bloccodurata5h` 11/08 | studente | 30 | **29** | 0,220 | 0 |
| `bloccononni` 12/08 | nonni | 150 | **144** | 0,360 | 0 |
| `bloccocadute_nonni` 12/08 | nonni | 56 | **51** | 0,740 | 0 |
| `bloccocadute_2persone` 12/08 | nonni | 10 | 6 | 0,840 | **1** |
| `bloccocadute_sola` 13/08 | nonni | 9 | 4 | 0,460 | 0 |
| `bloccomulti_3persone` 13/08 | nonni | 150 | **141** | 0,280 | 0 |
| **totale** | | **422** | **386** | | **3** |

### Il risultato, ed e' negativo

> **Su 422 clip, 386 --- il 91,5% --- non producono una sola decisione.**

Non e' che il modello dica «non e' una caduta»: **non dice niente**. Il piano
del pavimento non fa in tempo a essere stimato su una clip di una quindicina di
secondi, e senza quello il presidio scarta ogni finestra. E'
[ISS-156](ISSUES.md#iss-156), che lo descriveva gia' in un titolo --- *«con
l'altezza dal pavimento installata, una clip corta non e' valutabile»* --- e
che qui viene **quantificata per la prima volta**.

### Perche' il «3 allarmi su 422» non e' un risultato

Sembra una riduzione dei falsi allarmi del 99,3%. **Non lo e'**: in 386 casi su
422 il sistema non ha valutato nulla, e non valutare non e' non allarmare. Il
numero interpretabile e' un altro: **3 allarmi su 36 clip effettivamente
decise.**

### Che cosa questo impedisce

**Tutto il materiale di campo di agosto non e' rivalutabile con la
configurazione installata.** Sono 9,6 ore di registrazioni in due abitazioni,
422 eventi, ed e' il patrimonio di campo dell'intero lavoro. Con
`A3_h_pavimento` a bordo, il 91,5% e' cieco.

Ne segue che **la decisione 2 del relatore** --- mantenere l'altezza dal
pavimento, dichiarando che e' stata reintrodotta dopo aver osservato gli errori
domestici --- ha un costo che lui non conosceva: quella grandezza rende
impossibile rileggere il passato. Va detto.

### Il controllo che chiuderebbe la questione, e non e' stato fatto

Esportare un pacchetto **DTW a 12 colonne**, senza `A3_h_pavimento`, e rilanciare
le stesse 422 clip. Se le clip mute tornano a decidere, la causa e' accertata e
non solo coerente. **Non e' stato fatto.**

### La verita' di riferimento che esiste finora

Dichiarata dalla candidata su `bloccocadute_nonni_20260812_154007`:

| clip | che cosa contiene | esito |
|---|---|---|
| `evt_0067_155044` | **una caduta**, con due persone distese sui divani | picco **0,740**, 2 finestre sopra soglia su 5 richieste -> **nessun allarme**. E lo scheletro e' agganciato a una persona sul divano, non a chi cade ([ISS-134](ISSUES.md#iss-134)) |
| `evt_0090_155058` | a terra, poi si rialza | picco **0,020** --- corretto: l'evento e' la transizione, non lo stato |
| `evt_0173_155210` | **inizia una caduta** | muta |
| `evt_0191_155223` | la caduta | muta |
| `evt_0201_155236` | si rialza | muta |

**Tre difetti concorrono a perdere una caduta domestica vera**, e nessuno dei
tre e' il classificatore: [ISS-134](ISSUES.md#iss-134) (posa sulla persona
sbagliata), [ISS-156](ISSUES.md#iss-156) (clip non valutabile),
[ISS-162](ISSUES.md#iss-162) (la regola chiede cinque finestre e ne ha due).

**Artefatti:** `deploy_board/resa_v5_agosto/` (36 CSV per finestra),
`deploy_board/resa_v5_cadute_nonni/` (792 fotogrammi annotati delle cinque clip
con verita' di riferimento).

**Validita':** il conteggio delle clip mute e' solido. Il richiamo su cadute
domestiche **non e' misurabile da qui**: le clip esistono solo dove il sistema
di allora aveva suonato, quindi una caduta che il vecchio sistema si era persa
non ha lasciato immagini.
