# Simulazione d'esame — seduta del 22 ottobre 2026

Commissione: Garulli (presidente), Barni, Giannitrapani, Giorgi, Mecocci (relatore), Melacci (supplente).
Controrelatrice: Bianchini.

**Come usarla.** Le risposte sono scritte per essere dette a voce, in 20–40 secondi. Ogni numero viene dalla
tesi (capitoli 3, 4, 5, 6) e il capitolo è indicato. Dove la risposta è un ragionamento e **non** qualcosa che
la tesi ha misurato, c'è scritto «non misurato»: è il punto in cui la commissione può spingere, e conviene
ammetterlo prima che lo faccia.

Le corsie dei docenti sono dedotte da corsi e ricerca (Garulli: stima e filtraggio; Barni: statistica, teoria
dell'informazione, privacy; Giannitrapani: stima e controllo, robotica; Giorgi: architettura degli elaboratori;
Mecocci: elaborazione di immagini; Bianchini: apprendimento automatico; Melacci: deep learning, apprendimento
continuo). Per Giannitrapani, Bianchini e Melacci i corsi non sono verificati.

---

## 0. Le tre domande che arrivano comunque

**D. In due frasi: che cosa ha dimostrato la tesi?**
R. Che, a parità di rappresentazione e protocollo, la scelta dell'architettura conta poco rispetto alla
variabilità tra soggetti, mentre contano molto il punto di vista della camera, il dominio dei dati, la frequenza
di elaborazione e la regola che trasforma i punteggi in allarmi. Il contributo è la caratterizzazione di questi
fattori, non una architettura migliore delle altre. (Cap. 6)

**D. Il sistema funziona?**
R. Non lo dichiaro validato: è caratterizzato. In laboratorio, con LOSO su dieci soggetti, la GRU arriva a
F2 = 0,857. A casa le cadute sono cinque, tutte simulate, in due abitazioni: servono a far emergere i modi di
fallimento, non a stimare le prestazioni in servizio. (Cap. 5, §Protocol; Cap. 6, «How much we can generalise»)

**D. Qual è il limite più serio?**
R. Cinque cadute. Il recall è 4/5 con tolleranza ±60 s e una finestra positiva basta; con la regola
operativa (cinque finestre consecutive) è 2/5. L'intervallo di confidenza al 95% sul 4/5 va da 0,28 a 0,99.
La sessione che contiene le cadute ha inoltre solo il 25,9% di pose valide. (Cap. 5, §Recall)

---

## 1. Garulli — stima, filtraggio, sistemi dinamici

**D1. Perché non un filtro di Kalman sui landmark?**
R. Nessun filtro è stato applicato: l'EMA è stata considerata e non usata (Cap. 3, §Temporal filtering).
Le derivate contano poco nel modello finale: delle dodici feature, otto sono integrali, due statiche e solo due
sono derivate. Un Kalman a velocità costante attenuerebbe il *jitter*, ma non gli scambi di configurazione della
posa che persistono per più fotogrammi: su un divano la persona ferma produce un'escursione massima del tronco
di 93,5°, più della caduta (60,7°). E in caduta la dinamica non è a velocità costante. Non l'ho provato.

**D2. La frequenza va da 1,15 a 8,20 fps. Come gestisci il campionamento non uniforme?**
R. Le derivate usano il Δt vero dai timestamp, non quello nominale; rispetto al 18 fps fisso la differenza di F2
è −0,006 (t = −1,15). Non ricampiono, per non creare pose in istanti non osservati. Il limite è un altro:
finestra L = 22 e K = 31 sono in **campioni**, non in secondi. A 6,47 fps 22 campioni coprono 3,40 s invece di
2,44 s. La soluzione che indico è definire K come durata e ricavare i campioni dalla frequenza reale. Non
implementata. (Cap. 4 §Frame rate; Cap. 5 §Computational cost; Cap. 5 §K)

**D3. Il calcolo è causale?**
R. Sì. Le grandezze integrali usano un buffer circolare degli ultimi K campioni, azzerato quando la posa si
perde; lo stesso codice gira offline e sulla board. (Cap. 3, §Causal computation)

