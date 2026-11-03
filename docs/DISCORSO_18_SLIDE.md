# Discorso in 18 slide — copione parlato

> **Superato da [DISCORSO_15_SLIDE.md](DISCORSO_15_SLIDE.md) (5 ottobre 2026).**
> Questo file riportava i valori di $F_2$ della mail di agosto. I valori corretti
> del Cap. 4 sono: GRU 0,857, CNN 1D 0,838, Transformer 0,837, Random Forest 0,825.
> Resta utile solo per il tono e per la corrispondenza con le slide.

Written for: la candidata, che lo pronuncia davanti alla commissione.
Modello di struttura: il discorso di Petrilli (18 slide, un paragrafo per slide, una frase chiave).
Durata: circa 12 minuti. Ogni slide: un'idea, un numero al massimo.

Filo conduttore (lettera del relatore): quanto delle prestazioni da benchmark sopravvive quando si tolgono, una alla volta, le semplificazioni del laboratorio.

---

## Slide 1 — Titolo

Buongiorno a tutti. Sono Caterina Cerretani e oggi vi presento il mio lavoro di tesi: la valutazione di un sistema di rilevamento cadute basato sulla posa, dai laboratori fino a un dispositivo edge e a una casa reale. Il lavoro non cerca il classificatore migliore: cerca di capire cosa resta di un risultato quando si cambiano le condizioni.

*Frase chiave: non il classificatore migliore, ma cosa sopravvive.*

## Slide 2 — Il problema

Le cadute sono la prima causa di trauma grave negli anziani. Più della metà avviene in casa, il 54 per cento delle cadute negli over 65, e spesso nessuno le vede. Il tempo che la persona passa a terra incide sull'esito quanto la caduta stessa. Serve quindi un sistema che rilevi la caduta da solo, e che avvisi in fretta.

*Frase chiave: la caduta che nessuno vede è quella che conta.*

## Slide 3 — Le soluzioni esistenti

Ci sono tre famiglie di soluzioni. I dispositivi indossabili funzionano, ma la persona deve ricordarsi di portarli sempre. I sistemi ambientali, come i sensori a soffitto o di pressione, non distinguono una caduta da una persona che si sdraia di proposito. La visione con elaborazione locale è la via che ho scelto: una telecamera, ma nessuna immagine esce dalla casa. Il classificatore riceve solo coordinate.

*Frase chiave: la telecamera resta in casa, e il sistema lavora sulla posa, non sul video.*

## Slide 4 — Obiettivo e domande di ricerca

L'obiettivo è verificare se un rilevatore di cadute basato sulla posa, su un dispositivo a basso costo, mantiene le prestazioni di laboratorio quando cambiano il soggetto, la vista, il dataset e l'ambiente. Le domande sono tre. RQ1: quanto conta l'architettura del classificatore? RQ2: cosa sopravvive quando cambiano soggetto, vista, dataset e ambiente? RQ3: il sistema gira in locale, e con quali costi? Le tre domande tornano in ogni sezione dei risultati.

*Frase chiave: tre domande, una mappa.*

## Slide 5 — Requisiti e metriche

Ogni requisito è legato a una metrica misurabile. Il primo: i falsi allarmi, misurati in due modi diversi. I falsi positivi per finestra dicono come si comporta il classificatore. Gli allarmi all'ora dicono cosa riceve l'utente. Una caduta reale produce in media 44,8 finestre positive: contare le finestre non equivale a contare gli allarmi. Il secondo: le cadute rilevate, con la sensibilità. Il terzo: la latenza, cioè il tempo tra l'inizio della caduta e l'allarme.

*Frase chiave: due misure diverse, che non vanno confuse.*

## Slide 6 — La pipeline

