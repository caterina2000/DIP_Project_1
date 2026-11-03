# -*- coding: utf-8 -*-
"""
Scheda dei numeri: un estratto compatto di ogni file di risultato.

Serve a scrivere i capitoli contro i file che producono i numeri, invece che
contro il testo precedente. E' il rimedio a ISS-123: cinque valori del
Capitolo 1 venivano da un'edizione diversa della fonte e nessuno se n'era
accorto perche' nessuno li aveva riletti alla sorgente.
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def carica(p):
    with io.open(p, encoding='utf-8') as fh:
        return json.load(fh)


def breve(v, n=4):
    if isinstance(v, float):
        return round(v, n)
    return v


print('=' * 78)
print('RUN DI ADDESTRAMENTO  (LOSO, 10 soggetti)')
print('=' * 78)
print(f"{'run':<44}{'F2':>7}{'dev':>7}{'rec':>7}{'prec':>7}{'par':>9}{'s':>7}")
for nome in sorted(os.listdir('risultati/addestramento')):
    if not nome.startswith('run_'):
        continue
    d = carica(os.path.join('risultati/addestramento', nome))
    chiavi = list(d.keys())
    f2 = d.get('f2_media', d.get('f2'))
    print(f"{nome[4:-5]:<44}"
          f"{breve(f2,3) if f2 is not None else '?':>7}"
          f"{breve(d.get('f2_dev'),3) if d.get('f2_dev') is not None else '?':>7}"
          f"{breve(d.get('recall'),3) if d.get('recall') is not None else '?':>7}"
          f"{breve(d.get('precision'),3) if d.get('precision') is not None else '?':>7}"
          f"{d.get('n_parametri','?'):>9}"
          f"{int(d.get('durata_s',0)):>7}")
    if nome.startswith('run_gru_tre_classi_DTW_cam1_L22'):
        print('    chiavi disponibili:', chiavi)

print()
for p in ('risultati/laboratorio/run_10soggetti.json',
          'risultati/campo/valutazione_incrociata_10sog.json',
          'risultati/campo/pr_auc_allineato.json',
          'risultati/campo/compiti_in_casa.json',
          'risultati/campo/latenza.json',
          'risultati/campo/valutazione_10sog_k31.json',
          'risultati/occlusioni/foresta_DTW.json',
          'risultati/rumore/foresta_cam1.json',
          'risultati/esterno/urfall_foresta_caduta.json',
          'risultati/esterno/urfall_foresta_scarta.json',
          'risultati/compiti/foresta_DTW_cam1.json',
          'risultati/cinque_soggetti/exp017_rf_size.json'):
    if not os.path.exists(p):
        print('MANCA', p)
        continue
    print('=' * 78)
    print(p)
    print('=' * 78)
    d = carica(p)
    testo = json.dumps(d, ensure_ascii=False, indent=1, default=str)
    if len(testo) > 3500:
        testo = testo[:3500] + '\n  ...[troncato]'
    print(testo)
    print()
