# Telegram Bot Template

Questo progetto è un template minimale per un bot Telegram scritto in **Python**, progettato per girare in un **container Docker** e usare **PostgreSQL** tramite **SQLAlchemy** e **asyncpg**.

È pensato per essere distribuito tramite **Portainer** usando la funzione **Stacks → Repository Git**.

🔑 **Principio chiave:** tutte le variabili di configurazione (token, DB, credenziali, log, ecc.) vengono impostate **solo nel file `.env`**. Non è necessario (né consigliato) modificare `docker-compose.yml` o il codice Python per cambiare configurazione.

## Tecnologie principali

- Python 3.12
- `python-telegram-bot[http2] >= 21.0.0`
- `SQLAlchemy >= 2.0`
- `asyncpg >= 0.29`
- Docker / Portainer
- PostgreSQL

## Struttura del progetto

```text
.
├── docker-compose.yml   # Stack Docker/Portainer, NON modificare le variabili qui
├── Dockerfile
├── requirements.txt
├── .env                  # UNICO file dove cambi le variabili
└── bot
    ├── __init__.py
    ├── config.py
    ├── main.py
    ├── db
    │   ├── __init__.py
    │   ├── base.py
    │   └── models.py
    └── handlers
        ├── __init__.py
        ├── start.py
        └── errors.py
```

## Configurazione tramite `.env`

Tutte le variabili usate da Postgres e dal bot vengono definite qui.

```env
# Token del bot Telegram
BOT_TOKEN=your_bot_token_here

# Configurazione database PostgreSQL
DB_HOST=db
DB_PORT=5432
DB_NAME=telegram_bot
DB_USER=telegram
DB_PASSWORD=telegram

# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO
```

Per cambiare token, nome DB, utente o password, **modifica solo questo file** e fai push sul repository Git.

## docker-compose.yml (stack per Portainer)

Lo stack usa il file `.env` sia per:

- passare le variabili ai container,
- risolvere i valori `POSTGRES_*` tramite sostituzione `${VAR}`.

```yaml
version: "3.9"

services:
  db:
    image: postgres:16-alpine
    container_name: telegram_bot_db
    env_file:
      - .env
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  bot:
    build: .
    container_name: telegram_bot_app
    env_file:
      - .env
    depends_on:
      - db
    restart: unless-stopped

volumes:
  postgres_data:
```

In questo file **non è necessario modificare nulla** per cambiare la configurazione.

## Distribuzione con Portainer (Repository Git)

1. Crea una repository Git con dentro:
   - `docker-compose.yml`
   - `.env`
   - la cartella `bot/` e il resto del codice.
2. In Portainer: **Stacks → Add stack → Repository**.
3. Inserisci l'URL del repository, branch e path (se necessario).
4. Deploy dello stack.

Quando vorrai aggiornare variabili (token, DB, ecc.):

1. Modifica **solo** il file `.env` nel repository.
2. `git commit && git push`.
3. Aggiorna/re-deploy lo stack da Portainer (o usa auto-update se configurato).

## Comportamento del codice

- `bot/config.py` legge tutte le variabili con `os.getenv(...)` (`BOT_TOKEN`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `LOG_LEVEL`).
- `bot/main.py` non contiene alcun valore di configurazione hardcoded.

In altre parole: una volta impostato il template, **non dovrai più entrare nei file Python per cambiare la configurazione**, ma solo nello `.env`.