Il video entra nel sistema e da ogni fotogramma si stimano 33 punti del corpo con MediaPipe. Da qui in poi il classificatore non vede più immagini. Prima del classificatore c'è il preprocessing: le pose mancanti vengono segnalate e mai interpolate; la normalizzazione è stimata solo sul training; le finestre sono di 22 fotogrammi, con passo 2. Infine la logica di allarme: soglia 0,50, cinque finestre consecutive, trenta secondi di sospensione.

*Frase chiave: il classificatore riceve coordinate, non pixel.*

## Slide 7 — Dal video alla posa

Lo stimatore di posa restituisce, per ogni fotogramma, 33 landmark con una stima di visibilità. È una stima, non una misura: può sbagliare quando una parte del corpo è coperta o quando la telecamera cambia angolo. Per questo le pose mancanti vengono segnalate, e la finestra non attraversa mai una perdita di posa.

*Frase chiave: la posa è una stima, e il sistema lo tiene in conto.*

## Slide 8 — Tre modi di descrivere la stessa posa

La stessa posa si può descrivere in tre modi. A1: coordinate assolute, che conservano la posizione nella scena. A2: coordinate relative al baricentro. A3: normalizzazione sulla lunghezza del tronco, che rende la descrizione meno dipendente dalla corporatura. Le tre rappresentazioni vengono confrontate con lo stesso protocollo.

*Frase chiave: cambia la rappresentazione, non il problema.*

## Slide 9 — Dalle derivate alle grandezze integrali

Le derivate temporali delle coordinate sono rumorose, e il rumore cresce con la derivata. Integrando le derivate su una finestra si ottengono grandezze cumulative, più stabili. Il coefficiente ρ₁ passa da 0,22–0,54 a 0,82–0,99. È l'intervento che migliora ovunque: è il passo che rende utilizzabili le feature di movimento.

*Frase chiave: integrare il movimento lo rende leggibile.*

## Slide 10 — Dalla finestra all'allarme

Il sistema non allarma su una singola finestra. Servono cinque finestre consecutive sopra soglia 0,50, e una conferma di trenta secondi. Questo riduce i falsi allarmi, ma ha un costo: l'allarme arriva dopo. Nelle sessioni domestiche una caduta reale produce in media 44,8 finestre positive, e la regola le trasforma in pochi allarmi.

*Frase chiave: la regola separa il rumore dall'emergenza.*

## Slide 11 — Il dispositivo

Il sistema gira su una scheda Radxa ROCK 4D, con una webcam USB, per un costo inferiore ai cento euro. In inferenza continua raggiunge 7,3 fotogrammi al secondo, con una temperatura massima di 79,5 °C. Ho scartato la NPU di proposito: il guadagno di velocità non compensava la perdita di flessibilità della pipeline. La CPU basta per il tempo reale.

*Frase chiave: un sistema semplice, che costa poco e gira davvero.*

## Slide 12 — Un soggetto fuori alla volta

La valutazione è fatta con leave-one-subject-out. Ogni soggetto, a turno, resta fuori dall'addestramento e diventa il test. Il modello non vede mai i dati del soggetto di test mentre impara. Così il risultato misura la capacità di generalizzare a una persona nuova, non la capacità di ricordare le persone già viste.

*Frase chiave: il test non vede mai la persona su cui viene valutato.*

## Slide 13 — RQ1: sei architetture

Ho confrontato sei architetture: GRU, LSTM, una rete convoluzionale 1D, un Transformer, una rete a grafo e una foresta casuale. Con la stessa rappresentazione e lo stesso protocollo, la variabilità tra architetture è di 0,032 in F2. La variabilità tra soggetti è di 0,089. Il collo di bottiglia è la generalizzazione tra persone, non il modello. La finestra di 22 fotogrammi è un compromesso: con 44 il benchmark migliora di poco, ma l'allarme arriva più tardi.

*Frase chiave: il modello conta meno della persona.*

## Slide 14 — RQ2: dal laboratorio alla casa

