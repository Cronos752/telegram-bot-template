"""Handler del bot (comandi ed errori)."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from .auth import is_admin

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler semplice per /start."""
    if not update.effective_user or not update.effective_chat:
        return

    first_name = update.effective_user.first_name or "lì"
    await update.effective_chat.send_message(
        f"Ciao {first_name}! Il bot è attivo."
    )


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mostra l'ID Telegram dell'utente, utile per configurare ADMIN_IDS."""
    if not update.effective_user or not update.effective_chat:
        return

    user_id = update.effective_user.id
    text = f"Il tuo ID Telegram è:\n`{user_id}`"
    await update.effective_chat.send_message(text, parse_mode="Markdown")


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando disponibile solo agli admin configurati in ADMIN_IDS."""
    if not update.effective_user or not update.effective_chat:
        return

    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.effective_chat.send_message("❌ Non sei autorizzato a usare questo comando.")
        return

    # Qui ci metterai la vera logica admin
    await update.effective_chat.send_message("✅ Sei admin! Qui andranno i comandi amministratore.")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Logga l'errore senza far crashare il bot."""

    logger.exception("Exception while handling an update: %s", context.error)

    if isinstance(update, Update) and update.effective_chat:
        try:
            await update.effective_chat.send_message(
                "Si è verificato un errore inatteso. Riprova più tardi."
            )
        except Exception:  # pragma: no cover
            logger.exception("Failed to send error message to user")


def register_handlers(app: Application) -> None:
    """Registra tutti gli handler dell'applicazione."""

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("admin", admin))

    # Error handler globale
    app.add_error_handler(error_handler)
