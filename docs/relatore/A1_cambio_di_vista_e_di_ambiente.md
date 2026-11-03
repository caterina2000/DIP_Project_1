# A1 — Resilienza al cambio di telecamera e di ambiente

**Che cosa è stato chiesto:** verificare che il sistema non funzioni soltanto
sulle riprese su cui è stato addestrato — cambiando inquadratura e cambiando
ambiente.

**La risposta in una riga:** il sistema **non è resiliente**, e adesso sappiamo
di quanto, per quale causa, e **quale delle due cause candidate pesa
davvero**. Cambiare punto di vista costa **0,334 di F2**; cambiare archivio
porta la prestazione quasi a zero.

> **Aggiornato il 7 settembre 2026.** Le tre righe di questa risposta erano
> l'ultima misura del lavoro ancora ferma a cinque soggetti. Sono state
> rieseguite a dieci sul dataset riestratto, e nella stessa esecuzione è stata
> separata una domanda che il testo poteva solo dichiarare
> ([EXP-026](../EXPERIMENTS.md)).

---

## Come ci siamo arrivati, passo per passo

### Passo 1 — Separare due domande che sembravano una

«Cambio di telecamera» e «cambio di ambiente» sono cose diverse e si misurano
in modo diverso.

- Il **cambio di inquadratura** si misura *a parità di tutto il resto*: stessa
  persona, stessa caduta, stesso istante, ripresa da due telecamere
  sincronizzate. UP-Fall ne ha due, e questo permette un confronto pulito.
- Il **cambio di ambiente** richiede un archivio registrato da altri, in
  un'altra stanza, con altre persone: UR-Fall.

Le due misure sono tenute separate per tutta la tesi.

### Passo 2 — Le due telecamere di UP-Fall, e quale è «rialzata»

| | posizione | che cosa vede |
|---|---|---|
| **Camera 1** | **laterale**, all'altezza del busto | la persona di profilo: il tronco che ruota dalla verticale all'orizzontale attraversa il piano dell'immagine |
| **Camera 2** | **frontale e più in alto**, inclinata verso il basso | la persona di fronte, dall'alto: la stessa rotazione avviene in gran parte *verso* la telecamera, e sull'immagine si comprime |

**La «vista rialzata» è quindi la Camera 2.** È anche quella che
un'installazione reale tende a scegliere — un angolo della stanza, in alto, per
coprire più superficie — ed è il motivo per cui questa misura conta più di
quanto sembri.

### Passo 3 — Il cambio di inquadratura, misurato addestrando

Tre addestramenti con la stessa architettura, gli stessi iperparametri e la
stessa soglia dichiarata a priori. Cambia soltanto **da quale vista arrivano i
dati**:

| addestrata su | verificata su | F2 | falsi allarmi | cadute non viste |
|---|---|---:|---:|---:|
| Camera 1 | Camera 1 | **0,822 ± 0,099** | 722 | 186 |
| Camera 1 | **Camera 2** | **0,488 ± 0,119** | **3.252** | 451 |
| Camera 1 + 2 | Camera 2 | **0,731 ± 0,188** | 751 | 335 |
| *Camera 2* | *Camera 2* | *0,753 ± 0,179* | *1.067* | *246* |

*(La quarta riga non era nella tabella del capitolo. È stata aggiunta perché
serve al paragrafo del Passo 6-bis, ed è quella che lo smentisce.)*

**Cambiare inquadratura costa 0,334 di F2**, cioè circa **tre volte la
dispersione fra soggetti**: non è rumore. Addestrare su entrambe le viste ne
recupera il **73%** e riporta i falsi allarmi da 3.252 a 751, cioè al livello
della vista buona.

**Il dato che si vede solo separando i due errori** — ed è la richiesta del
punto 5 dell'email ([C3](C3_i_due_errori.md)) — è che trasferire alla vista
rialzata non peggiora un po' tutto: **fa esplodere un errore solo**. I falsi
allarmi si moltiplicano per quattro e mezzo, le cadute perse per due e mezzo.

