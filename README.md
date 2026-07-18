# Docker Sensore – Python + Redis + API Flask con Docker Compose

Mini-progetto didattico per imparare Docker e Docker Compose partendo da un caso realistico:

- un **sensore** simulato in Python che genera letture di temperatura e umidità,
- un **database Redis** che memorizza le letture,
- una **API Flask** che espone le letture via HTTP su `localhost:8000`.

Il tutto orchestrato con Docker Compose in un unico comando.

---

## Architettura

Stack a 3 servizi:

- `sensore`  
  - Container Python che genera una lettura ogni 2 secondi.  
  - Scrive le letture:
    - su file di log montato sull’host,
    - in Redis (ultima lettura + storico).

- `redis`  
  - Istanza Redis basata sull’immagine ufficiale `redis`.  
  - Dati persistenti su volume Docker nominato (`redis_data`).  
  - Abilitata persistenza `appendonly`.

- `api`  
  - API REST minimale in Flask.  
  - Legge da Redis e fornisce gli endpoint:
    - `GET /` – health-check
    - `GET /last-reading` – ultima lettura
    - `GET /history` – ultime 10 letture

I container comunicano tra loro tramite la rete interna di Docker Compose, usando il nome del servizio (`redis`) come hostname.

---

## Struttura del progetto

```text
docker-sensore/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── sensor.py        # generatore letture (producer)
└── api.py           # API Flask (consumer)
```

---

## Prerequisiti

- Docker Desktop (con backend WSL2 su Windows)
- Docker Compose v2 (`docker compose` integrato in Docker Desktop)
- (Windows) Cartella host per i log: `C:\log-sensore`

---

## Configurazione dei log sull’host

Per salvare i log del sensore su Windows (e non perderli quando i container vengono fermati):

```powershell
mkdir C:\log-sensore
```

Questa cartella viene montata nel container sotto `/app/log` tramite bind mount definito in `docker-compose.yml`.

---

## Avvio dello stack

Dalla cartella del progetto:

```bash
docker compose up -d --build
```

Questo comando:

1. builda l’immagine Python a partire dal `Dockerfile`,
2. avvia i servizi `redis`, `sensore`, `api` in background,
3. crea (se necessario) il volume Docker per Redis.

Verifica che i servizi siano attivi:

```bash
docker compose ps
```

Dovresti vedere:

- `redis-sensore` (Up)
- `sensore-compose` (Up)
- `api-sensore` (Up, port 8000)

---

## Endpoint API

Una volta avviato lo stack:

### Health-check

```bash
curl http://localhost:8000/
```

Risposta attesa (test semplice):

```text
API sensore attiva
```

### Ultima lettura

```bash
curl http://localhost:8000/last-reading
```

Esempio di risposta:

```json
{
  "ultima_lettura": "[2026-07-18T13:23:17] Temp: 16.11 °C  Umidità: 37.91%"
}
```

### Storico letture (ultime 10)

```bash
curl http://localhost:8000/history
```

Esempio di risposta:

```json
{
  "storico_letture": [
    "[2026-07-18T13:23:17] Temp: 16.11 °C  Umidità: 37.91%",
    "[2026-07-18T13:23:15] Temp: 17.02 °C  Umidità: 41.23%",
    ...
  ]
}
```

---

## Verifica log su filesystem host

Dopo qualche secondo che il sensore gira:

```powershell
cd C:\log-sensore
type sensore.log
```

Vedrai una riga ogni ~2 secondi, simile a:

```text
[2026-07-18T13:23:17] Temp: 16.11 °C  Umidità: 37.91%
[2026-07-18T13:23:19] Temp: 18.02 °C  Umidità: 42.10%
...
```

---

## Verifica diretta dentro Redis

Puoi entrare nella CLI Redis sul container:

```bash
docker exec -it redis-sensore redis-cli
```

Comandi utili:

```text
GET ultima_lettura
LRANGE storico_letture 0 5
exit
```

- `GET ultima_lettura` – mostra l’ultima stringa scritta dal sensore.
- `LRANGE storico_letture 0 5` – mostra le ultime 6 letture in ordine inverso (lista Redis).

---

## Comandi Docker/Compose utili

### Log in streaming

Log di tutti i servizi:

```bash
docker compose logs -f
```

Solo API:

```bash
docker compose logs -f api
```

Solo sensore:

```bash
docker compose logs -f sensore
```

### Stop / cleanup

Ferma i container senza rimuoverli:

```bash
docker compose stop
```

Ferma e rimuove container e rete Compose:

```bash
docker compose down
```

Ferma, rimuove e cancella anche i volumi definiti nel file:

```bash
docker compose down -v
```

> Attenzione: il volume `redis_data` verrà eliminato, e con lui i dati Redis.

---

## Dettagli implementativi

### `sensor.py`

- genera una lettura ogni 2 secondi (temperatura e umidità random),
- stampa la lettura a console,
- appende la riga al file `log/sensore.log` (bind mount sull’host),
- scrive in Redis:
  - chiave stringa `ultima_lettura`,
  - lista `storico_letture` tramite `LPUSH`.

### `api.py`

API Flask minimale:

- `/` – health-check testuale
- `/last-reading` – legge `ultima_lettura` da Redis e la restituisce in JSON
- `/history` – legge le ultime 10 voci da `storico_letture` e le restituisce in JSON

Gestisce alcuni retry sulla connessione Redis in fase di avvio.

### `docker-compose.yml`

- crea automaticamente una rete interna dove i container si vedono per nome di servizio (`redis`);
- monta:
  - un volume nominato `redis_data` per i dati Redis,
  - un bind mount `C:\log-sensore:/app/log` per i log del sensore su Windows;
- espone:
  - `6379:6379` per eventuali test da host verso Redis,
  - `8000:8000` per l’API HTTP.

---

## Possibili estensioni

Idee per sviluppi futuri:

- Aggiungere una piccola **UI web** (HTML/JS) che chiama `/last-reading` e visualizza i dati in tempo reale.
- Aggiungere un database relazionale (es. PostgreSQL) e salvare anche i dati storici su DB.
- Introdurre variabili d’ambiente per configurare intervallo di lettura, soglie di allarme, ecc.
- Creare test automatici per API e sensore.

