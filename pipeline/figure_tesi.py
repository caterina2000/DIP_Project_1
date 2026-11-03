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

UNA FIGURA NON STA QUI. `fig_rappresentazioni.png` e' prodotta da
`pipeline/figura_rappresentazioni.py`, che richiede MediaPipe e quindi
l'ambiente `fall_processing`: disegna le tre costruzioni geometriche su un
fotogramma vero di UP-Fall, con i landmark stimati e i valori calcolati dal
motore geometrico. Fino al 2026-09-02 una funzione di QUESTO file ne
disegnava una versione sintetica e sovrascriveva quella vera senza segnalarlo.
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
    'savefig.dpi': 400,
})


# =========================================================================
#  LINGUA E TITOLI
# =========================================================================
# `LINGUA` e `TITOLI` sono stato di modulo e non parametri di ogni funzione:
# le quattordici figure hanno firme diverse e passarli a mano significherebbe
# toccare ogni chiamata. main() li imposta una volta.
LINGUA = 'it'
TITOLI = False

AP = chr(8217)          # apostrofo tipografico
APS = chr(39)           # apostrofo dritto
NL = chr(10)          # il titolo sta nella didascalia, non nell'immagine


def T(it, en):
    """La stringa nella lingua corrente."""
    return it if LINGUA == 'it' else en


# Le etichette che arrivano dai file di risultato sono scritte in italiano
# dentro i dati. Si traducono alla resa, come gia' si fa per gli accenti in
# ACCENTI, per non toccare i risultati.
DATI_EN = {
    'evento': 'event', 'stato': 'state', 'allarme': 'alarm',
    'spalle': 'shoulders', 'caviglie': 'ankles', 'anche': 'hips',
    'naso': 'nose', 'ginocchia': 'knees',
    'metà sinistra': 'left half', 'metà destra': 'right half',
    'meta sinistra': 'left half', 'meta destra': 'right half',
    'casuale': 'random', 'nessuna': 'none',
    'senza integrali': 'without integrals',
    'con integrali': 'with integrals',
    'sottoinsieme DTW': 'DTW subset',
    'controesempi': 'counter-examples',
}


def D(s):
    """Etichetta proveniente dai dati, tradotta se serve."""
    if LINGUA == 'it':
        return s
    if s in DATI_EN:
        return DATI_EN[s]
    fuori = s
    for it, en in sorted(DATI_EN.items(), key=lambda kv: -len(kv[0])):
        if it in fuori:
            fuori = fuori.replace(it, en)
    return fuori


def titolo(ax, it, en, **kw):
    """Il titolo della figura: disegnato solo se TITOLI e' attivo."""
    if TITOLI:
        ax.set_title(T(it, en), **kw)


def suffisso(nome):
    """`fig_x.png` -> `fig_x_en.png` quando la lingua non e' l'italiano."""
    if LINGUA == 'it':
        return nome
    radice, punto, est = nome.rpartition('.')
    return radice + '_en' + punto + est


def grado_s():
    """Il simbolo di grado in matematica LaTeX, senza scriverlo a mano."""
    return '$^' + chr(92) + 'circ$'


def dec(v, n=3):
    """Numero decimale: virgola in italiano, punto in inglese.

    Il separatore NON e' un dettaglio di stile. In inglese il punto e' il
    separatore decimale e la virgola separa le migliaia, quindi «0,953»
    stampato in una figura inglese e' scorretto, e «13,330» si leggerebbe
    tredicimilatrecentotrenta. Prima questa funzione metteva la virgola
    sempre, e tutte le figure `_en` la portavano.
    """
    t = ('{:.' + str(n) + 'f}').format(v)
    return t.replace('.', ',') if LINGUA == 'it' else t


def mille(v):
    """Separatore delle MIGLIAIA: punto in italiano, virgola in inglese.

    Speculare a `dec`, e nata dallo stesso difetto visto dall'altro lato.
    Due punti del file scrivevano `'{:,}'.format(v).replace(',', '.')` senza
    guardare la lingua: Python produce gia' «24,483» all'inglese, e quella
    sostituzione lo riportava a «24.483», che in una figura inglese si legge
    ventiquattro virgola quattrocentottantatre. Colpiva `fig_architetture`
    (i parametri dei modelli) e `fig_viste` (falsi positivi e cadute non
    viste), cioe' proprio le due figure in cui i numeri sono migliaia.
    """
    t = '{:,}'.format(int(v))
    return t.replace(',', '.') if LINGUA == 'it' else t


def virgola(ax, assi='xy'):
    """Il separatore decimale sulle tacche. In inglese non si tocca nulla."""
    if LINGUA != 'it':
        return                      # matplotlib usa gia' il punto
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


def fattore_aggregato():
    """
    Il rapporto fra finestre sopra soglia ed eventi su TUTTE le sessioni.

    Era scritto a mano nelle schede fino al 7 settembre 2026, quando una
    sessione nuova lo ha spostato da 47,8 a 44,8 e le schede sono rimaste
    indietro (ISS-140). Ora viene dall'artefatto che lo calcola, prodotto da
    pipeline/eventi_sessioni.py; se manca, la scheda lo dichiara mancante
    invece di inventarlo.
    """
    d = carica('campo/eventi_sessioni.json')
    return dec(d['fattore_sovrastima'], 1) if d else '(non calcolato)'


def salva(fig, nome, dove, fonti, scheda=None):
    """
    Il PNG, e accanto la scheda che lo spiega.

    Perche' la spiegazione sta in un file di testo e non dentro l'immagine
    ------------------------------------------------------------------------
    Fino al 2026-09-06 diverse figure portavano stampata dentro la propria
    conclusione --- «Nessuna architettura fa meglio della GRU», «Nessun gruppo
    di punti e' critico» --- e sotto una nota in prosa. Sono due difetti
    distinti.

    Il primo e' che un titolo che afferma una tesi non e' una figura, e' una
    diapositiva: il lettore non puo' verificarlo guardando, gli viene detto. In
    una tesi la conclusione la trae il testo, e la figura mostra il dato su cui
    si regge. I titoli sono quindi **descrittivi**: dicono che cosa e'
    disegnato, non che cosa se ne deve concludere.

    Il secondo e' che quella prosa non e' modificabile senza rigenerare
    l'immagine, non compare nell'indice delle figure, non e' cercabile, e nel
    PDF finisce in un corpo tipografico diverso da quello della didascalia.

    Restano dentro l'immagine soltanto le due cose che senza di essa non si
    leggono: i **valori** sui marcatori e le **etichette degli elementi** di
    uno schema (il divano, la finestra, l'asse ottico).

    La scheda e' un dizionario con quattro voci, tutte facoltative:
    `mostra`, `come_si_legge`, `numeri`, `provenienza`.
    """
    nome = suffisso(nome)
    p = os.path.join(dove, nome)
    fig.savefig(p, bbox_inches='tight')
    plt.close(fig)
    print('  {:<34} <- {}'.format(nome, ', '.join(fonti)))
    if scheda:
        scrivi_scheda(nome, dove, fonti, scheda)


def scrivi_scheda(nome, dove, fonti, scheda):
    """La scheda `.txt` accanto al PNG, con lo stesso nome."""
    def blocco(titolo, testo):
        if not testo:
            return []
        righe = [titolo, '-' * len(titolo)]
        for par in [t.strip() for t in testo.strip().split('\n\n')]:
            righe += [_a_capo(par), '']
        return righe

    r = ['FIGURA — ' + nome, '=' * (9 + len(nome)), '']
    r += blocco('CHE COSA MOSTRA', scheda.get('mostra'))
    r += blocco('COME SI LEGGE', scheda.get('come_si_legge'))
    r += blocco('I NUMERI', scheda.get('numeri'))
    r += blocco('PROVENIENZA', scheda.get('provenienza'))
    r += ['PRODOTTA DA', '-' * 11,
          'pipeline/figure_tesi.py', 'su ' + ', '.join(fonti), '']
    percorso = os.path.join(dove, os.path.splitext(nome)[0] + '.txt')
    with open(percorso, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(r))
    return percorso


def _a_capo(testo, larghezza=76):
    """Manda a capo a 76 colonne, che e' come sono scritti gli altri .txt."""
    import textwrap
    return '\n'.join(textwrap.wrap(' '.join(testo.split()), larghezza))


