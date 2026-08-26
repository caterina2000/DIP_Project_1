"""
Dallo scheletro MediaPipe alle grandezze che descrivono la dinamica del corpo.

I tre bacini
------------
Non sono tre modelli in gara: sono tre modi di descrivere lo stesso movimento
a partire dagli stessi 33 punti, e insieme formano il bacino di candidate da
cui il DTW sceglie il sottoinsieme da dare alla rete.

    A1  la sagoma come ellisse       il corpo come nuvola di punti nel piano
                                     immagine; assi principali, rapporto,
                                     inclinazione. Non conosce l'anatomia.
    A2  la fisica in tre dimensioni  usa i world landmark, quindi non e' una
                                     proiezione. Angolo del tronco rispetto
                                     alla verticale, velocita' in m/s.
    A3  geometria riferita al corpo  tutto diviso per la lunghezza del torso:
                                     adimensionale, quindi indipendente da
                                     distanza e corporatura.

I NOMI SONO PREFISSATI, e non e' pedanteria: `d_trunk_angle` esisteva sia in
A2 sia in A3 con unita' diverse -- gradi per fotogramma contro gradi al
secondo, mediane 0,167 contro 1,700. Unendo i bacini senza prefisso le due
colonne si sarebbero fuse in silenzio.

Le tre correzioni rispetto alla versione precedente
---------------------------------------------------
1. ANGOLO SROTOLATO. `arctan2` avvolge a +-180 gradi. Nella versione
   precedente il 23,6% dei fotogrammi stava oltre i 170 gradi -- cioe'
   proprio nella fase a terra -- e 91 fotogrammi avevano una derivata fino a
   6480 gradi/s, che e' esattamente 360 gradi per 18 fps: un giro completo in
   un fotogramma. Qui l'angolo viene srotolato PRIMA di derivare.

2. dt OVUNQUE. A1 calcolava differenze per fotogramma, A2 e A3 dividevano per
   dt. Confrontare A1 con A3 confrontava anche due convenzioni temporali, e
   cambiando frame rate solo una delle due cambiava scala. Qui tutte le
   derivate sono per secondo.

3. NIENTE ENERGIE SOMMA-DI-QUADRATI. Ogni bacino ne aveva una: sommavano
   quadrati di gradi, rapporti adimensionali, pixel e frazioni di immagine,
   con rapporti fra massimo e mediana di 728.079 in A1 e 750.174 in A2.
   Dimensionalmente prive di senso e all'origine del fattore 646 fra le
   scale. Sostituite dalle grandezze integrali.

Le grandezze integrali stanno QUI, e non in uno script a parte
--------------------------------------------------------------
Nel progetto precedente erano calcolate a posteriori con `pandas.rolling()`
su un CSV completo, cioe' a registrazione conclusa. E' il motivo per cui non
sono mai arrivate sul dispositivo: la board riceve un fotogramma e deve
decidere, il video intero non ce l'ha. Il modello schierato infatti usa A3 a
dieci colonne, senza integrali, e ogni risultato su A3i e' un calcolo fuori
linea.

Qui il motore tiene un BUFFER CIRCOLARE degli ultimi K fotogrammi, quindi le
stesse grandezze si calcolano identiche fuori linea e in tempo reale. E'
questa la differenza fra un risultato e un sistema installabile.

Perche' accumulare invece di derivare: una derivata divide la differenza fra
due stime rumorose per un dt piccolo, e amplifica il rumore; un accumulo lo
cancella, perche' il rumore a media nulla si somma a zero mentre il movimento
vero si somma. E una caduta E' un'escursione: misurare quanto il tronco ha
ruotato in tutto e' piu' fedele al fenomeno di quanto ruota adesso.

Le pose mancanti
----------------
Quando la posa non e' stimabile le grandezze valgono zero e il fotogramma e'
marcato has_pose = 0. La marcatura serve: uno zero non e' neutro. Un angolo
del tronco pari a zero descrive un tronco ORIZZONTALE, e una sequenza di zeri
seguita da un valore reale produce una derivata esplosiva. Per la stessa
ragione lo stato temporale viene azzerato a ogni posa mancante, cosi' le
derivate non attraversano il buco.
"""

