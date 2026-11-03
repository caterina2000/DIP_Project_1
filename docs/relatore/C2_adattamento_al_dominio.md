# C2 — Punto 4: chiamarlo adattamento al dominio, non generalizzazione

**Che cosa è stato chiesto:** correggere la terminologia. Aggiungere
all'addestramento controesempi presi dall'ambiente di installazione non è
*generalizzazione* — è **adattamento al dominio**, e chiamarlo con il nome
giusto cambia ciò che il risultato dimostra.

**La risposta in una riga:** **fatto**, nel testo e nella struttura
dell'argomento.

---

## Perché la correzione non è solo di parole

Le due parole descrivono due affermazioni diverse:

- **generalizzazione** significa che il modello funziona in ambienti che non ha
  mai visto. È un'affermazione forte, e i dati di questo lavoro **non la
  sostengono**: il trasferimento a un archivio esterno porta l'F2 a 0,034
  ([B1](B1_pr_auc.md));
- **adattamento al dominio** significa che il modello funziona meglio
  nell'ambiente da cui ha ricevuto esempi. È un'affermazione più modesta, ed è
  quella che i dati sostengono: i controesempi dimezzano gli eventi di falso
  allarme ([B2](B2_controesempi.md)).

Chiamarlo generalizzazione avrebbe fatto sembrare il risultato più grande di
quello che è, **e per giunta nella direzione in cui il lavoro ha il punto più
debole**.

## Che cosa dice ora il testo

Nel Capitolo 5: «adattamento al dominio di installazione — *domain adaptation*
nella terminologia corrente — e non generalizzazione».

La conseguenza operativa è dichiarata accanto: un sistema installato ha bisogno
di una fase di raccolta di controesempi **in quella casa**, e questo è un costo
di installazione, non una proprietà gratuita del modello.

---

## Dove guardare

| | |
|---|---|
| il risultato che sostiene il termine | [B2](B2_controesempi.md), `risultati/campo/compiti_in_casa.json` |
| il risultato che vieta l'altro termine | [B1](B1_pr_auc.md), `risultati/campo/pr_auc_allineato.json` |
| nella tesi | Capitolo 5, sezione sull'adattamento al dominio |