> **La figura è `fig_viste.png`**, in `tesi/figure/`, prodotta da
> `pipeline/figure_tesi.py` (funzione `fig_viste`) a partire da
> `risultati/laboratorio/viste_incrociate_10sog.json`. Accanto al PNG c'è
> `fig_viste.txt` con la scheda e la didascalia già scritta.

#### Che cosa è cambiato rispetto ai numeri che le avevo mandato

| | prima (cinque soggetti) | **ora (dieci soggetti)** |
|---|---:|---:|
| Camera 1 → Camera 1 | 0,857 | 0,822 |
| Camera 1 → Camera 2 | 0,434 | 0,488 |
| Camera 1 + 2 → Camera 2 | 0,678 | 0,731 |
| **divario** | **0,422** | **0,334** |
| recuperato addestrando su due | 58% | **73%** |

Il divario si riduce di 0,088 e resta tre volte la dispersione: **la
conclusione non cambia, i numeri sì.** Con più persone il sistema trasferisce
un po' meglio di quanto sembrasse, e il rimedio — addestrare su entrambe le
viste — funziona meglio di quanto sembrasse.

#### La correzione del 1º settembre, e di quale modello si trattava

Nella versione precedente la prima riga riportava **0,872**. Quel valore non
era della foresta casuale — il modello di tutte e tre le righe e quello
installato sul dispositivo — ma di **un'altra architettura**, ripresa da una
tabella diversa del capitolo.

È un errore che rende il confronto privo di senso: se la prima riga viene da un
modello e le altre due da un altro, il divario fra le righe misura *anche* la
differenza fra i due modelli, e non solo il punto di vista. Corretto, la prima
riga vale 0,857 e il divario è passato da 0,438 a 0,422
([ISS-129](../ISSUES.md)). Il difetto è stato la ragione per cui, nella
riesecuzione, **tutte e tre le righe sono prodotte dallo stesso script in una
sola esecuzione**: così non possono più divergere.

### Passo 4 — Chiedersi *perché*, e misurarlo senza addestrare nulla

Il numero dice che la vista rialzata è peggiore, non perché. L'ipotesi era la
**compressione prospettica**: l'indicatore più forte di una caduta è la
rotazione del tronco dalla verticale all'orizzontale, e una telecamera che
guarda dall'alto proietta una persona in piedi e una distesa in modo simile.

Per verificarla abbiamo misurato l'**escursione dell'angolo del tronco** su
cinquanta cadute, sulle due telecamere, **senza addestrare nulla**: è una
grandezza geometrica, non una prestazione.

| | Camera 1 (laterale) | Camera 2 (frontale rialzata) |
|---|---:|---:|
| escursione media | 74,0° ± 24,2 | 33,2° ± 23,5 |
| sequenze sopra 60° | **30 su 39** | 8 su 39 |

Rapporto fra le medie **2,23×**. L'ipotesi regge, e l'informazione su cui il
sistema decide **dalla vista rialzata non c'è**.

#### Quante cadute sono, e perché sono così poche

La domanda è giusta: 39 sembrano poche, e lo sono.

| | |
|---|---:|
| attività di caduta in UP-Fall | 5 (`act01`…`act05`) |
| soggetti nel nostro archivio | 10 |
| **riprese di caduta per telecamera** | **50** |
| coppie sincronizzate (una per telecamera) | 50 |
| coppie **pulite**, dopo aver escluso quelle in cui lo stimatore cambia persona | **39** |

**Le 50 diventano 39 per un motivo solo: le 11 riprese contaminate**
([ISS-134](../ISSUES.md)), che restano disegnate nella figura ma non entrano
nelle medie.

