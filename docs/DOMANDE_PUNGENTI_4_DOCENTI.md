

## GARULLI — stima, filtraggio, sistemi dinamici

**D1. Perché non un filtro di Kalman sui landmark, invece di derivate su
dati grezzi?**
> *"Un filtro non è stato applicato nella versione finale — l'ho considerato
> durante lo sviluppo (una media mobile esponenziale) ma non l'ho adottato.
> Le feature principali sono otto integrali su dodici, già più stabili del
> singolo fotogramma per costruzione. Un Kalman attenuerebbe il rumore
> indipendente, ma non il caso più insidioso osservato in casa: lo stimatore
> che salta tra due configurazioni di posa plausibili e resta stabile per
> più fotogrammi — quello un filtro a velocità costante non lo distingue dal
> movimento vero."*

**D2. La persistenza (5 finestre consecutive) conta campioni, non secondi —
lo stesso difetto che riconosci per K e L. Quanto dura in secondi, sulla
board a frequenza variabile?**
> *"È lo stesso problema concettuale di K e L: una regola in numero di
> campioni cambia significato reale al variare della frequenza. A 9 fps, le
> cinque finestre corrispondono a circa un secondo; a 1,15 fps, molto di
> più. Non ho quantificato questo effetto per la persistenza con la stessa
> cura dedicata a K — è un'estensione naturale di un limite già dichiarato,
> non ancora misurata."*

**D3. 6 TOPS è un numero di throughput, non di latenza. Perché non
garantisce velocità, se il collo di bottiglia è altrove?**
> *"Perché il collo di bottiglia — la stima di posa con MediaPipe — non usa
> affatto la NPU: gira sulla CPU. Il numero di TOPS disponibile è quindi
> irrilevante per il sistema che ho installato; l'ho sfruttato solo nel test
> con uno stimatore diverso, YOLOv8-pose, dove però la qualità della posa è
> peggiorata."*

**D4. La retta del pavimento è stimata con minimi quadrati su punti
rumorosi. Hai scartato gli outlier?**
> *"No, uso tutti i punti raccolti indiscriminatamente. Non ho applicato un
> metodo robusto come RANSAC per scartare le osservazioni anomale — è un
> possibile miglioramento non esplorato. So già che il bordo del corpo esce
> dall'inquadratura nel 17,8% delle osservazioni in un caso controllato, e
> che questo sposta la retta di circa un sesto della lunghezza del tronco:
> un bias verso il basso, dichiarato."*

**D5bis — LEAKAGE. Il leakage lo hai misurato, ma non corretto: perché non
hai fatto una validazione annidata vera — ripetendo selezione DTW, scelta di
K e scelta della soglia dentro ogni fold, e riaddestrando con quei valori
specifici — invece di un controllo a posteriori sui soli valori scelti?**
> *"È esattamente quello che andrebbe fatto per eliminare il leakage del
> tutto: una validazione annidata, in cui ogni fold ripete l'intero processo
> — selezione, scelta di K, scelta della soglia — usando solo gli otto
> soggetti di addestramento, e poi riaddestra il modello con quei valori
> specifici di quel fold. Io ho fatto una versione parziale: ho ripetuto la
> selezione e la scelta di K dentro ogni fold e ho confrontato i valori
> ottenuti con quelli usati nell'esperimento principale — ma non ho
> riaddestrato l'intero modello con il sottoinsieme specifico di ciascun
> fold. Quindi conosco quanto cambiano le scelte fold per fold, ma non
> quanto cambierebbe la metrica finale se la pipeline fosse completamente
> annidata. È il limite più diretto: la validazione annidata vera è la
> correzione naturale, non ancora fatta per il tempo che avrebbe richiesto —
> dieci riaddestramenti completi in più, uno per fold, con dati diversi ogni
> volta."*

**D5. Perché K=31 e non K=45, se K=45 dà F2 più alto in laboratorio?**
> *"Perché 'migliore' dipende da dove lo misuri. In laboratorio K=45 dà F2
> più alto — 0,987 contro 0,980. Ma sul campo, nello stesso passaggio, gli
> allarmi all'ora salgono da 14,0 a 17,0 e le cadute riconosciute scendono
> da 4 su 5 a 3 su 5. K=45 è migliore sul benchmark e peggiore nell'uso
> reale. Ho privilegiato il comportamento sul campo. Dichiaro anche che
> questa scelta non è indipendente dai dati: K=31 è stato mantenuto anche
> guardando le prime prove domestiche."*

---

## BARNI — segnali, informazione, statistica

**D6. Hai scomposto calibrazione e capacità discriminativa solo sulla
configurazione precedente, non sul sottoinsieme DTW che usi davvero.
Potrebbe essere che per DTW la perdita sia tutta calibrazione?**
> *"È possibile, e non posso escluderlo. La scomposizione richiede la soglia
> oracolo, calcolata con le etichette del dataset di destinazione — l'ho
> fatta solo sulla configurazione precedente. Ripeterla sul sottoinsieme DTW
> è il primo esperimento che farei con più tempo."*

