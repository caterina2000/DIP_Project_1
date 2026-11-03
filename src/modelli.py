"""
Le architetture da confrontare, dietro un'interfaccia unica.

Perche' un'interfaccia unica
---------------------------
La domanda della tesi e' se una GRU su un dispositivo da cento euro regga il
confronto con architetture piu' pesanti. Una domanda del genere si risponde
solo se i modelli ricevono ESATTAMENTE lo stesso trattamento: stesse finestre,
stesso scaler, stessi fold, stessa regola di arresto, stessa scelta della
soglia. Se ognuno avesse il suo ciclo di addestramento, ogni differenza
misurata potrebbe venire dal ciclo invece che dall'architettura.

Qui ogni modello espone tre cose e nient'altro:

    .addestra(X, y, X_val, y_val, pesi)   -> se stesso
    .probabilita(X)                       -> (n, n_classi)
    .n_parametri                          -> intero

Chi le usa non sa se dietro c'e' Keras o scikit-learn.

Il numero di parametri non e' un dettaglio decorativo: e' la grandezza che
rende confrontabile «funziona meglio» con «ci sta sul dispositivo», ed e' meta'
della domanda di tesi. Va riportato accanto a ogni metrica.

Due o tre classi
----------------
`n_classi` vale 2 o 3 a seconda del modo di etichettatura. Cambia solo
l'ultimo strato: tutto il resto dell'architettura e' identico, altrimenti il
confronto fra modi misurerebbe anche una differenza di capacita'.

L'uscita e' SEMPRE softmax su `n_classi` colonne, anche nel caso binario dove
un singolo sigmoide basterebbe. Cosi' `valutazione.probabilita_allarme` riceve
sempre la stessa forma e la riduzione a probabilita' di allarme e' una sola
riga per tutti.

L'arresto anticipato
--------------------
Si sorveglia l'AUC sulla probabilita' di ALLARME, non la perdita ne'
l'accuratezza. La ragione e' che la soglia viene scelta DOPO, sul validation:
cio' che serve dall'addestramento non e' un modello che decide bene a 0,5, ma
un modello che ORDINA bene le finestre. L'AUC misura esattamente quello, ed e'
definita allo stesso modo per due e tre classi una volta ridotta l'uscita a
`1 - p(normale)`.

Con una classe positiva al 15% l'accuratezza premierebbe un modello che dice
sempre «normale», e la perdita con pesi di classe e' interpretabile ma non
misura l'ordinamento.
"""

from typing import Dict, Optional, Sequence

import numpy as np

import config

ARCHITETTURE = ('gru', 'lstm', 'cnn', 'transformer', 'grafo', 'foresta')


# ============================================================
# PESI DI CLASSE
# ============================================================
def pesi_classe(y: np.ndarray, n_classi: int) -> Dict[int, float]:
    """
    Peso inversamente proporzionale alla frequenza, normalizzato a media 1.

    Serve perche' le classi sono molto sbilanciate -- la caduta vera e' il
    4,8% dei fotogrammi -- e senza pesi la discesa del gradiente trova un
    minimo comodo dicendo sempre «normale».

    La normalizzazione a media 1 mantiene la perdita sulla stessa scala fra
    modi con due e tre classi, che altrimenti non sarebbero confrontabili.
    """
    y = np.asarray(y).astype(int)
    conteggi = np.array([max((y == c).sum(), 1) for c in range(n_classi)],
                        dtype=np.float64)
    p = len(y) / (n_classi * conteggi)
    return {c: float(v) for c, v in enumerate(p / p.mean())}


# ============================================================
# METRICA DI ORDINAMENTO
# ============================================================
def _auc_allarme(n_classi: int):
    """
    AUC calcolata su `1 - p(classe 0)`, cioe' sulla stessa quantita' che in
    esercizio decide se suonare. Definita identica per 2 e 3 classi.
    """
    import tensorflow as tf
    from tensorflow import keras

    class AUCAllarme(keras.metrics.AUC):
        def __init__(self, **kw):
            super().__init__(name='auc_allarme', **kw)

        def update_state(self, y_vero, y_prev, sample_weight=None):
            # y_vero arriva come indice di classe: allarme = classe != 0
            v = tf.cast(tf.not_equal(tf.cast(tf.reshape(y_vero, [-1]),
                                             tf.int32), 0), tf.float32)
            p = 1.0 - y_prev[:, 0]
            return super().update_state(v, p, sample_weight)

    return AUCAllarme()


