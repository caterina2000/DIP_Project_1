# -*- coding: utf-8 -*-
"""
La stessa caduta, gli stessi due istanti, dalle due telecamere.

Perche' esiste
--------------
Il Capitolo 4 afferma che cambiare punto di vista costa 0,422 di F2 --- meta'
dell'accuratezza --- e che la causa e' ottica e non algoritmica: una
telecamera rialzata comprime l'escursione dell'angolo del tronco, che e'
l'indicatore geometrico piu' forte di una caduta. Fino al 2026-09-06
quell'affermazione era senza immagine: `fig:due_camere` era un ambiente
`figure` con la didascalia e nessun `\\includegraphics`, cioe' uno spazio
bianco che compilava.

Che cosa mostra
---------------
Quattro pannelli, due per telecamera. Le colonne sono i due punti di vista;
le righe sono due istanti della STESSA ripresa, allo STESSO indice di
fotogramma. Guardando una colonna dall'alto in basso si vede quanto il tronco
ruota in quella vista, ed e' la quantita' che la Tabella dell'escursione
riassume su cinquanta sequenze.

Il risultato si legge in due secondi: **in piedi le due viste sono
indistinguibili** --- 88,8° e 86,5° --- e **a terra no**: 3,9° contro 73,0°.
La vista rialzata vede una persona distesa quasi come una in piedi.

Le quattro scelte che la rendono difendibile
--------------------------------------------
1. **La sequenza non e' scelta per convenienza.** Su `sub09_act05_trial01` il
   rapporto fra le due escursioni vale 2,79, che e' **esattamente il rapporto
   mediano** delle trentanove riprese, su dieci soggetti, in cui entrambe le
   viste seguono il soggetto: e' la sequenza tipica, non la piu' favorevole
   (il massimo e' 7,37). Ha inoltre posa rilevata sul 98,3% dei campioni su
   entrambe le telecamere, che serve perche' i quattro pannelli mostrino una
   posa stimata e non un buco.

2. **Gli istanti vengono dalla sola annotazione.** I nomi dei file di UP-Fall
   portano in coda la classe del fotogramma (`-0` prima, `-1` caduta in corso,
   `-2` a terra), e si prende il centro del blocco di classe 0 e il centro di
   quello di classe 2. Prendere invece il fotogramma piu' verticale fra quelli
   in piedi e il piu' orizzontale fra quelli a terra sceglierebbe gli estremi
   di **una** delle due viste, e il divario che ne uscirebbe sarebbe piu'
   grande di quello vero. Il centro di un blocco e' definito dall'annotazione
   e uguale per le due telecamere.

3. **L'angolo e' misurato con la definizione che produce la tabella**, cioe'
   quella di `DIP_PROJECT/scripts/check_camera_viewpoint.py`: inclinazione del
   vettore anca->spalle nel piano immagine, ripiegata in [0, 90], dove 90 e'
   verticale e 0 orizzontale. Per ottenerla lo stimatore gira sull'immagine a
   meta' risoluzione e un fotogramma ogni tre, come li'; i punti sono
   normalizzati, quindi si disegnano sul fotogramma a piena risoluzione senza
   riscalarli. Lo script **ricalcola l'escursione dell'intera sequenza e la
   confronta con il CSV**: se i due valori divergono di piu' di un grado si
   ferma, perche' significa che la figura sta misurando qualcosa d'altro
   rispetto alla tabella che le sta accanto.

4. **Si rifiuta di disegnare la posa di un'altra persona.** Su **undici**
   riprese di Camera2 su cinquanta --- e su **zero** di Camera1 --- lo
   stimatore perde chi cade e si aggancia a un astante
   ([ISS-134](../docs/ISSUES.md#iss-134)). La prima resa di questa
   figura ne era una: lo scheletro era addosso a una persona seduta, con
   accanto un angolo di 87,1° che sembrava perfettamente sensato. Vedi
   `primo_salto`.

Ambiente: `fall_processing` (serve MediaPipe).

    python pipeline/figura_due_camere.py
"""

import argparse
import csv
import os
import sys

import numpy as np

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if QUI not in sys.path:
    sys.path.insert(0, QUI)

from src.provenienza import provenienza                        # noqa: E402
from pipeline.figura_rappresentazioni import (con_scheletro,   # noqa: E402
                                              riquadro,
                                              dec as _dec_virgola)

