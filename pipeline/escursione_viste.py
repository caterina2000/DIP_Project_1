# -*- coding: utf-8 -*-
"""
L'escursione dell'angolo del tronco per punto di vista, rimisurata pulita.

Perche' esiste
--------------
La misura la produce oggi `DIP_PROJECT/scripts/check_camera_viewpoint.py`, e
quel file crea **un solo** stimatore di posa e lo passa a tutte e cinquanta le
sequenze del ciclo. MediaPipe Pose e' un tracciatore: mantiene stato fra una
chiamata e la successiva, e non sa che fra due chiamate e' cambiata la
sequenza. L'ultimo fotogramma di una ripresa --- persona a terra --- innesca
quindi il primo fotogramma della ripresa dopo, dove la persona e' in piedi.

Lo scarto e' misurabile, ed e' stato misurato su `sub01_act01_trial01`:

    stimatore condiviso   cam02  escursione 31,30°   (identico al CSV)
    stimatore per ripresa cam02  escursione 29,23°

cioe' il 7% su quella sequenza. Su cam01 non cambia nulla, perche' li'
l'escursione e' satura: il tronco passa da verticale a orizzontale e i due
estremi sono agli estremi del campo.

Questo script rifa' la stessa misura con **uno stimatore per ripresa**, che e'
la condizione in cui il sistema lavora davvero: quando si accende, non ha
visto la sequenza precedente.

Che cosa NON cambia
-------------------
Il protocollo, in tutto il resto: un fotogramma ogni tre, immagine a meta'
risoluzione, `model_complexity=1`, soglie 0,5, e le due definizioni
dell'angolo --- quella 3D sui world landmark e quella 2D nel piano immagine,
ripiegata in [0, 90]. Cambiare anche una di queste renderebbe i due CSV non
confrontabili, ed e' il confronto il punto di questo script.

Il secondo difetto, trovato mentre si sistemava il primo
---------------------------------------------------------
Su `sub01_act01_trial01_cam02` lo stimatore **perde il soggetto quando cade e
si aggancia a un astante seduto**: l'anca tracciata salta da x = 0,50 a
x = 0,87 e ci resta per trentaquattro campioni su sessantacinque, cioe' per
tutta la fase «a terra». L'angolo del tronco misurato in quei campioni e'
quello di una persona **seduta**, e vale 85-87°.

Il che vuol dire che l'escursione compressa di Camera2, su quella sequenza,
non misura la compressione prospettica: misura un'altra persona. Per questo lo
script registra anche la **traiettoria dell'anca** e segnala i salti
([ISS-134](../docs/ISSUES.md#iss-134)).

Uscita
------
`risultati/cinque_soggetti/exp013_camera_viewpoint_indipendente.csv`, con le
stesse colonne dell'originale piu' tre che riguardano il salto.
**L'originale non viene toccato**: i due file stanno accanto, e la differenza
fra loro e' il dato.

Accanto, `exp013_serie.json` con la serie per campione --- classe annotata,
anca, angolo --- di tutte e cinquanta le riprese. Serve perche' il criterio
con cui si dichiara un salto e' una scelta, e chi la vuole diversa deve poterla
rifare **senza rieseguire due ore di stima di posa**. E' la stessa ragione per
cui i punteggi per fold stanno in `risultati/addestramento/*.npz`.

    python pipeline/escursione_viste.py

Ambiente: `fall_processing`. Circa due ore su cinquanta riprese.
"""

import argparse
import csv
import json
import os
import statistics as st
import sys

import numpy as np

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if QUI not in sys.path:
    sys.path.insert(0, QUI)

PASSO = 3
SCALA = 0.5
SPALLA_SX, SPALLA_DX, ANCA_SX, ANCA_DX = 11, 12, 23, 24

# Un salto dell'anca fra due campioni consecutivi oltre questa soglia, in
# coordinate normalizzate e sommando le due componenti, e' dichiarato cambio
# di persona. Il valore non e' scelto a occhio: sulla ripresa dove il cambio
# e' stato visto a video il salto vale 0,59, mentre il passo piu' grande di
# una caduta seguita correttamente, sulla telecamera laterale della stessa
# ripresa, vale 0,31. La soglia sta in mezzo, piu' vicina al caso vero.
# La serie per campione e' salvata, quindi chi la vuole diversa la rifa'
# senza rieseguire la stima di posa.
SOGLIA_SALTO = 0.45

