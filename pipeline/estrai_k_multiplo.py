"""
Estrae le grandezze a PIU' valori di K in una sola passata di stima di posa.

Perche' esiste
--------------
`K_INTEGRALI = 31` non e' un valore fissato a priori: viene da una scansione
(EXP-053 del progetto storico) che ha confrontato cinque lunghezze misurandone
la prestazione **sui fold di prova**. E' quindi una forma di selezione sul test,
dichiarata in `sec:leakage` del Capitolo 3 (ISS-178). Per misurare quanto pesi
serve rifare la scansione DENTRO ciascun fold, come `dtw_per_fold.py` ha fatto
per la selezione delle grandezze --- e per farlo servono le feature a ogni K.

Estrarle una alla volta costerebbe 103 minuti per valore. Ma la parte cara e'
MediaPipe, non la geometria: qui lo stimatore gira UNA volta per fotogramma e
alimenta N motori geometrici, uno per K. Il costo e' quello di una estrazione
sola.

K tocca SOLTANTO le nove grandezze integrali
--------------------------------------------
`MotoreGeometrico.DURATA` governa unicamente `self._buf`, che e' usato solo da
`_integrali`. Le altre ventiquattro colonne devono quindi risultare identiche
fra i motori, e lo script lo VERIFICA invece di assumerlo: se due motori
divergono su una colonna non integrale, c'e' un difetto e l'estrazione si
ferma.

Uscita
------
Un CSV con le colonne di base piu' le nove integrali ripetute per ogni K, con
il suffisso `_k{K}`. Da li' `k_per_fold.py` costruisce il dataset a qualunque K
senza toccare le immagini.

Uso:
    conda activate fall_processing
    python pipeline/estrai_k_multiplo.py --camera 1 --k 5,15,22,31,45
"""

import argparse
import os
import re
import sys
import time

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RADICE not in sys.path:
    sys.path.insert(0, RADICE)

import pandas as pd

import config
from src.geometry import MotoreGeometrico, NOMI
from pipeline.estrai_feature import (cadenza, controlla_etichette,
                                     etichetta_da_nome, sequenze)

CAMERA = re.compile(r'cam(\d+)', re.IGNORECASE)

