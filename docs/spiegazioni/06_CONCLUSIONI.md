# Conclusioni — contributi, limiti, sviluppi

**File:** `tesi/Conclusioni.tex` · **etichetta:** `cap:conclusioni` · **2.226
parole**, 5 sezioni.

Fino al 26 agosto le conclusioni erano il Capitolo 8; ora hanno un file proprio,
e `tesi/controlla.py` è stato corretto perché non lo conosceva — si chiama
`Conclusioni.tex` e non `Cap*`, quindi segnalava `cap:conclusioni` come etichetta
assente e lasciava le sue 2.182 parole fuori dal totale.

**Il criterio con cui è scritto:** i contributi sono presentati come
**metodologici**. Il valore del lavoro non è un $F_2$ più alto di altri, ed è
importante che il capitolo non provi a farlo sembrare tale.

> **Nota nel sorgente, da non violare.** Non usare il «4,32× sull'escursione
> dell'angolo del tronco»: è stato accertato che non si riproduce (rieseguendo su
> 25 sequenze esce 1,99×). I numeri da citare sono il 2,9× sull'accuratezza
> oppure il divario **0,422 in $F_2$** fra le due camere.

---

## 1. I sette contributi, e la forza di ciascuno

L'apertura è una rinuncia esplicita:

> Il lavoro **non rivendica un record di accuratezza**, e sarebbe poco onesto
> farlo: i numeri pubblicati su UP-Fall sono più alti di quelli riportati qui.
> Rivendica invece **che quei numeri e questi rispondano a domande diverse**, e
> che la differenza sia misurabile.

### 1 — Un protocollo per dataset con pochi soggetti, e la misura di cosa succede senza

$F_1$ da **0,0000 a 0,234** applicando insieme le tre correzioni. Il primo valore
non è un modello mediocre: è **un modello che non ha mai predetto la classe
positiva, e che senza il protocollo corretto sarebbe stato indistinguibile da uno
funzionante.**

Il contesto che rende leggibile il contributo: i lavori pubblicati su UP-Fall
riportano accuratezze fra il 98% e il 99,58%, e **almeno uno dichiara
esplicitamente di usare partizioni casuali 70:30 dell'intero dataset** — cioè
esattamente il difetto qui documentato. Riscontro indipendente: lo stesso
classificatore che dà 89% in k-fold casuale **scende al 76% con divisione per
soggetto**.

### 2 — La quantificazione dell'effetto del punto di vista

*(Misura a cinque soggetti; l'ampiezza è tale che il riallineamento non può
ribaltarla, i valori assoluti sono indicativi.)*

**0,422 di $F_2$** — da 0,857 a 0,434 — a parità di soggetto, caduta e istante.
**La ragione è geometrica e non algoritmica**: una telecamera che guarda dall'alto
comprime la rotazione del tronco lungo il proprio asse ottico. *L'informazione che
distingue una caduta viene cancellata dall'ottica prima che un modello possa
elaborarla.*

Addestrando su entrambe le viste se ne recupera il **58%**, con i falsi positivi
in calo del **59%**: migliorano insieme, **il che distingue un apprendimento più
generale da uno spostamento di soglia**.

### 3 — Un confronto fra classificatori a parità di protocollo, con esito contrario

Cinque architetture entro **0,066** di $F_2$ contro una dispersione fra soggetti
di 0,08–0,12; **nessuna coppia distinguibile**, e il numero di parametri non
ordina il risultato.

**Il contributo non è la constatazione, che da sola sarebbe un risultato negativo:
è la sua quantificazione.** GRU contro LSTM: **113 soggetti**. Due definizioni del
compito: **2**. **Fattore cinquantasei fra le due domande**, e nessun archivio
pubblico di cadute si avvicina alla prima cifra.

### 4 — La caratterizzazione end-to-end su hardware edge reale

26,5 fps su cento euro, senza che alcun dato lasci l'abitazione. **La ripartizione
del costo è il dato meno atteso: percezione 88,4%, classificatore 5,8%.** *Tutta
la letteratura sul confronto fra architetture, e tutto il lavoro del punto 3,
agiscono su un ventesimo del problema.*

### 5 — La quantificazione dello scarto fra precision di laboratorio e falsi allarmi reali

Precision **0,819** su un insieme quasi bilanciato → proiettata sul funzionamento
continuo, **14–125 falsi allarmi all'ora**. **Misurati: 2.735.** *La previsione,
costruita per essere scomoda, era ottimistica di oltre un ordine di grandezza.*

