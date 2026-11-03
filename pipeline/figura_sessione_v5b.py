# -*- coding: utf-8 -*-
"""
La sessione v5 del 9 settembre in due figure, con TUTTO ricavato dai dati.

Perche' esiste, e in che cosa differisce da `figura_sessione_v5.py`
-------------------------------------------------------------------
Quella figura portava scritti dentro gli istanti degli allarmi:

    ALLARMI = [743.5, 856.3]

Erano giusti --- il registro del programma li conferma --- ma erano
*affermati*, non *ricavati*. Una figura che afferma dove suona l'allarme non
puo' dimostrare che la regola perda la caduta n. 2: lo dice e basta.

Qui gli allarmi vengono calcolati applicando la regola ai punteggi, e la
verita' di riferimento viene letta da `cadute.csv` invece di stare nel codice.
Il risultato e' piu' forte: si VEDE che tre raffiche raggiungono le cinque
finestre e che soltanto due diventano allarmi, perche' la terza cade dentro la
sospensione della prima.

Lo script verifica inoltre che l'esito ricavato coincida con quello dichiarato
nel LEGGIMI, e lo stampa. Se un giorno non coincidessero, si saprebbe.

Le due figure
-------------
  fig_sessione_v5_andamento.png   l'intera sessione, nello stile di
                                  `fig_sessione`: punteggio, soglia, finestre
                                  sopra soglia, allarmi, e i 697 s iniziali in
                                  cui il sistema NON decide perche' attende la
                                  stima del pavimento.

  fig_sessione_v5_cadute.png      la lettura delle quattro cadute, con le
                                  raffiche e le finestre di sospensione
                                  disegnate: e' li' che si vede perche' una
                                  caduta vista benissimo non suona.

Uso:
    python pipeline/figura_sessione_v5b.py
"""

import argparse
import csv
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)

from pipeline.figure_tesi import INK, GRIGIO, BLU, ROSSO, SABBIA, CHIARO  # noqa: E402

SESSIONE = os.path.join(RADICE, 'deploy_board', 'sessioni', '20260909_v5')
REGISTRO = os.path.join(SESSIONE, 'sess_20260909_v5.csv')
VERITA = os.path.join(SESSIONE, 'cadute.csv')
USCITA = os.path.join(RADICE, 'tesi', 'figure')

# La regola installata, come descritta nel Capitolo 3.
LINGUA = 'it'


def T(it, en):
    """La stringa nella lingua corrente, come in `figure_tesi.py`."""
    return it if LINGUA == 'it' else en


SOGLIA = 0.50
PERSISTENZA = 5
SOSPENSIONE = 30.0
DURATA = 900.0


# ----------------------------------------------------------------- lettura
def registro():
    with open(REGISTRO, encoding='utf-8') as f:
        r = list(csv.DictReader(f))
    return ([float(x['t_s']) for x in r], [float(x['punteggio']) for x in r])


def verita():
    righe = []
    with open(VERITA, encoding='utf-8') as f:
        for r in csv.DictReader(x for x in f if not x.startswith('#')):
            r['inizio_s'] = float(r['inizio_s'])
            r['fine_s'] = float(r['fine_s'])
            righe.append(r)
    return righe


# ------------------------------------------------------------------ regola
def applica_regola(t, p):
    """Ritorna (finestre sopra soglia, raffiche che toccano K, allarmi).

    Una raffica e' l'istante in cui la corsa di finestre consecutive sopra
    soglia raggiunge PERSISTENZA. Diventa allarme solo se sono trascorsi piu'
    di SOSPENSIONE secondi dall'ultimo allarme emesso.
    """
    sopra = [(ti, pi) for ti, pi in zip(t, p) if pi >= SOGLIA]
    raffiche, allarmi = [], []
    corsa, ultimo = 0, -1e9
    for ti, pi in zip(t, p):
        if pi >= SOGLIA:
            corsa += 1
            if corsa == PERSISTENZA:
                raffiche.append(ti)
                if ti - ultimo > SOSPENSIONE:
                    allarmi.append(ti)
                    ultimo = ti
        else:
            corsa = 0
    return sopra, raffiche, allarmi


def leggi_cadute(t, p, cadute, raffiche, allarmi):
    """Per ciascuna banda dichiarata: picco, finestre sopra soglia, esito."""
    esiti = []
    for c in cadute:
        a, b = c['inizio_s'], c['fine_s']
        dentro = [(ti, pi) for ti, pi in zip(t, p) if a <= ti <= b]
        picco = max((pi for _, pi in dentro), default=0.0)
        n_sopra = sum(1 for _, pi in dentro if pi >= SOGLIA)
        r = any(a <= x <= b for x in raffiche)
        al = any(a <= x <= b for x in allarmi)
        if al:
            esito = 'allarme'
        elif r:
            esito = 'soppressa'
        elif n_sopra:
            esito = 'non vista dal modello'
        else:
            esito = 'nessun allarme'
        esiti.append(dict(c, picco=picco, n_sopra=n_sopra,
                          raffica=r, allarme=al, esito=esito))
    return esiti