# ============================================================
# MODELLI KERAS
# ============================================================
class ModelloKeras:
    """Involucro comune: costruzione, addestramento, probabilita'."""

    def __init__(self, nome: str, forma, n_classi: int, seme: Optional[int] = None,
                 **kw):
        self.nome = nome
        self.forma = tuple(forma)          # (lunghezza_finestra, n_feature)
        self.n_classi = int(n_classi)
        self.seme = config.SEME if seme is None else seme
        self.kw = kw
        self._m = None
        self.storia = None

    # ---- costruzione ----
    def _corpo(self, x, keras):
        raise NotImplementedError

    def costruisci(self):
        import tensorflow as tf
        from tensorflow import keras
        tf.keras.utils.set_random_seed(self.seme)

        ing = keras.Input(shape=self.forma, name='finestra')
        x = self._corpo(ing, keras)
        usc = keras.layers.Dense(self.n_classi, activation='softmax',
                                 name='uscita')(x)
        m = keras.Model(ing, usc, name=self.nome)
        m.compile(
            optimizer=keras.optimizers.Adam(config.LEARNING_RATE),
            loss='sparse_categorical_crossentropy',
            metrics=[_auc_allarme(self.n_classi)],
        )
        self._m = m
        return self

    # ---- addestramento ----
    def addestra(self, X, y, X_val=None, y_val=None, pesi=None,
                 epoche=None, batch=None, verboso=0):
        from tensorflow import keras
        if self._m is None:
            self.costruisci()

        richiami = []
        dati_val = None
        if X_val is not None and len(X_val):
            dati_val = (X_val, y_val)
            richiami.append(keras.callbacks.EarlyStopping(
                monitor='val_auc_allarme', mode='max', patience=8,
                restore_best_weights=True, verbose=0))
            richiami.append(keras.callbacks.ReduceLROnPlateau(
                monitor='val_auc_allarme', mode='max', factor=0.5,
                patience=4, min_lr=1e-5, verbose=0))

        self.storia = self._m.fit(
            X, y,
            validation_data=dati_val,
            epochs=epoche or config.EPOCHE,
            batch_size=batch or config.BATCH,
            class_weight=pesi if pesi is not None else pesi_classe(y, self.n_classi),
            callbacks=richiami,
            shuffle=True,
            verbose=verboso,
        ).history
        return self

    # ---- uso ----
    def probabilita(self, X) -> np.ndarray:
        if self._m is None:
            raise RuntimeError('modello non addestrato')
        if len(X) == 0:
            return np.zeros((0, self.n_classi))
        return self._m.predict(X, verbose=0)

    @property
    def n_parametri(self) -> int:
        if self._m is None:
            self.costruisci()
        return int(self._m.count_params())