**D7. Il filtro di ridondanza nella selezione DTW usa la correlazione di
Pearson, soglia 0,85 — una misura lineare. Hai considerato l'informazione
mutua?**
> *"No, solo la correlazione lineare. È un limite del criterio: due
> grandezze potrebbero essere ridondanti in modo non lineare e sfuggire al
> filtro."*

**D8. Il teorema di Nyquist richiede campionare ad almeno il doppio della
frequenza utile del segnale. Hai fatto un'analisi spettrale del movimento di
una caduta per giustificare 9 fps, o 1,15 fps sul campo?**
> *"No. La frequenza viene da un vincolo pratico — cosa la board riesce a
> sostenere — verificato poi empiricamente sulle prestazioni, non da
> un'analisi spettrale. Non ho verificato se questo introduca aliasing in
> senso stretto."*

**D9. Con t=2,22 contro un critico di 2,26 per K=31 contro K=45 — differenza
risicata — hai calcolato la potenza statistica di quel test?**
> *"No, non per questo confronto specifico, a differenza di quanto ho fatto
> per le architetture. Il valore è vicinissimo alla soglia critica: lo
> dichiaro un'evidenza debole, non un risultato solido."*

**D9bis — LEAKAGE. Hai un limite superiore di quanto queste
non-indipendenze possano aver gonfiato l'F2 riportato — soglia, selezione
DTW, K, controesempi — tutte insieme?**
> *"No, non ho un limite superiore cumulativo. Ho misurato l'effetto di
> ciascuna separatamente dove potevo: per K, la differenza fra la scelta
> fatta e quella indipendente è 0,026 di F2, non significativa (t=2,22); per
> la selezione DTW, la sovrapposizione con la scelta indipendente è in media
> 0,769 secondo l'indice di Jaccard, ma non ho riaddestrato con i
> sottoinsiemi specifici di ciascun fold, quindi non conosco l'effetto sulla
> metrica. Non ho sommato questi effetti in un singolo numero di 'ottimismo
> complessivo': rischierebbe di sommare incertezze misurate in modi diversi
> e non direttamente comparabili."*

**D10. Perché la correzione di Bonferroni e non un metodo meno
conservativo, come Holm o Benjamini-Hochberg?**
> *"Bonferroni è il più semplice e il più conservativo fra i metodi
> disponibili — non ho esplorato alternative meno severe. Con un metodo
> meno conservativo alcune differenze potrebbero risultare significative, ma
> con una garanzia più debole."*

**D11. Il test t appaiato assume differenze distribuite normalmente — l'hai
verificato?**
> *"No. Con dieci soggetti è un campione troppo piccolo per un test di
> normalità affidabile. È un limite che riconosco."*

**D12. "Non significativo" vuol dire che le architetture sono uguali?**
> *"No. Vuol dire che non ho trovato evidenza sufficiente per distinguerle
> con i dati che ho. Per GRU contro Random Forest, per esempio, servirebbero
> circa 52 soggetti per rendere quella differenza statisticamente
> rilevabile — ne ho dieci."*

---

## GIANNITRAPANI — stima, controllo, robotica

**D13. Con frequenza variabile, la finestra di 22 campioni osserva una
porzione diversa di traiettoria ogni volta. Perché non ricampionare
uniformemente nel tempo invece di contare campioni?**
> *"Perché ricampionare per interpolazione significherebbe creare un dato in
> un istante mai osservato. È una scelta esplicita: niente pose vengono
> inventate. Preferisco il Δt reale nelle derivate piuttosto che fabbricare
> dati intermedi, anche se questo lascia aperto il problema che finestre e K
> rappresentano durate diverse a frequenze diverse."*

**D14. La Random Forest non ha memoria di stato — decide solo dalla
finestra corrente. Come fa il sistema a "ricordare" cosa è successo prima?**
> *"Non lo ricorda. Ogni finestra è valutata indipendentemente. La
> continuità nel tempo è affidata interamente alla regola di persistenza —
> cinque finestre consecutive — non al classificatore. È una separazione
> netta fra cosa riconosce il modello e cosa decide il sistema nel tempo."*

**D15. In 11 delle 50 cadute di Camera 2 lo stimatore perde la persona che
cade e si aggancia a un'altra in piedi. È un problema di inizializzazione o
di associazione dati?**
> *"Non ho diagnosticato la causa esatta. Probabilmente associazione dati:
> lo stimatore segue per continuità temporale e in quel passaggio aggancia
> una persona più stabile. Non l'ho isolato sperimentalmente."*

