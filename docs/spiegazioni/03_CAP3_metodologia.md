# Capitolo 3 — Metodologia: dal video alle feature

**File:** `tesi/Cap3.tex` · **etichetta:** `cap:metodologia` · **9.498 parole**,
7 sezioni, 13 sottosezioni.
**Codice:** `src/geometry.py`, `src/dtw.py`, `src/etichettatura.py`,
`src/dati.py`, `pipeline/estrai_feature.py`, `pipeline/analisi_dtw.py`,
`pipeline/mappa_omnifall.py`, `pipeline/rumore.py`.

È il capitolo tecnico: descrive la catena che porta da un video RGB al vettore
che il classificatore riceve. Ogni formula del capitolo è trascritta da
`src/geometry.py` e riverificata contro il codice.

---

## 0. La catena, in una figura a parole

```
PNG (640×480)                       pipeline/estrai_feature.py
   ↓  MediaPipe Pose (solutions)    33 landmark 2D + 33 world landmark 3D
   ↓  MotoreGeometrico.fotogramma() src/geometry.py — stato per ripresa
   ↓                                32 grandezze: A1 (9) + A2 (5) + A3 (9) + integrali (9)
CSV per fotogramma                  soggetto, ripresa, camera, fotogramma, label, ha_posa, 32 colonne
   ↓  analisi DTW                   src/dtw.py + pipeline/analisi_dtw.py
   ↓                                sottoinsieme di 12 grandezze → risultati/dtw/scelte.txt
   ↓  finestratura                  src/dati.py — 22 campioni, passo 2, dentro tratti continui
   ↓  etichettatura                 src/etichettatura.py — criterio K-su-M, due etichette
finestre (n, 22, 12) + y_train + y_allarme
```

---

## 1. Perché una finestra e non un fotogramma

Il rilevamento di una caduta è un caso di **motion analysis**: un video è una
funzione spazio-temporale $I(x,y,t)$, e il movimento non è deducibile da una
singola immagine.

La distinzione che interessa — caduta contro attività quotidiana — **non risiede
in una posa**. Chi si china a raccogliere un oggetto, chi si siede rapidamente,
chi si inginocchia, in un singolo fotogramma assume configurazioni visivamente
simili a quelle di chi sta cadendo. Ciò che le separa è la **traiettoria**.

Da qui la prima scelta strutturale: **non si classifica il singolo fotogramma,
ma una finestra temporale.**

Le tre fasi della caduta corrispondono alle tre etichette dell'annotazione:

| fase | etichetta | durata mediana (50 riprese, cam1) |
|---|---|---|
| pre-caduta, postura eretta | 0 | 0,92 s |
| **caduta in corso** (perdita di equilibrio → arrivo a terra) | 1 | **3,11 s** (decili 2,05 – 3,94) |
| post-caduta, a terra | 2 | 5,97 s (decili 4,82 – 6,89) |

Il fatto che la fase centrale duri **tre secondi** e non mezzo è già un dato
contro l'intuizione: l'annotazione fa cominciare la fase alla perdita di
equilibrio, non all'impatto. Sarà la base dell'ipotesi (poi smentita) sulla
lunghezza della finestra.

---

## 2. La stima della posa, e la natura del suo errore

### 2.1 Denso contro sparso, e i due stimatori

Il dato di partenza è **denso** (pixel). Il classificatore però non lo riceve:
fra immagine e modello si interpone uno stimatore di posa, che produce una
rappresentazione **sparsa**.

| stimatore | punti | coordinate | persone |
|---|---:|---|---|
| MediaPipe `solutions` | 33 | 2D + world 3D | 1 |
| MediaPipe `tasks` | 33 | 2D + world 3D | ≥ 1 |
| YOLOv8-pose | 17 (COCO) | **solo 2D** | tutte |

Due conseguenze che ritornano nel Capitolo 5:

- **YOLOv8 non fornisce i world landmark 3D**, quindi la rappresentazione A2
  *non è calcolabile* su quella pipeline. È una delle tre ragioni per cui è A3 —
  e non A2 — la rappresentazione su cui il sistema è costruito, malgrado A2 abbia
  in laboratorio un F2 medio leggermente più alto;
- uno stimatore **a persona singola sceglie la più prominente**, e una persona
  distesa occupa molta meno area di una in piedi.

### 2.2 Quali landmark, e perché quelli

Non si usano tutti e 33. Ogni rappresentazione ne seleziona un sottoinsieme, per
significato cinematico:

| rappresentazione | indici MediaPipe | landmark |
|---|---|---|
| **A1** — sagoma | 0, 11, 12, 23, 24, 27, 28 | naso, spalle, anche, caviglie |
| **A2** — tridimensionale | 0, 11, 12, 23, 24 | naso, spalle, anche |
| **A3** — riferita al corpo | 0, 11, 12, 23–28 | naso, spalle, anche, ginocchia, caviglie |
| B — scheletro grezzo | 12 punti | spalle, gomiti, polsi, anche, ginocchia, caviglie |

Nel codice sono costanti con nome (`src/geometry.py:80-90`): `NASO = 0`,
`SPALLA_SX, SPALLA_DX = 11, 12`, `ANCA_SX, ANCA_DX = 23, 24`, e così via.

> **Un difetto silenzioso già corretto.** `PUNTI_ELLISSE` contiene **sette**
> punti. Nella versione precedente `processing.py` ne usava sette e
> `demo_realtime.py` cinque: **la demo calcolava una A1 diversa da quella di
> addestramento**, senza che nulla lo segnalasse. È il tipo di divergenza che
> non produce errori, produce numeri.

**La distinzione fra le famiglie non è «pochi punti contro molti», ma
*grandezze progettate a mano contro coordinate grezze*.**

### 2.3 Il rumore, in due forme che richiedono trattamenti diversi

**Forma 1 — assenza della posa.** In una frazione dei fotogrammi lo stimatore
non produce nulla: **4,5% su UP-Fall, 19% su UR-Fall**. Il trattamento nel
codice (`geometry.py:350-358`):

```python
def fotogramma(self, landmarks, world, w, h, fps):
    if landmarks is None:
        self.reset()                       # azzera stato e buffer
        return {k: 0.0 for k in NOMI}      # tutte le grandezze a zero
```

e la riga `'ha_posa': int(lm is not None)` in `estrai_feature.py:133`.

**La marcatura è essenziale perché uno zero non è un valore neutro.** Un angolo
del tronco pari a zero descrive un tronco *orizzontale*; e una sequenza di zeri
seguita da un valore reale produce una derivata di ampiezza arbitraria. Per la
stessa ragione lo stato temporale viene azzerato a ogni interruzione, così
nessuna grandezza dinamica attraversa il buco.