### 6 — Le grandezze integrali al posto delle derivate istantanee

Il classificatore non usava la dinamica (correlazione punteggio/movimento
**+0,139**) **non per un difetto di architettura ma perché ciò che riceveva come
dinamica era rumore**: derivate con autocorrelazione 0,18–0,44 contro valori intorno a 0,9
delle grandezze statiche. Sostituendole con grandezze accumulate,
l'autocorrelazione sale a **0,91–0,94** e la separazione fra le classi raggiunge
fattori di 21–32 nelle mediane.

**È l'unico intervento del lavoro che migliora simultaneamente in laboratorio e
sul campo.**

### 7 — La misura di ciò che il dataset di riferimento non riesce a distinguere

**0,055 di $F_2$ in laboratorio** — dentro la dispersione, quindi non dichiarabile
— **contro un fattore cinquantadue sui falsi allarmi in una casa.** È il
contributo che il lavoro ritiene principale.

---

## 2. Il risultato che non era atteso

Il lavoro era impostato su una domanda di ingegneria: *quale architettura, e su
quale hardware*. **La risposta è che la domanda era mal posta**, per due ragioni
indipendenti.

**La prima: l'architettura del classificatore non è la variabile che decide.**
L'intero intervallo entro cui cadono cinque architetture vale 0,066; il divario
fra due posizioni della telecamera vale 0,422, cioè **più di sei volte tanto**;
quello fra due definizioni del compito 0,127 con differenza statisticamente
netta, mentre nessuna coppia di architetture lo è.

> Ha una conseguenza pratica immediata per chi installa questi sistemi, **ed è
> economicamente rilevante: spostare una telecamera costa meno che addestrare un
> modello più grande, e rende di più.**

**La seconda, e più importante: che cosa un insieme di verifica può misurare.**

### La precisazione che il lavoro deve a sé stesso

> Una versione precedente di questa tesi sosteneva qualcosa di più forte: che
> l'archivio di laboratorio **ordinasse in modo errato** le alternative, collocando
> ultima la configurazione che in casa risultava migliore. **Quella affermazione
> era fondata su cinque soggetti, e non è sopravvissuta al raddoppio**: su dieci,
> le due graduatorie concordano.

L'enunciato che regge è quindi **più debole in apparenza e più solido in
sostanza**:

> Un insieme di verifica non può misurare un miglioramento su una condizione che
> non rappresenta. Non si limita a sovrastimare le prestazioni: **rende
> indistinguibili alternative che in esercizio differiscono di ordini di
> grandezza**, e lo fa con la stessa apparente sicurezza con cui distinguerebbe
> alternative davvero equivalenti.

**L'effetto pratico coincide con quello di un ordinamento errato**, e il paragrafo
che lo spiega è quello da leggere all'orale: chi selezioni sul solo $F_2$ di
laboratorio non ha **alcuna ragione statistica** per preferire la configurazione
adottata; sceglierebbe la più semplice **avendo seguito la procedura corretta fino
in fondo**.

**La differenza fra le due formulazioni è operativa.** Che un dataset *sovrastimi*
è noto, ed è misurato su scala ben maggiore di questo lavoro — OmniFall riporta
per UP-Fall un crollo da 72,9% a 16,9% di F1. Che un dataset **non distingua** è
una proprietà diversa, e più dannosa: *chi sovrastima produce un sistema peggiore
di quanto crede; chi non distingue produce **il sistema sbagliato**, avendo
scartato quello giusto con piena fiducia nella misura e senza che nulla, nella
procedura, potesse segnalarglielo.*

> **Attenzione, questa è una trappola per l'orale.** L'Introduzione e le
> Conclusioni riportano lo stesso enunciato **allineato ai dieci soggetti**. La
> formulazione «ordina in modo errato le alternative» è stata **ritirata** ed è
> segnalata nei commenti dei sorgenti come da non reintrodurre: è il caso in cui
> l'affermazione più forte è anche quella che i dati non reggono.

---

## 3. I limiti — dichiarati senza attenuazioni