**D4. Persistenza e intervallo refrattario sono un filtro: che garanzie danno? Perché 30 s?**
R. Il ritardo introdotto dalla configurazione è 3,865 s a 8,02 fps: 0,125 s di calcolo, 2,743 s di riempimento
della finestra, 0,997 s di persistenza (5 finestre consecutive). I 30 s sono una scelta operativa, non
ottimizzata, e ha un costo che ho misurato: il 9 settembre la seconda caduta, sei secondi dopo la prima, è
stata riconosciuta dal classificatore ma soppressa dal refrattario. (Cap. 3 §Alarm; Cap. 5 §Latency)
Attenzione: la latenza *vera* dall'inizio fisico della caduta non è nota, perché le cadute sono annotate al minuto.

**D5. Come hai caratterizzato il rumore?**
R. Rumore gaussiano indipendente con σ frazione della lunghezza del tronco, fino a 0,04: la perdita massima
di F2 è 0,031, sotto la dispersione tra soggetti (circa 0,08). Ma questo è il rumore *facile*. Il caso difficile,
la posa che salta tra due configurazioni plausibili, non è rumore indipendente e il test non lo riproduce.
(Cap. 4 §Landmark noise)

---

## 2. Barni — statistica, informazione, privacy

**D6. Con cinque cadute, che cosa puoi dire sul recall?**
R. Quasi niente sul servizio reale. 4/5 = 0,80 con intervallo 0,28–0,99. E il 4/5 dipende dal criterio: con
persistenza 5 è 2/5; con tolleranza ±10 s è 0/5, ma le cadute sono annotate al minuto, quindi ±10 s non è
testabile. Il recall va sempre riportato con il criterio di associazione. (Cap. 5, Tab. associazione)

**D7. Soglia 0,50, selezione DTW e K=31 usano dati di valutazione. Non è data leakage?**
R. Sì, e lo dichiaro in Cap. 3 e 4. Quanto pesa: per K, ripetendo la scelta dentro ogni fold, nove fold su dieci
scelgono K = 45 e F2 passa da 0,825 a 0,851, quindi K = 31 non ha gonfiato il risultato (t = 2,22, sotto il
critico 2,26). Per le feature, nessun fold restituisce lo stesso sottoinsieme (Jaccard medio 0,769), ma sei
feature su dodici sono scelte in tutti i fold. **Non ho riaddestrato** con il sottoinsieme specifico di fold,
quindi l'effetto sulle metriche non è quantificato. Per la soglia, le regole basate sulla validazione danno
F2 0,787–0,823 contro 0,851 della soglia fissa: l'ordine di grandezza dell'ottimismo è questo.

**D8. Quali test hai usato per confrontare le architetture?**
R. t di Student appaiato fold per fold, cinque confronti contro la GRU; il valore critico corretto per
confronti multipli è circa 3,25 e nessuna differenza lo supera (la più alta è t = −3,14 per la rete a grafo).
Con questo campione l'assenza di differenza non è prova di equivalenza: per distinguere GRU e Random Forest
servirebbero circa 52 soggetti. (Cap. 4 §Architectures, Tab. sample size)

**D9. Perché DTW e non una misura informativa come l'informazione mutua?**
R. Perché le serie hanno forme che si deformano nel tempo, e il DTW confronta le forme. Non ho provato
l'informazione mutua. Il limite del criterio lo conosco: valuta ogni feature da sola. L'altezza delle anche è
al 21° posto con il minimo tra le due viste, ma sulla vista laterale è seconda (1,541). Per questo esiste la
configurazione DTWH. (Cap. 3 §DTW)

**D10. Dici che la posa riduce l'informazione identificabile. Non identifica comunque la persona?**
R. È un argomento di principio, non una analisi: non ho condotto uno studio di privacy. Quello che il sistema
fa è non trasmettere né salvare in continuo il flusso video; le immagini RGB si conservano solo in locale
attorno agli allarmi, per poter controllare gli errori. Andatura e proporzioni corporee restano nei landmark e
potrebbero in linea di principio identificare, ma non l'ho valutato.

**D11. Che prior hai sulla prevalenza e come cambia la precisione in servizio?**
R. Nel dataset il 12,72% delle finestre è positivo; in casa le cadute sono rarissime. Il 0,96% di falsi positivi
per finestra (46 su 4.767 negative) a stride 2 darebbe circa 3.751 finestre al giorno. Le finestre non sono
allarmi: nelle nove sessioni il rapporto finestre/eventi è 44,8 e gli eventi sono 11,1 all'ora. Non calcolo
un valore predittivo positivo perché non ho una stima credibile della frequenza reale di caduta.

---

## 3. Giannitrapani — stima e controllo

