"""Entry point del bot Telegram (webhook)."""

from __future__ import annotations

import logging

from telegram import (
    BotCommand,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeChat,
)
from telegram.ext import Application, ApplicationBuilder

from .config import load_settings
from .db import Base, engine
from .handlers import register_handlers


async def _setup_db(application: Application) -> None:
    """Crea le tabelle al bootstrap dell'applicazione."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _setup_bot_commands(application: Application) -> None:
    """Imposta i comandi visibili nel menu di Telegram.

    - Tutti vedono: /start, /myid
    - Gli admin (ADMIN_IDS) vedono anche: /admin
      tramite scope per-chat (chat privata = ID utente).
    """
    settings = application.bot_data.get("settings")
    if settings is None:
        settings = load_settings()

    base_commands = [
        BotCommand("start", "🚀 Start the bot"),
        BotCommand("myid", "🆔 Show your Telegram ID"),
    ]

    # Comandi per tutti gli utenti nelle chat private
    await application.bot.set_my_commands(
        base_commands,
        scope=BotCommandScopeAllPrivateChats(),
    )

    # Comandi specifici per ciascun admin (override a livello di chat privata)
    admin_commands = base_commands + [
        BotCommand("admin", "🛠 Admin commands"),
    ]

    for admin_id in settings.admin_ids:
        # Nelle chat private chat_id == user_id
        await application.bot.set_my_commands(
            admin_commands,
            scope=BotCommandScopeChat(chat_id=admin_id),
        )


async def _on_startup(application: Application) -> None:
    """Hook eseguito dopo l'inizializzazione dell'app."""
    await _setup_db(application)
    await _setup_bot_commands(application)


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

    # Rendo disponibile settings nello state dell'application
    application.bot_data["settings"] = settings

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
