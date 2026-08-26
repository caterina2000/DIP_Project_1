"""
Rilevamento cadute sulla board — DA ESEGUIRE SULLA BOARD.

    telecamera -> 640x480 -> MediaPipe -> 12 grandezze geometriche
               -> finestra di 22 campioni -> foresta -> allarme

Nessuna immagine lascia il dispositivo. Le clip attorno agli allarmi, se
attivate, restano su disco locale.

PRIMA DI TUTTO: la prova di parita'

    python3 rileva.py --parita

Confronta le predizioni della board con quelle calcolate sul PC su duecento
finestre. Se divergono oltre 1e-6 le versioni di scikit-learn non sono
compatibili, e nessuna misura successiva e' valida. Trenta secondi.

POI

    python3 rileva.py                      dalla telecamera
    python3 rileva.py --video clip/        da una cartella di fotogrammi
    python3 rileva.py --durata 60          si ferma dopo un minuto

Due cose che il sistema dichiara, e che vanno lette
---------------------------------------------------
RISCALDAMENTO. Nove delle dodici grandezze sono integrali accumulati sugli
ultimi 31 fotogrammi. Finche' il buffer non e' pieno i valori non sono
affidabili: il sistema non decide, e lo dichiara a schermo. Circa 1,7 secondi.

ALLARME CONTRO FINESTRA SOPRA SOGLIA. Una raffica di finestre consecutive
sopra soglia e' UN allarme, non N: servono 5 finestre consecutive e poi 30
secondi di silenzio. Il contatore mostra entrambi i numeri perche' il loro
rapporto -- misurato 47,8 sulle sessioni registrate -- e' esattamente cio' che
distingue un dato riportabile da uno che sovrastima di due ordini di grandezza.
"""

import argparse
import json
import os
import sys
import time
from collections import deque

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

VERDE, ROSSO, GIALLO, GRIGIO, FINE = (
    '\033[92m', '\033[91m', '\033[93m', '\033[90m', '\033[0m')


def carica():
    import joblib
    meta = json.load(open(os.path.join(QUI, 'metadata.json'), encoding='utf-8'))
    modello = joblib.load(os.path.join(QUI, 'modello.pkl'))
    blob = joblib.load(os.path.join(QUI, 'scaler.pkl'))
    return meta, modello, blob


def normalizza(X, blob):
    """log1p sulle colonne asimmetriche, poi standardizzazione. Come sul PC."""
    Z = np.asarray(X, dtype=np.float64).copy()
    m = np.asarray(blob['maschera_log1p'], dtype=bool)
    if m.any():
        c = np.where(m)[0]
        Z[..., c] = np.sign(Z[..., c]) * np.log1p(np.abs(Z[..., c]))
    forma = Z.shape
    return blob['scaler'].transform(Z.reshape(-1, forma[-1])).reshape(forma)


def riassumi(X):
    """Sei statistiche per grandezza. Identica a src/modelli.py sul PC."""
    return np.concatenate([X.mean(1), X.std(1), X.min(1), X.max(1),
                           X[:, 0, :], X[:, -1, :]], axis=1)


def prova_parita(tol=1e-6):
    meta, modello, blob = carica()
    d = np.load(os.path.join(QUI, 'parita.npz'))
    p = modello.predict_proba(riassumi(d['X']))[:, 1]
    scarto = float(np.abs(p - d['p_attesa']).max())
    print('=' * 62)
    print('PROVA DI PARITA con il PC')
    print('=' * 62)
    print(f'  finestre confrontate   {len(p)}')
    print(f'  scarto massimo         {scarto:.3e}')
    print(f'  tolleranza             {tol:.0e}')
    import sklearn
    print(f'  scikit-learn qui       {sklearn.__version__}')
    print()
    if scarto <= tol:
        print(f'{VERDE}  SUPERATA — la board riproduce il PC{FINE}')
        return 0
    print(f'{ROSSO}  FALLITA — le versioni non sono compatibili.{FINE}')
    print('  Nessuna misura successiva e valida finche non e risolta.')
    return 1


