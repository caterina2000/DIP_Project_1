# -*- coding: utf-8 -*-
"""
Griglia di otto fotogrammi: la regola di persistenza vista costruirsi,
sulla prima caduta che genera l'allarme e sul falso positivo del divano.

Perche' esiste
--------------
`figura_caduta_scheletro.py` mostra un solo fotogramma con la persona
sostituita dallo scheletro. Questa versione ne mette otto in griglia, quattro
per episodio, per mostrare la raffica che si costruisce finestra dopo
finestra: nella prima riga arriva a 5/5 e genera l'allarme (bordo rosso),
nella seconda si ferma a 4/5 e non lo genera (bordo verde sull'ultimo
fotogramma, dove il punteggio e' gia' tornato sotto soglia).

Privacy -- seconda riscrittura: niente fotografia, in nessun caso
------------------------------------------------------------------
La prima versione cancellava l'area della persona con cv2.inpaint partendo
dall'involucro dei giunti: insufficiente su pose distese. Una seconda
versione usava la segmentazione per pixel, migliore ma ancora un inpainting
su una fotografia reale, con margine di errore residuo. Questa versione non
mostra PIU' la fotografia: sfondo bianco, solo lo scheletro (i soli
landmark 11-32, mai il volto 0-10), nello stile di
`figura_scheletro_andamento.py`. Niente foto significa niente rischio di
corpo visibile, qualunque sia la qualita' della segmentazione.

I tempi e i punteggi delle didascalie vengono CALCOLATI dal registro della
sessione (`sess_20260909_v5.csv`), non scritti a mano.

Uso (ambiente fall_processing, l'unico con mediapipe):
    python pipeline/figura_griglia_finestre.py
"""
import csv
import os
import sys

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)

SESSIONE = os.path.join(RADICE, 'deploy_board', 'sessioni', '20260909_v5')
CLIP = os.path.join(SESSIONE, 'clip')
REGISTRO = os.path.join(SESSIONE, 'sess_20260909_v5.csv')
USCITA = os.path.join(RADICE, 'tesi', 'figure', 'fig_griglia_finestre.png')

INK = '#1C2430'
ROSSO = '#9B1B30'
VERDE = '#1D7A4C'
TEAL = '#2E7D8C'
GRIGIO_VUOTO = '#F0F1F3'

CONNESSIONI = [(11, 12), (11, 13), (13, 15), (12, 14), (14, 16), (11, 23),
               (12, 24), (23, 24), (23, 25), (25, 27), (24, 26), (26, 28),
               (27, 29), (29, 31), (28, 30), (30, 32), (15, 17), (15, 19),
               (15, 21), (16, 18), (16, 20), (16, 22), (27, 31), (28, 32)]

CADUTA = [742.3, 742.8, 743.2, 744.2]
DIVANO = [881.8, 882.2, 882.6, 883.1]


def riga_piu_vicina(righe, t):
    return min(righe, key=lambda r: abs(float(r['t_s']) - t))


def file_fotogramma(t_s):
    candidati = [f for f in os.listdir(CLIP) if f.startswith('f%05d' % int(t_s))]
    if not candidati:
        candidati = os.listdir(CLIP)
    return min(candidati, key=lambda f: abs(float(f[1:-4]) - t_s))


def rileva_landmark(img_rgb):
    """
    Solo i landmark, in pixel. Nessuna fotografia viene mai disegnata: non
    serve una maschera, perche' lo sfondo del pannello e' sempre bianco.
    """
    import mediapipe as mp
    h, w = img_rgb.shape[:2]
    with mp.solutions.pose.Pose(static_image_mode=True, model_complexity=2,
                                min_detection_confidence=0.3) as pose:
        res = pose.process(img_rgb)
    if not res.pose_landmarks:
        return None
    return [(lm.x * w, lm.y * h, lm.visibility) for lm in res.pose_landmarks.landmark]


def pannello_vuoto(ax, titolo, colore_titolo):
    ax.set_facecolor(GRIGIO_VUOTO)
    ax.set_xticks([]); ax.set_yticks([])
    ax.text(.5, .5, 'posa non rilevata', ha='center', va='center',
            fontsize=9, color='#5A6773', transform=ax.transAxes)
    for lato in ax.spines.values():
        lato.set_edgecolor('#C8CCD1'); lato.set_linewidth(.8)
    ax.set_title(titolo, fontsize=10, color=colore_titolo, fontweight='bold', pad=6)


