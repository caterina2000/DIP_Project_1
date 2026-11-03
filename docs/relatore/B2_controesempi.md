# B2 — I controesempi di una casa, verificati sull'altra

**Che cosa è stato chiesto:** i controesempi raccolti in un'abitazione riducono
i falsi allarmi **anche nell'altra**, o il modello ha semplicemente imparato
quella stanza? Erano due ipotesi distinte, e la verifica doveva scegliere fra
loro.

**La risposta in una riga:** **la prima ipotesi** — l'effetto si trasferisce
all'altra casa, in entrambi i versi, con un fattore circa due.

---

## Come ci siamo arrivati, passo per passo

### Passo 1 — Che cos'è un controesempio, qui

Le sessioni domestiche producono soprattutto un errore: il sistema chiama
«caduta» qualcuno che **si sdraia**. I controesempi sono finestre di quelle
registrazioni, etichettate come non-caduta, aggiunte all'addestramento.

La domanda del relatore è se il modello impari da esse *la categoria*
«sdraiarsi» — che è generale — oppure *quella stanza*: quel divano, quella
luce, quella distanza dalla telecamera.

### Passo 2 — Il disegno della verifica

L'unica forma che distingue le due ipotesi è **incrociare le case**: prendere i
controesempi di una sola abitazione e misurare l'effetto sull'altra, mai vista.
E poi rifarlo scambiando i ruoli, perché un solo verso non basterebbe: potrebbe
essere una proprietà di quella casa particolare.

### Passo 3 — Il risultato, in entrambi i versi

| controesempi presi da | verifica su | eventi/ora, prima → dopo |
|---|---|---|
| casa dei nonni | casa dello studente | 0,342 → **0,171** |
| casa dello studente | casa dei nonni | 1,781 → **0,890** |

**Circa un fattore due in entrambe le direzioni.** Con due sole abitazioni non è
una dimostrazione, ma fra le due ipotesi indica la prima: ciò che il modello
impara dai controesempi **non è la stanza**.

Nel testo l'effetto è chiamato **adattamento al dominio di installazione** e non
generalizzazione, come indicato al punto 4 dell'email
([C2](C2_adattamento_al_dominio.md)).

### Passo 4 — Il costo, che va dichiarato insieme al beneficio

In quella configurazione il **recall scende a due cadute su cinque**. I falsi
allarmi si dimezzano e metà delle cadute non viene più vista.

È la ragione per cui la scelta della configurazione da presentare resta una
domanda aperta rivolta al relatore ([D4](D_domande_al_relatore.md)) e non una
decisione presa in silenzio: in un sistema di sicurezza il peso relativo dei
due errori è una scelta di merito, non tecnica.

### Passo 5 — L'unità di misura, che qui è tutto

I numeri della tabella sono **eventi all'ora**, non finestre sopra soglia. Sulle
stesse registrazioni le due grandezze differiscono di un fattore **44,8**
([B4](B4_eventi_e_latenza.md)): riportare finestre farebbe sembrare il sistema
quarantacinque volte peggiore di quello che una persona in casa
percepirebbe.

---

## Che cosa questa risposta non copre

- **Due case non sono un campione.** Indicano una direzione, non la misurano.
- I controesempi vengono da persone che sanno di essere registrate: non è detto
  che si sdraino come farebbero se non lo sapessero.

---

## Dove guardare

| | |
|---|---|
| artefatto | `risultati/campo/compiti_in_casa.json` |
| eventi per sessione | `risultati/campo/eventi_sessioni.json` |
| script | `pipeline/confronto_compiti.py`, `pipeline/eventi_sessioni.py` |
| nella tesi | Capitolo 5, sezione sull'adattamento al dominio, `fig:compiti_casa` |