RAW = os.path.join('dataset', 'up_fall', 'raw', 'fall')
USCITA = os.path.join('risultati', 'cinque_soggetti',
                      'exp013_camera_viewpoint_indipendente.csv')
SERIE = os.path.join('risultati', 'cinque_soggetti', 'exp013_serie.json')
ORIGINALE = os.path.join('risultati', 'cinque_soggetti',
                         'exp013_camera_viewpoint.csv')

COLONNE = ['subject', 'activity', 'trial', 'camera', 'name', 'exc_3d',
           'exc_2d', 'min_3d', 'max_3d', 'min_2d', 'max_2d', 'det_pct',
           'salto_max', 'salto_a', 'exc_2d_prima_del_salto']


def classe(nome):
    """La classe del fotogramma, dal suffisso del nome del file UP-Fall."""
    coda = os.path.splitext(nome)[0].rsplit('-', 1)[-1]
    return int(coda) if coda.isdigit() else None


def angoli(cartella):
    """
    La serie per campione su una ripresa, con uno stimatore tutto suo.

    Lo stimatore per ripresa e' l'unica differenza rispetto all'originale, ed
    e' deliberata: nasce qui e muore alla fine della ripresa, quindi non porta
    dentro nulla di quella prima.

    Di ogni campione si tiene anche la posizione dell'anca in coordinate
    normalizzate. Non serve a calcolare l'angolo: serve a sapere **di chi** e'
    l'angolo. Senza, un cambio di persona e' invisibile nei numeri.
    """
    import cv2
    import mediapipe as mp

    files = sorted(f for f in os.listdir(cartella)
                   if f.lower().endswith(('.png', '.jpg', '.jpeg')))
    campioni = files[::PASSO]

    pose = mp.solutions.pose.Pose(min_detection_confidence=.5,
                                  min_tracking_confidence=.5,
                                  model_complexity=1)
    serie, n_det = [], 0
    for nome in campioni:
        img = cv2.imread(os.path.join(cartella, nome))
        if img is None:
            continue
        img = cv2.resize(img, None, fx=SCALA, fy=SCALA,
                         interpolation=cv2.INTER_AREA)
        r = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        d = {'classe': classe(nome), 'a3d': None, 'a2d': None,
             'anca_x': None, 'anca_y': None}

        if r.pose_world_landmarks:
            n_det += 1
            w = r.pose_world_landmarks.landmark
            msp = np.array([(w[SPALLA_SX].x + w[SPALLA_DX].x) / 2,
                            (w[SPALLA_SX].y + w[SPALLA_DX].y) / 2,
                            (w[SPALLA_SX].z + w[SPALLA_DX].z) / 2])
            man = np.array([(w[ANCA_SX].x + w[ANCA_DX].x) / 2,
                            (w[ANCA_SX].y + w[ANCA_DX].y) / 2,
                            (w[ANCA_SX].z + w[ANCA_DX].z) / 2])
            v = msp - man
            n = float(np.linalg.norm(v))
            if n > 1e-8:
                cos = float(np.dot(v, np.array([0., -1., 0.]))) / n
                d['a3d'] = float(np.degrees(np.arccos(np.clip(cos, -1, 1))))

        if r.pose_landmarks:
            p = r.pose_landmarks.landmark
            h, wd = img.shape[:2]
            sx = (p[SPALLA_SX].x + p[SPALLA_DX].x) / 2 * wd
            sy = (p[SPALLA_SX].y + p[SPALLA_DX].y) / 2 * h
            hx = (p[ANCA_SX].x + p[ANCA_DX].x) / 2 * wd
            hy = (p[ANCA_SX].y + p[ANCA_DX].y) / 2 * h
            dx, dy = sx - hx, sy - hy
            if abs(dx) + abs(dy) > 1e-6:
                a = abs(float(np.degrees(np.arctan2(-dy, dx))))
                d['a2d'] = 180 - a if a > 90 else a
            d['anca_x'] = float((p[ANCA_SX].x + p[ANCA_DX].x) / 2)
            d['anca_y'] = float((p[ANCA_SX].y + p[ANCA_DX].y) / 2)

        serie.append(d)

    pose.close()
    return serie, len(campioni), n_det


