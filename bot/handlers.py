"""Handler del bot (comandi ed errori)."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .auth import is_admin
from .message_view import update_view

logger = logging.getLogger(__name__)


# === COMANDI PRINCIPALI ======================================================


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler per /start: messaggio breve in inglese, con vista header+body.

    - Cancella il messaggio /start dell'utente.
    - Aggiorna header: '> /start'
    - Aggiorna body: '✅ Bot is running correctly.'
    """
    if not update.effective_user or not update.effective_chat:
        return

    await update_view(
        update,
        context,
        command_label="/start",
        body_text="✅ Bot is running correctly.",
    )


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mostra SOLO l'ID numerico dell'utente come body."""
    if not update.effective_user or not update.effective_chat:
        return

    user_id = update.effective_user.id

    await update_view(
        update,
        context,
        command_label="/myid",
        body_text=str(user_id),
    )


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando disponibile solo agli admin configurati in ADMIN_IDS.

    - Se non admin -> body: '❌ Access denied.'
    - Se admin -> body: '🛠 You have admin privileges.'
    """
    if not update.effective_user or not update.effective_chat:
        return

    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update_view(
            update,
            context,
            command_label="/admin",
            body_text="❌ Access denied.",
        )
        return

    await update_view(
        update,
        context,
        command_label="/admin",
        body_text="🛠 You have admin privileges.",
    )


# === HANDLER GENERICO DI CLEANUP ============================================


async def cleanup_other(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancella qualsiasi altro messaggio dell'utente (testo, media, ecc.).

    Non aggiorna header/body: la vista rimane quella dell'ultimo comando valido.
    """
    message = update.effective_message
    if not message:
        return

    try:
        await message.delete()
    except Exception as exc:  # noqa: BLE001
        logger.debug("Failed to delete non-command message: %s", exc)


# === ERROR HANDLER ===========================================================


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Logga l'errore senza far crashare il bot.

    Qui lasciamo che l'errore sia comunicato con un messaggio separato
    (eventi rari). Se volessimo, potremmo anche qui usare update_view
    per rispettare la stessa logica di trasformazione.
    """
    logger.exception("Exception while handling an update: %s", context.error)

    if isinstance(update, Update) and update.effective_chat:
        try:
            await update.effective_chat.send_message(
                "An unexpected error occurred. Please try again later."
            )
        except Exception:  # pragma: no cover
            logger.exception("Failed to send error message to user")


# === REGISTRAZIONE HANDLER ===================================================


def register_handlers(app: Application) -> None:
    """Registra tutti gli handler dell'applicazione."""

    # Comandi espliciti
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("admin", admin))

    # Qualsiasi altro messaggio (testo, foto, documenti, sticker, ecc.) viene solo cancellato
    app.add_handler(MessageHandler(filters.ALL, cleanup_other))

    # Error handler globale
    app.add_error_handler(error_handler)
