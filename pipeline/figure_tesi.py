# -*- coding: utf-8 -*-
"""Produce le figure della tesi dai risultati di QUESTO progetto.

Perche' esiste
--------------
Le figure ereditate dal progetto storico erano di due serie, entrambe
inutilizzabili: quelle del 7 agosto vengono dall'impianto a cinque soggetti,
e quelle prodotte per la relazione al relatore leggono i JSON di quel
progetto. Nessuna delle due e' costruita sui risultati correnti.

Questo script legge SOLO `risultati/` --- dieci soggetti, scaler stimato sui
fotogrammi del fold, soglia dichiarata a priori --- e scrive i PNG in
`tesi/figure/`, che dal 23 agosto sta in questo stesso progetto. Ogni figura
stampa in coda il file da cui ha preso i numeri, cosi' che una figura non
possa sopravvivere alla run che l'ha prodotta.

Uso
---
    python pipeline/figure_tesi.py
    python pipeline/figure_tesi.py --dove <cartella>     (per provare altrove)
"""

import argparse
import io
import json
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RIS = os.path.join(QUI, 'risultati')
DEFAULT = os.path.join(QUI, 'tesi', 'figure')

# --- aspetto -------------------------------------------------------------
# Tinte scelte per restare distinguibili anche stampate in scala di grigi:
# variano in luminosita', non solo in tinta.
INK = '#1A1F23'
GRIGIO = '#8A949B'
BLU = '#2B5D7D'
TEAL = '#2E8B8B'
ROSSO = '#9C3B45'
SABBIA = '#C4A55C'
CHIARO = '#C9D4DA'

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans'],
    'font.size': 9.5,
    'axes.edgecolor': GRIGIO,
    'axes.labelcolor': INK,
    'axes.titlesize': 11,
    'axes.titleweight': 'bold',
    'text.color': INK,
    'xtick.color': INK,
    'ytick.color': INK,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.facecolor': 'white',
    'savefig.facecolor': 'white',
    'savefig.dpi': 220,
})


def dec(v, n=3):
    """Numero con la virgola decimale, come da uso italiano."""
    return ('{:.' + str(n) + 'f}').format(v).replace('.', ',')


def virgola(ax, assi='xy'):
    """Virgola decimale anche sulle tacche: matplotlib usa il punto."""
    from matplotlib.ticker import FuncFormatter
    f = FuncFormatter(lambda v, _: ('{:g}'.format(v)).replace('.', ','))
    if 'x' in assi:
        ax.xaxis.set_major_formatter(f)
    if 'y' in assi:
        ax.yaxis.set_major_formatter(f)



# I JSON dei risultati sono stati scritti da un terminale senza accenti.
# Si correggono qui, alla resa, per non toccare i dati.
ACCENTI = {
    'meta sinistra': 'metà sinistra',
    'meta destra': 'metà destra',
}

