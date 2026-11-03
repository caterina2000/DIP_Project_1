# Le tre figure delle rappresentazioni: testo pronto da incollare

Per la Sezione «Rappresentazioni geometriche del movimento» del Capitolo 3.
Tre figure separate, una per sottosezione, più la versione affiancata se
servisse.

I file stanno in `tesi/figure/`:

| file | dove va |
|---|---|
| `fig_rappr_a1.png` | dentro `\subsection{A1...}` |
| `fig_rappr_a2.png` | dentro `\subsection{A2...}` |
| `fig_rappr_a3.png` | dentro `\subsection{A3...}` |
| `fig_rappresentazioni.png` | alternativa: i tre pannelli affiancati |

Tutte prodotte da `pipeline/figura_rappresentazioni.py`, che richiede
MediaPipe e quindi l'ambiente `fall_processing`.

---

## Perché tre figure separate e non una

Il paragrafo che apre la sezione dice che le tre rappresentazioni sono «tre
modi diversi di trasformare la stessa posa», e quella frase spinge verso una
figura comparativa unica. Ma le tre sottosezioni sono lunghe: mettendo una
figura sola in testa, chi legge A3 ha la figura tre pagine sopra.

**Con tre figure separate** ciascuna sta accanto al testo che la spiega, e la
comparazione resta comunque leggibile perché **il fotogramma è lo stesso in
tutte e tre**. Basta dirlo una volta, nella prima didascalia.

La versione affiancata resta disponibile se in impaginazione le tre singole
risultassero troppo piccole.

---

## Frase da aggiungere nel paragrafo di apertura

Subito dopo «Sono tre modi diversi di trasformare la stessa posa in feature
numeriche e costituiscono l'insieme di partenza...»:

```latex
Le Figure~\ref{fig:rappr-a1}, \ref{fig:rappr-a2} e~\ref{fig:rappr-a3} mostrano
le tre costruzioni sullo \emph{stesso} fotogramma, in modo che la differenza
fra loro non dipenda dalla posa scelta. In grigio chiaro la posa stimata da
MediaPipe; cerchiati in rosso i \emph{landmark} che ciascuna rappresentazione
impiega.
```

---

## A1 — la sagoma come ellisse

```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=.52\textwidth]{figure/fig_rappr_a1.png}
\caption{A1 sui sette \emph{landmark} impiegati --- naso, spalle, anche e
caviglie. L'ellisse è quella definita dagli autovettori della matrice di
covarianza dei sette punti: l'asse maggiore ne dà l'orientamento dominante,
l'asse minore la dispersione ortogonale. Nessuna delle relazioni anatomiche
che collegano i punti viene utilizzata.}
\label{fig:rappr-a1}
\end{figure}
```

**Dove metterla:** dopo il paragrafo che finisce con «...quanto la
configurazione appaia allungata o compressa», prima dell'elenco delle
grandezze estratte.

**Frase da aggiungere nel testo**, in coda al paragrafo sull'ellisse:

```latex
La Figura~\ref{fig:rappr-a1} mostra la costruzione su una caduta in corso: i
sette punti sono distribuiti lungo una direzione dominante, e l'ellisse che li
riassume risulta inclinata e allungata.
```

---

## A2 — il tronco nello spazio

```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=.52\textwidth]{figure/fig_rappr_a2.png}
\caption{A2 sui cinque \emph{landmark} impiegati --- naso, spalle e anche. La
freccia è il vettore del tronco, dal punto medio delle anche a quello delle
spalle; la crocetta segna l'origine del riferimento. La linea tratteggiata è
la verticale del riferimento dei \emph{world landmark}, rispetto alla quale
l'angolo viene misurato: \textbf{non} è la verticale della stanza.}
\label{fig:rappr-a2}
\end{figure}
```

**Dove metterla:** dopo l'elenco delle feature di base, accanto al paragrafo
che spiega il sistema di riferimento.

**Frase da aggiungere**, in coda al paragrafo «Tuttavia, i \emph{world
landmark} devono essere interpretati in modo corretto...»:

```latex
La Figura~\ref{fig:rappr-a2} rende esplicita questa differenza: la verticale
tratteggiata rispetto a cui l'angolo è misurato appartiene al riferimento del
corpo, e non coincide con la direzione della gravità nella scena.
```

> **Nota.** Il disegno è necessariamente una proiezione: A2 lavora in tre
> dimensioni, la figura è sul piano dell'immagine. Vale la pena dirlo in
> didascalia se il relatore ci fa caso — è il limite della rappresentazione
> grafica, non della rappresentazione geometrica.

---

## A3 — riferita alla geometria del corpo

```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=.52\textwidth]{figure/fig_rappr_a3.png}
\caption{A3 sui nove \emph{landmark} impiegati --- naso, spalle, anche,
ginocchia e caviglie. La crocetta è l'origine del riferimento locale, posta
nel centro del bacino, e il segmento che sale verso le spalle è la lunghezza
del tronco, che normalizza tutte le altre grandezze. Le tre quote a sinistra
sono le altezze relative di testa, ginocchia e caviglie rispetto al bacino,
espresse in lunghezze di tronco e quindi adimensionali.}
\label{fig:rappr-a3}
\end{figure}
```

