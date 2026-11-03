# Il data leakage: che cosa fa il codice, che cosa dice il Capitolo 3

Materiale per scrivere `sec:leakage_protocollo` (Capitolo 4, §4.1.5).
Raccolto il 2026-09-23.

La richiesta del relatore, lettera del 14 settembre 2026:

> In ogni fold, tutto ciò che «impara qualcosa dai dati» deve essere calcolato
> esclusivamente sul training/validation set. […] Questo punto va dichiarato
> esplicitamente nella tesi, perché altrimenti un lettore esperto potrebbe
> legittimamente chiedersi se ci sia leakage.

Le quattro operazioni che nomina: **normalizzazione, feature selection,
threshold selection, hyperparameter tuning**.

---

## ⚠ Una decisione da prendere prima di scrivere

**Il Capitolo 3 su disco contiene già le due misure per intero**, non solo la
dichiarazione: `sec:leakage` ha la tabella `tab:leakage_misura` con i dieci
fold, la tabella della scansione di $K$ per fold, e tutta la prosa
interpretativa — nucleo stabile, sedici scambi, $t = 2{,}22$, il difetto della
libreria.

Il relatore chiede però che il Capitolo 3 sia **metodologia** e il 4
**risultati**. Ci sono due strade:

- **A.** Il Cap3 tiene la *dichiarazione* (quali operazioni violano il
  protocollo e perché) e la *promessa* della misura; le due misure si spostano
  in Cap4 §4.6 `sec:misura_leakage`. È la strada coerente con la richiesta, e
  `sec:leakage_protocollo` diventa la tabella del protocollo.
- **B.** Il Cap3 tiene tutto, e Cap4 §4.1.5 si limita alla tabella con un
  rimando. Più rapido, ma mette un risultato sperimentale dentro il capitolo di
  metodologia — esattamente quello che il relatore separa.

Questo documento raccoglie il materiale per entrambe.

---

# Parte 1 — Che cosa fa il codice, operazione per operazione

## 1. Normalizzazione — **conforme**

**Dove:** `src/dati.py`, classe `Scaler`.

**Che cosa fa.** Due passaggi in sequenza:

1. `log1p` con segno — $x' = \operatorname{sgn}(x)\log(1+|x|)$ — su
   **quattordici** colonne asimmetriche, elencate in `ASIMMETRICHE`: le nove
   integrali più velocità angolare del tronco, velocità della testa, velocità
   del bacino, velocità della testa relativa al bacino e larghezza normalizzata.
2. `StandardScaler` sulle colonne risultanti.

**Perché è conforme.** Media e deviazione sono stimate **dentro ciascun fold,
sui soli fotogrammi di training**, e poi applicate senza ricalcolo a validation
e test. Il soggetto di prova non contribuisce ai parametri della trasformazione.

**Due dettagli che vanno detti perché non sono ovvi.**

- La stima è sui **fotogrammi**, non sulle finestre. Le finestre si
  sovrappongono di 20 campioni su 22: stimare dopo la finestratura conterebbe
  lo stesso campione fino a undici volte, con un peso che dipende anche dalla
  posizione nella registrazione.
- `ASIMMETRICHE` è un **elenco fisso di nomi**, compilato guardando le
  distribuzioni. Non è un criterio automatico, e il testo attuale che parla di
  «grandezze che soddisfano il criterio previsto nella fase di preprocessing»
  è da correggere.

**Effetto misurato:** il rapporto fra la scala maggiore e la minore passa da
**646** a **1,05–1,35**.

---

## 2. Soglia decisionale — **conforme, e più di quanto richiesto**

**Dove:** `pipeline/soglia.py` per il confronto fra regole; la decisione è
DEC-105.

**Che cosa fa.** $\theta = 0{,}50$ **fissa**, dichiarata prima degli
esperimenti, identica per tutti i fold e per tutte le configurazioni.

**Perché è più forte della richiesta.** La formulazione che il relatore
suggerisce — *«per ciascun fold la soglia è scelta sui soli dati di
addestramento e validazione, poi tenuta fissa»* — descrive la procedura che è
stata **esaminata e scartata**. La garanzia qui è di grado diverso: **la soglia
non vede il soggetto di prova perché non vede alcun dato.** È il caso limite di
quella regola, in cui l'insieme su cui la soglia viene stimata è vuoto.

