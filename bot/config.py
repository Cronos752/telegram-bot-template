"""Configurazione centrale del bot.

Tutta la configurazione viene letta da variabili d'ambiente (.env).

Quando distribuisci con Portainer (Stack), imposta queste variabili
nel file `.env` e **non** modificare i valori qui nel codice.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
import os
from typing import Final


@dataclass(slots=True)
class WebhookConfig:
    """Configurazione del webhook Telegram."""

    url: str
    host: str
    port: int
    path: str
    secret: str | None


@dataclass(slots=True)
class DbConfig:
    """Configurazione di connessione al database PostgreSQL."""

    host: str
    port: int
    name: str
    user: str
    password: str


@dataclass(slots=True)
class Settings:
    """Configurazione completa del bot."""

    bot_token: str
    log_level: str
    webhook: WebhookConfig
    db: DbConfig
    admin_ids: list[int]


_LOGGER: Final = logging.getLogger(__name__)


def _get_env(name: str, default: str | None = None, *, required: bool = False) -> str:
    """Legge una variabile d'ambiente.

    Se `required` è True e la variabile non è presente o vuota,
    solleva RuntimeError (fail-fast).
    """

    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value or ""


def _parse_admin_ids(raw: str | None) -> list[int]:
    """Parsa ADMIN_IDS in una lista di interi.

    Esempio: "123,456,789" -> [123, 456, 789]
    """
    if not raw:
        return []
    result: list[int] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            result.append(int(part))
        except ValueError:
            _LOGGER.warning("ADMIN_IDS contiene un valore non valido: %r", part)
    return result


def load_settings() -> Settings:
    """Carica la configurazione dal processo (variabili d'ambiente).

    Se mancano variabili obbligatorie solleva RuntimeError.
    Esegue anche alcune validazioni base e scrive warning a log.
    """

    # --- BOT TOKEN ---
    bot_token = _get_env("BOT_TOKEN", required=True).strip()
    if not bot_token:
        raise RuntimeError("BOT_TOKEN non può essere vuoto")
    if ":" not in bot_token:
        _LOGGER.warning(
            "BOT_TOKEN non sembra avere il formato tipico '<id>:<hash>'",
        )

    # --- LOG LEVEL ---
    log_level = _get_env("LOG_LEVEL", "INFO").upper()
    valid_levels = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
    if log_level not in valid_levels:
        _LOGGER.warning("LOG_LEVEL %r non valido, uso 'INFO' come default", log_level)
        log_level = "INFO"

    # --- WEBHOOK ---
    webhook_url = _get_env("WEBHOOK_URL", required=True).strip()
    if not (webhook_url.startswith("http://") or webhook_url.startswith("https://")):
        _LOGGER.warning(
            "WEBHOOK_URL %r non inizia con 'http://' o 'https://'", webhook_url,
        )

    webhook_host = _get_env("WEBHOOK_HOST", "0.0.0.0").strip() or "0.0.0.0"

    try:
        webhook_port = int(_get_env("WEBHOOK_PORT", "8080"))
    except ValueError as exc:
        raise RuntimeError("WEBHOOK_PORT deve essere un intero") from exc

    webhook_path = _get_env("WEBHOOK_PATH", "/telegram-bot/webhook").strip()
    # Normalizza il path per assicurare che inizi con '/'
    if not webhook_path.startswith("/"):
        webhook_path = "/" + webhook_path

    webhook_secret = _get_env("WEBHOOK_SECRET", "", required=False).strip() or None

    # --- DB ---
    try:
        db_port = int(_get_env("DB_PORT", "5432"))
    except ValueError as exc:
        raise RuntimeError("DB_PORT deve essere un intero") from exc

    db = DbConfig(
        host=_get_env("DB_HOST", "postgre-sql"),
        port=db_port,
        name=_get_env("DB_NAME", "telegram_bot_db"),
        user=_get_env("DB_USER", "telegram_bot_user"),
        password=_get_env("DB_PASSWORD", "telegram_bot_password"),
    )

    webhook = WebhookConfig(
        url=webhook_url,
        host=webhook_host,
        port=webhook_port,
        path=webhook_path,
        secret=webhook_secret,
    )

    # --- ADMIN IDS ---
    raw_admin_ids = os.getenv("ADMIN_IDS", "")
    admin_ids = _parse_admin_ids(raw_admin_ids)

    settings = Settings(
        bot_token=bot_token,
        log_level=log_level,
        webhook=webhook,
        db=db,
        admin_ids=admin_ids,
    )

    # Log di riepilogo (senza segreti)
    _LOGGER.info(
        "Configurazione caricata: db_host=%s db_name=%s webhook_url=%s log_level=%s admin_count=%d",
        settings.db.host,
        settings.db.name,
        settings.webhook.url,
        settings.log_level,
        len(settings.admin_ids),
    )

    return settings
