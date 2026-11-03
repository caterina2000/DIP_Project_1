# Domande probabili della commissione — per competenza

Commissione: sistemi dinamici · high performance systems · intelligenza artificiale · reinforcement learning.
Ogni risposta è pensata per essere **detta a voce in 20-40 secondi**. Dove un fatto non è verificato lo dico
con **[DA VERIFICARE]**; dove l'ho controllato nel codice o nella tesi lo dico con **[verificato: dove]**.

Regola generale per tutte le domande: **ammettere il limite per prima, poi dire che cosa si è misurato**.
Una commissione perdona un limite dichiarato, non un limite scoperto.

---

## 0. I sette punti più deboli (in ordine di rischio)

Sono quelli su cui, a mio parere, ti attaccheranno. Per ciascuno: la frase onesta.

| # | Punto debole | Frase da avere pronta |
|---|---|---|
| 1 | **Selezione DTW fatta sull'intero dataset prima del LOSO** (leakage) | «Lo dichiaro: il soggetto di test ha contribuito alla scelta delle 12 grandezze. L'ho misurato rifacendo la selezione per fold: sovrapposizione media 0,769 (Jaccard), e sei grandezze su dodici escono in tutti i fold. Non ho però riaddestrato tutto con il sottoinsieme di ogni fold, quindi non so quantificare l'effetto sulle metriche.» [verificato: Cap. 4, sez. leakage] |
| 2 | **Dieci soggetti, cinque cadute simulate in casa** | «Sul benchmark dieci soggetti bastano per dire che le differenze fra architetture sono piccole rispetto alla variabilità fra soggetti, non per dire quale è migliore: per distinguere GRU da Random Forest servirebbero circa 52 soggetti. In casa cinque cadute: richiamo 0,80 con intervallo di confidenza 0,28–0,99. Non è una validazione, è un'indagine dei guasti.» |
| 3 | **K, soglia, altezza e controesempi scelti guardando gli stessi dati** | «Sono scelte non indipendenti, e lo scrivo fra i limiti. Per K l'ho verificato: scelto dentro ogni fold, 9 fold su 10 scelgono 45 e F₂ sale da 0,825 a 0,851 (t = 2,22 contro 2,26 critico). K = 31 l'ho tenuto anche perché nelle prime prove domestiche riconosceva 4 cadute su 5 contro 3 con K = 45: quella parte non è verificabile in modo indipendente.» [verificato: Cap. 4] |
| 4 | **11,1 eventi/ora contro 0,049 della letteratura** | «È il dato più difficile da difendere e lo dico così. Le due cifre hanno basi di conteggio diverse, quindi non sono confrontabili uno a uno. Il punto è che in casa il carico di allarmi resta molto sopra il criterio clinico.» |
| 5 | **Finestra di 22 campioni addestrata a 9 fps, sulla scheda a circa 7,3 fps** | Vedi § 1.3: è un possibile disallineamento temporale. **Controllalo prima di discutere.** |
| 6 | **Una sola scheda, prove di ore non di giorni, consumo non misurato** | «Fattibilità per alcune ore: 4,59 ore continue, 297 MB di picco di memoria. Consumo e giorni non li ho misurati.» |
| 7 | **Latenza non misurabile dall'inizio fisico della caduta** | «La pipeline introduce circa 3,9 s, di cui il 71% è il riempimento della finestra. Non dico "l'allarme arriva in 3,9 s": le cadute sono annotate al minuto, manca l'istante d'inizio.» |

---

## 1. Sistemi dinamici

Che cosa tendono a chiedere: **campionamento, rumore, memoria finita, stabilità, osservabilità**. Il modo di rispondere è chiamare le cose col loro nome.

### 1.1 «Perché le grandezze integrali e non le derivate? Che cosa stai facendo, in termini di sistemi?»
**Risposta.** Le derivate istantanee amplificano il rumore della stima di posa: sono un filtro passa-alto su un segnale già rumoroso. Ho misurato che il punteggio dipendeva pochissimo dal movimento presente nella finestra (correlazione +0,139) e che le derivate erano instabili. Le grandezze integrali (percorso, escursione, discesa) sono funzionali su finestra mobile di durata finita: sommano il movimento su 1,72 s, quindi mediano il rumore e hanno memoria finita. In pratica passo da un derivatore a un integratore a finestra. [verificato: Cap. 5, riga sul +0,139]