**E le 50 sono 50 perché il nostro archivio contiene un solo trial per
attività.** Tutte le riprese si chiamano `..._trial01_...`: 11 attività × 10
soggetti × 2 telecamere = 220 riprese, di cui 100 di caduta. UP-Fall pubblica
più prove per attività, e scaricarne altre **moltiplicherebbe le cadute
disponibili senza cambiare nulla nel codice**. È l'intervento a costo più basso
per stringere tutti gli intervalli di questo capitolo, ed è dello stesso tipo di
quello già indicato per le cadute reali.

*(Da verificare sulla fonte prima di scriverlo in tesi: quante prove per
attività UP-Fall pubblichi davvero. Il nostro archivio locale ne ha una, e
questo è verificato.)*

#### E perché la soglia dei 60 gradi

Il conteggio «sopra 60°» è preferito al rapporto fra le medie perché le
deviazioni sono grandi — circa un terzo del valore medio sulla vista laterale e
più di due terzi su quella rialzata — e una media con quella dispersione
descrive male il fenomeno.

**Ma quel 60 non era giustificato da nessuna parte**: nel codice era un
letterale senza commento, nel testo compariva solo dentro la tabella
([ISS-144](../ISSUES.md), trovata rispondendo a questa domanda). È una
**convenzione di lettura**, non un criterio derivato dai dati.

Ciò che si può dire, ed è ora nella didascalia della tabella, è che **la
conclusione non dipende da quella scelta**:

| soglia | Camera 1 | Camera 2 |
|---:|---:|---:|
| 30° | 35 | 14 |
| 45° | 34 | 11 |
| **60°** | **30** | **8** |
| 70° | 30 | 4 |
| 80° | 26 | 2 |

Su tutto l'intervallo la vista laterale supera la soglia fra 2,5 e 13 volte più
spesso, senza mai cambiare verso. E le **mediane**, che da nessuna soglia
dipendono, valgono **87,3° contro 22,3°**.

> **La figura è `fig_viewpoint_dist.png`**: una linea per ogni caduta, che
> unisce quanto ha visto la telecamera laterale a quanto ha visto la rialzata
> *sulla stessa caduta*. Prodotta da `figure_tesi.py`, funzione
> `fig_viewpoint_dist`, da `risultati/laboratorio/escursione_viste_10sog.csv`.

### Passo 5 — Perché la misura originale (1,99×) era sbagliata

Due difetti, trovati il 6 settembre, e nessuno dei due riguardava la geometria.

**Il primo ([ISS-133](../ISSUES.md)).** Il codice di misura creava *un solo*
stimatore di posa e lo riusava per tutte le riprese in fila. MediaPipe Pose è
un **tracciatore**: mantiene stato fra un fotogramma e il successivo e non sa
che nel frattempo è cambiato il video. L'ultima immagine di una ripresa —
persona a terra — condizionava la prima della ripresa dopo. Su una singola
sequenza lo scarto arriva a **68°**.

**Il secondo ([ISS-134](../ISSUES.md)).** Su Camera 2 lo stimatore **perde chi
cade e si aggancia a una persona rimasta in piedi o seduta nel campo**, in
**11 riprese su 50**. Su Camera 1 in **0 su 50**. Il difetto arriva anche nei
dati di addestramento: in circa il 12% delle cadute di Camera 2 il
classificatore riceve, per la fase a terra, le grandezze di **un'altra
persona**. Non sta imparando male: sta ricevendo l'ingresso sbagliato.

Rifatta con uno stimatore per ripresa e su dieci soggetti invece di cinque, il
rapporto è **2,23×** escludendo le riprese contaminate (2,13× su tutte e
cinquanta).

### Passo 6 — Le due cause, separate

Questo è nuovo, ed è la risposta a un limite che il testo si limitava a
dichiarare: **il divario di F2 ha due cause dentro, e non sapevamo quale
pesasse.**

La verifica è diretta: rifare le stesse tre righe **escludendo le undici
riprese contaminate**, in addestramento e in verifica. Se il cambio di persona
fosse la causa del divario, sulle riprese pulite il divario dovrebbe
restringersi.

