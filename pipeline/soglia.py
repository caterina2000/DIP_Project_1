"""
Confronta le regole di scelta della soglia, senza riaddestrare nulla.

Perche' e' un esperimento a se'
------------------------------
La prima LOSO ha dato F2 = 0,813 con dispersione 0,110, ma guardando i fold si
vede che il modello non varia quanto la soglia: le soglie scelte andavano da
0,01 a 0,99, e i cinque fold in cui il tasso di allarme risultante era vicino
alla prevalenza vera (~12%) hanno dato F2 fra 0,88 e 0,95, mentre i quattro in
cui era due volte e mezzo tanto hanno dato 0,64-0,80.

Non e' il modello che va male su quei soggetti: e' la soglia scelta male. E la
soglia e' una decisione a valle, che si puo' cambiare senza toccare i pesi --
purche' le probabilita' siano state salvate. Con `punteggi_*.npz` su disco,
confrontare sei regole costa secondi invece di sei ore.

Le regole
---------
    fbeta       massimo F-beta sul validation           (quella attuale)
    f1          massimo F1: stessa idea, senza il peso 4x sul recall
    youden      massimo (recall + specificita' - 1)     indipendente dalla
                                                        prevalenza
    prevalenza  taglia dove la quota di allarmi sul validation eguaglia la
                quota di positivi veri del validation
    prev15      come sopra ma con margine: 1,5 volte la quota
    fissa05     0,5, come riferimento minimo

Cosa si misura
--------------
Non solo F2 medio. Anche e soprattutto il TRASFERIMENTO: di quanto il tasso di
allarme sul test si discosta da quello che la stessa soglia produceva sul
validation. Una regola che vince sulla media ma non trasferisce e' una regola
che ha avuto fortuna, e in esercizio -- dove il validation non esiste -- non
serve a niente.

Uso:
    python pipeline/soglia.py
    python pipeline/soglia.py --run gru_tre_classi_DTW_cam1
"""

import argparse
import glob
import os
import sys

import numpy as np

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

import config
from src.valutazione import aggrega, metriche

dec = lambda v, n=3: f'{v:.{n}f}'.replace('.', ',')


# ============================================================
# LE REGOLE
# ============================================================
def _griglia(passo=0.005):
    return np.arange(passo, 1.0, passo)


def r_fbeta(p_val, y_val, beta=None):
    beta = config.BETA if beta is None else beta
    s = max(_griglia(), key=lambda t: metriche(y_val, p_val, t, beta)['fbeta'])
    return float(s)


def r_f1(p_val, y_val):
    return r_fbeta(p_val, y_val, beta=1.0)


def r_youden(p_val, y_val):
    """
    Massimizza recall + specificita' - 1. A differenza di F-beta non dipende
    dalla prevalenza, quindi una soglia scelta cosi' su un insieme al 12% di
    positivi resta sensata su uno all'1%. E' la proprieta' che serve qui,
    visto che la prevalenza in casa non e' quella del dataset.
    """
    def j(t):
        m = metriche(y_val, p_val, t)
        spec = m['tn'] / max(m['tn'] + m['fp'], 1)
        return m['recall'] + spec - 1.0
    return float(max(_griglia(), key=j))


def _percentile(p_val, y_val, fattore=1.0):
    """Taglia dove la quota di allarmi eguaglia `fattore` volte la prevalenza."""
    quota = float(np.mean(y_val)) * fattore
    quota = min(max(quota, 1e-4), 0.999)
    return float(np.quantile(p_val, 1.0 - quota))


def r_prevalenza(p_val, y_val):
    return _percentile(p_val, y_val, 1.0)


def r_prev15(p_val, y_val):
    return _percentile(p_val, y_val, 1.5)


def r_fissa05(p_val, y_val):
    return 0.5


REGOLE = {
    'fbeta': r_fbeta, 'f1': r_f1, 'youden': r_youden,
    'prevalenza': r_prevalenza, 'prev15': r_prev15, 'fissa05': r_fissa05,
}