def salti(serie, soglia=SOGLIA_SALTO):
    """
    Dove la persona tracciata cambia, e quanto vale il salto piu' grande.

    Il criterio e' lo spostamento dell'anca fra due campioni **con posa**
    consecutivi, sommando le due componenti. I campioni senza posa non
    interrompono il confronto: il cambio avviene proprio li', quando lo
    stimatore perde il soggetto e il rilevatore riparte da capo agganciando
    chi e' piu' evidente nell'inquadratura.
    """
    prec, massimo, dove = None, 0.0, None
    for i, d in enumerate(serie):
        if d['anca_x'] is None:
            continue
        if prec is not None:
            s = abs(d['anca_x'] - prec[0]) + abs(d['anca_y'] - prec[1])
            if s > massimo:
                massimo, dove = s, i
        prec = (d['anca_x'], d['anca_y'])
    return massimo, (dove if massimo > soglia else None)


def escursione(serie, fino=None):
    v = [d['a2d'] for d in serie[:fino] if d['a2d'] is not None]
    return (max(v) - min(v)) if len(v) >= 5 else None


def riepilogo(percorso_csv, dest=None):
    """
    Le statistiche aggregate, in un file accanto al CSV.

    Medie, deviazioni, rapporti e conteggi sono **derivati**: nel CSV ci sono
    le singole riprese, non la loro media. Finche' restavano solo stampati a
    schermo, ogni numero della sezione sul punto di vista era un numero senza
    artefatto, che `pipeline/audit_numeri.py` segnala e giustamente.

    Si calcola dal CSV, quindi non richiede di rifare la stima di posa.
    """
    with open(percorso_csv, newline='') as f:
        righe = list(csv.DictReader(f))
    c = {}
    for r in righe:
        c.setdefault((r['subject'], r['activity'], r['trial']), {})[
            r['camera']] = r
    coppie = {k: v for k, v in c.items() if '1' in v and '2' in v}
    pulite = {k: v for k, v in coppie.items()
              if not (v['1']['salto_a'] or v['2']['salto_a'])}

    def blocco(gruppo):
        e1 = [float(v['1']['exc_2d']) for v in gruppo.values()]
        e2 = [float(v['2']['exc_2d']) for v in gruppo.values()]
        rp = sorted(a / b for a, b in zip(e1, e2))
        return {
            'n_coppie': len(e1),
            'cam1_media': st.mean(e1),
            'cam2_media': st.mean(e2),
            'cam1_dev': st.stdev(e1) if len(e1) > 1 else 0.0,
            'cam2_dev': st.stdev(e2) if len(e2) > 1 else 0.0,
            'rapporto_fra_le_medie': st.mean(e1) / st.mean(e2),
            'rapporto_per_sequenza_min': rp[0],
            'rapporto_per_sequenza_max': rp[-1],
            'rapporto_per_sequenza_mediano': st.median(rp),
            'cam1_sopra_60': sum(v > 60 for v in e1),
            'cam2_sopra_60': sum(v > 60 for v in e2),
            'sequenze_cam2_maggiore_o_uguale': sum(x <= 1 for x in rp),
        }

    d = {
        'sorgente': os.path.basename(percorso_csv),
        'soglia_salto': SOGLIA_SALTO,
        'tutte': blocco(coppie),
        'senza_cambio_di_persona': blocco(pulite),
        'cambi_di_persona': {
            'cam1': sum(1 for v in coppie.values() if v['1']['salto_a'] != ''),
            'cam2': sum(1 for v in coppie.values() if v['2']['salto_a'] != ''),
            'su': len(coppie),
        },
        'posa_rilevata_media': {
            'cam1': st.mean([float(v['1']['det_pct'])
                             for v in coppie.values()]),
            'cam2': st.mean([float(v['2']['det_pct'])
                             for v in coppie.values()]),
        },
        'salto_massimo_osservato': {
            'cam1': max(float(v['1']['salto_max']) for v in coppie.values()),
            'cam2': max(float(v['2']['salto_max']) for v in coppie.values()),
        },
    }
    dest = dest or (os.path.splitext(percorso_csv)[0] + '_riepilogo.json')
    with open(dest, 'w') as f:
        json.dump(d, f, indent=2)
    return dest, d


