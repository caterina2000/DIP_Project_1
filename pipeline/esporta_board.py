"""
Prepara il pacchetto da copiare sulla board.

Cosa esporta
------------
    modello.pkl        foresta addestrata su TUTTI i soggetti
    scaler.pkl         parametri di normalizzazione, colonne e maschera log1p
    geometry.py        IL MOTORE, copiato da src/ e non tenuto allineato a mano
    metadata.json      configurazione completa, schema delle grandezze incluso
    parita.npz         200 finestre con le predizioni calcolate sul PC

Perche' il motore sta nel pacchetto
-----------------------------------
Perche' il modo in cui questo lavoro ha sbagliato due volte e' lo stesso:
due copie della stessa cosa che dovevano essere d'accordo e non lo erano,
senza che nulla sollevasse un errore. `deploy_board/geometry.py` era una
copia tenuta allineata a mano, e il 6 settembre ha smesso di esserlo ---
`A3_h_pavimento` aggiunta di qua e non di la' (ISS-139). Una copia generata
non puo' divergere: o e' quella, o non e' stata esportata.

Insieme al motore va lo SCHEMA: l'elenco ordinato delle grandezze che quel
motore calcola. L'impronta sha256 dice SE due file differiscono, lo schema
dice IN CHE COSA --- e il messaggio «manca A3_h_pavimento» si legge, mentre
due impronte diverse no.

Perche' su tutti i soggetti
---------------------------
I modelli per fold della validazione incrociata servono a STIMARE la
prestazione, non a essere installati: ciascuno ha visto otto soggetti su dieci.
Il modello che si installa li vede tutti. E' la correzione di una discrepanza
gia' osservata nel progetto precedente, dove il recall fuori linea (2/5) era
piu' basso di quello di campo (4/5) sugli stessi eventi proprio perche' fuori
linea si mediavano modelli addestrati su meno dati.

La prova di parita'
-------------------
`parita.npz` contiene finestre gia' normalizzate e le probabilita' che il PC
produce su di esse. Il primo comando da eseguire sulla board le riconfronta: se
divergono oltre 1e-6, le versioni di scikit-learn non sono compatibili e
qualunque misura successiva non e' valida. E' un controllo di trenta secondi
che evita di scoprire il problema dopo dodici ore di registrazione.

Il compito
----------
Il positivo e' l'EVENTO, cioe' la transizione (`fall` nella tassonomia
OmniFall), non lo stato a terra. E' la conclusione del lavoro: sul compito
evento i falsi allarmi sulle persone distese volontariamente sono lo 0,0%,
contro il 12,5% del compito stato.

Uso:
    python pipeline/esporta_board.py
    python pipeline/esporta_board.py --feature A3 --compito allarme
"""

import argparse
import json
import os
import platform
import shutil
import sys
from datetime import datetime

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
from src.dati import (ASIMMETRICHE, COL_FOTOGRAMMA, COL_POSA, COL_RIPRESA,
                      COL_SOGGETTO, FEATURE, Scaler, carica, colonne_di,
                      feature_dtw)
from src.geometry import NOMI
from src.modelli import Foresta

dec = lambda v, n=3: f'{v:.{n}f}'.replace('.', ',')

COMPITI = {'evento': (1,), 'stato': (2,), 'allarme': (1, 2)}


def finestre(df, colonne, positive, k_min=5):
    L, passo, step = (config.LUNGHEZZA_FINESTRA, config.PASSO_FINESTRA,
                      config.FRAME_STEP)
    X, y = [], []
    for _, g in df.groupby([COL_SOGGETTO, COL_RIPRESA], sort=True):
        g = g.sort_values(COL_FOTOGRAMMA)
        if COL_POSA in g.columns:
            g = g[g[COL_POSA] == 1]
        if step > 1:
            g = g.iloc[::step]
        if len(g) < L:
            continue
        v = g[list(colonne)].to_numpy(np.float32)
        cls = g['classe_omnifall'].to_numpy()
        for i in range(0, len(g) - L + 1, passo):
            X.append(v[i:i + L])
            y.append(int(np.isin(cls[i:i + L], positive).sum() >= k_min))
    return np.stack(X), np.array(y, int)