def carica(rel):
    p = os.path.join(RIS, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def salva(fig, nome, dove, fonti):
    p = os.path.join(dove, nome)
    fig.savefig(p, bbox_inches='tight')
    plt.close(fig)
    print('  {:<34} <- {}'.format(nome, ', '.join(fonti)))


# =========================================================================
#  1. Le architetture
# =========================================================================
def fig_architetture(dove):
    nomi = [('gru', 'GRU'), ('lstm', 'LSTM'), ('cnn', 'CNN 1D'),
            ('transformer', 'Transformer'), ('foresta', 'Foresta')]
    dati, fonti = [], []
    for chiave, etichetta in nomi:
        rel = 'addestramento/run_{}_tre_classi_DTW_cam1.json'.format(chiave)
        d = carica(rel)
        if d is None:
            continue
        a = d['aggregato']
        dati.append((etichetta, a['fbeta_media'], a['fbeta_dev'],
                     d.get('n_parametri')))
        fonti.append(os.path.basename(rel))
    if not dati:
        return

    dati.sort(key=lambda r: -r[1])
    et = [r[0] for r in dati]
    f2 = np.array([r[1] for r in dati])
    dv = np.array([r[2] for r in dati])

    fig, ax = plt.subplots(figsize=(6.6, 3.5))
    y = np.arange(len(et))[::-1]

    # la banda grigia e' la dispersione fra soggetti della migliore: tutte le
    # architetture ci cadono dentro, ed e' questo il contenuto della figura
    ax.axvspan(f2[0] - dv[0], f2[0] + dv[0], color=CHIARO, alpha=.55, zorder=0)
    ax.errorbar(f2, y, xerr=dv, fmt='o', color=BLU, ecolor=GRIGIO,
                elinewidth=1.4, capsize=4, markersize=7, zorder=3)

    for i, (e, v, s, np_) in enumerate(dati):
        ax.text(v, y[i] + .26, dec(v), ha='center', va='bottom',
                fontsize=9, color=INK, fontweight='bold')
        if np_:
            ax.text(1.005, y[i], '{:,}'.format(np_).replace(',', '.'),
                    transform=ax.get_yaxis_transform(), va='center',
                    fontsize=8.5, color=GRIGIO)

    ax.set_yticks(y)
    ax.set_yticklabels(et)
    ax.set_xlabel('$F_2$ medio su dieci ripetizioni leave-one-subject-out')
    ax.set_title('Nessuna architettura è distinguibile dalle altre')
    ax.text(1.005, 1.11, 'parametri', transform=ax.transAxes,
            fontsize=8, color=GRIGIO, ha='left')
    ax.set_xlim(min(f2 - dv) - .04, max(f2 + dv) + .04)
    # margine in alto: l'etichetta della prima riga sta sopra il punto,
    # e senza questo finisce dentro al titolo
    ax.set_ylim(-.65, len(et) - .25)
    ax.grid(axis='x', color=CHIARO, linewidth=.7, zorder=0)
    ax.set_axisbelow(True)
    virgola(ax, 'x')

    fig.text(0, -.06,
             'La banda grigia è la dispersione fra soggetti della '
             'configurazione migliore ($\\pm$ {}). Tutte le architetture vi '
             'cadono dentro.'.format(dec(dv[0])),
             fontsize=8.5, color=GRIGIO)
    salva(fig, 'fig_architetture.png', dove, fonti)


# =========================================================================
#  2. Le configurazioni in laboratorio, a dieci soggetti
# =========================================================================
def fig_configurazioni(dove):
    d = carica('laboratorio/run_10soggetti.json')
    if d is None:
        return
    r = sorted(d['run'], key=lambda x: -x['f2'])
    et = [x['feature_set'] + ('  + controesempi' if x.get('controesempi')
                              else '') for x in r]
    f2 = np.array([x['f2'] for x in r])
    dv = np.array([x['f2_std'] for x in r])

    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    y = np.arange(len(et))[::-1]
    ax.barh(y, f2, height=.5, color=TEAL, alpha=.85, zorder=2)
    ax.errorbar(f2, y, xerr=dv, fmt='none', ecolor=INK,
                elinewidth=1.2, capsize=4, zorder=3)
    for i, v in enumerate(f2):
        ax.text(v + dv[i] + .006, y[i], dec(v), va='center',
                fontsize=9, fontweight='bold')
    ax.set_yticks(y)
    ax.set_yticklabels(et, fontsize=9)
    ax.set_xlabel('$F_2$ medio, dieci soggetti, leave-one-subject-out')
    ax.set_title('Le configurazioni a confronto, in laboratorio')
    ax.set_xlim(0, max(f2 + dv) + .09)
    ax.grid(axis='x', color=CHIARO, linewidth=.7, zorder=0)
    ax.set_axisbelow(True)
    virgola(ax, 'x')
    salva(fig, 'fig_configurazioni.png', dove,
          ['laboratorio/run_10soggetti.json'])


# =========================================================================
#  3. I tre compiti: F2 e falsi allarmi sui negativi difficili
# =========================================================================
def fig_compiti(dove):
    d = carica('compiti/foresta_DTW_cam1.json')
    if d is None:
        return
    c = d['compiti']
    et = [x['compito'] for x in c]
    f2 = np.array([x['fbeta_media'] for x in c])
    dv = np.array([x['fbeta_dev'] for x in c])
    diff = np.array([x['allarme_difficili'] for x in c]) * 100

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 3.1))
    x = np.arange(len(et))

    a1.bar(x, f2, width=.55, color=BLU, alpha=.85, zorder=2)
    a1.errorbar(x, f2, yerr=dv, fmt='none', ecolor=INK,
                elinewidth=1.2, capsize=4, zorder=3)
    for i, v in enumerate(f2):
        a1.text(i, v + dv[i] + .015, dec(v), ha='center',
                fontsize=9, fontweight='bold')
    a1.set_xticks(x)
    a1.set_xticklabels(et)
    a1.set_ylim(0, max(f2 + dv) + .12)
    a1.set_ylabel('$F_2$')
    a1.set_title('Quanto riconosce', fontsize=10.5)
    a1.grid(axis='y', color=CHIARO, linewidth=.7, zorder=0)
    a1.set_axisbelow(True)
    virgola(a1, 'y')

    colori = [ROSSO if v > 1 else TEAL for v in diff]
    a2.bar(x, diff, width=.55, color=colori, alpha=.85, zorder=2)
    for i, v in enumerate(diff):
        a2.text(i, v + max(diff) * .04, dec(v, 1) + '%', ha='center',
                fontsize=9, fontweight='bold')
    a2.set_xticks(x)
    a2.set_xticklabels(et)
    a2.set_ylim(0, max(diff) * 1.28 + .5)
    a2.set_ylabel('finestre in allarme')
    a2.set_title('Su una persona che si sdraia', fontsize=10.5)
    a2.grid(axis='y', color=CHIARO, linewidth=.7, zorder=0)
    a2.set_axisbelow(True)
    from matplotlib.ticker import FuncFormatter
    a2.yaxis.set_major_formatter(FuncFormatter(
        lambda v, _: ('{:g}'.format(v)).replace('.', ',') + '%'))
    # una barra a zero non si vede: un trattino sulla base dichiara che
    # il valore e' stato misurato, non che manca
    for i, v in enumerate(diff):
        if v == 0:
            a2.plot([i - .275, i + .275], [0, 0], color=TEAL,
                    linewidth=2.6, solid_capstyle='butt', zorder=4)

    fig.suptitle('La definizione del compito decide il comportamento',
                 fontsize=11.5, fontweight='bold', y=1.03)
    fig.tight_layout()
    salva(fig, 'fig_compiti.png', dove, ['compiti/foresta_DTW_cam1.json'])


