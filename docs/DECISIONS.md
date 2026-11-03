# DECISIONS — DIP_Project_1

Scelte metodologiche con la ragione che le motiva. Serve all'orale: ogni voce
deve reggere alla domanda «perche' cosi' e non altrimenti».

Numerazione da 100 per non confondersi con le DEC-0xx del progetto storico.

| ID | Decisione | Stato |
|---|---|---|
| [DEC-100](#dec-100) | Un solo CSV con tutte e 34 le grandezze | MOTIVATA |
| [DEC-101](#dec-101) | Separabilita' misurata per camera, criterio del minimo | MOTIVATA |
| [DEC-102](#dec-102) | Ricampionamento a lunghezza comune prima del DTW | MOTIVATA |
| [DEC-103](#dec-103) | Selezione avida con vincolo di correlazione | MOTIVATA |
| [DEC-104](#dec-104) | Tre modalita' di etichettatura da confrontare | DA DECIDERE CON ABLATION |
| [DEC-105](#dec-105) | Soglia fissa, dichiarata a priori | MOTIVATA |
| [DEC-106](#dec-106) | Tre dataset, tre ruoli distinti | MOTIVATA |
| [DEC-107](#dec-107) | Il classificatore risponde a «sta cadendo?» | MOTIVATA |
| [DEC-108](#dec-108) | La regola di allarme schierata resta «cinque consecutive» | MOTIVATA |
| [DEC-109](#dec-109) | Due configurazioni distinte: quella schierata e quella rivista sul campo | MOTIVATA |

---

<a id="dec-100"></a>
## DEC-100 — Un solo CSV con tutte e 34 le grandezze

Nel progetto precedente ogni bacino aveva il suo file e per confrontarli
bisognava rileggerli e allinearli a mano. Due colonne omonime di bacini diversi
(`d_trunk_angle` in A2 e in A3, con unita' diverse) potevano collassare
silenziosamente in un merge.

Qui A1, A2, A3 e le nove integrali stanno nelle stesse righe, con il prefisso
del bacino nel nome. Il DTW le confronta senza unire nulla e l'omonimia e'
impossibile per costruzione.

---

<a id="dec-101"></a>
## DEC-101 — Separabilita' misurata per camera, criterio del minimo

**Scelta:** il punteggio DTW si calcola separatamente su Camera 1 e Camera 2, e
la selezione usa `robusto = min(cam1, cam2)`.

**Perche'.** L'analisi precedente mescolava le due camere in un punteggio solo.
Ma il divario piu' grande misurato in tutto il lavoro e' proprio quello fra i
due punti di vista: l'angolo del tronco nel piano immagine ha 84 gradi di
escursione fra eretto e disteso sulla vista laterale e **3 gradi** sulla vista
frontale rialzata. Una grandezza che separa benissimo di profilo puo' non
separare nulla dall'alto, e mescolando le camere il crollo resta invisibile
fino alla misura sul modello finito.

**Perche' il minimo e non la media.** Una grandezza ottima da una vista e
inutile dall'altra e' esattamente quella da escludere, e la media la
premierebbe. Il minimo chiede che regga da entrambi i punti di vista.

**Costo accettato.** Il criterio scarta cose valide da una vista sola —
`A1_asse_mag` fa 1,314 su cam2, il secondo miglior punteggio dell'intera
analisi su quella camera, ma 1,101 su cam1 ed esce. E' il prezzo di un sistema
che deve funzionare senza sapere come e' stata montata la telecamera.

Vedi [EXP-005](EXPERIMENTS.md#exp-005).

---

<a id="dec-102"></a>
## DEC-102 — Ricampionamento a lunghezza comune prima del DTW

**Scelta:** ogni curva viene portata a 200 campioni dopo lo z-score e prima del
confronto DTW.

**Perche'.** Il vincolo di warping `|i - j| <= 10` non si puo' applicare a due
curve di lunghezza diversa senza allargarlo ad almeno `|n - m|`, altrimenti
nessun cammino di allineamento arriva in fondo — ed e' quello che il codice
faceva, con `window=max(finestra, abs(n - m))`.

Su questo dataset le riprese di caduta durano ~180 fotogrammi e quelle di
attivita' quotidiana ~820. Quindi:

- coppie caduta-caduta: lunghezze simili, banda 10
- coppie ADL-ADL: lunghezze simili, banda 10
- coppie **incrociate**: differenza ~640, banda **630**, di fatto libera

Le coppie che devono risultare distanti ricevevano la massima liberta' di
deformazione. `mu_FA` deflazionato, `mu_intra` intatto: tutti i punteggi
schiacciati verso 1.

**Cosa si perde.** L'informazione di durata. **Perche' e' accettabile:** la
durata di una ripresa e' identica per tutte e 34 le grandezze, quindi non puo'
in nessun caso contribuire a distinguerle fra loro — mentre il rumore che
introduce si'. Se la durata serve come discriminante, e' una feature a se' e va
misurata a parte, non fatta entrare di straforo nella metrica di forma.

**Verificato** su dati sintetici con la stessa asimmetria di durata: punteggio
da 5,055 a 7,201 sulle stesse curve. Vedi [ISS-101](ISSUES.md#iss-101) e
[EXP-005](EXPERIMENTS.md#exp-005).

---

<a id="dec-103"></a>
## DEC-103 — Selezione avida con vincolo di correlazione

**Scelta:** si scorre la classifica DTW dall'alto e si aggiunge una grandezza
solo se la sua correlazione assoluta con **tutte** le gia' scelte sta sotto
0,85. Chi viene escluso e' dichiarato, con il nome di chi lo blocca e il valore
di r.

**Perche'.** Il DTW valuta ogni grandezza isolatamente: non sa nulla delle
altre, quindi se lo stesso fenomeno fisico e' misurato in tre modi lo premia
tre volte. Le prime dodici della classifica contenevano `A2_testa_rel_y`,
`A2_angolo_tronco` e `A3_testa_rel_y` correlate fra loro sopra 0,94 — sono
tutte «quanto e' verticale il tronco». Darle tutte e tre alla rete significa
occupare tre posti con un segnale solo.

**Perche' 0,85.** Sopra 0,90 il vincolo non morde (correlazione media 0,393,
praticamente come senza vincolo). A 0,75 la media scende a 0,240 ma entrano
grandezze molto piu' in basso in classifica. 0,85 e' il compromesso adottato
come predefinito, non come verita': il parametro e' `--max-corr`.

**Su cosa si misura la correlazione.** Solo sui fotogrammi con posa valida. Sui
fotogrammi senza posa le grandezze valgono zero per costruzione e sarebbero
correlate fra loro per un motivo che non ha niente a che vedere con la dinamica
del corpo.

**Limite dichiarato.** Questa e la DTW sono una preselezione euristica.
L'arbitro e' la LOSO sul modello. Vedi [EXP-006](EXPERIMENTS.md#exp-006).

---

<a id="dec-104"></a>
## DEC-104 — Tre modalita' di etichettatura da confrontare

**Stato: DA DECIDERE CON ABLATION.** La voce esiste per fissare i termini del
confronto, non per dichiarare una scelta gia' fatta.

Il dataset ha tre etichette per fotogramma: 0 normale, 1 caduta in corso, 2 a
terra. Cosa farne a livello di finestra non e' ovvio, e la ragione emerge da un
dato misurato in [EXP-003](EXPERIMENTS.md#exp-003):

Fra le attivita' quotidiane c'e' `act11 = laying`, sdraiarsi volontariamente:
**20.980 fotogrammi, il 18% del dataset, etichettati 0.** Il dataset contiene
quindi ventimila fotogrammi di persona distesa a terra con etichetta 0 e
diecimila con etichetta 2. Lo stato finale e' visivamente quasi identico: la
differenza sta solo nel modo in cui ci si e' arrivati.

Le tre modalita' rispondono in modo diverso:

| modalita' | cosa fa | costo |
|---|---|---|
| `scarta` | butta le finestre di «a terra dopo caduta», tiene «sdraiato volontariamente» come negativo | perde il 59% dei fotogrammi di caduta |
| `caduta` | mappa 2 verso 1 | chiede di distinguere due immagini quasi identiche, con una finestra da 2,44 s che spesso non contiene piu' la transizione |
| `tre_classi` | tiene 2 separata | lascia decidere al modello, ma triplica lo spazio di uscita su una classe rara |

Il confronto va fatto a parita' di tutto il resto e valutato **a livello di
evento**, non di finestra: `y_allarme` e' fissa (la finestra contiene una
caduta o uno stato a terra) mentre `y_train` cambia con la modalita', altrimenti
si confronterebbero metriche calcolate su definizioni diverse di positivo.

---

<a id="dec-105"></a>
## DEC-105 — Soglia fissa, dichiarata a priori

**Scelta:** la soglia di allarme e' **0,5**, fissata prima di guardare i dati e
uguale per tutti i fold e tutte le architetture. Il validation serve solo a
fermare l'addestramento.

**Perche'.** [EXP-010](EXPERIMENTS.md#exp-010) ha confrontato sei regole. Le
soglie scelte per fold con il massimo di F-beta avevano deviazione **0,37 su un
intervallo [0, 1]**: da 0,01 a 0,99. Con un solo soggetto di validazione la
stima e' talmente rumorosa che l'adattamento costa piu' di quanto renda.

Una soglia fissa non stima nulla dai dati, quindi **non puo' sovradattarsi**.
E' la scelta che non richiede giustificazione empirica — il che e' esattamente
il punto, perche' una giustificazione empirica qui non sarebbe onesta.

**L'onesta' del ragionamento, che va detta all'orale.** Nell'esperimento la
soglia fissa risulta anche la migliore (F2 0,851 contro 0,810) e la piu'
stabile (±0,078 contro ±0,117). Ma **quel confronto e' stato fatto sui fold di
test**, quindi scegliere 0,5 «perche' vince» sarebbe selezione sul test set, e
0,851 non sarebbe piu' una stima imparziale.

Cio' che l'esperimento stabilisce legittimamente non e' «0,5 e' il valore
migliore» — che sarebbe una conclusione sui dati di test — ma **«scegliere la
soglia su un solo soggetto di validazione e' una procedura dannosa»**, che e'
una conclusione sulla PROCEDURA e non dipende da quale valore vinca. Da li' la
soglia fissa si adotta per la ragione a priori scritta sopra.

**Perche' e' necessaria anche per il confronto fra architetture.** Con la soglia
scelta per fold, la differenza fra GRU e LSTM resterebbe sepolta sotto il
rumore della taratura: la dispersione della soglia e' dello stesso ordine delle
differenze che si vogliono misurare. Con la soglia fissa, cio' che si misura e'
il modello.

**Cosa NON stabilisce.** Che 0,5 vada bene in esercizio. Non va bene: vedi
[DEC-106](#dec-106).

---

<a id="dec-106"></a>
## DEC-106 — Tre dataset, tre ruoli distinti

**Scelta:** UP-Fall, le registrazioni domestiche e UR-Fall non si mescolano.
Ognuno risponde a una domanda che gli altri non possono rispondere.

| dataset | cosa contiene | a cosa serve |
|---|---|---|
| **UP-Fall** | 10 soggetti, 218 riprese, laboratorio | addestrare e misurare il **recall** |
| **sessioni domestiche** | 10,6 ore, casa vera | **tarare la soglia** sui falsi allarmi reali |
| **UR-Fall** | 11.937 fotogrammi, altro laboratorio | **test esterno** di generalizzazione |

**Il motivo e' il problema della prevalenza di base.** UP-Fall ha il **12,4%**
di finestre positive: e' un laboratorio dove un quarto delle riprese sono
cadute. In casa la prevalenza e' praticamente zero — una persona anziana cade
forse due volte l'anno.

La board decide 4,5 volte al secondo, cioe' 16.200 volte l'ora. Con il tasso di
falsi positivi misurato in [EXP-009](EXPERIMENTS.md#exp-009), 9,4%:

```
16.200 decisioni/ora  x  9,4%  =  1.523 falsi allarmi all'ora
```

Un modello con F2 = 0,85 su UP-Fall e' **inutilizzabile** in casa senza
ricalibrazione. Non perche' sia cattivo, ma perche' la soglia e' stata scelta su
una distribuzione che fuori dal laboratorio non esiste.

**E il dato di esercizio esiste gia'.** Contando gli allarmi effettivamente
emessi dal sistema schierato nelle sessioni registrate:

| blocco | ore | allarmi | per ora |
|---|---:|---:|---:|
| `bloccononni` (senza cadute) | 1,20 | 150 | **124,9** |
| `bloccomulti_3persone` | 0,66 | 150 | 226,9 |
| `bloccocadute_nonni` (con cadute reali) | 0,75 | 57 | 76,0 |
| `bloccodurata5h` | 6,11 | 30 | **4,9** |

Il blocco da cinque ore fa molto meglio degli altri, il che dice che la
sbavatura dipende anche dalla scena e non solo dalla soglia. Ma 4,9 all'ora
sono comunque 118 al giorno.

**Divisione dei compiti che ne segue.** Le sessioni domestiche misurano i falsi
allarmi ma nei blocchi senza cadute non possono misurare il recall; UP-Fall
misura il recall ma non dice nulla sui falsi allarmi reali; UR-Fall, con camera
e frame rate diversi, dice se il modello ha imparato la caduta o ha imparato
UP-Fall. Nessuno dei tre e' sostituibile con un altro.

**Ostacolo tecnico dichiarato.** Le sessioni domestiche e UR-Fall hanno colonne
del vecchio insieme A3 a dieci grandezze, senza integrali. Per usarle con il
modello nuovo servira' riestrarre le feature con `src/geometry.py` dai
fotogrammi salvati (58.815 nelle sessioni). Finche' non e' fatto, quelle
registrazioni restano inutilizzabili.

---

<a id="dec-107"></a>
## DEC-107 — Il classificatore risponde alla domanda «sta cadendo?»

**Scelta:** il positivo è l'**evento** (`fall`), non lo stato (`fallen`) né la loro unione.

**Perché.** Misurato a parità di tutto il resto ([EXP-015](EXPERIMENTS.md#exp-015)), l'evento è l'unico compito su cui il negativo difficile sparisce — **0,0%** di allarmi sui distesi volontari contro 12,5% dello stato — ed è anche il più facile: F2 0,831 con precisione 0,924, il migliore dei tre.

La ragione è fisica ed è misurata sui fotogrammi: fra caduta e sdraiarsi volontario il rapporto delle mediane è 30× sulla velocità del bacino, 42× sull'escursione del tronco, **139× sulla discesa**. Fra *essere a terra dopo una caduta* ed *essere disteso per scelta* è **1,3×**. La transizione discrimina, la posa no.

**Cosa NON risolve.** Una caduta fuori campo o durante un buco di posa non produce transizione osservabile. Serve una via lenta — altezza dal pavimento, immobilità, durata — con tre condizioni congiunte e quindi pochi falsi allarmi. Il costo misurato è una caduta su cinque, che con cinque cadute non è interpretabile ma ha la direzione attesa.

**Conferma esterna.** OmniFall 2025, VideoMAE da 87 milioni di parametri: F1 65,6% sull'evento contro 41,0% sullo stato. Il divario evento-stato è il problema aperto del campo, e ha lo stesso segno del nostro.

**Il seguito.** Il confronto fra le tre modalità di [DEC-104](#dec-104) va riletto alla luce di questa scelta: `scarta` era stata misurata a recall 0,495 contro un metro che contava lo stato come positivo, cioè su una domanda diversa da quella che ora è la nostra.

---

<a id="dec-108"></a>
## DEC-108 — La regola di allarme schierata resta «cinque finestre consecutive»

**Scelta.** La configurazione dichiarata come schierata mantiene la regola
**cinque finestre consecutive sopra soglia, poi trenta secondi di
sospensione**. Le regole alternative --- cumulativa, e isteresi «K su M» ---
si riportano come **analisi di sensibilita' fuori linea**, non come nuova
configurazione validata.

**Perche', ed e' un argomento di metodo, non di prestazione.** La sessione del
9 settembre ([EXP-036](EXPERIMENTS.md#exp-036)) mostra che la regola schierata
non rileva nessuna delle tre cadute messe in scena, mentre `0,40 con due
consecutive` ne prenderebbe due. La tentazione e' evidente: cambiare la regola.

Ma quei punteggi sono **gli stessi dati su cui la nuova regola verrebbe
scelta**. Sceglierla li' e poi usarli per dimostrare che funziona meglio e'
adattamento ai dati, e produrrebbe un numero che non regge fuori. E' il rilievo
del relatore del 2026-09-09, ed e' corretto: *«il rischio sarebbe quello di
osservare gli stessi dati domestici, scegliere la regola che funziona meglio su
quei dati e poi usare quegli stessi dati per dimostrare che la nuova regola
funziona meglio»*.

**Cosa si puo' dire, e va detto.** Che la regola schierata ha mancato tre
cadute su tre; che il classificatore le aveva viste (picchi 0,540 e 0,720
contro una soglia di 0,50); che la causa e' la richiesta di **consecutivita'**,
fragile a un avvallamento di quattro centesimi; e che l'isteresi appare la
direzione piu' promettente. Tutto questo e' descrizione di cio' che e' stato
osservato. **Quello che non si puo' dire e' che l'isteresi sia migliore**:
servirebbero cadute registrate in una sessione diversa da quella su cui la
regola e' stata scelta.

**Conseguenza pratica.** Il pacchetto sulla board **non e' stato modificato**
nella regola. La prossima sessione di cadute e' anche il modo per ottenere i
dati indipendenti che mancano.

**Collegamenti:** [EXP-036](EXPERIMENTS.md#exp-036),
[EXP-029](EXPERIMENTS.md#exp-029), [DEC-105](#dec-105)

---

<a id="dec-109"></a>
## DEC-109 — Due configurazioni distinte, e la differenza va narrata

**Scelta.** Il testo distingue esplicitamente:

| | colonne | quando | come e' nata |
|---|---:|---|---|
| **configurazione schierata** | 12 (DTW) | agosto → 8 settembre | scelta a priori dal criterio DTW |
| **configurazione rivista** | 13 (DTWH) | dal 9 settembre | `A3_h_pavimento` **reintrodotta dopo** aver osservato gli errori domestici |

**Perche'.** `A3_h_pavimento` e' fisicamente motivata --- e' la sola grandezza
che distingue il pavimento dal divano --- e il guadagno e' misurato su tutte e
sei le architetture ([EXP-025](EXPERIMENTS.md#exp-025), media +0,056, sei segni
concordi su sei). Ma **non e' stata scelta a priori**: il criterio DTW la
esclude, perche' misura ogni grandezza da sola e questa e' 19esima su 33. E'
rientrata perche' l'analisi degli errori in casa ha mostrato che il sistema
confondeva «sdraiarsi sul divano» con una caduta.

Presentarla come scelta iniziale sarebbe **riscrivere la storia in modo
favorevole**. E' il rilievo del relatore: *«distingui fra configurazione
inizialmente deployata e configurazione rivista a seguito della validazione sul
campo. Non farei apparire come scelta a priori qualcosa che e' nato
dall'analisi degli errori»*.

**Che cosa comporta nel testo.** Il Capitolo 4 confronta DTW e DTWH come due
insiemi; il Capitolo 5 racconta **perche'** il secondo esiste, e in quale
ordine sono avvenute le cose: prima l'errore osservato in casa, poi la
grandezza, poi la misura. Il limite del criterio DTW --- valuta ogni grandezza
isolata, quindi non poteva sceglierla --- va detto dove il criterio viene
presentato, nel Capitolo 3.

**Collegamenti:** [ISS-139](ISSUES.md#iss-139),
[EXP-023](EXPERIMENTS.md#exp-023), [EXP-025](EXPERIMENTS.md#exp-025),
[ISS-156](ISSUES.md#iss-156)
