# -*- coding: utf-8 -*-
"""
Audit dei numeri dei capitoli sperimentali contro i file che li producono.

Non decide se un numero e' giusto: elenca quelli che compaiono nel testo e non
corrispondono a nessun valore presente nei file di risultato, che sono i
candidati da controllare a mano. E' il controllo che a ISS-123 e' mancato.
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ------------------------------------------------------------------ 1. i file
valori = {}          # valore arrotondato -> insiemi di provenienze


def registra(v, dove):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return
    for n in (1, 2, 3, 4):
        valori.setdefault(round(f, n), set()).add(dove)
    # anche le percentuali e i conteggi derivati
    for n in (1, 2):
        valori.setdefault(round(f * 100, n), set()).add(dove + ' [%]')


def scava(d, dove):
    if isinstance(d, dict):
        for k, v in d.items():
            scava(v, dove)
    elif isinstance(d, list):
        for v in d:
            scava(v, dove)
    elif isinstance(d, (int, float)) and not isinstance(d, bool):
        registra(d, dove)


# Le SERIE per campione non sono risultati: sono il dato grezzo da cui un
# risultato si calcola. Ammetterle nella riserva la riempie di decimali
# arbitrari e rende l'audit inutile, perche' con abbastanza numeri qualunque
# numero trova un riscontro per caso.
#
# Misurato il 2026-09-06, ed e' il motivo per cui questa riga esiste:
# aggiungendo `escursione_viste_10sog_serie.json` --- circa 24.000 valori, che
# `registra` moltiplica per sei arrotondamenti --- i numeri del Capitolo 5
# senza riscontro sono passati da 9 a 1 **senza che una riga del capitolo
# fosse toccata**. Non erano stati giustificati: erano stati sepolti.
def e_serie(nome):
    return nome.endswith('_serie.json') or nome.endswith('_serie.csv')


# Stessa ragione, seconda porta. Le registrazioni di sessione contengono un
# CSV per FINESTRA (`punteggi.csv`, `<sessione>.csv`) e uno per FOTOGRAMMA
# (`<sessione>_feature.csv`, 17,8 MB per le 4,6 ore del 6 settembre): sono il
# dato grezzo della sessione, non i suoi risultati. I risultati stanno nel
# `riepilogo.json`, che resta dentro.
#
# Misurato il 2026-09-07 (ISS-141): con i CSV delle sessioni nella riserva i
# numeri senza riscontro erano 0 in TUTTI i capitoli; togliendoli tornano a
# 11 nel Capitolo 4, 15 nel Capitolo 5 e 4 nelle Conclusioni. Trenta numeri
# non erano giustificati: erano sepolti sotto i decimali di una registrazione
# di quattro ore e mezzo.
def e_grezzo_di_sessione(percorso, nome):
    return (os.sep + 'sessioni' + os.sep) in percorso and nome.endswith('.csv')


for radice, _, files in os.walk('risultati'):
    for n in files:
        p = os.path.join(radice, n)
        if e_serie(n) or e_grezzo_di_sessione(p, n):
            continue
        if n.endswith('.json'):
            try:
                scava(json.load(io.open(p, encoding='utf-8')), os.path.relpath(p))
            except Exception:
                pass
        elif n.endswith('.csv'):
            # anche i CSV sono artefatti: exp013_camera_viewpoint.csv produce
            # meta' dei numeri della sezione sul punto di vista, e l'audit li
            # dichiarava orfani solo perche' non leggeva i CSV
            try:
                with io.open(p, encoding='utf-8') as fh:
                    for riga in fh:
                        for campo in riga.replace(';', ',').split(','):
                            registra(campo.strip(), os.path.relpath(p))
            except Exception:
                pass

print(f'valori distinti raccolti dai file di risultato: {len(valori)}')

# ------------------------------------------------------- 2. i numeri del testo
NUM = re.compile(r'(?<![\d,.])(\d{1,3}(?:\.\d{3})*|\d+)(?:\{,\}|,)(\d+)(?![\d])')

for capitolo in ('Cap3', 'Cap4', 'Cap5', 'Conclusioni'):
    s = io.open(f'tesi/{capitolo}.tex', encoding='utf-8').read()
    # via i commenti: contengono la storia delle correzioni, non affermazioni
    s = '\n'.join(l for l in s.split('\n') if not l.lstrip().startswith('%'))

    trovati, orfani = 0, []
    for m in NUM.finditer(s):
        intero = m.group(1).replace('.', '')
        f = float(f'{intero}.{m.group(2)}')
        trovati += 1
        if len(m.group(2)) > 3:
            continue
        d = min(len(m.group(2)), 4)
        # il segno non e' catturato dalla regola: si confronta il modulo,
        # altrimenti ogni valore negativo dei file risulta orfano
        chiavi = [round(f, d), round(-f, d)]
        if any(k in valori for k in chiavi):
            continue
        # contesto: quaranta caratteri prima e dopo
        a, b = max(0, m.start() - 55), min(len(s), m.end() + 45)
        ctx = re.sub(r'\s+', ' ', s[a:b])
        orfani.append((m.group(0), ctx))

    print()
    print('=' * 78)
    print(f'{capitolo}: {trovati} numeri decimali, {len(orfani)} senza riscontro nei file')
    print('=' * 78)
    visti = set()
    for v, ctx in orfani:
        if v in visti:
            continue
        visti.add(v)
        print(f'  {v:>10}   ...{ctx}...')