# =========================================================================
#  4. Gli stessi tre compiti, misurati in casa
# =========================================================================
def fig_compiti_casa(dove):
    d = carica('campo/compiti_in_casa.json')
    if d is None:
        return
    c = d['compiti']
    et = [x['compito'].split('(')[0].strip() for x in c]
    ev = np.array([x['eventi_ora_totale'] for x in c])
    ril = [x.get('cadute_rilevate') for x in c]

    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    x = np.arange(len(et))
    ax.bar(x, ev, width=.5, color=ROSSO, alpha=.85, zorder=2)
    for i, v in enumerate(ev):
        testo = dec(v, 1) + '  eventi/h'
        if ril[i] is not None:
            testo += '\n{} cadute su 5'.format(ril[i])
        ax.text(i, v + max(ev) * .04, testo, ha='center',
                fontsize=9, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(et)
    ax.set_ylabel('eventi di allarme per ora')
    ax.set_ylim(0, max(ev) * 1.35)
    ax.set_title('Gli stessi tre compiti, in due abitazioni')
    ax.grid(axis='y', color=CHIARO, linewidth=.7, zorder=0)
    ax.set_axisbelow(True)
    fig.text(0, -.05,
             'Regola di allarme: {} finestre consecutive sopra {}, '
             'sospensione di {} s.'.format(
                 d['persistenza'], dec(d['soglia'], 2),
                 dec(d['sospensione_s'], 0)),
             fontsize=8.5, color=GRIGIO)
    salva(fig, 'fig_compiti_casa.png', dove, ['campo/compiti_in_casa.json'])


# =========================================================================
#  5. Il rumore iniettato sui landmark
# =========================================================================
def fig_rumore(dove):
    d = carica('rumore/foresta_cam1.json')
    if d is None:
        return
    prove = d['prove']
    sigma = np.array([p['sigma'] for p in prove])
    insiemi = [k for k in prove[0] if isinstance(prove[0][k], dict)]

    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    for nome, colore, segno in zip(insiemi, (BLU, TEAL, SABBIA), 'os^'):
        f2 = np.array([p[nome]['f2'] for p in prove])
        dv = np.array([p[nome]['dev'] for p in prove])
        ax.plot(sigma, f2, segno + '-', color=colore, label=nome,
                markersize=5.5, linewidth=1.6, zorder=3)
        ax.fill_between(sigma, f2 - dv, f2 + dv, color=colore, alpha=.10,
                        zorder=1)
    ax.set_xlabel('$\\sigma$ del rumore, in frazione della lunghezza del torso')
    ax.set_ylabel('$F_2$')
    ax.set_title('Il rumore indipendente non degrada la prestazione')
    virgola(ax)
    ax.legend(frameon=False, fontsize=9)
    ax.grid(color=CHIARO, linewidth=.7, zorder=0)
    ax.set_axisbelow(True)
    fig.text(0, -.06,
             'La banda è la dispersione fra soggetti: è più '
             'larga di qualunque effetto del rumore.',
             fontsize=8.5, color=GRIGIO)
    salva(fig, 'fig_rumore.png', dove, ['rumore/foresta_cam1.json'])


# =========================================================================
#  6. L'occlusione dei gruppi di landmark
# =========================================================================
def fig_occlusioni(dove):
    d = carica('occlusioni/foresta_DTW.json')
    if d is None:
        return
    base = next(p['fbeta_media'] for p in d['prove']
                if 'nessuna' in p['occlusione'])
    disp = next(p['fbeta_dev'] for p in d['prove']
                if 'nessuna' in p['occlusione'])

    # ATTENZIONE al nome del campo. `perdita_f2` contiene in realta'
    # F2(occluso) - F2(base): e' un DELTA, non una perdita. Positivo =
    # migliora. Verificato: naso -0,0078 con F2 0,8488 su base 0,8566.
    prove = [p for p in d['prove'] if 'nessuna' not in p['occlusione']]
    prove.sort(key=lambda p: p['perdita_f2'])
    et = [ACCENTI.get(p['occlusione'], p['occlusione']) for p in prove]
    delta = np.array([p['perdita_f2'] for p in prove])

    fig, ax = plt.subplots(figsize=(7.0, max(3.0, .36 * len(et) + 1.1)))
    y = np.arange(len(et))[::-1]
    colori = [TEAL if v >= 0 else ROSSO for v in delta]
    ax.barh(y, delta, height=.56, color=colori, alpha=.85, zorder=2)

    # la dispersione fra soggetti come banda simmetrica: e' il metro con cui
    # va letta ogni barra, e nessuna barra la raggiunge
    ax.axvspan(-disp, disp, color=CHIARO, alpha=.5, zorder=0)
    ax.axvline(0, color=INK, linewidth=1.0, zorder=3)

    largo = max(abs(delta).max(), disp)
    for i, v in enumerate(delta):
        dx = largo * .025
        ax.text(v + (dx if v >= 0 else -dx), y[i], dec(v),
                va='center', ha='left' if v >= 0 else 'right', fontsize=8.5)

    ax.set_yticks(y)
    ax.set_yticklabels(et, fontsize=8.5)
    ax.set_xlabel('variazione di $F_2$ occludendo il gruppo '
                  '(base {})'.format(dec(base)))
    ax.set_title('Nessun gruppo di punti è critico', pad=16)
    ax.set_xlim(-largo * 1.35, largo * 1.35)
    ax.set_ylim(-.7, len(et) - .1)
    ax.grid(axis='x', color=CHIARO, linewidth=.7, zorder=1)
    ax.set_axisbelow(True)
    virgola(ax, 'x')
    fig.text(0, -.045,
             'A sinistra dello zero la prestazione peggiora, a destra '
             'migliora. Il peggioramento più grande è {}; la banda grigia è '
             'la dispersione fra soggetti ($\\pm$ {}), e nessuna barra la '
             'raggiunge.'.format(dec(abs(delta.min())), dec(disp)),
             fontsize=8.5, color=GRIGIO)
    salva(fig, 'fig_occlusioni.png', dove, ['occlusioni/foresta_DTW.json'])


# =========================================================================
#  7. La lunghezza della finestra
# =========================================================================
def fig_finestra(dove):
    dati, fonti = [], []
    for L in (22, 28, 36, 44):
        rel = 'addestramento/run_gru_tre_classi_DTW_cam1_L{}.json'.format(L)
        d = carica(rel)
        if d is None:
            continue
        a = d['aggregato']
        secondi = L / float(d.get('fps_esercizio') or 9.0)
        dati.append((L, secondi, a['fbeta_media'], a['fbeta_dev']))
        fonti.append(os.path.basename(rel))
    if len(dati) < 2:
        return

    L = np.array([r[0] for r in dati])
    sec = [r[1] for r in dati]
    f2 = np.array([r[2] for r in dati])
    dv = np.array([r[3] for r in dati])

    fig, ax = plt.subplots(figsize=(6.2, 3.2))
    ax.errorbar(L, f2, yerr=dv, fmt='o-', color=BLU, ecolor=GRIGIO,
                elinewidth=1.3, capsize=4, markersize=6, linewidth=1.6,
                zorder=3)
    for i, v in enumerate(f2):
        ax.text(L[i], v + dv[i] + .012, dec(v), ha='center', fontsize=8.5)
    ax.set_xticks(L)
    ax.set_xticklabels(['{}\n{} s'.format(l, dec(s, 1))
                        for l, s in zip(L, sec)])
    ax.set_xlabel('lunghezza della finestra, in campioni e in secondi')
    ax.set_ylabel('$F_2$')
    virgola(ax, 'y')
    ax.set_title('La lunghezza della finestra non cambia l’esito')
    ax.grid(color=CHIARO, linewidth=.7, zorder=0)
    ax.set_axisbelow(True)
    salva(fig, 'fig_finestra.png', dove, fonti)


# =========================================================================
#  8. Il trasferimento a UR-Fall
# =========================================================================
def fig_esterno(dove):
    d = carica('esterno/urfall_foresta_caduta.json')
    if d is None:
        return
    c = d['config']
    et = [x['rappresentazione'].strip() for x in c]
    gua = np.array([x['guadagno'] for x in c])
    f2 = np.array([x['f2'] for x in c])

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 3.2))
    y = np.arange(len(et))[::-1]

    a1.barh(y, gua, height=.5, color=BLU, alpha=.85, zorder=2)
    a1.axvline(1, color=ROSSO, linewidth=1.3, linestyle='--', zorder=3)
    a1.text(1, y[0] + .7, ' caso', color=ROSSO, fontsize=8.5, va='bottom')
    for i, v in enumerate(gua):
        a1.text(v + max(gua) * .02, y[i], dec(v, 1) + '×',
                va='center', fontsize=9, fontweight='bold')
    a1.set_yticks(y)
    a1.set_yticklabels(et, fontsize=8.5)
    a1.set_xlim(0, max(gua) * 1.25)
    a1.set_title('Guadagno di PR-AUC sul caso', fontsize=10.5)
    a1.grid(axis='x', color=CHIARO, linewidth=.7, zorder=0)
    a1.set_axisbelow(True)

    a2.barh(y, f2, height=.5, color=GRIGIO, alpha=.85, zorder=2)
    for i, v in enumerate(f2):
        a2.text(v + max(f2) * .02, y[i], dec(v), va='center', fontsize=9)
    a2.set_yticks(y)
    a2.set_yticklabels([])
    a2.set_xlim(0, max(f2) * 1.3)
    a2.set_title('$F_2$ sull’archivio esterno', fontsize=10.5)
    a2.grid(axis='x', color=CHIARO, linewidth=.7, zorder=0)
    a2.set_axisbelow(True)
    virgola(a1, 'x')
    virgola(a2, 'x')

    fig.suptitle('Il trasferimento a un archivio registrato altrove',
                 fontsize=11.5, fontweight='bold', y=1.03)
    fig.tight_layout()
    salva(fig, 'fig_esterno.png', dove, ['esterno/urfall_foresta_caduta.json'])



