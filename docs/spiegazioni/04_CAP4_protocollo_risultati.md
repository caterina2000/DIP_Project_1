# Capitolo 4 — Protocollo di valutazione e risultati sperimentali

**File:** `tesi/Cap4.tex` · **etichette:** `cap:risultati` + alias
`cap:protocollo`, `cap:sperimentale` · **9.110 parole**, 9 sezioni, 7
sottosezioni.
**Codice:** `src/dati.py`, `src/modelli.py`, `src/valutazione.py`,
`pipeline/addestra.py`, `pipeline/soglia.py`, `pipeline/confronto_compiti.py`,
`pipeline/occlusioni.py`, `pipeline/valuta_esterno.py`,
`pipeline/estrai_urfall.py`, `pipeline/rietichetta_urfall.py`.

Il capitolo nasce dalla **fusione** (26 agosto) del vecchio Capitolo 4
(protocollo) con il vecchio Capitolo 5 (risultati). Il protocollo da solo
contava 2.976 parole su ventidue titoli, **quattro dei quali erano una sezione
seguita immediatamente da un'altra sezione, senza testo proprio**. Non era un
capitolo: era il preambolo del capitolo seguente.

> Le tre etichette sono **alias e vanno tenute tutte**: una ventina di rimandi
> negli altri capitoli usa `cap:risultati`, altri `cap:protocollo`, e
> `cap:sperimentale` era già un alias. Toglierne una rompe i `\ref` senza dare
> in cambio niente.

**Perché protocollo e misure stanno insieme:** in un dominio con dieci soggetti e
classi sbilanciate il protocollo incide sul risultato più di qualunque scelta
architetturale — sugli **stessi identici dati e con lo stesso identico modello**
la differenza fra due protocolli vale il passaggio da un punteggio nullo a uno
utilizzabile.

L'ordine della seconda parte **non è cronologico ma argomentativo**: si parte
dalla prima configurazione difendibile, si individua la variabile che domina
tutte le altre, e si verifica in coda quanto sopravviva fuori dal dataset di
partenza.

---

## PARTE I — IL PROTOCOLLO

## 1. Sbilanciamento e scelta della metrica

### I numeri del problema

Sottoinsieme UP-Fall usato: **57.786 fotogrammi** della telecamera laterale, 109
riprese, 10 soggetti, posa valida sul **91,6%**.

| etichetta | significato | fotogrammi | quota |
|---|---|---:|---:|
| 0 | attività normale, pre-caduta | 49.691 | 86,0% |
| 1 | caduta in corso | 2.771 | 4,8% |
| 2 | soggetto a terra | 5.324 | 9,2% |

Dopo la finestratura: **11.510 finestre, di cui 1.423 positive (12,36%)**. I
positivi disponibili per la verifica variano **fra 76 e 171 a seconda del
soggetto** — è il primo segnale che *la persona su cui si misura pesa quanto il
metodo che si misura*.

E l'avvertenza subito dopo: **anche il 12,36% è enormemente superiore alla quota
di un impiego reale**, dove le cadute sono eventi rari nell'arco di mesi. È la
discrepanza che il Capitolo 5 quantifica.

### Perché l'accuratezza non è utilizzabile

Con l'87,64% di finestre negative, un classificatore che risponda sempre «non è
una caduta» **ottiene un'accuratezza superiore all'87% senza aver appreso nulla**.
Non è poco informativa: è **attivamente fuorviante**, perché premia il
comportamento degenere. Per questo ogni risultato viene confrontato con una
**baseline di maggioranza esplicita**.

### Perché $F_\beta$ con $\beta = 2$

$$F_\beta = (1+\beta^2)\frac{\text{precision}\cdot\text{recall}}{\beta^2\,\text{precision}+\text{recall}}$$

Un **falso negativo** è una caduta non rilevata — lo scenario della long-lie del
Capitolo 1. Un **falso positivo** è un allarme spurio: qualcuno accorre, non
trova nulla, e il costo è il disturbo. $F_1$ presuppone che si equivalgano; in
fall detection non si equivalgono. Con $\beta = 2$ il recall pesa il **quadruplo**.

Due precisazioni sull'uso, entrambe nel testo:

1. **β = 2 è stato dichiarato prima** di osservare i dati di verifica
   (`config.py:94`, `BETA = 2.0`), non scelto a posteriori fra i valori che
   davano il numero migliore;
2. **$F_2$ resta una sintesi, e in alcune circostanze nasconde ciò che dovrebbe
   mostrare.** Più avanti nel capitolo si incontra un caso in cui $F_2$ varia
   entro la dispersione fra fold mentre il recall cala di quattro punti e le
   cadute non rilevate raddoppiano: la precision compensa. **Per questo recall,
   FN e FP sono riportati sempre in chiaro accanto a $F_2$, e nessuna decisione
   del lavoro è presa sulla sola sintesi.**

### Riequilibrio delle classi

Pesi inversamente proporzionali alla frequenza, calcolati **sul solo insieme di
addestramento di ciascun fold** e registrati nei metadati
(`src/modelli.py:62-77`, normalizzati a media 1 così che la perdita resti sulla
stessa scala fra modi a due e a tre classi).

Il sottocampionamento della maggioritaria è stato **scartato**: con 1.423
finestre positive su 11.510, ridurre le negative allo stesso numero avrebbe
scartato circa il 75% dei dati, in un contesto dove il numero di soggetti è già
il vincolo dominante.

---

## 2. Partizionamento dei dati e LOSO

### Il difetto, e perché era invisibile

L'impostazione iniziale ripartiva i dati sulla base dell'identificativo della
**ripresa**. Ogni soggetto compare però in più riprese: uno split che separa le
riprese ma non le persone colloca lo stesso individuo su entrambi i lati.

**La misura non lascia margini: con lo split per ripresa, tutti e cinque i
soggetti risultavano contemporaneamente in addestramento e in verifica. Il
subject leakage non era parziale, era totale.**

L'effetto è quello descritto da Scheurer et al.: il modello impara corporatura,
andatura e abitudini posturali degli individui che dovrà poi riconoscere, e la
metrica risponde alla domanda *«quanto è bravo su persone che ha già visto»*.

### Il controllo che non poteva fallire

Vale la pena riportarlo perché illustra un modo di sbagliare che nessun test
automatico intercetta.

