# -*- coding: utf-8 -*-
"""
Una figura per rappresentazione: quali landmark usa, sopra una posa vera.

Tre file --- `fig_landmark_a1`, `_a2`, `_a3` --- ciascuno con due pannelli: il
fotogramma RGB del dataset a sinistra, e a destra la posa stimata con i punti
di quella rappresentazione evidenziati e numerati con il loro indice MediaPipe.
Dentro la figura non c'e' testo descrittivo: le didascalie stanno nel capitolo.

Che cosa e' calcolato e che cosa e' disegnato
---------------------------------------------
Tutto quello che si vede viene dai dati, non da una mano che traccia. Vale la
pena essere espliciti, elemento per elemento:

  lo scheletro     MediaPipe gira sul fotogramma e restituisce 33 landmark con
                   coordinate normalizzate in [0,1]; qui vengono moltiplicate
                   per larghezza e altezza e disegnate con matplotlib. Le ossa
                   sono `mp.solutions.pose.POSE_CONNECTIONS`, la lista di
                   collegamenti di MediaPipe, non una scelta di chi disegna.

  l'ellisse di A1  autovettori e autovalori della covarianza dei sette punti,
                   la stessa decomposizione di `MotoreGeometrico._ellisse`.
                   Viene disegnata a DUE deviazioni standard, cosi' avvolge la
                   persona: a una sola coprirebbe il solo tronco. Il fattore e'
                   di resa e non tocca le grandezze, perche' allungamento e
                   inclinazione sono un rapporto e una direzione, invarianti
                   per scala. La freccia resta a UNA deviazione standard: la
                   sua semilunghezza E' `A1_asse_mag`, quindi nella stessa
                   figura si leggono la misura e l'ingombro.

  il tronco di A2  il vettore fra punto medio delle anche e punto medio delle
                   spalle, e l'angolo con la verticale del riferimento.

  L e l'origine    di A3, calcolati come in `MotoreGeometrico.a3`.

  il pavimento     la retta che esce da `MotoreGeometrico._pavimento`: si
                   elaborano i fotogrammi della ripresa con il motore vero, lui
                   accumula il bordo inferiore dell'ingombro quando la persona
                   e' eretta e dopo almeno `PAV_MINIME` osservazioni ci adatta
                   una retta ai minimi quadrati. La retta disegnata e' quella,
                   letta da `_pav_retta`. Si noti che nel dataset la stessa
                   retta viene stimata su TUTTE le riprese di una telecamera,
                   mentre qui le osservazioni vengono dalle riprese passate a
                   `--pavimento`: la pendenza e' dello stesso tipo, i
                   coefficienti non sono identici. Il conteggio delle
                   osservazioni finisce nella scheda .txt accanto alla figura.

Da dove vengono gli indici
--------------------------
PUNTI_ELLISSE, NASO, SPALLA_*, ANCA_*, GINOCCHIO_* e CAVIGLIA_* sono importati
da `src/geometry.py`, cioe' dallo stesso modulo che calcola le feature: se un
giorno una rappresentazione cambiasse i suoi punti, la figura cambierebbe con
lei. B non ha figura --- e' la rappresentazione abbandonata nella fase
preliminare e non vive piu' in questo progetto.

Il fotogramma
-------------
Si sceglie da solo. Fra i candidati di una ripresa in piedi prende quello in
cui i landmark usati sono piu' visibili e l'ingombro e' piu' verticale.

Uso:
    python pipeline/figura_landmark.py
    python pipeline/figura_landmark.py --lingua en
    python pipeline/figura_landmark.py --solo a3
"""

import argparse
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Ellipse, FancyArrowPatch, Rectangle

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, QUI)

import cv2
import mediapipe as mp

from src.geometry import (MotoreGeometrico, NASO, SPALLA_SX, SPALLA_DX,
                          ANCA_SX, ANCA_DX, GINOCCHIO_SX, GINOCCHIO_DX,
                          CAVIGLIA_SX, CAVIGLIA_DX, PUNTI_ELLISSE)

