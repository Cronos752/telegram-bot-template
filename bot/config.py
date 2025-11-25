from __future__ import annotations

from dataclasses import dataclass
import os

"""Configurazione centrale del bot.

Tutta la configurazione del bot viene letta da variabili d'ambiente.

Quando distribuisci con Portainer (Stack), imposta queste variabili
nel file `.env` e **non** modificare i valori qui nel codice.
"""


@dataclass
class BotConfig:
    token: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    log_level: str = "INFO"

    # Webhook
    webhook_url: str | None = None
    webhook_host: str = "0.0.0.0"
    webhook_port: int = 8080
    webhook_path: str = "/webhook"
    webhook_secret_token: str | None = None

    @property
    def database_url(self) -> str:
        """Costruisce la database URL per SQLAlchemy con asyncpg."""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


def load_config() -> BotConfig:
    """Carica la configurazione dalle variabili d'ambiente."""

    token = os.getenv("BOT_TOKEN", "")
    if not token:
        raise RuntimeError("BOT_TOKEN non impostata nelle variabili d'ambiente.")

    webhook_url = os.getenv("WEBHOOK_URL")
    webhook_host = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    webhook_port = int(os.getenv("WEBHOOK_PORT", "8080"))
    webhook_path = os.getenv("WEBHOOK_PATH", "/webhook")
    webhook_secret = os.getenv("WEBHOOK_SECRET") or None

    return BotConfig(
        token=token,
        db_host=os.getenv("DB_HOST", "postgre-sql"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_name=os.getenv("DB_NAME", "telegram_bot"),
        db_user=os.getenv("DB_USER", "telegram"),
        db_password=os.getenv("DB_PASSWORD", "telegram"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        webhook_url=webhook_url,
        webhook_host=webhook_host,
        webhook_port=webhook_port,
        webhook_path=webhook_path,
        webhook_secret_token=webhook_secret,
    )