# =========================================================================
#  Il posizionamento della telecamera
# =========================================================================
def fig_stanza(dove):
    """
    Schema del posizionamento della telecamera: pianta e alzato.

    ECCEZIONE ALLA REGOLA DEL MODULO, dichiarata. Tutte le altre figure
    leggono `risultati/`; questa no, perche' non ha numeri da leggere: e' la
    resa grafica del protocollo di ripresa, che il capitolo descrive in mezza
    pagina di prosa. La sua sorgente e' quel protocollo, ed e' stampata in coda
    come per le altre.

    Le quantita' disegnate sono quelle prescritte: altezza 1,2-1,5 m, asse
    ottico orizzontale, distanza 3-4 m dall'area di caduta, lato lungo
    dell'area perpendicolare all'asse ottico, finestra alle spalle.

    Il campo visivo e' RITAGLIATO sulle pareti: un cono che le attraversa
    disegnerebbe una stanza che non c'e'.
    """
    from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch

    fig, (ax, bx) = plt.subplots(
        1, 2, figsize=(9.0, 3.6), gridspec_kw={'width_ratios': [1.30, 1]})

    # ---------------------------------------------------------------- PIANTA
    L, H = 6.0, 4.5
    muri = Rectangle((0, 0), L, H, fill=False, ec=INK, lw=1.6)
    ax.add_patch(muri)

    cx, cy = .40, 1.90
    mezzo = np.radians(31.0)                       # apertura 62 gradi
    cono = Polygon([(cx, cy),
                    (cx + 7, cy + 7 * np.tan(mezzo)),
                    (cx + 7, cy - 7 * np.tan(mezzo))],
                   fc=BLU, alpha=.11, ec='none')
    ax.add_patch(cono)
    ritaglio = Rectangle((0, 0), L, H, transform=ax.transData)
    cono.set_clip_path(ritaglio)
    for verso in (+1, -1):
        linea, = ax.plot([cx, cx + 7], [cy, cy + verso * 7 * np.tan(mezzo)],
                         color=BLU, lw=.8, ls=':', zorder=2)
        linea.set_clip_path(ritaglio)

    # parete attrezzata e divano
    ax.add_patch(Rectangle((2.0, H - .26), 3.0, .26, fc=CHIARO, ec=GRIGIO))
    ax.text(3.5, H - .13, T('parete attrezzata', 'fitted units'), ha='center', va='center',
            fontsize=7.5, color=INK)
    ax.add_patch(Rectangle((2.9, .48), 2.2, .78, fc=SABBIA, ec=GRIGIO,
                           alpha=.75))
    ax.text(4.0, .87, T('divano', 'sofa'), ha='center', va='center', fontsize=8.5,
            color=INK)

    # finestra alle spalle
    ax.plot([0, 0], [3.0, 4.1], color=TEAL, lw=4.5, solid_capstyle='butt')
    ax.text(-.14, 3.55, T('finestra', 'window'), rotation=90, ha='center', va='center',
            fontsize=7.5, color=TEAL)

    # area di caduta, lato lungo perpendicolare all'asse ottico
    ax.add_patch(Rectangle((3.20, 1.55), .72, 1.70, fc=ROSSO, ec=ROSSO,
                           alpha=.15, lw=1.1))
    ax.add_patch(FancyArrowPatch((3.56, 1.72), (3.56, 3.08),
                                 arrowstyle='<->', mutation_scale=12,
                                 color=ROSSO, lw=1.5))
    ax.text(3.56, 3.38, T('area di caduta', 'fall area'), ha='center', va='bottom',
            fontsize=8, color=ROSSO)

    # telecamera e asse ottico
    ax.plot([cx, L - .15], [cy, cy], color=BLU, lw=1.0, ls='--', zorder=3)
    ax.plot(cx, cy, marker='s', ms=10, color=BLU, zorder=4)
    ax.text(cx - .12, cy - .30, T('telecamera', 'camera'), ha='left', va='top',
            fontsize=8.5, color=BLU, weight='bold')
    ax.text(2.35, cy + .09, T('asse ottico', 'optical axis'), ha='center', va='bottom',
            fontsize=7.5, color=BLU)

    # distanza
    for qx in (cx, 3.56):
        ax.plot([qx, qx], [-.10, -.40], color=GRIGIO, lw=.7)
    ax.annotate('', xy=(3.56, -.28), xytext=(cx, -.28),
                arrowprops=dict(arrowstyle='<->', color=INK, lw=.9))
    ax.text((cx + 3.56) / 2, -.40, '3–4 m', ha='center', va='top',
            fontsize=8, color=INK)

    ax.text(L + .18, 2.45,
            T('la caduta attraversa\nl’inquadratura,\nnon si allontana',
              'the fall crosses the frame,\nit does not recede'),
            ha='left', va='center', fontsize=8, color=ROSSO)

    ax.set_xlim(-.55, L + 1.9)
    ax.set_ylim(-.95, H + .75)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(T('Pianta', 'Plan'), fontsize=10, pad=2)

    # ---------------------------------------------------------------- ALZATO
    h_cam = 1.35
    mezzo_v = np.radians(24.0)
    est = 4.4
    conov = Polygon([(0, h_cam),
                     (est, h_cam + est * np.tan(mezzo_v)),
                     (est, h_cam - est * np.tan(mezzo_v))],
                    fc=BLU, alpha=.11, ec='none')
    bx.add_patch(conov)
    conov.set_clip_path(Rectangle((0, 0), est, 3.0, transform=bx.transData))

    bx.plot([-.55, est], [0, 0], color=INK, lw=1.6)
    bx.text(-.52, -.16, T('pavimento', 'floor'), ha='left', va='top', fontsize=7.5,
            color=GRIGIO)

    bx.plot([0, 0], [0, h_cam], color=GRIGIO, lw=1.2)
    bx.plot(0, h_cam, marker='s', ms=10, color=BLU)
    bx.annotate('', xy=(-.30, h_cam), xytext=(-.30, 0),
                arrowprops=dict(arrowstyle='<->', color=INK, lw=.9))
    bx.text(-.38, h_cam / 2, '1,2–1,5 m', rotation=90, ha='right',
            va='center', fontsize=8, color=INK)

    bx.plot([0, est], [h_cam, h_cam], color=BLU, lw=1.0, ls='--')
    bx.text(1.05, h_cam + .09, T('asse ottico orizzontale', 'horizontal optical axis'), ha='center',
            va='bottom', fontsize=7.5, color=BLU)

    px = 2.7
    bx.plot([px, px], [0, 1.66], color=INK, lw=2.8, solid_capstyle='round')
    bx.plot(px, 1.76, marker='o', ms=7, color=INK)
    bx.text(px, 1.92, T('in piedi', 'standing'), ha='center', va='bottom', fontsize=8,
            color=INK)

    bx.plot([px - .78, px + .70], [.13, .13], color=ROSSO, lw=2.8,
            solid_capstyle='round')
    bx.plot(px + .78, .13, marker='o', ms=7, color=ROSSO)
    bx.text(px + .95, .13, T('a terra', 'on the ground'), ha='left', va='center', fontsize=8,
            color=ROSSO)

    bx.text(est / 2 - .1, 2.62,
            T('entrambe le posture devono stare intere\n'
              'nell’inquadratura, e con esse il pavimento',
              'both postures must fit entirely in the frame,\n'
              'and so must the floor'),
            ha='center', va='center', fontsize=7.8, color=INK)

    bx.set_xlim(-.95, est + 1.15)
    bx.set_ylim(-.55, 3.05)
    bx.set_aspect('equal')
    bx.axis('off')
    bx.set_title(T('Alzato', 'Elevation'), fontsize=10, pad=2)

    TITOLI and fig.suptitle(
        T('Posizionamento della telecamera: pianta e alzato',
          'Camera placement: plan and elevation'),
                 fontsize=11, fontweight='bold', y=1.03)

    salva(fig, 'fig_stanza.png', dove, ['protocollo di ripresa (schema, non dati)'], scheda={
        'mostra':
            'Come va messa la telecamera nella stanza: a sinistra la pianta '
            'vista dall\'alto, a destra l\'alzato visto di lato. Non e\' una '
            'misura: e\' la resa grafica del protocollo di ripresa, che il '
            'capitolo descrive altrimenti in mezza pagina di prosa.',
        'come_si_legge':
            'Nella pianta contano due cose: il cono del campo visivo '
            'contiene sia il divano sia l\'area libera, e il lato lungo '
            'dell\'area di caduta e\' PERPENDICOLARE all\'asse ottico, cosi\' '
            'che una caduta attraversi l\'inquadratura invece di allontanarsi. '
            'Nell\'alzato conta l\'altezza, 1,2-1,5 m, e l\'asse ottico '
            'orizzontale: una telecamera a picco vede una persona in piedi e '
            'una distesa quasi allo stesso modo.',
        'numeri':
            'Altezza 1,2-1,5 m; distanza 3-4 m dal centro dell\'area; '
            'finestra alle spalle o di lato, mai di fronte.',
        'provenienza':
            'Nessun file di risultato: la sorgente e\' il protocollo di '
            'ripresa. E\' l\'unica figura del capitolo che non legge da '
            'risultati/, ed e\' dichiarato.',
    })


