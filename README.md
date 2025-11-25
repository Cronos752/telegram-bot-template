# Telegram Bot Template

Questo progetto è un template minimale per un bot Telegram scritto in **Python**, progettato per girare in un **container Docker** e usare **PostgreSQL** tramite **SQLAlchemy** e **asyncpg**.

È pensato per essere distribuito facilmente tramite **Portainer** usando la funzione **Stacks**, senza bisogno di file `.env` in produzione: tutte le variabili vengono impostate direttamente nello stack YAML.

## Tecnologie principali

- Python 3.12
- `python-telegram-bot[http2] >= 21.0.0`
- `SQLAlchemy >= 2.0`
- `asyncpg >= 0.29`
- Docker (Docker Engine / Portainer)
- PostgreSQL

## Struttura del progetto

```text
.
├── docker-compose.yml   # Può essere usato come stack YAML in Portainer
├── Dockerfile
├── requirements.txt
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

## Distribuzione tramite Portainer (Stacks)

1. Apri Portainer → **Stacks** → **Add stack**.
2. Copia e incolla il contenuto di `docker-compose.yml` nel form YAML.
3. Modifica SOLO i valori delle variabili nella sezione `environment:` secondo le tue esigenze, ad esempio:

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: mio_utente
      POSTGRES_PASSWORD: mia_password
      POSTGRES_DB: mio_database

  bot:
    build: .
    environment:
      BOT_TOKEN: "123456:ABC-DEF..."  # Token reale del bot
      DB_HOST: db
      DB_PORT: "5432"
      DB_NAME: mio_database
      DB_USER: mio_utente
      DB_PASSWORD: mia_password
      LOG_LEVEL: INFO
```

> ✅ **Importante:** non devi modificare il codice Python per cambiare nome DB, password, utente, ecc. Basta aggiornare questi valori nello stack di Portainer.

4. Fai **Deploy the stack**.

Portainer creerà i due servizi:

- `db` → container PostgreSQL configurato con le variabili `POSTGRES_*`.
- `bot` → container con il bot Telegram che legge le variabili `BOT_TOKEN`, `DB_*`, `LOG_LEVEL`.

## Esecuzione locale opzionale

Se vuoi, puoi anche eseguire il progetto in locale con Docker Compose:

```bash
docker-compose up --build
```

In questo caso userai le variabili già presenti nel `docker-compose.yml`.

## Prossimi passi

- Aggiungere nuovi handler dentro `bot/handlers/`.
- Definire nuovi modelli SQLAlchemy in `bot/db/models.py`.
- Integrare eventualmente un sistema di migrazioni (es. Alembic).
