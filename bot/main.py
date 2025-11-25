"""Entry point del bot Telegram (webhook)."""

from __future__ import annotations

import logging

from telegram.ext import Application, ApplicationBuilder

from bot.config import load_settings
from bot.db import Base, engine
from bot.handlers import register_handlers


async def _setup_db(application: Application) -> None:
    """Crea le tabelle al bootstrap dell'applicazione."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _on_startup(application: Application) -> None:
    """Hook eseguito dopo l'inizializzazione dell'app."""
    await _setup_db(application)


async def _on_shutdown(application: Application) -> None:  # pragma: no cover
    """Hook eseguito in fase di shutdown."""
    # Qui potresti chiudere connessioni, pool, ecc.
    # Esempio (se vuoi essere super pulito):
    # await engine.dispose()
    pass


def main() -> None:
    """Funzione principale SINCRONA.

    Non usare asyncio.run qui, perché run_webhook gestisce da solo
    l'event loop internamente.
    """
    settings = load_settings()

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    application = (
        ApplicationBuilder()
        .token(settings.bot_token)
        .post_init(_on_startup)
        .post_shutdown(_on_shutdown)
        .build()
    )

    register_handlers(application)

    # Avvio in modalità webhook (bloccante, gestisce il suo event loop)
    application.run_webhook(
        listen=settings.webhook.host,
        port=settings.webhook.port,
        url_path=settings.webhook.path.lstrip("/"),
        webhook_url=settings.webhook.url,
        secret_token=settings.webhook.secret,
        drop_pending_updates=True,
        # allowed_updates=["message", "callback_query"],  # opzionale
    )


if __name__ == "__main__":
    main()