def riprese(radice, soggetti):
    fuori = []
    for s in soggetti:
        cart = os.path.join(radice, 'Subject_%02d' % s)
        if not os.path.isdir(cart):
            continue
        for nome in sorted(os.listdir(cart)):
            if not nome.endswith(('_cam01', '_cam02')):
                continue
            # sub01_act01_trial01_cam01
            pezzi = nome.split('_')
            fuori.append({
                'subject': s,
                'activity': int(pezzi[1][3:]),
                'trial': int(pezzi[2][5:]),
                'camera': int(pezzi[3][3:]),
                'name': nome,
                'path': os.path.join(cart, nome),
            })
    return fuori


def confronta(righe):
    """Le due misure affiancate, che e' il motivo per cui lo script esiste."""
    percorso = os.path.join(QUI, ORIGINALE)
    if not os.path.isfile(percorso):
        return
    vecchio = {}
    with open(percorso, newline='') as f:
        for r in csv.DictReader(f):
            vecchio[r['name']] = float(r['exc_2d'])

    print()
    print('=' * 72)
    print('CONFRONTO CON LA MISURA A STIMATORE CONDIVISO')
    print('=' * 72)
    print('%-28s %9s %9s %8s' % ('sequenza', 'condiv.', 'pulito', 'scarto'))
    scarti = []
    for r in righe:
        v = vecchio.get(r['name'])
        if v is None:
            continue
        d = r['exc_2d'] - v
        scarti.append(d)
        print('%-28s %9.2f %9.2f %+8.2f' % (r['name'], v, r['exc_2d'], d))

    for cam, etichetta in ((1, 'Camera1'), (2, 'Camera2')):
        n = [r for r in righe if r['camera'] == cam]
        v = [vecchio[r['name']] for r in n if r['name'] in vecchio]
        p = [r['exc_2d'] for r in n if r['name'] in vecchio]
        if not v:
            continue
        print()
        print('%s  media condivisa %.1f°   pulita %.1f°   sopra 60°: %d -> %d'
              % (etichetta, st.mean(v), st.mean(p),
                 sum(x > 60 for x in v), sum(x > 60 for x in p)))

    m1 = [r['exc_2d'] for r in righe if r['camera'] == 1]
    m2 = [r['exc_2d'] for r in righe if r['camera'] == 2]
    if m1 and m2:
        print()
        print('rapporto fra le medie, misura pulita: %.2f×'
              % (st.mean(m1) / st.mean(m2)))
    if scarti:
        print('scarto medio %+.2f°, massimo in valore assoluto %.2f°'
              % (st.mean(scarti), max(abs(x) for x in scarti)))

    print()
    print('=' * 72)
    print('CAMBI DI PERSONA (salto dell\'anca oltre %.2f)' % SOGLIA_SALTO)
    print('=' * 72)
    for cam, etichetta in ((1, 'Camera1'), (2, 'Camera2')):
        n = [r for r in righe if r['camera'] == cam]
        con = [r for r in n if r['salto_a'] != '']
        print('%s  %d riprese su %d con un cambio di persona'
              % (etichetta, len(con), len(n)))
        for r in con:
            print('    %-28s salto %.2f al campione %s, escursione %s -> %s'
                  % (r['name'], r['salto_max'], r['salto_a'],
                     ('%.1f°' % r['exc_2d']),
                     ('%.1f°' % r['exc_2d_prima_del_salto']
                      if r['exc_2d_prima_del_salto'] != '' else '---')))
    print()
    print('Una ripresa con un cambio di persona non misura l\'escursione del')
    print('soggetto: la misura va rifatta o la ripresa va esclusa.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--radice', default=os.path.join(QUI, RAW))
    ap.add_argument('--soggetti', default='1,2,3,4,5')
    ap.add_argument('--uscita', default=os.path.join(QUI, USCITA))
    # la serie va accanto al CSV, non in una cartella fissa: una misura a
    # dieci soggetti scritta in `cinque_soggetti/` e' un file che mente
    ap.add_argument('--solo-riepilogo', action='store_true',
                    dest='solo_riepilogo',
                    help="ricalcola le statistiche aggregate dal CSV gia' "
                         "prodotto, senza rifare la stima di posa")
    ap.add_argument('--serie', default=None,
                    help='dove scrivere la serie per campione. Senza, '
                         'accanto al CSV con suffisso _serie.json')
    a = ap.parse_args()

    if a.solo_riepilogo:
        dest, d = riepilogo(a.uscita)
        print('scritto   ', dest)
        p = d['senza_cambio_di_persona']
        print('senza cambi: %d coppie, cam1 %.1f, cam2 %.1f, rapporto %.2f'
              % (p['n_coppie'], p['cam1_media'], p['cam2_media'],
                 p['rapporto_fra_le_medie']))
        return

    radice = a.radice
    if not os.path.isdir(radice):
        alt = os.path.abspath(os.path.join(QUI, '..', 'DIP_PROJECT', RAW))
        if os.path.isdir(alt):
            radice = alt
        else:
            sys.exit('dataset non trovato: indicarlo con --radice')

    soggetti = [int(x) for x in a.soggetti.split(',')]
    elenco = riprese(radice, soggetti)
    print('radice    ', radice)
    print('riprese   ', len(elenco))
    print()
    print('%-28s %4s %6s %8s %8s' % ('sequenza', 'cam', 'det%', 'esc_3d',
                                     'esc_2d'))
    print('-' * 60)

    righe, tutte = [], {}
    for r in elenco:
        serie, n_tot, n_det = angoli(r['path'])
        tutte[r['name']] = serie
        a3 = np.array([d['a3d'] for d in serie if d['a3d'] is not None])
        a2 = np.array([d['a2d'] for d in serie if d['a2d'] is not None])
        if len(a3) < 5 or len(a2) < 5:
            print('%-28s %4d  pose insufficienti, saltata'
                  % (r['name'], r['camera']), flush=True)
            continue
        massimo, dove = salti(serie)
        riga = {
            'subject': r['subject'], 'activity': r['activity'],
            'trial': r['trial'], 'camera': r['camera'], 'name': r['name'],
            'exc_3d': float(a3.max() - a3.min()),
            'exc_2d': float(a2.max() - a2.min()),
            'min_3d': float(a3.min()), 'max_3d': float(a3.max()),
            'min_2d': float(a2.min()), 'max_2d': float(a2.max()),
            'det_pct': 100.0 * n_det / max(n_tot, 1),
            'salto_max': massimo,
            'salto_a': '' if dove is None else dove,
            'exc_2d_prima_del_salto': ('' if dove is None
                                       else escursione(serie, dove)),
        }
        righe.append(riga)
        print('%-28s %4d %6.1f %8.2f %8.2f  salto %.2f%s'
              % (riga['name'], riga['camera'], riga['det_pct'],
                 riga['exc_3d'], riga['exc_2d'], massimo,
                 '  <== CAMBIO DI PERSONA al campione %d' % dove
                 if dove is not None else ''), flush=True)

    os.makedirs(os.path.dirname(a.uscita), exist_ok=True)
    with open(a.uscita, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLONNE)
        w.writeheader()
        w.writerows(righe)
    print()
    print('scritto   ', a.uscita)

    dest_serie = a.serie or (os.path.splitext(a.uscita)[0] + '_serie.json')
    with open(dest_serie, 'w') as f:
        json.dump({'passo': PASSO, 'scala': SCALA,
                   'soglia_salto': SOGLIA_SALTO, 'soggetti': soggetti,
                   'serie': tutte}, f)
    print('scritto   ', dest_serie)

    dest, _ = riepilogo(a.uscita)
    print('scritto   ', dest)

    confronta(righe)


if __name__ == '__main__':
    main()
