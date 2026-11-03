# La corrispondenza con il relatore — punto di riferimento

**Questo file esiste per una ragione sola:** dire con esattezza **che cosa il
relatore ha letto**, perche' da allora dei numeri sono cambiati. Senza questo
riferimento e' impossibile distinguere «cio' che il relatore sa» da «cio' che
sappiamo adesso», ed e' il modo in cui un fatto corretto torna indietro
([ISS-110](../ISSUES.md#iss-110)).

**Non aggiornare i numeri qui dentro.** Qui sta cio' che e' stato mandato, non
cio' che e' vero oggi. Le divergenze si annotano nella tabella in fondo.

---

## 1. Che cosa e' stato mandato

Una mail con tre parti: il **modulo di registrazione dello stage** da firmare,
il **nuovo indice della tesi** a cinque capitoli con la funzione di ciascuno, e
la **risposta punto per punto** alle dieci osservazioni della mail precedente
del relatore, con le figure allegate.

I numeri dichiarati nella mail, quelli che il relatore ha sotto gli occhi:

| | valore comunicato |
|---|---|
| confronto architetture | LSTM **0,858** · GRU 0,847 · Transformer 0,846 · CNN 1D 0,833 · foresta 0,792 · grafo 0,779 |
| dispersione fra soggetti | 0,08 – 0,10 |
| viste | cam1->cam1 0,822 · cam1->cam2 **0,488** · cam1+2->cam2 0,731 · cam2->cam2 0,753 |
| escursione dell'angolo del tronco | 74,0° -> 33,2°, fattore **2,23** |
| tracking perso su cam2 | 11 riprese su 50 |
| UR-Fall | rapporto 18,7x -> **1,79x**; F2 0,034 con soglia di deployment, **0,492** con soglia oracolo, 0,971 in dominio; **49%** recuperabile ricalibrando |
| occlusioni | riferimento 0,853; peggioramento massimo **0,037** (spalle); dispersione 0,071 |
| costo per fotogramma | percezione **116,38 ms** (85%) + classificazione ammortizzata 19,51 ms = **136,65 ms**, circa **7,3 fps** |
| costo per finestra | board **39,04 ms**, PC 4,85 ms (il vecchio 4,47 ms era il PC attribuito alla board) |
| NPU | YOLOv8-pose costa **0,216** di F2; ridurre il frame rate di MediaPipe costa **0,041** |
| errori benchmark | A3 -> configurazione finale: FN **45 -> 14**, FP **172 -> 124** |
| benchmark vs casa | F2 da 0,898 a 0,953 (+0,055) in benchmark; in casa da ~140 a **<3** finestre positive/ora |
| controesempi incrociati | nonni->studente **0,342 -> 0,171** ev/h; studente->nonni **1,781 -> 0,890** ev/h |
| finestre contro eventi | 496 finestre/ora -> **11,1 eventi/ora**, rapporto **44,8** |
| latenza mediana in laboratorio | **2,44 s** |
| prova lunga | **4,59 ore**, nessuna sospensione, due interruzioni USB da ~5 s complessivi, **14 eventi non verificabili** perche' le clip non venivano salvate |

Tre domande poste in chiusura: se mantenere l'interpretazione sugli integrali,
se aggiornare la configurazione con l'altezza dal pavimento, se sostituire la
regola delle cinque finestre.

---

## 2. Che cosa ha risposto il relatore

Giudizio complessivo: l'impostazione e' **molto piu' chiara**, il lavoro non
sembra piu' una successione di esperimenti. **Indice approvato**, con la
separazione fra Capitolo 4 (valutazione controllata) e Capitolo 5 (dispositivo
e comportamento operativo) da mantenere **anche nella scrittura**.

### Le prescrizioni, una per una

| # | che cosa ha chiesto |
|---|---|
| 1 | **Non** «architetture equivalenti», ma «con questo protocollo e dieci soggetti **non emerge evidenza sufficiente** per attribuire un ruolo dominante all'architettura». Nelle figure dire **che cosa sono le barre d'errore**. La colonna «parametri» -> «**numero di parametri addestrabili**». La foresta e' giustificata come **scelta ingegneristica**, non come modello migliore |
| 2 | Integrali: interpretazione **da mantenere**. Ma **non** dire che LSTM e GRU «ricostruiscono autonomamente» l'integrale: dire che i modelli sequenziali **possono apprendere** dipendenze temporali dalla sequenza, mentre un modello non sequenziale **beneficia** di informazione temporale gia' esplicita. La figura e' **esplicativa del meccanismo**, non prova di superiorita' |
| 3 | Il messaggio solido non e' il rovesciamento dell'ordine, ma che **il benchmark comprime in pochi centesimi differenze che in esercizio sono enormi**. Confrontare sempre configurazioni **con la stessa soglia e la stessa regola**. Nel Cap. 5: **eventi/ora primaria**, finestre/ora diagnostica |
| 4 | Non «generalizzazione» ma «**adattamento al dominio mediante hard negatives con evidenza di trasferimento cross-home**». Riportare i **numeri assoluti** (4 cadute su 5), non la percentuale |
| 5 | Non generalizzare il «nessuno scambio fra i due errori»: riferirlo **a quel confronto e a quella soglia**. Aggiungere recall/precision o tassi normalizzati. **Distinguere la configurazione portata in casa da quella rivista dopo aver osservato gli errori domestici** |
| 6 | Non «ho dimostrato che la geometria e' la causa», ma «i risultati sono **coerenti con** la geometria della vista come principale spiegazione». **Refuso da correggere:** «recuperabile ritirando la soglia» -> «**mediante ricalibrazione della soglia**» |
| 7 | Non «robustezza alle occlusioni»: «nella simulazione controllata **non emerge un singolo gruppo di landmark la cui perdita determini da sola il collasso**». I +0,001/+0,003 sono **fluttuazioni**, non miglioramenti. Controllare l'etichetta dell'ultima barra della figura |
| 8 | Usare **solo** le nuove misure, togliere dal testo i vecchi valori non riproducibili. Descrivere **come** e' stata fatta la misura: durata, numero di fotogrammi, warm-up, I/O. **Spiegare** la differenza fra 116,38 + 19,51 e 136,65 |
| 9 | Tenere **entrambe** le misure. **Attenzione all'apparente incoerenza**: 208 finestre / 14 allarmi = 14,9x nella figura, contro 44,8x nella mail — va scritto nella didascalia a che cosa si riferisce ciascuno. **NON cambiare** la regola delle cinque finestre nel deployment: cumulativa e isteresi restano **analisi offline**, altrimenti si sceglie la regola sugli stessi dati con cui la si dimostra |
| 10 | I 14 eventi si chiamano «**eventi generati dal sistema**», non falsi positivi, finche' non c'e' verifica visiva |

### Le tre decisioni

1. **Integrali:** mantenere l'interpretazione, con la cautela del punto 2.
2. **Altezza del bacino:** mantenerla, ma **dichiarare che e' stata reintrodotta
   dopo aver osservato gli errori domestici**. Non farla apparire come scelta a priori.
3. **Cinque finestre consecutive:** **non sostituirla** nella configurazione dichiarata.

### E infine

> «Il lavoro va soprattutto **consolidato e scritto, non allargato**.» Niente
> nuove architetture, nuovi dataset, nuove analisi. Le tre figure da tenere in
> evidenza sono **le due telecamere**, **la scomposizione del domain shift** e
> **il confronto finestre/eventi**.

---

## 3. Che cosa e' cambiato DOPO l'invio

Da aggiornare ogni volta che un numero comunicato al relatore si muove.

| cosa | comunicato | oggi | dove |
|---|---|---|---|
| **confronto architetture** | LSTM 0,858 in testa | su `feature_v5` la **GRU** e' in testa con 0,857 e la LSTM scende a 0,829 su DTW; l'ordine cambia | [EXP-038](../EXPERIMENTS.md#exp-038) |
| **e le stesse su v3, che esisteva gia'** | --- | il riaddestramento su `feature_v3.csv` era **concluso il 7 settembre alle 12:44**, il giorno prima dell'invio, e dava LSTM **0,783** e grafo **0,699**. La mail riporta i valori del **20 agosto** | [EXP-025](../EXPERIMENTS.md#exp-025) |
| **rete a grafo** | 0,779, la piu' bassa | **0,794** su v5: recupera, e l'affermazione di EXP-018 va rivista | [EXP-038](../EXPERIMENTS.md#exp-038) |
| **altezza dal pavimento** | «migliora **tutte** le architetture provate» | **falso su v5**: tre segni positivi e tre negativi, guadagno medio +0,003. L'argomento della concordanza dei segni **cade** | [EXP-038](../EXPERIMENTS.md#exp-038) |
| **clip attorno agli allarmi** | «non vengono salvate», 14 eventi non verificabili | **risolto**: le sessioni del 9 settembre salvano i fotogrammi annotati | [ISS-142](../ISSUES.md#iss-142) |
| **cadenza della board** | 7,3 fps | 7,26 fps il 6 settembre, **6,47** il 9: varia fra sessioni | [EXP-035](../EXPERIMENTS.md#exp-035) |

### Le tre generazioni dello stesso confronto

I numeri della mail **esistono ancora** e stanno in
`risultati/addestramento/v2/`, messi da parte il 7 settembre proprio perche'
i nomi dei file non contengono la versione del dataset e sarebbero stati
sovrascritti. Verificati uno per uno: coincidono con la mail alla terza cifra.

| modello | **MAIL** (v2, run del 20 ago) | v3 (7 set, *prima* dell'invio) | v5 (9 set, oggi in `risultati/`) |
|---|---:|---:|---:|
| LSTM | **0,858** | 0,783 | 0,829 |
| GRU | **0,847** | 0,819 | **0,857** |
| Transformer | **0,846** | 0,799 | 0,837 |
| CNN 1D | **0,833** | 0,828 | 0,838 |
| foresta | **0,792** | 0,807 | 0,825 |
| rete a grafo | **0,779** | 0,699 | 0,794 |

**Due cose da tenere presenti.**

1. **Rigenerando `fig_architetture.png` oggi non escono i numeri della mail.**
   `figure_tesi.py` legge `risultati/addestramento/`, dove stanno le run su v5:
   la GRU passa in testa e la LSTM scende al quarto posto. La sottocartella
   `v2/` non viene letta --- e' esattamente cio' che il suo LEGGIMI dichiara.
2. **v3 non e' un passaggio intermedio fra v2 e v5**: su DTW e' piu' basso di
   entrambi per quattro architetture su sei. Le tre generazioni non stanno su
   una retta, quindi «il numero e' migliorato» non descrive cio' che e'
   successo.

**Il punto 5 della risposta del relatore diventa piu' delicato di quanto lui
sapesse.** Lui ha chiesto di dichiarare che l'altezza dal pavimento e' stata
reintrodotta *dopo* aver osservato gli errori domestici. Adesso sappiamo anche
che il suo beneficio **non e' generale**: dipende da quali altre grandezze sono
nella selezione. Va scritto cosi', ed e' un'informazione che il relatore non ha.
