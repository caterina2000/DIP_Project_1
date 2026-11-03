# -*- coding: utf-8 -*-
"""
Lo schema dei 33 landmark di MediaPipe Pose: scheletro numerato e legenda.

Perche' esiste
--------------
Il Capitolo 3 nomina i landmark per indice --- 0, 11, 12, 23--28 --- e la
Tabella dei landmark impiegati dalle tre rappresentazioni presuppone che chi
legge sappia quale punto anatomico stia dietro ciascun numero. La figura
equivalente esiste nella documentazione di MediaPipe, ma e' materiale altrui:
questa la ridisegna, cosi' la tesi non incorpora un'immagine di terzi e lo
stile resta quello delle altre figure.

CHE COSA E' DISEGNATO, E CHE COSA E' DATO
-----------------------------------------
Questa figura, a differenza di tutte le altre di `pipeline/`, **non e'
calcolata su dati**. E' uno schema, e va detto:

  le POSIZIONI dei punti  sono scelte a mano. Non sono l'uscita dello
                          stimatore su una persona: sono una posa di comodo,
                          scelta perche' i 33 punti risultino tutti separabili
                          e leggibili. Nessun numero di questa figura e' una
                          misura.

  i COLLEGAMENTI          sono `mp.solutions.pose.POSE_CONNECTIONS`, cioe' lo
                          schema di MediaPipe e non una scelta di chi disegna.
                          Sono trascritti in COLLEGAMENTI qui sotto perche'
                          questo script deve girare anche senza mediapipe
                          installato; se mediapipe c'e', lo script CONFRONTA
                          la propria lista con quella vera e avvisa se
                          differiscono.

  i NOMI e gli INDICI     sono quelli dell'API di MediaPipe Pose, in inglese.
                          Restano in inglese perche' sono identificatori del
                          programma, non prosa: nel codice di questo lavoro
                          `src/geometry.py` vi si riferisce per numero.

  la MANO                 lo schema di MediaPipe collega polso, mignolo,
                          indice e pollice in un triangolo. E' la loro
                          convenzione, riprodotta come tale.

Convenzione di lato
-------------------
Vista frontale: la persona guarda chi osserva, quindi il suo lato SINISTRO
(indici dispari: 11, 13, 15, 23, 25, 27...) sta a DESTRA nell'immagine. E' la
stessa convenzione della figura originale di MediaPipe, e va ricordata perche'
e' la fonte di equivoci piu' comune quando si legge un indice.

Uso
---
    python pipeline/figura_landmark_mediapipe.py
    python pipeline/figura_landmark_mediapipe.py --senza-legenda

Produce `tesi/figure/fig_landmark_mediapipe.png` e la scheda `.txt` accanto.
"""

import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USCITA = os.path.join(QUI, "tesi", "figure")

# --------------------------------------------------------------------- dati
# I nomi sono quelli dell'API di MediaPipe Pose.
NOMI = [
    "nose", "left_eye_inner", "left_eye", "left_eye_outer",
    "right_eye_inner", "right_eye", "right_eye_outer",
    "left_ear", "right_ear", "mouth_left", "mouth_right",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_pinky", "right_pinky",
    "left_index", "right_index", "left_thumb", "right_thumb",
    "left_hip", "right_hip", "left_knee", "right_knee",
    "left_ankle", "right_ankle", "left_heel", "right_heel",
    "left_foot_index", "right_foot_index",
]