def _impronta(percorso):
    """
    sha256 di un file, in esadecimale.

    Serve per l'impronta di `geometry.py`: la board ne tiene una copia, e le
    due sono allineate a mano. Scrivendo l'impronta nei metadati, `rileva.py`
    si rifiuta di partire se non coincidono -- che e' l'unico modo per
    accorgersene, perche' due motori geometrici diversi non sollevano alcun
    errore, producono solo numeri diversi.
    """
    import hashlib
    h = hashlib.sha256()
    with open(percorso, 'rb') as fh:
        for pezzo in iter(lambda: fh.read(65536), b''):
            h.update(pezzo)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='feature_v2_omnifall.csv')
    ap.add_argument('--feature', default='DTW',
                    help='DTW | DTWH (DTW + altezza dal pavimento) | A1 | A2 | A3')
    ap.add_argument('--compito', default='evento', choices=list(COMPITI))
    ap.add_argument('--camera', type=int, default=1)
    ap.add_argument('--soglia', type=float, default=0.5)
    ap.add_argument('--n-alberi', type=int, default=config.N_ALBERI)
    ap.add_argument('--scelte', default=None,
                    help='file della selezione DTW da usare. Predefinito: '
                         'risultati/dtw/scelte.txt, che viene RISCRITTO a ogni '
                         'analisi (ISS-159). Indicarlo esplicitamente e il solo '
                         'modo di sapere quale ordine di colonne e finito nel '
                         'pacchetto.')
    ap.add_argument('--out', default='deploy_board')
    ap.add_argument('--clip-parita', default=None,
                    help='la clip su cui vale il riferimento per fotogramma. '
                         'Se non data, la prima che esiste in clip_demo/')
    a = ap.parse_args()

    import joblib

    # La stessa funzione che usa l'addestramento: se i due divergessero, il
    # pacchetto porterebbe colonne diverse da quelle su cui il modello e'
    # stato addestrato, e nulla lo segnalerebbe.
    colonne = colonne_di(a.feature, a.scelte)
    df = carica(a.csv, camera=a.camera)
    if 'classe_omnifall' not in df.columns:
        sys.exit('il CSV non ha `classe_omnifall`: eseguire mappa_omnifall.py')

    print('=' * 78)
    print(f'PACCHETTO PER LA BOARD — {a.feature} ({len(colonne)} grandezze), '
          f'compito «{a.compito}»')
    print('=' * 78)

    X, y = finestre(df, colonne, COMPITI[a.compito])
    sc = Scaler(colonne).fit(df)
    Xs = sc.transform(X)

    print(f'finestre        {len(X):,}   positive {int(y.sum()):,} '
          f'({100*y.mean():.1f}%)')
    print(f'soggetti        {df[COL_SOGGETTO].nunique()}   camera {a.camera}')

    mod = Foresta(n_classi=2, n_alberi=a.n_alberi).addestra(Xs, y)
    p = mod.probabilita(Xs)[:, 1]
    print(f'alberi          {a.n_alberi}   nodi totali {mod.n_parametri:,}')
    print(f'in-sample       allarme sul {100*(p >= a.soglia).mean():.1f}% '
          f'delle finestre (atteso ~{100*y.mean():.1f}%)')

    out = os.path.join(RADICE, a.out)
    os.makedirs(out, exist_ok=True)

    # IL MOTORE, copiato e non ricordato. Da qui in poi la copia sulla board
    # e' un artefatto di questo script: se qualcuno modifica src/geometry.py
    # senza riesportare, l'impronta nel metadato non torna e `rileva.py` si
    # rifiuta di partire.
    sorgente_motore = os.path.join(config.RADICE, 'src', 'geometry.py')
    shutil.copyfile(sorgente_motore, os.path.join(out, 'geometry.py'))
    joblib.dump(mod._m, os.path.join(out, 'modello.pkl'))
    joblib.dump({'scaler': sc._s, 'colonne': list(colonne),
                 'maschera_log1p': sc.maschera.tolist()},
                os.path.join(out, 'scaler.pkl'))

    # ---- campioni di parita' ----
    rng = np.random.default_rng(config.SEME)
    pos = np.where(y == 1)[0]
    neg = np.where(y == 0)[0]
    idx = np.concatenate([rng.choice(pos, min(100, len(pos)), replace=False),
                          rng.choice(neg, min(100, len(neg)), replace=False)])
    np.savez_compressed(os.path.join(out, 'parita.npz'),
                        X=Xs[idx].astype(np.float32), p_attesa=p[idx],
                        y=y[idx])

    # La clip del riferimento per fotogramma. Fino al 2026-09-09 era un nome
    # SCRITTO A MANO nel metadato, e la clip che nominava --- evt_0067_155044
    # --- in `clip_demo/` non c'e'. Il metadato dichiarava quindi una verifica
    # su un file inesistente, e nessuno se n'e' accorto perche' il campo non
    # veniva letto da niente che potesse fallire.
    # La fonte di verita' e' il riferimento stesso: `parita_frame.py` scrive
    # dentro l'npz la clip su cui l'ha calcolato. Sceglierla qui a colpo
    # d'occhio non funziona --- due delle sei clip di prova non contengono
    # nessuno nei primi sessanta fotogrammi, e il primo tentativo aveva
    # pescato proprio una di quelle.
    clip_parita = a.clip_parita
    rif_np = os.path.join(out, 'parita_frame_pc.npz')
    if clip_parita is None and os.path.exists(rif_np):
        try:
            with np.load(rif_np, allow_pickle=True) as z:
                if 'clip' in z:
                    clip_parita = 'clip_demo/' + str(z['clip'])
        except Exception:
            pass

    meta = {
        'creato': datetime.now().isoformat(timespec='seconds'),
        'csv_sorgente': os.path.basename(a.csv),
        'selezione_dtw': os.path.basename(a.scelte) if a.scelte else 'scelte.txt (predefinito)',
        'compito': a.compito,
        'positivo': {'evento': 'la transizione: l atto di cadere',
                     'stato': 'essere a terra dopo una caduta',
                     'allarme': 'transizione oppure stato'}[a.compito],
        'modello': 'foresta casuale su feature aggregate della finestra',
        'n_alberi': a.n_alberi, 'n_nodi': mod.n_parametri,
        'aggregazione': 'media, dev.std, min, max, primo, ultimo -> '
                        '6 statistiche per grandezza',
        'feature_set': a.feature, 'colonne': list(colonne),
        'n_colonne': len(colonne),
        'maschera_log1p': sc.maschera.tolist(),
        'lunghezza_finestra': config.LUNGHEZZA_FINESTRA,
        'passo_finestra': config.PASSO_FINESTRA,
        'frame_step_dataset': config.FRAME_STEP,
        'fps_assunti': config.FPS_ESERCIZIO,
        'durata_finestra_s': round(config.LUNGHEZZA_FINESTRA / config.FPS_ESERCIZIO, 3),
        'k_integrali': config.K_INTEGRALI,
        # La finestra degli integrali come DURATA (ISS-148). E' questa che
        # governa il buffer sul dispositivo: il conteggio dipende dalla
        # cadenza, e la cadenza della board non e' quella del dataset.
        'durata_integrali_s': round(config.DURATA_INTEGRALI_S, 6),
        'fps_riferimento': config.FPS_DATASET,
        'riscaldamento_s': round(config.K_INTEGRALI / config.FPS_DATASET, 2),
        # Lo schema: tutte le grandezze che il motore calcola, nell'ordine in
        # cui le restituisce, e la posizione in esso delle dodici installate.
        # `rileva.py` lo confronta all'avvio con cio' che il suo motore
        # produce davvero.
        'schema_feature': list(NOMI),
        'n_schema': len(NOMI),
        'indici_colonne': [list(NOMI).index(c) for c in colonne],
        'soglia': a.soglia,
        'origine_soglia': 'dichiarata a priori. Il confronto fra sei regole di '
                          'selezione (EXP-010) mostra che sceglierla su un solo '
                          'soggetto di validazione aggiunge piu rumore di quanto '
                          'adattamento porti: deviazione 0,37 su [0,1].',
        'regola_decisione': {'persistenza_finestre': 5, 'sospensione_s': 30,
                             'nota': 'una raffica di finestre consecutive e UN '
                                     'allarme, non N. Fattore misurato 44,8.'},
        'camera': a.camera, 'n_soggetti': int(df[COL_SOGGETTO].nunique()),
        'n_finestre_train': int(len(X)), 'n_positive_train': int(y.sum()),
        'stimatore_posa': 'mediapipe 0.10.11, solutions, una persona',
        'risoluzione': '640x480 (ridimensionare prima di MediaPipe)',
        'versioni_pc': {'python': platform.python_version(),
                        'numpy': np.__version__,
                        'pandas': pd.__version__},
        'sha256_geometry': _impronta(os.path.join(
            config.RADICE, 'src', 'geometry.py')),
        'parita_fotogrammi': {
            'riferimento': 'parita_frame_pc.npz',
            'clip': clip_parita,
            'nota': 'Prodotto sul PC con la stessa versione di MediaPipe '
                    'della board. La parita sulle finestre salta lo '
                    'stimatore di posa: e questa la verifica che conta.'},
        'nota_parita': 'Le predizioni sulla board devono coincidere con '
                       'p_attesa in parita.npz entro 1e-6. Se divergono, le '
                       'versioni di scikit-learn non sono compatibili e nessuna '
                       'misura successiva e valida.',
    }
    with open(os.path.join(out, 'metadata.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    # La parita' per fotogramma e' calcolata con IL MOTORE, quindi se il
    # motore cambia il riferimento invecchia. Non e' rigenerabile da qui ---
    # serve MediaPipe nella versione della board --- ma tacere non aiuta.
    if clip_parita is None:
        print()
        print('  ATTENZIONE: il riferimento per fotogramma non dichiara su '
              'quale clip vale.')
        print('  Rigenerarlo:  python deploy_board/parita_frame.py --video '
              'clip_demo/<clip> \\')
        print('                       --out deploy_board/parita_frame_pc.npz')
    rif = os.path.join(out, 'parita_frame_pc.npz')
    if (os.path.exists(rif)
            and os.path.getmtime(rif) < os.path.getmtime(sorgente_motore)):
        print()
        print('  ATTENZIONE: parita_frame_pc.npz e piu vecchio di '
              'src/geometry.py.')
        print('  Il riferimento per fotogramma e stato prodotto da un motore '
              'diverso da questo:')
        print('  va rigenerato con deploy_board/parita_frame.py, altrimenti '
              'la verifica')
        print('  fallira sul dispositivo per una ragione che non e una '
              'divergenza vera.')

    print()
    print(f'riscaldamento   {meta["riscaldamento_s"]} s '
          f'(buffer degli integrali, {config.DURATA_INTEGRALI_S:.4f} s '
          f'= {config.K_INTEGRALI} campioni a {config.FPS_DATASET:.0f} fps)')
    print(f'finestra        {meta["durata_finestra_s"]} s '
          f'({config.LUNGHEZZA_FINESTRA} campioni a {config.FPS_ESERCIZIO:.0f} fps)')
    print()
    print(f'scritto in {a.out}/:')
    for f_ in ('modello.pkl', 'scaler.pkl', 'geometry.py', 'metadata.json',
               'parita.npz'):
        p_ = os.path.join(out, f_)
        print(f'   {f_:<16} {os.path.getsize(p_)/1024:8.1f} KB')


if __name__ == '__main__':
    main()
