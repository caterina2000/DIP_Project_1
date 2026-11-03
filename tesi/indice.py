"""
L'indice vero, ricavato dai sorgenti invece che dal PDF.

Perche' esiste
--------------
L'indice con i numeri di pagina lo produce LaTeX da `\\tableofcontents`, e su
questa macchina non c'e' un compilatore: quello che si ha in mano e' sempre la
fotografia dell'ultima compilazione su Overleaf. Fra una compilazione e l'altra
la struttura cambia, e non c'e' modo di accorgersene guardando il PDF vecchio.

Questo script legge i sorgenti e stampa la struttura **di adesso**, nell'ordine
in cui `tesi.tex` include i file.

I titoli che nell'indice NON compaiono
--------------------------------------
Sono due famiglie, e la ragione e' diversa.

`\\paragraph` --- 160 in questa tesi --- e' un titolo di quarto livello: ha un
nome ma **non una voce nell'indice**, perche' la classe `book` non porta in
indice oltre il terzo livello (`tocdepth` = 2). E' una scelta deliberata del
lavoro, scritta nelle sue regole di scrittura: *un titolo ogni ~400 parole;
sotto le 250 un blocco non giustifica una sottosezione, e si usa `\\paragraph`,
che ha un nome ma non una voce nell'indice*. Serve a dare un appiglio al
lettore che scorre la pagina senza gonfiare un indice che diventerebbe
illeggibile: con 160 voci in piu' l'indice occuperebbe piu' pagine dei capitoli
di sfondo.

Le forme **con l'asterisco** --- `\\section*`, `\\subsection*`,
`\\subsubsection*` --- non compaiono per un motivo tecnico diverso: la variante
stellata non incrementa il contatore e **non scrive nel file `.toc`**. Un
titolo stellato e' quindi invisibile all'indice anche se sarebbe abbastanza
importante da starci, a meno di aggiungerlo a mano con `\\addcontentsline`, che
e' esattamente cio' che `Introduzione.tex` fa per comparire in indice pur non
essendo numerata.

La differenza pratica: un `\\paragraph` e' fuori dall'indice **per scelta di
struttura**, un titolo stellato lo e' **per costruzione**. Il secondo va usato
con cautela, perche' toglie dall'indice qualcosa che ha il rango per starci.

Uso:
    python tesi/indice.py            struttura, con il conteggio dei paragrafi
    python tesi/indice.py --titoli   e anche i titoli di quarto livello
    python tesi/indice.py --soli-fuori   solo cio' che in indice non compare
"""

import argparse
import io
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

B = chr(92)
# `chapter*` e simili vanno riconosciuti PRIMA della forma senza asterisco,
# altrimenti l'asterisco resta fuori dalla cattura e il titolo sembra numerato.
COMANDO = re.compile(B + B + r'(chapter|section|subsection|subsubsection|paragraph)'
                     r'(\*?)\{')
LIVELLO = {'chapter': 0, 'section': 1, 'subsection': 2,
           'subsubsection': 3, 'paragraph': 4}
# La classe `book` porta in indice fino a `subsection` (tocdepth = 2): oltre,
# il titolo esiste nel testo e non nell'indice.


def titolo(s, i):
    """Il contenuto di una graffa bilanciata che comincia a `i`."""
    prof, j = 0, i
    while j < len(s):
        if s[j] == '{':
            prof += 1
        elif s[j] == '}':
            prof -= 1
            if prof == 0:
                return s[i + 1:j], j + 1
        j += 1
    return s[i + 1:], len(s)


def senza_commenti(s):
    """Via le righe di commento: contengono la storia, non il testo."""
    return '\n'.join(l for l in s.split('\n') if not l.lstrip().startswith('%'))


def struttura(percorso):
    s = senza_commenti(io.open(percorso, encoding='utf-8').read())
    fuori = []
    for m in COMANDO.finditer(s):
        t, ast = m.group(1), m.group(2) == '*'
        testo, _ = titolo(s, m.end() - 1)
        fuori.append((LIVELLO[t], t, ast, ' '.join(testo.split())))
    return fuori


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--titoli', action='store_true',
                    help='elenca anche i titoli di quarto livello')
    ap.add_argument('--soli-fuori', action='store_true', dest='soli_fuori',
                    help='solo i titoli che in indice non compaiono')
    a = ap.parse_args()

    ind_par = ' ' * 8
    ordine = ['Introduzione.tex', 'Cap1.tex', 'Cap2.tex', 'Cap3.tex',
              'Cap4.tex', 'Cap5.tex', 'Conclusioni.tex']
    cap = 0
    n_par, n_stellati = 0, 0

    print('=' * 78)
    print('STRUTTURA DELLA TESI, DAI SORGENTI')
    print('=' * 78)

    for f in ordine:
        p = os.path.join(QUI, f)
        if not os.path.exists(p):
            print(f'  manca: {f}')
            continue
        sez = sub = 0
        pendenti = []            # i paragrafi della sezione in corso
        for liv, tipo, ast, testo in struttura(p):
            if liv <= 2 and pendenti and not a.soli_fuori:
                if a.titoli:
                    for t in pendenti:
                        print(f'        · {t}')
                else:
                    print(ind_par + '({} titol{} di quarto livello, fuori indice)'.format(
                          len(pendenti), 'o' if len(pendenti) == 1 else 'i'))
                pendenti = []

            if tipo == 'chapter':
                if not ast:
                    cap += 1
                sez = 0
                marca = '' if not ast else '   [non numerato]'
                if not a.soli_fuori:
                    print(f'\n{"" if ast else cap}  {testo}{marca}')
            elif tipo == 'section':
                sez += 1
                sub = 0
                if ast:
                    n_stellati += 1
                if not a.soli_fuori:
                    print(f'  {cap}.{sez}  {testo}'
                          + ('   [stellata: fuori indice]' if ast else ''))
                elif ast:
                    print(f'  {cap}.{sez}  {testo}   [section* — fuori indice]')
            elif tipo == 'subsection':
                sub += 1
                if ast:
                    n_stellati += 1
                if not a.soli_fuori:
                    print(f'    {cap}.{sez}.{sub}  {testo}'
                          + ('   [stellata: fuori indice]' if ast else ''))
                elif ast:
                    print(f'    {cap}.{sez}.{sub}  {testo}'
                          f'   [subsection* — fuori indice]')
            else:
                # subsubsection e paragraph: entrambi oltre `tocdepth`
                if ast:
                    n_stellati += 1
                n_par += 1
                etichetta = testo + (f'   [{tipo}*]' if ast else '')
                if a.soli_fuori:
                    print(f'      {cap}.{sez}   {etichetta}')
                else:
                    pendenti.append(etichetta)

        if pendenti and not a.soli_fuori:
            if a.titoli:
                for t in pendenti:
                    print(f'        · {t}')
            else:
                print(ind_par + '({} titol{} di quarto livello, fuori indice)'.format(
                      len(pendenti), 'o' if len(pendenti) == 1 else 'i'))

    print()
    print('-' * 78)
    print(f'titoli fuori indice: {n_par}'
          f'  (di cui stellati: {n_stellati})')
    print('Un `paragraph` sta fuori per scelta di struttura --- un titolo ogni')
    print('~400 parole, sotto le 250 si usa `paragraph` --- mentre una forma')
    print('stellata ci sta fuori per costruzione: non scrive nel file .toc.')
    print('Con questi in indice, l\'indice sarebbe piu\' lungo dei capitoli')
    print('di sfondo.')


if __name__ == '__main__':
    main()
