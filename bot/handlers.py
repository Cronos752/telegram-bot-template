"""Handler del bot (comandi ed errori)."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from .auth import is_admin

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler per /start: messaggio breve in inglese."""
    if not update.effective_user or not update.effective_chat:
        return

    await update.effective_chat.send_message(
        "✅ Bot is running correctly."
    )


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mostra SOLO l'ID numerico dell'utente (nessun testo extra)."""
    if not update.effective_user or not update.effective_chat:
        return

    user_id = update.effective_user.id
    # solo il numero, senza testo
    await update.effective_chat.send_message(str(user_id))


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando disponibile solo agli admin configurati in ADMIN_IDS."""
    if not update.effective_user or not update.effective_chat:
        return

    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.effective_chat.send_message("❌ Access denied.")
        return

    # Qui potrai aggiungere la vera logica admin (pannello, statistiche, ecc.)
    await update.effective_chat.send_message(
        "🛠 You have admin privileges."
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Logga l'errore senza far crashare il bot."""

    logger.exception("Exception while handling an update: %s", context.error)

    if isinstance(update, Update) and update.effective_chat:
        try:
            await update.effective_chat.send_message(
                "An unexpected error occurred. Please try again later."
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
