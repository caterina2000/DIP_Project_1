"""
Da quale codice viene un numero.

Il problema
-----------
Un file di risultato che contiene solo il numero non e' rifacibile. E' il caso
di ISS-113: la ripartizione del costo per fotogramma --- 33,34 ms di percezione
contro 2,20 di classificatore --- fu trascritta da una sessione di terminale, e
oggi non esiste alcun file che la produca. Cercandola nei JSON, CSV, TXT e MD
dei due progetti non compare da nessuna parte.

Il rimedio non e' ricordarsi di annotare: e' che ogni scrittura di risultato
porti con se' commit, data, comando e versioni, senza che chi scrive lo script
debba pensarci.

Uso
---
    from src.provenienza import scrivi_json
    scrivi_json('risultati/laboratorio/costo.json', dati)

Il file conterra' i dati piu' una chiave `_provenienza`. La chiave comincia con
un trattino basso perche' chi rilegge il file per estrarne numeri la ignori
senza doverla conoscere.

Che cosa NON fa
---------------
Non blocca nulla se git non c'e' o se la cartella non e' un repository: in quel
caso scrive `"commit": null` e prosegue. Un risultato senza provenienza e'
peggio di uno con, ma molto meglio di uno che non e' stato prodotto perche' la
strumentazione ha sollevato un'eccezione.

`albero_pulito` e' la chiave che conta piu' del commit: dice se al momento
della run c'erano modifiche non committate. Con `false`, il commit indica
soltanto il punto di partenza e non lo stato reale del codice.
"""

import json
import os
import platform
import subprocess
import sys
import time

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _git(*argomenti):
    """Esito di un comando git, oppure None se git non risponde."""
    try:
        fuori = subprocess.run(('git',) + argomenti, cwd=RADICE,
                               capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if fuori.returncode != 0:
        return None
    return fuori.stdout.strip()


def provenienza(extra=None):
    """
    Dizionario con commit, stato dell'albero, data, comando e versioni.

    `extra` viene fuso nel risultato: serve a chi vuole aggiungere qualcosa
    di specifico, per esempio il nome del file di feature usato.
    """
    commit = _git('rev-parse', 'HEAD')
    stato = _git('status', '--porcelain')

    d = {
        'commit': commit,
        'commit_breve': commit[:8] if commit else None,
        # None quando git non risponde: e' diverso da «albero pulito», e i due
        # casi non vanno confusi in lettura
        'albero_pulito': (stato == '') if stato is not None else None,
        'data': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'comando': ' '.join(sys.argv),
        'python': platform.python_version(),
        'macchina': platform.node(),
        'sistema': platform.system(),
    }
    for nome in ('numpy', 'pandas', 'sklearn', 'tensorflow'):
        try:
            d[nome] = __import__(nome).__version__
        except Exception:
            pass
    if extra:
        d.update(extra)
    return d


def scrivi_json(percorso, dati, extra=None, indent=1):
    """
    Scrive `dati` in JSON aggiungendo la chiave `_provenienza`.

    La scrittura e' ATOMICA: prima un file temporaneo, poi `os.replace`. Senza,
    un'interruzione a meta' scrittura lascia un JSON troncato al posto del
    risultato precedente, e il danno e' silenzioso perche' il file esiste.
    """
    if not isinstance(dati, dict):
        raise TypeError('scrivi_json vuole un dizionario, cosi che la chiave '
                        '_provenienza possa esservi aggiunta')
    cartella = os.path.dirname(os.path.abspath(percorso))
    if cartella:
        os.makedirs(cartella, exist_ok=True)

    contenuto = dict(dati)
    contenuto['_provenienza'] = provenienza(extra)

    tmp = percorso + '.parziale'
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(contenuto, fh, ensure_ascii=False, indent=indent)
    os.replace(tmp, percorso)
    return percorso


def riga_provenienza():
    """Una riga sola, per le intestazioni stampate a schermo."""
    p = provenienza()
    c = p['commit_breve'] or 'senza git'
    if p['albero_pulito'] is False:
        c += ' + modifiche non committate'
    return f"{c} · {p['data']}"
