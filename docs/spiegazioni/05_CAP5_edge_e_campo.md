# Capitolo 5 — Implementazione su dispositivo edge e validazione in ambiente reale

**File:** `tesi/Cap5.tex` · **etichette:** `cap:edge` + alias `cap:campo` ·
**8.002 parole**, 9 sezioni, 9 sottosezioni.
**Codice:** `deploy_board/rileva.py`, `deploy_board/parita_frame.py`,
`pipeline/esporta_board.py`, `pipeline/eventi_sessioni.py`,
`pipeline/latenza.py`.
**Dati:** `risultati/sessioni/` (12 sessioni, 4,4 MB di punteggi),
`risultati/campo/*.json`.

Il capitolo nasce dalla **fusione** (26 agosto) del vecchio Capitolo 6
(deployment) con il vecchio Capitolo 7 (ambiente reale): due domande diverse —
*quanto costa* e *che cosa succede in una casa* — ma **lo stesso oggetto misurato
due volte**, e separarle costringeva a ripetere la descrizione della board in
entrambi i capitoli.

> **La cesura fra la prima e la seconda parte va segnata con un paragrafo di
> transizione, mai con un titolo:** un titolo la trasformerebbe in due mezzi
> capitoli.

---

# PARTE I — IL DISPOSITIVO

## 1. La piattaforma, e perché edge

**Radxa ROCK 4D**: SoC Rockchip RK3576, 6 GB di memoria, acceleratore neurale
integrato da 6 TOPS. **Costo dell'ordine del centinaio di euro**, telecamera USB
compresa.

| | nodo edge | server con GPU |
|---|---|---|
| calcolo | SoC ARM + NPU 6 TOPS | CPU x86 + GPU dedicata |
| costo per stanza | ~100 € | migliaia di € (condiviso) |
| rete richiesta | **nessuna** | flusso video continuo |
| dati in uscita | **solo allarmi** | fotogrammi |

**La differenza che conta non è il prezzo assoluto ma il costo per stanza.** Un
server si ammortizza su molte telecamere, ma richiede che ogni telecamera gli
mandi il proprio flusso: la scala abbatte il costo di calcolo e **moltiplica
quello di rete**, e soprattutto sposta fuori dall'abitazione dati che il Capitolo
1 ha argomentato debbano restarci. Un nodo autonomo non ha economia di scala, ma
il suo costo marginale è noto e la sua **superficie di esposizione è nulla**.

### I tre ostacoli del porting

Riportati perché un lavoro puramente simulativo non li incontra, e documentarli è
parte del contributo di un capitolo sul deployment. **Hanno una proprietà in
comune: nessuno dei tre produce un messaggio d'errore che indichi la causa.**

1. **L'architettura del processore.** Il RK3576 implementa **ARMv8.0**. I
   pacchetti MediaPipe recenti sono compilati per ARMv8.1 e usano le istruzioni
   atomiche **LSE**, assenti nel set precedente: l'esecuzione termina con
   `illegal instruction`, senza alcun messaggio che indichi la causa reale.
   **L'unica versione funzionante è la 0.10.9.**
2. **La rimozione di un'API.** MediaPipe 1.0 ha eliminato `mp.solutions`,
   l'interfaccia usata dal codice di estrazione. Aggiornare avrebbe comportato
   riscrivere l'intera catena di feature e **invalidare il confronto con tutte le
   misure precedenti**. La versione è stata congelata, ed è una decisione da
   dichiarare: **il sistema è vincolato a una libreria che gli autori considerano
   superata.**
3. **La forma statica del modello accelerato.** Il modello convertito per l'NPU
   accetta un tensore di forma fissa a quattro dimensioni. Fornendone uno a tre
   dimensioni **non si ottiene alcun errore**: l'inferenza semplicemente non
   viene eseguita, e la funzione ritorna in tempi bassissimi.

---

## 2. Verifica di equivalenza fra calcolatore e dispositivo

Prima di misurare **quanto è veloce** il sistema sul dispositivo, occorre
stabilire che calcoli **le stesse cose**.

| | |
|---|---:|
| scarto massimo sulle predizioni | $2{,}2 \times 10^{-16}$ |
| campioni divergenti | **0** |

È la precisione della rappresentazione in virgola mobile: i due sistemi sono
numericamente identici. Ripetuta sul pacchetto multi-persona: scarto massimo
esattamente nullo.

Nel codice è il primo comando da eseguire: `python3 rileva.py --parita`, che
confronta le predizioni su **duecento finestre precalcolate** in `parita.npz`. Se
divergono oltre 1e-6, le versioni di scikit-learn non sono compatibili e nessuna
misura successiva è valida. **Trenta secondi, contro il rischio di scoprire il
problema dopo dodici ore di registrazione.**

### Perché la verifica viene prima, e non dopo

Non è una formalità, e la ragione è che **tre misure distinte hanno riportato
come successo il proprio fallimento**, in forme diverse e tutte plausibili a
prima vista:

1. **Latenze identiche fra configurazioni diverse.** Quattro modelli di
   dimensione molto diversa producevano tempi indistinguibili. **Nessuna persona
   veniva rilevata** nei fotogrammi di prova: si stava cronometrando il ramo
   vuoto.
2. **1315 fotogrammi al secondo dichiarati.** Due ordini di grandezza fuori
   scala. L'input aveva **tre dimensioni invece di quattro** e l'inferenza non
   partiva affatto: il cronometro misurava una funzione che ritornava senza fare
   nulla.
3. **«Nove keypoint su nove trovati»**, con le ginocchia disegnate sul torace. Il
   criterio di validità era `x > 0 and y > 0`, **senza alcun controllo sulla
   confidenza**: qualunque coordinata numericamente lecita contava come
   rilevamento riuscito.

> **Un banco di prova che non verifica di aver svolto il lavoro misura il proprio
> fallimento e lo riporta come successo.**
>
> Regola operativa adottata dopo il secondo episodio e mantenuta fino alla fine:
> **la verifica di equivalenza precede sempre la verifica di velocità**, e nessuna
> misura di prestazione viene accettata prima che sia stato dimostrato che il
> calcolo è avvenuto.

---

## 3. Il confronto fra stimatori di posa, e la decisione contraria