# =========================================================================
#  9. Dimensione del modello   (CINQUE SOGGETTI)
# =========================================================================
#  Le due figure che seguono NON vengono dalle run a dieci soggetti. Leggono
#  `risultati/cinque_soggetti/`, e lo dichiarano dentro l'immagine: il
#  capitolo dei risultati riporta la stessa avvertenza accanto a entrambe.
#  Sono qui perche' le due misure non sono state ripetute, non perche' siano
#  equivalenti alle altre.

AVVISO_5 = 'misura a cinque soggetti, non ripetuta a dieci'


def _cinque(nome):
    p = os.path.join(RIS, 'cinque_soggetti', nome)
    return p if os.path.exists(p) else None


def fig_dimensione(dove):
    p = _cinque('exp017_rf_size.json')
    if p is None:
        return
    with open(p, encoding='utf-8') as f:
        prove = json.load(f)

    n = np.array([q['n_trees'] for q in prove], float)
    f2 = np.array([q['fbeta'] for q in prove])
    dv = np.array([q['fbeta_std'] for q in prove])
    ms = np.array([q['latency_ms_pc'] for q in prove])
    imax = int(np.argmax(f2))

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.errorbar(n, f2, yerr=dv, fmt='o-', color=BLU, capsize=3, lw=1.6,
                ms=5, label='$F_2$ (barre: dispersione fra fold)')
    ax.plot(n[imax], f2[imax], 'o', ms=11, mfc='none', mec=ROSSO, mew=2)
    ax.annotate(('{:g} alberi' + chr(10) + '$F_2$ {}')
                .format(n[imax], dec(f2[imax])),
                (n[imax], f2[imax]), textcoords='offset points',
                xytext=(6, 16), color=ROSSO, fontsize=8.5)
    ax.set_xscale('log')
    ax.set_xticks(n)
    ax.set_xticklabels([str(int(v)) for v in n])
    ax.set_xlabel('alberi della foresta')
    ax.set_ylabel('$F_2$', color=BLU)
    ax.tick_params(axis='y', colors=BLU)
    virgola(ax, 'y')

    ax2 = ax.twinx()
    ax2.plot(n, ms, 's--', color=SABBIA, lw=1.4, ms=4.5, label='latenza')
    ax2.set_ylabel('latenza per finestra [ms]', color=SABBIA)
    ax2.tick_params(axis='y', colors=SABBIA)
    ax2.spines['right'].set_visible(True)
    ax2.spines['right'].set_color(GRIGIO)
    virgola(ax2, 'y')

    ax.set_title('Accuratezza e latenza al variare della dimensione'
                 ' della foresta', pad=12)
    ax.text(0.5, -0.38, AVVISO_5, transform=ax.transAxes, ha='center',
            fontsize=8, color=GRIGIO, style='italic')
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc='upper center',
              bbox_to_anchor=(0.5, -0.20), ncol=2,
              frameon=False, fontsize=8.5)
    salva(fig, 'fig_dimensione.png', dove, ['cinque_soggetti/exp017_rf_size.json'])


