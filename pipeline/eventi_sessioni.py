"""
Metriche a livello di EVENTO per le sessioni domestiche.

Perche' esiste
--------------
Il grafico F4 e i numeri della lettera contano FINESTRE sopra soglia, e le
confrontano con lo 0,4/ora che la letteratura riporta per installazioni reali.
Le due grandezze non sono la stessa cosa: una singola falsa attivazione produce
decine di finestre consecutive sopra soglia, che un sistema installato aggrega
in un evento solo. Confrontarle direttamente sovrastima i nostri falsi allarmi
di uno o due ordini di grandezza.

Questo script rilegge i `punteggi.csv` gia' registrati dalla board -- il
punteggio di ogni finestra con il suo istante -- e ricalcola tutto con la
contabilita' corretta. Non riesegue nessun modello: sono le decisioni che la
board ha davvero preso.

Le due contabilita', e perche' servono entrambe
-----------------------------------------------
EVENTI. Una raffica di finestre consecutive sopra soglia e' un allarme solo.
Si dichiara un evento dopo `persistenza` finestre consecutive sopra soglia, e
poi si tace per `sospensione` secondi. E' la contabilita' che descrive cosa
sente l'utente, ed e' quella confrontabile con la letteratura.

TEMPO IN ALLARME. La quota di tempo in cui il punteggio sta sopra soglia. Serve
perche' il falso positivo dominante di questo progetto NON e' un evento: due
persone anziane distese sui divani per un'ora sono uno STATO che dura. La
sospensione lo ritaglia in eventi periodici e ne nasconde la natura -- il
numero di eventi diventa una funzione del periodo di sospensione invece che
del fenomeno. La quota di tempo, invece, e' la stessa qualunque sospensione si
scelga, e dice la verita': il sistema ha passato il 40% del pomeriggio
convinto che qualcuno fosse caduto.

Riportare solo la prima nasconderebbe il problema; riportare solo la seconda
non sarebbe confrontabile con nessuno.

Uso:
    python scripts/eventi_sessioni.py
    python scripts/eventi_sessioni.py --soglia 0.5 --persistenza 5 --sospensione 30
    python scripts/eventi_sessioni.py --sensibilita
"""

import argparse
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Dove stanno le sessioni, in ordine di preferenza:
#
#   1. la variabile SESSIONI_REALI, se qualcuno la imposta;
#   2. risultati/sessioni dentro questo progetto --- i punteggi per finestra,
#      i riepiloghi e i controlli di sanita', SENZA le clip. Bastano a
#      ricalcolare qualunque numero: la regola di decisione si applica ai
#      punteggi, non alle immagini;
#   3. la cartella di raccolta nel progetto storico, che contiene anche le
#      clip. Quelle non vengono duplicate qui perche' ritraggono persone
#      identificabili, ed e' l'unico dato del progetto per cui la copia in
#      piu' e' un rischio e non una comodita'.
def elenco_punteggi(radice: str) -> 'list[str]':
    """
    I file dei punteggi per finestra, un elemento per sessione.

    Due registratori hanno prodotto due nomi diversi. Le sessioni fino al
    13 agosto vengono da `session_recorder.py` e si chiamano tutte
    `punteggi.csv`; quelle di `deploy_board/rileva.py` portano il nome della
    sessione, per esempio `notte_20260906_1523.csv`. Cercare solo il primo
    nome faceva sparire la sessione del 6 settembre dal conto SENZA dirlo:
    lo script stampava sette blocchi invece di otto e nessun errore
    ([ISS-140](../docs/ISSUES.md#iss-140)).

    Il file delle feature, che sta nella stessa cartella e finisce per
    `_feature.csv`, non e' un file di punteggi e va escluso.
    """
    fuori = []
    for cartella in sorted(glob.glob(os.path.join(radice, '*', '*'))):
        if not os.path.isdir(cartella):
            continue
        canonico = os.path.join(cartella, 'punteggi.csv')
        if os.path.exists(canonico):
            fuori.append(canonico)
            continue
        proprio = os.path.join(cartella, os.path.basename(cartella) + '.csv')
        if os.path.exists(proprio):
            fuori.append(proprio)
    return fuori


def _dove_sono_le_sessioni():
    da_ambiente = os.environ.get('SESSIONI_REALI')
    if da_ambiente:
        return da_ambiente
    locale = os.path.join(RADICE, 'risultati', 'sessioni')
    if elenco_punteggi(locale):
        return locale
    return os.path.join(os.path.dirname(RADICE), 'DIP_PROJECT',
                        'sessioni_reali')