import math
from collections import deque
from typing import Optional

import numpy as np

# Indici MediaPipe Pose
NASO = 0
SPALLA_SX, SPALLA_DX = 11, 12
ANCA_SX, ANCA_DX = 23, 24
GINOCCHIO_SX, GINOCCHIO_DX = 25, 26
CAVIGLIA_SX, CAVIGLIA_DX = 27, 28

# Punti su cui A1 adatta l'ellisse. Sette, non cinque: nella versione
# precedente processing.py ne usava sette e demo_realtime.py cinque, quindi
# la demo calcolava una A1 diversa da quella di addestramento.
PUNTI_ELLISSE = [NASO, SPALLA_SX, SPALLA_DX, ANCA_SX, ANCA_DX,
                 CAVIGLIA_SX, CAVIGLIA_DX]

NOMI_A1 = ['A1_asse_mag', 'A1_asse_min', 'A1_allungamento', 'A1_inclinazione',
           'A1_d_inclinazione', 'A1_d_allungamento', 'A1_d_asse_mag',
           'A1_vx', 'A1_vy']
# A2 non ha grandezze di traslazione del bacino, e non e' una dimenticanza.
# I world landmark sono CENTRATI sul punto medio delle anche: il bacino e'
# l'origine del riferimento e non si muove per costruzione. Misurato su 40
# fotogrammi consecutivi, la sua deviazione standard e' 0,00003 m -- tre
# centesimi di millimetro -- contro 0,0175 m del naso, quattrocento volte
# tanto. Le grandezze A2_hip_vy e A2_hip_vel della prima versione misuravano
# quindi rumore numerico, ed erano indistinguibili da zero. Rimosse.
# La traslazione assoluta del corpo con i world landmark NON e' misurabile:
# la misurano A1 e A3, nel piano immagine.
NOMI_A2 = ['A2_angolo_tronco', 'A2_d_angolo_tronco', 'A2_vel_ang_tronco',
           'A2_testa_vel', 'A2_testa_rel_y']
NOMI_A3 = ['A3_torso_len', 'A3_angolo_tronco', 'A3_d_angolo_tronco',
           'A3_testa_rel_y', 'A3_ginocchia_rel_y', 'A3_caviglie_rel_y',
           'A3_larghezza', 'A3_hip_vel', 'A3_testa_vel_rel']

# Grandezze integrali, una terna per bacino. Accumulate su finestra mobile,
# mai divise per dt.
#   escursione  ampiezza dell'angolo nella finestra (massimo meno minimo)
#   percorso    lunghezza del cammino del punto seguito
#   discesa     di quanto il punto seguito e' sceso rispetto al suo massimo
#
# Il punto seguito NON e' lo stesso nei tre bacini, e va detto:
#   A1  il baricentro della nuvola di punti, nel piano immagine
#   A3  il bacino, nel piano immagine
#   A2  il NASO, in coordinate world -- cioe' la sua posizione relativa alle
#       anche. Nella prima versione era il bacino, che in quel riferimento e'
#       l'origine: percorso e discesa misuravano rumore. Il naso invece si
#       muove davvero, e in una caduta percorre un arco lungo e scende
#       parecchio rispetto al bacino: e' cio' che si voleva misurare.
NOMI_INT_A1 = ['A1_escursione', 'A1_percorso', 'A1_discesa']
NOMI_INT_A2 = ['A2_escursione', 'A2_percorso', 'A2_discesa']
NOMI_INT_A3 = ['A3_escursione', 'A3_percorso', 'A3_discesa']
NOMI_INTEGRALI = NOMI_INT_A1 + NOMI_INT_A2 + NOMI_INT_A3

NOMI = NOMI_A1 + NOMI_A2 + NOMI_A3 + NOMI_INTEGRALI


