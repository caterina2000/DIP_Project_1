# -*- coding: utf-8 -*-
"""
Quello che il sistema vede, in diretta, da un browser sul calcolatore.

Perche' esiste
--------------
`mostra.py` disegna lo scheletro su una tela nera --- di proposito: serve a far
vedere che il classificatore lavora sulla geometria e non sull'immagine. Ma per
sistemare l'inquadratura e per mettere in scena una caduta serve l'opposto:
vedersi dentro la stanza, con lo scheletro sopra, e sapere in tempo reale se la
posa e' agganciata e a che punto sta il punteggio.

La board non ha uno schermo e SSH non porta finestre. Il trasporto e' quindi
HTTP: un flusso MJPEG che qualunque browser apre senza installare niente.

    sulla board:   python mostra_web.py --clip clip_sessione --registro s.csv
    sul PC:        http://<indirizzo della board>:8080

**Le immagini restano sul dispositivo e sulla rete locale.** Il flusso non
esce dalla LAN: nessuna porta viene aperta verso l'esterno, e chi non e' in
casa non lo raggiunge.

La catena di decisione e' la STESSA di `rileva.py` --- stesso motore, stessa
cadenza misurata, stesso presidio sul pavimento, stessa regola di allarme ---
importata da li' invece che riscritta. Cio' che si vede e' cio' che il sistema
decide, altrimenti il visore mentirebbe.
"""

import argparse
import json
import os
import sys
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
if QUI not in sys.path:
    sys.path.insert(0, QUI)

from mostra import carica, disegna, normalizza, pannello, riassumi
from rileva import Cadenza, costruisci_motore

W, H, H_PAN = 640, 480, 170

# Lo stato condiviso fra il ciclo che elabora e il server che serve. Un lock
# solo, e nessuna coda: al browser interessa l'ultimo fotogramma, non tutti.
_stato = {'jpeg': None, 'punteggio': 0.0, 'allarmi': 0, 'fps': 0.0,
          'pavimento': False, 'pose_erette': 0, 'posa': False,
          'finestre': 0, 'non_decise': 0, 'avvio': time.time()}
_lock = threading.Lock()
_fine = threading.Event()


PAGINA = b"""<!doctype html><html><head><meta charset="utf-8">
<title>rilevamento cadute - diretta</title>
<style>
 body{background:#141414;color:#ddd;font:14px system-ui,sans-serif;margin:0;
      display:flex;flex-direction:column;align-items:center;gap:10px;padding:14px}
 img{max-width:100%;border:1px solid #333;border-radius:6px}
 #s{font-variant-numeric:tabular-nums;letter-spacing:.02em}
 b{color:#fff}
</style></head><body>
<img src="/flusso">
<div id="s">collegamento...</div>
<script>
setInterval(async () => {
  try {
    const r = await fetch('/stato');
    const d = await r.json();
    document.getElementById('s').innerHTML =
      'punteggio <b>' + d.punteggio.toFixed(3) + '</b> &nbsp; allarmi <b>' +
      d.allarmi + '</b> &nbsp; ' + d.fps.toFixed(1) + ' fps &nbsp; posa ' +
      (d.posa ? 'si' : '<span style="color:#a55">no</span>') +
      ' &nbsp; pavimento ' + (d.pavimento ? 'stimato' :
      '<span style="color:#a85">in attesa (' + d.pose_erette + '/50)</span>');
  } catch (e) {}
}, 500);
</script></body></html>"""