**Se insistono:** «percorso» = lunghezza della traiettoria, «escursione» = ampiezza max–min, «discesa» = quanto la quota cala rispetto al minimo della finestra.

### 1.2 «Il segnale è campionato a 18, poi 9, poi 7,3 fps. Il teorema del campionamento? Che cosa perdi?»
**Risposta.** Una caduta dura circa uno-due secondi, e la dinamica utile sta sotto qualche hertz: a 9 campioni al secondo il criterio di Nyquist per quella banda è rispettato. Il costo del sottocampionamento da 18 a 9 l'ho misurato: F₂ cala di 0,041 (falsi negativi da 24 a 49). Cambiare stimatore di posa costa invece 0,216, circa cinque volte di più. [verificato: Cap. 5, tab. scomposizione]

### 1.3 «Il sistema è addestrato a 9 campioni al secondo ma gira a 7,3. Il modello vede lo stesso segnale?» ⚠ punto vero
**Che cosa so dal codice.** [verificato: `deploy_board/pacchetto_dtw12/geometry.py` e `rileva.py`]
- Le **grandezze integrali** sulla scheda sono definite come **durata** (1,72 s), non come numero di campioni: a 7,26 fps tengono 13 campioni invece di 31, ma coprono lo stesso intervallo. È la correzione ISS-148.
- Le **derivate** usano il passo reale `dt = 1/fps` misurato.
- La **finestra del classificatore**, invece, è di **22 campioni** e avanza di **2 campioni** per volta, contati in fotogrammi: sulla scheda ogni fotogramma entra nel buffer (`buf.append`, poi `n_frame % passo`). A 7,3 fps 22 campioni coprono circa **3,0 s**, contro i **2,44 s** dell'addestramento a 9 fps.

**Che cosa NON so.** Se questa dilatazione di circa il 24% della finestra cambi le decisioni. La verifica di parità scheda–offline (200 finestre, scarto 0) controlla che il codice sia identico, non che la scala temporale sia la stessa. **[DA VERIFICARE]**: rilanciare offline una sessione con la finestra a 22 campioni ma a cadenza 7,3 fps e vedere se i punteggi cambiano.

**Risposta onesta se te lo chiedono.** «Le grandezze integrali le ho rese indipendenti dalla cadenza, perché sono durate. La finestra del classificatore resta in campioni: a 7,3 fps copre circa 3 s invece di 2,4. Non ho misurato separatamente l'effetto: è un limite, e lo metto fra gli sviluppi insieme alle finestre definite in tempo.» (L'hai già fra gli sviluppi: «finestre definite in termini di tempo».)

### 1.4 «La regola d'allarme (5 finestre, 30 s) è un sistema dinamico? È stabile?»
**Risposta.** È una macchina a stati finiti: un contatore con soglia (debounce) e un tempo di silenzio dopo l'allarme (refractory). Non ha dinamica continua, quindi non pongo un problema di stabilità in senso classico; il comportamento da analizzare è come interagisce con il classificatore. L'ho osservato: la seconda caduta, sei secondi dopo la prima, è riconosciuta dal modello ma soppressa dalla regola; una persona sul divano dà quattro finestre sopra soglia e non allarma perché ne servono cinque. Per questo classificatore e regola vanno valutati separatamente.

### 1.5 «Una sola camera, proiezione 2D: il sistema è osservabile?»
**Risposta.** Non del tutto, ed è esattamente ciò che ho misurato: stessa vista laterale F₂ = 0,822, vista frontale 0,488, entrambe in addestramento 0,731. Il cambio di punto di vista pesa più del cambio di modello. Per questo lo dichiaro come limite e non cerco di mascherarlo con più modelli.

---

## 2. High performance systems

Che cosa tendono a chiedere: **dove va il tempo, throughput contro latenza, accelerazione, memoria, termica, misure affidabili**.

### 2.1 «Dov'è il collo di bottiglia? Perché non hai ottimizzato il classificatore?»
**Risposta.** La stima della posa occupa l'85,2% del tempo (116,4 ms su 136,6 ms per fotogramma); il classificatore il 14,3% (19,5 ms, cioè circa 39 ms per finestra, una finestra ogni due fotogrammi). Ottimizzare il classificatore guadagna al massimo il 14%. [verificato: riepilogo.json della prova da 4,59 h]

