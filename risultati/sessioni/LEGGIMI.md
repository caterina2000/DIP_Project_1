# Le sessioni registrate sulla board

Dodici sessioni, quattro giornate, due abitazioni, **9,6 ore** e 205.905
fotogrammi. Sono i dati da cui vengono tutti i numeri di campo del lavoro.

Copiate qui il 23 agosto 2026 da `DIP_PROJECT/sessioni_reali/`, che resta la
cartella di raccolta.

---

## Che cosa c'e', e che cosa NON c'e'

Per ogni sessione:

| file | contenuto |
|---|---|
| `punteggi.csv` | **una riga per finestra**: istante e punteggio del classificatore. E' il file che conta: qualunque regola di decisione si ricalcola da qui, senza rifare le sessioni |
| `eventi.csv` | le finestre sopra soglia. **Il nome inganna**: vedi sotto |
| `riepilogo.json` | durata, fotogrammi, quota di pose valide, fps medio, stalli |
| `sanita.csv` | controlli di funzionamento durante la sessione |

**Le clip NON sono qui, ed e' deliberato.** Le immagini salvate attorno agli
allarmi ritraggono persone identificabili, e restano nella cartella di
raccolta, esclusa da git. Nessuna di esse e' necessaria a riprodurre un
numero: servono solo a capire *perche'* un allarme e' scattato, e per quello
si guardano dov'e' che stanno. Fanno eccezione tre clip usate per la
dimostrazione, descritte in fondo.

---

## Attenzione al nome `eventi.csv`

Il file contiene **finestre sopra soglia**, non eventi di allarme. Le due
grandezze differiscono di un fattore misurato in **44,8**: una singola caduta
produce una raffica di finestre consecutive, e su una delle sessioni ne ha
prodotte centoventinove.

Un evento richiede la regola dichiarata --- cinque finestre consecutive sopra
soglia, poi trenta secondi di sospensione --- che al momento della raccolta
**non era implementata a bordo** ([ISS-051](../../docs/ISSUES.md)). Gli eventi
si ricalcolano da `punteggi.csv` con `pipeline/eventi_sessioni.py`.

Ne segue che la colonna «finestre sopra soglia per ora» qui sotto **non e' un
numero riportabile** e non va confrontata con la letteratura, che riporta
eventi.

---

## Indice delle sessioni

| sessione | inizio | ore | fotogrammi | pose valide | fps | finestre sopra soglia | /ora |
|---|---|---:|---:|---:|---:|---:|---:|
| `20260810/bloccofps_20260810_165151` | 10/08 16:51 | 0,03 | 750 | 13,6% | 7,5 | 34 | 1223,7 |
| `20260810/bloccomultipersona_20260810_165538` | 10/08 16:55 | 0,00 | 9 | 0,0% | 8,2 | 0 | — |
| `20260810/bloccomultipersona_20260810_165645` | 10/08 16:56 | 0,35 | 5.148 | 36,5% | 4,1 | 67 | 191,4 |
| `20260810/bloccosolo_20260810_172124` | 10/08 17:21 | 0,25 | 3.612 | 39,8% | 4,0 | 78 | 311,9 |
| `20260810/bloccocadute2p_20260810_171806` | 10/08 17:18 | 0,05 | 932 | 0,6% | 5,3 | 0 | — |
| `20260810/bloccoduepersone_20260810_174446` | 10/08 17:44 | 0,23 | 3.830 | 5,1% | 4,6 | 0 | — |
| **`20260811/bloccodurata5h_20260811_130411`** | **11/08 13:04** | **4,99** | **109.814** | **83,0%** | **6,1** | **208** | **41,7** |
| `20260812/bloccononni_20260812_142519` | 12/08 14:25 | 1,20 | 31.776 | 92,0% | 7,3 | 1.965 | 1.635,5 |
| `20260812/bloccocadute_nonni_20260812_154007` | 12/08 15:40 | 0,75 | 19.373 | 99,3% | 7,2 | 1.038 | 1.384,0 |
| `20260812/bloccocadute_2persone_20260812_181033` | 12/08 18:10 | 0,49 | 2.022 | 86,8% | 1,1 | 113 | 230,9 |
| `20260813/bloccocadute_sola_20260813_091641` | 13/08 09:16 | 0,58 | 16.843 | 25,9% | 8,0 | 50 | 85,7 |
| `20260813/bloccomulti_3persone_20260813_113943` | 13/08 11:39 | 0,66 | 11.796 | 97,6% | 5,0 | 3.855 | 5.831,6 |

---

## La colonna che dice piu' delle altre: le pose valide

