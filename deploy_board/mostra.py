"""
Visualizzazione per la discussione: scheletro, punteggio, allarme.

Mostra cio' che il sistema vede davvero -- lo scheletro e le dodici grandezze
che ne derivano -- invece dell'immagine. Non e' soltanto una precauzione sulla
riservatezza: e' la dimostrazione visiva del paradigma privacy-by-design, perche'
rende evidente che dal fotogramma il sistema ricava trentatre punti e poi butta
via i pixel.

    python3 mostra.py --video clip/evt_xxx           riproduce una clip
    python3 mostra.py                                dalla telecamera
    python3 mostra.py --video clip/evt_xxx --salva out.mp4
    python3 mostra.py --video clip/evt_xxx --salva out.mp4 \
        --sfondo bianco --schema rosso_verde         sfondo bianco, scheletro
                                                      verde sotto soglia e
                                                      rosso sopra, per slide
    python3 mostra.py --video clip/evt_xxx --salva out.mp4 \
        --sfondo originale                           scheletro sopra il
                                                      fotogramma vero: si
                                                      vede la stanza
    python3 mostra.py --video clip/evt_xxx --salva out.mp4 \
        --sfondo ambiente                            si vede la stanza, non
                                                      la persona: sfondo
                                                      stimato come mediana
                                                      per pixel sui
                                                      fotogrammi della
                                                      cartella, la persona
                                                      (che si muove) sparisce

Cosa appare a schermo
---------------------
A sinistra lo scheletro su fondo scuro, a destra il punteggio nel tempo con la
soglia e le due condizioni della regola di decisione. Quando l'allarme scatta,
la banda rossa.

Il grafico del punteggio mostra anche la RAFFICA in corso, cioe' da quante
finestre consecutive il punteggio sta sopra soglia: e' la grandezza che
distingue un allarme da una finestra sopra soglia, e senza mostrarla la
differenza fra 1.636 e 34 all'ora resta invisibile.
"""

import argparse
import json
import os
import re
import sys
import time
from collections import deque

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

# Coppie di landmark che formano lo scheletro disegnato. Sono le connessioni
# anatomiche fra i punti che le grandezze usano davvero, piu' quelle che
# rendono la figura leggibile.
OSSA = [(11, 12), (11, 23), (12, 24), (23, 24),
        (11, 13), (13, 15), (12, 14), (14, 16),
        (23, 25), (25, 27), (24, 26), (26, 28),
        (0, 11), (0, 12)]
# I nove punti da cui derivano le dodici grandezze: si disegnano piu' grandi.
USATI = {0, 11, 12, 23, 24, 25, 26, 27, 28}

NOME_TEMPO_RE = re.compile(r'f(\d+\.\d+)\.jpg$', re.IGNORECASE)

# Le sessioni salvate in diretta da mostra_web.py NON contengono il solo
# fotogramma: contengono il composito gia' montato, cioe' l'immagine
# (640x480) impilata sopra il pannello del punteggio (640x170), per un
# totale di 640x650 --- vedi mostra_web.py:47 e :247-262. Rielaborarle
# senza accorgersene significa schiacciare immagine E pannello dentro
# l'inquadratura, e poi disegnarci sopra un secondo pannello.
#
# I rettangoli sono le zone in cui quella stessa diretta ha scritto il suo
# HUD SOPRA l'immagine (mostra_web.py:225-239). Il loro contenuto cambia a
# ogni fotogramma ma la posizione no, quindi la mediana nel tempo non li
# cancella: restano come fantasmi, e vanno ricostruiti a parte.
HUD_RETTANGOLI = [
    (0, 0, 310, 86),     # punteggio, e "allarmi N   X fps"
    (0, 415, 530, 480),  # "pavimento non stimato", "posa non rilevata"
]


def scorpora_composito(cv2, frame, w, h):
    """Dal composito salvato in diretta tiene la sola immagine, senza pannello."""
    if frame.shape[0] > h:
        frame = frame[:h]
    if frame.shape[:2] != (h, w):
        frame = cv2.resize(frame, (w, h))
    return frame


def ripulisci_hud(cv2, immagine):
    """
    Ricostruisce le zone dell'HUD della diretta a partire da cio' che le
    circonda (inpainting di Telea: algoritmo classico, deterministico, non
    inventa una scena -- propaga i pixel al bordo del buco verso l'interno).

    Si applica allo SFONDO gia' mediato, quindi la persona non c'e' piu':
    cio' che viene ricostruito e' soltanto muro e arredamento.
    """
    maschera = np.zeros(immagine.shape[:2], np.uint8)
    for x0, y0, x1, y1 in HUD_RETTANGOLI:
        maschera[y0:y1, x0:x1] = 255
    return cv2.inpaint(immagine, maschera, 3, cv2.INPAINT_TELEA)