# ------------------------------------------------------------------ figure
def _assi(ax, x0, x1):
    ax.set_xlim(x0, x1)
    ax.set_ylim(-.03, 1.06)
    ax.set_ylabel(T('punteggio', 'score'))
    ax.set_yticks([0, .25, .5, .75, 1.0])
    # la virgola decimale e' italiana: in inglese diventa il punto
    ax.set_yticklabels(['0'] + [T(v, v.replace(',', '.'))
                                for v in ('0,25', '0,50', '0,75')]
                       + ['1'])
    ax.grid(axis='y', color=CHIARO, lw=.7, alpha=.7, zorder=0)
    ax.set_axisbelow(True)
    for lato in ('top', 'right'):
        ax.spines[lato].set_visible(False)


def andamento(t, p, sopra, allarmi, fuori):
    """L'intera sessione, nello stile di fig_sessione."""
    fig, ax = plt.subplots(figsize=(9.6, 3.6))
    _assi(ax, 0, DURATA)

    # i secondi in cui il sistema non decide: il registro comincia dopo
    t0 = min(t)
    ax.axvspan(0, t0, color=CHIARO, alpha=.55, lw=0, zorder=1)
    ax.text(t0 / 2, .52,
            T('il sistema non decide\nattende la stima del pavimento'
              '\n%d s su %d',
              'the system does not decide\nwaiting for the floor'
              ' estimate\n%d s out of %d')
            % (round(t0), round(DURATA)),
            ha='center', va='center', fontsize=9, color=INK, linespacing=1.4)

    ax.plot(t, p, color=BLU, lw=1.1, zorder=3, solid_capstyle='round')
    ax.axhline(SOGLIA, color=GRIGIO, lw=1.0, ls='--', zorder=2)
    # l'etichetta sta nella fascia grigia, non a destra di t0: li' comincia
    # il punteggio e la scritta finirebbe sopra i punti sopra soglia
    ax.text(8, SOGLIA + .02, T('soglia 0,50', 'threshold 0.50'), ha='left',
            va='bottom',
            fontsize=8, color=GRIGIO)

    ax.plot([x for x, _ in sopra], [y for _, y in sopra], 'o', ms=3.2,
            color=ROSSO, zorder=4, alpha=.85, markeredgewidth=0)
    for ta in allarmi:
        pa = max(v for tt, v in zip(t, p) if abs(tt - ta) < .4)
        ax.plot([ta], [pa + .07], marker='v', ms=9, color=ROSSO, zorder=5,
                markeredgecolor='white', markeredgewidth=1.0)

    ax.set_xlabel(T('secondi dall' + chr(39) + 'avvio della sessione',
                    'seconds from the start of the session'))
    ax.set_xticks(range(0, 901, 100))
    ax.set_title(T('Una sessione di quindici minuti: %d finestre sopra '
                   'soglia, %d allarmi',
                   'A fifteen-minute session: %d windows above '
                   'threshold, %d alarms') % (len(sopra), len(allarmi)),
                 fontsize=10.5, pad=10)
    ax.legend(handles=[
        Line2D([], [], color=BLU, lw=1.4, label=T('punteggio per finestra', 'score per window')),
        Line2D([], [], marker='o', ls='', ms=4.5, color=ROSSO,
               label=T('finestra sopra soglia (%d)',
                       'window above threshold (%d)') % len(sopra)),
        Line2D([], [], marker='v', ls='', ms=7.5, color=ROSSO,
               markeredgecolor='white',
               label=T('allarme emesso (%d)',
                       'alarm raised (%d)') % len(allarmi)),
        Patch(facecolor=CHIARO, alpha=.55,
              label=T('nessuna decisione', 'no decision')),
    ], loc='upper left', fontsize=8, frameon=False, ncol=2)
    fig.tight_layout()
    return fig


