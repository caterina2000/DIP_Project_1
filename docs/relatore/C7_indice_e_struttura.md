# C7 — L'indice aggiornato e la struttura del capitolo sperimentale

**Che cosa è stato chiesto:** un indice aggiornato, e una struttura del capitolo
sperimentale che si capisca — con l'indicazione, per ogni sezione, di che cosa
serve a dimostrare.

**La risposta in una riga:** **fatto**, dopo un primo tentativo che descriveva
una struttura mai applicata.

---

## Passo 1 — Il primo tentativo, e perché non andava bene

Il documento `docs/INDICE_E_STRUTTURA.txt` del 26 agosto riportava, per ogni
sezione dei capitoli sperimentali, **la tesi che sostiene e non il suo
contenuto**. Quella è la forma giusta: un indice che elenca titoli non dice se
l'argomentazione tiene.

Ma proponeva una struttura che poi **non è stata applicata** — in particolare la
fusione fra il capitolo di contesto e quello sullo stato dell'arte — e sotto una
toppa di avvertenza conservava l'indice a **otto** capitoli, che nel frattempo
erano diventati cinque.

Un indice che descrive un documento diverso da quello che esiste è peggio di
nessun indice.

## Passo 2 — La riscrittura del 31 agosto

Riscritto sulla struttura effettiva a **cinque capitoli**:

| | capitolo | che cosa sostiene |
|---|---|---|
| 1 | Contesto applicativo e formulazione del problema | perché il problema è quello, e perché la visione |
| 2 | Stato dell'arte | che cosa esiste, e che cosa il lavoro non ripete |
| 3 | Metodologia: dalla stima di posa alla decisione | come si passa dalle immagini a una decisione |
| 4 | Protocollo di valutazione e risultati sperimentali | che cosa il sistema fa in laboratorio, e quanto ci si può credere |
| 5 | Implementazione su dispositivo edge e validazione in ambiente reale | che cosa succede quando esce dal laboratorio |

Più introduzione e conclusioni, che hanno file propri.

## Passo 3 — Il costo nascosto della fusione dei capitoli

Passando da otto capitoli a cinque, i riferimenti incrociati sono stati tenuti
grazie alle **etichette simboliche**: la numerazione è cambiata e i rimandi
hanno retto perché sono nomi e non numeri. Le etichette dei capitoli fusi sono
conservate come alias, perché una ventina di rimandi le usa.

Ma la fusione ha creato un difetto specifico: **un rimando dentro il capitolo in
cui si sta scrivendo**. Un «si veda il Capitolo 4» scritto quando era un
capitolo diverso, dopo la fusione dice «nel Capitolo 4» a chi sta leggendo il
Capitolo 4. Ne sono stati corretti cinque il 26 agosto.

## Passo 4 — Il controllo automatico, perché la struttura non si sfaldi da sola

`tesi/controlla.py` verifica a ogni giro: ambienti non chiusi, etichette
duplicate, riferimenti orfani, figure mancanti, **figure senza immagine** e
citazioni non definite.

L'ultimo controllo esiste per una ragione precisa: un ambiente `figure` senza
`\includegraphics` **compila**, e lascia uno spazio bianco con la didascalia
sotto. È così che quattro figure mancanti erano rimaste inosservate per
settimane.

Stato attuale: *«Nessun problema. Restano 0 figure da produrre.»*

---

## Che cosa resta

- **`tesi/Cap1_riordinato.tex`**, una proposta di riordino del Capitolo 1 che
  non è inclusa in `tesi.tex` e quindi non finisce nel PDF. Va adottata o
  archiviata; `controlla.py` la segnala a ogni esecuzione.
- **Cinque figure generate e mai inserite** nel testo, con la scheda accanto che
  contiene già il blocco LaTeX pronto.

---

## Dove guardare

| | |
|---|---|
| indice | `docs/INDICE_E_STRUTTURA.txt` |
| controllo | `python tesi/controlla.py` |
| registro | [ISS-107](../ISSUES.md), [ISS-120](../ISSUES.md) |
