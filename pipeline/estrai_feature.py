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
import datetime as dt
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


def controlla_etichette(cat, seq, files, predef):
    """
    Che le etichette di una ripresa siano quelle che ci si aspetta.

    Perche' esiste. Le etichette vengono dal suffisso -0/-1/-2 nel nome del
    PNG e, quando manca, dalla categoria della cartella. Il ripiego sulla
    categoria e' comodo e silenzioso, ed e' li' il rischio: **una ripresa di
    caduta senza suffissi verrebbe etichettata "caduta in corso" per intero**,
    compresi i secondi in cui la persona sta ancora camminando, e nessuno se
    ne accorgerebbe --- il conteggio globale «etichette dal suffisso: 99%»
    resterebbe rassicurante con una ripresa su cento sbagliata.

    Lo stato del dataset al 2026-09-06, verificato file per file:

      - tutte e 100 le riprese di CADUTA sono etichettate per intero;
      - degli ADL, 60 riprese hanno il suffisso e 60 no, e la spaccatura cade
        esattamente fra i soggetti 1-5 e i 6-10, cioe' fra l'impianto a cinque
        soggetti e l'estensione a dieci: sono due preparazioni diverse;
      - **tutti i 49.916 fotogrammi ADL etichettati portano -0**, mai -1 ne'
        -2. Il suffisso, negli ADL, non porta informazione: i soggetti 6-10
        non perdono nulla.

    Quindi la disomogeneita' esiste nella forma e non nell'effetto. I file NON
    vengono rinominati: sono il dato originale di UP-Fall, e allinearli
    renderebbe la copia locale diversa da quella pubblica senza guadagno.
    Si controlla invece che l'ipotesi regga, a ogni estrazione.
    """
    png = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not png:
        return
    con = [SUFFISSO.search(f).group(1) for f in png if SUFFISSO.search(f)]

    if cat == 'fall' and not con:
        sys.exit(f"RIPRESA DI CADUTA SENZA ETICHETTE: {seq}. "
                 f"Tutti i suoi {len(png)} fotogrammi verrebbero etichettati "
                 f"'caduta in corso', compresi quelli in cui la persona e' "
                 f"ancora in piedi. Estrazione interrotta.")

    if con and len(con) != len(png):
        sys.exit(f"RIPRESA CON ETICHETTE PARZIALI: {seq}. "
                 f"{len(con)} fotogrammi su {len(png)} hanno il suffisso. "
                 f"Gli altri prenderebbero il valore della categoria, che e' "
                 f"un'etichetta diversa. Estrazione interrotta.")

    if cat == 'adl' and set(con) - {'0'}:
        sys.exit(f"ATTIVITA NORMALE CON ETICHETTE NON NULLE: {seq}. "
                 f"valori trovati: {sorted(set(con))}. Finora negli ADL "
                 f"compariva solo -0, e su questo si regge il fatto che le "
                 f"riprese senza suffisso siano equivalenti. Estrazione "
                 f"interrotta.")


def sequenze(soggetti=None, riprese=None):
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
                if riprese and seq not in riprese:
                    continue
                p = os.path.join(d, seq)
                if os.path.isdir(p):
                    fuori.append((cat, sog, seq, p))
    return fuori


_STAMP = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}_\d{2}_\d{2})\.(\d+)')