PUNTI_A2 = [NASO, SPALLA_SX, SPALLA_DX, ANCA_SX, ANCA_DX]
PUNTI_A3 = [NASO, SPALLA_SX, SPALLA_DX, ANCA_SX, ANCA_DX,
            GINOCCHIO_SX, GINOCCHIO_DX, CAVIGLIA_SX, CAVIGLIA_DX]

ADL = os.path.join('dataset', 'up_fall', 'raw', 'adl', 'Subject_09')
RIPRESA = os.path.join(ADL, 'sub09_act07_trial01_cam01')
# le riprese da cui il motore raccoglie le osservazioni del pavimento: stessa
# telecamera, persona in piedi. Servono almeno PAV_MINIME osservazioni erette.
PAVIMENTO = [os.path.join(ADL, 'sub09_act06_trial01_cam01'),
             os.path.join(ADL, 'sub09_act07_trial01_cam01')]

# I colori sono scelti per stare sopra la fotografia, non sulla carta bianca.
# Lo sfondo delle riprese e' un pavimento grigio scuro e la persona indossa un
# giubbotto rosso: un rosso mattone spariva sul giubbotto e un verde scuro sul
# pavimento. Qui si usano tinte sature e piu' chiare che, con l'alone bianco
# di `osso`, si staccano da entrambi. Hanno anche luminosita' diverse fra
# loro, quindi restano distinguibili stampate in scala di grigi.
BLU = '#1565c0'
BLU_CHIARO = '#64b5f6'
GRIGIO = '#90a4ae'
ROSSO = '#d81b60'          # magenta, per non confondersi col giubbotto rosso
VERDE = '#00897b'          # verde-acqua, si stacca dal pavimento
ARANCIO = '#ef6c00'

TITOLI = {
    'it': {'foto': 'Fotogramma RGB', 'a1': 'A1 — sagoma',
           'a2': 'A2 — world landmark', 'a3': 'A3 — riferimento sul corpo'},
    'en': {'foto': 'RGB frame', 'a1': 'A1 — silhouette',
           'a2': 'A2 — world landmarks', 'a3': 'A3 — body-centred frame'},
}


# --------------------------------------------------------------- la posa

def candidati(cartella, quanti=24):
    """Indici di fotogramma distribuiti sulla ripresa, non i primi in fila:
    i primi sono quelli che il tracciatore ha appena iniziato a seguire."""
    nomi = sorted(n for n in os.listdir(cartella)
                  if n.lower().endswith(('.png', '.jpg', '.jpeg')))
    if not nomi:
        return []
    passo = max(1, len(nomi) // quanti)
    return [(k, os.path.join(cartella, nomi[k]))
            for k in range(passo, len(nomi), passo)]


def scegli(cartella):
    """Il fotogramma piu' eretto e piu' visibile fra i candidati.

    Punteggio = visibilita' media dei punti usati x quanto l'ingombro e'
    verticale. La verticalita' conta perche' su una persona eretta i nove
    punti di A3 restano separati e le altezze relative si leggono."""
    usati = sorted(set(PUNTI_ELLISSE) | set(PUNTI_A3))
    meglio = None
    with mp.solutions.pose.Pose(static_image_mode=True, model_complexity=2,
                                min_detection_confidence=0.5) as pose:
        for k, perc in candidati(cartella):
            img = cv2.imread(perc)
            if img is None:
                continue
            h, w = img.shape[:2]
            r = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            if not r.pose_landmarks:
                continue
            lm = r.pose_landmarks.landmark
            vis = float(np.mean([lm[i].visibility for i in usati]))
            xs = np.array([lm[i].x for i in usati]) * w
            ys = np.array([lm[i].y for i in usati]) * h
            larg = xs.max() - xs.min()
            if larg <= 1:
                continue
            p = vis * min((ys.max() - ys.min()) / larg, 4.0)
            if meglio is None or p > meglio[0]:
                meglio = (p, k, perc, img, lm)
    return meglio


def stima_pavimento(cartelle, tetto=500):
    """La retta del pavimento, calcolata dal motore vero.

    Si elaborano i fotogrammi con `MotoreGeometrico.a3`, che chiama
    `_pavimento`: lui decide da se' quando la persona e' eretta, accumula il
    bordo inferiore dell'ingombro e dopo `PAV_MINIME` osservazioni adatta la
    retta. Qui non si calcola niente --- si legge `_pav_retta` alla fine.

    Nel dataset le osservazioni vengono da TUTTE le riprese di una telecamera;
    qui da quelle passate in `cartelle`. Il tipo di stima e' lo stesso, i
    coefficienti no: la scheda accanto alla figura lo dichiara."""
    motore = MotoreGeometrico()
    n = 0
    with mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1,
                                min_detection_confidence=0.5,
                                min_tracking_confidence=0.5) as pose:
        for cartella in cartelle:
            if not os.path.isdir(cartella):
                continue
            nomi = sorted(f for f in os.listdir(cartella)
                          if f.lower().endswith(('.png', '.jpg', '.jpeg')))
            for nome in nomi:
                if n >= tetto:
                    break
                img = cv2.imread(os.path.join(cartella, nome))
                if img is None:
                    continue
                h, w = img.shape[:2]
                r = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                if r.pose_landmarks:
                    motore.a3(r.pose_landmarks.landmark, w, h, 1.0 / 18.0)
                n += 1
    pronto, oss = motore.pavimento_pronto()
    return (motore._pav_retta if pronto else None), oss, n