**D15bis — LEAKAGE. L'altezza dal pavimento e i controesempi sono stati
introdotti DOPO aver visto gli errori in casa, e poi valutati sugli stessi
dati in cui l'errore era stato osservato. Dal punto di vista di un sistema
di stima, non è un anello chiuso — calibri sull'errore e poi misuri il
guadagno sullo stesso errore?**
> *"Sì, è esattamente così, e lo dichiaro come limite. Non è una validazione
> indipendente: ho osservato un errore specifico — persone sdraiate su
> superfici rialzate — e ho introdotto una correzione pensata apposta per
> quel caso, poi misurata sugli stessi dati. Per verificarlo in modo pulito
> servirebbero nuove acquisizioni, raccolte dopo la correzione, mai viste
> durante la progettazione della correzione stessa."*

**D16. L'altezza dal pavimento dipende da distanza e angolo della camera.
Che succede se la camera cambia inclinazione o altezza dopo l'installazione?**
> *"La retta andrebbe ristimata: i parametri a e c sono legati
> all'installazione specifica. Non ho verificato quanto velocemente la
> stima si corregge dopo uno spostamento della camera, né se il sistema se
> ne accorge da solo."*

---

## GIORGI — architettura dei calcolatori, embedded

**D17. Il sottocampionamento a 9 fps avviene scartando fotogrammi PRIMA
della stima di posa, o si stima la posa su tutti e si scarta metà nella
costruzione delle finestre? [DA VERIFICARE]**
> Controlla `deploy_board/rileva.py` prima del 22. Se non hai una risposta
> certa: *"Non ho la certezza del punto esatto in cui avviene lo scarto nel
> codice installato — è una cosa che verifico prima della discussione."*
> Non rispondere a caso su questo: è una domanda che Giorgi farebbe per
> abitudine professionale, e sbagliarla in diretta pesa più che ammettere
> di doverla controllare.

**D18. Hai scartato le reti neurali per le dipendenze software — ma non hai
considerato un runtime più leggero, come TensorFlow Lite o ONNX Runtime?**
> *"No, non l'ho esplorato. Il confronto sulle dipendenze si basa su
> scikit-learn contro TensorFlow così come le ho implementate, non con un
> runtime alleggerito. È un confronto che indebolirebbe parzialmente
> l'argomento della semplicità, se qualcuno lo ripetesse con TFLite."*

**D19. Il costo di 150 euro include lo sviluppo software? E il consumo
energetico, importante per un dispositivo pensato per girare 24 ore su 24,
perché non è stato misurato?**
> *"Il costo è solo hardware — board e telecamera, verificato con il prezzo
> reale della variante da 6 GB. Il consumo energetico non è stato misurato:
> servirebbe uno strumento di misura della corrente assorbita che non avevo.
> È un limite dichiarato."*

**D20. I 6 TOPS dichiarati, a che precisione sono riferiti?**
> *"INT8 — stessa precisione a cui ho quantizzato YOLOv8-pose nel test con
> la NPU. La cifra dichiarata è quindi direttamente quella rilevante per il
> mio caso d'uso."* (Verificata: è corretta, puoi dirla senza esitazione.)

**D20bis — LEAKAGE. Se domani installi il sistema in una terza casa, devi
rifare la scelta di K guardando i nuovi dati, come hai fatto per questa? È
un processo automatizzabile o richiede sempre giudizio umano?**
> *"Con la pipeline attuale, richiederebbe giudizio umano: K e i
> controesempi sono stati scelti osservando gli errori di due case
> specifiche, non con una procedura automatica che si adatta da sola a un
> ambiente nuovo. È un limite pratico di riproducibilità: ogni nuova
> installazione, con questo approccio, ripeterebbe lo stesso processo
> non del tutto indipendente invece di ereditare una configurazione già
> validata in modo pulito."*

**D21. La prova di continuità copre 4 ore e 35 minuti. Perché non 24 ore,
visto che il sistema è pensato per restare acceso sempre?**
> *"È il limite più diretto della prova di fattibilità: 4 ore e 35 minuti
> bastano per osservare temperatura, interruzioni della camera e continuità
> per qualche ora, ma non sostituiscono un controllo dell'ordine di una
> giornata intera. Una sessione più lunga, di 6 ore e 7 minuti, ha avuto
> un'interruzione del sistema operativo di 68 minuti — motivo per cui non
> l'ho usata come riferimento di continuità."*

---

## Le cinque da sapere a memoria, se il tempo per prepararsi è poco

1. **D5bis** (Garulli) — perché non una validazione annidata vera: è la domanda che riassume tutto il leakage in un colpo solo, ed è la più probabile se uno qualunque dei quattro vuole affondare il colpo.
2. **D6** (Barni) — la scomposizione calibrazione/capacità non ripetuta sul DTW: è la vulnerabilità più seria dell'intero lavoro sul trasferimento esterno.
3. **D17** (Giorgi) — verifica nel codice dove avviene lo scarto dei fotogrammi, prima del 22.
4. **D5** (Garulli) — K=31 contro K=45, laboratorio contro campo: è il punto che lega insieme leakage, protocollo e scelta metodologica.
5. **D18** (Giorgi) — TFLite come alternativa non esplorata: ammettilo subito, non aspettare che te lo facciano notare.
