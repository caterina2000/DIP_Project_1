# Le richieste del relatore, e che cosa è stato fatto per ciascuna

> **Superato dal 7 settembre 2026.** Le risposte aggiornate stanno in
> **[docs/relatore/](relatore/INDICE.md)**: un testo unico
> ([RISPOSTE.md](relatore/RISPOSTE.md)) più una scheda per richiesta che
> racconta passo per passo come ci si è arrivati. Questo file è conservato
> per storia e **non viene più aggiornato**: i suoi numeri di campo sono
> fermi a prima che la sessione del 6 settembre entrasse nel conto.

Aggiornato al **6 settembre 2026**.

> ## Le correzioni del 6 settembre
>
> Nessuna richiesta è rimasta senza risposta. Ma in una giornata di verifiche
> **quattro risposte sono cambiate**, e tre di quei cambiamenti nascono dallo
> stesso componente: MediaPipe Pose è un tracciatore, e il progetto non aveva
> mai messo per iscritto che cosa comporta.
>
> **1. Il divario fra le due viste vale 2,23× e non 1,99×**, ed è misurato su
> dieci soggetti invece che su cinque — i fotogrammi delle due telecamere
> c'erano per tutti, la misura era rimasta a cinque solo perché fu fatta
> allora. Cade anche l'affermazione che «in 2 sequenze su 25 la vista rialzata
> osserva quanto quella laterale»: su trentanove ne resta una.
>
> **2. Il divario fra le viste ha due cause, non una.** Oltre alla compressione
> prospettica, **su Camera2 lo stimatore perde chi cade e si aggancia a
> un'altra persona in 11 riprese su 50** — su Camera1 in 0 su 50. Arriva anche
> nei dati di addestramento. Il capitolo ne dichiarava una sola.
>
> **3. Il dispositivo è 3,8 volte più lento di quanto il Capitolo 5
> dichiarasse**: 144,1 ms per fotogramma invece di 37,7, cioè 6,9 fps invece di
> 26,5. La misura viene ora da un file prodotto dall'esecuzione stessa, che era
> la riserva aperta su questo numero. Le proporzioni reggono, i valori assoluti
> no.
>
> **4. Il Capitolo 3 dichiara installata una configurazione che sul dispositivo
> non c'è.** Il testo dice che il sistema finale poggia su A3h — con l'altezza
> del bacino dal pavimento — e A3i; il dispositivo esegue il sottoinsieme
> scelto dal DTW, che quella grandezza non la contiene, perché il motore
> geometrico a 32 grandezze non la calcolava affatto. In corso di correzione:
> la grandezza è stata reintrodotta e la selezione va rifatta.
>
> Tutte e quattro sono documentate in `docs/ISSUES.md`, ISS-133, ISS-134,
> ISS-137 e ISS-139, con la misura di quanto pesano.

Le richieste vengono da tre momenti distinti, e sono tenute separate perché
hanno storie diverse:

| | quando | dove è registrata |
|---|---|---|
| **A** — le quattro richieste iniziali | prima del 17 agosto | `DIP_PROJECT/docs/STATO_E_PROSSIMI_PASSI.md`, `RIEPILOGO_RELATORE.md` |
| **B** — le cinque verifiche indicate | colloquio successivo alla lettera del 18 agosto | `docs/INDICE_E_STRUTTURA.txt`, parte 3 |
| **C** — i punti dell'email del 20 agosto | 20 agosto | `docs/CHANGELOG.md` del 26 agosto |
| **D** — le domande poste **a lui**, che attendono risposta | 26 agosto | `docs/INDICE_E_STRUTTURA.txt`, parti 4 e 5 |