# ------------------------------------------------------------- disegno

def osso(ax, P, a, b, colore, lw, zorder, alpha=1.0):
    """Un segmento con alone bianco sotto.

    Serve perche' lo scheletro sta sopra la fotografia: sul pavimento scuro
    una linea grigia sparirebbe, sulla maglietta rossa una linea rossa pure."""
    ax.plot([P[a, 0], P[b, 0]], [P[a, 1], P[b, 1]], color=colore, lw=lw,
            zorder=zorder, alpha=alpha, solid_capstyle='round',
            path_effects=[pe.withStroke(linewidth=lw + 2.0, foreground='white',
                                        alpha=0.85)])


def collo(ax, P, colore, lw, zorder, alpha=1.0):
    """Il segmento dal naso al punto medio delle spalle.

    Questo NON viene da MediaPipe. In `POSE_CONNECTIONS` non esiste alcun arco
    fra i punti del viso e le spalle: il grafo ha un gruppo per la testa e uno
    per il corpo, e i due non si toccano. Disegnato cosi' com'e', lo scheletro
    ha la testa che galleggia staccata dal busto.

    Il segmento e' quindi un'aggiunta di chi disegna, e va detto. Non
    introduce pero' nulla di inventato: il punto medio delle spalle e' lo
    stesso che A2 e A3 usano come estremo superiore del tronco, quindi la
    linea coincide con una grandezza che la pipeline calcola davvero."""
    sh = (P[SPALLA_SX] + P[SPALLA_DX]) / 2.0
    ax.plot([P[NASO, 0], sh[0]], [P[NASO, 1], sh[1]], color=colore, lw=lw,
            zorder=zorder, alpha=alpha, solid_capstyle='round',
            path_effects=[pe.withStroke(linewidth=lw + 2.0, foreground='white',
                                        alpha=0.85)])


def scheletro(ax, P, vis, evidenzia, colore, indici=True):
    """I 33 landmark sopra la fotografia: in chiaro quelli non usati da questa
    rappresentazione, a colori quelli usati, con l'indice MediaPipe accanto.

    Le ossa sono POSE_CONNECTIONS di MediaPipe, non una scelta di chi disegna.
    L'unica eccezione e' il collo: vedi `collo`.

    Un punto che lo stimatore dichiara poco visibile viene reso piu' pallido:
    e' informazione che il motore geometrico non usa ma il lettore deve
    vedere.

    `indici=False` disegna lo scheletro SENZA i numeri. Serve dove la figura
    spiega una costruzione geometrica invece di dire quali punti si usano: li'
    gli indici sono rumore. Il valore predefinito lascia il comportamento
    di prima."""
    for a, b in mp.solutions.pose.POSE_CONNECTIONS:
        osso(ax, P, a, b, GRIGIO, 1.1, 1)
    collo(ax, P, GRIGIO, 1.1, 1)
    ax.scatter(P[:, 0], P[:, 1], s=11, c=GRIGIO, zorder=2, linewidths=0.6,
               edgecolors='white')

    ev = list(evidenzia)
    for a, b in mp.solutions.pose.POSE_CONNECTIONS:
        if a in ev and b in ev:
            osso(ax, P, a, b, colore, 1.8, 3, alpha=0.95)
    if NASO in ev and SPALLA_SX in ev and SPALLA_DX in ev:
        collo(ax, P, colore, 1.8, 3, alpha=0.95)
    for i in ev:
        ax.scatter([P[i, 0]], [P[i, 1]], s=68, c=colore, zorder=5,
                   linewidths=1.0, edgecolors='white',
                   alpha=0.55 + 0.45 * min(float(vis[i]), 1.0))
    if indici:
        etichette(ax, P, ev, colore)


