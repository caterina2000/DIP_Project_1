# B3 — Verifica controllata sulle occlusioni

**Che cosa è stato chiesto:** non limitarsi a osservare che le occlusioni
esistono, ma **provocarle in modo controllato** — mascherare gruppi di punti del
corpo e misurare quanto la prestazione degrada.

**La risposta in una riga:** **fatta nella forma suggerita**, ed è la stessa
misura di [A2](A2_occlusioni.md): la perdita massima è **0,037** di F2 contro
una dispersione fra soggetti di **0,071**.

---

## Perché questa richiesta e A2 sono la stessa cosa

A2 chiedeva *se* il sistema regge alle occlusioni; B3 ha indicato *come*
verificarlo. La forma suggerita — congelare un gruppo di landmark all'ultima
posizione nota — è esattamente ciò che uno stimatore di posa fa quando smette
di vedere una parte del corpo, ed è per questo che è una simulazione
difendibile e non un'approssimazione comoda.

Il dettaglio dei passaggi, dei gruppi scelti e del confronto con la dispersione
fra soggetti sta in **[A2 — Resilienza alle occlusioni](A2_occlusioni.md)**.

---

## Le due cose che vale la pena ripetere qui

**1. Il confronto conta più della misura.** «0,037 di F2» non significa nulla da
solo. Significa qualcosa accanto alla dispersione fra soggetti — 0,071 — che è
di quanto il risultato cambia già da sé a seconda di chi è la persona esclusa
dall'addestramento. La degradazione da occlusione resta **sotto** il rumore
naturale dell'esperimento, ma di un fattore due e non più di quattro: la misura
è stata rifatta il 7 settembre con il motore corrente
([EXP-027](../EXPERIMENTS.md)).

**2. Il caso peggiore non è quello simulato.** L'occlusione simulata toglie
informazione. Il difetto trovato il 6 settembre ne mette una **falsa** al suo
posto: su Camera 2 lo stimatore perde chi cade e si aggancia a un'altra persona
in 11 riprese su 50 ([ISS-134](../ISSUES.md)). Lì il classificatore non riceve
un ingresso incompleto, ne riceve uno sbagliato, e nessuna misura di robustezza
alle occlusioni lo copre.

---

## Dove guardare

| | |
|---|---|
| artefatto | `risultati/occlusioni/foresta_DTW.json` |
| script | `pipeline/occlusioni.py` |
| registro | [ISS-134](../ISSUES.md) per il caso peggiore |
| nella tesi | Capitolo 4, `fig:occlusioni` |
