"""
UR-Fall con lo stesso motore geometrico di UP-Fall.

Perche' serve
-------------
UR-Fall e' l'archivio esterno su cui si misura la generalizzazione: altro
laboratorio, altre telecamere, altri soggetti. Ma il CSV che il progetto
precedente ne aveva ricavato contiene solo le dieci colonne di A3, senza gli
integrali -- cioe' senza le grandezze che misurano la DINAMICA, che sono
proprio quelle che distinguono una caduta da uno sdraiarsi volontario.

Misurato su UP-Fall, il rapporto fra le mediane di caduta e di sdraiarsi
volontario e' 30x sulla velocita' del bacino, 42x sull'escursione del tronco e
139x sulla discesa. Un modello senza quelle colonne non ha modo di usare
l'informazione, e infatti quello schierato -- A3 a dieci colonne -- su UR-Fall
allarma sull'11,6% delle finestre di persona distesa di proposito.

Questo script estrae UR-Fall con `src/geometry.py`, cioe' con lo stesso motore
e le stesse 32 grandezze di UP-Fall, cosi' che il confronto fra i due domini
sia a parita' di rappresentazione.

Le etichette
------------
NON si leggono dai nomi dei file. Il suffisso `-0` / `-1` nelle immagini
importate porta la conversione a due classi del progetto precedente, che
mescolava la transizione con lo stato (24% della transizione finita fra i
negativi). Le etichette vengono invece dalle annotazioni originali degli
autori, con la semantica di UP-Fall:

    postura originale -1  ->  0   normale
    postura originale  0  ->  1   transizione, sta cadendo   (solo riprese fall)
    postura originale +1  ->  2   a terra                    (solo riprese fall)
    qualunque postura in una ripresa ADL  ->  0

e con la colonna `disteso_volontario` a marcare i 2.289 fotogrammi di persona
distesa o in procinto di sdraiarsi durante un'attivita' quotidiana: i negativi
difficili, gli unici su cui il sistema sbaglia.

Uso:
    python pipeline/estrai_urfall.py --sorgente ../DIP_PROJECT/dataset/ur_fall
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

# UR-Fall gira a 30 fps; UP-Fall a 18. Le derivate dividono per dt, quindi il
# valore giusto va passato al motore, non assunto.
FPS_URFALL = 30.0


def annotazioni(dir_annot: str) -> pd.DataFrame:
    pezzi = []
    for nome, cat in (('urfall-cam0-falls.csv', 'fall'),
                      ('urfall-cam0-adls.csv', 'adl')):
        p = os.path.join(dir_annot, nome)
        if not os.path.exists(p):
            sys.exit(f'manca {p}')
        d = pd.read_csv(p, header=None, usecols=[0, 1, 2],
                        names=['ripresa_breve', 'frame_o', 'postura'])
        d['categoria'] = cat
        pezzi.append(d)
    return pd.concat(pezzi, ignore_index=True)


def sequenze(radice: str):
    fuori = []
    for cat in ('fall', 'adl'):
        base = os.path.join(radice, 'raw', cat)
        if not os.path.isdir(base):
            continue
        for seq in sorted(os.listdir(base)):
            p = os.path.join(base, seq)
            if os.path.isdir(p):
                fuori.append((cat, seq, p))
    return fuori


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sorgente', default=os.path.join(
        os.path.dirname(RADICE), 'DIP_PROJECT', 'dataset', 'ur_fall'))
    ap.add_argument('--out', default='feature_urfall.csv')
    ap.add_argument('--k', type=int, default=config.K_INTEGRALI)
    a = ap.parse_args()

    if 'fall_processing' not in sys.executable:
        sys.exit(f'Interprete sbagliato: {sys.executable}\n'
                 f"Serve l'ambiente fall_processing (MediaPipe 0.10.11).")

    import cv2
    import mediapipe as mp

    seqs = sequenze(a.sorgente)
    if not seqs:
        sys.exit(f'nessuna sequenza sotto {a.sorgente}/raw')
    ann = annotazioni(os.path.join(a.sorgente, 'raw', 'annotazioni'))

    print('=' * 74)
    print(f'UR-FALL — {len(seqs)} sequenze, K integrali = {a.k}, '
          f'{FPS_URFALL:.0f} fps')
    print('=' * 74)

    pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1,
                                  min_detection_confidence=0.5,
                                  min_tracking_confidence=0.5)
    motore = MotoreGeometrico(k_integrali=a.k)
    num = re.compile(r'-(\d{3})-\d\.png$', re.IGNORECASE)

    righe, t0 = [], time.time()
    for i, (cat, seq, perc) in enumerate(seqs, 1):
        files = sorted(f for f in os.listdir(perc)
                       if f.lower().endswith(('.png', '.jpg', '.jpeg')))
        if not files:
            continue
        breve = seq.replace('-cam0-rgb', '')
        motore.reset()
        for nome in files:
            m = num.search(nome)
            if not m:
                continue
            frame_o = int(m.group(1))          # numerazione originale, da 1
            img = cv2.imread(os.path.join(perc, nome))
            if img is None:
                continue
            h, w = img.shape[:2]
            r = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            lm = r.pose_landmarks.landmark if r.pose_landmarks else None
            wl = r.pose_world_landmarks.landmark if r.pose_world_landmarks else None
            f = motore.fotogramma(lm, wl, w, h, FPS_URFALL)
            righe.append({'soggetto': breve, 'categoria': cat, 'ripresa': seq,
                          'ripresa_breve': breve, 'camera': 0,
                          'fotogramma': frame_o - 1, 'frame_o': frame_o,
                          'ha_posa': int(lm is not None), **f})
        if i % 10 == 0 or i == len(seqs):
            el = time.time() - t0
            print(f'  {i:3d}/{len(seqs)}  {len(righe):7,} fotogrammi  '
                  f'{el/60:5.1f} min', flush=True)

    d = pd.DataFrame(righe)
    d = d.merge(ann[['ripresa_breve', 'frame_o', 'postura']],
                on=['ripresa_breve', 'frame_o'], how='left')

    caduta = d.categoria == 'fall'
    d['label'] = 0
    d.loc[caduta & (d.postura == 0), 'label'] = 1     # transizione
    d.loc[caduta & (d.postura == 1), 'label'] = 2     # a terra
    d['disteso_volontario'] = ((d.categoria == 'adl') &
                               d.postura.isin([0, 1])).astype(int)

    os.makedirs(config.FEATURE_DIR, exist_ok=True)
    dst = os.path.join(config.FEATURE_DIR, a.out)
    d.drop(columns=['frame_o', 'ripresa_breve']).to_csv(dst, index=False)

    print('\n' + '=' * 74)
    print(f'{len(d):,} fotogrammi, {d.ripresa.nunique()} riprese')
    print(f'pose valide: {100*d.ha_posa.mean():.1f}%')
    print(f'annotazione trovata: {100*d.postura.notna().mean():.1f}%')
    print(f'colonne di feature: {len([c for c in d.columns if c in NOMI])}/{len(NOMI)}')
    print('\netichette:')
    for k in (0, 1, 2):
        n = int((d.label == k).sum())
        print(f'  {k}: {n:7,}  {100*n/len(d):5.1f}%')
    print(f'negativi difficili (distesi volontari): '
          f'{int(d.disteso_volontario.sum()):,}')
    print(f'\nsalvato in {os.path.relpath(dst, RADICE)}')


if __name__ == '__main__':
    main()