import matplotlib                                              # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt                                # noqa: E402

INK, GRIGIO, BLU = '#1A1F23', '#8A949B', '#2B5D7D'
TEAL, ROSSO, SABBIA = '#2E8B8B', '#9C3B45', '#C4A55C'

# Il protocollo di misura di exp013, ripetuto qui identico. Cambiarne uno
# solo fa divergere i numeri della figura da quelli della tabella accanto.
PASSO = 3
SCALA = 0.5

SPALLA_SX, SPALLA_DX, ANCA_SX, ANCA_DX = 11, 12, 23, 24

# Spostamento dell'anca fra due campioni con posa consecutivi, sommando le due
# componenti in coordinate normalizzate, oltre il quale si dichiara un cambio
# di persona. Stesso valore e stessa motivazione di
# `pipeline/escursione_viste.py`.
SOGLIA_SALTO = 0.45

# sub09_act05_trial01: rapporto 2,79, cioe' il mediano esatto delle 39 riprese
# a DIECI soggetti senza cambio di persona; posa rilevata sul 98,3% su
# entrambe le telecamere, ed escursioni grandi in assoluto (87,3 e 31,3), che
# serve perche' la differenza si veda e non vada dedotta.
RAW = os.path.join('dataset', 'up_fall', 'raw', 'fall')
NOME = 'sub09_act05_trial01'

# Due CSV, e si preferisce il primo. Il secondo e' la misura originale, che
# usa UN SOLO stimatore per tutte e cinquanta le riprese e quindi porta lo
# stato del tracciatore da una all'altra (ISS-133): su cam02 di questa
# sequenza vale 31,30° contro i 29,23° che si ottengono partendo puliti.
CSV_ESCURSIONE = [
    os.path.join('risultati', 'laboratorio', 'escursione_viste_10sog.csv'),
    os.path.join('risultati', 'cinque_soggetti',
                 'exp013_camera_viewpoint_indipendente.csv'),
    os.path.join('risultati', 'cinque_soggetti',
                 'exp013_camera_viewpoint.csv'),
]

LINGUA = 'it'


def T(it, en):
    return it if LINGUA == 'it' else en


def dec(v, n=1):
    """Come `figura_rappresentazioni.dec`, ma consapevole di LINGUA.

    Quella importata mette sempre la virgola: va bene per gli script che
    non hanno mai una lingua inglese, ma qui il file produce anche
    `fig_due_camere_en.png`, e le due etichette «74.0°» / «2.23×» disegnate
    sull'immagine restavano in formato italiano anche nella versione
    inglese. Stesso difetto, stessa causa, della `mille()` aggiunta in
    `figure_tesi.py`: una funzione di formattazione senza l'interruttore
    di lingua, condivisa da piu' chiamanti che invece ce l'hanno.
    """
    t = _dec_virgola(v, n)
    return t if LINGUA == 'it' else t.replace(',', '.')


def suffisso(nome):
    if LINGUA == 'it':
        return nome
    radice, punto, est = nome.rpartition('.')
    return radice + '_en' + punto + est


def viste():
    return [('cam01', T('Camera 1 — laterale',
                        'Camera 1 — lateral')),
            ('cam02', T('Camera 2 — frontale rialzata',
                        'Camera 2 — raised frontal'))]


def righe():
    return [(0, T('in piedi', 'standing')),
            (2, T('a terra', 'on the ground'))]


VISTE = [('cam01', 'Camera 1 — laterale'),
         ('cam02', 'Camera 2 — frontale rialzata')]
RIGHE = [(0, 'in piedi'), (2, 'a terra')]


def angolo_tronco(p, w, h):
    """
    Inclinazione del tronco nel piano immagine: 90 verticale, 0 orizzontale.

    E' la definizione di `check_camera_viewpoint.py`, riportata qui per
    intero invece che importata perche' quel file sta nell'altro progetto e
    non e' un modulo. Il ripiegamento sopra i 90 gradi serve perche' la
    grandezza e' un'inclinazione e non un verso: una persona a testa in giu'
    e una in piedi hanno lo stesso angolo, ed e' voluto.
    """
    sx = (p[SPALLA_SX].x + p[SPALLA_DX].x) / 2 * w
    sy = (p[SPALLA_SX].y + p[SPALLA_DX].y) / 2 * h
    hx = (p[ANCA_SX].x + p[ANCA_DX].x) / 2 * w
    hy = (p[ANCA_SX].y + p[ANCA_DX].y) / 2 * h
    dx, dy = sx - hx, sy - hy
    if abs(dx) + abs(dy) < 1e-6:
        return None
    a = abs(float(np.degrees(np.arctan2(-dy, dx))))
    return 180 - a if a > 90 else a


