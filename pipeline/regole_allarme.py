"""
La regola di allarme si puo' scegliere meglio: quattro famiglie a confronto.

Perche' esiste
--------------
La regola installata chiede **cinque finestre consecutive** sopra soglia. Il
numero cinque non e' mai stato giustificato ([ISS-145](../docs/ISSUES.md)), ed
[EXP-028](../docs/EXPERIMENTS.md) ne ha misurato il prezzo: un secondo di
latenza e dieci punti di richiamo rispetto a una finestra sola.

Ma il difetto piu' serio non e' il valore di k: e' la parola CONSECUTIVE. Il
Capitolo 5 lo documenta senza trarne la conseguenza:

    «Le altre tre cadute non producono allarme a persistenza cinque, con corse
    massime di due, zero e tre finestre.»

Su tre cadute vere il punteggio era sopra soglia, ma con dei buchi: la corsa si
azzerava e ripartiva, e l'allarme non scattava mai. Una regola che chiede
consecutivita' butta via l'evidenza gia' accumulata ogni volta che un
fotogramma va storto -- ed e' proprio nelle cadute difficili che i fotogrammi
vanno storti, perche' la persona esce dal campo o si copre.

Le quattro famiglie
-------------------
Tutte leggono gli STESSI punteggi: nessun modello viene riaddestrato, cambia
solo come si decide a partire da essi.

    consecutive k       k finestre di fila sopra soglia   <- quella installata
    m su n              m finestre sopra soglia fra le ultime n, anche non
                        contigue: tollera un buco senza perdere la memoria
    cumulata c          si accumula (punteggio - soglia), il negativo scarica
                        l'accumulo ma non lo azzera; allarme quando supera c.
                        E' una regola CUSUM: pesa QUANTO si e' sopra, non solo
                        quante volte
    isteresi a/b/k      si entra in allarme a una soglia ALTA e si resta con
                        una BASSA: e' come si trattano i sensori rumorosi

Le due misure, e perche' servono entrambe
-----------------------------------------
Una regola si giudica su due assi che tirano in direzioni opposte:

    LABORATORIO  quante delle cinquanta cadute annotate fa scattare, e dopo
                 quanto tempo  (etichetta per fotogramma: la latenza si misura)
    CASA         quanti allarmi produce all'ora nelle nove sessioni domestiche
                 (nessuna caduta: sono tutti falsi)

Una regola migliore e' una che, a parita' di allarmi all'ora in casa, prende
piu' cadute o le prende prima. Il confronto e' quindi su una FRONTIERA, non su
un numero solo.

Uso:
    python pipeline/regole_allarme.py
    python pipeline/regole_allarme.py --run foresta_tre_classi_DTW_cam1_L22
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

import config
from src.provenienza import scrivi_json
from pipeline.latenza_laboratorio import (finestre_con_fotogramma,
                                          inizio_caduta, punteggi_per_soggetto)
from pipeline.eventi_sessioni import elenco_punteggi, SESSIONI

dec = lambda v, n=2: f'{v:.{n}f}'.replace('.', ',')


# ============================================================
#  LE REGOLE
#  Ognuna riceve i punteggi in ordine temporale e restituisce gli indici in
#  cui scatta un allarme. Nessuna guarda il futuro: si puo' eseguire in
#  tempo reale sul dispositivo cosi' com'e' scritta.
# ============================================================

def consecutive(p, soglia, k):
    """k finestre di fila sopra soglia. La regola installata."""
    fuori, corsa = [], 0
    for i, v in enumerate(p):
        corsa = corsa + 1 if v >= soglia else 0
        if corsa >= k:
            fuori.append(i)
            corsa = 0
    return fuori


def m_su_n(p, soglia, m, n):
    """
    m finestre sopra soglia fra le ultime n, anche non contigue.

    Costa una finestra scorrevole di n booleani, cioe' nulla. Tollera un buco
    isolato senza dimenticare quello che ha gia' visto, che e' esattamente il
    caso in cui la regola consecutiva fallisce.
    """
    fuori, coda = [], []
    for i, v in enumerate(p):
        coda.append(v >= soglia)
        if len(coda) > n:
            coda.pop(0)
        if sum(coda) >= m:
            fuori.append(i)
            coda = []
    return fuori


def cumulata(p, soglia, c):
    """
    Accumula lo scarto dalla soglia; il negativo scarica ma non azzera.

    A differenza delle prime due, questa pesa QUANTO il punteggio sta sopra:
    tre finestre a 0,95 valgono piu' di tre finestre a 0,51. E' la regola con
    cui si sorvegliano i processi industriali (CUSUM), e la sua unica
    costante e' la soglia di accumulo.
    """
    fuori, s = [], 0.0
    for i, v in enumerate(p):
        s = max(0.0, s + (v - soglia))
        if s >= c:
            fuori.append(i)
            s = 0.0
    return fuori


def isteresi(p, alta, bassa, k):
    """
    Si entra con la soglia alta, si resta con quella bassa.

    Chiede un indizio FORTE per cominciare a contare, e poi si accontenta di
    un indizio debole per continuare: e' il trattamento classico di un segnale
    rumoroso attorno a una soglia.
    """
    fuori, corsa, dentro = [], 0, False
    for i, v in enumerate(p):
        if not dentro:
            if v >= alta:
                dentro, corsa = True, 1
        else:
            if v >= bassa:
                corsa += 1
            else:
                dentro, corsa = False, 0
        if dentro and corsa >= k:
            fuori.append(i)
            dentro, corsa = False, 0
    return fuori


def famiglie(soglia):
    """(nome, funzione) per ogni regola messa a confronto."""
    r = [(f'consecutive {k}', lambda p, k=k: consecutive(p, soglia, k))
         for k in (1, 3, 5, 7, 10)]
    r += [(f'{m} su {n}', lambda p, m=m, n=n: m_su_n(p, soglia, m, n))
          for m, n in ((3, 5), (3, 6), (4, 6), (4, 8), (5, 8), (5, 10), (6, 10))]
    r += [(f'cumulata {dec(c, 1)}', lambda p, c=c: cumulata(p, soglia, c))
          for c in (0.5, 1.0, 1.5, 2.0, 2.5)]
    r += [(f'isteresi {dec(a, 2)}/{dec(b, 2)}/{k}',
           lambda p, a=a, b=b, k=k: isteresi(p, a, b, k))
          for a, b, k in ((0.7, 0.4, 3), (0.7, 0.4, 5), (0.8, 0.45, 3),
                          (0.9, 0.5, 3))]
    return r


# ============================================================
#  LE DUE MISURE
# ============================================================

def in_laboratorio(fin, inizio, fps, regola):
    """Richiamo e latenza sulle riprese di caduta annotate."""
    lat, senza = [], 0
    for r, t0 in inizio.items():
        g = fin[fin.ripresa == r]
        if g.empty:
            continue
        idx = regola(g.punteggio.to_numpy())
        if not idx:
            senza += 1
            continue
        lat.append((g.f_fine.to_numpy()[idx[0]] - t0) / fps)
    n = len(lat) + senza
    lat = np.array(lat, float)
    return {'riprese': n, 'con_allarme': len(lat),
            'richiamo': len(lat) / n if n else 0.0,
            'latenza_mediana_s': float(np.median(lat)) if len(lat) else None,
            'latenza_p90_s': float(np.percentile(lat, 90)) if len(lat) else None}


def in_casa(sessioni, regola, sospensione=30.0, min_ore=0.15):
    """Allarmi all'ora sulle sessioni domestiche, con la sospensione."""
    ore_tot, ev_tot = 0.0, 0
    for f in sessioni:
        d = pd.read_csv(f)
        if len(d) < 2 or 'punteggio' not in d.columns:
            continue
        t = d['t_unix' if 't_unix' in d.columns else 't_s'].to_numpy(float)
        ore = (t.max() - t.min()) / 3600.0
        if ore < min_ore:
            continue
        idx = regola(d['punteggio'].to_numpy(float))
        # la sospensione si applica DOPO la regola: due allarmi entro trenta
        # secondi sono lo stesso fatto, qualunque regola li abbia prodotti
        ultimo, n = -1e18, 0
        for i in idx:
            if t[i] - ultimo >= sospensione:
                n += 1
                ultimo = t[i]
        ore_tot += ore
        ev_tot += n
    return {'ore': ore_tot, 'eventi': ev_tot,
            'eventi_ora': ev_tot / ore_tot if ore_tot else 0.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='feature_v3.csv')
    ap.add_argument('--run', default='foresta_tre_classi_DTWH_cam1_L22')
    ap.add_argument('--camera', type=int, default=1)
    ap.add_argument('--soglia', type=float, default=0.5)
    ap.add_argument('--sospensione', type=float, default=30.0)
    ap.add_argument('--punteggi', default=None,
                    help='cartella dei punteggi per fold. Predefinita: '
                         'risultati/addestramento/. Serve per rileggere le run '
                         'archiviate, per esempio risultati/addestramento/v2/, '
                         'senza doverle spostare. Il controllo di allineamento '
                         'piu sotto rifiuta la combinazione sbagliata di CSV e '
                         'punteggi invece di produrre numeri privi di senso.')
    a = ap.parse_args()

    from src.dati import carica
    fps = config.FPS_DATASET
    df = carica(a.csv, camera=a.camera)
    fin = finestre_con_fotogramma(df)
    dove = a.punteggi or os.path.join(config.RISULTATI_DIR, 'addestramento')
    p = punteggi_per_soggetto(os.path.join(dove, f'punteggi_{a.run}.npz'))
    inizio = inizio_caduta(df)

    for s, punteggi in p.items():
        n = int((fin.soggetto == s).sum())
        if n != len(punteggi):
            sys.exit(f'disallineamento su {s}: {n} contro {len(punteggi)}')
    fin = fin.copy()
    fin['punteggio'] = np.nan
    for s, punteggi in p.items():
        fin.loc[fin.soggetto == s, 'punteggio'] = punteggi
    fin = fin.dropna(subset=['punteggio']).sort_values(['ripresa', 'f_fine'])

    sessioni = elenco_punteggi(SESSIONI)

    print('=' * 96)
    print(f'REGOLE DI ALLARME A CONFRONTO — {a.run}, soglia {dec(a.soglia)}')
    print(f'laboratorio: {len(inizio)} cadute annotate · '
          f'casa: {len(sessioni)} sessioni, sospensione {dec(a.sospensione, 0)} s')
    print('=' * 96)
    print(f"{'regola':<22}{'cadute prese':>14}{'richiamo':>10}"
          f"{'latenza med.':>14}{'p90':>8}{'allarmi/ora in casa':>22}")
    print('-' * 96)

    esito = []
    for nome, regola in famiglie(a.soglia):
        lab = in_laboratorio(fin, inizio, fps, regola)
        casa = in_casa(sessioni, regola, a.sospensione)
        esito.append({'regola': nome, **lab, 'casa': casa})
        print(f"{nome:<22}{lab['con_allarme']:>7} su {lab['riprese']:<4}"
              f"{dec(lab['richiamo']):>10}"
              f"{(dec(lab['latenza_mediana_s']) + ' s') if lab['latenza_mediana_s'] is not None else '—':>14}"
              f"{dec(lab['latenza_p90_s'], 1) if lab['latenza_p90_s'] is not None else '—':>8}"
              f"{dec(casa['eventi_ora'], 1):>22}")

    # la frontiera: chi fa meglio della regola installata su ENTRAMBI gli assi
    rif = next(e for e in esito if e['regola'] == 'consecutive 5')
    meglio = [e for e in esito
              if e['richiamo'] >= rif['richiamo']
              and e['casa']['eventi_ora'] <= rif['casa']['eventi_ora']
              and e['regola'] != rif['regola']]
    print('-' * 96)
    print(f"riferimento: {rif['regola']} -> richiamo {dec(rif['richiamo'])}, "
          f"{dec(rif['casa']['eventi_ora'], 1)} allarmi/ora")
    if meglio:
        print('regole che la battono su ENTRAMBI gli assi:')
        for e in meglio:
            print(f"   {e['regola']:<20} richiamo {dec(e['richiamo'])} "
                  f"(+{dec(e['richiamo'] - rif['richiamo'])})  "
                  f"{dec(e['casa']['eventi_ora'], 1)} allarmi/ora "
                  f"({dec(e['casa']['eventi_ora'] - rif['casa']['eventi_ora'], 1)})  "
                  f"latenza {dec(e['latenza_mediana_s'])} s")
    else:
        print('nessuna regola batte quella installata su entrambi gli assi.')

    dst = os.path.join(config.RISULTATI_DIR, 'laboratorio',
                       f'regole_allarme_{a.run}.json')
    scrivi_json(dst, {
        'run': a.run, 'csv': a.csv, 'camera': a.camera, 'soglia': a.soglia,
        'sospensione_s': a.sospensione,
        'n_cadute_laboratorio': len(inizio),
        'n_sessioni_casa': len(sessioni),
        'riferimento': rif['regola'],
        'regole': esito,
    })
    print(f'\nscritto: {os.path.relpath(dst, RADICE)}')


if __name__ == '__main__':
    main()
