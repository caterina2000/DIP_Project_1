"""
Rilevamento cadute sulla board — DA ESEGUIRE SULLA BOARD.

    telecamera -> 640x480 -> MediaPipe -> 12 grandezze geometriche
               -> finestra di 22 campioni -> foresta -> allarme

Nessuna immagine lascia il dispositivo. Le clip attorno agli allarmi, se
attivate, restano su disco locale.

PRIMA DI TUTTO: la prova di parita'

    python3 rileva.py --parita

Esegue TRE verifiche e le dichiara una per una:

  1. IMPRONTA DI geometry.py. Il file esiste in due copie, una qui e una in
     src/ sul PC, tenute allineate a mano. Se divergono, la board calcola
     grandezze diverse e nessuna misura successiva vale -- senza che nulla
     sollevi un errore. L'impronta attesa sta in metadata.json.
  2. PARITA SULLE FINESTRE. Duecento finestre gia' calcolate: verifica che
     modello e scaler si trasferiscano. Trenta secondi, non serve MediaPipe.
  3. PARITA SUI FOTOGRAMMI. La stessa clip elaborata dall'immagine in poi.
     E' la verifica che conta: la (2) e' passata con scarto ESATTAMENTE ZERO
     mentre le stesse clip davano risultati diversi sulle due macchine --
     picco 1,000 con allarme sul PC contro 0,560 senza allarme sulla board.
     Il modello era identico; a differire erano le grandezze in ingresso.

Le prime due sono obbligatorie e bloccanti. La terza richiede un riferimento
prodotto sul PC e la clip corrispondente: se mancano viene DICHIARATA non
eseguita, e non impedisce la sessione.

POI

    python3 rileva.py                      dalla telecamera
    python3 rileva.py --video clip/        da una cartella di fotogrammi
    python3 rileva.py --durata 60          si ferma dopo un minuto

Due cose che il sistema dichiara, e che vanno lette
---------------------------------------------------
RISCALDAMENTO. Nove delle dodici grandezze sono integrali accumulati sugli
ultimi 31 fotogrammi. Finche' il buffer non e' pieno i valori non sono
affidabili: il sistema non decide, e lo dichiara a schermo. Circa 1,7 secondi.

ALLARME CONTRO FINESTRA SOPRA SOGLIA. Una raffica di finestre consecutive
sopra soglia e' UN allarme, non N: servono 5 finestre consecutive e poi 30
secondi di silenzio. Il contatore mostra entrambi i numeri perche' il loro
rapporto -- misurato 47,8 sulle sessioni registrate -- e' esattamente cio' che
distingue un dato riportabile da uno che sovrastima di due ordini di grandezza.

IL RIEPILOGO SI SCRIVE MENTRE LA SESSIONE VA AVANTI, ogni cinque minuti, con
un campo `parziale` che dice se la sessione era ancora in corso. Prima veniva
scritto solo alla fine: una prova di dodici ore interrotta all'undicesima
lasciava il registro dei punteggi e nessun bilancio del costo per fase, che e'
il numero per cui la prova si fa.
"""

import argparse
import hashlib
import json
import os
import sys
import time
from collections import deque

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

VERDE, ROSSO, GIALLO, GRIGIO, FINE = (
    '\033[92m', '\033[91m', '\033[93m', '\033[90m', '\033[0m')

RIEPILOGO_OGNI_S = 300.0


# ---------------------------------------------------------------------
# CLIP ATTORNO AGLI ALLARMI
#
# Il registratore di agosto (`DIP_PROJECT/deploy_board/session_recorder.py`)
# le salvava; la riscrittura di questo file le ha perse, e la sessione del
# 6 settembre non ha una sola immagine. Due conseguenze, entrambe misurate:
# la verifica di parita' DAI FOTOGRAMMI si e' dichiarata non eseguita
# («cartella dei fotogrammi non trovata»), ed e' il punto cieco descritto nel
# Capitolo 5; e i quattordici allarmi di quella sessione non sono
# verificabili, quindi non si possono chiamare falsi positivi --- si puo'
# solo dire che il sistema li ha generati.
#
# Si salva il PRIMA e il DOPO. Il dopo da solo mostra una persona a terra
# senza dire come ci sia arrivata, ed e' proprio quello che distingue una
# caduta da uno sdraiarsi.
#
# NON e' una registrazione continua: sono pochi secondi attorno agli allarmi,
# restano sul dispositivo, e il tetto per sessione impedisce che una notte
# storta riempia il disco e faccia perdere le feature, che sono il dato
# principale.
CLIP_PRE_S = 10.0
CLIP_POST_S = 10.0
CLIP_FPS = 10             # sottocampionata: serve a capire, non a rivedere
CLIP_QUALITA = 80
CLIP_MAX = 150


class BufferClip:
    """Gli ultimi CLIP_PRE_S secondi, sottocampionati a CLIP_FPS."""

    def __init__(self):
        self.buf = deque(maxlen=int(CLIP_PRE_S * CLIP_FPS) + 2)
        self._ultimo = -1e18

    def offri(self, frame, t):
        if t - self._ultimo >= 1.0 / CLIP_FPS:
            self.buf.append((t, frame.copy()))
            self._ultimo = t

    def svuota(self):
        out = list(self.buf)
        self.buf.clear()
        return out


def carica():
    import joblib
    meta = json.load(open(os.path.join(QUI, 'metadata.json'), encoding='utf-8'))
    modello = joblib.load(os.path.join(QUI, 'modello.pkl'))
    blob = joblib.load(os.path.join(QUI, 'scaler.pkl'))
    return meta, modello, blob


def normalizza(X, blob):
    """log1p sulle colonne asimmetriche, poi standardizzazione. Come sul PC."""
    Z = np.asarray(X, dtype=np.float64).copy()
    m = np.asarray(blob['maschera_log1p'], dtype=bool)
    if m.any():
        c = np.where(m)[0]
        Z[..., c] = np.sign(Z[..., c]) * np.log1p(np.abs(Z[..., c]))
    forma = Z.shape
    return blob['scaler'].transform(Z.reshape(-1, forma[-1])).reshape(forma)


def riassumi(X):
    """Sei statistiche per grandezza. Identica a src/modelli.py sul PC."""
    return np.concatenate([X.mean(1), X.std(1), X.min(1), X.max(1),
                           X[:, 0, :], X[:, -1, :]], axis=1)


# ============================================================
# LE TRE VERIFICHE DI AVVIO
# ============================================================

def impronta_file(percorso):
    """sha256 del file. Serve a confrontare due copie che devono coincidere."""
    h = hashlib.sha256()
    with open(percorso, 'rb') as fh:
        for pezzo in iter(lambda: fh.read(65536), b''):
            h.update(pezzo)
    return h.hexdigest()


