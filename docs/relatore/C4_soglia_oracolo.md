# C4 — Punto 6: chiamarla soglia oracolo

**Che cosa è stato chiesto:** la soglia ritarata sul dominio di destinazione va
chiamata con il suo nome. Non è una prestazione del sistema: è ciò che si
otterrebbe **conoscendo già le risposte**.

**La risposta in una riga:** **fatto**, con la definizione esplicita nel testo e
la dichiarazione di che cosa non è.

---

## Perché il nome cambia la lettura del numero

Nel trasferimento a UR-Fall l'F2 passa da **0,034** a **0,492** ritarando la
soglia. Presentato senza qualificazioni, 0,492 sembra la prestazione del sistema
in un ambiente nuovo. Non lo è: per scegliere quella soglia servono **le
etichette del dominio di destinazione**, cioè bisogna già sapere quali finestre
sono cadute.

Chi installa il sistema in una casa non le possiede. Se le possedesse, non gli
servirebbe il sistema.

## Che cosa dice il testo

La soglia è definita come «valore ottenuto usando le etichette del dominio di
destinazione, che chi installa non possiede», e il numero è presentato come
**limite superiore** di ciò che una ritaratura potrebbe dare, non come
prestazione ottenibile.

## Perché il numero serve comunque

Serve a scomporre il fallimento. Il divario fra 0,034 e 0,492 è la parte
**recuperabile** ritarando; ciò che resta fra 0,492 e la prestazione in dominio
è **perdita reale** della capacità di separare. Le due parti sono quasi uguali,
49% e 51% ([B1](B1_pr_auc.md)).

Senza la soglia oracolo si saprebbe solo che il sistema non trasferisce. Con
essa si sa **quanta parte del problema sarebbe risolvibile da chi installa**, e
quanta no.

---

## Dove guardare

| | |
|---|---|
| artefatto | `risultati/campo/pr_auc_allineato.json`, `risultati/esterno/` |
| registro | [ISS-131](../ISSUES.md) per la correzione del valore |
| nella tesi | Capitolo 4, sezione sul trasferimento cross-dataset |
