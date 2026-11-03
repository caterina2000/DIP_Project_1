# Discorso di discussione — versione di riferimento (15 slide)

Versione del 5 ottobre 2026, costruita sui sei capitoli. **Sostituisce**
[DISCORSO_18_SLIDE.md](DISCORSO_18_SLIDE.md) e la Parte D di
[GUIDA_DIFESA.md](GUIDA_DIFESA.md): quelle due riportavano i valori di $F_2$ della
mail di agosto (LSTM 0,858, GRU 0,847), superati dai valori attuali del Cap. 4.

I titoli servono a orientarsi durante le prove e non vanno pronunciati.

---

## Slide 1 — Presentazione del lavoro

Buongiorno a tutti. Sono Caterina Cerretani e oggi presenterò il mio lavoro di tesi sul rilevamento automatico delle cadute attraverso la stima della posa.

Il lavoro segue un percorso che parte dal confronto tra modelli su un dataset controllato e arriva al funzionamento della pipeline su un dispositivo edge, in ambiente domestico. L'obiettivo è capire quali fattori influenzano il sistema quando cambiano le condizioni in cui deve operare.

## Slide 2 — Perché rilevare le cadute

Partiamo dal problema. Per una persona anziana, una caduta può compromettere la salute e l'autonomia, soprattutto quando si trova sola e non riesce a chiedere aiuto.

Secondo i dati PASSI d'Argento riportati nella tesi, circa un anziano su cinque riferisce almeno una caduta nei dodici mesi precedenti, e la frequenza aumenta con l'età.

In ambiente domestico, dove manca una supervisione continua, diventa quindi utile un sistema capace di osservare il movimento e segnalare una possibile caduta. La finalità è supportare una richiesta di assistenza tempestiva e aiutare la persona a mantenere la propria autonomia.

## Slide 3 — Tecnologie e approccio adottato

Esistono diverse soluzioni per questo monitoraggio. I dispositivi indossabili misurano il movimento direttamente sul corpo, ma richiedono che la persona li indossi e li mantenga carichi. Altre soluzioni utilizzano sensori installati nell'ambiente, tra cui sistemi basati su telecamere.

Nel mio lavoro ho scelto una telecamera RGB collegata a una board che esegue localmente l'elaborazione. Il terzo cerchio mostra quindi come viene realizzato il monitoraggio video nel progetto.

Questa architettura evita la necessità di inviare continuamente il video a un server esterno. Riduce la circolazione delle immagini, pur senza garantire automaticamente l'anonimato o una protezione completa della privacy.

## Slide 4 — Obiettivo della tesi

Per essere utile, il sistema deve riconoscere le cadute, contenere i falsi allarmi e funzionare con le risorse disponibili sul dispositivo.

Ho quindi studiato la pipeline a più livelli: prima attraverso confronti controllati, poi cambiando le condizioni di acquisizione e infine osservandone il funzionamento continuo in casa. Ogni passaggio permette di verificare un aspetto che il precedente lascia aperto.

## Slide 5 — Domande di ricerca

Questo percorso è organizzato intorno a tre domande.

La prima è quanto conti l'architettura del classificatore, mantenendo fissi rappresentazione del movimento, dati e protocollo.

La seconda è quanto le prestazioni ottenute sul benchmark si mantengano quando cambiano il soggetto, il punto di vista, il dataset e l'ambiente.

La terza riguarda il dispositivo: la pipeline completa può funzionare localmente e in modo continuo, trasformando le classificazioni in eventi di allarme?

## Slide 6 — Dall'immagine alla descrizione del movimento

Per rispondere a queste domande, ho costruito la pipeline mostrata nella slide.

Ogni fotogramma RGB viene elaborato da MediaPipe Pose, che restituisce 33 landmark anatomici. Da questi punti ricavo feature geometriche e temporali: il classificatore riceve quindi una descrizione numerica del movimento.

Ho considerato tre rappresentazioni: A1 descrive la forma del corpo nel piano immagine; A2 utilizza i world landmark tridimensionali stimati da MediaPipe; A3 esprime le coordinate rispetto al bacino e alla lunghezza del tronco, riducendo la dipendenza dalla posizione e dalla scala apparente della persona.