**D12. Come stimi l'altezza delle anche dal pavimento e che assunzioni fai?**
R. Dai fotogrammi con la persona in piedi raccolgo i punti (x del bacino, y del bordo inferiore del corpo) e
adatto una retta ai minimi quadrati: una retta e non una costante, per la prospettiva. Poi divido per la
lunghezza del tronco. Assunzioni: camera ferma, pavimento visibile, persona che cammina in più punti. Bias
dichiarato: il bordo usa tutti i 33 punti e le estremità escono dall'immagine, la retta si sposta di circa 12
pixel, un sesto del tronco. Se la camera si muove va ricalcolata. (Cap. 3 §Height above the floor)

**D13. Il riferimento al pavimento non c'è all'avvio.**
R. Vero, ed è un limite pesante: con h_pav attivo solo 36 sequenze su 422 (8,5%) producono una decisione. Nella
sessione del 9 settembre i primi 697 s sono senza decisioni. L'alternativa è calibrare il piano una volta in
installazione e salvare a e c; non l'ho implementata perché la retta salvata vale solo se la camera non si muove.

**D14. Perché non calibrare la camera, visto il crollo tra le viste (F2 da 0,822 a 0,488)?**
R. La normalizzazione di A3 toglie traslazione e scala, non la prospettiva; i world landmark di A2 sono
centrati sulle anche e non allineati alla gravità, quindi l'angolo del tronco non è un'inclinazione assoluta.
Non ho stimato i parametri intrinseci né estrinseci. Quello che ho misurato è che addestrare su entrambe le
viste riporta Camera 2 a 0,731: l'effetto si riduce, non sparisce.

**D15. Che cosa è osservabile da una sola camera?**
R. L'escursione del tronco dipende dalla vista: 74,0° laterale contro 33,2° frontale rialzata, e le sequenze
sopra 60° sono 30 su 39 contro 8 su 39. Una caduta lungo l'asse ottico perde la componente più informativa.
La camera del protocollo domestico è laterale, a 1,2–1,5 m.

**D16. Più persone?**
R. Il tracciamento per persona è stato esteso, ma l'unica sequenza con due persone ha 291 fotogrammi e nessuno
scambio di identità: troppo poco per validarlo. Il costo cresce: circa 7,5 fps con stanza vuota, 4 con una
persona, 2–3 con due. In 11 delle 50 cadute di Camera 2 lo stimatore perde la persona che cade e si aggancia a
un'altra in piedi. (Cap. 5 §Multiple people; Cap. 4 §Geometry)

---

## 4. Giorgi — architettura, embedded

**D17. Dov'è il collo di bottiglia?**
R. Nella percezione: 116,38 ms su 136,65 per fotogramma, 85,2%; il classificatore ne usa il 14,3%
(19,51 ms ammortizzati). Misurato sulla board nella sessione continua di 4,59 ore. Memoria: picco di 297 MB,
5% di quella disponibile, quindi non è un limite di capacità. Non ho fatto un profilo calcolo/memoria/larghezza
di banda: la misura è per stadio, non per risorsa.