def etichette(ax, P, ev, colore, passo=30.0, dx=26.0):
    """Gli indici, spinti fuori dal corpo e separati fra loro.

    Senza la separazione i punti che cadono alla stessa quota --- anca e
    ginocchio su una figura eretta --- si sovrappongono. Si ordinano per quota
    e si spinge in giu' chi e' troppo vicino al precedente, un lato per volta."""
    cx = float(P[ev, 0].mean())
    lati = {1: [], -1: []}
    for i in ev:
        lati[1 if P[i, 0] >= cx else -1].append(i)
    for verso, punti in lati.items():
        punti = sorted(punti, key=lambda j: P[j, 1])
        quote, y = [], None
        for i in punti:
            y = float(P[i, 1]) if y is None else max(float(P[i, 1]), y + passo)
            quote.append(y)
        # la passata sopra spinge solo in giu': su un corpo orizzontale i
        # punti stanno quasi tutti alla stessa quota e la colonna di etichette
        # sfonda il bordo inferiore. Si ricentra sullo span originale, cosi'
        # meta' vanno in su e meta' in giu'.
        if quote:
            scarto = (float(np.mean(quote))
                      - float(np.mean([P[i, 1] for i in punti])))
            quote = [q - scarto for q in quote]
        for i, y in zip(punti, quote):
            ax.annotate(str(i), (P[i, 0], P[i, 1]),
                        xytext=(float(P[i, 0]) + verso * dx, y),
                        ha='left' if verso > 0 else 'right', va='center',
                        fontsize=11, fontweight='bold', color=colore, zorder=7,
                        arrowprops=dict(arrowstyle='-', color=colore, lw=0.8,
                                        alpha=0.55, shrinkA=1, shrinkB=4),
                        bbox=dict(boxstyle='round,pad=0.18', fc='white',
                                  ec=colore, lw=0.9, alpha=0.95))


def ellisse_a1(ax, P):
    """L'ellisse di `MotoreGeometrico._ellisse`, a una deviazione standard.

    I semiassi sono le radici degli autovalori della covarianza dei sette
    punti, cioe' esattamente `A1_asse_mag` e `A1_asse_min`. Non sono gonfiati
    per farla sembrare una sagoma: quella e' la grandezza che A1 misura."""
    p = P[PUNTI_ELLISSE].astype(np.float64)
    c = p.mean(axis=0)
    val, vec = np.linalg.eigh(np.cov((p - c).T))
    o = np.argsort(val)[::-1]
    val, vec = val[o], vec[:, o]
    mag = float(np.sqrt(max(val[0], 0.0)))
    minore = float(np.sqrt(max(val[1], 0.0)))
    ang = float(np.degrees(np.arctan2(vec[1, 0], vec[0, 0])))
    # L'ellisse si disegna a DUE deviazioni standard: a una sola coprirebbe il
    # solo tronco e non si leggerebbe come sagoma. Il fattore e' di sola resa,
    # e non tocca le grandezze --- allungamento e inclinazione sono rapporti e
    # direzioni, invarianti per scala. La freccia resta a UNA deviazione
    # standard, cioe' la sua semilunghezza E' `A1_asse_mag`: nella stessa
    # figura si vedono cosi' la misura e l'ingombro.
    K = 2.0
    for riempi in (True, False):
        ax.add_patch(Ellipse(c, 2 * K * mag, 2 * K * minore, angle=ang,
                             fill=riempi,
                             fc=BLU_CHIARO if riempi else 'none', ec=BLU,
                             lw=0 if riempi else 1.9, alpha=0.22 if riempi else 1,
                             ls='-' if riempi else '--',
                             zorder=0 if riempi else 4))
    d = vec[:, 0] * mag
    ax.annotate('', xy=tuple(c + d), xytext=tuple(c - d),
                arrowprops=dict(arrowstyle='<->', color=BLU, lw=1.8))
    ax.scatter([c[0]], [c[1]], s=48, marker='x', c=BLU, zorder=6, lw=2.2)
    return mag, minore, ang