Va letta prima di qualunque punteggio, perche' **una sessione con pose valide
sotto meta' non misura il classificatore: misura l'inquadratura.**

| giornata | luogo | pose valide |
|---|---|---|
| **10 agosto** | casa dello studente | **0,6% -- 39,8%** |
| 11 agosto | casa dello studente | 83,0% |
| 12 agosto | casa dei nonni | 86,8% -- 99,3% |
| 13 agosto | casa dei nonni | 25,9% -- 97,6% |

Le sei sessioni del **10 agosto** sono quelle in cui la telecamera era
posizionata male: troppo vicina, troppo bassa, con il corpo che usciva
dall'inquadratura. Su `bloccocadute2p` lo stimatore trova una posa nello
**0,6%** dei fotogrammi, cioe' in pratica mai; su `bloccoduepersone` nel 5,1%.

Quelle sessioni **non entrano in alcun risultato**, e non e' una scelta: non
c'e' niente da misurare. Restano qui per tre ragioni:

1. documentano il difetto di posizionamento, che e' il motivo per cui esiste
   il protocollo di ripresa del Capitolo~6;
2. `bloccofps` e le due `bloccomultipersona` sono le uniche prove di frame
   rate e multi-persona condotte sul campo;
3. una registrazione fallita e' un dato: ripeterla per dimenticanza costa piu'
   che conservarla.

Anche `20260813/bloccocadute_sola` e' al 25,9%, ed e' da trattare con la
stessa cautela.

---

## Quali sessioni producono quali risultati

| risultato | sessioni usate |
|---|---|
| [valutazione_10sog_k31.json](../campo/valutazione_10sog_k31.json) --- le cinque configurazioni a confronto | `20260811/bloccodurata5h` (6,0 h) + `20260812/bloccononni` (1,1 h) |
| [compiti_in_casa.json](../campo/compiti_in_casa.json) --- i tre compiti | le stesse due |
| [valutazione_incrociata_10sog.json](../campo/valutazione_incrociata_10sog.json) --- controesempi di una casa, verifica sull'altra | le stesse due, incrociate |
| recall di campo (5 cadute) | `20260813/bloccocadute_sola` |
| [EXP-016](../../docs/EXPERIMENTS.md#exp-016) --- parita' PC contro board | `20260812/bloccocadute_nonni`, 56 clip |

Le **cinque cadute reali** su cui e' misurato il recall vengono da una sola
sessione. E' il limite piu' serio del lavoro, ed e' dichiarato come tale:
cinque eventi non permettono di stimare un recall.

---

## Le clip per la dimostrazione

Tre clip dell'11 agosto --- casa dello studente --- sono state copiate in
`deploy_board/clip_demo/`, accanto alle tre del 13 agosto che c'erano gia'.
Sono le tre con il punteggio piu' alto della sessione:

| clip | ora | punteggio | fotogrammi |
|---|---|---:|---:|
| `evt_0001_132012` | 13:20 | 0,757 | 170 |
| `evt_0188_182734` | 18:27 | 0,696 | 141 |
| `evt_0068_142026` | 14:20 | 0,618 | 141 |

Servono a far girare `rileva.py --video` su riprese vere senza dover
riaccendere la telecamera. **Nessuna delle tre e' una caduta**: sono i tre
falsi allarmi piu' netti della sessione di cinque ore, ed e' proprio per
questo che sono utili --- mostrano su che cosa il sistema sbaglia.

Sono immagini di persone identificabili, e il `.gitignore` alla radice del
progetto le esclude gia' oggi, prima che il progetto diventi un repository.

**Le sei sessioni del 10 agosto non hanno clip utilizzabili**, perche' con
pose valide fra lo 0,6% e il 39,8% quasi nessuna finestra ha superato la
soglia: due delle sei non hanno prodotto neppure un evento.

---

## Come ricalcolare gli eventi

```
python pipeline/eventi_sessioni.py
```

Lo script trova le sessioni da solo: preferisce questa cartella, e ripiega
sulla cartella di raccolta del progetto storico se qui non trova nulla.
Stampa in testa da dove sta leggendo.

Legge `punteggi.csv`, applica la regola di decisione dichiarata e produce i
conteggi per evento. **E' l'unica forma in cui i numeri di campo vanno
riportati.** Due parametri utili:

| | |
|---|---|
| `--soglia` | ricalcola con una soglia diversa da quella registrata dalla board |
| `--sensibilita` | mostra come cambia il conteggio al variare di persistenza e sospensione, che e' il modo di verificare che una conclusione non dipenda da come sono stati fissati quei due numeri |