def _srotola(angolo_gradi: float, precedente: Optional[float],
             periodo: float = 360.0) -> float:
    """
    Riporta l'angolo vicino al precedente, togliendo i salti di `periodo`.

    Senza questo, un tronco che oscilla attorno a +-180 gradi -- cioe' una
    persona distesa, la fase piu' lunga -- produce derivate di un giro intero
    per fotogramma. E' il difetto che rendeva d_trunk_angle quasi
    indistinguibile da rumore.

    IL PERIODO NON E' SEMPRE 360. Un vettore ha periodo 360: il tronco punta
    in una direzione precisa, e ruotarlo di mezzo giro lo capovolge. L'asse
    di un'ellisse invece ha periodo 180, perche' un autovettore e il suo
    opposto descrivono lo stesso asse: senza questa distinzione
    l'inclinazione dell'ellisse salta di 180 gradi a meta' rotazione, e la
    derivata registra un movimento che non c'e' stato.
    """
    if precedente is None:
        return angolo_gradi
    return angolo_gradi - periodo * round((angolo_gradi - precedente) / periodo)


class MotoreGeometrico:
    """
    Calcola i tre bacini su un fotogramma alla volta, mantenendo lo stato
    minimo necessario alle derivate.

    Lo stato e' esplicito e azzerabile: `reset()` va chiamato all'inizio di
    ogni ripresa e a ogni posa mancante.
    """

    # Il valore predefinito e' scritto qui e non letto da config, perche'
    # questo modulo viene copiato tale e quale sulla board, dove config.py
    # non esiste: un motore geometrico non deve dipendere dalla
    # configurazione del progetto per avere un valore di ripiego. Chi lo usa
    # dal progetto passa comunque `k_integrali` esplicitamente.
    K_PREDEFINITO = 31

    def __init__(self, k_integrali: int = None):
        self.K = int(k_integrali or self.K_PREDEFINITO)
        self.reset()

    def reset(self):
        self._a1 = None      # (inclinazione, allungamento, asse_mag, cx, cy)
        self._a2 = None      # (angolo, mid_hip, naso)
        self._a3 = None      # (angolo, hip_norm, testa_rel)
        # Buffer circolari per le grandezze integrali: per ogni bacino la
        # storia recente di (angolo, posizione_x, posizione_y, scala).
        # Azzerarli a ogni posa mancante e' voluto: un accumulo che
        # attraversa un buco misurerebbe uno spostamento mai avvenuto.
        self._buf = {b: deque(maxlen=self.K) for b in ('A1', 'A2', 'A3')}

    # ---------------------------------------------------------------- A1
    def _ellisse(self, punti: np.ndarray):
        """Autovalori e autovettori della covarianza dei punti del corpo."""
        if len(punti) < 3:
            return None
        c = np.cov((punti - punti.mean(axis=0)).T)
        if not np.all(np.isfinite(c)):
            return None
        val, vec = np.linalg.eigh(c)
        ordine = np.argsort(val)[::-1]
        return val[ordine], vec[:, ordine]

    def a1(self, landmarks, w: float, h: float, dt: float) -> dict:
        f = {k: 0.0 for k in NOMI_A1}
        pts = []
        for i in PUNTI_ELLISSE:
            if i < len(landmarks):
                lm = landmarks[i]
                pts.append([lm.x * w, lm.y * h])
        if len(pts) < 3:
            return f
        p = np.asarray(pts, np.float32)
        e = self._ellisse(p)
        if e is None:
            return f
        val, vec = e

        asse_mag = math.sqrt(max(float(val[0]), 0.0))
        asse_min = math.sqrt(max(float(val[1]), 0.0))
        allung = asse_mag / (asse_min + 1e-6)
        # NON in valore assoluto: l'assoluto cancellava il verso della
        # rotazione e faceva rimbalzare il valore attraversando lo zero,
        # producendo una derivata falsa.
        incl = math.degrees(math.atan2(vec[1, 0], vec[0, 0]))
        cx, cy = float(p[:, 0].mean() / w), float(p[:, 1].mean() / h)

        if self._a1 is not None:
            p_inc, p_all, p_mag, p_cx, p_cy = self._a1
            incl = _srotola(incl, p_inc, periodo=180.0)
            f['A1_d_inclinazione'] = (incl - p_inc) / dt
            f['A1_d_allungamento'] = (allung - p_all) / dt
            f['A1_d_asse_mag'] = (asse_mag - p_mag) / dt
            f['A1_vx'] = (cx - p_cx) / dt
            f['A1_vy'] = (cy - p_cy) / dt
        self._a1 = (incl, allung, asse_mag, cx, cy)

        f.update({'A1_asse_mag': asse_mag, 'A1_asse_min': asse_min,
                  'A1_allungamento': allung, 'A1_inclinazione': incl})
        return f

    # ---------------------------------------------------------------- A2
    def a2(self, world, dt: float) -> dict:
        f = {k: 0.0 for k in NOMI_A2}
        if world is None or len(world) <= ANCA_DX:
            return f
        P = lambda i: np.array([world[i].x, world[i].y, world[i].z], np.float32)
        naso = P(NASO)
        sh = (P(SPALLA_SX) + P(SPALLA_DX)) / 2.0
        hip = (P(ANCA_SX) + P(ANCA_DX)) / 2.0

        tronco = sh - hip
        L = float(np.linalg.norm(tronco))
        if L < 1e-8:
            return f

        # Angolo rispetto alla verticale del riferimento dei world landmark.
        # Va detto che quel riferimento e' canonico e centrato sulle anche,
        # non allineato alla gravita' reale: l'angolo e' quindi una misura
        # relativa al corpo, non assoluta. Sui dati resta pero' informativo,
        # ed e' l'unica delle tre a non essere una proiezione.
        cos_t = float(np.dot(tronco, [0.0, -1.0, 0.0]) / (L + 1e-9))
        ang = math.degrees(math.acos(max(-1.0, min(1.0, cos_t))))

        if self._a2 is not None:
            p_ang, p_naso, _p_L = self._a2
            ang = _srotola(ang, p_ang)
            d = (ang - p_ang) / dt
            f['A2_d_angolo_tronco'] = d
            f['A2_vel_ang_tronco'] = abs(d)
            # In coordinate world la posizione del naso e' gia' relativa alle
            # anche, quindi questa e' una velocita' vera. La velocita' del
            # BACINO nello stesso riferimento non lo sarebbe: vedi la nota
            # accanto a NOMI_A2.
            f['A2_testa_vel'] = float(np.linalg.norm((naso - p_naso) / dt))
        self._a2 = (ang, naso, L)

        f['A2_angolo_tronco'] = ang
        # normalizzata sulla lunghezza del tronco: senza, dipendeva
        # dall'altezza della persona
        f['A2_testa_rel_y'] = float((hip[1] - naso[1]) / L)
        return f

    # ---------------------------------------------------------------- A3
    def a3(self, landmarks, w: float, h: float, dt: float) -> dict:
        f = {k: 0.0 for k in NOMI_A3}
        if landmarks is None or len(landmarks) <= CAVIGLIA_DX:
            return f
        P = lambda i: np.array([landmarks[i].x * w, landmarks[i].y * h], np.float32)
        naso = P(NASO)
        sh = (P(SPALLA_SX) + P(SPALLA_DX)) / 2.0
        hip = (P(ANCA_SX) + P(ANCA_DX)) / 2.0
        gin = (P(GINOCCHIO_SX) + P(GINOCCHIO_DX)) / 2.0
        cav = (P(CAVIGLIA_SX) + P(CAVIGLIA_DX)) / 2.0

        tronco = sh - hip
        L = float(np.linalg.norm(tronco))
        if L < 1e-6:
            return f

        ang = math.degrees(math.atan2(float(tronco[1]), float(tronco[0])))
        hip_norm = np.array([hip[0] / w, hip[1] / h], np.float32)
        testa_rel = (naso - hip) / L

        if self._a3 is not None:
            p_ang, p_hip, p_testa = self._a3
            ang = _srotola(ang, p_ang)          # <- la correzione principale
            f['A3_d_angolo_tronco'] = (ang - p_ang) / dt
            # spostamento del bacino in lunghezze di torso al secondo
            scala = max(L / max(w, h), 1e-6)
            f['A3_hip_vel'] = float(np.linalg.norm(hip_norm - p_hip) / (scala * dt))
            f['A3_testa_vel_rel'] = float(np.linalg.norm(testa_rel - p_testa) / dt)
        self._a3 = (ang, hip_norm, testa_rel)

        f.update({
            'A3_torso_len': L,
            'A3_angolo_tronco': ang,
            'A3_testa_rel_y': float((hip[1] - naso[1]) / L),
            'A3_ginocchia_rel_y': float((hip[1] - gin[1]) / L),
            'A3_caviglie_rel_y': float((hip[1] - cav[1]) / L),
            'A3_larghezza': float(np.linalg.norm(P(SPALLA_SX) - P(SPALLA_DX)) / L),
        })
        return f

    # ------------------------------------------------------- INTEGRALI
    def _integrali(self, bacino: str, angolo: float, x: float, y: float,
                   scala: float) -> dict:
        """
        Aggiorna il buffer del bacino e restituisce le tre grandezze accumulate.

        `scala` rende il percorso adimensionale: e' la lunghezza del torso per
        A2 e A3, l'asse maggiore dell'ellisse per A1. Senza, il percorso
        sarebbe in pixel e dipenderebbe dalla distanza dalla telecamera.

        Il segno della discesa: y cresce verso il basso nel piano immagine,
        quindi scendere significa y crescente e la discesa e' y - min(y).
        """
        b = self._buf[bacino]
        b.append((angolo, x, y, max(scala, 1e-6)))
        if len(b) < 2:
            return {f'{bacino}_escursione': 0.0, f'{bacino}_percorso': 0.0,
                    f'{bacino}_discesa': 0.0}

        ang = [v[0] for v in b]
        xs = [v[1] for v in b]
        ys = [v[2] for v in b]
        sc = b[-1][3]

        escursione = max(ang) - min(ang)
        percorso = sum(math.hypot(xs[i] - xs[i - 1], ys[i] - ys[i - 1])
                       for i in range(1, len(b))) / sc
        discesa = (ys[-1] - min(ys)) / sc
        return {f'{bacino}_escursione': float(escursione),
                f'{bacino}_percorso': float(percorso),
                f'{bacino}_discesa': float(discesa)}

    # ---------------------------------------------------------------- tutto
    def fotogramma(self, landmarks, world, w: float, h: float,
                   fps: float) -> dict:
        """
        I tre bacini su un fotogramma. Se la posa manca, azzera lo stato e
        restituisce zeri: cosi' la derivata non attraversa il buco.
        """
        if landmarks is None:
            self.reset()
            return {k: 0.0 for k in NOMI}
        dt = 1.0 / max(fps, 1e-6)
        f = {}
        f.update(self.a1(landmarks, w, h, dt))
        f.update(self.a2(world, dt))
        f.update(self.a3(landmarks, w, h, dt))

        # Le grandezze integrali si appoggiano allo stato appena calcolato,
        # cosi' non ricalcolano nulla: leggono angolo, posizione e scala di
        # ciascun bacino e li accumulano sul buffer.
        if self._a1 is not None:
            incl, _all, mag, cx, cy = self._a1
            f.update(self._integrali('A1', incl, cx, cy, mag / max(w, h)))
        if self._a2 is not None:
            # Il naso, non il bacino: in coordinate world il bacino e'
            # l'origine. La y si passa cosi' com'e': nei world landmark
            # cresce verso il BASSO come nel piano immagine -- verificato,
            # naso y = -0,55 e caviglie y = +0,68 su persona eretta -- ed e'
            # la convenzione che `discesa` si aspetta. La scala e' la
            # lunghezza del tronco, cosi' il percorso resta adimensionale
            # come negli altri due bacini.
            ang, naso, L = self._a2
            f.update(self._integrali('A2', ang, float(naso[0]),
                                     float(naso[1]), L))
        if self._a3 is not None:
            ang, hipn, _tr = self._a3
            f.update(self._integrali('A3', ang, float(hipn[0]), float(hipn[1]),
                                     f['A3_torso_len'] / max(w, h)))

        for k in NOMI:
            f.setdefault(k, 0.0)
        return f