Alle feature geometriche e cinematiche ho aggiunto percorso, escursione e discesa, che descrivono il movimento su un intervallo più ampio. Per esempio, la discesa del bacino conserva l'informazione sullo spostamento verso il basso anche quando la velocità istantanea torna piccola.

Complessivamente sono state considerate 33 feature candidate, includendo anche l'altezza del bacino rispetto al pavimento. Una selezione basata sul Dynamic Time Warping le ha ridotte a 12, confrontando la somiglianza degli andamenti temporali nelle cadute e nelle attività quotidiane.

Le feature selezionate vengono organizzate in finestre, che il classificatore analizza per produrre uno score. La logica temporale utilizza infine questi score per generare gli allarmi.

## Slide 7 — Dati e protocollo sperimentale

Come riferimento ho utilizzato UP-Fall, considerando dieci soggetti e 220 registrazioni: 110 per ciascuna delle due telecamere sincronizzate. Si tratta quindi di due osservazioni degli stessi episodi da punti di vista differenti.

Il confronto principale tra classificatori usa la prima telecamera e un protocollo leave-one-subject-out: in ogni prova, otto soggetti sono destinati al training, uno alla validazione e uno al test. Anche la normalizzazione viene calcolata soltanto sui dati di training.

Per la valutazione ho scelto F₂, che attribuisce maggiore peso al recall, quindi alla capacità di riconoscere le finestre positive. Ho comunque mantenuto distinti falsi positivi e falsi negativi, perché due modelli con un punteggio simile possono produrre errori diversi.

Inoltre, ho distinto la transizione di caduta dallo stato successivo a terra: una postura orizzontale può comparire anche quando una persona si sdraia volontariamente, quindi la definizione della classe positiva modifica il compito richiesto al modello.

## Slide 8 — Lunghezza della finestra e risposta del sistema

Una scelta importante riguarda la quantità di storia temporale fornita al classificatore.

Ho confrontato finestre di 22 e 44 campioni. A circa nove campioni al secondo, corrispondono rispettivamente a 2,4 e 4,9 secondi. Nel confronto dedicato, la finestra più lunga migliora F₂ da circa 0,825 a 0,915.

Ho comunque mantenuto 22 campioni come compromesso tra riconoscimento e tempo necessario a rendere disponibile la sequenza. In un sistema di allarme, infatti, conta anche la tempestività della risposta.

La durata della finestra non coincide però automaticamente con il ritardo dell'allarme: durante il funzionamento la finestra scorre sui campioni già acquisiti, e il ritardo dipende anche dalla cadenza reale e dalla persistenza richiesta per attivare la segnalazione.

## Slide 9 — Quanto conta il classificatore

Con questa impostazione ho confrontato sei architetture: Random Forest, LSTM, GRU, CNN temporale, Transformer e una rete a grafo.

La GRU ottiene il valore medio più alto, con F₂ pari a 0,857. Tuttavia, il suo vantaggio rispetto alla Random Forest è di circa 0,032, mentre la deviazione standard tra soggetti per la GRU è 0,089.

Anche il confronto appaiato, dopo la correzione per confronti multipli, non evidenzia differenze statisticamente chiare. Questo non dimostra che i modelli siano equivalenti: indica che, nelle configurazioni e con i soggetti considerati, le differenze sono contenute rispetto alla variabilità tra persone.

Il risultato invita quindi a valutare, insieme al punteggio medio, anche il tipo di errore e la semplicità di esecuzione del modello.

## Slide 10 — Cosa cambia fuori dalle condizioni di riferimento

Il cambiamento del punto di vista produce un effetto più evidente.

Un modello addestrato e valutato sulla vista laterale raggiunge F₂ pari a 0,822. Applicandolo alla vista frontale rialzata, il valore scende a 0,488. Introducendo entrambe le viste durante il training, risale a 0,731.

La geometria della ripresa modifica quindi l'informazione disponibile: lo stesso movimento del corpo può produrre variazioni molto diverse nelle feature.

Ho poi verificato il trasferimento a UR-Fall, dove cambiano contemporaneamente soggetti, ambiente e acquisizione. In questa prova, il sottoinsieme selezionato con DTW raggiunge F₂ pari a 0,630, mantenendo la soglia di 0,50.