Con MediaPipe sulla CPU il dispositivo **non regge il carico**: 92,6 ms per
fotogramma a livello di sistema, cioè **10,8 fps**. Il Capitolo 4 ha misurato che
a 9 fps le cadute non rilevate raddoppiano: la configurazione di partenza è già
sotto la soglia.

Questa sezione descrive la strada per farlo reggere — portare la percezione
sull'acceleratore, il che comporta **cambiare stimatore** — e si chiude con la
decisione di **non percorrerla**. Occupa lo spazio che occupa perché il lavoro
speso per ottenere quel risultato negativo è stato consistente, *e perché una
scelta verificata e smentita è un risultato, mentre una scelta assunta e mai
messa alla prova non lo è.*

### Il guadagno dell'acceleratore, e dove finisce

Sostituendo MediaPipe con **YOLOv8-pose quantizzato INT8 sull'NPU**, la *sola
inferenza* risulta **5,16 volte** più veloce. Ma la misura **a livello di sistema
dà 1,71**.

La differenza stava nella post-elaborazione: decodifica dell'uscita e
soppressione dei rilevamenti ridondanti, scritte in Python con cicli espliciti,
costavano **12,14 ms** — più di un terzo del tempo totale. Riscritte in forma
vettoriale scendono a **0,94 ms**, cioè **12,9 volte**, e il guadagno di sistema
sale a 2,17.

> È un esempio di **collo di bottiglia che si sposta**: accelerando la componente
> più costosa se ne rende dominante una che prima era invisibile. Il primo numero,
> 5,16, **non era sbagliato** — misurava esattamente ciò che dichiarava — ma
> rispondeva a una domanda diversa da quella che interessava.

### Il prezzo del cambio di stimatore

**YOLOv8 non localizza una persona distesa.** Ritenzione delle pose per tipo di
attività, su 29.681 fotogrammi:

| attività | YOLOv8 INT8 | MediaPipe |
|---|---:|---:|
| in piedi, sedersi, raccogliere, saltare | 100% | 100% |
| caduta in avanti sulle mani | 79,2% | 99,5% |
| **stare sdraiati** | **43,6%** | **79,1%** |

**Su tutto ciò che accade in piedi i due stimatori sono indistinguibili. Il
divario si apre solo sui corpi orizzontali** — cioè esattamente sulla fase
post-caduta, che è la più lunga e la più informativa.

**Non è una questione di soglia**, ed è stato verificato: scendendo a confidenza
0,05 la ritenzione su «stare sdraiati» arriva al 58,9%, ancora venti punti sotto.
*Il rilevatore non è prudente, semplicemente non trova la persona.*

**E dove la trova, la misura male.** La lunghezza del torso proiettata passa da
83,5 a 56,5 pixel fra postura eretta e a terra (**−32%**); con MediaPipe va da
83,8 a **100,7**. Su una telecamera laterale un torso che si distende **non deve
accorciarsi**: l'avvicinamento alla telecamera semmai lo allunga.

> Il punto è che `torso_len` è il **denominatore dell'intera normalizzazione
> body-centric**. Un suo errore non resta locale: si propaga a ogni feature del
> vettore, ed è **sistematico e correlato con la classe** — cioè la forma di
> errore peggiore possibile, perché **imita il segnale che si vuole misurare**.

### Il confronto a parità di protocollo

> Provenienza: i valori di $F_2$ vengono dall'impianto a **cinque** soggetti. Le
> misure di **tempo** non ne dipendono, perché prese sul dispositivo e non su un
> insieme di verifica: quelle restano valide come sono.

| stimatore | F2 | falsi positivi | falsi negativi |
|---|---:|---:|---:|
| MediaPipe | **0,909 ± 0,095** | **17** | **23** |
| YOLOv8 INT8 | 0,682 ± 0,044 | 225 | 59 |

Divario **0,227**, molto fuori dalle deviazioni: **è una delle poche differenze
misurate in questo lavoro che *non* cada dentro il rumore.**

### La catena che va in esercizio

Il confronto onesto non è a parità di dati ma **a parità di condizioni
operative**: ciascuna catena valutata al frame rate che raggiunge davvero.

| catena | sul dispositivo | F2 | FP | FN |
|---|---|---:|---:|---:|
| MediaPipe @ 18 fps | non raggiungibile | 0,898 | 23 | 24 |
| **MediaPipe @ 9 fps** | **10,8 fps** | **0,857** | **57** | **49** |
| YOLOv8 @ 18 fps | 26,5 fps | 0,682 | 225 | 59 |

**MediaPipe sottocampionato batte YOLOv8 a piena velocità di 0,175**, e lo batte
su ogni voce: recall 0,866 contro 0,775, FN 49 contro 59, FP 57 contro 225.

| | costo |
|---|---:|
| sottocampionare MediaPipe da 18 a 9 fps | −0,041 |
| cambiare stimatore di posa | −0,216 |
| **rapporto** | **5,3×** |

**Rinunciare a metà del frame rate costa cinque volte meno che rinunciare allo
stimatore.** Il sistema va quindi costruito su MediaPipe, con il modello
addestrato alla frequenza che il dispositivo regge davvero, così che
**addestramento ed esercizio coincidano** — ed è la ragione per cui
`config.py:45-46` definisce `FPS_ESERCIZIO = 9.0` e `FRAME_STEP = 2`.

**Il costo è dichiarato e non attenuato:** le cadute non rilevate passano dal
9,6% al 13,4%.

**Che cosa resta del lavoro sull'acceleratore.** La velocità dell'NPU è reale e
misurata. Non è quel lavoro a essere in discussione, ma il rapporto fra ciò che
fa guadagnare e ciò che fa perdere **su questo compito**. Resta la strada più
promettente se il divario dello stimatore si chiude, e le tre vie sono note: un
modello più grande della famiglia; un confronto in virgola mobile contro la
versione INT8 **per isolare la quantizzazione** — che oggi non è isolata, ed è un
limite dichiarato: *non si sa quanta parte dei 0,227 sia dovuta alla rete e
quanta alla quantizzazione*; e il rilevamento del contesto (dove sono i mobili),
che su un rilevatore di oggetti sarebbe quasi gratuito.

---

## 4. Il bilancio computazionale

