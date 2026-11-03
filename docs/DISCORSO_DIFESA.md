# Discorso di discussione — copione e domande probabili

> **Superato da [DISCORSO_15_SLIDE.md](DISCORSO_15_SLIDE.md) (5 ottobre 2026)** per i numeri.
> Resta utile per l elenco delle domande probabili, qui corrette.

Written for: la candidata, che lo legge ad alta voce o lo usa come scaletta.
Durata: circa 12 minuti. Ogni blocco ha un messaggio solo.

Filo conduttore (dalla lettera del relatore): il contributo non è «il classificatore migliore», ma aver misurato cosa succede a un sistema basato sulla posa quando si passa dal benchmark al soggetto nuovo, alla vista diversa, al dataset diverso, ai vincoli del dispositivo e infine al funzionamento continuo in casa.

---

## 1. Il problema (1 minuto)

«Le cadute sono la prima causa di trauma grave negli anziani. Più della metà avviene in casa, dove nessuno vede la caduta e il soccorso arriva tardi. Il tempo che passa a terra incide sull'esito quanto la caduta stessa.»

Dato: 54% delle cadute negli over 65 avviene in casa (Cap. 1).

## 2. Le soluzioni e la scelta (1 minuto)

«Ci sono tre famiglie. I dispositivi indossabili funzionano, ma richiedono che la persona li indossi sempre. I sistemi ambientali non distinguono una caduta da una persona che si sdraia volontariamente. La visione con elaborazione locale: una telecamera, ma nessuna immagine esce dalla casa. Questa è la scelta di questo lavoro.»

## 3. Obiettivo e tre domande (1 minuto)

«L'obiettivo è verificare se un rilevatore di cadute basato sulla posa, su un dispositivo a basso costo, mantiene le prestazioni di laboratorio quando cambiano soggetto, vista, dataset e ambiente.»

- RQ1: quanto conta l'architettura del classificatore?
- RQ2: che cosa sopravvive quando cambiano soggetto, vista, dataset e ambiente?
- RQ3: il sistema gira in locale, e con quali costi?

Le tre domande tornano in ogni sezione dei risultati.

## 4. Requisiti e metriche (1 minuto)

«Ogni requisito ha una metrica. Due misure vanno tenute distinte: i falsi positivi per finestra, che misurano il classificatore, e gli allarmi all'ora, che misurano ciò che l'utente riceve. Una caduta reale produce in media 44,8 finestre positive: contare le finestre non equivale a contare gli allarmi.»

## 5. La pipeline (2 minuti)

Una sequenza, da sinistra a destra:
1. Video: telecamera RGB.
2. Stima della posa con MediaPipe: 33 punti per fotogramma. Da qui in poi il classificatore non vede più immagini.
3. Preprocessing:
   - le pose mancanti vengono segnalate, mai interpolate;
   - la normalizzazione è stimata solo sul training, così il soggetto di test non entra nel calcolo;
   - finestre di 22 fotogrammi, con passo 2.
4. Classificatore: sei architetture a confronto.
5. Logica di allarme: soglia 0,50, cinque finestre consecutive sopra soglia, 30 secondi di sospensione dopo l'allarme.

Frase chiave: «Il classificatore riceve coordinate, non pixel.»

## 6. RQ1 — quanto conta l'architettura (1,5 minuti)

«Ho confrontato sei architetture: GRU, LSTM, rete convoluzionale 1D, Transformer, grafo e foresta casuale. Con la stessa rappresentazione e lo stesso protocollo, la variabilità tra architetture è di 0,032 in F2. La variabilità tra soggetti è di 0,089. Il collo di bottiglia è la generalizzazione tra persone, non il modello.»

Valori F2 in LOSO su dieci soggetti (Cap. 4): GRU 0,857 · CNN 1D 0,838 · Transformer 0,837 · Random Forest 0,825.

Perché la finestra di 22 e non 44: «Con 44 fotogrammi il benchmark dà risultati un po' migliori. Ma in un sistema di allarme conta anche il tempo necessario a produrlo: una finestra più lunga significa un allarme più tardivo. Ho scelto 22 come compromesso tra riconoscimento e latenza.»

## 7. RQ2 — dal laboratorio alla casa (2 minuti)

«Il benchmark non basta. Passando alle feature integrali con i controesempi domestici, le finestre positive in casa scendono da circa 140 a 2,7 per ora, cioè circa 52 volte meno, mentre sul benchmark il guadagno di F2 è solo 0,055. Cambiare la vista, aggiungere l'altezza dal pavimento, cambiare l'ambiente: ciascuna configurazione sposta il compromesso fra falsi allarmi e cadute mancate. Il risultato non è un sistema pronto, ma una mappa di ciò che si rompe.»

Dati: ΔF2 0,055 sul benchmark; 139,9 → 2,7 finestre positive all ora in casa (Cap5.tex:510-515). Il compromesso: le cadute riconosciute scendono da 4/5 a 3/5.

## 8. RQ3 — dispositivo e casa (2 minuti)

«Il sistema gira su una scheda Radxa ROCK 4D, con una webcam, per circa cento euro. Sono 7,3 frame al secondo in inferenza continua, con una temperatura massima di 79,5 °C. Ho scartato la NPU di proposito: il guadagno di velocità non compensa la perdita di flessibilità della pipeline.»

