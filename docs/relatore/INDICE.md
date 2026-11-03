# Indice — le risposte al relatore

Aggiornato al **7 settembre 2026**, sera.

Questa cartella contiene, per ciascuna richiesta del relatore, una scheda che
racconta **passo per passo** che cosa è stato fatto, con i numeri, i limiti
dichiarati e i file da cui i numeri escono.

---

## Da dove cominciare

| file | che cos'è | quando serve |
|---|---|---|
| **[RELAZIONE_PER_IL_RELATORE.md](RELAZIONE_PER_IL_RELATORE.md)** | **il documento da mandare**: tutte le risposte in forma discorsiva, dall'inizio alla fine, con le tre nozioni per leggere i numeri spiegate una volta sola | è questo il primo da leggere |
| [NOVITA_6_7_settembre.md](NOVITA_6_7_settembre.md) | i **dodici** risultati degli ultimi due giorni, otto dei quali sono difetti trovati nel lavoro | per capire che cosa è cambiato dall'ultima volta |
| [D_domande_al_relatore.md](D_domande_al_relatore.md) | le **sette** domande che attendono una sua risposta | per preparare il colloquio |
| [RISPOSTE.md](RISPOSTE.md) | le stesse risposte ma **una sezione per richiesta**, con i rimandi alle schede | per cercare una risposta singola |

### Le lettere già pronte da inviare

Due richieste hanno anche una lettera a sé: stesso contenuto della scheda, ma
scritta per essere mandata così com'è, senza rimandi interni al progetto.

| lettera | copre |
|---|---|
| [lettera_A1.md](lettera_A1.md) | cambio di telecamera e di ambiente |
| [lettera_A2.md](lettera_A2.md) | occlusioni, e il protocollo leave-one-subject-out |

*Per le altre quattordici richieste la forma da mandare è la relazione unica.*

---

## A — Le quattro richieste iniziali

| | richiesta | stato | scheda |
|---|---|---|---|
| **A1** | Resilienza al cambio di telecamera e di ambiente | ✅ rifatta a dieci soggetti · le due cause **separate** · un risultato ritirato | [A1](A1_cambio_di_vista_e_di_ambiente.md) |
| **A2** | Resilienza alle occlusioni | ✅ nessun gruppo è critico · ⚠ il margine si è dimezzato, e dipende dalle colonne | [A2](A2_occlusioni.md) |
| **A3** | Porting su nodo edge, senza video verso l'esterno | ✅ fatta e **misurata**: il dispositivo è 3,6× più lento del dichiarato | [A3](A3_dispositivo_edge.md) |
| **A4** | Prova di durata in ambiente reale | ✅ 4,59 h sulla board · ⚠ non 12 h, e gli allarmi non sono verificabili | [A4](A4_prova_di_durata.md) |

## B — Le cinque verifiche indicate

| | verifica | stato | scheda |
|---|---|---|---|
| **B1** | PR-AUC nel passaggio all'archivio esterno | ✅ è perdita vera, non taratura | [B1](B1_pr_auc.md) |
| **B2** | Controesempi di una casa verificati sull'altra | ✅ fatta in entrambi i versi | [B2](B2_controesempi.md) |
| **B3** | Verifica controllata sulle occlusioni | ✅ fatta nella forma suggerita *(= A2)* | [B3](B3_occlusioni_controllate.md) |
| **B4** | Metriche di campo a livello di evento | ✅ **tutte e quattro**: la latenza è misurata in laboratorio, e in casa è dimostrato che non lo è | [B4](B4_eventi_e_latenza.md) |
| **B5** | Prova lunga con controllo della sospensione | ✅ sospensione misurata pari a zero | [B5](B5_prova_lunga.md) |

## C — I sette punti dell'email del 20 agosto

| | punto | stato | scheda |
|---|---|---|---|
| **C1** | Gli ingressi della foresta e le grandezze integrali | ⚠ meccanismo confermato, numeri no · sei architetture rifatte su v3 | [C1](C1_ingressi_della_foresta.md) |
| **C2** | Adattamento al dominio, non generalizzazione | ✅ fatto | [C2](C2_adattamento_al_dominio.md) |
| **C3** | Mostrare i due errori, non un solo F2 | ✅ la richiesta **più fertile** delle nove: due tabelle nuove e un'ipotesi smentita | [C3](C3_i_due_errori.md) |
| **C4** | Chiamarla soglia oracolo | ✅ fatto | [C4](C4_soglia_oracolo.md) |
| **C5** | La coerenza fra 4,47 e 2,20 ms | ⚠ spiegata, ma il numero di partenza è sospetto | [C5](C5_coerenza_dei_millisecondi.md) |
| **C6** | I parametri non dichiarati del richiamo di campo | ✅ recepito · e ora anche la **persistenza** ha una misura | [C6](C6_parametri_del_recall.md) |
| **C7** | L'indice aggiornato e la struttura | ✅ riscritto il 31 agosto | [C7](C7_indice_e_struttura.md) |

