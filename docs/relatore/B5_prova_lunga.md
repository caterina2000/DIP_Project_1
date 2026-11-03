# B5 — Prova lunga con controllo della sospensione

**Che cosa è stato chiesto:** una sessione lunga sul dispositivo, con la
garanzia che la macchina **non si sia sospesa** nel frattempo — perché una
sospensione non rilevata falsifica il risultato senza far fallire nulla.

**La risposta in una riga:** **fatta il 6 settembre**, 4,59 ore continue con
sospensione misurata pari a **zero**. Non sono le dodici ore, e gli allarmi che
ne sono usciti non sono verificabili.

---

## Perché questa richiesta era separata da A4

A4 chiedeva la prova di durata; B5 ha aggiunto la condizione che la rende
valida. La distinzione è nata da un fatto concreto: **il primo tentativo era
sembrato riuscire e non era vero.**

La sessione si era chiusa senza errori, con il registro completo. Ma il
conteggio dei fotogrammi non tornava con la durata dichiarata e la temperatura
della board era scesa di tredici gradi a metà sessione: il dispositivo si era
sospeso per inattività dopo venti minuti, e il registratore — che misurava il
tempo con un orologio che durante la sospensione non avanza — al risveglio
riprendeva e alla fine dichiarava la durata richiesta.

**Un test notturno avrebbe prodotto un tasso di falsi allarmi eccellente e privo
di significato.** È il modo peggiore in cui una misura può essere sbagliata:
non fallisce, sembra riuscire ([ISS-130](../ISSUES.md)).

---

## Come è stata resa verificabile, passo per passo

### Passo 1 — Due orologi invece di uno

`rileva.py` tiene ora l'**orologio di sistema** — che avanza anche durante la
sospensione — e il **cronometro monotòno**, che non lo fa. La differenza fra i
due *è* il tempo dormito, e viene scritta in ogni riepilogo insieme a un flag
esplicito.

### Passo 2 — Il riepilogo scritto durante, non alla fine

Ogni cinque minuti, in modo atomico, anche su interruzione. Una prova che si
ferma all'undicesima ora lascia comunque il bilancio: prima non lo lasciava, ed
è il difetto che avrebbe fatto perdere la misura una seconda volta.

### Passo 3 — La sessione del 6 settembre

| | |
|---|---:|
| durata di orologio | 16.508,357 s |
| durata di cronometro | 16.508,357 s |
| **differenza** | **3,4 microsecondi** |
| flag `sospesa` | `false` |

**La macchina non si è sospesa, e stavolta lo sappiamo invece di sperarlo.**

Il resto dei numeri della sessione — 7,26 fps, 35,1% di pose, 14 eventi, 136,65
ms per fotogramma — sta in [A4](A4_prova_di_durata.md).

---

## Che cosa resta aperto

- **La durata.** 4,59 ore non sono le dodici richieste. La prova è però ora
  ripetibile e il difetto che l'aveva invalidata è rilevabile: manca solo di
  lasciare il dispositivo acceso più a lungo.
- **Le clip degli allarmi**, senza le quali anche una prova da dodici ore
  produrrebbe un conteggio non verificabile ([ISS-142](../ISSUES.md)).

---

## Dove guardare

| | |
|---|---|
| riepilogo della sessione | `risultati/sessioni/20260906/notte_20260906_1523/notte_20260906_1523_riepilogo.json` |
| script | `deploy_board/rileva.py` |
| registro | [EXP-024](../EXPERIMENTS.md), [ISS-130](../ISSUES.md), [ISS-142](../ISSUES.md) |
| nella tesi | Capitolo 5, «Il test che sembrava riuscito» |