Il sistema conserva parte della capacità di riconoscimento, ma il trasferimento rimane incompleto. Il benchmark fornisce quindi un riferimento necessario, che va affiancato a prove in condizioni differenti.

## Slide 11 — Cosa emerge nell'ambiente domestico

Le prove in due abitazioni hanno permesso di osservare situazioni poco rappresentate nel dataset, come persone sdraiate su un letto o su un divano.

Queste posture possono assomigliare a quelle successive a una caduta. Per distinguerle ho analizzato l'informazione sul movimento, l'altezza rispetto al pavimento e l'introduzione di controesempi domestici, cioè attività normali che il sistema tendeva a confondere con cadute.

Nel confronto riportato, passando dalla rappresentazione A3 a quella con feature integrali e controesempi, le finestre positive scendono da circa 140 a 2,7 per ora. Sul benchmark, invece, il miglioramento di F₂ è di 0,055.

Una differenza relativamente contenuta nel laboratorio diventa quindi molto più evidente a casa. Rimane però un compromesso: rispetto alle sole feature integrali, aggiungere i controesempi riduce le cadute riconosciute da quattro su cinque a tre su cinque.

Questi dati descrivono il percorso di sviluppo su pochi eventi simulati. Inoltre, le finestre positive devono essere tenute distinte dagli allarmi effettivamente emessi.

## Slide 12 — Esecuzione sul dispositivo edge

Per verificare la fattibilità operativa ho eseguito l'intera pipeline sulla Radxa ROCK 4D, utilizzando MediaPipe e una Random Forest.

La Random Forest è stata scelta per la semplicità di esecuzione e per le minori dipendenze software, considerando che nel confronto controllato il vantaggio delle principali reti neurali era contenuto.

Ho valutato anche YOLOv8-pose quantizzato in INT8 sulla NPU. Era più veloce, ma nelle prove preliminari conservava meno frequentemente la posa quando la persona era sdraiata: circa il 44% dei fotogrammi, contro il 79% di MediaPipe. Ho quindi privilegiato la disponibilità dell'informazione utile al riconoscimento. Questo confronto riguarda la versione quantizzata provata e non permette di separare l'effetto del modello da quello della quantizzazione.

Nella configurazione installata, la pipeline completa raggiunge circa 7,3 fotogrammi al secondo. L'85,2% del tempo è occupato dalla stima della posa, che rappresenta il principale limite computazionale.

La prova continua di riferimento dura 4,59 ore, senza sospensioni rilevate del sistema operativo e con recupero automatico delle interruzioni della telecamera. Il risultato documenta la fattibilità per alcune ore, lasciando aperta la verifica su periodi più lunghi.

## Slide 13 — Dalla classificazione all'allarme

Il funzionamento continuo richiede un ultimo passaggio: trasformare gli score in segnalazioni.

Il sistema genera un allarme quando cinque finestre consecutive superano la soglia di 0,50. Dopo ogni allarme applica un intervallo refrattario di 30 secondi, durante il quale non ne emette altri.

Queste regole limitano le attivazioni brevi e le notifiche ripetute, ma influenzano anche il riconoscimento operativo.

Nella sessione mostrata sono presenti quattro cadute simulate: il classificatore ne riconosce tre, mentre il sistema emette due allarmi. Una caduta avviene circa sei secondi dopo la precedente e viene soppressa dall'intervallo refrattario, pur essendo riconosciuta dal modello.

Questo esempio rende evidente perché sia necessario valutare separatamente il classificatore e la logica che produce gli allarmi. Anche il ritardo complessivo deve essere misurato dall'inizio fisico della caduta: i soli tempi di calcolo non sono sufficienti a descriverlo.

## Slide 14 — Conclusioni, limiti e sviluppi

Il lavoro mostra che il comportamento del sistema dipende dall'intera pipeline. Le differenze tra le architetture risultano contenute rispetto alla variabilità tra soggetti, mentre il punto di vista e le condizioni domestiche producono cambiamenti importanti.

L'esecuzione locale è fattibile nella configurazione provata, ma la qualità della posa, la frequenza effettiva e le regole d'allarme rimangono determinanti.

Questi risultati hanno limiti precisi. Alcune scelte, tra cui la soglia, la selezione DTW, il parametro K e i controesempi domestici, sono state influenzate dai dati osservati durante lo sviluppo. La valutazione dell'intero processo non è quindi completamente indipendente. Inoltre, le prove in poche abitazioni e con cadute simulate non costituiscono una validazione clinica.

