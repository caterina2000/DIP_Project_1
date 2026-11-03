"""
Prova a file d'oro sul motore geometrico.

Perche' questa e' la prova che serve piu' di tutte
--------------------------------------------------
`geometry.py` produce le trentadue grandezze da cui viene OGNI numero della
tesi: l'F2 di laboratorio, il trasferimento all'archivio esterno, i punteggi
delle sessioni domestiche. Se qualcuno lo modifica, tutti quei numeri cambiano
**in silenzio**: non c'e' errore, non c'e' eccezione, ci sono solo risultati
diversi da quelli scritti nel testo.

Questa prova tiene una copia dei valori attesi e segnala se cambiano. Non dice
che siano giusti --- dice che sono gli stessi su cui la tesi e' stata scritta.
Se una modifica e' voluta, si rigenera il file d'oro e si registra il perche':

    python prove/prova_geometria.py --aggiorna

Perche' i landmark sono finti, e va bene
----------------------------------------
La sequenza di ingresso e' costruita analiticamente e non viene da MediaPipe:
una figura in piedi che si inclina fino a terra, piu' una fase immobile. Cosi'
la prova gira in qualunque ambiente, anche senza MediaPipe installato, ed e'
deterministica su qualunque macchina --- nessun generatore casuale, nessun
file di immagini.

Quello che si verifica non e' la qualita' della stima di posa, che non e'
nostra: e' che a parita' di ingresso il motore dia lo stesso risultato di ieri.
"""

import argparse
import os
import sys
import unittest

import numpy as np

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RADICE not in sys.path:
    sys.path.insert(0, RADICE)

from src.geometry import MotoreGeometrico            # noqa: E402

ATTESO = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      'dati', 'geometria_attesa.npz')

N_LANDMARK = 33
N_FOTOGRAMMI = 40
W, H, FPS = 640.0, 480.0, 9.0


class Punto:
    """Il minimo che il motore geometrico legge di un landmark: x, y, z."""

    __slots__ = ('x', 'y', 'z')

    def __init__(self, x, y, z):
        self.x, self.y, self.z = float(x), float(y), float(z)


def _corpo(inclinazione, altezza, scala=1.0):
    """
    Trentatre punti in coordinate normalizzate, nella disposizione di
    MediaPipe Pose. `inclinazione` in radianti attorno all'anca: 0 e' in piedi,
    pi/2 e' orizzontale. `altezza` e' la quota dell'anca, 0 in alto.

    Non e' un modello anatomico: e' una figura rigida che si inclina, e serve
    solo a produrre una sequenza di ingresso ripetibile.
    """
    c, s = np.cos(inclinazione), np.sin(inclinazione)

    # (avanti lungo l'asse del corpo, laterale) rispetto all'anca, in unita'
    # di altezza del torso. L'ordine e' quello dei 33 punti di MediaPipe.
    schema = [
        (0.62, 0.00),                                    # 0  naso
        (0.64, -0.03), (0.65, -0.04), (0.66, -0.05),     # 1-3  occhio sx
        (0.64, 0.03), (0.65, 0.04), (0.66, 0.05),        # 4-6  occhio dx
        (0.60, -0.07), (0.60, 0.07),                     # 7-8  orecchie
        (0.56, -0.03), (0.56, 0.03),                     # 9-10 bocca
        (0.42, -0.13), (0.42, 0.13),                     # 11-12 spalle
        (0.22, -0.15), (0.22, 0.15),                     # 13-14 gomiti
        (0.03, -0.16), (0.03, 0.16),                     # 15-16 polsi
        (-0.02, -0.17), (-0.02, 0.17),                   # 17-18 mignoli
        (-0.03, -0.15), (-0.03, 0.15),                   # 19-20 indici
        (0.00, -0.14), (0.00, 0.14),                     # 21-22 pollici
        (0.00, -0.08), (0.00, 0.08),                     # 23-24 anche
        (-0.26, -0.08), (-0.26, 0.08),                   # 25-26 ginocchia
        (-0.52, -0.08), (-0.52, 0.08),                   # 27-28 caviglie
        (-0.55, -0.09), (-0.55, 0.09),                   # 29-30 talloni
        (-0.58, -0.07), (-0.58, 0.07),                   # 31-32 punte
    ]

    punti = []
    for avanti, lato in schema:
        # inclinando, cio' che era altezza diventa distanza orizzontale
        y = altezza - scala * avanti * c
        x = 0.5 + scala * (avanti * s * 0.55 + lato)
        punti.append(Punto(x, y, scala * lato * 0.5))
    return punti


def sequenza():
    """
    Quaranta fotogrammi: dieci in piedi, quindici di caduta, quindici a terra.
    Restituisce (landmark_immagine, landmark_mondo) per ciascun fotogramma.
    """
    fuori = []
    for i in range(N_FOTOGRAMMI):
        if i < 10:
            frazione = 0.0
        elif i < 25:
            frazione = (i - 10) / 15.0
        else:
            frazione = 1.0
        # profilo morbido: la caduta accelera e poi si ferma
        f = frazione * frazione * (3.0 - 2.0 * frazione)
        inclinazione = f * (np.pi / 2.0)
        altezza = 0.88 - 0.32 * f

        immagine = _corpo(inclinazione, altezza, scala=0.62)
        # i landmark «mondo» sono in metri e centrati sull'anca
        mondo = [Punto((p.x - 0.5) * 1.7, (p.y - altezza) * 1.7, p.z * 1.7)
                 for p in _corpo(inclinazione, altezza, scala=0.62)]
        fuori.append((immagine, mondo))
    return fuori