SESSIONI = _dove_sono_le_sessioni()

dec = lambda v, n=1: f'{v:.{n}f}'.replace('.', ',')


def eventi(sopra: np.ndarray, tempi: np.ndarray, persistenza: int,
           sospensione: float):
    """
    Indici in cui scatta un allarme.

    Un allarme richiede `persistenza` finestre consecutive sopra soglia, e dopo
    averlo emesso il sistema tace per `sospensione` secondi. E' la stessa regola
    del sistema installato, non una ricostruzione a posteriori.
    """
    fuori, corsa, ultimo = [], 0, -1e18
    for i, s in enumerate(sopra):
        corsa = corsa + 1 if s else 0
        if corsa >= persistenza and (tempi[i] - ultimo) >= sospensione:
            fuori.append(i)
            ultimo = tempi[i]
    return fuori


def tempo_e_decisione(d: 'pd.DataFrame', soglia):
    """
    Istante e decisione per finestra, qualunque sia il registratore.

    `session_recorder.py` scrive `t_unix` (epoch) e `sopra_soglia`;
    `rileva.py` scrive `t_s` (secondi dall'avvio, orologio monotono) e
    `sopra`. Per il conteggio degli eventi conta solo la DIFFERENZA fra gli
    istanti, quindi le due origini sono equivalenti.

    `soglia=None` usa la colonna registrata dalla board, cioe' la decisione
    effettivamente presa in esercizio; un valore esplicito la ricalcola.
    """
    t = d['t_unix' if 't_unix' in d.columns else 't_s'].to_numpy(float)
    p = d['punteggio'].to_numpy(float)
    colonna = 'sopra_soglia' if 'sopra_soglia' in d.columns else 'sopra'
    sopra = (d[colonna].to_numpy() == 1) if soglia is None else (p >= soglia)
    return t, p, sopra