# =========================================================================
#  La selezione con il DTW
# =========================================================================
def fig_dtw(dove):
    """
    Separabilita' di ogni grandezza sulle due camere, e le dodici scelte.

    Ogni punto e' una grandezza: in ascissa quanto separa le classi sulla
    vista laterale, in ordinata sulla frontale rialzata. La diagonale e' il
    luogo delle grandezze che si comportano allo stesso modo dalle due viste;
    sotto la diagonale stanno quelle che funzionano di profilo e non dall'alto.

    Il criterio di selezione e' il MINIMO fra le due camere, non la media: una
    grandezza che separa benissimo da un punto di vista e per niente dall'altro
    non e' utile a un sistema che verra' installato in una stanza qualunque.
    """
    import csv

    p = os.path.join(RIS, 'dtw', 'classifica_dtw.csv')
    q = os.path.join(RIS, 'dtw', 'scelte.txt')
    if not os.path.exists(p):
        return
    righe = []
    with io.open(p, encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            try:
                righe.append((r['grandezza'], float(r['punteggio_cam1']),
                              float(r['punteggio_cam2'])))
            except (KeyError, ValueError):
                continue
    if not righe:
        return
    scelte = set()
    if os.path.exists(q):
        scelte = {l.strip() for l in io.open(q, encoding='utf-8') if l.strip()}

    fig, ax = plt.subplots(figsize=(7.4, 6.6))
    lim = [min(min(x for _, x, _ in righe), min(y for _, _, y in righe)) - .02,
           max(max(x for _, x, _ in righe), max(y for _, _, y in righe)) + .04]
    ax.plot(lim, lim, ls='--', lw=1.1, color=GRIGIO, zorder=1)

    for nome, x, y in righe:
        dentro = nome in scelte
        ax.scatter(x, y, s=76 if dentro else 34,
                   color=TEAL if dentro else ROSSO,
                   edgecolor='white', linewidth=.8,
                   zorder=3 if dentro else 2)
        ax.annotate(nome, (x, y), textcoords='offset points',
                    xytext=(7, 4), fontsize=7.4,
                    color=INK if dentro else GRIGIO,
                    fontweight='bold' if dentro else 'normal')

    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_xlabel(T('separazione sulla Camera 1 (laterale)',
                    'separation on Camera 1 (lateral)'))
    ax.set_ylabel(T('separazione sulla Camera 2 (frontale rialzata)',
                    'separation on Camera 2 (raised frontal)'))
    ax.set_aspect('equal')
    virgola(ax)
    salva(fig, 'fig_dtw.png', dove, ['dtw/classifica_dtw.csv', 'dtw/scelte.txt'], scheda={
        'mostra':
            'Ogni punto e\' una delle trentadue grandezze geometriche. In '
            'ascissa quanto quella grandezza separa le cadute dal resto sulla '
            'telecamera laterale, in ordinata sulla frontale rialzata. Sono '
            'evidenziate le dodici scelte.',
        'come_si_legge':
            'La diagonale e\' il luogo delle grandezze che si comportano allo '
            'stesso modo dalle due viste. I punti SOTTO la diagonale '
            'funzionano di profilo e non dall\'alto: sono quelli che '
            'renderebbero il sistema dipendente da come e\' installata la '
            'telecamera.',
        'numeri':
            'Il criterio di selezione e\' il MINIMO fra le due telecamere, '
            'non la media. Una grandezza che separa benissimo da un punto di '
            'vista e per niente dall\'altro non serve a un sistema che verra\' '
            'montato in una stanza qualunque, e la media la premierebbe.',
        'provenienza': 'Dieci soggetti.',
    })


# =========================================================================
#  Il profilo temporale di una sessione domestica
# =========================================================================
def fig_sessione(dove):
    """
    Cinque ore di esercizio continuo: punteggio per finestra, soglia, raffiche
    sopra soglia, e allarmi emessi dopo l'antirimbalzo.

    Perche' questa figura serve. Il rapporto fra finestre sopra soglia ed
    eventi vale 44,8 ed e' il numero che distingue un dato riportabile da uno
    che sovrastima di due ordini di grandezza. Fino a oggi era solo un numero:
    qui si vede, perche' le raffiche sono visibilmente raggruppate e gli
    allarmi che ne escono sono pochi triangoli.

    La regola applicata e' quella del sistema installato --- cinque finestre
    consecutive sopra soglia, poi trenta secondi di silenzio --- ricalcolata
    qui dai punteggi, non letta da `eventi.csv`, che contiene finestre e non
    eventi.
    """
    import csv

    rel = os.path.join('sessioni', '20260811',
                       'bloccodurata5h_20260811_130411', 'punteggi.csv')
    p = os.path.join(RIS, rel)
    if not os.path.exists(p):
        return

    t, punteggio = [], []
    with io.open(p, encoding='utf-8') as fh:
        for riga in csv.DictReader(fh):
            try:
                t.append(float(riga['t_unix']))
                punteggio.append(float(riga['punteggio']))
            except (KeyError, ValueError):
                continue
    if len(t) < 100:
        return

    t = np.asarray(t)
    y = np.asarray(punteggio)
    ore = (t - t[0]) / 3600.0

    SOGLIA, PERSISTENZA, SOSPENSIONE = 0.5, 5, 30.0
    sopra = y >= SOGLIA

    # la stessa regola di pipeline/eventi_sessioni.py, riscritta qui in tre
    # righe perche' la figura non dipenda dall'ordine degli import
    allarmi, corsa, ultimo = [], 0, -1e18
    for i, v in enumerate(sopra):
        corsa = corsa + 1 if v else 0
        if corsa >= PERSISTENZA and (t[i] - ultimo) >= SOSPENSIONE:
            allarmi.append(i)
            ultimo = t[i]

    # L'INTERRUZIONE. Fra due finestre consecutive c'e' un salto di oltre un
    # ora: e' la sospensione automatica del sistema operativo, il difetto che
    # ha reso non valida la prima prova di durata. Va mostrata, non nascosta:
    # una figura che la interpolasse racconterebbe una sessione continua che
    # non c'e' stata.
    salti = np.where(np.diff(t) > 60)[0]
    y_plot = y.astype(float).copy()
    ore_plot = ore.copy()
    for i in salti:
        y_plot = np.insert(y_plot, i + 1, np.nan)
        ore_plot = np.insert(ore_plot, i + 1, (ore[i] + ore[i + 1]) / 2)

    fig, ax = plt.subplots(figsize=(7.4, 3.2))

    for i in salti:
        ax.axvspan(ore[i], ore[i + 1], color=SABBIA, alpha=.22, zorder=0)
        ax.text((ore[i] + ore[i + 1]) / 2, .93,
                T('sospensione\n{} min',
                  'suspended\n{} min').format(
                      dec((t[i + 1] - t[i]) / 60, 0)),
                ha='center', va='top', fontsize=8, color=INK, zorder=5)

    ax.plot(ore_plot, y_plot, lw=.35, color=GRIGIO, zorder=1)
    ax.scatter(ore[sopra], y[sopra], s=3.5, color=ROSSO, zorder=2,
               label=T('finestre sopra soglia ({})',
                       'windows above threshold ({})'
                       ).format(int(sopra.sum())))
    ax.axhline(SOGLIA, color=INK, lw=.9, ls='--', zorder=3)

    if allarmi:
        ax.scatter(ore[allarmi], [1.05] * len(allarmi), marker='v', s=46,
                   color=BLU, zorder=4,
                   label=T('allarmi emessi ({})',
                       'alarms raised ({})').format(len(allarmi)))

    ax.set_xlim(0, ore.max())
    ax.set_ylim(0, 1.12)
    ax.set_yticks([0, .25, .5, .75, 1])
    ax.set_xlabel(T('ore dall\'inizio della sessione (orologio di sistema)',
                    'hours from the start of the session (system clock)'))
    ax.set_ylabel(T('punteggio', 'score'))
    titolo(ax, 'Finestre sopra soglia ed eventi, sulla stessa sessione',
           'Windows above threshold and events, same session', pad=8)
    virgola(ax, 'y')

    # la legenda sta SOTTO: dentro gli assi si sovrapporrebbe ai marcatori
    # degli allarmi, che stanno in alto per non confondersi con i punteggi
    ax.legend(loc='upper center', bbox_to_anchor=(.5, -.24), ncol=2,
              frameon=False, fontsize=8.5, handletextpad=.4,
              columnspacing=2.4)

    fattore = sopra.sum() / max(len(allarmi), 1)
    ax.text(ore.max(), 1.05,
            '  {}× '.format(dec(fattore, 1)),
            ha='right', va='center', fontsize=8.5, color=BLU, weight='bold')

    salva(fig, 'fig_sessione.png', dove, [os.path.basename(rel)], scheda={
        'mostra':
            'Cinque ore di esercizio continuo in casa: il punteggio di ogni '
            'finestra nel tempo, la soglia, le finestre che la superano, e i '
            'pochi allarmi che ne escono dopo l\'antirimbalzo.',
        'come_si_legge':
            'Le finestre sopra soglia sono visibilmente RAGGRUPPATE: quando '
            'il sistema si insospettisce lo fa per qualche secondo di fila, '
            'non una volta sola. La regola di decisione chiede cinque '
            'finestre consecutive e poi tace per trenta secondi, e cosi\' una '
            'raffica intera diventa UN allarme. E\' la differenza fra i due '
            'conteggi in legenda.',
        'numeri':
            'Su QUESTA sessione il rapporto fra finestre sopra soglia ed '
            'eventi vale {}: {} finestre sopra soglia diventano {} allarmi. '
            'Sull\'insieme delle sessioni il fattore vale {}, ed e\' quello '
            'riportato nel capitolo; qui se ne vede una sola, e una singola '
            'sessione non e\' l\'insieme. E\' il fattore che distingue un dato '
            'riportabile da uno che sovrastima di quasi due ordini di '
            'grandezza, ed e\' la ragione per cui i numeri di campo di questo '
            'lavoro sono sempre eventi e mai finestre.'.format(
                dec(fattore, 1), int(sopra.sum()), len(allarmi),
                fattore_aggregato()),
        'provenienza':
            'Una sessione domestica vera. Gli allarmi sono RICALCOLATI qui '
            'dai punteggi, non letti da eventi.csv, che contiene finestre '
            'sopra soglia e non eventi.',
    })
    print('     -> {} finestre, {} sopra soglia, {} allarmi, fattore {}'
          .format(len(y), int(sopra.sum()), len(allarmi), dec(fattore, 1)))


# =========================================================================
#  1. Le architetture
# =========================================================================
def fig_architetture(dove):
    nomi = [('gru', 'GRU'), ('lstm', 'LSTM'), ('cnn', 'CNN 1D'),
            ('transformer', 'Transformer'),
            ('grafo', T('Grafo', 'Graph')),
            ('foresta', T('Foresta', 'Random Forest'))]
    dati, fonti = [], []
    for chiave, etichetta in nomi:
        # `_L22` PRIMA della forma nuda, e l'ordine non e' arbitrario.
        # Le due forme sono due CAMPAGNE diverse sullo stesso nome di modello:
        # la nuda e' del 20 agosto su feature_v2 (218 riprese), `_L22` e' del
        # 9 settembre su feature_v5 (220 riprese, Delta t reale, integrali
        # ricalcolate). Il Capitolo 3 descrive v5, quindi la figura deve
        # leggere v5. Con l'ordine precedente cinque architetture venivano da
        # v2 e il grafo da v5, e la figura mescolava due campagne.
        for suffisso in ('_L22', ''):
            rel = 'addestramento/run_{}_tre_classi_DTW_cam1{}.json'.format(
                chiave, suffisso)
            d = carica(rel)
            if d is not None:
                break
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
            ax.text(1.005, y[i], mille(np_),
                    transform=ax.get_yaxis_transform(), va='center',
                    fontsize=8.5, color=GRIGIO)

    ax.set_yticks(y)
    ax.set_yticklabels(et)
    ax.set_xlabel(T('$F_2$ medio su dieci fold leave-one-subject-out',
                    'mean $F_2$ over ten leave-one-subject-out folds'))
    titolo(ax, 'F2 per architettura, LOSO su dieci soggetti',
           'F2 by architecture, LOSO over ten subjects')
    ax.text(1.005, 1.11, T('parametri', 'parameters'),
            transform=ax.transAxes,
            fontsize=8, color=GRIGIO, ha='left')
    ax.set_xlim(min(f2 - dv) - .04, max(f2 + dv) + .04)
    # margine in alto: l'etichetta della prima riga sta sopra il punto,
    # e senza questo finisce dentro al titolo
    ax.set_ylim(-.65, len(et) - .25)
    ax.grid(axis='x', color=CHIARO, linewidth=.7, zorder=0)
    ax.set_axisbelow(True)
    virgola(ax, 'x')

    salva(fig, 'fig_architetture.png', dove, fonti, scheda={
        'mostra':
            'Il valore di F2 di sei architetture, misurato con lo stesso '
            'identico protocollo: stesse finestre, stessi fold, stessa '
            'soglia, dieci soggetti in leave-one-subject-out. La barra e\' '
            'la media sui dieci fold, il segmento la dispersione fra '
            'soggetti. A destra di ciascuna barra e\' scritto il numero di '
            'parametri del modello.',
        'come_si_legge':
            'La banda grigia verticale e\' la dispersione fra soggetti della '
            'configurazione migliore. Serve da metro: un divario fra due '
            'architetture piu\' stretto della banda e\' piu\' piccolo della '
            'variabilita\' che si osserva cambiando persona, e non e\' '
            'distinguibile dal caso. Guardare quali barre cadono dentro la '
            'banda, non quale barra e\' la piu\' lunga.',
        'numeri':
            'La differenza fra la prima e l\'ultima architettura va letta '
            'insieme a EXP-013, che dice quanti soggetti servirebbero per '
            'dichiararla: 113 per separare GRU da LSTM, 26 per separare GRU '
            'da foresta. UP-Fall ne ha 17 in tutto.',
        'provenienza':
            'Dieci soggetti. Le sei run sono in risultati/addestramento/.',
    })


# =========================================================================
#  2. Le configurazioni in laboratorio, a dieci soggetti
# =========================================================================
def fig_configurazioni(dove):
    """Le configurazioni di grandezze sul piano mancate / falsi allarmi.

    Perche' non un grafico a barre dell'F2. I cinque valori stanno fra 0,898 e
    0,953: su un asse che parte da zero le barre sono indistinguibili, e l'F2
    comprime in un numero solo due errori che qui si muovono in modo diverso.
    Separandoli si vede che le aggiunte non fanno la stessa cosa --- l'altezza
    dal pavimento e gli integrali recuperano cadute mancate, i controesempi
    tagliano falsi allarmi --- e questo e' il motivo per cui la configurazione
    installata le tiene tutte.
    """
    from matplotlib.patches import FancyArrowPatch

    d = carica('laboratorio/run_10soggetti.json')
    if d is None:
        return

    per_chiave = {}
    for x in d['run']:
        per_chiave[(x['feature_set'], bool(x.get('controesempi')))] = x
    if len(per_chiave) < 5:
        return

    NOMI = {
        ('A3', False): (T('A3', 'A3'),
                        T('sola geometria centrata sul corpo',
                          'body-centric geometry only')),
        ('A3h', False): (T('A3h', 'A3h'),
                         T("+ altezza dal pavimento",
                           '+ height above the floor')),
        ('A3i', False): (T('A3i', 'A3i'),
                         T('+ grandezze integrali',
                           '+ integral features')),
        ('A3h', True): (T('A3h + contro', 'A3h + counter-ex.'), ''),
        ('A3i', True): (T('A3i + contro', 'A3i + counter-ex.'), ''),
    }

    fig, ax = plt.subplots(figsize=(7.4, 4.8))

    # le frecce, disegnate prima dei punti cosi' passano sotto
    def freccia(a, b, colore):
        xa, ya = per_chiave[a]['fp'], per_chiave[a]['fn']
        xb, yb = per_chiave[b]['fp'], per_chiave[b]['fn']
        ax.add_patch(FancyArrowPatch((xa, ya), (xb, yb), arrowstyle='-|>',
                                     mutation_scale=12, color=colore,
                                     lw=1.3, alpha=.55, zorder=2,
                                     shrinkA=11, shrinkB=11))

    for a, b in ((('A3', False), ('A3h', False)),
                 (('A3', False), ('A3i', False))):
        freccia(a, b, BLU)
    for a, b in ((('A3h', False), ('A3h', True)),
                 (('A3i', False), ('A3i', True))):
        freccia(a, b, ROSSO)

    for chiave, x in per_chiave.items():
        installata = chiave == ('A3i', True)
        ax.plot(x['fp'], x['fn'], marker='o',
                ms=13 if installata else 10,
                color=TEAL if installata else 'white',
                markeredgecolor=INK, markeredgewidth=1.6, zorder=4)
        nome, spiega = NOMI[chiave]
        testo = nome if not spiega else nome + '\n' + spiega
        # le due con i controesempi stanno a sinistra e in basso, dove
        # si accavallerebbero fra loro e con le note: si scrivono a sinistra
        # del proprio punto
        if chiave[1]:
            dx, dy, ha, va = -14, 0, 'right', 'center'
        elif chiave[0] == 'A3i':
            # sotto finirebbe sulle tacche dell'asse: va a destra
            dx, dy, ha, va = 15, 0, 'left', 'center'
        else:
            dx, dy, ha, va = 0, 20, 'center', 'bottom'
        ax.annotate(testo + '\n$F_2$ = ' + dec(x['f2']),
                    xy=(x['fp'], x['fn']),
                    xytext=(dx, dy), textcoords='offset points',
                    ha=ha, va=va,
                    fontsize=8.4, color=INK, linespacing=1.35, zorder=5)

    ax.set_xlabel(T('falsi allarmi (finestre)', 'false alarms (windows)'))
    ax.set_ylabel(T('cadute mancate (finestre)', 'missed falls (windows)'))
    titolo(ax,
           'Le due aggiunte non correggono lo stesso errore',
           'The two additions do not fix the same error')

    # che cosa fa ciascun colore, detto una volta sola
    ax.annotate(T("freccia blu: altezza dal pavimento\ne grandezze "
                  "integrali\nscendono: meno cadute mancate",
                  'blue arrow: height above the floor\nand integral '
                  'features\ngo down: fewer missed falls'),
                xy=(.025, .97), xycoords='axes fraction', fontsize=8.6,
                color=BLU, linespacing=1.5, va='top')
    ax.annotate(T("freccia rossa: controesempi domestici\nvanno a sinistra: "
                  "meno falsi allarmi",
                  'red arrow: domestic counter-examples\ngo left: fewer '
                  'false alarms'),
                xy=(.025, .74), xycoords='axes fraction', fontsize=8.6,
                color=ROSSO, linespacing=1.5, va='top')

    fp = [x['fp'] for x in per_chiave.values()]
    fn = [x['fn'] for x in per_chiave.values()]
    ax.set_xlim(min(fp) - 50, max(fp) + 30)
    ax.set_ylim(min(fn) - 9, max(fn) + 20)
    ax.grid(color=CHIARO, linewidth=.7, zorder=0)
    ax.set_axisbelow(True)
    for lato in ('top', 'right'):
        ax.spines[lato].set_visible(False)

    salva(fig, 'fig_configurazioni.png', dove,
          ['laboratorio/run_10soggetti.json'], scheda={
        'mostra':
            'Le cinque configurazioni di grandezze sul piano cadute mancate '
            'contro falsi allarmi, su dieci soggetti in leave-one-subject-out. '
            'Il punto pieno e\' la configurazione installata. Accanto a '
            'ciascun punto il suo F2.',
        'come_si_legge':
            'In basso a sinistra si sbaglia meno, su entrambi i conti. Le '
            'frecce blu sono le aggiunte di grandezza --- altezza dal '
            'pavimento, integrali --- e scendono: tolgono cadute mancate, da '
            '45 a 22 e a 14. Le frecce rosse sono i controesempi domestici e '
            'vanno a sinistra: tolgono falsi allarmi, da 150 a 124, e non '
            'cambiano di una sola unita\' le cadute mancate. Le due aggiunte '
            'agiscono su assi diversi, ed e\' la ragione per cui conviene '
            'tenerle entrambe.',
        'numeri':
            'La versione precedente di questa figura era un grafico a barre '
            'dell\'F2. I cinque valori stanno fra 0,898 e 0,953: su un asse '
            'che parte da zero le barre erano indistinguibili, e l\'F2 '
            'comprime in un numero solo due errori che qui si muovono in '
            'direzioni diverse.',
        'provenienza': 'Dieci soggetti, leave-one-subject-out.',
    })


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
    a1.set_xticklabels([D(e) for e in et])
    a1.set_ylim(0, max(f2 + dv) + .12)
    a1.set_ylabel('$F_2$')
    a1.set_title(T('Quanto riconosce', 'How much it detects'),
                 fontsize=10.5)
    a1.grid(axis='y', color=CHIARO, linewidth=.7, zorder=0)
    a1.set_axisbelow(True)
    virgola(a1, 'y')

    colori = [ROSSO if v > 1 else TEAL for v in diff]
    a2.bar(x, diff, width=.55, color=colori, alpha=.85, zorder=2)
    for i, v in enumerate(diff):
        a2.text(i, v + max(diff) * .04,
                dec(v, 2 if v < 1 else 1) + '%', ha='center',
                fontsize=9, fontweight='bold')
    a2.set_xticks(x)
    a2.set_xticklabels([D(e) for e in et])
    a2.set_ylim(0, max(diff) * 1.28 + .5)
    a2.set_ylabel(T('finestre in allarme', 'windows in alarm'))
    a2.set_title(T('Su una persona che si sdraia',
                   'On a person lying down'), fontsize=10.5)
    a2.grid(axis='y', color=CHIARO, linewidth=.7, zorder=0)
    a2.set_axisbelow(True)
    from matplotlib.ticker import FuncFormatter
    a2.yaxis.set_major_formatter(FuncFormatter(
        lambda v, _: (('{:g}'.format(v)).replace('.', ',')
                      if LINGUA == 'it' else '{:g}'.format(v)) + '%'))
    # una barra a zero non si vede: un trattino sulla base dichiara che
    # il valore e' stato misurato, non che manca
    for i, v in enumerate(diff):
        if v < max(diff) * .01:
            a2.plot([i - .275, i + .275], [v, v], color=TEAL,
                    linewidth=2.6, solid_capstyle='butt', zorder=4)

    TITOLI and fig.suptitle(
        T('Le tre definizioni del compito a confronto',
          'The three task definitions compared'),
                 fontsize=11.5, fontweight='bold', y=1.03)
    fig.tight_layout()
    salva(fig, 'fig_compiti.png', dove, ['compiti/foresta_DTW_cam1.json'], scheda={
        'mostra':
            'Le tre definizioni possibili del compito, a parita\' assoluta di '
            'tutto il resto. A sinistra quanto ciascuna riconosce (F2); a '
            'destra quante finestre manda in allarme su una persona che si '
            'sdraia volontariamente, cioe\' su un falso positivo.',
        'come_si_legge':
            'I tre compiti sono: riconoscere la TRANSIZIONE (l\'atto di '
            'cadere), riconoscere lo STATO (essere a terra), oppure accettare '
            'entrambi. Vanno letti i due pannelli INSIEME: il compito che '
            'riconosce di piu\' non e\' quello che sbaglia di meno, ed e\' '
            'esattamente il punto della figura.',
        'numeri':
            'Il compito «evento» e\' l\'unico che azzera i falsi allarmi sui '
            'distesi volontari, su 2.234 finestre. Distinguere due '
            'definizioni del compito richiede due soggetti; distinguere una '
            'GRU da una LSTM ne richiede centotredici.',
        'provenienza': 'Dieci soggetti, foresta sul sottoinsieme DTW.',
    })


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
        testo = dec(v, 1) + T('  eventi/h', '  events/h')
        if ril[i] is not None:
            testo += T('\n{} cadute su 5', '\n{} falls out of 5').format(ril[i])
        ax.text(i, v + max(ev) * .04, testo, ha='center',
                fontsize=9, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([D(e) for e in et])
    ax.set_ylabel(T('eventi di allarme per ora', 'alarm events per hour'))
    ax.set_ylim(0, max(ev) * 1.35)
    titolo(ax, 'Gli stessi tre compiti, in due abitazioni',
           'The same three tasks, in two homes')
    ax.grid(axis='y', color=CHIARO, linewidth=.7, zorder=0)
    ax.set_axisbelow(True)

    salva(fig, 'fig_compiti_casa.png', dove, ['campo/compiti_in_casa.json'], scheda={
        'mostra':
            'Gli stessi tre compiti della figura precedente, misurati pero\' '
            'in due abitazioni vere invece che sull\'archivio: eventi di '
            'allarme per ora, e quante cadute su cinque ciascuno rileva.',
        'come_si_legge':
            'L\'unita\' e\' l\'EVENTO e non la finestra sopra soglia: sulle '
            'stesse registrazioni le due grandezze differiscono di un fattore '
            '{}. La regola applicata e\' quella del sistema installato, '
            'cinque finestre consecutive sopra soglia e poi trenta secondi di '
            'silenzio.'.format(fattore_aggregato()),
        'numeri':
            'Il confronto con il laboratorio e\' il punto: la classifica dei '
            'tre compiti in casa non e\' quella che l\'archivio prevedeva. Il '
            'riferimento di letteratura per un sistema installato e\' 0,049 '
            'eventi/ora.',
        'provenienza':
            'Due abitazioni, dodici sessioni. Due case non sono un campione: '
            'indicano una direzione, non la misurano.',
    })


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
    ax.set_xlabel(T('$\\sigma$ del rumore, in frazione della lunghezza del torso',
                    '$\\sigma$ of the noise, as a fraction of torso length'))
    ax.set_ylabel('$F_2$')
    titolo(ax, 'F2 al crescere del rumore iniettato sui landmark',
           'F2 as injected landmark noise grows')
    virgola(ax)
    ax.legend(frameon=False, fontsize=9)
    ax.grid(color=CHIARO, linewidth=.7, zorder=0)
    ax.set_axisbelow(True)
    salva(fig, 'fig_rumore.png', dove, ['rumore/foresta_cam1.json'], scheda={
        'mostra':
            'Che cosa succede all\'F2 iniettando rumore gaussiano sulle '
            'coordinate dei landmark, a deviazione crescente. In ascissa la '
            'deviazione del rumore espressa in frazioni della lunghezza del '
            'torso, cosi\' da essere confrontabile fra persone di statura '
            'diversa; in ordinata l\'F2.',
        'come_si_legge':
            'La banda orizzontale e\' la dispersione fra soggetti. Se le '
            'curve restano dentro la banda, l\'effetto del rumore e\' piu\' '
            'piccolo della differenza che si osserva cambiando persona, e '
            'quindi non e\' l\'anello debole della catena.',
        'provenienza':
            'Dieci soggetti. Il rumore e\' SIMULATO e indipendente fra '
            'landmark: e\' un modello di rumore, non il rumore vero dello '
            'stimatore, che invece e\' correlato fra punti vicini e nel '
            'tempo. La figura dice quindi che il sistema regge il rumore '
            'indipendente, non che regga qualunque degrado della posa.',
    })


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
    ax.set_yticklabels([D(e) for e in et], fontsize=8.5)
    ax.set_xlabel(T('variazione di $F_2$ occludendo il gruppo (base {})',
                    'change in $F_2$ when the group is occluded (baseline {})'
                    ).format(dec(base)))
    titolo(ax, 'Variazione di F2 congelando gruppi di landmark',
           'Change in F2 when groups of landmarks are frozen', pad=16)
    ax.set_xlim(-largo * 1.35, largo * 1.35)
    ax.set_ylim(-.7, len(et) - .1)
    ax.grid(axis='x', color=CHIARO, linewidth=.7, zorder=1)
    ax.set_axisbelow(True)
    virgola(ax, 'x')

    salva(fig, 'fig_occlusioni.png', dove, ['occlusioni/foresta_DTW.json'], scheda={
        'mostra':
            'Di quanto cambia l\'F2 se si «congela» un gruppo di landmark, '
            'cioe\' se ne si tiene ferma la posizione all\'ultima nota, come '
            'accade quando un mobile ne nasconde una parte. Un gruppo per '
            'barra.',
        'come_si_legge':
            'Lo zero e\' la prestazione senza occlusione. A sinistra dello '
            'zero il sistema peggiora, a destra migliora. La banda grigia e\' '
            'la dispersione fra soggetti: una barra che non la raggiunge '
            'segnala un effetto piu\' piccolo della differenza fra due '
            'persone.',
        'numeri':
            'La perdita massima e\' sulle spalle e vale 0,020 di F2, contro '
            'una dispersione fra soggetti di 0,078: nessun gruppo di punti '
            'e\' critico. Non e\' il risultato che ci si aspettava.',
        'provenienza':
            'Dieci soggetti. L\'occlusione e\' SIMULATA con il punto '
            'congelato: le occlusioni da mobilio reale non sono annotate ne\' '
            'in UP-Fall ne\' in UR-Fall, e non sono misurate.',
    })


# =========================================================================
#  7. La lunghezza della finestra
# =========================================================================
def fig_finestra(dove):
    # La stessa base di `tab:finestra` e delle differenze appaiate: foresta su
    # feature_v5. Prima leggeva i quattro run GRU del 20 agosto su feature_v2,
    # e la figura contraddiceva la tabella che le stava accanto.
    dati, fonti = [], []
    d = carica(os.path.join('laboratorio', 'tabelle_v5.json'))
    if d is None:
        return
    for q in d['finestra']:
        dati.append((q['L'], q['durata_s'], q['f2'], q['dev']))
    fonti.append('laboratorio/tabelle_v5.json')
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
    ax.set_xticklabels([T('{}\n{} s', '{}\n{} s').format(l, dec(s, 1))
                        for l, s in zip(L, sec)])
    ax.set_xlabel(T('lunghezza della finestra, in campioni e in secondi',
                    'window length, in samples and in seconds'))
    ax.set_ylabel('$F_2$')
    virgola(ax, 'y')
    titolo(ax, 'F2 al variare della lunghezza della finestra',
           'F2 as the window length varies')
    ax.grid(color=CHIARO, linewidth=.7, zorder=0)
    ax.set_axisbelow(True)
    salva(fig, 'fig_finestra.png', dove, fonti, scheda={
        'mostra':
            'L\'F2 al variare della lunghezza della finestra di decisione: 22, '
            '28, 36 e 44 campioni, indicati sia in campioni sia in secondi, a '
            'parita\' di tutto il resto.',
        'come_si_legge':
            'L\'ipotesi da cui si partiva era che una finestra piu\' lunga '
            'aiutasse, perche\' 22 campioni sono 2,44 s mentre una caduta dura '
            'in mediana 3,11 s. Guardare se l\'andamento e\' MONOTONO: se non '
            'lo e\', la lunghezza non e\' la variabile che conta.',
        'numeri':
            'L\'ipotesi era sbagliata: nessuna differenza significativa e '
            'andamento non monotono. La spiegazione probabile e\' che la '
            'memoria effettiva non sia la finestra, perche\' ogni campione '
            'porta con se\' gli integrali accumulati su 31 fotogrammi.',
        'provenienza': 'Dieci soggetti, leave-one-subject-out.',
    })


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
    a1.text(1, y[0] + .7, T(' caso', ' chance'), color=ROSSO,
            fontsize=8.5, va='bottom')
    for i, v in enumerate(gua):
        a1.text(v + max(gua) * .02, y[i], dec(v, 1) + '×',
                va='center', fontsize=9, fontweight='bold')
    a1.set_yticks(y)
    a1.set_yticklabels([D(e) for e in et], fontsize=8.5)
    a1.set_xlim(0, max(gua) * 1.25)
    a1.set_title(T('Guadagno di PR-AUC sul caso',
                   'PR-AUC gain over chance'), fontsize=10.5)
    a1.grid(axis='x', color=CHIARO, linewidth=.7, zorder=0)
    a1.set_axisbelow(True)

    a2.barh(y, f2, height=.5, color=GRIGIO, alpha=.85, zorder=2)
    for i, v in enumerate(f2):
        a2.text(v + max(f2) * .02, y[i], dec(v), va='center', fontsize=9)
    a2.set_yticks(y)
    a2.set_yticklabels([])
    a2.set_xlim(0, max(f2) * 1.3)
    a2.set_title(T('$F_2$ sull’archivio esterno',
                   '$F_2$ on the external archive'), fontsize=10.5)
    a2.grid(axis='x', color=CHIARO, linewidth=.7, zorder=0)
    a2.set_axisbelow(True)
    virgola(a1, 'x')
    virgola(a2, 'x')

    TITOLI and fig.suptitle(
        T('Il trasferimento a un archivio registrato altrove',
          'Transfer to an archive recorded elsewhere'),
                 fontsize=11.5, fontweight='bold', y=1.03)
    fig.tight_layout()
    salva(fig, 'fig_esterno.png', dove, ['esterno/urfall_foresta_caduta.json'], scheda={
        'mostra':
            'Che cosa succede addestrando su un archivio e verificando su un '
            'altro, mai visto. A sinistra il guadagno di PR-AUC rispetto alla '
            'prevalenza, che e\' una misura indipendente dalla soglia; a '
            'destra l\'F2 con la soglia installata e con la soglia ritarata.',
        'come_si_legge':
            'Il pannello di sinistra e\' quello che decide, perche\' non '
            'dipende dalla soglia: dice se il modello ORDINA ancora le '
            'finestre. Se il guadagno crolla, non e\' un problema di '
            'taratura, e\' perdita reale della capacita\' di separare.',
        'numeri':
            'PR-AUC 0,990 sull\'archivio di addestramento, cioe\' 18,7 volte '
            'la prevalenza; 0,169 su quello mai visto, cioe\' 1,79 volte. La '
            'soglia scelta a posteriori sul dominio di destinazione e\' '
            'chiamata SOGLIA ORACOLO, e non e\' una prestazione ottenibile da '
            'chi installa il sistema, perche\' richiede le etichette del posto '
            'in cui lo si installa.',
        'provenienza': 'Addestrato su UP-Fall, verificato su UR-Fall.',
    })



# =========================================================================
#  9. Dimensione del modello   (CINQUE SOGGETTI)
# =========================================================================
#  Le due figure che seguono NON vengono dalle run a dieci soggetti. Leggono
#  `risultati/cinque_soggetti/`, e lo dichiarano dentro l'immagine: il
#  capitolo dei risultati riporta la stessa avvertenza accanto a entrambe.
#  Sono qui perche' le due misure non sono state ripetute, non perche' siano
#  equivalenti alle altre.

def avviso_5():
    return T('misura a cinque soggetti, non ripetuta a dieci',
             'measured on five subjects, not repeated on ten')


def _cinque(nome):
    p = os.path.join(RIS, 'cinque_soggetti', nome)
    return p if os.path.exists(p) else None


def fig_dimensione(dove):
    # dieci soggetti, prodotto da pipeline/dimensione_foresta.py.
    # Il file precedente, cinque_soggetti/exp017_rf_size.json, veniva
    # dall'impianto a cinque e nessuno script lo rigenerava.
    p = os.path.join(RIS, 'laboratorio', 'dimensione_foresta.json')
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
                ms=5, label=T('$F_2$ (barre: dispersione fra fold)',
                          '$F_2$ (bars: dispersion across folds)'))
    ax.plot(n[imax], f2[imax], 'o', ms=11, mfc='none', mec=ROSSO, mew=2)
    ax.annotate((T('{:g} alberi', '{:g} trees') + chr(10) + '$F_2$ {}')
                .format(n[imax], dec(f2[imax])),
                (n[imax], f2[imax]), textcoords='offset points',
                xytext=(6, 16), color=ROSSO, fontsize=8.5)
    ax.set_xscale('log')
    ax.set_xticks(n)
    ax.set_xticklabels([str(int(v)) for v in n])
    ax.set_xlabel(T('alberi della foresta', 'trees in the forest'))
    ax.set_ylabel('$F_2$', color=BLU)
    ax.tick_params(axis='y', colors=BLU)
    virgola(ax, 'y')

    ax2 = ax.twinx()
    ax2.plot(n, ms, 's--', color=SABBIA, lw=1.4, ms=4.5,
             label=T('latenza', 'latency'))
    ax2.set_ylabel(T('latenza per finestra [ms]',
                     'latency per window [ms]'), color=SABBIA)
    ax2.tick_params(axis='y', colors=SABBIA)
    ax2.spines['right'].set_visible(True)
    ax2.spines['right'].set_color(GRIGIO)
    virgola(ax2, 'y')

    titolo(ax,
           'Accuratezza e latenza al variare della dimensione'
           ' della foresta',
           'Accuracy and latency as the size of the forest varies',
           pad=12)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc='upper center',
              bbox_to_anchor=(0.5, -0.20), ncol=2,
              frameon=False, fontsize=8.5)
    salva(fig, 'fig_dimensione.png', dove, ['laboratorio/dimensione_foresta.json'], scheda={
        'mostra':
            'Due grandezze sullo stesso asse orizzontale, il numero di alberi '
            'della foresta: a sinistra l\'F2, a destra la latenza per '
            'finestra in millisecondi.',
        'come_si_legge':
            'Serve a scegliere una dimensione, non a mostrare un risultato. '
            'Si cerca il punto oltre il quale l\'F2 smette di salire mentre '
            'la latenza continua: la\' si ferma, ed e\' il motivo dei 50 '
            'alberi installati.',
        'provenienza':
            'Dieci soggetti, leave-one-subject-out su feature_v5, camera 1, '
            'dodici grandezze DTW, soglia 0,50. Prodotta da '
            'pipeline/dimensione_foresta.py. La latenza e\' misurata UNA '
            'FINESTRA ALLA VOLTA e su un solo processo, come fa il sistema '
            'installato, ma SUL CALCOLATORE: sulla board il Capitolo 5 '
            'riporta 39,04 ms per finestra.',
    })