| fase | tempo | quota |
|---|---:|---:|
| pre-elaborazione | 1,21 ms | 3,2% |
| **inferenza sull'acceleratore (percezione)** | **33,34 ms** | **88,4%** |
| post-elaborazione | 0,94 ms | 2,5% |
| classificatore (ammortizzato) | 2,20 ms | 5,8% |
| **totale** | **37,7 ms** | **26,5 fps** |

**Il classificatore — l'oggetto su cui si concentra la letteratura, e su cui si è
concentrato il Capitolo 4 — è il 5,8% del costo. Tutto il resto è percezione.**

Coerente con quanto misurato sull'accuratezza: fra la migliore e la peggiore
architettura corrono 0,066, dentro la dispersione fra soggetti, mentre fra due
punti di vista ne corrono 0,422. **Il classificatore è marginale due volte: nel
costo di calcolo e nella determinazione del risultato.**

### La nota sulle unità (richiesta esplicita del relatore, §8)

Il costo del classificatore compare con **due valori diversi**: 4,47 ms *per
finestra* nel capitolo dei risultati, 2,20 ms *per fotogramma* qui. **Non sono
due misure in disaccordo, sono la stessa misura in due unità**: la finestra
avanza con passo due, quindi si decide una volta ogni due fotogrammi, e il costo
ammortizzato per fotogramma è circa la metà di quello per finestra.

### ISS-113 — questi numeri non avevano un artefatto che li producesse (APERTA)

Cercando `33.34` e `33,34` in **tutti** i JSON, CSV, TXT e MD dei due progetti,
il valore **non compare in nessun file di risultato**. `benchmark_board.py`
**stampava a schermo e non salvava**: i valori erano stati trascritti da una
sessione di terminale.

> È una delle quattro richieste del relatore e una delle affermazioni di
> intestazione del lavoro (*«il collo di bottiglia non è la classificazione ma la
> percezione»*), quindi è anche **il numero che meno può permettersi di non
> essere rifacibile.**

**Intervento, prima metà (26 agosto).** Non si aggiunge un banco separato:
`deploy_board/rileva.py` misura ora le quattro fasi **dentro l'esecuzione vera**,
con `perf_counter` attorno a pre-elaborazione, percezione, post-elaborazione e
classificatore, e scrive il bilancio nel `riepilogo.json` insieme a tutto il
resto. **Il numero verrà quindi dalla stessa esecuzione che produce gli allarmi**
— è il solo modo perché non possa divergere dalla catena in esercizio. Riporta
anche il costo per finestra *accanto* a quello per fotogramma.

**Resta da fare: eseguirlo sulla board**, nella stessa sessione della prova
lunga. Verificato finora solo sul calcolatore.

---

## 5. Comportamento termico e i tre limiti che solo l'esercizio prolungato rivela

**La temperatura a regime.** Dieci minuti di carico continuo, 18.291 inferenze:
deriva della latenza **+3,9%**, frequenza dell'acceleratore invariata a 950 MHz,
temperature stabili fra 60 e 63 °C. Esteso a una sessione domestica: **cinque ore
continue**, picco di **79,5 °C** con andamento a plateau dopo ~40 minuti, frame
rate senza gradini.

> **L'assenza di gradini è il criterio**: un dispositivo che si rallenta da solo
> mostra cali bruschi, non una deriva lenta.

### I tre difetti

**1. Il costo del multi-persona cresce con le persone.** Lo stimatore esegue il
modello dei landmark **una volta per ogni persona rilevata**:

| | fps |
|---|---:|
| stanza vuota | 7,5 |
| una persona | ~4,0 |
| due persone | ~2–3 |

**Il degrado è massimo esattamente nella condizione che la modalità multi-persona
esiste per gestire.** A 4 fps una finestra di 22 campioni copre 5,5 secondi
invece di 2,4: il modello riceve una densità temporale mai vista in
addestramento. La correzione — riaddestrare con finestra più corta — è nota e non
eseguita.

**2. Il dispositivo si sospendeva da solo.** La gestione dell'energia sospendeva
la macchina dopo venti minuti senza interazione, **anche ad alimentazione di
rete**. In una sessione da cinque ore ha dormito **un'ora e nove minuti**.

> È il difetto peggiore possibile per una prova di durata, perché **non fallisce:
> sembra riuscire.** Il conteggio del tempo usa l'orologio monotòno, che durante
> la sospensione non avanza; al risveglio la registrazione riprende e alla fine
> dichiara la durata richiesta. **Un test notturno avrebbe prodotto un tasso di
> falsi allarmi eccellente e privo di significato.**

La correzione è banale — disattivare la sospensione — ma **il difetto non era
osservabile senza una sessione lunga e non sorvegliata**, ed è stato individuato
solo confrontando l'orologio da parete con quello di esecuzione. Il registratore
ora riporta **entrambi** (`time.time()` e `time.monotonic()`): la loro differenza
a fine sessione **è** il tempo in cui la macchina ha dormito, e se supera un
secondo il riepilogo lo dichiara in rosso e **marca la sessione come non valida
come prova di durata**.

*(Nello stesso intervento è stata corretta una collisione di nomi: `sospensione`
indicava sia il silenzio dopo un allarme sia la sospensione della macchina. Il
primo è ora `sospensione_regola`. È il genere di collisione che produce un numero
plausibile e sbagliato.)*

**3. La cattura si interrompe.** Il dispositivo di acquisizione viene rienumerato
dal sistema operativo (`/dev/video0` → `/dev/video1`), tipicamente al risveglio.
Senza sorveglianza la sessione **prosegue cieca fino alla fine**. La correzione
sposta la lettura in un flusso separato: se non arrivano fotogrammi entro venti
secondi, il ciclo principale lo dichiara e riapre il dispositivo. Nella sessione
da cinque ore è intervenuto una volta, recuperando in venti secondi ciò che il
giorno precedente era costato **otto minuti di cecità silenziosa**.

> **I tre difetti hanno una caratteristica comune: nessuno di essi produce un
> errore.** Producono numeri plausibili, e sono osservabili solo confrontando ciò
> che il sistema dichiara con **una grandezza indipendente** — l'orologio, il
> conteggio dei fotogrammi, la temperatura. È la stessa lezione della verifica di
> parità, incontrata una seconda volta in un contesto diverso.