# =========================================================================
#  10. Il punto di vista, distribuzione   (CINQUE SOGGETTI)
# =========================================================================

def fig_viewpoint_dist(dove):
    p = _cinque('exp013_camera_viewpoint.csv')
    if p is None:
        return
    import csv
    righe = list(csv.DictReader(open(p, encoding='utf-8')))

    # una coppia per sequenza: stesso soggetto, stessa prova, stesso istante
    coppie = {}
    for r in righe:
        k = (r['subject'], r['activity'], r['trial'])
        coppie.setdefault(k, {})[int(r['camera'])] = float(r['exc_2d'])
    coppie = {k: v for k, v in coppie.items() if 1 in v and 2 in v}

    c1 = np.array([v[1] for v in coppie.values()])
    c2 = np.array([v[2] for v in coppie.values()])
    pari = int((c2 >= c1).sum())
    rapporto = c1.mean() / c2.mean()

    fig, ax = plt.subplots(figsize=(5.6, 4.6))
    for a, b in zip(c1, c2):
        rov = b >= a
        ax.plot([0, 1], [a, b], '-', lw=1.3,
                color=ROSSO if rov else CHIARO, zorder=3 if rov else 1)
        ax.plot([0, 1], [a, b], 'o', ms=3.5,
                color=ROSSO if rov else GRIGIO, zorder=3 if rov else 1)
    ax.plot([0, 1], [c1.mean(), c2.mean()], 'o-', color=BLU, lw=2.6, ms=8,
            zorder=5, label='media')
    grado = '$^' + chr(92) + 'circ$'
    for x, v in ((0, c1.mean()), (1, c2.mean())):
        ax.annotate(dec(v, 1) + grado, (x, v), textcoords='offset points',
                    xytext=(-46 if x == 0 else 12, -5), color=BLU,
                    fontweight='bold', fontsize=10)

    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Camera 1' + chr(10) + 'laterale',
                        'Camera 2' + chr(10) + 'frontale rialzata'])
    ax.set_xlim(-0.45, 1.45)
    ax.set_ylabel('escursione dell' + chr(39) + 'angolo del tronco [gradi]')
    ax.set_title('Che cosa vede ciascuna telecamera, sulla stessa caduta',
                 pad=14)
    virgola(ax, 'y')
    nota = ('{} sequenze, rapporto fra le medie {}' + chr(215) + '.  '
            'In {} la vista rialzata osserva quanto quella laterale.')
    ax.text(0.5, -0.22, nota.format(len(c1), dec(rapporto, 2), pari),
            transform=ax.transAxes, ha='center', va='top',
            fontsize=8.5, color=INK)
    ax.text(0.5, -0.31, AVVISO_5, transform=ax.transAxes, ha='center',
            va='top', fontsize=8, color=GRIGIO, style='italic')
    ax.legend(frameon=False, loc='upper right', fontsize=8.5)
    salva(fig, 'fig_viewpoint_dist.png', dove,
          ['cinque_soggetti/exp013_camera_viewpoint.csv'])
    print('     -> {} coppie, rapporto {}, {} rovesciate'
          .format(len(c1), dec(rapporto, 2), pari))


