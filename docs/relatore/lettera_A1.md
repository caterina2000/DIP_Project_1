# Lettera al relatore — A1, resilienza al cambio di telecamera e di ambiente

*Testo pronto da inviare. La scheda completa, con i passaggi e gli artefatti, è
in [A1_cambio_di_vista_e_di_ambiente.md](A1_cambio_di_vista_e_di_ambiente.md).*

---

Buongiorno professore,

la aggiorno sulla prima delle sue richieste — verificare che il sistema non
funzioni soltanto sulle riprese su cui è stato addestrato, cambiando
inquadratura e cambiando ambiente.

**La risposta breve è che il sistema non è resiliente**, e negli ultimi due
giorni siamo riusciti a dire anche *perché*, separando due cause che prima
stavano insieme. Cambiare punto di vista costa **0,334 di F2**; cambiare
archivio porta la prestazione quasi a zero.

## Il cambio di inquadratura

UP-Fall riprende ogni caduta con due telecamere sincronizzate, quindi il
confronto si fa a parità di tutto il resto: stessa persona, stessa caduta,
stesso istante. **Camera 1 è laterale**, all'altezza del busto; **Camera 2 è
frontale e più in alto**, inclinata verso il basso — è la «vista rialzata», ed è
anche quella che un'installazione reale tende a scegliere, perché da un angolo
in alto si copre più stanza.

Tre addestramenti, stessa architettura, stessi iperparametri, stessa soglia
dichiarata prima di guardare i risultati:

| addestrata su | verificata su | F2 | falsi allarmi | cadute perse |
|---|---|---:|---:|---:|
| Camera 1 | Camera 1 | 0,822 ± 0,099 | 722 | 186 |
| Camera 1 | **Camera 2** | **0,488 ± 0,119** | **3.252** | 451 |
| Camera 1 + 2 | Camera 2 | **0,731 ± 0,188** | 751 | 335 |

Cambiare inquadratura costa **0,334 di F2**, cioè circa **tre volte la
dispersione fra soggetti**: non è un effetto del caso. Addestrare su entrambe le
viste ne recupera il **73%**, e riporta i falsi allarmi da 3.252 a 751 — al
livello della vista buona.

Il dato che si vede solo separando i due errori, come lei aveva chiesto al punto
5, è che **trasferire su una vista mai vista non peggiora un po' tutto: fa
esplodere un errore solo.** I falsi allarmi si moltiplicano per quattro e mezzo,
le cadute perse per due e mezzo.

**C'è una figura**, `fig_viste.png`: a sinistra l'F2 con la dispersione fra
soggetti, a destra i due errori contati separatamente. È prodotta dal codice
(`pipeline/figure_tesi.py`) a partire dal file dei risultati, come tutte le
altre.

### Questi numeri sono cambiati, e le dico perché

Nella versione che le avevo mandato le tre righe erano **0,857 / 0,434 / 0,678**,
con un divario di 0,422. Erano l'ultima misura del lavoro ancora ferma a
**cinque** soggetti, mentre la misura geometrica che le spiega era già a dieci:
due provenienze diverse nello stesso paragrafo. Le ho rieseguite a dieci
soggetti, sul dataset riestratto.

Il divario si riduce da 0,422 a 0,334 e il rimedio funziona meglio (dal 58% al
73%). **La conclusione non cambia, i numeri sì.**

Nella stessa occasione ho corretto un errore precedente: la prima riga
riportava 0,872, che apparteneva a **un'altra architettura** ripresa da una
tabella diversa. Con la prima riga di un modello e le altre due di un altro, il
divario misurava anche la differenza fra i due modelli. Ora tutte e tre le
righe escono da una sola esecuzione dello stesso script, così non possono più
divergere.

## Perché la vista rialzata è peggiore

L'ipotesi era la compressione prospettica: l'indicatore più forte di una caduta
è la rotazione del tronco dalla verticale all'orizzontale, e una telecamera che
guarda dall'alto vede quella rotazione avvenire *verso di sé*, quindi compressa.

Misurando l'escursione dell'angolo del tronco su cinquanta cadute, **senza
addestrare nulla**:

| | Camera 1 (laterale) | Camera 2 (rialzata) |
|---|---:|---:|
| escursione media | 74,0° ± 24,2 | 33,2° ± 23,5 |
| sequenze sopra 60° | **30 su 39** | 8 su 39 |

Rapporto **2,23×**. L'ipotesi regge: dalla vista rialzata l'informazione su cui
il sistema decide, semplicemente, non c'è. La figura è
`fig_viewpoint_dist.png`, e mostra una linea per ogni caduta che unisce le due
viste della *stessa* caduta.

**Questo numero era 1,99× e prima ancora 4,32×.** Le tre versioni non hanno mai
cambiato la direzione dell'effetto, e ogni volta hanno cambiato il modo di
misurarlo. L'ultima correzione è la più istruttiva: il codice di misura creava
**un solo** stimatore di posa e lo riusava per tutte le riprese in fila, ma
MediaPipe Pose è un *tracciatore* — mantiene stato fra un fotogramma e il
successivo e non sa che nel frattempo è cambiato il video. L'ultima immagine di
una ripresa, persona a terra, condizionava la prima della ripresa dopo: su una
sequenza lo scarto arriva a 68°.

## Il difetto che ho trovato guardando le immagini, non i numeri

Componendo una figura ho visto uno scheletro corretto disegnato addosso alla
persona sbagliata, con accanto un angolo che sembrava perfettamente sensato.

