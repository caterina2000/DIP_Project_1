# ISSUES — DIP_Project_1

Registro dei difetti. Nulla si cancella: cio' che viene risolto si sposta in
«Risolti» con data e intervento. La storia dei difetti serve.

Numerazione da 100 per non confondersi con le ISS-0xx del progetto storico.

---

## Aperti


<a id="iss-170"></a>
### ISS-170 — Il sottocampionamento allinea la durata della finestra, non la scala delle derivate

**Trovata:** 2026-09-21 · **Gravita': bassa** · **Stato: DICHIARATA**

`FRAME_STEP = 2` esiste per far somigliare il dataset alla cadenza di
esercizio: `config.py:43` dice che *«le feature dinamiche dipendono da dt,
quindi addestrare a 18 e girare a 9 le cambia di scala»*. L'intento e' giusto,
ma l'operazione non lo realizza fino in fondo, e la ragione e' l'ordine dei
passaggi.

| passaggio | dove | che cosa fa |
|---|---|---|
| calcolo delle grandezze | `pipeline/estrai_feature.py:279` | chiama il motore su **ogni** fotogramma originale, con l'fps misurato di quel fotogramma: derivate e integrali nascono qui |
| costruzione delle finestre | `src/dati.py:275` | `tratto.iloc[::2]` prende **una riga su due** del CSV gia' calcolato |

Le derivate sono quindi **gia' calcolate** quando il sottocampionamento
avviene, e **non vengono ricalcolate**. Dentro una finestra due campioni
adiacenti distano ~111 ms, ma la velocita' che ciascuno porta descrive i ~55 ms
fra due fotogrammi *originariamente* consecutivi. Il movimento del fotogramma
scartato non viene ripiegato nel campione successivo.

**Perche' la gravita' e' bassa.** Due ragioni misurate:

- delle dodici grandezze adottate **due sole sono derivate** (`A3_hip_vel`,
  `A3_testa_vel_rel`); otto sono integrali --- definiti in secondi dopo
  [ISS-148](#iss-148), quindi immuni --- e due sono statiche;
- [EXP-033](EXPERIMENTS.md#exp-033) ha misurato che cambiare la politica di
  `dt` sposta l'$F_2$ di **-0,006**, non distinguibile dal caso.

**Perche' non e' nulla.** Il rumore su una derivata scala come
$\sigma\sqrt{2}/\Delta t$: a 55 ms e' circa **2,8 volte** quello a 155 ms.
L'addestramento vede quindi velocita' sistematicamente piu' rumorose di quelle
che la board produce, su quelle due colonne.

**Che cosa NON e' questa voce.** Non e' [ISS-148](#iss-148), che riguardava
l'fps sbagliato passato al motore *sulla board*; non e' [ISS-158](#iss-158),
che riguarda la durata della finestra di decisione. Nessuna delle due dice che
in addestramento l'intervallo della derivata e' meta' dell'intervallo fra i
campioni della finestra.

**Intervento: dichiarata, non corretta.** Aggiunto un paragrafo in
`tesi/Cap3.tex`, sezione `sec:finestre`. Correggerla richiederebbe di
ricalcolare le derivate sui campioni sottocampionati, cioe' di buttare
l'informazione dei fotogrammi scartati, e nessuna misura indica che ne valga la
pena.

**Verificato con:** lettura di `pipeline/estrai_feature.py:279` e
`src/dati.py:275`; [EXP-038](EXPERIMENTS.md#exp-038) conferma che
`feature_v5.csv` ha il `dt` misurato per fotogramma.

**Collegamenti:** [ISS-148](#iss-148), [ISS-158](#iss-158),
[EXP-033](EXPERIMENTS.md#exp-033)

<a id="iss-167"></a>
### ISS-167 — 1,41 ore su 14,98 sono buchi in cui il sistema non decideva, e gli eventi/ora ci dividono sopra

**Trovata:** 2026-09-10 · **Gravita': media** · **Stato: APERTA**

`pipeline/eventi_sessioni.py` calcola gli eventi/ora dividendo per **l'arco
temporale** della sessione, cioe' l'ultimo istante meno il primo. Se il
sistema smette di produrre decisioni e poi riprende, quel tempo entra lo stesso
nel denominatore.

**Non e' teorico: succede in tre sessioni su nove.**

| sessione | arco | **buco** | attive | ev/h dichiarati | ev/h sulle ore attive |
|---|---:|---:|---:|---:|---:|
| `bloccodurata5h_20260811` | 6,11 h | **1,13 h** | 4,98 h | 2,3 | **2,8** |
| `bloccosolo_20260810` | 0,38 h | 0,14 h | 0,25 h | 10,4 | **16,1** |
| `bloccoduepersone_20260810` | 0,35 h | 0,14 h | 0,21 h | 0,0 | 0,0 |
| | **14,98 h** | **1,41 h** | **13,57 h** | **11,1** | **12,2** |

Il buco piu' grande e' **uno solo**, ed e' netto: nella sessione di durata
dell'11 agosto le finestre si fermano alle **16:03:30** e riprendono alle
**17:11:12**. **4.062 secondi**, un'ora e otto minuti, nel mezzo della
seconda sessione piu' lunga del lavoro. L'intervallo mediano fra due finestre,
in quella stessa sessione, e' **0,281 s**.

**E il riepilogo non lo registra.** `riepilogo.json` di quella sessione
dichiara:

```
durata_h            4.991      <- il tempo in cui ha davvero deciso
tempo_effettivo_h   4.986
stalli              1
stallo_totale_s     20.0       <- venti secondi, contro 4.062 misurati
```

I 4.062 s **non compaiono da nessuna parte** come stallo o sospensione: il
riepilogo registra 20 secondi. La sessione dura 6,11 ore di orologio e ne
lavora 4,99, e le due grandezze convivono nel file senza che nulla dica dove
sia finita la differenza. `fps_medio` 6,11 e' calcolato sul tempo **effettivo**
(109.814 fotogrammi / 4,986 h), quindi e' corretto: e' la durata a essere
riportata in due modi che non si sommano.

**Perche' conta per il testo.** Sono i numeri del **punto 9 della mail al
relatore**. Le 14,98 ore comprendono 1,41 ore di cecita', quindi il tasso di
allarme e' sottostimato del **10%**: 11,1 eventi/ora diventano **12,2** sulle
ore in cui il sistema guardava davvero. E riguarda anche il **punto 10**, dove
la prova di durata viene presentata come verifica delle sospensioni: qui una
sospensione di un'ora e otto minuti c'e' stata e non e' stata contata.

**Il fattore 44,8 NON e' toccato.** E' il rapporto fra finestre ed eventi, e
il denominatore si semplifica: 496/11,1 sulle ore totali, 547/12,2 sulle ore
attive, **44,8 in entrambi i casi**. L'affermazione centrale della mail regge;
si muove solo il valore assoluto.

**Intervento previsto.**

1. `analizza()` deve calcolare le **ore attive** --- l'arco meno la somma
   degli intervalli oltre una soglia --- e usarle come denominatore,
   dichiarando quante ore ha scartato.
2. Il buco va **stampato**, non dedotto: una sessione con un'ora di cecita' e
   una senza non sono la stessa misura, e oggi si presentano identiche.
3. Il registratore deve contare come stallo anche le interruzioni lunghe:
   4.062 s registrati come 20 e' un difetto di contabilita' della salute, non
   dell'analisi.

**Verificato con:** `pipeline/eventi_sessioni.py` -> 496 finestre/ora, 11,1
eventi/ora, fattore 44,8 su 14,98 h (i valori della mail, riprodotti);
`numpy.diff` sui `t_unix` delle nove sessioni -> 1,41 h in intervalli oltre i
60 s, di cui 4.062 s in un unico salto 16:03:30 -> 17:11:12; ricalcolo sulle
ore attive -> 547 finestre/ora, 12,2 eventi/ora, fattore 44,8.

**Collegamenti:** [EXP-041](EXPERIMENTS.md#exp-041),
[EXP-024](EXPERIMENTS.md#exp-024), [ISS-165](#iss-165)

---

<a id="iss-166"></a>
### ISS-166 — Un pacchetto non dichiara da quale dataset e' stato addestrato, e non c'e' modo di riconoscere quello del relatore

**Trovata:** 2026-09-10 · **Gravita': media** · **Stato: APERTA**

`pipeline/esporta_board.py` accetta `--csv` e lo usa (`riga 146`,
`df = carica(a.csv, camera=a.camera)`), ma **non lo scrive in
`metadata.json`**. Nessuno dei tre pacchetti presenti sul disco dice da dove
viene:

| pacchetto | creato | feature set | colonne | **CSV sorgente** |
|---|---|---|---:|---|
| `deploy_board/` (installato) | 09-09 19:40 | DTWH | 13 | non dichiarato |
| `deploy_board/pacchetto_dtw12/` | 09-09 11:27 | DTW | 12 | **non dichiarato** |
| `deploy_board/pacchetto_installato_20260909_1018/` | 09-09 10:18 | DTWH | 13 | non dichiarato |

Che il pacchetto installato venga da `feature_v5_omnifall.csv` si sa **solo
dal CHANGELOG**, cioe' da una frase scritta a mano accanto al file, non dal
file. Per gli altri due non si sa affatto.

**Perche' blocca una cosa concreta.** Il piano per rileggere le sessioni di
agosto prevede un ripiego esplicito: *se v5 non funziona, si usa la
configurazione data al relatore, cioe' `feature_v2_omnifall.csv`*. Quel
ripiego **non e' eseguibile**, perche' non esiste modo di stabilire se un
pacchetto sia quello: `pacchetto_dtw12` ha il feature set giusto (DTW a 12
colonne, come nella mail) ma e' stato creato il 9 settembre, quando sul disco
c'erano gia' v3, v4 e v5.

I tre pacchetti dichiarano lo **stesso** `n_finestre_train` (12.357) e
`n_positive_train` (595), quindi il conteggio non discrimina: le versioni del
dataset condividono soggetti e riprese, e producono lo stesso numero di
finestre. **Non c'e' nessun campo che li distingua.**

E' lo stesso difetto di [ISS-159](#iss-159) --- il file di selezione non
pinnato --- su un altro artefatto: un parametro che governa il risultato e non
viene registrato insieme a esso.

**Intervento previsto.**

1. `metadata.json` deve portare **nome, dimensione e impronta sha256 del CSV
   sorgente**, scritti da chi addestra.
2. Va aggiunto anche il **file di selezione DTW effettivamente letto**
   ([ISS-159](#iss-159)): sono i due ingressi che decidono quali colonne
   entrano e in quale ordine.
3. Per i tre pacchetti gia' esistenti la provenienza va **ricostruita o
   dichiarata ignota**. Se serve la configurazione del relatore, la via
   sicura e' **riesportarla** da `feature_v2_omnifall.csv`, non fidarsi di
   `pacchetto_dtw12`.

**Verificato con:** lettura dei tre `metadata.json` --- nessun campo contenente
`csv`, `sorgente` o `dataset` oltre a `frame_step_dataset`;
`pipeline/esporta_board.py:146` usa `a.csv` e non lo propaga nel metadato.

**Collegamenti:** [ISS-159](#iss-159), [ISS-156](#iss-156),
[ISS-154](#iss-154)

---

<a id="iss-165"></a>
### ISS-165 — La scelta della cartella delle sessioni e' tutto-o-niente, e cancellare i duplicati farebbe sparire undici sessioni su dodici in silenzio

**Trovata:** 2026-09-10 · **Gravita': alta** · **Stato: APERTA**

`pipeline/eventi_sessioni.py`, `_dove_sono_le_sessioni()`:

```python
locale = os.path.join(RADICE, 'risultati', 'sessioni')
if elenco_punteggi(locale):
    return locale
return os.path.join(os.path.dirname(RADICE), 'DIP_PROJECT', 'sessioni_reali')
```

**Basta UNA sessione nella cartella locale perche' il progetto storico non
venga mai guardato.** La scelta e' fra le due cartelle, non fra le due
collezioni: non c'e' unione, e non c'e' nessun controllo che il numero di
sessioni sia quello atteso.

**Come e' emersa.** Ripulendo i duplicati. Delle tredici sessioni in
`risultati/sessioni/`, dodici sono un duplicato verificato del progetto
storico --- **60 file confrontati, 60 md5 identici, nessuno assente** --- e una
sola, `20260906/notte_20260906_1523/`, esiste **soltanto** qui: e' la prova di
durata di 4,59 ore, cioe' il **punto 10** della mail al relatore, e ha
`fps_medio` 7,2646, il valore comunicato come 7,26.

Cancellare i quattro mesi di agosto perche' duplicati --- che e' la cosa
ovvia da fare --- lascerebbe la cartella locale **non vuota**, quindi il
ripiego non scatterebbe:

| | sessioni viste da `elenco_punteggi` |
|---|---:|
| oggi | **13** |
| dopo aver cancellato i duplicati | **1** |

Lo script non solleverebbe nulla: stamperebbe un blocco invece di tredici. E i
numeri che ne dipendono sono quelli del **punto 9 della mail** --- 496
finestre/ora contro 11,1 eventi/ora, rapporto **44,8** --- che diventerebbero
la statistica di una sessione sola.

**E' lo stesso modo di sbagliare di [ISS-140](#iss-140)**, che questo stesso
file cita nella docstring di `elenco_punteggi`: *«lo script stampava sette
blocchi invece di otto e nessun errore»*. La correzione di allora ha
insegnato al codice a riconoscere un secondo schema di nomi, ma non gli ha
insegnato a **dire quante sessioni si aspetta**.

**Intervento previsto.**

1. `_dove_sono_le_sessioni()` deve **unire** le due sorgenti, non sceglierne
   una, deduplicando per nome di sessione e dichiarando da dove viene ciascuna.
2. Il numero di sessioni attese va **scritto e verificato**: se ne trova meno,
   si ferma. Un conteggio che cala in silenzio e' esattamente cio' che
   ISS-140 aveva gia' prodotto una volta.
3. Solo dopo si possono cancellare i duplicati.

**Verificato con:** `elenco_punteggi(SESSIONI)` -> **13** sessioni, sorgente
`risultati/sessioni`; confronto md5 ricorsivo fra
`risultati/sessioni/2026081[0-3]` e `DIP_PROJECT/sessioni_reali/2026081[0-3]`
-> 60 file, 60 identici, 0 diversi, 0 assenti; `20260906` assente dal progetto
storico.

**Collegamenti:** [ISS-140](#iss-140), [EXP-024](EXPERIMENTS.md#exp-024)

---

<a id="iss-164"></a>
### ISS-164 — Due riferimenti di parita' con contenuto identico dichiarano due versioni di MediaPipe diverse

**Trovata:** 2026-09-10 · **Gravita': media** · **Stato: APERTA**

In radice stanno tre file del 22 agosto --- `board.npz`, `pc.npz`, `pc09.npz`
--- prodotti da `deploy_board/parita_frame.py` sulla clip
`evt_0067_155044`, fotogramma `000_615.23.jpg`, pacchetto DTW a **12** colonne.
Sono i riferimenti della prova di parita' per fotogramma di agosto.

**`pc.npz` e `pc09.npz` sono identici bit per bit e dichiarano due versioni
diverse dello stimatore di posa.**

```
pc vs pc09  landmark identici bit per bit : True
pc vs pc09  valori   identici bit per bit : True
pc dichiara mediapipe 0.10.10  |  pc09 dichiara 0.10.9
```

Il campo `mediapipe` **e' l'unica cosa che rende un riferimento un
riferimento**: dice con quale stimatore i landmark sono stati prodotti, ed e'
il presupposto di qualunque confronto fra le due macchine. Qui uno dei due
valori e' falso --- o il file e' stato rietichettato senza ricalcolare, o il
campo e' stato scritto da una fonte diversa da quella che ha prodotto i
numeri. **Non e' possibile stabilire quale delle due versioni ha prodotto quei
landmark**, e quindi nessuno dei due file puo' essere usato come riferimento.

**E la parita' che quei file misurano non e' zero.** Confrontando `board.npz`
con `pc.npz` sulle dodici grandezze:

| grandezza | scarto |
|---|---:|
| `A2_discesa` | **53,7%** |
| `A3_testa_vel_rel` | 46,0% |
| `A3_hip_vel` | 39,9% |
| `A3_discesa` | 29,9% |
| `A1_discesa` | 26,7% |
| le altre sette | 8,1 -- 11,0% |

L'ordine e' la firma nota di [ISS-106](#iss-106) --- le derivate in cima,
gli integrali in fondo --- ma la **grandezza** e' un altro ordine di
grandezza rispetto al 3,7% misurato il 9 settembre sul pacchetto a 13 colonne
([ISS-161](#iss-161)). Le due misure non sono confrontabili: clip diversa
(`000_615.23.jpg` contro `000_936.87.jpg`), pacchetto diverso (12 contro 13
colonne), e qui una posa mancante su 60 contro nessuna.

**Che cosa questo NON dimostra.** Non dimostra da solo che lo «scarto peggiore
0,00%» della mattina del 9 settembre fosse un confronto del PC con se stesso
--- e' l'ipotesi di [ISS-153](#iss-153), e riguarda altri artefatti. Mostra
pero' che un file di riferimento **e' gia' esistito in due copie che
dichiaravano provenienze diverse a parita' di contenuto**, che e' esattamente
il modo in cui una misura di parita' smette di misurare qualcosa.

**Intervento previsto.**

1. **Il campo `mediapipe` va scritto da chi calcola**, non copiato: se il
   riferimento viene rigenerato, va riletto da `mediapipe.__version__` nello
   stesso processo che produce i landmark.
2. **Il riferimento deve dichiarare anche l'architettura** (`platform.machine()`):
   fra PC e board a divergere non e' la versione ma l'architettura, ed e' il
   campo che oggi non c'e'.
3. I tre file in radice vanno **archiviati o eliminati** con la ragione scritta:
   sono a 12 colonne, il pacchetto installato ne ha 13, e non sono piu' un
   riferimento valido per nulla.

**Verificato con:** lettura diretta dei tre `.npz` --- `np.array_equal` su
`landmark` e `valori` fra `pc.npz` e `pc09.npz` -> `True` su entrambi, campo
`mediapipe` `0.10.10` contro `0.10.9`; scarto relativo per grandezza fra
`board.npz` e `pc.npz` -> tabella qui sopra.

**Collegamenti:** [ISS-153](#iss-153), [ISS-161](#iss-161),
[ISS-106](#iss-106)

---

<a id="iss-162"></a>
### ISS-162 — I trenta secondi di sospensione perdono la seconda caduta, ed e' lo scenario che conta

**Trovata:** 2026-09-09 · **Gravita': alta** · **Stato: APERTA**

Dopo un allarme la regola installata **sospende per 30 secondi**: continua a
decidere e a scrivere i punteggi, ma non emette un secondo evento.

**Perche' la sospensione esiste, ed e' giusto che esista.** Una caduta produce
una raffica di finestre positive consecutive, non una: il rapporto misurato fra
finestre sopra soglia ed eventi e' **44,8**. Senza sospensione una caduta sola
genererebbe decine di allarmi.

**Il costo, misurato il 9 settembre.** Nella sessione
[EXP-039](EXPERIMENTS.md#exp-039) le prime due cadute distano **sei secondi**:

| | | |
|---|---|---|
| caduta 1 | 742--746 s, picco 0,960, 13 finestre | allarme emesso |
| caduta 2 | 748--751 s, picco **0,800**, 9 finestre | **nessun allarme** |

La seconda caduta e' stata **vista benissimo** dal classificatore. Non e' stata
segnalata perche' cadeva dentro la sospensione della prima.

**E' lo scenario domestico che conta di piu'.** Una persona cade, prova a
rialzarsi, ricade: e' il caso in cui il non riuscire a rialzarsi e' il pericolo
vero, ed e' esattamente quello che il presidio contro le raffiche cancella.

**Il parametro non e' mai stato analizzato.** Come K e M ([ISS-160](#iss-160)),
i 30 secondi sono un valore ereditato: non esiste una misura che li giustifichi
ne' un'analisi di sensibilita'. E come K e M sono espressi in un'unita' che
sembra fisica ma non e' stata scelta.

**Vie possibili, nessuna gratis:**

1. **Sospendere la ripetizione, non l'evento nuovo.** Sopprimere solo finche' la
   raffica corrente non si e' chiusa, e riarmare appena il punteggio torna sotto
   soglia per un tempo minimo. Distingue «la stessa caduta che continua» da «una
   seconda caduta».
2. **Accorciare la sospensione** e misurare quanti falsi allarmi in piu' costa
   sulle sessioni gia' registrate --- si fa **senza riaddestrare**, dai
   `punteggi.csv`.
3. **Dichiarare il limite** e basta.

**Attenzione al metodo.** Il relatore ha prescritto di **non** cambiare la
regola di deployment scegliendola sugli stessi dati domestici con cui la si
dimostra (mail dell'8 settembre, punto 9). Questa resta quindi **analisi
offline** finche' non ci sono dati indipendenti.

**Verificato con:** `deploy_board/sessioni/20260909_v5/sess_20260909_v5.csv`,
raffiche a 742,3 e 748,3 s; verita' di riferimento dichiarata sui fotogrammi
annotati.

**Collegamenti:** [EXP-039](EXPERIMENTS.md#exp-039),
[EXP-029](EXPERIMENTS.md#exp-029), [ISS-160](#iss-160),
[DEC-108](DECISIONS.md#dec-108)

---

<a id="iss-161"></a>
### ISS-161 — La parita' per fotogramma confronta per POSIZIONE, e l'ordine delle colonne l'ha gia' resa cieca

**Trovata:** 2026-09-09 · **Risolta:** 2026-09-09 · **Gravita': alta**

`deploy_board/rileva.py`, `verifica_parita_fotogrammi()`: la verifica ricalcola
le grandezze sulla board con `meta['colonne']` --- l'ordine del pacchetto
**installato adesso** --- e le confronta con il riferimento cosi':

```python
va, vb = V[:n], R['valori'][:n]
scale    = np.maximum(np.abs(vb).mean(axis=0), 1e-9)
relativi = np.abs(va - vb).mean(axis=0) / scale
peggiore = int(np.argmax(relativi))
```

**Il confronto e' posizionale.** `R['colonne']` esiste --- `parita_frame.py:174`
lo scrive apposta dentro l'npz --- e **non viene mai letto**. Se l'ordine delle
colonne del pacchetto non e' quello con cui il riferimento fu prodotto, la
colonna *i* della board viene confrontata con una grandezza **diversa**, e il
numero che esce non significa niente.

**Come e' saltata fuori.** Installando il pacchetto v5/DTWH sulla board il
9 settembre. Fra il pacchetto delle 10:18 e quello delle 19:40 cambiano due
grandezze su tredici --- `A2_angolo_tronco` -> `A2_testa_rel_y` e
`A3_ginocchia_rel_y` -> `A3_caviglie_rel_y` --- e con esse **l'ordine di
quattro posizioni**:

| indice | pacchetto 10:18 | pacchetto v5 19:40 |
|---:|---|---|
| 5 | `A3_ginocchia_rel_y` | **`A3_escursione`** |
| 6 | `A3_escursione` | **`A3_caviglie_rel_y`** |
| 7 | `A3_hip_vel` | **`A3_percorso`** |
| 8 | `A3_percorso` | **`A3_hip_vel`** |

Esito della verifica di avvio, stessa board, stessa clip, stesso motore
(impronta `e4c0d354...` identica), stesso riferimento:

| pacchetto | esito |
|---|---|
| 10:18 (ordine del riferimento) | `A3_hip_vel` al **3,7%** |
| v5 19:40 (ordine diverso) | `A3_escursione` al **5807,4%** |

Il 5807% non e' una divergenza fra le due macchine: e' `A3_escursione`
confrontata con `A3_ginocchia_rel_y`. Deterministico, ripetuto due volte con
lo stesso valore.

**Perche' e' grave.** Il Capitolo 5 chiama questa verifica «la sola che
intercetterebbe [ISS-106](#iss-106)». Nella direzione sbagliata sbaglia in modo
appariscente e si nota; **nella direzione giusta puo' tacere**: se due colonne
scambiate hanno per caso valori simili, il confronto passa e la verifica
dichiara una parita' che non ha misurato. E' lo stesso modo di sbagliare di
[ISS-139](#iss-139) e di [ISS-159](#iss-159) --- due copie che devono essere
d'accordo, e nulla che sollevi un errore.

**RISOLTA il 2026-09-09**, `deploy_board/rileva.py`. L'allineamento e' ora
**per nome**: le colonne comuni vengono riordinate, quelle che il riferimento
non ha sono dichiarate e **non confrontate**, e se le comuni sono meno di due
la verifica si dichiara **non eseguita** invece di «superata». Se il
riferimento non porta i nomi --- quelli anteriori a [ISS-153](#iss-153) --- si
ripiega sulla posizione, ma solo a parita' di larghezza.

La stampa dice ora **quanto diverge ciascuna grandezza**, non solo la peggiore:
un unico numero non distingue un motore diverso da una sola derivata rumorosa.

Con il correttivo, il pacchetto v5 da' **esattamente lo stesso profilo** del
pacchetto 10:18 --- `A3_hip_vel` al 3,70% --- e le due colonne nuove compaiono
come «non nel riferimento, NON confrontate». Il 5807% era interamente
l'artefatto posizionale.

**E il 3,7% e' una misura vera, non un difetto.** Confrontando direttamente i
landmark della board con quelli del riferimento sulla stessa clip:

```
landmark  board (60, 29, 3)   riferimento (60, 29, 3)
  identici bit per bit : False
  differenza massima   : 8,19e-02
  differenza media     : 1,21e-03
  coordinate diverse   : 5.219 su 5.220  (99,98%)
```

**MediaPipe 0.10.9 su aarch64 non produce gli stessi landmark di MediaPipe
0.10.9 su x86.** E lo scarto per grandezza si ordina esattamente come ci si
aspetta se la causa e' quella:

| grandezza | scarto | che cos'e' |
|---|---:|---|
| `A3_h_pavimento` | **0,000%** | statica |
| `A3_escursione`, `A2_percorso`, `A1_escursione` | 0,41-0,58% | integrali, che mediano |
| `A2_discesa`, `A3_percorso`, `A1_percorso` | 1,1-1,7% | |
| `A3_testa_vel_rel`, `A1_discesa`, `A3_discesa`, `A3_hip_vel` | 2,4-3,7% | **derivate**, che amplificano |

Le derivate stanno in cima e le statiche a zero: e' la firma di una piccola
differenza nei landmark propagata attraverso le formule, non di un motore
diverso --- l'impronta di `geometry.py` del resto coincide. **E' [ISS-106](#iss-106)
misurata**, cioe' proprio cio' che questa verifica esiste per intercettare.

**Che cosa ne discende per [ISS-153](#iss-153).** Lo «scarto peggiore 0,00%»
registrato la mattina del 9 settembre **non puo' essere stato misurato fra PC e
board**: con landmark diversi al 99,98% le derivate non possono coincidere. Le
due macchine non erano due. Va ricontrollato come e' stato prodotto quel
numero, e finche' non lo si sa non va citato.

**Verificato con:** `rileva.py --parita` sulla board dopo il correttivo ->
`A3_hip_vel al 3.7%` con la ripartizione per grandezza e le due colonne nuove
dichiarate non confrontate; confronto diretto dei landmark sulla stessa clip
(60 fotogrammi, 29 punti, 3 coordinate).

**Verificato con:** `rileva.py --parita` sulla board 192.168.1.20, quattro
esecuzioni --- due col pacchetto v5 (5807,4%, identico), una col pacchetto
10:18 (3,7%), e la parita' sulle **finestre** sempre a **0,000e+00**. Lettura di
`deploy_board/rileva.py` (`verifica_parita_fotogrammi`) e
`deploy_board/parita_frame.py:118,173-174`.

**Collegamenti:** [ISS-159](#iss-159), [ISS-153](#iss-153), [ISS-139](#iss-139),
[ISS-106](#iss-106)

---

<a id="iss-160"></a>
### ISS-160 — K-su-M e' una durata travestita da conteggio, e dipende dal sottocampionamento

**Trovata:** 2026-09-09 · **Gravita': media** · **Stato: APERTA**

`src/dati.py:275-283`: l'etichetta di finestra viene calcolata su
`lab = t[COL_LABEL]` dove `t = tratto.iloc[::step]`, cioe' **sul flusso gia'
sottocampionato**. K e M contano quindi campioni, non fotogrammi originali, e
un campione dura `step / FPS_DATASET` secondi.

Con `step = 2` e 18 fps, `K_CADUTA = 5` e `M_BLOCCO = 8` significano:

> servono **0,56 s** di caduta dentro una finestra di **0,89 s**

**Il problema.** Se il sottocampionamento cambia --- ed e' la correzione che
[ISS-158](#iss-158) mette sul tavolo per allineare la board --- gli stessi K e
M cambiano significato senza che nessuno li tocchi:

| `step` | cadenza | K = 5 campioni | M = 8 campioni |
|---:|---:|---:|---:|
| 2 | 9,0 fps | 0,56 s | 0,89 s |
| 3 | 6,0 fps | **0,83 s** | **1,33 s** |

Passare a `step = 3` renderebbe il criterio **il 50% piu' severo** come effetto
collaterale, e l'insieme delle finestre positive cambierebbe per una ragione
che nessuno ha deciso.

**Il criterio in se' e' sano** --- «abbastanza evento dentro la finestra» e'
piu' robusto sia di «l'evento intero» sia di «almeno un fotogramma» --- e con
una caduta mediana di 3,08 s chiedere 0,56 s significa chiedere il 23% della
finestra. **Quello che va cambiato e' l'unita'**: K e M vanno espressi in
secondi e convertiti in campioni alla cadenza in uso, come gia' fatto per gli
integrali ([ISS-148](#iss-148)).

**Aggravante gia' dichiarata.** `config.py` scrive dei propri valori: *«NON
sono ottimizzate: sono i valori ereditati, ed esiste un'analisi di sensibilita'
da fare»*. Quell'analisi non e' mai stata fatta, quindi il criterio ha
parametri ne' scelti ne' misurati.

**Verificato con:** lettura di `src/dati.py:275-283` e
`src/etichettatura.py:89`; durata mediana delle 104 cadute annotate misurata su
`feature_v5.csv` -> 55,5 fotogrammi = 3,08 s.

**Collegamenti:** [ISS-158](#iss-158), [ISS-148](#iss-148),
[ISS-157](#iss-157)

---

<a id="iss-159"></a>
### ISS-159 — `scelte.txt` viene sovrascritto a ogni analisi DTW, e la foresta dipende dall'ORDINE

**Trovata:** 2026-09-09 · **Gravita': alta** · **Stato: APERTA**

`feature_dtw()` legge `risultati/dtw/scelte.txt`. Quel file **non e' versionato**:
ogni esecuzione di `analisi_dtw.py` lo riscrive. Accanto esistono
`scelte_v3.txt` e `scelte_v4.txt`, ma il codice non li guarda: guarda sempre
`scelte.txt`, qualunque cosa contenga in quel momento.

**Oggi contiene l'ordine di v4**, che differisce da quello di v3 per due
posizioni:

| posizione | `scelte.txt` (oggi) | `scelte_v3.txt` (EXP-023) |
|---:|---|---|
| 8 | `A3_hip_vel` | `A3_percorso` |
| 9 | `A3_percorso` | `A3_hip_vel` |

**Stesse dodici grandezze, ordine diverso --- e il risultato cambia.** La
foresta campiona un sottoinsieme di feature a ogni nodo: a seme fisso, cambiare
l'ordine delle colonne cambia quali feature vengono estratte, quindi cambia il
modello. La candidata l'aveva gia' misurato l'8 settembre --- **F2 da 0,808 a
0,819 scambiando l'ottava e la nona** --- e il difetto si e' ripresentato oggi.

**Il danno accertato.** Rieseguendo la foresta su `feature_v3.csv` con lo
stesso comando di [EXP-023](EXPERIMENTS.md#exp-023):

| | EXP-023 (registrato) | rieseguito il 9 settembre |
|---|---:|---:|
| DTWH | F2 0,866 · TP 1328 · FP 443 · FN 163 | F2 **0,858** · TP 1323 · FP 489 · FN 168 |
| DTW | F2 0,807 · TP 1242 · FP 501 · FN 249 | F2 **0,819** · TP 1252 · FP 445 · FN 239 |

**Le run di EXP-023 non sono riproducibili** con il repository nello stato
attuale, e la ragione non e' il codice ne' i dati: e' un file di dodici righe
che nessuno considerava un parametro.

**E contamina un confronto.** Lo scarto fra l'ordine (0,011) e' dello stesso
ordine di grandezza delle differenze fra architetture che il Capitolo 4
discute, e **maggiore** della differenza fra v3 e v5 (0,005-0,006). Chi
confronta due run prese in giorni diversi puo' stare misurando l'ordine delle
colonne.

**Conseguenza sui numeri gia' scritti.** Il guadagno di `A3_h_pavimento`
riportato come **+0,059** ([EXP-023](EXPERIMENTS.md#exp-023),
[EXP-025](EXPERIMENTS.md#exp-025)) vale **+0,040** a parita' di ordine, su
entrambi i dataset. Le cinque architetture di EXP-025 sono state addestrate il
7 settembre con l'ordine di allora: il loro confronto interno regge, il
confronto con qualunque run successiva no.

**Intervento previsto.**

1. `addestra.py` deve **registrare le colonne effettivamente usate, in ordine**,
   nel `run_*.json`. Oggi il campo `colonne` c'e': va confrontato, non solo
   scritto.
2. La selezione va **pinnata**: `feature_dtw()` deve accettare un percorso
   esplicito, e ogni run deve dichiarare quale file di selezione ha letto.
3. Va **deciso quale ordine e' canonico** --- e la scelta non e' innocua,
   perche' vale 0,011.

**Verificato con:** `run_foresta_tre_classi_DTW_cam1_L22.json` rieseguito su
`feature_v3.csv` il 2026-09-09 -> F2 0,8194, contro 0,807 di EXP-023; diff fra
`scelte.txt` e `scelte_v3.txt` -> due posizioni scambiate, stesso insieme.

**Collegamenti:** [EXP-023](EXPERIMENTS.md#exp-023),
[EXP-025](EXPERIMENTS.md#exp-025), [ISS-138](#iss-138)

---

<a id="iss-158"></a>
### ISS-158 — La finestra di DECISIONE e' ancora un conteggio, e sulla board dura il 39% in piu'

**Trovata:** 2026-09-09 · **Gravita': alta** · **Stato: APERTA**

[ISS-148](#iss-148) e' stata risolta per gli **integrali** e per il `dt` delle
derivate. La **finestra di classificazione** e' rimasta un conteggio, e ai due
lati non e' la stessa cosa.

| | come si costruisce | durata | passo fra i campioni |
|---|---|---:|---:|
| addestramento | `g.iloc[::2]`, poi 22 campioni consecutivi del flusso sottocampionato | **2,44 s** | **0,111 s** |
| board | `buf` di 22 fotogrammi **consecutivi**, nessun sottocampionamento | **3,40 s** | **0,155 s** |

Sulla board `% passo` non sottocampiona: decide soltanto **ogni quanto**
classificare. Il sottocampionamento `FRAME_STEP` non viene mai applicato al
flusso in ingresso.

**Il progetto era coerente, ed e' l'hardware ad averlo rotto.**
`FRAME_STEP = round(FPS_DATASET / FPS_ESERCIZIO) = round(18/9) = 2`: si
sottocampiona il dataset **per farlo somigliare alla board**, che si assumeva
girasse a 9 fps. A 9 fps 22 fotogrammi consecutivi sarebbero 2,44 s, identici.
La board ne fa **6,47**, e la finestra si allunga del **39%**.

**Perche' conta piu' degli integrali.** La finestra di decisione e' cio' che il
modello *vede*: le sei statistiche di aggregazione --- media, deviazione, min,
max, primo, ultimo --- sono calcolate su di essa. Una finestra piu' lunga e piu'
rada contiene una caduta in una proporzione diversa, e le statistiche cambiano
di conseguenza.

**E qui la correzione di ISS-148 non si puo' ripetere.** Per gli integrali
bastava tenere secondi invece di campioni. Qui no: a 6,47 fps il dispositivo
**non puo' produrre** un campionamento a 0,111 s, perche' non ha abbastanza
fotogrammi. Le vie sono tre, e nessuna e' gratis:

1. **Riaddestrare alla cadenza di esercizio**: sottocampionare il dataset in
   modo che il passo sia quello vero della board. Cambia tutti i numeri.
2. **Ricampionare la finestra nel tempo** sul dispositivo, interpolando fra i
   fotogrammi disponibili per ottenere 22 campioni a 0,111 s. Introduce valori
   non osservati.
3. **Dichiarare lo scarto** e misurarne l'effetto, senza correggerlo.

**Non e' stato deciso.** La terza e' il minimo indispensabile: il Capitolo 5
deve dire che la finestra di esercizio dura 3,40 s contro i 2,44 s
dell'addestramento.

**Verificato con:** `pipeline/esporta_board.py:95-101` e `src/dati.py:275`
(sottocampionamento in addestramento); `deploy_board/rileva.py:722, 887, 925`
(nessun sottocampionamento a bordo); cadenza misurata 6,469 fps nella sessione
del 9 settembre ([EXP-035](EXPERIMENTS.md#exp-035)).

**Collegamenti:** [ISS-148](#iss-148), [ISS-147](#iss-147),
[EXP-035](EXPERIMENTS.md#exp-035), [EXP-036](EXPERIMENTS.md#exp-036)

---

<a id="iss-157"></a>
### ISS-157 — EXP-053 giustifica K = 31 confrontando conteggi su due flussi diversi

**Trovata:** 2026-09-09 · **Gravita': media** · **Stato: APERTA**

La scheda che scelse `K_INTEGRALI = 31`
([EXP-053](../../DIP_PROJECT/docs/EXPERIMENTS.md#exp-053), 17 agosto) contiene
un paragrafo intitolato «Perche' non e' un artefatto» che comincia cosi':

> *«A K >= 22 la finestra di accumulazione supera quella di classificazione,
> quindi la grandezza integrale calcolata sul primo fotogramma di una finestra
> guarda fotogrammi precedenti alla finestra stessa.»*

**In tempo non e' vero, ed e' un confronto fra unita' diverse.**

| | conteggio | flusso su cui e' contato | durata |
|---|---:|---|---:|
| finestra di classificazione | 22 campioni a passo 2 | 18 fps | **2,44 s** |
| finestra di accumulazione | 31 fotogrammi | 18 fps | **1,72 s** |

I 22 campioni sono presi a passo 2 sul flusso pieno, quindi coprono 44
fotogrammi; i 31 dell'accumulazione sono consecutivi. **L'accumulazione e' piu'
corta della classificazione, non piu' lunga**, e il confronto «31 > 22» mette
insieme un conteggio sul flusso sottocampionato e uno sul flusso pieno.

**Che cosa NON cambia.** La conclusione di quel paragrafo --- l'informazione e'
solo passata, non c'e' lookahead --- **resta vera**, e per una ragione
indipendente dal confronto: gli integrali si accumulano all'indietro per
costruzione. Il risultato di EXP-053 (K = 31 e' il punto in cui i falsi allarmi
in casa scendono di un fattore 11 a parita' di recall) **non e' toccato**: e'
una misura, non un'inferenza dal paragrafo sbagliato.

**Che cosa cambia.** Il *significato fisico* dichiarato. Chi legge EXP-053
conclude che gli integrali guardino piu' indietro della finestra di decisione,
e che K = 31 corrisponda a 31/9 = **3,44 s**. Sono invece **1,72 s**, e la
prova sta nel codice che scelse K: `scripts/aggiungi_feature_integrali.py:63`,
il commento sopra `K = 9`, dice *«a 18 fps sono ~0,5 s»* --- cioe' 9/18, il
flusso pieno.

**Perche' e' emersa.** Da un'obiezione della candidata, che leggendo EXP-053
aveva ricavato 3,44 s ed era arrivata alla conclusione giusta per la strada
sbagliata: **le grandezze vanno definite sul tempo, non sui fotogrammi.** Il
principio e' corretto ed e' stato applicato lo stesso giorno
([ISS-148](#iss-148)); il numero era il doppio di quello vero.

**Intervento previsto.** Correggere il paragrafo di EXP-053 nel registro
storico e, ovunque il testo descriva gli integrali, esprimere l'orizzonte come
**durata** --- «l'evoluzione recente su un intervallo prefissato, 1,72 s nella
configurazione di riferimento» --- invece che come conteggio di fotogrammi.
Il Capitolo 3 va riletto con questo criterio.

**Collegamenti:** [ISS-148](#iss-148), [ISS-149](#iss-149),
[EXP-053](../../DIP_PROJECT/docs/EXPERIMENTS.md#exp-053)

---

<a id="iss-156"></a>
### ISS-156 — Con l'altezza dal pavimento installata, una clip corta non e' valutabile

**Nota 2026-09-14 --- un numero sbagliato in tesi, corretto.** La tabella di
`tesi/Cap3.tex` che riporta questa misura dichiarava **"253 su 253"** per la
configurazione senza `h_pavimento`. La misura registrata in
[EXP-042](EXPERIMENTS.md#exp-042) e' **422 su 422 --- 100,0%**, e la frase che
introduce la tabella diceva gia' 422: la tabella si contraddiceva con il
proprio testo. La stringa `253` non compare in nessun punto di
`EXPERIMENTS.md` ne' di `ISSUES.md`, quindi non veniva da alcuna misura.
Corretta in `36 su 422` / `422 su 422`.

**Trovata:** 2026-09-09 · **Gravita': alta** · **Stato: APERTA**

`A3_h_pavimento` vale 0,0 finche' la retta del pavimento non e' stimata, e
stimarla richiede **cinquanta osservazioni di persona eretta**. Il presidio
aggiunto il 9 settembre impedisce di decidere finche' la stima non c'e' --- ed
e' giusto, perche' 0,0 e' anche il valore di chi *e'* a terra
([ISS-139](#iss-139)).

**La conseguenza non era stata prevista.** Rileggendo le sei clip di agosto con
la configurazione installata, **quattro su sei non producono nessuna
decisione**: sono diciassette secondi attorno a un allarme, e in quei diciassette
secondi nessuno cammina eretto abbastanza a lungo. La configurazione a tredici
colonne **non e' valutabile su materiale corto**, che e' precisamente il
formato in cui il progetto conserva i propri eventi.

**E il caso peggiore non e' la clip.** In esercizio vale la stessa regola: una
sessione che comincia con la persona **gia' a terra**, o in una stanza dove
nessuno attraversa in piedi, non decide mai. Il sistema resta cieco e lo
dichiara --- il che e' meglio che decidere su una colonna finta --- ma resta
cieco.

**Aggirato, non risolto.** `rendi_clip.py` accetta `--pacchetto` e le clip di
agosto sono state rilette con un pacchetto a **dodici** colonne, che il
pavimento non lo chiede ([EXP-037](EXPERIMENTS.md#exp-037)). E' un aggiramento
per l'analisi fuori linea: non aiuta il dispositivo.

**Le vie possibili, nessuna ancora scelta.**

1. **Stimare il pavimento una volta e conservarlo.** La retta e' una proprieta'
   della TELECAMERA, non della ripresa --- lo dice gia' la docstring di
   `reset_pavimento` --- quindi puo' essere calibrata all'installazione e
   salvata nel metadato. Toglie l'asimmetria fra addestramento ed esercizio, e
   rende le clip valutabili.
2. **Un valore sentinella** distinto da 0,0 per «non stimato», e un modello
   addestrato a riceverlo. Costa un riaddestramento.
3. **Rinunciare a `A3_h_pavimento`** e tornare alle dodici colonne, perdendo il
   guadagno misurato da [EXP-023](EXPERIMENTS.md#exp-023) e
   [EXP-025](EXPERIMENTS.md#exp-025).

La prima e' la sola che non perde nulla, ed e' anche la piu' vicina a come il
sistema verrebbe installato davvero.

**ACCERTATA il 2026-09-10 su tutte le clip disponibili**, non piu' su sei
([EXP-042](EXPERIMENTS.md#exp-042)). Le 422 sequenze salvate attorno agli allarmi
delle quattro giornate di agosto sono state rilette con il pacchetto a dodici
grandezze:

| | v5/DTWH (13 colonne) | DTW (12 colonne) |
|---|---:|---:|
| clip che producono una decisione | 36 --- **8,5%** | **422 --- 100,0%** |

**Nessuna clip scartata.** La causa e' quella descritta: su una clip di una
quindicina di secondi la stima del piano non converge, e senza il riferimento il
presidio scarta ogni finestra. Il difetto **non riguarda l'esercizio continuo**,
dove il riscaldamento si paga una volta all'avvio, ma rende non valutabile
qualunque analisi fuori linea condotta su spezzoni brevi --- ed e' il motivo per
cui le riletture di questo lavoro usano la configurazione a dodici grandezze.

Resta aperta perche' la via 1 --- calibrare il piano una volta all'installazione
e conservarlo nel metadato --- **non e' stata realizzata**: e' la sola che
toglierebbe il limite senza rinunciare alla grandezza.

**Verificato con:** `rendi_clip.py` sulle sei clip dimostrative con il pacchetto
installato -> 4 su 6 «nessuna finestra decisa»; con `--pacchetto pacchetto_dtw12`
-> tutte e sei valutate. Poi su tutte le 422 clip di agosto -> **422 CSV su 422**,
contro 36 su 422 della rilettura del 9 settembre.

**Collegamenti:** [ISS-139](#iss-139), [ISS-155](#iss-155),
[EXP-037](EXPERIMENTS.md#exp-037)

---

<a id="iss-155"></a>
### ISS-155 — Il presidio sul pavimento non bloccava, perche' confrontava una tupla

**Trovata:** 2026-09-09 · **Risolta:** 2026-09-09 · **Gravita': alta**

Il presidio aggiunto la mattina del 9 settembre --- non decidere finche' la
retta del pavimento non e' stimata, perche' `A3_h_pavimento` vale 0,0 e 0,0 e'
anche il valore di chi *e'* a terra --- era scritto cosi':

```python
if serve_pavimento and not motore.pavimento_pronto():
```

`pavimento_pronto()` **non restituisce un booleano**: restituisce la coppia
`(pronto, n_osservazioni)`, e la sua docstring lo dice. Una tupla non vuota e'
sempre vera, quindi `not (False, 3)` vale `False` esattamente come
`not (True, 95)`: **la condizione non poteva scattare in nessun caso.**

**Il danno.** La prima sessione con la configurazione a tredici colonne
([EXP-035](EXPERIMENTS.md#exp-035)) ha deciso su tutte e 297 le finestre,
comprese quelle in cui la colonna valeva 0,0 per assenza di stima, e ha
riportato «0 finestre non decise» --- un numero che sembrava confermare il
presidio e invece ne certificava l'inerzia. **Un difetto che produce il numero
che ci si aspetta e' peggio di uno che produce un errore.**

**Come e' saltato fuori, ed e' la parte che vale.** Non da una rilettura: dal
**visore in diretta** scritto un'ora dopo, che sullo stesso valore faceva
`int(pav)` per scriverlo nel registro e si e' fermato con
`TypeError: int() argument must be ... not 'tuple'`. Lo stesso valore, in un
punto che lo *usava* invece di limitarsi a valutarne la verita', ha smesso di
tacere. E' l'argomento per cui conviene che un valore finisca in un file: un
booleano finto passa il test della condizione e non passa quello della
scrittura.

**Intervento.** La coppia si spacchetta, in `rileva.py` e in `mostra_web.py`:

```python
pav_pronto, pav_oss = motore.pavimento_pronto()
if serve_pavimento and not pav_pronto:
```

**Verificato con:** il visore in diretta sulla board, sessione del 9 settembre
-> `non_decise` = **14** finestre effettivamente scartate prima della stima,
poi `pavimento: true` con 95 osservazioni di persona eretta. A presidio rotto
il contatore restava a zero in ogni condizione.

**Collegamenti:** [ISS-139](#iss-139), [EXP-035](EXPERIMENTS.md#exp-035)

---

<a id="iss-154"></a>
### ISS-154 — Il modello installato e quello misurato non hanno lo stesso positivo

**Trovata:** 2026-09-09 · **Gravita': alta** · **Stato: APERTA**

`pipeline/esporta_board.py` costruisce le etichette del modello che va sul
dispositivo dalla colonna **`classe_omnifall`**: il positivo del compito
«evento» e' la classe `fall` di OmniFall, e lo script si rifiuta di partire se
quella colonna manca.

`pipeline/addestra.py`, che produce **tutti gli F2 del Capitolo 4**, usa
`--modo tre_classi`, cioe' le **etichette manuali** per fotogramma 0/1/2.

**Sono due definizioni diverse dello stesso evento, e non coincidono.** Con i
tempi riallineati ([EXP-034](EXPERIMENTS.md#exp-034)), dei fotogrammi che
l'annotazione manuale chiama caduta OmniFall ne chiama `fall` il **67,2%**: un
terzo no. Il disaccordo non e' di allineamento --- quello e' stato corretto e
non ha spostato questa cifra --- e' di definizione.

**Che cosa ne discende.** L'F2 **0,866** di [EXP-023](EXPERIMENTS.md#exp-023) e
il guadagno di `A3_h_pavimento` su tutte e sei le architetture
([EXP-025](EXPERIMENTS.md#exp-025)) sono misurati su un compito che **non e'
quello su cui il modello installato e' addestrato**. Non li rende falsi: li
rende riferiti a un'altra cosa. Il numero che descrive il dispositivo non e'
stato misurato.

**Perche' esistono entrambe, e nessuna delle due va buttata.** Le etichette
manuali sono le sole che coprono l'intero dataset e distinguono la transizione
dallo stato. Le classi OmniFall sono le sole che separano **sdraiarsi
volontariamente** dal camminare --- 21.444 fotogrammi di `lying`/`lie_down`,
il 18,4% --- ed e' da li' che viene il negativo difficile su cui si misura lo
0,0% di falsi allarmi sui distesi volontari. Senza OmniFall il divano e'
invisibile; senza le etichette manuali la transizione lo e'.

**Che cosa va deciso.**

1. **Misurare il compito installato**: una LOSO sulle etichette OmniFall, per
   avere l'F2 del modello che gira davvero. E' una run.
2. **Oppure esportare sul compito misurato**: addestrare il pacchetto sulle
   etichette manuali, e perdere la misura sul negativo difficile.
3. In entrambi i casi **il Capitolo 4 deve dire quale delle due** produce i
   suoi numeri: oggi non lo dice.

**PERCHE' il 67,2%, misurato il 2026-09-09.** Non e' disallineamento e non e'
un difetto: e' la **durata dell'evento**, e
[DEC-018](../../DIP_PROJECT/docs/DECISIONS.md#dec-018) l'aveva gia' dichiarata
nell'agosto 2026 --- «la nostra fase di caduta dura 3,11 s mediani, il loro
`fall` 2,04 s: la nostra annotazione fa finire la caduta piu' tardi. E' una
differenza di definizione, non un errore».

Rimisurato su `feature_v3_omnifall.csv` con i tempi corretti:

| | segmenti | durata mediana |
|---|---:|---:|
| nostra caduta (`label` = 1) | 104 | 55,5 fotogrammi = **3,08 s** |
| OmniFall `fall` | 100 | 39,5 fotogrammi = **2,19 s** |
| rapporto | | **0,712** |

**L'accordo misurato e' 0,672 contro un rapporto di durate di 0,712**: la quasi
totalita' del disaccordo e' spiegata dal fatto che la nostra annotazione tiene
la caduta aperta piu' a lungo. Il residuo, quattro punti, sono i bordi.

Quindi la scheda **non descrive un errore nascosto** ma una scelta dichiarata
di cui il Capitolo 4 non porta le conseguenze: due compiti diversi, misurati
uno e installato l'altro.

**E' la parte di [ISS-139](#iss-139) che resta aperta dopo l'allineamento
delle colonne: quella scheda annotava gia' che «l'etichettatura delle run
della catena A non e' dichiarata nell'artefatto», e questa e' la stessa
malattia sull'altra catena.

**Trovata** rispondendo a una domanda della candidata --- «perche' OmniFall mi
prendi?» --- che chiedeva conto di un passaggio dato per scontato.

**Collegamenti:** [ISS-139](#iss-139), [ISS-150](#iss-150),
[EXP-034](EXPERIMENTS.md#exp-034), [EXP-023](EXPERIMENTS.md#exp-023)

---

<a id="iss-153"></a>
### ISS-153 — Il riferimento di parita' per fotogramma era calcolato su una clip senza nessuno

**Trovata:** 2026-09-09 · **Risolta:** 2026-09-09 · **Gravita': media**

La verifica di parita' per fotogramma --- quella che il Capitolo 5 chiama «la
sola che intercetterebbe [ISS-106](#iss-106)» --- confronta le grandezze
calcolate sul PC con quelle calcolate sulla board sugli stessi fotogrammi. Il
riferimento sta in `deploy_board/parita_frame_pc.npz`.

**Due difetti, e il secondo e' peggiore del primo.**

1. Il metadato dichiarava che il riferimento valeva su
   `clip_demo/evt_0067_155044`. **Quella cartella non esiste**: le clip
   presenti sono altre sei. Il campo non era letto da niente che potesse
   fallire, quindi nominava un file inesistente da agosto.
2. Rigenerandolo, la clip scelta automaticamente --- la prima in ordine
   alfabetico --- e' risultata avere **60 fotogrammi e zero pose**. Un
   riferimento in cui nessun fotogramma ha una posa e' fatto di **soli zeri**:
   il confronto fra due macchine passerebbe sempre, anche se i due motori
   geometrici calcolassero cose diverse. **Due delle sei clip di prova sono
   cosi'.**

**Intervento.** `parita_frame.py` si rifiuta ora di scrivere un riferimento in
cui nessun fotogramma ha posa, e dice perche'. Scrive inoltre **dentro l'npz**
la clip su cui l'ha calcolato, e `esporta_board.py` la legge da li' invece di
portarsela scritta a mano: la fonte di verita' e' l'artefatto, non un nome nel
metadato.

`esporta_board.py` avverte anche quando `parita_frame_pc.npz` e' **piu'
vecchio di `src/geometry.py`**, perche' un riferimento prodotto da un motore
diverso fa fallire la verifica sul dispositivo per una ragione che non e' una
divergenza vera.

**Verificato con:** il rifiuto scatta su `evt_0001_092019` (0 pose su 60); il
riferimento rigenerato su `evt_0001_132012` da **60 fotogrammi, 60 con posa**;
`rileva.py` all'avvio -> «fotogrammi 60 confrontati su evt_0001_132012, scarto
peggiore **0,00%**».

**Collegamenti:** [ISS-106](#iss-106), [ISS-142](#iss-142), Capitolo 5

---

<a id="iss-152"></a>
### ISS-152 — `tab:esterno` confronta quattro righe misurate su due popolazioni di finestre

**Trovata:** 2026-09-09 · **Gravita': media** · **Stato: APERTA**

La tabella del trasferimento a UR-Fall (Capitolo 4, `tab:esterno`) mette in
colonna quattro configurazioni come se fossero misurate allo stesso modo. Non
lo sono: **la prima riga viene da un file, le altre tre da un altro**, e i due
file non valutano lo stesso insieme di finestre.

| riga | file | finestre | prevalenza | PR-AUC | guadagno | F2 a 0,50 |
|---|---|---:|---:|---:|---:|---:|
| configurazione schierata precedente | `risultati/campo/pr_auc_allineato.json` | **1.075** | **9,4%** | 0,1685 | 1,79x | 0,0345 |
| A3 senza integrali | `risultati/esterno/urfall_foresta_caduta.json` | 884 | 13,0% | 0,4401 | 3,38x | 0,4036 |
| A3 con integrali | idem | 884 | 13,0% | 0,4664 | 3,59x | 0,4793 |
| sottoinsieme DTW | idem | 884 | 13,0% | 0,6597 | 5,07x | 0,6304 |

**Perche' conta.** Il *guadagno* e' il rapporto fra PR-AUC e prevalenza, e le
due prevalenze differiscono del 38%. Confrontare 1,79x con 5,07x significa
quindi confrontare due rapporti calcolati su denominatori diversi. La
direzione del confronto quasi certamente regge --- la differenza fra 0,169 e
0,660 di PR-AUC e' troppo grande per essere spiegata dalla popolazione --- ma
**l'entita' del salto non e' quella che la tabella lascia leggere.**

**Come e' saltata fuori.** Ricostruendo la coda di §4.10.2 nella stesura della
candidata. L'intestazione di quel file segnalava una contraddizione apparente:
la scomposizione fra taratura e capacita' discriminativa da' $F_2 = 0{,}492$
con la **soglia oracolo**, mentre la tabella riporta $0{,}630$ per il
sottoinsieme DTW alla **soglia dichiarata** --- un valore superiore a quello
che dovrebbe essere il limite superiore.

**La contraddizione non c'e'**, ed e' proprio questo difetto a spiegarla: la
scomposizione riguarda la configurazione schierata *in precedenza*, misurata
su 1.075 finestre; lo 0,630 riguarda la configurazione *attuale*, misurata su
884. Sono due misure diverse su due popolazioni diverse, e ora il testo lo
dichiara.

**Intervento previsto.** Rieseguire la configurazione schierata precedente
sulla stessa popolazione delle altre tre --- oppure, che costa meno, dichiarare
nella didascalia che la prima riga proviene da una valutazione distinta, con
finestre e prevalenza diverse. Finche' non e' fatto, **il guadagno di 1,8x non
va sottratto a 5,1x** come se fosse un incremento misurato.

**Non ancora fatto:** la scomposizione fra taratura e capacita' discriminativa
**non esiste per la configurazione attuale**. Esiste solo per quella
precedente. Il testo lo dichiara, ma resta un numero che manca.

**Verificato con:** lettura diretta dei due file JSON, 2026-09-09; le cifre
della tabella coincidono con i file riga per riga.

**Collegamenti:** [ISS-110](#iss-110), Capitolo 4 §4.10

---

<a id="iss-151"></a>
### ISS-151 — Il registratore aveva perso il salvataggio delle immagini

**Trovata:** 2026-09-09 · **Risolta:** 2026-09-09 · **Gravita': alta**

`DIP_PROJECT/deploy_board/session_recorder.py`, il registratore di agosto,
salvava una clip di +-10 s attorno a ogni allarme. `deploy_board/rileva.py`,
che lo ha sostituito, **non lo faceva piu'**: nessun `imwrite`, nessun buffer.
Le uniche righe che nominano «clip» servono a *leggere* una cartella per la
verifica di parita'.

**Due conseguenze, entrambe gia' visibili nei dati.**

1. La sessione del 6 settembre non ha **una sola immagine**, e la verifica di
   parita' dai fotogrammi si e' dichiarata non eseguita --- «cartella dei
   fotogrammi non trovata». E' il punto cieco che il Capitolo 5 descrive nella
   sezione sulla parita', e [ISS-147](#iss-147) ci vive dentro.
2. I **quattordici allarmi** di quella sessione non sono verificabili. Senza
   immagini non si puo' dire se fossero falsi positivi: si puo' solo dire che
   il sistema li ha generati --- ed e' esattamente l'osservazione del relatore
   al punto 10 della sua lettera del 2026-09-08.

**Intervento.** Portata da `session_recorder.py` la classe `BufferClip` e la
logica di completamento: 10 s prima e 10 s dopo ogni allarme, a 10 fps,
JPEG qualita' 80, al massimo 150 clip per sessione. Si attiva con `--clip`.
Le immagini restano sul dispositivo.

**Un difetto trovato nel provarlo, e vale la pena scriverlo.** La prima
versione scriveva la clip solo alla scadenza dei 10 s di coda. Provandola su
una clip di **9,7 secondi** il ciclo finiva prima della scadenza: **due
allarmi, zero immagini**. Su una sessione vera si sarebbe perso l'ultimo
allarme di ogni sessione --- e su una prova interrotta a mano, spesso proprio
quello che si voleva guardare. La clip in sospeso viene ora scritta anche nel
blocco `finally`, quindi anche su Ctrl+C.

**Aggiunta nello stesso intervento:** la traccia `--feature` scrive ora anche
le **sei grandezze grezze** che agosto salvava --- `hip_x`, `hip_y` e il
riquadro --- oltre alle trentadue calcolate. Sono quelle da cui si ricava
`h_pavimento`, che il motore della board non calcola: senza, una sessione
nuova permette di valutare meno configurazioni di una di agosto. Con
entrambe, **una sessione diventa rivalutabile con qualunque configurazione**,
che e' la condizione per confrontarle a parita' di soglia e di regola
([ISS-139](#iss-139)).

**Nessuna delle due modifiche tocca una decisione del classificatore:**
scrivono file. La configurazione installata resta quella dichiarata.

**Verificato con:** `rileva.py --video <clip di agosto> --clip ... --feature ...`
sulla clip `evt_0006_092211`, soglia vera 0,50 -> **1 allarme, 81 immagini,
4,0 MB**, traccia a **40 colonne**; con soglia abbassata a 0,15 su
`evt_0001_092019` -> 2 allarmi e la clip di coda scritta correttamente;
`python prove/esegui.py` -> 31 su 31.

**Da tenere d'occhio:** 150 clip da ~4 MB sono ~600 MB. Il registratore di
agosto aveva anche un controllo sullo spazio libero, che non e' stato portato:
il tetto sul numero di clip e' oggi l'unica difesa.

**Collegamenti:** [ISS-147](#iss-147), [ISS-139](#iss-139), Capitolo 5

---

<a id="iss-149"></a>
### ISS-149 — `FPS_DATASET = 18,0` e' un'assunzione mai verificata, e su un terzo delle riprese e' falsa

**Trovata:** 2026-09-08 · **Gravita': alta** · **Stato: APERTA**

`config.py:40` dichiara `FPS_DATASET = 18.0` con il commento *«UP-Fall e'
consolidato a ~18 fps: gli autori hanno omogeneizzato»*. Quel valore entra in
`estrai_feature.py:212` e da li' in **ogni derivata del dataset**, che si
divide per `dt = 1/18`.

**Non era mai stato misurato, e i dati per misurarlo c'erano da sempre**: i
nomi dei fotogrammi di UP-Fall sono timestamp al microsecondo. Misurato su
tutte e 220 le riprese, 116.362 fotogrammi, senza aprire una sola immagine
(`pipeline/fps_dataset.py`):

| | fps |
|---|---:|
| minimo | **14,43** |
| primo quartile | 17,58 |
| **mediana** | **18,09** |
| terzo quartile | 18,67 |
| massimo | **19,63** |
| media / dev.st | 17,81 / 1,23 |

**Settanta riprese su 220 (32%) stanno oltre il 5% da 18,00.** E lo scarto
**non e' rumore: e' sistematico per soggetto.** Le dieci riprese piu' lontane
dal valore dichiarato sono **tutte del soggetto 6**, fra 14,43 e 14,85 fps.

**Perche' e' grave, e non e' un dettaglio di taratura.** La validazione e'
leave-one-subject-out. Un errore sistematico *per soggetto* nelle feature e'
esattamente cio' che il LOSO mette in un fold intero:

| | fps vero | derivate calcolate | K=31 fotogrammi dura |
|---|---:|---:|---:|
| soggetto 6 | 14,43 | **+25%** | 2,15 s |
| mediana | 18,09 | +0,5% | 1,71 s |
| il piu' veloce | 19,63 | $-8$% | 1,58 s |

Le derivate del soggetto 6 sono **sopravvalutate di un quarto** rispetto a
quelle di chiunque altro, perche' il suo intervallo vero fra fotogrammi e' 69
ms e vengono divise per 55.

**C'e' anche il jitter dentro la ripresa.** L'intervallo fra fotogrammi ha
mediana 49,6 ms, nono decile **70,2 ms** e 99mo percentile **159,8 ms**: non e'
una cadenza regolare con una media diversa da 18, e' una cadenza che salta.
Dividere per una costante e' sbagliato anche dentro la stessa ripresa.

**Conseguenza sulla finestra degli integrali** ([ISS-148](#iss-148)): K = 31
fotogrammi non dura 1,72 s ma **fra 1,58 e 2,15 s** a seconda della ripresa. Se
K fosse dichiarato come durata, il conteggio andrebbe da 25 a 34, e **in 151
riprese su 220 (69%) non sarebbe 31**.

**Correzione, in due livelli.**

*Livello 1, una variabile sola:* `estrai_feature.py` ricava l'fps vero di ogni
ripresa dai timestamp e lo passa a `fotogramma()` al posto della costante.
Sistema le derivate, non tocca il motore geometrico, e costa una riestrazione
(95 minuti) piu' un riaddestramento.

*Livello 2:* il buffer degli integrali diventa una **durata** invece di un
conteggio, con eviction per anzianita' come gia' fa il prototipo di
riferimento. Sistema anche [ISS-148](#iss-148) e vale sia in laboratorio sia
sulla board, ma tocca `geometry.py` --- che e' copiato sul dispositivo e
verificato per sha256 --- e obbliga a rigenerare il file d'oro delle prove.

**Il livello 1 va fatto per primo** perche' muove un solo parametro e il suo
esito e' interpretabile.

**FATTO il 2026-09-08, ed e' negativo** ([EXP-033](EXPERIMENTS.md#exp-033)).
`feature_v4.csv` e' stato prodotto con il dt vero per fotogramma. Il difetto
sparisce come previsto --- l'ampiezza delle derivate del soggetto 6 passa da
1,110 a 0,910 --- la selezione DTW **non cambia**, e l'F2 della foresta passa
da **0,819 ± 0,105 a 0,813 ± 0,112**: differenza $-0{,}006$, t = $-1{,}15$
contro un critico di 2,262, **non distinguibile dal caso**. Il fold del
soggetto 6, quello che la correzione doveva aiutare, **peggiora di 0,020**.

La spiegazione e' nelle colonne scelte: delle dodici, **otto sono integrali**
--- che non si dividono per dt --- due sono statiche, e solo due sono
derivate, entrambe in fondo alla classifica DTW. La nona integrale,
`A2_escursione`, e' stata scartata per ridondanza con `A3_escursione`
(r = 0,86). La preselezione aveva gia'
isolato la pipeline dal difetto, ed e' anche il motivo per cui il difetto non
dava sintomi.

**Resta aperta la decisione su quale dataset porti i numeri della tesi**: v4 e'
prodotto da codice corretto, v3 e' quello su cui e' scritto tutto il testo.
Adottare v4 costa il riaddestramento completo e una riscrittura di decimali.

**Il livello 2 e' stato fatto il 2026-09-09** ([ISS-148](#iss-148), risolta):
il buffer degli integrali e' ora una durata con scarto per anzianita', e la
board misura la propria cadenza invece di assumerla. A 18 fps il motore
produce valori identici bit per bit, quindi **questa decisione non cambia**:
resta aperta come prima, e riguarda solo il dt delle derivate.

**Verificato con:** `python pipeline/fps_dataset.py <radice>` su
`DIP_PROJECT/dataset/up_fall/raw` -> 220 riprese, 116.362 fotogrammi, la
tabella qui sopra. Il conteggio dei fotogrammi coincide esattamente con quello
di `feature_v3.csv`, quindi le riprese misurate sono le stesse.

**Collegamenti:** [ISS-148](#iss-148), [ISS-147](#iss-147),
[EXP-022](EXPERIMENTS.md#exp-022), Capitolo 3

---

<a id="iss-147"></a>
### ISS-147 — Le finestre su cui decide la board non sono quelle su cui e' addestrata

**Trovata:** 2026-09-08 · **Gravita': alta** · **Stato: APERTA**

In addestramento `src/dati.py::_tratti_continui` spezza ogni ripresa nei suoi
tratti di **posa valida continua** e costruisce le finestre dentro un tratto
solo. Il commento del modulo lo dichiara: *«ventidue campioni presi a cavallo
di un'interruzione descrivono un movimento mai avvenuto»*. **Nessuna finestra
di addestramento contiene un fotogramma senza posa.**

Sulla board, `deploy_board/rileva.py:658` fa `buf.append(...)`
**incondizionatamente**, e `geometry.fotogramma(None, ...)` restituisce
**zeri su tutte le colonne** quando la posa manca. Le finestre di decisione
contengono quindi righe di zeri, che la distribuzione di addestramento non ha
mai.

**Misurato sulla sessione del 6 settembre**, 120.051 fotogrammi, 35,1% di pose
valide, ricostruendo esattamente le finestre che il buffer ha visto:

| | finestre | quota |
|---|---:|---:|
| totali | 60.015 | |
| tutte con posa, **come in addestramento** | 14.780 | **24,6%** |
| con almeno un fotogramma a zero | 45.235 | **75,4%** |
| con integrali NON riscaldati (corsa < K=31) | 46.376 | **77,3%** |

La quota mediana di fotogrammi con posa dentro una finestra e' **0,00**: piu'
di meta' delle decisioni sono prese su finestre interamente di zeri.

**Il secondo numero e' il piu' grave, perche' viola un contratto scritto.**
`rileva.py:39-42` dichiara: *«Nove delle dodici grandezze sono integrali
accumulati sugli ultimi 31 fotogrammi. Finche' il buffer non e' pieno i valori
non sono affidabili: il sistema non decide, e lo dichiara a schermo»*. La
guardia esiste **solo all'avvio**, per 1,7 s. Ma `fotogramma(None, ...)` chiama
`reset()`, che **svuota il buffer degli integrali a ogni buco di posa**, e la
guardia non viene riarmata: il sistema decide lo stesso. La promessa vale una
volta sola su 60.015.

**Perche' non era emerso.** E' esattamente il punto cieco che il Capitolo 5
gia' descrive nella sezione sulla parita': la verifica di equivalenza parte da
**duecento finestre gia' calcolate**, quindi non percorre mai questo cammino.
La verifica dai fotogrammi, che lo percorrerebbe, in quella sessione **non e'
stata eseguita** --- `riepilogo.json` riporta
`parita_fotogrammi.eseguita: false`, *«cartella dei fotogrammi non trovata»*.

**Che cosa NON tocca.** Le misure di laboratorio del Capitolo 4: la board non
c'entra. E non tocca la causa della discordanza fra laboratorio e casa, che e'
misurata sull'altezza del bacino dei negativi orizzontali e non dipende dai
buchi di posa.

**Che cosa tocca, e va deciso.** I numeri di campo del Capitolo 5 sono prodotti
da uno stream in cui il 75,4% delle decisioni e' fuori distribuzione. Il tasso
di falsi allarmi ne esce probabilmente **sottostimato in modo benigno** --- una
finestra tutta a zeri e' un vettore costante e non ha prodotto allarmi, visto
che la sessione ne conta 14 in 4,59 ore --- ma il **richiamo** e' l'altra
faccia: una caduta ripresa con buchi di posa arriva al classificatore in una
forma che non ha mai visto, e le cinque cadute della sessione dedicata vengono
da una ripresa con **il 25,9% di pose valide**.

**QUANTO VALE, misurato il 2026-09-08** ([EXP-032](EXPERIMENTS.md#exp-032)).
La sessione e' stata riclassificata fuori linea dalla sua traccia per
fotogramma, con lo stesso modello, lo stesso scaler, la stessa soglia e la
stessa regola di allarme, sotto le due regole di finestratura. La
ricostruzione della regola attuale **riproduce la board esattamente** --- 168
finestre sopra soglia e 14 allarmi, gli stessi numeri del riepilogo di quella
sera --- quindi il confronto e' fra due cose confrontabili.

| | decisioni | finestre sopra soglia | allarmi | eventi/ora |
|---|---:|---:|---:|---:|
| come fa oggi la board | 60.015 | 168 | **14** | **3,05** |
| con la finestratura dell'addestramento | 13.639 | 51 | **4** | **0,87** |

**Dieci allarmi su quattordici erano prodotti dal difetto.** Il tasso di falsi
allarmi di quella sessione scende di **3,5 volte**, da 3,05 a 0,87 eventi
all'ora, e la distanza dagli 0,049 di Kangas passa da 62 volte a 18. Non e' un
miglioramento del modello: e' un difetto tolto.

**Il costo in richiamo non e' misurabile, e va detto.** Quella sessione non
contiene cadute. Le cinque cadute stanno nella sessione del 13 agosto, che ha
`punteggi.csv` ma **non** la traccia per fotogramma --- il flag `--feature` non
esisteva ancora --- e da un punteggio non si ricostruisce una finestra. E'
esattamente il limite che `rileva.py` dichiara di se stesso. Correggere il
difetto **puo' costare richiamo**, perche' una caduta ripresa con buchi di posa
produce meno decisioni, e con i dati in archivio non si puo' sapere quanto.

**Da fare, in ordine di costo.**
1. Riarmare la guardia del riscaldamento dopo ogni `reset()`: il sistema non
   decide finche' non ha di nuovo K fotogrammi validi consecutivi. E' una riga,
   e allinea il comportamento al contratto dichiarato.
2. Rifare la verifica di parita' **dai fotogrammi** su una clip con buchi di
   posa, che e' il caso che nessuna verifica ha mai coperto.
3. Dichiarare nel Capitolo 5 che il richiamo di campo e' misurato su uno
   stream con quella quota di pose, accanto all'intervallo gia' riportato.

**Verificato con:** ricostruzione delle finestre dalla traccia per fotogramma
`notte_20260906_1523_feature.csv` con L=22 e passo 2, gli stessi di
`metadata.json` -> tabella qui sopra; `deploy_board/rileva.py:658` e
`src/geometry.py:489-491` letti.

**Collegamenti:** [ISS-106](#iss-106), [ISS-137](#iss-137),
[EXP-031](EXPERIMENTS.md#exp-031), Capitolo 5 `sec:parita`

---

<a id="iss-142"></a>
### ISS-142 — Il registratore della board non salva le immagini, e la docstring dice di sì

**Trovata:** 2026-09-07 · **Gravità: alta** · **Stato: APERTA**

`deploy_board/rileva.py` apre la propria documentazione così:

> *«Nessuna immagine lascia il dispositivo. Le clip attorno agli allarmi, **se
> attivate**, restano su disco locale.»*

**Non esiste alcun modo di attivarle:** `imwrite` non compare nel file, non c'è
un'opzione da riga di comando che le accenda, e nessun fotogramma viene mai
scritto. La frase descrive una capacità che il programma non ha.

Il registratore precedente — `DIP_PROJECT/scripts/session_recorder.py`, quello
delle dodici sessioni di agosto — **le salvava**: una clip di ±10 s attorno a
ogni allarme, con un tetto giornaliero e un `--no-clip` per spegnerle. È con
quelle clip che gli allarmi delle sessioni di agosto sono stati guardati uno
per uno.

### Che cosa costa, ed è già costato

**I quattordici allarmi della prova di durata del 6 settembre non sono
verificabili.** Non esistono immagini di quei momenti, né sul dispositivo né
altrove: restano quattordici punteggi sopra soglia di cui nessuno può dire se
fossero una persona che si sdraiava, un'ombra o davvero una caduta. Il numero
riportabile di quella sessione è il **tasso di eventi**, 3,1 all'ora; chiamarli
falsi allarmi sarebbe un'affermazione senza prova.

**E la terza verifica di avvio non ha potuto girare.** La parità sui fotogrammi
— la stessa clip elaborata dall'immagine in poi sul calcolatore e sulla board,
che è l'unica che intercetta [ISS-106](#iss-106) — si è dichiarata *non
eseguita* per «cartella dei fotogrammi non trovata». Manca perché nessuna
sessione della board ne produce più.

### Perché era andata così, e perché non basta come ragione

La scelta di non scrivere immagini viene da un argomento giusto: la
riservatezza è un pilastro dichiarato del lavoro, e dal prototipo era già stata
tolta una registrazione video continua che lo contraddiceva. **Ma le due cose
non sono la stessa cosa.** Salvare dieci secondi attorno a un allarme, su disco
locale, con un tetto giornaliero, era la soluzione già adottata in agosto e
già discussa: nessuna immagine lascia il dispositivo comunque.

**Il difetto non è la scelta, è lo scarto fra la scelta e ciò che il codice
dichiara.** Chi legge la docstring conclude che le clip esistono e che basta
attivarle, e imposta una prova di dodici ore convinto di poterla poi guardare.

### Che cosa va fatto, in ordine

1. **Portare in `rileva.py` il salvataggio delle clip** di `session_recorder.py`
   — buffer circolare, ±10 s, tetto giornaliero, `--no-clip` per spegnerlo —
   prima della prossima sessione lunga. Senza, ogni sessione futura produrrà
   numeri che non si possono verificare.
2. **Nel frattempo correggere la docstring**, che oggi afferma il falso.
3. Con le clip torna eseguibile anche la parità sui fotogrammi.

**Verificato con:** `grep -c imwrite deploy_board/rileva.py` -> **0**; nessuna
opzione di clip fra i venti argomenti di `--help`;
`session_recorder.py` righe 26 e 255 per il confronto;
`notte_20260906_1523_riepilogo.json` -> `parita_fotogrammi.eseguita: false`.

**Collegamenti:** [ISS-106](#iss-106), [ISS-113](#iss-113),
[EXP-024](EXPERIMENTS.md#exp-024)

---

<a id="iss-139"></a>
### ISS-139 — La tesi dichiara installata una configurazione che sulla board non c'e'

**Trovata:** 2026-09-06 · **Gravita': alta** · **Stato: APERTA, ma la parte
sulle colonne e' chiusa dal 2026-09-09**

> **Aggiornamento 2026-09-09.** La configurazione installata e' ora **DTWH, le
> dodici del DTW piu' `A3_h_pavimento`**, esportata da `feature_v3_omnifall.csv`.
> `python pipeline/audit_board.py` dice **«Nessuna differenza: la board esegue
> cio' che il progetto dichiara»**, dove il 8 settembre ne diceva due. Il
> motore non e' piu' una copia tenuta a mano: `esporta_board.py` lo copia, e il
> pacchetto porta lo schema delle 33 grandezze che `rileva.py` verifica
> all'avvio.
>
> **Con una condizione nuova, e va dichiarata.** `A3_h_pavimento` vale 0,0
> finche' la retta del pavimento non e' stimata --- servono cinquanta
> osservazioni di persona eretta --- e 0,0 e' anche il valore di chi *e'* a
> terra. Il dispositivo **non decide** finche' la stima non c'e', e conta le
> finestre saltate in `finestre_senza_pavimento`. In estrazione il problema non
> esiste, perche' la retta si stima su tutta la telecamera: **e' un'asimmetria
> fra addestramento ed esercizio, ed e' nuova.**
>
> **Resta aperto** cio' che riguarda il testo --- il Capitolo 5 mette in
> grassetto A3i+controesempi con F2 0,953, che appartiene all'altra catena ---
> e [ISS-154](#iss-154), che e' la stessa malattia sull'etichettatura. E
> soprattutto: **niente di questo ha girato sulla board**, spenta il 9
> settembre.

Il Capitolo 3, nel paragrafo che introduce i nomi delle configurazioni, dice:

> *«Le due estensioni sono indipendenti e possono comparire insieme. [...] e'
> su di esse che poggia la configurazione finale del sistema.»*

dove «esse» sono **A3h** --- che aggiunge l'altezza del bacino dal pavimento ---
e **A3i** --- che aggiunge la terna integrale. Il Capitolo 5 riporta la
tabella delle configurazioni e mette in grassetto **A3i + controesempi**, con
F2 **0,953**.

**Sulla board non gira quella configurazione.** `deploy_board/metadata.json`
dichiara:

```
feature_set : DTW
n_colonne   : 12
colonne     : A2_testa_rel_y, A2_discesa, A2_percorso, A1_discesa,
              A3_escursione, A3_discesa, A3_percorso, A1_percorso,
              A3_ginocchia_rel_y, A1_escursione, A3_hip_vel, A3_testa_vel_rel
```

**Nessuna delle dodici e' l'altezza dal pavimento.** E non e' una svista di
selezione: `h_pavimento` **non e' fra le 32 grandezze** che
`src/geometry.py` calcola, quindi il DTW non avrebbe potuto sceglierla
nemmeno volendo. Verificato: `'h_pavimento' in tutte` -> `False`.

Non e' nemmeno un metadato vecchio: `rileva.py` legge `meta['colonne']` e
passa quelle dodici al modello, e la prova di parita' sulle duecento finestre
passa con scarto `0,000e+00`. Se il modello si aspettasse le quattordici
colonne di A3i, le forme non tornerebbero e si fermerebbe.

### Sono due catene diverse, presentate come una

| | catena A | catena B, **installata** |
|---|---|---|
| dove | `DIP_PROJECT`, run del 21 agosto | `DIP_Project_1`, run del 20 agosto |
| grandezze | A3 (10) -> A3h (+`h_pavimento`) -> A3i (+integrali) | 32 -> il DTW ne sceglie 12 |
| `h_pavimento` | **si** | **no** |
| miglior F2 | **0,953** (A3i + controesempi), FN 14, FP 124 | **0,792** (foresta DTW), FN 271, FP 421 |
| dove compare nel testo | Capitolo 5, tabella delle configurazioni | Capitolo 4, confronto fra architetture |

**Il divario di F2 e' 0,161, cioe' quasi il doppio della dispersione fra
soggetti (0,085).** Le due catene non sono confrontabili cifra per cifra ---
l'etichettatura delle run della catena A non e' dichiarata nell'artefatto, e
la catena B usa `tre_classi` con il compito «evento» --- ma sono
**presentate nel testo come un unico percorso**, e non lo sono.

### Perche' e' emersa, e da una domanda giusta

Chiedendosi perche' il sistema confonda «sdraiarsi sul divano» con una caduta.
Il ragionamento era: **l'altezza dal pavimento distingue il divano dal
pavimento a prescindere dalla velocita'**, quindi il modello dovrebbe
riuscirci. E' corretto --- e la risposta e' che quella grandezza il modello
installato non ce l'ha.

Nella catena A l'aggiunta di `h_pavimento` **dimezza i falsi negativi**, da 45
a 22: e' il salto singolo piu' grande di tutta la tabella delle
configurazioni. Poi il motore geometrico nuovo a 32 grandezze e' stato scritto
senza quella grandezza, e nessuno se n'e' accorto perche' i due impianti non
erano mai stati confrontati colonna per colonna.

### Che cosa va deciso

1. **Rimettere `h_pavimento` fra le grandezze del motore** e rifare la
   selezione DTW. La stima esiste gia' in
   `DIP_PROJECT/scripts/aggiungi_altezza_pavimento.py`: adatta una retta ai
   piedi di chi sta in piedi nel video e misura quanto l'anca sta sopra quella
   retta. Richiede almeno cinquanta fotogrammi di persona eretta, e in una
   sessione domestica dove qualcuno sta sdraiato quasi sempre puo' non
   riuscire: va gestito, non ignorato.
2. **Oppure allineare il testo**, dichiarando che la configurazione installata
   e' il sottoinsieme DTW a dodici colonne e che A3h/A3i appartengono
   all'impianto precedente.

La prima e' l'unica che rende vero cio' che il testo afferma. La seconda e'
onesta ma rinuncia al risultato migliore del lavoro.

**Verificato con:** `metadata.json` della board; `'h_pavimento' in` le 32
grandezze di `src/geometry.py` -> `False`; `run_10soggetti.json` per la
catena A; `run_foresta_tre_classi_DTW_cam1.json` per la catena B.

---

**Aggiornamento 2026-09-07: la grandezza e' tornata nel motore ed e' stata
misurata. Paga, e non e' il DTW ad averlo detto.**

Sulle stesse dieci persone, stessa foresta, stessa soglia dichiarata a priori,
solo `feature_v3.csv` al posto di v2:

| | colonne | F2 | richiamo | FN | FP |
|---|---:|---:|---:|---:|---:|
| DTW | 12 | 0,807 ± 0,104 | 0,834 | 249 | 501 |
| **DTW + `A3_h_pavimento`** | 13 | **0,866 ± 0,102** | **0,894** | **163** | 443 |

**I falsi negativi calano del 35% aggiungendo una sola colonna**, ed e' lo
stesso comportamento che la catena A mostrava (45 -> 22). Il guadagno di F2 e'
**+0,059**, cioe' sotto la dispersione fra soggetti (±0,085): sul F2 aggregato
non e' distinguibile, sul richiamo e sul conteggio dei falsi negativi si'.

**Il particolare che va scritto nel testo:** `A3_h_pavimento` e' **19esima su
33** nella classifica DTW e il criterio non l'avrebbe scelta. Serve al
classificatore e non al criterio di selezione --- che misura la separabilita'
di una grandezza **da sola**, mentre l'altezza dal pavimento e' utile
*insieme* alla dinamica, non al posto suo. E' un limite del criterio di
selezione, e va detto la' dove il Capitolo 3 lo presenta.

**Resta aperta la scelta, che ora e' informata invece che teorica:**

1. **installare DTWH sulla board** --- rifare l'export, la prova di parita' e
   una sessione di controllo --- e allora il testo dice il vero;
2. **allineare il testo** dichiarando che l'installato e' il sottoinsieme DTW
   a dodici colonne.

La prima costa una sessione di lavoro sul dispositivo e rende vero il
risultato migliore; la seconda e' gratis e rinuncia a 86 falsi negativi.

**Verificato con:** `run_foresta_tre_classi_DTW_cam1_L22.json` e
`run_foresta_tre_classi_DTWH_cam1_L22.json` del 6 settembre, entrambi con
`--csv feature_v3.csv`; `risultati/dtw/classifica_dtw.csv` per il rango.

**Collegamenti:** [EXP-022](EXPERIMENTS.md#exp-022),
[EXP-023](EXPERIMENTS.md#exp-023), [ISS-138](#iss-138)

**Collegamenti:** [ISS-138](#iss-138), Capitolo 3 §nomi, Capitolo 5

---


<a id="iss-137"></a>
### ISS-137 — Il costo per fotogramma della board e' un terzo di quello dichiarato

**Trovata:** 2026-09-06 · **Gravita': alta** · **Stato: APERTA**

Installato `rileva.py` sulla board e fatta girare la catena completa sulla
telecamera vera, il bilancio del costo per fotogramma esce per la prima volta
da una sessione reale --- che era il punto di [ISS-113](#iss-113). **Non
corrisponde al Capitolo 5.**

| | Capitolo 5 | misurato sulla board |
|---|---:|---:|
| pre-elaborazione | 1,21 ms (3,2%) | 0,25 ms (0,2%) |
| **percezione** | 33,34 ms (88,4%) | **124,26 ms (86,2%)** |
| post-elaborazione | 0,94 ms | 1,35 ms |
| **classificatore** | 2,20 ms (5,8%) | **18,26 ms (12,7%)** |
| **totale** | **37,7 ms = 26,5 fps** | **144,1 ms = 6,9 fps** |
| classificatore per finestra | 4,47 ms | **38,58 ms** |

**La board e' 3,8 volte piu' lenta di quanto la tesi dichiari.**

**Che cosa regge.** Le proporzioni: percezione ~85%, classificatore ~15%.
L'affermazione portante del capitolo --- *il collo di bottiglia e' la
percezione, non la classificazione* --- **resta vera**, e resta vero che
cambiare classificatore non cambia la frequenza di esercizio. Cambia la quota
del classificatore, da 5,8% a 12,7%.

**Che cosa non regge, e perche' il numero sbagliato e' quello in tesi.**
`config.py` dichiara da sempre: *«La board regge ~9 fps con MediaPipe a persona
singola»*, ed e' su quel presupposto che il dataset viene sottocampionato in
addestramento. **6,9 fps con una persona in scena e' coerente con il
progetto; 26,5 fps non lo e' mai stato**, e nessuno aveva mai confrontato i due.

**Un'ipotesi sulla provenienza dei 4,47 ms, da verificare.**
[EXP-019](EXPERIMENTS.md#exp-019) misura il costo per finestra della foresta
**sul calcolatore**: 4,85 ms. Il Capitolo 4 attribuisce **alla board** 4,47 ms.
I due valori distano l'8%, mentre la board misurata ora sta a 38,58 ms, cioe'
8,0 volte piu' lenta. **Sembra un numero del calcolatore etichettato come
numero della board.** All'epoca il controllo di EXP-019 fu letto come una
conferma («compatibile con i 4,47 ms dichiarati»); alla luce di questa misura
la stessa vicinanza e' invece il sospetto.

**L'ipotesi della stanza vuota e' stata verificata, ed era sbagliata.** Le
prime misure erano su stanza vuota, e l'obiezione ovvia era che con nessuno in
scena MediaPipe rilancia il rilevatore a ogni fotogramma invece di seguire una
persona gia' agganciata, quindi costerebbe **di piu'**. Rifatta con un
soggetto in campo, 99,8% di pose valide:

| | stanza vuota | **con una persona** |
|---|---:|---:|
| percezione | 106,65 ms | **124,26 ms** |
| classificatore | 19,07 ms | 18,26 ms |
| **totale** | 126,0 ms (7,8 fps) | **144,1 ms (6,9 fps)** |

**Con una persona in scena costa il 14% in piu', non di meno**: al rilevatore
si aggiunge il modello dei landmark, che a stanza vuota non gira mai. Il
divario con la tesi non si restringe, **si allarga**: da 3,3 a **3,8 volte**.
Il classificatore non cambia fra le due condizioni, come atteso: non dipende
dalla scena.

**Il bilancio consolidato, 2026-09-07.** La prova lunga e' stata fatta:
**4,59 ore** continue con la telecamera collegata, persone che entrano ed
escono, nessuna sospensione della macchina. Il totale si assesta a
**136,65 ms per fotogramma (7,3 fps)**, fra i 126,0 della stanza vuota e i
144,1 con una persona sempre in campo, che e' esattamente dove doveva stare.
**Il divario con la tesi e' quindi 3,6 volte**, non 3,3 ne' 3,8, e la
ripartizione regge: percezione 85,2%, classificatore 14,3%.

Il Capitolo 5 e' stato riscritto su questi numeri il 6 settembre
(`tab:costo_misurato`): la tabella dichiarata e quella misurata stanno una
accanto all'altra, con la discordanza detta per intero.

**Cosa resta, ed e' una cosa sola.** I **4,47 ms per finestra** attribuiti
alla board nel Capitolo 4. La board misurata ne fa **39,04**, e
[EXP-019](EXPERIMENTS.md#exp-019) misura 4,85 ms **sul calcolatore**: la
distanza dell'8% fra i due e' il sospetto, non la conferma. Va deciso se
ritirare quel numero o dichiararlo come misura sul calcolatore.

**Un dato secondario, e va nella direzione giusta:** con una persona che
cammina in scena il punteggio massimo e' stato **0,120**, nessuna finestra
sopra soglia, nessun allarme. Il sistema non si allarma per una persona che
sta in piedi.

**Artefatti:** `~/rileva/prova_1021_riepilogo.json` (stanza vuota) e
`~/rileva/costo_persona_riepilogo.json` (con soggetto) sulla board.

**Collegamenti:** [ISS-113](#iss-113), [EXP-019](EXPERIMENTS.md#exp-019),
[EXP-021](EXPERIMENTS.md#exp-021)

---

<a id="iss-136"></a>
### ISS-136 — Lo stimatore disegna una persona sopra una cyclette, con confidenza 1,00

**Trovata:** 2026-09-06 · **Gravita': alta** · **Stato: APERTA**

Posizionando la telecamera nel soggiorno, con la **stanza vuota**, MediaPipe
Pose ha prodotto una posa completa **sul telaio di una cyclette**: manubrio,
sella, pedali interpretati come tronco e arti. Confidenza dei landmark fra
**0,97 e 1,00**, e **72-76% di fotogrammi «con persona rilevata»** su una
stanza in cui non c'era nessuno.

E' l'estensione di [ISS-134](#iss-134) --- li' lo stimatore passava a
un'**altra persona**, qui aggancia un **oggetto**.

**La conseguenza che conta, ed e' operativa.** Il
[protocollo di sessione](../../DIP_PROJECT/docs/PROTOCOLLO_SESSIONE_REALE.md)
usa la quota di pose valide come criterio per accettare o fermare un blocco:
*«Se `% pose` e' sotto il 50% mentre qualcuno e' in scena, fermare il blocco»*.
Quel criterio intercetta il caso in cui il sistema **non vede nessuno**, ma non
intercetta questo, in cui il sistema **vede qualcosa che non e' nessuno**. Una
stanza vuota con un attrezzo da palestra soddisfa il criterio al 72%.

**Verificato dal vivo, due volte nella stessa sessione.** Con il soggetto
sdraiato a terra e fuori dal bordo basso dell'inquadratura, lo stimatore ha
abbandonato la persona e si e' agganciato alla cyclette; correggendo
l'inclinazione della telecamera, la persona e' rientrata e la posa e' tornata
su di lei, 100% dei fotogrammi. **Non e' un caso limite raro: e' successo alla
prima inquadratura provata.**

**Intervento da valutare, non ancora fatto.** Il criterio di accettazione
dovrebbe guardare **dove** sta la posa e quanto si muove, non solo se c'e':
una posa immobile per minuti nello stesso punto e' un mobile, non una persona.
La serie della posizione dell'anca --- gia' salvata da
`pipeline/escursione_viste.py` per il laboratorio --- e' la grandezza giusta.

**Collegamenti:** [ISS-134](#iss-134), [ISS-106](#iss-106),
[EXP-021](EXPERIMENTS.md#exp-021)

---

<a id="iss-134"></a>
### ISS-134 — Su Camera2 lo stimatore perde chi cade e si aggancia a un astante seduto

**Trovata:** 2026-09-06 · **Gravita': alta** · **Stato: APERTA**

Su `sub01_act01_trial01_cam02`, MediaPipe Pose **abbandona il soggetto nel
momento in cui cade e passa a una persona seduta sullo sfondo**. La
traiettoria dell'anca tracciata lo dice senza margine:

| campioni | classe annotata | anca x | anca y | angolo |
|---:|---:|---:|---:|---:|
| 0-20 | 0, in piedi | 0,513 | 0,41 -> 0,42 | ~89,7° |
| 21-29 | 1, caduta | 0,513 -> 0,501 | 0,42 -> **0,68** | 89,9 -> 82,2° |
| 30 | 1 | *nessuna posa* | | |
| 31-64 | 1 e 2 | **0,870 -> 0,897** | **0,46** | 66,7 -> 84,4° |

Al campione 30 lo stimatore perde il soggetto; al 31 il rilevatore riparte e
aggancia chi e' piu' evidente nell'inquadratura, che e' un astante **seduto**
sulla destra. L'anca salta di 0,37 in orizzontale e **risale** di 0,22 in
verticale: la persona tracciata si rialza nell'istante in cui quella annotata
sta arrivando a terra.

Da li' in poi non torna piu' indietro: **34 campioni su 65, cioe' il 52% della
ripresa, e tutti e ventisei quelli di classe «a terra»**, misurano il tronco
di un'altra persona. Vale 84-88°, che e' l'inclinazione di chi sta seduto.

Sulla telecamera laterale **la stessa caduta e' seguita correttamente per
intero**: l'anca si sposta con continuita' da 0,72 a 0,36 e l'angolo scende da
89,6° a 0,4°. Non e' quindi un difetto dello stimatore in generale: e' quello
che gli succede su questa inquadratura, dove chi e' caduto diventa piccolo e
lontano mentre altre persone restano in piedi o sedute nel campo.

**Come e' venuto fuori.** Guardando la prima resa di `fig_due_camere.png`: nel
pannello in basso a destra lo scheletro era addosso alla persona in maglia
rossa seduta sulla sedia, mentre il soggetto era a terra in basso a sinistra.
Nei numeri non si vedeva --- l'angolo era 87,1° e la confidenza dei landmark
1,00.

**Che cosa mette in discussione.** Il Capitolo 4 spiega il divario fra le due
viste con la compressione prospettica: *«Una telecamera che guarda dall'alto
vede una persona in piedi e una distesa proiettarsi in modo simile:
l'escursione angolare si comprime.»* Su questa ripresa **l'escursione di
Camera2 non e' compressa: e' di un'altra persona.** Le due spiegazioni portano
allo stesso numero e non sono la stessa cosa, e finora e' stata dichiarata solo
la prima.

**Il divario di F2 resta un fatto, ma la sua causa cambia.** I valori 0,857
contro 0,434 sono misurati dal classificatore sulle feature, non da questa
grandezza descrittiva, e non sono in discussione. Il **2026-09-06 e' pero'
stato verificato** che il cambio di persona arriva anche li':
`landmarks_raw_5sog_backup.npz`, che contiene i landmark da cui quelle feature
sono state costruite, ha **3 riprese su 25 con un cambio di persona su
Camera2 e 0 su 24 su Camera1** ([EXP-020](EXPERIMENTS.md#exp-020)).

Nel 12% delle cadute di Camera2 il modello riceve dunque, per la fase «a
terra», le grandezze di un'altra persona: non sta imparando male, sta
ricevendo l'ingresso sbagliato. **Resta un effetto del punto di vista** --- e'
la vista rialzata a far perdere il soggetto --- ma il meccanismo non e' quello
dichiarato nel capitolo.

Sui fotogrammi interi i cambi sono 3 su 25; campionando un fotogramma ogni
tre, come fa EXP-013, sono 6 su 25. **Il sottocampionamento raddoppia le
perdite di aggancio**, quindi la grandezza descrittiva e' misurata in
condizioni peggiori di quelle in cui il sistema lavora.

**Estensione, misurata su dieci soggetti: 0 su 50 su Camera1, 11 su 50 su
Camera2.** Una ripresa non faceva una regola.
`pipeline/escursione_viste.py` conta i cambi di persona su tutte e cento le
riprese con un criterio dichiarato --- spostamento dell'anca fra due campioni
con posa consecutivi oltre 0,45 in coordinate normalizzate, sommando le
componenti --- e salva la serie per campione in
`risultati/laboratorio/escursione_viste_10sog_serie.json`, cosi' che il
criterio si possa cambiare senza rieseguire la stima di posa.

Sulla vista laterale il salto piu' grande di tutte e cinquanta le riprese vale
**0,31**, sotto la soglia: i due gruppi non si sovrappongono, e non e' la
soglia a produrre l'asimmetria.

**Nel frattempo `fig_due_camere.png` non esiste.** La prima resa e' stata
cancellata: mostrava lo scheletro giusto sulla persona sbagliata, ed e'
esattamente il tipo di immagine di cui non si accorge nessuno che sia falsa.
`pipeline/figura_due_camere.py` ha ora una guardia che si rifiuta di disegnare
un istante successivo a un cambio di persona.

**Verificato con:** traiettoria dell'anca sui 65 campioni delle due telecamere
di `sub01_act01_trial01`, stimatore per ripresa -> tabella qui sopra; prima
resa della figura ispezionata a video.

**Collegamenti:** [ISS-133](#iss-133), [ISS-106](#iss-106),
[EXP-013](EXPERIMENTS.md#exp-013)

---

<a id="iss-133"></a>
### ISS-133 — La misura dell'escursione per vista porta lo stato del tracciatore da una ripresa all'altra

**Trovata:** 2026-09-06 · **Gravita': media** · **Stato: APERTA**

`DIP_PROJECT/scripts/check_camera_viewpoint.py:168` crea **un solo** stimatore
di posa e lo passa a tutte e cinquanta le riprese del ciclo (`:178`).
MediaPipe Pose e' un tracciatore: mantiene stato fra una chiamata e la
successiva, e non sa che nel frattempo e' cambiata la sequenza. L'ultimo
fotogramma di una ripresa --- persona a terra --- innesca quindi il primo
fotogramma della ripresa dopo, dove la persona e' in piedi.

E' lo stesso meccanismo di [ISS-106](#iss-106), applicato pero' a un confine
fra sequenze invece che fra architetture.

**Come e' venuto fuori.** `pipeline/figura_due_camere.py` ricalcola
l'escursione della ripresa che disegna e la confronta con il CSV, per non
mostrare un'immagine che misura qualcosa di diverso dalla tabella accanto. Il
confronto e' fallito.

| `sub01_act01_trial01` | stimatore condiviso | stimatore per ripresa |
|---|---:|---:|
| cam01 | 89,57° | 89,57° |
| cam02 | **31,30°** | **29,23°** |

Il valore a stimatore condiviso coincide cifra per cifra con
`exp013_camera_viewpoint.csv` --- min 58,65 e max 89,95 compresi --- il che
identifica la causa senza margine.

**Perche' cam01 non cambia e cam02 si.** Su cam01 l'escursione e' satura: il
tronco passa da 89,59° a 0,02°, e i due estremi stanno agli estremi del campo.
Su cam02 l'escursione e' un terzo, quindi lo stesso spostamento assoluto pesa
di piu' in proporzione: **il 7% su quella sequenza.**

**Che cosa tocca.** La Tabella `tab:escursione` del Capitolo 4 (71,0° contro
35,7°), il rapporto 1,99x, il conteggio 18 su 25 contro 6 su 25, l'intervallo
da 0,39x a 6,21x, e `fig_viewpoint_dist.png`. Tutti questi numeri escono dal
CSV contaminato. **Non tocca** alcuna metrica di classificazione: l'escursione
e' descrittiva e non entra in un addestramento.

**Perche' probabilmente non ribalta la conclusione, e perche' va rifatto lo
stesso.** La direzione dell'effetto e' fuori discussione --- cam01 e' satura
vicino a 90° in diciotto sequenze su venticinque, e nessuno scarto di due
gradi la sposta. Ma il capitolo dichiara valori con una cifra decimale e un
rapporto con due, e quei valori dipendono dall'**ordine** in cui le riprese
sono state elaborate: non sono riproducibili da chi non conosce quell'ordine.

**Intervento in corso.** `pipeline/escursione_viste.py` (nuovo) rifa' la stessa
misura con **uno stimatore per ripresa**, identica in tutto il resto --- un
fotogramma ogni tre, meta' risoluzione, `model_complexity=1`, soglie 0,5, le
due definizioni dell'angolo. Scrive
`risultati/cinque_soggetti/exp013_camera_viewpoint_indipendente.csv`
**accanto** all'originale, che non viene toccato: la differenza fra i due file
e' il dato.

**Fatto il 2026-09-06.** La misura e' stata rifatta su **dieci** soggetti e
non su cinque, perche' i grezzi delle due telecamere esistono per tutti:
il Capitolo 4 riporta ora 74,0° contro 33,2°, rapporto **2,23×**, 30 su 39
contro 8 su 39, e `fig_viewpoint_dist.png` e' rigenerata senza l'avvertenza di
provenienza.

**Aggiornamento 2026-09-07: le due cause sono state separate, e non pesano
allo stesso modo.** Rieseguendo le tre righe di `tab:viste` a dieci soggetti
con e senza le undici riprese contaminate ([EXP-026](EXPERIMENTS.md#exp-026)),
il divario di F2 fra le viste **non si chiude**: 0,334 con tutte le riprese,
0,356 senza. Il cambio di persona falsava la **misura geometrica** --- il
rapporto fra le escursioni --- ma **non e' cio' che rende la vista rialzata
peggiore per il classificatore**, che e' sostanzialmente tutto compressione
prospettica. Il testo puo' quindi dichiarare le due cause **e** dire quale
delle due pesa sul risultato, invece di limitarsi a elencarle. Resta aperta perche' la storia del numero --- tre valori
successivi, $4{,}32\times$, $1{,}99\times$, $2{,}23\times$ --- e' ora nel
testo ma la lettera al relatore va ancora allineata.

**Verificato con:** stessa ripresa elaborata due volte, stimatore condiviso e
stimatore per ripresa -> tabella qui sopra; il primo riproduce il CSV a 0,00°
su entrambe le telecamere.

**Collegamenti:** [ISS-134](#iss-134), [ISS-106](#iss-106),
[ISS-111](#iss-111), [ISS-129](#iss-129)

---


<a id="iss-110"></a>
### ISS-110 — Due versioni divergenti dei capitoli, e i fatti che tornano indietro

**Trovata:** 2026-08-26 · **Gravita': alta** · **Stato: APERTA**

La candidata scrive i capitoli in Overleaf; il repository ne conserva un'altra
versione. Le due divergono, e la fusione avviene a mano.

**Il danno accertato.** La versione Overleaf del Capitolo 2 riportava per
OmniFall «circa 14 ore di registrazioni uniche, 101 soggetti e 29 viste».
Sono i numeri **gia' trovati sbagliati e corretti il 25 agosto**: l'abstract
dichiara quindicimila riprese, ottanta ore, sedici classi. La stessa versione
attribuiva la rassegna skeleton-based a una «review del 2024 con oltre cento
metodi» invece che a `nguyen` (Sensors 23(11):5121, 2023).

Un fatto verificato e corretto e' quindi tornato indietro. E' il modo di
sbagliare piu' pericoloso del progetto, perche' non lascia traccia: il testo
compila, si legge bene, e il numero e' falso.

**Danno secondario.** Dieci chiavi di citazione su dodici non esistono in
`Bibliografia.tex` (`1`, `kangas2015falsealarm`, `scheurer2019aidemoi`,
`mubashir2013survey`, `gutierrez2021vision`, `huang2024skeleton`,
`lin2021openpose`, `martinez2019upfall`, `broadley2018realworld`,
`schneider2025omnifall`). Con `thebibliography` scritto a mano non
compilano come riferimento.

**Aggiornamento 2026-09-08: la divergenza si e' ripresentata, ed e' stata
decisa la copia buona.**

I capitoli su cui la candidata sta lavorando non sono quelli del repository. Il
Capitolo 1 che ha in mano non coincide ne' con `tesi/Cap1.tex` (31 agosto) ne'
con `tesi/Cap1_riordinato.tex` (5 settembre): e' una terza variante, con le
sottosezioni convertite in `\subsection*`. Il suo Capitolo 2 **non esiste in
questo repository**: quello qui presente non contiene neppure le stringhe
«Dispositivi indossabili», «Sensori ambientali», «Livelli di generalizzazione»,
perche' e' la versione appiattita il 25 agosto.

**Che cosa c'e' solo qui, e che si perderebbe copiando l'altra copia sopra
questa:** l'escursione fra le viste a dieci soggetti (2,23x), il costo per
fotogramma misurato (136,65 ms), il fattore fra finestre ed eventi (44,8), il
risultato «controintuitivo» ritirato, `tab:viste`, `tab:latenza_misurata`,
`fig:viste`, `fig:dominio`, le occlusioni rimisurate e la latenza di
laboratorio. Cioe' tutto il lavoro dal 25 agosto a oggi.

**Decisione presa l'8 settembre: la copia autorevole e' il repository.** Le
modifiche di struttura fatte nell'altra copia vanno portate qui, non il
contrario. La prima e' gia' stata portata: la promozione di «Definizione
dell'evento da riconoscere» a sezione.

**Resta aperta** finche' la copia su Overleaf non viene sostituita con questa:
finche' esistono due copie, il difetto puo' ripresentarsi una terza volta.

**Aggiornamento 2026-09-09: le stesure di Cap1 e Cap2 sono state
installate nel repository, e hanno riportato indietro cinque citazioni.**

La direzione decisa l'8 settembre e' stata di fatto invertita: il testo del
Capitolo 1 e del Capitolo 2 e' ora la prosa della candidata, corretta, e non
piu' la riscrittura del repository. L'operazione ha portato con se' cinque
difetti, tre segnalati da `controlla.py` e **due invisibili**, perche' una voce
mai citata non e' un errore per LaTeX: con `thebibliography` scritto a mano
viene stampata lo stesso.

| chiave | che cosa e' successo |
|---|---|
| `gazem` | **rientrata**: e' una delle tre voci ritirate il 26 agosto perche' inventate ([ISS-114](#iss-114)) |
| `fnopi`, `epicentro` | chiavi nuove, non definite in `Bibliografia.tex` |
| `fleming` | persa: era l'unico riferimento clinico del *long lie* |
| `mediapipe`, `blazepose` | perse: il testo dice quale stimatore di posa usa e non lo attribuiva |
| `gomes` | persa da Cap2 |

Tutte e sei sistemate lo stesso giorno; `fnopi` ed `epicentro` verificate sulla
fonte con URL e commento `% VERIFICATO`. Vedi
[CHANGELOG 2026-09-09](CHANGELOG.md).

**Quanto costerebbe fare lo stesso con Cap3, Cap4 e Cap5: misurato, non
stimato.** Le tre stesure restanti sono in `tesi/da_incorporare/`. Rispetto
alla copia del repository perdono:

| | parole | figure che spariscono | tabelle che spariscono | sezioni |
|---|---|---|---|---|
| Cap3 | 9.388 contro 10.246 | `fig:finestra`, `fig:rappresentazioni` | `tab:grandezze`, `tab:landmark`, `tab:stimatori` | `sec:nomi`, `sec:metodoB`, `sec:elenco-grandezze` |
| Cap4 | 9.041 contro 11.770 | `fig:viste`, `fig:dominio`, `fig:configurazioni`, `fig:due_camere` | `tab:alberi`, `tab:cambio_persona`, `tab:errori_attivita`, `tab:richiamo_tipo` | `sec:sei-regole` |
| Cap5 | 9.745 contro 10.766 | --- | `tab:latenza_misurata`, `tab:costo_misurato`, `tab:fps_scena`, `tab:prima_ora`, `tab:scambio` | `sec:frequenza-base`, `sec:prima-ora` |

Le stesure portano anche materiale proprio: Cap4 aggiunge `tab:ordine`,
`sec:loso`, `sec:soglia`, `sec:prauc`, `sec:numerosita`, `sec:calibrazione`,
`sec:normalizzazione`; Cap5 aggiunge `tab:qualita_sessioni`,
`tab:controesempi_cross`, `sec:termico`, `sec:costo`, `sec:limiti-operativi`.

**Il punto che rende la cosa pericolosa:** nessuno di quei rimandi e' usato da
un altro capitolo. Verificato cercando `ref{...}` su tutti i `.tex`: le uniche
occorrenze sono interne al capitolo stesso. Quindi **`controlla.py` non
segnalerebbe nulla** --- niente riferimenti orfani, niente figure mancanti ---
e quel materiale sparirebbe in silenzio, esattamente come sono sparite
`fleming`, `mediapipe`, `blazepose` e `gomes`.

**Decisione sospesa** su richiesta del 9 settembre: fusione, installazione
secca o direzione opposta. Finche' non e' presa, le tre stesure restano in
`tesi/da_incorporare/` e i capitoli del repository non si toccano.

**Contesto che aggrava.** Solo **7 voci su 31** portano il commento
`% VERIFICATO`: `broadley`, `gomes`, `gutierrez`, `kangasreali`, `lin`,
`nguyen`, `omnifall`. Tutte le altre non sono state controllate sulla fonte.

**Intervento previsto.** Una sola copia del testo. Finche' ne esistono due,
ogni fusione va fatta confrontando i numeri contro i commenti `% VERIFICATO`
in `Bibliografia.tex`, mai a memoria. I due numeri di OmniFall e Nguyen sono
ora protetti da un avviso in testa a `tesi/Cap2.tex`.

**Aggiornamento 2026-09-13: il Capitolo 2 e' riconciliato. Restano 3, 4, 5.**

Le copie in gioco erano cinque: `tesi/Cap2.tex` (9 set), `Desktop/tesi/Cap2.tex`
(10 set), `Downloads/Cap2(1)(1).tex` (24 ago) e due archiviate in `_superato/`.
Il diff paragrafo per paragrafo ha dato 10 differenze fra la copia del
repository e quella del 10 settembre; la copia in lavorazione della candidata
era piu' recente di entrambe. `tesi/Cap2.tex` e' stato riscritto su quella,
rimettendo cio' che il repository aveva e la sua copia aveva perso.

L'avviso in testa al file non serve piu' ed e' stato tolto: la copia buona e'
questa, e le citazioni non poggiano piu' sulla memoria.

**Chiavi.** Il capitolo ora usa 11 citazioni, tutte fornite e controllate dalla
candidata: `MU`, `LI`, `GU`, `HO`, `LIN`, `kangasreali`, `bagala`, `upfall`,
`scheurer`, `omnifall`, `broadley`. Le sei non ancora controllate (`nguyen`,
`urfall`, `vira`, `tcnte`, `gcn3stream`, `gomes`) sono state **rimosse**, e le
affermazioni che sostenevano riscritte su `HO`, verificato leggendo il PDF
(IEEE Access 11:92322--92352, open access CC BY): sezioni III.A--III.D per i
classificatori, Tabella 2 per UP-Fall, IV-F.2 per la $F_eta$, IV-G.1 e V-D
per il protocollo. Nessuna affermazione poggia piu' su una chiave assente.

**Correzione registrata.** Durante la revisione `HO` era stata identificata
come Ho 1995, *Random Decision Forests* — la chiave `randomforest`. E' invece
Hoang et al. 2023. Le due collocazioni della candidata erano corrette; le
obiezioni sollevate contro di esse no.

**Cosa resta aperto.** Capitoli 3, 4 e 5 hanno ancora due copie ciascuno.

---

<a id="iss-107"></a>
### ISS-107 — I capitoli 3 e 4 sono suddivisi troppo

**Trovata:** 2026-08-25 · **Gravita': media** · **Stato: APERTA**

Misurato il rapporto fra parole e titoli in ciascun capitolo:

| capitolo | parole | sez. | sottosez. | parole per titolo |
|---|---:|---:|---:|---:|
| 4 Protocollo | 2.976 | 5 | 17 | **135** |
| 6 Deployment | 2.664 | 7 | 7 | 190 |
| 3 Metodologia | 9.408 | 10 | 39 | 192 |
| 1 Contesto | 3.738 | 6 | 11 | 220 |
| 7 Ambiente reale | 4.823 | 11 | 6 | 284 |
| **2 Stato dell'arte** | 2.416 | 5 | 0 | **483** |
| 8 Conclusioni | 2.418 | 5 | 0 | 484 |

Il Capitolo 3 ha **quarantanove titoli** in 9.400 parole; il Capitolo 4 ne ha
ventidue in meno di tremila, cioe' un titolo ogni mezza paginetta.

**Quattro sezioni del Capitolo 4 non hanno testo proprio**: un titolo seguito
immediatamente da un altro titolo. Sono «Sbilanciamento delle classi»,
«Dallo split per video al LOSO», «Normalizzazione stimata sul solo
addestramento» e «La soglia decisionale».

**Il criterio.** Sotto le 250 parole un blocco non giustifica una
`\subsection`: va reso `\paragraph`, che porta un nome ma non una voce
nell'indice. Il Capitolo 2, sistemato il 26 agosto, e' il modello.

**Due casi accertati nel Capitolo 3, da risolvere insieme alla suddivisione.**
La sezione «B --- coordinate scheletriche grezze» conta 90 parole e non e'
una sezione: va assorbita fra le rappresentazioni. Le sottosezioni «Cosa e'
stato rimosso, e perche'» e «Cosa sostituiscono» dicono la stessa cosa in due
punti diversi.

**Intervento previsto** Ridurre il Capitolo 3 da 49 a circa 21 titoli e il
Capitolo 4 da 22 a circa 10, senza togliere contenuto: le sezioni sono tutte
necessarie, e' la gerarchia a essere sbagliata.

---

<a id="iss-106"></a>
### ISS-106 — Lo stimatore di posa non si trasferisce fra architetture

**Trovata:** 2026-08-22 · **Gravita': media** · **Stato: APERTA (accertata, non risolvibile)**

Le stesse clip, elaborate sul PC (x86) e sulla board (ARM) con la stessa
versione di MediaPipe e lo stesso modello, producono grandezze diverse.

La parita' sulle **finestre gia' calcolate** era passata con scarto
`0,000e+00`: modello e scaler si trasferiscono esattamente. La divergenza
nasce prima, nello stimatore di posa, che e' un **tracciatore**: mantiene
stato fra fotogrammi, e uno scarto infinitesimo nella decodifica
dell'immagine si amplifica lungo la sequenza.

| fotogramma | scarto medio sui landmark |
|---:|---:|
| 1 | 0,0001 |
| 11 | 0,0755 |

**Effetto misurato** ([EXP-016](EXPERIMENTS.md#exp-016)): su 56 clip, 55
decisioni identiche e una diversa — una caduta reale che il PC segnala con
punteggio 1,000 e la board non segnala (picco 0,560, l'antirimbalzo a cinque
finestre non scatta).

**Perche' non e' risolvibile.** Non e' un difetto di versione ne' di
configurazione: e' la natura del componente. Le implementazioni delle
operazioni in virgola mobile differiscono fra le due architetture, e un
sistema con stato le amplifica.

**Cosa comporta.**

1. La verifica di trasferimento deve partire dai **fotogrammi**. La prova
   sulle finestre precalcolate e' passata con scarto esattamente zero pur
   mascherando l'unica divergenza reale: e' un punto cieco, non una prova.
2. **Le prestazioni misurate sul PC non sono le prestazioni della board.** Il
   recall va misurato sulla board.
3. L'antirimbalzo amplifica la divergenza: trasforma uno scarto continuo di
   punteggio in una decisione binaria diversa. E' un costo del meccanismo,
   accettato consapevolmente ([DEC-107](DECISIONS.md#dec-107)).

---

## Risolti


<a id="iss-178"></a>
### ISS-178 — `tab:leakage` dichiarava gli iperparametri fissati a priori, ma K e' stato scelto per scansione

**Trovata:** 2026-09-22 · **Gravita': alta** · **Stato: RISOLTA il 2026-09-22**

Il Capitolo 3 elencava **quattro** operazioni che ricavano qualcosa dai dati e
dichiarava, per la terza: «Iperparametri --- nessun dato: fissati a priori,
identici ovunque --- vede il test: no».

**E' falso per un iperparametro, e non uno qualsiasi.** `config.py:108` dice
`K_INTEGRALI = 31   # fotogrammi, ~1,7 s a 18 fps. Misurato in EXP-053`.
[EXP-053](../../DIP_PROJECT/docs/EXPERIMENTS.md#exp-053) del progetto storico si
intitola, testualmente, **«La finestra di accumulazione era scelta, non
ottimizzata — e il valore giusto e' piu' del triplo»**: il valore di partenza
era `K=9`, e 31 e' il risultato di una scansione su cinque lunghezze.

**Da dove vengono i numeri che hanno deciso.** Da due insiemi, ed entrambi
pongono un problema:

1. la colonna «F2 laboratorio» e' misurata **sui fold di prova** del LOSO,
   quindi la scelta di K ha visto i soggetti lasciati fuori;
2. il pareggio fra 31 e 45 e' stato rotto sul **campo**: in laboratorio 45 fa
   meglio (F2 0,987 contro 0,980, FN 3 contro 4), ma a 45 il richiamo sulle
   registrazioni domestiche scende da 4/5 a 3/5. Quel richiamo e' poi riportato
   fra i risultati del Capitolo 5: **e' stato usato per scegliere il parametro,
   e non e' indipendente dal parametro scelto**.

Si aggiunga che la scansione appartiene all'impianto a **cinque** soggetti e
non e' stata ripetuta su dieci, mentre il valore e' stato mantenuto.

**Perche' conta.** E' esattamente il punto che il relatore chiede di dichiarare
esplicitamente: «lo stesso vale per normalizzazione, feature selection,
threshold selection, hyperparameter tuning --- in ogni fold, tutto cio' che
impara qualcosa dai dati deve essere calcolato esclusivamente sul
training/validation set». Il capitolo dichiarava il leakage della selezione DTW
e taceva quello di K, che e' della stessa natura.

**Intervento.** `sec:leakage` rivista:
- il **procedimento corretto enunciato per intero** come sequenza numerata
  (metti da parte s, calcola il criterio sui rimasti, stima la normalizzazione
  sui rimasti, addestra e tara sui rimasti, congela, valuta su s una volta
  sola), con l'ordine sbagliato dichiarato accanto;
- le operazioni passano da quattro a **cinque**, separando gli iperparametri
  del **modello** (fissati a priori, corretti) da quelli della
  **rappresentazione** (K, non fissato a priori);
- nuovo paragrafo «La quarta: K non e' stato fissato a priori», con la
  provenienza dei numeri e la direzione dell'errore;
- il confronto con il parametro vicino che si comporta bene: la lunghezza della
  finestra di classificazione e' stata anch'essa sottoposta a scansione, ma li'
  **si e' tenuto il valore a priori**. Misurare e cambiare non e' come misurare
  e tenere.

`tesi/Cap5.tex`, `sec:finestra-k`: aggiunto il rimando che dichiara
`tab:kappa` per quello che e' --- la misura da cui K e' stato scelto, non una
semplice analisi di sensibilita'.

**Verificato con:** `config.py:108`, EXP-053 del progetto storico,
`risultati/cinque_soggetti/scansione_k_cinque_soggetti.json` (K=45 da' F2
0,9867 contro 0,9796 di K=31: conferma che 31 non ha vinto la scansione di
laboratorio). `python tesi/controlla.py` -> gli stessi 8 problemi preesistenti.

**Misurata il 2026-09-22, e l'esito ribalta l'attesa.**
[EXP-045](EXPERIMENTS.md#exp-045) ha rifatto la scelta dentro ogni fold:
**nove fold su dieci scelgono K = 45**, non 31, e l'F2 medio sale da 0,825
a **0,851**. Il leakage su K **non ha gonfiato le prestazioni: le ha
ridotte** di 0,026. E' la direzione opposta a quella della selezione DTW, ed
e' coerente con EXP-053, dove sul solo criterio di laboratorio 45 batteva
gia' 31. Il testo del Capitolo 3 e' stato corretto: dichiarava la direzione
sbagliata.

**Resta fuori dalla misura** il leakage di campo: la preferenza per 31 si
fonda sul richiamo domestico (4/5 contro 3/5), che il Capitolo 5 riporta poi
come risultato. Separarli richiederebbe cadute diverse da quelle usate per
scegliere, e cinque non bastano a fare due insiemi disgiunti.

**Collegamenti:** [ISS-172](#iss-172), [ISS-174](#iss-174),
[EXP-053](../../DIP_PROJECT/docs/EXPERIMENTS.md#exp-053)

---

<a id="iss-175"></a>
### ISS-175 — `sec:allarme` descriveva l'istante dell'allarme e l'intervallo refrattario al contrario del codice

**Trovata:** 2026-09-22 · **Gravita': alta** · **Stato: RISOLTA il 2026-09-22**

La sezione del Capitolo 3 che definisce la regola di allarme --- quella che il
relatore ha chiesto proprio per rendere interpretabile il Capitolo 5 ---
affermava due cose che il codice non fa.

**1. L'istante dell'evento.** Il testo diceva: «L'inizio dell'evento e'
l'istante della \emph{prima} delle cinque finestre, non della quinta: e' la
scelta che rende confrontabile la latenza». Il codice fa l'opposto.
`deploy_board/rileva.py:1016` e `pipeline/eventi_sessioni.py:127` emettono
l'allarme nell'indice in cui `corsa >= persistenza` diventa vera, cioe' alla
**quinta** finestra. E `pipeline/latenza.py:114` somma esplicitamente
`persistenza_s = (P-1) * cadenza` fra le componenti della latenza, proprio
perche' l'allarme arriva alla quinta.

**Direzione dell'errore:** la dichiarazione **sottostimava** la latenza,
esattamente del termine di persistenza --- 0,997 s dei 3,778 s totali, cioe' il
26,4%, secondo `tab:latenza` del Capitolo 5. Il Capitolo 5 era quindi corretto
e il Capitolo 3 lo contraddiceva.

**2. L'intervallo refrattario.** Il testo diceva che l'evento «si chiude quando
trascorrono 30 secondi senza nuove finestre positive». Nel codice `ultimo` e'
l'istante dell'**ultimo allarme emesso**, non dell'ultima finestra positiva:
una raffica che resti sopra soglia oltre i trenta secondi produce una seconda
segnalazione allo scadere dell'intervallo, e poi una ogni trenta secondi. Non
e' un dettaglio: il falso positivo dominante del lavoro e' uno **stato** che
dura --- una persona distesa su un divano --- e con la regola vera il conteggio
degli eventi dipende in buona parte dalla durata della sospensione.

**Intervento.** `sec:allarme` riscritta per intero. Nuova `tab:allarme` con le
sei voci chieste dal relatore, una per riga: soglia, positivi consecutivi,
istante dell'allarme, fusione degli eventi, intervallo refrattario, fine
dell'evento --- quest'ultima dichiarata **non definita**, perche' la
segnalazione e' un istante e non un intervallo, e il codice non calcola alcuna
chiusura. Aggiunti tre paragrafi: perche' l'allarme e' la quinta finestra e che
cosa costa; perche' una raffica lunga non e' una segnalazione sola; e le **due
contabilita'** --- falsi positivi per finestra contro allarmi per ora --- che il
relatore indica come uno dei messaggi forti della tesi, con la ragione per cui
servono entrambe (il conteggio degli eventi e' confrontabile con la letteratura
ma dipende dalla sospensione; la quota di tempo sopra soglia non ne dipende ma
non e' confrontabile con nulla).

**Verificato con:** lettura di `rileva.py:1016`, `eventi_sessioni.py:114-130` e
`latenza.py:96-135`; confronto con `tab:latenza` del Capitolo 5, che era gia'
coerente con il codice. `python tesi/controlla.py` -> gli stessi 8 problemi
preesistenti.

**Collegamenti:** [ISS-172](#iss-172), [DEC-108](DECISIONS.md#dec-108)

---

<a id="iss-176"></a>
### ISS-176 — Tre voci del protocollo di campo erano rimaste «da completare»

**Trovata:** 2026-09-22 · **Gravita': bassa** · **Stato: RISOLTA il 2026-09-22**

`tab:campo` del Capitolo 5, scritta per rispondere alla richiesta del relatore
di descrivere con precisione la validazione domestica, portava tre righe
marcate \emph{da completare}: partecipanti, dimensioni degli ambienti, ore di
presenza nel campo di vista.

**Esito della ricerca.** Le prime due **non esistono in alcun artefatto**: non
sono nei `riepilogo.json`, non sono nel LEGGIMI delle sessioni, non sono nei
registri. Sono state dichiarate non rilevate, con la nota che il protocollo
avrebbe dovuto raccoglierle.

**La terza e' stata sostituita, non riempita.** Le ore di *presenza* della
persona richiederebbero un'annotazione della presenza, che non e' stata fatta.
Cio' che si puo' contare sono le ore con **posa valida**, calcolate dai dodici
`riepilogo.json` come somma di `durata_h * quota_pose`: **7,45 ore su 9,58**,
cioe' il 77,8%. Il testo dichiara che e' un limite **inferiore** della presenza
e non una sua stima --- con un'inquadratura sbagliata la persona c'e' e la posa
no --- e cita il 10 agosto, dove la quota di pose valide va dallo 0,6% al
39,8%.

**Verificato con:** somma ricalcolata sui dodici `riepilogo.json`; il totale
9,58 h coincide con le «circa 9,6 ore» gia' dichiarate nel capitolo.

---

<a id="iss-177"></a>
### ISS-177 — Il LEGGIMI delle sessioni dichiarava 47,8 dove il valore calcolato e' 44,8

**Trovata:** 2026-09-22 · **Gravita': bassa** · **Stato: RISOLTA il 2026-09-22**

`risultati/sessioni/LEGGIMI.md` riportava «un fattore misurato in **47,8**» fra
finestre sopra soglia ed eventi. Il valore prodotto da
`pipeline/eventi_sessioni.py` e conservato in
`risultati/campo/eventi_sessioni.json` e' `fattore_sovrastima: 44,753`, ed e'
il 44,8 che il Capitolo 5 riporta in tre punti e che `CLAUDE.md` dichiara.
Corretto nel LEGGIMI. Nessun numero della tesi dipendeva dal valore sbagliato.

---

<a id="iss-172"></a>
### ISS-172 — Il Capitolo 3 dichiarava una soglia scelta sul validation, ma e' fissa

**Trovata:** 2026-09-22 · **Gravita': alta** · **Stato: RISOLTA il 2026-09-22**

Il Capitolo 3 dichiarava, in `tab:leakage` e nella prosa di `sec:leakage`, che
la soglia di decisione e' **scelta sul soggetto di validation** e poi applicata
al test una volta sola --- «e' la ragione per cui un soggetto di validation
esiste». Il Capitolo 4 chiudeva la sua sezione sulla soglia adottandone una
**fissa a 0,50**, e tre paragrafi dopo citava alla lettera la frase suggerita
dal relatore («for each LOSO fold, the decision threshold was selected using
only training/validation data»), che descrive la procedura **scartata**.

**Che cosa fa davvero il codice.** `pipeline/addestra.py:185` espone `--soglia`
con valore predefinito **0.5**, e `soglia_fissa=None if a.soglia < 0 else
a.soglia`: la scelta sul validation avviene solo con `--soglia -1`, che nessuna
delle run riportate usa. Nei log di campagna la colonna della soglia vale
**0.50 su tutti e dieci i fold**, per tutte e sei le architetture.
`deploy_board/metadata.json` dichiara `origine_soglia: "dichiarata a priori"`.

**E' la procedura giusta, ed e' registrata.** [DEC-105](DECISIONS.md#dec-105):
soglia 0,5 dichiarata prima di guardare i dati, uguale per tutti i fold; il
validation serve solo a fermare l'addestramento. La ragione e'
[EXP-010](EXPERIMENTS.md#exp-010): le soglie scelte per fold vanno da 0,01 a
0,99 con deviazione **0,37** su un intervallo di ampiezza uno.

**Perche' conta.** La dichiarazione sbagliata era piu' **debole** del vero. Una
soglia fissa non stima nulla e non puo' sovradattarsi: e' una garanzia piu'
forte di «scelta sul validation», non piu' debole. Il capitolo si attribuiva
una procedura inferiore a quella effettivamente seguita, e nel punto che il
relatore ha chiesto di dichiarare senza ambiguita'.

**Intervento.** `tesi/Cap3.tex`: aggiunta la riga della soglia in
`tab:addestramento`; riscritta la riga di `tab:leakage` («nessun dato: fissata
a priori a 0,50»); due paragrafi nuovi in `sec:leakage` con la ragione misurata
e il limite del ragionamento (il confronto fra regole e' stato fatto sui fold
di prova, quindi stabilisce che la scelta per fold e' dannosa, non che 0,50 sia
il valore migliore); corretto `sec:modelli`, che aveva propagato l'errore;
`sec:allarme` dice «fissata» invece di «scelta». `tesi/Cap4.tex`: riscritto il
paragrafo «La soglia non vede il soggetto di prova», che ora dichiara la
garanzia piu' forte e nomina l'unica eccezione, la soglia **oracolo** del
trasferimento a UR-Fall, che e' diagnostica e dichiarata dove compare.

**Verificato con:** `python tesi/controlla.py` -> gli stessi 8 problemi
preesistenti, nessuno nuovo. Nessuna compilazione LaTeX: non c'e' un
compilatore su questa macchina.

**Collegamenti:** [DEC-105](DECISIONS.md#dec-105),
[EXP-010](EXPERIMENTS.md#exp-010)

---

<a id="iss-173"></a>
### ISS-173 — Le sei architetture non erano descritte in nessun punto della metodologia

**Trovata:** 2026-09-22 · **Gravita': media** · **Stato: RISOLTA il 2026-09-22**

Il Capitolo 3 rimandava al Capitolo 4 per «le sei architetture messe a
confronto, con il rispettivo numero di parametri»; il Capitolo 4, in
`sec:architetture`, le nominava in una riga e passava ai risultati. Struttura,
iperparametri e scelte di costruzione non stavano quindi da nessuna parte.
Il `Cap2.tex` rimandava a `\ref{sec:architetture}` per l'architettura a grafo
«con nodi di natura diversa», cioe' a una sezione di risultati per una
questione di metodo --- ed e' esattamente lo spostamento che il relatore
chiedeva in senso opposto.

**Intervento.** Nuova `sec:modelli` in `tesi/Cap3.tex` con `tab:modelli`
(struttura e parametri delle sei architetture, da `src/modelli.py` e dai
`risultati/addestramento/run_*.json`), e cinque paragrafi su: uscita softmax
identica per tutti, che cosa sorveglia l'arresto anticipato, la rete a grafo
che ha per nodi le grandezze e non i giunti con il limite che ne segue, il
riassunto a 72 numeri della foresta, e che cosa non e' stato fatto (nessuna
ricerca di iperparametri). `Cap2.tex` ora rimanda a `sec:modelli`, e la sua
sottosezione sulle famiglie di modelli ha l'etichetta `sec:famiglie` che le
mancava.

**Verificato con:** `python tesi/controlla.py` -> nessun riferimento orfano,
gli stessi 8 problemi preesistenti.

---

<a id="iss-174"></a>
### ISS-174 — Il filtro di ridondanza del DTW era usato ma mai definito

**Trovata:** 2026-09-22 · **Gravita': media** · **Stato: RISOLTA il 2026-09-22**

`sec:leakage` citava «$0,85$, la soglia oltre la quale la procedura stessa
considera due grandezze intercambiabili» senza che `sec:dtw` avesse mai
introdotto un filtro di correlazione. Il lettore vedeva 33 candidate, un
punteggio di separabilita' e dodici scelte, e non poteva sapere che quattro
grandezze meglio piazzate erano state escluse per ridondanza. Il capitolo,
inoltre, non elencava da nessuna parte quali fossero le dodici.

**Intervento.** Nuova `sec:ridondanza` in `tesi/Cap3.tex`: la selezione avida,
la soglia 0,85, la correlazione misurata sui soli fotogrammi con posa valida,
`tab:ridondanti` con le quattro escluse e con chi le rende ridondanti, e
l'elenco delle dodici adottate con la loro correlazione media (0,435). Dati da
`risultati/dtw/log_dtw_v5_top12.txt`.

Aggiunto anche il limite del criterio, che il registro chiedeva di scrivere nel
Capitolo 3 e che non c'era: il punteggio valuta ogni grandezza **da sola**, e
`A3_h_pavimento` si colloca **21ª su 33** e non viene selezionata, mentre
aggiunta alle dodici porta i falsi negativi da 249 a 163
([EXP-023](EXPERIMENTS.md#exp-023)).

**Attenzione a un numero superato.** [EXP-022](EXPERIMENTS.md#exp-022) dice
«19ª su 33»: era il rango nella classifica **v3**
(`risultati/dtw/classifica_dtw_v3.csv`). Nella classifica adottata
(`risultati/dtw/classifica_dtw.csv`, quella che produce `scelte.txt`) il rango
e' **21**. Nella tesi va il 21.

**Verificato con:** rango ricontato su entrambi i CSV; `python
tesi/controlla.py` -> nessun problema nuovo.

**Collegamenti:** [ISS-139](#iss-139), [EXP-022](EXPERIMENTS.md#exp-022),
[EXP-023](EXPERIMENTS.md#exp-023)

---

<a id="iss-171"></a>
### ISS-171 — «Nessun filtraggio temporale» era falso: `smooth_landmarks` e' attivo per impostazione predefinita

**Trovata:** 2026-09-21 · **Risolta:** 2026-09-21 · **Gravita': media**

`tesi/Cap3.tex`, sezione `sec:filtraggio`, dichiarava in grassetto:

> La configurazione adottata **non applica alcun filtraggio temporale**. Le
> coordinate entrano nel calcolo delle grandezze cosi' come lo stimatore le
> restituisce.

La seconda frase e' vera, la prima no. `mp.solutions.pose.Pose` espone
l'opzione **`smooth_landmarks`**, che con `static_image_mode=False` vale
**`True`** per impostazione predefinita e applica un livellamento temporale ai
landmark. **Il progetto non la passa mai.**

    $ grep -rn "smooth_landmarks" --include=*.py .
    (nessun risultato)

    pipeline/estrai_feature.py:267
        pose = mp.solutions.pose.Pose(static_image_mode=False,
                                      model_complexity=1,
                                      min_detection_confidence=0.5,
                                      min_tracking_confidence=0.5)

Lo stesso vale per tutte le altre quindici costruzioni di `Pose` nel progetto,
compresa quella a bordo in `deploy_board/rileva.py:775`.

**Perche' conta.** Non cambia alcun numero --- il livellamento c'era anche
quando i risultati sono stati prodotti, su entrambi i lati --- ma cambia
l'interpretazione della prova sul filtraggio. Quella prova misura che cosa
costerebbe **aggiungere** una media mobile sopra l'uscita dello stimatore; non
misura il passaggio da un segnale grezzo a uno filtrato, perche' il segnale
grezzo non e' mai stato usato. Dichiarare «nessun filtraggio» invitava alla
seconda lettura.

**Che cosa resta vero.** La pipeline non aggiunge alcun filtro proprio, e tutti
i consumatori --- selezione DTW, addestramento, valutazione, dispositivo ---
leggono lo stesso segnale. Su questo l'affermazione originale reggeva.

**Intervento.** Riscritto il passaggio in `sec:filtraggio`: «la pipeline non
aggiunge alcun filtro temporale», piu' un capoverso che dichiara il
livellamento interno dello stimatore e precisa che cosa la prova della
Sezione `sec:robustezza` misura davvero.

**Da valutare, non fatto:** disattivare `smooth_landmarks` e rimisurare
sarebbe l'esperimento che scioglie la questione --- direbbe quanto del segnale
stabile venga dallo stimatore e quanto dalla scelta di non filtrare. Non e'
stato eseguito.

**Verificato con:** `grep -rn "smooth_landmarks" --include=*.py .` -> nessun
risultato; lettura di `pipeline/estrai_feature.py:267`.

**Collegamenti:** `tesi/Cap3.tex` sez. `sec:filtraggio`, `sec:robustezza`


<a id="iss-169"></a>
### ISS-169 — La tesi contava 218 riprese mentre i risultati venivano da un'estrazione a 220

**Trovata:** 2026-09-21 · **Risolta:** 2026-09-21 · **Gravita': media**

Il Capitolo 3 dichiarava **218 riprese** e **114.923 fotogrammi**, e il
Capitolo 4 **109 registrazioni** di Camera 1 con **57.786 fotogrammi** e posa
valida al **91,6%**. Sono i numeri di `feature_v2.csv`. Tutti i risultati
riportati vengono pero' da `feature_v5.csv`, che ne ha **220** e **116.362**,
con Camera 1 a **110 registrazioni**, **58.359 fotogrammi** e posa al
**92,3%**.

Misurato su tutti i file delle feature:

| file | riprese | fotogrammi | etichetta 0 | con posa |
|---|---:|---:|---:|---:|
| `feature_v2.csv` | 218 | 114.923 | 98.857 | 109.767 |
| `feature_v3.csv` | **220** | **116.362** | **100.296** | **111.570** |
| `feature_v4.csv` | 220 | 116.362 | 100.296 | 111.570 |
| `feature_v5.csv` | 220 | 116.362 | 100.296 | 111.570 |
| `feature_v6_220.csv` | 220 | 116.362 | 100.296 | 111.570 |

Le due riprese mancanti in v2 erano rientrate **gia' con v3**, e il testo non
era stato aggiornato: descriveva quindi un dataset diverso da quello che
produceva i numeri.

**Perche' non era emersa.** Le due riprese sono entrambe di attivita'
quotidiana e valgono 1.439 fotogrammi **tutti di etichetta 0**: le due classi
positive restano 5.542 e 10.524 in ogni versione. La didascalia di
`tab:etichette` lo aveva persino previsto --- *«aggiungerle sposterebbe
soltanto la prima riga»* --- e proprio per questo nessun controllo se n'e'
accorto: i numeri che contano non cambiavano, e quelli che cambiavano non
venivano ricontrollati.

**Intervento.** Conteggi allineati a v5 in `tesi/Cap3.tex` (testo, `tab:dati`,
`tab:etichette`) e in `tesi/Cap4.tex`. Tolto il paragrafo sulla doppia
contabilita' 220/218, che non ha piu' oggetto.

**Verificato con:** conteggio diretto su tutti i CSV delle feature con pandas
-> i valori della tabella qui sopra; `grep "218\|114923\|109767\|98857\|57786" tesi/*.tex`
-> nessuna occorrenza residua; `python tesi/controlla.py` -> gli stessi 8
problemi preesistenti.


<a id="iss-168"></a>
### ISS-168 — `use_pruning=True` con una finestra restituisce `inf`, e tre grandezze su 33 sparivano dalla selezione

**Trovata:** 2026-09-21 · **Risolta:** 2026-09-21 · **Gravita': alta**

`src/dtw.py` chiamava `dtaidistance.dtw.distance_fast` con **entrambi**
`window=` e `use_pruning=True`. I due non stanno insieme: il limite di potatura
viene ricavato dalla distanza euclidea, che e' un maggiorante del DTW *libero*
ma **non** di quello *vincolato da una finestra*. Un cammino costretto in una
banda stretta puo' costare piu' dell'allineamento uno-a-uno; quando succede, la
funzione pota l'intera matrice e restituisce `inf`.

Misurato su una coppia reale di curve di `feature_v5.csv`, entrambe finite:

| | valore |
|---|---|
| `use_pruning=True` | **`inf`** |
| `use_pruning=False` | 27,54 |

**Perche' e' grave, ed e' il punto.** L'infinito non arriva mai a chi legge, e
non produce alcun errore. Attraversa `punteggio()` e si trasforma in due modi
opposti, tutti e due silenziosi:

- se cade fra le distanze **intra-classe**, `intra.mean()` diventa infinita e
  il punteggio della grandezza vale `fa.mean()/inf` = **esattamente 0**: la
  grandezza scompare dalla classifica e non viene mai selezionata;
- se cade fra quelle **incrociate**, il punteggio diventa `inf` e la grandezza
  balza in testa.

Su `feature_v5.csv` con `dtaidistance` 2.5.1 ne erano colpite **tre grandezze
su 33**: `A3_angolo_tronco` (0,0000 invece di 1,3560), `A3_testa_rel_y` e
`A3_larghezza` (`inf` su cam2). La selezione che ne risultava **non era quella
adottata**: scambiava `A2_testa_rel_y` con `A3_testa_rel_y`.

**Perche' non era mai emersa.** Il difetto e' latente e dipende dalla versione
di `dtaidistance`: quando `scelte.txt` fu prodotto, la libreria installata non
si comportava cosi', e i punteggi salvati sono corretti. Chiunque avesse
rifatto l'analisi con una versione recente avrebbe pero' ottenuto **una
selezione diversa senza accorgersene**, e senza che nulla lo segnalasse. E'
stata scoperta perche' `pipeline/dtw_per_fold.py` rifa' la selezione
sull'intero insieme e **si ferma** se non riproduce quella adottata.

**Intervento.** `use_pruning=False` in `src/dtw.py`, con il commento che spiega
perche' non e' una scelta di prestazione. La passata completa su 33 grandezze e
due camere passa da 29,6 s a circa 25 s: il pruning non stava nemmeno
facendo risparmiare.

**Verificato con:** `python pipeline/dtw_per_fold.py --csv feature_v5.csv --top 12`
-> il controllo sull'intero insieme «riproduce esattamente scelte.txt».

<a id="iss-163"></a>
### ISS-163 — 2.842 immagini di persone erano fuori dal `.gitignore`, e `git status` le proponeva

**Trovata:** 2026-09-10 · **Risolta:** 2026-09-10 · **Gravita': alta**

`deploy_board/riletture/` --- creata fra il 9 e il 10 settembre da
`rendi_clip.py` --- contiene **2.889 file, di cui 2.842 JPEG**: gli stessi
fotogrammi delle clip con lo scheletro e il punteggio disegnati sopra, cioè le
stesse persone identificabili. **Nessuna regola del `.gitignore` li copriva.**

    git ls-files --others --exclude-standard deploy_board/riletture/ | wc -l
    2889

**Perché è sfuggita, ed è il punto che conta.** Il `.gitignore` difendeva per
**elenco di cartelle**:

    deploy_board/clip_demo/
    risultati/sessioni/**/clip/
    **/clip/
    deploy_board/resa_clip*/
    deploy_board/sessioni/**/clip/

Le ultime due erano state aggiunte il 9 settembre proprio perché le cartelle
dei fotogrammi annotati **non si chiamano `clip`** e la regola `**/clip/` non
le prendeva. Il commento in testa dice che il difetto fu trovato *«con
`git check-ignore` prima di committare, che è l'unico momento in cui ci si
accorge in tempo»*. **Ventiquattro ore dopo si è ripresentato identico**, su
una cartella che quel giorno non esisteva ancora.

Un elenco di cartelle è una difesa che **invecchia**: ogni cartella nuova
ricomincia da capo, e la protezione dipende da chi si ricorda di aggiornarlo
nel momento giusto. È lo stesso modo di sbagliare di [ISS-139](#iss-139) e
[ISS-161](#iss-161) --- due cose che devono restare d'accordo, e nulla che
sollevi un errore se smettono.

**RISOLTA il 2026-09-10**, `.gitignore`. La difesa non è più l'elenco delle
cartelle ma **l'estensione**: `*.jpg` e `*.jpeg`, che vale per qualunque
cartella, anche per quelle che non esistono ancora.

L'invariante che lo rende sicuro è stato verificato, non supposto: **in questo
repository non esiste un solo JPEG che sia un risultato.**

| | |
|---|---:|
| JPEG già tracciati | `git ls-files \| grep -c jpg` -> **0** |
| immagini che `git status` proponeva prima | **2.842** |
| immagini che `git status` propone dopo | **0** |
| CSV e LEGGIMI di `riletture/` ancora tracciabili | **47** --- invariati |
| PNG di risultato ancora tracciabili | **47** --- invariati |

I PNG restano fuori dalla regola perché sono figure e curve DTW, cioè
risultati. La separazione è netta e non è un caso: i fotogrammi di telecamera
in questo progetto sono **sempre** JPEG, le figure **sempre** PNG.

**Cosa NON risolve.** Le immagini restano sul disco, ed è giusto: servono a
dichiarare la verità di riferimento sulle sessioni. Questa regola impedisce
che finiscano in un commit, non che esistano.

**Verificato con:** `git ls-files --others --exclude-standard | grep -ci jpe\?g`
-> **0** dopo l'intervento, **2.842** prima; `git ls-files --others
--exclude-standard deploy_board/riletture/ | wc -l` -> **47**, tutti `.csv` e
il LEGGIMI.

**Collegamenti:** [ISS-161](#iss-161), [ISS-139](#iss-139),
[ISS-142](#iss-142)

---

<a id="iss-148"></a>
### ISS-148 — La finestra degli integrali dura 1,72 s in addestramento e 4,27 s sulla board

**Trovata:** 2026-09-08 · **Risolta:** 2026-09-09 · **Gravita': alta**

`K_INTEGRALI = 31` e' un numero di **fotogrammi**, non una durata. Le nove
grandezze integrali --- che sono nove delle **dodici colonne installate** ---
si accumulano sugli ultimi 31 fotogrammi. Quanto tempo siano 31 fotogrammi
dipende da chi li produce, e i due lati non coincidono.

| | fotogrammi al secondo | finestra degli integrali |
|---|---:|---:|
| estrazione (`FPS_DATASET`) | 18,00 | **1,72 s** |
| board, come progettata (`fps_assunti`) | 9,00 | 3,44 s |
| board, **misurata** ([EXP-024](EXPERIMENTS.md#exp-024)) | 7,26 | **4,27 s** |

**Il rapporto e' 2,48.** E non e' soltanto deriva di misura: gia' nell'intento
di progetto --- 18 fps in estrazione contro 9 in esercizio --- il fattore
sarebbe **2**. E' un'incoerenza di progetto, non un imprevisto.

Dalla stessa costante dipendono altre due grandezze:

- **le derivate.** `geometry.fotogramma` divide per `dt = 1/fps`. In estrazione
  riceve 18,0 ed e' il valore vero. Sulla board riceve `fps_assunti = 9,0`
  mentre l'intervallo vero e' 1/7,26 = 0,138 s: le derivate escono
  **sopravvalutate del 24%**;
- **la finestra di decisione.** In addestramento 22 campioni con passo 2 su uno
  stream a 18 fps coprono 2,44 s --- ed e' il valore che `metadata.json`
  dichiara. Sulla board 22 campioni consecutivi a 7,26 fps coprono **3,03 s**.

**Perche' conta.** Il modello ha imparato su grandezze che riassumono 1,72 s e
in esercizio ne riceve di omonime che ne riassumono 4,27. Tre quarti del
vettore di ingresso hanno un significato fisico diverso fra addestramento ed
esercizio. E' la stessa famiglia di [ISS-147](#iss-147) --- la board e
l'addestramento non calcolano la stessa cosa --- e la stessa gia' incontrata
nel Capitolo 5, dove un sottocampionamento ereditato dava 2 cadute su 5 invece
di 4.

**La correzione NON richiede una riestrazione, e questo e' il punto.** Rendere
`K` una durata invece di un conteggio produce su UP-Fall un CSV **identico**:
il dataset e' a 18 fps costanti, e `round(1,72 x 18) = 31`. Il disallineamento
sta tutto sul lato che legge una telecamera vera. Si corregge in
`deploy_board/rileva.py`, misurando i fotogrammi al secondo effettivi e
derivando da quelli sia `dt` sia la lunghezza del buffer.

**Da fare.**
1. `rileva.py` stima l'fps corrente su una finestra mobile e passa **quello**
   a `fotogramma()`, invece di `fps_assunti`.
2. Il buffer degli integrali del motore diventa lungo `round(1,72 x fps)`
   invece di 31 fissi.
3. Dichiarare in `metadata.json` la **durata** 1,72 s accanto al conteggio 31,
   perche' e' la durata la grandezza che deve coincidere.
4. Rifare una sessione, che serve comunque per [ISS-147](#iss-147).

**Non tocca** il Capitolo 4: in laboratorio l'fps e' costante e tutto e'
coerente. Tocca i numeri di campo, insieme a [ISS-147](#iss-147).

**Verificato con:** `pipeline/estrai_feature.py:212` passa `config.FPS_DATASET`
= 18,0 su **ogni** fotogramma (nessun sottocampionamento in estrazione);
`deploy_board/rileva.py:658` passa `meta['fps_assunti']` = 9,0;
`src/geometry.py:210` costruisce `deque(maxlen=K)` con K in fotogrammi;
`riepilogo.json` della sessione del 6 settembre da `fps_medio` 7,2647.

**Collegamenti:** [ISS-147](#iss-147), [ISS-137](#iss-137),
[EXP-024](EXPERIMENTS.md#exp-024), Capitolo 5

---

### Risolta il 2026-09-09

**Intervento.** Il buffer degli integrali conserva **secondi** invece di
campioni. Ogni campione porta il proprio `dt` e lo scarto e' per anzianita':
restano i piu' recenti la cui durata complessiva non supera
`DURATA_INTEGRALI_S` = 1,7222 s. Cosi' la finestra e' corretta anche quando la
cadenza salta *dentro* la ripresa, che e' il caso reale.

Sul dispositivo, `rileva.py` non passa piu' `fps_assunti` a `fotogramma()` ma
la **cadenza misurata** (classe `Cadenza`: mediana degli intervalli su
finestra mobile di trenta, scartando quelli oltre i cinque secondi, che sono
riaperture della telecamera e risvegli). Il metadato dichiara
`durata_integrali_s` accanto al conteggio, e il riepilogo della sessione
riporta `fps_dichiarato` e `fps_usato_ultimo`.

**Il punto che rendeva la correzione praticabile ha retto:** a 18 fps costanti
le due formulazioni sono la stessa cosa. Verificato confrontando il motore
precedente e quello nuovo sulla stessa sequenza, tutte e 33 le grandezze:
scarto **0,000e+00**. Il dataset e i numeri della tesi non si muovono.

A 9 e a 7,26 fps cambiano soltanto le nove colonne integrali --- ed e'
esattamente cio' che il difetto descriveva.

**Verificato con:** `python prove/esegui.py` -> 33 su 33, comprese due prove
nuove che il file d'oro non poteva dare (il buffer copre la durata dichiarata
a 18, 9 e 7,26 fps; il costruttore accetta i secondi);
`rileva.py --video` con l'ambiente della board -> parita' sulle finestre
`0,000e+00` e sui fotogrammi 0,00%.

**Resta da fare:** **non e' stato provato sulla board**, che era spenta il 9
settembre. Il punto 4 dell'elenco qui sopra --- rifare una sessione --- non e'
stato eseguito, e senza quella nessun numero di campo cambia.

---

<a id="iss-150"></a>
### ISS-150 — L'allineamento delle annotazioni OmniFall deriva fino a 14,8 secondi

**Trovata:** 2026-09-08 · **Risolta:** 2026-09-09 · **Gravita': alta**

Il Capitolo 3 dichiara, a proposito delle annotazioni di OmniFall applicate a
UP-Fall:

> *«I segmenti, espressi in secondi, sono stati convertiti nei corrispondenti
> intervalli di fotogrammi utilizzando la frequenza di acquisizione di
> 18~fps.»*

OmniFall annota **in secondi**; la conversione in indici di fotogramma
moltiplica per una costante. Ma [ISS-149](#iss-149) ha misurato che la cadenza
vera va da 14,43 a 19,63 fps. **L'errore non e' costante: cresce lungo la
ripresa**, perche' e' proporzionale al tempo trascorso dall'inizio.

Deriva a fine ripresa, misurata su tutte e 220:

| ripresa | fps vero | durata | deriva |
|---|---:|---:|---:|
| `sub06_act08_trial01_cam01/02` | 14,43 | 60 s | **214 fotogrammi = 14,8 s** |
| `sub06_act07_trial01_cam01/02` | 14,59 | 60 s | 205 fotogrammi = 14,0 s |
| `sub06_act11_trial01_cam01/02` | 14,66 | 60 s | 200 fotogrammi = 13,7 s |

| | |
|---|---:|
| deriva mediana | 11 fotogrammi (**0,58 s**) |
| riprese in cui supera **1 secondo** | **64 su 220** |
| riprese in cui supera la durata mediana di una caduta (3,11 s) | **15 su 220** |

**In quindici riprese l'etichetta OmniFall puo' quindi indicare un momento
diverso dall'evento che descrive**, perche' lo scarto e' piu' lungo dell'evento
stesso.

**Che cosa NON invalida.** Le etichette 0/1/2 usate per addestrare **non
vengono da OmniFall**: sono annotazioni manuali per fotogramma, e il Capitolo 3
lo dichiara. L'addestramento e la validazione non sono toccati.

**Che cosa tocca.** Tutto cio' che usa le classi OmniFall, e in particolare la
tabella del Capitolo 3 che confronta le grandezze dinamiche fra `fall` e
`lie_down` e fra `fallen` e `lying` (rapporti 30,1x, 42,5x, 33,0x, 139,4x).
Quei rapporti sono calcolati su segmenti allineati con la costante sbagliata, e
sulle riprese piu' lente il segmento puo' cadere altrove. **Vanno ricalcolati**
prima di restare nel testo.

Tocca anche il 96,4% di copertura dichiarato: una parte della quota non
allineata puo' essere deriva e non assenza di annotazione.

**Correzione.** `pipeline/mappa_omnifall.py` deve convertire i secondi in
fotogrammi usando **i timestamp dei fotogrammi stessi** --- che ci sono, e sono
al microsecondo --- invece di moltiplicare per 18. Non e' una stima: per ogni
istante annotato si cerca il fotogramma il cui timestamp gli e' piu' vicino.
E' anche piu' semplice del codice attuale.

**Perche' non era emerso.** Perche' 18 fps era scritto in `config.py` come un
dato di fatto, e chiunque scrivesse un convertitore lo usava. Lo stesso valore
sbagliato ha prodotto [ISS-149](#iss-149) sulle derivate e questo
sull'allineamento: **una costante non verificata si propaga a tutto cio' che la
legge**, e i due difetti non hanno niente in comune se non quella.

**Verificato con:** per ogni ripresa, `durata x (18 - fps_vero)` sui timestamp
dei nomi dei file; `pipeline/fps_dataset.py` per le cadenze.

**Collegamenti:** [ISS-149](#iss-149), [ISS-148](#iss-148),
[EXP-033](EXPERIMENTS.md#exp-033), Capitolo 3

---

### Risolta il 2026-09-09

**Intervento.** `pipeline/mappa_omnifall.py` non converte piu' i secondi
moltiplicando per una cadenza costante: legge i **timestamp dei fotogrammi**
dai nomi dei file e cerca per ogni istante annotato il fotogramma che gli
corrisponde. Come la scheda prevedeva, e' anche piu' semplice del codice
precedente. Una ripresa entra nella mappa solo se **tutti** i suoi nomi
portano un timestamp leggibile e ordinato; altrimenti resta il ripiego
dichiarato, che e' meglio di un tempo inventato su meta' dei fotogrammi.

**Copertura: 220 riprese su 220**, il 100% delle righe. Nessuna col ripiego.

**Quanto valeva il difetto** ([EXP-034](EXPERIMENTS.md#exp-034)): spostamento
mediano dell'etichetta **0,398 s**, massimo **11,890 s**, il **22,2%** delle
righe spostate di oltre un secondo, e **2.727 fotogrammi su 116.362 (2,3%)
cambiano classe OmniFall**.

**L'esito sulle metriche e' parziale, e va detto:** la copertura sale dal 97,3
al **98,5%** e l'accordo fra la nostra etichetta «a terra» e `fallen` sale dal
81,5 all'**85,1%**; l'accordo sulla **transizione** non si muove (67,4% ->
67,2%). La correzione e' giusta perche' usa il dato invece di una costante
falsa, non perche' produca un salto.

**E lascia un'eredita' utile:** che il disaccordo sulla transizione resista ai
tempi giusti significa che **non era un problema di allineamento** ma di
definizione dell'evento. Vedi [ISS-154](#iss-154).

**Resta da fare:** la tabella del Capitolo 3 che confronta `fall` con
`lie_down` e `fallen` con `lying` (rapporti 30,1x, 42,5x, 33,0x, 139,4x) e' la
ragione per cui il difetto era grave, e **non e' ancora stata ricalcolata**
sui segmenti riallineati. Finche' non lo e', quei quattro numeri restano
sospesi.

---

<a id="iss-146"></a>
### ISS-146 — La scomposizione della latenza usava ancora il costo per fotogramma ritirato

**Trovata:** 2026-09-08 · **Risolta:** 2026-09-08 · **Gravità: media**

`pipeline/latenza.py` portava `CALCOLO_MS = 37.7`, cioè il valore che
[ISS-137](#iss-137) aveva ritirato il 6 settembre. La board misurata ne fa
**136,65** ([EXP-024](EXPERIMENTS.md#exp-024)), e il Capitolo 5 stampa i due
valori a due sezioni di distanza: la tabella del costo dichiara che i 37,7 ms
non sono più sostenuti, e la tabella della latenza li somma.

**Perché era passato inosservato.** [ISS-145](#iss-145), che il 7 settembre ha
riscritto proprio quel paragrafo, cita l'addendo di calcolo per nome --- «la
tabella somma riempimento della finestra (2,743 s), persistenza (0,997 s) e
calcolo (0,038 s)» --- e non lo mette in dubbio: la revisione guardava
l'assunzione sul *riempimento*, e l'addendo più piccolo è passato come dato di
sfondo. Un numero che vale l'1% di un totale non viene riletto.

**Che cosa cambia, e che cosa no.**

| | prima | dopo |
|---|---:|---:|
| calcolo per fotogramma | 0,038 s (1,0%) | **0,125 s (3,2%)** |
| riempimento della finestra | 2,743 s (72,6%) | 2,743 s (71,0%) |
| persistenza | 0,997 s (26,4%) | 0,997 s (25,8%) |
| **totale, caso conservativo** | **3,778 s** | **3,865 s** |
| finestra ÷ calcolo | 73× | **22×** |

**La conclusione regge, il fattore no.** La latenza resta dominata dalla
finestra di decisione e non dall'hardware, che è ciò che il capitolo sostiene;
ma il margine passa da settantatré volte a ventidue. Anche il corollario si
sposta: un dispositivo dieci volte più veloce toglieva l'1% del totale, ne
toglie il 3%.

**Intervento.** La costante è stata tolta. L'addendo si ricava ora da
**1/fps della sessione stessa**: sulla board il ciclo è seriale, quindi la
cadenza fra due fotogrammi *è* il costo di un fotogramma. La sessione del 6
settembre lo conferma sui propri dati --- 136,65 ms sommando le quattro fasi
contro 137,65 ms di cadenza, cioè uno scarto dello 0,7% --- e ricavarlo dalla
sessione evita di sommare due sessioni diverse in un totale solo.

**Due residui, nello stesso giro.** Il Capitolo 5 riaffermava in due punti che
il classificatore è il **5,8%** del costo, dopo che la sezione precedente aveva
dichiarato quel valore ritirato e sostituito da **14,3%**: la sezione si
contraddiceva a quattro paragrafi di distanza.

E le **Conclusioni** dichiaravano ancora il bilancio intero della versione
ritirata --- *«gira a 26,5 fotogrammi al secondo, la percezione è l'88,4% del
tempo, il classificatore il 5,8%, [...] agiscono su un ventesimo del
problema»* --- dove la board misurata dà 7,3 fps, 85,2%, 14,3% e un settimo.
Era il punto del testo in cui quel numero pesava di più, perché è uno dei
cinque contributi elencati. Corretti tutti e tre i luoghi, e nelle Conclusioni
il valore ritirato è dichiarato accanto a quello nuovo invece di sparire.

**Verificato con:** `python pipeline/latenza.py` -> calcolo 0,125 s, totale
3,865 s, «il calcolo e' il 3,2% del totale»; `python tesi/controlla.py` ->
«Nessun problema»; `grep '5,8' tesi/Cap5.tex` -> resta solo la riga della
tabella dichiarata ritirata.

**Collegamenti:** [ISS-137](#iss-137), [ISS-145](#iss-145),
[EXP-024](EXPERIMENTS.md#exp-024), [EXP-030](EXPERIMENTS.md#exp-030),
Capitolo 5 `tab:latenza`

---

<a id="iss-145"></a>
### ISS-145 — Il «limite inferiore» della latenza non è un limite inferiore, e la persistenza non era giustificata

**Trovata:** 2026-09-07 · **Risolta:** 2026-09-07 · **Gravità: media**

Due difetti nello stesso paragrafo del Capitolo 5, trovati rispondendo a una
domanda che nessuno aveva fatto: *da che cosa si dice che cinque finestre
consecutive vanno bene?*

### Primo: la persistenza vale 5 e nessuno sa perché

`deploy_board/metadata.json` dichiara `persistenza_finestre: 5`,
`esporta_board.py` la scrive come costante, `rileva.py` la applica. **In nessun
punto del progetto è giustificata.** La soglia 0,50 ha una provenienza scritta
nel metadato (`origine_soglia`, che rimanda a [EXP-010](EXPERIMENTS.md#exp-010));
la persistenza no.

Non è un dettaglio: il Capitolo 5 mostra già che passando da k=1 a k=5 il
richiamo di campo crolla da **4 cadute su 5 a 1 su 5**. Un parametro che sposta
un numero di intestazione di quel tanto non può essere ereditato in silenzio.

**Ora è misurato** ([EXP-028](EXPERIMENTS.md#exp-028)): in laboratorio, su
cinquanta cadute, ogni passo di persistenza costa **0,222 s** di latenza e una
frazione di richiamo; k=1 dà richiamo 1,00 e mediana 1,44 s, k=5 dà 0,90 e
2,44 s. In cambio i falsi allarmi domestici calano del **31%**, da 16,0 a 11,1 eventi
all'ora. Il compromesso è ora esposto invece che nascosto.

### Secondo: 3,778 s è presentato come limite inferiore e non lo è

La tabella `tab:latenza` somma riempimento della finestra (2,743 s),
persistenza (0,997 s) e calcolo (0,038 s), e chiama il totale **limite
inferiore**.

**La mediana misurata alla stessa regola è 2,44 s** — 2,74 s riportata alla
frequenza di quella tabella — cioè **circa un secondo sotto**.

L'assunzione implicita è che la finestra debba riempirsi *dopo* l'inizio della
caduta. Non è richiesto: il classificatore decide su finestre **a cavallo**
dell'istante di inizio, e il movimento iniziale basta a portarle sopra soglia.
Il minimo misurato a k=1 è **+0,17 s**, cioè una finestra con tre fotogrammi di
caduta e quarantuno di ciò che la precede.

**Intervento.** Il Capitolo 5 chiama ora quel valore **caso conservativo** e non
limite inferiore, e gli mette accanto la misura empirica con la curva della
persistenza. La scomposizione resta: dice ancora, correttamente, che la latenza
è dominata dalla finestra e non dall'hardware.

**Perché era passato inosservato.** Perché il numero era analitico e nessuno
poteva contraddirlo: la latenza era dichiarata non misurabile. Vero per il
campo, **falso per il laboratorio**, dove l'etichetta è per fotogramma. La
conclusione «non è misurabile» era stata estesa oltre i dati che la
sostenevano.

**Verificato con:** `pipeline/latenza_laboratorio.py` sulle configurazioni DTW
e DTWH -> tabella in [EXP-028](EXPERIMENTS.md#exp-028); allineamento fra
finestre ricostruite e punteggi salvati verificato su tutti e dieci i fold.

**Collegamenti:** [ISS-108](#iss-108), [ISS-115](#iss-115),
[EXP-028](EXPERIMENTS.md#exp-028), Capitolo 5 `tab:latenza`

---

<a id="iss-144"></a>
### ISS-144 — La soglia dei 60 gradi non è dichiarata da nessuna parte

**Trovata:** 2026-09-07 · **Risolta:** 2026-09-07 · **Gravità: media**

La tabella dell'escursione per vista riporta «sequenze con escursione sopra
**60°**: 30 su 39 contro 8 su 39». È il conteggio che il testo preferisce al
rapporto fra le medie, perché le deviazioni sono grandi.

**Quel 60 non è giustificato in nessun punto del progetto.** Nel codice è un
letterale --- `sum(v > 60 for v in e1)` in `escursione_viste.py` --- senza
commento; nella tesi compare solo dentro la tabella; nel registro non c'è. È
una **soglia scelta a occhio** e presentata come se fosse un criterio.

È lo stesso difetto di [ISS-112](#iss-112), dove le soglie di etichettatura
erano dichiarate in due posti: qui non è dichiarata in nessuno.

### La sensibilità, misurata

| soglia | Camera 1 | Camera 2 |
|---:|---:|---:|
| 30° | 35 | 14 |
| 40° | 34 | 13 |
| 45° | 34 | 11 |
| 50° | 32 | 11 |
| **60°** | **30** | **8** |
| 70° | 30 | 4 |
| 80° | 26 | 2 |

**La conclusione non dipende dalla soglia.** Su tutto l'intervallo da 30° a 80°
la vista laterale supera la soglia fra 2,5 e 13 volte più spesso di quella
rialzata, e il verso non cambia mai. Le mediane, che non dipendono da alcuna
soglia, sono **87,3° contro 22,3°**.

**Intervento.** La didascalia della tabella dichiara ora che 60° è una
convenzione di lettura e non un criterio derivato, e riporta l'intervallo su
cui il conteggio è stato verificato. Il valore resta 60°: cambiarlo adesso, per
sceglierne uno che dia numeri migliori, sarebbe peggio che tenerlo dichiarato.

**Verificato con:** ricalcolo del conteggio a sette soglie da
`risultati/laboratorio/escursione_viste_10sog.csv`, tabella qui sopra.

**Collegamenti:** [ISS-112](#iss-112), [EXP-020](EXPERIMENTS.md#exp-020),
[EXP-026](EXPERIMENTS.md#exp-026)

---

<a id="iss-143"></a>
### ISS-143 — Il risultato «controintuitivo» del Capitolo 4 si rovescia a dieci soggetti

**Trovata:** 2026-09-07 · **Risolta:** 2026-09-07 · **Gravità: alta**

Il Capitolo 4 chiudeva la sezione sul punto di vista con un paragrafo
intitolato «Un risultato controintuitivo»:

> *«Un modello addestrato su Camera1 e verificato su Camera2 batte di
> $2{,}5\times$ un modello addestrato direttamente su Camera2, sullo stesso
> identico insieme di verifica. La qualità del punto di vista in addestramento
> conta più della sua corrispondenza con quello di esercizio.»*

Era il tipo di affermazione che si ricorda: contraria all'intuizione, con una
morale operativa chiara, e appoggiata a un numero.

**A dieci soggetti si rovescia.**

| | cinque soggetti | **dieci soggetti** |
|---|---:|---:|
| Camera1 -> Camera2 | 0,434 | 0,488 |
| Camera2 -> Camera2 | ~0,17 | **0,753** |
| | 2,5x a favore del trasferimento | **1,5x a favore dell'addestramento diretto** |

E si rovescia anche togliendo le riprese in cui lo stimatore cambia persona:
0,466 contro 0,747. Non e' quindi un effetto di [ISS-134](#iss-134).

**Perché era successo.** Con cinque soggetti, addestrare su Camera2 significa
addestrare su quattro persone di riprese che contengono poca informazione, e
la varianza fra fold e' enorme: la dispersione di quella riga era la piu' alta
della tabella. Il valore basso era compatibile con il caso quanto con
l'effetto, e nessuno aveva calcolato quanti soggetti servissero per
distinguerli --- che e' esattamente la disciplina che
[EXP-013](EXPERIMENTS.md#exp-013) ha introdotto **dopo**.

**Intervento.** Il paragrafo e' stato riscritto: l'affermazione e' dichiarata
**ritirata**, con i numeri vecchi e nuovi accanto, e sostituita da quella
ordinaria --- addestrare sulla vista di esercizio e' meglio che trasferirvi da
un'altra. Al suo posto resta un'osservazione piu' debole e piu' utile:
addestrare su entrambe le viste (0,731) e addestrare solo su quella di
esercizio (0,753) **non sono distinguibili**, quindi chi installa il sistema
puo' scegliere in base a ciò che ha.

**La lezione, ed è la stessa di altre tre voci di questo registro:** i
risultati piu' memorabili di questo lavoro sono stati anche i piu' fragili.
$4{,}32\times$ sul punto di vista, «due terzi taratura», «la foresta e' la
migliore», e ora questo: quattro affermazioni nate da pochi soggetti o da un
artefatto, tutte cadute quando la misura e' stata rifatta con piu' persone o
con lo strumento corretto.

**Verificato con:** `pipeline/viste_incrociate.py --csv feature_v3.csv
--feature A3 --escludi A3_h_pavimento`, con e senza `--senza-contaminate` ->
quarta riga 0,753 e 0,747 contro 0,488 e 0,466.

**Collegamenti:** [EXP-026](EXPERIMENTS.md#exp-026), [ISS-134](#iss-134),
[ISS-129](#iss-129), [EXP-013](EXPERIMENTS.md#exp-013)

---

<a id="iss-141"></a>
### ISS-141 — Una registrazione di quattro ore ha sepolto trenta numeri non giustificati

**Trovata:** 2026-09-07 · **Risolta:** 2026-09-07 · **Gravità: alta**

È [ISS-135](#iss-135) che rientra da un'altra porta, e la porta è la sessione
di durata del 6 settembre.

`pipeline/audit_numeri.py` raccoglie i valori da tutti i JSON e CSV sotto
`risultati/` e segnala i decimali del testo che non trovano riscontro. La
sessione `notte_20260906_1523` ha portato in quella cartella due CSV **per
campione**: uno per finestra (1,3 MB) e uno per fotogramma (**17,8 MB**).
Ogni valore viene registrato con sei arrotondamenti, e la riserva è salita a
**1.827.905 valori distinti**.

**Effetto immediato, misurato togliendo quei soli file:**

| | con i CSV di sessione | **senza** |
|---|---:|---:|
| valori distinti nella riserva | 1.827.905 | **10.769** |
| Cap3, numeri senza riscontro | 0 | **5** |
| Cap4 | 0 | **11** |
| Cap5 | 0 | **15** |
| Conclusioni | 0 | **4** |

**I due CSV erano il 99,4% della riserva.** Diecimila valori distinti vengono da tutti i risultati di tutto il progetto; un milione e ottocentomila venivano da una registrazione sola.

**Trentacinque numeri del testo non erano giustificati: erano sepolti.** E l'audit
non segnalava nulla — anzi, dava il risultato migliore mai visto, zero orfani
in tutti i capitoli. Esattamente come [ISS-135](#iss-135): *lo strumento non
fallisce, migliora.*

**E il difetto è arrivato da solo.** Nessuno ha modificato l'audit: è bastato
copiare una registrazione nella cartella dei risultati. Chi avesse eseguito
l'audit stamattina, senza sapere della sessione, avrebbe concluso che il
Capitolo 5 era a posto.

**Intervento.** `e_grezzo_di_sessione()` esclude i CSV sotto
`risultati/sessioni/`: sono il dato grezzo di una registrazione, non i suoi
risultati. Il `riepilogo.json` della sessione resta dentro, perché quello i
risultati li contiene. Il commento nel codice riporta i tre numeri qui sopra.

**Conseguenza, e non è piccola:** i trentacinque numeri riemersi vanno
guardati uno per uno. Alcuni sono valori di letteratura (99,58% di accuratezza dichiarata,
il crollo 72,9% → 16,9% fra dataset) e un artefatto non possono averlo; altri
sono i numeri *dichiarati* del costo edge (33,34 ms), che [ISS-137](#iss-137)
ha già dimostrato sbagliati; altri ancora sono statistiche derivate che un
artefatto dovrebbero averlo. La distinzione va fatta a mano.

**Verificato con:** `pipeline/audit_numeri.py` con e senza l'esclusione ->
riserva 1.827.905 -> 10.769 valori distinti; Cap3 0 -> 5, Cap4 0 -> 11,
Cap5 0 -> 15, Conclusioni 0 -> 4.

**Collegamenti:** [ISS-135](#iss-135), [ISS-126](#iss-126),
[ISS-140](#iss-140), [EXP-024](EXPERIMENTS.md#exp-024)

---

<a id="iss-140"></a>
### ISS-140 — La sessione del 6 settembre spariva dai numeri di campo, in silenzio

**Trovata:** 2026-09-07 · **Risolta:** 2026-09-07 · **Gravita': media**

`pipeline/eventi_sessioni.py` cercava i punteggi per finestra con
`glob('*/*/punteggi.csv')`. Le sessioni fino al 13 agosto vengono da
`session_recorder.py` e si chiamano cosi'; **`deploy_board/rileva.py`, il
registratore nuovo, scrive invece `<nome_sessione>.csv`**, e usa altri due
nomi di colonna: `t_s` invece di `t_unix`, `sopra` invece di `sopra_soglia`.

**La sessione di 4,6 ore del 6 settembre non entrava quindi in nessun numero
di campo, e lo script non se ne lamentava:** stampava otto blocchi invece di
nove e un totale coerente con se stesso. E' lo stesso modo di sbagliare di
[ISS-135](#iss-135) --- lo strumento non fallisce, da' un risultato piu'
pulito di quello vero.

**Quanto cambia.** Con la sessione dentro, sulle stesse regole di
aggregazione:

| | senza | **con** |
|---|---:|---:|
| sessioni | 8 | **9** |
| ore | 10,39 | **14,98** |
| eventi | 152 | **166** |
| eventi/ora | 14,6 | **11,1** |
| **fattore di sovrastima** | **47,8** | **44,8** |

Il **47,8** compariva nel Capitolo 5, nella guida al lavoro, nel documento per
il relatore e nelle schede di due figure. Va sostituito ovunque con **44,8**.

**Secondo difetto, trovato mentre si sistemava il primo: quel numero non aveva
un artefatto.** `eventi_sessioni.py` stampava e non salvava, quindi
`audit_numeri.py` lo dava per coperto solo perche' la cifra `47.8` compare per
caso dentro i JSON di addestramento. Ora ogni esecuzione scrive
`risultati/campo/eventi_sessioni.json` con la tabella per sessione e
l'aggregato.

**Intervento.** `elenco_punteggi()` accetta entrambi i nomi di file ed esclude
`*_feature.csv`; `tempo_e_decisione()` accetta entrambi gli schemi di colonne
--- per il conteggio degli eventi conta solo la differenza fra gli istanti,
quindi epoch e orologio monotono sono equivalenti.

**Verificato con:** `python pipeline/eventi_sessioni.py` -> nove blocchi
invece di otto, `notte_20260906_1523` presente con 4,59 ore e 3,1 eventi/ora,
fattore 44,8; artefatto scritto in `risultati/campo/eventi_sessioni.json`.

**Collegamenti:** [ISS-135](#iss-135), [ISS-113](#iss-113),
[EXP-024](EXPERIMENTS.md#exp-024)

---

<a id="iss-138"></a>
### ISS-138 — Le feature dell'intero dataset dipendono dall'ordine di estrazione

**Trovata:** 2026-09-06 · **Risolta:** 2026-09-07 · **Gravita': alta**

`pipeline/estrai_feature.py` creava **un solo** stimatore di posa, fuori dal
ciclo sulle riprese, e lo usava per tutte e 220. Il motore geometrico invece
veniva azzerato a ogni ripresa, con tanto di commento che ne spiegava la
ragione:

> *«Lo stato va azzerato a ogni ripresa: le derivate e gli accumuli non devono
> attraversare il confine fra due video.»*

**Il ragionamento era giusto e si e' fermato a meta'.** MediaPipe Pose e' un
tracciatore quanto lo e' il motore geometrico: mantiene stato fra un fotogramma
e il successivo, e non sa che nel frattempo e' cambiato il video. L'ultimo
fotogramma di una ripresa condiziona quindi il primo della successiva.

**Ne segue che `feature_v2.csv` --- 114.923 fotogrammi, il dataset su cui
poggia ogni risultato del lavoro --- dipende dall'ORDINE in cui le 220 riprese
sono state elaborate.**

**Come e' venuto fuori.** Aggiungendo al dataset i due video mancanti
(`sub06_act08_trial01_cam02` e `sub07_act10_trial01_cam01`, scaricati il
6 settembre) e' stata riestratta anche una ripresa **gia' presente**, come
controllo: `sub06_act08_trial01_cam01`. Su 866 fotogrammi, **zero righe
identiche** a quelle del dataset.

**Quanto pesa, misurato.** Scarto medio fra le due estrazioni, in deviazioni
standard della colonna:

| fotogrammi | scarto |
|---|---:|
| 0-5 | **2,32 σ** |
| 5-50 | 0,26 σ |
| 50-100 | 0,13 σ |
| 100-300 | 0,061 σ |
| oltre 300 | 0,026 σ |

**Decade**, perche' il tracciatore converge sulla persona che ha davanti. Sulle
dodici colonne che il modello usa, la mediana sull'intera ripresa e' 0,023 σ.

**Perche' non e' comunque trascurabile.** Il controllo e' una ripresa di
attivita' normale, 866 fotogrammi. Le riprese di **caduta** ne hanno circa
duecento: la parte contaminata --- i primi cinquanta, dove lo scarto sta fra
0,26 e 2,32 σ --- e' li' un quarto del video invece di un ventesimo. E la
finestra di decisione e' di 22 campioni a passo 2, cioe' 44 fotogrammi: **le
prime una o due finestre di ogni ripresa cadono dentro la zona contaminata.**

**Che cosa NON e' in discussione.** Le conclusioni qualitative del lavoro
poggiano su divari molto piu' grandi di questo: 0,422 di F2 fra le due viste,
0,309 fra due definizioni del compito. Uno scarto mediano di 0,023 σ sulle
feature non li ribalta.

**Che cosa invece lo e'.** La **riproducibilita'**: chi riestrae il dataset non
ottiene gli stessi numeri, e non c'e' modo di sapere quale ordine fu usato. E'
lo stesso difetto di [ISS-133](#iss-133), che riguardava pero' una misura
descrittiva; qui riguarda il dato di addestramento.

E' la **terza** volta in un giorno che la natura di tracciatore di MediaPipe
produce un difetto: [ISS-133](#iss-133) fra riprese di una misura,
[ISS-134](#iss-134) fra persone dentro una ripresa, e ora fra riprese del
dataset. Non e' una svista ripetuta: e' una proprieta' del componente che il
progetto non aveva mai messo per iscritto.

**Intervento (2026-09-06).** `estrai_feature.py` crea ora uno stimatore
**per ripresa** e lo chiude alla fine, con il commento che riporta i numeri
qui sopra. Aggiunto anche `--riprese`, per riestrarre pochi video invece di un
soggetto intero.

**Resta da decidere, ed e' una scelta di merito, non tecnica.** Riestrarre
tutto con lo stimatore corretto significa rifare ogni addestramento e ogni
numero del Capitolo 4. Le alternative:

1. **Riestrarre e riaddestrare.** Costa ore di calcolo e la riscrittura dei
   numeri, e rende il dataset riproducibile.
2. **Tenere il dataset com'e' e dichiarare il difetto**, con la misura di
   quanto pesa. Nessun numero cambia, e la tesi dice che le feature dipendono
   dall'ordine di elaborazione, con la tabella qui sopra a quantificarlo.

La seconda e' difendibile solo se il difetto e' dichiarato per intero. La
prima e' l'unica che rende il lavoro rifacibile da altri.

**Nota sui due video aggiunti.** Sono estratti e pronti in
`dataset/processed/features/feature_nuovi.csv`, ma **non sono stati uniti** a
`feature_v2.csv`: mescolare righe prodotte con due stati diversi peggiorerebbe
il problema invece di risolverlo. Vanno unite con la riestrazione completa, se
si sceglie la prima strada.

**Verificato con:** `estrai_feature.py --riprese sub06_act08_trial01_cam02,
sub07_act10_trial01_cam01,sub06_act08_trial01_cam01` -> 2.305 fotogrammi,
100% pose valide; confronto della ripresa di controllo contro `feature_v2.csv`
-> tabella qui sopra.

**Collegamenti:** [ISS-133](#iss-133), [ISS-134](#iss-134), [ISS-106](#iss-106)

---

**Risolta il 2026-09-07: si e' scelta la prima strada.** La riestrazione
completa e' partita la sera del 6 e si e' chiusa alle 20:57 con
`feature_v3.csv`: **220 riprese** contro 218, **116.362 fotogrammi** contro
114.923, **95,9%** di pose valide, uno stimatore di posa **per ripresa** e un
motore geometrico per telecamera. Il dataset non dipende piu' dall'ordine.

Le run su `feature_v2.csv` non sono state buttate: stanno in
`risultati/addestramento/v2/` con il loro LEGGIMI. Serviva perche' i nomi dei
file prodotti da `addestra.py` non contengono la versione del dataset --- le
run di GRU e della rete a grafo sarebbero state sovrascritte senza avviso.

**Cio' che resta da fare non e' questo difetto ma la sua conseguenza:** ogni
numero del Capitolo 4 viene da run su v2, e vanno rifatte su v3
([EXP-025](EXPERIMENTS.md#exp-025)).

**Verificato con:** `feature_v3.csv` riletto -> 220 riprese, 10 soggetti,
33 grandezze, 95,9% di pose; `pipeline/addestra.py --csv feature_v3.csv`
-> le run girano sul dataset nuovo.

---

<a id="iss-113"></a>
### ISS-113 — I numeri del costo edge non hanno un artefatto che li produca

**Trovata:** 2026-08-26 · **Risolta:** 2026-09-07 · **Gravita': media**

La ripartizione del costo per fotogramma --- pre-elaborazione 1,21 ms,
percezione **33,34 ms (88,4%)**, post 0,94 ms, classificatore 2,20 ms,
totale **37,7 ms** cioe' **26,5 fps** --- esiste **soltanto nel testo della
tesi**. Cercando `33.34` e `33,34` in tutti i JSON, CSV, TXT e MD dei due
progetti non compare in nessun file di risultato.

`DIP_PROJECT/deploy_board/benchmark_board.py` **stampa a schermo e non
salva**: i valori sono stati trascritti da una sessione di terminale.

E' una delle quattro richieste del relatore e una delle affermazioni di
intestazione del lavoro (*«il collo di bottiglia non e' la classificazione ma
la percezione»*), quindi e' anche il numero che meno puo' permettersi di non
essere rifacibile.

**Intervento, prima meta' (2026-08-26).** Non si aggiunge un banco
separato: `deploy_board/rileva.py` misura ora le quattro fasi **dentro
l'esecuzione vera**, con `perf_counter` attorno a pre-elaborazione,
percezione, post-elaborazione e classificatore, e scrive il bilancio nel
`riepilogo.json` insieme a tutto il resto. Il numero verra' quindi dalla
stessa esecuzione che produce gli allarmi, non da una prova a parte: e' il
solo modo perche' non possa divergere dalla catena in esercizio.

Riporta anche il costo del classificatore **per finestra** accanto a quello
**per fotogramma**, che sono i due valori la cui differenza il Capitolo 5
doveva spiegare.

**Verificato con:** `rileva.py --video clip_demo/evt_0001_092019` sul
calcolatore -> bilancio prodotto, JSON scritto. I valori sono quelli del PC e
non della board.

**Aggiornamento 2026-09-01.** Il riepilogo si scrive ora **ogni cinque
minuti** e non solo alla fine, in modo atomico e anche su interruzione: una
prova lunga che si ferma all'undicesima ora lascia comunque il bilancio. Prima
non lo lasciava, ed e' il difetto che avrebbe fatto perdere il numero una
seconda volta.

**Eseguito sulla board il 2026-09-06.** `rileva.py` e' stato installato ---
sulla board c'era ancora il deployment di agosto, e il registratore nuovo non
c'era mai arrivato --- e ha girato sulla telecamera vera. **L'artefatto ora
esiste**: `~/rileva/prova_*_riepilogo.json` contiene il bilancio per fase
prodotto dalla stessa esecuzione che produce gli allarmi.

**Il difetto della riproducibilita' e' quindi chiuso. Ne apre pero' un altro,
piu' grande:** i numeri che ne escono non sono quelli della tesi ---
144,1 ms per fotogramma invece di 37,7 --- ed e' [ISS-137](#iss-137).

**Resta da fare:** il bilancio consolidato sulla prova lunga, invece che su
sessanta secondi. La misura con una persona in scena e' stata fatta lo stesso
giorno ed e' in [ISS-137](#iss-137).

---

**Chiusa il 2026-09-07 con la prova lunga.** La sessione
`notte_20260906_1523` ha girato **4,59 ore** sulla telecamera vera e il suo
`riepilogo.json` porta il bilancio consolidato, prodotto dalla stessa
esecuzione che ha prodotto i quattordici allarmi:

| fase | ms per fotogramma | quota |
|---|---:|---:|
| pre-elaborazione | 0,25 | 0,2% |
| **percezione** | **116,38** | **85,2%** |
| post-elaborazione | 0,50 | 0,4% |
| classificatore (ammortizzato) | 19,51 | 14,3% |
| **totale** | **136,65** | **7,3 fps** |

Non e' piu' una trascrizione da terminale ne' una prova di sessanta secondi:
e' un file, e viene da un'esecuzione lunga con persone che entrano ed escono.
La deriva termica e' dentro la misura invece che fuori.

**Il difetto della riproducibilita' e' chiuso; quello del merito ---
136,65 ms contro i 37,7 dichiarati --- e' [ISS-137](#iss-137).**

**Verificato con:** `risultati/sessioni/20260906/notte_20260906_1523/
notte_20260906_1523_riepilogo.json` -> `costo_per_fotogramma_ms` per le
quattro fasi, `durata_orologio_s` 16.508, `sospensione_stimata_s` ~0.

---


<a id="iss-135"></a>
### ISS-135 — Aggiungere un file di dati grezzi ha indebolito l'audit dei numeri

**Trovata:** 2026-09-06 · **Risolta:** 2026-09-06 · **Gravita': alta**

`pipeline/audit_numeri.py` raccoglie i valori da tutti i JSON e CSV sotto
`risultati/` e segnala i decimali del testo che non trovano riscontro. Ogni
valore viene registrato **arrotondato a 1, 2, 3 e 4 decimali, piu' le due
varianti moltiplicate per cento**: sei voci per numero.

Salvando `escursione_viste_10sog_serie.json` --- la serie per campione di
cento riprese, circa 24.000 float --- la riserva si e' riempita di **oltre
centomila** valori arbitrari. Effetto immediato:

| | prima | dopo aver aggiunto le serie |
|---|---:|---:|
| Cap4, numeri senza riscontro | 5 | **0** |
| Cap5, numeri senza riscontro | 9 | **1** |

**Il Capitolo 5 non e' stato toccato.** Otto suoi numeri sono passati da
«senza riscontro» a «con riscontro» perche' con abbastanza decimali arbitrari
qualunque numero trova una corrispondenza per caso. Non erano stati
giustificati: erano stati **sepolti**.

**Il difetto e' pericoloso quanto e' silenzioso.** L'audit non fallisce, non
segnala niente: migliora. Chi lo esegue vede un risultato migliore e conclude
di aver sistemato qualcosa. E' lo stesso modo di sbagliare di
[ISS-110](#iss-110) --- il testo compila, si legge bene, e il numero e' falso
--- applicato allo strumento che dovrebbe intercettarlo.

**Come e' venuto fuori.** Il Capitolo 5 e' passato da 9 numeri orfani a 1
nella stessa sessione in cui era stato modificato solo il Capitolo 4. Un
miglioramento che nessuno ha causato e' un difetto, non un successo.

**Intervento.** `audit_numeri.py` esclude ora i file `*_serie.json` e
`*_serie.csv`: una serie per campione e' il **dato grezzo da cui** un
risultato si calcola, non un risultato. Il commento nel codice riporta i due
numeri qui sopra, perche' la riga non ha senso senza di essi.

**Conseguenza sul lavoro fatto.** Anche lo zero del Capitolo 4 era in parte
falso. Ripristinato l'audit, i suoi numeri orfani sono tornati a 5, cioe' agli
stessi di prima della sessione; i due numeri nuovi (il rapporto $2{,}23\times$
e la mediana $2{,}79\times$) sono statistiche derivate e sono state dotate di
un artefatto proprio, `escursione_viste_10sog_riepilogo.json`, prodotto da
`escursione_viste.py --solo-riepilogo` senza rifare la stima di posa.

**Verificato con:** `python pipeline/audit_numeri.py` prima e dopo
l'esclusione -> Cap4 0 -> 5, Cap5 1 -> 8; poi, aggiunto il riepilogo,
Cap4 5 -> 5 con i due numeri nuovi coperti.

**Collegamenti:** [ISS-110](#iss-110), [EXP-020](EXPERIMENTS.md#exp-020)

---


<a id="iss-115"></a>
### ISS-115 — La scomposizione della latenza e' misurata e non compare nel testo

**Trovata:** 2026-08-27 · **Risolta:** 2026-09-01 · **Gravita': media**

[EXP-017](EXPERIMENTS.md#exp-017) ha misurato la scomposizione della latenza di
rilevamento --- calcolo 0,038 s, riempimento della finestra 2,743 s,
persistenza 0,997 s, limite inferiore **3,778 s** --- e ha stabilito che
l'addendo dipendente dall'evento **non e' misurabile** con annotazione al
minuto.

**Nessuno di quei numeri e' nella tesi.** Cercati uno per uno: `3,778`,
`riempimento della finestra` e `2,743` non compaiono in alcun `.tex`; la parola
«latenza» compare una volta sola nel Capitolo 5, e riguarda il costo per
fotogramma.

E' una delle quattro metriche operative chieste dal relatore, quindi il difetto
non e' che manchi la misura --- c'e' --- ma che il lettore della tesi non la
trovi. La sua sede naturale e' il Capitolo 5, accanto al bilancio
computazionale: **li' il collo di bottiglia era la percezione, qui e' la
finestra di decisione, e in entrambi i casi il classificatore non conta.**

**Risolta il 2026-09-01.** Il Capitolo 5 ha ora la sezione
«La latenza di rilevamento, e che cosa non e' misurabile» (`sec:latenza`), con
`tab:latenza` e i tre addendi. La sezione apre dichiarando che il ritardo fra
evento e allarme non e' misurabile con annotazione al minuto, e chiude con la
verifica empirica del terzo addendo --- 1,70 e 1,28 s contro 1,00 attesi.

E' collocata subito dopo il bilancio del costo per fotogramma, perche' i due
risultati sono l'uno il complemento dell'altro: la' il collo di bottiglia e' la
percezione, qui la finestra di decisione, e in entrambi il classificatore e' il
termine che non conta.

**Verificato con:** `python tesi/controlla.py` -> «Nessun problema»;
i valori riletti da `risultati/campo/latenza.json`.

**Collegamenti:** [ISS-108](#iss-108), [EXP-017](EXPERIMENTS.md#exp-017)

---

<a id="iss-105"></a>
### ISS-105 — La finestra e' piu' corta dell'evento da riconoscere

**Trovata:** 2026-08-20 · **Risolta:** 2026-08-20 · **Gravita': alta**

`config.py`: `LUNGHEZZA_FINESTRA = 22` campioni a 9 fps = **2,44 s**.

Misurata la durata delle fasi sulle 50 riprese di caduta della camera 1:

| fase | mediana | decile 10% | decile 90% |
|---|---:|---:|---:|
| in piedi, prima | 0,92 s | | |
| **caduta in corso (classe 1)** | **3,11 s** | 2,05 s | 3,94 s |
| a terra (classe 2) | 5,97 s | 4,82 s | 6,89 s |

La finestra non puo' contenere una caduta intera: ne vede sempre un frammento,
e nella meta' dei casi al massimo il 78%.

**Da dove viene il 22.** E' 45 diviso due, dove 45 era `SEQUENCE_LENGTH` nel
`config.py` del progetto precedente — un valore che in quel progetto esisteva
in tre versioni contrastanti: 45 in config, 75 in `demo_realtime.py:23`, **39**
nei metadati della run migliore ([ISS-004](../../DIP_PROJECT/docs/ISSUES.md#iss-004) del vecchio registro).
Nessuna delle tre e' mai stata giustificata, e nessuna e' mai stata confrontata
con la durata dell'evento.

**Costo della correzione: basso.** I parametri di una GRU **non dipendono**
dalla lunghezza della sequenza; cresce solo il tempo di inferenza, in modo
lineare, e la memoria del buffer sulla board.

**Intervento previsto:** ablation su 22 / 28 / 36 campioni a parita' di tutto
il resto. 28 copre la caduta mediana, 36 il decile 90%.

**Chiusa da [EXP-012](EXPERIMENTS.md#exp-012), come «misurata, nessun
effetto» e non come «corretta».** L'ablation prevista e' stata eseguita su
22 / 28 / 36 / 44 campioni a parita' di tutto il resto, e l'ipotesi era
sbagliata: nessuna differenza significativa e andamento **non monotono**
--- 0,847 a 22 campioni, 0,838 a 28, 0,817 a 36, 0,881 a 44, con tutti i
$|t| < 1{,}3$.

La spiegazione probabile e' che la memoria effettiva non sia la finestra:
ogni campione porta gli integrali accumulati su 31 fotogrammi, cioe' 1,7 s di
storia in piu', e due terzi dei positivi sono lo stato «a terra», che si
riconosce da una finestra corta quanto si vuole.

**Il guadagno e' che 22 campioni non e' piu' un valore ereditato ma un valore
verificato contro tre alternative.** La voce era rimasta in «Aperti» dopo la
chiusura, ed e' stata spostata il 2026-09-06.

**Verificato con:** `pipeline/addestra.py --lunghezza {22,28,36,44}`, LOSO a
dieci soggetti -> tabella in EXP-012.

### ISS-132 — Il preambolo LaTeX dichiarava un formato e ne produceva un altro

**Trovata:** 2026-09-04 · **Risolta:** 2026-09-04 · **Gravita': media**

Il preambolo in uso su Overleaf fissava il formato due volte, in due punti
distanti fra loro, e la seconda dichiarazione annullava silenziosamente la
prima. Nessun errore di compilazione: il documento usciva, con margini e
interlinea diversi da quelli scritti.

| grandezza | dichiarata | effettiva |
|---|---|---|
| margine sinistro | 3,5 cm (`geometry`) | **4,02 cm** (`\oddsidemargin=42pt`) |
| margine destro | 3,5 cm | **2,98 cm** |
| margine superiore | 2 cm | **3,54 cm** (`\topmargin=-0.3cm` + intestazione) |
| margine inferiore | 2 cm | **3,66 cm** |
| altezza del testo | 25,7 cm | **22,5 cm** (`\textheight`) |
| interlinea | 1,5 (`\baselinestretch`) | **1,3** (`\linespread{1.3}`) |

L'asimmetria orizzontale e' di **1,03 cm** su un documento dichiarato
`oneside`, ed e' visibile a occhio nudo sfogliando il PDF.

**Tre difetti che avrebbero rotto la compilazione su Overleaf**, tutti dovuti
al fatto che Windows non distingue le maiuscole nei nomi di file e Linux si:

- `\usepackage[latin1]{inputenc}` caricato dopo `\usepackage[utf8]{inputenc}`.
  Tutti e undici i `.tex` di `tesi/` sono UTF-8 puro, verificato: la
  dichiarazione `latin1` corrompeva i circa 3.500 caratteri accentati.
- `\include{Conclusione}` — il file si chiama `Conclusioni.tex`.
- `\include{bibliografia}` e `\input frontespizio` in minuscolo — i file sono
  `Bibliografia.tex` e `Frontespizio.tex`.

**Una configurazione inerte.** Il preambolo impostava le intestazioni con
`fancyhdr` (`\rhead`, `\headwidth`, `\chaptermark`), ma nel corpo del
documento un `\pagestyle{myheadings}` la sostituiva prima del primo capitolo.
Tutta quella configurazione non aveva effetto.

**Un errore di una pagina nell'indice.** `\addcontentsline` era chiamato
*prima* di `\include`, quindi registrava il numero della pagina corrente ---
l'ultima del capitolo precedente --- e non quella su cui la bibliografia
comincia davvero. Lo stesso per i Ringraziamenti.

**Intervento.** `tesi/tesi.tex` riscritto: il formato e' definito in un solo
posto (`geometry`), l'interlinea con `setspace` e `\onehalfspacing`, che
corrisponde all'interlinea 1,5 di Word; `\linespread{1.5}` sarebbe stato
troppo, perche' su un corpo di 12 pt da' 21,8 pt, cioe' 1,8 volte il corpo.
Aggiunto `hyperref` (la tesi contiene 101 `\ref` e 38 `\cite`), tolti
`newlfont`, `epsfig`, `ifsym`, `soul`, `tikz`, `url` e `subfig` --- nessuno
usato in alcun capitolo, e `subfig` in conflitto con `caption` e `hyperref`.

**Non verificato con una compilazione**: su questa macchina non c'e' una
distribuzione LaTeX. Le tre correzioni sui nomi dei file e sulla codifica sono
verificate leggendo il disco; il layout e' calcolato, non compilato. Va
provato su Overleaf prima di considerarlo chiuso.

**Sul formato richiesto dall'ateneo.** Il DIISM non pubblica specifiche
tipografiche vincolanti: le linee guida di dipartimento riguardano scadenze,
procedura e lingua, e rimandano alle Avvertenze dell'Ufficio Studenti per il
frontespizio. Il vademecum UNISI che circola con «Times New Roman corpo 12,
interlinea 1 1/2» e' di un altro dipartimento e non vincola Ingegneria. I
valori scelti sono quindi una decisione, non un adempimento.

---


<a id="iss-131"></a>
### ISS-131 — La scomposizione del divario cross-dataset veniva da un altro esperimento

**Trovata:** 2026-09-03 · **Risolta:** 2026-09-03 · **Gravita': alta**

Il Capitolo 4 riportava $0{,}612$ come prestazione con **soglia oracolo** su
UR-Fall, e le Conclusioni scomponevano il crollo cross-dataset in «due terzi
taratura, un terzo perdita reale». L'artefatto di questo progetto,
`risultati/campo/pr_auc_allineato.json`, da' altri numeri.

Sono due esperimenti diversi, non due letture dello stesso:

| | impianto precedente | impianto attuale |
|---|---|---|
| file | `scripts/out/exp041_domain_shift.json` | `risultati/campo/pr_auc_allineato.json` |
| feature | `body_features_bodycentric.csv` | motore geometrico corretto |
| finestre / prevalenza | 1.125 / 0,128 | 1.075 / 0,094 |
| riferimento in dominio | **0,872** | 0,971 |
| $F_2$ alla soglia schierata | 0,073 | **0,034** |
| $F_2$ con soglia oracolo | **0,612** | **0,492** |
| quota di taratura | 67,5% | **48,8%** |
| perdita che resta | 32,5% | **51,2%** |

**Il difetto e' doppio.** Primo: il riferimento in dominio dell'esperimento
vecchio e' $0{,}872$, cioe' proprio il valore che [ISS-129](#iss-129) ha
mostrato appartenere a un modello diverso --- quindi la scomposizione
poggiava su un termine sbagliato. Secondo: dei due esperimenti il testo
prendeva la tabella del trasferimento dal nuovo (3,4x / 3,6x / 5,1x,
$F_2 = 0{,}630$) e la soglia oracolo dal vecchio, mescolandoli nella stessa
sezione.

**Che cosa cambia nella sostanza.** «Due terzi taratura» diceva che il crollo
e' soprattutto un problema di scala, correggibile ritarando. Sui dati attuali
la divisione e' **quasi esatta a meta'**: meta' si recupererebbe ritarando,
meta' e' perdita di capacita' discriminativa che nessuna soglia recupera.

**Ed e' la lettura coerente con il resto del capitolo.** La PR-AUC su UR-Fall
vale $1{,}79$ volte il caso contro $18{,}7$ in dominio, e il testo gia'
concludeva che «c'e' perdita reale della capacita' di separare». Con «due
terzi taratura» il capitolo si contraddiceva a due pagine di distanza; con la
divisione a meta' le due affermazioni dicono la stessa cosa.

**Intervento.** Il Capitolo 4 riporta ora $0{,}492$ e la scomposizione
completa, ricalcolabile dal file. Le Conclusioni passano da «due terzi / un
terzo» a «49% / 51%». L'esperimento di taratura per percentile --- che
recupera il 70% del divario di taratura --- resta citato ma **attribuito
all'impianto precedente**, perche' sull'artefatto attuale non e' stato
rifatto. Corretto anche `docs/RISPOSTE_AL_RELATORE.md`, che oltre a questo era
fermo a prima di ISS-129.

**Verificato con:** ricalcolo dai due JSON, riportato sopra riga per riga.

**Collegamenti:** [ISS-129](#iss-129), [ISS-126](#iss-126)

---

<a id="iss-130"></a>
### ISS-130 — Il registratore dichiarava venti secondi di stallo su sessantotto minuti di sospensione

**Trovata:** 2026-09-01 · **Gravita': alta** · **Stato: superata dal codice
attuale, conservata perche' e' la prova che il rimedio serviva**

Producendo la figura del profilo di sessione e' emersa nei dati
un'interruzione che nessun riepilogo dichiarava. Sulla sessione
`20260811/bloccodurata5h`, fra due finestre consecutive di `punteggi.csv`:

| | |
|---|---|
| ultima finestra prima del buco | **16:03:30** |
| prima finestra dopo il buco | **17:11:12** |
| interruzione | **67,7 minuti** |
| ampiezza da capo a coda | 6,11 ore di orologio |
| somma degli intervalli sotto il minuto | **4,98 ore** |

Il `riepilogo.json` scritto dalla board sulla stessa sessione dichiara:

```
"durata_h": 4.991,  "tempo_effettivo_h": 4.986,
"stalli": 1,  "stallo_totale_s": 20.0,  "stallo_massimo_s": 20.0
```

**Uno stallo di venti secondi**, su sessantotto minuti di assenza. E una
durata di 4,99 ore che e' esatta --- come *tempo di registrazione* --- e per
questo non insospettisce nessuno.

**Il meccanismo del difetto.** Il contatore sommava il tempo in cui il
programma era attivo. Un programma sospeso **non conta il tempo in cui non
gira**: al risveglio riprende, il conteggio riparte, e il riepilogo esce
coerente con se stesso. Non c'e' un valore sbagliato da cercare --- c'e' un
valore giusto che risponde a una domanda diversa da quella che il lettore
crede di porre.

**Perche' e' registrata anche se il codice attuale non ha piu' il difetto.**
`deploy_board/rileva.py` porta dal 26 agosto **due orologi** --- l'ora di
sistema, che avanza anche durante la sospensione, e un cronometro monotono che
no --- e dichiara la loro differenza in ogni riepilogo. Questa scheda e' la
misura di quanto quel rimedio serviva: **senza, una prova di durata puo'
perdere un'ora su sei e chiudersi con un riepilogo che sembra sano.** E' la
ragione per cui la prova da dodici ore non va fatta con il registratore
vecchio.

**Un secondo effetto, sui numeri gia' pubblicati.** Il tasso di allarmi di
questa sessione e' calcolato su 4,99 ore, che e' il denominatore giusto: le
finestre non esistono durante la sospensione, quindi ne' numeratore ne'
denominatore la contengono. **I numeri restano validi**, e questa e' la sola
ragione per cui il difetto non ne invalida nessuno.

**Verificato con:** ricalcolo degli intervalli fra finestre consecutive di
`risultati/sessioni/20260811/bloccodurata5h_20260811_130411/punteggi.csv` ->
una sola interruzione sopra il minuto, 67,7 minuti; `riepilogo.json` della
stessa sessione riletto.

**Collegamenti:** [ISS-113](#iss-113)

---

<a id="iss-129"></a>
### ISS-129 — Il divario fra le due viste confrontava due modelli diversi

**Trovata:** 2026-09-01 · **Risolta:** 2026-09-01 · **Gravita': alta**

La tabella del trasferimento fra punti di vista del Capitolo 4 e' introdotta da
«con la configurazione poi effettivamente installata sul dispositivo (foresta
casuale a 50 alberi...)», e riportava:

| addestrata | verificata | F2 dichiarato | run che lo produce |
|---|---|---|---|
| Camera1 | Camera1 | 0,872 ± 0,099 | **nessuna** |
| Camera1 | Camera2 | 0,434 ± 0,182 | `rf_A3_L22_cam1to2_ds_cam1to2` |
| Camera1+2 | Camera2 | 0,678 ± 0,123 | `rf_A3_L22to2_ds_both` |

Le righe due e tre coincidono **alla quarta cifra** con le rispettive run della
foresta. **La prima no.** La foresta su Camera1, stessa configurazione, e'
`rf_A3_L22_cam1_arch50` e vale **0,857 ± 0,088**. Il valore 0,872 appartiene a
run diverse --- `gru_A3_L22_cam1_arch` da' 0,873, la *precisione* della foresta
vale 0,872 --- e in nessun caso e' l'F2 della foresta.

**Il capitolo si contraddiceva da solo, mezza pagina sopra.** Il paragrafo
immediatamente precedente dice: «ripetendo l'esperimento sulla sola Camera1, a
parita' di tutto il resto, l'F2 passa da 0,29 a **0,857**». Il numero giusto era
gia' nel testo, due paragrafi prima della tabella che ne riportava un altro.

**Perche' pesa piu' di un refuso.** Da quella riga discende il numero piu'
citato del lavoro:

| grandezza | diceva | vale |
|---|---:|---:|
| divario fra le due viste | 0,438 | **0,422** |
| recupero addestrando su due viste | 56% | **58%** |
| divario residuo | 0,194 | **0,178** |
| rapporto sul divario fra architetture | «quasi sette volte» | **piu' di sei volte** |

Il divario e' il metro rispetto a cui il lavoro dichiara che l'architettura non
decide, e compariva in Introduzione, Cap. 4, Cap. 5 e due volte nelle
Conclusioni. **Un divario fra due righe ottenute con modelli diversi non misura
il punto di vista**: misura il punto di vista piu' la differenza fra i modelli.

**Che cosa non cambia.** La conclusione regge e si rafforza: 0,422 resta oltre
sei volte l'intervallo di 0,066 entro cui cadono le architetture, e le righe due
e tre --- da cui viene il risultato sul recupero --- erano gia' corrette.

**Intervento.** Prima riga corretta a 0,857 ± 0,088, con la colonna dei falsi
positivi completata (57). I tre derivati ricalcolati e allineati in tutti i
punti. La tabella e' diventata una **tabella vera**, con didascalia, etichetta
`tab:viste` e la dichiarazione che tutte e tre le righe sono lo stesso modello.
Gli artefatti sono stati consolidati in
`risultati/cinque_soggetti/viste_cinque_soggetti.json`, che chiude per questa
misura [ISS-126](#iss-126).

**Verificato con:** `python _estrai_viewpoint.py` in `DIP_PROJECT` ->
i tre `run_metadata.json` riletti; falsi positivi 57 / 1.113 / 460, che
corrispondono ai due valori gia' nel testo; F2 per fold su Camera2
0,42 / 0,28 / 0,77 / 0,27 / 0,42, coerenti con «su due soggetti su cinque
scendeva a 0,28». `python tesi/controlla.py` -> «Nessun problema».

**Collegamenti:** [ISS-126](#iss-126), [ISS-111](#iss-111), [ISS-128](#iss-128)

---

<a id="iss-128"></a>
### ISS-128 — Due tabelle del Capitolo 3 venivano dall'impianto precedente

**Trovata:** 2026-09-01 · **Risolta:** 2026-09-01 · **Gravita': alta**

Ricalcolando da `feature_v2.csv` le tre tabelle descrittive del Capitolo 3
(`pipeline/statistiche_cap3.py`, nuovo), **una si riproduce e due no**.

| tabella | il testo diceva | il ricalcolo da' |
|---|---|---|
| durata delle fasi | 0,92 / **3,11** / 5,97 s | 0,94 / **3,11** / 5,89 s |
| autocorrelazione, derivate | 0,18--0,44 | **0,33--0,47** |
| autocorrelazione, integrali | 0,91--0,94 | **0,95--0,98** |
| rapporto fra le mediane | 30,1x / 42,5x / 33,0x / 139,4x | 5,2x--26,2x (derivate), 7,2x--90,4x (integrali) |

**La prova che venissero da un altro impianto e' dentro la tabella stessa.**
Fra le quattro derivate dell'autocorrelazione c'era **«Energia del corpo»**, che
**non esiste fra le trentadue grandezze** del motore geometrico attuale:
`energy` era una feature del progetto precedente --- proprio quella con la scala
646 volte piu' grande delle altre, causa di ISS-008. Una tabella che elenca una
grandezza ritirata stava in un capitolo che descrive il feature set nuovo.

Per il rapporto fra le mediane la causa e' diversa e altrettanto concreta: il
confronto dichiarato era **transizione contro sdraiarsi volontario**, e
`feature_v2.csv` non lo permette --- porta due sole categorie, `adl` e `fall`, e
gli identificativi delle undici attivita' di UP-Fall non sono stati conservati
in estrazione.

**Che cosa NON cambia.** Nessuna delle tre conclusioni si muove: le derivate
restano molto meno autocorrelate delle integrali e ora i due intervalli **non si
sovrappongono nemmeno**; la transizione separa di uno o due ordini di grandezza
e lo stato a terra no, con tutti i rapporti della seconda colonna fra 0,4 e 1,6.
Cambia che ora esiste un file che li produce.

**Intervento.** Le tre tabelle sono state rifatte sui valori ricalcolati, con la
definizione dichiarata in didascalia; «Energia del corpo» e' stata ritirata; il
confronto con lo sdraiarsi volontario e' dichiarato come non riproducibile da
questi dati invece di essere riportato. L'intervallo 0,18--0,44 compariva anche
nel Capitolo 5 e nelle Conclusioni: allineato in entrambi.

**Questa e' la terza volta che quell'intervallo cambia.** [ISS-118](#iss-118) lo
aveva trovato citato come 0,18--0,44 nel Cap. 3 e 0,11--0,41 nel Cap. 5, e li
aveva allineati sul primo. Il primo era a sua volta sbagliato: allineare due
numeri fra loro non li rende veri, e la sola verifica che conta e' il ricalcolo
alla sorgente.

**Verificato con:** `python pipeline/statistiche_cap3.py` -> 57.786 fotogrammi,
109 riprese, 50 con caduta, 10 soggetti, 91,61% di pose valide;
`python tesi/controlla.py` -> «Nessun problema».

**Collegamenti:** [ISS-118](#iss-118), [ISS-126](#iss-126), [ISS-123](#iss-123)

---

<a id="iss-126"></a>
### ISS-126 — Quattro famiglie di numeri dei capitoli 4 e 5 non hanno un artefatto

**Trovata:** 2026-09-01 · **Gravita': alta** · **Stato: APERTA**

Confrontando **483 numeri decimali** dei capitoli sperimentali contro tutti i
JSON di `risultati/`, alla stessa precisione con cui sono scritti
(`pipeline/audit_numeri.py`), **119 non si ritrovano alla sorgente**: 28 nel
Cap. 3, 40 nel Cap. 4, 41 nel Cap. 5, 10 nelle Conclusioni.

Il conteggio va letto per quello che e': lo strumento e' uno **screening**, non
una condanna. Molti orfani sono legittimi --- valori di letteratura, statistiche
calcolate dal CSV delle feature, conteggi di fotogrammi --- e vanno scremati a
mano. Ma quelli del Capitolo 5 non sono sparsi: formano **quattro gruppi**, e
tutti e quattro hanno la stessa causa.

| gruppo | esempi | dove nasce |
|---|---|---|
| **bilancio del costo edge** | 1,21 / 33,34 / 0,94 / 2,20 ms; 3,2 / 88,4 / 2,5 / 5,8 %; 26,5 fps; 12,14 ms; 12,9x | trascritto da terminale — gia' [ISS-113](#iss-113) |
| **confronto fra stimatori di posa** | 99,5 / 43,6 / 79,1 / 58,9 % di ritenzione; 83,5 e 100,7 pixel; $-0{,}216$ di F2 | impianto a cinque soggetti, `DIP_PROJECT` |
| **scansione di $K$** | $0{,}896 \pm 0{,}090$, $0{,}928 \pm 0{,}048$, $0{,}963 \pm 0{,}016$; 156,7 / 137,6 / 17,3 allarmi/ora | idem: in `risultati/` esiste **solo** $K = 31$ |
| **effetto del punto di vista** | $0{,}872 \to 0{,}434$, e quindi il divario $0{,}438$ | idem |

**L'ultimo e' il piu' serio.** Il divario di **0,438 di F2 fra le due viste**
e' l'affermazione piu' citata del lavoro: compare nel Cap. 4, nel Cap. 5 e due
volte nelle Conclusioni, ed e' il termine di paragone rispetto a cui si dichiara
che l'architettura non conta. In `risultati/` non c'e' alcun file che lo
produca: `cinque_soggetti/exp013_camera_viewpoint.csv` contiene gli **angoli**,
non le due prestazioni.

**Non significa che i numeri siano sbagliati.** Significa che oggi non sono
rifacibili, e che se qualcuno li contestasse non ci sarebbe niente da mostrare
oltre al testo. E' la stessa forma di ISS-113, con la differenza che qui il
numero e' quello di intestazione.

**Seguito del 2026-09-01.** Tre dei quattro gruppi hanno ora un artefatto:
`risultati/cinque_soggetti/viste_cinque_soggetti.json` (trasferimento fra
viste, e nel copiarlo e' emersa [ISS-129](#iss-129)) e
`scansione_k_cinque_soggetti.json` (scansione di $K$ e confronto fra
stimatori). Quindici righe su diciassette coincidono alla terza cifra.

**Due righe non corrispondono ad alcuna run trovata** e restano da chiarire:
la riga $K = 9$ della scansione ($0{,}896 \pm 0{,}090$, 21 falsi negativi) e
la riga «MediaPipe @ 18 fps» della tabella delle catene ($0{,}898$, 23, 24).
Non sono state modificate: correggere un numero verso un altro numero non
verificato sarebbe peggio che lasciarlo dichiarato come non rintracciato.

Resta senza artefatto il **bilancio del costo edge**, che dipende da
[ISS-113](#iss-113) e quindi dalla prova di durata.

**Intervento previsto**, in ordine di costo:
1. i tre gruppi a cinque soggetti hanno i loro artefatti in `DIP_PROJECT`:
   vanno **copiati** in `risultati/cinque_soggetti/` come e' stato fatto per
   `exp013` e `exp017`, con il LEGGIMI che dichiara la numerosita';
2. il bilancio edge esce dalla prova di durata ([ISS-113](#iss-113));
3. dove un artefatto non esiste piu', il testo deve **dichiarare la
   provenienza** invece di riportare il numero come se fosse riproducibile.

**Verificato con:** `python pipeline/audit_numeri.py` -> 28 orfani su 96 nel
Cap. 3, 40 su 205 nel Cap. 4, 41 su 148 nel Cap. 5, 10 su 34 nelle Conclusioni.

**Nota su come e' stato trovato questo difetto**, perche' e' istruttivo. La
prima versione dell'audit arrotondava i valori dei file a zero decimali, e con
4.500 valori raccolti **quasi ogni numero del testo trovava un riscontro per
caso**: dichiarava «Cap. 4: zero orfani». Era uno strumento che dava sempre
ragione. La versione calibrata confronta alla stessa precisione con cui il
numero e' scritto. Il primo conteggio finito in questa scheda veniva dalla
versione sbagliata ed e' stato corretto lo stesso giorno.

**Collegamenti:** [ISS-113](#iss-113), [ISS-123](#iss-123)

---

<a id="iss-127"></a>
### ISS-127 — Trentadue tabelle su quaranta non sono tabelle

**Trovata:** 2026-09-01 · **Gravita': media** · **Stato: APERTA**

Inventario degli ambienti nei tre capitoli sperimentali
(`pipeline/inventario_figure.py`):

| capitolo | `tabular` | dentro un `table` con didascalia ed etichetta |
|---|---:|---:|
| Cap. 3 | 8 | 6 -> **8 su 8** (2026-09-01) |
| Cap. 4 | 15 | 2 -> **15 su 15** (2026-09-01) |
| Cap. 5 | 17 | 0 -> **17 su 17** (2026-09-01) |

Le altre trentadue sono `tabular` inseriti nel testo: **compilano**, si
leggono, e non hanno numero, didascalia ne' etichetta. Ne segue che non si
possono richiamare («come mostra la Tabella 4.3»), non compaiono nell'elenco
delle tabelle, e il lettore che torna indietro a cercarne una non ha un numero
a cui riferirsi.

Fra queste ci sono i risultati portanti: il confronto fra le sei architetture,
il bilancio del costo per fotogramma, la tabella dei tre compiti misurati in
casa, e la scansione della finestra di accumulazione. **Il Capitolo 5 non ha
una sola tabella numerata**, ed e' il capitolo con piu' dati tabellari.

**Intervento previsto:** ogni `tabular` che porta un risultato diventa un
`table` con `\caption` e `\label{tab:...}`, e il testo lo richiama con
`\ref`. Restano `tabular` inline solo gli elenchi di servizio di due o tre
righe che non sono risultati.

**Risolta il 2026-09-01.** Quaranta tabelle su quaranta sono ora numerate,
con didascalia ed etichetta. Nelle didascalie e' stata messa anche la
**provenienza** dove non era ovvia --- «impianto a cinque soggetti»,
«ricalcolabile da...», «trascritto da terminale» --- perche' e' l'informazione
che il lettore cerca quando torna a una tabella, e stava sparsa nel testo.

**Verificato con:** `python pipeline/inventario_figure.py` -> Cap. 3 8/8,
Cap. 4 15/15, Cap. 5 17/17; `python tesi/controlla.py` -> «Nessun problema».

**Collegamenti:** [ISS-107](#iss-107)

---

<a id="iss-125"></a>
### ISS-125 — Settemila righe di codice senza una sola prova automatica

**Trovata:** 2026-09-01 · **Risolta in parte:** 2026-09-01 · **Gravita': alta**

Il progetto non aveva **alcuna** prova automatica. Tre funzioni, se sbagliate,
non producono un'eccezione ma un numero: il motore geometrico, che genera le
grandezze da cui viene ogni misura; `etichetta_finestra`, che decide che cosa
sia un positivo; e l'aggregazione delle finestre in eventi, che e' il fattore
47,8 gia' costato un numero sbagliato in relazione.

Una modifica a `geometry.py` cambia **tutti** i numeri della tesi in silenzio:
il codice gira, i risultati sono diversi da quelli scritti nel testo, e nulla
lo segnala. Con due copie del file tenute allineate a mano, la stessa cosa puo'
accadere fra calcolatore e board.

**Intervento.** `prove/`, 31 prove con `unittest` della libreria standard --
nessuna dipendenza nuova, gira in tutti e tre gli ambienti conda. Il motore
geometrico e' protetto da un file d'oro: quaranta fotogrammi sintetici,
costruiti analiticamente perche' la prova sia deterministica e non richieda
MediaPipe.

**Perche' «in parte».** Le prove coprono i tre punti ciechi, non il resto:
addestramento, trasferimento esterno e catena sulla board si verificano
eseguendoli. E il file d'oro fissa i valori **correnti**: dice che non
cambiano, non che siano giusti. Se il motore avesse gia' un difetto, la prova
lo conserverebbe --- il che e' comunque meglio di un difetto che cambia da una
run all'altra.

**Verificato con:** `python prove/esegui.py` -> 31 prove, OK.

**Collegamenti:** [ISS-113](ISSUES.md#iss-113), [ISS-106](ISSUES.md#iss-106)

---

<a id="iss-123"></a>
### ISS-123 — Cinque numeri epidemiologici del Capitolo 1 erano di un'altra edizione

**Trovata:** 2026-08-31 · **Risolta:** 2026-08-31 · **Gravita': alta**

I dati PASSI d'Argento della prima sezione del Capitolo 1 sono stati ricontrollati
sulla fonte. **Cinque valori su sette non corrispondono** al biennio dichiarato nel
testo e nella voce di bibliografia:

| grandezza | diceva la tesi | dice la fonte (2023--2024) |
|---|---:|---:|
| almeno una caduta in 12 mesi | «circa uno su cinque» | 20% — **corretto** |
| fascia 65--74 anni | 16% | **15%** |
| oltre gli 85 anni | 33% | **31%** |
| donne / uomini | 25% / 16% | **24% / 15%** |
| in casa | 60% | **54%** |
| in strada / in giardino | 19% / 11% | **20% / 21%** |
| ricovero di almeno un giorno | 14% | **16%** |

I valori sbagliati non sono inventati: sono quelli del **biennio 2022--2023**,
pubblicati il 31 ottobre 2024, dove la fascia 65--74 sta al 16%, gli ultra 85 al
33%, le donne al 25% contro il 16% degli uomini e i ricoveri al 16%. La
bibliografia dichiarava pero' il biennio **2023--2024**, e i numeri erano
dell'edizione precedente. La voce portava gia' un avviso — «ATTENZIONE: i
dettagli di edizione vanno confermati sulla fonte prima della consegna» — che
non era mai stato sciolto.

**Il caso peggiore e' il 60% in casa**, perche' non corrisponde ad alcuna delle
due edizioni: 2023--2024 dice 54%, 2022--2023 dice 64%. Era una terza cifra,
di provenienza ignota, usata per sostenere l'affermazione su cui poggia la
scelta dell'ambiente domestico.

**Intervento.** Tutti i valori vengono ora dal comunicato ISS del 31 ottobre
2025, biennio 2023--2024, e sono elencati uno per uno nel commento della voce
`passi` insieme a quelli che sostituiscono. L'argomento sul domicilio e' stato
riformulato in una forma che i dati sostengono e che e' anche piu' forte:
**casa e giardino insieme rendono conto di tre cadute su quattro.**

**Aggiunta [fleming]** — Fleming e Brayne, BMJ 2008;337:a2227 — perche' il
*long lie* era l'unica affermazione clinica del capitolo priva di riferimento.
Porta i numeri che rendono la tempestivita' un requisito e non una preferenza:
fra chi cade, l'80% non riesce a rialzarsi da solo almeno una volta, il 30%
resta a terra un'ora o piu', l'82% delle cadute avviene mentre la persona e'
sola, e i dispositivi di chiamata c'erano ma non sono stati usati.

**Verificato con:** comunicato ISS del 31-10-2025 e Rapporto annuale ISTAT
2026 riletti sulla fonte; `python tesi/controlla.py` -> «Nessun problema».

**Collegamenti:** [ISS-110](#iss-110), [ISS-124](#iss-124)

---

<a id="iss-124"></a>
### ISS-124 — Una voce di bibliografia fondeva due lavori diversi

**Trovata:** 2026-08-31 · **Risolta:** 2026-08-31 · **Gravita': alta**

La voce `kangas` portava il **titolo** di un lavoro — *Comparison of real-life
accidental falls in older people with experimental falls in middle-aged test
subjects* — e i **numeri** di un altro: «studio longitudinale su 15.500 ore di
utilizzo reale, tasso di falsi allarmi 0,049/ora». Sono due pubblicazioni
distinte degli stessi autori, e la prima e' gia' in bibliografia come
`kangasreali`.

**In piu' la voce affermava che il tasso era stato «ridotto a 0,025 dopo
revisione dell'algoritmo».** Quel valore **non e' stato trovato sulla fonte**
ed e' stato ritirato dal testo e dalla bibliografia. Non e' un riferimento
inventato come quelli di [ISS-114](#iss-114) — il lavoro esiste — ma
l'affermazione che gli veniva attribuita non risulta.

**Intervento.** La voce e' ora Kangas, Korpelainen, Vikman, Nyberg, Jämsä,
*Sensitivity and False Alarm Rate of a Fall Sensor in Long-Term Fall Detection
in the Elderly*, Gerontology 61 (2015), 61--68, DOI 10.1159/000362720, con i
soli numeri verificati: sedici anziani, 1.105 giornate, uso medio 14,2 ore al
giorno, quindici cadute reali, 0,049 falsi allarmi/ora.

Al posto della riduzione non verificata, il Capitolo 1 riporta ora quella
**documentata** di AIDE-MOI, dove entrambi i valori esistono: sensibilita' dal
27,3% all'80,0% e falsi allarmi da 0,43 a 0,17 per settimana e per soggetto,
su venti soggetti e trentuno cadute reali (Sensors 19(6):1357, 2019).

**Restano sedici voci mai verificate** sulle trentadue della bibliografia. Le
verificate sono ora undici: le sette del 25 agosto piu' `istat2026`, `passi`,
`fleming`, `kangas` e `aidemoi`. Delle prime sette, due affermazioni non
avevano retto; di queste cinque, due non hanno retto. **La proporzione non sta
migliorando, ed e' l'argomento per verificare le restanti.**

**Verificato con:** PubMed 25138139, Gerontology 61:61--68, e la scheda
Sensors 19(6):1357 riletti sulla fonte.

**Collegamenti:** [ISS-114](#iss-114), [ISS-123](#iss-123)

---

<a id="iss-122"></a>
### ISS-122 — Il Capitolo 2 dichiarava di non aver provato le reti a grafo

**Trovata:** 2026-08-31 · **Risolta:** 2026-08-31 · **Gravita': alta**

Il Capitolo 2 conteneva, in due punti, la dichiarazione che le reti a grafo non
erano state provate:

> «Questo lavoro confronta reti ricorrenti, convoluzioni temporali, un modello
> ad attenzione e un classificatore non sequenziale. **Le reti a grafo non
> vengono considerate**, e la dichiarazione vale quanto il confronto: non sono
> state provate, quindi su di esse il lavoro non dice nulla.»

> «Restano fuori, e vanno dichiarate: le reti a grafo, mai provate; [...]»

**Dal 27 agosto è falso.** Quel giorno una rete a grafo spazio-temporale è
stata aggiunta a `src/modelli.py`, addestrata in LOSO sui dieci soggetti con lo
stesso protocollo delle altre cinque, e confrontata fold per fold
([EXP-018](EXPERIMENTS.md#exp-018)). Il testo non è stato aggiornato, e la
sessione si è interrotta prima di registrare la run.

**Perché è grave.** È la terza occorrenza dello stesso modo di sbagliare, dopo
[ISS-110](#iss-110) e [ISS-117](#iss-117): il testo compila, si legge bene, e
l'affermazione non è vera. Qui in più l'affermazione è una **dichiarazione di
limite**, cioè una di quelle su cui il lavoro chiede di essere creduto. Una
dichiarazione di limite falsa costa più di un numero sbagliato.

**Intervento.** I due punti del Capitolo 2 dicono ora che la famiglia è
compresa nel confronto, con la precisazione che decide la portata del
risultato: **i nodi sono le dodici grandezze geometriche, non i giunti**, e
l'adiacenza è appresa. Ciò che resta fuori — ed è dichiarato — è la GCN
costruita sui giunti dello scheletro, che richiederebbe le coordinate dei
landmark e cambierebbe insieme modello e rappresentazione. Aggiornato anche il
commento in testa al file, che portava il criterio di rilevanza sbagliato, e la
sezione corrispondente di `docs/spiegazioni/00_PANORAMICA.md`.

**Verificato con:** `grep -n -i grafo tesi/*.tex` -> nessuna occorrenza residua
di «mai provate» o «non vengono considerate»; `python tesi/controlla.py` ->
«Nessun problema».

**Seguito del 2026-09-01.** La correzione era stata applicata al Capitolo 2, che
*dichiara*, e non al Capitolo 4, che *misura*: la tabella delle architetture, la
scansione di numerosita' e la figura sono rimaste a cinque per cinque giorni.
E' la terza volta che una correzione applicata in un punto lascia scoperta la
stessa affermazione altrove --- come [ISS-117](#iss-117) e [ISS-110](#iss-110).
**Un numero corretto in un capitolo non e' corretto nel lavoro**: la verifica
deve essere un `grep` su tutti i sorgenti, non sul file che si sta toccando.

**Collegamenti:** [EXP-018](EXPERIMENTS.md#exp-018),
[EXP-019](EXPERIMENTS.md#exp-019), [ISS-110](#iss-110), [ISS-117](#iss-117)

---

<a id="iss-121"></a>
### ISS-121 — La nota di provenienza del Capitolo 4 rivendicava una misura in piu'

**Trovata:** 2026-08-27 · **Risolta:** 2026-08-27 · **Gravita': media**

La sezione «Analisi di sensibilita'» del Capitolo 4 apriva con:

> «Provenienza delle misure di questa sezione. **Tutte e tre** risalgono
> all'impianto a cinque soggetti e non sono state ripetute dopo l'estensione a
> dieci.»

Le misure della sezione sono tre --- dimensione del modello, frequenza dei
fotogrammi, occlusioni --- ma **la terza e' a dieci soggetti**:
`risultati/occlusioni/foresta_DTW.json` dichiara `n_fold: 10` per ogni prova, e
la didascalia della figura nella stessa sezione dice gia' «sui risultati a
dieci soggetti».

**La nota contraddiceva quindi la figura che le stava sotto**, e nella
direzione che sminuisce il risultato: dichiarava provvisoria una misura che non
lo e'. E' il rovescio del difetto solito --- di norma un numero vecchio
sopravvive spacciandosi per nuovo, qui un numero buono si dichiarava vecchio.

**Intervento:** la nota nomina ora le due misure che vengono da cinque soggetti
e dichiara esplicitamente che la degradazione al mascheramento dei landmark e'
misurata su dieci, con validazione incrociata a dieci fold.

**Verificato con:** `n_fold` letto da `risultati/occlusioni/foresta_DTW.json`
per tutte le prove -> 10; base senza occlusione $F_2 = 0{,}857 \pm 0{,}078$,
che e' il valore della configurazione DTW a dieci soggetti riportato altrove
nel capitolo. `python tesi/controlla.py` -> «Nessun problema».

**Collegamenti:** [ISS-116](#iss-116)

---

<a id="iss-108"></a>
### ISS-108 — Il Capitolo 1 prometteva una misura di ritardo che non esiste

**Trovata:** 2026-08-26 · **Risolta:** 2026-08-27 · **Gravita': media**

Il Capitolo 1 dichiarava: «Per questa ragione il Capitolo~\ref{cap:campo}
misura esplicitamente il *ritardo* di rilevamento, e non soltanto se l'allarme
arrivi.» La parola «ritardo» non compariva nel capitolo di campo: zero
occorrenze. Il difetto era doppio --- una promessa non mantenuta nel testo, e
una delle quattro metriche operative chieste dal relatore non ancora eseguita.

**Come si e' chiusa, in due tempi e non per un intervento solo.**

1. **La misura e' stata fatta** ([EXP-017](EXPERIMENTS.md#exp-017),
   `pipeline/latenza.py`), e la risposta e' che **il ritardo fra caduta e
   allarme non e' misurabile** con questi dati: le cadute sono annotate al
   minuto, la grandezza da misurare e' di pochi secondi, e gli scarti osservati
   (+11,8 ... +32,3 s) misurano il punto del minuto in cui si e' caduti, non il
   ritardo del sistema.
2. **La promessa non c'e' piu' nel testo, ma non perche' sia stata riscritta:**
   e' sparita con l'installazione della versione del Capitolo 1 della candidata,
   il 26 agosto. Verificato il 27 agosto con
   `grep -n "ritard\|misura esplicit" tesi/Cap1.tex` -> nessuna occorrenza.
   Sono spariti con essa anche i due paragrafi che aprivano entrambi con
   «Questa osservazione ha una conseguenza...».

**Resta, e ha un numero proprio:** i valori della scomposizione non compaiono in
alcun capitolo. Vedi [ISS-115](#iss-115).

**Collegamenti:** [EXP-017](EXPERIMENTS.md#exp-017), [ISS-115](#iss-115)

---

<a id="iss-116"></a>
### ISS-116 — Il Capitolo 4 dichiarava i numeri di un impianto a cinque soggetti

**Trovata:** 2026-08-27 · **Risolta:** 2026-08-27 · **Gravita': alta**

La sezione «I numeri del problema» apriva con i valori a dieci soggetti
(57.786 fotogrammi, 109 riprese, 91,6% di pose valide, 11.510 finestre e 1.423
positive) e proseguiva con una tabella e due conteggi rimasti fermi
all'impianto precedente. Ricalcolati da `feature_v2.csv`, camera 1:

| affermazione nel testo | valore ricalcolato |
|---|---|
| etichette 25.552 / 1.463 / 2.483 --- 86,6 / 5,0 / 8,4 % | **49.691 / 2.771 / 5.324 --- 86,0 / 4,8 / 9,2 %** |
| «94,55% di finestre negative» | **87,64%**, complemento del 12,36% dichiarato tre righe sopra |
| «accuratezza superiore al 94%» | **superiore all'87%** |
| «con 344 finestre positive ... oltre il 94% dei dati» | **1.423 positive su 11.510 ... circa il 75%** |

Le due quote erano **internamente incompatibili**: 12,36% di positive e 94,55%
di negative non possono stare nello stesso insieme. I valori vecchi sono quelli
di camera 1 a **cinque** soggetti (29.498 fotogrammi, 6.313 finestre):
l'intestazione era stata aggiornata al raddoppio dei soggetti, il corpo no.

**Difetto minore nello stesso capitolo:** il massimo di `energy` era scritto
`$15{,}499$`, che con la virgola decimale italiana si legge «quindici e 499
millesimi» mentre il valore e' **quindicimila**. Corretto in `\num{15499}`,
che e' anche la forma usata dodici righe sopra per lo stesso numero.

**Verificato con:** ricalcolo da `dataset/processed/features/feature_v2.csv`
tramite `src.dati.carica` e `costruisci_finestre` --- 57.786 fotogrammi, 109
riprese, 10 soggetti, 91,61% di pose valide, 11.510 finestre, 1.423 positive
(12,36%). La somma della colonna «cadute nel test» della tabella dei fold, che
il capitolo riporta poche righe dopo, vale esattamente 1.423 e concorda.
`python tesi/controlla.py` -> «Nessun problema».

---

<a id="iss-117"></a>
### ISS-117 — I numeri ritirati di OmniFall erano sopravvissuti nel Capitolo 3

**Trovata:** 2026-08-27 · **Risolta:** 2026-08-27 · **Gravita': alta**

`tesi/Cap3.tex` descriveva OmniFall come «un benchmark del **2026** che unifica
otto dataset [...] per un totale di **101 soggetti e 29 punti di vista**».

Sono **esattamente i valori gia' trovati sbagliati e ritirati dal Capitolo 2 il
25 agosto** ([ISS-110](#iss-110)): l'abstract dichiara quindicimila riprese,
ottanta ore, sedici classi, ed e' del 2025 (arXiv:2505.19889). La correzione era
stata applicata al Capitolo 2, e l'avviso messo in testa a quel file soltanto,
mentre la stessa affermazione stava anche nel Capitolo 3.

E' la seconda occorrenza dello stesso difetto, ed e' la conferma di cio' che
ISS-110 dichiarava: **un numero ritirato in un punto non e' ritirato nel
lavoro**. La difesa --- un avviso accanto al numero --- va messa in **ogni**
punto in cui il numero compare, non nel file in cui e' stato corretto la prima
volta.

**Intervento:** valori riportati a quelli verificati, e avviso replicato in
`Cap3.tex` nella stessa forma di quello di `Cap2.tex`.

**Verificato con:** ricerca di «101 soggetti», «29 punti di vista», «29 viste»
e «benchmark del 2026» su tutti i `.tex` -> nessuna occorrenza residua fuori
dai commenti che ne vietano il rientro.

**Collegamenti:** [ISS-110](#iss-110)

---

<a id="iss-118"></a>
### ISS-118 — La stessa misura citata con due intervalli diversi in tre capitoli

**Trovata:** 2026-08-27 · **Risolta:** 2026-08-27 · **Gravita': media**

L'autocorrelazione a un passo delle grandezze dinamiche compariva in tre punti
del lavoro con **due valori diversi**:

| dove | derivate | statiche |
|---|---|---|
| `Cap3.tex`, tabella e testo | **0,18 -- 0,44** | «intorno a 0,9» |
| `Cap5.tex`, modi di fallire | 0,11 -- 0,41 | 0,84 -- 0,93 |
| `Conclusioni.tex`, contributo 6 | 0,11 -- 0,41 | 0,84 -- 0,93 |

La coppia 0,11--0,41 viene dalla misura sull'impianto precedente, su A3 a dieci
colonne, ed e' quella riportata nella lettera al relatore del 17 agosto, dove la
velocita' angolare del tronco vale 0,110. La tabella del Capitolo 3 e' invece la
misura che la tesi **mostra**; e il valore degli integrali che le tre sedi
citano --- 0,91--0,94 --- e' gia' quello del Capitolo 3: era disallineata solo
meta' della frase.

**Intervento:** Capitolo 5 e Conclusioni allineati alla tabella del Capitolo 3.
Non il contrario: si cita il numero che il lettore puo' vedere.

**Da non rifare:** l'intervallo delle grandezze statiche resta «intorno a 0,9»,
che e' cio' che il Capitolo 3 afferma. Il `0,84--0,93` non ha una tabella dietro
in questo impianto, e sostituirlo con un altro intervallo preciso avrebbe
rifatto il difetto con numeri nuovi.

---

<a id="iss-119"></a>
### ISS-119 — La docstring del motore geometrico sosteneva l'argomento smentito

**Trovata:** 2026-08-27 · **Risolta:** 2026-08-27 · **Gravita': media**

`src/geometry.py` dichiarava, in testa: «un accumulo lo cancella, perche' il
rumore a media nulla si somma a zero mentre il movimento vero si somma».

**E' l'argomento che `pipeline/rumore.py` e il Capitolo 3 dichiarano
esplicitamente falso** per queste tre grandezze: percorso, escursione e discesa
sono funzioni **monotone crescenti** del rumore, perche' sommano valori
assoluti, allargano un intervallo e abbassano un minimo. Cio' che le rende
preferibili alle derivate non e' la robustezza, e' la **regolarita'**.

Il calcolo era ed e' corretto: il difetto stava solo nel commento --- ma e' il
commento che si legge per capire perche' il codice fa cosi', ed era la terza
sede in cui la stessa affermazione smentita sopravviveva.

**Intervento:** docstring riscritta con l'argomento corretto, i valori di
autocorrelazione (0,91--0,94 contro 0,18--0,44) e il rimando a
`pipeline/rumore.py`, compresa la vulnerabilita' vera --- l'ambiguita' di posa,
93,5 gradi di escursione su una persona ferma contro 60,7 di una caduta.
**La copia sulla board e' stata riallineata**: i due file erano identici, e
`deploy_board/geometry.py` sarebbe rimasta l'unica copia con il testo vecchio.

**Verificato con:** `diff src/geometry.py deploy_board/geometry.py` -> identici;
importazione della copia della board -> 32 grandezze, K predefinito 31.

---

<a id="iss-120"></a>
### ISS-120 — Rimandi che puntavano al posto sbagliato

**Trovata:** 2026-08-27 · **Risolta:** 2026-08-27 · **Gravita': bassa**

Tre casi, trovati con un controllo automatico delle ancore dei registri.

1. **[EXP-016](EXPERIMENTS.md#exp-016)** citava `EXP-014` come fonte della
   parita' sulle finestre precalcolate. EXP-014 e' l'estrazione di UR-Fall: la
   parita' non e' una run del registro, e' la prova del pacchetto esportato.
   Rimando sostituito con `deploy_board/parita.npz`.
2. **[ISS-105](#iss-105)** rimandava a `#iss-004` **dentro questo file**, dove
   la numerazione parte da 100. ISS-004 sta nel progetto storico: percorso
   corretto.
3. **`PROJECT_CONTEXT.md`** dichiarava «`tesi/` contiene il testo: otto
   capitoli» e, due paragrafi sotto, «Cinque capitoli, non otto».

**Nello stesso giro:** `docs/INDICE_E_STRUTTURA.txt`, che e' il documento per il
relatore, **propone una struttura che non e' quella applicata** --- proponeva di
fondere contesto e stato dell'arte, e non e' stato fatto: sono i capitoli 1 e 2.
Non e' stato riscritto, perche' e' un documento datato e firmato: gli e' stata
messa in testa una nota che dichiara la struttura in vigore e che **la domanda A
in coda e' superata dai fatti**.

---

<a id="iss-111"></a>
### ISS-111 — Il fattore fra le due viste non si riproduceva dal file citato

**Trovata:** 2026-08-26 · **Risolta:** 2026-08-26 · **Gravita': media**

Il capitolo dichiarava $1{,}90	imes$ e «tre sequenze su 24»; il file indicato
come sorgente dava altro. Rileggendo il capitolo per intero e' emerso che i
valori discordanti non erano due ma **quattro**, tutti dentro due paragrafi
consecutivi.

| affermazione nel testo | valore dal file |
|---|---|
| medie 71,0 / 35,7 gradi | corretto |
| 18 su 25 e 6 su 25 sopra i 60 gradi | corretto |
| rapporto delle medie 1,99 | corretto |
| deviazioni standard 25,3 e 24,4 | **25,8 e 24,9** |
| rapporto per sequenza da 0,33 a 13,22 | **da 0,39 a 6,21** |
| «in 3 casi su 24» | **2 su 25** |
| «rieseguendo si ottiene 1,90» | **1,99** |

Il paragrafo che doveva *correggere* il valore preliminare di $4{,}32	imes$
ne dichiarava uno diverso da quello riportato dodici righe sopra, e diceva
«il valore di riferimento e' quello riportato sopra».

**Intervento.** I quattro valori sono stati riportati a quelli calcolati da
`risultati/cinque_soggetti/exp013_camera_viewpoint.csv`. La menzione di una
«misura indipendente che conferma 1,90» e' stata **ritirata**: non e'
verificabile, e il file dichiarato come sorgente dice 1,99. Il paragrafo di
correzione ora nomina il file e dichiara che la correzione dimezza l'effetto
senza cambiarne la direzione.

Con il testo allineato, `fig_viewpoint_dist.png` **e' stata inserita**: le
figure mancanti passano da tre a una.

**Verificato con:** ricalcolo di tutti e sette i valori dal CSV;
`python tesi/controlla.py` -> «Nessun problema».

---

<a id="iss-109"></a>
### ISS-109 — Le rappresentazioni si chiamavano A1 nella tesi e A nella lettera

**Trovata:** 2026-08-26 · **Risolta:** 2026-08-26 · **Gravita': bassa**

Il codice usa `A1` (`src/geometry.py:92`, colonne con prefisso `A1_`), il
Capitolo 3 usava `A1` nei titoli ma `A (PCA 2D)` nella tabella dei landmark, e
il Capitolo 4 usava `A (PCA 2D)` nella tabella delle rappresentazioni. Tre
nomi per la stessa cosa, in due capitoli e una tabella.

**Intervento.** Adottato `A1` ovunque, con la forma discorsiva usata nei
titoli: «A1 --- descrittori della sagoma», «A2 --- descrittori
tridimensionali», «A3 --- descrittori riferiti al corpo». Nessun residuo di
`A (PCA 2D)`, `physics 3D`, `body-centric 2D`.

**Resta da sapere** che la lettera al relatore del 17 agosto dichiarava «non
esiste un A1, il primo e' semplicemente A». Se la nomenclatura torna in
discussione con lui, la tesi usa `A1` e il codice pure.

---


<a id="iss-112"></a>
### ISS-112 — Le soglie di etichettatura erano dichiarate in due posti

**Trovata:** 2026-08-26 · **Risolta:** 2026-08-26 · **Gravita': media**

`config.py` dichiarava `CADUTA_MIN_FOTOGRAMMI = 5` e `TRANSIZIONE_MAX = 10`;
`src/etichettatura.py` aveva i propri default `k_caduta=5, m_blocco=8,
k_terra=10, m_terra=15`; nessuno collegava i due, e i chiamanti non passavano
nulla. `pipeline/addestra.py` scriveva pero' nel `run_metadata.json` i valori
di `config`: **il file che serve a rendere una run rifacibile dichiarava
parametri che non la governavano**. Le due ampiezze di blocco, che rendono il
criterio «K su M» invece di «K totali», non erano registrate da nessuna parte.

**Intervento.** Le quattro soglie stanno ora in `config.py` con **gli stessi
nomi dei parametri della funzione**, raccolte in `SOGLIE_ETICHETTATURA`;
`etichetta_finestra` le legge da li' quando l'argomento e' `None`, e un
valore passato esplicitamente continua a prevalere; `addestra.py` registra il
dizionario intero. Le due costanti vecchie sono state rimosse: nessun
riferimento residuo.

**Verificato con:** `etichetta_finestra` su sequenze costruite --- 5
fotogrammi consecutivi di classe 1 -> `1`; 4 -> `0`; 10 di classe 2 -> `2`;
con `k_caduta=4` esplicito, 4 -> `1`. **Comportamento identico a prima**, che
era il requisito: la correzione non doveva cambiare alcun risultato gia'
prodotto.

---


<a id="iss-114"></a>
### ISS-114 — Tre riferimenti di bibliografia non corrispondono a lavori reali

**Trovata:** 2026-08-26 · **Risolta:** 2026-08-26 · **Gravita': alta**

`asif`, `zobi` e `gazem` erano segnaposto marcati `[DA CERCARE]`, con autore e
titolo plausibili e un `TODO: recuperare titolo completo, autori e sede`.
Erano citati nel testo: `gazem` nel Capitolo 2, `asif` e `zobi` nel Capitolo 1
--- questi ultimi aggiunti lo stesso 26 agosto durante l'installazione del
Capitolo 1, per non lasciare voci orfane, senza controllare che cosa fossero.

**Intervento.** Le tre voci sono state ritirate da `Bibliografia.tex` e le
citazioni tolte dal testo. **Nessuna e' stata riattaccata a un altro
riferimento**: sostituire un riferimento non verificato con un altro scelto
in fretta produce lo stesso difetto con un nome diverso. Le tre affermazioni
sono state riscritte in modo da reggere da sole:

| voce | affermazione | come regge ora |
|---|---|---|
| `asif` | le rappresentazioni pose-based sono invarianti all'aspetto | riscritta come conseguenza dell'architettura: volto, texture e abbigliamento non raggiungono il classificatore, quindi il modello non puo' apprenderli. E' vera per costruzione |
| `zobi` | lo stimatore perde landmark sotto occlusione | rimando in avanti al capitolo che lo **misura**, senza anticipare il numero |
| `gazem` | i wearable dipendono dalla compliance | citazione tolta; la frase resta, ed e' gia' attribuita alla famiglia dalla rassegna citata a inizio sezione |

In testa a `Bibliografia.tex` c'e' ora un avviso che dice di non
reinserirle e che un eventuale riferimento va **verificato sulla fonte**.

**Verificato con:** `python tesi/controlla.py` -> «Nessun problema»; nessuna
citazione non definita; l'elenco delle voci mai citate e' invariato
(`gru`, `lstm`, `noury`, `randomforest`, `rougier`).

**Collegamenti:** [ISS-110](#iss-110)

---


<a id="iss-104"></a>
### ISS-104 — Quattro grandezze A2 misuravano l'origine del riferimento

**Trovata:** 2026-08-20 · **Risolta:** 2026-08-20 · **Gravita': alta**

`src/geometry.py`, metodo `a2()` e chiamata a `_integrali('A2', ...)`.

I world landmark di MediaPipe sono **centrati sul punto medio delle anche**: il
bacino e' l'origine del sistema di riferimento e non si muove per costruzione.
Misurato su 40 fotogrammi consecutivi:

```
bacino  dev.std   [0,000034  0,000047  0,000046]  m   <- 0,03 mm
naso    dev.std   [0,012700  0,002712  0,017535]  m   <- 400 volte tanto
```

Quattro grandezze misuravano quindi rumore numerico:

| grandezza | max misurato | destino |
|---|---:|---|
| `A2_hip_vy` | 0,000 | rimossa |
| `A2_hip_vel` | 0,1 | rimossa |
| `A2_percorso` | 7,6 | ridefinita sul naso |
| `A2_discesa` | 1,4 | ridefinita sul naso |

**Aggravante: la grandezza degenere era stata SELEZIONATA.** `A2_percorso` era
entrata fra le dodici scelte di [EXP-006](EXPERIMENTS.md#exp-006), al nono
posto, e la sua bassa correlazione con `A1_percorso` (0,25) e `A3_percorso`
(0,30) era stata interpretata come «porta la componente in profondita'». Era
indipendente perche' era rumore, e il rumore non correla con niente. E' il
modo tipico in cui una grandezza degenere supera un filtro di ridondanza.

**Intervento.** `A2_hip_vy` e `A2_hip_vel` rimosse: la traslazione assoluta del
corpo con i world landmark non e' misurabile, e la misurano gia' A1 e A3 nel
piano immagine. `A2_percorso` e `A2_discesa` ridefinite sul **naso**, la cui
posizione in coordinate world e' gia' relativa alle anche, quindi e' un
movimento vero. Verificata anche la direzione dell'asse y: cresce verso il
basso come nel piano immagine (naso y = −0,55, caviglie y = +0,68 su persona
eretta).

**Verificato con:** riestrazione completa
([EXP-007](EXPERIMENTS.md#exp-007)) — 30 colonne identiche bit per bit fra v1 e
v2, solo le due ridefinite cambiate; e nuova analisi DTW
([EXP-008](EXPERIMENTS.md#exp-008)), dove le due riabilitate entrano al secondo
e terzo posto della classifica.

---

<a id="iss-100"></a>
### ISS-100 — Periodo di srotolamento sbagliato per l'angolo dell'ellisse

**Trovata:** 2026-08-19 · **Risolta:** 2026-08-19 · **Gravita': alta**

`src/geometry.py`, funzione `_srotola`. L'angolo veniva srotolato con periodo
360 gradi per tutte le grandezze angolari, incluso l'asse maggiore
dell'ellisse.

L'asse di un'ellisse e' una **direzione, non un verso**: ha periodo 180 gradi.
Con il periodo sbagliato la serie presentava salti artificiali — misurato un
passaggio 201,9 -> 49,5 gradi fra due fotogrammi consecutivi, cioe' una
rotazione di 152 gradi in un diciottesimo di secondo, fisicamente impossibile.
Ogni salto si propagava sulla derivata e sugli integrali accumulati.

**Intervento:** `incl = _srotola(incl, p_inc, periodo=180.0)` per l'inclinazione
dell'ellisse; le grandezze vettoriali mantengono 360.

**Verificato con:** riestrazione del pilota, i salti spuri spariti dalla serie.

---

<a id="iss-101"></a>
### ISS-101 — Il vincolo di warping si allargava sulle coppie incrociate

**Trovata:** 2026-08-19 · **Risolta:** 2026-08-19 · **Gravita': alta**

`src/dtw.py`, funzione `dtw`: `window=max(finestra, abs(n - m))`.

L'allargamento e' necessario — con `|n - m|` maggiore della banda nessun
cammino di allineamento arriva in fondo — ma su questo dataset produceva un
effetto perverso. Le riprese di caduta durano ~180 fotogrammi, quelle di
attivita' quotidiana ~820:

| coppia | differenza di lunghezza | banda effettiva |
|---|---:|---:|
| caduta - caduta | piccola | 10 |
| ADL - ADL | piccola | 10 |
| **caduta - ADL** | ~640 | **630** |

Le coppie incrociate — quelle che devono risultare distanti — si allineavano
quasi senza vincolo, e la loro distanza risultava artificialmente bassa.

**Impatto misurato.** Su dati sintetici con la stessa asimmetria: punteggio
5,055 invece di 7,201, cioe' **−30% su forme volutamente diversissime**.

L'effetto non era uniforme, ed e' questa la parte grave: colpiva
**selettivamente gli integrali**, che sono curve lisce e sotto warping libero
si deformano l'una nell'altra a costo quasi nullo, mentre le grandezze
posizionali hanno un gradino netto che il warping non cancella. Cinque delle
nove integrali risultavano sotto 1,0 e venivano scartate come rumore. Il
difetto era conservativo sui valori ma **falsava l'ordine della classifica**,
che e' esattamente cio' che serviva.

**Intervento:** ricampionamento a 200 campioni prima del confronto, cosi' `n =
m` per ogni coppia e la banda vale 10 per tutte. Vedi
[DEC-102](DECISIONS.md#dec-102).

**Verificato con:** test sintetico riproducibile (8 curve da 180 con discesa
netta contro 9 da 820 oscillanti) e riesecuzione su dati reali, dove nessuna
grandezza resta sotto 1,0 e cinque integrali risalgono di oltre +0,19.

**Run annullata:** [EXP-004](EXPERIMENTS.md#exp-004).

---

<a id="iss-102"></a>
### ISS-102 — Selezione DTW cieca alla ridondanza

**Trovata:** 2026-08-19 · **Risolta:** 2026-08-19 · **Gravita': media**

`pipeline/analisi_dtw.py` selezionava `cl.head(top)`, cioe' le prime k della
classifica. Il DTW valuta ogni grandezza isolatamente, quindi lo stesso
fenomeno misurato in tre modi occupa tre posti.

Sui dati reali le prime dodici contenevano cinque coppie con |r| > 0,80:

```
A2_testa_rel_y      A2_angolo_tronco      r = 0,972
A2_testa_rel_y      A3_testa_rel_y        r = 0,981
A2_angolo_tronco    A3_testa_rel_y        r = 0,946
A3_ginocchia_rel_y  A3_caviglie_rel_y     r = 0,931
A3_escursione       A2_escursione         r = 0,852
```

Le prime tre sono la stessa cosa: quanto e' verticale il tronco. Alla rete
sarebbero arrivati circa otto segnali indipendenti travestiti da dodici.

Difetto collaterale dello stesso punto: fra il dodicesimo (1,163) e il
tredicesimo (1,162) della classifica c'era **un millesimo**. Sotto 1,16
l'ordine era un pareggio, non una graduatoria, e tagliare a dodici secchi era
arbitrario.

**Intervento:** funzione `seleziona`, selezione avida con soglia `--max-corr`
(predefinito 0,85). Le escluse vengono dichiarate con il nome di chi le blocca
e il valore di r. Correlazione media fra le scelte da 0,385 a 0,325. Vedi
[DEC-103](DECISIONS.md#dec-103) e [EXP-006](EXPERIMENTS.md#exp-006).

---

<a id="iss-103"></a>
### ISS-103 — `.replace('.', ',')` applicato a f-string gia' composte

**Trovata:** 2026-08-19 · **Risolta:** 2026-08-19 · **Gravita': bassa**

Ricorrente in tutto il progetto, storico e nuovo. Per scrivere i decimali con
la virgola si applicava `.replace('.', ',')` alla stringa finita, che
trasformava in virgola **tutti** i punti: quelli degli elenchi numerati
(`1.` diventava `1,`), quelli delle estensioni, quelli delle frasi.

**Intervento:** in `pipeline/analisi_dtw.py` i numeri si formattano prima di
entrare nella stringa, con un `dec()` locale, e il perche' e' scritto in un
commento accanto — l'errore si nota tardi e male.