> Il codice conteneva un controllo esplicito contro il leakage, che sollevava
> un'eccezione se addestramento e verifica avessero condiviso dei dati. **Non è
> mai scattato — e non poteva**: verificava la sovrapposizione degli
> identificativi di *ripresa*, che per costruzione dello split erano sempre
> disgiunti, mentre la grandezza da controllare era il *soggetto*.
>
> **Un controllo che non può fallire non è un controllo: è una rassicurazione.**
> La sua presenza aveva anzi reso più difficile sospettare del problema, perché
> sembrava già escluso.

### La correzione: leave-one-subject-out a dieci fold

`src/dati.py:274-307`. In ciascun fold: **un soggetto in verifica, un secondo in
validazione, gli otto rimanenti in addestramento**. Il validation è il soggetto
successivo in ordine circolare — così i tre insiemi restano disgiunti per persona
senza doverlo scegliere a mano.

| fold (verifica) | validazione | finestre train | cadute nel test |
|---|---|---:|---:|
| Subject_01 | 2 | 9.120 | 121 |
| Subject_02 | 3 | 9.139 | 155 |
| Subject_03 | 4 | 9.170 | 140 |
| Subject_04 | 5 | 9.410 | **76** |
| Subject_05 | 6 | 9.530 | 142 |
| Subject_06 | 7 | 9.375 | 135 |
| Subject_07 | 8 | 9.154 | 167 |
| Subject_08 | 9 | 9.014 | 167 |
| Subject_09 | 10 | 9.066 | **171** |
| Subject_10 | 1 | 9.102 | 149 |

Costa dieci addestramenti invece di uno, ma è l'unico protocollo che restituisca
una stima interpretabile: uno split singolo produrrebbe un numero il cui valore
dipende in modo determinante da *quale* soggetto sia finito nella verifica.

### La statistica rilevante è la dispersione, non la media

Condiziona la lettura di tutto ciò che segue:

> La deviazione standard fra fold **non è una nota a margine della media**: è la
> misura di quanto il risultato dipenda da chi capita nella verifica. In queste
> run sta fra **±0,05 e ±0,14**, dello stesso ordine di molte differenze che si
> vorrebbero confrontare. **Raddoppiare i soggetti da cinque a dieci non l'ha
> ridotta in modo apprezzabile**, il che è di per sé un risultato: non è rumore
> di campionamento che si media via, è differenza fra persone.

**Conseguenza operativa applicata con coerenza in tutto il capitolo:** una
differenza di due o tre centesimi fra due configurazioni **non è una
differenza**, ed è più corretto dichiararle indistinguibili che proclamare un
vincitore — anche quando porta a rinunciare a conclusioni che i numeri grezzi
sembrerebbero autorizzare.

---

## 3. Normalizzazione e soglia: due parametri stimati sull'insieme sbagliato

### 3.1 Lo scaler

**La causa accertata dell'F1 = 0,0000.** Il vettore comprendeva angoli in gradi,
rapporti adimensionali prossimi all'unità ed energie cinetiche, e il rapporto fra
le deviazioni standard raggiungeva **646**: `energy` aveva media 11,58 e massimo
15.499, mentre altre variabili oscillavano attorno a 1.

Senza normalizzazione **la discesa del gradiente è dominata dalla variabile di
scala maggiore**: le altre nove contribuiscono in modo trascurabile.

**Due dettagli che non sono dettagli**, entrambi implementati in
`src/dati.py:149-175` e `301`:

1. **La stima avviene sul solo addestramento.** Media e deviazione sono calcolate
   esclusivamente sui soggetti di train del fold e poi applicate invariate a
   validation e test. Stimarle sull'intero dataset sarebbe leakage sottile ma
   reale.
2. **La stima avviene sui *fotogrammi*, non sulle *finestre*.** È l'aspetto meno
   evidente: con passo 2 su finestre da 22, **ogni fotogramma compare in circa
   undici finestre**, e stimare sulle finestre lo peserebbe undici volte — con un
   peso che per giunta varia agli estremi di ciascuna ripresa. Nel codice:
   `Scaler(colonne).fit(df[df[COL_SOGGETTO].isin(train)])`, cioè sulla tabella
   dei fotogrammi.

**Trasformazione logaritmica sulle code lunghe.** Alle grandezze non negative
fortemente asimmetriche si applica $\mathrm{sgn}(x)\log(1+|x|)$ prima della
standardizzazione. Il criterio **non è a occhio**: sono le colonne non negative
il cui rapporto fra 99,9-esimo percentile e mediana supera 10, misurato su
109.746 fotogrammi con posa valida (`src/dati.py:109-130`):

```
A3_discesa 908×   A1_discesa 550×   A3_hip_vel 292×   A3_testa_vel_rel 228×
A3_percorso 137×  A1_escursione 111× A2_vel_ang_tronco 105× A3_escursione 96×
A1_percorso 90×   A2_testa_vel 56×  A2_escursione 30×  A3_larghezza 9,6× (al limite)
```

Restano fuori `A1_asse_mag`, `A1_asse_min`, `A3_torso_len`, `A1_allungamento`
(fra 2,5× e 5,2×). **Le grandezze con segno — angoli, derivate, velocità
proiettate — non possono passare per log1p e non ci passano.**

**Effetto misurato:** il rapporto fra le scale passa da **646 a 1,05–1,35**, i
soggetti condivisi da 10 su 10 a **zero**, e $F_1$ da **0,0000 a 0,234**, con
**144 veri positivi contro nessuno**.

**Lo scaler è parte del modello.** I parametri vengono salvati insieme al modello
e distribuiti con esso, perché in inferenza le feature devono attraversare
esattamente la stessa catena. E il rischio è che l'omissione avvenga **in
silenzio**: un vettore non normalizzato ha la stessa forma di uno normalizzato,
il classificatore lo accetta e restituisce una probabilità **che semplicemente
non significa nulla**. Per questo il pacchetto distribuito include
`parita.npz` — 200 finestre con le predizioni attese, ricontrollate prima di
ogni impiego.

### 3.2 La soglia

**Il difetto iniziale erano due difetti distinti:** la soglia valeva 0,5 in un
modulo, 0,7 in un altro, ed era oggetto di esplorazione manuale in un terzo.
Sceglierla osservando la verifica è **leakage**; fissarla arbitrariamente rende
le configurazioni **non confrontabili**, perché ciascuna viene valutata in un
punto diverso della propria curva.