# Le nove che dipendono da K. Tutto il resto no, ed e' verificato.
INTEGRALI = ['A1_escursione', 'A1_percorso', 'A1_discesa',
             'A2_escursione', 'A2_percorso', 'A2_discesa',
             'A3_escursione', 'A3_percorso', 'A3_discesa']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--k', default='5,15,22,31,45',
                    help='valori di K da estrarre insieme')
    ap.add_argument('--camera', type=int, default=1,
                    help='solo questa telecamera (0 = tutte)')
    ap.add_argument('--soggetti', default='')
    ap.add_argument('--riprese', default='')
    ap.add_argument('--out', default='feature_k_multiplo.csv')
    a = ap.parse_args()

    if 'fall_processing' not in sys.executable:
        sys.exit(f"Interprete sbagliato: {sys.executable}\n"
                 f"Serve l'ambiente fall_processing.")

    import cv2
    import mediapipe as mp

    kappa = [int(x) for x in a.k.split(',') if x.strip()]
    if config.K_INTEGRALI not in kappa:
        sys.exit(f'K adottato ({config.K_INTEGRALI}) assente dall\'elenco: '
                 f'senza non si puo\' fare il controllo di riproduzione')

    voluti = {int(s) for s in a.soggetti.split(',') if s.strip()} or None
    quali = {s.strip() for s in a.riprese.split(',') if s.strip()} or None
    seqs = sequenze(voluti, quali)

    if a.camera:
        tenute = []
        for cat, sog, seq, perc in seqs:
            m = CAMERA.search(seq)
            if m and int(m.group(1)) == a.camera:
                tenute.append((cat, sog, seq, perc))
        seqs = tenute

    if not seqs:
        sys.exit('nessuna sequenza trovata')

    print('=' * 74)
    print(f'ESTRAZIONE MULTI-K — {len(seqs)} sequenze, camera {a.camera}, '
          f'K = {kappa}')
    print('=' * 74)
    print('Lo stimatore gira una volta per fotogramma; i motori geometrici')
    print(f'sono {len(kappa)}, uno per K, e ricevono gli stessi landmark.')
    print()

    # Un motore per (telecamera, K). Le osservazioni del pavimento si
    # accumulano su tutta la telecamera, come nell'estrazione normale.
    motori = {}
    righe, n_predef, t0 = [], 0, time.time()
    n_divergenze = 0

    for i, (cat, sog, seq, perc) in enumerate(seqs, 1):
        files = sorted(f for f in os.listdir(perc)
                       if f.lower().endswith(('.png', '.jpg', '.jpeg')))
        if not files:
            continue
        fps_seq, _ = cadenza(files, config.FPS_DATASET)

        m = CAMERA.search(seq)
        cam = int(m.group(1)) if m else 0
        predef = 1 if cat == 'fall' else 0
        controlla_etichette(cat, seq, files, predef)

        for k in kappa:
            mot = motori.setdefault((cam, k), MotoreGeometrico(k_integrali=k))
            mot.reset()

        # Uno stimatore per ripresa: MediaPipe Pose e' un tracciatore, e
        # riusarlo fra riprese fa dipendere le feature dall'ordine.
        pose = mp.solutions.pose.Pose(static_image_mode=False,
                                      model_complexity=1,
                                      min_detection_confidence=0.5,
                                      min_tracking_confidence=0.5)
        for j, nome in enumerate(files):
            img = cv2.imread(os.path.join(perc, nome))
            if img is None:
                continue
            h, w = img.shape[:2]
            r = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            lm = r.pose_landmarks.landmark if r.pose_landmarks else None
            wl = (r.pose_world_landmarks.landmark
                  if r.pose_world_landmarks else None)

            # LA STIMA DI POSA E' AVVENUTA UNA VOLTA SOLA. Da qui in giu'
            # costa poco: e' aritmetica su trentatre numeri.
            uscite = {k: motori[(cam, k)].fotogramma(lm, wl, w, h, fps_seq[j])
                      for k in kappa}

            rif = uscite[config.K_INTEGRALI]

            # Le colonne non integrali NON devono dipendere da K. Verificato,
            # non assunto: se divergono, la separazione fra cio' che K tocca
            # e cio' che non tocca non regge, e il confronto per fold non
            # significherebbe nulla.
            for k in kappa:
                if k == config.K_INTEGRALI:
                    continue
                for c in NOMI:
                    if c in INTEGRALI:
                        continue
                    if uscite[k][c] != rif[c]:
                        n_divergenze += 1
                        if n_divergenze <= 5:
                            print(f'  DIVERGENZA {seq} f{j} K={k} {c}: '
                                  f'{uscite[k][c]!r} != {rif[c]!r}')

            lab, usato_predef = etichetta_da_nome(nome, predef)
            n_predef += usato_predef

            if lm is not None:
                hx = (lm[23].x + lm[24].x) / 2 * w
                hy = (lm[23].y + lm[24].y) / 2 * h
            else:
                hx = hy = 0.0

            riga = {'soggetto': sog, 'categoria': cat, 'ripresa': seq,
                    'camera': cam, 'fotogramma': j, 'label': lab,
                    'ha_posa': int(lm is not None),
                    '_hip_x': hx, '_hip_y': hy}
            # le non integrali una volta sola, dal motore di riferimento
            riga.update({c: rif[c] for c in NOMI if c not in INTEGRALI})
            # le integrali una volta per K
            for k in kappa:
                for c in INTEGRALI:
                    riga[f'{c}_k{k}'] = uscite[k][c]
            righe.append(riga)

        pose.close()

        if i % 10 == 0 or i == len(seqs):
            el = time.time() - t0
            print(f'  {i:4d}/{len(seqs)}  {len(righe):8,} fotogrammi  '
                  f'{el/60:5.1f} min  (stima totale '
                  f'{el/i*len(seqs)/60:.0f} min)', flush=True)

    if n_divergenze:
        sys.exit(f'\nFERMATO: {n_divergenze} divergenze su colonne non '
                 f'integrali. K tocca dunque piu\' delle nove grandezze '
                 f'attese, e il confronto per fold non sarebbe valido.')

    d = pd.DataFrame(righe)

    # L'altezza dal pavimento non dipende da K: si rifa' una volta sola, con
    # la retta stimata su tutta la telecamera, dal motore di riferimento.
    print()
    for (cam, k), mot in sorted(motori.items()):
        if k != config.K_INTEGRALI:
            continue
        pronto, n = mot.pavimento_pronto()
        m = (d.camera == cam) & (d.ha_posa == 1) & (d.A3_torso_len > 1e-6)
        if not pronto:
            print(f'  Camera{cam}: solo {n} fotogrammi eretti, '
                  f'altezza dal pavimento non stimata (resta 0)')
            continue
        d.loc[m, 'A3_h_pavimento'] = [
            mot.altezza_su_pavimento(hx, hy, L)
            for hx, hy, L in zip(d.loc[m, '_hip_x'], d.loc[m, '_hip_y'],
                                 d.loc[m, 'A3_torso_len'])]
        a_, c_ = mot._pav_retta
        print(f'  Camera{cam}: y = {a_:+.4f}*x {c_:+.1f} '
              f'({n:,} fotogrammi eretti)')

    d.drop(columns=['_hip_x', '_hip_y'], inplace=True)

    os.makedirs(config.FEATURE_DIR, exist_ok=True)
    dst = os.path.join(config.FEATURE_DIR, a.out)
    d.to_csv(dst, index=False)

    print('\n' + '=' * 74)
    print(f'{len(d):,} fotogrammi, {d.ripresa.nunique()} riprese, '
          f'{d.soggetto.nunique()} soggetti')
    print(f'pose valide: {100*d.ha_posa.mean():.1f}%')
    print(f'nessuna divergenza sulle colonne non integrali')
    print(f'salvato in {os.path.relpath(dst, RADICE)}')
    print()
    print('Prossimo passo: il controllo di riproduzione contro feature_v5.csv')
    print('  python pipeline/k_per_fold.py --controlla')


if __name__ == '__main__':
    main()