def costruisci_motore(meta):
    """
    Il motore, con la finestra degli integrali espressa come DURATA.

    ISS-148: `k_integrali` e' un conteggio di fotogrammi, e lo stesso
    conteggio non e' la stessa cosa ai due lati. In estrazione 31 fotogrammi
    a 18 fps sono 1,72 s; qui, alla cadenza misurata di 7,26 fps, sarebbero
    4,27 s. Il modello ha imparato su grandezze che riassumono 1,72 s e ne
    riceverebbe di omonime che ne riassumono due volte e mezzo tanto.

    Con la durata il buffer tiene 1,72 s comunque vada la telecamera.
    """
    from geometry import MotoreGeometrico

    durata = meta.get('durata_integrali_s')
    if durata:
        return MotoreGeometrico(durata_integrali=float(durata))
    # Pacchetto vecchio, senza la durata dichiarata: si ricade sul conteggio,
    # ed e' esattamente il caso che ISS-148 descrive. Non e' un errore da
    # fermare qui -- lo dice la verifica dello schema -- ma non e' allineato.
    return MotoreGeometrico(k_integrali=meta['k_integrali'])


class Cadenza:
    """
    La cadenza vera, misurata su una finestra mobile.

    Serve a `fotogramma()`, che divide per dt: fino al 2026-09-09 riceveva
    `fps_assunti` = 9,0 mentre la board ne faceva 7,26, e le derivate
    uscivano sopravvalutate del 24%.

    Si usa la MEDIANA degli intervalli, non la media: un fotogramma che
    arriva in ritardo perche' il sistema operativo ha fatto altro non deve
    spostare la stima. Gli intervalli oltre i cinque secondi si scartano ---
    sono le riaperture della telecamera e i risvegli, non cadenza.
    """

    def __init__(self, fps_ripiego, campioni=30, minimi=5):
        self.d = deque(maxlen=campioni)
        self.t_prec = None
        self.ripiego = float(fps_ripiego)
        self.minimi = minimi

    def osserva(self, t):
        if self.t_prec is not None:
            dt = t - self.t_prec
            if 1e-4 < dt < 5.0:
                self.d.append(dt)
        self.t_prec = t

    def fps(self):
        """Finche' i campioni non bastano, il valore dichiarato."""
        if len(self.d) < self.minimi:
            return self.ripiego
        v = sorted(self.d)
        return 1.0 / v[len(v) // 2]


def verifica_schema(meta):
    """
    Le grandezze che il motore calcola contro quelle che il pacchetto
    dichiara, nome per nome e nello stesso ordine.

    L'impronta sha256 dice SE due file differiscono, non IN CHE COSA: un
    commento riscritto la fa fallire, e una grandezza mancante la fa fallire
    allo stesso modo. Questa dice quale grandezza manca --- ed e' il caso
    vero, accaduto: `A3_h_pavimento` e' stata aggiunta al motore del progetto
    il 6 settembre e la copia sul dispositivo non l'aveva (ISS-139), mentre
    il modello girava lo stesso perche' le dodici colonne installate non la
    contenevano.
    """
    from geometry import MotoreGeometrico

    atteso = meta.get('schema_feature')
    qui = list(MotoreGeometrico().fotogramma(None, None, 640, 480, 18.0).keys())
    colonne = list(meta.get('colonne', []))
    mancanti = [c for c in colonne if c not in qui]
    if not atteso:
        return {'dichiarato': False, 'n_qui': len(qui),
                'colonne_mancanti': mancanti,
                'coincide': None if not mancanti else False}
    atteso = list(atteso)
    return {
        'dichiarato': True,
        'n_qui': len(qui), 'n_atteso': len(atteso),
        'solo_qui': [c for c in qui if c not in atteso],
        'solo_atteso': [c for c in atteso if c not in qui],
        'ordine_diverso': bool(sorted(qui) == sorted(atteso) and qui != atteso),
        'colonne_mancanti': mancanti,
        'coincide': bool(qui == atteso and not mancanti),
    }


def verifica_geometria(meta):
    """
    L'impronta di geometry.py contro quella dichiarata in metadata.json.

    Le due copie del motore geometrico -- src/geometry.py sul PC e questa --
    devono essere lo stesso file. Sono tenute allineate a mano, e il giorno in
    cui divergeranno la board produrra' grandezze diverse senza segnalare
    niente: non un errore, solo numeri sbagliati.
    """
    atteso = meta.get('sha256_geometry')
    percorso = os.path.join(QUI, 'geometry.py')
    qui = impronta_file(percorso) if os.path.exists(percorso) else None
    return {
        'sha256_qui': qui,
        'sha256_atteso': atteso,
        'dichiarato': atteso is not None,
        # senza impronta dichiarata non si puo' concludere nulla: e' un caso
        # diverso da «coincide», e va tenuto distinto in lettura
        'coincide': (qui == atteso) if (atteso and qui) else None,
    }


def verifica_parita_finestre(meta, modello, blob, tol=1e-6):
    """Duecento finestre gia' calcolate: modello e scaler si trasferiscono?"""
    percorso = os.path.join(QUI, 'parita.npz')
    if not os.path.exists(percorso):
        return {'eseguita': False, 'motivo': 'manca parita.npz'}
    d = np.load(percorso)
    p = modello.predict_proba(riassumi(d['X']))[:, 1]
    scarto = float(np.abs(p - d['p_attesa']).max())
    try:
        import sklearn
        versione = sklearn.__version__
    except Exception:
        versione = None
    return {'eseguita': True, 'finestre': int(len(p)), 'scarto_massimo': scarto,
            'tolleranza': tol, 'superata': bool(scarto <= tol),
            'sklearn': versione}


def verifica_parita_fotogrammi(meta, riferimento=None, clip=None, limite=60):
    """
    La stessa clip elaborata dall'immagine in poi, confrontata colonna per
    colonna con un riferimento prodotto sul PC.

    E' la verifica che chiude il punto cieco: quella sulle finestre salta lo
    stimatore di posa, che e' un tracciatore e diverge fra architetture, ed e'
    proprio li' che nasce l'unica differenza di comportamento mai osservata.

    Non e' bloccante. Se manca il riferimento o la clip, viene dichiarata non
    eseguita: una prova di dodici ore non deve fermarsi perche' un file di
    controllo non e' stato copiato.
    """
    cfg = meta.get('parita_fotogrammi') or {}
    riferimento = riferimento or os.path.join(QUI, cfg.get('riferimento', ''))
    clip = clip or cfg.get('clip')

    if not cfg.get('riferimento') and not os.path.isfile(str(riferimento)):
        return {'eseguita': False,
                'motivo': 'nessun riferimento dichiarato in metadata.json'}
    if not os.path.isfile(str(riferimento)):
        return {'eseguita': False,
                'motivo': f'riferimento non trovato: {riferimento}'}
    if not clip or not os.path.isdir(str(clip)):
        return {'eseguita': False,
                'motivo': f'cartella dei fotogrammi non trovata: {clip}'}

    try:
        from parita_frame import estrai
        V, P, LM, files, mpv, cvv = estrai(clip, meta['colonne'],
                                           meta['k_integrali'],
                                           meta['fps_assunti'], limite)
    except Exception as e:                       # MediaPipe assente, clip rotta
        return {'eseguita': False, 'motivo': f'{type(e).__name__}: {e}'}

    R = np.load(riferimento, allow_pickle=True)
    n = min(len(V), len(R['valori']))
    if n == 0:
        return {'eseguita': False, 'motivo': 'nessun fotogramma confrontabile'}

    # Le colonne si allineano per NOME. Il riferimento porta i propri nomi ---
    # `parita_frame.py` li scrive apposta dentro l'npz --- e confrontare per
    # POSIZIONE significa mettere a confronto due grandezze diverse appena
    # l'ordine del pacchetto cambia. E' ISS-161: installando il pacchetto v5 la
    # verifica ha dichiarato `A3_escursione` divergente al 5807%, che era
    # `A3_escursione` confrontata con `A3_ginocchia_rel_y`.
    #
    # La direzione pericolosa non e' quella: e' che due colonne scambiate con
    # valori simili facciano PASSARE la verifica, che allora dichiara una
    # parita' che non ha misurato.
    nostre = [str(c) for c in meta['colonne']]
    try:
        loro = [str(c) for c in R['colonne']]
    except (KeyError, ValueError):     # riferimento anteriore a ISS-153
        loro = []

    valori_rif = np.asarray(R['valori'], dtype=float)
    valori_qui = np.asarray(V, dtype=float)

    if loro:
        pos = {c: i for i, c in enumerate(loro)}
        comuni = [c for c in nostre if c in pos]
        if len(comuni) < 2:
            return {'eseguita': False,
                    'motivo': f'il riferimento e di un altro insieme di '
                              f'grandezze: {len(comuni)} in comune su '
                              f'{len(nostre)}. Rigenerare parita_frame_pc.npz.'}
        ia = [nostre.index(c) for c in comuni]
        ib = [pos[c] for c in comuni]
        assenti = [c for c in nostre if c not in pos]
    else:
        # Senza nomi si puo' solo confrontare per posizione, e allora la
        # larghezza deve almeno coincidere: se non coincide, non e' allineabile
        # e la verifica va dichiarata NON ESEGUITA, non superata.
        if valori_rif.shape[1] != len(nostre):
            return {'eseguita': False,
                    'motivo': 'riferimento senza nomi di colonna e di larghezza '
                              f'diversa ({valori_rif.shape[1]} contro '
                              f'{len(nostre)}): non allineabile'}
        comuni, assenti = list(nostre), []
        ia = ib = list(range(len(nostre)))

    va = valori_qui[:n][:, ia]
    vb = valori_rif[:n][:, ib]
    scale = np.maximum(np.abs(vb).mean(axis=0), 1e-9)
    relativi = np.abs(va - vb).mean(axis=0) / scale
    peggiore = int(np.argmax(relativi))
    pa, pb = P[:n], R['posa'][:n]

    return {
        'eseguita': True,
        'fotogrammi': int(n),
        'clip': os.path.basename(str(clip)),
        'riferimento': os.path.basename(str(riferimento)),
        'pose_concordi': int((pa == pb).sum()),
        'allineamento': 'per nome' if loro else 'per posizione (riferimento senza nomi)',
        'grandezze_confrontate': len(comuni),
        'grandezze_assenti_dal_riferimento': assenti,
        'per_grandezza': {c: float(r) for c, r in zip(comuni, relativi)},
        'scarto_relativo_peggiore': float(relativi[peggiore]),
        'grandezza_peggiore': comuni[peggiore],
        'superata': bool(relativi.max() < 0.01),
        'mediapipe_qui': str(mpv),
        'mediapipe_riferimento': str(R['mediapipe']),
    }


def esegui_verifiche(meta, modello, blob, riferimento=None, clip=None,
                     con_fotogrammi=True):
    v = {'geometria': verifica_geometria(meta),
         'schema': verifica_schema(meta),
         'parita_finestre': verifica_parita_finestre(meta, modello, blob)}
    v['parita_fotogrammi'] = (
        verifica_parita_fotogrammi(meta, riferimento, clip) if con_fotogrammi
        else {'eseguita': False, 'motivo': 'saltata su richiesta'})
    return v


def stampa_verifiche(v):
    """Ritorna 0 se la sessione puo' partire, 1 altrimenti."""
    print('=' * 62)
    print('VERIFICHE DI AVVIO')
    print('=' * 62)

    g = v['geometria']
    if not g['dichiarato']:
        print(f'{GIALLO}  geometria      impronta non dichiarata in '
              f'metadata.json{FINE}')
        print(f'{GRIGIO}                 sha256 qui: {g["sha256_qui"]}{FINE}')
    elif g['coincide']:
        print(f'{VERDE}  geometria      impronta coincide '
              f'({g["sha256_qui"][:16]}...){FINE}')
    else:
        print(f'{ROSSO}  geometria      IMPRONTA DIVERSA{FINE}')
        print(f'    attesa   {g["sha256_atteso"]}')
        print(f'    trovata  {g["sha256_qui"]}')
        print(f'{ROSSO}    Il motore geometrico non e quello con cui il modello'
              f' e stato addestrato.{FINE}')

    s = v['schema']
    if not s['dichiarato']:
        print(f'{GIALLO}  schema         non dichiarato nel pacchetto '
              f'({s["n_qui"]} grandezze qui){FINE}')
    elif s['coincide']:
        print(f'{VERDE}  schema         {s["n_qui"]} grandezze, nomi e ordine '
              f'coincidono{FINE}')
    else:
        print(f'{ROSSO}  schema         NON COINCIDE{FINE}')
        if s['solo_atteso']:
            print('    il pacchetto attende, e qui non ci sono: '
                  + ', '.join(s['solo_atteso']))
        if s['solo_qui']:
            print('    qui ci sono, e il pacchetto non le attende: '
                  + ', '.join(s['solo_qui']))
        if s['ordine_diverso']:
            print('    stessi nomi, ORDINE diverso')
    if s['colonne_mancanti']:
        print(f'{ROSSO}    colonne del modello che il motore non calcola: '
              + ', '.join(s['colonne_mancanti']) + f'{FINE}')

    f = v['parita_finestre']
    if not f.get('eseguita'):
        print(f'{ROSSO}  finestre       non eseguita: {f.get("motivo")}{FINE}')
    elif f['superata']:
        print(f'{VERDE}  finestre       {f["finestre"]} confrontate, scarto '
              f'{f["scarto_massimo"]:.3e}{FINE}')
    else:
        print(f'{ROSSO}  finestre       FALLITA, scarto {f["scarto_massimo"]:.3e}'
              f' oltre {f["tolleranza"]:.0e}{FINE}')
        print('    Le versioni di scikit-learn non sono compatibili.')

    p = v['parita_fotogrammi']
    if not p.get('eseguita'):
        print(f'{GIALLO}  fotogrammi     non eseguita: {p.get("motivo")}{FINE}')
        print(f'{GRIGIO}                 e la verifica che conta: senza, la '
              f'parita sulle finestre puo passare mascherando una '
              f'divergenza reale{FINE}')
    elif p['superata']:
        print(f'{VERDE}  fotogrammi     {p["fotogrammi"]} confrontati su '
              f'{p["clip"]}, {p.get("grandezze_confrontate", "?")} grandezze '
              f'{p.get("allineamento", "")}, scarto peggiore '
              f'{100 * p["scarto_relativo_peggiore"]:.2f}% '
              f'({p["grandezza_peggiore"]}){FINE}')
    else:
        print(f'{ROSSO}  fotogrammi     DIVERGONO: {p["grandezza_peggiore"]} '
              f'al {100 * p["scarto_relativo_peggiore"]:.1f}%{FINE}')
        print(f'    pose concordi {p["pose_concordi"]}/{p["fotogrammi"]}   '
              f'mediapipe {p["mediapipe_qui"]} contro '
              f'{p["mediapipe_riferimento"]}')
        # Quale grandezza diverge e di quanto: senza questo, un unico numero
        # non dice se il motore differisce o se e' una sola derivata rumorosa.
        for c, r in sorted(p.get('per_grandezza', {}).items(),
                           key=lambda kv: -kv[1])[:6]:
            print(f'      {c:24s} {100 * r:8.2f}%')
    if p.get('grandezze_assenti_dal_riferimento'):
        print(f'{GIALLO}    non nel riferimento, NON confrontate: '
              f'{", ".join(p["grandezze_assenti_dal_riferimento"])}{FINE}')

    print()
    bloccanti = []
    if g['dichiarato'] and g['coincide'] is False:
        bloccanti.append('impronta di geometry.py')
    if not f.get('eseguita') or not f.get('superata'):
        bloccanti.append('parita sulle finestre')
    # Una colonna che il modello chiede e il motore non calcola e' fatale:
    # `f[c]` solleverebbe KeyError al primo fotogramma. Uno schema diverso
    # senza colonne mancanti, invece, non ferma la sessione --- il modello
    # riceve cio' che si aspetta --- ma resta scritto in rosso.
    if s['colonne_mancanti']:
        bloccanti.append('colonne mancanti nel motore')
    if bloccanti:
        print(f'{ROSSO}  BLOCCATO — {", ".join(bloccanti)}.{FINE}')
        print('  Nessuna misura successiva sarebbe valida.')
        return 1
    print(f'{VERDE}  Si puo procedere.{FINE}')
    return 0


# ============================================================
# RIEPILOGO
# ============================================================

def costruisci_riepilogo(meta, colonne, cfg, stato, costo, t0, t, t_mono,
                         verifiche, parziale):
    """
    Il riepilogo della sessione, in qualunque istante.

    Chiamata durante la sessione da' un riepilogo `parziale`; chiamata alla
    fine, quello definitivo. E' una funzione sola perche' i due non possano
    divergere: due blocchi di codice che calcolano lo stesso bilancio finiscono
    per calcolarlo in modo diverso.
    """
    n_frame = max(stato['n_frame'], 1)
    sospensione = max(0.0, t - t_mono)
    per_frame = {k: v / n_frame for k, v in costo.items()}
    per_finestra = costo['classificatore'] / max(stato['n_decisioni'], 1)
    return {
        'parziale': bool(parziale),
        'avvio': time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(t0)),
        'aggiornato': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'durata_orologio_s': t,
        'durata_cronometro_s': t_mono,
        'sospensione_stimata_s': sospensione,
        'sospesa': bool(sospensione > 1.0),
        # Quante volte la telecamera e' sparita da sotto il processo, e per
        # quanti secondi in tutto. Vanno nel riepilogo per la stessa ragione
        # della sospensione: una sessione di dodici ore che ne ha passate
        # quattro senza immagine non e' una sessione di dodici ore, e senza
        # questi due campi lo sarebbe sembrata.
        'interruzioni_camera': stato.get('interruzioni_camera', 0),
        'secondi_persi_camera': round(
            stato.get('secondi_persi_camera', 0.0), 1),
        'fotogrammi': stato['n_frame'],
        'fps_medio': stato['n_frame'] / max(t_mono, 1e-6),
        'pose_valide': stato['n_pose'],
        'quota_pose': stato['n_pose'] / n_frame,
        'punteggio_massimo': stato['picco'],
        # Le finestre che il sistema ha SCARTATO perche' la retta del
        # pavimento non era ancora stimata. Se e' un numero grande, la
        # sessione ha visto meno di quanto la sua durata suggerisce, ed e'
        # meglio saperlo dal riepilogo che dedurlo.
        'finestre_senza_pavimento': stato.get('n_senza_pavimento', 0),
        'finestre_sopra_soglia': stato['n_sopra'],
        'allarmi': stato['n_allarmi'],
        'decisioni': stato['n_decisioni'],
        'costo_per_fotogramma_ms': {k: 1000 * v for k, v in per_frame.items()},
        'costo_totale_per_fotogramma_ms': 1000 * sum(per_frame.values()),
        'costo_classificatore_per_finestra_ms': 1000 * per_finestra,
        'verifiche_avvio': verifiche,
        'configurazione': {
            'compito': meta.get('compito'), 'feature_set': meta.get('feature_set'),
            'n_colonne': len(colonne), 'lunghezza_finestra': cfg['L'],
            'passo_finestra': cfg['passo'], 'k_integrali': meta.get('k_integrali'),
            'durata_integrali_s': meta.get('durata_integrali_s'),
            # La cadenza DAVVERO usata per dividere le derivate, contro
            # quella dichiarata nel pacchetto. Se divergono molto, le
            # derivate della sessione non sono confrontabili con quelle del
            # dataset, e ora si vede invece di doverlo dedurre.
            'fps_dichiarato': meta.get('fps_assunti'),
            'fps_usato_ultimo': stato.get('fps_usato'),
            'soglia': cfg['soglia'], 'persistenza_finestre': cfg['persistenza'],
            'sospensione_s': cfg['sospensione_regola'],
            'stimatore_posa': meta.get('stimatore_posa')},
        'nota_costo': ('I tempi sono misurati con perf_counter attorno alle '
                       'quattro fasi della catena in esercizio, non da un '
                       'banco separato: sono i tempi della stessa esecuzione '
                       'che ha prodotto gli allarmi. La strumentazione stessa '
                       'costa quattro letture di orologio per fotogramma.'),
    }