### 2.2 «Hai una NPU da 6 TOPS. Perché giri MediaPipe sulla CPU?»
**Risposta.** L'ho provata. YOLOv8-pose INT8 sulla NPU: inferenza 5,16 volte più veloce, pipeline a 26,5 fps (dopo aver vettorizzato il post-processing da 12,14 a 0,94 ms). Ma sul benchmark a cinque soggetti F₂ scende da 0,909 a 0,682 (falsi positivi da 17 a 225), e da sdraiati conserva la posa nel 43,6% dei fotogrammi contro il 79,1%. Quindi non è un limite dell'acceleratore, ma dello stimatore usato. Non posso separare l'effetto del modello da quello della quantizzazione INT8: l'ho valutato solo in INT8. [verificato: Cap. 5]

**Cosa NON dire:** «la NPU non funziona». Dire: «la NPU è utile, lo stimatore che ho potuto eseguire lì non era abbastanza buono da sdraiati».

### 2.3 «92,6 ms nel benchmark, 116,4 ms in esercizio. Perché?» ⚠ punto vero
**Che cosa so.** Il benchmark dà 92,6 ms/fotogramma (10,8 fps); nella prova continua la percezione costa 116,4 ms (7,3 fps). [verificato: Cap. 5 e riepilogo.json] **Che cosa NON so**: la causa della differenza (cattura dalla telecamera USB, scritture su disco, altri processi, temperatura). **[DA VERIFICARE]** o dichiarare: «in esercizio ci sono la cattura e la registrazione; non ho scomposto la differenza».

### 2.4 «Termica e consumo?»
**Risposta.** Ho misurato la temperatura in una sessione di 6,11 ore (con 68 minuti di sospensione del sistema operativo): massimo 79,5 °C, regime dopo circa 40 minuti, cadenza che cala con le ore. Nella prova di riferimento da 4,59 ore la cadenza resta fra 7,3 e 7,8 fps. Il **consumo elettrico non è stato misurato**: lo dico subito.

**Attenzione.** La temperatura non è registrata nella prova da 4,59 ore, solo nella sessione da 6,11. Non attribuire i 79,5 °C alla prova da 4,59 ore.

### 2.5 «Come fai a fidarti delle tue misure di velocità?»
**Risposta.** Mi sono già sbagliato e l'ho scritto. In una prova avevo 1.315 fps perché l'inferenza sulla NPU non veniva eseguita: il tensore d'ingresso aveva tre dimensioni invece di quattro e non c'era errore esplicito. Da allora controllo che il calcolo sia davvero eseguito e che l'uscita sia corretta prima di usare un tempo. [verificato: Cap. 5]

### 2.6 «Quanto serve di memoria? Scala a più telecamere?»
**Risposta.** 297 MB di picco, circa il 5% dei 6 GB; il classificatore pesa circa 0,6 MB. La memoria non è il limite. Più telecamere su una sola scheda: non l'ho provato; il costo per fotogramma è dominato dalla posa, quindi la capacità si divide quasi linearmente. **[DA VERIFICARE]** se la commissione chiede il numero.

### 2.7 «Throughput contro latenza?»
**Risposta.** I 7,3 fps sono il throughput; la latenza della pipeline è circa 3,9 s, di cui il 71% è il riempimento della finestra, cioè è dovuta all'algoritmo, non al calcolo. Più potenza di calcolo non la riduce di molto: per ridurla servirebbero finestre più corte (che costano F₂: da 44 a 22 campioni il F₂ scende da 0,915 a 0,825).

---

## 3. Intelligenza artificiale

Che cosa tendono a chiedere: **validazione, leakage, significatività, baseline, calibrazione, generalizzazione**.

### 3.1 «Perché il LOSO e non uno split semplice? E la validazione?»
**Risposta.** Con 10 soggetti uno split fisso dipende dal soggetto scelto. Il LOSO dà dieci prove su soggetti mai visti. Ogni fold: otto soggetti per l'addestramento, uno per la validazione, uno per il test; la normalizzazione è stimata solo sul training di ciascun fold.