def cadute_fig(t, p, esiti, falso, raffiche, allarmi):
    """Le quattro cadute, con raffiche e sospensioni ricavate."""
    fig, ax = plt.subplots(figsize=(9.6, 4.0))
    x0, x1 = 690.0, DURATA
    _assi(ax, x0, x1)

    # le sospensioni: 30 s dopo ciascun allarme, dentro i quali nulla suona
    for k, ta in enumerate(allarmi):
        ax.axvspan(ta, min(ta + SOSPENSIONE, x1), color=ROSSO, alpha=.07,
                   lw=0, zorder=1)
        ax.annotate('', xy=(ta, 1.005), xytext=(min(ta + SOSPENSIONE, x1), 1.005),
                    arrowprops=dict(arrowstyle='<->', color=ROSSO, lw=.9))
        if k == 0:
            ax.text(ta + SOSPENSIONE / 2, 1.018, T('sospensione 30 s', '30 s suspension'),
                    ha='center', va='bottom', fontsize=8, color=ROSSO)

    for e in esiti:
        a, b = e['inizio_s'], e['fine_s']
        ax.axvspan(a, b, color=SABBIA, alpha=.32, lw=0, zorder=2)
        ax.text((a + b) / 2, -.005, e['etichetta'], ha='center', va='top',
                fontsize=10, weight='bold', color=INK)

    a, b = falso['inizio_s'], falso['fine_s']
    ax.axvspan(a, b, color=CHIARO, alpha=.95, lw=0, zorder=2)
    ax.annotate(T('divano\nnon e' + chr(39) + ' una caduta',
                  'sofa\nnot a fall'),
                xy=((a + b) / 2, .62), xytext=(x1 - 2, .93),
                ha='right', va='top', fontsize=8, color=INK, linespacing=1.3,
                arrowprops=dict(arrowstyle='-', color=GRIGIO, lw=.8))

    ax.plot(t, p, color=BLU, lw=1.6, zorder=4, solid_capstyle='round')
    ax.axhline(SOGLIA, color=GRIGIO, lw=1.0, ls='--', zorder=3)
    ax.text(x0 + 2, SOGLIA + .02, T('soglia 0,50', 'threshold 0.50'), ha='left', va='bottom',
            fontsize=8, color=GRIGIO)

    # le raffiche: tutte, comprese quelle che NON diventano allarme
    for tr in raffiche:
        pr = max(v for tt, v in zip(t, p) if abs(tt - tr) < .4)
        suona = tr in allarmi
        ax.plot([tr], [pr], marker='v' if suona else 'o', ms=9 if suona else 7,
                color=ROSSO if suona else GRIGIO, zorder=6,
                markeredgecolor='white', markeredgewidth=1.0)

    for tr in raffiche:
        if tr not in allarmi:
            pr = max(v for tt, v in zip(t, p) if abs(tt - tr) < .4)
            ax.annotate(T('cinque finestre\nma dentro la sospensione',
                          'five windows,\nbut inside the suspension'),
                        xy=(tr, pr), xytext=(tr + 26, pr + .10),
                        ha='left', fontsize=8, color=GRIGIO, linespacing=1.3,
                        arrowprops=dict(arrowstyle='-', color=GRIGIO, lw=.8))

    ax.set_xlabel(T('secondi dall' + chr(39) + 'avvio della sessione',
                    'seconds from the start of the session'))
    ax.set_xticks(range(700, 901, 25))
    # «vista dal classificatore» = la corsa di finestre sopra soglia raggiunge
    # la persistenza. Contare una sola finestra sopra soglia direbbe che la
    # caduta 3 e' stata vista, e il LEGGIMI dichiara il contrario.
    n_viste = sum(1 for e in esiti if e['raffica'])
    ax.set_title(T('Quattro cadute: il classificatore ne vede %d, la '
                   'regola ne segnala %d',
                   'Four falls: the classifier sees %d, the rule '
                   'reports %d')
                 % (n_viste, sum(1 for e in esiti if e['allarme'])),
                 fontsize=10.5, pad=24)
    ax.legend(handles=[
        Line2D([], [], marker='v', ls='', ms=8, color=ROSSO,
               markeredgecolor='white',
               label=T('raffica che diventa allarme',
                       'burst that becomes an alarm')),
        Line2D([], [], marker='o', ls='', ms=6.5, color=GRIGIO,
               markeredgecolor='white',
               label=T('raffica soppressa', 'suppressed burst')),
        Patch(facecolor=SABBIA, alpha=.32,
              label=T('caduta dichiarata', 'declared fall')),
    ], loc='upper left', fontsize=8, frameon=False)
    fig.tight_layout()
    return fig


