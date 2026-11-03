# Preparazione della discussione — tre parti

Aggiornato il 5 ottobre 2026. Ogni affermazione è stata controllata contro il codice
(`src/`, `pipeline/`, `deploy_board/`, `config.py`) e contro i capitoli (`tesi/Cap1-6.tex`).
Il riferimento è scritto accanto a ogni punto; dove non ho potuto verificare lo dico.

- **Parte 1** — discorso riassuntivo, circa due minuti, da ripetere al controrelatore.
- **Parte 2** — spiegazione di ogni scelta: cosa, nel codice dove, come, perché, domanda probabile.
- **Parte 3** — discorso di 12 minuti, slide per slide, con tempi e contenuto della slide.

---

# PARTE 1 — Discorso riassuntivo (circa 2 minuti)

Il filo logico: **ogni scelta nasce da un problema scoperto nel passo precedente**.

> Il lavoro valuta un rilevatore di cadute basato sulla posa, che gira interamente su una scheda da
> circa cento euro, la Radxa ROCK 4D. L'elaborazione è locale: il video non va a un server. Non lo
> presento come garanzia di privacy, perché il sistema le immagini le vede comunque.
>
> La pipeline trasforma ogni fotogramma in 33 punti del corpo, e da quei punti ricava grandezze
> geometriche. Il classificatore quindi non vede pixel, ma una descrizione del movimento che posso
> interpretare. Ho confrontato tre rappresentazioni della posa, e ho aggiunto tre grandezze integrali
> perché la velocità istantanea si azzera appena la persona è a terra e perde la traccia dell'evento.
> Da 33 grandezze candidate ne tengo 12 con il Dynamic Time Warping, e le organizzo in finestre di 22
> campioni, perché una caduta si distingue da un sedersi solo guardandone l'evoluzione.
>
> Su questa base rispondo a tre domande. Prima: quanto conta l'architettura? Poco: tra i sei modelli
> la differenza è 0,032 di F2, contro 0,089 di variabilità tra soggetti, e dopo la correzione per
> confronti multipli nessuna differenza è significativa. Seconda: le prestazioni reggono fuori dal
> laboratorio? Solo in parte. Cambiando punto di vista F2 scende da 0,822 a 0,488, e su un dataset
> esterno arriva a 0,630. In casa emergono posture che il dataset non contiene, come le persone
> sdraiate su un divano: per questo ho aggiunto l'altezza del bacino dal pavimento e dei controesempi
> domestici, che riducono le finestre positive da circa 140 a 2,7 all'ora, al prezzo di una caduta
> riconosciuta in meno su cinque. Terza: la pipeline gira? Sì, a 7,3 fotogrammi al secondo, con la
> posa che occupa l'85% del tempo, e per 4,59 ore di prova continua. Poi c'è la regola d'allarme, con
> cinque finestre consecutive e 30 secondi di silenzio, che in una sessione ha soppresso una caduta
> vera riconosciuta dal modello.
>
> Dichiaro i limiti: soglia, selezione DTW, parametro K e controesempi sono stati influenzati dai
> dati osservati, le prove domestiche sono su due abitazioni e cadute simulate, e non sono una
> validazione clinica. Il contributo non è il classificatore migliore, ma aver seguito cosa cambia
> quando un sistema basato sulla posa esce dal benchmark ed entra in casa.

---

# PARTE 2 — Cosa è stato fatto, nel codice, come e perché

Ogni voce: **cosa** · **dove nel codice** · **come** · **perché** · **domanda probabile**.

## 2.1 Dati: UP-Fall