| | con tutte le riprese | **senza le 11 contaminate** |
|---|---:|---:|
| Camera 1 → Camera 1 | 0,822 | 0,822 |
| Camera 1 → Camera 2 | 0,488 | **0,466** |
| Camera 1 + 2 → Camera 2 | 0,731 | 0,673 |
| **divario** | 0,334 | **0,356** |

**Non si restringe: semmai cresce di 0,022, che è dentro il rumore.**

> **Un equivoco da evitare quando si racconta questo passaggio.** Il salto da
> **0,822 a 0,488 non c'entra con le undici riprese**: è l'effetto del cambio di
> telecamera, cioè la differenza fra la prima e la seconda riga della tabella.
> L'effetto dell'esclusione delle riprese contaminate è il confronto fra le due
> colonne qui sopra, ed è piccolo: da 0,488 a 0,466.

**La conclusione è quindi più precisa di quanto il testo dicesse:** il cambio di
persona dello stimatore falsava la **misura geometrica** — è lì che toglierlo
sposta il rapporto da 2,13× a 2,23× — ma **non è ciò che rende la vista
rialzata peggiore per il classificatore**. Il divario di F2 è sostanzialmente
tutto compressione prospettica.

*Una cautela, dichiarata anche nel codice:* le due esecuzioni non hanno lo
stesso insieme di verifica, perché togliere undici riprese di caduta toglie 274
finestre positive da Camera 2. La seconda colonna misura «il divario sulle
riprese pulite», non «lo stesso divario senza l'effetto dello stimatore». Per la
domanda posta è la misura giusta lo stesso.

### Passo 6-bis — Un risultato del capitolo che il rifacimento smentisce

Il Capitolo 4 chiudeva questa sezione con un paragrafo intitolato «Un risultato
controintuitivo»:

> *un modello addestrato su Camera 1 e verificato su Camera 2 **batte di 2,5×**
> un modello addestrato direttamente su Camera 2 — quindi la qualità del punto
> di vista in addestramento conta più della sua corrispondenza con quello di
> esercizio.*

Era l'affermazione più memorabile della sezione: contraria all'intuizione, con
una morale operativa netta.

**A dieci soggetti si rovescia.**

| | cinque soggetti | **dieci soggetti** |
|---|---:|---:|
| Camera 1 → Camera 2 | 0,434 | 0,488 |
| Camera 2 → Camera 2 | ≈ 0,17 | **0,753** |
| | 2,5× a favore del **trasferimento** | **1,5× a favore dell'addestramento diretto** |

E si rovescia anche escludendo le riprese contaminate (0,466 contro 0,747),
quindi non è un effetto dello stimatore.

**Perché era successo.** Con cinque soggetti, addestrare su Camera 2 significa
imparare da quattro persone su riprese che contengono poca informazione, e la
varianza fra fold è enorme — quella riga aveva la dispersione più alta della
tabella. Il valore basso era compatibile con il caso quanto con l'effetto, e
nessuno aveva calcolato quanti soggetti servissero per distinguerli: è la
disciplina che il lavoro ha adottato **dopo**, ed è la stessa che ha fatto
cadere «la foresta è la migliore» ([C1](C1_ingressi_della_foresta.md)).

**Che cosa dice il capitolo adesso.** L'affermazione è dichiarata **ritirata**,
con i numeri vecchi e nuovi accanto, e sostituita da quella ordinaria:
addestrare sulla vista di esercizio è meglio che trasferirvi da un'altra, anche
quando quella di esercizio è la vista povera.

Sopravvive però un'osservazione più debole e più utile: **addestrare su
entrambe le viste (0,731) e addestrare solo su quella di esercizio (0,753) non
sono distinguibili**, perché distano meno della dispersione fra soggetti. Chi
installa il sistema può quindi scegliere in base a ciò che ha: se dispone di
riprese dalla vista in cui il sistema lavorerà, gli bastano quelle.

### Passo 7 — Il dato che ha cambiato un criterio di lavoro