### 3.2 «Significatività? Come fai a dire che le architetture sono simili?»
**Risposta.** Test t a campioni appaiati fold per fold, con correzione di Bonferroni: soglia critica circa 3,25 invece di 2,26. Le differenze sono piccole rispetto alla deviazione fra soggetti (circa 0,07). Per distinguere GRU (F₂ 0,857) da Random Forest (0,825) servirebbero circa 52 soggetti. Non dichiaro quindi un vincitore.

### 3.3 «Leakage?» (vedi § 0, punto 1)
Aggiungi: «La normalizzazione è per fold, quindi pulita. Il leakage è nella selezione DTW e in K, e li ho misurati entrambi.»

### 3.4 «Perché F₂ e non F₁/AUC? E come hai scelto la soglia?»
**Risposta.** In un sistema di allarme un falso negativo costa più di un falso positivo: F₂ pesa di più il richiamo. La soglia è fissa a 0,50 in tutti gli esperimenti, non regolata sul test. **Ma**: sul nuovo dataset i punteggi non sono più calibrati allo stesso modo: ricalcolando la soglia su UR-Fall si recupera una parte della perdita, non tutta. Cioè cambiano sia la calibrazione sia la capacità discriminativa. [verificato: Cap. 6]

### 3.5 «Perché non una rete end-to-end sul video?»
**Risposta.** Con 10 soggetti e poche cadute registrate una rete sul video avrebbe appreso lo sfondo e il soggetto. Passare per lo scheletro riduce la dimensione, toglie le informazioni identificative (privacy: nessuna immagine esce dal dispositivo) e permette di girare su una scheda da circa 100 €. Non ho confrontato direttamente con un modello end-to-end: è un limite del confronto. **[DA VERIFICARE]** se in tesi c'è un riferimento.

### 3.6 «Le etichette, chi le ha fatte?»
**[DA VERIFICARE]** la risposta esatta prima di arrivare: chi ha annotato, se una sola persona, se c'è un accordo fra annotatori. Se è stata una persona sola, dirlo: «annotazione manuale per fotogramma, un solo annotatore, senza misura di accordo».

### 3.7 «UR-Fall: il sottoinsieme DTW arriva a F₂ 0,630. Non è un crollo?»
**Risposta.** Sì, dal benchmark. Lì cambiano soggetti, ambiente e acquisizione (30 fps, camera 0, 67 registrazioni, 11.400 fotogrammi). Il risultato è proprio il messaggio: ciò che funziona in laboratorio non si trasferisce intatto, e la selezione DTW sul solo UP-Fall non è un garante. Il sottoinsieme da integrali dà 0,479, A3 0,404.

### 3.8 «Una persona sdraiata sul divano è un falso positivo. Perché?»
**Risposta.** Nel dataset le posizioni orizzontali negative stanno quasi tutte vicino al pavimento (altezza mediana dei fianchi circa +0,02 lunghezze del busto); in casa, a letto o sul divano, +1,47. Quindi ho reintrodotto l'altezza e aggiunto controesempi domestici. Costo dichiarato: le cadute riconosciute scendono da 4 su 5 a 3 su 5.

---

## 4. Reinforcement learning

Che cosa tendono a chiedere: **perché non RL, come lo useresti, come formuleresti il problema**. Qui conta mostrare di aver pensato alla formulazione.

