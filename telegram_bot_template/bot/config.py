from __future__ import annotations

from dataclasses import dataclass
import os


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
    """Carica la configurazione dalle variabili d'ambiente."""

    token = os.getenv("BOT_TOKEN", "")

    return BotConfig(
        token=token,
        db_host=os.getenv("DB_HOST", "db"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_name=os.getenv("DB_NAME", "telegram_bot"),
        db_user=os.getenv("DB_USER", "telegram"),
        db_password=os.getenv("DB_PASSWORD", "telegram"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
