# -*- coding: utf-8 -*-
"""I valori installati sulla board coincidono con quelli del codice?

Perche' esiste. `deploy_board/` e' una copia: metadata.json, modello.pkl,
scaler.pkl e geometry.py sono stati esportati un giorno preciso e da allora
vivono per conto loro. Il progetto e' andato avanti. Nessuno controllava.

Questo script confronta, uno per uno, i valori che la board dichiara con
quelli che il progetto dichiara oggi, e stampa solo cio' che NON coincide.

Uso:
    python pipeline/audit_board.py
"""

import hashlib
import json
import os
import sys

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RADICE not in sys.path:
    sys.path.insert(0, RADICE)

import config  # noqa: E402

BOARD = os.path.join(RADICE, 'deploy_board')


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(65536), b''):
            h.update(b)
    return h.hexdigest()


def main():
    meta = json.load(open(os.path.join(BOARD, 'metadata.json'),
                          encoding='utf-8'))
    # Le colonne attese sono quelle dell'insieme che il pacchetto DICHIARA di
    # usare, non quelle del DTW per definizione: da quando la board monta
    # DTWH, confrontarla con le dodici del DTW segnalerebbe una differenza a
    # ogni esecuzione. Un controllo che grida al lupo si smette di leggerlo.
    from src.dati import colonne_di  # noqa: E402
    insieme = meta.get('feature_set', 'DTW')
    try:
        scelte = list(colonne_di(insieme))
    except Exception as e:
        print('non so risolvere l insieme %r: %s' % (insieme, e))
        scelte = None

    print('=' * 72)
    print('CONFRONTO FRA LA BOARD E IL PROGETTO')
    print('=' * 72)
    print('board esportata il %s\n' % meta.get('creato', '?'))

    diff = []

    def confronta(nome, board, qui, nota=''):
        ok = (board == qui)
        if not ok:
            diff.append((nome, board, qui, nota))
        print('  %-28s %-22s %-22s %s'
              % (nome, str(board), str(qui), 'ok' if ok else '<<< DIVERSO'))

    print('  %-28s %-22s %-22s' % ('parametro', 'sulla board', 'nel progetto'))
    print('  ' + '-' * 70)
    confronta('lunghezza_finestra', meta['lunghezza_finestra'],
              config.LUNGHEZZA_FINESTRA)
    confronta('passo_finestra', meta['passo_finestra'], config.PASSO_FINESTRA)
    confronta('k_integrali', meta['k_integrali'], config.K_INTEGRALI)
    # La durata e' cio' che deve coincidere davvero: il conteggio dipende
    # dalla cadenza, che ai due lati non e' la stessa (ISS-148).
    confronta('durata_integrali_s',
              meta.get('durata_integrali_s'),
              round(config.DURATA_INTEGRALI_S, 6))
    confronta('soglia', meta['soglia'], 0.5)
    confronta('n_colonne', meta['n_colonne'],
              len(scelte) if scelte else meta['n_colonne'])
    confronta('fps_assunti', meta['fps_assunti'], config.FPS_ESERCIZIO)

    print()
    print('  LE COLONNE  (insieme dichiarato: %s)' % insieme)
    b = list(meta['colonne'])
    if scelte is None:
        print('    (scelte.txt assente: impossibile confrontare)')
    else:
        sb, ss = set(b), set(scelte)
        if sb == ss:
            print('    stesse %d grandezze  ok' % len(ss))
        else:
            print('    installate ma NON scelte oggi: %s'
                  % (', '.join(sorted(sb - ss)) or '---'))
            print('    scelte oggi ma NON installate: %s'
                  % (', '.join(sorted(ss - sb)) or '---'))
            diff.append(('colonne', sorted(sb - ss), sorted(ss - sb), ''))

    print()
    print('  LO SCHEMA DELLE GRANDEZZE')
    from src.geometry import NOMI  # noqa: E402
    schema = meta.get('schema_feature')
    if schema is None:
        print('    il pacchetto non dichiara lo schema: esportarlo di nuovo')
        diff.append(('schema_feature', 'assente', '%d grandezze' % len(NOMI), ''))
    elif list(schema) == list(NOMI):
        print('    %d grandezze, nomi e ordine coincidono  ok' % len(NOMI))
    else:
        so, sn = set(schema), set(NOMI)
        print('    dichiarate dalla board e non calcolate oggi: %s'
              % (', '.join(sorted(so - sn)) or '---'))
        print('    calcolate oggi e non dichiarate dalla board: %s'
              % (', '.join(sorted(sn - so)) or '---'))
        if so == sn:
            print('    stessi nomi, ORDINE diverso')
        diff.append(('schema_feature', sorted(so - sn), sorted(sn - so), ''))

    print()
    print('  IL MOTORE GEOMETRICO')
    a = sha(os.path.join(BOARD, 'geometry.py'))
    c = sha(os.path.join(RADICE, 'src', 'geometry.py'))
    print('    deploy_board/geometry.py  %s' % a[:16])
    print('    src/geometry.py           %s' % c[:16])
    if a == c:
        print('    coincidono  ok')
    else:
        print('    <<< DIVERSI: la board non calcola le stesse grandezze')
        diff.append(('geometry.py', a[:16], c[:16], ''))
    atteso = meta.get('sha256_geometry')
    if atteso:
        print('    impronta dichiarata nel metadato: %s  %s'
              % (atteso[:16], 'ok' if atteso == a else '<<< NON CORRISPONDE'))

    print()
    print('=' * 72)
    if not diff:
        print('Nessuna differenza: la board esegue cio\' che il progetto dichiara.')
    else:
        print('%d DIFFERENZE. Ognuna significa che un numero della tesi'
              % len(diff))
        print('descrive una configurazione che sul dispositivo non c\'e\'.')
        for n, bb, qq, _ in diff:
            print('  - %s: board %s, progetto %s' % (n, bb, qq))
    return 1 if diff else 0


if __name__ == '__main__':
    sys.exit(main())
