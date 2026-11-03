# -*- coding: utf-8 -*-
"""
Confronto appaiato fra architetture, e numerosita' necessaria per dichiararlo.

Perche' appaiato
----------------
Ogni architettura e' valutata sugli STESSI dieci soggetti, quindi le dieci
differenze per fold sono osservazioni appaiate. Confrontare le medie con un
test a campioni indipendenti butterebbe via proprio l'informazione che rende
il confronto sensibile: la variabilita' fra persone e' comune ai due modelli e
si cancella nella differenza.

Che cosa stampa
---------------
Per ogni architettura, contro la GRU di riferimento: la differenza media di
F2, la deviazione delle differenze, il t appaiato, e **quanti soggetti
servirebbero** per rendere significativa la differenza osservata con potenza
dell'80% e alfa del 5%.

L'ultima colonna e' quella che conta. Una differenza non significativa non dice
«i due modelli sono uguali»: dice che con questo numero di soggetti non si
distinguono. Il numero di soggetti necessari trasforma quel silenzio in una
misura.

Uso:
    python pipeline/confronto_appaiato.py
    python pipeline/confronto_appaiato.py --riferimento lstm
"""

import argparse
import glob
import json
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
from src.provenienza import scrivi_json

# t critico bilaterale al 5% e z per potenza 80%: servono a stimare la
# numerosita' senza dipendere da scipy, che non e' fra le dipendenze.
T_CRIT_05 = {2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571, 7: 2.447,
             8: 2.365, 9: 2.306, 10: 2.262, 15: 2.145, 20: 2.093, 30: 2.045,
             50: 2.010, 100: 1.984, 200: 1.972, 1000: 1.962}


def t_critico(n):
    """t bilaterale al 5% con n-1 gradi di liberta', per interpolazione."""
    g = n - 1
    chiavi = sorted(T_CRIT_05)
    if g <= chiavi[0]:
        return T_CRIT_05[chiavi[0]]
    for a, b in zip(chiavi, chiavi[1:]):
        if a <= g <= b:
            q = (g - a) / (b - a)
            return T_CRIT_05[a] + q * (T_CRIT_05[b] - T_CRIT_05[a])
    return 1.96


def soggetti_necessari(effetto, dev, potenza_z=0.84):
    """
    Numerosita' per un test appaiato: n >= ((t_crit + z_potenza) * dev / d)^2.

    Si itera perche' t_crit dipende da n. Il valore restituito e' il primo n
    che soddisfa la disuguaglianza.
    """
    if not np.isfinite(effetto) or abs(effetto) < 1e-12 or dev <= 0:
        return None
    n = 3
    for _ in range(2000):
        serve = ((t_critico(n) + potenza_z) * dev / abs(effetto)) ** 2
        if n >= serve:
            return n
        n += 1
    return None


def carica_run(cartella):
    """{architettura: [F2 per fold]} dalle run con la stessa configurazione."""
    fuori = {}
    for p in sorted(glob.glob(os.path.join(cartella, 'run_*.json'))):
        d = json.load(open(p, encoding='utf-8'))
        chiave = (d['modo_etichettatura'], d['n_feature'], d['camera'],
                  d['lunghezza_finestra'])
        fuori.setdefault(chiave, {})[d['architettura']] = {
            'file': os.path.basename(p),
            'f2': [f['fbeta'] for f in d['fold']],
            'fold': [f['test'] for f in d['fold']],
            'par': d.get('n_parametri'),
            'durata': d.get('durata_s'),
            'agg': d['aggregato'],
        }
    return fuori


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--riferimento', default='gru')
    ap.add_argument('--modo', default='tre_classi')
    ap.add_argument('--feature', type=int, default=12)
    ap.add_argument('--camera', type=int, default=1)
    ap.add_argument('--lunghezza', type=int, default=config.LUNGHEZZA_FINESTRA)
    a = ap.parse_args()

    cartella = os.path.join(config.RISULTATI_DIR, 'addestramento')
    gruppi = carica_run(cartella)
    chiave = (a.modo, a.feature, a.camera, a.lunghezza)
    if chiave not in gruppi:
        sys.exit(f'nessuna run con configurazione {chiave}. '
                 f'Disponibili: {sorted(gruppi)}')
    run = gruppi[chiave]
    if a.riferimento not in run:
        sys.exit(f'manca la run di riferimento {a.riferimento!r}')

    rif = run[a.riferimento]
    print('=' * 86)
    print(f'CONFRONTO APPAIATO CONTRO {a.riferimento.upper()} — modo {a.modo}, '
          f'{a.feature} grandezze, camera {a.camera}, finestra {a.lunghezza}')
    print('=' * 86)
    print(f"{'architettura':<14}{'F2':>18}{'diff':>9}{'dev diff':>10}"
          f"{'t':>8}{'vince':>8}{'soggetti':>10}{'parametri':>11}")
    print('-' * 86)

    fuori = []
    for arch in sorted(run, key=lambda k: -run[k]['agg']['fbeta_media']):
        d = run[arch]
        if d['fold'] != rif['fold']:
            print(f'  {arch}: fold in ordine diverso, saltata')
            continue
        v = np.asarray(d['f2']) - np.asarray(rif['f2'])
        n = len(v)
        dev = float(v.std(ddof=1))
        eff = float(v.mean())
        t = eff / (dev / np.sqrt(n)) if dev > 0 else float('nan')
        vince = int((v > 0).sum())
        serve = soggetti_necessari(eff, dev) if arch != a.riferimento else None
        ag = d['agg']
        print(f"{arch:<14}{ag['fbeta_media']:8.3f} ± {ag['fbeta_dev']:5.3f}"
              f"{eff:>9.3f}{dev:>10.3f}{t:>8.2f}{vince:>6}/{n}"
              f"{(serve if serve else '—'):>10}{d['par']:>11,}")
        fuori.append({'architettura': arch, 'file': d['file'],
                      'f2_media': ag['fbeta_media'], 'f2_dev': ag['fbeta_dev'],
                      'recall': ag['recall_media'], 'precision': ag['precision_media'],
                      'fn_tot': ag['fn_tot'], 'fp_tot': ag['fp_tot'],
                      'differenza': eff, 'dev_differenza': dev, 't': t,
                      'vince_su': vince, 'n_fold': n,
                      'soggetti_necessari': serve, 'n_parametri': d['par'],
                      'durata_s': d['durata']})

    print('-' * 86)
    print(f'|t| critico con {len(rif["f2"])} fold: {t_critico(len(rif["f2"])):.3f}. '
          f'Sopra quel valore la differenza si dichiara, sotto no.')

    p = os.path.join(config.RISULTATI_DIR, 'laboratorio',
                     f'confronto_appaiato_{a.riferimento}.json')
    os.makedirs(os.path.dirname(p), exist_ok=True)
    scrivi_json(p, {'riferimento': a.riferimento, 'modo': a.modo,
                    'n_feature': a.feature, 'camera': a.camera,
                    'lunghezza_finestra': a.lunghezza,
                    'soglia': 'fissa 0,50 dichiarata a priori',
                    'confronti': fuori}, indent=2)
    print(f'salvato: {os.path.relpath(p, RADICE)}')


if __name__ == '__main__':
    main()
