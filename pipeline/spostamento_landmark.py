# -*- coding: utf-8 -*-
"""
Quanto si sposta ogni landmark da un fotogramma al successivo.

Perche' esiste
--------------
Il capitolo afferma che le coordinate dei landmark sono stime e oscillano
anche quando il corpo si muove poco, e che l'instabilita' non e' la stessa per
tutti i punti. Finora era un'affermazione senza numeri accanto. Questo script
li misura: per ogni landmark, la distribuzione dello spostamento fra fotogrammi
consecutivi, separata fra riprese di attivita' quotidiana e riprese di caduta.

Rispetto al bacino, non nell'immagine
-------------------------------------
La prima versione misurava lo spostamento nel piano immagine e dava un
risultato che non rispondeva alla domanda: le riprese di attivita' quotidiana
uscivano PIU' mosse di quelle di caduta (naso, mediana 0,0080 contro 0,0051) e
il terzo quartile valeva circa 0,055 per quasi tutti e trentatre' i punti,
uguale per il naso e per il mignolo.

La spiegazione e' che quella misura era dominata dalla traslazione della
persona. Le ADL campionate sono camminata e stazione eretta, e camminare
sposta tutti i punti della stessa quantita'; una caduta invece e' quasi tutta
statica --- avvicinamento, un istante di caduta, poi immobile a terra ---
quindi la mediana la fanno i fotogrammi fermi.

Qui lo spostamento e' quindi misurato RISPETTO AL BACINO: si sottrae lo
spostamento del punto medio delle anche prima di misurare quello di ciascun
punto. Resta il moto del punto rispetto al corpo, che e' la grandezza che
interessa: quanto quella stima balla, non quanto la persona cammina.

Normalizzazione
---------------
Lo spostamento e' diviso per la lunghezza del tronco, la stessa scala che usa
A3 e la stessa dell'esperimento sul rumore. Senza, una persona ripresa da
vicino sembrerebbe muoversi il doppio di una lontana e il confronto fra
soggetti non starebbe in piedi.

Che cosa NON e'
---------------
Non e' una misura di errore. Non esiste una verita' di riferimento sui
landmark di UP-Fall: nessuno ha annotato a mano dove stiano davvero i punti.
E' una misura di quanto il segnale si muove, e sulle ADL e' un limite
superiore al rumore, non il rumore.

Uso:
    python pipeline/spostamento_landmark.py
    python pipeline/spostamento_landmark.py --per-soggetto 6
    python pipeline/spostamento_landmark.py --solo-dati        # niente figura
"""

import argparse
import json
import os
import re
import sys
import time

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, QUI)

import cv2
import mediapipe as mp

from src.geometry import (SPALLA_SX, SPALLA_DX, ANCA_SX, ANCA_DX,
                          PUNTI_ELLISSE)
from pipeline.figura_landmark import BLU, GRIGIO, ROSSO, VERDE, PUNTI_A2, PUNTI_A3

RAW = os.path.join(QUI, 'dataset', 'up_fall', 'raw')
USATI = sorted(set(PUNTI_ELLISSE) | set(PUNTI_A2) | set(PUNTI_A3))

# i nomi dei 33 punti di MediaPipe, per l'asse della figura
NOMI33 = [
    'naso', 'occhio sx int', 'occhio sx', 'occhio sx est', 'occhio dx int',
    'occhio dx', 'occhio dx est', 'orecchio sx', 'orecchio dx', 'bocca sx',
    'bocca dx', 'spalla sx', 'spalla dx', 'gomito sx', 'gomito dx',
    'polso sx', 'polso dx', 'mignolo sx', 'mignolo dx', 'indice sx',
    'indice dx', 'pollice sx', 'pollice dx', 'anca sx', 'anca dx',
    'ginocchio sx', 'ginocchio dx', 'caviglia sx', 'caviglia dx',
    'tallone sx', 'tallone dx', 'punta sx', 'punta dx']