# `mp.solutions.pose.POSE_CONNECTIONS`, trascritte. Verificate a valle.
COLLEGAMENTI = [
    (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8), (9, 10),
    (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
    (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
    (11, 23), (12, 24), (23, 24),
    (23, 25), (24, 26), (25, 27), (26, 28),
    (27, 29), (28, 30), (29, 31), (30, 32), (27, 31), (28, 32),
]

# Posa di comodo. Lato sinistro della persona a destra nell'immagine.
# Il viso e' disegnato in scala maggiorata dentro il richiamo ovale: i punti
# del volto sono cosi' ravvicinati che a scala reale si sovrapporrebbero.
P = {
    0: (0.00, 9.22),      # nose
    1: (0.62, 9.56), 2: (0.88, 9.56), 3: (1.14, 9.56),          # occhio sx
    4: (-0.62, 9.56), 5: (-0.88, 9.56), 6: (-1.14, 9.56),       # occhio dx
    7: (1.52, 9.26), 8: (-1.52, 9.26),                          # orecchie
    9: (0.34, 8.86), 10: (-0.34, 8.86),                         # bocca
    11: (2.20, 7.55), 12: (-2.20, 7.55),                        # spalle
    13: (4.35, 6.92), 14: (-4.35, 6.92),                        # gomiti
    15: (5.85, 6.74), 16: (-5.85, 6.74),                        # polsi
    17: (6.62, 6.70), 18: (-6.62, 6.70),                        # mignoli
    19: (6.86, 7.34), 20: (-6.86, 7.34),                        # indici
    21: (6.30, 7.30), 22: (-6.30, 7.30),                        # pollici
    23: (1.45, 4.85), 24: (-1.45, 4.85),                        # anche
    25: (1.72, 2.60), 26: (-1.72, 2.60),                        # ginocchia
    27: (1.92, 0.62), 28: (-1.92, 0.62),                        # caviglie
    29: (1.70, 0.06), 30: (-1.70, 0.06),                        # talloni
    31: (2.46, 0.00), 32: (-2.46, 0.00),                        # punte
}

# Dove mettere l'etichetta di ciascun punto, rispetto al punto stesso.
# 'sx' = a sinistra, 'dx' = a destra, 'su' = sopra, 'giu' = sotto.
POSA_ETICHETTA = {
    0: "su",
    1: "su", 2: "su", 3: "su", 4: "su", 5: "su", 6: "su",
    7: "dx", 8: "sx", 9: "giu", 10: "giu",
    11: "su", 12: "su", 13: "sx", 14: "dx", 15: "giu", 16: "giu",
    17: "giu", 18: "giu", 19: "su", 20: "su", 21: "su", 22: "su",
    23: "dx", 24: "sx", 25: "dx", 26: "sx", 27: "su", 28: "su",
    29: "giu", 30: "giu", 31: "dx", 32: "sx",
}

INCHIOSTRO = "#4a4a6a"
OSSO = "#8a8ab0"
TESTO = "#2b2b3d"


def verifica_collegamenti():
    """Se mediapipe c'e', confronta COLLEGAMENTI con la lista vera."""
    try:
        import mediapipe as mp
    except ImportError:
        return "mediapipe non installato in questo interprete: " \
               "collegamenti NON verificati contro POSE_CONNECTIONS"
    veri = set(tuple(sorted(c)) for c in mp.solutions.pose.POSE_CONNECTIONS)
    nostri = set(tuple(sorted(c)) for c in COLLEGAMENTI)
    if veri == nostri:
        return "collegamenti verificati contro mp.solutions.pose." \
               "POSE_CONNECTIONS: identici (%d)" % len(veri)
    return "ATTENZIONE: collegamenti DIVERSI da POSE_CONNECTIONS. " \
           "solo nostri %s | solo veri %s" % (sorted(nostri - veri),
                                              sorted(veri - nostri))


def disegna(legenda=True):
    larghezza = 13.0 if legenda else 6.5
    fig, ax = plt.subplots(figsize=(larghezza, 6.0))
    ax.set_aspect("equal")
    ax.axis("off")

    # --- richiamo ovale attorno al viso, disegnato per primo cosi' sta sotto
    # Deve contenere tutti i punti del viso, 0-10, e le loro etichette:
    # 8 e 7 sono i piu' esterni (x = +-1.52), 9 e 10 i piu' bassi (y = 8.86)
    # con etichetta sotto, 1-6 i piu' alti (y = 9.56) con etichetta sopra.
    ax.add_patch(FancyBboxPatch(
        (-1.62, 8.62), 3.24, 1.30,
        boxstyle="round,pad=0.46,rounding_size=0.60",
        linewidth=1.0, edgecolor=OSSO, facecolor="none"))

    # --- ossa
    for a, b in COLLEGAMENTI:
        xa, ya = P[a]
        xb, yb = P[b]
        ax.plot([xa, xb], [ya, yb], color=OSSO, linewidth=1.1,
                zorder=1, solid_capstyle="round")

    # --- punti e indici
    scarto = 0.30
    for i, (x, y) in P.items():
        ax.plot(x, y, "o", color=INCHIOSTRO, markersize=6.2, zorder=3)
        dove = POSA_ETICHETTA[i]
        if dove == "sx":
            tx, ty, ha, va = x - scarto, y, "right", "center"
        elif dove == "dx":
            tx, ty, ha, va = x + scarto, y, "left", "center"
        elif dove == "su":
            tx, ty, ha, va = x, y + scarto, "center", "bottom"
        else:
            tx, ty, ha, va = x, y - scarto, "center", "top"
        ax.text(tx, ty, str(i), fontsize=9.5, color=TESTO,
                ha=ha, va=va, zorder=4)

    ax.set_xlim(-8.6, 8.6)
    ax.set_ylim(-0.9, 10.6)

    # --- legenda su due colonne, alla destra del disegno
    if legenda:
        sinistra, destra = NOMI[:17], NOMI[17:]
        y0, passo = 0.955, 0.0555
        for colonna, (voci, xrel) in enumerate(
                ((sinistra, 0.575), (destra, 0.795))):
            base = colonna * 17
            for k, nome in enumerate(voci):
                fig.text(xrel, y0 - k * passo,
                         "%2d." % (base + k), fontsize=11.5, color=TESTO,
                         ha="right", family="DejaVu Sans")
                fig.text(xrel + 0.008, y0 - k * passo,
                         nome, fontsize=11.5, color=TESTO, ha="left")

    fig.subplots_adjust(left=0.01, right=0.56 if legenda else 0.99,
                        top=0.99, bottom=0.01)
    return fig


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--senza-legenda", action="store_true",
                   help="solo lo scheletro numerato, senza l'elenco dei nomi")
    a = p.parse_args()

    if not os.path.isdir(USCITA):
        print("cartella non trovata: %s" % USCITA)
        return 1

    nota = verifica_collegamenti()
    print(nota)

    # I nomi dei landmark sono quelli ufficiali di MediaPipe, inglesi, e
    # il resto sono numeri: la figura e' gia' inglese e il nome lo dice.
    nome = "fig_landmark_mediapipe_en" + ("_solo" if a.senza_legenda else "")
    fig = disegna(legenda=not a.senza_legenda)
    png = os.path.join(USCITA, nome + ".png")
    fig.savefig(png, dpi=300, facecolor="white")
    plt.close(fig)
    print("scritto %s" % png)

    scheda = os.path.join(USCITA, nome + ".txt")
    with open(scheda, "w", encoding="utf-8") as f:
        f.write(
            "schema dei 33 landmark di MediaPipe Pose\n"
            "\n"
            "prodotta da  pipeline/figura_landmark_mediapipe.py\n"
            "\n"
            "NON E' UNA MISURA. Le posizioni dei punti sono scelte a mano: e'\n"
            "una posa di comodo, costruita perche' tutti e 33 i punti\n"
            "risultino separabili. Nessun numero della figura viene dai dati.\n"
            "\n"
            "collegamenti  mp.solutions.pose.POSE_CONNECTIONS (%d archi),\n"
            "              trascritti nello script perche' giri anche senza\n"
            "              mediapipe installato.\n"
            "              %s\n"
            "\n"
            "nomi          identificatori dell'API di MediaPipe Pose, in\n"
            "              inglese: sono nomi di programma, non prosa.\n"
            "\n"
            "lato          vista frontale. Il lato SINISTRO della persona\n"
            "              (indici dispari) sta a DESTRA nell'immagine.\n"
            "\n"
            "viso          disegnato in scala maggiorata dentro il richiamo\n"
            "              ovale: a scala reale i punti 0-10 si\n"
            "              sovrapporrebbero.\n"
            % (len(COLLEGAMENTI), nota))
    print("scritto %s" % scheda)
    return 0


if __name__ == "__main__":
    sys.exit(main())
