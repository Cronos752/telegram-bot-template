# Telegram Bot Template (variant 1 - compact package)

Template di bot Telegram in Python 3.12 con struttura compatta:

- `bot/config.py`    → lettura configurazione da `.env`
- `bot/db.py`        → SQLAlchemy async + modello `User`
- `bot/handlers.py`  → handler `/start` + error handler globale
- `bot/main.py`      → crea l'Application e avvia il webhook

Il bot usa:
- python-telegram-bot (webhook + http2)
- SQLAlchemy async
- asyncpg
- Docker + docker-compose
- PostgreSQL esterno (container `postgre-sql` esistente)

## Configurazione

1. Crea/compila il file `.env` nella root del progetto:
   - `BOT_TOKEN`
   - parametri `DB_*`
   - parametri `WEBHOOK_*`
   - `LOG_LEVEL`

2. Deploy da Portainer:
   - Stack → Git repository con questo progetto
   - Il servizio `bot` usa:
     - network esterna `nginx_network`
     - network esterna `postgre_sql_network`
     - container PostgreSQL esistente `postgre-sql`

3. Il bot parte **solo in modalità webhook**:
   - ascolta su `WEBHOOK_HOST:WEBHOOK_PORT` dentro il container
   - espone la route HTTP `WEBHOOK_PATH`
   - registra il webhook su `WEBHOOK_URL`
