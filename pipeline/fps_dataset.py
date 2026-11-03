# -*- coding: utf-8 -*-
"""L'fps vero di UP-Fall, dai timestamp nei nomi dei file.

`config.FPS_DATASET = 18.0` e' un valore dichiarato in un commento
(«UP-Fall e' consolidato a ~18 fps»), mai verificato. I nomi dei fotogrammi
sono timestamp al microsecondo, quindi l'intervallo vero si misura senza
aprire una sola immagine.

La domanda a cui serve rispondere: rendere K_INTEGRALI una durata invece di
un conteggio cambierebbe le feature? Cambia solo se l'fps NON e' costante.
"""
import os
import re
import statistics
import sys
from datetime import datetime

RADICE = sys.argv[1]
# alcuni nomi hanno sette cifre decimali: %f ne accetta al massimo sei.
STAMP = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}_\d{2}_\d{2})\.(\d+)')


def istanti(cartella):
    ts = []
    for nome in os.listdir(cartella):
        m = STAMP.match(nome)
        if m:
            frazione = (m.group(2) + '000000')[:6]
            ts.append(datetime.strptime(m.group(1) + '.' + frazione,
                                        '%Y-%m-%dT%H_%M_%S.%f'))
    ts.sort()
    return ts


def main():
    riprese = []
    for cat in ('adl', 'fall'):
        base = os.path.join(RADICE, cat)
        if not os.path.isdir(base):
            continue
        for sog in sorted(os.listdir(base)):
            d1 = os.path.join(base, sog)
            if not os.path.isdir(d1):
                continue
            for rip in sorted(os.listdir(d1)):
                d2 = os.path.join(d1, rip)
                if os.path.isdir(d2):
                    riprese.append((rip, d2))

    fps_per_ripresa, tutti_dt = [], []
    for nome, d in riprese:
        ts = istanti(d)
        if len(ts) < 30:
            continue
        durata = (ts[-1] - ts[0]).total_seconds()
        if durata <= 0:
            continue
        fps = (len(ts) - 1) / durata
        fps_per_ripresa.append((fps, nome, len(ts)))
        dt = [(ts[i + 1] - ts[i]).total_seconds() for i in range(len(ts) - 1)]
        tutti_dt.extend(dt)

    f = sorted(x[0] for x in fps_per_ripresa)
    n = len(f)
    print('riprese misurate: %d   fotogrammi: %d'
          % (n, sum(x[2] for x in fps_per_ripresa)))
    print()
    print('FPS PER RIPRESA')
    print('  minimo   %.2f' % f[0])
    print('  1o quart %.2f' % f[n // 4])
    print('  MEDIANA  %.2f' % f[n // 2])
    print('  3o quart %.2f' % f[3 * n // 4])
    print('  massimo  %.2f' % f[-1])
    print('  media    %.2f   dev.st %.2f' % (statistics.mean(f),
                                             statistics.pstdev(f)))
    print()
    print('  dichiarato in config: 18,00')
    fuori = sum(1 for x in f if abs(x - 18.0) > 0.9)   # oltre il 5%
    print('  riprese che stanno oltre il 5%% da 18,00: %d su %d (%.0f%%)'
          % (fuori, n, 100.0 * fuori / n))
    print()
    d = sorted(tutti_dt)
    m = len(d)
    print('INTERVALLO FRA FOTOGRAMMI (%d misure)' % m)
    print('  mediana %.1f ms   1o quart %.1f   9o dec %.1f   99o %.1f'
          % (1000 * d[m // 2], 1000 * d[m // 4],
             1000 * d[int(0.9 * m)], 1000 * d[int(0.99 * m)]))
    print()
    print('CHE COSA SIGNIFICA PER K = 31 FOTOGRAMMI')
    print('  a %.2f fps (mediana)  -> %.2f s' % (f[n // 2], 31 / f[n // 2]))
    print('  a %.2f fps (minimo)   -> %.2f s' % (f[0], 31 / f[0]))
    print('  a %.2f fps (massimo)  -> %.2f s' % (f[-1], 31 / f[-1]))
    print()
    print('  Se K fosse una DURATA di 1,72 s, il conteggio per ripresa')
    print('  andrebbe da %d a %d fotogrammi invece che 31 fissi.'
          % (round(1.72 * f[0]), round(1.72 * f[-1])))
    diversi = sum(1 for x in f if round(1.72 * x) != 31)
    print('  riprese in cui il conteggio NON sarebbe 31: %d su %d (%.0f%%)'
          % (diversi, n, 100.0 * diversi / n))
    print()
    print('LE DIECI RIPRESE PIU\' LONTANE DA 18,00')
    for fps, nome, k in sorted(fps_per_ripresa,
                               key=lambda x: -abs(x[0] - 18.0))[:10]:
        print('  %-34s %6.2f fps  (%d fotogrammi)' % (nome, fps, k))


if __name__ == '__main__':
    main()