Gli sviluppi successivi riguardano nuove acquisizioni indipendenti in più ambienti, prove continue più lunghe e finestre definite in termini di tempo, per gestire meglio le variazioni della frequenza di elaborazione.

Il contributo della tesi è aver caratterizzato progressivamente questi fattori, mostrando che cosa cambia quando un sistema pose-based passa dal benchmark al funzionamento continuo in casa.

## Slide 15 — Chiusura

Grazie per l'attenzione.

---

## Corrispondenza con il mazzo Canva

Il mazzo è stato riordinato il 5 ottobre 2026: le prime 15 pagine corrispondono una a una alle slide del discorso (1 presentazione, 2 perché rilevare le cadute, 3 tecnologie e approccio, 4 obiettivo, 5 domande, 6 dall'immagine al movimento, 7 dati e protocollo, 8 lunghezza della finestra, 9 quanto conta il classificatore, 10 fuori dalle condizioni di riferimento, 11 ambiente domestico, 12 dispositivo edge, 13 dalla classificazione all'allarme, 14 conclusioni limiti e sviluppi, 15 chiusura).

**Riserve, dalla 16 alla 23** — non si recitano, servono per le domande: rappresentazioni A1-A2-A3, grandezze integrali, finestre e allarmi di una sessione, limiti in dettaglio, requisiti e metriche, i tre messaggi, fuga di informazione e soglia, le basi di conteggio delle ore.

## Verifica dei numeri (5 ottobre 2026)

Ogni valore pronunciato è stato ritrovato nei sorgenti della tesi.

| Valore | Dove |
|---|---|
| un anziano su cinque, PASSI d'Argento 2023-2024; 15% fra 65 e 74 anni, 31% oltre 85 | `Cap1.tex:55-60` |
| 0,049 allarmi all'ora su 15.500 ore (letteratura) | `Cap1.tex:163` |
| GRU 0,857; CNN 1D 0,838; Transformer 0,837; Random Forest 0,825 | `Cap4.tex:302-304` |
| differenza 0,032, deviazione fra soggetti 0,089 | `Cap4.tex:302` |
| finestra 22 → 44: F₂ da 0,825 a 0,915, recall da 0,849 a 0,945 | `Cap4.tex:437` |
| viste: 0,822 → 0,488 → 0,731; falsi positivi 722 → 3.252 → 751 | `Cap4.tex:807` |
| UR-Fall, sottoinsieme DTW: F₂ 0,630 alla soglia fissata su UP-Fall | `Cap4.tex:856, 866` |
| casa: finestre positive da 139,9 a 2,7 per ora, circa 52 volte meno; ΔF₂ 0,055; cadute 4/5 → 3/5 | `Cap5.tex:510, 515` |
| YOLOv8 INT8 sdraiato 43,6% contro 79,1% di MediaPipe; ΔF₂ 0,227 | `Cap5.tex:85, 102` |
| 7,3 fps, percezione 85,2% del tempo | `Cap5.tex:183-199` |
| prova continua 4,59 ore, nessuna sospensione, cadenza media 7,26 fps | `Cap5.tex:222` |
| finestra di 22 campioni = 2,44 s a 9 fps, 3,40 s a 6,47 fps | `Cap5.tex:199` |
| 11,1 eventi/ora su 14,98 ore e nove sessioni | `Cap5.tex:667`, `Cap6.tex:43` |

### Due avvertenze d'uso

- **Non accostare 11,1 eventi/ora a 0,049 allarmi/ora senza spiegare.** Il primo viene da nove sessioni domestiche con cadute simulate, il secondo da uno studio di letteratura su 15.500 ore d'uso. Popolazioni e basi di conteggio sono diverse. Il discorso qui sopra, correttamente, non li mette a confronto diretto.
- **Le ore.** 9,6 ore è il tempo effettivo delle dodici registrazioni di agosto; 14,98 ore è il tempo di parete delle nove sessioni, inclusa quella del 6 settembre. La prova continua di riferimento è 4,59 ore; la sessione di 6,11 ore è usata solo per la temperatura, perché sospesa per 68 minuti.
