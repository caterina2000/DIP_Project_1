# Le riletture — quale CSV e' quale

**Il problema che questo file risolve.** Nel progetto ci sono CSV che si
somigliano e vogliono dire cose diverse. Prima di leggerne uno, guardare qui.

---

## I due tipi di CSV, e non vanno confusi

| | dove sta | che cos'e' |
|---|---|---|
| **la REGISTRAZIONE** | `risultati/sessioni/<data>/<sessione>/` | quello che il sistema **di allora** decise **mentre registrava**, in agosto |
| **la RILETTURA** | qui dentro | quello che il sistema **di oggi** dice **delle stesse immagini**, ricalcolato adesso |

Non sono confrontabili riga per riga: la prima e' in tempo reale sulla board,
la seconda e' una rilettura sul calcolatore a cadenza dichiarata di 10 fps.

### Nella cartella di una registrazione (agosto) ci sono quattro file

| file | contenuto |
|---|---|
| `feature.csv` | le grandezze **per fotogramma** --- il piu' grosso, fino a 18 MB. **Nomi vecchi** (`trunk_angle`, `head_rel_y`, ...): non contiene ne' gli integrali ne' l'altezza dal pavimento, quindi **da qui NON si puo' ricalcolare col modello di oggi** |
| `punteggi.csv` | il punteggio **per finestra**. E' il file che conta: da qui si ricalcola qualunque **regola** senza rifare niente |
| `eventi.csv` | le finestre sopra soglia. **Il nome inganna**: non sono eventi di allarme, il fattore fra le due cose e' 47,8 |
| `sanita.csv` | i controlli di funzionamento durante la registrazione |

### Nella cartella di una rilettura (qui) c'e' un CSV per clip

`<nome_clip>.csv`, accanto alla cartella `<nome_clip>/` con i fotogrammi
annotati. Colonne: `t_s, punteggio, sopra, corsa, allarme, posa, pavimento`.

**Se il CSV manca, la clip non ha prodotto nessuna decisione.** Non vuol dire
«non e' una caduta»: vuol dire che il sistema non si e' pronunciato. Vedi sotto.

---

## Che cosa c'e' in ciascuna cartella

### `v5_sessioni_agosto/` — tutte le sessioni, pacchetto v5

Le 422 clip delle quattro giornate di agosto rilette con il pacchetto
**v5/DTWH a 13 colonne** installato il 9 settembre sera. Solo i CSV: le
immagini non sono state prodotte perche' il disco e' pieno.

| cartella | casa | clip | **senza CSV** |
|---|---|---:|---:|
| `casaA_20260810_multipersona` | studente | 9 | 6 |
| `casaA_20260810_solo` | studente | 8 | 5 |
| `casaA_20260811_durata5h` | studente | 30 | **29** |
| `casaB_20260812_cadute_2persone` | nonni | 10 | 6 |
| `casaB_20260812_cadute_nonni` | nonni | 56 | **51** |
| `casaB_20260812_nonni` | nonni | 150 | **144** |
| `casaB_20260813_cadute_sola` | nonni | 9 | 4 |
| `casaB_20260813_multi_3persone` | nonni | 150 | **141** |
| | | **422** | **386 --- il 91,5%** |

**Le quattro sessioni del 10 agosto senza clip non compaiono**
(`bloccocadute2p`, `bloccoduepersone`, `bloccofps`, e una delle due
`bloccomultipersona`): sono quelle con le pose valide fra lo 0,6% e il 39,8%,
telecamera posizionata male, e non hanno salvato nessuna immagine.

Vedi [EXP-040](../../docs/EXPERIMENTS.md#exp-040).

### `v5_cadute_nonni_con_immagini/` — le cinque clip annotate

Le cinque clip di `casaB_20260812_cadute_nonni` di cui la candidata ha
dichiarato il contenuto, rilette **con i fotogrammi annotati**: scheletro,
punteggio, soglia, contatore della raffica.

| clip | che cosa contiene | esito |
|---|---|---|
| `evt_0067_155044` | **una caduta**, due persone distese sui divani | picco 0,740, **2** finestre sopra soglia su 5 richieste -> nessun allarme. **Lo scheletro e' agganciato a una persona sul divano**, non a chi cade |
| `evt_0090_155058` | a terra, poi si rialza | picco 0,020 --- corretto: l'evento e' la transizione, non lo stato |
| `evt_0173_155210` | **inizia una caduta** | nessuna decisione |
| `evt_0191_155223` | la caduta | nessuna decisione |
| `evt_0201_155236` | si rialza | nessuna decisione |

### `clipdemo_pacchetto_installato/` e `clipdemo_pacchetto_dtw12/`

**Non sono sessioni.** Sono le **sei clip dimostrative di agosto** in
`deploy_board/clip_demo/`, rilette due volte il 9 settembre mattina con due
configurazioni diverse, per confrontarle:

| cartella | pacchetto |
|---|---|
| `clipdemo_pacchetto_installato` | quello installato quella mattina, DTWH 13 colonne |
| `clipdemo_pacchetto_dtw12` | `deploy_board/pacchetto_dtw12/`, DTW **12** colonne, senza altezza dal pavimento |

**Difetto noto:** in `clipdemo_pacchetto_installato` il CSV c'e' per **due clip
su sei**. Le immagini ci sono tutte, i numeri no. Per rifarle:
`python deploy_board/rendi_clip.py clip_demo/* --out ...`

---

## Perche' il 91,5% non produce decisioni

Il pacchetto installato contiene `A3_h_pavimento`, che richiede la stima del
**piano del pavimento**. Su una clip di una quindicina di secondi la stima non
fa in tempo, e senza di essa il presidio scarta ogni finestra. E'
[ISS-156](../../docs/ISSUES.md#iss-156).

**Non e' dimostrato, e' coerente.** Il controllo che lo accerterebbe: riesportare
un pacchetto **DTW a 12 colonne** e rilanciare le stesse clip. Se tornano a
decidere, la causa e' quella. **Non e' stato fatto.**

---

## Che cosa NON si puo' misurare da qui

**Il richiamo sulle cadute domestiche.** Le clip esistono solo dove il sistema
**di allora** aveva suonato: una caduta che il vecchio sistema si era persa non
ha lasciato nessuna immagine, e nessuna rilettura la puo' recuperare.

Da qui si misura quanti dei vecchi allarmi il modello di oggi rifarebbe --- e
anche quello solo sulle 36 clip che decidono, non su 422.
