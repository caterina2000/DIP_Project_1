# Scheda dei numeri — da avere a memoria per il 22 ottobre

Tutti i valori vengono dalla tesi attuale (`tesi/Cap3–Cap6.tex`). «n=5» e «n=10» indicano i soggetti.

## Dati e protocollo
| | |
|---|---|
| Dataset | UP-Fall, 10 soggetti su 17, 2 camere, 220 registrazioni (100 cadute, 120 ADL), 116.362 fotogrammi |
| Valutazione (Camera 1) | 58.359 fotogrammi, 110 registrazioni; posa valida 92,3% |
| Finestre | 11.719, di cui 1.491 positive (12,72%) |
| Finestra / stride | L = 22 campioni (2,44 s a 9 fps), stride 2 |
| Positivi nel test per fold | da 104 a 171 |
| Etichette | 0 attività 86,1% · 1 transizione 4,7% · 2 post-caduta 9,1% |
| Metrica | F2 (β = 2), fissata prima del confronto |
| Soglia | 0,50 fissa (scelta dopo il confronto di sei regole, dichiarato) |
| Soglie per-fold con max F2 in validazione | da 0,01 a 0,99, dev. 0,37 → instabili |
| Scala feature, prima/dopo | 646× → 1,05–1,35× |
| Candidate / selezionate | 33 → 12 (8 integrali), correlazione max 0,85 |
| Frame rate UP-Fall | mediana 18,09 fps (14,43–19,63) |

## Risultati principali (n=10, LOSO)
| Architettura | F2 | Recall | FN | FP | Parametri |
|---|---|---|---|---|---|
| GRU | 0,857 ± 0,089 | 0,940 | 89 | 938 | 24.483 |
| 1D CNN | 0,838 | 0,938 | 93 | 1.134 | 46.147 |
| Transformer | 0,837 | 0,920 | 119 | 969 | 34.499 |
| LSTM | 0,829 | 0,945 | 82 | 1.266 | 32.227 |
| Random Forest | 0,825 | 0,844 | 232 | 468 | 12.928 nodi |
| Rete a grafo | 0,794 | 0,860 | 209 | 934 | 12.323 |

- Dev. standard di F2 tra soggetti: circa 0,05–0,14.
- Correzione per confronti multipli: critico ≈ 3,25; nessun confronto lo supera (max |t| = 3,14).
- Soggetti necessari: GRU/RF 52, GRU/Transformer 54, GRU/CNN 58, GRU/LSTM 9, GRU/grafo 8.
- Rappresentazioni: A3 senza integrali 0,831 · con integrali 0,832 · DTW 0,825 → spread 0,007.
- Finestra: 22 → 0,825 · 28 → 0,851 · 36 → 0,871 · 44 → 0,915 (t = 3,62).
- Alberi (10/50/400): F2 0,850 / 0,838 / 0,836; tempo per finestra 1,8 → 43,7 ms.
- Compiti (event/state/alarm): F2 0,415 / 0,587 / 0,830; in casa 1,6 / 29,5 / 36,4 eventi/h, cadute 3/5, 0/5, 4/5.
- Dinamica caduta/stendersi: velocità anche 30,1×, escursione tronco 42,5×, percorso 33,0×, discesa 139,4×.
- Rumore σ = 0,04: perdita massima 0,031. Occlusioni: spalle −0,037, massimo.

## Punto di vista e dominio
| | |
|---|---|
| Escursione tronco, Camera 1 / 2 | 74,0° / 33,2° (39 coppie valide) |
| Sequenze > 60° | 30/39 contro 8/39 |
| Cam 2 perde la persona che cade | 11 cadute su 50 |
| Addestra C1 → test C1 | F2 0,822 |
| Addestra C1 → test C2 | 0,488 (FP 722 → 3.252) |
| Addestra C1+C2 → test C2 | 0,731 |
| h_pav separazione mediane | +1,510 laterale, +0,060 rialzata |
| h_pav nel DTW | 1,541 (cam 1), 1,124 (cam 2), 21° con il minimo |
| Trasferimento a UR-Fall (soglia 0,50) | A3 0,404 · A3i 0,479 · DTW 0,630 (PR-AUC 0,660, guadagno 5,1×) |
| Config. precedente | 0,971 sorgente → 0,034 diretto → 0,492 oracolo |
| Posa valida su UR-Fall | 81,0% (UP-Fall 92,3%) |

## Controlli di leakage
- K: 9 fold su 10 scelgono 45; F2 0,825 → 0,851; t = 2,22 (critico 2,26); senza soggetto 9: Δ 0,016, t = 2,72.
- Feature: Jaccard medio 0,769; sei feature sempre selezionate; nessun fold uguale al sottoinsieme usato; effetto sulle metriche **non** quantificato.