Lo stesso principio è applicato più a valle in `src/dati.py:181-202`
(`_tratti_continui`): ogni ripresa viene spezzata nei suoi tratti di posa valida
continua, e **le finestre si costruiscono dentro un tratto solo** — ventidue
campioni presi a cavallo di un'interruzione descriverebbero un movimento mai
avvenuto e coprirebbero più tempo di quanto la finestra dichiara.

**Forma 2 — rumore sulla posizione stimata.** Il landmark c'è, ma la coordinata
oscilla anche a corpo fermo. È la forma insidiosa: non è rilevabile da un
controllo di validità e si propaga a tutte le grandezze derivate.

### 2.4 Perché il filtro non è la risposta

La risposta immediata sarebbe una media mobile esponenziale,
$\tilde{x}_t = \alpha x_t + (1-\alpha)\tilde{x}_{t-1}$: ricorsiva, senza storia,
una operazione per fotogramma — la scelta naturale su edge.

Due cose vanno dette, e il capitolo le dice entrambe.

**La prima è un fatto sull'implementazione, dichiarato invece che nascosto.** Nel
prototipo il filtro era **previsto ma non applicato**: il motore geometrico
accettava i parametri α e non li usava, mentre un'altra componente ne applicava
uno proprio. Le grandezze usate in addestramento e quelle prodotte in esercizio
avevano quindi caratteristiche di segnale diverse.

**La seconda è che correggerlo non avrebbe risolto niente**, e la ragione
riguarda l'ordine delle operazioni:

> Il filtraggio agisce sulla **posizione**; le grandezze che interessano sono
> **derivate** della posizione. Filtrare prima di derivare riduce il rumore ma
> riduce anche il segnale, perché la derivazione amplifica le alte frequenze e
> il filtro le attenua entrambe senza distinguerle. **Il compromesso non si
> risolve: si sposta.**

La misura che rende il problema quantitativo è l'autocorrelazione a un passo
(sezione 4).

---

## 3. Le tre rappresentazioni geometriche

Non sono tre modelli in competizione: sono **tre punti di vista sullo stesso
dato**, e insieme formano il bacino di candidate da cui il DTW estrae il
sottoinsieme usato.