**D18. Hai una NPU da 6 TOPS. Perché la posa gira sulla CPU?**
R. Con YOLOv8-pose INT8 sulla NPU l'inferenza è 5,16 volte più veloce e la catena arriva a 26,5 fps (37,7 ms),
ma la qualità peggiora: pose trattenute da sdraiati 43,6% contro 79,1%, F2 0,682 contro 0,909 (cinque soggetti).
MediaPipe resta sulla CPU: le versioni recenti danno *illegal instruction* (ARMv8.1 contro ARMv8.0 dell'RK3576),
quindi uso la 0.10.9. Limite: ho testato YOLOv8 solo in INT8, non separo l'effetto della quantizzazione da
quello dello stimatore. MediaPipe sulla NPU non l'ho provato.

**D19. La foresta impiega 39 ms a finestra sulla board. Non è troppo?**
R. Sul calcolatore lo stesso classificatore impiega circa 4,85 ms, quindi sulla board è circa otto volte più
lento; non ho fatto il profilo del perché. Un margine esiste: nella sensibilità al numero di alberi, 10 alberi
danno F2 0,850 contro 0,838 con 50, con un costo per finestra molto inferiore. Ho tenuto 50 alberi, ereditati dal
prototipo, perché il classificatore pesa il 14% del tempo e l'intervento giusto è sulla percezione.

**D20. Autonomia e termica?**
R. Dieci minuti: 18.291 inferenze, variazione di latenza 3,9%, 60–63 °C. Sessione dell'11 agosto: massimo
79,5 °C, assestata in circa quaranta minuti, senza *throttling* osservato. Prova di durata del 6 settembre:
4,59 ore continue. Il consumo **non è misurato**. Non copre una notte né 24 ore.

**D21. Perché il tempo non basta come metrica?**
R. Perché due misure sbagliate mi hanno insegnato a controllare: 1.315 fps misurati con un tensore di ingresso
a tre dimensioni invece di quattro, senza errore ma senza inferenza; e un confronto in cui i modelli avevano
tempi quasi identici perché non c'era nessuna persona nei fotogrammi. Da lì ogni misura è accettata solo
dopo aver verificato l'esecuzione e la coerenza dell'uscita. (Cap. 5 §Equivalence)

---

## 5. Mecocci — elaborazione di immagini (relatore)

**D22. Perché la posa e non una CNN sull'immagine?**
R. Tre ragioni: dimensionalità (poche coordinate invece di pixel), interpretabilità (ogni feature ha un
significato geometrico) e privacy. Il prezzo è che la qualità della posa diventa il limite: i modi di
fallimento in casa vengono quasi tutti da lì. Una CNN diretta sui pixel non è stata provata.

**D23. MediaPipe contro YOLOv8-pose: come li hai confrontati?**
R. Su 29.681 fotogrammi di attività diverse: in piedi, seduto, raccolta, salto 100% per entrambi; caduta in
avanti sulle mani 79,2% contro 99,5%; sdraiato 43,6% contro 79,1%. Anche la geometria cambia: il tronco proiettato
va da 83,5 a 56,5 pixel con YOLO, da 83,8 a 100,7 con MediaPipe, e la normalizzazione di A3 lo usa. Il confronto
su F2 è a cinque soggetti e non è stato ripetuto a dieci.

**D24. Quali casi falliscono?**
R. Persone sdraiate su superfici rialzate (la mediana dell'altezza delle anche nei negativi orizzontali è +0,02
lunghezze di tronco nel dataset, +1,47 in casa); scambi di configurazione della posa; Camera 2 che perde chi
cade; le sei sessioni del 10 agosto con 0,6–39,8% di pose valide, scartate perché la camera era troppo vicina.

**D25. Illuminazione, risoluzione, sfocatura?**
R. Non misurate: la tesi non contiene prove controllate su illuminazione o risoluzione. Le registrazioni
domestiche avvengono con la luce reale delle case, ma non l'ho variata.

---

## 6. Bianchini — apprendimento automatico (controrelatrice)

**D26. Perché la GRU, se non è significativamente migliore?**
R. Non affermo che sia la migliore. È quella con F2 medio più alto (0,857), con il 24% di parametri in meno
della LSTM, ma nessuna differenza supera la correzione. Sulla board uso la Random Forest: più semplice, niente
TensorFlow, 0,6 MB. (Cap. 4 §Architectures; Cap. 5 §Operating configuration)

**D27. Senza ricerca degli iperparametri, come puoi dire che le architetture si equivalgono?**
R. Non lo dico in generale: il confronto riguarda le configurazioni effettivamente usate, con una corsa per
fold e seme fisso 42. La dispersione che riporto misura i soggetti, non le inizializzazioni. È un limite
dichiarato anche in Cap. 6.

**D28. Perché F2, e chi sceglie β = 2?**
R. Perché in questo problema un falso negativo costa più di un falso positivo. β è stato fissato prima del
confronto tra modelli; recall, FN e FP sono riportati separatamente perché configurazioni con F2 simile
sbagliano in modo diverso: LSTM 82 FN e 1.266 FP, Random Forest 232 FN e 468 FP.

**D29. Come gestisci lo squilibrio?**
R. Pesi di classe inversamente proporzionali alla frequenza, calcolati sul solo training di ogni fold. Niente
sottocampionamento: pareggiare le classi eliminerebbe l'85,4% dei negativi, cioè gran parte delle attività
quotidiane. Positivi: 1.491 su 11.719 (12,72%).

**D30. Calibrazione: come separi perdita di calibrazione e perdita di capacità discriminativa?**
R. Sulla configurazione precedente, con la soglia fissata su UP-Fall F2 = 0,034 su UR-Fall; con la soglia
«oracolo» 0,492; nel dominio sorgente 0,971. Dei 0,937 punti persi, circa 0,457 si recuperano cambiando soglia
e circa 0,480 no. La scomposizione è stata fatta solo su quella configurazione, **non** sul sottoinsieme DTW,
per il quale ho solo il trasferimento diretto: PR-AUC 0,660, F2 0,630.

**D31. Overfitting?**
R. Early stopping sull'area della curva della probabilità d'allarme in validazione (pazienza 8, ripristino dei
pesi migliori), riduzione del learning rate, dropout 0,3, al massimo 40 epoche. La GRU ha 24.483 parametri su
circa 9.300 finestre di training molto sovrapposte. Non ho curve di apprendimento, e le finestre vicine non
sono osservazioni indipendenti: il numero di finestre sovrastima la dimensione del campione.

**D32. La rete a grafo: perché sta sotto?**
R. Nei miei nodi ci sono le dodici feature, non le giunture: non è una rete sullo scheletro. F2 = 0,794;
il risultato riguarda quella configurazione e non le reti a grafo in generale.

**D33. Il tuo F1 iniziale era 0.**
R. Per tre cause insieme: nessuna normalizzazione (rapporto fra scale 646×), split per registrazione con lo
stesso soggetto in train e test (5 su 5), e scelte dipendenti dai dati di verifica. Dopo la correzione F1 = 0,234
con 144 veri positivi. Non è attribuibile a un solo intervento e F1 non si confronta con gli F2 del resto.

---

## 7. Melacci — deep learning, apprendimento continuo (se interviene)

**D34. Adattamento di dominio o apprendimento continuo invece dei controesempi a mano?**
R. I controesempi sono una forma di adattamento supervisionato: portano gli eventi per ora da 0,342 a 0,171
(casa 1) e da 1,781 a 0,890 (casa 2), addestrando con i controesempi dell'altra casa. Apprendimento continuo sul
dispositivo richiederebbe etichette che all'installazione non ci sono. Non l'ho provato. Effetto collaterale
misurato: con A3i le cadute riconosciute vanno da 4/5 a 3/5.

**D35. Perché non il rilevamento di anomalie?**
R. Non provato. Il mio argomento: stendersi volontariamente è un'attività normale che termina in una postura
simile al post-caduta, e un modello a una classe tenderebbe a segnalarla; la dinamica della transizione
(velocità delle anche 30,1× rispetto allo stendersi, discesa 139,4×) è l'informazione utile.

**D36. Perché feature progettate a mano e non rappresentazioni apprese?**
R. Per interpretabilità e per il costo sul dispositivo. Sul benchmark le tre rappresentazioni sono quasi
indistinguibili (F2 tra 0,825 e 0,832): non ho evidenza che una rappresentazione appresa guadagnerebbe, e non
l'ho testato.

**D37. Le cadute simulate sono rappresentative?**
R. No, non del tutto: sia UP-Fall sia le cinque domestiche sono simulate e gli anziani non sono stati invitati
a cadere. Per questo il Cap. 6 dice che la validazione non è clinica.

---

## 8. Domande-trabocchetto per coerenza dei numeri

- **«Perché F2 di A3 è 0,831 al Cap. 4 e 0,898 al Cap. 5?»** Sono due tabelle diverse: la prima è Random Forest
  50 alberi, A3 senza integrali, dieci soggetti, definizione del positivo del §Compito; la seconda è il
  confronto di cinque configurazioni del §Comparison. *Non ho potuto verificare dai soli testi perché i valori
  differiscano; controlla la didascalia o la fonte prima di rispondere.*
- **«0,857» compare due volte**: GRU a dieci soggetti (Cap. 4) e MediaPipe a 9 fps, cinque soggetti (Cap. 5).
  Coincidenza, non lo stesso dato.
- **«Hai scelto L = 22 ma L = 44 dà 0,915.»** Sì, t = +3,62: la differenza è rilevabile con dieci soggetti. Tengo
  22 per la latenza (2,44 s contro 4,9 s di riempimento), che è il 71% del ritardo del sistema.
- **«Il tuo recall è 0,80.»** Con persistenza 1 e tolleranza ±60 s; con la regola operativa è 2/5.
- **«Il 90% dei cadute è riconosciuto?»** No: 0,94 è il recall sulle *finestre* della GRU nel dataset; non è un
  recall sugli *eventi*.

## 9. Che cosa faresti con più tempo

1. Più cadute reali in inquadratura corretta (il limite più serio).
2. Ripetere in casa il confronto fra architetture, fatto solo sul dataset.
3. Calibrare il pavimento in installazione, per togliere i primi minuti senza decisioni.
4. Definire K e L come durate, non come numero di campioni.
5. Provare una stima di posa più robusta a terra, e misurare il consumo.