### 4.1 «Perché non reinforcement learning?»
**Risposta.** Nel mio problema ho dati etichettati e l'obiettivo è la classificazione di una sequenza: è un problema supervisionato. L'RL serve quando le azioni cambiano le osservazioni future o quando manca l'etichetta immediata. Qui l'azione (dare l'allarme) non cambia ciò che la telecamera vede.

### 4.2 «Ma la regola d'allarme è una politica. Come la ottimizzeresti?»
**Risposta.** È una politica a tre parametri scritta a mano: soglia 0,50, persistenza 5 finestre, silenzio 30 s. Si può formulare come decisione sequenziale: stato = storia dei punteggi, azioni = allarme/attesa, costo = falso negativo molto più caro del falso positivo, più un costo di ritardo. Si potrebbe ottimizzare come problema di controllo ottimo o con un metodo a bandit, non per forza con RL completo: lo spazio dei parametri è tre-dimensionale e si cerca con una ricerca guidata, rispettando un vincolo sul numero di allarmi all'ora.

### 4.3 «Perché non l'hai fatto?»
**Risposta.** Mancano i dati per farlo in modo valido: ho cinque cadute simulate in casa e quattro il 9 settembre. Qualunque ottimizzazione di queste regole su quei dati sarebbe un'ottimizzazione su dati già visti, cioè ripeterebbe il problema di non-indipendenza che ho già dichiarato per la soglia e per K. Lo metto fra gli sviluppi: servono acquisizioni indipendenti.

### 4.4 «Che cosa renderebbe difficile un approccio RL?»
**Risposta.** Quattro cose.
1. **Eventi rari**: le cadute sono poche e simulate, la ricompensa è quasi sempre zero.
2. **Asimmetria dei costi** e difficile definizione del costo di un falso allarme (fastidio, disattivazione del sistema).
3. **Sicurezza**: non si può esplorare in casa di un anziano «provando a non dare l'allarme».
4. **Osservabilità parziale**: una sola proiezione 2D, quindi sarebbe un problema parzialmente osservabile.

### 4.5 «Feedback dell'utente?»
**Risposta.** Se l'utente conferma o smentisce gli allarmi, si ottengono etichette per una soglia per-abitazione, in apprendimento online. Il rischio è l'asimmetria: si vedono solo gli allarmi emessi, non le cadute mancate.

---

## 5. Domande trasversali (arrivano da chiunque)

**«Qual è il contributo, se i modelli sono quasi equivalenti?»**
Non è il classificatore migliore: è aver misurato che cosa sopravvive quando il sistema esce dal benchmark. Il punto di vista pesa più del modello (0,822 → 0,488), e a casa le finestre sopra soglia passano da circa 140 a 2,7 per ora con altezza, integrali e controesempi.

**«Perché F₂ di 0,415 / 0,587 / 0,830 per tre compiti?»**
Sono tre domande diverse: riconoscere l'**evento** (la transizione di caduta), lo **stato** (a terra), o **dare l'allarme**. Quello che conta per l'utente è l'allarme (0,830). L'evento è il più difficile perché è breve (pochi campioni).

**«44,8 finestre per evento: una caduta fa 44,8 finestre?»** ⚠
No. 44,8 è il rapporto fra finestre sopra soglia ed eventi, calcolato sulle nove sessioni (7.429 finestre, 166 eventi). Gli eventi non sono tutti cadute e il rapporto cambia da sessione a sessione (14,9 nella sessione dell'11 agosto). Non è il numero di finestre per caduta.

**«Il tuo risultato in casa regge?»**
Cinque cadute simulate nella prima valutazione e quattro il 9 settembre: non le sommo. È un percorso di sviluppo su due case, non una verifica indipendente. L'ho scritto nella tesi.

---

## 6. Da controllare prima della discussione (elenco chiuso)

1. **Finestra di 22 campioni a 7,3 fps** sulla scheda (§ 1.3): rilanciare offline e vedere se i punteggi cambiano.
2. **92,6 ms contro 116,4 ms** per la posa (§ 2.3): sapere almeno la causa probabile.
3. **Chi ha annotato le etichette**, e se esiste un accordo fra annotatori (§ 3.6).
4. **Quale classificatore produce la tabella domestica** (F₂ da 0,898 a 0,953, non il GRU 0,857).
5. **K nella tesi (campioni) e nel codice (durata)**: una frase pronta per spiegare che sono equivalenti a 18 fps.
6. **«La scheda non restava attiva» e «cadute non salvate»**: non verificati nei log.
7. **Riferimento a un confronto end-to-end** (§ 3.5): c'è o non c'è in tesi.

## 7. Cose da non dire

- «La NPU non funziona.» → «Lo stimatore che ho potuto eseguire sulla NPU perdeva la posa da sdraiati.»
- «L'allarme arriva in 3,9 secondi.» → «La pipeline introduce circa 3,9 s; dall'inizio fisico della caduta non è misurabile.»
- «Una caduta produce 44,8 finestre.» → «In media 44,8 finestre sopra soglia formano un evento.»
- «I 79,5 °C sono della prova da 4,59 ore.» → sono della sessione da 6,11 ore.
- «Il sistema ha 0,953 di F₂.» → in laboratorio, sul benchmark, con selezione non indipendente.
- «Il consumo è basso.» → non è stato misurato.
