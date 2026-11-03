# Le prove

    python prove/esegui.py

Trentuno prove, due secondi, nessuna dipendenza oltre numpy e pandas: usano
`unittest` della libreria standard e girano in tutti e tre gli ambienti conda
del progetto senza installare niente.

## Perche' esistono queste tre e non altre

Coprono i soli punti in cui un errore **non produce un'eccezione ma un numero
sbagliato**. Il resto del codice, se si rompe, si ferma; questi tre no.

| prova | protegge | l'errore che eviterebbe |
|---|---|---|
| `prova_geometria` | le trentadue grandezze | una modifica al motore geometrico cambia **ogni numero della tesi** senza segnalare nulla |
| `prova_etichettatura` | la regola K-su-M | sposta il confine fra positivo e negativo, e quindi tutte le metriche |
| `prova_eventi` | l'aggregazione in eventi | e' il fattore **47,8** fra finestre sopra soglia ed eventi, gia' costato una volta |

## Il file d'oro

`prova_geometria` tiene una copia dei valori attesi in
`dati/geometria_attesa.npz`: quaranta fotogrammi sintetici, trentadue
grandezze. Non dice che i valori siano *giusti* --- dice che sono **gli stessi
su cui la tesi e' stata scritta**.

I landmark di ingresso sono costruiti analiticamente e non vengono da
MediaPipe: una figura che si inclina fino a terra. Cosi' la prova e'
deterministica su qualunque macchina e gira anche dove MediaPipe non e'
installato.

Se una modifica al motore e' voluta:

    python prove/prova_geometria.py --aggiorna

e **si registra in CHANGELOG perche'**. Un file d'oro rigenerato senza una
ragione scritta e' un file d'oro inutile.

## Che cosa NON coprono

L'addestramento, il trasferimento all'archivio esterno e la catena sulla
board. Quelli si verificano eseguendoli, e il loro esito sta in
`docs/EXPERIMENTS.md`. Le verifiche della board stanno altrove ancora, in
`deploy_board/rileva.py --parita`, perche' devono girare sul dispositivo.
