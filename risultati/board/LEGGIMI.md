# Scansione delle 56 clip, sul PC e sulla board

Dati grezzi di [EXP-016](../../docs/EXPERIMENTS.md#exp-016), copiati dalla
board il 22 agosto 2026 prima dello spegnimento.

Blocco: `bloccocadute_nonni_20260812_154007`, 56 clip.

## Colonne

```
nome_clip    pose_valide%    picco_punteggio    finestre_sopra_soglia    allarmi_emessi
```

L'ultima colonna applica la regola dichiarata: cinque finestre consecutive
sopra `0,50` e trenta secondi di sospensione.

## Che cosa dicono

| | PC | board |
|---|---:|---:|
| allarmi emessi | 2 | 1 |
| pose valide (media) | 96,4% | 96,3% |
| clip con decisione identica | — | 55 / 56 |
| picco: scarto medio | — | 0,063 |
| picco: correlazione | — | r = 0,781 |

L'unica divergenza di comportamento e' `evt_0067_155044`, **che e' una caduta
vera**: il PC la porta a 1,000 con nove finestre sopra soglia ed emette
l'allarme, la board si ferma a 0,560 con due finestre e l'antirimbalzo non
scatta.

La causa non e' il classificatore --- la parita' sulle finestre precalcolate
e' esatta, scarto `0,000e+00` --- ma lo stimatore di posa, che e' un
tracciatore e diverge fra architetture: [ISS-106](../../docs/ISSUES.md#iss-106).
