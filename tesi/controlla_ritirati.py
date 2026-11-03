# -*- coding: utf-8 -*-
"""
Cerca nei sorgenti della tesi i numeri che non devono piu' comparire.

Perche' esiste
--------------
`docs/NUMERI_PER_LA_TESI.txt` ha una sezione «NUMERI CHE NON DEVONO PIU
COMPARIRE»: valori di campagne superate, o misure di una macchina attribuite a
un'altra. Sono rientrati nel testo piu' di una volta, perche' vengono ricopiati
da una versione all'altra e a occhio sembrano plausibili.

Questo script li cerca. Segnala anche i contesti LEGITTIMI --- un numero
ritirato puo' comparire se il testo lo sta dichiarando tale --- lasciando la
decisione a chi legge: stampa la riga, e chi controlla vede subito se e' un
uso o una dichiarazione.

Uso
---
    python tesi/controlla_ritirati.py
"""
import io
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))

# (espressione, che cosa vale invece, dove il valore giusto e' documentato)
RITIRATI = [
    (r'26,5\s*~?\s*fps',
     '7,3 fps', 'la catena accelerata su banco, non quella installata'),
    (r'4,47\s*~?\s*ms',
     '4,85 ms sul calcolatore, 39,04 sulla board',
     'era una misura del calcolatore attribuita alla board'),
    (r'\b47,8\b',
     '44,8', 'il fattore fra finestre ed eventi, su 14,98 ore e nove sessioni'),
    (r'14\s+e\s+125',
     '14 e 156', 'e sono FINESTRE positive, non allarmi'),
    (r'\b0,4\s*allarmi\b|\b0,4/ora\b',
     '0,049/ora di Kangas', 'nessuna fonte produce lo 0,4'),
    (r'\b3,778\b',
     '3,865 s', 'la scomposizione della latenza, ricalcolata'),
    (r'\b0,038\s*s\b',
     '0,125 s', 'il calcolo per fotogramma, misurato sul dispositivo'),
    (r'superiore a settanta',
     'un rapporto di ventidue', 'fra riempimento della finestra e calcolo'),
]

# frasi che rendono legittima la presenza di un numero ritirato
# Un numero ritirato puo' comparire legittimamente in due casi: quando il testo
# lo sta DICHIARANDO superato, e quando e' vero ma riferito a un altro oggetto
# --- i 26,5 fps sono la frequenza reale della catena accelerata su banco, e
# sono sbagliati solo se attribuiti al sistema installato.
SCUSANTI = ('ritirat', 'non deve', 'una versione precedente', 'precedentemente',
            'riportava invece', 'era una misura', 'quel numero',
            'acceleratore', 'accelerata', 'quella catena', 'yolov8', 'npu',
            'a sistema', 'non si conclude', 'non trova riscontro')


def main():
    file = sorted(f for f in os.listdir(QUI)
                  if f.endswith('.tex') and not f.startswith('archiv'))
    trovati, dichiarati = [], []

    for nome in file:
        with io.open(os.path.join(QUI, nome), encoding='utf-8',
                     errors='replace') as f:
            righe = f.read().split('\n')
        for i, riga in enumerate(righe, 1):
            basso = riga.lower()
            for pattern, giusto, perche in RITIRATI:
                if re.search(pattern, riga):
                    voce = (nome, i, pattern, giusto, perche, riga.strip())
                    if any(s in basso for s in SCUSANTI):
                        dichiarati.append(voce)
                    else:
                        trovati.append(voce)

    print('=' * 74)
    print('NUMERI RITIRATI NEI SORGENTI DELLA TESI')
    print('=' * 74)

    if dichiarati:
        print('\nDichiarati come superati, quindi leciti (%d):' % len(dichiarati))
        for nome, i, _, _, _, riga in dichiarati:
            print('   %s:%d  %s' % (nome, i, riga[:76]))

    if not trovati:
        print('\nNessun uso da correggere.')
        return 0

    print('\nDA CORREGGERE (%d):' % len(trovati))
    for nome, i, _, giusto, perche, riga in trovati:
        print('\n   %s:%d' % (nome, i))
        print('      %s' % riga[:96])
        print('      -> %s   (%s)' % (giusto, perche))
    return 1


if __name__ == '__main__':
    sys.exit(main())
