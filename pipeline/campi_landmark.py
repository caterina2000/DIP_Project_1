# -*- coding: utf-8 -*-
"""
Che cosa contengono davvero i campi x, y, z e visibility.

Perche' esiste
--------------
La documentazione dice che x e y sono normalizzate fra 0 e 1, z e' una
profondita' relativa e visibility una confidenza fra 0 e 1. Sono affermazioni
generiche, e due di esse hanno conseguenze dirette su questa pipeline:

  - se x o y possono uscire da [0,1], allora moltiplicandole per larghezza e
    altezza si ottengono punti FUORI dall'immagine. Conta perche' la stima del
    pavimento usa il bordo inferiore dell'ingombro di tutti e 33 i punti: un
    punto estrapolato sotto il bordo dell'immagine sposterebbe quella stima;

  - se la visibilita' e' bassa su punti che le rappresentazioni usano, allora
    ignorarla --- come fa questa pipeline --- non e' una scelta neutra.

Invece di fidarsi della documentazione, lo script misura i quattro campi sulle
riprese del dataset e riporta i numeri.

Uso:
    python pipeline/campi_landmark.py
    python pipeline/campi_landmark.py --per-soggetto 2
"""

import argparse
import json
import os
import sys

import numpy as np

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, QUI)

import cv2
import mediapipe as mp

from src.geometry import SPALLA_SX, SPALLA_DX, ANCA_SX, ANCA_DX, PUNTI_ELLISSE
from pipeline.figura_landmark import PUNTI_A2, PUNTI_A3

RAW = os.path.join(QUI, 'dataset', 'up_fall', 'raw')
USATI = sorted(set(PUNTI_ELLISSE) | set(PUNTI_A2) | set(PUNTI_A3))


