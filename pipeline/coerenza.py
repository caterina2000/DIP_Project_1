# -*- coding: utf-8 -*-
"""Il progetto e' coerente con se stesso?

Perche' esiste. Ogni difetto serio trovato in questo lavoro ha avuto la stessa
forma: **la stessa cosa calcolata in due posti che dovevano essere d'accordo, e
non lo erano.** La finestratura fra addestramento e board (ISS-147), la durata
degli integrali (ISS-148), l'fps del dataset (ISS-149), l'allineamento delle
annotazioni esterne (ISS-150), le colonne installate (ISS-139), i capitoli in
tre copie (ISS-110). Nessuno di questi produceva un errore: producevano numeri
plausibili.

Un controllo che si esegue e' meglio di una rilettura che si ricorda. Questo
script confronta cio' che DEVE coincidere e stampa solo cio' che non coincide.

Uso:
    python pipeline/coerenza.py
    python pipeline/coerenza.py --verboso    anche cio' che va bene
"""

import argparse
import csv
import glob
import os
import re
import subprocess
import sys

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORICO = os.path.join(os.path.dirname(RADICE), 'DIP_PROJECT')

problemi = []


def segnala(area, testo, dettaglio=''):
    problemi.append((area, testo, dettaglio))
    print('  [!] %s' % testo)
    if dettaglio:
        for r in dettaglio.splitlines():
            print('      %s' % r)


def ok(testo, verboso):
    if verboso:
        print('      %s' % testo)


# ======================================================================
# 1. Le funzioni scritte due volte
# ======================================================================
def corpo(percorso, nome):
    """Il corpo di una funzione, senza commenti, righe vuote e spazi."""
    try:
        s = open(percorso, encoding='utf-8').read()
    except OSError:
        return None
    m = re.search(r'^def %s\(.*?(?=^\S)' % re.escape(nome), s,
                  re.S | re.M)
    if not m:
        return None
    righe = []
    for r in m.group(0).splitlines():
        r = re.sub(r'#.*', '', r).strip()
        if r and not r.startswith('"""') and not r.startswith("'''"):
            righe.append(re.sub(r'\s+', ' ', r))
    return '\n'.join(righe)


def controlla_duplicati(verboso):
    print('\n1. LE FUNZIONI SCRITTE DUE VOLTE')
    print('   Se divergono, la board calcola qualcosa di diverso dal PC.\n')
    coppie = [
        ('riassumi', ['src/modelli.py', 'deploy_board/rileva.py',
                      'deploy_board/mostra.py']),
        ('normalizza', ['deploy_board/rileva.py', 'deploy_board/mostra.py']),
    ]
    for nome, files in coppie:
        corpi = {}
        for f in files:
            c = corpo(os.path.join(RADICE, f), nome)
            if c is not None:
                corpi[f] = c
        if len(corpi) < 2:
            ok('%s: presente in un solo file' % nome, verboso)
            continue
        distinti = set(corpi.values())
        if len(distinti) == 1:
            ok('%s: %d copie, tutte identiche' % (nome, len(corpi)), verboso)
        else:
            gruppi = {}
            for f, c in corpi.items():
                gruppi.setdefault(c, []).append(f)
            segnala('duplicati',
                    '`%s` esiste in %d copie e NON coincidono'
                    % (nome, len(corpi)),
                    '\n'.join('gruppo %d: %s' % (i + 1, ', '.join(g))
                              for i, g in enumerate(gruppi.values())))


# ======================================================================
# 2. Le sessioni di campo
# ======================================================================
def controlla_sessioni(verboso):
    print('\n2. LE SESSIONI DI CAMPO')
    print('   Ogni sessione deve avere la traccia per fotogramma, altrimenti')
    print('   produce punteggi e nient\'altro: non si ricalcola nulla.\n')
    qui = sorted(glob.glob(os.path.join(RADICE, 'risultati', 'sessioni',
                                        '*', '*')))
    print('   %-38s %8s %9s' % ('sessione', 'colonne', 'traccia'))
    print('   ' + '-' * 58)
    senza, forme = [], {}
    for d in qui:
        if not os.path.isdir(d):
            continue
        nome = os.path.basename(d)
        tracce = (glob.glob(os.path.join(d, 'feature.csv'))
                  + glob.glob(os.path.join(d, '*_feature.csv')))
        if not tracce:
            senza.append(nome)
            print('   %-38s %8s %9s' % (nome[:37], '--', 'ASSENTE'))
            continue
        with open(tracce[0], encoding='utf-8') as f:
            n = len(next(csv.reader(f)))
        forme.setdefault(n, []).append(nome)
        print('   %-38s %8d %9s' % (nome[:37], n, 'si'))
    if senza:
        segnala('sessioni',
                '%d sessioni su %d non hanno la traccia per fotogramma'
                % (len(senza), len([d for d in qui if os.path.isdir(d)])),
                'senza traccia: ' + ', '.join(senza[:6])
                + (' ...' if len(senza) > 6 else '')
                + '\nda quelle sessioni si possono leggere i punteggi, ma non'
                  '\nsi puo\' rivalutare nessuna configurazione.')
    if len(forme) > 1:
        segnala('sessioni',
                'le tracce hanno FORME DIVERSE: %s colonne'
                % ' / '.join(str(k) for k in sorted(forme)),
                'una configurazione valutabile su una sessione puo\' non\n'
                'esserlo su un\'altra, e i confronti fra sessioni non sono\n'
                'automaticamente leciti.')