# =========================================================================
#  10. Il punto di vista, distribuzione   (CINQUE SOGGETTI)
# =========================================================================

def fig_viewpoint_dist(dove):
    # Tre sorgenti in ordine di preferenza (EXP-020):
    #   1. dieci soggetti, uno stimatore per ripresa;
    #   2. cinque soggetti, uno stimatore per ripresa;
    #   3. cinque soggetti, UN SOLO stimatore per tutte e cinquanta le riprese
    #      --- porta lo stato del tracciatore da una all'altra (ISS-133), e
    #      resta solo perche' lo script deve girare dove gli altri non ci sono.
    # Il caso 1 e' l'unico che NON e' a cinque soggetti, quindi e' anche
    # l'unico in cui l'avviso in calce non va stampato.
    sorgente = os.path.join('laboratorio', 'escursione_viste_10sog.csv')
    p = os.path.join(RIS, sorgente)
    if not os.path.exists(p):
        for nome in ('exp013_camera_viewpoint_indipendente.csv',
                     'exp013_camera_viewpoint.csv'):
            p = _cinque(nome)
            if p is not None:
                sorgente = os.path.join('cinque_soggetti', nome)
                break
    if p is None or not os.path.exists(p):
        return
    dieci = 'laboratorio' in sorgente
    import csv
    righe = list(csv.DictReader(open(p, encoding='utf-8')))

    # una coppia per sequenza: stesso soggetto, stessa prova, stesso istante
    coppie = {}
    for r in righe:
        k = (r['subject'], r['activity'], r['trial'])
        coppie.setdefault(k, {})[int(r['camera'])] = (
            float(r['exc_2d']), r.get('salto_a', '') != '')
    coppie = {k: v for k, v in coppie.items() if 1 in v and 2 in v}

    # Le riprese in cui lo stimatore cambia persona non misurano l'escursione
    # del soggetto (ISS-134): restano nel grafico, perche' toglierle in
    # silenzio nasconderebbe che esistono, ma non entrano nelle medie.
    valide = [v for v in coppie.values() if not (v[1][1] or v[2][1])]
    perse = [v for v in coppie.values() if v[1][1] or v[2][1]]

    c1 = np.array([v[1][0] for v in valide])
    c2 = np.array([v[2][0] for v in valide])
    pari = int((c2 >= c1).sum())
    rapporto = c1.mean() / c2.mean()

    # Una tinta media, non pallida: le cinquanta linee sono il DATO, non uno
    # sfondo. Erano in CHIARO e la figura si leggeva come grigia.
    TRACCIA = '#7E9AAB'

    fig, ax = plt.subplots(figsize=(6.0, 4.8))

    # la soglia dei 60 gradi e' il criterio con cui la tabella del capitolo
    # conta le sequenze «informative»: senza il riferimento, il conteggio
    # 30 su 39 contro 8 su 39 non si vede nel grafico
    ax.axhline(60, color=SABBIA, lw=1.1, ls=(0, (6, 4)), zorder=0)
    ax.annotate(T('soglia 60', 'threshold 60') + grado_s(), (1.5, 61),
                ha='right', va='bottom',
                fontsize=8, color=SABBIA)

    for v in perse:
        ax.plot([0, 1], [v[1][0], v[2][0]], '--', lw=1.0, color=GRIGIO,
                alpha=.75, zorder=1)
        ax.plot([0, 1], [v[1][0], v[2][0]], 'x', ms=5, color=GRIGIO,
                alpha=.85, zorder=1)
    for a, b in zip(c1, c2):
        rov = b >= a
        ax.plot([0, 1], [a, b], '-', lw=2.0 if rov else 1.2,
                color=ROSSO if rov else TRACCIA, alpha=1 if rov else .55,
                zorder=4 if rov else 2)
        ax.plot([0, 1], [a, b], 'o', ms=4.5 if rov else 3.2,
                color=ROSSO if rov else TRACCIA, alpha=1 if rov else .55,
                zorder=4 if rov else 2)
    ax.plot([0, 1], [c1.mean(), c2.mean()], 'o-', color=BLU, lw=3.2, ms=9,
            zorder=6,
               label=T('media delle {} sequenze valide',
                       'mean of the {} valid sequences').format(len(c1)))
    ax.plot([], [], '-', color=TRACCIA, lw=1.2, alpha=.75,
            label=T('una caduta, vista dalle due telecamere',
                       'one fall, seen by both cameras'))
    if pari:
        ax.plot([], [], '-', color=ROSSO, lw=2.0,
                label=T('la vista rialzata osserva quanto la laterale',
                       'the raised view sees as much as the lateral one')
                      + (' ({})'.format(pari) if pari > 1 else ''))
    if perse:
        ax.plot([], [], 'x--', color=GRIGIO, lw=1.0, ms=5,
                label=T('soggetto perso dallo stimatore ({}), fuori dalle medie',
                       'subject lost by the estimator ({}), excluded from the means')
                      .format(len(perse)))

    for x, v in ((0, c1.mean()), (1, c2.mean())):
        ax.annotate(dec(v, 1) + grado_s(), (x, v), textcoords='offset points',
                    xytext=(-52 if x == 0 else 14, -5), color=BLU,
                    fontweight='bold', fontsize=11)
    # il rapporto fra le medie e' il numero che il testo cita: sta sulla
    # figura perche' e' un VALORE, non una conclusione
    ax.annotate(dec(rapporto, 2) + chr(215), (0.5, (c1.mean() + c2.mean()) / 2),
                textcoords='offset points', xytext=(0, 20), ha='center',
                color=BLU, fontweight='bold', fontsize=12,
                bbox=dict(fc='white', ec='none', pad=1.5))

    ax.set_xticks([0, 1])
    ax.set_xticklabels([T('Camera 1' + chr(10) + 'laterale',
                          'Camera 1' + chr(10) + 'lateral'),
                        T('Camera 2' + chr(10) + 'frontale rialzata',
                          'Camera 2' + chr(10) + 'raised frontal')])
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(0, 97)
    ax.set_ylabel(T('escursione dell' + APS + 'angolo del tronco [gradi]',
                    'trunk-angle excursion [degrees]'))
    titolo(ax,
           'Escursione dell' + AP + 'angolo del tronco, '
           'la stessa caduta vista dalle due telecamere',
           'Trunk-angle excursion, the same fall seen by both cameras',
           pad=12, fontsize=10.5)
    virgola(ax, 'y')
    ax.grid(axis='y', color=CHIARO, lw=.7, zorder=0)
    ax.set_axisbelow(True)
    if not dieci:
        ax.text(0.5, -0.20, avviso_5(), transform=ax.transAxes, ha='center',
                va='top', fontsize=8, color=GRIGIO, style='italic')
    ax.legend(frameon=False, loc='upper center', bbox_to_anchor=(.5, -.13),
              ncol=1, fontsize=8.5, handletextpad=.6, labelspacing=.35)

    salva(fig, 'fig_viewpoint_dist.png', dove,
          [sorgente.replace(os.sep, '/')], scheda={
        'mostra':
            'Una linea per ogni caduta, che unisce quanto la telecamera '
            'laterale ha visto ruotare il tronco (a sinistra) a quanto ne ha '
            'visto la frontale rialzata (a destra), sulla STESSA caduta, '
            'nello stesso istante. In blu la linea delle medie.',
        'come_si_legge':
            'Ogni linea che scende da sinistra a destra e\' una caduta in cui '
            'la vista rialzata ha osservato MENO di quella laterale: sono '
            'quasi tutte. In rosso l\'unica in cui non accade. Le linee '
            'tratteggiate con la croce sono le riprese in cui lo stimatore di '
            'posa ha perso il soggetto e si e\' agganciato a un\'altra '
            'persona: non misurano l\'escursione di chi cade e sono escluse '
            'dalle medie, ma restano disegnate perche\' toglierle in silenzio '
            'nasconderebbe che esistono. La riga orizzontale a 60 gradi e\' '
            'il criterio con cui il testo conta le sequenze informative.',
        'numeri':
            'La media da sola descrive male questo fenomeno, ed e\' il motivo '
            'per cui la figura mostra tutte le linee invece di due barre: le '
            'deviazioni valgono circa un terzo del valore medio sulla vista '
            'laterale e piu\' di due terzi su quella rialzata, e il rapporto '
            'calcolato sequenza per sequenza va da 0,98 a 7,37.',
        'provenienza':
            'Dieci soggetti, cinquanta riprese per due telecamere, uno '
            'stimatore di posa per ripresa. E\' una grandezza DESCRITTIVA: '
            'non entra in alcun addestramento, e i valori di F2 del capitolo '
            'non ne dipendono.',
        'didascalia':
            'Escursione dell\'angolo del tronco durante la caduta, misurata '
            'sulla stessa ripresa dalle due telecamere di UP-Fall. Ogni linea '
            'e\' una caduta; la linea spessa unisce le due medie. La vista '
            'rialzata comprime l\'escursione di un fattore {}: e\' '
            'l\'informazione geometrica su cui il sistema decide, e da quel '
            'punto di vista non c\'e\'. Escluse dalle medie le {} riprese in '
            'cui lo stimatore di posa passa a un\'altra persona '
            '(ISS-134).'.format(dec(rapporto, 2) + chr(215), len(perse)),
    })
    print('     -> {} coppie valide, rapporto {}, {} rovesciate, {} escluse'
          .format(len(c1), dec(rapporto, 2), pari, len(perse)))


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
    b1 = ax.bar(x - w / 2, fn, w, color=ROSSO, label=T('falsi negativi', 'false negatives'))
    b2 = ax.bar(x + w / 2, fp, w, color=BLU, label=T('falsi positivi', 'false positives'))
    for b in list(b1) + list(b2):
        ax.annotate(str(int(b.get_height())),
                    (b.get_x() + b.get_width() / 2, b.get_height()),
                    textcoords='offset points', xytext=(0, 3),
                    ha='center', fontsize=8.5)
    ax.set_xticks(x)
    ax.set_xticklabels([D(x) for x in nomi])
    ax.set_ylabel(T('finestre classificate male',
                    'misclassified windows'))
    titolo(ax, 'Falsi negativi e falsi positivi per configurazione',
           'False negatives and false positives by configuration')
    ax.legend(frameon=False, fontsize=8.5)
    ax.set_ylim(0, max(fp.max(), fn.max()) * 1.18)

    nota = ('Dalla configurazione di riferimento alla finale: '
            'falsi negativi {:.0f} -> {:.0f}, falsi positivi {:.0f} -> {:.0f}. '
            'Nessuno scambio.')
    ax.text(0.5, -0.24, nota.format(fn[0], fn[-1], fp[0], fp[-1]),
            transform=ax.transAxes, ha='center', va='top',
            fontsize=8.5, color=INK)
    salva(fig, 'fig_errori.png', dove, ['laboratorio/run_10soggetti.json'], scheda={
        'mostra':
            'I due tipi di errore separati, invece di un solo numero '
            'riassuntivo: per ogni configurazione, quante finestre di caduta '
            'sono state perse (falsi negativi) e quante finestre normali sono '
            'state scambiate per cadute (falsi positivi).',
        'come_si_legge':
            'Un F2 solo nasconde COME il modello sbaglia, e i due errori '
            'costano cose diverse: un falso negativo e\' una caduta non '
            'soccorsa, un falso positivo e\' un allarme di troppo. Guardare '
            'se passando da una configurazione all\'altra i due scendono '
            'INSIEME, oppure se uno scende perche\' l\'altro sale: nel secondo '
            'caso non e\' un miglioramento, e\' uno scambio.',
        'numeri':
            'Da A3 alla configurazione finale i falsi negativi passano da 45 '
            'a 14 e i falsi positivi da 172 a 124: in laboratorio scendono '
            'entrambi, quindi non c\'e\' scambio. Lo scambio compare solo in '
            'casa, ed e\' la tesi del capitolo sull\'ambiente reale.',
        'provenienza': 'Dieci soggetti, leave-one-subject-out.',
    })