**Dove metterla:** dopo l'elenco delle grandezze, accanto al paragrafo sulla
normalizzazione.

**Frase da aggiungere**, in coda al paragrafo «Le distanze e le velocità
vengono espresse rispetto alla lunghezza del tronco...»:

```latex
Nella Figura~\ref{fig:rappr-a3} il segmento del tronco è l'unità di misura di
tutte le quote riportate a sinistra: raddoppiando la distanza dalla telecamera
raddoppierebbero sia le quote sia il segmento, e i loro rapporti resterebbero
invariati.
```

---

## Se preferisci la figura unica

```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{figure/fig_rappresentazioni.png}
\caption{Le tre rappresentazioni sullo stesso fotogramma. A sinistra A1, con
l'ellisse e i suoi due assi; al centro A2, con il vettore del tronco e
l'origine sul bacino; a destra A3, con la lunghezza del tronco come unità di
misura e le altezze relative. In grigio chiaro la posa stimata da MediaPipe,
cerchiati in rosso i \emph{landmark} che ciascuna rappresentazione impiega:
sette, cinque e nove.}
\label{fig:rappresentazioni}
\end{figure}
```

In questo caso va in testa alla sezione, subito dopo il paragrafo di apertura,
e le tre sottosezioni la richiamano con `\ref{fig:rappresentazioni}`.

---

## Due cose da sapere sulla figura

**Il fotogramma è lo stesso in tutte e tre**, ed è scelto e fissato nel codice
(`RIPRESA` e `FOTOGRAMMA` in testa allo script), non ricavato da un criterio
automatico. Il criterio automatico --- massima inclinazione del tronco ---
restituisce la persona già distesa a terra, dove le costruzioni ci sono ma non
si leggono. Il fotogramma attuale è stato scelto confrontando un candidato per
ripresa su sei soggetti: qui la persona occupa il 55% dell'altezza
dell'inquadratura ed è a metà caduta.

**La posa è calcolata in sequenza, non sul fotogramma isolato.** Lo stimatore è
un tracciatore: la posa che restituisce su un'immagine singola non è quella che
otterrebbe seguendo il movimento, ed è quest'ultima che il sistema usa in
esercizio. Se in didascalia serve una riga sola, è questa:

> *Ripresa elaborata in sequenza; la posa mostrata è quella che lo stimatore
> produce seguendo il movimento, non quella ricavabile dal fotogramma isolato.*

---

## Per cambiare fotogramma

```
conda activate fall_processing
python pipeline/figura_rappresentazioni.py --provini      # foglio a contatto
python pipeline/figura_rappresentazioni.py --fotogramma 31
python pipeline/figura_rappresentazioni.py --ripresa <cartella> --fotogramma 20
```

Il foglio a contatto finisce in `tesi/figure/_provini_rappresentazioni.png` e
**non è una figura della tesi**: va cancellato prima della consegna, o tenuto
fuori da quella cartella.


---

## `fig_striscia.png` — una caduta, quattro istanti, due grandezze

Va nella sezione sulle **grandezze integrali** del Capitolo 3, dove il testo
sostiene che le derivate istantanee sono dominate dal rumore e che le
grandezze accumulate le sostituiscono.

```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{figure/fig_striscia.png}
\caption{Una caduta di UP-Fall seguita nel tempo. In alto quattro istanti con
la posa stimata da MediaPipe, tutti con lo stesso ritaglio: (a) prima della
caduta, (b) durante la transizione, (c) all'arrivo a terra, (d) a terra e
ferma. In basso l'andamento di due grandezze sullo stesso asse dei tempi,
ciascuna normalizzata al proprio massimo: la velocità del bacino, che è una
derivata istantanea, e la discesa del bacino, che è un integrale su finestra
mobile. Le linee tratteggiate segnano i quattro istanti.}
\label{fig:striscia}
\end{figure}
```

**Frase da aggiungere nel testo**, dove introduci le grandezze integrali:

```latex
La Figura~\ref{fig:striscia} mostra il contrasto su una caduta singola. La
derivata istantanea produce un picco isolato a $1{,}45$~s, mentre la persona
sta ancora camminando, e torna a zero non appena il corpo si ferma: è alta
quando il corpo si muove, non quando sta cadendo. La grandezza integrale sale
con continuità fino alla transizione e vi \emph{resta} per tutto il tempo in
cui la persona è a terra, decadendo solo quando la finestra di accumulazione
esce dall'evento.
```

**La cosa che vale la pena dire, e che non è nel testo attuale:** l'argomento
per gli integrali nel capitolo è che sono meno rumorosi. La figura mostra che
hanno anche **memoria** — restano alti mentre lo stato dura. È la ragione per
cui il compito «stato» e il compito «evento» si comportano in modo diverso, e
per cui gli integrali aiutano sul campo, dove il positivo dura minuti.

Se vuoi usarla anche nel Capitolo 4, accanto al confronto fra rappresentazioni,
basta richiamarla: è la stessa figura, non serve rigenerarla.

**Per rifarla su un'altra caduta:**

```
conda activate fall_processing
python pipeline/figura_striscia.py --ripresa <cartella> --istanti 18,29,38,54
```

Senza `--istanti` li sceglie da sé attorno al fotogramma in cui l'angolo del
tronco cambia più in fretta.