# gli stessi, con i nomi che usa MediaPipe
NOMI33_EN = [
    'nose', 'left eye inner', 'left eye', 'left eye outer', 'right eye inner',
    'right eye', 'right eye outer', 'left ear', 'right ear', 'mouth left',
    'mouth right', 'left shoulder', 'right shoulder', 'left elbow',
    'right elbow', 'left wrist', 'right wrist', 'left pinky', 'right pinky',
    'left index', 'right index', 'left thumb', 'right thumb', 'left hip',
    'right hip', 'left knee', 'right knee', 'left ankle', 'right ankle',
    'left heel', 'right heel', 'left foot index', 'right foot index']

TESTI = {
    'it': {
        'nomi': NOMI33,
        'adl': 'attività quotidiana', 'fall': 'caduta',
        'y': 'spostamento rispetto al bacino\n'
             'fra fotogrammi consecutivi [lunghezze di tronco]',
        'titolo': 'Spostamento di ciascun landmark rispetto al bacino fra '
                  'fotogrammi consecutivi: mediana e intervallo '
                  'interquartile\nsu %d riprese di attività quotidiana e %d '
                  'di caduta. In giallo i punti impiegati dalle '
                  'rappresentazioni.',
    },
    'en': {
        'nomi': NOMI33_EN,
        'adl': 'daily activity', 'fall': 'fall',
        'y': 'displacement relative to the hips\n'
             'between consecutive frames [torso lengths]',
        'titolo': 'Displacement of each landmark relative to the hips between '
                  'consecutive frames: median and interquartile\nrange over '
                  '%d daily-activity and %d fall recordings. In yellow, the '
                  'points used by the representations.',
    },
}


def riprese(per_soggetto, camera='cam01'):
    """Alcune riprese per soggetto e per categoria, sempre le stesse.

    Non a caso: si prendono le prime in ordine alfabetico, cosi' due
    esecuzioni danno lo stesso insieme e il numero non cambia sotto i piedi."""
    fuori = []
    for cat in ('adl', 'fall'):
        base = os.path.join(RAW, cat)
        if not os.path.isdir(base):
            continue
        for sog in sorted(os.listdir(base)):
            d = os.path.join(base, sog)
            if not os.path.isdir(d):
                continue
            seqs = sorted(s for s in os.listdir(d) if camera in s)
            for s in seqs[:per_soggetto]:
                fuori.append((cat, sog, os.path.join(d, s)))
    return fuori


