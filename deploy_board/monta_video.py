# -*- coding: utf-8 -*-
"""
Monta un video mp4 a partire dai fotogrammi annotati di una sessione.

Le sessioni in deploy_board/sessioni/*/clip/ sono gia' fotogrammi annotati
(scheletro, punteggio, soglia, raffica), salvati non a cadenza fissa: il nome
file e' il secondo di sessione, es. f00742.3.jpg = 742,3 s dall'avvio. Per
questo il montaggio non puo' usare un -framerate fisso di ffmpeg sul pattern
dei nomi: si costruisce una lista di concatenazione con la durata vera di
ciascun fotogramma (la distanza dal successivo), cosi' il video rispetta il
tempo reale della sessione anche se la cadenza di cattura non era costante.

Uso:
    python deploy_board/monta_video.py sessioni/20260909_v5/clip \
        --da 740 --a 752 --out evento_1.mp4

    python deploy_board/monta_video.py sessioni/20260909_v5/clip \
        --da 740 --a 752 --velocita 1.5 --out evento_1_veloce.mp4
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile

NOME_RE = re.compile(r'f(\d+\.\d+)\.jpg$')


def elenca_fotogrammi(cartella: str, da: float, a: float):
    """
    Fotogrammi in [da, a], ordinati per il secondo nel nome file.

    I percorsi sono resi assoluti perche' il demuxer concat di ffmpeg
    risolve i percorsi relativi del file di lista rispetto alla cartella
    del file di lista stesso (in TEMP), non rispetto alla cartella di
    lavoro di questo script.
    """
    cartella_assoluta = os.path.abspath(cartella)
    trovati = []
    for nome in os.listdir(cartella_assoluta):
        m = NOME_RE.search(nome)
        if not m:
            continue
        t = float(m.group(1))
        if da <= t <= a:
            trovati.append((t, os.path.join(cartella_assoluta, nome)))
    trovati.sort(key=lambda x: x[0])
    return trovati


def scrivi_lista_concat(fotogrammi, percorso_lista: str, velocita: float,
                         durata_ultimo: float = 0.4):
    """
    File di concatenazione per `ffmpeg -f concat`: un fotogramma per riga,
    con la sua durata reale (al netto della velocita' di riproduzione).
    """
    def normalizza(path):
        # Barre in avanti: su Windows il backslash e' anche carattere di
        # escape nel formato concat di ffmpeg.
        return path.replace('\\', '/').replace("'", "'\\''")

    with open(percorso_lista, 'w', encoding='utf-8') as f:
        for i, (t, path) in enumerate(fotogrammi):
            f.write(f"file '{normalizza(path)}'\n")
            if i + 1 < len(fotogrammi):
                durata = (fotogrammi[i + 1][0] - t) / velocita
            else:
                durata = durata_ultimo / velocita
            f.write(f"duration {max(durata, 0.02):.3f}\n")
        # ffmpeg richiede l'ultimo file ripetuto senza `duration` per non
        # troncare l'ultimo fotogramma.
        if fotogrammi:
            f.write(f"file '{normalizza(fotogrammi[-1][1])}'\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cartella', help="cartella clip/ della sessione")
    ap.add_argument('--da', type=float, required=True, help="inizio, in secondi di sessione")
    ap.add_argument('--a', type=float, required=True, help="fine, in secondi di sessione")
    ap.add_argument('--velocita', type=float, default=1.0,
                     help="moltiplicatore di velocita' (2.0 = il doppio piu' veloce)")
    ap.add_argument('--out', default='evento.mp4')
    args = ap.parse_args()

    fotogrammi = elenca_fotogrammi(args.cartella, args.da, args.a)
    if not fotogrammi:
        print(f"Nessun fotogramma trovato in [{args.da}, {args.a}] dentro {args.cartella}",
              file=sys.stderr)
        sys.exit(1)

    print(f"{len(fotogrammi)} fotogrammi, da {fotogrammi[0][0]:.1f}s a {fotogrammi[-1][0]:.1f}s "
          f"({fotogrammi[-1][0] - fotogrammi[0][0]:.1f}s di sessione, "
          f"{(fotogrammi[-1][0] - fotogrammi[0][0]) / args.velocita:.1f}s di video)")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
        lista = tmp.name
    scrivi_lista_concat(fotogrammi, lista, args.velocita)

    cmd = [
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', lista,
        '-fps_mode', 'vfr', '-pix_fmt', 'yuv420p', '-c:v', 'libx264',
        '-crf', '18', args.out,
    ]
    try:
        subprocess.run(cmd, check=True)
    finally:
        os.remove(lista)

    print(f"Scritto {args.out}")


if __name__ == '__main__':
    main()