## Board (Radxa ROCK 4D, RK3576, 6 GB, NPU 6 TOPS, ~100 € per stanza)
| | MediaPipe CPU (installato) | YOLOv8-pose NPU |
|---|---|---|
| Percezione | 116,38 ms (85,2%) | 33,34 ms (88,4%) |
| Classificazione | 19,51 ms (14,3%) | 2,21 ms |
| Totale per fotogramma | 136,65 ms → 7,3 fps | 37,7 ms → 26,5 fps |

- Foresta: 39,04 ms per finestra sulla board (≈ 4,85 ms sul calcolatore).
- Inferenza YOLO 5,16× più veloce; post-processing 12,14 → 0,94 ms.
- F2 n=5: MediaPipe 0,909 · YOLOv8 INT8 0,682. A 18 → 9 fps: −0,041; cambio stimatore: −0,216 (5,3×).
- Posa trattenuta da sdraiati: 43,6% (YOLO) · 79,1% (MediaPipe).
- Memoria 297 MB (5%), modello 606.409 byte. **Consumo non misurato.**
- Durata: 4,59 h, cadenza 7,26 fps, 14 eventi, 2 cadute della camera (~5 s). Massimo 79,5 °C (sessione 11 agosto, 6,11 h wall-clock, 68 min di sospensione).
- Equivalenza: 200 finestre → 0 decisioni diverse; 56 clip → 55 uguali, 1 diversa (una caduta).
- Frequenza reale in casa: 1,15–8,20 fps; con persone: 7,5 / 4 / 2–3 fps.

## Campo (case)
| | |
|---|---|
| Blocchi agosto | 12, 4 giorni, 2 case, 9,6 h; posa valida 77,8% |
| Sessioni per gli eventi | 9, 14,98 h (wall clock); 1,41 h senza decisioni |
| Finestre sopra soglia / evento | 44,8 |
| Eventi all'ora | 11,1 (12,2 sulle sole ore con decisioni) |
| Cadute | 5 simulate, 4 annotate al fotogramma il 9 settembre |
| Recall | 4/5 (±60 s, persistenza 1) · 2/5 (persistenza 5) · IC 95% 0,28–0,99 |
| Sessione con le cadute | 25,9% di pose valide |
| Latenza, a 8,02 fps | 3,865 s = 0,125 + 2,743 (finestra) + 0,997 (persistenza) |
| Regola d'allarme | soglia 0,50, 5 finestre consecutive, refrattario 30 s |
| Seconda caduta del 9 settembre | riconosciuta, soppressa dal refrattario (6 s dopo la prima) |
| Con h_pav, sequenze con decisione | 36/422 (8,5%) |
| FP prima del campo | 46 su 4.767 negative (0,96%) → ~3.751 finestre/giorno a stride 2 |

Configurazioni, laboratorio contro casa (Cap. 5):

| | F2 lab | finestre/h a casa | cadute |
|---|---|---|---|
| A3 | 0,898 | 139,9 | 3/5 |
| A3h | 0,931 | 70,4 | 2/5 |
| A3h + controesempi | 0,942 | 2,1 | 2/5 |
| A3i | 0,943 | 9,8 | 4/5 |
| A3i + controesempi | 0,953 | 2,7 | 3/5 |

Controesempi trasferiti tra case: casa 1 da 0,342 a 0,171 eventi/h; casa 2 da 1,781 a 0,890.

## Valori che sembrano contraddirsi: preparati
- **A3: 0,831 (Cap. 4) e 0,898 (Cap. 5).** Tabelle e configurazioni diverse; non ho potuto verificare il motivo dai soli testi.
- **0,857** compare per la GRU (n=10) e per MediaPipe a 9 fps (n=5): coincidenza.
- **K = 31** scelto in parte su dati domestici; il controllo per fold dice che non gonfia il laboratorio.
- **4/5 contro 2/5**: dipende dal criterio, non dal modello.
- **h_pav** è il 21° nel DTW (Cap. 3) ma serve in casa: il criterio guarda ogni feature da sola.

## Cinque cose da dire in 15 secondi
1. Architettura ≈ variabilità tra soggetti; geometria della camera e dominio contano di più.
2. Il collo di bottiglia della board è la posa (85%), non il classificatore.
3. Finestre ≠ allarmi: rapporto 44,8; regola con persistenza e refrattario.
4. Cinque cadute simulate: caratterizzazione, non validazione.
5. Tutto ciò che ho scelto guardando i dati di valutazione l'ho dichiarato e misurato dove possibile.