**Prima correzione:** sceglierla **sul validation** massimizzando $F_2$, e
applicarla **una sola volta** alla verifica (`src/valutazione.py:88-104`,
`pipeline/addestra.py:105-108`). Soglia e criterio registrati nei metadati.

**Questa correzione si è rivelata insufficiente**, ed è
[EXP-009](../EXPERIMENTS.md#exp-009): le soglie scelte per fold sono state

```
0,01 · 0,02 · 0,22 · 0,43 · 0,71 · 0,75 · 0,90 · 0,94 · 0,95 · 0,99
```

cioè **quasi tutto l'intervallo utile, con deviazione standard 0,37 su [0,1]**.
Riletti in termini di quota di finestre su cui il sistema suona:

| quota di allarme | fold | F2 |
|---|---|---|
| vicina alla prevalenza (12–15%) | 01, 05, 06, 09, 10 | **0,88 – 0,95** |
| due volte e mezzo (25–31%) | 02, 03, 04, 08 | 0,64 – 0,80 |
| troppo bassa (10,3%) | 07 | 0,72 |

**Non è il modello a variare fra i soggetti: è la soglia.**

### 3.3 Sei regole a confronto — EXP-010

Poiché la soglia è a tutti gli effetti un iperparametro, la domanda si è potuta
porre in forma sperimentale. **Le probabilità per fold erano già state salvate**
(`punteggi_*.npz`, `pipeline/addestra.py:172-182`), quindi il confronto **non ha
richiesto alcun riaddestramento**: costa secondi invece di sei ore.
Script: `pipeline/soglia.py`.

| regola | F2 medio ± dev | recall | soglia media ± dev | scarto di trasferimento |
|---|---:|---:|---:|---:|
| massimo $F_\beta$ sul validation | 0,810 ± 0,117 | 0,908 | 0,59 ± 0,37 | 0,094 |
| massimo $F_1$ | 0,790 ± 0,120 | 0,851 | 0,70 ± 0,34 | **0,068** |
| indice di Youden | 0,808 ± 0,117 | 0,910 | 0,59 ± 0,37 | 0,096 |
| pari alla prevalenza | 0,787 ± 0,116 | 0,858 | 0,68 ± 0,35 | 0,076 |
| prevalenza maggiorata (×1,5) | 0,823 ± 0,136 | **0,972** | 0,43 ± 0,31 | 0,106 |
| **fissa a 0,50, a priori** | **0,851 ± 0,078** | 0,926 | 0,50 ± 0,00 | 0,080 |

**Vince non scegliere.** La soglia fissa dà l'$F_2$ più alto **e** la dispersione
più bassa. Tutte le regole adattive fanno peggio.

**Perché:** stimare la soglia da un solo soggetto di validazione introduce una
variabilità di 0,37; una soglia dichiarata a priori ha variabilità **nulla per
costruzione**. *Quando la quantità di rumore che una stima aggiunge supera
l'adattamento che porta, non stimare è la scelta migliore* — caso particolare
del principio che il numero di parametri stimabili è vincolato dalla quantità di
dati indipendenti disponibili.

### L'avvertenza che conta più del risultato — DEC-105

> Confrontare sei regole sui fold di verifica e sceglierne una è, formalmente,
> **selezione sull'insieme di verifica**. Il valore 0,851 non è quindi una stima
> imparziale, e non viene riportato come tale.
>
> Ciò che si può portare avanti **non** è «0,50 è la soglia migliore», che
> sarebbe una conclusione sui dati di verifica. È **«scegliere la soglia su un
> solo soggetto di validazione è una procedura dannosa»**, che è una conclusione
> sulla *procedura* e regge indipendentemente da quale valore fisso si adotti.
> Da lì la scelta a priori difendibile è una soglia costante, perché non stima
> nulla e quindi non può sovradattarsi.

**Perché serve anche per il confronto fra architetture:** con la soglia scelta
per fold, la differenza fra GRU e LSTM resterebbe sepolta sotto il rumore della
taratura — la dispersione della soglia è dello stesso ordine delle differenze da
misurare. Con la soglia fissa, **ciò che si misura è il modello**.

**Ciò che nessuna soglia risolve:** anche a soglia fissa la quota di finestre in
allarme varia da **5,5% a 34,7%** a seconda del soggetto, mentre i positivi veri
stanno fra 6,7% e 14,9%. La distribuzione dei punteggi si sposta da persona a
persona: è **domain shift fra individui**, e non si corregge scegliendo un
numero. Si affronta tarando sulle registrazioni dell'ambiente di installazione.

### 3.4 Tracciabilità: il `run_metadata.json`

`pipeline/addestra.py:134-162`. Ogni esecuzione produce un descrittore con:
feature set, lunghezza e passo della finestra, `frame_step`, fps, `k_integrali`,
**le quattro soglie di etichettatura**, tipo di split, soggetti assegnati a
ciascun insieme, descrizione dello scaler, pesi delle classi, **soglia adottata e
criterio con cui è stata scelta**, conteggi per classe, metriche per fold, seme,
versione di Python, durata.

> L'ultimo campo è quello che rende utili gli altri. **Una soglia registrata
> senza il criterio che l'ha prodotta non è riproducibile**: non si distingue una
> scelta compiuta sul validation da una compiuta guardando la verifica, e la
> differenza fra le due è precisamente ciò che questo capitolo ha inteso
> stabilire.

---

## PARTE II — LE MISURE

## 4. Effetto congiunto delle correzioni al protocollo

| | prima | dopo |
|---|---:|---:|
| $F_1$ | 0,0000 | **0,234** |
| veri positivi | 0 | **144** |
| rapporto fra le scale | 646× | 1,05–1,35× |
| soggetti condivisi fra i due insiemi | 5 su 5 | **zero** |

**Resta un risultato modesto, e va detto**: 0,234 è lontano da qualunque soglia
di utilizzabilità. Il capitolo spiega perché, e **la risposta non è nel modello**.

---

## 5. Effetto della geometria di ripresa — la variabile che domina

> **Provenienza:** impianto a **cinque** soggetti, non ripetuto su dieci. È
> riportata perché la conclusione è di un ordine di grandezza superiore alla
> dispersione fra soggetti e nessun riallineamento può ribaltarla; i valori
> assoluti vanno letti come indicativi.

UP-Fall riprende ogni evento con **due telecamere sincronizzate**: cam1 laterale
all'altezza del busto, cam2 frontale rialzata. **Stesso soggetto, stessa caduta,
stesso istante — cambia soltanto il punto da cui si guarda.** È una condizione
che nessun'altra misura del capitolo può avere, e rende il degrado attribuibile
con certezza a una sola causa.

### La causa è ottica

L'indicatore geometrico più forte di una caduta è la variazione dell'inclinazione
del tronco, ma è osservabile solo se il piano di proiezione la conserva.

| | Camera1 (laterale) | Camera2 (frontale alta) |
|---|---:|---:|
| escursione media dell'angolo del tronco | 71,0° | 35,7° |
| sequenze con escursione sopra 60° | **18 su 25** | 6 su 25 |

Rapporto fra le medie: **1,99×**. Ma **va preferito il conteggio al rapporto**,
per una ragione che il dato stesso impone: le deviazioni standard (25,8 e 24,9)
valgono più di un terzo del valore medio, e il rapporto per sequenza spazia da
**0,39× a 6,21×** — in **2 sequenze su 25** Camera2 osserva quanto o più di
Camera1. Il fenomeno è reale e sistematico, ma molto variabile.

#### ISS-111 — quattro valori discordanti in due paragrafi (risolta il 26 agosto)

Il capitolo dichiarava **1,90×** e «tre sequenze su 24»; il file indicato come
sorgente diceva altro. Rileggendo, i valori discordanti non erano due ma
**quattro**:

| affermazione nel testo | valore dal file |
|---|---|
| medie 71,0 / 35,7 gradi | corretto |
| 18 su 25 e 6 su 25 sopra i 60° | corretto |
| rapporto delle medie 1,99 | corretto |
| deviazioni 25,3 e 24,4 | **25,8 e 24,9** |
| rapporto per sequenza da 0,33 a 13,22 | **da 0,39 a 6,21** |
| «in 3 casi su 24» | **2 su 25** |
| «rieseguendo si ottiene 1,90» | **1,99** |

E il paragrafo che doveva *correggere* il valore preliminare di **4,32×** ne
dichiarava uno diverso da quello riportato dodici righe sopra, dicendo «il valore
di riferimento è quello riportato sopra».

**Intervento:** i quattro valori riportati a quelli calcolati da
`risultati/cinque_soggetti/exp013_camera_viewpoint.csv`. La menzione di una
«misura indipendente che conferma 1,90» è stata **ritirata**: non è verificabile.
Con il testo allineato, `fig_viewpoint_dist.png` è stata inserita.

*(Il 4,32× originale proveniva da cinque sequenze di un solo soggetto. La
correzione **dimezza l'effetto dichiarato senza toccarne la direzione**.)*

### Quanto costa in accuratezza

Ripetendo l'esperimento della baseline sulla sola Camera1, a parità di tutto il
resto, **l'F2 passa da 0,29 a 0,857**. *Il difetto principale della baseline non
era il modello: era che metà dei dati proveniva da un punto di vista che non
contiene l'informazione cercata.*

### Il trasferimento fra viste, e la sua cura

| addestrata su | verificata su | F2 | falsi positivi |
|---|---|---:|---:|
| Camera1 | Camera1 | 0,872 ± 0,099 | — |
| Camera1 | Camera2 | **0,434 ± 0,182** | 1.113 |
| **Camera1 + Camera2** | Camera2 | **0,678 ± 0,123** | **460** |

Il cambio di inquadratura costa **metà dell'accuratezza**. Ma il dato che conta è
la terza riga: **esporre il modello a due punti di vista in addestramento ne
recupera il 58%**, e lo fa migliorando **insieme** recall (0,649 → 0,814) e
precision (0,216 → 0,543).

> Il miglioramento simultaneo delle due grandezze è **ciò che distingue un
> apprendimento più generale da uno spostamento di soglia**: una soglia scambia
> recall e precision, non le alza entrambe.

Anche la dispersione si stringe da ±0,182 a ±0,123: la fragilità non era solo
media, era **irregolare** — su due soggetti su cinque la versione a vista singola
scendeva a 0,28.

**Il risultato controintuitivo:** un modello addestrato su Camera1 e verificato
su Camera2 batte di **2,5×** un modello addestrato *direttamente* su Camera2,
sullo stesso identico insieme di verifica. **La qualità del punto di vista in
addestramento conta più della sua corrispondenza con quello di esercizio.**

---

## 6. Confronto fra rappresentazioni e fra architetture

### 6.1 Le rappresentazioni

A cinque soggetti (con riserva):

| rappresentazione | F2 | recall |
|---|---:|---:|
| A2 — tridimensionali | 0,867 ± 0,099 | — |
| A3 — riferiti al corpo | 0,857 ± 0,088 | **0,929** |
| A1 — sagoma | 0,834 ± 0,121 | — |

**Il risultato da riportare non è «A2 vince».** Scarto fra migliore e peggiore:
0,033, dentro deviazioni fra 0,088 e 0,121. **Le tre differenze non sono
distinguibili.**

**Due riserve dichiarate.** La prima è la provenienza (cinque soggetti). La
seconda è più seria: **A2 conteneva due grandezze degeneri per costruzione**
(ISS-104), quindi il suo punteggio è stato ottenuto con otto grandezze utili su
dieci.

Ripetuto su dieci soggetti dopo la correzione del motore:

| rappresentazione | $F_2$ |
|---|---:|
| A3 senza integrali | 0,874 ± 0,080 |
| A3 con integrali | 0,858 ± 0,075 |
| sottoinsieme DTW | 0,857 ± 0,078 |

**Diciassette millesimi separano la prima dall'ultima, contro dispersioni di
ottanta.** In laboratorio restano indistinguibili anche con il doppio dei
soggetti — **ed è un risultato che il Capitolo 5 ribalta**, perché in una casa la
stessa scelta divide i falsi allarmi per quattordici.

Ciò che invece esce dal rumore: **tutte e tre migliorano di 2,5–3,4 volte
cambiando telecamera.** *Il punto di vista conta più della rappresentazione — e
questo confronto, preso da solo, avrebbe suggerito di investire nella direzione
sbagliata.*

**Perché comunque A3.** Un criterio secondario: ha il **recall più alto**
(0,929) e il numero più basso di falsi negativi (17). In un sistema di sicurezza
il falso negativo è l'errore che pesa. *(Le altre due ragioni, dalla lettera al
relatore: A2 usa l'angolo del tronco 3D, che sulla Camera2 riporta 135 gradi dove
nell'immagine se ne osservano 31; e A3 è l'unica producibile anche da YOLOv8, che
fornisce solo punti 2D — scegliendo A3 il confronto fra stimatori resta
possibile.)*

### 6.2 Le architetture — la domanda da cui il progetto era partito

L'ipotesi esplicita era: *una rete ricorrente compatta svolge lo stesso lavoro
consumando meno risorse*. Il confronto impiega **la stessa rappresentazione, la
stessa lunghezza di finestra, lo stesso protocollo di divisione, la stessa
normalizzazione e la stessa soglia dichiarata a priori. Varia soltanto il
modello.**

Questo è il motivo per cui `src/modelli.py` espone **un'interfaccia unica**
(`.addestra`, `.probabilita`, `.n_parametri`): se ogni modello avesse il suo
ciclo, ogni differenza misurata potrebbe venire dal ciclo invece che
dall'architettura.

| modello | $F_2$ | recall | FN | FP | parametri | addestr. |
|---|---:|---:|---:|---:|---:|---:|
| LSTM | **0,858 ± 0,082** | 0,934 | 102 | 807 | 32.227 | 16,6 min |
| GRU | 0,847 ± 0,085 | 0,928 | 105 | 885 | 24.483 | 22,7 min |
| Transformer | 0,846 ± 0,100 | **0,939** | **89** | 1.028 | 34.499 | 11,5 min |
| CNN 1D | 0,833 ± 0,118 | 0,937 | 95 | 1.161 | 46.147 | 11,1 min |
| Foresta casuale | 0,792 ± 0,080 | 0,807 | 271 | **421** | — | **0,2 min** |

Confronto appaiato contro la GRU, fold per fold:

```
lstm          +0,011   vince 6/10   t = +0,84
transformer   −0,002   vince 4/10   t = −0,08
cnn           −0,014   vince 5/10   t = −0,60
foresta       −0,055   vince 3/10   t = −1,74      (serve |t| > 2,26)
```

**Fra la migliore e la peggiore corrono 0,066; la dispersione fra soggetti della
migliore è 0,082. La differenza fra due architetture è più piccola della
differenza fra due persone.**

**Il numero di parametri non ordina il risultato.** La CNN, con quasi il doppio
dei parametri della GRU, è penultima e ha la dispersione più alta; il Transformer
ottiene lo stesso $F_2$ della GRU con il minor numero di falsi negativi.

**La foresta si stacca in una direzione istruttiva:** perde 0,066 di $F_2$ e più
che raddoppia i falsi negativi, ma **dimezza i falsi allarmi** rispetto a ogni
rete. Non è un modello peggiore, è un modello con **un altro punto di
funzionamento** — ed è il motivo per cui è quello installato, dove il costo di un
falso allarme non è una riga in una tabella ma un sistema che viene spento.

#### Dettagli di implementazione che rendono il confronto onesto

- **Arresto anticipato sull'AUC della probabilità di allarme**, non sulla perdita
  né sull'accuratezza (`src/modelli.py:83-102`, `144-171`). La ragione: la soglia
  si sceglie *dopo*, quindi dall'addestramento serve un modello che **ordini**
  bene, non che decida bene a 0,5. Con positivi al 15% l'accuratezza premierebbe
  chi dice sempre «normale».
- **Uscita sempre softmax su `n_classi` colonne**, anche nel caso binario dove
  basterebbe un sigmoide, così `probabilita_allarme` riceve sempre la stessa
  forma e la riduzione è una riga sola per tutti
  (`src/valutazione.py:41-61`): binario → colonna 1, ternario → $1-p(\text{classe }0)$.
- **Cambia solo l'ultimo strato** fra 2 e 3 classi: tutto il resto
  dell'architettura è identico, altrimenti il confronto fra modi misurerebbe
  anche una differenza di capacità.
- **La foresta riassume la finestra con sei statistiche per grandezza** — media,
  dev.std, min, max, **primo e ultimo campione** (`src/modelli.py:299-306`). Il
  primo e l'ultimo ci sono perché senza di loro la foresta non saprebbe **in che
  verso** è andato il movimento, e una caduta e un rialzarsi darebbero lo stesso
  riassunto. Ed è un **parametro** (`estremi=False`) proprio perché è la variabile
  dell'esperimento sul ruolo degli integrali.

### 6.3 Modalità di etichettatura, stesso modello

```
caduta      0,854 ±0,077     scarta contro tre_classi:  −0,309   t = −6,85
tre_classi  0,847 ±0,085     caduta contro tre_classi:  +0,007   t = +0,33
scarta      0,538 ±0,137
```

**Una scelta di rappresentazione del problema produce un effetto ventotto volte
più grande della scelta fra tutte le architetture messe insieme.**

### 6.4 Analisi di numerosità campionaria — EXP-013

Il confronto è **appaiato** (ogni architettura valutata sugli stessi dieci
soggetti), il che permette di calcolare per ciascuna coppia la numerosità
necessaria a rilevare la differenza osservata con potenza dell'80% e α = 5%.

| confronto | differenza | dev. diff | $t$ (n=10) | soggetti necessari |
|---|---:|---:|---:|---:|
| **modo `scarta` contro `tre_classi`** | −0,309 | 0,143 | −6,85 | **2** |
| GRU contro foresta | −0,055 | 0,100 | −1,74 | 26 |
| integrali, foresta con estremi | −0,022 | 0,045 | −1,53 | 34 |
| finestra 22 contro 44 | +0,033 | 0,086 | +1,23 | 52 |
| integrali, foresta senza estremi | +0,039 | 0,117 | +1,06 | 70 |
| **GRU contro LSTM** | +0,011 | 0,042 | +0,84 | **113** |
| integrali sulla GRU | +0,016 | 0,096 | +0,54 | 274 |

**Distinguere una GRU da una LSTM richiederebbe 113 soggetti; distinguere due
definizioni del compito ne richiede 2. Un fattore cinquantasei fra le due
domande.** UP-Fall ne contiene diciassette in tutto, e nessun archivio pubblico
di cadute si avvicina ai centotredici.

### 6.5 Due ablation precedenti, e perché la loro discordanza è il risultato

Prima del passaggio a dieci soggetti, lo stesso confronto era stato condotto due
volte su cinque, con configurazioni leggermente diverse. **La prima assegnava
alla GRU 0,779 e la collocava ultima**, dietro la foresta di 0,108; **la seconda
le assegnava 0,873 e la collocava seconda**, a due centesimi dalla LSTM.

> La tentazione sarebbe di scartarle come misure superate. È invece opportuno
> riportarle, perché la loro discordanza dice qualcosa che nessuna delle due dice
> da sola: **con cinque soggetti, l'ordinamento fra architetture dipende da quale
> configurazione si scelga.**
>
> La conclusione della prima ablation — «la GRU non fa lo stesso lavoro, ed è la
> più costosa» — **non è sopravvissuta al raddoppio dei soggetti. Quella
> conclusione era stata scritta, e sarebbe finita in questa tesi. Ciò che
> l'ha impedita non è stato un ripensamento, ma il fatto di avere misurato la
> dispersione accanto alla media, e di avere trovato che la seconda era più
> piccola della prima.**

*(Nella lettera al relatore la candidata ha poi ritirato anche l'interpretazione
che ne aveva dato: quel 0,779 non era confrontabile perché veniva da A2 invece
che A3 e da una finestra lunga il doppio. Cambiavano tre variabili, non una.)*

### 6.6 Che cosa se ne conclude

> **Non è che una rete leggera regga il confronto con una pesante — è che
> l'architettura non è la variabile che decide.**

| confronto | ampiezza |
|---|---:|
| fra la migliore e la peggiore architettura | 0,066 |
| fra due definizioni del compito | 0,127 (statisticamente netta) |
| **fra due punti di vista della telecamera** | **0,422** |

**Limiti dichiarati:** nessuna ricerca sistematica di iperparametri — le
architetture sono confrontate nella configurazione in cui sono state definite.
Data la dimensione degli scarti rispetto alla dispersione è però improbabile che
un'ottimizzazione possa renderli distinguibili. Sull'approccio non supervisionato
(autoencoder + classificatore) l'unico dato disponibile viene da un'esecuzione in
cui i due metodi erano valutati **su verità di riferimento diverse**: va citato
come lavoro preliminare, non come confronto.

---

## 7. Analisi di sensibilità — tre controlli che chiudono altrettante domande

> **Due delle tre** — dimensione del modello e frequenza dei fotogrammi —
> risalgono all'impianto a **cinque** soggetti. La terza, la degradazione al
> mascheramento dei landmark, è misurata sui **dieci**, con validazione
> incrociata a dieci fold.
>
> *(Fino al 27 agosto la nota diceva «tutte e tre», e contraddiceva la
> didascalia della figura che sta nella stessa sezione: è
> [ISS-121](../ISSUES.md#iss-121). È il rovescio del difetto solito — di norma
> un numero vecchio si spaccia per nuovo, qui un numero buono si dichiarava
> vecchio.)*
>
> Nessuno dei tre apre un filone e nessuno produce il risultato principale.
> Servono a stabilire che quelle tre scelte non stiano determinando ciò che si
> osserva — **una conclusione utile soltanto se il controllo viene effettivamente
> eseguito, e priva di valore se viene assunta.**

### Dimensione del modello

La foresta installata usa cinquanta alberi, valore ereditato dal prototipo. Sei
dimensioni fra 10 e 400 alberi:

| alberi | F2 | falsi negativi | latenza |
|---:|---:|---:|---:|
| **50** | **0,906** | **15** | **4,47 ms** |
| 200 | 0,888 | 19 | 17,98 ms |

**Il modello più piccolo è migliore *e* quattro volte più veloce.** Con 4.990
finestre e 223 positivi, 200 alberi hanno capacità sufficiente per **memorizzare
la variabilità individuale** invece della struttura comune dell'evento.

Lo conferma la dispersione fra fold, che **cresce in modo monotono da
venticinque alberi in su**: 0,028 · 0,040 · 0,041 · 0,050 · 0,051. *I modelli
grandi non sono solo meno accurati su questi dati — sono anche i meno stabili fra
soggetti, che in un sistema destinato a persone diverse da quelle osservate è il
difetto peggiore.*

**Ma le barre di errore si sovrappongono tutte**: applicando il criterio
dichiarato, **le sei dimensioni non sono distinguibili**. Ciò che la misura
stabilisce non è che cinquanta alberi siano l'ottimo, ma che **aumentare la
dimensione non compra nulla e costa latenza in modo lineare**. È il motivo per
cui il valore ereditato è stato *mantenuto* invece che sostituito.

### Frame rate

| | 18 fps | 9 fps |
|---|---:|---:|
| cadute non rilevate | 6,8% | **12,4%** |
| scarto di F2 | — | −0,045 |

**Le cadute non rilevate raddoppiano**, mentre lo scarto di $F_2$ resta
formalmente dentro la dispersione. **È il caso esemplare di perché una metrica
aggregata non basti a decidere**: la precision migliora al calare del frame rate
e compensa nel punteggio complessivo il peggioramento della grandezza che in un
sistema di sicurezza conta davvero.

Confronto incrociato utile al Capitolo 5: la foresta a 9 fps (0,861) **eguaglia
la Bi-GRU a 18 fps** (0,862). *Metà del frame rate si compra con un cambio di
modello.*

### Robustezza all'occlusione — `pipeline/occlusioni.py`

**Come si simula un punto non disponibile.** *Non* azzerandolo: uno zero in
coordinate immagine è l'angolo in alto a sinistra, cioè una posizione
**plausibile e sbagliata**, che produrrebbe velocità enormi verso quell'angolo.
Sotto occlusione MediaPipe continua a emettere una posizione con confidenza
bassa, propagandola dal fotogramma precedente. **Il punto mascherato viene quindi
congelato all'ultima posizione nota**, perché è il comportamento reale dello
stimatore ed è anche il più benevolo: le derivate vanno a zero invece che
esplodere. **Il risultato è un limite superiore alla robustezza.**

Sono stati provati sia gruppi **anatomici** sia gruppi **casuali** di dimensione
crescente, che servono da termine di paragone: *se un gruppo anatomico costasse
più di un gruppo casuale della stessa dimensione, quel gruppo sarebbe critico.*

| gruppo congelato | punti | variazione di $F_2$ |
|---|---:|---:|
| spalle | 2 | **−0,020** |
| caviglie | 2 | −0,015 |
| naso | 1 | −0,008 |
| gambe (ginocchia+caviglie) | 4 | −0,000 |
| metà sinistra | 6 | +0,008 |
| **anche (riferimento di A3)** | 2 | **+0,012** |
| casuale 11% | 1 | −0,012 |
| casuale 22% | 2 | −0,006 |
| casuale 33% | 3 | −0,001 |
| casuale 55% | 5 | −0,008 |

Base senza occlusione: 0,857 ± 0,078.

**Il peggioramento più grande è 0,020, contro una dispersione fra soggetti di
0,078: nessun gruppo di punti è critico.** La variazione prodotta
dall'occlusione è quattro volte più piccola di quella prodotta dal cambio di
persona.

Due osservazioni controintuitive:

1. **congelare le anche migliora di 0,012.** Un riferimento *stabile* produce
   grandezze meno rumorose di uno stimato a ogni fotogramma: congelarlo equivale
   a filtrarlo — ed è la conferma indiretta dell'utilità di $h_{\text{pav}}$
   (vedi Cap. 3);
2. **i gruppi casuali non costano sistematicamente meno di quelli anatomici.** Se
   esistesse un sottoinsieme di punti che porta l'informazione dell'evento,
   occludere proprio quello dovrebbe costare di più. Non accade: **l'informazione
   è distribuita** sulla configurazione nel suo insieme.

> **Limite dichiarato:** questa è un'occlusione *simulata*. Le occlusioni da
> mobilio non sono state misurate, perché né UP-Fall né UR-Fall le annotano.
> Inoltre il risultato sull'**auto-occlusione** (il viso nascosto quando si è a
> terra) riguarda **YOLOv8** e non si riproduce su MediaPipe: lì la confidenza
> del naso passa da 0,997 a 0,989, cioè non degrada — degradano gli arti. **Va
> attribuito allo stimatore, non al problema.**

---

## 8. Effetto della definizione del compito — il fulcro del capitolo

Tutte le sezioni precedenti confrontano modi diversi di risolvere **lo stesso**
problema. Questa confronta **tre problemi diversi**, a parità di modello,
grandezze, dati e protocollo. Script: `pipeline/confronto_compiti.py`.

| compito | prevalenza | $F_2$ | precisione | **negativi difficili** |
|---|---:|---:|---:|---:|
| **evento** (`fall`) | 0,047 | **0,831 ± 0,072** | **0,924** | **0,0%** |
| stato (`fallen`) | 0,089 | 0,704 ± 0,084 | 0,755 | 12,5% |
| allarme (`fall` O `fallen`) | 0,115 | 0,810 ± 0,068 | 0,833 | 13,1% |

**Il compito *evento* ha la prevalenza più bassa** — meno di un quinto delle
finestre positive del compito *allarme* — **e nonostante questo ottiene l'$F_2$
più alto, la precisione più alta, e sbaglia sullo zero per cento delle 2.234
finestre di persona distesa volontariamente.**

**Perché misurare i difficili a parte:** un tasso di falsi allarmi complessivo
nasconde il problema. I negativi facili — camminare, stare in piedi — sono la
grande maggioranza e sono banali. Su UR-Fall: 0,2% di allarmi sui facili contro
35–50% sui difficili. **La media dei due non descrive nessuno dei due.**

La ragione è che i tre non sono tre gradazioni di difficoltà ma **tre problemi
con confini diversi**: una persona a terra e una sdraiata sul divano sono, come
configurazione, la stessa cosa. Chi riconosce lo *stato* non ha modo di
distinguerle e sbaglia su una su otto; chi riconosce l'*evento* cerca una
transizione, e chi si corica lentamente non la produce.

> **Perché è il fulcro.** Fra la GRU e la LSTM la differenza è 0,011 e
> servirebbero 113 soggetti. Fra il compito *stato* e il compito *evento* la
> differenza è **0,127** e ne servirebbero **due**. Le due domande non sono dello
> stesso ordine, **e il lavoro ha speso la maggior parte del proprio tempo su
> quella meno importante.**

---

## 9. Trasferimento a un archivio esterno (UR-Fall)

Tutte le misure precedenti vengono da un solo archivio: misurano la
generalizzazione fra **persone**, mai quella fra **ambienti**.

**Che cosa è stato provato:** non un modello addestrato per l'occasione, ma **il
sistema effettivamente installato** — gli stessi file di modello e di
normalizzazione che girano sul dispositivo, applicati a un secondo archivio
pubblico. *«Un modello addestrato su questi dati generalizzerebbe?» è una domanda
accademica; «il sistema che sto consegnando generalizza?» è la domanda che decide
se il lavoro serva a qualcosa.*

### La correzione preliminare, senza la quale la misura non significherebbe nulla

Una prima versione riportava un crollo pressoché totale. **Quel numero era
misurato contro una verità di riferimento sbagliata.** Le due annotazioni sono di
**natura diversa**:

| archivio | che cosa annota |
|---|---|
| UP-Fall | **fase dell'evento**: 0 normale · 1 sta cadendo · 2 a terra dopo |
| UR-Fall | **postura**: −1 non disteso · 0 in transizione · +1 disteso |

`label = 1` significa quindi cose opposte: in UP-Fall è la caduta in corso, in
UR-Fall è la persona **distesa** — e in una ripresa ADL significa una persona che
si è sdraiata di proposito. Confrontando riga per riga con le annotazioni
originali, la vecchia conversione risultava:

```
originale −1  →  nostro 0    99%
originale  0  →  nostro 1    76%   e nostro 0 il 24%
originale +1  →  nostro 1   100%
```

**La classe di transizione era stata spalmata sulle altre due senza una regola**,
e le 1.470 pose «disteso» delle riprese ADL — cioè esattamente il negativo
difficile — erano state forzate a 0.

**Intervento** (`pipeline/rietichetta_urfall.py` + `pipeline/estrai_urfall.py`):
l'archivio è stato **riestratto con lo stesso motore geometrico** e rietichettato
secondo la semantica dichiarata dai suoi autori, con una colonna
`disteso_volontario` che marca i **2.289 fotogrammi** di negativi difficili.

**Risultato dell'estrazione ([EXP-014](../EXPERIMENTS.md#exp-014)):** 11.400
fotogrammi, 67 riprese, 32/32 colonne, **81,0% di pose valide contro il 95,8% di
UP-Fall** — è di per sé un dato: le condizioni di ripresa sono sensibilmente
peggiori.

### La metrica indipendente dalla soglia

La prevalenza nei due archivi è diversa, e questo rende il confronto diretto fra
due $F_2$ privo di significato. La grandezza che regge il confronto è la
**PR-AUC rapportata alla prevalenza**: quante volte il modello fa meglio di una
decisione presa a caso *su quello specifico archivio*. È adimensionale e risponde
alla domanda giusta — **il modello *ordina* ancora correttamente le finestre?**

| rappresentazione | n | PR-AUC | guadagno sul caso | $F_2$ | difficili in allarme |
|---|---:|---:|---:|---:|---:|
| modello schierato (vecchio, A3 a 10 col.) | 10 | 0,169 | 1,8× | 0,034 | 11,6% |
| A3 senza integrali | 9 | 0,440 | 3,4× | 0,404 | 47,1% |
| A3 con integrali | 12 | 0,466 | 3,6× | 0,479 | 41,7% |
| **sottoinsieme DTW** | 12 | **0,660** | **5,1×** | **0,630** | 50,5% |

### Scomposizione: calibrazione contro capacità discriminativa

**Il modello mantiene capacità discriminativa e perde calibrazione.** Cinque
volte il caso su un archivio mai visto non è il comportamento di un modello che
ha imparato l'ambiente di addestramento: è il comportamento di un modello che ha
imparato qualcosa del fenomeno ma assegna punteggi su una **scala** diversa da
quella su cui la soglia era stata fissata.

**Conseguenza pratica precisa:** un difetto di *ordinamento* richiederebbe di
riaddestrare; un difetto di *scala* richiede di **ritarare**, che costa
incomparabilmente meno.

> **Questo però non è consolante**, ed è il punto che il lavoro deve dichiarare:
> per ritarare la soglia servono **cadute etichettate dell'ambiente di
> destinazione**, e chi installa un sistema in un'abitazione **non le possiede**.
> È una correzione disponibile soltanto a chi già dispone della risposta.

### Due direzioni che si sommano

1. **La rappresentazione temporale**: da 3,4× a 5,1×. E il salto maggiore **non
   viene dagli integrali in sé ma dal motore geometrico corretto** — angoli
   srotolati, derivate non esplosive — che già sulla rappresentazione di base
   quasi raddoppia il guadagno.
2. **La definizione del compito**: restringendo il positivo alla sola
   transizione, il guadagno sale a **6,8×** e i falsi allarmi sui difficili
   scendono dal 50,5% al **35,9%**.

**È la stessa coppia di scelte che le sezioni 6 e 8 isolano in laboratorio, e
ritrovarle qui, su dati di un altro laboratorio, è la corroborazione più forte
che il lavoro possa offrire.**

### Che cosa resta, e i limiti

Il guadagno di 5,1× **non va letto come un successo**: significa che il sistema,
su un ambiente nuovo, distingue le cadute meglio del caso ma non abbastanza da
essere impiegato senza taratura — alla soglia dichiarata i falsi allarmi sui
difficili restano fra un terzo e la metà.

**Limiti:**

- **un solo archivio di destinazione**: non si distingue ciò che è specifico di
  UR-Fall da ciò che varrebbe per qualunque ambiente nuovo;
- **la soglia migliore è scelta sullo stesso insieme su cui viene misurata**: è
  una **soglia oracolo**, cioè un valore ottenuto usando le etichette del dominio
  di destinazione, che chi installa non possiede. Il valore 0,612 è un **limite
  superiore ottimistico** — utile a separare le due componenti del divario, non
  una prestazione ottenibile. *(Il termine «soglia oracolo» è entrato nel testo su
  richiesta esplicita del relatore.)*

**Due indicazioni operative, indipendenti e quindi sommabili:**

1. **sulla soglia**: serve una calibrazione che non richieda cadute etichettate —
   per esempio un percentile delle probabilità osservate nelle prime ore di
   funzionamento ordinario;
2. **sul punto di vista**: o si prescrive l'inquadratura come parte
   dell'installazione, oppure si addestra su una molteplicità di viste. La
   seconda è misurata come efficace.

---

## 10. Che cosa è cambiato nel testo di questo capitolo

- **26 agosto — fusione**: protocollo + risultati, con le due introduzioni
  **sostituite** da un'apertura nuova (non concatenate) e un paragrafo di
  transizione nel punto di giunzione. Testo delle sezioni invariato.
- **26 agosto — gerarchia**: da 14 sezioni + 30 sottosezioni a **9 + 7**, cioè
  492 parole per titolo. 79 operazioni di declassamento e rinomina, **nessuna
  riscrittura**. Titoli portati in forma nominale («Effetto della geometria di
  ripresa» al posto di «L'effetto del punto di vista»).
- **26 agosto — le quattro richieste del relatore**, verificate una per una con
  `grep`: nessuna delle quattro espressioni compariva nel testo.

| punto del relatore | intervento |
|---|---|
| §4 chiamarlo *adattamento al dominio* | «adattamento al dominio di installazione — *domain adaptation* — e non generalizzazione» (Cap. 5) |
| §5 mostrare i **due errori**, non un solo $F_2$ | tabella FN/FP per le cinque configurazioni + `fig_errori.png` |
| §6 chiamarla **soglia oracolo** | definita come «valore ottenuto usando le etichette del dominio di destinazione, che chi installa non possiede» |
| §8 coerenza fra 4,47 e 2,20 ms | il classificatore decide una volta ogni due fotogrammi (passo 2), quindi il costo ammortizzato è metà di quello per finestra |

**Il dato nuovo del §5**, a dieci soggetti e non a cinque: da A3 ad A3i con i
controesempi i falsi negativi passano da **45 a 14** e i falsi positivi da **172
a 124**. *In laboratorio la configurazione finale non introduce alcuno scambio:
migliora entrambi gli errori. Lo scambio compare solo in casa* — che è esattamente
la tesi del Capitolo 5.

### Figure

Prodotte da `pipeline/figure_tesi.py`, che scrive in `tesi/figure/`:
`fig_configurazioni`, `fig_architetture`, `fig_compiti`, `fig_esterno`,
`fig_occlusioni`, `fig_finestra`, `fig_rumore`, `fig_dimensione`,
`fig_viewpoint_dist`, `fig_errori`, `fig_compiti_casa`.

**Resta mancante una figura**: la 4.1, i due fotogrammi simultanei della stessa
caduta dalle due telecamere, che va composta scegliendo l'istante. È dichiarata
nel `.tex` con un commento che indica le due cartelle sorgente.

> **Attenzione:** un ambiente `figure` senza `\includegraphics` **compila**:
> lascia uno spazio bianco con la didascalia sotto. È così che quattro figure
> mancanti sono rimaste inosservate per settimane, ed è il motivo per cui
> `tesi/controlla.py` verifica anche questo.