def scrivi_riepilogo(dest, dati):
    """
    Scrittura ATOMICA: file temporaneo e poi rinomina.

    Senza, un'interruzione durante la scrittura periodica lascerebbe un JSON
    troncato al posto del riepilogo precedente -- e il danno sarebbe silenzioso,
    perche' il file esiste.
    """
    tmp = dest + '.parziale'
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(dati, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, dest)


def barra(v, larghezza=34, soglia=0.5):
    n = int(round(v * larghezza))
    pieno = '#' * n + '.' * (larghezza - n)
    tick = int(round(soglia * larghezza))
    pieno = pieno[:tick] + '|' + pieno[tick:]
    colore = ROSSO if v >= soglia else (GIALLO if v >= soglia * .6 else VERDE)
    return f'{colore}[{pieno}]{FINE}'


def dispositivo(v):
    """
    La telecamera: un indice se e' un numero, altrimenti un percorso.

    Serve perche' l'indice non e' stabile fra un riavvio e l'altro, ne' fra
    uno stacca-e-riattacca del cavo, mentre `/dev/v4l/by-id/...` contiene il
    numero di serie del dispositivo e non cambia mai.
    """
    return int(v) if str(v).lstrip('-').isdigit() else str(v)


def riapri(cap, sorgente, stato, attesa=2.0, limite_s=300.0):
    """
    Riapre la telecamera sparita, e registra quanto e' durato il buco.

    Torna (cap, secondi_persi). Se dopo `limite_s` non torna, torna
    (None, secondi_persi) e il chiamante chiude la sessione.

    Il ritardo fra un tentativo e l'altro serve al kernel per ricreare il nodo
    /dev: riprovare subito fallisce sempre. Il percorso stabile
    /dev/v4l/by-id/... e' quello che rende possibile riaprire *la stessa*
    telecamera, perche' dopo una ri-enumerazione l'indice numerico e' cambiato.
    """
    import cv2
    inizio = time.time()
    try:
        cap.release()
    except Exception:
        pass
    stato['interruzioni_camera'] = stato.get('interruzioni_camera', 0) + 1
    n = stato['interruzioni_camera']
    print(f'\n  telecamera persa (interruzione n. {n}), riprovo...')

    while time.time() - inizio < limite_s:
        time.sleep(attesa)
        nuovo = cv2.VideoCapture(sorgente)
        nuovo.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        nuovo.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if nuovo.isOpened():
            ok, _ = nuovo.read()
            if ok:
                persi = time.time() - inizio
                stato['secondi_persi_camera'] = (
                    stato.get('secondi_persi_camera', 0.0) + persi)
                print(f'  telecamera tornata dopo {persi:.0f} s, riprendo')
                return nuovo, persi
        nuovo.release()

    persi = time.time() - inizio
    stato['secondi_persi_camera'] = (
        stato.get('secondi_persi_camera', 0.0) + persi)
    return None, persi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--parita', action='store_true',
                    help='esegue le tre verifiche e termina')
    ap.add_argument('--video', default=None,
                    help='cartella di fotogrammi invece della telecamera')
    ap.add_argument('--durata', type=float, default=None, help='secondi')
    # Un indice, oppure un percorso di dispositivo. L'indice NON e' stabile:
    # il 2026-09-06 la stessa telecamera e' passata da /dev/video0 a
    # /dev/video1 per un semplice stacca-e-riattacca, e una prova lunga
    # lanciata sull'indice sbagliato non parte affatto. Il percorso
    # /dev/v4l/by-id/... contiene il numero di serie e non cambia.
    # `cv2.VideoCapture` accetta entrambi: intero o stringa.
    ap.add_argument('--camera', type=dispositivo, default=0,
                    help='indice della telecamera, oppure percorso stabile '
                         'tipo /dev/v4l/by-id/usb-...-video-index0')
    ap.add_argument('--feature', default=None,
                    help='CSV su cui scrivere le TRENTADUE grandezze per ogni '
                         'fotogramma. Senza questo una sessione produce '
                         'punteggi e basta, e da un punteggio non si '
                         "riaddestra nulla: e' il motivo per cui le cadute "
                         'registrate in agosto non sono aggiungibili al '
                         'dataset. Da usare in ogni sessione di cadute')
    ap.add_argument('--clip', default=None,
                    help='cartella in cui salvare le immagini attorno a ogni '
                         'allarme: %d s prima e %d s dopo, a %d fps. Senza '
                         'questo un allarme non e\' verificabile, e non si '
                         'puo\' dire se sia stato un falso positivo o una '
                         'caduta vera: si puo\' solo dire che il sistema lo ha '
                         'generato. Le immagini restano sul dispositivo'
                         % (CLIP_PRE_S, CLIP_POST_S, CLIP_FPS))
    ap.add_argument('--registro', default=None,
                    help='file CSV su cui scrivere OGNI finestra: '
                         'istante, punteggio, sopra soglia, corsa, '
                         'allarme. Senza questo una prova lunga '
                         'produce tre numeri e nulla di ricalcolabile, '
                         'e le regole di decisione non si possono '
                         'ritarare a posteriori')
    ap.add_argument('--riepilogo', default=None,
                    help='dove scrivere il riepilogo JSON. Senza questo, '
                         'accanto al registro. Contiene la SOSPENSIONE '
                         'stimata: senza, una prova lunga puo sembrare '
                         'riuscita mentre la macchina ha dormito.')
    ap.add_argument('--riepilogo-ogni', type=float, default=RIEPILOGO_OGNI_S,
                    dest='riepilogo_ogni',
                    help='secondi fra due scritture del riepilogo durante la '
                         'sessione (0 per scriverlo solo alla fine). Una prova '
                         'lunga interrotta senza questo perde il bilancio del '
                         'costo per fase, che e il numero per cui si fa')
    ap.add_argument('--riferimento', default=None,
                    help='npz di riferimento per la parita sui fotogrammi')
    ap.add_argument('--clip-parita', default=None, dest='clip_parita',
                    help='cartella di fotogrammi per la parita sui fotogrammi')
    ap.add_argument('--salta-verifiche', action='store_true',
                    dest='salta_verifiche',
                    help='parte senza verificare. Lo stato resta scritto nel '
                         'riepilogo: una sessione non verificata resta '
                         'riconoscibile a posteriori')
    a = ap.parse_args()

    # rediretta su file, la riga di stato con \r diventa una riga sola
    # di centinaia di migliaia di caratteri: si stampa un rigo ogni
    # minuto invece del contatore continuo
    interattivo = sys.stdout.isatty()

    meta, modello, blob = carica()

    if a.parita:
        v = esegui_verifiche(meta, modello, blob, a.riferimento, a.clip_parita)
        sys.exit(stampa_verifiche(v))

    if a.salta_verifiche:
        verifiche = {'eseguite': False,
                     'motivo': 'saltate con --salta-verifiche'}
    else:
        # la parita sui fotogrammi richiede MediaPipe e una clip: si esegue
        # solo se il riferimento c'e', e in ogni caso non blocca
        verifiche = esegui_verifiche(meta, modello, blob,
                                     a.riferimento, a.clip_parita)
        if stampa_verifiche(verifiche) != 0:
            sys.exit(1)
        print()

    import cv2
    import mediapipe as mp
    from geometry import MotoreGeometrico

    colonne = meta['colonne']
    L, passo = meta['lunghezza_finestra'], meta['passo_finestra']
    soglia = meta['soglia']
    regola = meta['regola_decisione']
    # `sospensione_regola` e' il silenzio dopo un allarme, in secondi. Da non
    # confondere con la sospensione della MACCHINA calcolata a fine sessione:
    # portavano lo stesso nome, ed e' il genere di collisione che produce un
    # numero plausibile e sbagliato.
    persistenza = regola['persistenza_finestre']
    sospensione_regola = regola['sospensione_s']
    riscaldamento = meta['riscaldamento_s']
    cfg = {'L': L, 'passo': passo, 'soglia': soglia,
           'persistenza': persistenza, 'sospensione_regola': sospensione_regola}

    print('=' * 62)
    print(f'RILEVAMENTO CADUTE — compito «{meta["compito"]}»')
    print('=' * 62)
    print(f'  positivo          {meta["positivo"]}')
    print(f'  grandezze         {len(colonne)}   ({meta["feature_set"]})')
    print(f'  finestra          {meta["durata_finestra_s"]} s '
          f'({L} campioni)')
    print(f'  soglia            {soglia}')
    print(f'  allarme dopo      {persistenza} finestre consecutive, '
          f'poi {sospensione_regola:.0f} s di silenzio')
    print(f'  riscaldamento     {riscaldamento} s')
    print(f'{GRIGIO}  nessuna immagine lascia il dispositivo{FINE}')
    print()

    pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1,
                                  min_detection_confidence=0.5,
                                  min_tracking_confidence=0.5)
    motore = costruisci_motore(meta)
    buf = deque(maxlen=L)

    # L'altezza dal pavimento, se e' fra le colonne installate, impone una
    # condizione in piu' per decidere.
    #
    # `A3_h_pavimento` vale 0,0 finche' la retta del pavimento non e' stimata
    # --- servono cinquanta osservazioni di persona eretta --- e 0,0 e' anche
    # il valore di chi E' a terra. Decidere prima significa dare al modello,
    # su ogni fotogramma, la lettura piu' simile a una caduta che esista.
    #
    # In estrazione il problema non esiste: la retta si stima su TUTTA la
    # telecamera e viene poi applicata a ogni riga. Qui si accumula lungo la
    # sessione, ed e' causale. In una stanza dove nessuno attraversa in piedi
    # puo' non arrivare mai: allora la sessione non decide, e lo dichiara.
    serve_pavimento = 'A3_h_pavimento' in colonne
    if serve_pavimento:
        print(f'pavimento         richiesto: nessuna decisione prima della '
              f'stima ({MotoreGeometrico.PAV_MINIME} pose erette)')

    if a.video:
        files = sorted(f for f in os.listdir(a.video)
                       if f.lower().endswith(('.jpg', '.png', '.jpeg')))
        sorgente, n_tot = iter(files), len(files)
        print(f'sorgente: {n_tot} fotogrammi da {a.video}\n')
        cap = None
    else:
        cap = cv2.VideoCapture(a.camera)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if not cap.isOpened():
            sys.exit('telecamera non disponibile')
        print('sorgente: telecamera  —  Ctrl+C per fermare\n')

    registro = None
    if a.registro:
        registro = open(a.registro, 'w', buffering=1, encoding='utf-8')
        registro.write('t_s,punteggio,sopra,corsa,allarme\n')
        print(f'registro           {a.registro}')

    traccia_feature = None
    if a.feature:
        traccia_feature = open(a.feature, 'w', buffering=1, encoding='utf-8')
        # TUTTE E TRENTADUE, non le dodici che il modello di oggi usa.
        # Salvare solo le colonne in uso e' esattamente l'errore delle sessioni
        # di agosto: registrarono le dieci grandezze di allora, il modello
        # cambio', e quelle registrazioni sono diventate inutilizzabili --- le
        # dodici che servono adesso non ci sono, e non sono ricavabili senza i
        # fotogrammi, che non si salvano.
        # Nomi e ordine sono quelli di dataset/processed/features/feature_v2.csv
        # (colonne 8-39), cosi' che una sessione domestica si unisca al dataset
        # aggiungendo soltanto i metadati e l'etichetta.
        #
        # L'elenco si chiede a un motore USA E GETTA: chiederlo a `motore`
        # gli farebbe consumare un fotogramma vuoto, e i primi valori della
        # sessione nascerebbero con il buffer degli integrali gia' sporco.
        tutte = list(costruisci_motore(meta)
                     .fotogramma(None, None, 640, 480,
                                 meta['fps_assunti']).keys())
        traccia_feature.write('t_s,ha_posa,' + ','.join(tutte)
                              + ',hip_x,hip_y,x0,y0,x1,y1\n')
        print(f'feature           {a.feature}  ({len(tutte)} grandezze)')

    buf_clip = None
    clip_pendente = None
    if a.clip:
        os.makedirs(a.clip, exist_ok=True)
        buf_clip = BufferClip()
        print(f'clip              {a.clip}  '
              f'({CLIP_PRE_S:.0f}+{CLIP_POST_S:.0f} s a {CLIP_FPS} fps, '
              f'max {CLIP_MAX})')

    # La destinazione si calcola PRIMA del ciclo: il riepilogo va scritto anche
    # mentre la sessione e' in corso, non solo alla fine.
    dest = a.riepilogo
    if dest is None:
        dest = (os.path.splitext(a.registro)[0] + '_riepilogo.json'
                if a.registro else 'riepilogo.json')
    if a.riepilogo_ogni:
        print(f'riepilogo          {dest}   '
              f'(riscritto ogni {a.riepilogo_ogni:.0f} s)')

    # Solo leggendo una telecamera: su una cartella di fotogrammi
    # l'intervallo fra due letture e' la velocita' di elaborazione, non la
    # cadenza con cui le immagini furono riprese, e misurarla darebbe un dt
    # inventato. Li' vale il valore dichiarato, che e' anche cio' che usa la
    # prova di parita'.
    cadenza = Cadenza(meta['fps_assunti']) if cap is not None else None

    t0 = time.time()
    t0_mono = time.monotonic()
    # DUE OROLOGI. time.time() e' l'ora di sistema e avanza anche mentre la
    # macchina dorme; time.monotonic() no. La loro differenza a fine sessione
    # e' il tempo di sospensione, ed e' l'unico modo per accorgersi che il
    # dispositivo si e' addormentato: il 10 agosto una prova di durata e'
    # SEMBRATA RIUSCIRE mentre la board aveva dormito un'ora e nove minuti.
    costo = {'pre': 0.0, 'percezione': 0.0, 'post': 0.0,
             'classificatore': 0.0}
    stato = {'n_frame': 0, 'n_pose': 0, 'n_sopra': 0, 'n_allarmi': 0,
             'n_decisioni': 0, 'picco': 0.0, 'n_clip': 0,
             'n_senza_pavimento': 0}
    ultimo_rigo = 0.0
    ultimo_riepilogo = 0.0
    corsa = 0
    ultimo_allarme = -1e18

    def salva(parziale):
        scrivi_riepilogo(dest, costruisci_riepilogo(
            meta, colonne, cfg, stato, costo, t0,
            time.time() - t0, time.monotonic() - t0_mono,
            verifiche, parziale))

    try:
        while True:
            if cap is not None:
                ok, frame = cap.read()
                if not ok:
                    # La telecamera puo' sparire da sotto il processo senza
                    # che nessuno tocchi il cavo: sulla board l'autosuspend
                    # USB la fa ri-enumerare, il nodo /dev cambia numero e la
                    # lettura fallisce con "No such device". Il 2026-09-06 e'
                    # successo dopo 193 secondi e ha ucciso una prova di
                    # dodici ore al terzo minuto.
                    #
                    # Si riprova a riaprirla invece di uscire. L'interruzione
                    # NON viene nascosta: quante volte e per quanti secondi
                    # finisce nel riepilogo, perche' un'ora di buco passata
                    # sotto silenzio sarebbe peggio della prova fallita.
                    cap, persi = riapri(cap, a.camera, stato)
                    if cap is None:
                        print(f'\n  telecamera persa e non piu\' riaperta '
                              f'dopo {persi:.0f} s: sessione chiusa')
                        break
                    continue
            else:
                try:
                    frame = cv2.imread(os.path.join(a.video, next(sorgente)))
                except StopIteration:
                    break
                if frame is None:
                    continue
            stato['n_frame'] += 1
            t = time.time() - t0
            if cadenza is not None:
                cadenza.osserva(t)
            if buf_clip is not None:
                buf_clip.offri(frame, t)
            if a.durata and t > a.durata:
                break

            h, w = frame.shape[:2]
            _c = time.perf_counter()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            _p = time.perf_counter()
            costo['pre'] += _p - _c
            r = pose.process(rgb)
            _q = time.perf_counter()
            costo['percezione'] += _q - _p
            lm = r.pose_landmarks.landmark if r.pose_landmarks else None
            wl = r.pose_world_landmarks.landmark if r.pose_world_landmarks else None
            stato['n_pose'] += int(lm is not None)

            fps_ora = (cadenza.fps() if cadenza is not None
                       else meta['fps_assunti'])
            stato['fps_usato'] = fps_ora
            f = motore.fotogramma(lm, wl, w, h, fps_ora)
            buf.append([f[c] for c in colonne])
            costo['post'] += time.perf_counter() - _q

            # Le grandezze per fotogramma, se richieste.
            #
            # Senza questo file una sessione domestica NON e' riutilizzabile:
            # produce punteggi, e da un punteggio non si riaddestra niente. Le
            # sessioni di agosto registravano dieci colonne A3, e nessuna
            # delle dodici che il modello attuale usa --- che sono integrali
            # su finestra mobile, e vanno calcolati mentre la sessione gira
            # perche' a posteriori servirebbero i fotogrammi, che non si
            # salvano. Il risultato e' che quelle cadute non si possono
            # aggiungere al dataset: il dato non c'e', e non e' recuperabile.
            #
            # Con `--feature` una sessione di cadute recitate diventa
            # etichettabile e utilizzabile come qualunque altra ripresa.
            if traccia_feature is not None:
                # Le sei grandezze GREZZE, oltre alle trentadue calcolate.
                # Le sessioni di agosto le salvavano ed e' per questo che da
                # esse si ricava `h_pavimento`, che il motore della board non
                # calcola; quelle di settembre no, e infatti non lo permettono.
                # Salvandole entrambe, una sessione diventa rivalutabile con
                # QUALUNQUE configurazione --- che e' la condizione per
                # confrontarle a parita' di soglia e di regola.
                if lm is not None:
                    xs = [q.x * w for q in lm]
                    ys = [q.y * h for q in lm]
                    grezze = ((lm[23].x + lm[24].x) / 2 * w,
                              (lm[23].y + lm[24].y) / 2 * h,
                              min(xs), min(ys), max(xs), max(ys))
                else:
                    grezze = (0.0,) * 6
                traccia_feature.write(
                    '%.3f,%d,' % (t, int(lm is not None))
                    + ','.join('%.6g' % f[c] for c in tutte)
                    + ',' + ','.join('%.6g' % v for v in grezze) + '\n')

            caldo = t >= riscaldamento
            if len(buf) < L or stato['n_frame'] % passo:
                continue

            if not caldo:
                if interattivo:
                    print(f'\r{GIALLO}riscaldamento  '
                          f'{t:4.1f}/{riscaldamento:.1f} s{FINE}   ',
                          end='', flush=True)
                continue

            # `pavimento_pronto()` restituisce (pronto, n_osservazioni):
            # una tupla non vuota e' SEMPRE vera, quindi `not ...` non era mai
            # vero e il presidio non ha mai bloccato nulla. Trovato il
            # 2026-09-09 provando il visore, che sullo stesso valore e'
            # andato in errore invece di tacere.
            pav_pronto, pav_oss = motore.pavimento_pronto()
            if serve_pavimento and not pav_pronto:
                stato['n_senza_pavimento'] += 1
                if interattivo:
                    print(f'\r{GIALLO}attesa del pavimento   '
                          f'{stato["n_senza_pavimento"]:5d} finestre non '
                          f'decise{FINE}   ', end='', flush=True)
                continue

            _r = time.perf_counter()
            X = np.asarray(buf, dtype=np.float32)[None, :, :]
            p = float(modello.predict_proba(riassumi(normalizza(X, blob)))[0, 1])
            costo['classificatore'] += time.perf_counter() - _r
            stato['n_decisioni'] += 1
            stato['picco'] = max(stato['picco'], p)

            sopra = p >= soglia
            stato['n_sopra'] += sopra
            corsa = corsa + 1 if sopra else 0
            if corsa >= persistenza and (t - ultimo_allarme) >= sospensione_regola:
                ultimo_allarme = t
                stato['n_allarmi'] += 1
                nome_clip = ''
                if (buf_clip is not None and clip_pendente is None
                        and stato['n_clip'] < CLIP_MAX):
                    nome_clip = 'evt_%04d_%s' % (stato['n_allarmi'],
                                                 time.strftime('%H%M%S'))
                    clip_pendente = [t + CLIP_POST_S, buf_clip.svuota(),
                                     nome_clip]
                    stato['n_clip'] += 1
                print(f'\r{ROSSO}  *** ALLARME #{stato["n_allarmi"]} ***   '
                      f'punteggio {p:.3f}   a {t:6.1f} s{FINE}'
                      + (f'  -> {nome_clip}' if nome_clip else '')
                      + ' ' * 20)

            if registro is not None:
                registro.write(f'{t:.3f},{p:.4f},{int(sopra)},{corsa},'
                               f'{int(corsa >= persistenza and ultimo_allarme == t)}\n')

            # La clip in corso: si continua a riempirla finche' non scade,
            # poi si scrive su disco in una volta sola. Scriverla fotogramma
            # per fotogramma dentro il ciclo di decisione rallenterebbe la
            # cadenza proprio mentre sta succedendo qualcosa.
            if clip_pendente is not None:
                scadenza, fotogrammi, nome = clip_pendente
                if t <= scadenza:
                    if (not fotogrammi
                            or t - fotogrammi[-1][0] >= 1.0 / CLIP_FPS):
                        fotogrammi.append((t, frame.copy()))
                else:
                    d = os.path.join(a.clip, nome)
                    os.makedirs(d, exist_ok=True)
                    for i, (tt, fr) in enumerate(fotogrammi):
                        cv2.imwrite(os.path.join(d, '%03d_%.2f.jpg' % (i, tt)),
                                    fr, [cv2.IMWRITE_JPEG_QUALITY, CLIP_QUALITA])
                    clip_pendente = None

            # Il riepilogo parziale: la prova lunga diventa incrementale
            # invece che tutto-o-niente.
            if a.riepilogo_ogni and (t - ultimo_riepilogo) >= a.riepilogo_ogni:
                ultimo_riepilogo = t
                salva(parziale=True)

            fps = stato['n_frame'] / max(t, 1e-6)
            if interattivo:
                print(f'\r{barra(p, soglia=soglia)} {p:5.3f}   '
                      f'{fps:4.1f} fps   '
                      f'pose {100*stato["n_pose"]/stato["n_frame"]:3.0f}%   '
                      f'allarmi {stato["n_allarmi"]}  '
                      f'(finestre sopra {stato["n_sopra"]})   ',
                      end='', flush=True)
            elif t - ultimo_rigo >= 60:
                ultimo_rigo = t
                print(f'{t/60:7.1f} min   {fps:4.1f} fps   '
                      f'pose {100*stato["n_pose"]/stato["n_frame"]:3.0f}%   '
                      f'picco {stato["picco"]:.3f}   '
                      f'allarmi {stato["n_allarmi"]}   '
                      f'(finestre sopra {stato["n_sopra"]})', flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        # La clip ancora in sospeso va scritta comunque. Senza questo si perde
        # l'ultimo allarme di ogni sessione --- quello piu' vicino alla fine,
        # che su una prova interrotta a mano e' spesso proprio quello che si
        # voleva guardare. Trovato provando il registratore su una clip di
        # 9,7 s con la finestra di coda a 10: due allarmi, zero immagini.
        if clip_pendente is not None and a.clip:
            try:
                import cv2 as _cv
                _, fotogrammi, nome = clip_pendente
                d = os.path.join(a.clip, nome)
                os.makedirs(d, exist_ok=True)
                for i, (tt, fr) in enumerate(fotogrammi):
                    _cv.imwrite(os.path.join(d, '%03d_%.2f.jpg' % (i, tt)), fr,
                                [_cv.IMWRITE_JPEG_QUALITY, CLIP_QUALITA])
                print(f'clip {nome} chiusa alla fine della sessione '
                      f'({len(fotogrammi)} immagini)')
            except Exception as e:
                print(f'{ROSSO}clip non scritta: {e}{FINE}')
        if cap is not None:
            cap.release()
        if registro is not None:
            registro.close()
        # anche su interruzione: il riepilogo di una sessione fermata a mano
        # vale quanto quello di una conclusa
        try:
            salva(parziale=False)
        except Exception as e:
            print(f'\n{ROSSO}riepilogo non scritto: {e}{FINE}')

    t = time.time() - t0
    t_mono = time.monotonic() - t0_mono
    # La differenza fra i due orologi E' il tempo in cui la macchina ha
    # dormito. Va calcolata sempre, non solo quando si sospetta: il difetto
    # del 10 agosto non ha prodotto un errore, ha prodotto una sessione che
    # sembrava riuscita.
    fuori = costruisci_riepilogo(meta, colonne, cfg, stato, costo, t0, t,
                                 t_mono, verifiche, parziale=False)
    sospensione = fuori['sospensione_stimata_s']
    per_frame = fuori['costo_per_fotogramma_ms']
    totale_frame = fuori['costo_totale_per_fotogramma_ms']

    print()
    print('=' * 62)
    print('  durata (orologio)    %.1f s' % t)
    print('  durata (cronometro)  %.1f s' % t_mono)
    if sospensione > 1.0:
        print('  %sSOSPENSIONE STIMATA  %.1f s  (%.1f min)%s'
              % (ROSSO, sospensione, sospensione / 60, FINE))
        print('  %sLa macchina ha dormito: la sessione NON e\' valida come'
              ' prova di durata.%s' % (ROSSO, FINE))
    else:
        print('  sospensione          nessuna')
    print('  fotogrammi           %s   (%.1f fps)'
          % ('{:,}'.format(stato['n_frame']), fuori['fps_medio']))
    print('  pose valide          %.1f%%' % (100 * fuori['quota_pose']))
    print('  punteggio massimo    %.3f' % stato['picco'])
    print()
    print('  BILANCIO PER FOTOGRAMMA')
    for k in ('pre', 'percezione', 'post', 'classificatore'):
        quota = 100 * per_frame[k] / max(totale_frame, 1e-12)
        print('    %-16s %7.2f ms   %5.1f%%' % (k, per_frame[k], quota))
    print('    %-16s %7.2f ms' % ('totale', totale_frame))
    print('    classificatore per FINESTRA: %.2f ms  (una ogni %d fotogrammi)'
          % (fuori['costo_classificatore_per_finestra_ms'], passo))
    print()
    print('  finestre sopra soglia   %d' % stato['n_sopra'])
    print('  ALLARMI emessi          %d' % stato['n_allarmi'])
    if stato['n_allarmi']:
        print('  fattore                 %.1fx'
              % (stato['n_sopra'] / stato['n_allarmi']))
    if t_mono > 60:
        print('  allarmi/ora             %.2f'
              % (stato['n_allarmi'] / (t_mono / 3600)))
        print('%s  riferimento letteratura: 0,049 eventi/ora%s' % (GRIGIO, FINE))

    scrivi_riepilogo(dest, fuori)
    print()
    print('  riepilogo scritto in %s' % dest)


if __name__ == '__main__':
    main()
