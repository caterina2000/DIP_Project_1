# C5 — Punto 8: la coerenza fra 4,47 e 2,20 ms

**Che cosa è stato chiesto:** nel testo il costo del classificatore compare con
due valori diversi, 4,47 ms in un capitolo e 2,20 ms in un altro. O uno dei due
è sbagliato, o manca la spiegazione.

**La risposta in una riga:** **la spiegazione c'era e ora è scritta** — sono la
stessa misura in due unità — **ma il 6 settembre è emerso che il numero di
partenza è probabilmente quello sbagliato**, e questa parte resta aperta.

---

## Passo 1 — La spiegazione, che è corretta

Il classificatore **non viene eseguito a ogni fotogramma**. La finestra avanza
con passo due, quindi si decide una volta ogni due fotogrammi:

- **4,47 ms per finestra** — il costo di una decisione;
- **2,20 ms per fotogramma** — lo stesso costo ammortizzato, cioè circa la metà.

Non sono due misure in disaccordo, sono la stessa misura in due unità. Il
Capitolo 5 riporta ora entrambe con la spiegazione accanto, perché senza sembra
una contraddizione.

## Passo 2 — Il controllo indipendente del 27 agosto

Misurando il costo per finestra delle sei architetture **sul calcolatore**, la
foresta dà **4,85 ms**: compatibile con i 4,47 dichiarati. All'epoca fu letto
come la prima conferma esterna che quel numero avesse mai avuto.

Nello stesso risultato emerge un fatto che obbliga a una precisazione nel testo:
**la foresta è la più lenta per finestra delle sei architetture**. È stata
scelta per costo di addestramento, dipendenze e riproducibilità, non per
velocità in inferenza, e ora il testo lo dice.

## Passo 3 — Il 6 settembre: la stessa vicinanza diventa il sospetto

Misurando il classificatore **sulla board**, dentro l'esecuzione vera:

| | valore |
|---|---:|
| dichiarato in tesi, «sulla board» | 4,47 ms per finestra |
| misurato sul **calcolatore** | 4,85 ms per finestra |
| **misurato sulla board** | **39,04 ms per finestra** |

**La board è otto volte più lenta del numero che le è attribuito, e il numero
che le è attribuito dista l'8% da quello del calcolatore.** Sembra un numero del
PC etichettato come numero della board ([ISS-137](../ISSUES.md)).

Se è così, la vicinanza del controllo del 27 agosto non era una conferma: era il
sintomo.

## Che cosa resta da decidere

Due strade, ed è una decisione sul testo:

1. **ritirare** i 4,47 ms dal Capitolo 4;
2. **dichiararli** per quello che sono — una misura sul calcolatore — e mettere
   accanto i 39,04 ms della board.

La seconda conserva l'informazione e rende visibile il rapporto di otto fra le
due macchine, che è a sua volta un dato del lavoro.

---

## Dove guardare

| | |
|---|---|
| costo per finestra delle sei architetture | [EXP-019](../EXPERIMENTS.md), `risultati/compiti/` |
| misura sulla board | `risultati/sessioni/20260906/notte_20260906_1523/notte_20260906_1523_riepilogo.json` |
| registro | [ISS-137](../ISSUES.md), [ISS-113](../ISSUES.md) |
| nella tesi | Capitolo 5, «Una nota sulle unità»; Capitolo 4, costo del classificatore |
