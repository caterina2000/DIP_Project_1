# Archivio delle run su `feature_v2.csv`

Copiate qui il **7 settembre 2026**, prima di riaddestrare su
`feature_v3.csv`. I nomi dei file prodotti da `pipeline/addestra.py` non
contengono la versione del dataset: `run_gru_tre_classi_DTW_cam1_L22.json` e
`run_grafo_tre_classi_DTW_cam1_L22.json` sarebbero stati sovrascritti dalle
run nuove.

Sono le run del **20 e 27 agosto**, quelle su cui poggiano le tabelle del
Capitolo 4 fino a questa data. Il dataset che le ha prodotte dipende
dall'ordine di estrazione ([ISS-138](../../../docs/ISSUES.md#iss-138)) e non
contiene `A3_h_pavimento` ([ISS-139](../../../docs/ISSUES.md#iss-139)).

`pipeline/scheda_numeri.py` non le legge: scandisce la cartella superiore e
tiene solo i nomi che cominciano per `run_`, quindi questa sottocartella
resta fuori. **Servono al confronto v2/v3, non vanno usate come risultati
correnti.**

Le due run del 6 settembre sera (`foresta`, DTW e DTWH) sono gia' su v3 e non
stanno qui.