### EXP-016 — le stesse 56 clip, sul PC e sulla board

| | PC | board |
|---|---:|---:|
| clip | 56 | 56 |
| allarmi emessi | 2 | **1** |
| pose valide (media) | 96,4% | 96,3% |
| scarto medio sul picco | — | 0,063 |
| correlazione | — | r = 0,781 |
| **clip concordi** | — | **55 / 56** |

**Le due macchine concordano sul comportamento, non sui punteggi.** La sola
divergenza è `evt_0067_155044`: il PC la classifica con punteggio saturo (1,000,
9 finestre sopra soglia, allarme emesso), la board si ferma a 0,560 e
l'antirimbalzo — che pretende cinque finestre consecutive — non emette l'allarme.
**Ed era una caduta vera.**

#### ISS-106 — la causa, e perché non è risolvibile

**Non è il classificatore**: la parità sulle finestre precalcolate è *esatta*,
scarto 0,000e+00. È lo **stimatore di posa, che è un tracciatore**: mantiene
stato fra fotogrammi, e differenze infinitesime nella decodifica dell'immagine si
amplificano lungo la sequenza.

| fotogramma | scarto medio sui landmark |
|---:|---:|
| 1 | 0,0001 |
| 11 | **0,0755** |

Non è un difetto di versione né di configurazione: **è la natura del componente**.
Le implementazioni delle operazioni in virgola mobile differiscono fra
architetture, e un sistema con stato le amplifica.

**Tre conseguenze:**

1. **La verifica di trasferimento deve partire dai *fotogrammi*.** La prova sulle
   finestre precalcolate è passata con scarto esattamente zero **pur mascherando
   l'unica divergenza reale**: è un punto cieco, non una prova.
2. **Le prestazioni misurate sul PC non sono le prestazioni della board.** Il
   recall va misurato sulla board.
3. **L'antirimbalzo amplifica la divergenza**: trasforma uno scarto continuo di
   punteggio in una decisione binaria diversa. È un costo del meccanismo,
   accettato consapevolmente.

---

# PARTE II — LA CASA

> *Fin qui il dispositivo è stato misurato per quello che costa. Da qui in avanti
> viene misurato per quello che fa, in una casa, per ore, con nessuno che cade.*

## 6. Perché il laboratorio non basta, e la previsione fatta prima

Quattro cose, **nell'ordine cronologico e non espositivo**: la ragione, la
previsione, il protocollo, e ciò che la prima ora ha mostrato. *L'ordine è
l'unica forma in cui la previsione conserva valore: una previsione registrata
dopo i fatti non è una previsione.*

### Il fenomeno è documentato, non ipotizzato

- **Bagalà et al.**: tredici algoritmi con sensibilità dichiarata 76–100% su
  cadute simulate → **57,0% ± 27,3** su ventinove cadute reali, e falsi allarmi
  fra **cinque e ottantacinque al giorno** a seconda dell'algoritmo.
- **OmniFall**: il modello addestrato su UP-Fall passa da **F1 72,9% in dominio a
  16,9% sulle cadute reali**; su Le2i il crollo è da 100% a 58,8%. E il collo di
  bottiglia è proprio la distinzione fra `fallen` e `lying`.

### Le due ragioni, di natura diversa

**La prima è la frequenza di base**, ed è quantificabile a priori.
**La seconda è più insidiosa perché non si vede finché non si va a misurare: il
dataset non contiene le situazioni difficili dell'ambiente di destinazione.**
UP-Fall non ha divani, non ha più persone in scena, e le sue persone orizzontali
che non sono cadute **stanno a terra invece che rialzate**.

> **Ogni intervento progettato per una condizione che il dataset non rappresenta
> viene giudicato da quel dataset come un peggioramento.**

### La previsione — scritta prima della prima sessione

Il modello di riferimento produce ~46 falsi positivi su 4.767 finestre negative,
cioè **0,96% per finestra**. In laboratorio, con le positive al 4,5%, quello
0,96% corrisponde a una **precision di 0,819** — un numero che si presenta bene.

In un soggiorno la quota di finestre positive è ~0%. Proiettando lo stesso tasso:

| modalità di finestratura | finestre/giorno | falsi allarmi/giorno |
|---|---:|---:|
| finestre non sovrapposte | ~34.560 | ~332 |
| finestre con stride 5 | ~311.000 | ~2.990 |

cioè **fra 14 e 125 falsi allarmi all'ora**.

> **Il punto metodologico: la precision non è una proprietà del modello.** Dipende
> da quanto sono frequenti gli eventi positivi nell'insieme su cui la si calcola.
> Riportare una precision misurata su un insieme quasi bilanciato come se
> descrivesse il comportamento in esercizio è un errore diffuso in letteratura, e
> qui viene quantificato con dati propri.

Il termine di paragone esterno: il criterio che circola come soglia di
accettabilità clinica è **95% delle cadute con al massimo uno o due falsi allarmi
alla settimana**. I sistemi realmente installati riportano 73% di sensibilità con
un falso allarme ogni quarantasei giorni, oppure 80% con uno ogni venti giorni.
**Fra la previsione di 14–125/ora e il bersaglio di uno o due alla settimana ci
sono tre o quattro ordini di grandezza, e non si colmano migliorando il
classificatore.**

### Il protocollo delle sessioni

**Dodici blocchi, quattro giornate, due abitazioni, 9,6 ore complessive.** I
partecipanti sono familiari dello studente, informati e consenzienti; il relatore
è stato informato della natura della raccolta.

**La telecamera è montata lateralmente a 1,5–2 m di altezza.** Non è una scelta
di comodo: **discende direttamente dal risultato del Capitolo 4**, dove il
passaggio da vista laterale a frontale rialzata dimezza l'accuratezza.

Tre tipi di blocco:

- **vita normale** — fornisce il denominatore dei falsi allarmi, ed è l'unico
  tipo registrato a casa dei nonni;
- **cadute recitate**, con orari annotati dall'operatore — fornisce il recall;
- **trappole** — attività costruite per far sbagliare il sistema: sdraiarsi sul
  divano, sedersi di scatto, chinarsi, stare a terra volontariamente, più persone
  in campo.

