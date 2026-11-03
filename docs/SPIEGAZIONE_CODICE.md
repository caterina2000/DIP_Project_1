# Cosa è stato fatto, nel codice, come e perché

Aggiornato il 6 ottobre 2026. Stesso ordine del discorso al controrelatore
([DISCORSO_CONTRORELATORE.md](DISCORSO_CONTRORELATORE.md)). Ogni punto è stato controllato contro il codice
(`src/`, `pipeline/`, `deploy_board/`, `config.py`) e i capitoli (`tesi/Cap1-6.tex`).

Per ciascun passo: **cosa**, **dove nel codice**, **come**, **perché**.

## Dispositivo e rete

- **Cosa.** Radxa ROCK 4D, webcam USB, MediaPipe sulla CPU, Random Forest ([deploy_board/rileva.py](../deploy_board/rileva.py)).
- **Rete.** Nel codice di `deploy_board` non ci sono chiamate di rete. La board però salva clip locali intorno agli allarmi, quindi le
  immagini esistono sul dispositivo. Non dire che «non memorizza immagini».

## Stima della posa

- **Come.** Un motore per telecamera, con stato azzerato a ogni registrazione
  ([estrai_feature.py:221-295](../pipeline/estrai_feature.py#L221)).
- **Perché.** Riduce l'ingresso da pixel a 33 punti interpretabili: inclinazione del tronco, discesa del bacino.

## Le tre rappresentazioni ([src/geometry.py](../src/geometry.py))

- **A1**: matrice di covarianza dei punti 2D, `np.linalg.eigh` ([riga 357](../src/geometry.py#L357)). Orientamento e allungamento.
- **A2**: world landmark 3D di MediaPipe, origine al bacino. Profondità stimata da una sola immagine.
- **A3**: nove grandezze relative al bacino e al tronco: lunghezza del tronco, angolo e sua variazione, altezza relativa di testa,
  ginocchia e caviglie, larghezza, velocità dell'anca, velocità della testa rispetto all'anca.
- **Perché tre.** Ognuna rinuncia a qualcosa di diverso: posizione nella scena, profondità, o indipendenza dalla corporatura.
- **Attenzione.** Il confronto preliminare era su cinque soggetti; fu ripetuto su dieci dopo una correzione (Cap. 4).

## Altezza dal pavimento

- **Come.** Nei fotogrammi con persona in piedi si prendono bordo inferiore del corpo e centro dei fianchi; una retta `y = a·x + c` per
  minimi quadrati dà il pavimento; l'altezza è in lunghezze di tronco ([geometry.py:274-340](../src/geometry.py#L274)).
- **Perché.** Nei negativi con persona orizzontale l'altezza mediana è +0,02 tronchi nel dataset e +1,47 in casa.
- **La DTW la scarta.** 1,541 sulla laterale (seconda su 33), 1,124 sulla frontale: il minimo fra le viste la mette ventunesima. Viene
  reintrodotta come DTWH (12 + 1 = 13) perché il sistema installato usa la vista laterale. **Non dire «poco discriminativa».**
- **Limite.** Reintrodotta dopo aver visto falsi positivi in casa: non è una verifica indipendente. Sul campo la board aspetta una
  stima del pavimento prima di decidere ([rileva.py:997](../deploy_board/rileva.py#L997)).

## Grandezze integrali e parametro K

- **Come.** Escursione = massimo meno minimo dell'angolo del tronco; percorso = somma delle distanze fra posizioni successive del
  punto seguito; discesa = di quanto il punto è sotto il suo massimo recente
  ([geometry.py:539-545](../src/geometry.py#L539)). K = 31 ([config.py:108](../config.py#L108)), circa 1,7 s a 18 fps.
- **Perché.** Appena la persona è a terra la velocità torna piccola: nell'esempio della tesi va da 3,76 a 0,11, mentre la discesa
  accumulata resta a 1,40. L'autocorrelazione ρ₁ sale da 0,22–0,54 a 0,82–0,99.
- **Limite.** K fu scelto con un controllo che usava dati poi usati nella valutazione. Senza il soggetto di test nove fold su dieci
  scelgono 45 e F2 passa da 0,825 a 0,851 (t = 2,22, sotto il critico 2,26): 31 non ha gonfiato il risultato.
- **Nota.** Nelle integrali di A2 si segue il naso e non i fianchi: dai fianchi percorso e discesa misuravano rumore.

### Spiegazione semplice (le tre grandezze)

Le tre grandezze sono **escursione, percorso e discesa**. La velocità è come il tachimetro: dice quanto vai *adesso*. Le tre
grandezze integrali sono come il contachilometri parziale: dicono cosa è successo *negli ultimi 31 campioni*, circa 1,7 secondi.

- **Percorso**: quanta strada ha fatto il punto che seguo (i fianchi) in quei 1,7 secondi, sommando tutti i piccoli spostamenti da un
  fotogramma al successivo. Una persona ferma ha percorso quasi zero; una che si muove o cade ha percorso molto.
- **Escursione**: di quanto è cambiata l'inclinazione del tronco, cioè il massimo meno il minimo dell'angolo nei 1,7 secondi. Se il
  tronco passa da verticale a orizzontale, l'escursione è grande, anche se ora è fermo.
- **Discesa**: quanto il punto è più in basso rispetto al suo punto più alto degli ultimi 1,7 secondi. Se i fianchi erano a 1 metro e
  ora sono a 20 cm, la discesa è grande.

**Perché servono.** Una caduta dura circa un secondo e mezzo; appena la persona è a terra smette di muoversi, quindi la velocità
istantanea torna vicino a zero e, guardando solo quella, il sistema vede «persona ferma» come se non fosse successo niente. Le tre
grandezze invece guardano indietro nella finestra di 1,7 secondi, e per un po' ricordano che c'è stata una grande discesa e una grande
rotazione del tronco. Nell'esempio della tesi la velocità dell'anca passa da 3,76 a 0,11 quando il corpo si ferma, mentre la discesa
accumulata sale a 1,40 e ci resta.

**Il limite della memoria.** Ricordano solo gli ultimi 31 campioni. Quando la finestra esce dall'evento i valori tornano a decadere.
Inoltre misurano anche il rumore: se lo stimatore di posa passa a una posa sbagliata, l'escursione può crescere senza che il corpo si
sia mosso davvero (Cap. 4).

**Perché K = 31.** Non è un valore ottimizzato. Rifacendolo senza il soggetto di test, nove fold su dieci scelgono 45, e F2 passa da
0,825 a 0,851: quindi 31 non ha gonfiato il risultato, ma resta una scelta non indipendente.

**Frase per il controrelatore.** «La velocità dice cosa succede adesso e si azzera quando la persona è a terra. Percorso, escursione e
discesa riassumono gli ultimi 1,7 secondi: quanta strada ha fatto il punto, quanto è ruotato il tronco, quanto è sceso. Così il
sistema ricorda che c'è stata una caduta anche dopo che il corpo si è fermato.»

## Selezione con Dynamic Time Warping ([src/dtw.py](../src/dtw.py))

1. z-score per curva ([dtw.py:38](../src/dtw.py#L38)), perché le scale sono eterogenee.
2. DTW fra curve della stessa classe e di classi diverse: tollera velocità diverse.
3. Punteggio per telecamera, si tiene il minimo: `S_robusto = min(S_cam1, S_cam2)`.
4. Si percorrono le grandezze in ordine di punteggio e si scarta quella con |ρ| ≥ 0,85 rispetto a una già scelta (quattro scartate).

- **Risultato.** 12 su 33, correlazione media 0,435, otto integrali.
- **Limite.** Fatta una volta sull'intero dataset prima del LOSO: il soggetto di test contribuisce indirettamente (dichiarato nel Cap. 3,
  misurato nel Cap. 4).

### Spiegazione semplice (DTW e selezione)

**Il problema.** Le grandezze candidate sono 33, ma non tutte servono: alcune sono ridondanti, altre non distinguono una caduta da
un'attività quotidiana. Voglio tenere solo quelle **discriminative**.

**Cos'è il DTW.** Il Dynamic Time Warping confronta due curve nel tempo anche se una è più lenta dell'altra. Esempio: due persone
cadono, una in un secondo e una in un secondo e mezzo. Le due curve hanno la stessa forma ma tempi diversi. Un confronto punto per punto
le giudicherebbe diverse; il DTW le «allinea» (stira un po' una delle due) e vede che sono simili. Qui è ristretto a scostamenti
piccoli: `|i − j| ≤ 10` campioni, per non accoppiare parti troppo lontane.

**Attenzione: le classi sono due, non tre.** Le classi sono **cadute** e **attività quotidiane**. Quelle che sono tre sono le **famiglie
di confronti**, per ogni grandezza:
- **D_FF**: distanza fra coppie di cadute;
- **D_AA**: distanza fra coppie di attività quotidiane;
- **D_FA**: distanza fra una caduta e un'attività quotidiana.

**Il punteggio.** `S = μ_FA / (media di μ_FF e μ_AA)`: la distanza media fra le due classi divisa per la distanza media dentro ciascuna.
Una grandezza è buona se le cadute si somigliano fra loro, le attività si somigliano fra loro, e le due classi sono diverse. Allora il
numeratore è grande e il denominatore piccolo, e S è alto. Se S è circa 1, la grandezza non distingue.

**Passi pratici prima del confronto.**
1. Ogni curva è normalizzata a media zero e deviazione 1, per confrontare la *forma* e non la scala (alcune sono angoli, altre
   velocità).
2. Tutte le curve sono riportate a 200 campioni: le cadute durano circa 180 fotogrammi, le attività circa 820, e senza questo ci
   vorrebbe una banda enorme.
3. Il punteggio si calcola per ciascuna telecamera e si tiene il **minimo**: una grandezza che funziona solo da una vista non passa.
4. Si scartano le grandezze troppo correlate (|ρ| ≥ 0,85) con una già scelta.

**Risultato.** Da **33 grandezze a 12** (non «da tre»), con correlazione media 0,435, e **8 delle 12 sono integrali**.

**Il DTW non fa parte del classificatore.** È solo uno strumento di analisi per scegliere le grandezze: il classificatore non lo usa.

**Altezza dal pavimento.** Ha un punteggio di 1,541 sulla vista laterale (secondo fra 33) e 1,124 sulla frontale: il minimo la porta
al ventunesimo posto e viene scartata. La si reintroduce come configurazione a 13 grandezze (DTWH) perché il sistema installato usa la
vista laterale.

**Come va detta la ragione della vista laterale.** Il tuo ricordo («la laterale è più accurata, quindi si usa quella») è solo in parte
corretto. Ciò che sta nella tesi è: il protocollo di acquisizione del sistema installato prevede una telecamera laterale, a 1,2–1,5 m
dal pavimento (Cap. 5), coerente con la Camera 1 di UP-Fall. L'esperimento sulle viste (qui sotto) mostra che un modello addestrato su
una vista non si trasferisce all'altra; non prova che la laterale sia «più accurata» in assoluto, perché i numeri sono 0,822 ± 0,099 per
la laterale e 0,753 ± 0,179 per la frontale, con differenza (0,069) minore della dispersione.

### L'esperimento sulle viste (Cap. 4, tabella `viste`)

Configurazione: rappresentazione A3i (dodici grandezze, senza altezza dal pavimento), Random Forest, formulazione a tre classi,
soglia 0,50. UP-Fall ha due telecamere sincronizzate: Camera 1 laterale (altezza torace) e Camera 2 frontale rialzata.

| Addestramento | Test | F2 | Falsi positivi |
|---|---|---|---|
| Camera 1 | Camera 1 | 0,822 ± 0,099 | 722 |
| Camera 1 | Camera 2 | 0,488 ± 0,119 | 3.252 |
| Camera 1 + Camera 2 | Camera 2 | 0,731 ± 0,188 | 751 |
| Camera 2 | Camera 2 | 0,753 ± 0,179 | 1.067 |

- **Cosa dice.** Passando da Camera 1 a Camera 2 si perdono 0,334 di F2, circa tre volte la dispersione fra soggetti; i falsi positivi
  quasi quintuplicano. Con entrambe le viste in addestramento si recupera molto (0,731) ma non tutto. Recall da 0,670 a 0,762,
  precisione da 0,316 a 0,713.
- **Perché.** La stessa caduta, vista da due posizioni, dà grandezze diverse: nell'esempio della tesi l'escursione dell'angolo del tronco
  è 84,9° nella vista laterale e 13,5° nella frontale rialzata.
- **Conseguenza.** Il sistema funziona nelle condizioni di ripresa in cui è stato addestrato; cambiare inquadratura richiede di
  riaddestrare o di includere più punti di vista.

## Preprocessing

| Passo | Dove | Perché |
|---|---|---|
| Ordine per timestamp, intervalli reali | [dati.py:273](../src/dati.py#L273), [estrai_feature.py:136](../pipeline/estrai_feature.py#L136) | Cadenza non costante: mediana 18,09 fps, da 14,43 a 19,63; in 70 registrazioni su 220 lo scarto supera il 5% |
| Stimatore azzerato per registrazione | [estrai_feature.py:264-295](../pipeline/estrai_feature.py#L264) | MediaPipe ha stato: l'ultima posa di una ripresa influenzava la prima della successiva. Difetto trovato il 6 settembre |
| Posa mancante: buffer azzerati | Cap. 3 | Una finestra non attraversa mai un buco |
| Logaritmo con segno `segno(x)·log(1+|x|)` | [dati.py:205](../src/dati.py#L205) | Code lunghe: una grandezza ha rapporto 908 fra estremo e tipico |
| Standardizzazione solo sul training, prima delle finestre | Cap. 4 | Il test non influenza la scala. Prima della correzione il classificatore non riconosceva nessun positivo (F1 = 0) |

### Preprocessing spiegato in modo semplice

**1. Ordinare i fotogrammi per timestamp e usare gli intervalli reali.**
- *Cosa sono i dati.* UP-Fall non ha video, ma cartelle di immagini PNG. Il nome di ogni file è un orario al microsecondo, per esempio
  `2018-07-04T12_14_09.030460.png`.
- *Cosa ho fatto* ([estrai_feature.py:134-187](../pipeline/estrai_feature.py#L134)). Leggo l'orario dal nome, metto i fotogrammi in
  ordine e per ognuno calcolo il tempo trascorso dal precedente. Se i nomi mancano o non sono ordinati, uso il valore dichiarato (18
  fps) invece di inventare un intervallo.
- *Perché non assumo 18 fps costanti.* Il dataset dichiara 18 fps, ma misurato è diverso: da 14,43 a 19,63 fps fra le riprese, e in
  70 registrazioni su 220 lo scarto supera il 5%. Gli scarti sono sistematici per soggetto: le dieci riprese più lontane dal valore
  dichiarato sono tutte dello stesso soggetto, e con il leave-one-subject-out un errore per soggetto finirebbe dentro un fold intero.
  Anche dentro una stessa ripresa la cadenza non è regolare: intervallo mediano 49,6 ms, nono decile 70,2 ms, 99° percentile 159,8 ms.
- *Esempio.* Una velocità è una differenza di posizione divisa per il tempo. Se fra due fotogrammi c'è un buco di mezzo secondo e io
  divido per 1/18 di secondo, quella piccola differenza diventa una velocità enorme che non c'è mai stata. Usando il tempo vero, il
  buco non crea un falso picco.
- *Nota.* Non ricampiono le curve su una griglia uniforme: così non creo mai una posa in un istante che non è stato osservato.

**2. Azzerare lo stimatore a ogni registrazione.**
- *Cosa fa MediaPipe.* È un *tracciatore*: dopo aver trovato la persona, nel fotogramma successivo parte dalla posizione precedente
  invece di cercarla da capo. È ciò che lo rende veloce e stabile.
- *Il problema.* Se uso lo stesso stimatore per 220 registrazioni di fila, la prima immagine di una ripresa parte dall'ultima posa
  della ripresa precedente (per esempio una persona a terra). Le prime pose di ogni ripresa risultano condizionate da un video che non
  c'entra, e quindi anche le feature calcolate da quelle pose.
- *Quanto pesava.* Rifacendo il controllo su una ripresa già presente, nessuna delle 866 righe coincideva con il dataset. Lo scarto
  sui primi 5 fotogrammi era di 2,32 deviazioni standard della colonna, calava a 0,26 fra 5 e 50 fotogrammi e a 0,026 oltre i 300. Le
  riprese di caduta durano circa 200 fotogrammi, quindi la parte contaminata era circa un quarto del video.
- *Cosa ho fatto* ([estrai_feature.py:264-295](../pipeline/estrai_feature.py#L264)). Un nuovo stimatore per ogni registrazione, che
  nasce e muore con essa. Costa qualche decimo di secondo di inizializzazione, ma rende il dataset riproducibile.
- *Come dirlo.* «Lo stimatore tiene memoria del fotogramma precedente: se non lo riavvio, l'ultima posa di una registrazione
  influenza la prima della successiva, e le feature di quei primi fotogrammi risultano alterate.»

**3. Posa mancante: azzerare i buffer.**
- *Quanto capita.* La posa è valida nel 95,9% dei fotogrammi (111.570 su 116.362). Quindi nel 4,1% restante lo stimatore non
  restituisce uno scheletro.
- *Cosa ho fatto* ([geometry.py:554-556](../src/geometry.py#L554)). Quando manca la posa, il motore geometrico richiama `reset()`,
  cioè cancella la memoria delle ultime posizioni usata per le velocità e per le grandezze integrali, e restituisce zeri.
- *Perché.* Esempio: la persona esce dall'inquadratura per due secondi e poi rientra. Se mantenessi la memoria, il sistema
  calcolerebbe uno spostamento enorme fra l'ultima posa prima del buco e la prima dopo, come se la persona avesse fatto un salto: uno
  spostamento mai avvenuto. Azzerando, quello spostamento non viene calcolato.
- *Conseguenza.* Una finestra non attraversa mai una perdita di posa: nessuna finestra contiene osservazioni separate da un buco.
  Dopo il reset le integrali hanno bisogno di un breve periodo per riempirsi di nuovo (circa 31 campioni).

**4. Logaritmo che conserva il segno.**
- *Il problema.* Alcune grandezze hanno quasi sempre valori piccoli e, rarissimamente, valori enormi. Per esempio la discesa di A3: il
  suo 99,9° percentile è 908 volte la mediana. Per standardizzare si calcolano media e deviazione standard, e pochi valori enormi
  gonfiano la deviazione: tutti gli altri valori, «normali», finirebbero schiacciati vicino a zero.
- *Cosa ho fatto* ([dati.py:152-205](../src/dati.py#L152)). Sulle colonne con quella coda lunga applico `log(1 + x)`: il logaritmo
  comprime i valori grandi (da 1.000 a circa 6,9) senza toccare troppo quelli piccoli. Il «+1» evita `log(0)`. «Conserva il segno»
  significa che per un valore negativo calcolo `-log(1 + |x|)`: la formula è `segno(x) · log(1 + |x|)`.
- *Quali colonne.* Sono quelle con rapporto fra 99,9° percentile e mediana superiore a 10, misurato su 109.746 fotogrammi con posa
  valida (per esempio A3_discesa 908×, A1_discesa 550×, A3_hip_vel 292×). Gli angoli e le derivate con segno non passano dal
  logaritmo.
- *Come dirlo.* «Alcune grandezze hanno code lunghissime: pochi valori enormi dominerebbero la standardizzazione. Il logaritmo li
  comprime, e il segno lo conservo per non confondere valori positivi e negativi.»

**5. Standardizzazione con i soli dati di addestramento.**
- *Cos'è.* Standardizzare significa sottrarre la media e dividere per la deviazione standard, così tutte le grandezze hanno scala
  confrontabile (media 0, deviazione 1). Serve perché senza scala comune le grandezze con numeri più grandi dominano
  l'addestramento. Prima della correzione il classificatore non riconosceva nessun positivo (F1 = 0), perché l'energia aveva media
  11,58 e massimo 15.499 e schiacciava le altre nove grandezze.
- *Il rischio.* Se calcolo media e deviazione su tutti i dati, compresi quelli del soggetto di test, il test ha già influenzato la scala:
  è una fuga di informazione, anche se piccola.
- *Cosa ho fatto* ([dati.py:344](../src/dati.py#L344)). In ogni fold lo `Scaler` viene calcolato solo sui fotogrammi dei soggetti di
  addestramento e poi applicato senza modifiche a validazione e test. Il calcolo avviene sui fotogrammi *prima* di costruire le
  finestre: con finestre da 22 campioni e passo 2, due finestre consecutive condividono 20 campioni, e calcolare le statistiche dopo
  conterebbe gli stessi dati più volte.
- *Come dirlo.* «Media e deviazione le calcolo solo sul training di ogni fold e le applico così com'erano al test: il soggetto di
  test non influenza la scala.»

**Cosa NON è nel preprocessing, per non confondersi.** La selezione DTW è fatta una sola volta sull'intero dataset prima del LOSO (non
dentro ogni fold): questo è un limite dichiarato e misurato, e non va nascosto.

## Finestre e sottocampionamento

- **Come.** Un campione ogni due; finestre di 22 con passo 2 ([dati.py:249-280](../src/dati.py#L249), [config.py:46,57](../config.py#L46)).
  Sulla board la finestra avanza ogni `passo` fotogrammi ([rileva.py:982](../deploy_board/rileva.py#L982)).
- **Perché.** La board non regge 18 fps: MediaPipe sulla CPU costa 92,6 ms per fotogramma.
- **22 contro 44.** A 9 campioni al secondo sono 2,4 e 4,9 s. Con 44 F2 passa da 0,825 a 0,915 (+0,091, t = 3,62). Ho tenuto 22 come
  compromesso con la tempestività: non è dimostrato ottimale.
- **Attenzione, due cose diverse.**
  - **La finestra di classificazione (22 campioni) è un conteggio**, non una durata: a 6,47 fps copre 3,40 s invece di 2,44 s. È
    una questione aperta nel registro del progetto (ISS-158) e uno degli sviluppi dichiarati.
  - **Il parametro K delle integrali: tesi e codice non dicono la stessa cosa.** La tesi (Cap. 3, riga 489; Cap. 5, riga 636) scrive
    che K è un numero di campioni, quindi a 9 fps coprirebbe circa 3,4 s. Il codice attuale ([geometry.py:203-255](../src/geometry.py#L203))
    definisce invece le integrali come una **durata** di 1,7222 s e converte K = 31 in durata dividendolo per 18 fps (ISS-148,
    risolta per le integrali): a 18 fps i valori sono identici, ma con cadenza più bassa la finestra resta di 1,72 s. **Prima della
    discussione va allineato il testo della tesi al codice, o viceversa. Non dire che K «si espande» sulla board senza averlo
    verificato.**

## Etichette

- **Come.** Per fotogramma: 0 attività quotidiana, 1 transizione, 2 stato post-caduta. Per finestra, criterio K-su-M: transizione 5 su
  8, post-caduta 10 su 15 (non ottimizzati sul classificatore). Tre formulazioni di addestramento: scartare le finestre di sola
  post-caduta, considerarle positive, oppure tre classi. Nella configurazione finale la transizione è l'evento positivo principale.
- **Perché separare.** «Sdraiarsi» è 20.980 fotogrammi, circa il 18% del dataset: «a terra» = «caduta» insegnerebbe «orizzontale =
  caduta».
- Le reti producono sempre una softmax; lo score è la probabilità della classe positiva, oppure, a tre classi, quella di non essere
  nella classe normale.

### Finestre, etichette e classificazione spiegate in modo semplice

**Perché le finestre.** In un singolo istante una caduta può avere la stessa postura di chi si siede di colpo o si piega a raccogliere un
oggetto. Ciò che le distingue è la **dinamica**: come si arriva a quella postura. Una finestra raccoglie 22 campioni consecutivi, ognuno
con 12 valori, quindi una tabella 22×12 che racconta come cambia il corpo in circa 2,4 secondi.

**Cosa dice il tuo ragionamento sulla lunghezza, e cosa dicono i dati.**
- *Troppo corta*: poco contesto, l'intera dinamica non c'è. Corretto, è scritto nel Cap. 3.
- *Troppo lunga*: contiene frame che non appartengono all'evento e aumenta il tempo necessario a riempire la finestra. Corretto, è
  scritto nel Cap. 3. **Ma nell'esperimento non si vede alcuna «diluizione»:** da 22 a 44 campioni F2 continua a salire.
- *L'esperimento* ([Cap4.tex:411-442](../tesi/Cap4.tex#L411)) confronta **quattro** lunghezze, non due: 22, 28, 36, 44.

| L | Durata | F2 | Recall | FN / FP |
|---|---|---|---|---|
| 22 | 2,4 s | 0,825 ± 0,080 | 0,849 | 232 / 468 |
| 28 | 3,1 s | 0,851 ± 0,075 | 0,880 | 164 / 414 |
| 36 | 4,0 s | 0,871 ± 0,085 | 0,900 | 113 / 341 |
| 44 | 4,9 s | 0,915 ± 0,084 | 0,945 | 53 / 249 |

  Salgono tutte le metriche e scendono sia i falsi negativi sia i falsi positivi: non è un semplice spostamento fra precisione e
  recall. Il confronto 22 contro 44: +0,091 di F2, t = 3,62. Non è «per la maggior parte delle feature»: è F2 medio sui dieci fold.
- *Perché 22.* Per la **tempestività**: con 44 campioni servono circa 4,9 s prima di poter decidere, con 22 servono 2,44 s. In più il
  22 è un valore **ereditato** da una configurazione precedente (45 campioni a 18 fps, durata simile). La mediana della transizione di
  caduta dura 3,11 s, quindi nemmeno 22 la contiene tutta.
- ***Non esiste un esperimento sulla latenza*** *di 22 contro 44.* Il fatto che 44 sia più lento è un conto (tempo di riempimento
  della finestra), non una misura. La scomposizione della latenza del Cap. 5 (calcolo 0,125 s, riempimento 2,743 s, persistenza
  0,997 s, totale 3,865 s) è fatta solo per la configurazione con 22 campioni e a 8,02 fps. Va detto così: «la scelta è un
  compromesso dichiarato, non un ottimo dimostrato».

**Cosa sono le etichette.** Il Cap. 3 dice che le registrazioni di UP-Fall sono state annotate a mano fotogramma per fotogramma in tre
fasi: **0** attività prima della caduta, **1** transizione (dalla perdita di equilibrio all'arrivo a terra), **2** stato a terra dopo la
caduta. Durate mediane: prima 0,94 s, transizione 3,11 s, stato a terra 5,97 s. **La tesi non dice che il dataset originale fosse solo
binario**: se vuoi dirlo, verificalo; la frase sicura è «le tre fasi sono annotazioni fotogramma per fotogramma».

**Da fotogramma a finestra.** Una finestra contiene fotogrammi di fasi diverse, quindi non si può etichettare con un solo fotogramma. Si
usa il criterio **K-su-M**: la fase è presente se almeno K fotogrammi sono dentro un intervallo locale di M. Transizione: 5 su 8;
stato a terra: 10 su 15. Questi valori non sono ottimizzati sul classificatore (nel registro è ancora indicato come analisi di
sensibilità da fare).

**Lo sbilanciamento è reale, ma separare le fasi non aumenta le cadute.** Nei dati la transizione è meno del 5% dei fotogrammi e lo stato
a terra circa il doppio; il 4,7% è la prevalenza della classe positiva se la transizione è l'unico positivo. Separare transizione e stato
a terra non crea cadute in più. Servono a tre cose:
1. costruire le etichette delle finestre nel modo giusto;
2. **confrontare diverse definizioni del compito** sugli stessi dati;
3. non insegnare «orizzontale = caduta»: l'attività «sdraiarsi» è 20.980 fotogrammi (circa 18% del dataset), contro 10.524 dello stato a
   terra dopo la caduta.

**Due livelli di confronto da non confondere.**
- **Tre formulazioni di addestramento** (Cap. 3): *scarta* (positivo = transizione, le finestre di sola post-caduta escluse
  dall'addestramento), *caduta* (transizione e post-caduta entrambe positive), *tre classi* (normale, transizione, post-caduta separate).
  Nel codice: `modo` in `fold_loso` ([dati.py:329](../src/dati.py#L329)).
- **Tre compiti di valutazione** (Cap. 4, definiti con le annotazioni OmniFall su 12.140 finestre, 1.399 positive): *event*, *state*,
  *alarm*.

| Compito | Prevalenza in training | F2 | Recall | Precisione | Finestre «sdraiarsi» segnalate |
|---|---|---|---|---|---|
| Event (solo transizione) | 0,047 | 0,415 | 0,364 | 0,990 | 0,04% |
| State (solo a terra) | 0,089 | 0,587 | 0,552 | 0,874 | 8,4% |
| Alarm (transizione + a terra) | 0,115 | 0,830 | 0,836 | 0,841 | 11,7% |

  Messaggio: con il solo evento la precisione è altissima (0,990) ma si perde più della metà delle finestre positive; con l'allarme si
  recupera la recall (0,836) ma il 11,7% delle finestre in cui la persona si sdraia volontariamente viene segnalato. **Cambiare la
  definizione del compito pesa più che cambiare l'architettura.**

**Attenzione sulla valutazione.** Il tuo testo dice «l'evento positivo principale è la transizione»: vale per l'**addestramento**
(Cap. 3, riga 744). Per la **valutazione comune** l'etichetta `y_allarme` vale 1 se nella finestra c'è la transizione **o** lo stato a
terra ([Cap3.tex:767](../tesi/Cap3.tex#L767)). Nel confronto fra architetture le finestre sono 11.719, con 1.491 positive (12,72%).
Quindi gli F2 riportati contano come positive anche le finestre di stato a terra. Questo è un punto che un controrelatore attento può
chiedere.

**Come funziona la classificazione.**
- *Ingresso.* Una tabella 22×12. Le reti (LSTM, GRU, CNN 1D, Transformer, rete a grafo) la leggono come sequenza. La Random Forest non
  segue l'ordine: ogni finestra è riassunta con sei numeri per grandezza (media, deviazione, minimo, massimo, primo e ultimo campione),
  cioè 12 × 6 = 72 valori. Primo e ultimo ci sono perché senza di loro una caduta e un rialzarsi risulterebbero uguali.
- *Uscita.* Una distribuzione di probabilità (softmax) sulle classi, anche nel caso binario. Lo **score di allarme** è la probabilità
  della classe positiva (caso binario) oppure, a tre classi, la probabilità di *non* essere nella classe normale: `1 − P(normale)`
  ([Cap3.tex:847,864](../tesi/Cap3.tex#L847)). In questo modo la stessa soglia 0,50 vale per tutte le formulazioni.
- *Addestramento.* Pesi di classe per compensare lo sbilanciamento ([modelli.py:62-67](../src/modelli.py#L62)) e arresto anticipato su
  `val_auc_allarme` con pazienza 8 ([modelli.py:155](../src/modelli.py#L155)). Il soggetto di validazione serve a fermare l'addestramento,
  non a scegliere la soglia (fissa a 0,50). Seme 42, un addestramento per fold.
- *Perché la Random Forest come riferimento.* Se un modello che non segue l'ordine temporale ottiene risultati simili a una rete
  ricorrente, il vantaggio di modellare la sequenza è limitato nelle condizioni considerate.

## Protocollo

- LOSO a dieci fold, 8 training / 1 validazione / 1 test ([dati.py:25](../src/dati.py#L25)). Seme 42, un addestramento per fold,
  nessuna ricerca di iperparametri: la deviazione misura la variabilità fra soggetti.
- **Soglia 0,50.** Sceglierla per fold sul soggetto di validazione era instabile (deviazione circa 0,37). Si sono confrontate sei
  regole sugli stessi fold e 0,50 è stata la migliore. **Non è indipendente dai risultati.**

### Protocollo e statistica spiegati in modo semplice

**1. Perché LOSO e non lo split per video (ISS-007).** Ogni soggetto compare in molti video. Se si divide per video, la stessa persona
sta sia in training sia in test: il modello può riconoscere *la persona* (corporatura, vestiti, modo di muoversi) invece della
caduta, e il risultato è gonfiato. Nella vecchia versione del progetto tutti e 5 i soggetti stavano in train *e* in test. Con il
LOSO si tiene fuori un intero soggetto: è la domanda giusta, «funziona su una persona mai vista?».

**2. Come funziona il LOSO qui.** Dieci soggetti → dieci fold. In ogni fold: 1 soggetto test, 1 soggetto validazione (serve solo a
fermare l'addestramento, early stopping), 8 soggetti training. Poi si ruota. Scaler e normalizzazione si stimano solo sugli 8.
Il risultato finale è la media dei dieci F2.

**3. Perché F2.** F2 pesa il richiamo più della precisione: una caduta mancata è peggio di un falso allarme. Per questo il
punteggio principale è F2 e non F1.

**4. Deviazione standard / «variabilità fra soggetti».** Dieci F2, uno per soggetto test. La deviazione standard dice quanto
questi dieci numeri si disperdono attorno alla media. Se per un soggetto il modello va a 0,95 e per un altro a 0,70, la deviazione
è grande. «Variabilità fra soggetti 0,089» significa: cambiare *persona* sposta l'F2 di circa 0,09; cambiare *architettura*
(0,032) lo sposta di meno. Quindi il limite è la generalizzazione tra persone, non il modello.

**5. Confronto appaiato fold per fold.** GRU e Random Forest si confrontano sugli *stessi* dieci soggetti. Per ogni soggetto si
calcola la differenza di F2 (GRU − RF); poi si guarda se la media delle differenze è grande rispetto alla sua dispersione
(statistica t). Appaiare toglie la difficoltà del soggetto: un soggetto difficile lo è per entrambi.

**6. «Soglia di significatività».** Con 10 fold, 9 gradi di libertà, α = 0,05 il valore critico di t è circa 2,26. Se |t| lo supera,
la differenza è improbabile per caso. I t contro la GRU sono −1,24 (RF), −1,22 (Transformer), −1,16 (CNN): sotto soglia. LSTM
(−2,98) e grafo (−3,14) la superano *da soli*.

**7. Bonferroni.** Facendo cinque confronti la probabilità di avere almeno un falso «significativo» sale. Bonferroni divide α per
5 (0,05/5 = 0,01) e il valore critico sale a circa 3,25. Con questa correzione nessuno dei cinque lo supera, neanche il grafo
(−3,14). Quindi: nessuna differenza dimostrata con 10 soggetti.

**8. «Equivalenti».** Attenzione: non significa «uguali», significa **non distinguibili con 10 soggetti**. Assenza di prova di
differenza ≠ prova di uguaglianza. Per vedere la differenza GRU–RF servirebbero circa 52 soggetti (9 per GRU–LSTM). Frase sicura:
«con dieci soggetti non posso distinguere GRU, CNN, Transformer e Random Forest; il vantaggio della GRU non è dimostrato».

**9. Soglia 0,50.** Scelta per fold sul soggetto di validazione era instabile (deviazione ~0,37: un solo soggetto di validazione
dà una soglia casuale). Sei regole confrontate sugli stessi fold: max-F2 su validazione 0,810 ± 0,117; max-F1 0,790; Youden 0,808;
prevalenza 0,787; prevalenza aumentata 0,823 ± 0,136; **fissa 0,50 → 0,851 ± 0,078**. Vince la fissa, ma il confronto è sui
fold di test: la scelta **non è indipendente dai risultati** (limite dichiarato).

### Cambio di vista (domain shift)

Il modello addestrato sulla vista laterale (Cam1) e valutato sulla frontale (Cam2) crolla: 0,822 ± 0,099 → 0,488 ± 0,119, con falsi
positivi da 722 a 3.252. Allenando con entrambe le viste risale a 0,731 (751 FP). Lettura: la geometria 2D dipende dall'angolo di
ripresa; la rappresentazione non è invariante alla vista. **Non** dire che la vista laterale è «più accurata» in generale: la tesi
dice solo che il protocollo installato è laterale. «0,82» è l'F2 nella stessa vista (laterale→laterale), non una prestazione
trasferita.

### UR-Fall

- **Cos'è** (dai file): `dataset/ur_fall/raw/{adl,fall}` con annotazioni; file tipo `adl-01-cam0-rgb`. Si usa solo la camera cam0
  RGB, a 30 fps ([estrai_urfall.py](../pipeline/estrai_urfall.py)): 67 registrazioni, 11.400 fotogrammi. Stesso stimatore, stesse
  feature; annotazioni rimappate sulle tre fasi. Posa valida 81,0% (contro 92,3% nel nostro dataset).
- **Fuori dalla tesi (conoscenza esterna, da non citare come dato della tesi):** dataset dell'Università di Rzeszów, cadute e ADL
  registrate con due Kinect; verificare prima di dirlo.
- **Esito.** F2: A3 0,404, A3 con integrali 0,479, sottoinsieme DTW 0,630. Guadagno PR-AUC sul caso: 3,4× / 3,6× / 5,1×.
- **Perché «incompleto».** Su una configurazione precedente la perdita si scompone in: ~49% **taratura** (la soglia 0,50 non è più
  quella giusta; spostandola si recupera ~0,457) e ~51% **potere discriminante** perso (ciò che resta, ~0,480, la soglia non lo
  aggiusta). La soglia «oracolo» è solo diagnostica (usa le etichette di test). Quindi il trasferimento recupera metà, non tutto.
  Questa scomposizione è su una configurazione precedente, non su quella finale.

### Esperimenti in casa

- **Cosa sono.** Cinque configurazioni su A3 (tabella nella sezione «Vista, UR-Fall, casa»): A3 base; A3h (+ altezza dal
  pavimento); A3i (+ grandezze integrali); versioni «+ controesempi» = aggiunta come negativi di finestre registrate nelle due
  abitazioni (attività quotidiane, sedersi, chinarsi, sdraiarsi sul divano), quindi *dentro* l'addestramento.
- **«Finestre positive»** = finestre con punteggio ≥ 0,50. **Non** sono allarmi. Una caduta ne produce in media 44,8, perché
  finestre vicine si sovrappongono (passo 2). La regola d'allarme le raccoglie in eventi: 7.429 finestre → 166 eventi.
- **Finestre/ora vs eventi/ora.** Le finestre misurano il classificatore (139,9 → 2,7/h); gli eventi misurano ciò che riceve
  l'utente (11,1/h nelle nove sessioni). Non vanno confusi né sommati.
- **Posa valida in casa.** 7,45 h su 9,58 registrate = 77,8% (limite inferiore della presenza). Il 10 agosto (sei blocchi, 0,6–39,8%)
  ha telecamera troppo vicina e non entra nei risultati.
- **Cadute.** Tesi: cinque simulate nella prima valutazione (agosto) + quattro il 9 settembre, annotate sui fotogrammi (tre
  riconosciute, due allarmi: la seconda a 6 s dalla prima soppressa dalla sospensione di 30 s). **Da non dire «nove cadute» come
  un unico totale**: la tesi non le somma, sono due prove con protocolli diversi.
- **Controesempi non è un test indipendente**: raccolti nelle stesse due case della valutazione; il controllo incrociato fra case
  (Cap. 5, «Transfer of the counter-examples») serve proprio a questo.
- **Persona sul divano** (9 settembre): quattro finestre sopra soglia, nessun allarme (la regola chiede cinque consecutive).

### Dalla finestra all'allarme (softmax)

L'ultimo strato dà una probabilità per classe con softmax (la somma fa 1). Nel caso binario il punteggio è P(caduta); nel caso a tre
classi (prima/durante/dopo) il punteggio d'allarme è la probabilità della classe caduta. Il punteggio per finestra si confronta con
0,50; la regola (5 consecutive, poi 30 s di silenzio) trasforma la serie di finestre in eventi. Un errore del classificatore è
diverso da un errore della regola: nella seconda caduta del 9 settembre il modello ha riconosciuto, la regola ha soppresso.

### «Riempimento della finestra» e 7,3 fps

- La finestra ha 22 campioni: finché non sono arrivati, il sistema non può decidere. A 8,02 fps sono 22 / 8,02 = 2,743 s, il 71%
  dei 3,865 s di latenza. È attesa, non calcolo.
- **7,3 fps** = capacità di elaborazione della scheda (136,65 ms/fotogramma: percezione 116,38 + classificazione 19,51 + 0,76 resto),
  misura sulla scheda. **Non** è né i 18 fps del dataset né i 9 fps di progetto dopo il sottocampionamento 1:2. La cadenza in uso è
  di circa 7–8 fps (7,26 nella prova continua, 8,02 nel calcolo di latenza): i 9 fps non vengono raggiunti, e per questo i
  campioni per finestra corrispondono a più secondi che nel dataset. **Il confronto in secondi è approssimato.**
- **Random Forest sulla scheda.** La tesi (bozza Cap. 5) lo motiva con la semplicità di deployment, il tempo di addestramento
  ridotto e l'assenza della dipendenza da TensorFlow sul dispositivo. Non è il più veloce (39,04 ms per finestra); il collo di
  bottiglia è la percezione (85,2%), quindi cambiare classificatore guadagna poco. Modello 606 KB + scaler 1,2 KB.

### Da controllare ancora

1. Quale classificatore produce gli F2 della tabella delle configurazioni (0,898–0,953): non indicato nel testo trovato; non
   coincide con lo 0,857 della GRU con DTW.
2. Differenza K in durata (codice) vs campioni (tesi), vedi sezione K.
3. Percentuali di posa valida per singola sessione domestica oltre al 77,8%.

## Classificatori ([src/modelli.py:56,431](../src/modelli.py#L56))

- Sei architetture. La Random Forest ha 50 alberi e sei numeri per grandezza: media, deviazione, minimo, massimo, primo e ultimo
  campione ([modelli.py:364](../src/modelli.py#L364)).
- **Risultati.** GRU 0,857, CNN 0,838, Transformer 0,837, Random Forest 0,825. LSTM: recall 0,945 ma 1.266 falsi positivi contro 938
  della GRU. Random Forest: 468 falsi positivi, 232 falsi negativi.
- **Statistica.** t contro la GRU: Random Forest −1,24, Transformer −1,22, CNN −1,16, LSTM −2,98, grafo −3,14. Con Bonferroni su
  cinque confronti il valore critico è circa 3,25 e nessuno lo supera. Soggetti necessari: 52 per GRU contro Random Forest, 9 per GRU
  contro LSTM.

## Vista, UR-Fall, casa

- **Vista.** 0,822 ± 0,099 → 0,488 ± 0,119 (falsi positivi 722 → 3.252) → 0,731 (751).
- **UR-Fall.** 11.400 fotogrammi, 67 registrazioni, stesso stimatore e stesso calcolo; annotazioni rimappate sulle tre fasi. F2 0,630.
- **Casa.**

| Configurazione | F2 laboratorio | Finestre/ora | Cadute |
|---|---|---|---|
| A3 | 0,898 | 139,9 | 3/5 |
| A3h | 0,931 | 70,4 | 2/5 |
| A3h + controesempi | 0,942 | 2,1 | 2/5 |
| A3i | 0,943 | 9,8 | 4/5 |
| A3i + controesempi | 0,953 | 2,7 | 3/5 |

  7.429 finestre sopra soglia diventano 166 eventi, rapporto 44,8.
- **Trabocchetto.** Gli F2 di questa tabella sono di una configurazione diversa dallo 0,857 della GRU con DTW. **Da controllare nel
  Cap. 5 quale classificatore la usa.**

## Board, regola d'allarme, latenza

- **Costi.** Percezione 116,38 ms (85,2%) + classificazione 19,51 ms (14,3%) = 136,65 ms, circa 7,3 fps.
- **YOLOv8-pose INT8 sulla NPU.** Più veloce (26,5 fps) ma con persona sdraiata conserva la posa nel 43,6% dei fotogrammi contro il
  79,1% di MediaPipe; F2 0,682. Esperimento su cinque soggetti, non ripetuto su dieci, e non separa modello e quantizzazione.
- **Prove continue.** Riferimento: 4,59 ore, nessuna sospensione, due interruzioni della camera per circa 5 s, riaperta in automatico,
  cadenza 7,26 fps. La sessione di 6,11 ore ha 68 minuti di sospensione (4,99 ore effettive) e serve solo per la temperatura (79,5 °C).
- **Regola** ([rileva.py:1013-1018](../deploy_board/rileva.py#L1013)):
  ```
  sopra = p >= soglia
  corsa = corsa + 1 se sopra, altrimenti 0
  allarme se corsa >= persistenza e (t - ultimo_allarme) >= sospensione
  ```
  Soglia 0,50, persistenza 5, sospensione 30 s, letti dal modello esportato.
- **9 settembre.** Quattro cadute simulate, tre riconosciute, due allarmi: una soppressa perché sei secondi dopo la precedente. Persona
  sul divano: quattro finestre sopra soglia, nessun allarme.
- **Latenza** a 8,02 fps: calcolo 0,125 s (3,2%), riempimento finestra 2,743 s (71%), persistenza 0,997 s (25,8%), totale 3,865 s.
  La latenza completa non è misurabile: manca l'inizio fisico della caduta.

## Trappole del controrelatore

- **11,1 eventi/ora contro 0,049**: nove sessioni domestiche (14,98 ore di tempo di parete) contro un dato di letteratura su 15.500
  ore. Basi diverse.
- **9,6 contro 14,98 ore**: tempo effettivo delle dodici registrazioni di agosto contro tempo di parete delle nove sessioni. Non si
  sommano.
- **4,59 contro 6,11 ore**: vedi sopra.
- **Privacy**: riduce la circolazione delle immagini, non garantisce l'anonimato.

## Limiti

Soglia, selezione DTW, K, altezza e controesempi influenzati dai dati osservati; DTW sull'intero dataset prima del LOSO; dieci soggetti e
un addestramento per fold; cinque cadute simulate in due abitazioni, nessuna validazione clinica; YOLOv8 su cinque soggetti; finestre in
campioni e non in secondi; prove di alcune ore e non di un giorno; consumo non misurato.
