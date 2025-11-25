"""Entry point del bot Telegram (webhook)."""

from __future__ import annotations

import asyncio
import logging

from telegram import Update
from telegram.ext import Application, ApplicationBuilder

from bot.config import load_settings
from bot.db import Base, engine
from bot.handlers import register_handlers


async def _setup_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _on_startup(app: Application) -> None:
    await _setup_db()


async def _on_shutdown(app: Application) -> None:  # pragma: no cover
    # Qui potresti chiudere connessioni, pool, ecc.
    pass


async def main() -> None:
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

    # Avvio in modalità webhook
    await application.run_webhook(
        listen=settings.webhook.host,
        port=settings.webhook.port,
        url_path=settings.webhook.path.lstrip("/"),
        webhook_url=settings.webhook.url,
        secret_token=settings.webhook.secret,
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    asyncio.run(main())