| limite | perché conta |
|---|---|
| **dieci soggetti**, tutti giovani adulti, contro una popolazione bersaglio anziana | la dispersione fra fold, ±0,05–0,14, che il raddoppio non ha ridotto, è dell'ordine di molte differenze confrontate |
| **le cadute sono recitate**, qui come in UP-Fall, UR-Fall e nella quasi totalità della letteratura | nessuno studio di pochi giorni può misurare cadute accidentali: una persona anziana cade meno di una volta all'anno. È il limite che il lavoro **condivide con il settore**, e va detto invece che lasciato intendere |
| **il recall sul campo poggia su cinque cadute**, in una sessione con inquadratura difettosa | non è una stima, è un indizio. E non è mai misurato sulla popolazione anziana |
| **un solo archivio esterno** | non si distingue ciò che è specifico di UR-Fall da ciò che varrebbe per qualunque ambiente nuovo |
| **due sole abitazioni** per i controesempi | parte del guadagno potrebbe essere adattamento a quelle due stanze; servirebbe una terza casa |
| **nessuna ricerca di iperparametri**, in nessun esperimento | differenze inferiori a ~0,02 fra modelli neurali non sono interpretabili |
| **il multi-persona non è validato** | e non lo è per **assenza di dati**: nessun archivio pubblico contiene più persone in scena |
| **l'effetto della quantizzazione INT8 non è isolato** | non si sa quanta parte dei 0,227 sia dovuta alla rete e quanta alla quantizzazione |
| **le occlusioni da mobilio non sono state misurate** | e il risultato sull'auto-occlusione riguarda YOLOv8: su MediaPipe il naso passa da 0,997 a 0,989, cioè **non degrada** — degradano gli arti. **Va attribuito allo stimatore e non al problema** |
| **la prova di durata da dodici ore non è stata eseguita** | la sospensione automatica, che aveva invalidato senza segnalarlo la prima sessione lunga, è ora rilevabile, ma la prova resta da fare |

---

## 4. Gli sviluppi — cinque direzioni incontrate e non percorse

*Non un elenco di possibilità: sono le cinque che il lavoro ha incontrato senza
poterle percorrere, e per ciascuna è noto che cosa manchi. Sono ordinate per
quanto sbloccano il resto, non per quanto sono interessanti.*

**1. Taratura della soglia senza etichette, sul tasso di base *stimato*.** Il
crollo cross-dataset si scompone in 49% di taratura e 51% di perdita
reale. Fissare la soglia a un percentile della distribuzione dei punteggi
osservati recupera il **70%** di quel divario su UR-Fall, portando $F_2$ da 0,073
a 0,449.

**Ma il numero è ingannevole**, e il motivo è istruttivo: il valore migliore si
ottiene assumendo il 20% perché in UR-Fall le cadute sono davvero il 12,8% delle
finestre — **è un archivio costruito attorno alle cadute**. E c'è un'identità che
rende il conto immediato: *se la soglia è il percentile, allora esattamente quella
frazione di finestre lo supera, per costruzione e indipendentemente dal modello.*
Le sessioni domestiche producono 8.448 finestre all'ora: assumere l'1%
significherebbe **84 falsi allarmi/ora**, il 20% **millesettecento**.

> **Il metodo sostituisce un parametro non trasferibile — la soglia — con un
> altro parametro non trasferibile: il tasso di base assunto**, che è la quantità
> che cambia più di ogni altra fra un archivio e una casa.

La direzione promettente non è **assumere** il tasso ma **stimarlo**, per esempio
da un periodo iniziale in cui si assuma l'assenza di cadute — *ipotesi realistica
in una casa e falsa in un archivio*.

**2. Mappa del contesto tramite rilevamento degli oggetti.** La distinzione fra
divano e pavimento è oggi affidata alla stima automatica del piano del pavimento.
Un rilevamento dei mobili eseguito **all'avvio** e non per fotogramma — *i mobili
non si muovono* — avrebbe costo nullo in esercizio.

**3. Sessioni più lunghe e in più abitazioni**, con partecipanti anziani per il
solo blocco di vita normale, e la prova di durata da dodici ore.

**4. Sintesi di punti di vista per riproiezione dello scheletro**, per attaccare
il divario più grande misurato. **Con un limite noto dichiarato**: ruotare uno
scheletro produce le coordinate di una vista nuova **ma non la degradazione di
confidenza che quella vista causerebbe realmente**. Una vista sintetica avrebbe un
naso perfettamente visibile anche quando quella reale non lo avrebbe. *Il guadagno
riportato in letteratura va preso come limite superiore.*

**5. Ensemble di architetture.** I benchmark cross-dataset più recenti indicano
negli ensemble il guadagno di generalizzazione più affidabile. **Cinque modelli
addestrati a parità di protocollo sono già disponibili**, quindi il costo
dell'esperimento è quasi nullo.

**6. Ricerca di iperparametri**, per rendere interpretabili le differenze che il
lavoro dichiara non distinguibili.

---

## 5. La conclusione