def analizza(percorso: str, soglia, persistenza: int, sospensione: float):
    d = pd.read_csv(percorso)
    if len(d) < 2 or 'punteggio' not in d.columns:
        return None
    t, p, sopra = tempo_e_decisione(d, soglia)
    ore = (t.max() - t.min()) / 3600.0
    if ore < 1e-4:
        return None

    ev = eventi(sopra, t, persistenza, sospensione)
    # tempo medio fra falsi allarmi: con meno di due eventi non e' definito
    mtba = (np.diff(t[ev]).mean() / 60.0) if len(ev) >= 2 else float('nan')

    return {
        'blocco': os.path.basename(os.path.dirname(percorso)),
        'ore': ore, 'finestre': len(d),
        'finestre_sopra': int(sopra.sum()),
        'finestre_ora': sopra.sum() / ore,
        'eventi': len(ev), 'eventi_ora': len(ev) / ore,
        'mtba_min': mtba,
        'quota_tempo': float(sopra.mean()),
        'fattore': (sopra.sum() / len(ev)) if len(ev) else float('nan'),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--soglia', type=float, default=None,
                    help='ricalcola con questa soglia; senza, usa la decisione '
                         'registrata dalla board')
    ap.add_argument('--persistenza', type=int, default=5,
                    help='finestre consecutive sopra soglia per un allarme')
    ap.add_argument('--sospensione', type=float, default=30.0,
                    help='secondi di silenzio dopo un allarme')
    ap.add_argument('--min-ore', type=float, default=0.15)
    ap.add_argument('--sensibilita', action='store_true',
                    help='mostra come cambia il conteggio al variare dei due '
                         'parametri di debounce')
    a = ap.parse_args()

    elenco = elenco_punteggi(SESSIONI)
    righe = [r for f in elenco
             if (r := analizza(f, a.soglia, a.persistenza, a.sospensione))
             and r['ore'] >= a.min_ore]
    if not righe:
        sys.exit(f'nessuna sessione utilizzabile in {SESSIONI}')

    print(f'sessioni da: {SESSIONI}')
    print('=' * 100)
    print(f'EVENTI CONTRO FINESTRE — persistenza {a.persistenza}, '
          f'sospensione {dec(a.sospensione, 0)} s, '
          f'soglia {"registrata dalla board" if a.soglia is None else dec(a.soglia, 2)}')
    print('=' * 100)
    print(f"{'blocco':<34}{'ore':>6}{'finestre/ora':>14}{'EVENTI/ora':>12}"
          f"{'fattore':>9}{'MTBA min':>10}{'tempo in allarme':>18}")
    print('-' * 100)
    for r in sorted(righe, key=lambda x: -x['eventi_ora']):
        m = dec(r['mtba_min']) if np.isfinite(r['mtba_min']) else '—'
        f = dec(r['fattore']) if np.isfinite(r['fattore']) else '—'
        print(f"{r['blocco'][:33]:<34}{dec(r['ore'], 2):>6}"
              f"{dec(r['finestre_ora'], 0):>14}{dec(r['eventi_ora']):>12}"
              f"{f:>9}{m:>10}{dec(100*r['quota_tempo']) + '%':>18}")

    tot_ore = sum(r['ore'] for r in righe)
    tot_fin = sum(r['finestre_sopra'] for r in righe)
    tot_ev = sum(r['eventi'] for r in righe)
    print('-' * 100)
    print(f"{'TOTALE':<34}{dec(tot_ore, 2):>6}"
          f"{dec(tot_fin / tot_ore, 0):>14}{dec(tot_ev / tot_ore):>12}"
          f"{dec(tot_fin / max(tot_ev, 1)):>9}")
    print()
    print(f'Il fattore di sovrastima e\' {dec(tot_fin / max(tot_ev, 1))}: '
          f'contando finestre invece che eventi i falsi allarmi risultano')
    print(f'{dec(tot_fin / max(tot_ev, 1))} volte piu\' numerosi di quelli che '
          f'una persona in casa percepirebbe.')
    print('Riferimento di letteratura per installazioni funzionanti:')
    print('   0,049 eventi/ora   studio longitudinale, 15.500 ore, 16 anziani')
    print('   0,22 al giorno     pilota in casa di riposo')
    print('Il valore 0,4/ora usato finora nel progetto non trova riscontro:')
    print('e otto volte lo studio piu solido (ISS-050).')

    # L'artefatto. Il fattore di sovrastima e' citato nel Capitolo 5, nella
    # guida al lavoro e nel documento per il relatore, e fino al 7 settembre
    # 2026 esisteva SOLTANTO in quei testi: `audit_numeri.py` lo dava per
    # coperto perche' la cifra compariva per caso dentro altri file
    # ([ISS-135](../docs/ISSUES.md#iss-135)). Ora ogni esecuzione lo scrive,
    # con la tabella da cui esce.
    fuori = {
        # relativo: l'artefatto viaggia fra macchine, il percorso assoluto no
        'sorgente': os.path.relpath(SESSIONI, RADICE),
        'persistenza': a.persistenza,
        'sospensione_s': a.sospensione,
        'soglia': 'registrata dalla board' if a.soglia is None else a.soglia,
        'min_ore': a.min_ore,
        'n_sessioni': len(righe),
        'ore_totali': tot_ore,
        'finestre_sopra_totali': tot_fin,
        'eventi_totali': tot_ev,
        'eventi_ora_totale': tot_ev / tot_ore,
        'finestre_ora_totale': tot_fin / tot_ore,
        'fattore_sovrastima': tot_fin / max(tot_ev, 1),
        'sessioni': sorted(righe, key=lambda x: -x['eventi_ora']),
    }
    dst = os.path.join(RADICE, 'risultati', 'campo', 'eventi_sessioni.json')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(fuori, f, indent=1, ensure_ascii=False)
    print()
    print(f'scritto: {os.path.relpath(dst, RADICE)}')

    if a.sensibilita:
        print()
        print('=' * 100)
        print('SENSIBILITA\' AI DUE PARAMETRI DI DEBOUNCE — eventi/ora sul totale')
        print('Il conteggio degli eventi non e\' una proprieta\' dei dati: '
              'dipende da come si aggrega.')
        print('=' * 100)
        print(f"{'persistenza':>12}" + ''.join(f'{"sosp. " + str(s) + " s":>14}'
                                               for s in (10, 30, 60, 300)))
        print('-' * 100)
        for pers in (1, 3, 5, 10):
            riga = f'{pers:>12}'
            for sosp in (10, 30, 60, 300):
                n = 0
                for f in elenco:
                    d = pd.read_csv(f)
                    if len(d) < 2:
                        continue
                    t, _, sopra = tempo_e_decisione(d, a.soglia)
                    if (t.max() - t.min()) / 3600 < a.min_ore:
                        continue
                    n += len(eventi(sopra, t, pers, sosp))
                riga += f'{dec(n / tot_ore):>14}'
            print(riga)
        print()
        print('Per questo la quota di TEMPO in allarme e\' la misura piu\' onesta '
              'per un falso positivo')
        print('che e\' uno stato e non un evento: non dipende da questi due '
              'parametri.')


if __name__ == '__main__':
    main()