def misura(cartella, tetto):
    """Gli spostamenti fra fotogrammi consecutivi, in lunghezze di tronco.

    Lo stimatore e' creato QUI, per questa ripresa, e muore alla fine: la
    stessa condizione dell'estrazione. Una coppia conta solo se entrambi i
    fotogrammi hanno la posa --- a cavallo di un buco non c'e' spostamento,
    c'e' un'interruzione."""
    nomi = sorted(n for n in os.listdir(cartella)
                  if n.lower().endswith(('.png', '.jpg', '.jpeg')))[:tetto]
    fuori = [[] for _ in range(33)]
    prec = None
    with mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1,
                                min_detection_confidence=0.5,
                                min_tracking_confidence=0.5) as pose:
        for nome in nomi:
            img = cv2.imread(os.path.join(cartella, nome))
            if img is None:
                prec = None
                continue
            h, w = img.shape[:2]
            r = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            if not r.pose_landmarks:
                prec = None
                continue
            lm = r.pose_landmarks.landmark
            P = np.array([[l.x * w, l.y * h] for l in lm], np.float64)
            sh = (P[SPALLA_SX] + P[SPALLA_DX]) / 2.0
            hip = (P[ANCA_SX] + P[ANCA_DX]) / 2.0
            L = float(np.linalg.norm(sh - hip))
            if L < 1e-6:
                prec = None
                continue
            if prec is not None:
                Pp, Lp, hipp = prec
                # la scala e' la media dei due tronchi: se si usasse solo
                # quello nuovo, un fotogramma in cui il tronco si accorcia
                # per la prospettiva gonfierebbe tutti gli spostamenti
                s = 0.5 * (L + Lp)
                # RELATIVO AL BACINO, non nell'immagine. Misurato
                # nell'immagine, camminare sposta tutti e 33 i punti della
                # stessa quantita' e quello che si legge e' la traslazione
                # della persona, non il ballo delle stime: infatti sulle ADL
                # --- camminata --- usciva piu' grande che sulle cadute, e il
                # terzo quartile era quasi identico per ogni punto. Togliendo
                # lo spostamento del bacino resta il moto di ciascun punto
                # RISPETTO al corpo, che e' la grandezza di interesse.
                d = np.linalg.norm((P - hip) - (Pp - hipp), axis=1) / s
                for j in range(33):
                    fuori[j].append(float(d[j]))
            prec = (P, L, hip)
    return fuori


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--per-soggetto', type=int, default=2,
                    help='riprese per soggetto e per categoria (10 soggetti '
                         'x 2 categorie x questo numero)')
    ap.add_argument('--tetto', type=int, default=400,
                    help='fotogrammi al massimo per ripresa')
    ap.add_argument('--dove', default=os.path.join(QUI, 'tesi', 'figure'))
    ap.add_argument('--solo-dati', action='store_true')
    ap.add_argument('--lingua', default='it', choices=('it', 'en'))
    ap.add_argument('--da-json', action='store_true',
                    help='ridisegna da fig_spostamento.json senza rimisurare')
    a = ap.parse_args()

    elenco = riprese(a.per_soggetto)
    if not elenco:
        sys.exit('nessuna ripresa trovata sotto ' + RAW)
    print('%d riprese, al massimo %d fotogrammi ciascuna'
          % (len(elenco), a.tetto))

    fuori_json = os.path.join(a.dove, 'fig_spostamento.json')
    if a.da_json:
        # ridisegnare senza rimisurare: la misura costa una decina di minuti
        # e la figura si ritocca piu' spesso di quanto i dati cambino
        with open(fuori_json, encoding='utf-8') as f:
            salvato = json.load(f)
        print('letto %s (%d ADL, %d caduta)'
              % (fuori_json, salvato['riprese']['adl'],
                 salvato['riprese']['fall']))
        disegna(salvato['statistiche'], salvato['riprese'], a)
        return

    dati = {'adl': [[] for _ in range(33)], 'fall': [[] for _ in range(33)]}
    conta = {'adl': 0, 'fall': 0}
    t0 = time.time()
    for k, (cat, sog, perc) in enumerate(elenco, 1):
        d = misura(perc, a.tetto)
        for j in range(33):
            dati[cat][j].extend(d[j])
        conta[cat] += 1
        if k % 5 == 0 or k == len(elenco):
            el = time.time() - t0
            print('  %3d/%d  %s  %.1f min (stima totale %.1f)'
                  % (k, len(elenco), os.path.basename(perc), el / 60,
                     el / 60 * len(elenco) / k))

    riga = {}
    for cat in ('adl', 'fall'):
        riga[cat] = []
        for j in range(33):
            v = np.asarray(dati[cat][j], np.float64)
            riga[cat].append({
                'n': int(v.size),
                'mediana': float(np.median(v)) if v.size else float('nan'),
                'q25': float(np.percentile(v, 25)) if v.size else float('nan'),
                'q75': float(np.percentile(v, 75)) if v.size else float('nan'),
                'q90': float(np.percentile(v, 90)) if v.size else float('nan'),
            })

    os.makedirs(a.dove, exist_ok=True)
    with open(fuori_json, 'w', encoding='utf-8') as f:
        json.dump({'riprese': conta, 'tetto': a.tetto,
                   'per_soggetto': a.per_soggetto,
                   'nomi': NOMI33, 'usati': USATI, 'statistiche': riga},
                  f, indent=1)
    print('scritto', fuori_json)
    if a.solo_dati:
        return

    disegna(riga, conta, a)


