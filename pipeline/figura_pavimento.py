# -*- coding: utf-8 -*-
"""
Come si stima la retta del pavimento, e che cosa e' l'altezza del bacino.

Perche' esiste
--------------
La Sezione `sec:pavimento` del Capitolo 3 descrive a parole una costruzione
geometrica fatta di quattro oggetti --- ingombro, osservazioni, retta, segmento
--- che il lettore deve tenere a mente uno per uno. In figura si vedono tutti
insieme.

Perche' e' un DIAGRAMMA e non una fotografia annotata
-----------------------------------------------------
La prima versione disegnava sopra il fotogramma. Il fondo di UP-Fall e' pero'
una hall con vetrate, manifesti e tavoli: la retta e le osservazioni ci
finivano sopra, e la cosa che la figura deve mostrare era quella che si vedeva
peggio. Qui il fondo e' pulito e restano i soli oggetti della costruzione.

Il fotogramma resta disponibile con `--sfondo foto`, perche' serve a controllare
che lo scheletro sia davvero quello della persona e non una posa inventata.

Che cosa e' vero
----------------
Cambia il fondo, non i numeri. Tutto quello che si vede e' calcolato:

  - le coordinate dei landmark sono quelle che MediaPipe produce su quel
    fotogramma, in pixel;
  - l'ingombro e' il riquadro dei trentatre landmark, e il suo bordo inferiore
    e' esattamente il valore che il motore accumula;
  - le osservazioni sono quelle vere, lette da `MotoreGeometrico._pav_oss`;
  - la retta e' `_pav_retta`, cioe' il `polyfit` del motore, non una retta
    tracciata a occhio;
  - `h_pav` e' il valore che `altezza_su_pavimento` restituisce su quel bacino.

Il problema dei landmark stimati sotto il bordo dell'immagine NON viene
disegnato: ci vorrebbe un secondo pannello e toglierebbe leggibilita' a cio'
che la figura deve spiegare. Resta dichiarato nel testo.

Una cosa va dichiarata nella didascalia e non si puo' evitare: nel dataset le
osservazioni vengono da TUTTE le riprese di una telecamera, qui da due sole.
Il tipo di stima e' lo stesso, i coefficienti no.

Uso:
    conda activate fall_processing
    python pipeline/figura_pavimento.py --lingua en
    python pipeline/figura_pavimento.py --sfondo foto
"""

import argparse
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, QUI)

import cv2
import mediapipe as mp

from src.geometry import MotoreGeometrico
from pipeline.figura_landmark import (scheletro, scegli, PAVIMENTO,
                                      PUNTI_A3, BLU, ROSSO, VERDE, ARANCIO,
                                      SPALLA_SX, SPALLA_DX,
                                      ANCA_SX, ANCA_DX)

TESTI = {
    'it': {
        'bordo': "bordo inferiore dell'ingombro",
        'ingombro': 'ingombro dei 33 landmark',
        'oss': r'osservazioni $(x_{\mathrm{bacino}},\,y_{\mathrm{bordo}})$',
        'retta': r'retta del pavimento $y_{\mathrm{pav}}(x)=ax+c$',
        'hpav': r'$h_{\mathrm{pav}}$: altezza del bacino sul pavimento',
        'L': r'$L$: lunghezza del tronco, che normalizza $h_{\mathrm{pav}}$',
        'x': '$x$ [pixel]', 'y': '$y$ [pixel]',
    },
    'en': {
        'bordo': 'bottom edge of the bounding box',
        'ingombro': 'bounding box of the 33 landmarks',
        'oss': r'observations $(x_{\mathrm{hip}},\,y_{\mathrm{edge}})$',
        'retta': r'floor line $y_{\mathrm{pav}}(x)=ax+c$',
        'hpav': r'$h_{\mathrm{pav}}$: hip height above the floor',
        'L': r'$L$: trunk length, which normalises $h_{\mathrm{pav}}$',
        'x': '$x$ [pixel]', 'y': '$y$ [pixel]',
    },
}

GRIGIO_SCURO = '#263238'


