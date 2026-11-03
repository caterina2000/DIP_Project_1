# Sessione del 9 settembre 2026 — le prime immagini di settembre

Registrata sulla Radxa (`192.168.1.20`) con `deploy_board/mostra_web.py`, la
configurazione **DTWH a 13 colonne** installata lo stesso giorno, e cadute
messe in scena dalla candidata.

## Perche' questa cartella conta

**Di settembre non esisteva nessuna immagine.** `clip_demo/` sono le clip di
**agosto**; il registratore che le ha sostituite aveva perso il salvataggio
([ISS-142](../../../docs/ISSUES.md#iss-142)), ed e' il motivo per cui i
quattordici eventi della prova di durata del 6 settembre **non sono
verificabili**: non si puo' dire se fossero falsi positivi, solo che il sistema
li ha generati. Queste sono le prime immagini di settembre che esistano.

## Cosa c'e'

| | |
|---|---|
| `clip/` | 2.539 fotogrammi **annotati** — scheletro, punteggio, soglia, raffica — uno ogni ~0,3 s. **Esclusi da git** per `**/clip/`: ritraggono una persona identificabile |
| `sess_20260909_diretta.csv` | il registro di **ogni finestra decisa**: istante, punteggio, sopra soglia, raffica, allarme, posa, pavimento. E' testo, ed e' tracciato: da qui si ricalcola qualunque regola di decisione senza le immagini |

## Cosa dicono, in breve

**Tre cadute messe in scena**, dichiarate dalla candidata sui fotogrammi:
f00431-f00467, f00503-f00529,3, f00547,0-f00566,5.

Con la regola installata --- soglia 0,50 e **cinque** finestre consecutive ---
gli allarmi sono **zero su tre**. E le tre cadute sono tre casi diversi:

| | picco | finestre sopra 0,50 | senza posa |
|---|---:|---:|---:|
| caduta 1 | 0,540 | 1 | 11% |
| caduta 2 | **0,200** | 0 | **1%** |
| caduta 3 | 0,720 | 5, ma non consecutive | 0% |

La **caduta 2 il classificatore non la vede affatto**, e non e' il
tracciamento: le finestre senza posa sono l'1%. Nei fotogrammi la persona e'
distesa lungo l'asse ottico, e il tronco si proietta in un segmento corto.

Rivalutando il registro senza riaddestrare nulla:

| soglia | persistenza | allarmi |
|---|---:|---:|
| 0,50 | **5** *(installata)* | **0** |
| 0,50 | 3 | 1 |
| 0,40 | 2 | 2 |
| 0,30 | 2 | 3 |

Il tetto di qualunque regola provata e' **2 su 3**. L'ultima riga non e' un
guadagno: uno degli allarmi **non e' una caduta**. In `clip/f00213.6.jpg` la stanza e' vuota e lo stimatore ha disegnato
uno scheletro **sulla cyclette** --- e'
[ISS-136](../../../docs/ISSUES.md#iss-136), che finora era un'osservazione e
adesso ha un fotogramma con l'ora sopra.

**Il 26,7% delle finestre e' senza posa.** Una caduta avvenuta dentro un buco
di tracciamento non lascia traccia nel registro, e nessuna regola la recupera.