**Su Camera 2 lo stimatore perde chi cade e si aggancia a una persona rimasta in
piedi o seduta nel campo, in 11 riprese su 50. Su Camera 1 in 0 su 50.** Il
difetto arriva anche nei dati di addestramento: in circa il 12% delle cadute di
Camera 2 il classificatore riceve, per la fase a terra, le grandezze di
un'altra persona. Non sta imparando male — sta ricevendo l'ingresso sbagliato.

Un dato collegato, che mi ha fatto cambiare un criterio di lavoro: su Camera 2
una posa viene trovata nel **97,0%** dei campioni, contro l'**85,7%** di
Camera 1. **La vista che porta meno informazione è quella in cui lo stimatore
fallisce meno spesso**, perché quando perde il soggetto trova comunque
qualcun altro. La quota di pose rilevate non è una misura di qualità, e la usavo
per decidere se accettare una sessione registrata in casa.

## Le due cause, separate

Nella versione precedente dovevo limitarmi a dichiarare che il divario di F2 ha
**due** cause — la compressione ottica e il cambio di persona — senza sapere
quale pesasse. Ho rifatto le tre righe escludendo le undici riprese contaminate,
in addestramento e in verifica:

| | con tutte le riprese | senza le 11 contaminate |
|---|---:|---:|
| Camera 1 → Camera 1 | 0,822 | 0,822 |
| Camera 1 → Camera 2 | 0,488 | 0,466 |
| Camera 1 + 2 → Camera 2 | 0,731 | 0,673 |
| **divario** | 0,334 | **0,356** |

**Il divario non si chiude: semmai cresce di 0,022, che è dentro il rumore.**

La conclusione è quindi più precisa di prima: il cambio di persona falsava la
**misura geometrica** — è lì che toglierlo sposta il rapporto — ma **non è ciò
che rende la vista rialzata peggiore per il classificatore**, che è
sostanzialmente tutta compressione prospettica.

## Un risultato del capitolo che ho dovuto ritirare

Devo segnalarle che il rifacimento a dieci soggetti ha smentito un'affermazione
che il capitolo presentava come «risultato controintuitivo»: che un modello
addestrato su Camera 1 e verificato su Camera 2 battesse di **2,5×** un modello
addestrato direttamente su Camera 2.

| | cinque soggetti | dieci soggetti |
|---|---:|---:|
| Camera 1 → Camera 2 | 0,434 | 0,488 |
| Camera 2 → Camera 2 | ≈ 0,17 | **0,753** |

**Il confronto si rovescia**, e si rovescia anche escludendo le riprese
contaminate. Con cinque soggetti quella riga aveva la dispersione più alta della
tabella, e il valore basso era compatibile con il caso quanto con l'effetto:
nessuno aveva calcolato quanti soggetti servissero per distinguerli, che è la
disciplina che il lavoro ha adottato dopo.

Ho quindi ritirato l'affermazione dal Capitolo 4, sostituendola con quella
ordinaria — addestrare sulla vista di esercizio è meglio che trasferirvi da
un'altra. Sopravvive un'osservazione più debole e più utile: **addestrare su
entrambe le viste (0,731) e addestrare solo su quella di esercizio (0,753) non
sono distinguibili fra loro**, perché distano meno della dispersione fra
soggetti. Chi installa il sistema può scegliere in base a ciò che ha.

## Il cambio di ambiente

Qui serve un archivio registrato da altri, in un'altra stanza, con altre
persone: ho usato UR-Fall. Il modello addestrato su UP-Fall, applicato senza
toccare nulla:

| | F2 |
|---|---:|
| in dominio, per riferimento | 0,971 |
| archivio nuovo, con la soglia con cui è schierato | **0,034** |
| archivio nuovo, con la soglia ritarata sulle sue etichette | 0,492 |

Il contributo originale della sezione non è «il sistema non trasferisce», ma la
**scomposizione** di quel crollo, perché da esso dipendono due conclusioni
opposte. Un crollo può nascere da due cose molto diverse:

1. il modello **ordina ancora bene** le finestre ma su una scala spostata: la
   soglia taglia nel posto sbagliato, e **basta ritararla**;
2. il modello **non separa più**: nessuna soglia serve a niente.

Per distinguerle si cerca la soglia migliore possibile sull'archivio nuovo
*usando le sue etichette* — la soglia oracolo, che chi installa non possiede — e
si guarda dove arriva. Il divario totale è 0,971 − 0,034 = **0,937**, e si
divide così:

- **da 0,034 a 0,492 — il 49%** — è **taratura**: recuperabile, in principio, da
  chi installa;
- **da 0,492 a 0,971 — il 51%** — è **perdita reale** della capacità di
  separare: nessuna soglia la recupera.

**Circa metà e metà.** La conferma indipendente viene dalla PR-AUC, che non
dipende dalla soglia per costruzione: vale **1,79 volte il caso** sull'archivio
nuovo contro **18,7 volte** in dominio. Se il problema fosse solo di scala, la
PR-AUC non si muoverebbe. C'è una figura anche per questa scomposizione,
`fig_dominio.png`.

## Che cosa questa risposta non copre

- **Due archivi non sono una popolazione di ambienti.** UR-Fall è un secondo
  laboratorio, non una casa: il trasferimento a un ambiente domestico è misurato
  altrove, con le sessioni registrate.
- **Il verso opposto non è misurato per intero.** Ho aggiunto Camera 2 su sé
  stessa, ma non «addestrare sulla rialzata e verificare sulla laterale», che
  direbbe se la fragilità al cambio di vista sia simmetrica.
- Le riprese contaminate sono escluse da un criterio automatico — un salto
  dell'angolo del tronco oltre una soglia dichiarata — e non da un controllo
  umano su tutte e cinquanta.

Resto a disposizione, e la ringrazio.