**Etica e privacy come contenuto, non come adempimento.** Il registratore salva in
modo continuo **soltanto posa e feature: mai il video**. Le immagini restano solo
in una finestra di pochi secondi attorno agli allarmi, restano sul dispositivo e
non entrano nel repository. *È il privacy-by-design argomentato nel Capitolo 1
dimostrato in pratica invece che dichiarato — e ha richiesto di rimuovere dal
prototipo una registrazione video continua che era stata aggiunta per comodità di
sviluppo e che contraddiceva l'argomento stesso della tesi.*

**Un limite dichiarato perché limita i risultati: i partecipanti anziani non
eseguono cadute recitate.** Nei loro blocchi c'è soltanto vita normale. La ragione
è di sicurezza, e la conseguenza è che **il recall non è mai misurato sulla
popolazione a cui il sistema sarebbe destinato**.

### La qualità delle sessioni: la colonna che dice più delle altre

| giornata | luogo | pose valide |
|---|---|---|
| **10 agosto** | casa dello studente | **0,6% – 39,8%** |
| 11 agosto | casa dello studente | 83,0% |
| 12 agosto | casa dei nonni | 86,8% – 99,3% |
| 13 agosto | casa dei nonni | 25,9% – 97,6% |

**Una sessione con pose valide sotto metà non misura il classificatore: misura
l'inquadratura.** Le sei sessioni del 10 agosto sono quelle con la telecamera
posizionata male — troppo vicina, troppo bassa, con il corpo che usciva
dall'inquadratura. **Non entrano in alcun risultato**, e non è una scelta: non
c'è niente da misurare. Restano perché documentano il difetto di posizionamento
(che è il motivo per cui esiste il protocollo di ripresa), perché contengono le
uniche prove di frame rate e multi-persona sul campo, e perché **una
registrazione fallita è un dato**.

### La prima ora, e cosa ha cambiato

Il primo blocco è durato trentanove minuti e ha prodotto **2.735 allarmi
all'ora**: **ventidue volte** il limite *superiore* della previsione.

> **Una previsione costruita per essere scomoda si è rivelata ottimistica di
> oltre un ordine di grandezza.** È il momento in cui il lavoro ha cambiato
> direzione.

Il dato che spiega il meccanismo è la distribuzione nel tempo:

| minuti | pose valide | allarmi |
|---|---:|---:|
| 0–15 (stanza vuota) | 0–29% | **0** |
| 15–25 | 76% | 105–124 |
| 25–35 | 76–99% | 454–462 |
| 35–40 (cadute) | 81% | 642 |

**Zero allarmi in quindici minuti di stanza vuota.** Il problema non è rumore di
fondo: **è che ogni movimento di una persona presente genera finestre positive**,
e a finestre sovrapposte un singolo evento ne produce decine.

---

## 7. Dalle finestre agli eventi — l'unità di misura

**È all'origine di gran parte dei numeri irriportabili del capitolo.**

Una singola caduta genera una **raffica** di finestre consecutive sopra soglia —
su una sessione registrata una sola caduta ne ha prodotte **centoventinove** — e
contarle come altrettanti allarmi non è una semplificazione: **è un errore di un
fattore misurato in 47,8**.

**La regola di allarme, dichiarata:** cinque finestre consecutive sopra soglia
perché venga emesso, **trenta secondi** di sospensione dopo l'emissione. Ogni
numero espresso in «eventi all'ora» adotta questa regola; **i numeri espressi in
«finestre all'ora» la precedono, e i due non vanno confrontati fra loro né con la
letteratura, che riporta eventi.**

> **Attenzione operativa.** Il file `eventi.csv` nelle sessioni contiene
> **finestre sopra soglia, non eventi** — il nome inganna, perché al momento della
> raccolta la regola non era implementata a bordo. Gli eventi si ricalcolano da
> `punteggi.csv` con `pipeline/eventi_sessioni.py`, che **non riesegue nessun
> modello**: rilegge le decisioni che la board ha davvero preso.

### Le due contabilità, e perché servono entrambe

**EVENTI** — la contabilità che descrive cosa sente l'utente, ed è quella
confrontabile con la letteratura.

**TEMPO IN ALLARME** — la quota di tempo in cui il punteggio sta sopra soglia.
Serve perché **il falso positivo dominante di questo progetto non è un evento**:
due persone anziane distese sui divani per un'ora sono uno **stato che dura**. La
sospensione lo ritaglia in eventi periodici e ne nasconde la natura — il numero
di eventi diventa una funzione del periodo di sospensione invece che del
fenomeno. La quota di tempo è la stessa qualunque sospensione si scelga, e dice
la verità: **il sistema ha passato il 40% del pomeriggio convinto che qualcuno
fosse caduto.**

*Riportare solo la prima nasconderebbe il problema; riportare solo la seconda non
sarebbe confrontabile con nessuno.*

### I numeri di campo

Nella sessione da cinque ore, dopo aver alzato la soglia: 41,7 finestre sopra
soglia all'ora, che diventano **3,41 allarmi all'ora contando gli eventi**.
Miglioramento di quasi tre ordini di grandezza rispetto alla prima ora, **e
ancora settanta volte** sopra gli 0,049 eventi/ora di Kangas et al.

**La terza sessione, a casa dei nonni: 1.635 allarmi all'ora — trentanove volte
la casa precedente**, a parità di configurazione, soglia e stimatore. La causa è
stata **osservata direttamente sui fotogrammi conservati attorno agli allarmi**:

> **due persone anziane distese su due divani, immobili, nel pomeriggio.**
>
> Non è un caso limite costruito per mettere in difficoltà il sistema; è la loro
> vita normale, ed è esattamente la popolazione a cui il sistema sarebbe
> destinato.

**Il filtro temporale non basta, e la ragione è strutturale.** La logica di
soppressione delle raffiche è progettata per **eventi**. Una persona distesa per
un'ora non è un evento ma uno **stato che dura**, e fa riscattare l'allarme a
ogni scadenza della sospensione. *Il filtro comprime le raffiche e non gli stati,
e in una casa con anziani il falso positivo dominante è uno stato.*

### La definizione del compito, misurata in abitazione

**La diagnosi contiene già la soluzione, in una direzione che non è quella del
filtro: se lo stato è il problema, il sistema non deve riconoscere lo stato.**

Stesse registrazioni, stessa regola di allarme, stessa soglia:

