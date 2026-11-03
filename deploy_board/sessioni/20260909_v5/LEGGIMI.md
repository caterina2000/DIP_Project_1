# Sessione del 9 settembre 2026, sera — la selezione v5 sulla board

Registrata sulla Radxa (`192.168.1.20`) con `deploy_board/mostra_web.py`, la
configurazione **v5/DTWH a 13 colonne** installata la sera stessa, e cadute
messe in scena dalla candidata. Quindici minuti pieni, terminata da sola.

## Perche' questa cartella conta

E' la **prima prova di campo della selezione v5**. Il pacchetto e' stato
esportato da `feature_v5_omnifall.csv` alle 19:40 e differisce da quello di
stamattina per **due grandezze su tredici**:

| | 10:18 (mattina) | v5 (sera) |
|---|---|---|
| | `A2_angolo_tronco` | **`A2_testa_rel_y`** |
| | `A3_ginocchia_rel_y` | **`A3_caviglie_rel_y`** |

**Il motore geometrico non cambia** --- impronta `e4c0d354...` identica ---
quindi qualunque differenza viene dal modello e da quelle due colonne, non
dall'estrattore.

## Cosa c'e'

| | |
|---|---|
| `clip/` | **2.254 fotogrammi annotati** --- scheletro, punteggio, soglia, raffica --- uno ogni ~0,3 s. **Esclusi da git** per `**/clip/`: ritraggono una persona identificabile |
| `sess_20260909_v5.csv` | il registro di **ogni finestra decisa**: 624 righe. E' testo, ed e' tracciato: da qui si ricalcola qualunque regola senza le immagini |
| `sess_20260909_v5.log` | l'uscita del programma, con gli allarmi stampati |

## Cosa dicono

**Quattro cadute messe in scena**, dichiarate dalla candidata sui fotogrammi
annotati. **Due allarmi.**

| # | istante | il classificatore la vede? | l'allarme suona? | perche' |
|---|---|---|---|---|
| 1 | 742--746 s | **si**, picco 0,960, 13 finestre | **si** | |
| 2 | 748--751 s | **si**, picco 0,800, 9 finestre | **no** | sei secondi dopo la prima: **soppressa dai 30 s di sospensione** ([ISS-162](../../../docs/ISSUES.md#iss-162)) |
| 3 | 803--807 s | **no**, picco 0,520, **una** finestra | no | discesa lenta: nei fotogrammi si accovaccia e rotola |
| 4 | 855--857 s | **si**, picco 0,800, 7 finestre | **si** | alle 850,0 s e' **in piedi** con punteggio 0,000: evento distinto dal n. 3 |

> **Il classificatore vede 3 cadute su 4. La regola ne segnala 2 su 4.**
> **Una caduta su quattro e' persa dalla REGOLA, non dal modello.**

### Il falso positivo

La raffica delle **881,6 s** --- 4 finestre, picco **0,660** --- **non e' una
caduta**: in `clip/f00881.8.jpg` la persona e' **seduta sul divano con il
telefono**. La regola non ha suonato, e ha fatto bene.

Il pacchetto installato e' **DTWH**, cioe' quello **con `A3_h_pavimento`**, la
grandezza reintrodotta apposta per distinguere chi e' a terra da chi sta su una
superficie rialzata. Su un divano vero da **0,660**.

**Correzione a un'analisi fatta prima di guardare i fotogrammi:** sembrava che
abbassare la persistenza da 5 a 4 recuperasse un evento. **E' falso**, quella
raffica e' il divano. Abbassare la regola **aggiungerebbe un falso allarme** e
non recupererebbe la caduta n. 3, che ha una sola finestra sopra soglia.

### Il confronto con la mattina

| | picchi | allarmi |
|---|---|---|
| mattina, DTWH precedente | 0,540 · 0,200 · 0,720 | 0 su 3 |
| sera, **v5** | 0,960 · 0,800 · 0,520 · 0,800 | **2 su 4** |

**Il confronto NON e' pulito, e non va citato come se lo fosse.** La mattina il
**26,7%** delle finestre era senza posa; qui il **98,7%** ce l'ha. Parte del
guadagno e' v5 e parte e' l'inquadratura. Per separarli vanno rigirate le clip
della mattina col pacchetto v5 (`deploy_board/rendi_clip.py`).

## Due difetti che questa sessione ha reso visibili

**1. Il sistema ha deciso per 203 secondi su 900.** Le prime **624 finestre
utili cominciano a 697,4 s**: per undici minuti e trentasette secondi non ha
deciso nulla, e **2.717 finestre sono state scartate perche' il piano del
pavimento non era ancora stimato**. E' [ISS-156](../../../docs/ISSUES.md#iss-156)
osservata dal vivo. In esercizio continuo il riscaldamento si paga una volta;
per una prova a tempo si mangia i tre quarti della sessione.

**2. La sospensione di 30 secondi ha perso una caduta vera.** Le cadute 1 e 2
distano sei secondi; la seconda e' stata vista benissimo e non ha prodotto
allarme. E' lo scenario domestico che conta di piu' --- cade, prova a
rialzarsi, ricade. Registrato come [ISS-162](../../../docs/ISSUES.md#iss-162).

**3. La colonna `allarme` del registro e' `0` su tutte e 624 le righe.** Il log
stampa `ALLARME 1 a 743.5 s`, e alla riga corrispondente la colonna `corsa`
arriva davvero a 5 --- la regola scatta --- ma l'allarme **non viene scritto**.
Chi ricalcolasse gli eventi dal CSV ne conterebbe **zero**. E' lo stesso modo di
sbagliare di [ISS-142](../../../docs/ISSUES.md#iss-142): il fatto accade e
l'artefatto non lo registra.

## Da fare

- ~~Dichiarare sui fotogrammi dove sono state le cadute~~ **fatto**: quattro cadute, elencate sopra.
- Rigirare le clip della mattina con il pacchetto v5, per rendere pulito il
  confronto.