Su Camera 2 una posa viene trovata nel **97,0%** dei campioni; su Camera 1
nell'**85,7%**.

**La vista che porta meno informazione è quella in cui lo stimatore fallisce
meno spesso** — perché quando perde il soggetto trova comunque qualcun altro.

La quota di pose rilevate **non è una misura di qualità**, e veniva usata come
criterio per accettare o scartare una sessione registrata in casa. Non lo è
più, e il protocollo di ripresa del Capitolo 5 non la usa più da sola.

### Passo 8 — Il cambio di ambiente

Il modello addestrato su UP-Fall, applicato a UR-Fall senza toccare nulla:

| | F2 |
|---|---:|
| con la soglia con cui è schierato | **0,034** |
| con la soglia ritarata sul dominio di destinazione | 0,492 |
| *(riferimento: la stessa misura in dominio)* | *0,971* |

> **La figura è `fig_dominio.png`**, prodotta da `figure_tesi.py`, funzione
> `fig_dominio`, da `risultati/campo/pr_auc_allineato.json`. Mostra il divario
> diviso nelle due parti descritte qui sotto.

### Passo 9 — La scomposizione del divario, spiegata

È il contributo originale della sezione, e vale la pena dirla per esteso perché
in una riga sembra un tecnicismo.

**Il problema.** Il sistema, portato su un archivio nuovo, passa da 0,971 a
0,034. Un crollo così può nascere da due cose molto diverse:

1. il modello **ordina ancora bene** le finestre — le cadute ricevono punteggi
   più alti delle non-cadute — ma su una **scala diversa**. La soglia 0,50,
   giusta nel dominio di casa, nel dominio nuovo è troppo alta o troppo bassa e
   taglia nel posto sbagliato. In questo caso **basta ritarare la soglia**, e
   chi installa il sistema può farlo;
2. il modello **non separa più**: cadute e non-cadute ricevono punteggi
   mescolati. Qui **nessuna soglia salva niente**, perché non esiste un taglio
   buono su un ordinamento sbagliato.

Le due diagnosi portano a conclusioni opposte — «serve una taratura in loco»
contro «serve un altro modello» — e l'F2 con una soglia fissa non le distingue.

**Come si separano.** Si cerca la soglia che sull'archivio nuovo dà il risultato
migliore possibile, usando le sue etichette — la **soglia oracolo**, che chi
installa non possiede ([C4](C4_soglia_oracolo.md)) — e si guarda dove arriva:

| | valore | che cos'è |
|---|---:|---|
| in dominio, soglia schierata | 0,971 | quanto il sistema vale a casa propria |
| archivio nuovo, soglia schierata | 0,034 | quanto vale davvero fuori |
| archivio nuovo, **soglia oracolo** | 0,492 | il massimo che una ritaratura potrebbe dare |

Il divario totale è 0,971 − 0,034 = **0,937**, e si divide in due:

- **da 0,034 a 0,492 → 0,457, cioè il 49% del divario:** è **taratura**.
  Recuperabile, in linea di principio, da chi installa il sistema — se avesse un
  modo per scegliere la soglia, che è a sua volta un problema aperto.
- **da 0,492 a 0,971 → 0,479, cioè il 51%:** è **perdita reale** della capacità
  di separare. Nessuna soglia la recupera.

**Circa metà e metà.** La conferma indipendente viene dalla PR-AUC, che è
indipendente dalla soglia per costruzione: vale **1,79 volte il caso**
sull'archivio nuovo contro **18,7 volte** in dominio ([B1](B1_pr_auc.md)). Se
il problema fosse solo di scala, la PR-AUC non si muoverebbe.

*(Fino al 3 settembre qui comparivano 0,612 e una divisione «due terzi
taratura, un terzo perdita»: venivano da un altro esperimento, con un'altra
estrazione delle feature e un'altra prevalenza — [ISS-131](../ISSUES.md).
Con «due terzi taratura» il capitolo si contraddiceva a due pagine di
distanza, perché la PR-AUC diceva già che la perdita è reale.)*

