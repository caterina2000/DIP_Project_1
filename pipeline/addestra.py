"""
Addestra e valuta in leave-one-subject-out, con soglia scelta sul validation.

Il ciclo, una volta sola
------------------------
Ogni combinazione di architettura e modo di etichettatura passa esattamente da
qui. Non esistono cicli alternativi: e' l'unico modo perche' una differenza
misurata fra due configurazioni sia attribuibile alla configurazione.

Per ogni fold:

    1. tre insiemi disgiunti per persona (test, validation, resto)
    2. scaler stimato sui soli fotogrammi di addestramento
    3. addestramento con pesi di classe, arresto sull'AUC di allarme del
       validation
    4. soglia scelta sul VALIDATION, massimizzando F-beta
    5. quella soglia applicata al TEST, una volta sola

Il punto 5 e' la ragione per cui il punto 4 esiste. Scegliere la soglia
guardando il test significa usare per una decisione di progetto l'insieme che
dovrebbe dare una stima imparziale, e il numero che ne esce non dice piu' nulla
su come andra' su una persona nuova.

Cosa viene salvato
------------------
Un `run_metadata.json` per run con TUTTO cio' che serve a rifarla: colonne,
lunghezza della finestra, passo, modo, soglie di etichettatura, architettura,
iperparametri, seme, soggetti di ogni fold, soglia scelta e metriche. Una run
senza metadati e' una run che fra un mese non si sa piu' cosa fosse.

Uso:
    python pipeline/addestra.py --modello gru --modo tre_classi
    python pipeline/addestra.py --modello gru --feature A3 --camera 2
    python pipeline/addestra.py --tutti          # 5 architetture x 3 modi
"""

import argparse
import json
import os
import platform
import sys
import time
from datetime import datetime

import numpy as np

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '3')

import config
from src.dati import FEATURE, carica, conteggio, costruisci_finestre, feature_dtw, fold_loso
from src.etichettatura import MODI
from src.modelli import ARCHITETTURE, costruisci
from src.valutazione import (aggrega, metriche, probabilita_allarme,
                             scegli_soglia, tabella_fold)


def colonne_di(nome: str):
    """'DTW' legge il file dell'analisi; gli altri sono i bacini."""
    if nome.upper() == 'DTW':
        return feature_dtw()
    # Prima il nome esatto, poi maiuscolo: i bacini si chiamano A1/A2/A3 ma le
    # varianti senza integrali A1base/A2base/A3base, e un .upper() secco le
    # renderebbe irraggiungibili.
    for chiave in (nome, nome.upper()):
        if chiave in FEATURE:
            return FEATURE[chiave]
    raise ValueError(f'insieme di feature sconosciuto: {nome!r} '
                     f'(attesi: DTW, {", ".join(FEATURE)})')


def una_run(df, colonne, modo, architettura, camera, verboso=False,
            soglia_fissa=None, lunghezza=None, **kw):
    """Un LOSO completo. Ritorna (elenco_metriche, nomi_fold, metadati)."""
    t0 = time.time()
    risultati, nomi, dettagli, punteggi = [], [], [], []
    n_par = None

    for f in fold_loso(df, colonne, modo, lunghezza=lunghezza):
        m = costruisci(architettura, (f.X_train.shape[1], f.X_train.shape[2]),
                       f.n_classi, **kw)
        m.addestra(f.X_train, f.y_train, f.Xv_modello, f.yv_modello,
                   verboso=1 if verboso else 0)
        n_par = m.n_parametri

        p_val = probabilita_allarme(m.probabilita(f.X_val))
        if soglia_fissa is not None:
            # Soglia dichiarata prima di guardare i dati. Con un solo soggetto
            # di validazione la scelta per fold aggiunge piu' rumore di quanto
            # adattamento porta -- misurato in EXP-008: deviazione della soglia
            # 0,37 su un intervallo [0,1]. Una soglia fissa non stima nulla,
            # quindi non puo' sovradattarsi, ed e' quella che rende il
            # confronto fra architetture una misura del MODELLO.
            soglia = float(soglia_fissa)
            fb_val = metriche(f.y_val, p_val, soglia)['fbeta']
        else:
            soglia, fb_val = scegli_soglia(f.y_val, p_val)

        p_test = probabilita_allarme(m.probabilita(f.X_test))
        r = metriche(f.y_test, p_test, soglia)
        r['fbeta_val'] = fb_val

        # Le probabilita' si salvano, non solo le metriche. Confrontare una
        # regola di scelta della soglia diversa non deve costare un nuovo
        # addestramento: con queste su disco costa secondi.
        punteggi.append({'test': f.soggetto_test, 'val': f.soggetto_val,
                         'p_val': p_val, 'y_val': f.y_val,
                         'p_test': p_test, 'y_test': f.y_test})

        risultati.append(r)
        nomi.append(f.soggetto_test)
        dettagli.append({
            'test': f.soggetto_test, 'val': f.soggetto_val,
            'train': list(f.soggetti_train),
            'n_train': int(len(f.X_train)), 'n_val': int(len(f.X_val)),
            'n_test': int(len(f.X_test)),
            'positivi_test': int(f.y_test.sum()),
            'soglia': soglia, **{k: r[k] for k in
                                 ('fbeta', 'f1', 'recall', 'precision',
                                  'tp', 'fp', 'fn', 'tn')},
        })
        if verboso:
            print(f'  {f.soggetto_test}: soglia {soglia:.2f} '
                  f'F2 {r["fbeta"]:.3f} (val {fb_val:.3f})', flush=True)

    meta = {
        'data': datetime.now().isoformat(timespec='seconds'),
        'architettura': architettura, 'modo_etichettatura': modo,
        'n_classi': 3 if modo == 'tre_classi' else 2,
        'colonne': list(colonne), 'n_feature': len(colonne),
        'camera': camera,
        'lunghezza_finestra': lunghezza or config.LUNGHEZZA_FINESTRA,
        'passo_finestra': config.PASSO_FINESTRA,
        'frame_step': config.FRAME_STEP,
        'fps_dataset': config.FPS_DATASET, 'fps_esercizio': config.FPS_ESERCIZIO,
        'k_integrali': config.K_INTEGRALI,
        'soglie_etichettatura': dict(config.SOGLIE_ETICHETTATURA),
        'beta': config.BETA, 'seme': config.SEME,
        'epoche_max': config.EPOCHE, 'batch': config.BATCH,
        'learning_rate': config.LEARNING_RATE,
        'iperparametri': kw,
        'n_parametri': n_par,
        'scaler': 'log1p sulle asimmetriche + StandardScaler, '
                  'stimato sui fotogrammi di addestramento del fold',
        'split': 'leave-one-subject-out, validation = soggetto successivo',
        'scelta_soglia': (f'fissa a {soglia_fissa}, dichiarata a priori'
                          if soglia_fissa is not None else
                          'massimo F-beta sul validation, applicata al test '
                          'una volta sola'),
        'durata_s': round(time.time() - t0, 1),
        'python': platform.python_version(),
        'fold': dettagli,
        'aggregato': aggrega(risultati),
    }
    return risultati, nomi, meta, punteggi