def tempo_da_nome(percorso):
    """Il secondo di sessione scritto nel nome del file, o None."""
    m = NOME_TEMPO_RE.search(os.path.basename(percorso))
    return float(m.group(1)) if m else None


def leggi_registro(percorso, persistenza, sospensione):
    """
    Le decisioni che la board ha preso davvero, dal suo registro.

    Restituisce (tempi, punteggi, corse, istanti_allarme).

    Gli allarmi NON si leggono dalla colonna `allarme`: in questa sessione
    vale 0 su tutte le righe, pur essendo scattati davvero --- il fatto
    accade e l'artefatto non lo registra (ISS-142). Si ricostruiscono
    invece dalla colonna `corsa`, che e' scritta correttamente: la regola
    installata e' la stessa (persistenza raggiunta piu' intervallo
    refrattario), applicata ai valori della board, non a valori nuovi.
    """
    import csv as _csv
    tempi, punteggi, corse = [], [], []
    with open(percorso, newline='', encoding='utf-8') as f:
        for riga in _csv.DictReader(f):
            tempi.append(float(riga['t_s']))
            punteggi.append(float(riga['punteggio']))
            corse.append(int(riga['corsa']))

    allarmi, ultimo = [], -1e18
    for t, c in zip(tempi, corse):
        if c >= persistenza and (t - ultimo) >= sospensione:
            allarmi.append(t)
            ultimo = t
    return (np.asarray(tempi), np.asarray(punteggi),
            np.asarray(corse), allarmi)


def nel_tempo(nome_file, da, a):
    """True se il nome non ha il formato f<secondi>.jpg, o se lo ha ed e' in [da, a]."""
    if da is None and a is None:
        return True
    m = NOME_TEMPO_RE.search(nome_file)
    if not m:
        return True
    t = float(m.group(1))
    return (da is None or t >= da) and (a is None or t <= a)


def carica(dove=None):
    """
    Il pacchetto da usare: quello installato, oppure un altro.

    Serve perche' la configurazione installata --- DTWH, tredici colonne
    --- **non e' valutabile su una clip corta**: `A3_h_pavimento` richiede
    cinquanta osservazioni di persona eretta, e in una quindicina di
    secondi non ci sono. Su quelle clip il pavimento resta non stimato e la
    grandezza vale zero per tutta la clip ([EXP-040](../docs/EXPERIMENTS.md#exp-040):
    il 91,5% delle clip di agosto non produce nessuna decisione). Per
    guardarle serve un pacchetto a dodici colonne, che il pavimento non lo
    chiede, e la differenza va dichiarata invece che nascosta.
    """
    import joblib
    dove = dove or QUI
    meta = json.load(open(os.path.join(dove, 'metadata.json'), encoding='utf-8'))
    return (meta, joblib.load(os.path.join(dove, 'modello.pkl')),
            joblib.load(os.path.join(dove, 'scaler.pkl')))


def normalizza(X, blob):
    Z = np.asarray(X, dtype=np.float64).copy()
    m = np.asarray(blob['maschera_log1p'], dtype=bool)
    if m.any():
        c = np.where(m)[0]
        Z[..., c] = np.sign(Z[..., c]) * np.log1p(np.abs(Z[..., c]))
    f = Z.shape
    return blob['scaler'].transform(Z.reshape(-1, f[-1])).reshape(f)


def riassumi(X):
    return np.concatenate([X.mean(1), X.std(1), X.min(1), X.max(1),
                           X[:, 0, :], X[:, -1, :]], axis=1)


def sfondo_mediano(cv2, percorsi, w, h):
    """
    Stima della stanza senza la persona: mediana per pixel sui fotogrammi
    della cartella.

    La persona si muove, quindi in ogni punto dell'immagine occupa quel
    pixel solo per una minoranza dei fotogrammi: la mediana nel tempo
    restituisce il valore che prevale, cioe' lo sfondo fermo. Non e' una
    stima generativa, e' un filtro temporale classico -- niente inventa
    cosa c'e' dietro la persona, si limita a scartarla perche' e' il
    valore transitorio in ciascun pixel.

    Richiede piu' fotogrammi di quelli che la persona copre nello stesso
    punto: con pochissimi fotogrammi, o con la persona ferma a lungo nello
    stesso punto, puo' lasciare una traccia visibile.
    """
    pile = []
    for p in percorsi:
        f = cv2.imread(p)
        if f is not None:
            pile.append(scorpora_composito(cv2, f, w, h))
    if not pile:
        return np.full((h, w, 3), 26, np.uint8)
    return np.median(np.stack(pile, axis=0), axis=0).astype(np.uint8)