def tronco_a2(ax, P):
    hip = (P[ANCA_SX] + P[ANCA_DX]) / 2.0
    sh = (P[SPALLA_SX] + P[SPALLA_DX]) / 2.0
    L = float(np.linalg.norm(sh - hip))
    ax.add_patch(FancyArrowPatch(tuple(hip), tuple(sh), color=ROSSO, lw=2.6,
                                 arrowstyle='-|>', mutation_scale=16, zorder=6))
    ax.plot([hip[0], hip[0]], [hip[1], hip[1] - L * 1.18], color=ARANCIO,
            lw=1.7, ls=':', zorder=4)
    ax.annotate(r'$\theta$', (hip[0] + 9, hip[1] - L * 0.82), fontsize=15,
                color=ARANCIO, fontweight='bold', ha='left', va='center',
                zorder=8, path_effects=[pe.withStroke(linewidth=3.2, foreground='white')])
    ax.scatter([hip[0]], [hip[1]], s=130, marker='o', facecolors='white',
               edgecolors=ROSSO, lw=2.1, zorder=7)
    ax.annotate('O', (hip[0], hip[1]), fontsize=10.5, color=ROSSO,
                fontweight='bold', ha='center', va='center',
                zorder=8, path_effects=[pe.withStroke(linewidth=3.2, foreground='white')])
    return float(np.degrees(np.arctan2(sh[0] - hip[0], hip[1] - sh[1])))


def riferimento_a3(ax, P, retta, x0, x1):
    hip = (P[ANCA_SX] + P[ANCA_DX]) / 2.0
    sh = (P[SPALLA_SX] + P[SPALLA_DX]) / 2.0
    gin = (P[GINOCCHIO_SX] + P[GINOCCHIO_DX]) / 2.0
    cav = (P[CAVIGLIA_SX] + P[CAVIGLIA_DX]) / 2.0
    L = float(np.linalg.norm(sh - hip))

    ax.add_patch(FancyArrowPatch(tuple(hip), tuple(sh), color=VERDE, lw=2.4,
                                 arrowstyle='<|-|>', mutation_scale=12,
                                 zorder=6))
    ax.annotate(r'$L$', ((hip[0] + sh[0]) / 2 - 14, (hip[1] + sh[1]) / 2),
                fontsize=14, color=VERDE, fontweight='bold', ha='right',
                va='center',
                zorder=8, path_effects=[pe.withStroke(linewidth=3.2, foreground='white')])
    for p in (P[NASO], gin, cav):
        ax.plot([hip[0], p[0]], [p[1], p[1]], color=VERDE, lw=1.1, ls=':',
                zorder=3)
        ax.plot([hip[0], hip[0]], [hip[1], p[1]], color=VERDE, lw=1.1, ls=':',
                zorder=3)
    ax.scatter([hip[0]], [hip[1]], s=130, marker='o', facecolors='white',
               edgecolors=VERDE, lw=2.1, zorder=7)
    ax.annotate('O', (hip[0], hip[1]), fontsize=10.5, color=VERDE,
                fontweight='bold', ha='center', va='center',
                zorder=8, path_effects=[pe.withStroke(linewidth=3.2, foreground='white')])

    if retta is not None:
        a, c = retta
        xs = np.array([x0, x1], np.float64)
        ax.plot(xs, a * xs + c, color=ARANCIO, lw=2.0, ls='-.', zorder=3)
        # l'altezza del bacino su quella retta: e' A3_h_pavimento, x L
        ax.plot([hip[0], hip[0]], [hip[1], a * hip[0] + c], color=ARANCIO,
                lw=1.4, ls=':', zorder=3)
        return float((a * hip[0] + c - hip[1]) / L)
    return None


