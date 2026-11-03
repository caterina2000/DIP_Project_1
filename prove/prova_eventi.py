"""
Prova sull'aggregazione delle finestre in eventi.

E' l'errore piu' costoso gia' commesso in questo lavoro. Una caduta produce una
raffica di finestre consecutive sopra soglia --- su una sessione ne ha prodotte
centoventinove --- e contarle come allarmi distinti sovrastima di due ordini di
grandezza: il fattore misurato fra le due grandezze e' **47,8**.

La regola e' quella del sistema installato: servono `persistenza` finestre
consecutive sopra soglia, e dopo un allarme il sistema tace per `sospensione`
secondi. Questa prova verifica che una raffica nota produca esattamente il
numero di allarmi che ci si aspetta.

    python prove/prova_eventi.py
"""

import os
import sys
import unittest

import numpy as np

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (RADICE, os.path.join(RADICE, 'pipeline')):
    if p not in sys.path:
        sys.path.insert(0, p)

from pipeline.eventi_sessioni import eventi                # noqa: E402


def sopra_da(bit):
    """'00111' -> array di booleani, una finestra per carattere."""
    return np.array([c == '1' for c in bit], dtype=bool)


def tempi(n, passo=0.25):
    """Istanti regolari, come li produce la board: una finestra ogni 0,25 s."""
    return np.arange(n, dtype=float) * passo


class ProvaEventi(unittest.TestCase):

    PERSISTENZA = 5
    SOSPENSIONE = 30.0

    def eventi_di(self, bit, passo=0.25, persistenza=None, sospensione=None):
        s = sopra_da(bit)
        return eventi(s, tempi(len(s), passo),
                      self.PERSISTENZA if persistenza is None else persistenza,
                      self.SOSPENSIONE if sospensione is None else sospensione)

    def test_una_raffica_lunga_e_un_allarme_solo(self):
        """E' il caso del fattore 47,8: cento finestre consecutive sopra
        soglia sono UN evento, non cento."""
        self.assertEqual(len(self.eventi_di('0' * 5 + '1' * 100 + '0' * 5)), 1)

    def test_niente_sopra_soglia_niente_allarmi(self):
        self.assertEqual(self.eventi_di('0' * 50), [])

    def test_sotto_la_persistenza_non_scatta(self):
        """Quattro finestre consecutive con persistenza cinque: niente.
        E' l'antirimbalzo, ed e' cio' che tiene bassi i falsi allarmi."""
        self.assertEqual(self.eventi_di('0011110000'), [])

    def test_esattamente_la_persistenza_scatta(self):
        ev = self.eventi_di('00' + '1' * 5 + '000')
        self.assertEqual(len(ev), 1)
        self.assertEqual(ev[0], 6, 'l allarme deve scattare sulla QUINTA '
                                   'finestra consecutiva, non sulla prima')

    def test_la_corsa_si_azzera_su_una_finestra_sotto(self):
        """Tre sopra, una sotto, tre sopra non fanno sei consecutive."""
        self.assertEqual(self.eventi_di('1110111000'), [])

    def test_due_raffiche_dentro_la_sospensione_sono_un_allarme(self):
        """A 0,25 s per finestra, due raffiche a pochi secondi di distanza
        cadono dentro i trenta secondi di silenzio: un allarme solo."""
        self.assertEqual(len(self.eventi_di('1' * 10 + '0' * 10 + '1' * 10)), 1)

    def test_due_raffiche_oltre_la_sospensione_sono_due_allarmi(self):
        """Con finestre distanti dieci secondi, le due raffiche superano i
        trenta secondi di silenzio e diventano due eventi."""
        ev = self.eventi_di('1' * 6 + '0' * 2 + '1' * 6, passo=10.0)
        self.assertEqual(len(ev), 2)

    def test_la_sospensione_si_misura_dall_allarme_non_dalla_raffica(self):
        """Il silenzio parte dall'istante in cui l'allarme e' stato emesso.
        Se partisse dall'inizio della raffica, una raffica lunga quanto la
        sospensione produrrebbe un secondo allarme mentre e' ancora in corso."""
        ev = self.eventi_di('1' * 40, passo=1.0, sospensione=30.0)
        self.assertEqual(len(ev), 2)
        self.assertEqual(ev[0], 4)
        self.assertGreaterEqual(ev[1] - ev[0], 30)

    def test_persistenza_uno_ogni_finestra_isolata_e_un_allarme(self):
        """Caso degenere, ma va tenuto: con persistenza 1 e sospensione 0 il
        conteggio degli eventi coincide con quello delle finestre. E' la
        configurazione in cui il fattore 47,8 vale 1, ed e' il modo di
        verificare che le due grandezze siano davvero la stessa regola."""
        ev = self.eventi_di('10101', persistenza=1, sospensione=0.0)
        self.assertEqual(ev, [0, 2, 4])

    def test_gli_indici_puntano_alla_finestra_giusta(self):
        """Gli indici restituiti servono a ritrovare l'istante dell'allarme
        nel registro: se sono spostati, lo e' anche la latenza misurata."""
        bit = '0' * 7 + '1' * 5 + '0' * 3
        ev = self.eventi_di(bit)
        self.assertEqual(len(ev), 1)
        self.assertTrue(sopra_da(bit)[ev[0]],
                        'l indice dell allarme cade su una finestra che non '
                        'era sopra soglia')


if __name__ == '__main__':
    unittest.main()