### Passo 10 — «In 2 sequenze su 25 la vista rialzata osserva quanto quella laterale»

Questa frase era nel testo e non c'è più. Vale la pena spiegare che cos'era,
perché è un buon esempio di come un'affermazione può reggere per mesi.

**Che cosa diceva.** Su 25 cadute, in 2 la telecamera rialzata aveva misurato
un'escursione **uguale o maggiore** di quella laterale. Serviva come cautela:
*il vantaggio della vista laterale è medio, non universale, e ci sono casi in
cui le due si equivalgono.*

**Perché non regge.** Le due sequenze «alla pari» erano **due delle undici in
cui lo stimatore cambia persona**: la telecamera rialzata sembrava vedere una
grande rotazione del tronco perché stava misurando **il tronco di qualcun
altro**, che nel frattempo si sedeva.

**Che cosa resta.** Rifatta la misura su 39 sequenze pulite, il caso alla pari
è **uno**, e il rapporto minimo su tutte è **0,98** — cioè nella peggiore delle
sequenze la vista rialzata osserva il 98% di quella laterale, mai di più.

**La cautela quindi si indebolisce invece di rafforzarsi:** l'effetto del punto
di vista è **più regolare** di quanto il testo dichiarasse. È la stessa
direzione del rapporto fra le medie, che è passato da 1,99× a 2,23×.

---

## Che cosa questa risposta non copre

Tre limiti restavano dichiarati; **due sono stati chiusi il 7 settembre.**

- ~~Le tre righe sono run a cinque soggetti mentre la misura geometrica è a
  dieci.~~ **Chiuso:** rieseguite a dieci soggetti sul dataset riestratto
  ([EXP-026](../EXPERIMENTS.md)).
- ~~Le tre righe non sono state rieseguite escludendo le riprese contaminate,
  quindi le due cause non sono separate.~~ **Chiuso:** separate, e il divario
  **non** dipende dallo stimatore.
- **Due archivi non sono una popolazione di ambienti.** Questo resta, e non è
  chiudibile con i dati disponibili: UR-Fall è un secondo laboratorio, non una
  casa. Il trasferimento a un ambiente domestico è misurato altrove e in
  un'altra forma, con le sessioni registrate ([B2](B2_controesempi.md)).
- **Il verso opposto non è misurato per intero.** È stato aggiunto Camera 2 su
  sé stessa (Passo 6-bis), ma non «addestrare sulla vista rialzata e verificare
  sulla laterale», che direbbe se la fragilità al cambio di vista sia simmetrica
  o valga solo in una direzione.

---

## Dove guardare

| | |
|---|---|
| le tre righe, a dieci soggetti | `risultati/laboratorio/viste_incrociate_10sog.json` |
| le stesse senza le riprese contaminate | `..._senza_contaminate.json` |
| misura geometrica | `risultati/laboratorio/escursione_viste_10sog.csv` e il suo `_riepilogo.json` |
| trasferimento esterno | `risultati/campo/pr_auc_allineato.json`, `risultati/esterno/` |
| misura originale, tenuta per confronto | `risultati/cinque_soggetti/exp013_camera_viewpoint.csv` |
| script | `pipeline/viste_incrociate.py`, `pipeline/escursione_viste.py`, `pipeline/valuta_esterno.py` |
| figure | `tesi/figure/fig_viste.png`, `fig_viewpoint_dist.png`, `fig_dominio.png`, `fig_due_camere.png` — ciascuna con la sua scheda `.txt` accanto |
| registro | [EXP-020](../EXPERIMENTS.md), [EXP-026](../EXPERIMENTS.md), [ISS-133](../ISSUES.md), [ISS-134](../ISSUES.md), [ISS-129](../ISSUES.md), [ISS-131](../ISSUES.md) |
| nella tesi | Capitolo 4, `tab:escursione`, `tab:viste`, `fig:due_camere`, `fig:viewpoint_dist` |