def salva(meta, punteggi, out_dir, etichetta):
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, f'run_{etichetta}.json')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    # Un .npz con le probabilita' di ogni fold, appiattite con un indice di
    # fold accanto: cosi' resta un file solo e si ricostruisce con una
    # maschera. Serve a pipeline/soglia.py.
    fuori = {}
    for i, q in enumerate(punteggi):
        for k in ('p_val', 'y_val', 'p_test', 'y_test'):
            fuori[f'{k}_{i}'] = np.asarray(q[k])
    fuori['fold_test'] = np.array([q['test'] for q in punteggi])
    fuori['fold_val'] = np.array([q['val'] for q in punteggi])
    np.savez_compressed(os.path.join(out_dir, f'punteggi_{etichetta}.npz'),
                        **fuori)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='feature.csv')
    ap.add_argument('--modello', default='gru', choices=list(ARCHITETTURE))
    ap.add_argument('--modo', default='tre_classi', choices=list(MODI))
    ap.add_argument('--feature', default='DTW',
                    help='DTW | A1 | A2 | A3 | TUTTE')
    ap.add_argument('--camera', type=int, default=1)
    ap.add_argument('--tutti', action='store_true',
                    help='tutte le architetture per tutti i modi')
    ap.add_argument('--lunghezza', type=int, default=None,
                    help='campioni per finestra (default da config)')
    ap.add_argument('--soglia', type=float, default=0.5,
                    help='soglia fissa (default 0,5); -1 per sceglierla sul '
                         'validation con il massimo di F-beta')
    ap.add_argument('--senza-estremi', action='store_true',
                    help='foresta: riassume la finestra senza primo e ultimo '
                         'campione, togliendo l ultima traccia di ordine '
                         'temporale che il riassunto conserva')
    ap.add_argument('--verboso', action='store_true')
    a = ap.parse_args()

    colonne = colonne_di(a.feature)
    df = carica(a.csv, camera=a.camera)

    print('=' * 74)
    print(f'{a.feature}: {len(colonne)} grandezze · camera {a.camera} · '
          f'{df.soggetto.nunique()} soggetti · {df.ripresa.nunique()} riprese')
    print('=' * 74)

    _, ytr, yal, _, _ = costruisci_finestre(df, colonne, a.modo,
                                           lunghezza=a.lunghezza)
    print(conteggio(ytr, yal))
    print()

    out = os.path.join(config.RISULTATI_DIR, 'addestramento')
    combinazioni = ([(m, mo) for m in ARCHITETTURE for mo in MODI]
                    if a.tutti else [(a.modello, a.modo)])

    riepilogo = []
    for modello, modo in combinazioni:
        print(f'--- {modello} · {modo}', flush=True)
        r, nomi, meta, punteggi = una_run(
            df, colonne, modo, modello, a.camera, verboso=a.verboso,
            soglia_fissa=None if a.soglia < 0 else a.soglia,
            lunghezza=a.lunghezza,
            **({'estremi': False} if a.senza_estremi else {}))
        print(tabella_fold(r, nomi))
        ag = meta['aggregato']
        print(f'parametri: {meta["n_parametri"]:,} · '
              f'durata {meta["durata_s"]:.0f} s')
        p = salva(meta, punteggi, out,
                  f'{modello}_{modo}_{a.feature}_cam{a.camera}'
                  f'_L{a.lunghezza or config.LUNGHEZZA_FINESTRA}'
                  f'{"_noestremi" if a.senza_estremi else ""}')
        print(f'salvato: {os.path.relpath(p, RADICE)}\n', flush=True)
        riepilogo.append((modello, modo, ag, meta['n_parametri']))

    if len(riepilogo) > 1:
        print('=' * 74)
        print(f"{'architettura':<14}{'modo':<12}{'F2':>16}{'recall':>10}"
              f"{'prec.':>9}{'parametri':>12}")
        print('-' * 74)
        for modello, modo, ag, np_ in sorted(riepilogo,
                                             key=lambda t: -t[2]['fbeta_media']):
            print(f"{modello:<14}{modo:<12}"
                  f"{ag['fbeta_media']:8.3f} +-{ag['fbeta_dev']:5.3f}"
                  f"{ag['recall_media']:10.3f}{ag['precision_media']:9.3f}"
                  f"{np_:12,}")


if __name__ == '__main__':
    main()
