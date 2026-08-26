"""
Dalle sequenze di PNG al CSV delle 34 grandezze.

Un solo CSV, non quattro
------------------------
Nel progetto precedente ogni bacino aveva il suo file, e per confrontarli
bisognava rileggerli e allinearli. Qui A1, A2, A3 e le nove integrali stanno
nelle stesse righe: il DTW le confronta senza dover unire nulla, e non c'e'
modo che due colonne omonime di bacini diversi si sovrappongano.

Le etichette
------------
Vengono dal suffisso -0/-1/-2 nel nome del PNG. Se manca, vale la categoria
della cartella: 0 per le ADL, 1 per le cadute. La distinzione non e'
innocua -- in una cartella di cadute un fotogramma senza suffisso diventa
"caduta" anche se la persona e' ancora in piedi -- quindi lo script conta e
dichiara quanti fotogrammi hanno usato il valore predefinito.

Uso:
    python pipeline/estrai_feature.py                  # tutti i soggetti
    python pipeline/estrai_feature.py --soggetti 1,2   # solo alcuni
    python pipeline/estrai_feature.py --out prova.csv
"""

import argparse
import os
import re
import sys
import time

import numpy as np
import pandas as pd

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

import config
from src.geometry import MotoreGeometrico, NOMI

SUFFISSO = re.compile(r'-(\d)\.(png|jpg|jpeg)$', re.IGNORECASE)
CAMERA = re.compile(r'cam(\d+)', re.IGNORECASE)


def etichetta_da_nome(nome: str, predefinita: int):
    m = SUFFISSO.search(nome)
    return (int(m.group(1)), False) if m else (predefinita, True)


def sequenze(soggetti=None):
    """Elenca le sequenze come (categoria, soggetto, nome, percorso)."""
    fuori = []
    for cat in ('fall', 'adl'):
        base = os.path.join(config.RAW_DIR, cat)
        if not os.path.isdir(base):
            continue
        for sog in sorted(os.listdir(base)):
            n = int(sog.split('_')[-1]) if sog.split('_')[-1].isdigit() else -1
            if soggetti and n not in soggetti:
                continue
            d = os.path.join(base, sog)
            if not os.path.isdir(d):
                continue
            for seq in sorted(os.listdir(d)):
                p = os.path.join(d, seq)
                if os.path.isdir(p):
                    fuori.append((cat, sog, seq, p))
    return fuori


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--soggetti', default='',
                    help='elenco, es. 1,2 (default: tutti)')
    ap.add_argument('--out', default='feature.csv')
    ap.add_argument('--k', type=int, default=config.K_INTEGRALI)
    a = ap.parse_args()

    if 'fall_processing' not in sys.executable:
        sys.exit(f"Interprete sbagliato: {sys.executable}\n"
                 f"Serve l'ambiente fall_processing (MediaPipe 0.10.11, la "
                 f"versione con cui sono stati generati i dati esistenti).")

    import cv2
    import mediapipe as mp

    voluti = {int(s) for s in a.soggetti.split(',') if s.strip()} or None
    seqs = sequenze(voluti)
    if not seqs:
        sys.exit('nessuna sequenza trovata')

    print('=' * 74)
    print(f'ESTRAZIONE — {len(seqs)} sequenze, K integrali = {a.k}')
    print('=' * 74)

    pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1,
                                  min_detection_confidence=0.5,
                                  min_tracking_confidence=0.5)
    motore = MotoreGeometrico(k_integrali=a.k)

    righe, n_predef, t0 = [], 0, time.time()
    for i, (cat, sog, seq, perc) in enumerate(seqs, 1):
        files = sorted(f for f in os.listdir(perc)
                       if f.lower().endswith(('.png', '.jpg', '.jpeg')))
        if not files:
            continue
        m = CAMERA.search(seq)
        cam = int(m.group(1)) if m else 0
        predef = 1 if cat == 'fall' else 0

        # Lo stato va azzerato a ogni ripresa: le derivate e gli accumuli non
        # devono attraversare il confine fra due video.
        motore.reset()
        for j, nome in enumerate(files):
            img = cv2.imread(os.path.join(perc, nome))
            if img is None:
                continue
            h, w = img.shape[:2]
            r = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            lm = r.pose_landmarks.landmark if r.pose_landmarks else None
            wl = r.pose_world_landmarks.landmark if r.pose_world_landmarks else None
            f = motore.fotogramma(lm, wl, w, h, config.FPS_DATASET)

            lab, usato_predef = etichetta_da_nome(nome, predef)
            n_predef += usato_predef
            righe.append({'soggetto': sog, 'categoria': cat, 'ripresa': seq,
                          'camera': cam, 'fotogramma': j, 'label': lab,
                          'ha_posa': int(lm is not None), **f})

        if i % 10 == 0 or i == len(seqs):
            el = time.time() - t0
            print(f'  {i:4d}/{len(seqs)}  {len(righe):8,} fotogrammi  '
                  f'{el/60:5.1f} min  (stima totale {el/i*len(seqs)/60:.0f} min)',
                  flush=True)

    d = pd.DataFrame(righe)
    os.makedirs(config.FEATURE_DIR, exist_ok=True)
    dst = os.path.join(config.FEATURE_DIR, a.out)
    d.to_csv(dst, index=False)

    print('\n' + '=' * 74)
    print(f'{len(d):,} fotogrammi, {d.ripresa.nunique()} riprese, '
          f'{d.soggetto.nunique()} soggetti')
    print(f'pose valide: {100*d.ha_posa.mean():.1f}%')
    print(f'etichette dal suffisso: {100*(1-n_predef/max(len(d),1)):.1f}%  '
          f'(dalla categoria: {n_predef:,})')
    print('\ndistribuzione delle etichette:')
    for k in (0, 1, 2):
        n = int((d.label == k).sum())
        print(f'  {k}: {n:8,}  {100*n/len(d):5.1f}%')
    print(f'\ncolonne di feature: {len([c for c in d.columns if c in NOMI])}/{len(NOMI)}')
    print(f'salvato in {os.path.relpath(dst, RADICE)}')


if __name__ == '__main__':
    main()