**In sintesi.** Delle richieste esplicite ne resta aperta **una**: la prova di
durata sul dispositivo. Ma il conteggio «tutte tranne una» sarebbe generoso, e
va detto perché: **due risposte esistono come misura e non come testo**, cioè
il lettore della tesi non le trova (la scomposizione della latenza,
[ISS-115](ISSUES.md#iss-115)); e **una risposta non ha un artefatto che la
produca**, cioè non è rifacibile (il bilancio del costo per fotogramma,
[ISS-113](ISSUES.md#iss-113)). Una misura che non è nel testo e un numero che
non è riproducibile non sono richieste evase.

---

## A. Le quattro richieste iniziali

### A1 — Resilienza al cambio di telecamera e di ambiente

**Fatta**, in due modi complementari: il cambio di punto di vista a parità di
tutto il resto, e il trasferimento verso un archivio mai visto.

*Cambio di inquadratura*, a parità di soggetto, caduta e istante:

| addestrata su | verificata su | F2 | falsi positivi |
|---|---|---:|---:|
| Camera 1 | Camera 1 | 0,857 | 57 |
| Camera 1 | Camera 2 | 0,434 | 1.113 |
| Camera 1 + Camera 2 | Camera 2 | **0,678** | **460** |

Cambiare inquadratura costa **0,422 di F2**, cioè metà dell'accuratezza;
addestrare su due viste ne recupera il 58% e taglia i falsi positivi del 59%.

> **Correzione del 1º settembre.** La prima riga riportava $0{,}872$, che
> appartiene a un altro modello: la foresta su Camera 1 vale $0{,}857$
> ([ISS-129](ISSUES.md#iss-129)). Il divario passa da 0,438 a **0,422**.

Recall e precisione migliorano **insieme**, che è ciò che distingue un
apprendimento più generale dallo spostamento di una soglia.

> **Provenienza da dichiarare:** queste tre righe sono run di addestramento e
> restano a **cinque** soggetti. La misura geometrica che le accompagna —
> l'escursione dell'angolo del tronco — è invece stata rifatta su **dieci** il
> 6 settembre, e non porta più quell'avvertenza.

> **Correzione del 6 settembre, ed è la terza su questo numero.** Il rapporto
> fra le escursioni delle due viste era dichiarato $1{,}99\times$. Vale
> **$2{,}23\times$**, su dieci soggetti invece di cinque, con $74{,}0^\circ$
> contro $33{,}2^\circ$ e 30 sequenze su 39 sopra i 60 gradi contro 8. Cade
> anche l'affermazione che «in 2 sequenze su 25 Camera2 osserva quanto o più di
> Camera1»: su trentanove ne resta **una**, e il rapporto minimo è $0{,}98$.
>
> Le cause sono due, e sono di natura diversa
> ([ISS-133](ISSUES.md#iss-133), [ISS-134](ISSUES.md#iss-134)).
>
> La prima è un difetto del codice di misura: un unico stimatore di posa
> veniva riusato per tutte le riprese in successione, e poiché MediaPipe Pose
> mantiene stato fra un fotogramma e il successivo, l'ultima immagine di una
> ripresa — persona a terra — condizionava la prima della ripresa dopo. Su una
> singola sequenza lo scarto arriva a $68^\circ$.
>
> La seconda non è un errore di misura ma un comportamento reale del sistema,
> e mi sembra il risultato più interessante emerso in questi giorni: **su
> Camera2 lo stimatore perde chi cade e si aggancia a una persona rimasta in
> piedi o seduta nel campo, in 11 riprese su 50. Su Camera1 in 0 su 50.** L'ho
> verificato anche sui landmark da cui sono costruite le grandezze usate per
> addestrare, e il difetto arriva anche lì: 3 riprese su 25 di Camera2 contro
> 0 su 24 di Camera1. Nel dodici per cento delle cadute di Camera2 il
> classificatore riceve, per la fase a terra, le grandezze di un'altra persona.
>
> Ne segue che il divario di F2 fra le viste ha **due** cause e non una, e che
> il testo ne dichiarava solo la prima. Non le ho separate: le tre righe della
> tabella non sono state rieseguite escludendo le riprese contaminate, e nel
> capitolo è scritto che non lo sono.
>
> Aggiungo il dato che mi ha fatto più impressione: su Camera2 una posa viene
> trovata nel $97{,}0\%$ dei campioni, contro l'$85{,}7\%$ di Camera1. **La
> vista che porta meno informazione è quella in cui lo stimatore fallisce meno
> spesso**, perché quando perde il soggetto trova comunque qualcun altro. La
> quota di pose rilevate non è una misura di qualità, e la usavo come criterio
> per accettare una sessione registrata in casa.
>
> Come me ne sono accorta: componendo la figura che mancava al capitolo, dove
> uno scheletro corretto era disegnato addosso alla persona sbagliata con
> accanto un angolo che sembrava perfettamente sensato. Nei numeri non si
> vedeva.

*Trasferimento a un archivio esterno* (UR-Fall), a dieci soggetti: F2 **0,034**
con la soglia schierata, **0,492** con la soglia ritarata sul dominio di
destinazione. La scomposizione del divario è il contributo originale, e sui
dati attuali dà due parti quasi uguali: **il 49% è taratura** — il modello
ordina ancora le finestre, su una scala di punteggi diversa — e **il 51% è
perdita reale** di capacità discriminativa, che nessuna soglia recupera.

> **Correzione del 3 settembre.** Fino a oggi qui e nel Capitolo 4 comparivano
> $0{,}612$ di soglia oracolo e una scomposizione «due terzi taratura, un terzo
> perdita». Venivano da `exp041_domain_shift.json` del progetto storico, che è
> un altro esperimento: altra estrazione delle feature, 1.125 finestre invece
> di 1.075, prevalenza 0,128 invece di 0,094, e come riferimento in dominio
> proprio quel $0{,}872$ di [ISS-129](ISSUES.md#iss-129). Sull'artefatto
> attuale il valore è **0,492** e la divisione è **quasi esatta a metà**
> ([ISS-131](ISSUES.md#iss-131)).

**Artefatti:** `risultati/campo/valutazione_incrociata_10sog.json`,
`risultati/esterno/`, `risultati/laboratorio/escursione_viste_10sog.csv` (e il
suo `_serie.json`); `risultati/cinque_soggetti/exp013_camera_viewpoint.csv` è
la misura originale, tenuta solo per il confronto.

### A2 — Resilienza alle occlusioni

**Fatta**, e il risultato non è quello atteso. Mascherando gruppi di landmark
con il punto congelato all'ultima posizione nota, la perdita massima è
**0,020 di F2**, sulle spalle, contro una dispersione fra soggetti di 0,078:
**nessun gruppo è critico**.

Il fenomeno di auto-occlusione osservato all'inizio del lavoro — la confidenza
del naso che passa da 0,938 in piedi a 0,240 a terra — è **specifico di
YOLOv8** e su MediaPipe non esiste. Nel testo resta attribuito allo stimatore
su cui è stato misurato, e non presentato come proprietà del problema.

**Non misurate:** le occlusioni da mobilio reale. Né UP-Fall né UR-Fall le
annotano; ciò che è misurato è l'occlusione *simulata*.

**Artefatto:** `risultati/occlusioni/foresta_DTW.json`.

### A3 — Porting su nodo edge, senza video verso l'esterno

**Fatta e caratterizzata, e il 6 settembre rimisurata.** La catena completa
gira su una Radxa ROCK 4D, circa cento euro con telecamera USB.

| | dichiarato prima | **misurato il 6 settembre** |
|---|---:|---:|
| pre-elaborazione | 1,21 ms | 0,25 ms |
| **percezione** | 33,34 ms (88,4%) | **124,26 ms (86,2%)** |
| post-elaborazione | 0,94 ms | 1,35 ms |
| **classificatore** | 2,20 ms (5,8%) | **18,26 ms (12,7%)** |
| **totale** | **37,7 ms — 26,5 fps** | **144,1 ms — 6,9 fps** |

**Il dispositivo è 3,8 volte più lento di quanto il capitolo dichiarasse.** Le
proporzioni reggono, e con esse l'affermazione portante: il collo di bottiglia
è la percezione, non la classificazione. I valori assoluti no.

Il numero sbagliato è quello che era in tesi, e l'indizio era già nel progetto:
il file di configurazione dichiara da sempre che il dispositivo regge circa
nove fotogrammi al secondo, ed è su quel presupposto che il dataset viene
sottocampionato in addestramento. I 6,9 misurati sono coerenti con quello; i
26,5 non lo erano, e nessuno aveva mai confrontato i due.

L'obiezione che la misura fosse presa a stanza vuota è stata verificata e
**falsificata**: con un soggetto in scena il costo sale da 126,0 a 144,1 ms,
perché al rilevatore si aggiunge il modello dei landmark.

Prima di ogni misura sul dispositivo si verifica che le predizioni coincidano
con quelle del calcolatore su duecento finestre precalcolate: la verifica passa
con scarto **0,000e+00**. Sulle stesse 56 clip elaborate dai fotogrammi,
invece, **55 decisioni su 56 coincidono e una no** — ed è una caduta vera. La
causa non è il classificatore ma lo stimatore di posa, che è un tracciatore e
diverge fra architetture ([ISS-106](ISSUES.md#iss-106)).

L'acceleratore neurale **non viene usato**: costa 0,216 di F2, mentre dimezzare
la frequenza dei fotogrammi ne costa 0,041. È un risultato negativo su un
lavoro consistente, e resta nel testo.

Sulla riservatezza: il registratore salva in continuo **soltanto posa e
punteggi**; le immagini restano sul dispositivo e solo attorno agli allarmi.
Per ottenerlo è stata tolta dal prototipo una registrazione video continua che
contraddiceva l'argomento della tesi.

> **Riserva, ed è aperta:** la ripartizione del costo per fotogramma esiste
> **soltanto nel testo**. Fu trascritta da una sessione di terminale, e
> cercando `33,34` in tutti i file di risultato dei due progetti non compare
> ([ISS-113](ISSUES.md#iss-113)). `deploy_board/rileva.py` è stato strumentato
> il 26 agosto e scrive ora il bilancio nel proprio `riepilogo.json`, ma è
> stato eseguito **solo sul calcolatore**.

### A4 — Prova di durata in ambiente reale

**Fatta nella sostanza, non nella forma richiesta.** Dodici blocchi, quattro
giornate, due abitazioni, **9,6 ore** e 205.905 fotogrammi, con il consenso dei
partecipanti. La sessione più lunga è di **4,99 ore** continuative.

**La prova da dodici ore con controllo della sospensione non è stata
eseguita.** Il primo tentativo era sembrato riuscire, e non era vero: la
macchina si era sospesa da sola. `deploy_board/rileva.py` ha ora **due
orologi** e dichiara in ogni riepilogo quanto la macchina ha dormito, quindi il
difetto che aveva invalidato silenziosamente quel tentativo è **rilevabile**.
Manca di collegare la telecamera e lasciare il dispositivo acceso.

**Artefatti:** `risultati/sessioni/`, dodici sessioni con punteggi per finestra.

---

## B. Le cinque verifiche indicate

### B1 — PR-AUC nel passaggio all'archivio esterno

**Fatta, e la risposta è quella meno comoda delle due prospettate.**

| | PR-AUC | rispetto alla prevalenza |
|---|---:|---:|
| archivio di addestramento | 0,990 | 18,7× |
| archivio mai visto | **0,169** | **1,79×** |

Con ROC-AUC 0,750. Non è quindi soltanto uno spostamento della distribuzione
dei punteggi: **c'è perdita reale della capacità di separare**. La soglia
scelta a posteriori sul dominio di destinazione porta l'F2 da 0,034 a 0,492, e
nel testo è chiamata esplicitamente **soglia oracolo**, con la dichiarazione
che non è una prestazione ottenibile da chi installa il sistema.

**Artefatto:** `risultati/campo/pr_auc_allineato.json`.

### B2 — Controesempi di una casa verificati sull'altra

**Fatta, in entrambe le direzioni.**

| controesempi da | verifica su | eventi/ora |
|---|---|---|
| casa dei nonni | casa dello studente | 0,342 → **0,171** |
| casa dello studente | casa dei nonni | 1,781 → **0,890** |

Circa un fattore due in entrambi i versi. Con due sole abitazioni non è una
dimostrazione, ma fra le due ipotesi distinte nell'email indica **la prima**:
il modello ha imparato una categoria trasferibile, non le caratteristiche della
stanza da cui vengono i controesempi. Nel testo l'effetto è chiamato
**adattamento al dominio** e non generalizzazione, come indicato.

**Il costo va dichiarato, e nel testo lo è:** in quella configurazione il
recall scende a **due cadute su cinque**.

### B3 — Verifica controllata sulle occlusioni

**Fatta, nella forma suggerita** — mascheramento di gruppi di landmark con il
punto congelato all'ultima posizione nota, e misura della degradazione. Vedi
[A2](#a2--resilienza-alle-occlusioni): perdita massima 0,020 di F2 contro una
dispersione fra soggetti di 0,078.

### B4 — Metriche di campo a livello di evento

**Fatta per tre grandezze su quattro**: quota di cadute rilevate, falsi allarmi
per ora, tempo medio fra falsi allarmi. Il testo distingue esplicitamente
**eventi** e **finestre sopra soglia**, che sulle stesse registrazioni
differiscono di un fattore **44,8**.

**La quarta — la latenza dall'inizio della caduta alla prima segnalazione — è
stata affrontata, e la risposta è che non è misurabile con questi dati.** Le
cadute sono annotate **al minuto**, mentre la grandezza da misurare è di pochi
secondi: l'incertezza sull'istante vero è fino a sessanta volte la quantità da
misurare. Il dato che lo rende evidente: la prima finestra sopra soglia cade a
+11,8, +19,4, +27,7 e +32,3 secondi dal minuto annotato, e quegli scarti non
sono ritardi del sistema ma il punto del minuto in cui la persona è caduta.

Ciò che invece si misura è la **scomposizione** della latenza:

| addendo | valore | quota |
|---|---:|---:|
| calcolo per fotogramma | 0,038 s | 1,0% |
| **riempimento della finestra** (22 campioni a 8,02 fps) | **2,743 s** | **72,6%** |
| persistenza (5 finestre, una ogni 0,249 s) | 0,997 s | 26,4% |
| **limite inferiore** | **3,778 s** | |

**La latenza è dominata dalla finestra di decisione, non dall'hardware: 2,74 s
contro 38 ms, un fattore settantatré.** È il complemento del risultato sul
costo per fotogramma: lì il collo di bottiglia era la percezione, qui è la
finestra, e in entrambi i casi il classificatore non conta.

> **Difetto aperto, e va detto prima che lo trovi lui:** nessuno di questi
> numeri è in alcun capitolo. Né 3,778, né 2,743, né la parola «riempimento»
> ([ISS-115](ISSUES.md#iss-115)). La misura esiste, il lettore della tesi non
> la trova.

**Artefatto:** `risultati/campo/latenza.json`.

### B5 — Prova lunga con controllo della sospensione

**Non fatta.** È l'unica delle cinque che resta aperta, e coincide con
[A4](#a4--prova-di-durata-in-ambiente-reale).

---

## C. I punti dell'email del 20 agosto

### C1 — Punto 1: gli ingressi della foresta e le grandezze integrali

**La sua lettura del meccanismo è corretta; i numeri su cui poggiava non lo
erano.** Sul come sono costruiti gli ingressi della foresta l'ipotesi è esatta:
la finestra viene riassunta con sei statistiche per grandezza, e non c'è alcuna
nozione di ordine, quindi la foresta è l'unica architettura a cui
l'informazione temporale vada consegnata già calcolata.

Il problema è che il confronto veniva da **cinque** soggetti. Rifatto a dieci:

- il guadagno di **0,040** sulla foresta **non è distinguibile dal caso**; con
  la regola di etichettatura che include gli estremi il segno si rovescia a
  **−0,022**;
- per distinguere l'effetto servirebbero fra **34 e 70 soggetti** secondo la
  variante; sulla GRU ne servirebbero **274**;
- a dieci soggetti la foresta **non è più la prima della tabella ma l'ultima**
  delle cinque, con 0,792 contro 0,858 della LSTM. Resta indistinguibile dalla
  GRU, $t = -1{,}74$ contro un valore critico di 2,26, quindi l'indicazione di
  non dichiarare un vincitore **vale ancora, nell'altro verso**.

**Conclusione proposta:** l'interpretazione meccanicistica resta come lettura
dichiarata del fenomeno accanto alla tabella della numerosità, e non come
contributo misurato. Su questo è chiesto un parere ([D2](#d2--linterpretazione-sugli-ingressi-della-foresta)).

**Aggiornamento del 27 agosto.** È stata aggiunta una sesta architettura, una
rete a grafo ([EXP-018](EXPERIMENTS.md#exp-018)), e il quadro non cambia:
nessuna fa meglio della GRU. Il grafo è il primo confronto che supera la soglia
critica, $t = -2{,}37$, e la supera **nel verso sbagliato** — e non sopravvive
comunque alla correzione per molteplicità, che con cinque confronti richiede
$|t| > 3{,}25$.

### C2 — Punto 4: chiamarlo adattamento al dominio, non generalizzazione

**Fatto.** Nel Capitolo 5: «adattamento al dominio di installazione — *domain
adaptation* nella terminologia corrente — e non generalizzazione».

### C3 — Punto 5: mostrare i due errori, non un solo F2

**Fatto**, con la tabella dei falsi negativi e falsi positivi per le cinque
configurazioni, più la figura `fig_errori.png`.

Il dato nuovo, **a dieci soggetti e non a cinque**: da A3 ad A3i con i
controesempi i falsi negativi passano da **45 a 14** e i falsi positivi da
**172 a 124**. In laboratorio la configurazione finale **non introduce alcuno
scambio**: migliora entrambi gli errori. Lo scambio compare solo in casa, che è
esattamente la tesi del capitolo.

> **Aggiunta del 6 settembre.** La richiesta si è rivelata la più fertile delle
> nove, e il capitolo ha ora due tabelle in più. Scomponendo i falsi allarmi
> **per attività**: su 419, ben **389 — il 93% — vengono da una sola attività,
> sdraiarsi**. Camminare, stare in piedi e saltare non ne producono nemmeno
> uno, su cinquemila finestre.
>
> L'ipotesi che il sistema si allarmi per il movimento rapido è stata
> verificata e **smentita**: il picco di velocità verticale di una camminata
> (0,087) supera quello della finestra mediana di caduta (0,055), perché in due
> secondi e mezzo di passi il corpo oscilla molte volte. Se il sistema
> decidesse sulla velocità, camminare sarebbe il falso allarme principale.
>
> E scomponendo i positivi **per tipo di caduta**, il richiamo va da 0,934
> (di lato) a **0,704 (all'indietro)**: ventitré punti, un divario più grande
> di quello fra due qualunque delle sei architetture confrontate.

### C4 — Punto 6: chiamarla soglia oracolo

**Fatto.** Definita nel testo come «valore ottenuto usando le etichette del
dominio di destinazione, che chi installa non possiede».

### C5 — Punto 8: la coerenza fra 4,47 e 2,20 ms

**Fatto.** Il classificatore decide una volta ogni due fotogrammi (passo 2),
quindi il costo ammortizzato **per fotogramma** è metà di quello **per
finestra**. Il Capitolo 5 riporta ora entrambe le unità con la spiegazione
accanto.

**Controllo indipendente del 27 agosto:** misurando il costo per finestra delle
sei architetture sul calcolatore, la foresta dà **4,85 ms**
([EXP-019](EXPERIMENTS.md#exp-019)), compatibile con i 4,47 ms dichiarati. È il
primo controllo esterno che quel numero abbia superato — e nello stesso
risultato si vede che **la foresta è la più lenta per finestra delle sei**, il
che obbliga a dire che è stata scelta per costo di addestramento, dipendenze e
riproducibilità, non per velocità in inferenza.

### C6 — Punto 9: i parametri non dichiarati del recall di campo

**Recepito.** Un sistema installato non produce finestre ma **eventi**, e sulle
stesse registrazioni le due grandezze differiscono di un fattore **44,8**. Il
recall di campo dipende inoltre da due parametri che non erano stati dichiarati
— la tolleranza di accoppiamento e la persistenza — ed è quindi riportato come
**intervallo con i parametri esposti**, mai come numero singolo.

### C7 — L'indice aggiornato e la struttura del capitolo sperimentale

**Fatto una volta, e da rifare.** Il documento `docs/INDICE_E_STRUTTURA.txt` del
26 agosto riporta, per ogni sezione dei capitoli sperimentali, **la tesi che
sostiene e non il suo contenuto**.

Ma propone una struttura che poi **non è stata applicata**: propone di fondere
contesto e stato dell'arte, e quella fusione non si è fatta. Il documento ha
una toppa in testa che lo avverte, e sotto la toppa l'indice a otto capitoli.
**Va riscritto prima di consegnarlo**, ed è il primo lavoro in ordine di
urgenza.

---

## D. Le domande che attendono una sua risposta

### D1 — La fusione fra contesto e stato dell'arte

*Superata dai fatti.* La struttura applicata tiene i due capitoli **separati**,
e la ripetizione che la fusione doveva togliere è stata tolta diversamente:
tre argomenti che comparivano in entrambi — la scelta della visione contro gli
indossabili, la motivazione di riservatezza della posa, il conto sulla
frequenza di base — stanno ora solo nel Capitolo 1, e il Capitolo 2 vi rimanda.

### D2 — L'interpretazione sugli ingressi della foresta

Resta aperta: presentarla come lettura dichiarata e non misurata, oppure
toglierla del tutto. Vedi [C1](#c1--punto-1-gli-ingressi-della-foresta-e-le-grandezze-integrali).

### D3 — La latenza di rilevamento

*Risposta nel frattempo, con una misura.* Non è calcolabile sulle cinque cadute
annotate, per la ragione data in [B4](#b4--metriche-di-campo-a-livello-di-evento):
l'annotazione è al minuto. La scelta fatta è **dichiarare che non è misurabile
e scomporre ciò che invece lo è**. Resta da inserirla nel testo.

### D4 — Quale dei due sistemi installabili presentare

Ce ne sono due e non uno: con i controesempi, **2,5 falsi allarmi/ora e 3
cadute su 5**; senza, **14,0 all'ora e 4 su 5** nella configurazione
ottimizzata. Con questi numeri la seconda sembra preferibile, perché in un
sistema di sicurezza una caduta su cinque pesa più di undici allarmi all'ora in
più. La domanda è se presentare la scelta come aperta dichiarando il criterio,
oppure indicare la configurazione a recall pieno come sistema proposto e
l'altra come variante.

> Va detto che **cinque cadute non stimano un recall**: l'intervallo di
> confidenza va da 0,28 a 0,99 e non permette di distinguere alcuna
> configurazione da un'altra. È la ragione per cui nel testo non compare una
> configurazione vincitrice scelta su «quattro su cinque contro tre su cinque».

---

## E. Che cosa resta aperto, in ordine

1. **`docs/INDICE_E_STRUTTURA.txt` da riscrivere** sulla struttura a cinque
   capitoli, prima del 2 settembre.
2. **[ISS-115](ISSUES.md#iss-115)** — la scomposizione della latenza dentro il
   Capitolo 5. La misura c'è; è una modifica di testo.
3. **La prova di durata sul dispositivo**, che chiude insieme A4, B5 e
   [ISS-113](ISSUES.md#iss-113): il bilancio per fase esce dal `riepilogo.json`
   della prova stessa.
4. **`fig:due_camere`**, l'unica figura del Capitolo 4 ancora senza immagine.
5. **Sedici voci di bibliografia mai verificate** su trentadue. Delle sette
   verificate il 25 agosto, due affermazioni non ressero; delle cinque
   verificate il 31 agosto, due non hanno retto
   ([ISS-123](ISSUES.md#iss-123), [ISS-124](ISSUES.md#iss-124)). La proporzione
   non sta migliorando, ed è l'argomento per verificare le restanti.
6. **Più cadute reali.** È il limite più serio del lavoro. La sessione da cui
   vengono tutte e cinque ha il 25,9% di pose valide, peggio di sessioni che
   sono state scartate: rifarla con l'inquadratura giusta è l'intervento a
   costo più basso.
