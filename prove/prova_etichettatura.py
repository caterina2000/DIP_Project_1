"""
Prova sulla regola che decide che cosa sia un positivo.

`etichetta_finestra` trasforma le etichette per fotogramma nell'etichetta della
finestra, con il criterio K-su-M: servono almeno K fotogrammi della classe
dentro un blocco di M consecutivi. E' la funzione che stabilisce quali finestre
entrano nell'addestramento e con quale segno, quindi decide il valore di ogni
metrica del lavoro.

I casi che contano sono ai bordi --- esattamente K, K meno uno, blocco piu'
lungo della finestra --- ed e' esattamente dove una modifica innocua sposta il
confine senza sollevare eccezioni.

    python prove/prova_etichettatura.py
"""

import os
import sys
import unittest

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RADICE not in sys.path:
    sys.path.insert(0, RADICE)

import config                                              # noqa: E402
from src.etichettatura import MODI, etichetta_finestra, _blocco_k_su_m  # noqa: E402

import numpy as np                                         # noqa: E402


def maschera(bit):
    """'00111' -> array di booleani. Rende i casi leggibili nel test."""
    return np.array([c == '1' for c in bit], dtype=bool)


class ProvaBloccoKsuM(unittest.TestCase):
    """Il criterio di conteggio, isolato dalla logica delle tre classi."""

    def test_k_esatti_consecutivi_bastano(self):
        self.assertTrue(_blocco_k_su_m(maschera('0011100'), k=3, m=3))

    def test_uno_in_meno_non_basta(self):
        self.assertFalse(_blocco_k_su_m(maschera('0011000'), k=3, m=3))

    def test_tollera_un_buco_dentro_il_blocco(self):
        """E' la ragione per cui M e' piu' grande di K: un fotogramma
        annotato male non deve spezzare l'evento."""
        self.assertTrue(_blocco_k_su_m(maschera('0110100'), k=3, m=4))

    def test_sparpagliati_oltre_il_blocco_non_contano(self):
        """Tre fotogrammi lontani fra loro non sono una dinamica continua.
        E' il difetto della regola precedente, che li contava ovunque fossero."""
        self.assertFalse(_blocco_k_su_m(maschera('1000100010'), k=3, m=4))

    def test_finestra_piu_corta_di_k(self):
        self.assertFalse(_blocco_k_su_m(maschera('11'), k=3, m=8))

    def test_blocco_piu_lungo_della_finestra_degrada_al_conteggio_totale(self):
        """Con M oltre la lunghezza, il criterio deve diventare il conteggio
        sull'intera finestra, non fallire."""
        self.assertTrue(_blocco_k_su_m(maschera('10101'), k=3, m=99))
        self.assertFalse(_blocco_k_su_m(maschera('10001'), k=3, m=99))

    def test_k_zero_e_sempre_vero(self):
        self.assertTrue(_blocco_k_su_m(maschera('000'), k=0, m=3))

    def test_vuota(self):
        self.assertFalse(_blocco_k_su_m(maschera(''), k=1, m=3))


class ProvaEtichettaFinestra(unittest.TestCase):

    def test_finestra_vuota_da_none(self):
        for modo in MODI:
            self.assertIsNone(etichetta_finestra([], modo=modo))

    def test_tutta_quotidiana_da_zero(self):
        e = [0] * 22
        for modo in MODI:
            self.assertEqual(etichetta_finestra(e, modo=modo), 0)

    def test_la_fase_due_ha_la_precedenza_sulla_uno(self):
        """Una finestra che contiene entrambe descrive il momento in cui la
        caduta si e' appena conclusa: lo stato finale e' l'informazione piu'
        recente. Se questa precedenza si inverte, cambiano di segno migliaia
        di finestre senza che nulla lo segnali."""
        e = [1] * 6 + [2] * 12 + [0] * 4
        self.assertEqual(etichetta_finestra(e, modo='tre_classi'), 2)
        self.assertIsNone(etichetta_finestra(e, modo='scarta'))
        self.assertEqual(etichetta_finestra(e, modo='caduta'), 1)

    def test_solo_caduta(self):
        e = [0] * 8 + [1] * 6 + [0] * 8
        self.assertEqual(etichetta_finestra(e, modo='tre_classi'), 1)
        self.assertEqual(etichetta_finestra(e, modo='scarta'), 1)
        self.assertEqual(etichetta_finestra(e, modo='caduta'), 1)

    def test_solo_terra(self):
        e = [0] * 6 + [2] * 12 + [0] * 4
        self.assertEqual(etichetta_finestra(e, modo='tre_classi'), 2)
        self.assertIsNone(etichetta_finestra(e, modo='scarta'))
        self.assertEqual(etichetta_finestra(e, modo='caduta'), 1)

    def test_il_confine_di_k_caduta(self):
        """Con K_CADUTA fotogrammi la finestra e' positiva, con uno in meno no.
        E' il confine che decide quante finestre positive esistono."""
        k, m = config.K_CADUTA, config.M_BLOCCO
        self.assertEqual(
            etichetta_finestra([0] * 5 + [1] * k + [0] * 5, modo='tre_classi'), 1)
        self.assertEqual(
            etichetta_finestra([0] * 5 + [1] * (k - 1) + [0] * 5,
                               modo='tre_classi'), 0)
        self.assertLessEqual(k, m, 'K non puo essere maggiore di M: '
                                   'il criterio sarebbe insoddisfacibile')

    def test_il_confine_di_k_terra(self):
        k = config.K_TERRA
        self.assertEqual(
            etichetta_finestra([0] * 3 + [2] * k + [0] * 3, modo='tre_classi'), 2)
        self.assertEqual(
            etichetta_finestra([0] * 3 + [2] * (k - 1) + [0] * 3,
                               modo='tre_classi'), 0)

    def test_i_parametri_espliciti_hanno_la_meglio_su_config(self):
        """Chi passa un valore deve ottenere quel valore. E' la garanzia che
        rende possibile l'analisi di sensibilita sulle soglie."""
        e = [0] * 5 + [1] * 2 + [0] * 5
        self.assertEqual(etichetta_finestra(e, modo='tre_classi',
                                            k_caduta=2, m_blocco=2), 1)
        self.assertEqual(etichetta_finestra(e, modo='tre_classi',
                                            k_caduta=9, m_blocco=9), 0)

    def test_i_default_vengono_da_config(self):
        """Nessun default scritto dentro il modulo: era ISS-112, e produceva
        run i cui metadati dichiaravano parametri diversi da quelli usati."""
        e = [0] * 5 + [1] * config.K_CADUTA + [0] * 5
        self.assertEqual(
            etichetta_finestra(e, modo='tre_classi'),
            etichetta_finestra(e, modo='tre_classi',
                               **config.SOGLIE_ETICHETTATURA))

    def test_modo_sconosciuto_solleva(self):
        with self.assertRaises(ValueError):
            etichetta_finestra([0, 1, 2], modo='qualunque')


if __name__ == '__main__':
    unittest.main()