| compito | eventi/ora | cadute rilevate |
|---|---:|---:|
| **evento** — la transizione | **1,6** | 3/5 |
| stato — persona a terra | 29,5 | **0/5** |
| allarme — l'uno o l'altro | 36,4 | 4/5 |

**Un fattore ventitré sui falsi allarmi, al costo di una caduta su cinque.** Il
compito *stato*, che è la formulazione più diffusa in letteratura, è anche
**l'unico che in queste registrazioni non rileva alcuna caduta**: riconosce la
persona distesa sul divano e quella caduta a terra come la stessa
configurazione, e alla soglia dichiarata **satura sui divani**.

Il dato è coerente con il laboratorio, dove il compito *evento* sbaglia sullo
zero per cento delle finestre di persona distesa volontariamente. **Che la stessa
scelta produca lo stesso ordine in due contesti così diversi è la corroborazione
più solida di cui questo lavoro disponga.**

**Che cosa NON risolve:** un evento e mezzo all'ora resta lontano dagli 0,05
delle installazioni documentate, **di un fattore trenta**. E il compito *evento*
paga il proprio vantaggio esattamente dove costa di più: una caduta non rilevata
su cinque.

---

## 8. Il recall di campo, e i parametri impliciti

Sulle cinque cadute annotate, la configurazione di riferimento ne rileva
**quattro**. Il numero va letto con **tre riserve**.

1. **La numerosità**: cinque cadute non stimano un recall, danno un indizio.
2. **L'inquadratura era difettosa** in quella sessione — il corpo esce dal bordo
   inferiore in quattro casi su cinque (25,9% di pose valide).
3. **Quel «quattro su cinque» conta finestre, non allarmi.**