# ============================================================
# VALUTAZIONE
# ============================================================
def carica_punteggi(percorso):
    z = np.load(percorso, allow_pickle=True)
    n = len(z['fold_test'])
    fold = []
    for i in range(n):
        fold.append({
            'test': str(z['fold_test'][i]), 'val': str(z['fold_val'][i]),
            'p_val': z[f'p_val_{i}'], 'y_val': z[f'y_val_{i}'],
            'p_test': z[f'p_test_{i}'], 'y_test': z[f'y_test_{i}'],
        })
    return fold


def applica(fold, regola):
    """Una regola su tutti i fold. Ritorna metriche e scarto di trasferimento."""
    ris, soglie, scarti = [], [], []
    for f in fold:
        s = REGOLE[regola](f['p_val'], f['y_val'])
        m = metriche(f['y_test'], f['p_test'], s)
        ris.append(m)
        soglie.append(s)
        # quota di finestre su cui si suona, sui due insiemi
        q_val = float(np.mean(f['p_val'] >= s))
        q_test = float(np.mean(f['p_test'] >= s))
        scarti.append(abs(q_test - q_val))
    return ris, np.array(soglie), np.array(scarti)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', default=None,
                    help='etichetta della run; senza, prende quella piu recente')
    ap.add_argument('--dettaglio', action='store_true',
                    help='tabella per fold della regola migliore')
    a = ap.parse_args()

    d = os.path.join(config.RISULTATI_DIR, 'addestramento')
    if a.run:
        p = os.path.join(d, f'punteggi_{a.run}.npz')
    else:
        f = sorted(glob.glob(os.path.join(d, 'punteggi_*.npz')),
                   key=os.path.getmtime)
        if not f:
            sys.exit(f'nessun punteggi_*.npz in {d}: eseguire prima '
                     f'pipeline/addestra.py')
        p = f[-1]
    if not os.path.exists(p):
        sys.exit(f'manca {p}')

    fold = carica_punteggi(p)
    prev = np.mean([np.mean(f['y_test']) for f in fold])

    print('=' * 78)
    print(f'REGOLE DI SOGLIA — {os.path.basename(p)}')
    print(f'{len(fold)} fold · prevalenza media nel test '
          f'{dec(100*prev, 1)}%')
    print('=' * 78)
    print(f"{'regola':<12}{'F2':>16}{'recall':>9}{'prec.':>8}"
          f"{'soglia':>16}{'scarto':>9}")
    print(f"{'':<12}{'media +- dev':>16}{'':>9}{'':>8}"
          f"{'media +- dev':>16}{'trasf.':>9}")
    print('-' * 78)

    tabella = {}
    for nome in REGOLE:
        ris, soglie, scarti = applica(fold, nome)
        ag = aggrega(ris)
        tabella[nome] = (ag, soglie, scarti, ris)
        print(f"{nome:<12}"
              f"{dec(ag['fbeta_media']):>8}{' +-' + dec(ag['fbeta_dev']):>8}"
              f"{dec(ag['recall_media']):>9}{dec(ag['precision_media']):>8}"
              f"{dec(soglie.mean(), 2):>8}{' +-' + dec(soglie.std(), 2):>8}"
              f"{dec(scarti.mean()):>9}")

    migliore = max(tabella, key=lambda k: tabella[k][0]['fbeta_media'])
    stabile = min(tabella, key=lambda k: tabella[k][2].mean())
    print('-' * 78)
    print(f'F2 piu alto:        {migliore}')
    print(f'trasferimento piu stabile: {stabile}')

    if a.dettaglio:
        ag, soglie, scarti, ris = tabella[migliore]
        print()
        print(f'--- {migliore}, per fold')
        print(f"{'fold':<14}{'soglia':>8}{'F2':>8}{'recall':>8}{'prec.':>8}"
              f"{'suona su':>10}{'positivi':>10}")
        for f, s, m in zip(fold, soglie, ris):
            q = (m['tp'] + m['fp']) / m['n']
            print(f"{f['test']:<14}{dec(s, 2):>8}{dec(m['fbeta']):>8}"
                  f"{dec(m['recall']):>8}{dec(m['precision']):>8}"
                  f"{dec(100*q, 1) + '%':>10}"
                  f"{dec(100*m['quota_positivi'], 1) + '%':>10}")


if __name__ == '__main__':
    main()