Sessioni domestiche: nove sessioni, 14,98 ore di tempo di parete. Il sistema produce 11,1 eventi all'ora, contro 0,049 riportati in letteratura. È il dato più difficile da difendere, e lo dico così.

Prova continua di riferimento: 4,59 ore senza sospensioni. La sessione di 6,11 ore è usata solo per la temperatura, perché il sistema operativo l'ha sospesa per 68 minuti.

## 9. Limiti (1 minuto)

«Dichiaro cinque limiti. Il carico di allarmi resta due-tre ordini di grandezza sopra il criterio clinico. Cinque cadute simulate non bastano per un richiamo statisticamente solido. Il consumo elettrico non è misurato. La stima del pavimento non converge su sequenze brevi, sotto i quindici secondi. La sospensione di 30 secondi può nascondere una seconda caduta ravvicinata.»

Due punti metodologici da dichiarare:
- la selezione delle feature con DTW è stata fatta su tutto il dataset prima della validazione LOSO: c'è una fuga di informazione, misurata nel Cap. 5;
- la soglia 0,50, il parametro K e l'introduzione dell'altezza dal pavimento e dei controesempi domestici sono state influenzate dai dati osservati durante lo sviluppo. Non sono una validazione completamente indipendente.

Le prove domestiche mostrano problemi che il benchmark non mostra. Non sono una validazione clinica.

## 10. Chiusura (30 secondi)

«Il contributo non è il classificatore migliore. È aver seguito cosa succede a un sistema basato sulla posa quando si esce dal laboratorio: dal soggetto nuovo, alla vista, al dataset, al dispositivo, fino al funzionamento continuo in casa. Il margine di miglioramento sta soprattutto fuori dal classificatore.»

---

## Domande probabili, con risposta breve

**Perché 22 e non 44, se 44 fa meglio sul benchmark?**
Perché in un sistema di allarme conta anche la latenza. Una finestra più lunga ritarda l'allarme. È un compromesso, e lo dichiaro come tale.

**La soglia 0,50 non è stata scelta sui dati?**
Sì, in parte. Lo dichiaro come limite: la soglia è influenzata dai dati osservati e non è una validazione indipendente.

**C'è una fuga di informazione con la DTW?**
Sì. La selezione delle feature con DTW è stata fatta su tutto il dataset prima del LOSO. È dichiarata nel Cap. 3 e misurata nel Cap. 5.

**Cinque cadute bastano?**
No, e non lo sostengo. Con cinque cadute l'intervallo di confidenza sul recall è molto largo. È il limite più serio del lavoro.

**Perché 11,1 eventi all'ora, se la letteratura dice 0,049?**
Il dato è reale ma non va confrontato direttamente: le sessioni domestiche includono attività quotidiane molto diverse, e il sistema non è ottimizzato per quel carico. Resta un limite dichiarato.

**Perché 9,6 ore nel Cap. 5 e 14,98 nelle sessioni?**
Sono due basi di conto diverse. 9,6 ore è il tempo effettivo di funzionamento delle dodici registrazioni di agosto, al netto delle sospensioni. 14,98 ore è il tempo di parete delle nove sessioni, con la sessione del 6 settembre. Le due cifre non si sommano.

**Perché 4,59 ore e non 6,11 come prova più lunga?**
La sessione di 6,11 ore è stata interrotta dal sistema operativo per 68 minuti. La prova di 4,59 ore è l'unica continua e strumentata. La sessione di 6,11 ore serve solo per la temperatura.

**Perché non la NPU?**
Il guadagno di velocità non compensava la perdita di flessibilità della pipeline, e la CPU bastava per il tempo reale.

**Il sistema è clinicamente valido?**
No. Le prove domestiche sono utili perché fanno emergere problemi che il benchmark non mostra. Non sono una validazione clinica.

**Perché GRU e non LSTM, se LSTM fa meglio?**
La GRU ha il valore medio più alto, 0,857; il divario con la Random Forest è 0,032, contro una deviazione fra soggetti di 0,089. Sul dispositivo ho installato la Random Forest, per semplicità di esecuzione e minori dipendenze.

**Perché la rete a grafo non è migliore?**
La rete a grafo è la meno performante del confronto. Dopo la correzione per confronti multipli nessuna differenza fra architetture risulta statisticamente chiara: le differenze sono contenute rispetto alla variabilità fra soggetti.

**La telecamera non viola la privacy?**
Nessuna immagine esce dalla casa: il classificatore riceve solo coordinate. Ma le coordinate possono conservare caratteristiche individuali; lo riconosco nel Cap. 1.

**Cosa succede con soggetti diversi o anziani?**
Il protocollo LOSO testa soggetti non visti in addestramento, ma i soggetti sono cinque in parte degli esperimenti e dieci in quelli principali. Con soggetti anziani reali i risultati non sono ancora verificati.

**Cosa cambierebbe con più dati?**
Più soggetti, più cadute reali, sessioni più lunghe in più abitazioni, e la misura del consumo. Sono le proposte dichiarate nel Cap. 6, non lavoro svolto.

---

## Controlli prima di presentare

- Ripetere ad alta voce ogni numero e verificarlo con la fonte indicata (Cap. 1, 3, 5, 6).
- Decidere la lingua: la tesi nei capitoli 1–3 è in inglese, la presentazione è in italiano.
- Non dire «validazione» per le prove domestiche: dire «prove di funzionamento» o «misura in casa».
