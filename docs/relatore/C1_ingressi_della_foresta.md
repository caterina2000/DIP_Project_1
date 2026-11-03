# C1 — Punto 1: gli ingressi della foresta e le grandezze integrali

**Che cosa è stato chiesto:** una lettura del meccanismo. La foresta riceve la
finestra riassunta da statistiche, quindi senza alcuna nozione di ordine
temporale; le grandezze integrali le restituirebbero quell'informazione già
calcolata, e sarebbe questo il motivo per cui le aiutano più che alle reti
ricorrenti.

**La risposta in una riga:** **la lettura del meccanismo è corretta; i numeri su
cui poggiava non lo erano.** A dieci soggetti il vantaggio non è distinguibile
dal caso, e con una variante della regola di etichettatura cambia perfino segno.

---

## Come ci siamo arrivati, passo per passo

### Passo 1 — Verificare che il meccanismo sia davvero quello

Sì. La finestra viene riassunta con **sei statistiche per grandezza** — media,
deviazione standard, minimo, massimo, primo e ultimo campione — e la foresta
riceve quel vettore. Non c'è alcuna rappresentazione dell'ordine: scambiando
due campioni interni della finestra, l'ingresso della foresta cambia
pochissimo.

Le grandezze integrali (percorso, discesa, escursione) sono accumuli lungo la
finestra: portano dentro l'ordine temporale in forma già calcolata. **È l'unica
architettura a cui quell'informazione vada consegnata, perché le altre cinque
la ricostruiscono da sole.**

Fin qui la lettura è confermata.

### Passo 2 — Rifare il confronto a dieci soggetti

Il numero che sosteneva la lettura — un guadagno di 0,040 di F2 sulla foresta —
veniva da un impianto a **cinque** soggetti. Rifatto a dieci:

- il guadagno di **0,040 non è distinguibile dal caso**;
- con la regola di etichettatura che include gli estremi il segno **si
  rovescia**, a −0,022;
- per distinguere l'effetto servirebbero fra **34 e 70 soggetti** secondo la
  variante; sulla GRU ne servirebbero **274**.

### Passo 3 — Un secondo effetto, che ribalta una frase del capitolo

A cinque soggetti la foresta era la prima della tabella. A dieci è **l'ultima
delle cinque**: 0,792 contro 0,858 della LSTM. Ma resta **indistinguibile dalla
GRU**: $t = -1{,}74$ contro un valore critico di 2,26.

L'indicazione di non dichiarare un vincitore **vale ancora, nell'altro verso**:
non si può dire che la foresta vinca, e non si può dire che perda.

### Passo 4 — La sesta architettura, aggiunta il 27 agosto

Una rete a grafo, per verificare che il quadro non dipendesse dall'aver provato
solo architetture «a sequenza piatta». Non cambia nulla: nessuna fa meglio della
GRU. Il grafo è il primo confronto che **supera** la soglia critica,
$t = -2{,}37$, e la supera **nel verso sbagliato** — e non sopravvive comunque
alla correzione per molteplicità, che con cinque confronti richiede
$|t| > 3{,}25$.

### Passo 5 — Il 7 settembre: rifatto tutto, e l'affermazione ne esce più forte

Il 6 settembre è emerso che il dataset su cui poggiano quei confronti
**dipendeva dall'ordine in cui i video erano stati elaborati**
([ISS-138](../ISSUES.md), e il perché sta in
[NOVITA](NOVITA_6_7_settembre.md)). Il dataset è stato riestratto e le sei
architetture sono state riaddestrate su di esso: **dodici run**, dalle 09:22
alle 12:44 del 7 settembre ([EXP-025](../EXPERIMENTS.md)).

| architettura | F2 su v2 | **F2 su v3** | scarto |
|---|---:|---:|---:|
| CNN 1D | 0,833 ± 0,118 | **0,828 ± 0,099** | −0,005 |
| GRU | 0,847 ± 0,085 | **0,819 ± 0,096** | −0,028 |
| foresta | 0,792 ± 0,080 | **0,807 ± 0,104** | **+0,015** |
| Transformer | 0,846 ± 0,100 | **0,799 ± 0,099** | −0,047 |
| LSTM | 0,858 ± 0,082 | **0,783 ± 0,103** | −0,075 |
| rete a grafo | 0,779 ± 0,122 | **0,699 ± 0,088** | −0,080 |

**Nessuno scarto arriva alla dispersione fra soggetti (±0,085):** il
rifacimento non ribalta nulla. Ma l'ordine si rimescola — su v2 la LSTM era
prima e la foresta ultima, su v3 la CNN è prima e la LSTM penultima — e
**l'escursione fra le cinque architetture non a grafo si stringe da 0,066 a
0,045**, cioè a metà della dispersione.

È la dimostrazione più forte che il capitolo abbia dell'affermazione che porta:
**le architetture non sono distinguibili fra loro**, e chi ne dichiarasse una
vincitrice starebbe leggendo il rumore. La rete a grafo resta ultima in entrambi
i dataset, ed è l'unica che si distingua — in peggio.

#### E il secondo giro, che risponde a una domanda diversa

Le stesse sei architetture sono state riaddestrate anche con **l'altezza del
bacino dal pavimento** aggiunta alle dodici colonne
([C3](C3_i_due_errori.md), [ISS-139](../ISSUES.md)):

| architettura | 12 colonne | **13 colonne** | guadagno |
|---|---:|---:|---:|
| CNN 1D | 0,828 | **0,885 ± 0,093** | +0,057 |
| foresta | 0,807 | **0,866 ± 0,102** | +0,059 |
| LSTM | 0,783 | **0,864 ± 0,067** | +0,081 |
| Transformer | 0,799 | **0,860 ± 0,089** | +0,061 |
| GRU | 0,819 | **0,842 ± 0,098** | +0,023 |
| rete a grafo | 0,699 | 0,756 ± 0,107 | +0,057 |

**Migliora tutte e sei.** Preso da solo nessun guadagno è distinguibile — il
maggiore, +0,081, sta sotto la dispersione — ma **sei segni concordi su sei**
lo sono: sotto l'ipotesi che la colonna non serva, la probabilità di sei
miglioramenti su sei è $2^{-6} = 0{,}016$. Il guadagno medio è **+0,056**.

Ed è un fatto che riguarda **il compito, non un modello**: la grandezza non
aiuta la foresta perché la foresta è fatta in un certo modo, aiuta chiunque
debba distinguere una caduta da uno sdraiarsi.

---

## Che cosa si propone di scrivere

L'interpretazione meccanicistica resta **come lettura dichiarata del fenomeno**,
accanto alla tabella della numerosità necessaria, e **non come contributo
misurato**. Su questa scelta è chiesto un parere:
[D2](D_domande_al_relatore.md).

---

## Dove guardare

| | |
|---|---|
| run di addestramento | `risultati/addestramento/run_*.json`, con `v2/` per quelle precedenti |
| numerosità necessaria | [EXP-013](../EXPERIMENTS.md) |
| confronto appaiato | `pipeline/confronto_appaiato.py` |
| registro | [EXP-011](../EXPERIMENTS.md), [EXP-018](../EXPERIMENTS.md), [EXP-025](../EXPERIMENTS.md) |
| nella tesi | Capitolo 4, confronto fra architetture e tabella della numerosità |