Il benchmark non basta. Aggiungendo le grandezze integrali e i controesempi domestici, sul benchmark F2 guadagna solo 0,055, mentre in casa le finestre positive scendono da circa 140 a 2,7 per ora, cioè circa 52 volte meno. Cambiano la vista, l'altezza dal pavimento, l'ambiente, e ciascuna configurazione sposta il compromesso fra falsi allarmi e cadute mancate. Il risultato non è un sistema pronto: è la mappa di ciò che si rompe.

*Frase chiave: il benchmark sopravvive solo in parte.*

## Slide 15 — RQ3: in casa, per quindici ore

Il sistema è stato provato in due abitazioni, per nove sessioni e 14,98 ore di tempo di parete. Produce 11,1 eventi all'ora, contro 0,049 riportati in letteratura. È il dato più difficile da difendere, e lo dico così. La prova continua di riferimento dura 4,59 ore, senza sospensioni: è l'unica completa e strumentata. Nella quarta caduta la raffica raggiunge le cinque finestre e l'allarme scatta con punteggio 0,64.

*Frase chiave: funziona, ma il carico di allarmi è ancora alto.*

## Slide 16 — Che cosa questo lavoro non dimostra

Dichiaro cinque limiti. Il carico di allarmi resta due-tre ordini di grandezza sopra il criterio clinico. Cinque cadute simulate non bastano per un richiamo statisticamente solido. Il consumo elettrico non è misurato. La stima del pavimento non converge su sequenze brevi, sotto i quindici secondi. La sospensione di trenta secondi può nascondere una seconda caduta ravvicinata. Inoltre, la selezione delle feature con DTW è stata fatta su tutto il dataset prima del LOSO: c'è una fuga di informazione, misurata nel Cap. 5.

*Frase chiave: dico cosa non dimostro, senza scuse.*

## Slide 17 — Conclusioni e sviluppi

Il contributo non è il classificatore migliore. È aver seguito cosa succede a un sistema basato sulla posa quando si esce dal laboratorio: dal soggetto nuovo, alla vista, al dataset, al dispositivo, fino al funzionamento continuo in casa. Il margine di miglioramento sta soprattutto fuori dal classificatore. Gli sviluppi indicati sono proposte: più soggetti, più cadute reali, sessioni più lunghe in più abitazioni, la misura del consumo.

*Frase chiave: il lavoro misura, e indica dove migliorare.*

## Slide 18 — Grazie

Grazie per l'attenzione. Sono pronta a rispondere alle domande, partendo dai limiti dichiarati.

---

## Corrispondenza con le slide del mazzo Canva

| Slide del discorso | Slide del mazzo |
|---|---|
| 1 Titolo | 1 |
| 2 Problema | 2 |
| 3 Soluzioni | 3 |
| 4 Obiettivo | 4 |
| 5 Requisiti | 17 (da spostare qui) |
| 6 Pipeline | 6 |
| 7 Posa | 7 |
| 8 Rappresentazioni | 8 |
| 9 Integrali | 9 |
| 10 Finestra e allarme | 10 (da spostare) |
| 11 Dispositivo | 14 |
| 12 LOSO | 11 (da spostare) |
| 13 RQ1 | 13 |
| 14 RQ2 | 13, 12 |
| 15 RQ3 | 15 |
| 16 Limiti | 16 |
| 17 Conclusioni | 19 |
| 18 Grazie | 20 |

Riserve: 21, 22, 23 (non recitate: servono per le domande).

## Controlli prima di presentare

- Ogni numero deve essere verificato con la fonte: Cap. 1 (54%, 0,049), Cap. 3 (DTW, normalizzazione), Cap. 5 (14,98 ore, 4,59 ore, 6,11 ore), Cap. 6 (contributi, limiti).
- Non dire «validazione» per le prove domestiche: «prove di funzionamento» o «misura in casa».
- Lingua: la presentazione è in italiano, la tesi nei capitoli 1–3 è in inglese. Decidere prima.