def barra(v, larghezza=34, soglia=0.5):
    n = int(round(v * larghezza))
    pieno = '#' * n + '.' * (larghezza - n)
    tick = int(round(soglia * larghezza))
    pieno = pieno[:tick] + '|' + pieno[tick:]
    colore = ROSSO if v >= soglia else (GIALLO if v >= soglia * .6 else VERDE)
    return f'{colore}[{pieno}]{FINE}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--parita', action='store_true',
                    help='confronta con il PC e termina')
    ap.add_argument('--video', default=None,
                    help='cartella di fotogrammi invece della telecamera')
    ap.add_argument('--durata', type=float, default=None, help='secondi')
    ap.add_argument('--camera', type=int, default=0)
    ap.add_argument('--registro', default=None,
                    help='file CSV su cui scrivere OGNI finestra: '
                         'istante, punteggio, sopra soglia, corsa, '
                         'allarme. Senza questo una prova lunga '
                         'produce tre numeri e nulla di ricalcolabile, '
                         'e le regole di decisione non si possono '
                         'ritarare a posteriori')
    ap.add_argument('--riepilogo', default=None,
                    help='dove scrivere il riepilogo JSON. Senza questo, '
                         'accanto al registro. Contiene la SOSPENSIONE '
                         'stimata: senza, una prova lunga puo sembrare '
                         'riuscita mentre la macchina ha dormito.')
    a = ap.parse_args()

    # rediretta su file, la riga di stato con \r diventa una riga sola
    # di centinaia di migliaia di caratteri: si stampa un rigo ogni
    # minuto invece del contatore continuo
    interattivo = sys.stdout.isatty()

    if a.parita:
        sys.exit(prova_parita())

    import cv2
    import mediapipe as mp
    from geometry import MotoreGeometrico

    meta, modello, blob = carica()
    colonne = meta['colonne']
    L, passo = meta['lunghezza_finestra'], meta['passo_finestra']
    soglia = meta['soglia']
    reg = meta['regola_decisione']
    # `sospensione_regola` e' il silenzio dopo un allarme, in secondi. Da non
    # confondere con la sospensione della MACCHINA calcolata a fine sessione:
    # portavano lo stesso nome, ed e' il genere di collisione che produce un
    # numero plausibile e sbagliato.
    persistenza, sospensione_regola = reg['persistenza_finestre'], reg['sospensione_s']
    riscaldamento = meta['riscaldamento_s']

    print('=' * 62)
    print(f'RILEVAMENTO CADUTE — compito «{meta["compito"]}»')
    print('=' * 62)
    print(f'  positivo          {meta["positivo"]}')
    print(f'  grandezze         {len(colonne)}   ({meta["feature_set"]})')
    print(f'  finestra          {meta["durata_finestra_s"]} s '
          f'({L} campioni)')
    print(f'  soglia            {soglia}')
    print(f'  allarme dopo      {persistenza} finestre consecutive, '
          f'poi {sospensione_regola:.0f} s di silenzio')
    print(f'  riscaldamento     {riscaldamento} s')
    print(f'{GRIGIO}  nessuna immagine lascia il dispositivo{FINE}')
    print()

    pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1,
                                  min_detection_confidence=0.5,
                                  min_tracking_confidence=0.5)
    motore = MotoreGeometrico(k_integrali=meta['k_integrali'])
    buf = deque(maxlen=L)

    if a.video:
        files = sorted(f for f in os.listdir(a.video)
                       if f.lower().endswith(('.jpg', '.png', '.jpeg')))
        sorgente, n_tot = iter(files), len(files)
        print(f'sorgente: {n_tot} fotogrammi da {a.video}\n')
        cap = None
    else:
        cap = cv2.VideoCapture(a.camera)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if not cap.isOpened():
            sys.exit('telecamera non disponibile')
        print('sorgente: telecamera  —  Ctrl+C per fermare\n')

    reg = None
    if a.registro:
        reg = open(a.registro, 'w', buffering=1, encoding='utf-8')
        reg.write('t_s,punteggio,sopra,corsa,allarme\n')
        print(f'registro           {a.registro}')

    t0 = time.time()
    t0_mono = time.monotonic()
    # DUE OROLOGI. time.time() e' l'ora di sistema e avanza anche mentre la
    # macchina dorme; time.monotonic() no. La loro differenza a fine sessione
    # e' il tempo di sospensione, ed e' l'unico modo per accorgersi che il
    # dispositivo si e' addormentato: il 10 agosto una prova di durata e'
    # SEMBRATA RIUSCIRE mentre la board aveva dormito un'ora e nove minuti.
    costo = {'pre': 0.0, 'percezione': 0.0, 'post': 0.0,
             'classificatore': 0.0}
    n_decisioni = 0
    n_frame = n_pose = n_sopra = n_allarmi = 0
    ultimo_rigo = 0.0
    corsa = 0
    ultimo_allarme = -1e18
    picco = 0.0

    try:
        while True:
            if cap is not None:
                ok, frame = cap.read()
                if not ok:
                    break
            else:
                try:
                    frame = cv2.imread(os.path.join(a.video, next(sorgente)))
                except StopIteration:
                    break
                if frame is None:
                    continue
            n_frame += 1
            t = time.time() - t0
            if a.durata and t > a.durata:
                break

            h, w = frame.shape[:2]
            _c = time.perf_counter()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            _p = time.perf_counter()
            costo['pre'] += _p - _c
            r = pose.process(rgb)
            _q = time.perf_counter()
            costo['percezione'] += _q - _p
            lm = r.pose_landmarks.landmark if r.pose_landmarks else None
            wl = r.pose_world_landmarks.landmark if r.pose_world_landmarks else None
            n_pose += int(lm is not None)

            f = motore.fotogramma(lm, wl, w, h, meta['fps_assunti'])
            buf.append([f[c] for c in colonne])
            costo['post'] += time.perf_counter() - _q

            caldo = t >= riscaldamento
            if len(buf) < L or n_frame % passo:
                continue

            if not caldo:
                if interattivo:
                    print(f'\r{GIALLO}riscaldamento  '
                          f'{t:4.1f}/{riscaldamento:.1f} s{FINE}   ',
                          end='', flush=True)
                continue

            _r = time.perf_counter()
            X = np.asarray(buf, dtype=np.float32)[None, :, :]
            p = float(modello.predict_proba(riassumi(normalizza(X, blob)))[0, 1])
            costo['classificatore'] += time.perf_counter() - _r
            n_decisioni += 1
            picco = max(picco, p)

            sopra = p >= soglia
            n_sopra += sopra
            corsa = corsa + 1 if sopra else 0
            if corsa >= persistenza and (t - ultimo_allarme) >= sospensione_regola:
                ultimo_allarme = t
                n_allarmi += 1
                print(f'\r{ROSSO}  *** ALLARME #{n_allarmi} ***   '
                      f'punteggio {p:.3f}   a {t:6.1f} s{FINE}'
                      + ' ' * 20)

            if reg is not None:
                reg.write(f'{t:.3f},{p:.4f},{int(sopra)},{corsa},'
                          f'{int(corsa >= persistenza and ultimo_allarme == t)}\n')

            fps = n_frame / max(t, 1e-6)
            if interattivo:
                print(f'\r{barra(p, soglia=soglia)} {p:5.3f}   '
                      f'{fps:4.1f} fps   pose {100*n_pose/n_frame:3.0f}%   '
                      f'allarmi {n_allarmi}  (finestre sopra {n_sopra})   ',
                      end='', flush=True)
            elif t - ultimo_rigo >= 60:
                ultimo_rigo = t
                print(f'{t/60:7.1f} min   {fps:4.1f} fps   '
                      f'pose {100*n_pose/n_frame:3.0f}%   '
                      f'picco {picco:.3f}   allarmi {n_allarmi}   '
                      f'(finestre sopra {n_sopra})', flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        if cap is not None:
            cap.release()
        if reg is not None:
            reg.close()

    t = time.time() - t0
    t_mono = time.monotonic() - t0_mono
    # La differenza fra i due orologi E' il tempo in cui la macchina ha
    # dormito. Va calcolata sempre, non solo quando si sospetta: il difetto
    # del 10 agosto non ha prodotto un errore, ha prodotto una sessione che
    # sembrava riuscita.
    sospensione = max(0.0, t - t_mono)

    fps = n_frame / max(t_mono, 1e-6)
    quota_pose = n_pose / max(n_frame, 1)
    per_frame = {k: (v / max(n_frame, 1)) for k, v in costo.items()}
    # Il classificatore non gira a ogni fotogramma ma una volta ogni `passo`:
    # il costo per FINESTRA e quello per FOTOGRAMMA differiscono di quel
    # fattore, ed e' la discordanza fra i due numeri che compaiono in tesi.
    per_finestra = costo['classificatore'] / max(n_decisioni, 1)
    totale_frame = sum(per_frame.values())

    print()
    print('=' * 62)
    print('  durata (orologio)    %.1f s' % t)
    print('  durata (cronometro)  %.1f s' % t_mono)
    if sospensione > 1.0:
        print('  %sSOSPENSIONE STIMATA  %.1f s  (%.1f min)%s'
              % (ROSSO, sospensione, sospensione / 60, FINE))
        print('  %sLa macchina ha dormito: la sessione NON e\' valida come'
              ' prova di durata.%s' % (ROSSO, FINE))
    else:
        print('  sospensione          nessuna')
    print('  fotogrammi           %s   (%.1f fps)' % ('{:,}'.format(n_frame), fps))
    print('  pose valide          %.1f%%' % (100 * quota_pose))
    print('  punteggio massimo    %.3f' % picco)
    print()
    print('  BILANCIO PER FOTOGRAMMA')
    for k in ('pre', 'percezione', 'post', 'classificatore'):
        ms = 1000 * per_frame[k]
        quota = 100 * per_frame[k] / max(totale_frame, 1e-12)
        print('    %-16s %7.2f ms   %5.1f%%' % (k, ms, quota))
    print('    %-16s %7.2f ms' % ('totale', 1000 * totale_frame))
    print('    classificatore per FINESTRA: %.2f ms  (una ogni %d fotogrammi)'
          % (1000 * per_finestra, passo))
    print()
    print('  finestre sopra soglia   %d' % n_sopra)
    print('  ALLARMI emessi          %d' % n_allarmi)
    if n_allarmi:
        print('  fattore                 %.1fx' % (n_sopra / n_allarmi))
    if t_mono > 60:
        print('  allarmi/ora             %.2f' % (n_allarmi / (t_mono / 3600)))
        print('%s  riferimento letteratura: 0,049 eventi/ora%s' % (GRIGIO, FINE))

    dest = a.riepilogo
    if dest is None:
        dest = (os.path.splitext(a.registro)[0] + '_riepilogo.json'
                if a.registro else 'riepilogo.json')
    fuori = {
        'avvio': time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(t0)),
        'durata_orologio_s': t,
        'durata_cronometro_s': t_mono,
        'sospensione_stimata_s': sospensione,
        'sospesa': bool(sospensione > 1.0),
        'fotogrammi': n_frame,
        'fps_medio': fps,
        'pose_valide': n_pose,
        'quota_pose': quota_pose,
        'punteggio_massimo': picco,
        'finestre_sopra_soglia': n_sopra,
        'allarmi': n_allarmi,
        'decisioni': n_decisioni,
        'costo_per_fotogramma_ms': {k: 1000 * v for k, v in per_frame.items()},
        'costo_totale_per_fotogramma_ms': 1000 * totale_frame,
        'costo_classificatore_per_finestra_ms': 1000 * per_finestra,
        'configurazione': {
            'compito': meta.get('compito'), 'feature_set': meta.get('feature_set'),
            'n_colonne': len(colonne), 'lunghezza_finestra': L,
            'passo_finestra': passo, 'k_integrali': meta.get('k_integrali'),
            'soglia': soglia, 'persistenza_finestre': persistenza,
            'sospensione_s': sospensione_regola,
            'stimatore_posa': meta.get('stimatore_posa')},
        'nota_costo': ('I tempi sono misurati con perf_counter attorno alle '
                       'quattro fasi della catena in esercizio, non da un '
                       'banco separato: sono i tempi della stessa esecuzione '
                       'che ha prodotto gli allarmi. La strumentazione stessa '
                       'costa quattro letture di orologio per fotogramma.'),
    }
    with open(dest, 'w', encoding='utf-8') as fh:
        json.dump(fuori, fh, ensure_ascii=False, indent=1)
    print()
    print('  riepilogo scritto in %s' % dest)


if __name__ == '__main__':
    main()