def calcola():
    """Esegue il motore sulla sequenza e restituisce (nomi, matrice)."""
    motore = MotoreGeometrico()
    righe, nomi = [], None
    for immagine, mondo in sequenza():
        f = motore.fotogramma(immagine, mondo, W, H, FPS)
        if nomi is None:
            nomi = sorted(f.keys())
        righe.append([float(f[c]) for c in nomi])
    return nomi, np.asarray(righe, dtype=np.float64)


def aggiorna():
    nomi, M = calcola()
    os.makedirs(os.path.dirname(ATTESO), exist_ok=True)
    np.savez_compressed(ATTESO, valori=M,
                        colonne=np.array(nomi, dtype=object))
    print(f'file d\'oro riscritto: {ATTESO}')
    print(f'{M.shape[0]} fotogrammi x {M.shape[1]} grandezze')
    print('Registrare in CHANGELOG PERCHE\' e\' stato rigenerato: se cambia '
          'senza una ragione scritta, i numeri della tesi sono cambiati con lui.')


class ProvaGeometria(unittest.TestCase):

    def test_i_valori_non_sono_cambiati(self):
        if not os.path.exists(ATTESO):
            self.skipTest('manca il file d\'oro: '
                          'python prove/prova_geometria.py --aggiorna')
        atteso = np.load(ATTESO, allow_pickle=True)
        nomi, M = calcola()

        self.assertEqual(list(atteso['colonne']), nomi,
                         'sono cambiati i NOMI delle grandezze, non solo i '
                         'valori: cambia anche il significato delle colonne '
                         'nei CSV gia prodotti')
        self.assertEqual(atteso['valori'].shape, M.shape)
        np.testing.assert_allclose(
            M, atteso['valori'], rtol=1e-9, atol=1e-9, equal_nan=True,
            err_msg='il motore geometrico produce valori diversi da quelli su '
                    'cui la tesi e stata scritta. Se la modifica e voluta: '
                    'python prove/prova_geometria.py --aggiorna, e registrarla.')

    def test_la_finestra_degli_integrali_e_una_durata(self):
        """
        ISS-148: il buffer conserva 1,72 s di storia, non 31 fotogrammi.

        E' la prova che il file d'oro non puo' dare, perche' il file d'oro
        gira a una cadenza sola. Quel che deve restare costante al variare
        della cadenza non e' il numero di campioni --- che infatti cambia ---
        ma il tempo che coprono: a 18 fps ne servono 31, a 7,26 ne bastano 12,
        e in tutti i casi la finestra non supera la durata dichiarata.

        Il conteggio a 18 fps vale 31 ESATTAMENTE, ed e' la ragione per cui
        feature_v3.csv non cambia di un bit: a cadenza costante la
        formulazione a durata e quella a conteggio sono la stessa cosa.
        """
        seq = list(sequenza())
        for fps, atteso in ((18.0, 31), (9.0, 15), (7.26, 12)):
            motore = MotoreGeometrico()
            for immagine, mondo in seq:
                motore.fotogramma(immagine, mondo, W, H, fps)
            for bacino in ('A1', 'A2', 'A3'):
                n = len(motore._buf[bacino])
                self.assertEqual(
                    n, atteso,
                    f'a {fps} fps il bacino {bacino} conserva {n} campioni '
                    f'invece di {atteso}: la finestra non e piu una durata')
                self.assertLessEqual(
                    n / fps, motore.DURATA * (1 + 1e-9),
                    f'a {fps} fps la finestra copre {n / fps:.4f} s, oltre i '
                    f'{motore.DURATA:.4f} s dichiarati')

    def test_la_durata_si_puo_dichiarare_in_secondi(self):
        """Il costruttore accetta i secondi, e il conteggio ne discende."""
        m = MotoreGeometrico(durata_integrali=1.0)
        self.assertAlmostEqual(m.DURATA, 1.0)
        for immagine, mondo in sequenza():
            m.fotogramma(immagine, mondo, W, H, 18.0)
        self.assertEqual(len(m._buf['A3']), 18)
        # e passare il conteggio equivale a passare la durata corrispondente
        self.assertAlmostEqual(MotoreGeometrico(k_integrali=31).DURATA,
                               31 / 18.0)

    def test_senza_posa_non_solleva(self):
        """Un fotogramma senza persona in scena non deve far cadere la catena."""
        motore = MotoreGeometrico()
        f = motore.fotogramma(None, None, W, H, FPS)
        self.assertIsInstance(f, dict)
        self.assertGreater(len(f), 0)

    def test_le_grandezze_sono_finite_quando_la_posa_c_e(self):
        """Nessun NaN o infinito sui fotogrammi con posa, dopo il riscaldamento."""
        nomi, M = calcola()
        coda = M[20:]                      # oltre il buffer degli integrali
        non_finiti = ~np.isfinite(coda)
        if non_finiti.any():
            colonne = {nomi[j] for j in np.where(non_finiti.any(axis=0))[0]}
            self.fail(f'grandezze non finite dopo il riscaldamento: '
                      f'{sorted(colonne)}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--aggiorna', action='store_true',
                    help='riscrive il file d\'oro con i valori correnti')
    a, resto = ap.parse_known_args()
    if a.aggiorna:
        aggiorna()
    else:
        unittest.main(argv=[sys.argv[0]] + resto)
