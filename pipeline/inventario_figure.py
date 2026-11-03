# -*- coding: utf-8 -*-
"""Che figure e tabelle ci sono, capitolo per capitolo."""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

INCL = re.compile(r'\\includegraphics[^{]*\{([^}]+)\}')
LABF = re.compile(r'\\label\{fig:([^}]+)\}')
LABT = re.compile(r'\\label\{tab:([^}]+)\}')
CAPT = re.compile(r'\\caption\{(.{0,80})', re.S)

for c in ('Cap3', 'Cap4', 'Cap5', 'Conclusioni'):
    s = io.open('tesi/%s.tex' % c, encoding='utf-8').read()
    print('=' * 78)
    print(c)
    print('=' * 78)
    print('  ambienti figure : %d   tabelle: %d   tabular: %d'
          % (s.count(r'\begin{figure}'), s.count(r'\begin{table}'),
             s.count(r'\begin{tabular}')))
    print('  immagini incluse:', INCL.findall(s) or '(nessuna)')
    print('  label figura    :', LABF.findall(s) or '(nessuna)')
    print('  label tabella   :', LABT.findall(s) or '(nessuna)')
    didascalie = [re.sub(r'\s+', ' ', x).strip() for x in CAPT.findall(s)]
    for d in didascalie:
        print('    cap:', d[:95])

print()
print('figure disponibili in tesi/figure:')
for f in sorted(os.listdir('tesi/figure')):
    print('   ', f)