**L'ipotesi economica di partenza è verificata:** cento euro eseguono in tempo
reale l'intera catena, senza che alcuna immagine lasci l'abitazione, e con il
classificatore al 5,8% del budget.

**L'ipotesi tecnica non è verificata, e la sua confutazione è il risultato più
utile del lavoro.** La variabile che decide è **dove si mette la telecamera**, e
il fattore che più di ogni altro distorce le decisioni progettuali è **la distanza
fra l'insieme su cui si misura e l'ambiente in cui si installa**.

**Il sistema non è pronto per l'installazione**: fra i suoi 14 falsi allarmi
all'ora e il criterio clinico restano due o tre ordini di grandezza. *Ma la
distanza è ora misurata invece che ignorata, il suo meccanismo è spiegato, ed è
stato mostrato che l'insieme di verifica su cui il settore misura non solo non la
rivela, ma indica la direzione opposta a quella che la riduce.*

---

## 6. I tre risultati negativi, dichiarati come tali

Sono annunciati nell'Introduzione e ripresi qui, perché sono la firma
metodologica del lavoro:

1. **l'acceleratore neurale del dispositivo non viene utilizzato** — costa 0,216
   di $F_2$ contro 0,041 del dimezzare il frame rate;
2. **l'architettura ricorrente di partenza non è giustificata dai dati** —
   nessuna delle cinque è distinguibile;
3. **un filtro geometrico progettato per ridurre i falsi allarmi peggiora il
   bilancio complessivo** — il *Physics Guard* in addestramento.

> **Sono riportati come tali, perché una scelta verificata e smentita è un
> risultato, mentre una scelta assunta e mai messa alla prova non lo è.**

---

## 7. Che cosa è ancora aperto, al 27 agosto 2026

In ordine di quanto blocca il resto (dal `CLAUDE.md` del progetto):

1. **La prova di durata sulla board** — l'ultima richiesta esplicita del relatore
   ancora aperta. Chiude anche ISS-113 nella stessa sessione.
2. **Le sedici voci di bibliografia mai verificate.** Quando le sette furono
   verificate, **due su sette non ressero**.
3. **Tre figure mancanti nel Capitolo 4** — ora due, dopo la risoluzione di
   ISS-111. Quella che resta va **composta** dai fotogrammi delle due telecamere,
   scegliendo l'istante.
4. **Più cadute reali.** Con cinque, l'intervallo di confidenza sul recall va da
   **0,28 a 0,99**. È il limite più serio del lavoro, e l'intervento a costo più
   basso è **rifare la sessione con l'inquadratura giusta**: quella da cui vengono
   tutte e cinque ha il 25,9% di pose valide.
5. **`docs/INDICE_E_STRUTTURA.txt` da riscrivere** prima di rimandarlo: contiene
   ancora l'indice a otto capitoli e una domanda su una fusione che non si fa più.
6. **La scomposizione della latenza entri nel testo** ([ISS-115](../ISSUES.md#iss-115)):
   la misura esiste (EXP-017) e nessun capitolo la riporta. *(La promessa sul
   «ritardo» nel Capitolo 1 non c'è più: è sparita con la riscrittura del
   capitolo, e ISS-108 è chiusa.)*

### Le tre domande poste al relatore, ancora senza risposta

Dal documento del 26 agosto (`docs/INDICE_E_STRUTTURA.txt`):

- **A.** La fusione del capitolo sul contesto con quello sullo stato dell'arte
  toglie una ripetizione reale, ma unisce in un capitolo solo il problema clinico
  e la letteratura. Accettabile, o preferisce che restino separati?
  *(Nel frattempo è stata applicata la struttura a cinque capitoli in cui i due
  restano **separati**, Cap. 1 e Cap. 2.)*
- **B.** L'interpretazione sugli ingressi della foresta — le grandezze integrali
  giovano solo al modello che non legge la sequenza — va presentata come **lettura
  dichiarata e non misurata**, oppure tolta del tutto? *(A dieci soggetti il
  guadagno di 0,040 sulla foresta non è distinguibile dal caso: con la regola di
  etichettatura che include gli estremi il segno si rovescia a −0,022, e
  servirebbero fra 34 e 70 soggetti.)*
- **C.** La latenza di rilevamento: calcolarla sulle cinque cadute annotate,
  sapendo che cinque eventi non permettono di dire quasi nulla, oppure dichiarare
  che non è misurabile con i dati disponibili? *(EXP-017 ha risposto de facto: non
  è misurabile, e si riporta la scomposizione.)*