def pannello(ax, nome_file, titolo, colore_titolo, bordo=None):
    """Solo lo scheletro, su sfondo bianco: nessuna fotografia disegnata."""
    img_bgr = cv2.imread(os.path.join(CLIP, nome_file))
    img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    h, w = img.shape[:2]

    pts = rileva_landmark(np.ascontiguousarray(img))
    if pts is None:
        pannello_vuoto(ax, titolo, colore_titolo)
        return False

    ax.set_facecolor('white')
    ax.set_xlim(0, w); ax.set_ylim(h, 0); ax.set_aspect('equal')
    ax.set_xticks([]); ax.set_yticks([])
    for lato in ax.spines.values():
        lato.set_edgecolor(bordo or '#C8CCD1')
        lato.set_linewidth(3.2 if bordo else .8)

    for a, b in CONNESSIONI:
        xa, ya, va = pts[a]
        xb, yb, vb = pts[b]
        if min(va, vb) < 0.3:
            continue
        colore = (bordo or (ROSSO if a in (11, 12, 23, 24) or b in (11, 12, 23, 24) else TEAL))
        ax.plot([xa, xb], [ya, yb], color=colore, lw=6.5, solid_capstyle='round',
                zorder=4)
    for i, (x, y, v) in enumerate(pts):
        if i <= 10 or v < 0.3:
            continue
        ax.scatter([x], [y], s=150, color=(bordo or INK), zorder=5,
                  edgecolor='white', linewidth=1.6)

    ax.set_title(titolo, fontsize=14, color=colore_titolo, fontweight='bold', pad=8)
    return True


def main():
    righe = list(csv.DictReader(open(REGISTRO, encoding='utf-8')))
    fig, assi = plt.subplots(2, 4, figsize=(19.0, 10.2))
    riusciti = 0

    def etichetta(corsa):
        return f'{corsa} finestr{"a" if corsa == 1 else "e"} di 5'

    for col, t in enumerate(CADUTA):
        r = riga_piu_vicina(righe, t)
        rt, corsa = float(r['t_s']), int(r['corsa'])
        nome = file_fotogramma(rt)
        if col < 3:
            tit = f'{rt:.1f} s: {etichetta(corsa)}'
            ok = pannello(assi[0, col], nome, tit, INK)
        else:
            tit = f'{rt:.1f} s: 5 di 5, allarme'
            ok = pannello(assi[0, col], nome, tit, ROSSO, bordo=ROSSO)
            if ok:
                assi[0, col].text(.5, .08, 'CADUTA RILEVATA', transform=assi[0, col].transAxes,
                                  ha='center', va='bottom', color=ROSSO, fontsize=16,
                                  fontweight='bold')
        riusciti += int(ok)

    for col, t in enumerate(DIVANO):
        r = riga_piu_vicina(righe, t)
        rt, corsa = float(r['t_s']), int(r['corsa'])
        nome = file_fotogramma(rt)
        if col < 3:
            tit = f'{rt:.1f} s: {etichetta(corsa)}'
            ok = pannello(assi[1, col], nome, tit, INK)
        else:
            tit = f'{rt:.1f} s: nessun allarme'
            ok = pannello(assi[1, col], nome, tit, VERDE, bordo=VERDE)
        riusciti += int(ok)

    fig.suptitle('Dalla finestra positiva alla regola: una caduta vera e un falso positivo sul divano',
                 fontsize=17, color=INK, y=.985)
    fig.subplots_adjust(left=.01, right=.99, top=.91, bottom=.02, wspace=.05, hspace=.22)
    fig.savefig(USCITA, dpi=220, facecolor='white')
    plt.close(fig)
    print(f'scritta {USCITA}  |  {riusciti}/8 pannelli con segmentazione riuscita')
    if riusciti < 8:
        print('ATTENZIONE: alcuni pannelli sono vuoti per sicurezza. '
              'Controllare la figura prima di usarla.')


if __name__ == '__main__':
    sys.exit(main())
