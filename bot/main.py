from __future__ import annotations

import logging
import sys

from telegram.ext import Application

from .config import load_config
from .db import init_engine
from .handlers import setup_handlers
from .handlers.errors import error_handler


logger = logging.getLogger(__name__)


def main() -> None:
    """Entry point principale del bot."""

    config = load_config()

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        stream=sys.stdout,
    )

    logger.info("Starting Telegram bot template …")

    # Inizializza il DB (engine + sessionmaker globale)
    init_engine(config)

    # Crea l'application di python-telegram-bot
    application = (
        Application.builder()
        .token(config.token)
        .build()
    )

    # Registra gli handler
    setup_handlers(application)

    # Handler globale per gli errori
    application.add_error_handler(error_handler)

    # Avvio in modalità webhook (bloccante)
    application.run_webhook(
        listen=config.webhook_host,
        port=config.webhook_port,
        url_path=config.webhook_path.lstrip("/"),
        webhook_url=config.webhook_url,
        secret_token=config.webhook_secret_token,
    )



if __name__ == "__main__":
    main()