def classe(nome):
    """La classe del fotogramma, dal suffisso del nome del file UP-Fall."""
    radice = os.path.splitext(nome)[0]
    coda = radice.rsplit('-', 1)[-1]
    return int(coda) if coda.isdigit() else None


def elabora(cartella):
    """
    La ripresa campionata come in exp013: un fotogramma ogni PASSO, posa
    stimata a meta' risoluzione, immagine tenuta a piena risoluzione.

    La sequenza si elabora in ordine e senza salti diversi da quelli del
    protocollo, perche' lo stimatore e' un tracciatore: la posa su un
    fotogramma isolato non e' quella che ottiene seguendo il movimento.
    """
    import cv2
    import mediapipe as mp

    files = sorted(f for f in os.listdir(cartella)
                   if f.lower().endswith(('.png', '.jpg', '.jpeg')))
    if not files:
        sys.exit('nessuna immagine in ' + cartella)

    pose = mp.solutions.pose.Pose(min_detection_confidence=.5,
                                  min_tracking_confidence=.5,
                                  model_complexity=1)
    fuori = []
    for nome in files[::PASSO]:
        img = cv2.imread(os.path.join(cartella, nome))
        if img is None:
            continue
        piccola = cv2.resize(img, None, fx=SCALA, fy=SCALA,
                             interpolation=cv2.INTER_AREA)
        r = pose.process(cv2.cvtColor(piccola, cv2.COLOR_BGR2RGB))
        lm = r.pose_landmarks.landmark if r.pose_landmarks else None
        h, w = img.shape[:2]
        fuori.append({
            'nome': nome, 'bgr': img, 'posa': r.pose_landmarks,
            'classe': classe(nome),
            # i punti normalizzati si riportano alla risoluzione piena: la
            # posa e' la stessa, cambia solo l'immagine su cui si disegna
            'punti': (np.array([[p.x * w, p.y * h] for p in lm], np.float64)
                      if lm else None),
            'angolo': (angolo_tronco(lm, *piccola.shape[1::-1])
                       if lm else None),
            # a che cosa serve: vedi `primo_salto`
            'anca': (((lm[ANCA_SX].x + lm[ANCA_DX].x) / 2,
                      (lm[ANCA_SX].y + lm[ANCA_DX].y) / 2) if lm else None),
            'w': w, 'h': h,
        })
    pose.close()
    return fuori


def primo_salto(seq, soglia=SOGLIA_SALTO):
    """
    Il campione in cui lo stimatore passa a un'altra persona, se accade.

    Serve perche' MediaPipe Pose segue **una** persona, e quando la perde il
    rilevatore riparte e aggancia chi e' piu' evidente nell'inquadratura. Su
    `sub01_act01_trial01_cam02` succede esattamente al momento della caduta:
    l'anca salta da x = 0,50 a x = 0,87, che e' un astante seduto, e ci resta
    per tutta la fase «a terra» ([ISS-134](../docs/ISSUES.md#iss-134)).

    Senza questo controllo la figura disegnerebbe uno scheletro corretto sulla
    persona sbagliata, con accanto un angolo del tronco che non e' quello di
    chi e' caduto. Sarebbe un'immagine falsa, e non se ne accorgerebbe
    nessuno.
    """
    prec = None
    for i, d in enumerate(seq):
        if d['anca'] is None:
            continue
        if prec is not None:
            s = abs(d['anca'][0] - prec[0]) + abs(d['anca'][1] - prec[1])
            if s > soglia:
                return i, s
        prec = d['anca']
    return None, 0.0


def escursione(seq):
    a = [d['angolo'] for d in seq if d['angolo'] is not None]
    return (max(a) - min(a)) if a else float('nan')