I nomi sono **prefissati** (`A1_`, `A2_`, `A3_`), e non è pedanteria: nella
versione iniziale `d_trunk_angle` esisteva sia in A2 sia in A3 **con unità
diverse** — gradi/fotogramma contro gradi/secondo, mediane 0,167 e 1,700 — ed era
l'unica colonna in comune. Un accorpamento senza prefisso le avrebbe fuse in
silenzio. → [DEC-100](../DECISIONS.md#dec-100)

### 3.1 A1 — la sagoma come ellisse (9 grandezze)

Sette landmark trattati come **distribuzione di punti** nel piano immagine.
Dalla matrice di covarianza si ricavano autovalori e autovettori
(`geometry.py:185-194`): gli autovettori danno le direzioni principali, gli
autovalori la dispersione lungo di esse. Intuitivamente: il corpo approssimato
da un'ellisse.

Grandezze: `asse_mag`, `asse_min`, `allungamento` (rapporto fra gli assi),
`inclinazione`, le tre derivate, e `vx`, `vy` (velocità del baricentro).

**Il pregio: non conosce l'anatomia.** Non le serve identificare correttamente
il tronco per accorgersi che la sagoma è passata da verticale e stretta a
orizzontale e larga. Funziona anche quando lo stimatore sbaglia l'attribuzione
dei singoli giunti. **Il limite è lo stesso:** non distingue una persona distesa
da una chinata in avanti.

#### ISS-100 — il periodo di srotolamento (risolta il 19 agosto)

`arctan2` avvolge a ±180°. L'angolo va **srotolato prima di derivare**, e la
funzione è `_srotola` (`geometry.py:132-151`):

```python
return angolo_gradi - periodo * round((angolo_gradi - precedente) / periodo)
```

**Il periodo non è sempre 360.** Un vettore ha periodo 360: il tronco punta in
una direzione, ruotarlo di mezzo giro lo capovolge. **L'asse di un'ellisse ha
periodo 180**, perché un autovettore e il suo opposto descrivono lo stesso asse.

Con il periodo sbagliato si misurava un passaggio da **201,9° a 49,5° fra due
fotogrammi consecutivi**, cioè 152 gradi in un diciottesimo di secondo:
fisicamente impossibile. Ogni salto si propagava alla derivata e a ogni grandezza
accumulata. La correzione è una riga: `incl = _srotola(incl, p_inc, periodo=180.0)`
(`geometry.py:222`).

### 3.2 A2 — descrittori tridimensionali (5 grandezze)

Usa i **world landmark**: coordinate metriche 3D stimate dalla rete. È l'unica
delle tre a non essere una proiezione, quindi potenzialmente meno sensibile al
punto di vista — ed è confermato dal DTW: `A2_angolo_tronco` fa 1,486/1,284 sulle
due camere contro 1,270/1,104 di `A3_angolo_tronco`.

Grandezze: `angolo_tronco`, `d_angolo_tronco` (con segno), `vel_ang_tronco`
(modulo), `testa_vel`, `testa_rel_y`.

Due precisazioni, entrambe sul sistema di riferimento.

**La prima:** il riferimento dei world landmark è **canonico e centrato sulle
anche**, non allineato alla gravità reale. L'angolo calcolato non è quindi
un'inclinazione assoluta rispetto al pavimento: è una misura relativa al corpo.
Resta informativa, ma chiamarla «inclinazione rispetto alla verticale» sarebbe
impreciso. Il commento è nel codice, `geometry.py:249-253`.

**La seconda è ISS-104, ed è la più grave del capitolo.**

#### ISS-104 — quattro grandezze A2 misuravano l'origine del riferimento

Poiché il riferimento è centrato sulle anche, **il bacino è l'origine e non si
muove per costruzione**. Misurato su 40 fotogrammi consecutivi:

```
bacino  dev.std  [0,000034  0,000047  0,000046] m   ← 0,03 mm
naso    dev.std  [0,012700  0,002712  0,017535] m   ← 400 volte tanto
```

Quattro grandezze misuravano quindi **rumore numerico**:

| grandezza | massimo misurato | destino |
|---|---:|---|
| `A2_hip_vy` | 0,000 | **rimossa** |
| `A2_hip_vel` | 0,1 | **rimossa** |
| `A2_percorso` | 7,6 | **ridefinita sul naso** |
| `A2_discesa` | 1,4 | **ridefinita sul naso** |

**L'aggravante: la grandezza degenere era stata selezionata.** `A2_percorso` era
entrata fra le dodici scelte di [EXP-006](../EXPERIMENTS.md#exp-006), al nono
posto, e la sua bassa correlazione con `A1_percorso` (0,25) e `A3_percorso`
(0,30) era stata interpretata come «porta la componente in profondità».

> Era indipendente **perché era rumore**, e il rumore non correla con niente.
> È il modo tipico in cui una grandezza degenere supera un filtro di ridondanza.

**Verifica della correzione ([EXP-007](../EXPERIMENTS.md#exp-007)):**
riestrazione completa e confronto colonna per colonna su 114.923 righe — **30
colonne identiche bit per bit**, solo le due ridefinite cambiate, due rimosse.
La modifica ha toccato esattamente ciò che doveva.

| grandezza | v1 mediana\|·\| | v1 max | v2 mediana\|·\| | v2 max |
|---|---:|---:|---:|---:|
| `A2_percorso` | 0,000 | 7,6 | **0,185** | 17,7 |
| `A2_discesa` | 0,000 | 1,4 | **0,015** | 7,9 |

E nel DTW rifatto ([EXP-008](../EXPERIMENTS.md#exp-008)) le due riabilitate
entrano al **secondo e terzo posto** della classifica, dove prima erano in fondo
come rumore.

Il file v1 è stato **rinominato** `feature_v1_A2_degenere.csv` invece che
cancellato: 124 minuti di calcolo non si buttano, ma il nome deve rendere
impossibile usarlo per sbaglio.

### 3.3 A3 — descrittori riferiti al corpo (9 grandezze)

Landmark 2D come A1, ma **ogni grandezza divisa per la lunghezza del tronco**.
Il risultato è adimensionale, quindi indipendente da distanza e corporatura: la
stessa posa a due o a cinque metri, su una persona alta o bassa, produce gli
stessi numeri.

Grandezze: `torso_len` (il fattore di normalizzazione), `angolo_tronco` e
derivata, `testa_rel_y`, `ginocchia_rel_y`, `caviglie_rel_y`, `larghezza`,
`hip_vel` (in lunghezze di torso al secondo), `testa_vel_rel`.

**È la rappresentazione anatomicamente più ricca** — l'unica che osservi gli
arti inferiori, e sapere che le caviglie sono salite all'altezza del bacino
distingue una caduta all'indietro da un piegarsi — ma vive nel piano immagine e
ne eredita la dipendenza dal punto di vista.

**E il suo pregio è anche il suo limite:** normalizzando tutto rispetto al
bacino, A3 **cancella per costruzione** l'informazione su *dove* il corpo si
trovi nella stanza. È il motivo per cui esiste la sezione sull'altezza dal
pavimento.

### 3.4 Che cosa è stato rimosso, e perché

Rispetto alle dieci grandezze per rappresentazione della formulazione iniziale:

**Grandezze degenerate per costruzione** — le due A2 di ISS-104.

**Grandezze dimensionalmente prive di senso** — le tre `energy`, una per
rappresentazione, calcolate come somme di quadrati dei contributi dinamici.
Sommavano quadrati di **gradi, rapporti adimensionali, pixel e frazioni di
immagine**: quantità non omogenee, risultato senza unità interpretabile.
Rapporti fra massimo e mediana di **728.079 in A1 e 750.174 in A2**, ed erano
all'origine del **fattore 646** fra le scale che senza normalizzazione rendeva
nove colonne su dieci invisibili al modello.

**Derivate seconde** — le accelerazioni di A2: se la derivata prima amplifica il
rumore dello stimatore, la seconda lo amplifica due volte.

**Bacino risultante: 32 grandezze** = 9 (A1) + 5 (A2) + 9 (A3) + 3×3 integrali.

**Una convenzione temporale unica.** Nella formulazione iniziale A1 calcolava
differenze *per fotogramma* mentre A2 e A3 dividevano per Δt: confrontare A1 con
A3 significava confrontare anche due convenzioni temporali, e cambiando frame
rate una sola delle due cambiava scala. Ora **tutte le derivate sono per
secondo** (`geometry.py:359`, `dt = 1.0 / fps`).

### 3.5 B — coordinate scheletriche grezze, e perché non entra nei confronti

Dodici landmark in coordinate relative al bacino, 24 valori per fotogramma, dati
a un autoencoder seguito da un classificatore. L'idea era stabilire se costruire
a mano le grandezze produca una classificazione migliore del lasciare che sia il
modello a scoprire la rappresentazione.

**Non entra nei confronti, ed è dichiarato qui e non altrove.** Appartiene al
prototipo di partenza, e l'unica esecuzione disponibile **valutava i due approcci
su verità di riferimento diverse**. Va citato come lavoro preliminare, non come
confronto.

---

## 4. Le grandezze integrali — il contributo metodologico del capitolo

### 4.1 L'osservazione da cui parte

Non teorica, sperimentale: verificando il classificatore sulle registrazioni
domestiche è emerso che **assegnava punteggio elevato anche a corpi
completamente immobili**, e che la correlazione fra il punteggio prodotto e il
movimento effettivamente presente nella finestra era **+0,139**, cioè
praticamente nulla.

Il modello aveva imparato una **scorciatoia posturale**: tronco orizzontale ⇒
caduta, indipendentemente da come il corpo ci fosse arrivato. È una regola
perfetta su un dataset in cui nessuno si sdraia mai su un divano, e sbagliata in
una casa vera.

**La prima ipotesi era che il difetto fosse del classificatore. La verifica ha
mostrato che era a monte, nelle grandezze che gli venivano fornite.**

### 4.2 Perché derivare amplifica il rumore

$v(t) = \dfrac{x(t)-x(t-1)}{\Delta t}$ divide la differenza fra **due stime
rumorose** per un intervallo piccolo. Se ciascuna ha errore σ, la differenza ne
ha $\sigma\sqrt{2}$, e la divisione per $\Delta t = 1/\text{fps}$ la moltiplica
per il frame rate: **a 18 fps l'errore sulla velocità è circa venticinque volte
quello sulla posizione.**

### 4.3 La misura: autocorrelazione a un passo

$\rho_1 = \operatorname{Cov}(x_t, x_{t-1}) / (\sigma_{x_t}\sigma_{x_{t-1}})$.
Un segnale fisico vero cambia con continuità ed è molto correlato con sé stesso
da un fotogramma al successivo; un rumore bianco non lo è affatto.

| grandezza | ρ₁ |
|---|---:|
| *derivate istantanee* | |
| variazione dell'angolo del tronco | 0,176 |
| energia del corpo | 0,228 |
| velocità del bacino | 0,322 |
| velocità della testa | 0,438 |
| *grandezze integrali* | |
| escursione del tronco | **0,916** |
| percorso del bacino | **0,939** |
| discesa del bacino | **0,911** |

Le derivate stanno fra 0,18 e 0,44, le integrate fra 0,91 e 0,94. Le grandezze
statiche stanno attorno a 0,9: **nessuna scelta di α porta le derivate in
quell'intervallo.**

> **La precisazione che il relatore ha chiesto esplicitamente, ed è nel testo.**
> Un ρ₁ basso non dimostra da solo che una grandezza sia rumore, e uno alto non
> dimostra che sia informativa; una grandezza ottenuta integrando tende **per
> costruzione** a essere più regolare. L'autocorrelazione va usata come
> **spiegazione del fenomeno, non come sua dimostrazione**. La dimostrazione è il
> comportamento discriminativo, riportato nel capitolo dei risultati.
>
> Per questo l'autocorrelazione **resta nella metodologia**, declassata a
> `\paragraph`, invece di stare fra le misure.

### 4.4 Le tre grandezze, e che cosa NON fanno

$$\text{escursione}_t = \max_{\tau \in W}\theta_\tau - \min_{\tau \in W}\theta_\tau$$
$$\text{percorso}_t = \frac{1}{s}\sum_{\tau \in W}\sqrt{(x_\tau-x_{\tau-1})^2+(y_\tau-y_{\tau-1})^2}$$
$$\text{discesa}_t = \frac{1}{s}\Big(y_t - \min_{\tau \in W} y_\tau\Big)$$

con $W = \{t-K+1,\dots,t\}$. Nel codice: `_integrali` (`geometry.py:318-347`).
Rispondono a tre domande diverse: **di quanto il tronco ha ruotato in tutto**,
**quanta strada ha percorso il corpo**, **di quanto è sceso rispetto al punto
più alto raggiunto di recente**.

La normalizzazione $s$ è la lunghezza del tronco per A2 e A3, l'asse maggiore
dell'ellisse per A1: senza, il percorso sarebbe in pixel e dipenderebbe dalla
distanza dalla telecamera.

**Il punto seguito non è lo stesso nei tre bacini**, e il codice lo dichiara:
A1 il baricentro della nuvola, A3 il bacino nel piano immagine, **A2 il naso in
coordinate world** (dopo ISS-104).

#### L'argomento che sembra giusto ed è sbagliato

> Si sarebbe tentati di affermare che accumulando il rumore si cancella, poiché
> un errore a media nulla sommato su molti fotogrammi tende a zero.

**Vale per una somma di incrementi con segno, e queste tre non lo sono:**

- il **percorso** è una somma di valori assoluti, e i valori assoluti non si
  cancellano mai;
- l'**escursione** è max − min, e il rumore allarga l'intervallo;
- la **discesa** è uno scarto dal massimo recente, e il rumore abbassa il minimo.

**Tutte e tre sono funzioni monotone crescenti del rumore.** Ciò che le rende
preferibili alle derivate **non è la robustezza, è la regolarità**.

*(Nota storica: fino al 27 agosto la docstring di `src/geometry.py` conteneva
ancora la formulazione vecchia — «un accumulo lo cancella, perché il rumore a
media nulla si somma a zero» — cioè la terza sede in cui l'affermazione smentita
sopravviveva. È stata riscritta con l'argomento corretto, e la copia sulla board
riallineata: [ISS-119](../ISSUES.md#iss-119). Era una discordanza fra commento e
testo, non fra codice e testo — il calcolo era ed è lo stesso.)*

### 4.5 Fin dove regge: `pipeline/rumore.py`

Poiché le tre grandezze crescono con il rumore, va misurato quanto questo le
penalizzi. Lo script inietta rumore gaussiano indipendente sulle coordinate dei
landmark, con deviazione espressa in **frazione della lunghezza del torso**, e
rimisura.

| σ | senza integrali | con integrali | sottoinsieme scelto |
|---|---:|---:|---:|
| 0 | 0,874 | 0,858 | 0,857 |
| 0,005 | 0,863 | 0,864 | 0,844 |
| 0,010 | 0,855 | 0,866 | 0,863 |
| 0,020 | 0,864 | 0,846 | 0,836 |
| 0,040 | 0,863 | 0,856 | 0,825 |

**Il rumore indipendente non degrada apprezzabilmente nessuno dei tre insiemi**:
quadruplicando l'ampiezza rispetto a quella stimata sulle registrazioni
domestiche, la perdita massima è 0,031, inferiore alla dispersione fra soggetti
(±0,08). La spiegazione: un errore indipendente su ciascun punto e a ciascun
fotogramma si media comunque, anche attraverso una funzione monotona, perché
punti diversi sbagliano in direzioni diverse.

**La vulnerabilità vera è un'altra, e non è il rumore: è l'ambiguità di posa.**
In una ripresa domestica ravvicinata, con gli arti scorciati verso l'obiettivo,
lo stimatore non oscilla a caso: **alterna fra due interpretazioni plausibili**
della stessa configurazione, e ciascuna resta stabile per diversi fotogrammi.

| escursione del tronco su finestra mobile | mediana | massimo |
|---|---:|---:|
| persona **ferma** su un divano | 9,0° | **93,5°** |
| **caduta** reale | 9,0° | 60,7° |

**Una persona immobile produce un'escursione superiore a quella di una caduta.**
Per un accumulatore un salto coerente ripetuto è indistinguibile da un movimento
reale. La difesa non può essere un filtro — il segnale spurio è regolare quanto
quello vero — deve essere un **criterio di affidabilità della stima**: quando la
confidenza dei punti cade durante la finestra, il sistema deve **dichiarare** di
non poter decidere, come già fa durante il riscaldamento.

### 4.6 Vincolo di causalità: perché sono in `geometry.py` e non in uno script

Questa è la differenza fra un risultato e un sistema installabile.

Le formule si possono calcolare in due modi:

1. **`pandas.rolling()` su un CSV completo**, cioè a registrazione conclusa.
   Semplice, e produce gli stessi numeri per un'analisi fuori linea.
2. **Buffer circolare** degli ultimi K fotogrammi, aggiornato a ogni campione.
   Più laborioso, ed è l'unico compatibile con il dispositivo: **la board riceve
   un fotogramma e deve decidere, il video intero non ce l'ha.**

> Nel progetto precedente era il primo modo, **ed è la ragione per cui le
> grandezze integrali non sono mai arrivate sul dispositivo**: il sistema
> installato usava A3 a dieci colonne, e ogni risultato su A3i era un calcolo
> fuori linea.

Nell'implementazione attuale (`geometry.py:182`):

```python
self._buf = {b: deque(maxlen=self.K) for b in ('A1', 'A2', 'A3')}
```

I buffer si azzerano a ogni posa mancante — un accumulo che attraversa un buco
misurerebbe uno spostamento mai avvenuto.

**Costo: un ritardo di riscaldamento.** Con K = 31 a 18 fps sono ~1,7 secondi in
cui il buffer non è pieno e i valori non sono affidabili. Il sistema lo dichiara
a schermo invece di decidere (`deploy_board/rileva.py`).

**Dettaglio implementativo che vale la pena notare:** `MotoreGeometrico`
dichiara `K_PREDEFINITO = 31` *nel modulo* e non lo legge da `config`, perché il
file viene copiato tale e quale sulla board, dove `config.py` non esiste. Chi lo
usa dal progetto passa comunque `k_integrali` esplicitamente.

**La scelta di K = 31** non è arbitraria ed è misurata nel Capitolo 5: il
parametro sposta il tasso di falsi allarmi in ambiente reale di un **fattore
undici**. È il tipo di parametro che, non dichiarato, rende un risultato non
riproducibile.

---

## 5. L'altezza del bacino dal pavimento (A3h)

### Perché serve

A3 normalizza tutto rispetto al bacino, quindi cancella l'informazione su dove
il corpo si trovi nella stanza. Il modello apprende allora una regola posturale
— tronco orizzontale ⇒ caduta — corretta su un dataset in cui nessuno si sdraia
su un divano, sbagliata in un'abitazione.

**La misura rende la differenza quantitativa.** Fra i fotogrammi negativi in cui
il corpo è orizzontale, l'altezza mediana del bacino vale:

- **+0,02** lunghezze di torso nel dataset di laboratorio (la persona è *a
  terra*: sdraiarsi sul pavimento è una delle attività registrate);
- **+1,47** nelle registrazioni domestiche (la persona è su un supporto
  rialzato).

**La grandezza «corpo orizzontale» non distingue nulla nel primo insieme e
distingue tutto nel secondo.** È la frase su cui poggia l'intero Capitolo 5.

### Come viene stimata

Il piano del pavimento non lo fornisce nessuno: il sistema lo stima da sé,
osservando che **quando una persona è in piedi il bordo inferiore della sua
sagoma coincide con il pavimento a quella distanza dalla telecamera**.

1. si selezionano i fotogrammi in cui il soggetto è eretto — rapporto
   altezza/larghezza del riquadro sopra soglia, angolo del tronco prossimo alla
   verticale, posa valida;
2. si raccolgono le coppie (posizione orizzontale del bacino, bordo inferiore
   del riquadro);
3. si adatta la retta $y_{\text{pav}}(x) = ax + c$, che rappresenta il pavimento
   nell'immagine **prospettiva compresa** — in una ripresa non frontale il
   pavimento non è una riga orizzontale, e la pendenza $a$ ne tiene conto;
4. $h_{\text{pav}} = \dfrac{y_{\text{pav}}(x_{\text{bacino}}) - y_{\text{bacino}}}{L_{\text{tronco}}}$.

La normalizzazione la rende adimensionale e confrontabile fra stanze e
corporature. **Ciò che resta specifico dell'installazione sono solo $a$ e $c$, e
il sistema li stima senza chiedere nulla all'utente.**

### Un limite dipendente dal punto di vista, dichiarato

Funziona solo se la telecamera vede il pavimento come piano distinto dalla
posizione della persona, cioè se è **all'altezza del busto**. Separazione fra le
mediane di caduta e non-caduta:

- vista laterale: **+1,43** lunghezze di torso;
- vista frontale rialzata: **−0,18** — assente, e di segno opposto.

È quindi una grandezza **condizionata all'installazione**, e va dichiarata come
tale.

### Una conferma arrivata per altra via

Nell'esperimento sulle occlusioni, mascherare i landmark delle **anche** — cioè
il riferimento rispetto a cui A3 normalizza tutto — non peggiora il risultato ma
lo **migliora** di 0,012.

La spiegazione: con il bacino congelato in posizione fissa, l'altezza della
testa smette di essere misurata rispetto al bacino ed è misurata rispetto a un
punto fisso nella stanza — **A3 si trasforma di fatto in una rappresentazione
riferita all'ambiente**. Con telecamera fissa, un riferimento fisso è più
informativo di uno che si sposta insieme alla persona.

È la stessa informazione che $h_{\text{pav}}$ fornisce esplicitamente, ottenuta
per caso da un esperimento che aveva un altro scopo.

### La nomenclatura

**A3** = riferita al corpo, forma base. **A3h** = + altezza dal pavimento.
**A3i** = + terna integrale al posto delle derivate. Le due estensioni sono
indipendenti e possono comparire insieme.

Entrambe **sono nate dalla validazione in ambiente reale**, non da un'analisi di
laboratorio. Sono descritte fra le scelte di metodo perché è su di esse che
poggia la configurazione finale, e il capitolo che le ha rese necessarie
dichiara esplicitamente di esserne la causa.

---

## 6. Selezione delle grandezze con DTW

### 6.1 Perché il DTW

Il confronto avviene fra serie temporali di **durata e velocità diverse**: due
cadute possono avere la stessa struttura e svolgersi in tempi differenti, o
presentare il picco qualche fotogramma prima o dopo. Una distanza punto per
punto giudicherebbe diverse due curve identiche ma sfasate. Il DTW confronta la
**forma**, deformando l'asse dei tempi alla ricerca dell'allineamento di costo
minimo.

### 6.2 Le tre scelte, nessuna neutra

**Normalizzazione per curva (z-score).** Le grandezze hanno scale eterogenee; sui
valori grezzi la distanza sarebbe dominata da quelle di ampiezza maggiore. Si
perde l'ampiezza assoluta, accettabile perché qui interessa la forma.

**Vincolo sul cammino:** $|i-j| \le w$ con $w = 10$ fotogrammi. Un DTW libero può
deformare l'asse dei tempi al punto da far somigliare un'attività normale a una
caduta.

**Ricampionamento a lunghezza comune (200 campioni).** Deriva dalla precedente,
ed è [ISS-101](../ISSUES.md#iss-101) — il secondo difetto grave del progetto.

#### ISS-101 — il vincolo di warping si allargava da solo

Il codice faceva `window = max(finestra, abs(n - m))`. L'allargamento **è
necessario** — con $|n-m|$ maggiore della banda nessun cammino arriva in fondo —
ma su questo dataset produceva un effetto perverso:

| coppia | differenza di lunghezza | banda effettiva |
|---|---:|---:|
| caduta – caduta (~180 fotogrammi) | piccola | 10 |
| ADL – ADL (~820 fotogrammi) | piccola | 10 |
| **caduta – ADL** | ~640 | **630** |

**Le coppie che devono risultare distanti ricevevano la massima libertà di
deformazione.** $\mu_{FA}$ deflazionato, $\mu_{\text{intra}}$ intatto, tutti i
punteggi schiacciati verso 1.

**E l'effetto non era uniforme, ed è questa la parte grave**: colpiva
**selettivamente le grandezze integrali**, che sono curve lisce e sotto warping
libero si deformano l'una nell'altra a costo quasi nullo, mentre le posizionali
hanno un gradino netto che il warping non cancella. **Cinque delle nove
integrali risultavano sotto 1,0 e venivano scartate come rumore.**

Il difetto era *conservativo sui valori* ma **falsava l'ordine della
classifica**, che è esattamente ciò che serviva.

**Verifica su dati sintetici** con la stessa asimmetria di durata (8 curve da 180
con discesa netta contro 9 da 820 oscillanti):

| | μ_FA | μ_intra | punteggio |
|---|---:|---:|---:|
| senza ricampionamento | 0,0207 | 0,0041 | 5,055 |
| **con ricampionamento** | 0,0420 | 0,0058 | **7,201** |

Sui dati reali: nessuna grandezza resta sotto 1,0 (minimo 1,046), e le cinque
integrali risalgono di oltre +0,19. La run precedente
([EXP-004](../EXPERIMENTS.md#exp-004)) è stata **annullata**, e la sua classifica
conservata come `classifica_dtw_senza_ricampionamento.csv` per rendere il
confronto verificabile.

**Che cosa si perde: l'informazione di durata.** Ed è accettabile per una ragione
precisa: *la durata di una ripresa è identica per tutte e trentadue le
grandezze*, quindi non può contribuire a distinguerle fra loro, mentre il rumore
che introduce sì. Se la durata serve come discriminante, è una feature a sé e va
misurata a parte. → [DEC-102](../DECISIONS.md#dec-102)

### 6.3 Il punteggio di separabilità

Tre popolazioni di distanze: $D_{FF}$ (fra cadute), $D_{AA}$ (fra ADL), $D_{FA}$
(incrociate). Una grandezza discriminativa produce curve simili dentro la classe
e diverse fra classi:

$$S = \frac{\mu_{FA}}{\mu_{\text{intra}}+\varepsilon}, \qquad
S_{\text{rob}} = \frac{\mu_{FA}-\mu_{\text{intra}}}{\sigma_{FA}+\sigma_{\text{intra}}+\varepsilon}$$

$S = 1$ indica **assenza di separazione**. Il secondo tiene conto della
dispersione: un punteggio alto può derivare da valori anomali invece che da una
separazione reale.

### 6.4 Il criterio del minimo fra le due camere — DEC-101

L'analisi iniziale calcolava un punteggio unico mescolando le due telecamere.
Questa scelta **nasconde il divario più grande misurato in tutto il lavoro**: la
stessa grandezza che di profilo mostra **84 gradi** di escursione fra persona
eretta e distesa ne mostra **3** dall'alto.

$$S_{\text{robusto}} = \min\big(S_{\text{cam}_1}, S_{\text{cam}_2}\big)$$

**Il minimo e non la media**, perché una grandezza ottima da una vista e inutile
dall'altra è esattamente quella da escludere, e la media la premierebbe.

**Il costo è dichiarato:** `A1_asse_mag` fa 1,314 su cam2 — secondo miglior
punteggio dell'intera analisi su quella camera — ma 1,101 su cam1, ed esce. *È il
prezzo di un sistema che deve funzionare senza sapere come è stata montata la
telecamera.*

### 6.5 Il controllo della ridondanza — ISS-102 / DEC-103

Il DTW valuta ogni grandezza **isolatamente**: se lo stesso fenomeno fisico è
misurato in tre modi, lo premia tre volte. Sui dati reali, le prime dodici
contenevano cinque coppie con |r| > 0,80:

```
A2_testa_rel_y     A2_angolo_tronco     r = 0,972
A2_testa_rel_y     A3_testa_rel_y       r = 0,981
A2_angolo_tronco   A3_testa_rel_y       r = 0,946
A3_ginocchia_rel_y A3_caviglie_rel_y    r = 0,931
A3_escursione      A2_escursione        r = 0,852
```

Le prime tre sono la stessa cosa — **quanto è verticale il tronco** — e il legame
è geometrico: il tronco è un segmento rigido, quindi $\text{testa\_rel\_y}
\approx L\cos\theta$. Alla rete sarebbero arrivati circa **otto segnali
indipendenti travestiti da dodici**.

Difetto collaterale: fra il dodicesimo (1,163) e il tredicesimo (1,162) della
classifica c'era **un millesimo**. Sotto 1,16 l'ordine era un pareggio, non una
graduatoria, e tagliare a dodici secchi era arbitrario.

**Soluzione:** selezione avida — si scorre la classifica dall'alto e si aggiunge
una grandezza **solo se la sua correlazione assoluta con tutte le già scelte sta
sotto soglia**. Le escluse sono dichiarate con il nome di chi le blocca e il
valore di r.

**Perché 0,85:**

| soglia | corr. media fra le scelte | note |
|---|---:|---|
| prime 12 secche | 0,385 | 5 coppie sopra 0,80 |
| 0,90 | 0,393 | quasi nessun effetto |
| **0,85** | **0,325** | adottata |
| 0,75 | 0,240 | ammette grandezze molto più in basso in classifica |

**Su cosa si misura la correlazione:** solo sui fotogrammi con **posa valida** —
sugli altri tutte le grandezze valgono zero per costruzione e risulterebbero
correlate fra loro per un motivo che non ha nulla a che vedere con la dinamica.

### 6.6 Il sottoinsieme definitivo (EXP-008)

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
| 11 | `A3_hip_vel` | 1,160 | velocità |
| 12 | `A3_testa_vel_rel` | 1,157 | velocità |

**Nove integrali su dodici.** Escluse per ridondanza: `A2_angolo_tronco`
(r = 0,97), `A3_testa_rel_y` (0,98), `A2_escursione` (0,85),
`A3_caviglie_rel_y` (0,93).

Il file prodotto è `risultati/dtw/scelte.txt`, e **`src/dati.py:99-106` lo legge
da file invece di avere l'elenco copiato a mano** — così non può divergere
dall'analisi che lo ha prodotto.

### 6.7 I limiti dichiarati

- **È una preselezione euristica, non una dimostrazione.** Nessuna grandezza da
  sola separa le classi: i valori stanno fra 1,05 e 1,31 e 1,0 significa assenza
  di separazione. **L'arbitro è la LOSO sul modello.**
- **La selezione dipende dal campione.** Su un pilota a due soggetti
  ([EXP-002](../EXPERIMENTS.md#exp-002)) la classifica era sensibilmente diversa,
  e due grandezze che apparivano fra le migliori si rivelavano sotto soglia una
  volta esteso il campione. Le conclusioni di quella run **non vanno citate**:
  serviva a validare il codice, non a scegliere le grandezze.
- La correlazione media fra le scelte sale da 0,325 a 0,424 fra EXP-006 ed
  EXP-008: le due A2 riabilitate passano il filtro ma restano parenti delle
  altre. **È il prezzo di tre bacini che descrivono lo stesso corpo.**

---

## 7. Finestratura e definizione del compito

### 7.1 Lunghezza e sovrapposizione

$X_t = [f_t, f_{t+1}, \dots, f_{t+L-1}]$ con **L = 22 campioni a 9 fps = 2,44 s**
(`config.py:56-57`), **passo 2**.

**Da dove viene il 22.** È 45 diviso due, dove 45 era `SEQUENCE_LENGTH` nel
config del progetto precedente — un valore che in quel progetto esisteva in **tre
versioni contrastanti**: 45 in config, 75 in `demo_realtime.py`, **39** nei
metadati della run migliore. Nessuna delle tre era mai stata giustificata, né
confrontata con la durata dell'evento. Il 22 mantiene la stessa **durata** dei 45
a 18 fps, riportata alla frequenza di esercizio.

**L'ipotesi ragionevole ([ISS-105](../ISSUES.md#iss-105)) era che 2,44 s fosse
troppo poco**, dato che la caduta mediana dura 3,11 s. Verificata
([EXP-012](../EXPERIMENTS.md#exp-012)):

| campioni | durata | F2 | dispersione |
|---:|---:|---:|---:|
| 22 | 2,44 s | 0,847 | ±0,085 |
| 28 | 3,11 s | 0,838 | ±0,077 |
| 36 | 4,00 s | 0,817 | ±0,146 |
| 44 | 4,89 s | 0,881 | ±0,090 |

**Nessuna differenza significativa, andamento non monotono. L'ipotesi era
sbagliata.** Spiegazione probabile: la memoria effettiva non è la finestra —
ogni campione porta gli integrali accumulati su 31 fotogrammi, cioè 1,7 s di
storia in più; e due terzi dei positivi sono lo stato «a terra», che si riconosce
da una finestra corta quanto si vuole.

**ISS-105 si chiude come «misurata, nessun effetto», non come «corretta».** Da
valore ereditato, 22 diventa un valore verificato contro tre alternative.

**Il passo 2** serve perché una caduta può iniziare in un punto qualsiasi: con
finestre disgiunte l'evento potrebbe cadere a cavallo di due e non essere
contenuto per intero in nessuna. Introduce però una criticità — due finestre
consecutive condividono **venti campioni su ventidue** — che il Capitolo 4 tratta
due volte: nella divisione dei dati e nella stima dello scaler.

### 7.2 Tre compiti, non tre gradazioni

| compito | positivo | il sistema riconosce |
|---|---|---|
| **evento** | la finestra contiene la transizione | *l'atto* del cadere |
| **stato** | la finestra contiene la persona a terra | *la condizione* di essere caduti |
| **allarme** | l'una o l'altra | quando suonare |

**Il criterio clinico suggerirebbe il terzo, o il secondo** — il danno della
long-lie dipende dal tempo a terra, e lo stato dura molto più della transizione,
offrendo più occasioni di rilevamento. **Ed è la formulazione che il lavoro aveva
adottato inizialmente.**

#### Il negativo che rende la scelta non ovvia

In UP-Fall una delle attività registrate come normali è `act11 = laying`,
sdraiarsi volontariamente: **20.980 fotogrammi, il 18% dell'intero dataset,
etichettati 0**. Il dataset contiene quindi *ventimila fotogrammi di persona
distesa etichettati come normali e diecimila etichettati come post-caduta*.

**Nello stato finale i due casi sono quasi indistinguibili: la differenza sta
unicamente nel modo in cui la persona ci è arrivata.**

Verificabile quantitativamente, sui rapporti fra le mediane:

| grandezza | caduta / sdraiarsi | a terra / disteso |
|---|---:|---:|
| velocità del bacino | **30,1×** | 1,3× |
| escursione del tronco | **42,5×** | 2,8× |
| percorso del bacino | **33,0×** | 1,3× |
| discesa del bacino | **139,4×** | 2,1× |

> **La transizione discrimina; la posa no.** Nessuno si sdraia su un divano con
> un'escursione del tronco di trenta gradi in mezzo secondo. Lo stato finale è
> ambiguo per costruzione, la transizione no.

Da qui [DEC-107](../DECISIONS.md#dec-107): il positivo è l'**evento**.

**Cosa NON risolve, dichiarato:** una caduta fuori campo o durante un buco di
posa non produce transizione osservabile. Servirebbe una via lenta — altezza dal
pavimento, immobilità, durata — con tre condizioni congiunte. Il costo misurato è
**una caduta su cinque**, che con cinque cadute non è interpretabile ma ha la
direzione attesa.

### 7.3 Assegnazione dell'etichetta di finestra: il criterio K-su-M

La regola adottata inizialmente contava i fotogrammi della classe **ovunque
fossero** nella finestra: cinque fotogrammi di caduta sparsi valevano quanto
cinque consecutivi. Per un evento che è per natura una dinamica continua è
incoerente.

Sostituita dal criterio **K-su-M**: la finestra è positiva se

$$\max_i \sum_{t=i}^{i+M-1} m_t \ \ge\ K$$

Implementazione: `_blocco_k_su_m` in `src/etichettatura.py:54-73`, con somma
mobile calcolata sulla cumulata.

**Perché è elegante:** con M = K degenera in «K consecutivi stretti», con M molto
grande nel conteggio totale sulla finestra. **I due estremi sono casi particolari
dello stesso parametro**, quindi il confronto fra criteri è una variazione di
parametro invece che di codice.

**Valori:** K = 5 su M = 8 per la transizione, K = 10 su M = 15 per lo stato.
**Non sono ottimizzati**: sono soglie di preprocessing scelte per imporre una
presenza minima della fase nella finestra.

#### ISS-112 — le soglie erano dichiarate in due posti (risolta)

`config.py` dichiarava `CADUTA_MIN_FOTOGRAMMI = 5` e `TRANSIZIONE_MAX = 10`;
`src/etichettatura.py` aveva i propri default `k_caduta=5, m_blocco=8,
k_terra=10, m_terra=15`; **nessuno collegava i due**, e i chiamanti non passavano
nulla. `pipeline/addestra.py` scriveva però nel `run_metadata.json` i valori di
`config`:

> **Il file che serve a rendere una run rifacibile dichiarava parametri che non
> la governavano.** Le due ampiezze di blocco, che rendono il criterio «K su M»
> invece di «K totali», non erano registrate da nessuna parte.

**Intervento:** le quattro soglie stanno ora in `config.SOGLIE_ETICHETTATURA`
**con gli stessi nomi dei parametri della funzione**; `etichetta_finestra` le
legge da lì quando l'argomento è `None`; `addestra.py` registra il dizionario
intero. Comportamento invariato, verificato su sequenze costruite — che era il
requisito: la correzione non doveva cambiare alcun risultato già prodotto.

### 7.4 Le due etichette: il metro deve essere unico

È il cuore del confronto fra compiti, e sta in `src/dati.py:228-250`.

Se ciascun modello venisse misurato sulla propria definizione di positivo, il
confronto non sarebbe interpretabile: il compito *evento* **scarta le finestre di
stato, che sono le più ambigue**, e apparirebbe avvantaggiato per un motivo che
non ha nulla a che vedere con la sua qualità.

Ogni finestra porta quindi **due etichette**:

```python
e = etichetta_finestra(fin, modo, **soglie)          # y_train: la variabile
y_tr.append(-1 if e is None else e)                  #   dell'esperimento
y_al.append(int(etichetta_finestra(fin, 'caduta', **soglie) == 1))
                                                     # y_allarme: il metro comune
```

- **`y_train`** dipende dal modo (`scarta` | `caduta` | `tre_classi`);
- **`y_allarme`** è **fissa**: 1 se la finestra contiene la transizione *oppure*
  lo stato.

Le finestre che il modo `scarta` esclude **restano in X con `y_train = -1`**:
servono in verifica, dove tutti i modelli vanno misurati sullo stesso insieme.

I tre modi (`src/etichettatura.py:117-128`) e il loro costo:

| modo | che cosa fa | costo |
|---|---|---|
| `scarta` | butta le finestre di «a terra dopo caduta», tiene «sdraiato volontariamente» come negativo | perde il ~40–59% dei fotogrammi di caduta |
| `caduta` | mappa 2 → 1 | chiede di distinguere due immagini quasi identiche |
| `tre_classi` | tiene 2 separata | lascia decidere al modello, ma triplica lo spazio d'uscita su una classe rara |

### 7.5 Il vocabolario OmniFall — `pipeline/mappa_omnifall.py`

Le etichette originali non distinguono una persona distesa **dopo una caduta** da
una distesa **per scelta**: `act11 = laying` vale 0, esattamente come camminare.
Era il negativo difficile del progetto, e finora era misurabile solo sulle
registrazioni domestiche — che sono anche la fonte dei controesempi, quindi
contaminate — oppure su UR-Fall.

OmniFall ha riannotato a mano otto dataset, UP-Fall compreso, con sedici classi.
Quattro sono esattamente le distinzioni che servono:

```
fall      l'atto di cadere, da qualunque stato precedente
fallen    essere a terra DOPO una caduta
lie_down  sdraiarsi INTENZIONALMENTE
lying     essere disteso dopo esserci andato intenzionalmente
```

**Che cosa NON cambia: nulla della pipeline.** Gli autori distribuiscono solo le
annotazioni, non i video, quindi si applicano ai CSV di feature già estratti.

**Il vincolo di allineamento, verificato e non assunto:** i segmenti OmniFall
sono in **secondi**, i dati in **fotogrammi**. La conversione usa i 18 fps del
dataset, e lo script confronta la classe OmniFall con l'etichetta esistente
stampando la matrice di accordo — se l'allineamento fosse sbagliato di mezzo
secondo, `fall` e `fallen` non cadrebbero dove cadono le annotazioni originali.
**Copertura ottenuta: 96,4% dei fotogrammi**, con 21.322 distesi volontari resi
misurabili.

**Due conseguenze utili:** i negativi critici diventano misurabili *dentro* il
dataset di addestramento; e i risultati diventano confrontabili con un benchmark
pubblicato — OmniFall riporta, con un modello video da 87 milioni di parametri,
**F1 65,6% sull'evento e 41,0% sullo stato**. *Il divario evento-stato non è un
limite di questo lavoro: è un problema aperto del settore, e ha lo stesso segno.*

---

## 8. Il lavoro fatto sul testo di questo capitolo

### ISS-107 — era il capitolo più suddiviso della tesi

Misurato: **quarantanove titoli in 9.400 parole**, cioè un titolo ogni 185
parole. Il criterio del progetto è ~400.

Intervento del 26 agosto: **50 operazioni di declassamento e rinomina, nessun
testo cancellato** — la candidata ha chiesto che tutto ciò che è stato misurato
resti nella tesi, quindi si è agito solo sul livello dei titoli.

| | prima | dopo |
|---|---:|---:|
| sezioni | 10 | **7** |
| sottosezioni | 39 | **13** |
| parole per titolo | 185 | **453** |

Tre accorpamenti: il rumore dei landmark diventa sottosezione della stima di
posa; «B — coordinate scheletriche grezze», che contava novanta parole, è
assorbita fra le rappresentazioni; finestratura e definizione del compito, che
erano due sezioni consecutive, diventano una sola con tre sottosezioni.

**L'autocorrelazione resta nella metodologia**, declassata a `\paragraph`: era
prevista per il capitolo dei risultati, ma il relatore ha chiesto esplicitamente
di usarla come **spiegazione del fenomeno e non come prova**, quindi la sua sede
naturale è accanto alla motivazione delle grandezze integrali.

### ISS-109 — tre nomi per la stessa cosa (risolta)

Il codice usa `A1`; il Capitolo 3 usava `A1` nei titoli ma `A (PCA 2D)` nella
tabella dei landmark; il Capitolo 4 usava `A (PCA 2D)`. Adottato **`A1`
ovunque**, con la forma discorsiva dei titoli.

*Resta da sapere che la lettera al relatore del 17 agosto dichiarava «non esiste
un A1, il primo è semplicemente A». Se la nomenclatura torna in discussione, la
tesi usa `A1` e il codice pure.*