def riprese(per_soggetto, camera='cam01'):
    fuori = []
    for cat in ('adl', 'fall'):
        base = os.path.join(RAW, cat)
        if not os.path.isdir(base):
            continue
        for sog in sorted(os.listdir(base)):
            d = os.path.join(base, sog)
            if not os.path.isdir(d):
                continue
            for s in sorted(x for x in os.listdir(d) if camera in x)[:per_soggetto]:
                fuori.append((cat, os.path.join(d, s)))
    return fuori


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--per-soggetto', type=int, default=1)
    ap.add_argument('--tetto', type=int, default=150)
    a = ap.parse_args()

    elenco = riprese(a.per_soggetto)
    print('%d riprese, al massimo %d fotogrammi ciascuna' % (len(elenco), a.tetto))

    X, Y, Z, V = [], [], [], []
    Zanca, Wsca = [], []
    fuori_x = fuori_y = tot = 0
    n_pose = 0
    fuori_per_punto = np.zeros((2, 33), dtype=np.int64)
    sotto_uno = np.zeros(33, dtype=np.int64)

    for k, (cat, cartella) in enumerate(elenco, 1):
        nomi = sorted(n for n in os.listdir(cartella)
                      if n.lower().endswith(('.png', '.jpg', '.jpeg')))[:a.tetto]
        with mp.solutions.pose.Pose(static_image_mode=False,
                                    model_complexity=1,
                                    min_detection_confidence=0.5,
                                    min_tracking_confidence=0.5) as pose:
            for nome in nomi:
                img = cv2.imread(os.path.join(cartella, nome))
                if img is None:
                    continue
                r = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                if not r.pose_landmarks:
                    continue
                n_pose += 1
                lm = r.pose_landmarks.landmark
                x = np.array([l.x for l in lm])
                y = np.array([l.y for l in lm])
                X.append(x); Y.append(y)
                Z.append(np.array([l.z for l in lm]))
                V.append(np.array([l.visibility for l in lm]))
                # z sul punto medio delle anche: se l'origine e' li', deve
                # stare intorno a zero
                Zanca.append(0.5 * (lm[ANCA_SX].z + lm[ANCA_DX].z))
                fuori_x += int(((x < 0) | (x > 1)).sum())
                fuori_y += int(((y < 0) | (y > 1)).sum())
                # per punto, per sapere QUALI landmark escono: conta perche'
                # la stima del pavimento usa il bordo inferiore dell'ingombro
                # di tutti e 33, e un punto estrapolato sotto l'immagine lo
                # sposta
                fuori_per_punto[0] += ((x < 0) | (x > 1))
                fuori_per_punto[1] += ((y < 0) | (y > 1))
                sotto_uno[:] += (y > 1)
                tot += 33
                if r.pose_world_landmarks:
                    wl = r.pose_world_landmarks.landmark
                    sh = np.array([(wl[SPALLA_SX].x + wl[SPALLA_DX].x) / 2,
                                   (wl[SPALLA_SX].y + wl[SPALLA_DX].y) / 2,
                                   (wl[SPALLA_SX].z + wl[SPALLA_DX].z) / 2])
                    hp = np.array([(wl[ANCA_SX].x + wl[ANCA_DX].x) / 2,
                                   (wl[ANCA_SX].y + wl[ANCA_DX].y) / 2,
                                   (wl[ANCA_SX].z + wl[ANCA_DX].z) / 2])
                    Wsca.append(float(np.linalg.norm(sh - hp)))
        if k % 5 == 0 or k == len(elenco):
            print('   %2d/%d  %s' % (k, len(elenco), os.path.basename(cartella)))

    X = np.concatenate(X); Y = np.concatenate(Y)
    Z = np.vstack(Z); V = np.vstack(V)
    print()
    print('=' * 66)
    print('%d fotogrammi con posa, %d valori per campo' % (n_pose, X.size))
    print('=' * 66)
    print('x   min %+.3f  max %+.3f   fuori da [0,1]: %d su %d  (%.2f%%)'
          % (X.min(), X.max(), fuori_x, tot, 100 * fuori_x / tot))
    print('y   min %+.3f  max %+.3f   fuori da [0,1]: %d su %d  (%.2f%%)'
          % (Y.min(), Y.max(), fuori_y, tot, 100 * fuori_y / tot))
    print('z   min %+.3f  max %+.3f   mediana %+.3f' % (Z.min(), Z.max(),
                                                        np.median(Z)))
    za = np.asarray(Zanca)
    print('    z sul punto medio delle anche: mediana %+.4f, |z| < 0,01 nel '
          '%.1f%% dei fotogrammi' % (np.median(za), 100 * (np.abs(za) < 0.01).mean()))
    print('    -> l\'origine di z e\' il bacino' if np.abs(np.median(za)) < 0.02
          else '    -> l\'origine di z NON sembra il bacino')
    print('vis min %+.3f  max %+.3f   mediana %.3f' % (V.min(), V.max(),
                                                       np.median(V)))
    print()
    print('visibilita\' sui punti che le rappresentazioni usano')
    print('  %-4s %-8s %8s %8s %8s' % ('idx', '', 'mediana', '<0,5', '<0,9'))
    for j in USATI:
        v = V[:, j]
        print('  %-4d %-8s %8.3f %7.2f%% %7.2f%%'
              % (j, '', float(np.median(v)), 100 * (v < 0.5).mean(),
                 100 * (v < 0.9).mean()))
    altri = [j for j in range(33) if j not in USATI]
    print('  %-13s %8.3f %7.2f%% %7.2f%%   (mediana sui punti scartati)'
          % ('scartati', float(np.median(V[:, altri])),
             100 * (V[:, altri] < 0.5).mean(), 100 * (V[:, altri] < 0.9).mean()))
    print()
    print('quali punti escono sotto il bordo inferiore (y > 1)')
    ordine = np.argsort(sotto_uno)[::-1]
    for j in ordine[:8]:
        if sotto_uno[j] == 0:
            break
        print('  %2d  %6.2f%% dei fotogrammi   %s'
              % (j, 100 * sotto_uno[j] / max(n_pose, 1),
                 'USATO' if j in USATI else ''))
    usati_sotto = int(sotto_uno[USATI].sum())
    print('  sui punti usati dalle rappresentazioni: %d casi su %d'
          % (usati_sotto, n_pose * len(USATI)))

    if Wsca:
        w = np.asarray(Wsca)
        print()
        print('tronco nei world landmark: mediana %.3f, intervallo %.3f-%.3f'
              % (np.median(w), w.min(), w.max()))
        print('  -> unita\' coerenti con il metro se il valore sta fra 0,3 e 0,7')

    fuori = os.path.join(QUI, 'risultati', 'laboratorio', 'campi_landmark.json')
    os.makedirs(os.path.dirname(fuori), exist_ok=True)
    with open(fuori, 'w', encoding='utf-8') as f:
        json.dump({
            'fotogrammi_con_posa': n_pose,
            'x': {'min': float(X.min()), 'max': float(X.max()),
                  'fuori_pct': 100 * fuori_x / tot},
            'y': {'min': float(Y.min()), 'max': float(Y.max()),
                  'fuori_pct': 100 * fuori_y / tot},
            'z': {'min': float(Z.min()), 'max': float(Z.max()),
                  'mediana': float(np.median(Z)),
                  'mediana_sul_bacino': float(np.median(za))},
            'visibilita': {'mediana': float(np.median(V)),
                           'mediana_usati': float(np.median(V[:, USATI])),
                           'mediana_scartati': float(np.median(V[:, altri]))},
            'tronco_world_mediano': float(np.median(Wsca)) if Wsca else None,
        }, f, indent=1)
    print()
    print('scritto', fuori)


if __name__ == '__main__':
    main()
