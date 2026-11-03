# B1 — PR-AUC nel passaggio all'archivio esterno

**Che cosa è stato chiesto:** nel trasferimento a un archivio mai visto, non
fermarsi all'F2 con la soglia schierata, ma guardare la **PR-AUC** — che è
indipendente dalla soglia — per capire se il crollo sia solo taratura o perdita
vera.

**La risposta in una riga:** **è perdita vera**, ed è la meno comoda delle due
possibilità prospettate.

---

## Come ci siamo arrivati, passo per passo

### Passo 1 — Perché la domanda è quella giusta

Un F2 che crolla può significare due cose molto diverse:

- il modello **ordina ancora bene** le finestre, ma su una scala di punteggi
  spostata: allora basta ritarare la soglia e il sistema torna utile;
- il modello **non separa più**: nessuna soglia lo salva.

L'F2 con una soglia fissa non distingue i due casi. La PR-AUC sì, perché
riassume tutte le soglie possibili.

### Passo 2 — La misura, con il riferimento giusto accanto

La PR-AUC va sempre letta contro la **prevalenza**, cioè contro il valore che
avrebbe un classificatore casuale: 0,169 è un numero diverso se i positivi sono
il 10% o l'1% dei campioni.

| | PR-AUC | rispetto alla prevalenza |
|---|---:|---:|
| archivio di addestramento (UP-Fall) | 0,990 | **18,7×** il caso |
| archivio mai visto (UR-Fall) | **0,169** | **1,79×** il caso |

Con ROC-AUC 0,750.

**Nel dominio nuovo il modello è meno di due volte meglio del caso.** Non è
zero — qualcosa dell'ordinamento sopravvive, ed è coerente con il ROC-AUC di
0,750 — ma non è un sistema utilizzabile.

### Passo 3 — Quantificare le due componenti

Ritarando la soglia *usando le etichette del dominio di destinazione* l'F2
passa da **0,034** a **0,492**. Quella soglia nessuno che installi il sistema
la possiede, ed è per questo che nel testo si chiama **soglia oracolo**
([C4](C4_soglia_oracolo.md)).

Il divario si scompone quindi in due metà quasi uguali:

| | quota |
|---|---:|
| recuperabile ritarando la soglia | **49%** |
| perdita reale della capacità di separare | **51%** |

È il contributo originale di questa sezione: non «il sistema non trasferisce»,
ma *quanta parte* del fallimento sarebbe rimediabile da chi installa e quanta
no.

### Passo 4 — Una correzione, perché il numero precedente veniva da altrove

Fino al 3 settembre qui comparivano 0,612 di soglia oracolo e una divisione
«due terzi taratura, un terzo perdita». Quei valori venivano da un file del
progetto storico: **un altro esperimento**, con un'altra estrazione delle
feature, 1.125 finestre invece di 1.075 e una prevalenza di 0,128 invece di
0,094 ([ISS-131](../ISSUES.md)).

Ricalcolato sull'artefatto attuale, il valore è 0,492 e la divisione è quasi
esatta a metà. Il contributo regge, il numero cambia.

---

## Che cosa questa risposta non copre

- Un archivio esterno solo. UR-Fall è registrato in un'altra stanza, con altre
  persone e un'altra telecamera, ma resta un ambiente di laboratorio.
- Le etichette di UR-Fall hanno una definizione di «caduta» leggermente diversa,
  e la rietichettatura è documentata: parte del divario può venire da lì, e nel
  testo è dichiarato.

---

## Dove guardare

| | |
|---|---|
| artefatto | `risultati/campo/pr_auc_allineato.json` |
| trasferimento | `risultati/campo/valutazione_incrociata_10sog.json`, `risultati/esterno/` |
| script | `pipeline/valuta_esterno.py`, `pipeline/rietichetta_urfall.py` |
| registro | [EXP-014](../EXPERIMENTS.md), [ISS-131](../ISSUES.md) |
| nella tesi | Capitolo 4, sezione sul trasferimento cross-dataset |