class GRU(ModelloKeras):
    """
    Il modello di riferimento della tesi.

    Due strati ricorrenti: il primo restituisce la sequenza, il secondo la
    riassume. La GRU ha tre porte contro le quattro della LSTM, quindi circa
    un quarto di parametri in meno a parita' di unita' -- ed e' la ragione per
    cui e' il candidato naturale su un dispositivo da cento euro.
    """

    def _corpo(self, x, keras):
        u = self.kw.get('unita', 64)
        drop = self.kw.get('dropout', 0.3)
        x = keras.layers.GRU(u, return_sequences=True)(x)
        x = keras.layers.Dropout(drop)(x)
        x = keras.layers.GRU(max(u // 2, 8))(x)
        x = keras.layers.Dropout(drop)(x)
        return x


class LSTM(ModelloKeras):
    """Identica alla GRU salvo il tipo di cella: e' il confronto piu' pulito."""

    def _corpo(self, x, keras):
        u = self.kw.get('unita', 64)
        drop = self.kw.get('dropout', 0.3)
        x = keras.layers.LSTM(u, return_sequences=True)(x)
        x = keras.layers.Dropout(drop)(x)
        x = keras.layers.LSTM(max(u // 2, 8))(x)
        x = keras.layers.Dropout(drop)(x)
        return x


class CNN(ModelloKeras):
    """
    Convoluzioni monodimensionali sul tempo.

    Non ha memoria: vede solo cio' che entra nel campo recettivo, che con due
    strati a nucleo 5 copre 9 campioni su 22. E' un limite dichiarato, non un
    difetto dell'implementazione -- serve a misurare quanto la ricorrenza
    conti davvero su finestre di 2,4 s.
    """

    def _corpo(self, x, keras):
        f = self.kw.get('filtri', 64)
        drop = self.kw.get('dropout', 0.3)
        for n in (f, f * 2):
            x = keras.layers.Conv1D(n, 5, padding='same', activation='relu')(x)
            x = keras.layers.BatchNormalization()(x)
            x = keras.layers.MaxPooling1D(2)(x)
            x = keras.layers.Dropout(drop)(x)
        return keras.layers.GlobalAveragePooling1D()(x)


class Transformer(ModelloKeras):
    """
    Un blocco di auto-attenzione con codifica posizionale imparata.

    Uno solo, non sei: con poche migliaia di finestre e dieci soggetti un
    modello piu' profondo memorizzerebbe. Il confronto e' comunque
    informativo, ma va letto per quello che e' -- un Transformer piccolo su
    dati piccoli, non lo stato dell'arte.
    """

    def _corpo(self, x, keras):
        import tensorflow as tf
        d = self.kw.get('d_modello', 64)
        teste = self.kw.get('teste', 4)
        drop = self.kw.get('dropout', 0.2)

        x = keras.layers.Dense(d)(x)
        pos = keras.layers.Embedding(self.forma[0], d)(
            tf.range(self.forma[0]))
        x = x + pos

        a = keras.layers.MultiHeadAttention(teste, d // teste, dropout=drop)(x, x)
        x = keras.layers.LayerNormalization(epsilon=1e-6)(x + a)
        f = keras.layers.Dense(d * 2, activation='relu')(x)
        f = keras.layers.Dropout(drop)(f)
        f = keras.layers.Dense(d)(f)
        x = keras.layers.LayerNormalization(epsilon=1e-6)(x + f)
        return keras.layers.GlobalAveragePooling1D()(x)


def _strato_adiacenza():
    """
    Restituisce lo strato che mescola i nodi del grafo.

    E' definito dentro una funzione, e non a livello di modulo, per la stessa
    ragione di `_auc_allarme`: importare TensorFlow all'importazione di questo
    file renderebbe impossibile usarlo dagli script che non ce l'hanno.

    L'adiacenza e' APPRESA e non fissata, ed e' una scelta obbligata: su un
    grafo di giunti l'adiacenza e' l'anatomia, qui i nodi sono grandezze
    geometriche e non esiste un'adiacenza data. Ricavarla dalla correlazione
    misurata sui dati porrebbe la domanda di su quali dati -- e stimarla su
    tutto sarebbe leakage. Una matrice appresa non stima nulla dall'esterno del
    fold, e la variante e' quella dei lavori con adiacenza adattiva.

    La softmax sulle righe fa si' che ogni nodo distribuisca un peso totale
    unitario sui vicini: senza normalizzazione la scala delle attivazioni
    dipenderebbe dal numero di nodi.
    """
    import tensorflow as tf
    from tensorflow import keras

    class Adiacenza(keras.layers.Layer):
        def build(self, forma_ingresso):
            n = int(forma_ingresso[2])
            self.A = self.add_weight(
                shape=(n, n), initializer='glorot_uniform',
                trainable=True, name='adiacenza')
            super().build(forma_ingresso)

        def call(self, x):
            return tf.einsum('btnc,nm->btmc', x, tf.nn.softmax(self.A, axis=-1))

    return Adiacenza


class Grafo(ModelloKeras):
    """
    Rete a grafo spazio-temporale sulle grandezze.

    CHE COS'E', E CHE COSA NON E'
    -----------------------------
    E' la famiglia che la tesi dichiarava di non aver provato. La struttura e'
    quella di una ST-GCN: si alternano una convoluzione SPAZIALE, che mescola
    i nodi secondo l'adiacenza, e una convoluzione TEMPORALE, che guarda una
    finestra di fotogrammi sullo stesso nodo.

    NON e' una GCN sullo scheletro. I nodi qui sono le dodici grandezze
    geometriche in ingresso, non i giunti del corpo: l'ingresso e' lo stesso
    delle altre cinque architetture, ed e' l'unico modo perche' il confronto
    misuri l'ARCHITETTURA e non la rappresentazione. Una GCN sui giunti
    richiederebbe le coordinate grezze dei landmark, che questo CSV non
    contiene -- andrebbero riestratte -- e cambierebbe insieme architettura e
    ingresso, cioe' due variabili invece di una.

    Va detto anche il limite che ne segue: con dodici nodi che non hanno una
    struttura anatomica, il vantaggio tipico di una rete a grafo -- sfruttare
    una topologia nota -- non c'e'. Cio' che resta e' il meccanismo: mescolare
    esplicitamente i canali con pesi appresi prima di guardare il tempo.
    """

    def _corpo(self, x, keras):
        canali = self.kw.get('canali', 32)
        nucleo = self.kw.get('nucleo_tempo', 5)
        blocchi = self.kw.get('blocchi', 2)
        drop = self.kw.get('dropout', 0.3)

        L, N = self.forma           # (lunghezza_finestra, n_grandezze)
        Adiacenza = _strato_adiacenza()

        # (B, L, N) -> (B, L, N, 1): ogni grandezza diventa un nodo con un canale
        h = keras.layers.Reshape((L, N, 1))(x)
        for _ in range(blocchi):
            h = Adiacenza()(h)                                   # spaziale
            h = keras.layers.Conv2D(canali, (1, 1), activation='relu')(h)
            h = keras.layers.BatchNormalization()(h)
            h = keras.layers.Conv2D(canali, (nucleo, 1), padding='same',
                                    activation='relu')(h)        # temporale
            h = keras.layers.BatchNormalization()(h)
            h = keras.layers.Dropout(drop)(h)
        return keras.layers.GlobalAveragePooling2D()(h)


# ============================================================
# FORESTA CASUALE
# ============================================================
class Foresta:
    """
    La linea di riferimento non profonda, e il modello effettivamente
    schierato sulla board nella versione precedente del lavoro.

    Non accetta sequenze, quindi la finestra va riassunta. Il riassunto e'
    dichiarato ed e' lo stesso per tutte le colonne: media, deviazione
    standard, minimo, massimo, primo e ultimo campione. Sei numeri per
    grandezza. Il primo e l'ultimo ci sono perche' senza di loro la foresta
    non saprebbe in che VERSO e' andato il movimento, e una caduta e un
    rialzarsi darebbero lo stesso riassunto.
    """

    def __init__(self, nome='foresta', n_classi=2, seme=None, **kw):
        self.nome = nome
        self.n_classi = int(n_classi)
        self.seme = config.SEME if seme is None else seme
        self.kw = kw
        self._m = None

    # Il riassunto e' un parametro, non una costante, perche' e' proprio la
    # variabile dell'esperimento sul ruolo degli integrali: `estremi=False`
    # toglie primo e ultimo campione e con essi l'ultima traccia di ordine
    # temporale che il riassunto conserva.
    @staticmethod
    def riassumi(X: np.ndarray, estremi: bool = True) -> np.ndarray:
        if len(X) == 0:
            return np.zeros((0, 0))
        pezzi = [X.mean(1), X.std(1), X.min(1), X.max(1)]
        if estremi:
            pezzi += [X[:, 0, :], X[:, -1, :]]
        return np.concatenate(pezzi, axis=1)

    def addestra(self, X, y, X_val=None, y_val=None, pesi=None, **kw):
        from sklearn.ensemble import RandomForestClassifier
        self._m = RandomForestClassifier(
            n_estimators=self.kw.get('n_alberi', config.N_ALBERI),
            max_depth=self.kw.get('profondita', None),
            class_weight='balanced',
            random_state=self.seme,
            n_jobs=-1,
        ).fit(self.riassumi(X, self.kw.get('estremi', True)),
              np.asarray(y).astype(int))
        return self

    def probabilita(self, X) -> np.ndarray:
        if self._m is None:
            raise RuntimeError('modello non addestrato')
        if len(X) == 0:
            return np.zeros((0, self.n_classi))
        p = self._m.predict_proba(
            self.riassumi(X, self.kw.get('estremi', True)))
        # Se una classe non compare nell'addestramento del fold, sklearn
        # restituisce meno colonne. Si reimpagina sulle classi attese,
        # altrimenti probabilita_allarme leggerebbe la colonna sbagliata.
        if p.shape[1] != self.n_classi:
            pieno = np.zeros((len(p), self.n_classi))
            for i, c in enumerate(self._m.classes_):
                pieno[:, int(c)] = p[:, i]
            p = pieno
        return p

    @property
    def n_parametri(self) -> int:
        """Numero totale di nodi negli alberi: il posto che occupa in memoria."""
        if self._m is None:
            return 0
        return int(sum(t.tree_.node_count for t in self._m.estimators_))


# ============================================================
# FABBRICA
# ============================================================
_CLASSI = {'gru': GRU, 'lstm': LSTM, 'cnn': CNN,
           'transformer': Transformer, 'grafo': Grafo, 'foresta': Foresta}


def costruisci(architettura: str, forma, n_classi: int, **kw):
    """
    `forma` e' (lunghezza_finestra, n_feature). La foresta la ignora, ma la
    riceve lo stesso: chi chiama non deve sapere quale modello sta creando.
    """
    a = architettura.lower()
    if a not in _CLASSI:
        raise ValueError(f'architettura sconosciuta: {architettura!r} '
                         f'(attese: {", ".join(ARCHITETTURE)})')
    if a == 'foresta':
        return Foresta(nome=a, n_classi=n_classi, **kw)
    return _CLASSI[a](nome=a, forma=forma, n_classi=n_classi, **kw)