# =========================================================================
#  Le tre configurazioni della vista, addestrando invece che descrivendo
# =========================================================================
#  La figura che mancava: il capitolo aveva la tabella con le tre righe e la
#  figura con la misura geometrica, e nessuna immagine del RISULTATO di
#  classificazione. Prodotta da pipeline/viste_incrociate.py.

def fig_viste(dove):
    d = carica(os.path.join('laboratorio', 'viste_incrociate_10sog.json'))
    if d is None:
        return
    righe = d['righe']
    nomi = [T('addestrata e verificata' + NL + 'su Camera 1',
              'trained and tested' + NL + 'on Camera 1'),
            T('addestrata su Camera 1' + NL + 'verificata su Camera 2',
              'trained on Camera 1' + NL + 'tested on Camera 2'),
            T('addestrata su Camera 1+2' + NL + 'verificata su Camera 2',
              'trained on Camera 1+2' + NL + 'tested on Camera 2'),
            # la quarta riga del file di risultato: mancava, ed e' la
            # ragione per cui questa figura non veniva prodotta
            T('addestrata e verificata' + NL + 'su Camera 2',
              'trained and tested' + NL + 'on Camera 2')]
    nomi = nomi[:len(righe)]
    f2 = np.array([r['aggregato']['fbeta_media'] for r in righe])
    dev = np.array([r['aggregato']['fbeta_dev'] for r in righe])
    fp = np.array([r['aggregato']['fp_tot'] for r in righe], float)
    fn = np.array([r['aggregato']['fn_tot'] for r in righe], float)
    y = np.arange(len(righe))[::-1]

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 3.1),
                                 gridspec_kw={'width_ratios': [1, 1.15]})

    # --- F2, con la dispersione fra soggetti accanto a ogni barra ---------
    # una sola grandezza, quindi una sola tinta; il rosso segnala la riga di
    # cui la figura parla, non una categoria diversa
    a1.barh(y, f2, height=.52, zorder=2,
            color=[ROSSO if i == 1 else BLU for i in range(len(f2))])
    a1.errorbar(f2, y, xerr=dev, fmt='none', ecolor=INK, elinewidth=1.1,
                capsize=3, zorder=4)
    for yy, v, e in zip(y, f2, dev):
        a1.text(v - .025, yy, dec(v), va='center', ha='right', fontsize=10,
                fontweight='bold', color='white', zorder=5)
        a1.text(v + e + .025, yy, '± ' + dec(e, 3), va='center', fontsize=8.5,
                color=GRIGIO)
    a1.set_yticks(y)
    a1.set_yticklabels([D(x) for x in nomi], fontsize=8.5)
    a1.set_xlim(0, 1.05)
    a1.set_xlabel('$F_2$')
    a1.set_title(T('$F_2$, con la dispersione fra soggetti',
                   '$F_2$, with the dispersion across subjects'),
                 fontsize=10)
    a1.grid(axis='x', color=CHIARO, lw=.7, zorder=0)
    a1.set_axisbelow(True)
    virgola(a1, 'x')

    # --- i due errori, separati (punto 5 dell'email del relatore) ---------
    h = .26
    a2.barh(y + h / 2 + .02, fp, height=h, color=SABBIA, zorder=2,
            label=T('falsi allarmi', 'false alarms'))
    a2.barh(y - h / 2 - .02, fn, height=h, color=ROSSO, zorder=2,
            label=T('cadute non viste', 'missed falls'))
    for yy, v in zip(y, fp):
        a2.text(v + 60, yy + h / 2 + .02, mille(v),
                va='center', fontsize=8.5)
    for yy, v in zip(y, fn):
        a2.text(v + 60, yy - h / 2 - .02, mille(v),
                va='center', fontsize=8.5)
    a2.set_yticks(y)
    a2.set_yticklabels([])
    a2.set_xlim(0, max(fp.max(), fn.max()) * 1.22)
    a2.set_xlabel(T('finestre', 'windows'))
    a2.set_title(T('I due errori, separati',
                   'The two errors, separated'), fontsize=10)
    a2.grid(axis='x', color=CHIARO, lw=.7, zorder=0)
    a2.set_axisbelow(True)
    a2.legend(frameon=False, fontsize=8.5, loc='lower right')

    fig.subplots_adjust(wspace=.08)
    salva(fig, 'fig_viste.png', dove,
          ['laboratorio/viste_incrociate_10sog.json'], scheda={
        'mostra':
            'Che cosa succede alla decisione quando cambia il punto di vista: '
            'a sinistra F2 con la dispersione fra soggetti, a destra i due '
            'errori contati separatamente. Tre configurazioni: la vista '
            'laterale con se stessa, il trasferimento alla vista rialzata, e '
            'l\'addestramento su entrambe.',
        'come_si_legge':
            'La barra dell\'errore sull\'F2 e\' la DISPERSIONE FRA '
            'SOGGETTI: una differenza piu\' piccola di quella non e\' '
            'distinguibile dall\'aver pescato una persona invece di '
            'un\'altra. Il divario fra la prima e la seconda riga e\' molte '
            'volte piu\' grande, quindi e\' un effetto vero.',
        'numeri':
            'I falsi allarmi della seconda riga sono l\'ordine di grandezza '
            'che il capitolo commenta: trasferire alla vista rialzata non '
            'peggiora un po\' tutto, fa esplodere un errore solo.',
        'provenienza':
            'Dieci soggetti, dataset riestratto (feature_v3), foresta '
            'casuale, soglia 0,50 dichiarata a priori, leave-one-subject-out. '
            'Prodotta da pipeline/viste_incrociate.py.',
        'didascalia':
            'Effetto del punto di vista sulla decisione, su dieci soggetti. '
            'A sinistra F2 con la dispersione fra soggetti; a destra falsi '
            'allarmi e cadute non viste, contati separatamente come richiesto '
            'al punto 5 dell\'email del relatore.',
    })