**La prova che giustifica lo scarto.** La procedura per fold dà dieci soglie
fra $0{,}01$ e $0{,}99$, deviazione $0{,}37$. Il confronto fra sei regole
(`tab:soglie`) riusa le probabilità già prodotte dai dieci fold, quindi non
richiede riaddestramenti.

**La cautela obbligatoria.** Le sei regole sono confrontate **sui fold di
test**: adottare $0{,}50$ «perché vince» sarebbe selezione sul test. Ciò che
l'esperimento stabilisce legittimamente riguarda la **procedura** — stimare la
soglia su un solo soggetto di validation è instabile — non il valore.

**L'unica eccezione, dichiarata dove compare:** la **soglia oracolo** del
trasferimento a UR-Fall, ricalcolata sulle etichette del nuovo archivio. È
diagnostica e non disponibile in esercizio.

---

## 3. Iperparametri del modello — **conforme**

**Dove:** `src/modelli.py`, `pipeline/addestra.py`.

**Che cosa fa.** Le configurazioni delle sei architetture sono fissate e
mantenute identiche durante tutto il confronto. **Non c'è stata ricerca di
iperparametri**, né sui fold di test né altrove.

Seme casuale **42**, fissato prima della costruzione di ciascun modello; **una
ripetizione per fold**. Ne segue che la dispersione riportata nei risultati
misura la variabilità **fra soggetti**, non quella fra inizializzazioni dello
stesso modello — e va detto, perché sono due cose che si confondono facilmente.

L'arresto anticipato usa il soggetto di **validation**, e soltanto per decidere
quando fermarsi. Il criterio è l'area sotto la curva della probabilità di
allarme, non l'accuratezza: con la classe positiva attorno al 13 % delle
finestre, l'accuratezza premierebbe un modello che risponde sempre «normale».

---

## 4. Parametro $K$ della rappresentazione — **VIOLA il protocollo**

**Dove:** `config.py:108`, che rimanda a EXP-053 del progetto storico.

**Che cosa è successo.** `K_INTEGRALI = 31` **non è stato fissato a priori**.
Il valore di partenza era 9; 31 è il risultato di una scansione su cinque
lunghezze. I numeri che hanno deciso vengono da due insiemi, ed entrambi pongono
un problema:

1. la colonna «$F_2$ laboratorio» della scansione è misurata **sui fold di
   prova**, quindi la scelta di $K$ ha visto i soggetti lasciati fuori;
2. il pareggio fra 31 e 45 è stato rotto sul **richiamo di campo**, che il
   Capitolo 5 riporta poi come risultato.

Registrata come **ISS-178**.

---

## 5. Selezione DTW delle grandezze — **VIOLA il protocollo**

**Dove:** `src/dtw.py`, `pipeline/analisi_dtw.py`.

**Che cosa è successo.** La selezione è stata eseguita **una volta sola
sull'intero insieme**, prima del LOSO, e le dodici grandezze che ne risultano
sono le stesse in tutti i fold. Il soggetto lasciato fuori ha contribuito al
punteggio di separabilità che decide quali colonne il classificatore riceve.

**Conseguenza attesa:** sopravvalutazione delle prestazioni. I valori del
Capitolo 4 vanno letti come un **limite superiore**.

---

## La tabella per §4.1.5

| operazione | calcolata su | vede il soggetto di prova? |
|---|---|---|
| normalizzazione | training del proprio fold | no |
| soglia decisionale | nessun dato | no |
| iperparametri del modello | nessun dato | no |
| parametro $K$ | scansione su dati poi valutati | **sì** |
| selezione DTW | tutti i soggetti | **sì** |

---

# Parte 2 — Le due misure

## 2.1 Selezione DTW rifatta per fold

**Script:** `pipeline/dtw_per_fold.py`
**Comando:** `python pipeline/dtw_per_fold.py --csv feature_v5.csv --top 12`

### Il controllo che viene prima

Lo script **prima** rifà la selezione sull'intero insieme e verifica di
riprodurre esattamente `risultati/dtw/scelte.txt`. Se non coincidono si ferma:
senza quel controllo si confronterebbero due cose calcolate in modo diverso.

Lo script dichiara anche **quale backend di distanza** sta usando. `src/dtw.py`
usa `dtaidistance` quando è disponibile e una versione in puro Python
altrimenti, e le due **non restituiscono lo stesso valore**: la prima è la
radice della somma dei quadrati, la seconda la somma degli assoluti.

### Il difetto trovato per strada — ISS-168

