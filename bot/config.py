from __future__ import annotations

from dataclasses import dataclass
import os

"""Configurazione centrale del bot.

Tutta la configurazione del bot viene letta da variabili d'ambiente.

Quando distribuisci con Portainer (Stack), imposta queste variabili
nel file di stack e **non** modificare i valori qui nel codice.
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

    @property
    def database_url(self) -> str:
        """Costruisce la database URL per SQLAlchemy con asyncpg."""

        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


def load_config() -> BotConfig:
    """Carica la configurazione dalle variabili d'ambiente.

    In caso di distribuzione tramite Portainer, tutte queste variabili
    vanno impostate nello stack YAML o nel file `.env` referenziato.
    """

    token = os.getenv("BOT_TOKEN", "")
    if not token:
        raise RuntimeError("BOT_TOKEN non impostata nelle variabili d'ambiente.")

    return BotConfig(
        token=token,
        db_host=os.getenv("DB_HOST", "db"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_name=os.getenv("DB_NAME", "telegram_bot"),
        db_user=os.getenv("DB_USER", "telegram"),
        db_password=os.getenv("DB_PASSWORD", "telegram"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
