# Guida slide per slide — presentazione 13-14 minuti

Written for: la candidata, per costruire le slide e provare il discorso.
Aggiornata il 6 ottobre 2026, dopo il salvataggio del mazzo Canva
([modifica](https://www.canva.com/d/2_rA-ileR6B4PBz)).

Il testo parlato è già nelle **note** delle slide 1-16 del mazzo. Questo file lo
affianca con: cosa sta sulla slide, quale immagine, quanto dura, dove si può
essere attaccati. Le spiegazioni di dettaglio sono in
[SPIEGAZIONE_CODICE.md](SPIEGAZIONE_CODICE.md) e
[DISCORSO_CONTRORELATORE.md](DISCORSO_CONTRORELATORE.md).

Regola per tutte: una idea e al massimo un numero per slide; i dettagli vanno
nelle riserve (17-20) o nelle risposte.

---

## Slide 1 — Titolo · 0:30

**Sulla slide:** titolo in inglese, candidata, relatore, data. Nessuna immagine.

**Cosa dire:** buongiorno, sono Caterina Cerretani, presento la valutazione di
un sistema di rilevamento automatico delle cadute basato sulla stima della posa.
Il percorso va dal confronto fra modelli su un dataset controllato al
funzionamento su un dispositivo edge in ambiente domestico — *from controlled
benchmark to real-world edge deployment*. Il filo conduttore è una domanda sola:
che cosa resta dei risultati di laboratorio quando le condizioni cambiano.

---

## Slide 2 — Perché rilevare le cadute · 0:45

**Sulla slide:** pittogramma «1 su 5» a sinistra; a destra il grafico a barre
«dove avvengono le cadute negli over 65» (casa 54%).

**Cosa dire:** la popolazione invecchia e serve monitorare in modo continuo,
perché la persona mantenga la sua autonomia anche se fragile. Un anziano su
cinque riferisce almeno una caduta nei dodici mesi precedenti (15% fra 65 e 74
anni, 31% oltre gli 85); il luogo più frequente è la casa, 54%. Il problema non è
solo la caduta, ma quanto la persona resta a terra prima di essere soccorsa, e in
casa manca una supervisione continua.

**Attenzione:** la fonte è PASSI d'Argento 2023-2024, Cap. 1. Che il personale
sanitario stia diminuendo **non è nella tesi**: non dirlo come dato.

---

## Slide 3 — Tre famiglie di soluzioni · 0:50

**Sulla slide:** tre cerchi con foto — smartwatch, schema del sensore
ambientale, webcam + board — ciascuno con un «+» e un «−».

**Cosa dire:** gli indossabili rilevano subito ma vanno indossati e caricati; i
sensori ambientali non si indossano ma hanno copertura limitata. Io uso una
telecamera RGB collegata a una Radxa ROCK 4D che elabora tutto in locale: verso
l'esterno esce solo l'allarme, non il video.

**Attenzione:** dire «riduce la circolazione delle immagini», **mai**
«privacy-preserving»: il sistema acquisisce comunque immagini della persona.
Non citare un prezzo preciso: non è verificato nella tesi.

---

## Slide 4 — Obiettivo e tre domande · 0:40

**Sulla slide:** una riga di obiettivo; tre scudi colorati RQ1, RQ2, RQ3.

**Cosa dire:** il sistema deve riconoscere le cadute, contenere i falsi allarmi e
funzionare in continuo con risorse limitate. Tre domande: RQ1 quanto conta
l'architettura a parità di tutto il resto; RQ2, la più importante, che cosa
sopravvive quando cambiano soggetto, vista, dataset e ambiente; RQ3 se la
pipeline gira in locale su un dispositivo a basso costo.

**Da dire:** «queste tre domande torneranno nelle slide dei risultati». Serve a
dare la mappa.

---

## Slide 5 — Dal video all'allarme (pipeline) · 1:40

**Sulla slide:** schema a blocchi: fotogrammi → MediaPipe → landmark → tre
riquadri verdi (preprocessing, feature e finestre, classificatore e allarme); a
destra le tre rappresentazioni in piccolo.

**Cosa dire:** da ogni fotogramma MediaPipe estrae 33 punti anatomici. Da questi
costruisco feature geometriche e temporali: il vantaggio è la riduzione di
dimensionalità, il classificatore riceve una descrizione compatta e
interpretabile invece di centinaia di migliaia di pixel, e da qui in poi non vede
più immagini. Seguono preprocessing, finestre, classificatore, logica d'allarme.

**Attenzione:** la posa è una **stima**, non una misura: può sbagliare quando una
parte del corpo è coperta. Dirlo prima che lo chiedano.

---

## Slide 6 — Tre modi di descrivere la stessa posa · 0:50

**Sulla slide:** tre scheletri affiancati, A1 / A2 / A3, con sotto «Piano
immagine (ellisse)», «Landmark 3D (world)», «Origine al bacino, scala del
tronco».

**Cosa dire:** il confronto non serve a dire quale sia la migliore, perché ognuna
ha un limite. A1 descrive forma e orientamento nel piano immagine (nove
grandezze) ma dipende dalla ripresa. A2 usa i world landmark 3D (cinque
grandezze) e conserva la profondità, che però è anch'essa una stima. A3 usa
coordinate 2D con origine al bacino e scala sul tronco (nove grandezze), dipende
meno da posizione e corporatura ma perde la posizione assoluta nella scena.

**Da verificare prima:** quale configurazione è quella installata sulla scheda.
Le 12 feature finali vengono da tutte e tre; le prove in casa sono su A3.

---

## Slide 7 — Dalle derivate alle grandezze integrali · 1:00

**Sulla slide:** la striscia con i quattro fotogrammi della caduta (a-b-c-d) e
sotto il grafico velocità istantanea (grigio) contro discesa integrata (rosso).

**Cosa dire:** le derivate sono rumorose e tornano piccole appena il corpo si
ferma: nel grafico la velocità del bacino crolla da 3,76 a 0,11, mentre la
discesa accumulata sale a 1,40 e **resta lì**. Per questo aggiungo tre grandezze
integrali — percorso (la strada fatta), escursione (l'ampiezza), discesa (quanto
il bacino è sceso) — su una finestra mobile K = 31, circa 1,7 s. Aggiungo anche
l'altezza del bacino dal pavimento. In tutto 33 candidate; con una selezione
basata su Dynamic Time Warping ne tengo 12, di cui otto integrali.

**Attenzione:** dichiarare che il DTW è calcolato su tutto il dataset prima del
LOSO — è una fuga di informazione. E **non** confondere K = 31 con la finestra
del classificatore da 22.

---

## Slide 8 — Dati e protocollo · 1:10

**Sulla slide:** quattro righe di testo e lo schema del fold: otto caselle blu
(training), una gialla (validazione), una rossa (test).

**Cosa dire:** UP-Fall, dieci soggetti, 220 registrazioni da due telecamere
sincronizzate; il confronto principale usa la laterale. Le etichette sono
annotate a mano in tre fasi: attività normale, transizione di caduta, stato a
terra — le distinguo perché una postura orizzontale compare anche quando una
persona si sdraia di proposito. Valuto con leave-one-subject-out: un soggetto
intero in test, uno in validazione, otto in training, e la normalizzazione è
stimata solo sugli otto. Non divido per video perché lo stesso soggetto finirebbe
in training e test, e il risultato sarebbe gonfiato. Metrica F₂, che pesa di più
le cadute mancate, ma tengo separati falsi positivi e falsi negativi.

---

## Slide 9 — Lunghezza della finestra · 0:50

**Sulla slide:** testo e due barre, 22 campioni F₂ 0,825 e 44 campioni F₂ 0,915.

**Cosa dire:** una caduta è un evento nel tempo, un fotogramma solo non basta.
Con 44 campioni l'F₂ sale da 0,825 a 0,915 (Random Forest), ma ho tenuto 22 come
compromesso con la tempestività: una finestra più lunga impiega più tempo a
riempirsi prima di poter decidere.

**Attenzione:** l'effetto della finestra da 44 sul ritardo **non è stato
misurato**: è un ragionamento, non un risultato. E «2,4 s» vale a 9 fps; sulla
scheda, a 7-8 fps, dura di più.

---

## Slide 10 — RQ1: quanto conta il classificatore · 1:00

**Sulla slide:** il grafico con le sei architetture, F₂ medio e barre di
dispersione; a destra la frase sul confronto statistico.

**Cosa dire:** GRU 0,857, CNN 1D 0,838, Transformer 0,837, LSTM 0,829, Random
Forest 0,825, rete a grafo 0,794. La differenza GRU-Random Forest è 0,032, la
deviazione fra soggetti 0,089: cambiare persona sposta l'F₂ più che cambiare
modello. Confronto fold per fold sugli stessi dieci soggetti; con la correzione
di Bonferroni per cinque confronti nessuna differenza supera la soglia.

**Attenzione:** «non distinguibili» **non** vuol dire «equivalenti». Servirebbero
circa 52 soggetti per distinguere GRU e Random Forest. Dire anche che non c'è
stata ricerca di iperparametri e un solo addestramento per fold.

---

## Slide 11 — RQ2: fuori dalle condizioni di riferimento · 1:10

**Sulla slide:** a sinistra le due viste (laterale e frontale rialzata); a destra
le barre 0,822 / 0,488 / 0,731 / 0,753 e il grafico dei due tipi di errore.

**Cosa dire:** sulla vista laterale F₂ 0,822; lo stesso modello sulla frontale
rialzata scende a 0,488, con i falsi positivi da 722 a 3.252; con entrambe le
viste in training risale a 0,731. La rappresentazione non è invariante al punto
di vista. Poi UR-Fall, dataset esterno: sola telecamera frontale RGB a 30 fps, 67
registrazioni e 11.400 fotogrammi, stesso stimatore e stessa soglia 0,50 — il
sottoinsieme DTW arriva a F₂ 0,630.

**Attenzione:** 0,822 è la prestazione **nella stessa vista**, non trasferita.
Sul perché il trasferimento è incompleto: circa metà della perdita è di taratura
(la soglia non è più adatta), circa metà è potere discriminante perso, che
nessuna soglia recupera.

---

## Slide 12 — Cosa emerge in ambiente domestico · 1:10

**Sulla slide:** la foto «quello che vede la telecamera» con la superficie
rialzata evidenziata, pianta e alzato della stanza; a destra il testo.

**Cosa dire:** in due abitazioni compaiono situazioni assenti dal dataset,
soprattutto persone sdraiate su divano o letto. Ho studiato cinque configurazioni
su A3: base, con altezza dal pavimento, con grandezze integrali, e le due
versioni con controesempi domestici, cioè attività normali registrate in casa e
aggiunte come esempi negativi. Le finestre positive passano da circa 140 a 2,7
per ora — 52 volte meno — mentre sul benchmark l'F₂ guadagna solo 0,055.

**Attenzione (la slide più attaccabile):** una finestra positiva **non** è un
allarme, una caduta ne produce in media 44,8. Le cadute riconosciute **scendono**
da 4/5 a 3/5 con i controesempi: dirlo prima tu. Altezza e controesempi sono
stati scelti guardando quegli stessi errori, nelle stesse due case: percorso di
sviluppo, non verifica indipendente. Cadute: cinque nella prima valutazione,
quattro il 9 settembre — **non** dire «nove».

---

## Slide 13 — RQ3: esecuzione sul dispositivo · 1:15

**Sulla slide:** il grafico della temperatura durante la prova continua; a
sinistra il testo.

**Cosa dire:** Radxa ROCK 4D con MediaPipe e Random Forest, circa 7,3 fotogrammi
al secondo. Il Random Forest l'ho scelto per semplicità di esecuzione,
addestramento rapido e nessuna dipendenza da TensorFlow sul dispositivo. Non è il
più veloce, ma il collo di bottiglia è la posa: 85,2% del tempo contro 14,3% del
classificatore, circa 136 ms a fotogramma. YOLOv8-pose INT8 sulla NPU era più
veloce ma con la persona sdraiata conservava la posa nel 43,6% dei fotogrammi
contro il 79,1% di MediaPipe. Prova continua di riferimento: 4,59 ore senza
sospensioni.

**Attenzione:** 7,3 fps è la capacità della scheda, non i 18 fps del dataset né i
9 di progetto. Il grafico mostra la sessione di **6,11 ore**, con 68 minuti
sospesi, usata solo per la temperatura (79,5 °C): non confonderla con le 4,59.
Il confronto YOLO è su cinque soggetti e non separa modello e quantizzazione.
Consumo elettrico **non misurato**.

---

## Slide 14 — Dalla finestra all'allarme (sessione) · 0:40

**Sulla slide:** l'andamento della sessione di 6,11 ore: punteggio, soglia
tratteggiata, puntini rossi (208 finestre), triangoli blu (14 allarmi).

**Cosa dire:** 208 finestre sopra soglia diventano 14 allarmi, perché la regola
raccoglie le finestre vicine in un solo evento. Per questo uso due misure
diverse: i falsi positivi per finestra descrivono il classificatore, gli allarmi
all'ora descrivono quello che riceve l'utente.

**Da controllare:** nel grafico resta un'etichetta «14,9×» che non è spiegata.

---

## Slide 15 — Dalla classificazione all'allarme (caso) · 1:10

**Sulla slide:** lo scheletro della caduta e sotto l'andamento del punteggio con
il marcatore rosso dell'allarme a 0,64.

**Cosa dire:** per ogni finestra il softmax produce una probabilità, confrontata
con 0,50; l'allarme scatta dopo cinque finestre consecutive sopra soglia, poi 30
secondi di silenzio. Il 9 settembre: quattro cadute simulate, il classificatore
ne riconosce tre, il sistema emette due allarmi — una caduta arriva sei secondi
dopo la precedente, il modello la vede ma la regola la nasconde. Al contrario,
una persona sul divano ha prodotto quattro finestre sopra soglia e nessun
allarme, perché ne servivano cinque. Classificatore e logica d'allarme vanno
quindi valutati separatamente.

**Attenzione:** il ritardo della pipeline è circa 3,9 s, di cui il 71% è il
riempimento della finestra; ma **non** dire «l'allarme arriva in 3,9 secondi»,
perché l'inizio fisico della caduta non è misurabile.

---

## Slide 16 — Conclusioni, limiti e sviluppi · 1:00

**Sulla slide:** tre blocchi di testo, l'ultimo in rosso con il contributo.

**Cosa dire:** il comportamento dipende dall'intera pipeline; le differenze fra
architetture sono contenute rispetto alla variabilità fra soggetti, mentre vista
e condizioni domestiche pesano molto. Limiti: soglia, DTW, K, altezza e
controesempi influenzati dai dati osservati; DTW prima del LOSO; dieci soggetti,
un addestramento per fold; due abitazioni e cadute simulate, nessuna validazione
clinica; carico di allarmi ancora alto; consumo non misurato; prove di ore, non
di giorni. Sviluppi: acquisizioni indipendenti in più ambienti, prove più lunghe,
finestre definite in secondi e non in campioni. Il contributo è aver
caratterizzato che cosa cambia quando un sistema pose-based passa dal benchmark
controllato al funzionamento continuo in casa.

---

## Slide 17-20 — Riserve, non recitate

17 limiti in dettaglio · 18 requisiti e metriche · 19 i tre messaggi · 20 grazie.
Servono per le domande. Alla slide 19 ricordare che 11,1 eventi/ora e 0,049
hanno **basi di conteggio diverse** (nove sessioni con cadute simulate contro uno
studio su 15.500 ore d'uso).

---

## Prima della discussione

1. K: nella tesi è un numero di campioni, nel codice una durata. Da chiarire.
2. Quale classificatore produce la tabella delle configurazioni domestiche
   (F₂ 0,898-0,953): non coincide con lo 0,857 della GRU.
3. Verificare che il confronto 22 → 44 (0,825 → 0,915) sia Random Forest.
4. «Board che non restava attiva» e «cadute non salvate»: non verificato nei log.
5. I fotogrammi delle slide 5, 7 e 11 mostrano persone riconoscibili (soggetti
   UP-Fall): decidere se sostituirli con scheletri.
6. Le note tra parentesi quadre non vanno lette ad alta voce.