def cadenza(files, ripiego):
    """
    Il tempo trascorso PRIMA di ciascun fotogramma, dai timestamp nei nomi.

    Perche' non una costante. `config.FPS_DATASET = 18,0` era un'assunzione
    scritta in un commento e mai verificata, e i dati per verificarla c'erano
    da sempre: i nomi dei fotogrammi di UP-Fall sono timestamp al
    microsecondo. Misurata, la cadenza vera va da 14,43 a 19,63 fps fra le
    riprese, e **lo scarto e' sistematico per soggetto** --- le dieci riprese
    piu' lontane dal valore dichiarato sono tutte del soggetto 6. Con
    validazione leave-one-subject-out un errore per soggetto finisce dentro un
    fold intero ([ISS-149](docs/ISSUES.md#iss-149)).

    Perche' PER FOTOGRAMMA e non una media per ripresa. La cadenza non e'
    regolare nemmeno dentro la stessa ripresa: mediana 49,6 ms, nono decile
    70,2 ms, 99mo percentile 159,8 ms. Una derivata e' una differenza divisa
    per il tempo in cui e' avvenuta, e quel tempo e' noto esattamente: usare
    una media --- di ripresa o di dataset --- trasforma ogni buco di cattura
    in un picco di velocita' che non c'e' stato. E' la stessa ragione per cui
    un buco di posa azzera lo stato invece di essere attraversato.

    Restituisce (elenco di fps efficaci, misurato). L'fps efficace del
    fotogramma j e' 1 / (t_j - t_{j-1}); per il primo si usa la mediana della
    ripresa, perche' un tempo precedente non esiste.
    """
    ts = []
    for nome in files:
        m = _STAMP.match(nome)
        if m:
            frazione = (m.group(2) + '000000')[:6]
            try:
                ts.append(dt.datetime.strptime(
                    m.group(1) + '.' + frazione, '%Y-%m-%dT%H_%M_%S.%f'))
                continue
            except ValueError:
                pass
        ts.append(None)

    buoni = [t for t in ts if t is not None]
    if len(buoni) < 30 or len(buoni) != len(ts) or buoni != sorted(buoni):
        # timestamp assenti, illeggibili, o nomi non ordinati per tempo:
        # meglio il valore dichiarato che un dt inventato.
        return [float(ripiego)] * len(files), False

    dts = [(ts[i] - ts[i - 1]).total_seconds() for i in range(1, len(ts))]
    positivi = sorted(x for x in dts if x > 0)
    if not positivi:
        return [float(ripiego)] * len(files), False
    mediana = positivi[len(positivi) // 2]

    fps = [1.0 / mediana]
    for x in dts:
        fps.append(1.0 / x if x > 1e-3 else 1.0 / mediana)
    return fps, True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--soggetti', default='',
                    help='elenco, es. 1,2 (default: tutti)')
    ap.add_argument('--riprese', default='',
                    help='nomi di ripresa separati da virgola, per '
                         'riestrarne poche invece di un soggetto intero. '
                         'Serve quando si aggiunge un video al dataset senza '
                         'rifare ore di stima di posa')
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
    quali = {s.strip() for s in a.riprese.split(',') if s.strip()} or None
    seqs = sequenze(voluti, quali)
    if not seqs:
        sys.exit('nessuna sequenza trovata')

    print('=' * 74)
    print(f'ESTRAZIONE — {len(seqs)} sequenze, K integrali = {a.k}')
    print('=' * 74)

    # Un motore per TELECAMERA: lo stato per ripresa si azzera con reset(),
    # ma le osservazioni del pavimento devono accumularsi su tutta la
    # telecamera --- in una ripresa di caduta nessuno sta in piedi abbastanza
    # a lungo per stimarlo.
    motori = {}

    righe, n_predef, t0 = [], 0, time.time()
    fps_misurati = []
    for i, (cat, sog, seq, perc) in enumerate(seqs, 1):
        files = sorted(f for f in os.listdir(perc)
                       if f.lower().endswith(('.png', '.jpg', '.jpeg')))
        if not files:
            continue
        # Il dt vero fotogramma per fotogramma, misurato e non assunto
        # (ISS-149). Un elenco lungo quanto `files`, allineato a esso.
        fps_seq, misurato = cadenza(files, config.FPS_DATASET)
        med = sorted(fps_seq)[len(fps_seq) // 2]
        fps_misurati.append((seq, med, misurato))

        m = CAMERA.search(seq)
        cam = int(m.group(1)) if m else 0
        predef = 1 if cat == 'fall' else 0
        controlla_etichette(cat, seq, files, predef)

        # Lo stato va azzerato a ogni ripresa: le derivate e gli accumuli non
        # devono attraversare il confine fra due video.
        motore = motori.setdefault(cam, MotoreGeometrico(k_integrali=a.k))
        motore.reset()

        # E LO STIMATORE DI POSA ANCHE, per la stessa ragione. Fino al
        # 2026-09-06 ne veniva creato UNO SOLO fuori dal ciclo: il motore
        # geometrico si azzerava, lo stimatore no. MediaPipe Pose e' un
        # tracciatore, quindi l'ultimo fotogramma di una ripresa condizionava
        # il primo della successiva, e le feature dipendevano dall'ORDINE in
        # cui le riprese erano state elaborate.
        #
        # Misurato sul controllo `sub06_act08_trial01_cam01`, riestratto da
        # solo e confrontato con il dataset: scarto medio 2,32 deviazioni
        # standard sui primi cinque fotogrammi, 0,26 fra il quinto e il
        # cinquantesimo, 0,026 dopo il trecentesimo. Decade, ma su una ripresa
        # di caduta -- circa duecento fotogrammi -- la parte contaminata e'
        # una frazione molto piu' grande che su una di attivita' normale.
        #
        # Creare uno stimatore per ripresa costa qualche decimo di secondo di
        # inizializzazione ed e' la condizione in cui il sistema lavora
        # davvero: quando si accende, non ha visto la ripresa precedente.
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
            wl = r.pose_world_landmarks.landmark if r.pose_world_landmarks else None
            f = motore.fotogramma(lm, wl, w, h, fps_seq[j])

            lab, usato_predef = etichetta_da_nome(nome, predef)
            n_predef += usato_predef
            # anca e torso in pixel servono a ricalcolare l'altezza dal
            # pavimento alla fine, con la retta stimata su tutta la telecamera
            if lm is not None:
                hx = (lm[23].x + lm[24].x) / 2 * w
                hy = (lm[23].y + lm[24].y) / 2 * h
            else:
                hx = hy = 0.0
            righe.append({'soggetto': sog, 'categoria': cat, 'ripresa': seq,
                          'camera': cam, 'fotogramma': j, 'label': lab,
                          'ha_posa': int(lm is not None),
                          '_hip_x': hx, '_hip_y': hy, **f})

        # lo stimatore muore con la ripresa: senza, i grafi di TensorFlow
        # Lite si accumulano e su 220 riprese la memoria non basta
        pose.close()

        if i % 10 == 0 or i == len(seqs):
            el = time.time() - t0
            print(f'  {i:4d}/{len(seqs)}  {len(righe):8,} fotogrammi  '
                  f'{el/60:5.1f} min  (stima totale {el/i*len(seqs)/60:.0f} min)',
                  flush=True)

    d = pd.DataFrame(righe)

    # L'ALTEZZA DAL PAVIMENTO, ricalcolata con la retta finale.
    #
    # Durante il ciclo ogni riga ha ricevuto il valore che la retta stimata
    # *fino a quel momento* permetteva, e per le prime riprese di ogni
    # telecamera era zero. Qui si rifa' con la retta stimata su TUTTA la
    # telecamera, cosi' il valore non dipende dall'ordine di elaborazione.
    print()
    for cam, mot in sorted(motori.items()):
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
        v = d.loc[m, 'A3_h_pavimento']
        a_, c_ = mot._pav_retta
        print(f'  Camera{cam}: y = {a_:+.4f}*x {c_:+.1f}  '
              f'({n:,} fotogrammi eretti)   altezza mediana {v.median():+.2f} '
              f'torsi, 5-95% [{v.quantile(.05):+.2f}, {v.quantile(.95):+.2f}]')
    d.drop(columns=['_hip_x', '_hip_y'], inplace=True)

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