def motore_pavimento(cartelle, tetto=600):
    """
    Come `figura_landmark.stima_pavimento`, ma restituisce il MOTORE.

    Serve perche' oltre alla retta questa figura disegna le osservazioni
    singole, che stanno in `_pav_oss` e che quella funzione non espone.
    """
    motore = MotoreGeometrico()
    n = 0
    with mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1,
                                min_detection_confidence=0.5,
                                min_tracking_confidence=0.5) as pose:
        for cartella in cartelle:
            perc = os.path.join(QUI, cartella)
            if not os.path.isdir(perc):
                continue
            nomi = sorted(f for f in os.listdir(perc)
                          if f.lower().endswith(('.png', '.jpg', '.jpeg')))
            for nome in nomi:
                if n >= tetto:
                    break
                img = cv2.imread(os.path.join(perc, nome))
                if img is None:
                    continue
                h, w = img.shape[:2]
                r = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                if r.pose_landmarks:
                    motore.a3(r.pose_landmarks.landmark, w, h, 1.0 / 18.0)
                n += 1
    return motore, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lingua', default='en', choices=('it', 'en'))
    ap.add_argument('--sfondo', default='bianco', choices=('bianco', 'foto'),
                    help="'bianco' e' il diagramma; 'foto' sovrappone al "
                         "fotogramma, e serve a controllare che lo scheletro "
                         "sia quello della persona")
    ap.add_argument('--tetto', type=int, default=600,
                    help="quanti fotogrammi al piu' per raccogliere il pavimento")
    a = ap.parse_args()
    T = TESTI[a.lingua]

    if 'fall_processing' not in sys.executable:
        sys.exit(f"Interprete sbagliato: {sys.executable}\n"
                 f"Serve l'ambiente fall_processing.")

    print('raccolta delle osservazioni del pavimento...')
    motore, n_visti = motore_pavimento(PAVIMENTO, a.tetto)
    pronto, n_oss = motore.pavimento_pronto()
    if not pronto:
        sys.exit(f'pavimento non stimato: solo {n_oss} osservazioni su '
                 f'{n_visti} fotogrammi (ne servono {motore.PAV_MINIME})')
    a_r, c_r = motore._pav_retta
    oss = np.asarray(motore._pav_oss, dtype=np.float64)
    print(f'  {n_oss} osservazioni su {n_visti} fotogrammi')
    print(f'  retta: y = {a_r:+.4f}*x {c_r:+.1f}')

    print('scelta del fotogramma da mostrare...')
    scelto = scegli(os.path.join(QUI, PAVIMENTO[1]))
    if scelto is None:
        sys.exit('nessun fotogramma utilizzabile')
    _, k, perc, img, lm = scelto
    h, w = img.shape[:2]
    P = np.array([[p.x * w, p.y * h] for p in lm], dtype=np.float64)
    vis = np.array([p.visibility for p in lm], dtype=np.float64)

    hip = (P[ANCA_SX] + P[ANCA_DX]) / 2.0
    sh = (P[SPALLA_SX] + P[SPALLA_DX]) / 2.0
    L = float(np.linalg.norm(sh - hip))
    x0, x1 = float(P[:, 0].min()), float(P[:, 0].max())
    y0, y1 = float(P[:, 1].min()), float(P[:, 1].max())
    h_pav = motore.altezza_su_pavimento(hip[0], hip[1], L)
    y_ret = a_r * hip[0] + c_r
    print(f'  fotogramma {k}: h_pav = {h_pav:+.3f} lunghezze di tronco '
          f'(L = {L:.1f} px)')

    # ------------------------------------------------------------- disegno
    fig, ax = plt.subplots(figsize=(11.2, 6.2))
    ALONE = [pe.withStroke(linewidth=4.4, foreground='white')]
    ALONE_FINE = [pe.withStroke(linewidth=2.6, foreground='white')]

    if a.sfondo == 'foto':
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(float)
        rgb = rgb * 0.70 + 255.0 * 0.30
        ax.imshow(rgb.astype('uint8'), extent=[0, w, h, 0])
    else:
        # Diagramma: fondo chiaro, e una fascia appena piu' scura sotto la
        # retta. Non e' il pavimento misurato --- e' solo un riferimento
        # visivo per capire da che parte sta il basso.
        ax.set_facecolor('#fbfbfc')
        xs_f = np.array([0.0, float(w)])
        ax.fill_between(xs_f, a_r * xs_f + c_r, h, color='#eceff1',
                        zorder=0, linewidth=0)

    # 1. l'ingombro dei 33 landmark, e il suo bordo inferiore
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False,
                           edgecolor=GRIGIO_SCURO, lw=1.9, ls=(0, (6, 3)),
                           zorder=4))
    ax.plot([x0, x1], [y1, y1], color=ROSSO, lw=4.2, zorder=8,
            solid_capstyle='butt', path_effects=ALONE)

    # 2. le osservazioni vere, raccolte su altri fotogrammi
    ax.scatter(oss[:, 0], oss[:, 1], s=26, marker='o', color=ARANCIO,
               alpha=0.8, linewidths=0.4, edgecolors='white', zorder=5)

    # 3. la retta adattata su quelle osservazioni
    xs = np.array([0.0, float(w)])
    ax.plot(xs, a_r * xs + c_r, color=ARANCIO, lw=3.2, zorder=7,
            path_effects=ALONE)

    # 4. lo scheletro, senza indici: qui non dicono nulla e affollano
    scheletro(ax, P, vis, set(PUNTI_A3), BLU, indici=False)

    # 5. L, la lunghezza del tronco
    ax.add_patch(FancyArrowPatch(tuple(hip), tuple(sh), color=VERDE, lw=2.8,
                                 arrowstyle='<|-|>', mutation_scale=13,
                                 zorder=9, path_effects=ALONE_FINE))
    # L'etichetta va portata FUORI dall'ingombro: dentro finisce sul braccio
    # e sul bordo tratteggiato, e si legge male.
    y_L = (hip[1] + sh[1]) / 2
    ax.plot([x0 - 10, (hip[0] + sh[0]) / 2 - 4], [y_L, y_L], color=VERDE,
            lw=1.2, ls=':', zorder=9, path_effects=ALONE_FINE)
    ax.annotate(r'$L$', (x0 - 16, y_L),
                fontsize=16, color=VERDE, fontweight='bold',
                ha='right', va='center', zorder=11,
                path_effects=[pe.withStroke(linewidth=4.4, foreground='white')])

    # 6. il bacino, e h_pav quotata di lato come in un disegno tecnico.
    #    Dentro le gambe il segmento si legge male.
    xq = hip[0] + 62.0
    for yy in (hip[1], y_ret):
        ax.plot([hip[0], xq + 9], [yy, yy], color=ROSSO, lw=1.4, ls=':',
                zorder=9, path_effects=ALONE_FINE)
    ax.add_patch(FancyArrowPatch((xq, hip[1]), (xq, y_ret), color=ROSSO,
                                 lw=2.8, arrowstyle='<|-|>',
                                 mutation_scale=13, zorder=10,
                                 path_effects=ALONE_FINE))
    ax.scatter([hip[0]], [hip[1]], s=150, marker='o', facecolors='white',
               edgecolors=ROSSO, lw=2.3, zorder=11)
    ax.annotate(r'$h_{\mathrm{pav}}$' + f' = {h_pav:.2f}'.replace('.', ',')
                + r' $L$',
                (xq + 13, (hip[1] + y_ret) / 2),
                fontsize=14, color=ROSSO, fontweight='bold',
                ha='left', va='center', zorder=12,
                path_effects=[pe.withStroke(linewidth=4.2, foreground='white')])

    # ------------------------------------------------------------- legenda
    # Una voce per ciascun oggetto della costruzione, L compreso: senza,
    # resta una freccia verde che il lettore deve indovinare.
    voci = [
        (Line2D([], [], color=GRIGIO_SCURO, lw=1.9, ls=(0, (6, 3))),
         T['ingombro']),
        (Line2D([], [], color=ROSSO, lw=4.2), T['bordo']),
        (Line2D([], [], color=ARANCIO, lw=0, marker='o', markersize=6.5,
                markeredgecolor='white', markeredgewidth=0.4), T['oss']),
        (Line2D([], [], color=ARANCIO, lw=3.2), T['retta']),
        (Line2D([], [], color=ROSSO, lw=2.6), T['hpav']),
        (Line2D([], [], color=VERDE, lw=2.6), T['L']),
    ]
    leg = ax.legend([v[0] for v in voci], [v[1] for v in voci],
                    loc='upper left', fontsize=9.8, framealpha=0.95,
                    borderpad=0.75, labelspacing=0.55,
                    facecolor='white', edgecolor='#b0bec5')
    leg.set_zorder(20)

    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.set_xlabel(T['x'], fontsize=10)
    ax.set_ylabel(T['y'], fontsize=10)
    ax.tick_params(labelsize=9)
    for lato in ('top', 'right'):
        ax.spines[lato].set_visible(False)

    fig.tight_layout()
    nome = 'fig_pavimento' + ('_en' if a.lingua == 'en' else '')
    if a.sfondo == 'foto':
        nome += '_foto'
    dst = os.path.join(QUI, 'tesi', 'figure', nome + '.png')
    fig.savefig(dst, dpi=190, facecolor='white')
    plt.close(fig)
    print(f'salvata in {os.path.relpath(dst, QUI)}')

    # ------------------------------------------------------------- scheda
    def it(x, n=2):
        return f'{x:.{n}f}'.replace('.', ',')

    scheda = dst.replace('.png', '.txt')
    with open(scheda, 'w', encoding='utf-8') as f:
        f.write(f"""FIGURA — LA STIMA DELLA RETTA DEL PAVIMENTO
File: {os.path.basename(dst)}
Prodotta da: pipeline/figura_pavimento.py  (ambiente fall_processing)
Comando:     python pipeline/figura_pavimento.py --lingua {a.lingua} --sfondo {a.sfondo}

CHE COSA SI VEDE
  Un diagramma, non una fotografia annotata: il fondo e' pulito e restano i
  soli oggetti della costruzione.
   - lo scheletro, alle coordinate vere dei landmark su quel fotogramma;
   - l'ingombro dei 33 landmark (tratteggio scuro) e il suo bordo inferiore
     (magenta), che e' l'osservazione che il motore raccoglie;
   - le {n_oss} osservazioni (x_bacino, y_bordo) raccolte su altri fotogrammi
     della stessa telecamera (arancio);
   - la retta adattata su di esse;
   - h_pav quotata di lato, e L che la normalizza.
  Ogni oggetto ha la sua voce in legenda, L compreso.

NUMERI DI QUESTA ESECUZIONE
  osservazioni       {n_oss} su {n_visti} fotogrammi esaminati
  retta              y = {a_r:+.4f}*x {c_r:+.1f}
  fotogramma         indice {k}
  L                  {L:.1f} pixel
  h_pav              {h_pav:+.3f} lunghezze di tronco
  riprese usate      {', '.join(os.path.basename(p) for p in PAVIMENTO)}

DA DICHIARARE NELLA DIDASCALIA
  Nel dataset le osservazioni vengono da TUTTE le riprese di una telecamera;
  qui da due sole. Il tipo di stima e' lo stesso, i coefficienti no.
  Il problema dei landmark stimati sotto il bordo dell'immagine NON e'
  disegnato: e' dichiarato nel testo e servirebbe un secondo pannello.

DA METTERE IN LATEX
-------------------
\\begin{{figure}}[htbp]
\\centering
\\includegraphics[width=\\textwidth]{{figure/{os.path.basename(dst)}}}
\\caption{{La stima della retta del pavimento, su una ripresa di UP-Fall.
Quando la persona e' eretta il bordo inferiore dell'ingombro dei
\\emph{{landmark}} e' un'osservazione della posizione del pavimento all'ascissa
del bacino; raccogliendone molte --- qui {n_oss}, da altre riprese della stessa
telecamera --- si adatta la retta $y_{{\\mathrm{{pav}}}}(x)=ax+c$. L'altezza del
bacino $h_{{\\mathrm{{pav}}}}$ e' il segmento verticale fra il bacino e quella
retta, diviso per la lunghezza del tronco $L$, e vale {it(h_pav)} in questo
istante. Le coordinate sono quelle vere dei \\emph{{landmark}}, e la retta e'
quella adattata dal motore geometrico: cambia il fondo rispetto al fotogramma,
non i numeri. Nel dataset le osservazioni provengono da \\emph{{tutte}} le
riprese di una telecamera: il tipo di stima e' lo stesso, i coefficienti no.
Prodotta da \\texttt{{pipeline/figura\\_pavimento.py}}.}}
\\label{{fig:pavimento}}
\\end{{figure}}
""")
    print(f'scheda in {os.path.relpath(scheda, QUI)}')


if __name__ == '__main__':
    main()