# -------------------------------------------------------------------- main
def main():
    global LINGUA
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', default=USCITA)
    ap.add_argument('--lingua', default='it', choices=('it', 'en'))
    a = ap.parse_args()
    LINGUA = a.lingua

    t, p = registro()
    righe = verita()
    cadute = [r for r in righe if r['tipo'] == 'caduta']
    falso = next(r for r in righe if r['tipo'] == 'falso_positivo')

    sopra, raffiche, allarmi = applica_regola(t, p)
    esiti = leggi_cadute(t, p, cadute, raffiche, allarmi)

    print('registro: %d finestre decise, da %.1f a %.1f s'
          % (len(t), min(t), max(t)))
    print('sopra soglia: %d   raffiche da %d finestre: %d   allarmi: %d'
          % (len(sopra), PERSISTENZA, len(raffiche), len(allarmi)))
    print('allarmi ricavati: %s' % [round(x, 1) for x in allarmi])
    print()
    print('%-4s %8s %8s %-24s %s' % ('#', 'picco', 'sopra', 'esito ricavato',
                                     'coincide col LEGGIMI?'))
    tutti_ok = True
    for e in esiti:
        ok = e['esito'] == e['esito_atteso']
        tutti_ok = tutti_ok and ok
        print('%-4s %8.3f %8d %-24s %s'
              % (e['etichetta'], e['picco'], e['n_sopra'], e['esito'],
                 'si' if ok else 'NO (atteso: %s)' % e['esito_atteso']))
    print()
    print('verifica contro la verita' + chr(39) + ' dichiarata: %s'
          % ('tutto coincide' if tutti_ok else 'DISCORDANZA'))

    os.makedirs(a.out, exist_ok=True)
    f1 = andamento(t, p, sopra, allarmi, DURATA - max(t))
    p1 = os.path.join(a.out, 'fig_sessione_v5_andamento%s.png'
                      % ('' if LINGUA == 'it' else '_en'))
    f1.savefig(p1, dpi=200, facecolor='white'); plt.close(f1)

    f2 = cadute_fig(t, p, esiti, falso, raffiche, allarmi)
    p2 = os.path.join(a.out, 'fig_sessione_v5_cadute%s.png'
                      % ('' if LINGUA == 'it' else '_en'))
    f2.savefig(p2, dpi=200, facecolor='white'); plt.close(f2)
    print('\nscritte:\n  %s\n  %s' % (p1, p2))

    scheda = os.path.join(a.out, 'fig_sessione_v5b%s.txt'
                          % ('' if LINGUA == 'it' else '_en'))
    with open(scheda, 'w', encoding='utf-8') as f:
        f.write('FIGURE — fig_sessione_v5_andamento.png e '
                'fig_sessione_v5_cadute.png\n'
                '=' * 62 + '\n\n'
                'PROVENIENZA\n-----------\n'
                'deploy_board/sessioni/20260909_v5/sess_20260909_v5.csv\n'
                '  (624 finestre decise, dai %.1f ai %.1f s)\n'
                'deploy_board/sessioni/20260909_v5/cadute.csv\n'
                '  (verita\' di riferimento, trascritta dal LEGGIMI)\n\n'
                'CHE COSA E\' RICAVATO, E CHE COSA E\' DICHIARATO\n'
                '---------------------------------------------\n'
                'Ricavato dai punteggi applicando la regola installata\n'
                '(soglia %.2f, %d finestre consecutive, sospensione %.0f s):\n'
                '  finestre sopra soglia   %d\n'
                '  raffiche che toccano %d  %d  -> %s\n'
                '  allarmi emessi          %d  -> %s\n\n'
                'Dichiarato, e NON usato per disegnare: le bande delle quattro\n'
                'cadute e del falso positivo, che vengono da cadute.csv.\n\n'
                'VERIFICA\n--------\n'
                'L\'esito ricavato per ciascuna caduta e\' stato confrontato\n'
                'con quello dichiarato nel LEGGIMI: %s.\n\n'
                'PERCHE\' DUE FIGURE\n------------------\n'
                'La prima mostra la sessione intera e i %d s iniziali in cui il\n'
                'sistema non decide: e\' il costo del riscaldamento della stima\n'
                'del pavimento. La seconda entra nei duecento secondi in cui\n'
                'accade tutto, e disegna le sospensioni: e\' li\' che si vede\n'
                'perche\' una caduta vista benissimo non suona.\n\n'
                'PRODOTTA DA\n-----------\npipeline/figura_sessione_v5b.py\n'
                % (min(t), max(t), SOGLIA, PERSISTENZA, SOSPENSIONE,
                   len(sopra), PERSISTENZA, len(raffiche),
                   [round(x, 1) for x in raffiche], len(allarmi),
                   [round(x, 1) for x in allarmi],
                   'tutto coincide' if tutti_ok else 'DISCORDANZA',
                   round(min(t))))
    print('  %s' % scheda)
    return 0


if __name__ == '__main__':
    sys.exit(main())