# =========================================================================
#  11. I due tipi di errore, per configurazione   (dieci soggetti)
# =========================================================================
#  Il relatore, nel punto 5 della sua email del 20 agosto: «Non cerchereidi
#  nascondere questa differenza dentro un unico F2. Al contrario la
#  mostrerei esplicitamente.» Questa figura e' quella richiesta: falsi
#  negativi e falsi positivi separati, non riassunti.

def fig_errori(dove):
    d = carica(os.path.join('laboratorio', 'run_10soggetti.json'))
    if d is None:
        return
    run = d['run']
    nomi = [r['feature_set'] + (' + contro.' if r['controesempi'] else '')
            for r in run]
    fn = np.array([r['fn'] for r in run], float)
    fp = np.array([r['fp'] for r in run], float)
    x = np.arange(len(run))
    w = 0.36

    fig, ax = plt.subplots(figsize=(6.6, 3.8))
    b1 = ax.bar(x - w / 2, fn, w, color=ROSSO, label='falsi negativi')
    b2 = ax.bar(x + w / 2, fp, w, color=BLU, label='falsi positivi')
    for b in list(b1) + list(b2):
        ax.annotate(str(int(b.get_height())),
                    (b.get_x() + b.get_width() / 2, b.get_height()),
                    textcoords='offset points', xytext=(0, 3),
                    ha='center', fontsize=8.5)
    ax.set_xticks(x)
    ax.set_xticklabels(nomi)
    ax.set_ylabel('finestre classificate male')
    ax.set_title('I due tipi di errore, separati')
    ax.legend(frameon=False, fontsize=8.5)
    ax.set_ylim(0, max(fp.max(), fn.max()) * 1.18)

    nota = ('Dalla configurazione di riferimento alla finale: '
            'falsi negativi {:.0f} -> {:.0f}, falsi positivi {:.0f} -> {:.0f}. '
            'Nessuno scambio.')
    ax.text(0.5, -0.24, nota.format(fn[0], fn[-1], fp[0], fp[-1]),
            transform=ax.transAxes, ha='center', va='top',
            fontsize=8.5, color=INK)
    salva(fig, 'fig_errori.png', dove, ['laboratorio/run_10soggetti.json'])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dove', default=DEFAULT)
    a = ap.parse_args()
    os.makedirs(a.dove, exist_ok=True)

    print('risultati da : {}'.format(RIS))
    print('figure verso : {}\n'.format(a.dove))
    for f in (fig_errori, fig_dimensione, fig_viewpoint_dist,
              fig_architetture, fig_configurazioni, fig_compiti,
              fig_compiti_casa, fig_rumore, fig_occlusioni, fig_finestra,
              fig_esterno):
        try:
            f(a.dove)
        except Exception as e:                      # una figura non blocca le altre
            print('  {:<34} FALLITA: {}'.format(f.__name__, e))
    print('\nfatto')


if __name__ == '__main__':
    main()
