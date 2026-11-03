# A4 — Prova di durata in ambiente reale

**Che cosa è stato chiesto:** lasciare il sistema acceso a lungo in una casa
vera, e vedere che cosa succede.

**La risposta in una riga:** **fatta**, in due tempi — dodici blocchi domestici
in agosto e una sessione continua di **4,59 ore sulla board** il 6 settembre,
la prima con il controllo della sospensione della macchina. Non sono ancora le
dodici ore, e i quattordici allarmi che ne sono usciti **non sono
verificabili**.

---

## Come ci siamo arrivati, passo per passo

### Passo 1 — Le registrazioni domestiche di agosto

Dodici blocchi, quattro giornate, **due abitazioni**, con il consenso dei
partecipanti. Otto blocchi superano i nove minuti e sono utilizzabili per le
statistiche: **10,39 ore**. Gli altri quattro durano fra i due e i sette minuti
e servono solo come controlli puntuali.

Il blocco più lungo, `bloccodurata5h`, dura **6,11 ore** di orologio (nel testo
compare come «4,99 ore continuative», che è il tempo di esercizio effettivo
dopo le interruzioni).

### Passo 2 — La prova che sembrava riuscita, e non era vero

Il primo tentativo di prova lunga si era chiuso senza errori, con il registro
completo fino in fondo. Ma il conteggio dei fotogrammi non tornava con la
durata dichiarata, e la temperatura della board era scesa di tredici gradi a
metà sessione: **il dispositivo si era sospeso per inattività**, e il
registratore — che misurava il tempo con un orologio che durante la sospensione
non avanza — non se ne era accorto.

**È il difetto peggiore possibile per una prova di durata, perché non
fallisce: sembra riuscire.** Al risveglio la registrazione riprende e alla fine
dichiara la durata richiesta. Un test notturno avrebbe prodotto un tasso di
falsi allarmi eccellente e privo di significato
([ISS-130](../ISSUES.md)).

**La correzione è un secondo orologio.** `rileva.py` tiene ora l'orologio di
sistema *e* il cronometro monotòno, e dichiara la differenza fra i due in ogni
riepilogo: se la macchina ha dormito, il riepilogo lo dice.

E scrive il riepilogo **ogni cinque minuti**, in modo atomico, anche su
interruzione: una prova che si ferma all'undicesima ora lascia comunque il
bilancio. Prima non lo lasciava, ed è il difetto che avrebbe fatto perdere la
misura una seconda volta.

### Passo 3 — La sessione del 6 settembre

Board accesa alle 15:23 con la telecamera collegata, configurazione installata,
nessun intervento.

| | |
|---|---:|
| durata | **4,59 ore** (16.508 s) |
| **sospensione della macchina** | **~0 s** — differenza fra i due orologi: 3,4 µs |
| fotogrammi | 119.928 |
| frequenza media | 7,26 fps |
| pose valide | 35,1% |
| interruzioni della telecamera | 2, per 5,1 s in tutto, riprese da sole |
| finestre sopra soglia | 168 |
| **eventi di allarme** | **14**, cioè 3,05 all'ora |
| tempo passato sopra soglia | 0,3% |

**Il doppio orologio ha fatto il suo lavoro:** stavolta sappiamo che la macchina
non si è sospesa, invece di sperarlo.

**La telecamera USB è caduta due volte** e si è ripresa da sola dopo tre
secondi. È un dato di affidabilità che una prova breve non avrebbe mostrato.

Nella stessa sessione è uscito il bilancio del costo per fotogramma —
136,65 ms, vedi [A3](A3_dispositivo_edge.md) — che chiude una riserva aperta
dal 26 agosto ([ISS-113](../ISSUES.md)).

### Passo 4 — Che cosa quella sessione *non* dice, e perché

**I quattordici allarmi non sono verificabili.** Il registratore della board
**non salva immagini**: né in continuo, il che è voluto, né attorno agli
allarmi, il che non lo è. La sua documentazione afferma che le clip «se
attivate» restano su disco locale, ma non esiste alcun modo di attivarle: il
codice non le scrive ([ISS-142](../ISSUES.md)).

Il registratore usato in agosto le salvava — ±10 s attorno a ogni allarme, con
un tetto giornaliero — ed è con quelle clip che gli allarmi delle sessioni
domestiche sono stati guardati uno per uno. Sulla board quella parte non è mai
arrivata.

Restano quindi quattordici punteggi sopra soglia di cui **nessuno può dire** se
fossero una persona che si sdraiava, un'ombra, o davvero una caduta. Il numero
riportabile è il **tasso di eventi**, 3,1 all'ora; chiamarli falsi allarmi
sarebbe un'affermazione senza prova.

**E le pose valide sono il 35%:** per gran parte delle quattro ore e mezzo la
stanza era vuota. È una prova di **durata e di costo**, non di rilevamento.

---

## Che cosa resta aperto

1. **Le dodici ore.** 4,59 non sono 12. La prova ora è ripetibile e il difetto
   che l'aveva invalidata è rilevabile, quindi manca solo di lasciare il
   dispositivo acceso più a lungo.
2. **Il salvataggio delle clip**, prima di rifarla: senza, anche una prova da
   dodici ore produrrebbe un numero di allarmi che non si può verificare.

---

## Dove guardare

| | |
|---|---|
| la sessione | `risultati/sessioni/20260906/notte_20260906_1523/` |
| le sessioni di agosto | `risultati/sessioni/2026081*/` |
| conteggio degli eventi | `risultati/campo/eventi_sessioni.json`, da `pipeline/eventi_sessioni.py` |
| registro | [EXP-024](../EXPERIMENTS.md), [ISS-130](../ISSUES.md), [ISS-113](../ISSUES.md), [ISS-142](../ISSUES.md) |
| nella tesi | Capitolo 5, sezione sulle sessioni domestiche |