# --------------------------------------------------------------- figura

def una(nome_r, punti, colore, img, P, vis, titolo_foto, titolo, dove, nome,
        retta=None, sfondo='foto'):
    mx = 0.17 * (P[:, 0].max() - P[:, 0].min()) + 48
    my = 0.20 * (P[:, 1].max() - P[:, 1].min()) + 38
    h, w = img.shape[:2]
    x0, x1 = max(P[:, 0].min() - mx, 0), min(P[:, 0].max() + mx, w)
    y0, y1 = max(P[:, 1].min() - my, 0), min(P[:, 1].max() + my, h)

    larghezza = 3.1
    fig, (sx, dx) = plt.subplots(
        1, 2, figsize=(2 * larghezza, larghezza * (y1 - y0) / (x1 - x0) + 0.55))
    fig.patch.set_facecolor('white')

    # gli assi sono in pixel dell'immagine, con l'origine in alto a sinistra e
    # y crescente verso il basso: e' la convenzione in cui MediaPipe
    # restituisce le coordinate e in cui il motore geometrico le riceve. Senza
    # i numeri sugli assi non si legge a quale quota cada il pavimento.
    for ax in (sx, dx):
        ax.set_xlim(x0, x1)
        ax.set_ylim(y1, y0)
        ax.set_aspect('equal')
        ax.tick_params(labelsize=7.5, colors='#5a6b7a', length=3, width=0.8)
        ax.set_xlabel('$x$ [pixel]', fontsize=8.5, color='#5a6b7a', labelpad=2)
        for s in ax.spines.values():
            s.set_edgecolor('#b9c6d2')
            s.set_linewidth(0.9)
    sx.set_ylabel('$y$ [pixel]', fontsize=8.5, color='#5a6b7a', labelpad=2)
    dx.tick_params(labelleft=False)

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    if sfondo == 'foto':
        # la stessa fotografia sotto entrambi i pannelli, senza velo: a destra
        # lo scheletro sta SOPRA la persona, cosi' si vede che e' la posa di
        # quel fotogramma e non un disegno accanto. A tenere leggibili le linee
        # ci pensa l'alone bianco di `osso`, non lo schiarimento dell'immagine.
        for ax in (sx, dx):
            ax.imshow(rgb, extent=(0, w, h, 0), zorder=0,
                      interpolation='lanczos')
    else:
        sx.imshow(rgb, extent=(0, w, h, 0), zorder=0, interpolation='lanczos')
        dx.set_facecolor('#fbfcfd')
    sx.set_title(titolo_foto, fontsize=12, color='#1d2b36', pad=7)
    misure = {}
    if nome_r == 'a1':
        mag, minore, ang = ellisse_a1(dx, P)
        misure = {'A1_asse_mag': mag, 'A1_asse_min': minore,
                  'A1_allungamento': mag / (minore + 1e-6),
                  'A1_inclinazione': ang}
    if nome_r == 'a3':
        h_pav = riferimento_a3(dx, P, retta, x0, x1)
        if h_pav is not None:
            misure['A3_h_pavimento'] = h_pav
    scheletro(dx, P, vis, punti, colore)
    if nome_r == 'a2':
        misure = {'A2_angolo_tronco': tronco_a2(dx, P)}
    dx.set_title(titolo, fontsize=12, color='#1d2b36', pad=7)

    fig.tight_layout()
    os.makedirs(dove, exist_ok=True)
    fuori = os.path.join(dove, nome)
    fig.savefig(fuori, dpi=400, facecolor='white', bbox_inches='tight')
    plt.close(fig)
    print('scritto %s' % fuori)
    return fuori, misure