class Servitore(BaseHTTPRequestHandler):

    def log_message(self, *a):
        pass                      # niente rumore sul terminale della sessione

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(PAGINA)))
            self.end_headers()
            self.wfile.write(PAGINA)
            return

        if self.path == '/stato':
            with _lock:
                d = {k: v for k, v in _stato.items() if k != 'jpeg'}
            corpo = json.dumps(d).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)
            return

        if self.path == '/flusso':
            self.send_response(200)
            self.send_header('Content-Type',
                             'multipart/x-mixed-replace; boundary=fotogramma')
            self.end_headers()
            try:
                while not _fine.is_set():
                    with _lock:
                        j = _stato['jpeg']
                    if j is None:
                        time.sleep(0.05)
                        continue
                    self.wfile.write(b'--fotogramma\r\n')
                    self.wfile.write(b'Content-Type: image/jpeg\r\n')
                    self.wfile.write(
                        b'Content-Length: ' + str(len(j)).encode() + b'\r\n\r\n')
                    self.wfile.write(j)
                    self.wfile.write(b'\r\n')
                    time.sleep(0.08)
            except (BrokenPipeError, ConnectionResetError):
                pass               # il browser ha chiuso: non e' un errore
            return

        self.send_error(404)


def ciclo(a, cv2, mp):
    meta, modello, blob = carica()
    colonne = meta['colonne']
    L = meta['lunghezza_finestra']
    passo = meta['passo_finestra']
    soglia = meta['soglia']
    reg = meta['regola_decisione']
    persistenza = reg['persistenza_finestre']
    sospensione = reg['sospensione_s']
    riscaldamento = meta.get('riscaldamento_s', 1.72)
    serve_pav = 'A3_h_pavimento' in colonne

    pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1,
                                  min_detection_confidence=0.5,
                                  min_tracking_confidence=0.5)
    motore = costruisci_motore(meta)
    cadenza = Cadenza(meta['fps_assunti'])
    buf = deque(maxlen=L)
    storia = deque(maxlen=W)

    cap = cv2.VideoCapture(a.camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H)
    if not cap.isOpened():
        print('telecamera non aperta'); _fine.set(); return

    if a.immagini:
        os.makedirs(a.immagini, exist_ok=True)
    registro = open(a.registro, 'w', buffering=1) if a.registro else None
    if registro:
        registro.write('t_s,punteggio,sopra,corsa,allarme,posa,pavimento\n')

    t0 = time.time()
    n_frame = n_allarmi = corsa = lampeggio = n_salvate = 0
    non_decise = 0
    ultimo_allarme = -1e18
    p_corr = 0.0
    ultima_img = 0.0

    try:
        while not _fine.is_set():
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.2)
                continue
            n_frame += 1
            t = time.time() - t0
            if a.durata and t > a.durata:
                break
            cadenza.osserva(t)
            frame = cv2.resize(frame, (W, H))

            r = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            lm = r.pose_landmarks.landmark if r.pose_landmarks else None
            wl = r.pose_world_landmarks.landmark if r.pose_world_landmarks else None

            f = motore.fotogramma(lm, wl, W, H, cadenza.fps())
            buf.append([f[c] for c in colonne])

            # (pronto, n_osservazioni): la tupla va spacchettata, non
            # valutata --- una tupla non vuota e' sempre vera.
            pav_pronto, pav_oss = motore.pavimento_pronto()
            pav = pav_pronto or not serve_pav
            deciso = False
            if len(buf) == L and n_frame % passo == 0 and t >= riscaldamento:
                if pav:
                    X = np.asarray(buf, np.float32)[None]
                    p_corr = float(modello.predict_proba(
                        riassumi(normalizza(X, blob)))[0, 1])
                    storia.append(p_corr)
                    deciso = True
                    sopra = p_corr >= soglia
                    corsa = corsa + 1 if sopra else 0
                    if (corsa >= persistenza
                            and (t - ultimo_allarme) >= sospensione):
                        ultimo_allarme = t
                        n_allarmi += 1
                        lampeggio = 20
                        print(f'\n  ALLARME {n_allarmi} a {t:.1f} s '
                              f'(punteggio {p_corr:.3f})', flush=True)
                else:
                    non_decise += 1

            # ---- il disegno: lo scheletro SOPRA l'immagine vera ----
            tela = frame.copy()
            colore = ((70, 70, 240) if p_corr >= soglia
                      else (120, 230, 120) if lm is not None else (90, 90, 90))
            disegna(cv2, tela, lm, W, H, colore)

            cv2.putText(tela, f'{p_corr:.3f}', (16, 42),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, colore, 2, cv2.LINE_AA)
            cv2.putText(tela, f'allarmi {n_allarmi}   {cadenza.fps():.1f} fps',
                        (16, 70), cv2.FONT_HERSHEY_SIMPLEX, .55,
                        (230, 230, 230), 1, cv2.LINE_AA)
            if lm is None:
                cv2.putText(tela, 'posa non rilevata', (16, H - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, .6, (90, 90, 220), 2,
                            cv2.LINE_AA)
            if not pav:
                cv2.putText(tela,
                            f'pavimento non stimato: cammina in piedi '
                            f'({pav_oss}/{motore.PAV_MINIME})',
                            (16, H - 48), cv2.FONT_HERSHEY_SIMPLEX, .55,
                            (60, 190, 240), 2, cv2.LINE_AA)
            if lampeggio > 0:
                lampeggio -= 1
                cv2.rectangle(tela, (0, 0), (W - 1, H - 1), (60, 60, 250), 6)
                cv2.putText(tela, 'CADUTA RILEVATA', (W // 2 - 170, H // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (70, 70, 250), 3,
                            cv2.LINE_AA)

            fuori = np.vstack([tela, pannello(cv2, storia, soglia, W, H_PAN,
                                              corsa, persistenza)])
            ok_j, j = cv2.imencode('.jpg', fuori,
                                   [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            if ok_j:
                with _lock:
                    _stato.update(jpeg=j.tobytes(), punteggio=p_corr,
                                  allarmi=n_allarmi, fps=cadenza.fps(),
                                  pavimento=bool(pav), posa=lm is not None,
                                  pose_erette=pav_oss,
                                  finestre=len(storia), non_decise=non_decise)

            # le immagini da rivedere dopo: annotate, a cadenza ridotta
            if a.immagini and (t - ultima_img) >= 1.0 / max(a.fps_immagini, .1):
                ultima_img = t
                cv2.imwrite(os.path.join(a.immagini, 'f%07.1f.jpg' % t), fuori,
                            [int(cv2.IMWRITE_JPEG_QUALITY), 78])
                n_salvate += 1

            if registro and deciso:
                registro.write('%.3f,%.4f,%d,%d,%d,%d,%d\n'
                               % (t, p_corr, int(p_corr >= soglia), corsa,
                                  int(lampeggio == 20), int(lm is not None),
                                  int(pav)))
    finally:
        cap.release()
        if registro:
            registro.close()
        _fine.set()
        print(f'\n  fine: {n_frame} fotogrammi, {n_allarmi} allarmi, '
              f'{non_decise} finestre non decise per pavimento, '
              f'{n_salvate} immagini salvate in {a.immagini}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--camera', type=int, default=0)
    ap.add_argument('--porta', type=int, default=8080)
    ap.add_argument('--durata', type=float, default=None, help='secondi')
    ap.add_argument('--immagini', default=None,
                    help='cartella in cui salvare i fotogrammi ANNOTATI, per '
                         'rivedere la sessione dopo. Restano sul dispositivo')
    ap.add_argument('--fps-immagini', type=float, default=3.0,
                    dest='fps_immagini')
    ap.add_argument('--registro', default=None,
                    help='CSV di ogni finestra decisa')
    a = ap.parse_args()

    import cv2
    import mediapipe as mp

    srv = ThreadingHTTPServer(('0.0.0.0', a.porta), Servitore)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print(f'visore su http://<indirizzo della board>:{a.porta}')
    print('  (le immagini non escono dalla rete locale)')

    try:
        ciclo(a, cv2, mp)
    except KeyboardInterrupt:
        _fine.set()
    finally:
        srv.shutdown()


if __name__ == '__main__':
    main()