def disegna(riga, conta, a):
    t = TESTI[a.lingua]
    nomi = t['nomi']
    x = np.arange(33)
    fig, ax = plt.subplots(figsize=(11.5, 4.6))
    fig.patch.set_facecolor('white')

    for cat, colore, scarto, eti in (
            ('adl', VERDE, -0.17, t['adl']),
            ('fall', BLU, 0.17, t['fall'])):
        med = np.array([r['mediana'] for r in riga[cat]])
        q25 = np.array([r['q25'] for r in riga[cat]])
        q75 = np.array([r['q75'] for r in riga[cat]])
        ax.vlines(x + scarto, q25, q75, color=colore, lw=4.5, alpha=0.32)
        ax.plot(x + scarto, med, 'o', ms=5.5, color=colore, mec='white',
                mew=1.0, label=eti, zorder=4, ls='none')

    # i punti che le rappresentazioni usano davvero
    for j in USATI:
        ax.axvspan(j - 0.5, j + 0.5, color='#f2c94c', alpha=0.13, zorder=0)

    ax.set_xticks(x)
    ax.set_xticklabels(['%d  %s' % (j, nomi[j]) for j in x], rotation=90,
                       fontsize=7.5)
    for e in ax.get_xticklabels():
        j = int(e.get_text().split()[0])
        if j in USATI:
            e.set_fontweight('bold')
            e.set_color('#1d2b36')
        else:
            e.set_color('#8a99a6')
    ax.set_ylabel(t['y'], fontsize=9.5)
    ax.set_yscale('log')
    ax.grid(axis='y', color='#e3e9ee', lw=0.8)
    ax.set_axisbelow(True)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'):
        ax.spines[s].set_edgecolor('#b9c6d2')
    ax.legend(frameon=False, fontsize=9.5, loc='upper left', ncol=2)
    # niente titolo sopra la figura: la spiegazione sta nella didascalia del
    # capitolo, e ripeterla qui la farebbe leggere due volte
    fig.tight_layout()
    suff = '' if a.lingua == 'it' else '_en'
    fuori = os.path.join(a.dove, 'fig_spostamento%s.png' % suff)
    fig.savefig(fuori, dpi=400, facecolor='white', bbox_inches='tight')
    print('scritto', fuori)

    with open(os.path.join(a.dove, 'fig_spostamento%s.txt' % suff), 'w',
              encoding='utf-8') as f:
        f.write('spostamento per landmark fra fotogrammi consecutivi,\n')
        f.write('RISPETTO AL BACINO, in lunghezze di tronco, '
                'mediana [q25-q75]\n\n')
        f.write('riprese: %d ADL, %d caduta, camera 1, max %d fotogrammi\n\n'
                % (conta['adl'], conta['fall'], a.tetto))
        f.write('%-4s %-16s %-22s %-22s %s\n'
                % ('idx', 'punto', 'ADL', 'caduta', 'usato'))
        for j in range(33):
            A, F = riga['adl'][j], riga['fall'][j]
            f.write('%-4d %-16s %6.4f [%.4f-%.4f]  %6.4f [%.4f-%.4f]  %s\n'
                    % (j, nomi[j], A['mediana'], A['q25'], A['q75'],
                       F['mediana'], F['q25'], F['q75'],
                       'si' if j in USATI else ''))
        f.write('\ncoppie contate: %d per landmark sulle ADL, %d sulle cadute\n'
                % (riga['adl'][0]['n'], riga['fall'][0]['n']))

        # I due gruppi che il capitolo confronta. Le anche restano FUORI dal
        # gruppo degli usati: sono il riferimento da cui si sottrae, quindi il
        # loro spostamento relativo e' piccolo per costruzione e non e'
        # confrontabile con gli altri.
        anche = [ANCA_SX, ANCA_DX]
        usati_veri = [j for j in USATI if j not in anche]
        mani = list(range(15, 23))
        f.write('\nriassunto (mediana delle mediane)\n')
        for cat, eti in (('adl', 'ADL'), ('fall', 'caduta')):
            u = float(np.median([riga[cat][j]['mediana'] for j in usati_veri]))
            m = float(np.median([riga[cat][j]['mediana'] for j in mani]))
            f.write('  %-7s punti impiegati (senza le anche) %.4f\n'
                    '          polsi e dita                  %.4f   '
                    '%.1f volte tanto\n' % (eti, u, m, m / u if u else 0))
        f.write('  le anche (23, 24) valgono %.4f su ADL, ma sono il punto da\n'
                '  cui si sottrae: il loro valore non e comparabile.\n'
                % riga['adl'][ANCA_SX]['mediana'])


if __name__ == '__main__':
    main()
