# C6 — Punto 9: i parametri non dichiarati del recall di campo

**Che cosa è stato chiesto:** il recall misurato in casa dipende da parametri
che non erano dichiarati. Senza quelli, il numero non è interpretabile — e non è
confrontabile con nessun altro lavoro.

**La risposta in una riga:** **recepito**: il recall di campo è ora riportato
come **intervallo con i parametri esposti**, mai come numero singolo.

---

## I tre parametri, e che cosa cambia ciascuno

### 1. L'unità: evento o finestra

Un sistema installato non produce finestre, produce **eventi**. Sulle stesse
registrazioni le due contabilità differiscono di un fattore **44,8**
([B4](B4_eventi_e_latenza.md)). È il parametro che pesa di più: sbagliarlo
sposta il risultato di quasi due ordini di grandezza.

### 2. La tolleranza di accoppiamento

Perché una segnalazione conti come «caduta rilevata», deve cadere entro una
certa distanza temporale dalla caduta annotata. Quella distanza è una scelta, e
il recall dipende da essa: le annotazioni delle sessioni domestiche sono **al
minuto** ([B4](B4_eventi_e_latenza.md)), quindi una tolleranza stretta
scarterebbe rilevamenti corretti solo perché l'istante vero non è noto.

### 3. La persistenza

Quante finestre consecutive sopra soglia servono per dichiarare un allarme.
Alzarla riduce i falsi allarmi e fa perdere cadute brevi; abbassarla fa il
contrario. Il sistema installato usa **cinque** finestre e **trenta secondi** di
sospensione, e sono dichiarate ovunque compaia un numero di campo.

---

## Come si presenta ora il numero

Non «il recall di campo è X», ma: *con questa tolleranza, questa persistenza e
contando eventi, il recall sta fra A e B*. La sensibilità ai due parametri di
aggregazione è mostrata esplicitamente, perché **il conteggio degli eventi non è
una proprietà dei dati: dipende da come si aggrega**, e nasconderlo
renderebbe il numero non riproducibile.

## E la precisazione che pesa più di tutte

**Cinque cadute non stimano un recall.** L'intervallo di confidenza va da
**0,28 a 0,99**: qualunque valore riportato è compatibile con quasi qualunque
altro. È la ragione per cui nel testo non compare una configurazione vincitrice
scelta su «quattro su cinque contro tre su cinque»
([D4](D_domande_al_relatore.md)), ed è il limite più serio del lavoro.

---

## Dove guardare

| | |
|---|---|
| eventi e sensibilità ai parametri | `pipeline/eventi_sessioni.py --sensibilita`, `risultati/campo/eventi_sessioni.json` |
| recall di campo | `risultati/campo/compiti_in_casa.json` |
| registro | [ISS-140](../ISSUES.md), [EXP-017](../EXPERIMENTS.md) |
| nella tesi | Capitolo 5, sezione sulle metriche di campo |