## D — Le sette domande rivolte a lui

Tutte in [D_domande_al_relatore.md](D_domande_al_relatore.md).

| | domanda | costa |
|---|---|---|
| **D1** | Fusione fra contesto e stato dell'arte | una decisione sul testo |
| **D2** | L'interpretazione sugli ingressi della foresta: tenerla o toglierla | una decisione sul testo |
| **D3** | La latenza: misurata in laboratorio, non misurabile in casa — è una forma accettabile? | una decisione sul testo |
| **D4** | Quale dei due sistemi installabili presentare | una decisione di merito |
| **D5** | *(nuova)* L'altezza dal pavimento: installarla o correggere il testo | una giornata sul dispositivo |
| **D6** | *(nuova)* I 4,47 ms attribuiti alla board | una decisione sul testo |
| **D7** | *(nuova)* Cambiare la regola di allarme | quattro righe di codice |

**D5 e D7 sono quelle che pesano di più**, perché migliorano il sistema
installato senza toccare il modello — e perché finché non sono decise il testo
descrive una configurazione diversa da quella che il dispositivo esegue.

---

## Come leggere le schede

Ognuna ha la stessa forma:

1. **che cosa è stato chiesto** — la richiesta, riformulata;
2. **la risposta in una riga** — così che ci si possa fermare lì;
3. **come ci siamo arrivati, passo per passo** — il ragionamento, gli errori
   commessi e corretti, le ipotesi verificate e quelle smentite;
4. **che cosa la risposta non copre** — i limiti dichiarati;
5. **dove guardare** — i file di risultato, gli script, le voci di registro.

Il quarto punto è deliberato: **dichiarare che cosa non si è fatto vale più che
descriverlo come se lo si fosse fatto**, ed è la regola che questo lavoro segue
ovunque.

---

## Gli esperimenti nuovi, per chi vuole risalire

Le misure del 6 e 7 settembre stanno nel registro degli esperimenti, un livello
sopra. Queste sono quelle a cui le schede rimandano più spesso:

| | che cosa ha misurato |
|---|---|
| EXP-022 | la riestrazione del dataset e la nuova selezione delle grandezze |
| EXP-023 | l'altezza dal pavimento su una architettura |
| EXP-024 | la prova di durata sulla board |
| EXP-025 | le sei architetture rifatte, con e senza l'altezza dal pavimento |
| EXP-026 | le tre righe sul punto di vista, e le due cause separate |
| EXP-027 | le occlusioni rimisurate, e la dipendenza dalle colonne |
| EXP-028 | la latenza in laboratorio, e la curva della persistenza |
| EXP-029 | ventuno regole di allarme a confronto |

E i difetti trovati in quei due giorni: **ISS-138** (dataset dipendente
dall'ordine), **ISS-139** (l'altezza dal pavimento che non c'era), **ISS-140**
(la sessione che spariva), **ISS-141** (i numeri sepolti), **ISS-142** (le clip
che non esistono), **ISS-143** (il risultato ritirato), **ISS-144** (la soglia
dei 60 gradi), **ISS-145** (il limite inferiore che non lo era).

---

## I registri del progetto

| | |
|---|---|
| [../ISSUES.md](../ISSUES.md) | i difetti, aperti e risolti, con la data e l'intervento |
| [../EXPERIMENTS.md](../EXPERIMENTS.md) | le run, comprese quelle fallite |
| [../CHANGELOG.md](../CHANGELOG.md) | le modifiche al codice |
| [../DECISIONS.md](../DECISIONS.md) | le scelte metodologiche |
| [../GUIDA_AL_LAVORO.md](../GUIDA_AL_LAVORO.md) | la stessa materia, ma scritta per me: che cosa regge e che cosa no |

Il documento precedente, `../RISPOSTE_AL_RELATORE.md`, è **superato da questa
cartella** ed è conservato per storia.
