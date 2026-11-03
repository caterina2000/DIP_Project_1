# -*- coding: utf-8 -*-
"""Quanto cambierebbe correggere ISS-147, misurato sulla sessione registrata.

Due regole di finestratura sulla STESSA traccia per fotogramma, lo stesso
modello, la stessa soglia, la stessa regola di allarme.

  A  come la board fa oggi: ogni fotogramma entra nel buffer, anche quello
     senza posa, che vale zeri su tutte le colonne. La guardia del
     riscaldamento e' un tempo dall'avvio e non viene mai riarmata.

  B  come `src/dati.py` in addestramento: il fotogramma senza posa NON entra,
     il buffer si azzera sul buco, e non si decide finche' non ci sono di
     nuovo K=31 fotogrammi validi consecutivi.

PRIMA di confrontare si esegue la verifica di parita' su `parita.npz`: il
modello e' stato serializzato con scikit-learn 1.7.2 e qui gira 1.6.0, e senza
quel controllo nessuno dei due numeri vale niente.

Limite dichiarato: le grandezze integrali nel CSV sono quelle che il motore ha
calcolato dal vivo, con il proprio reset. B non le ricalcola --- servirebbero i
landmark, che non si salvano. B corregge le due cose correggibili a
posteriori: quali fotogrammi entrano nella finestra, e quando e' lecito
decidere.
"""
import csv
import json
import os
import sys
import warnings
from collections import deque

import joblib
import numpy as np

warnings.filterwarnings('ignore')

R = sys.argv[1]
SESSIONE = os.path.join(R, 'risultati', 'sessioni', '20260906',
                        'notte_20260906_1523',
                        'notte_20260906_1523_feature.csv')


def normalizza(X, blob):
    Z = np.asarray(X, dtype=np.float64).copy()
    m = np.asarray(blob['maschera_log1p'], dtype=bool)
    if m.any():
        c = np.where(m)[0]
        Z[..., c] = np.sign(Z[..., c]) * np.log1p(np.abs(Z[..., c]))
    forma = Z.shape
    return blob['scaler'].transform(Z.reshape(-1, forma[-1])).reshape(forma)


def riassumi(X):
    return np.concatenate([X.mean(1), X.std(1), X.min(1), X.max(1),
                           X[:, 0, :], X[:, -1, :]], axis=1)


def punteggio(finestre, modello, blob, i_pos):
    X = riassumi(normalizza(np.asarray(finestre, np.float64), blob))
    return modello.predict_proba(X)[:, i_pos]


def eventi(tempi, sopra, persistenza, sospensione):
    corsa, ultimo, out = 0, -1e9, []
    for t, s in zip(tempi, sopra):
        corsa = corsa + 1 if s else 0
        if corsa >= persistenza and t - ultimo >= sospensione:
            out.append(t)
            ultimo = t
            corsa = 0
    return out


def main():
    meta = json.load(open(os.path.join(R, 'deploy_board', 'metadata.json'),
                          encoding='utf-8'))
    modello = joblib.load(os.path.join(R, 'deploy_board', 'modello.pkl'))
    blob = joblib.load(os.path.join(R, 'deploy_board', 'scaler.pkl'))
    i_pos = list(modello.classes_).index(1)

    # ---- parita', prima di ogni altra cosa ----------------------------
    # parita.npz contiene finestre GIA' normalizzate: la verifica della board
    # fa riassumi(X) e non riassumi(normalizza(X)). Applicare qui lo scaler
    # una seconda volta da uno scarto di 0,94 invece di 1e-16.
    par = np.load(os.path.join(R, 'deploy_board', 'parita.npz'))
    p = modello.predict_proba(riassumi(np.asarray(par['X'], np.float64)))[:, i_pos]
    scarto = float(np.abs(p - par['p_attesa']).max())
    print('PARITA su %d finestre precalcolate: scarto massimo %.3g  -> %s'
          % (len(p), scarto, 'OK' if scarto < 1e-6 else 'FALLITA'))
    if scarto >= 1e-6:
        print('  i numeri qui sotto non sarebbero confrontabili: mi fermo.')
        return
    print()

    colonne = meta['colonne']
    L, passo, K = (meta['lunghezza_finestra'], meta['passo_finestra'],
                   meta['k_integrali'])
    soglia = meta['soglia']
    reg = meta['regola_decisione']
    P, S = reg['persistenza_finestre'], reg['sospensione_s']

    t_s, posa, righe = [], [], []
    with open(SESSIONE, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            t_s.append(float(r['t_s']))
            posa.append(int(r['ha_posa']))
            righe.append([float(r[c]) for c in colonne])
    n = len(righe)
    ore = (t_s[-1] - t_s[0]) / 3600.0
    print('sessione   %d fotogrammi, %.2f ore, %.1f%% pose valide'
          % (n, ore, 100.0 * sum(posa) / n))

    esiti = {}
    for nome in ('A', 'B'):
        buf, corsa = deque(maxlen=L), 0
        tempi, finestre = [], []
        for i in range(n):
            if nome == 'A':
                buf.append(righe[i])
                pronto = len(buf) == L and t_s[i] >= meta['riscaldamento_s']
            else:
                if not posa[i]:
                    buf.clear()
                    corsa = 0
                    continue
                buf.append(righe[i])
                corsa += 1
                pronto = len(buf) == L and corsa >= K
            if not pronto or (i + 1) % passo:
                continue
            tempi.append(t_s[i])
            finestre.append(list(buf))

        pr = (punteggio(finestre, modello, blob, i_pos)
              if finestre else np.zeros(0))
        sopra = pr >= soglia
        ev = eventi(tempi, sopra, P, S)
        esiti[nome] = (len(pr), int(sopra.sum()), len(ev))
        print()
        print('REGOLA %s' % nome)
        print('  decisioni               %6d' % len(pr))
        print('  finestre sopra soglia   %6d   (%.1f/ora)'
              % (sopra.sum(), sopra.sum() / ore))
        print('  ALLARMI                 %6d   (%.2f/ora)'
              % (len(ev), len(ev) / ore))
        if len(pr):
            print('  punteggio  mediana %.4f   90mo %.4f   max %.4f'
                  % (float(np.median(pr)), float(np.percentile(pr, 90)),
                     float(pr.max())))

    print()
    print('La board quella sera dichiarava 168 finestre sopra soglia e 14 allarmi.')
    a, b = esiti['A'], esiti['B']
    print('A ricostruita: %d finestre, %d allarmi' % (a[1], a[2]))
    print('B corretta:    %d finestre, %d allarmi' % (b[1], b[2]))


if __name__ == '__main__':
    main()