def insieme(img, P, vis, t, dove, nome, retta=None):
    """Una figura sola: la fotografia a sinistra, le tre rappresentazioni a
    destra su fondo chiaro.

    La persona e' la stessa per tutte e tre, quindi ripeterla tre volte come
    facevano le figure separate non aggiungeva niente: la si mostra una volta
    e accanto si mettono le tre letture, ciascuna con i suoi punti numerati e
    la sua costruzione geometrica. Sui pannelli delle rappresentazioni non c'e'
    la fotografia sotto --- li' non serve dimostrare che la posa e' vera, cosa
    che fa il primo pannello, ma leggere la geometria senza niente intorno."""
    mx = 0.17 * (P[:, 0].max() - P[:, 0].min()) + 48
    my = 0.20 * (P[:, 1].max() - P[:, 1].min()) + 38
    h, w = img.shape[:2]
    x0, x1 = max(P[:, 0].min() - mx, 0), min(P[:, 0].max() + mx, w)
    y0, y1 = max(P[:, 1].min() - my, 0), min(P[:, 1].max() + my, h)

    larghezza = 2.85
    fig, assi = plt.subplots(
        1, 4, figsize=(4 * larghezza,
                       larghezza * (y1 - y0) / (x1 - x0) + 0.55))
    fig.patch.set_facecolor('white')
    for ax in assi:
        ax.set_xlim(x0, x1)
        ax.set_ylim(y1, y0)
        ax.set_aspect('equal')
        ax.tick_params(labelsize=7, colors='#5a6b7a', length=3, width=0.8)
        ax.set_xlabel('$x$ [pixel]', fontsize=8, color='#5a6b7a', labelpad=2)
        for s in ax.spines.values():
            s.set_edgecolor('#b9c6d2')
            s.set_linewidth(0.9)
    assi[0].set_ylabel('$y$ [pixel]', fontsize=8, color='#5a6b7a', labelpad=2)
    for ax in assi[1:]:
        ax.tick_params(labelleft=False)
        ax.set_facecolor('#fbfcfd')

    assi[0].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), extent=(0, w, h, 0),
                   zorder=0, interpolation='lanczos')
    assi[0].set_title(t['foto'], fontsize=11.5, color='#1d2b36', pad=7)

    misure = {}
    for ax, (nome_r, punti, colore) in zip(
            assi[1:], (('a1', PUNTI_ELLISSE, BLU), ('a2', PUNTI_A2, ROSSO),
                       ('a3', PUNTI_A3, VERDE))):
        m = {}
        if nome_r == 'a1':
            mag, minore, ang = ellisse_a1(ax, P)
            m = {'A1_asse_mag': mag, 'A1_asse_min': minore,
                 'A1_allungamento': mag / (minore + 1e-6),
                 'A1_inclinazione': ang}
        if nome_r == 'a3':
            hp = riferimento_a3(ax, P, retta, x0, x1)
            if hp is not None:
                m['A3_h_pavimento'] = hp
        scheletro(ax, P, vis, punti, colore)
        if nome_r == 'a2':
            m = {'A2_angolo_tronco': tronco_a2(ax, P)}
        ax.set_title(t[nome_r], fontsize=11.5, color='#1d2b36', pad=7)
        misure[nome_r] = m

    fig.tight_layout()
    os.makedirs(dove, exist_ok=True)
    fuori = os.path.join(dove, nome)
    fig.savefig(fuori, dpi=400, facecolor='white', bbox_inches='tight')
    plt.close(fig)
    print('scritto %s' % fuori)
    return fuori, misure


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ripresa', default=RIPRESA)
    ap.add_argument('--pavimento', nargs='*', default=PAVIMENTO)
    ap.add_argument('--lingua', default='it', choices=('it', 'en'))
    ap.add_argument('--solo', default=None, choices=('a1', 'a2', 'a3'))
    ap.add_argument('--sfondo', default='foto', choices=('foto', 'bianco'),
                    help="'foto': lo scheletro sopra la persona. 'bianco': "
                         'solo lo scheletro, su fondo chiaro.')
    ap.add_argument('--insieme', action='store_true',
                    help='una figura sola a quattro pannelli: la fotografia '
                         'e le tre rappresentazioni su fondo chiaro')
    ap.add_argument('--dove', default=os.path.join(QUI, 'tesi', 'figure'))
    a = ap.parse_args()

    t = TITOLI[a.lingua]
    suff = '' if a.lingua == 'it' else '_en'
    coda = '' if a.sfondo == 'foto' else '_bianco'
    if a.insieme:
        coda = '_insieme'
    cartella = a.ripresa if os.path.isabs(a.ripresa) \
        else os.path.join(QUI, a.ripresa)
    if not os.path.isdir(cartella):
        sys.exit('ripresa non trovata: ' + cartella)

    scelto = scegli(cartella)
    if scelto is None:
        sys.exit('nessuna posa valida in ' + cartella)
    punteggio, k, perc, img, lm = scelto
    h, w = img.shape[:2]
    P = np.array([[l.x * w, l.y * h] for l in lm], np.float64)
    vis = np.array([l.visibility for l in lm], np.float64)
    print('ripresa    %s' % os.path.basename(cartella))
    print('fotogramma %d (%s), punteggio %.2f' % (k, os.path.basename(perc),
                                                  punteggio))

    retta = oss = nfot = None
    if a.solo in (None, 'a3'):
        carte = [c if os.path.isabs(c) else os.path.join(QUI, c)
                 for c in a.pavimento]
        retta, oss, nfot = stima_pavimento(carte)
        if retta is None:
            print('ATTENZIONE: il motore non ha stimato il pavimento '
                  '(%d osservazioni su %d richieste)'
                  % (oss, MotoreGeometrico.PAV_MINIME))
        else:
            print('pavimento  y = %.5f x + %.2f  su %d osservazioni '
                  '(%d fotogrammi)' % (retta[0], retta[1], oss, nfot))

    lavoro = [('a1', PUNTI_ELLISSE, BLU), ('a2', PUNTI_A2, ROSSO),
              ('a3', PUNTI_A3, VERDE)]
    if a.solo:
        lavoro = [x for x in lavoro if x[0] == a.solo]

    if a.insieme:
        fuori, mis = insieme(img, P, vis, t, a.dove,
                             'fig_landmark%s.png' % suff, retta=retta)
        tutte = {r: (fuori, p, mis.get(r, {})) for r, p, _c in lavoro}
    else:
        tutte = {}
        for nome_r, punti, colore in lavoro:
            fuori, misure = una(nome_r, punti, colore, img, P, vis, t['foto'],
                                t[nome_r], a.dove,
                                'fig_landmark_%s%s%s.png' % (nome_r, coda, suff),
                                retta=retta, sfondo=a.sfondo)
            tutte[nome_r] = (fuori, punti, misure)

    scheda = os.path.join(a.dove, 'fig_landmark%s%s.txt' % (coda, suff))
    with open(scheda, 'w', encoding='utf-8') as f:
        f.write('figure dei landmark impiegati, una per rappresentazione\n\n')
        f.write('ripresa     %s\n' % os.path.basename(cartella))
        f.write('fotogramma  %d (%s)\n\n' % (k, os.path.basename(perc)))
        for nome_r, (fuori, punti, misure) in tutte.items():
            f.write('%s  %s\n' % (nome_r.upper(), os.path.basename(fuori)))
            f.write('    indici %s  (%d punti)\n' % (list(punti), len(punti)))
            for nome_m, v in misure.items():
                f.write('    %-18s %.4f\n' % (nome_m, v))
        f.write('\nindici importati da src/geometry.py\n')
        f.write('ellisse A1: disegnata a 2 deviazioni standard per avvolgere la persona;\n'
                '            la freccia resta a 1 sigma: la sua semilunghezza e A1_asse_mag.\n'
                '            Allungamento e inclinazione non dipendono dal fattore di scala.\n')
        if retta is not None:
            f.write('pavimento : y = %.6f x + %.3f, stimato da\n'
                    '            MotoreGeometrico._pavimento su %d '
                    'osservazioni\n            raccolte in %d fotogrammi di '
                    '%s.\n'
                    '            Nel dataset la retta viene stimata su TUTTE '
                    'le riprese\n            della telecamera: stessa '
                    'procedura, coefficienti diversi.\n'
                    % (retta[0], retta[1], oss, nfot,
                       ', '.join(os.path.basename(c) for c in a.pavimento)))
    print('scheda     %s' % scheda)


if __name__ == '__main__':
    main()