def disegna(cv2, tela, lm, w, h, colore):
    if lm is None:
        return
    pt = [(int(p.x * w), int(p.y * h)) for p in lm]
    for a, b in OSSA:
        if a < len(pt) and b < len(pt):
            cv2.line(tela, pt[a], pt[b], colore, 2, cv2.LINE_AA)
    for i, p in enumerate(pt):
        if i in USATI:
            cv2.circle(tela, p, 5, colore, -1, cv2.LINE_AA)
        elif i > 10:
            cv2.circle(tela, p, 2, (110, 110, 110), -1, cv2.LINE_AA)


def pannello(cv2, storia, soglia, larghezza, altezza, corsa, persistenza,
             sfondo=22):
    """Il punteggio nel tempo, con soglia e raffica in corso."""
    chiaro = sfondo > 127
    p = np.full((altezza, larghezza, 3), sfondo, np.uint8)
    testo = (60, 60, 60) if chiaro else (170, 170, 170)
    y_soglia = int(altezza - soglia * (altezza - 30)) - 10
    cv2.line(p, (0, y_soglia), (larghezza, y_soglia), (90, 90, 200), 1)
    cv2.putText(p, f'soglia {soglia:.2f}', (6, y_soglia - 6),
                cv2.FONT_HERSHEY_SIMPLEX, .42, (120, 120, 220), 1, cv2.LINE_AA)

    if len(storia) > 1:
        n = min(len(storia), larghezza)
        v = list(storia)[-n:]
        passo = larghezza / max(n - 1, 1)
        for i in range(1, n):
            y0 = int(altezza - v[i - 1] * (altezza - 30)) - 10
            y1 = int(altezza - v[i] * (altezza - 30)) - 10
            c = (80, 80, 235) if v[i] >= soglia else (200, 190, 90)
            cv2.line(p, (int((i - 1) * passo), y0), (int(i * passo), y1),
                     c, 2, cv2.LINE_AA)

    # la raffica in corso: quante finestre consecutive sopra soglia
    spento = (180, 180, 180) if chiaro else (60, 60, 60)
    for k in range(persistenza):
        x = larghezza - 18 * (persistenza - k) - 8
        acceso = k < corsa
        cv2.rectangle(p, (x, 8), (x + 13, 21),
                      (80, 80, 235) if acceso else spento,
                      -1 if acceso else 1)
    cv2.putText(p, f'raffica {corsa}/{persistenza}',
                (larghezza - 18 * persistenza - 118, 20),
                cv2.FONT_HERSHEY_SIMPLEX, .42, testo, 1, cv2.LINE_AA)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--video', nargs='+', default=None,
                     help="una o piu' cartelle di fotogrammi: con piu' di "
                          "una, le unisce in un unico video nell'ordine "
                          "dato (prima tutti i fotogrammi della prima "
                          "cartella, poi tutti quelli della seconda)")
    ap.add_argument('--eventi-da', default=None,
                     help="cartella 'clip' che contiene molte sottocartelle "
                          "evt_*: le unisce TUTTE, in ordine di nome, come "
                          "se fossero elencate una per una con --video. "
                          "Evita di dover costruire la lista a mano nella "
                          "shell. Alternativo a --video, non insieme.")
    ap.add_argument('--da', type=float, default=None,
                     help="limite inferiore, in secondi di sessione: tiene "
                          "solo i fotogrammi 'f<secondi>.<decimale>.jpg' con "
                          "il secondo nel nome dentro [--da, --a]. Richiede "
                          "quel formato di nome file (le sessioni a "
                          "fotogrammi sciolti come 20260909_v5, non le "
                          "cartelle evt_*).")
    ap.add_argument('--a', type=float, default=None,
                     help="limite superiore, in secondi di sessione (v. --da)")
    ap.add_argument('--camera', type=int, default=0)
    ap.add_argument('--salva', default=None, help='scrive un mp4')
    ap.add_argument('--salva-fotogrammi', default=None,
                     help="con --mantieni-overlay: invece di (o insieme a) "
                          "scrivere un mp4 direttamente, salva ogni "
                          "fotogramma elaborato come immagine in questa "
                          "cartella, con lo stesso nome dell'originale. "
                          "Poi si compone il video con monta_video.py, che "
                          "usa una codifica di qualita' piu' alta e rispetta "
                          "i tempi veri dai nomi dei file.")
    ap.add_argument('--fps-riproduzione', type=float, default=8.0)
    ap.add_argument('--sfondo',
                     choices=['scuro', 'bianco', 'originale', 'ambiente'],
                     default='scuro',
                     help="'originale': scheletro sopra il fotogramma vero, "
                          "si vede la stanza E la persona. 'ambiente': "
                          "scheletro sopra uno sfondo stimato come mediana "
                          "dei fotogrammi della cartella -- si vede la "
                          "stanza, non la persona (si muove, sparisce)")
    ap.add_argument('--schema', choices=['standard', 'rosso_verde'],
                     default='standard',
                     help="'rosso_verde': scheletro verde sotto soglia, "
                          "rosso sopra soglia, invece della scala di grigi")
    ap.add_argument('--mantieni-overlay', action='store_true',
                     help="per cartelle dove lo scheletro e i testi sono "
                          "gia' disegnati sul fotogramma (es. le sessioni "
                          "salvate da mostra_web.py in diretta): non rifa' "
                          "la rilevazione ne' ridisegna nulla di nuovo "
                          "-- prende lo sfondo mediano (--sfondo ambiente) "
                          "e ci rimette sopra solo i pixel del colore dello "
                          "scheletro/testo gia' disegnato, scartando il "
                          "resto (la persona vera). Richiede --sfondo "
                          "ambiente, salta modello e MediaPipe.")
    ap.add_argument('--pacchetto', default=None,
                     help="cartella del pacchetto da usare (metadata.json, "
                          "modello.pkl, scaler.pkl). Senza, usa quello "
                          "installato in deploy_board/. Su clip corte serve "
                          "'pacchetto_dtw12': quello installato e' DTWH e "
                          "richiede l'altezza dal pavimento, che su una "
                          "clip di pochi secondi non fa in tempo a essere "
                          "stimata (EXP-040).")
    ap.add_argument('--punteggi', default=None,
                     help="CSV del registro della sessione (t_s,punteggio,"
                          "sopra,corsa,allarme,...), scritto dalla board in "
                          "diretta. Con questa opzione il punteggio, la "
                          "raffica e gli allarmi NON vengono ricalcolati: "
                          "si leggono da li', associati a ogni fotogramma "
                          "per istante. Il modello non viene interrogato, "
                          "MediaPipe serve solo a disegnare lo scheletro.")
    ap.add_argument('--soglia-sfondo', type=int, default=30,
                     help="con --mantieni-overlay: di quanto un pixel deve "
                          "discostarsi dalla stanza vuota stimata per essere "
                          "considerato 'roba da togliere' (0-255). "
                          "Abbassala (es. 18) se la persona si vede ancora, "
                          "alzala (es. 50) se sparisce anche l'arredamento.")
    ap.add_argument('--tolleranza-overlay', type=int, default=55,
                     help="con --mantieni-overlay: quanto puo' discostarsi "
                          "un pixel dal colore esatto dello scheletro/testo "
                          "per essere comunque tenuto (0-255). Alzala se "
                          "lo scheletro resta invisibile o a tratteggio, "
                          "abbassala se compaiono macchie sulla stanza.")
    ap.add_argument('--salva-sfondo', default=None,
                     help="scrive su file lo sfondo stimato, per guardarlo "
                          "prima di elaborare tutto: se la stanza non e' "
                          "vuota (si vede ancora la persona) la stima non "
                          "ha abbastanza fotogrammi in cui quel punto e' "
                          "libero, e il resto non puo' funzionare.")
    ap.add_argument('--solo-sfondo', action='store_true',
                     help="stima lo sfondo, lo scrive (--salva-sfondo) e si "
                          "ferma subito, senza elaborare il video: serve a "
                          "controllare che la stanza stimata sia vuota "
                          "prima di impegnare minuti di elaborazione.")
    ap.add_argument('--solo-scheletro', action='store_true',
                     help="niente pannello del punteggio sotto, niente "
                          "numero del punteggio ne' scritta 'allarmi' in "
                          "alto a sinistra -- resta solo lo scheletro sopra "
                          "la tela scelta (e la scritta 'CADUTA RILEVATA' "
                          "quando scatta un allarme vero)")
    ap.add_argument('--senza-contatore', action='store_true',
                     help="toglie solo la scritta 'allarmi N' in alto a "
                          "sinistra, lasciando tutto il resto come "
                          "l'impostazione predefinita -- pannello del "
                          "punteggio sotto compreso. Indipendente da "
                          "--solo-scheletro.")
    ap.add_argument('--statico', action='store_true',
                     help="tratta ogni fotogramma come immagine isolata "
                          "(static_image_mode), invece di assumere un video "
                          "continuo: rileva meglio su una cartella di "
                          "fotogrammi non strettamente in sequenza, costa "
                          "qualcosa in piu' per fotogramma")
    ap.add_argument('--complessita', type=int, choices=[0, 1, 2], default=1,
                     help="complessita' del modello MediaPipe Pose: 2 e' il "
                          "piu' preciso (e il piu' lento), utile se la "
                          "persona non viene rilevata con 1")
    ap.add_argument('--conf-detezione', type=float, default=0.5,
                     help="soglia minima di confidenza per rilevare la posa; "
                          "abbassarla (es. 0.3) aiuta su fotogrammi mossi o "
                          "con la persona parzialmente fuori campo")
    a = ap.parse_args()
    sfondo_val = 255 if a.sfondo == 'bianco' else 26

    if a.eventi_da:
        a.video = sorted(
            os.path.join(a.eventi_da, nome)
            for nome in os.listdir(a.eventi_da)
            if nome.startswith('evt_')
            and os.path.isdir(os.path.join(a.eventi_da, nome)))
        print(f"{len(a.video)} cartelle evento trovate in {a.eventi_da}")

    import cv2

    if a.mantieni_overlay:
        if a.sfondo != 'ambiente':
            sys.exit('--mantieni-overlay richiede --sfondo ambiente')
        if not a.video:
            sys.exit("--mantieni-overlay richiede --video (una o piu' cartelle)")
        W, H = 640, 480
        files, files_tutti = [], []
        for cartella in a.video:
            for f in sorted(os.listdir(cartella)):
                if not f.lower().endswith(('.jpg', '.png', '.jpeg')):
                    continue
                percorso = os.path.join(cartella, f)
                files_tutti.append(percorso)
                if nel_tempo(f, a.da, a.a):
                    files.append(percorso)
        if a.da is not None or a.a is not None:
            print(f"{len(files)} fotogrammi nell'intervallo [{a.da}, {a.a}]")
        if not files:
            sys.exit('nessun fotogramma trovato')

        # Lo sfondo si stima su TUTTI i fotogrammi della sessione, non solo
        # su quelli da mostrare. E' il punto che faceva fallire la rimozione
        # su questa sessione: nell'intervallo richiesto la persona cade e
        # resta a terra a lungo nello stesso punto, quindi in quei pixel e'
        # presente nella maggioranza dei fotogrammi e la mediana diventa
        # LEI invece del pavimento. Con la sessione intera quei pixel sono
        # liberi quasi sempre, e la mediana torna a essere la stanza.
        print(f'Stima dello sfondo su {len(files_tutti)} fotogrammi '
              f'(tutta la sessione, non solo l\'intervallo)...')
        sfondo = ripulisci_hud(cv2, sfondo_mediano(cv2, files_tutti, W, H))
        if a.salva_sfondo:
            cv2.imwrite(a.salva_sfondo, sfondo)
            print(f'sfondo stimato scritto in: {a.salva_sfondo} '
                  f'-- guardalo: deve essere la stanza VUOTA')

        # Colori da PROTEGGERE dentro la sagoma della persona: li' lo
        # scheletro e' disegnato sopra il corpo, e senza protezione
        # sparirebbe insieme a lui.
        #
        # SOLO i colori dello scheletro e dell'allarme. I colori dei testi
        # dell'HUD sono esclusi apposta, ed e' il punto che faceva fallire
        # tutto: il bianco del testo (230,230,230) con una tolleranza larga
        # copre qualunque pixel chiaro --- pelle di braccia e gambe
        # comprese --- e proteggeva il corpo invece dello scheletro. I
        # testi stanno comunque negli angoli, fuori dalla sagoma: dentro
        # non serve proteggerli. Stesso motivo per il grigio della posa
        # non vista, troppo vicino a pelle e vestiti.
        colori_overlay = [
            (70, 70, 240),    # scheletro sopra soglia (rosso)
            (120, 230, 120),  # scheletro sotto soglia (verde)
            (60, 60, 250),    # bordo lampeggiante "CADUTA RILEVATA"
            (70, 70, 250),    # testo "CADUTA RILEVATA"
        ]
        tolleranza = a.tolleranza_overlay
        nucleo = np.ones((3, 3), np.uint8)
        nucleo_chiusura = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))

        # Le zone dell'HUD non si toccano mai: li' il testo e' quello vero
        # della diretta, e differisce dallo sfondo per costruzione.
        fuori_mano = np.zeros((H, W), bool)
        for x0, y0, x1, y1 in HUD_RETTANGOLI:
            fuori_mano[y0:y1, x0:x1] = True

        if a.salva_fotogrammi:
            os.makedirs(a.salva_fotogrammi, exist_ok=True)

        scrittore = None
        senza_sagoma = n_con_sagoma = 0
        quota_sostituita = 0.0
        for i, percorso in enumerate(files):
            originale = cv2.imread(percorso)
            if originale is None:
                continue
            # alto: l'immagine con lo scheletro gia' disegnato.
            # basso: il pannello col grafico vero, da non toccare mai.
            alto = scorpora_composito(cv2, originale, W, H)
            basso = originale[H:] if originale.shape[0] > H else None

            # Tutto cio' che si discosta dalla stanza vuota e' roba da
            # togliere: la persona, la sua ombra, qualunque cosa si muova.
            # Non serve riconoscerla, basta sapere com'e' la stanza senza.
            scarto = np.abs(alto.astype(np.int16)
                            - sfondo.astype(np.int16)).max(axis=2)
            diverso = scarto > a.soglia_sfondo
            # chiusura con nucleo largo: riempie i buchi interni, cioe' le
            # zone del corpo che per caso somigliano allo sfondo (un capo
            # chiaro su una parete chiara). Un nucleo 3x3 chiuderebbe buchi
            # di pochi pixel, non una maglietta.
            diverso = cv2.morphologyEx(diverso.astype(np.uint8),
                                       cv2.MORPH_CLOSE, nucleo_chiusura,
                                       iterations=3).astype(bool)

            # lo scheletro disegnato sopra il corpo va invece conservato
            protetti = np.zeros((H, W), bool)
            for c in colori_overlay:
                d = np.abs(alto.astype(np.int16) - np.array(c, np.int16))
                protetti |= (d.max(axis=2) <= tolleranza)
            protetti = cv2.dilate(protetti.astype(np.uint8), nucleo,
                                  iterations=1).astype(bool)

            da_sostituire = diverso & ~protetti & ~fuori_mano
            fuori_alto = alto.copy()
            fuori_alto[da_sostituire] = sfondo[da_sostituire]
            quota_sostituita += da_sostituire.mean()
            n_con_sagoma += 1

            fuori = (np.vstack([fuori_alto, basso]) if basso is not None
                     else fuori_alto)

            if a.salva and scrittore is None:
                scrittore = cv2.VideoWriter(
                    a.salva, cv2.VideoWriter_fourcc(*'mp4v'),
                    a.fps_riproduzione, (fuori.shape[1], fuori.shape[0]))
            if scrittore is not None:
                scrittore.write(fuori)
            if a.salva_fotogrammi:
                # qualita' 95: se poi passano da monta_video.py questa non
                # e' l'ultima codifica, e non si deve accumulare perdita
                cv2.imwrite(os.path.join(a.salva_fotogrammi,
                                         os.path.basename(percorso)),
                            fuori, [cv2.IMWRITE_JPEG_QUALITY, 95])
            if (i + 1) % 25 == 0:
                print(f'\r{i + 1}/{len(files)} fotogrammi elaborati',
                      end='', flush=True)

        if scrittore is not None:
            scrittore.release()
            print(f'\nsalvato: {a.salva}')
        if a.salva_fotogrammi:
            print(f'\n{len(files)} fotogrammi scritti in: {a.salva_fotogrammi}')
        if n_con_sagoma:
            media = 100.0 * quota_sostituita / n_con_sagoma
            print(f'area sostituita in media: {media:.1f}% del fotogramma '
                  f'(soglia {a.soglia_sfondo})')
            if media < 1.5:
                print("   -> troppo poco: la persona restera' visibile. "
                      'Riprova con --soglia-sfondo 18')
            elif media > 40.0:
                print('   -> troppo: sta cancellando anche la stanza. '
                      'Riprova con --soglia-sfondo 50')
        return

    import mediapipe as mp
    from geometry import MotoreGeometrico

    meta, modello, blob = carica(a.pacchetto)
    print(f"pacchetto: {a.pacchetto or 'installato'} — "
          f"{meta.get('feature_set', '?')}, {len(meta['colonne'])} colonne")
    colonne = meta['colonne']
    L, passo, soglia = (meta['lunghezza_finestra'], meta['passo_finestra'],
                        meta['soglia'])
    reg = meta['regola_decisione']
    persistenza, sospensione = reg['persistenza_finestre'], reg['sospensione_s']

    reg_tempi = reg_punteggi = reg_corse = None
    reg_allarmi = []
    if a.punteggi:
        reg_tempi, reg_punteggi, reg_corse, reg_allarmi = leggi_registro(
            a.punteggi, persistenza, sospensione)
        print(f'registro: {len(reg_tempi)} finestre decise dalla board, '
              f'{len(reg_allarmi)} allarmi '
              f'({", ".join("%.1f s" % t for t in reg_allarmi)})')
        print('   il punteggio mostrato e\' quello registrato, non '
              'ricalcolato')

    pose = mp.solutions.pose.Pose(static_image_mode=a.statico,
                                  model_complexity=a.complessita,
                                  min_detection_confidence=a.conf_detezione,
                                  min_tracking_confidence=a.conf_detezione)
    motore = MotoreGeometrico(k_integrali=meta['k_integrali'])
    buf, storia = deque(maxlen=L), deque(maxlen=460)

    W, H = 640, 480
    H_PAN = 190

    sfondi_cartella = []  # uno sfondo mediano per cartella, solo se serve
    if a.video:
        files = []
        # indici in 'files' che iniziano una cartella successiva alla prima:
        # a questi punti lo stato geometrico va azzerato, perche' due
        # cartelle sono due riprese distinte, non un video continuo.
        confini_cartella = set()
        # Per lo sfondo servono TUTTI i fotogrammi della cartella, non solo
        # quelli da mostrare: nell'intervallo richiesto la persona puo'
        # restare ferma a lungo nello stesso punto (per esempio a terra
        # dopo una caduta), e allora in quei pixel e' lei la maggioranza e
        # la mediana diventa lei invece della stanza.
        per_cartella_tutti = []
        for cartella in a.video:
            if files:
                confini_cartella.add(len(files))
            tutti_qui = []
            for f in sorted(os.listdir(cartella)):
                if not f.lower().endswith(('.jpg', '.png', '.jpeg')):
                    continue
                percorso = os.path.join(cartella, f)
                tutti_qui.append(percorso)
                if nel_tempo(f, a.da, a.a):
                    files.append(percorso)
            per_cartella_tutti.append(tutti_qui)
        sorgente, cap = iter(enumerate(files)), None

        if a.da is not None or a.a is not None:
            print(f"{len(files)} fotogrammi nell'intervallo "
                  f"[{a.da}, {a.a}]")

        # Un fotogramma piu' alto dell'inquadratura e' un composito salvato
        # in diretta (immagine + pannello): va scorporato, e il suo HUD va
        # ricostruito nello sfondo. Si riconosce dall'altezza, senza
        # bisogno di dirlo a mano.
        primo = cv2.imread(files[0]) if files else None
        composito = primo is not None and primo.shape[0] > H
        if composito:
            print('Fotogrammi compositi (%dx%d): tolgo il pannello gia\' '
                  'montato e ricostruisco le zone dell\'HUD della diretta.'
                  % (primo.shape[1], primo.shape[0]))

        if a.sfondo == 'ambiente':
            n_tot = sum(len(t) for t in per_cartella_tutti)
            print(f'Stima dello sfondo su {n_tot} fotogrammi '
                  f'(tutta la sessione, non solo l\'intervallo)...')
            for i, tutti_qui in enumerate(per_cartella_tutti):
                s = sfondo_mediano(cv2, tutti_qui, W, H)
                if composito:
                    s = ripulisci_hud(cv2, s)
                sfondi_cartella.append(s)
                print(f'\r  {i + 1}/{len(per_cartella_tutti)}', end='', flush=True)
            print()
            if a.salva_sfondo:
                cv2.imwrite(a.salva_sfondo, sfondi_cartella[0])
                print(f'sfondo stimato scritto in: {a.salva_sfondo}')
                print('   GUARDALO PRIMA DI PROSEGUIRE: deve essere la '
                      'stanza VUOTA. Se ci sei ancora tu, anche sbiadita, '
                      'quella sagoma finirebbe nel video.')
            if a.solo_sfondo:
                return
    else:
        cap = cv2.VideoCapture(a.camera)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        sorgente = None
    scrittore = None
    if a.salva:
        altezza_uscita = H if a.solo_scheletro else H + H_PAN
        scrittore = cv2.VideoWriter(
            a.salva, cv2.VideoWriter_fourcc(*'mp4v'), a.fps_riproduzione,
            (W, altezza_uscita))

    t0 = time.time()
    n_frame = corsa = n_allarmi = cartella_corrente = 0
    ultimo_allarme = -1e18
    p_corr = 0.0
    lampeggio = 0

    try:
        while True:
            if cap is not None:
                ok, frame = cap.read()
                if not ok:
                    break
            else:
                try:
                    idx, percorso = next(sorgente)
                except StopIteration:
                    break
                if idx in confini_cartella:
                    # nuova cartella: nuova ripresa, azzera lo stato
                    # geometrico e la finestra, non la retta del pavimento
                    # (resta valida per la stessa telecamera) ne' il
                    # conteggio allarmi complessivo
                    motore.reset()
                    buf.clear()
                    corsa = 0
                    cartella_corrente += 1
                frame = cv2.imread(percorso)
                if frame is None:
                    continue
            n_frame += 1
            if a.video and n_frame % 25 == 0:
                print(f'\r{n_frame}/{len(files)} fotogrammi elaborati',
                      end='', flush=True)
            t = time.time() - t0
            # scorpora: se e' un composito salvato in diretta tiene la sola
            # immagine, se e' gia' un fotogramma normale non cambia nulla
            frame = scorpora_composito(cv2, frame, W, H)
            h, w = frame.shape[:2]

            r = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            lm = r.pose_landmarks.landmark if r.pose_landmarks else None
            wl = r.pose_world_landmarks.landmark if r.pose_world_landmarks else None

            if reg_tempi is not None:
                # Il punteggio NON si ricalcola: si legge dal registro della
                # board, alla riga piu' recente non successiva all'istante
                # di questo fotogramma -- cioe' esattamente il valore che il
                # sistema mostrava in quel momento.
                t_frame = tempo_da_nome(percorso) if sorgente else None
                if t_frame is not None:
                    fino_a = int(np.searchsorted(reg_tempi, t_frame,
                                                 side='right'))
                    if fino_a > len(storia):
                        for k in range(len(storia), fino_a):
                            storia.append(float(reg_punteggi[k]))
                    if fino_a > 0:
                        p_corr = float(reg_punteggi[fino_a - 1])
                        corsa = int(reg_corse[fino_a - 1])
                    # lampeggio sugli allarmi veri della board
                    while (reg_allarmi and n_allarmi < len(reg_allarmi)
                           and t_frame >= reg_allarmi[n_allarmi]):
                        n_allarmi += 1
                        lampeggio = 18
            else:
                f = motore.fotogramma(lm, wl, w, h, meta['fps_assunti'])
                buf.append([f[c] for c in colonne])

                if len(buf) == L and n_frame % passo == 0:
                    X = np.asarray(buf, np.float32)[None]
                    p_corr = float(modello.predict_proba(
                        riassumi(normalizza(X, blob)))[0, 1])
                    storia.append(p_corr)
                    sopra = p_corr >= soglia
                    corsa = corsa + 1 if sopra else 0
                    if (corsa >= persistenza
                            and (t - ultimo_allarme) >= sospensione):
                        ultimo_allarme = t
                        n_allarmi += 1
                        lampeggio = 18

            # --- lo scheletro, sopra la tela scelta ---
            if a.sfondo == 'originale':
                chiaro = False
                tela = frame.copy()
            elif a.sfondo == 'ambiente':
                chiaro = False
                tela = sfondi_cartella[cartella_corrente].copy()
            else:
                chiaro = sfondo_val > 127
                tela = np.full((H, W, 3), sfondo_val, np.uint8)
            testo_hud = (90, 90, 90) if chiaro else (170, 170, 170)
            if a.schema == 'rosso_verde':
                # BGR: rosso sopra soglia, verde sotto, grigio se non vista
                colore = ((40, 40, 220) if p_corr >= soglia
                          else (40, 150, 40) if lm else
                          ((190, 190, 190) if chiaro else (90, 90, 90)))
            else:
                colore = ((70, 70, 240) if p_corr >= soglia
                          else (200, 200, 200) if lm else (90, 90, 90))
            disegna(cv2, tela, lm, w, h, colore)
            if not a.solo_scheletro:
                if lm is None:
                    cv2.putText(tela, 'posa non rilevata', (18, H - 22),
                                cv2.FONT_HERSHEY_SIMPLEX, .6, testo_hud, 1,
                                cv2.LINE_AA)
                cv2.putText(tela, f'{p_corr:.3f}', (18, 44),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.1, colore, 2,
                            cv2.LINE_AA)
                if not a.senza_contatore:
                    cv2.putText(tela, f'allarmi {n_allarmi}', (18, 74),
                                cv2.FONT_HERSHEY_SIMPLEX, .55, testo_hud, 1,
                                cv2.LINE_AA)
            if lampeggio > 0:
                lampeggio -= 1
                cv2.rectangle(tela, (0, 0), (W - 1, H - 1), (60, 60, 250), 6)
                cv2.putText(tela, 'CADUTA RILEVATA', (W // 2 - 165, H // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (70, 70, 250), 3,
                            cv2.LINE_AA)

            if a.solo_scheletro:
                fuori = tela
            else:
                fuori = np.vstack([tela, pannello(cv2, storia, soglia, W, H_PAN,
                                                  corsa, persistenza,
                                                  sfondo=sfondo_val)])
            if scrittore is not None:
                scrittore.write(fuori)
            else:
                cv2.imshow('rilevamento cadute — cio che il sistema vede', fuori)
                if cv2.waitKey(int(1000 / a.fps_riproduzione)) & 0xFF == 27:
                    break
    except KeyboardInterrupt:
        pass
    finally:
        if cap is not None:
            cap.release()
        if scrittore is not None:
            scrittore.release()
            print(f'salvato: {a.salva}')
        cv2.destroyAllWindows()

    print(f'\nfotogrammi {n_frame}   allarmi {n_allarmi}')


if __name__ == '__main__':
    main()