**Il controllo di riproducibilità, la prima volta, è fallito.** La causa non era
il protocollo ma la libreria: in presenza di un vincolo di finestra restituiva
**silenziosamente un valore infinito** per certe coppie di curve, azzerando il
punteggio di tre grandezze su trentatré.

Va raccontato, perché è la ragione per cui il controllo esiste: senza, la
sezione riporterebbe un confronto fra due selezioni calcolate in modo diverso,
e nulla lo segnalerebbe.

### Il risultato

**Nessuno dei dieci fold riproduce la selezione adottata.** Jaccard medio
**0,769**.

| soggetto escluso | in comune | scambio |
|---|---|---|
| 1 | 10/12 | `A2_percorso`, `A3_escursione` escono |
| 2 | 11/12 | `A2_testa_rel_y` → `A2_angolo_tronco` |
| 3 | 10/12 | `A2_testa_rel_y`, `A3_caviglie_rel_y` escono |
| 4 | 11/12 | `A2_testa_rel_y` → `A2_angolo_tronco` |
| 5 | 11/12 | `A1_escursione` → `A1_asse_mag` |
| 6 | 11/12 | `A1_escursione` → `A1_asse_mag` |
| 7 | 10/12 | `A1_escursione`, `A2_testa_rel_y` escono |
| 8 | 11/12 | `A1_escursione` → `A2_escursione` |
| 9 | 9/12 | tre scambi |
| 10 | 10/12 | `A1_percorso`, `A3_caviglie_rel_y` escono |

### Come si legge

**Il nucleo stabile.** Sei grandezze su dodici compaiono in tutti e dieci i
fold: `A1_discesa`, `A2_discesa`, `A3_discesa`, `A3_percorso`, `A3_hip_vel`,
`A3_testa_vel_rel`. **Cinque delle sei sono integrali**, cioè proprio quelle
introdotte perché accumulano invece di derivare.

**Dove sta l'instabilità.** Dei sedici scambi osservati, la correlazione fra
chi esce e chi entra ha mediana **0,793**, e **otto su sedici superano 0,85** —
la soglia oltre la quale la procedura stessa considera due grandezze
intercambiabili. `A2_testa_rel_y` contro `A2_angolo_tronco` vale 0,972;
`A3_caviglie_rel_y` contro `A3_ginocchia_rel_y` vale 0,934.

**Ma non tutti.** `A2_percorso` che lascia il posto a `A1_asse_mag` è uno
scambio fra grandezze correlate **0,065**: lì cambia l'informazione, non il nome.

### La conclusione, senza tirare la coperta

Il leakage **esiste ed è misurato**; la selezione adottata non è quella che un
protocollo corretto avrebbe prodotto in **nessuno** dei dieci fold; i valori del
Capitolo 4 restano quindi un **limite superiore**.

L'instabilità si concentra però sulla metà ridondante, mentre il nucleo che
porta l'informazione non ridondante non si muove. Questo rende **plausibile —
non dimostrato —** che l'effetto sulle metriche sia piccolo. Dimostrarlo
richiederebbe di riaddestrare le sei architetture dieci volte con il
sottoinsieme proprio di ciascun fold: **è la prova che manca.**

---

## 2.2 Scelta di $K$ rifatta per fold

**Script:** `pipeline/k_per_fold.py`
**Dati:** `feature_k_multiplo.csv` — una sola passata di stima della posa che
alimenta cinque motori geometrici, uno per ciascun $K$. Ricalcolare gli
integrali dal CSV non è possibile: servono le posizioni dei punti tracciati.

### Il protocollo annidato

Per ciascun soggetto $s$ lasciato fuori:

1. si mette $s$ da parte e non lo si guarda più;
2. si sceglie $K$ con un **LOSO interno sui soli nove rimasti**, prendendo
   quello con l'$F_\beta$ medio più alto;
3. si addestra sui rimasti con quel $K$ e si valuta su $s$, **una volta sola**.

È esattamente la sequenza che il relatore enuncia. Il confronto è contro la
procedura effettivamente seguita: $K = 31$ fisso in tutti i fold.

### Il controllo che viene prima

Come per il DTW: si verifica che il dataset a $K = 31$ ricostruito dal CSV
multi-$K$ riproduca `feature_v5.csv` sulle colonne che contano. Se non lo
riproduce, lo script si ferma.

### Il risultato, che va nella direzione opposta all'attesa

**Nove fold su dieci scelgono $K = 45$**, non il valore adottato. Con quel
valore l'$F_2$ medio sale da **0,825 a 0,851**: una differenza di **0,026 a
favore del protocollo corretto**, mediana 0,023.