- **Cosa.** Dieci dei diciassette soggetti, 220 registrazioni (110 per telecamera), 100 di caduta e 120 di
  attività quotidiane, 116.362 fotogrammi. Due viste sincronizzate: laterale a altezza torace e frontale rialzata.
  [Cap3.tex:52](../tesi/Cap3.tex#L52)
- **Perché.** È un benchmark con cadute e attività quotidiane simili alle cadute, e con due punti di vista.
- **Domanda.** «Perché dieci soggetti e non diciassette?» Risposta: dieci per cui erano disponibili tutte le registrazioni
  nel formato usato; lo dichiaro come limite sul numero di soggetti.

## 2.2 Stima della posa

- **Cosa.** MediaPipe Pose restituisce 33 landmark per fotogramma, ciascuno con una visibilità.
- **Come.** Un motore per telecamera, con stato azzerato a ogni registrazione.
  [estrai_feature.py:221-295](../pipeline/estrai_feature.py#L221)
- **Perché.** Riduce l'ingresso da centinaia di migliaia di pixel a 33 punti, e le grandezze derivate si
  collegano a comportamenti osservabili: inclinazione del tronco, discesa del bacino.

## 2.3 Le tre rappresentazioni

- **A1.** Landmark 2D come nuvola di punti; matrice di covarianza, autovalori e autovettori
  (`np.linalg.eigh`, [geometry.py:357-363](../src/geometry.py#L357)). Dà orientamento ed allungamento dell'ellisse.
- **A2.** World landmark 3D di MediaPipe, origine al bacino. Profondità stimata da una sola immagine,
  quindi ricostruzione monoculare: non dà la posizione rispetto a stanza e pavimento.
- **A3.** Landmark 2D relativi al bacino, divisi per la lunghezza del tronco. Nove grandezze: lunghezza del tronco, angolo
  e sua variazione, altezza relativa di testa, ginocchia e caviglie, larghezza normalizzata, velocità dell'anca,
  velocità della testa rispetto all'anca. [Cap3.tex:412](../tesi/Cap3.tex#L412)
- **Perché tre.** Ognuna rinuncia a qualcosa di diverso: A1 conserva la posizione nella scena, A2 la profondità, A3
  l'indipendenza da posizione e corporatura ma perde il contesto.
- **Domanda.** «Perché A3 e non A2?» Nel confronto preliminare era su cinque soggetti, ed è dichiarato come preliminare;
  il confronto è stato ripetuto su dieci dopo una correzione ([Cap4.tex:234-256](../tesi/Cap4.tex#L234)).

## 2.4 Altezza del bacino dal pavimento (h_pav)

- **Cosa.** Una grandezza in più: la distanza del bacino dal pavimento, in lunghezze di tronco.
- **Come.** Il pavimento non è dato a mano: nei fotogrammi con persona abbastanza in piedi si prende il bordo inferiore
  del corpo e il centro dei fianchi, e si stima per minimi quadrati una retta `y_pav(x) = a·x + c`. La retta (non un livello
  costante) cattura la prospettiva. [geometry.py:274-340](../src/geometry.py#L274), [Cap3.tex:536-547](../tesi/Cap3.tex#L536)
- **Perché.** In casa una persona sdraiata sul divano ha una postura quasi uguale a una caduta, ma il bacino è più alto.
  Nei fotogrammi negativi con persona orizzontale l'altezza mediana è +0,02 tronchi nel dataset e +1,47 in casa
  ([Cap5.tex:650](../tesi/Cap5.tex#L650)).
- **Attenzione.** La DTW la **scarta**: punteggio 1,541 sulla laterale (secondo fra 33) ma 1,124 sulla frontale, quindi il
  minimo fra le viste la mette ventunesima. Viene reintrodotta come configurazione DTWH (12 + 1 = 13) perché il sistema
  installato usa la vista laterale. Non dire «non era abbastanza discriminativa».
  [Cap3.tex:668-670](../tesi/Cap3.tex#L668)
- **Limite.** Reintrodotta dopo aver visto falsi positivi in casa: il risultato sulle stesse registrazioni non è una verifica
  indipendente ([Cap5.tex:493](../tesi/Cap5.tex#L493)). Inoltre dipende dall'inquadratura. Sul campo la board aspetta di avere
  una stima del pavimento prima di decidere ([rileva.py:997-1004](../deploy_board/rileva.py#L997)).

## 2.5 Grandezze integrali e parametro K

- **Cosa.** Per ciascuna rappresentazione tre grandezze su una memoria di K = 31 campioni (circa 1,7 s a 18 fps):
  - **escursione** = massimo meno minimo dell'angolo del tronco;
  - **percorso** = somma delle distanze fra posizioni successive del punto seguito;
  - **discesa** = di quanto il punto è sotto il suo massimo recente.
  [geometry.py:539-545](../src/geometry.py#L539), [config.py:108](../config.py#L108)
- **Perché.** Appena la persona è a terra la velocità torna piccola e non ricorda più l'evento. Nell'esempio della tesi la
  velocità dell'anca va da 3,76 a 0,11, mentre la discesa accumulata resta a 1,40. L'autocorrelazione ρ₁ sale da 0,22–0,54 a
  0,82–0,99: sono grandezze molto più regolari.
- **Limite su K.** 31 fu scelto con un controllo che usava dati poi usati nella valutazione. Rifacendo la scelta senza il
  soggetto di test, nove fold su dieci scelgono K = 45 e F2 passa da 0,825 a 0,851 (+0,026, t = 2,22, sotto il valore critico
  2,26). Quindi 31 non ha gonfiato il risultato. [Cap4.tex:699](../tesi/Cap4.tex#L699)
- **Nota su A2.** Nelle integrali di A2 si segue il naso e non i fianchi: dalle origini dei fianchi percorso e discesa misuravano
  rumore ([geometry.py:150-155](../src/geometry.py#L150)).

## 2.6 Selezione con Dynamic Time Warping

- **Cosa.** Da 33 candidate a 12.
- **Come.**
  1. z-score per curva ([dtw.py:38](../src/dtw.py#L38)): le scale delle grandezze sono eterogenee.
  2. DTW fra curve della stessa classe e fra classi diverse. Il DTW confronta andamenti tollerando velocità diverse.
  3. Un punteggio per ogni telecamera e si tiene il **minimo**, `S_robusto = min(S_cam1, S_cam2)`.
  4. Si percorrono le feature in ordine di punteggio e si scarta quella con |ρ| ≥ 0,85 rispetto a una già scelta.
  Quattro scartate per ridondanza; correlazione media delle 12 scelte 0,435; otto sono integrali.
  [Cap3.tex:629-668](../tesi/Cap3.tex#L629)
- **Perché.** Molte candidate sono ridondanti o non distinguono caduta e attività quotidiana. Il minimo fra le viste evita di
  favorire grandezze che funzionano da un solo punto di vista.
- **Limite dichiarato.** La selezione è fatta una volta sull'intero dataset prima del LOSO: il soggetto di test contribuisce
  indirettamente alla scelta. È misurata nel Cap. 4 ([Cap3.tex:120](../tesi/Cap3.tex#L120)).

## 2.7 Preprocessing

| Passo | Cosa fa | Dove | Perché |
|---|---|---|---|
| Ordine per timestamp | I nomi dei PNG contengono l'istante; si ordina e si usano gli intervalli reali | [dati.py:273](../src/dati.py#L273), [estrai_feature.py:136-174](../pipeline/estrai_feature.py#L136) | Cadenza non costante: mediana 18,09 fps, da 14,43 a 19,63; in 70 registrazioni su 220 lo scarto supera il 5% |
| Stimatore azzerato per registrazione | Un nuovo stimatore a ogni ripresa | [estrai_feature.py:264-295](../pipeline/estrai_feature.py#L264) | MediaPipe è un tracciatore con stato: senza reset l'ultima posa di una ripresa influenza la prima della successiva. Fu un difetto trovato il 6 settembre: nessuna delle 866 righe di controllo coincideva con il dataset |
| Posa mancante | Si azzerano i buffer; una finestra non attraversa mai una perdita | [Cap3.tex:116](../tesi/Cap3.tex#L116) | Non collegare osservazioni separate da un buco |
| Log con segno | `segno(x)·log(1+|x|)` sulle colonne asimmetriche | [dati.py:152-205](../src/dati.py#L152) | Code lunghissime: la discesa di A3 ha un rapporto di 908 volte fra estremo e tipico |
| Standardizzazione | Media e deviazione calcolate nel training di ciascun fold, sui fotogrammi prima delle finestre | [Cap4.tex:121](../tesi/Cap4.tex#L121) | Il test non influisce sulla scala. Prima della correzione il classificatore non riconosceva nessun positivo: F1 = 0 |

## 2.8 Finestre e sottocampionamento

- **Cosa.** Si tiene un campione ogni due (da circa 18 a circa 9 al secondo); finestre di 22 campioni con passo 2.
  [dati.py:249-280](../src/dati.py#L249), [config.py:46,57](../config.py#L46)
- **Perché il sottocampionamento.** La pipeline sulla board non regge 18 fps (MediaPipe sulla CPU: 92,6 ms per fotogramma).
- **Perché le finestre.** Una caduta è un evento che si evolve: sedersi di colpo o raccogliere un oggetto possono avere una posa
  istantanea simile.
- **22 contro 44.** A 9 campioni al secondo sono 2,4 e 4,9 secondi. Con 44 F2 passa da 0,825 a 0,915 (+0,091, t = 3,62). Ho tenuto
  22 come compromesso con la tempestività: non è dimostrato ottimale. [Cap4.tex:437,358](../tesi/Cap4.tex#L437)
- **Sulla board.** La finestra avanza ogni `passo` fotogrammi: [rileva.py:982](../deploy_board/rileva.py#L982).
- **Attenzione.** Frequenza e finestra sono in campioni, non in secondi: a 6,47 fps la stessa finestra copre 3,40 s invece di
  2,44 s ([Cap5.tex:199](../tesi/Cap5.tex#L199)). È uno degli sviluppi proposti.

## 2.9 Etichette

- **Cosa.** Per fotogramma: 0 attività quotidiana, 1 transizione di caduta, 2 stato post-caduta. Per finestra, criterio K-su-M:
  transizione positiva con 5 fotogrammi su 8, post-caduta con 10 su 15. Questi valori non sono ottimizzati sul classificatore.
  [Cap3.tex:721-753](../tesi/Cap3.tex#L721)
- **Tre formulazioni** di addestramento: scartare le finestre di sola post-caduta, considerarle positive, oppure tre classi. Nella
  configurazione finale la transizione è l'evento positivo principale. La valutazione usa un'etichetta comune che vale 1 se c'è
  transizione o post-caduta, così le formulazioni si confrontano sullo stesso insieme.
- **Perché separare la post-caduta.** UP-Fall contiene l'attività «sdraiarsi» (20.980 fotogrammi, circa 18%). Se «a terra» fosse
  «caduta», il modello imparerebbe «orizzontale = caduta».
- **Le reti producono sempre una softmax**, anche nel caso binario: lo score di allarme è la probabilità della classe positiva,
  oppure, a tre classi, la probabilità di non essere nella classe normale ([Cap3.tex:847,864](../tesi/Cap3.tex#L847)).

## 2.10 Protocollo di valutazione

- **LOSO a dieci fold.** Un soggetto in test, uno in validazione, otto in training ([dati.py:25,317](../src/dati.py#L25)).
- **Metrica F2.** Pesa di più la recall, quindi le cadute mancate. Falsi positivi e falsi negativi restano distinti.
- **Seme fisso a 42**, un addestramento per fold, nessuna ricerca di iperparametri: la deviazione misura la variabilità fra soggetti,
  non fra inizializzazioni ([Cap3.tex:850](../tesi/Cap3.tex#L850)).
- **Soglia 0,50.** Si provò a sceglierla per fold sul soggetto di validazione: deviazione standard circa 0,37, quindi instabile. Si
  confrontarono sei regole sugli stessi fold e 0,50 fu la migliore. **Va detto così:** è stata scelta guardando i fold di test,
  quindi non è indipendente. Eccezione: la soglia «oracolo» usata solo come diagnosi su UR-Fall.
  [Cap4.tex:147-196](../tesi/Cap4.tex#L147)

## 2.11 I sei classificatori

- **Cosa.** Random Forest, LSTM, GRU, CNN 1D, Transformer, rete a grafo (sulle dodici grandezze come nodi, con adiacenza appresa).
  [modelli.py:56,431](../src/modelli.py#L56)
- **Random Forest.** 50 alberi; ogni finestra è riassunta con sei numeri per grandezza (media, deviazione, minimo, massimo, primo e
  ultimo campione: primo e ultimo conservano un po' di ordine) [modelli.py:364](../src/modelli.py#L364).
- **Risultati.** GRU 0,857, CNN 1D 0,838, Transformer 0,837, Random Forest 0,825 [Cap4.tex:302](../tesi/Cap4.tex#L302). Errori diversi:
  la LSTM ha la recall più alta (0,945, 82 falsi negativi) ma 1.266 falsi positivi contro i 938 della GRU; la Random Forest ha 468
  falsi positivi ma 232 falsi negativi.

## 2.12 Confronto statistico

- Fold per fold con la GRU come riferimento: Random Forest t = −1,24, Transformer −1,22, CNN −1,16, LSTM −2,98, grafo −3,14.
  Senza correzione, LSTM e grafo supererebbero il valore critico 2,26. Con **Bonferroni** sui cinque confronti il valore critico sale
  a circa 3,25 e nessuna differenza lo supera. [Cap4.tex:323](../tesi/Cap4.tex#L323)
- Numero di soggetti necessario: 52 per GRU contro Random Forest, 9 per GRU contro LSTM.
- **Non dire** che i modelli «sono equivalenti»: significa che con dieci soggetti non si distinguono.

## 2.13 Punto di vista

- Modello addestrato e valutato su Camera 1: F2 0,822 ± 0,099. Applicato a Camera 2: 0,488 ± 0,119 (perdita 0,334, circa tre volte la
  dispersione fra soggetti); i falsi positivi passano da 722 a 3.252. Con entrambe le viste in training: 0,731, falsi positivi 751.
  [Cap4.tex:807](../tesi/Cap4.tex#L807)
- **Perché succede.** La stessa postura del corpo, proiettata da un'altra posizione, produce feature diverse.

## 2.14 Trasferimento a UR-Fall

- UR-Fall è stato rielaborato con lo stesso stimatore e lo stesso calcolo delle feature: 11.400 fotogrammi, 67 registrazioni, 33
  feature. Le annotazioni, che descrivono soprattutto la postura, sono state mappate sulle tre fasi della pipeline.
  [Cap4.tex:824-828](../tesi/Cap4.tex#L824)
- Sottoinsieme DTW, soglia fissata su UP-Fall: F2 0,630. La degradazione ha due componenti: perdita di calibrazione (recuperabile con
  una soglia) e perdita di potere discriminante (no). Con soglia oracolo si recupera una parte.

## 2.15 Casa: grandezze integrali, altezza, controesempi

- **Controesempi domestici.** Attività normali registrate in casa che il sistema confondeva con cadute, aggiunte
  all'addestramento come negativi. [Cap5.tex:491](../tesi/Cap5.tex#L491)
- **Tabella** ([Cap5.tex:506-510](../tesi/Cap5.tex#L506)):

| Configurazione | F2 laboratorio | Finestre/ora in casa | Cadute |
|---|---|---|---|
| A3 | 0,898 | 139,9 | 3/5 |
| A3h | 0,931 | 70,4 | 2/5 |
| A3h + controesempi | 0,942 | 2,1 | 2/5 |
| A3i | 0,943 | 9,8 | 4/5 |
| A3i + controesempi | 0,953 | 2,7 | 3/5 |

- **Messaggio.** Sul benchmark ogni configurazione migliora e la differenza A3 → A3i + controesempi è 0,055, dello stesso ordine
  della variabilità fra soggetti. In casa le finestre positive scendono di circa 52 volte.
- **Costo.** Con i controesempi si perde una caduta su cinque (da 4/5 a 3/5).
- **Limiti.** Solo cinque cadute simulate; h_pav e controesempi scelti dopo aver visto gli errori in quelle registrazioni. Le
  finestre positive non sono allarmi: 7.429 finestre sopra soglia diventano 166 eventi, rapporto 44,8.
- **Trabocchetto.** Questi F2 (0,898–0,953) sono diversi dallo 0,857 della GRU con DTW. Sono configurazioni e classificatore
  diversi: non confrontarli fra loro. **Da controllare nel Cap. 5 quale classificatore usa questa tabella** prima di rispondere.

## 2.16 La board

- **Cosa.** Radxa ROCK 4D, webcam USB, MediaPipe sulla CPU, Random Forest. [deploy_board/rileva.py](../deploy_board/rileva.py)
- **Costi.** Per fotogramma: percezione 116,38 ms (85,2%) + classificazione ammortizzata 19,51 ms (14,3%) = 136,65 ms, circa 7,3 fps.
  La percezione è il collo di bottiglia: cambiare classificatore avrebbe effetto limitato. [Cap5.tex:183-199](../tesi/Cap5.tex#L183)
- **Perché Random Forest sul dispositivo.** Semplicità di esecuzione e meno dipendenze software, dato che nel confronto controllato
  il vantaggio delle reti era contenuto.
- **YOLOv8-pose INT8 sulla NPU.** Più veloce (26,5 fps), ma con persona sdraiata conservava la posa nel 43,6% dei fotogrammi contro il
  79,1% di MediaPipe; F2 0,682 contro 0,857 (−0,227). Esperimento su cinque soggetti, non ripetuto su dieci, e il confronto non separa
  l'effetto del modello da quello della quantizzazione. [Cap5.tex:85-102](../tesi/Cap5.tex#L85)
- **Nessun invio di rete.** Nel codice di `deploy_board` non ci sono chiamate di rete. Però la board **salva clip locali** intorno
  agli allarmi: le immagini esistono sul dispositivo. Nella prova del 6 settembre quelle clip non venivano ancora salvate.
- **Prove continue.** Quella di riferimento: 4,59 ore, nessuna sospensione del sistema operativo, due cadute di camera per circa 5
  secondi complessivi, riaperta in automatico, cadenza media 7,26 fps. La sessione di 6,11 ore ha 68 minuti di sospensione del
  sistema operativo (4,99 ore effettive), massima temperatura 79,5 °C: si usa solo per la temperatura.
  [Cap5.tex:208,222](../tesi/Cap5.tex#L208)

## 2.17 La regola di allarme

- **Dove.** Nel firmware: [rileva.py:1013-1018](../deploy_board/rileva.py#L1013).
  ```
  sopra  = p >= soglia
  corsa  = corsa + 1 if sopra else 0
  se corsa >= persistenza e (t - ultimo_allarme) >= sospensione: allarme
  ```
  Parametri: soglia 0,50, persistenza 5 finestre, sospensione 30 s, letti dal modello esportato.
- **Perché.** Una singola finestra positiva è rumore; cinque consecutive sono una condizione persistente. Il silenzio di 30 secondi
  evita notifiche ripetute per lo stesso episodio.
- **Costi.** Una positività breve può non raggiungere cinque finestre; una seconda caduta vicina può essere riconosciuta ma non
  segnalata. Il silenzio non sa quando un episodio finisce.
- **Il caso del 9 settembre.** Quattro cadute simulate, il classificatore ne riconosce tre, vengono emessi due allarmi: una caduta
  avviene circa sei secondi dopo la precedente ed è soppressa. Nella stessa sessione una persona seduta sul divano produce quattro
  finestre consecutive sopra soglia e nessun allarme, perché ne servono cinque. [Cap5.tex:435-450](../tesi/Cap5.tex#L435)
- **Prima di decidere** la board aspetta il riscaldamento e la stima del pavimento (circa 697 s all'inizio della sessione).

## 2.18 Latenza

- Non è misurabile per intero: serve l'inizio fisico della caduta. Si può stimare solo il tempo introdotto dalla pipeline a 8,02 fps:
  calcolo per fotogramma 0,125 s (3,2%), riempimento finestra 2,743 s (71,0%), persistenza 0,997 s (25,8%), totale 3,865 s.
  [Cap5.tex:459-481](../tesi/Cap5.tex#L459)
- Messaggio: la latenza dipende da lunghezza della finestra e persistenza, non dal calcolo.

## 2.19 Limiti da dire senza scuse

1. Soglia, selezione DTW, K, h_pav e controesempi sono influenzati dai dati osservati: il LOSO separa i soggetti ma non rende
   indipendenti le scelte precedenti.
2. Selezione DTW sull'intero dataset prima del LOSO.
3. Dieci soggetti, un solo addestramento per fold, nessuna ricerca di iperparametri.
4. Cinque cadute simulate in casa, due abitazioni: non è validazione clinica.
5. Il confronto con YOLOv8 è su cinque soggetti.
6. Frequenza e finestra espresse in campioni, non in secondi.
7. Prove continue di alcune ore, non di un giorno: la prova di 4,59 ore non copre una notte intera.
8. Consumo elettrico non misurato.

## 2.20 Cose che il controrelatore può cogliere

- «**11,1 eventi all'ora contro 0,049**»: base diversa. 11,1 viene da nove sessioni domestiche (14,98 ore di tempo di parete);
  0,049 è un dato di letteratura su 15.500 ore. Non confrontarli direttamente senza spiegarlo.
- «**9,6 ore o 14,98?**»: 9,6 è il tempo effettivo delle dodici registrazioni di agosto; 14,98 è il tempo di parete delle nove
  sessioni, con quella del 6 settembre. Non si sommano.
- «**4,59 o 6,11 ore?**» Vedi 2.16.
- «**La telecamera preserva la privacy?**» Riduce la circolazione delle immagini, non garantisce l'anonimato.

---

# PARTE 3 — Discorso di 12 minuti, slide per slide

Budget: 720 secondi, circa 130 parole al minuto, quindi circa 1.560 parole in tutto. **Il discorso che mi hai incollato è
molto più lungo (circa il doppio): a ritmo normale starebbe sui 22–25 minuti.** Questa versione è tagliata sul filo
«scelta → problema → misura» e sposta il resto nella Parte 2, da usare nelle domande.

I titoli non si pronunciano. Le pagine sono quelle del mazzo Canva già riordinato.

## Pagina 1 — Presentazione (30 s)
**Slide:** titolo, candidata, relatore, data. Niente altro.
> Buongiorno. Sono Caterina Cerretani e presento il mio lavoro sul rilevamento automatico delle cadute con la stima della
> posa. Parto da un confronto su un dataset controllato e arrivo al funzionamento in casa su un dispositivo edge: voglio capire
> cosa cambia quando cambiano le condizioni.

## Pagina 2 — Perché (35 s)
**Slide:** «1 su 5» in grande con la fonte PASSI d'Argento; grafico a barre dei luoghi delle cadute (casa 54%).
> Circa un anziano su cinque riferisce almeno una caduta in un anno, e la frequenza cresce con l'età. Una caduta pesa anche per il
> tempo trascorso a terra prima di ricevere aiuto, e in casa spesso nessuno sta guardando. Serve un sistema che osservi il
> movimento e segnali una possibile caduta.

## Pagina 3 — Approccio (40 s)
**Slide:** tre cerchi: indossabili, ambientali, telecamera + board.
> I dispositivi indossabili vanno portati e tenuti carichi; i sensori ambientali comprendono anche le telecamere. Io uso una
> telecamera RGB e una Radxa ROCK 4D che elabora tutto in locale, per circa cento euro. Il video non va a un server, e questo riduce
> la circolazione delle immagini, ma non è una garanzia di privacy: il sistema le immagini le vede comunque.

## Pagina 4 — Obiettivo (35 s)
**Slide:** tre requisiti: riconoscere le cadute, pochi falsi allarmi, funzionare in continuo con risorse limitate.
> Per essere utile il sistema deve riconoscere le cadute, contenere i falsi allarmi, perché troppi lo rendono inutilizzabile, e
> funzionare in continuo su un dispositivo piccolo. Ho studiato la pipeline a più livelli, e ogni passo verifica ciò che il
> precedente lascia aperto.

## Pagina 5 — Domande (50 s)
**Slide:** tre schede RQ1, RQ2, RQ3.
> Tre domande. Prima: quanto conta l'architettura del classificatore, a parità di dati, rappresentazione e protocollo? Seconda, la
> più importante: le prestazioni del benchmark si mantengono quando cambiano soggetto, punto di vista, dataset e ambiente? Molti studi
> riportano solo il benchmark. Terza: la pipeline completa gira in locale e in continuo, trasformando i punteggi in allarmi?

## Pagina 6 — Dall'immagine al movimento (80 s)
**Slide:** schema video → 33 landmark → feature → finestre; elenco A1/A2/A3 e «33 → 12 con DTW».
> MediaPipe restituisce 33 punti per fotogramma, e da lì ricavo grandezze geometriche: il classificatore non analizza pixel ma una
> descrizione compatta, che posso interpretare, per esempio l'inclinazione del tronco. Ho confrontato tre rappresentazioni: A1
> riassume i punti in 2D con un'ellisse; A2 usa i punti 3D stimati da MediaPipe; A3 li esprime rispetto al bacino e alla lunghezza
> del tronco, quindi meno dipendente da posizione e corporatura. In casa ho aggiunto l'altezza del bacino dal pavimento, perché una
> persona sul divano e una caduta hanno posture simili. E tre grandezze integrali, escursione, percorso e discesa su circa 1,7
> secondi, perché la velocità si azzera appena la persona è a terra. Da 33 candidate, con il Dynamic Time Warping ne tengo 12.

## Pagina 7 — Dati e protocollo (50 s)
**Slide:** UP-Fall: 10 soggetti, 220 registrazioni, 2 viste; schema LOSO 8/1/1.
> Uso UP-Fall: dieci soggetti, 220 registrazioni da due telecamere sincronizzate. Valuto con leave-one-subject-out: un soggetto in
> test, uno in validazione, otto in addestramento, e la normalizzazione è calcolata solo sul training. La metrica è F2, che pesa di più
> le cadute mancate, ma tengo distinti falsi positivi e falsi negativi. Separo anche la transizione di caduta dallo stato a terra,
> perché chi si sdraia volontariamente è a terra senza essere caduto.

## Pagina 8 — Lunghezza della finestra (50 s)
**Slide:** 22 e 44 campioni = 2,4 e 4,9 s; F2 0,825 → 0,915.
> Una caduta si distingue da un sedersi solo guardandone l'evoluzione, quindi uso finestre. Ho confrontato 22 e 44 campioni, cioè
> 2,4 e 4,9 secondi. Con 44 F2 sale da 0,825 a 0,915. Ho tenuto 22 come compromesso con la tempestività: la finestra va riempita
> prima di decidere. Non lo presento come ottimo.

## Pagina 9 — Il classificatore (55 s)
**Slide:** figura delle sei architetture con F2 medio e intervalli.
> Ho confrontato sei architetture. La GRU ha F2 medio più alto, 0,857, e la Random Forest 0,825: differenza 0,032, contro 0,089 di
> variabilità fra soggetti. Con la correzione di Bonferroni per cinque confronti nessuna differenza è significativa. Non significa
> che i modelli siano equivalenti: con dieci soggetti non si distinguono, e fanno errori diversi, la Random Forest meno falsi
> positivi della GRU ma più falsi negativi. L'architettura conta, ma da sola non risolve la generalizzazione.

## Pagina 10 — Fuori dal riferimento (55 s)
**Slide:** 0,822 → 0,488 → 0,731; UR-Fall 0,630.
> Il punto di vista pesa di più. Addestrato e valutato sulla vista laterale: 0,822. Lo stesso modello sulla frontale rialzata: 0,488.
> Con entrambe le viste in addestramento: 0,731. La stessa postura, vista da altrove, produce feature diverse. Su UR-Fall, dove
> cambiano soggetti, ambiente e acquisizione, il sottoinsieme DTW con la soglia fissa arriva a 0,630: conserva parte della
> capacità, ma il trasferimento è incompleto.

## Pagina 11 — Casa (60 s)
**Slide:** tabella configurazioni (F2 laboratorio, finestre/ora, cadute); schema della stanza.
> In casa compaiono situazioni poco presenti nel dataset, come persone sdraiate su letto o divano. Ho quindi aggiunto altezza dal
> pavimento, grandezze integrali e controesempi domestici. Sul benchmark F2 migliora solo di 0,055, ma in casa le finestre positive
> scendono da circa 140 a 2,7 all'ora. Il costo: da quattro cadute riconosciute su cinque a tre. Sono poche cadute simulate e scelte
> fatte guardando quegli errori: è un percorso di sviluppo, non una verifica indipendente.

## Pagina 12 — Dispositivo (60 s)
**Slide:** costi 116 ms + 19,5 ms ≈ 7,3 fps; grafico temperatura; YOLO 43,6% contro 79,1%.
> Sulla Radxa ho eseguito MediaPipe e una Random Forest, scelta per semplicità di esecuzione. Si arriva a circa 7,3 fotogrammi al
> secondo, e l'85% del tempo è la stima della posa. Ho provato YOLOv8 sulla NPU, più veloce, ma con la persona sdraiata conservava la
> posa nel 44% dei fotogrammi contro il 79% di MediaPipe. La prova continua di riferimento dura 4,59 ore, senza sospensioni del sistema
> operativo: mostra la fattibilità per alcune ore, non per giorni.

## Pagina 13 — Dall'allarme (55 s)
**Slide:** scheletro + andamento del punteggio; regola 5 finestre / 30 s.
> L'allarme scatta con cinque finestre consecutive sopra 0,50, poi trenta secondi di silenzio. Nella sessione del 9 settembre, con
> quattro cadute simulate, il classificatore ne riconosce tre ed emette due allarmi: una caduta, sei secondi dopo la precedente, è
> riconosciuta dal modello ma soppressa dalla regola. Una persona sul divano produce quattro finestre positive e nessun allarme.
> Quindi classificatore e logica di allarme vanno valutati separatamente, e il ritardo va misurato dall'inizio fisico della caduta.

## Pagina 14 — Conclusioni (55 s)
**Slide:** tre messaggi; limiti; sviluppi.
> La pipeline va giudicata nel suo insieme: le architetture differiscono poco rispetto ai soggetti, mentre punto di vista e ambiente
> pesano molto. L'esecuzione locale è fattibile. Dichiaro i limiti: soglia, selezione DTW, K, altezza e controesempi sono stati
> influenzati dai dati osservati, e due abitazioni con cadute simulate non sono una validazione clinica. Gli sviluppi: acquisizioni
> indipendenti, prove continue più lunghe, finestre definite in secondi. Il contributo è aver seguito cosa cambia quando un sistema
> basato sulla posa esce dal benchmark ed entra in casa.

## Pagina 15 — Chiusura (10 s)
> Grazie per l'attenzione.

**Totale: 720 secondi.** Se superi, taglia nell'ordine: pagina 8 (riducila a due frasi), poi 12, poi 3.

## Riserve (pagine 16–23)
Rappresentazioni A1/A2/A3 · grandezze integrali · sessione con finestre e allarmi · limiti in dettaglio · requisiti e metriche · tre
messaggi · fuga di informazione e soglia · basi di conteggio delle ore. Non si recitano.

---

## Cosa NON ho potuto verificare

- Quale classificatore e quali impostazioni usa la tabella delle configurazioni in casa (F2 0,898–0,953): controlla nel Cap. 5.
- La tabella dei numeri esatti per la prova continua del 6 settembre nei file di risultati della board (ho verificato il testo del
  Cap. 5, non i file `riepilogo.json`).
- Quanto dura davvero la lettura: i tempi sono stimati a 130 parole al minuto. Provala una volta ad alta voce con un cronometro.
