# Telegram Bot Template

Questo progetto è un template minimale per un bot Telegram scritto in **Python**, progettato per girare in un **container Docker** e usare **PostgreSQL** tramite **SQLAlchemy** e **asyncpg**.

## Tecnologie principali

- Python 3.12
- [python-telegram-bot](https://python-telegram-bot.org/) `python-telegram-bot[http2] >= 21.0.0`
- [SQLAlchemy](https://www.sqlalchemy.org/) `SQLAlchemy >= 2.0`
- [asyncpg](https://github.com/MagicStack/asyncpg) `asyncpg >= 0.29`
- Docker + docker-compose
- PostgreSQL

## Struttura del progetto

```text
.
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
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

## Setup rapido

1. Copia il file `.env.example` in `.env` e imposta il token del bot e i parametri del DB.
2. Avvia docker-compose:

```bash
docker-compose up --build
```

Il servizio `db` avvierà PostgreSQL, mentre il servizio `bot` costruirà l'immagine Docker del bot e lo farà partire.

## Prossimi passi

- Aggiungere nuovi handler dentro `bot/handlers/`
- Definire nuovi modelli SQLAlchemy in `bot/db/models.py`
- Integrare eventualmente un sistema di migrazioni (es. Alembic)