# ======================================================================
# 3. I risultati che dipendono da file fuori dal repository
# ======================================================================
def controlla_esterni(verboso):
    print('\n3. I DATI CHE STANNO FUORI DAL REPOSITORY')
    print('   Un numero della tesi che dipende da una cartella esterna non e\'')
    print('   riproducibile da chi clona questo repository.\n')
    trovati = []
    for f in sorted(glob.glob(os.path.join(RADICE, 'pipeline', '*.py'))):
        s = open(f, encoding='utf-8').read()
        for m in re.finditer(r"^(?!\s*#).*'DIP_PROJECT'.*$", s, re.M):
            riga = m.group(0).strip()
            if 'os.path.join' in riga or 'abspath' in riga:
                trovati.append((os.path.basename(f), riga[:78]))
    if trovati:
        segnala('esterni',
                '%d punti leggono da `../DIP_PROJECT`' % len(trovati),
                '\n'.join('%-26s %s' % (a, b) for a, b in trovati))
        if not os.path.isdir(STORICO):
            segnala('esterni',
                    'e `../DIP_PROJECT` NON esiste su questa macchina: '
                    'quei numeri non si rifanno')
    else:
        ok('nessuna dipendenza esterna', verboso)


# ======================================================================
# 4. Le costanti dichiarate due volte
# ======================================================================
def controlla_costanti(verboso):
    print('\n4. LE COSTANTI DICHIARATE PIU\' DI UNA VOLTA')
    print('   `config.py` e\' la sola sorgente di verita\'. Un valore ripetuto')
    print('   altrove prima o poi diverge --- e\' cosi\' che e\' nata ISS-112.\n')
    cfg = open(os.path.join(RADICE, 'config.py'), encoding='utf-8').read()
    nomi = dict(re.findall(r'^([A-Z_]{4,})\s*=\s*([0-9.]+)\s*$', cfg, re.M))
    sospetti = []
    for f in (sorted(glob.glob(os.path.join(RADICE, 'src', '*.py')))
              + sorted(glob.glob(os.path.join(RADICE, 'pipeline', '*.py')))):
        if os.path.basename(f) == 'config.py':
            continue
        s = open(f, encoding='utf-8').read()
        for nome, val in re.findall(r'^([A-Z_]{4,})\s*=\s*([0-9.]+)\s*$',
                                    s, re.M):
            if nome in nomi and nomi[nome] != val:
                sospetti.append((os.path.basename(f), nome, val, nomi[nome]))
    if sospetti:
        segnala('costanti', '%d costanti ridefinite con valore DIVERSO'
                % len(sospetti),
                '\n'.join('%-24s %-18s qui %s, in config %s' % s
                          for s in sospetti))
    else:
        ok('nessuna costante di config ridefinita altrove', verboso)


# ======================================================================
# 5. La board
# ======================================================================
def controlla_board(verboso):
    print('\n5. LA BOARD CONTRO IL PROGETTO')
    r = subprocess.run([sys.executable,
                        os.path.join(RADICE, 'pipeline', 'audit_board.py')],
                       capture_output=True, text=True)
    coda = [x for x in r.stdout.splitlines() if x.strip().startswith('-')]
    if r.returncode:
        segnala('board', 'la board NON esegue cio\' che il progetto dichiara',
                '\n'.join(x.strip() for x in coda)
                + '\ndettagli: python pipeline/audit_board.py')
    else:
        ok('board allineata al progetto', verboso)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--verboso', action='store_true')
    a = ap.parse_args()

    print('=' * 70)
    print('CONTROLLO DI COERENZA DEL PROGETTO')
    print('=' * 70)

    controlla_duplicati(a.verboso)
    controlla_sessioni(a.verboso)
    controlla_esterni(a.verboso)
    controlla_costanti(a.verboso)
    controlla_board(a.verboso)

    print('\n' + '=' * 70)
    if not problemi:
        print('Nessuna incoerenza.')
        return 0
    print('%d INCOERENZE, per area:' % len(problemi))
    per_area = {}
    for area, testo, _ in problemi:
        per_area.setdefault(area, []).append(testo)
    for area, elenco in per_area.items():
        print('  %s:' % area)
        for t in elenco:
            print('    - %s' % t)
    return 1


if __name__ == '__main__':
    sys.exit(main())