La terza è emersa solo ricontando gli allarmi nel modo in cui li conterebbe chi
usa il sistema. Il recall dipende da **due parametri dell'analisi che non erano
stati dichiarati**: la **tolleranza di accoppiamento** (entro quanto tempo dalla
caduta annotata un allarme conta come rilevamento) e la **persistenza** (quante
finestre consecutive servono perché l'allarme scatti).

| tolleranza | persistenza 1 | persistenza 5 |
|---|---:|---:|
| ±10 s | 0/4 | 0/4 |
| ±30 s | 2/5 | 1/5 |
| ±60 s | 3/5 | 1/5 |
| ±90 s | **4/5** | 1/5 |

**Il valore riportato finora si colloca nell'angolo più permissivo della
tabella.** Con parametri clinicamente difendibili — allarme entro mezzo minuto e
non su una finestra isolata — **il recall è una caduta su cinque**.

**Perché la tolleranza larga non è sostenibile**, tre ragioni: l'annotazione è al
minuto, quindi ±30 s è già generoso; in una sessione che produce centinaia di
finestre sopra soglia all'ora, **in una banda di tre minuti un allarme si trova
quasi sempre** e viene attribuito alla caduta anche quando è stato causato da
altro; e contraddice la motivazione clinica del Capitolo 1.

Sullo stesso criterio è stato ricontato l'archivio esterno: **su venti riprese di
caduta di UR-Fall il sistema non ne segnala nessuna.** Il conteggio per finestra
ne dava nove su 144; per evento dà zero, perché i punteggi si fermano appena
sotto la soglia e non vi restano abbastanza a lungo.

### Il terzo parametro implicito — l'osservazione metodologica

> **È la terza volta in questo lavoro che un numero di intestazione dipende da
> un'impostazione dell'analisi lasciata come costante:** dopo il sottocampionamento
> applicato alle sessioni e la media dei modelli della validazione incrociata al
> posto di quello installato, ora la tolleranza e la persistenza. **Tutte e tre
> nella direzione che migliora il risultato, e nessuna per scelta deliberata** —
> sono impostazioni ereditate da uno script all'altro.
>
> Il rimedio adottato è **esporle come parametri** e riportare il recall di campo
> come **intervallo con i parametri dichiarati, mai come numero singolo**.

### L'errore di misura che andava trovato prima di ogni confronto

La valutazione fuori linea dava **2 cadute su 5** dove la board, sugli stessi
eventi e con lo stesso modello, ne aveva segnalate **4**. *Due procedure che
guardano gli stessi dati non possono dare risultati diversi, e finché la
discrepanza non è stata spiegata nessun confronto fra configurazioni era valido.*

**Causa minore:** fuori linea si mediavano i modelli della validazione incrociata,
ciascuno addestrato su un sottoinsieme dei soggetti, mentre sul dispositivo gira
un modello addestrato su tutti. *(Corretto in `pipeline/esporta_board.py`, che
riaddestra su tutti i soggetti prima dell'esportazione.)*

**Causa decisiva:** l'analisi applicava alle sessioni **lo stesso
sottocampionamento usato su UP-Fall** — un fotogramma su due, per portare i 18
fps del dataset ai 9 su cui il modello è addestrato — **ma le sessioni sulla board
girano già a 7–8 fps**, e dimezzarle le porta a quattro. La finestra da 22
campioni copriva così **cinque secondi e mezzo invece di due e mezzo**, e la
caduta ci si perdeva dentro.

> **È lo stesso difetto già trovato e risolto sul lato hardware, ricomparso dal
> lato opposto della catena: introdotto dall'analisi invece che dal dispositivo.**

Corrette entrambe le cause, la configurazione di riferimento dà 4 su 5,
esattamente come la board — **e da quel momento i confronti valgono**.

---

## 9. Il risultato centrale: discordanza fra benchmark e comportamento reale

**Tre interventi progettati per la robustezza domestica**, tutti valutati con la
*stessa* procedura, sugli *stessi* modelli, su **due insiemi di verifica
diversi**: la LOSO su dieci soggetti di laboratorio, e sette ore di registrazione
continua in due abitazioni.

| configurazione | $F_2$ laboratorio | finestre/ora in casa | cadute |
|---|---:|---:|---:|
| A3 — riferimento | 0,898 ± 0,075 | 139,9 | 3/5 |
| A3h — con l'altezza | 0,931 ± 0,051 | 70,4 | 2/5 |
| A3h + controesempi | 0,942 ± 0,060 | **2,1** | 2/5 |
| A3i — con gli integrali | 0,943 ± 0,064 | 9,8 | **4/5** |
| **A3i + controesempi** | **0,953 ± 0,055** | 2,7 | 3/5 |

*(La colonna centrale conta **finestre** sopra soglia, non eventi: si usano qui
perché è la grandezza su cui le cinque configurazioni sono direttamente
confrontabili, non perché sia quella da riportare.)*

### Il ritiro del «rovesciamento» — e perché va detto subito

**Una versione precedente di questo lavoro sosteneva il contrario.** Con cinque
soggetti la configurazione A3h+controesempi risultava **la peggiore in
laboratorio** ($F_2 = 0{,}780$) e quasi la migliore in casa, e se ne era tratto un
**rovesciamento dell'ordine**.

Con dieci soggetti quella stessa configurazione ottiene **0,942**, e **le due
graduatorie non si contraddicono**: la peggiore in laboratorio è anche la
peggiore in casa.

> Il rovesciamento era in larga parte **un effetto della scarsità di dati**.
> Averlo scritto e poi smentito è, nell'economia di questo lavoro, un episodio
> della stessa storia che il capitolo sul protocollo racconta: **una differenza
> più piccola della dispersione fra soggetti non è una differenza**, e con cinque
> persone 0,780 e 0,917 non lo erano.

### L'enunciato che regge: ampiezza, non ordine

**Sul dataset di riferimento i due errori migliorano insieme.** Prima di leggere
lo scambio conviene guardare i due tipi di errore separatamente invece di
comprimerli in $F_2$:

| configurazione | $F_2$ | recall | falsi neg. | falsi pos. |
|---|---:|---:|---:|---:|
| A3 — riferimento | 0,898 | 0,929 | 45 | 172 |
| A3h | 0,931 | 0,962 | 22 | 137 |
| A3h + controesempi | 0,942 | 0,965 | 22 | 129 |
| A3i | 0,943 | 0,977 | 14 | 150 |
| **A3i + controesempi** | **0,953** | **0,980** | **14** | **124** |

**In laboratorio la configurazione finale non introduce alcuno scambio: migliora
entrambi gli errori. Lo scambio compare soltanto in casa** — ed è precisamente il
punto del capitolo.

| da A3 ad A3i + controesempi | in laboratorio | in casa |
|---|---|---|
| variazione | +0,055 di $F_2$ | da 139,9 a 2,7 finestre/ora |
| rapporto | — | **52×** |
| confronto con il rumore | **dentro** la dispersione (±0,06–0,08) | — |

> **La stessa coppia di configurazioni differisce di un fattore cinquantadue in
> una casa e di una quantità indistinguibile dal rumore in laboratorio. Il
> dataset di riferimento non sbaglia l'ordine: comprime una differenza enorme in
> una differenza che non si può dichiarare.**

**L'effetto pratico è identico a quello di un ordinamento errato.** Chi selezioni
la configurazione sulla base del solo $F_2$ di laboratorio **non ha alcuna ragione
statistica** per preferire A3i+controesempi ad A3: le due sono indistinguibili, e
la seconda è più semplice. Sceglierebbe la più semplice, **e installerebbe un
sistema che produce cinquantadue volte i falsi allarmi — avendo seguito la
procedura corretta fino in fondo.**

### La causa, misurata e non congetturata

| negativi orizzontali | quota | dove stanno |
|---|---|---|
| archivio di laboratorio | ~un quinto | **a terra** |
| sessioni domestiche | ~metà | **su una superficie rialzata** |

Altezza mediana del bacino fra i negativi orizzontali: **+0,02** lunghezze di
torso in laboratorio, **+1,47** in casa.

In laboratorio sdraiarsi sul pavimento è una delle azioni registrate come
attività ordinaria: lì «corpo a terra» non discrimina. In una casa chi è
orizzontale senza essere caduto sta quasi sempre su un divano, **e la distinzione
fra divano e pavimento è esattamente quella che serve — ed è quella che
l'archivio, non avendo divani, non può premiare.**

> **Un insieme di verifica non può misurare un miglioramento su una condizione
> che non rappresenta. Non si limita a sovrastimare le prestazioni: rende
> indistinguibili alternative che in esercizio differiscono di ordini di
> grandezza, e lo fa con la stessa apparente sicurezza con cui distinguerebbe
> alternative davvero equivalenti.**

### Il compromesso, e la riserva più seria

**I controesempi riducono le finestre in allarme di un fattore cinquantadue, ma
fanno scendere il recall da quattro cadute su cinque a tre.** Su A3h scendono a
due. **Non è un miglioramento: è uno scambio**, e in un sistema di sicurezza è lo
scambio nella direzione che pesa di più.

**E c'è di più.** I controesempi sono ricavati **dalle stesse abitazioni su cui il
sistema viene poi misurato**. La verifica incrociata — controesempi di una casa,
misura sull'altra — mostra che il beneficio **trasferisce ma dimezzato**, e che il
costo in recall **resta intero**:

- controesempi dei nonni, verifica a casa dello studente: da 0,342 a **0,171**
  eventi/ora;
- controesempi di casa dello studente, verifica dai nonni: da 1,781 a **0,890**.

Circa **un fattore due in entrambi i versi**. Con due sole abitazioni non è una
dimostrazione, ma fra le due ipotesi indica la prima: il modello ha imparato una
categoria trasferibile, non le caratteristiche della stanza.

> **I controesempi sono adattamento al dominio di installazione — *domain
> adaptation* — e non generalizzazione.** Sono utili, e vanno raccolti al momento
> dell'installazione come si tara un sensore; ma chiamarli robustezza sarebbe
> improprio, **e due abitazioni non bastano a dire quanto di quel beneficio
> sopravviva alla terza.**

*(La terminologia «adattamento al dominio» è entrata nel testo su richiesta
esplicita del relatore, §4 della sua email.)*

---

## 10. Lo stesso fenomeno su un iperparametro: la finestra di accumulazione

**È il caso in cui la discordanza è meno attesa e più facile da ignorare**, ed è
stato trovato **senza cercarlo** — perché a quel punto ogni configurazione veniva
misurata su entrambi gli insiemi.

> Provenienza: i valori di laboratorio vengono dall'impianto a **cinque**
> soggetti. Il fenomeno riguarda il confronto fra due colonne, non il valore
> assoluto dell'una.

$K$ era stato **scelto e non ottimizzato**, a 9.

| $K$ | F2 laboratorio | falsi neg. | falsi allarmi/ora | cadute |
|---:|---:|---:|---:|---:|
| 5 | 0,859 ± 0,125 | 23 | — | — |
| 9 | 0,896 ± 0,090 | 21 | 156,7 | 4/5 |
| 15 | 0,928 ± 0,048 | 24 | 137,6 | 4/5 |
| 22 | 0,963 ± 0,016 | 9 | 17,3 | 4/5 |
| **31** | **0,980 ± 0,020** | 4 | **14,0** | **4/5** |
| 45 | **0,987 ± 0,008** | **3** | 17,0 | **3/5** |

A $K = 31$ i falsi allarmi in casa scendono di un **fattore undici a parità di
recall**, e la dispersione fra soggetti passa da ±0,090 a ±0,020.

**La riga decisiva è l'ultima.** Da $K = 31$ a $K = 45$ **l'$F_2$ di laboratorio
continua a salire — ed è il valore più alto misurato in tutto il lavoro — mentre
sul campo si perde una caduta** e i falsi allarmi risalgono. *Ottimizzando sulla
sola metrica di laboratorio si sceglierebbe 45, cioè il valore sbagliato.*

**Perché non è un artefatto** (dichiarato esplicitamente perché sembra sospetto).
Per $K > 22$ la finestra di accumulazione supera quella di classificazione, quindi
le grandezze integrali riassumono fotogrammi **precedenti** alla finestra su cui il
modello decide. Ma:

- l'informazione è **solo passata**, quindi disponibile in tempo reale a un
  sistema che riceve fotogrammi in streaming;
- le grandezze si calcolano da geometria e **mai dalle etichette**;
- l'accumulazione **non attraversa il confine fra due riprese**;
- **la conferma sostanziale**: il miglioramento si osserva sulle **sessioni
  domestiche**, che non entrano in alcuna validazione incrociata e che il modello
  non ha mai visto.

**Resta da dichiarare che il campo di ricezione temporale effettivo passa da 2,4
a circa 5,8 secondi**: il sistema decide su ventidue campioni, ma le sue feature
riassumono più del doppio del tempo.

**Effetto collaterale interessante:** i controesempi domestici, che sopra le
feature vecchie erano dannosi anche in laboratorio, **sopra le grandezze
integrali diventano utili**. Non erano quindi dannosi in sé: **lo diventavano
quando il modello non aveva una dinamica affidabile con cui separare chi si
corica da chi cade**, e senza quella l'unica regola estraibile da centoventimila
fotogrammi di divano era «le persone orizzontali non cadono mai» — che cancella
anche i veri positivi.

---

## 11. Modalità di fallimento osservate

**Il modello non guardava la dinamica.** L'obiezione naturale al problema del
divano è che sdraiarsi e cadere hanno dinamiche diverse, e che il modello
dovrebbe distinguerle **senza sapere dove si trova il corpo**. La verifica ha
mostrato punteggi alti anche su corpi completamente immobili, con correlazione
fra punteggio e movimento effettivo **+0,139**. La causa non era il modello ma le
grandezze fornite (Capitolo 3). *Questa obiezione è arrivata dal relatore, ed è
la cosa che ha prodotto il contributo metodologico del Capitolo 3.*

**Il tracciamento multi-persona funziona e non è validabile.** Implementato con
identità e motore di feature indipendenti per ciascuna persona. Nell'unica
finestra in cui è stato messo alla prova — **291 fotogrammi con due persone
contemporaneamente visibili** — non ha prodotto alcuno scambio di soggetto. Ma
nessun archivio pubblico contiene più persone in scena: **UP-Fall ne ha una sola
nel 99,8% dei fotogrammi**. *La capacità che serve davvero in una casa è
precisamente quella che nessun dato di laboratorio può misurare, e settantun
secondi di prova non la sostituiscono.*

**Un filtro geometrico in addestramento peggiora il bilancio.** Il *Physics Guard*
del prototipo agiva solo in inferenza. Portato anche in addestramento, con soglia
a 110° sull'angolo del tronco, **riduce i falsi positivi da 141 a 65** — il valore
più basso ottenuto senza controesempi — **ma porta il recall da 0,941 a 0,872 e
raddoppia i falsi negativi**. Con una metrica che pesa il recall il doppio della
precision lo scambio è **netto negativo**, e i controesempi ottengono lo stesso
effetto sui falsi positivi senza costare recall.

*(Anche questa prova è stata suggerita dal relatore, e il risultato è negativo.
È uno dei tre risultati negativi dichiarati nell'Introduzione.)*

---

## 12. In sintesi, e che cosa resta aperto

Il sistema, nella configurazione ottimizzata, produce **14,0 falsi allarmi
all'ora** contando le finestre sopra soglia, e ne rileva **4 su 5 con il criterio
permissivo oppure 1 su 5 con quello clinicamente difendibile**. Entrambi restano
sopra il criterio clinico di uno o due alla settimana, **e questo va detto senza
attenuazioni: il sistema misurato in questo lavoro non è pronto per
l'installazione.**

> **Ma il capitolo non serviva a dimostrare che lo fosse.** Serviva a misurare la
> distanza, a spiegarne il meccanismo, e a mostrare che **quella distanza non è
> visibile dall'insieme di verifica su cui il settore misura** — il quale, anzi,
> avrebbe indicato la direzione opposta.

### Lavoro aperto su questo capitolo

1. **La prova di durata sulla board.** È l'ultima richiesta esplicita del relatore
   ancora aperta. `rileva.py` ha ora il doppio orologio e dichiara la sospensione,
   quindi il difetto che aveva invalidato silenziosamente il primo tentativo è
   rilevabile. **Nella stessa sessione si chiude anche ISS-113**: il bilancio del
   costo per fotogramma esce dal `riepilogo.json` della prova stessa.
2. **Più cadute reali.** Con cinque, l'intervallo di confidenza sul recall va da
   **0,28 a 0,99**. È il limite più serio del lavoro. E la sessione da cui vengono
   tutte e cinque ha il **25,9% di pose valide**, peggio di sessioni che sono state
   scartate: **rifarla con l'inquadratura giusta è l'intervento a costo più
   basso.**
