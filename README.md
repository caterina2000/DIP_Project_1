# Rilevamento cadute da video RGB su dispositivo edge

Tesi magistrale in Ingegneria dell'Intelligenza Artificiale e dell'Automazione,
Università di Siena.

Pipeline: `video RGB → MediaPipe Pose → feature geometriche → finestre
temporali (~2,4 s) → classificatore → allerta`, pensata per girare su un
dispositivo edge da ~100 euro senza che alcuna immagine lasci il dispositivo.

La domanda a cui risponde il classificatore è «sta cadendo?», non «è a
terra?» — è la scelta che separa un sistema usabile da uno che suona per un
pomeriggio intero quando due persone sono sedute sul divano.

---

## Relazione con l'altro repository

Questo progetto continua [**DIP_PROJECT /
Fall-Detection-project**](https://github.com/caterina2000/Fall-Detection-project),
il lavoro iniziale di Digital Image Processing da cui sono nati la pipeline di
estrazione feature e il primo confronto fra metodi di rappresentazione.

La tesi è stata spostata qui il 23 agosto 2026 e da qui prosegue il lavoro
attivo: testo, pipeline e codice di libreria. `DIP_PROJECT` resta come
progetto storico — raccolta sessioni reali e registro delle sperimentazioni
iniziali.

---

## Il dataset

Il progetto usa **UP-Fall** (55 sequenze, 5 soggetti) più le sessioni
registrate in ambiente reale durante la validazione su dispositivo edge — lo
stesso dataset descritto nel README e in `docs/` di
[DIP_PROJECT](https://github.com/caterina2000/Fall-Detection-project).

**Non è incluso in nessuno dei due repository**, per due motivi:

- **dimensione** — il dataset grezzo pesa diversi gigabyte, oltre ai limiti
  ragionevoli per un repository git;
- **privacy** — le sessioni reali contengono fotogrammi di persone
  identificabili (familiari). Non vengono mai tracciate né pubblicate: il
  `.gitignore` le esclude esplicitamente, e la regola di decisione del
  sistema si applica solo ai punteggi numerici, mai alle immagini.

Per ottenere UP-Fall: [sito ufficiale del
dataset](https://sites.google.com/up.edu.mx/har-up/). Le feature estratte e
il dettaglio della pipeline di elaborazione sono documentati in
`docs/PROJECT_CONTEXT.md`.

---

## Struttura

```
DIP_Project_1/
├── tesi/          testo della tesi (cinque capitoli), figure, controlla.py
├── pipeline/      script che producono risultati e figure
├── src/           codice di libreria (geometria, dati, modelli)
├── risultati/     numeri prodotti, incluse le sessioni di campo
├── dataset/       feature estratte (dataset grezzo escluso, vedi sopra)
├── deploy_board/  codice eseguito sul dispositivo edge
└── docs/          registro vivo: contesto, changelog, esperimenti, difetti, decisioni
```

---

## Documentazione

Il progetto mantiene un registro vivo in [`docs/`](docs/), aggiornato a ogni
intervento:

| Documento | Contenuto |
|---|---|
| [PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md) | **Da leggere per primo.** Mappa di cosa sta dove e perché |
| [ISSUES.md](docs/ISSUES.md) | Difetti catalogati, con gravità ed evidenza |
| [EXPERIMENTS.md](docs/EXPERIMENTS.md) | Ogni run di training, test e analisi |
| [CHANGELOG.md](docs/CHANGELOG.md) | Modifiche al codice, datate e motivate |
| [DECISIONS.md](docs/DECISIONS.md) | Scelte metodologiche e loro supporto empirico |

[`CLAUDE.md`](CLAUDE.md) contiene le regole di lavoro sul repository.

---

## Stato

Lavoro di tesi attivo, non concluso. Lo stato verificato — cosa funziona, cosa
è ancora da validare, i limiti noti (fra cui il numero ridotto di cadute reali
registrate finora) — è in [`docs/PROJECT_CONTEXT.md`](docs/PROJECT_CONTEXT.md)
e nella sezione "Lavoro aperto" di [`CLAUDE.md`](CLAUDE.md#6-lavoro-aperto).
