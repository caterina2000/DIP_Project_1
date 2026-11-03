"""
Esegue tutte le prove.

    python prove/esegui.py

Nessuna dipendenza oltre numpy e pandas: le prove usano `unittest` della
libreria standard, quindi girano in tutti e tre gli ambienti conda del
progetto senza installare nulla.

Che cosa coprono, e che cosa no
-------------------------------
Coprono i tre punti in cui un errore non produce un'eccezione ma un numero
sbagliato:

    prova_geometria      le trentadue grandezze da cui viene ogni numero
    prova_etichettatura  la regola che decide che cosa sia un positivo
    prova_eventi         la differenza fra finestre sopra soglia ed eventi

Non coprono l'addestramento, il trasferimento all'archivio esterno, ne' la
catena sulla board: quelli si verificano eseguendoli, e il loro esito sta in
EXPERIMENTS.md. Queste sono le tre cose che devono restare vere fra una run e
l'altra senza che nessuno le riesegua.
"""

import os
import sys
import unittest

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
if RADICE not in sys.path:
    sys.path.insert(0, RADICE)


def main():
    caricatore = unittest.TestLoader()
    suite = caricatore.discover(start_dir=QUI, pattern='prova_*.py',
                                top_level_dir=RADICE)
    esito = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if esito.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