# =========================================================================
#  Il divario fra i due archivi, scomposto
# =========================================================================
#  Il contributo originale della sezione sul trasferimento: non «il sistema
#  non trasferisce», ma quanta parte del fallimento sarebbe rimediabile da
#  chi installa il sistema e quanta no.

def fig_dominio(dove):
    d = carica(os.path.join('campo', 'pr_auc_allineato.json'))
    if d is None:
        return
    dom = {x['dominio'].split('(')[0].strip(): x for x in d['domini']}
    dentro = dom.get('UP-Fall')
    fuori = dom.get('UR-Fall')
    if dentro is None or fuori is None:
        return

    f2_dentro = dentro['f2_soglia_upfall']
    f2_fuori = fuori['f2_soglia_upfall']
    f2_oracolo = fuori['f2_soglia_oracolo']
    taratura = f2_oracolo - f2_fuori
    perdita = f2_dentro - f2_oracolo
    divario = f2_dentro - f2_fuori

    # Tre misure affiancate, nell'ordine in cui la sezione le racconta.
    # La precedente era una barra impilata: mostrava un valore e due
    # differenze come se fossero tre lunghezze omogenee.
    etichette = [
        T('archivio di addestramento' + NL + 'soglia dichiarata',
          'training archive' + NL + 'declared threshold'),
        T('archivio nuovo' + NL + 'soglia dichiarata',
          'new archive' + NL + 'declared threshold'),
        T('archivio nuovo' + NL + 'soglia oracolo',
          'new archive' + NL + 'oracle threshold'),
    ]
    valori = [f2_dentro, f2_fuori, f2_oracolo]
    colori = [BLU, ROSSO, SABBIA]

    fig, ax = plt.subplots(figsize=(8.8, 4.5))
    x = np.arange(3)
    ax.bar(x, valori, width=.56, color=colori, zorder=3)

    for i, v in enumerate(valori):
        ax.text(i, v + .022, dec(v), ha='center', va='bottom',
                fontsize=13, fontweight='bold', color=INK)

    # i due passi, con quanto costano e se siano recuperabili
    def passo(i, j_, quota, testo, colore):
        alto = max(valori[i], valori[j_]) + quota
        ax.annotate('', xy=(j_, alto), xytext=(i, alto),
                    arrowprops=dict(arrowstyle='<->', color=colore, lw=1.5))
        ax.text((i + j_) / 2.0, alto + .018, testo, ha='center', va='bottom',
                fontsize=9.5, color=colore, fontweight='bold')

    passo(0, 1, .10,
          T('il divario complessivo: $-%s$' % dec(divario),
            'the full gap: $-%s$' % dec(divario)),
          ROSSO)
    passo(1, 2, .30,
          T('recuperabile spostando la soglia: $+%s$' % dec(taratura),
            'recovered by moving the threshold: $+%s$' % dec(taratura)),
          SABBIA)

    # cio' che resta anche con la soglia migliore possibile
    ax.plot([-.45, 2.45], [f2_dentro, f2_dentro], ls=':', lw=1.2,
            color=BLU, zorder=2)
    ax.annotate('', xy=(2.32, f2_dentro), xytext=(2.32, f2_oracolo),
                arrowprops=dict(arrowstyle='<->', color=INK, lw=1.5))
    ax.text(2.42, (f2_dentro + f2_oracolo) / 2.0,
            T('non recuperabile:' + NL + '$-%s$' % dec(perdita),
              'not recoverable:' + NL + '$-%s$' % dec(perdita)),
            ha='left', va='center', fontsize=9.5, color=INK,
            fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(etichette, fontsize=9.5)
    ax.set_ylabel('$F_2$')
    ax.set_ylim(0, 1.42)
    ax.set_xlim(-.55, 3.05)
    ax.grid(axis='y', color=CHIARO, lw=.7, zorder=0)
    ax.set_axisbelow(True)
    virgola(ax, 'y')
    titolo(ax,
           'Il divario fra l' + APS + 'archivio di addestramento e '
           'un archivio mai visto, scomposto',
           'The gap between the training archive and an unseen one,'
           ' decomposed',
           fontsize=10.5, pad=10)

    salva(fig, 'fig_dominio.png', dove, ['campo/pr_auc_allineato.json'],
          scheda={
        'mostra':
            'Il divario fra la prestazione nell\'archivio di addestramento e '
            'quella su un archivio mai visto, diviso nelle due parti di cui e\' '
            'fatto: quella che si recupererebbe ritarando la soglia, e quella '
            'che nessuna soglia recupera.',
        'come_si_legge':
            'Il segmento blu e\' cio\' che il sistema ottiene davvero '
            'sull\'archivio nuovo, con la soglia con cui e\' stato '
            'schierato. Il segmento sabbia e\' quanto si guadagnerebbe '
            'scegliendo la soglia migliore CONOSCENDO le risposte: e\' la '
            'soglia oracolo, e chi installa il sistema non la possiede. Il '
            'segmento rosso e\' cio\' che resta, cioe\' capacita\' di '
            'separare che si e\' persa e che nessuna taratura restituisce.',
        'numeri':
            'Le due parti sono quasi uguali. E\' la lettura coerente con la '
            'PR-AUC: 1,79 volte il caso sull\'archivio nuovo contro 18,7 in '
            'dominio.',
        'provenienza':
            'Dieci soggetti su UP-Fall, verifica su UR-Fall rietichettato. '
            'Prodotta da campo/pr_auc_allineato.json.',
        'didascalia':
            'Scomposizione del divario fra i due archivi. Il valore in '
            'dominio e\' {}, quello sull\'archivio mai visto {}; la soglia '
            'oracolo porta a {}. Circa meta\' del divario e\' taratura e '
            'meta\' perdita reale della capacita\' di separare.'.format(
                dec(f2_dentro), dec(f2_fuori), dec(f2_oracolo)),
    })
    print('     -> divario {}, taratura {}%, perdita {}%'
          .format(dec(divario), dec(100 * taratura / divario, 0),
                  dec(100 * perdita / divario, 0)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dove', default=DEFAULT)
    ap.add_argument('--lingua', default='it', choices=('it', 'en'))
    ap.add_argument('--titoli', action='store_true',
                    help="stampa il titolo dentro l'immagine; "
                         "per la tesi il titolo sta nella didascalia")
    a = ap.parse_args()

    global LINGUA, TITOLI
    LINGUA, TITOLI = a.lingua, a.titoli
    os.makedirs(a.dove, exist_ok=True)

    print('risultati da : {}'.format(RIS))
    print('figure verso : {}\n'.format(a.dove))
    for f in (fig_errori, fig_dimensione, fig_viewpoint_dist,
              fig_viste, fig_dominio,
              fig_architetture, fig_configurazioni, fig_compiti,
              fig_sessione, fig_stanza, fig_dtw,
              fig_compiti_casa, fig_rumore, fig_occlusioni, fig_finestra,
              fig_esterno):
        try:
            f(a.dove)
        except Exception as e:                      # una figura non blocca le altre
            print('  {:<34} FALLITA: {}'.format(f.__name__, e))
    print('\nfatto')


if __name__ == '__main__':
    main()
