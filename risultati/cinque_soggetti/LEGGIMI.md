# Due misure rimaste a cinque soggetti

Copiate dal progetto storico il 2026-08-26, da `DIP_PROJECT/scripts/out/`.

| file | misura | figura |
|---|---|---|
| `exp017_rf_size.json` | F2 e latenza al variare del numero di alberi | `fig_dimensione.png` |
| `exp013_camera_viewpoint.csv` | escursione dell'angolo del tronco, 25 sequenze x 2 telecamere | `fig_viewpoint_dist.png` |

**Provengono dall'impianto a cinque soggetti**, non dalle run a dieci. Il
Capitolo dei risultati lo dichiara accanto a entrambe, e le due figure
riportano la stessa avvertenza stampata dentro l'immagine.

Stanno qui, e non in `risultati/laboratorio/`, proprio per non essere
confuse con i risultati a dieci soggetti.

---

## `viste_cinque_soggetti.json` — aggiunto il 2026-09-01

Le tre run del trasferimento fra punti di vista, consolidate da
`DIP_PROJECT/training_results_baseline/`:

| condizione | run | F2 | falsi positivi |
|---|---|---:|---:|
| Camera1 su Camera1 | `rf_A3_L22_cam1_arch50` | 0,857 ± 0,088 | 57 |
| Camera1 su Camera2 | `rf_A3_L22_cam1to2_ds_cam1to2` | 0,434 ± 0,182 | 1.113 |
| Camera1+2 su Camera2 | `rf_A3_L22to2_ds_both` | 0,678 ± 0,123 | 460 |

Tutte e tre foresta casuale a 50 alberi, feature A3, finestra 22 a 9 fps,
LOSO a **cinque** fold.

**Perche' e' stato copiato qui.** Il divario fra le viste --- 0,422 di F2 --- e'
il numero rispetto a cui il lavoro dichiara che l'architettura non decide, e
non aveva un file che lo producesse ([ISS-126](../../docs/ISSUES.md#iss-126)).
Nel copiarlo e' emerso che la prima riga citata nel testo apparteneva a un
modello diverso ([ISS-129](../../docs/ISSUES.md#iss-129)).
