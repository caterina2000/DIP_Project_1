"""
Costanti del progetto. Unica fonte: nessun modulo ridefinisce questi valori.

Perche' un file solo
--------------------
Nel progetto precedente le stesse costanti erano ridefinite a livello di
modulo in tre punti diversi -- SEQUENCE_LENGTH valeva 45 in config, 75 in
demo_realtime e 39 nei metadati di una run; FPS valeva 18, 30, 15 e 20 in
quattro file. Le feature dinamiche si dividono per dt = 1/FPS, quindi lo
stesso movimento produceva numeri diversi a seconda di quale file lo
calcolava. Qui i valori stanno solo qui, e chi ne vuole uno diverso lo passa
come argomento invece di ridefinirlo.
"""

import os

# ============================================================
# PERCORSI
# ============================================================
RADICE = os.path.dirname(os.path.abspath(__file__))

DATASET_DIR = os.path.join(RADICE, 'dataset')
RAW_DIR = os.path.join(DATASET_DIR, 'up_fall', 'raw')        # giunzione
FEATURE_DIR = os.path.join(DATASET_DIR, 'processed', 'features')
RISULTATI_DIR = os.path.join(RADICE, 'risultati')

# Un CSV per rappresentazione. I nomi seguono le rappresentazioni del Cap. 2.
CSV = {
    'A':  os.path.join(FEATURE_DIR, 'feature_A_pca2d.csv'),
    'A2': os.path.join(FEATURE_DIR, 'feature_A2_physics3d.csv'),
    'A3': os.path.join(FEATURE_DIR, 'feature_A3_bodycentric.csv'),
    'B':  os.path.join(FEATURE_DIR, 'feature_B_scheletro.csv'),
}

# ============================================================
# ACQUISIZIONE
# ============================================================
# UP-Fall e' consolidato a ~18 fps: gli autori hanno omogeneizzato il
# campionamento sulla telecamera con meno fotogrammi acquisiti.
FPS_DATASET = 18.0

# La board regge ~9 fps con MediaPipe a persona singola. Le feature dinamiche
# dipendono da dt, quindi addestrare a 18 e girare a 9 le cambia di scala:
# per questo il dataset viene sottocampionato di FRAME_STEP in addestramento.
FPS_ESERCIZIO = 9.0
FRAME_STEP = int(round(FPS_DATASET / FPS_ESERCIZIO))          # 2

W_IMMAGINE, H_IMMAGINE = 640.0, 480.0

# ============================================================
# FINESTRE TEMPORALI
# ============================================================
# 22 campioni a 9 fps = 2,44 s. La durata e' la stessa dei 45 campioni a
# 18 fps della prima impostazione: cambia il numero di campioni, non il
# tempo coperto.
LUNGHEZZA_FINESTRA = 22
PASSO_FINESTRA = 2

# ============================================================
# ETICHETTATURA
# ============================================================
# Etichette per fotogramma:
#   0  attivita' quotidiana o pre-caduta
#   1  caduta in corso, dalla perdita di equilibrio all'arrivo a terra
#   2  post-caduta, la persona e' a terra
#
# Le soglie qui sotto trasformano una sequenza di etichette per fotogramma
# nell'etichetta della finestra. NON sono ottimizzate: sono i valori
# ereditati, ed esiste un'analisi di sensibilita' da fare.
# Il criterio e' K-SU-M: servono almeno K fotogrammi della classe dentro un
# blocco di M consecutivi. Con M == K diventa «K consecutivi stretti», con M
# molto grande degenera nel conteggio sull'intera finestra: i due estremi
# sono casi particolari dello stesso parametro.
#
# I NOMI COINCIDONO con i parametri di src.etichettatura.etichetta_finestra,
# che li legge da qui. Prima del 2026-08-26 erano dichiarati in due posti e
# ne comandava uno solo: config diceva 5 e 10, il modulo aveva i propri
# default, e addestra.py scriveva nel run_metadata i valori di config, cioe'
# documentava parametri che non governavano la run (ISS-112).
K_CADUTA = 5     # fotogrammi di classe 1 richiesti nel blocco
M_BLOCCO = 8     # ampiezza del blocco per la classe 1
K_TERRA = 10     # fotogrammi di classe 2 richiesti nel blocco
M_TERRA = 15     # ampiezza del blocco per la classe 2

# Raccolte in un dizionario perche' vanno passate insieme e registrate
# insieme: e' l'unico modo perche' il metadato non possa divergere.
# Le finestre di confine: quelle che contengono fotogrammi di classe 1 o 2
# ma non abbastanza da superare il criterio K-su-M. Con False valgono 0, cioe'
# negativi puliti, ed e' un'ipotesi sul confine invece che un dato. Con True
# sono escluse dall'addestramento come qualunque altra finestra ambigua.
#
# Sta a False perche' cambiarlo cambia ogni numero della tesi: va acceso
# insieme a un riaddestramento completo, non da solo.
ESCLUDI_FINESTRE_INCERTE = False

SOGLIE_ETICHETTATURA = {'k_caduta': K_CADUTA, 'm_blocco': M_BLOCCO,
                        'k_terra': K_TERRA, 'm_terra': M_TERRA}

# ============================================================
# ADDESTRAMENTO
# ============================================================
SEME = 42
BETA = 2.0                       # F-beta: il recall pesa il quadruplo
EPOCHE = 40
BATCH = 16
LEARNING_RATE = 0.001
N_ALBERI = 50                    # foresta casuale
K_INTEGRALI = 31   # fotogrammi, ~1,7 s a 18 fps. Misurato in EXP-053.

# La stessa finestra espressa come DURATA, ed e' questa la forma che va
# trasmessa al dispositivo (ISS-148). Il conteggio dipende da chi produce i
# fotogrammi: 31 sono 1,72 s a 18 fps, ma 4,27 s alla cadenza di 7,26 fps
# misurata sulla board. Il modello ha imparato su 1,72 s di storia, e sono
# 1,72 s che deve ricevere in esercizio, non 31 fotogrammi.
#
# A 18 fps costanti le due formulazioni sono la stessa cosa: verificato, il
# motore geometrico produce valori identici bit per bit (scarto 0,000e+00 su
# tutte e 33 le grandezze). Quindi feature_v3.csv, e ogni numero della tesi
# che ne discende, non cambiano.
DURATA_INTEGRALI_S = K_INTEGRALI / FPS_DATASET       # 1,7222 s