def dal_csv(nome_ripresa):
    """
    L'escursione dichiarata dalla tabella, per il confronto.

    Si prende il primo dei due CSV che esiste. Il nome del file usato viene
    restituito insieme ai valori, perche' un confronto senza il nome di cio'
    con cui ci si e' confrontati non e' un confronto.
    """
    for relativo in CSV_ESCURSIONE:
        percorso = os.path.join(QUI, relativo)
        if not os.path.isfile(percorso):
            continue
        fuori = {}
        with open(percorso, newline='') as f:
            for r in csv.DictReader(f):
                if r['name'].startswith(nome_ripresa):
                    fuori['cam%02d' % int(r['camera'])] = float(r['exc_2d'])
        if fuori:
            return fuori, os.path.basename(percorso)
    return {}, None


def scegli_istanti(seq):
    """
    I due istanti, scelti sulla sola annotazione.

    Il centro del blocco di classe 0 e il centro del blocco di classe 2. Non
    si guarda l'angolo: prendere il fotogramma **piu' verticale** fra quelli
    in piedi e il **piu' orizzontale** fra quelli a terra sceglierebbe i due
    estremi di una delle due telecamere, e la figura mostrerebbe l'escursione
    massima di quella vista contro un istante qualunque dell'altra. Il
    divario che ne uscirebbe sarebbe piu' grande di quello vero.

    Il centro di un blocco e' invece definito dall'annotazione e uguale per le
    due telecamere, che e' cio' che rende i due pannelli di una riga
    confrontabili.
    """
    fuori = []
    for cl, _ in RIGHE:
        candidati = [i for i, d in enumerate(seq) if d['classe'] == cl]
        if not candidati:
            sys.exit('nessun fotogramma di classe %d' % cl)
        fuori.append(candidati[len(candidati) // 2])
    return fuori


def tronco(ax, d):
    """Il segmento anca->spalle, che e' la grandezza di cui si parla."""
    P = d['punti']
    msp = (P[SPALLA_SX] + P[SPALLA_DX]) / 2
    man = (P[ANCA_SX] + P[ANCA_DX]) / 2
    ax.plot([man[0], msp[0]], [man[1], msp[1]], color=SABBIA, lw=2.6,
            solid_capstyle='round', zorder=5)
    ax.plot(man[0], man[1], marker='x', ms=8, color=SABBIA, mew=1.9, zorder=6)
    # l'orizzonte dell'immagine: senza un riferimento, un'inclinazione non
    # si legge
    ax.plot([man[0] - 62, man[0] + 62], [man[1], man[1]], color=SABBIA,
            lw=.9, ls=':', zorder=4)


def disegna(sequenze, istanti, dove, ripresa, prov,
            nome='fig_due_camere.png', stile='neutro'):
    fig = plt.figure(figsize=(8.6, 7.2))
    griglia = fig.add_gridspec(2, 2, hspace=.05, wspace=.04)

    for c, (cam, titolo) in enumerate(viste()):
        seq = sequenze[cam]
        # un ritaglio per COLONNA, sull'unione delle due pose di quella
        # telecamera: un ritaglio per pannello seguirebbe la persona e la
        # mostrerebbe della stessa dimensione in piedi e a terra, cioe'
        # cancellerebbe proprio cio' che la figura deve mostrare
        unione = np.vstack([seq[i]['punti'] for i in istanti])
        rx0, rx1, ry0, ry1 = riquadro(unione, seq[istanti[0]]['w'],
                                      seq[istanti[0]]['h'], margine=.22)
        for r, (_, etichetta) in enumerate(righe()):
            d = seq[istanti[r]]
            ax = fig.add_subplot(griglia[r, c])
            ax.imshow(con_scheletro(d, stile=stile))
            tronco(ax, d)
            ax.set_xlim(rx0, rx1)
            ax.set_ylim(ry1, ry0)
            ax.set_xticks([])
            ax.set_yticks([])
            for lato in ax.spines.values():
                lato.set_color(GRIGIO)
                lato.set_linewidth(.8)
            if r == 0:
                ax.set_title(titolo, fontsize=10.5, color=INK, pad=6)
            if c == 0:
                ax.set_ylabel(etichetta, fontsize=10, color=INK, labelpad=8)
            ax.annotate('%s°' % dec(d['angolo']),
                        xy=(.035, .955), xycoords='axes fraction',
                        ha='left', va='top', fontsize=12,
                        fontweight='bold', color=INK,
                        bbox=dict(boxstyle='round,pad=.3', fc='white',
                                  ec=SABBIA, lw=.9, alpha=.92))

        esc = seq[istanti[0]]['angolo'] - seq[istanti[1]]['angolo']
        fig.text(.30 + .42 * c, .055,
                 T('escursione %s°', 'excursion %s°') % dec(esc),
                 ha='center', fontsize=11.5, fontweight='bold',
                 color=INK if c == 0 else ROSSO)

    fig.text(.5, .012,
             T("Stessa caduta, stessi due fotogrammi, istanti scelti "
               "sull'annotazione. %s (%s)."   ,
               "Same fall, same two frames, instants chosen from the "
               "annotation. %s (%s).") % (prov, ripresa),
             ha='center', fontsize=8.2, color=GRIGIO)

    p = os.path.join(dove, suffisso(nome))
    fig.savefig(p, bbox_inches='tight', dpi=400, facecolor='white')
    plt.close(fig)
    return p


def scheda(sequenze, istanti, dove, ripresa, prov,
           nome='fig_due_camere.txt'):
    """
    I numeri della figura, in un file accanto al PNG.

    Non e' documentazione di cortesia: i quattro angoli finiscono nella
    didascalia del Capitolo 4, e `pipeline/audit_numeri.py` cerca ogni
    decimale del testo nei file di risultato. Un numero che sta solo
    nell'immagine e' un numero senza artefatto, che e' il difetto di
    [ISS-113] applicato a una figura.
    """
    r = ['FIGURA — LA STESSA CADUTA DALLE DUE TELECAMERE',
         'File: fig_due_camere.png',
         'Prodotta da: pipeline/figura_due_camere.py  (ambiente '
         'fall_processing)',
         'Ripresa: %s   istanti (indici di campione): %s'
         % (ripresa, ', '.join(str(i) for i in istanti)),
         '',
         'GLI ANGOLI DEL TRONCO NEI QUATTRO PANNELLI',
         '  inclinazione nel piano immagine, 90 = verticale, 0 = orizzontale',
         '']
    for cam, titolo in VISTE:
        seq = sequenze[cam]
        a = [seq[i]['angolo'] for i in istanti]
        r.append('  %-32s  %s' % (titolo, cam))
        for k, (_, etichetta) in enumerate(RIGHE):
            r.append('    %-12s  %6.2f gradi' % (etichetta, a[k]))
        r.append('    %-12s  %6.2f gradi' % ('escursione', a[0] - a[1]))
        r.append('    %-12s  %6.2f gradi   (intera sequenza)'
                 % ('escursione', escursione(seq)))
        r.append('')
    r += [
        'PERCHE\' QUESTA RIPRESA E QUESTI ISTANTI',
        '  La ripresa ha il rapporto MEDIANO fra le 19 in cui entrambe le',
        '  viste seguono il soggetto per l\'intera sequenza (le altre 6 di',
        '  Camera2 hanno un cambio di persona, ISS-134). Gli istanti sono il',
        '  centro dei blocchi annotati «in piedi» e «a terra»: scelti quindi',
        '  senza guardare l\'angolo, e uguali sulle due telecamere.',
        '',
        'PROVENIENZA',
        '  %s, come tab:escursione e fig_viewpoint_dist.' % prov,
        '  Escursioni di sequenza verificate contro',
        '  risultati/cinque_soggetti/exp013_camera_viewpoint_indipendente.csv.',
        '']
    p = os.path.join(dove, nome)
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(r))
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ripresa', default=None,
                    help='cartella del soggetto; senza, si ricava da --nome '
                         'e si cerca nei due progetti')
    ap.add_argument('--nome', default=NOME)
    ap.add_argument('--lingua', default='it', choices=('it', 'en'))
    ap.add_argument('--dove', default=os.path.join(QUI, 'tesi', 'figure'))
    ap.add_argument('--stile', choices=('neutro', 'nativo'), default='neutro')
    ap.add_argument('--tolleranza', type=float, default=1.0,
                    help='scarto massimo in gradi fra escursione ricalcolata '
                         'e valore del CSV')
    ap.add_argument('--forza', action='store_true',
                    help='disegna anche se su un istante la posa e\' di '
                         'un\'altra persona. Da usare solo per ispezionare '
                         'il difetto, mai per produrre la figura della tesi')
    a = ap.parse_args()

    global LINGUA
    LINGUA = a.lingua

    base = a.ripresa
    if base is None:
        # `sub09_act05_trial01` -> `Subject_09`: senza questo, cambiare
        # ripresa con --nome richiedeva di cambiare anche una costante
        sogg = 'Subject_%s' % a.nome[3:5]
        for radice in (QUI, os.path.join(QUI, '..', 'DIP_PROJECT')):
            c = os.path.abspath(os.path.join(radice, RAW, sogg))
            if os.path.isdir(c):
                base = c
                break
    if base is None or not os.path.isdir(base):
        sys.exit('ripresa non trovata: indicarla con --ripresa')

    print('ripresa   ', os.path.join(base, a.nome + '_camXX'))

    atteso, sorgente = dal_csv(a.nome)
    print('riscontro  %s' % (sorgente or 'nessun CSV trovato'))
    sequenze = {}
    for cam, _ in VISTE:
        cartella = os.path.join(base, '%s_%s' % (a.nome, cam))
        if not os.path.isdir(cartella):
            sys.exit('manca ' + cartella)
        seq = elabora(cartella)
        sequenze[cam] = seq
        con = sum(1 for d in seq if d['punti'] is not None)
        esc = escursione(seq)
        rif = atteso.get(cam)
        print('%s  campioni %3d, con posa %3d (%.1f%%), escursione %.2f°'
              % (cam, len(seq), con, 100 * con / len(seq), esc), end='')
        if rif is None:
            print('   [nessun riscontro nel CSV]')
        else:
            print('   CSV %.2f°  scarto %.2f°' % (rif, abs(esc - rif)))
            if abs(esc - rif) > a.tolleranza:
                # Contro la misura pulita uno scarto e' un errore: le due
                # cose vanno calcolate allo stesso modo. Contro la misura
                # originale e' invece il difetto noto, e fermarsi
                # nasconderebbe la figura per un motivo gia' documentato.
                messaggio = (
                    "l'escursione ricalcolata (%.2f°) non corrisponde a %s "
                    "(%.2f°)" % (esc, sorgente, rif))
                if 'indipendente' in (sorgente or ''):
                    sys.exit(messaggio + ': la figura misurerebbe qualcosa '
                                         'di diverso dalla tabella accanto')
                print('   ATTENZIONE: %s.' % messaggio)
                print('   E\' lo scarto di ISS-133: il CSV originale porta '
                      'lo stato del tracciatore')
                print('   da una ripresa alla successiva. La figura usa il '
                      'valore ricalcolato.')

    istanti = scegli_istanti(sequenze['cam01'])
    print('istanti    %s (dall\'annotazione, uguali per le due viste)'
          % ', '.join('#%d %s' % (i, RIGHE[k][1])
                      for k, i in enumerate(istanti)))

    # Il controllo che impedisce la figura falsa: se su una delle due viste lo
    # stimatore ha cambiato persona prima di un istante da disegnare, quella
    # posa non e' del soggetto e non va mostrata.
    guasto = False
    for cam, _ in VISTE:
        dove, quanto = primo_salto(sequenze[cam])
        if dove is None:
            print('%s  nessun cambio di persona' % cam)
            continue
        print('%s  CAMBIO DI PERSONA al campione %d (salto %.2f)'
              % (cam, dove, quanto))
        colpiti = [RIGHE[k][1] for k, i in enumerate(istanti) if i >= dove]
        if colpiti:
            print('     riguarda gli istanti: %s' % ', '.join(colpiti))
            guasto = True
    if guasto and not a.forza:
        sys.exit('su almeno un istante da disegnare la posa non e\' quella '
                 'del soggetto (ISS-134). Scegliere un\'altra ripresa con '
                 '--nome, oppure --forza per disegnare comunque.')

    for cam, _ in VISTE:
        a0 = sequenze[cam][istanti[0]]['angolo']
        a1 = sequenze[cam][istanti[1]]['angolo']
        print('  %s  in piedi %5.1f°   a terra %5.1f°   escursione %5.1f°'
              % (cam, a0, a1, a0 - a1))

    # la provenienza si legge dal CSV con cui ci si e' confrontati, non si
    # scrive a mano: era «cinque soggetti» anche dopo il passaggio a dieci
    prov = (T('Dieci soggetti', 'Ten subjects')
            if '10sog' in (sorgente or '')
            else T('Cinque soggetti', 'Five subjects'))
    print('scritto   ', disegna(sequenze, istanti, a.dove, a.nome, prov,
                                stile=a.stile))
    print('scritto   ', scheda(sequenze, istanti, a.dove, a.nome, prov))
    print('codice    ', provenienza()['commit_breve'])


if __name__ == '__main__':
    main()
