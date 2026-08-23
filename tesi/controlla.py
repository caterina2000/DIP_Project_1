# -*- coding: utf-8 -*-
"""Controlli statici sui sorgenti della tesi.

Non sostituisce la compilazione --- su questa macchina non c'e' LaTeX, il PDF
si produce su Overleaf --- ma intercetta gli errori che la compilazione
segnalerebbe tardi o non segnalerebbe affatto:

  ambienti      un \\begin senza \\end passa inosservato finche' il documento
                non finisce fuori posto;
  etichette     due \\label uguali fanno puntare ogni riferimento al secondo,
                in silenzio;
  riferimenti   un \\ref senza \\label esce come «??» nel PDF, e ce n'erano
                venti prima del 22 agosto;
  figure        un ambiente `figure` senza immagine COMPILA: lascia uno spazio
                bianco con la didascalia sotto, ed e' cosi' che quattro figure
                mancanti sono rimaste per settimane;
  citazioni     una chiave citata e non definita esce come «[?]».

Uso:
    python tesi/controlla.py
"""

import collections
import glob
import io
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
os.chdir(QUI)

CAPITOLI = sorted(glob.glob('Cap*.tex'))
FILE = CAPITOLI + ['Introduzione.tex', 'Bibliografia.tex']
FILE = [f for f in FILE if os.path.exists(f)]

problemi = []


def leggi(f):
    return io.open(f, encoding='utf-8').read()


def riga_di(t, i):
    return t[:i].count('\n') + 1


# ---------------------------------------------------------------- ambienti
for f in FILE:
    t = leggi(f)
    pila = []
    for m in re.finditer(r'\\(begin|end)\{([^}]+)\}', t):
        n = riga_di(t, m.start())
        if m.group(1) == 'begin':
            pila.append((m.group(2), n))
        elif not pila:
            problemi.append('%s:%d  \\end{%s} senza begin' % (f, n, m.group(2)))
        elif pila[-1][0] != m.group(2):
            problemi.append('%s:%d  atteso end{%s} (aperto a riga %d), trovato '
                            'end{%s}' % (f, n, pila[-1][0], pila[-1][1],
                                         m.group(2)))
            pila.pop()
        else:
            pila.pop()
    for nome, n in pila:
        problemi.append('%s:%d  \\begin{%s} mai chiuso' % (f, n, nome))

# --------------------------------------------------------------- etichette
etichette = collections.defaultdict(list)
for f in FILE:
    t = leggi(f)
    for m in re.finditer(r'\\label\{([^}]+)\}', t):
        etichette[m.group(1)].append('%s:%d' % (f, riga_di(t, m.start())))
for k, dove in sorted(etichette.items()):
    if len(dove) > 1:
        problemi.append('label duplicata «%s»: %s' % (k, ', '.join(dove)))

# ------------------------------------------------------------- riferimenti
for f in FILE:
    t = leggi(f)
    for m in re.finditer(r'\\(ref|eqref)\{([^}]+)\}', t):
        if m.group(2) not in etichette:
            problemi.append('%s:%d  \\ref{%s} senza label --- uscira\' come ??'
                            % (f, riga_di(t, m.start()), m.group(2)))

# ------------------------------------------------------------------ figure
vuote = []
for f in CAPITOLI:
    t = leggi(f)
    for m in re.finditer(r'\\begin\{figure\}.*?\\end\{figure\}', t, re.S):
        b, n = m.group(0), riga_di(t, m.start())
        lab = re.search(r'\\label\{([^}]+)\}', b)
        if 'includegraphics' not in b:
            vuote.append('%s:%d  %s' % (f, n, lab.group(1) if lab else '?'))
            continue
        for g in re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', b):
            if not any(os.path.exists(g + e) for e in
                       ('', '.png', '.pdf', '.jpg', '.jpeg', '.eps')):
                problemi.append('%s:%d  figura mancante «%s»' % (f, n, g))

# --------------------------------------------------------------- citazioni
if os.path.exists('Bibliografia.tex'):
    # una riga commentata non produce una voce: una \bibitem preceduta
    # da % e' una voce RITIRATA, e contarla farebbe segnalare come «mai
    # citata» qualcosa che non viene nemmeno stampato
    bib = '\n'.join(r for r in leggi('Bibliografia.tex').split('\n')
                    if not r.lstrip().startswith('%'))
    chiavi = set(re.findall(r'\\bibitem\{([^}]+)\}', bib))
    usate = collections.defaultdict(set)
    for f in FILE:
        for m in re.findall(r'\\cite\{([^}]+)\}', leggi(f)):
            for k in m.split(','):
                usate[k.strip()].add(f)
    for k in sorted(set(usate) - chiavi):
        problemi.append('citazione «%s» non definita (%s) --- uscira\' come [?]'
                        % (k, ', '.join(sorted(usate[k]))))
    mai = sorted(chiavi - set(usate))

# ============================================================== resoconto
print('=' * 74)
print('CONTROLLO DEI SORGENTI  —  %s' % QUI)
print('=' * 74)

print('\n%-16s %7s %7s %5s %6s' % ('file', 'righe', 'parole', 'sez.', 'fig.'))
print('-' * 46)
tot = 0
for f in CAPITOLI + ['Introduzione.tex']:
    if not os.path.exists(f):
        continue
    t = leggi(f)
    par = len(re.findall(r'\w+', re.sub(r'%.*', '', t)))
    tot += par
    n_fig = len(re.findall(r'\\includegraphics', t))
    n_vuote = len(re.findall(r'\\begin\{figure\}', t)) - n_fig
    print('%-16s %7d %7d %5d %6s' % (
        f, len(t.split('\n')), par, len(re.findall(r'\n\\section\{', t)),
        '%d+%dv' % (n_fig, n_vuote) if n_vuote else str(n_fig)))
print('-' * 46)
print('%-16s %7s %7d' % ('TOTALE', '', tot))

if vuote:
    print('\nFIGURE SENZA IMMAGINE (compilano, lasciano uno spazio bianco):')
    for v in vuote:
        print('   ' + v)

if 'mai' in dir() and mai:
    print('\nvoci di bibliografia mai citate: ' + ', '.join(mai))

print()
if problemi:
    print('PROBLEMI: %d' % len(problemi))
    for p in problemi:
        print('   ' + p)
    sys.exit(1)
print('Nessun problema. Restano %d figure da produrre.' % len(vuote))