**Il leakage su $K$ non ha gonfiato le prestazioni. Le ha ridotte.**

### L'onestà statistica, che non va omessa

- Il vantaggio è positivo in **otto fold su dieci**, nullo nel nono — quello che
  sceglie 31 — e negativo soltanto in uno, per 0,012.
- Ma su `Subject_09` vale **0,122**, cioè quasi **cinque volte la media**.
- Test appaiato sui dieci: $t = 2{,}22$ contro un critico di **2,26**. La
  differenza **non è dichiarabile significativa**.
- Escludendo quel soggetto la media scende a 0,016 **ma la dispersione si
  dimezza**, e il test sale a $t = 2{,}72$ contro un critico di 2,31.

Effetto **piccolo e sistematico** più che grande e incerto.

### Perché non sorprende

La scansione originale mostrava già che **sul solo criterio di laboratorio 45
batte 31**, e ci si fermò a 31 per il comportamento in ambiente domestico. Il
LOSO interno usa soltanto il criterio di laboratorio, e ritrova 45. La misura
conferma, a dieci soggetti e con il protocollo corretto, ciò che la scansione a
cinque aveva mostrato con quello sbagliato.

### Che cosa questa misura NON tocca

Il motivo per cui si è preferito 31 a 45 **non è di laboratorio ma di campo**, e
il richiamo su cui quella preferenza si fonda — quattro cadute su cinque contro
tre — è un risultato del Capitolo 5. Misurarne l'effetto richiederebbe cadute
domestiche **diverse** da quelle già usate per scegliere, e cinque cadute non
bastano a produrne due insiemi disgiunti. Su cinque casi la differenza fra
quattro e tre non è una misura ma un indizio.

---

# Parte 3 — Il confronto che rende visibile la differenza

Un parametro vicino aiuta a vedere il punto.

| | scansione | esito |
|---|---|---|
| lunghezza della finestra $L$ | 22, 28, 36, 44 campioni | si è misurato e si è **tenuto** ciò che si aveva: $L = 22$ |
| finestra di accumulazione $K$ | 5, 15, 22, 31, 45 | si è misurato e si è **cambiato**: da 9 a 31 |

**Sono due cose diverse**, e solo la seconda è leakage: una scansione che non
cambia la scelta non trasferisce informazione dal soggetto di prova alla
configurazione.

---

# Parte 4 — Le due forme non si comportano allo stesso modo

È il fatto più interessante, e va messo in evidenza invece di lasciarlo dedurre:

| | direzione dell'effetto | conseguenza sulla lettura |
|---|---|---|
| **selezione DTW** | spinge le prestazioni **verso l'alto** | i valori del Cap4 sono un **limite superiore** |
| **scelta di $K$** | spinge **verso il basso**, di 0,026 | il soggetto di prova ha contribuito a una scelta che, sul criterio di laboratorio, è costata prestazioni |

---

# Parte 5 — La sequenza da enunciare in §4.1.5

Nella forma in cui il relatore l'ha scritta, come sequenza numerata:

1. si mette da parte il soggetto $s$;
2. si calcola il criterio di selezione delle grandezze **sui rimasti**;
3. si stima la normalizzazione **sui rimasti**;
4. si addestra e si tara il modello **sui rimasti**;
5. si congela tutto;
6. si valuta su $s$, **una volta sola**.

E accanto, l'ordine sbagliato che va escluso esplicitamente:

- si selezionano le grandezze migliori **usando tutti i soggetti**;
- si esegue il LOSO **dopo**.

Il testo deve dire quale dei due questo lavoro ha seguito **per ciascuna delle
cinque operazioni**, senza attenuazioni: tre lo seguono, due no, e le due che
non lo seguono sono misurate.

---

## Rimandi da tenere allineati

- **Cap3 riga 89** — «la normalizzazione lo fa, la selezione no: la
  Sezione~\ref{sec:leakage} dichiara la differenza e ne misura la conseguenza»
- **Cap3 `sec:dtw`** — promette che la procedura viene ripetuta per fold
- **Cap3 `sec:classificatori`** — dichiara che soglia e iperparametri non
  vedono il test, e che $K$ sì
- **Cap4 §4.1.5** `sec:leakage_protocollo` — la tabella e la sequenza
- **Cap4 §4.6** `sec:misura_leakage` — le due misure, se si sceglie la strada A
