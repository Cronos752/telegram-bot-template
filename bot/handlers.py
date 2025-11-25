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
from .message_view import update_dashboard

logger = logging.getLogger(__name__)


# === COMANDI PRINCIPALI ======================================================


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler per /start: messaggio breve in inglese su dashboard.

    - Cancella il messaggio /start dell'utente.
    - Dashboard (unico messaggio visibile):
        Last command: /start
        ✅ Bot is running correctly.
    """
    if not update.effective_user or not update.effective_chat:
        return

    await update_dashboard(
        update,
        context,
        command_label="/start",
        body_text="✅ Bot is running correctly.",
    )


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mostra SOLO l'ID numerico dell'utente nella dashboard.

    - Cancella il messaggio /myid dell'utente.
    - Dashboard:
        Last command: /myid
        <ID numerico>
    """
    if not update.effective_user or not update.effective_chat:
        return

    user_id = update.effective_user.id

    await update_dashboard(
        update,
        context,
        command_label="/myid",
        body_text=str(user_id),
    )


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando disponibile solo agli admin configurati in ADMIN_IDS.

    - Se non admin:
        Last command: /admin
        ❌ Access denied.
    - Se admin:
        Last command: /admin
        🛠 You have admin privileges.
    """
    if not update.effective_user or not update.effective_chat:
        return

    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update_dashboard(
            update,
            context,
            command_label="/admin",
            body_text="❌ Access denied.",
        )
        return

    await update_dashboard(
        update,
        context,
        command_label="/admin",
        body_text="🛠 You have admin privileges.",
    )


# === HANDLER GENERICO DI CLEANUP ============================================


async def cleanup_other(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancella qualsiasi messaggio dell'utente che NON è un comando gestito.

    Non aggiorna la dashboard: rimane visibile l'ultimo comando valido.
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
    """Gestione globale degli errori.

    - Logga l'errore.
    - Se abbiamo un Update e una chat, aggiorna la dashboard con stato di errore.
    """

    logger.exception("Exception while handling an update: %s", context.error)

    if isinstance(update, Update) and update.effective_chat:
        try:
            # Proviamo a riusare la stessa logica di trasformazione: una sola dashboard.
            await update_dashboard(
                update,
                context,
                command_label="ERROR",
                body_text="An unexpected error occurred. Please try again later.",
            )
        except Exception:  # pragma: no cover
            # Se anche questo fallisce, logghiamo e basta.
            logger.exception("Failed to update dashboard for error.")


# === REGISTRAZIONE HANDLER ===================================================


def register_handlers(app: Application) -> None:
    """Registra tutti gli handler dell'applicazione."""

    # Comandi espliciti
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("admin", admin))

    # Qualsiasi altro messaggio (testo, media, sticker, ecc.) viene solo cancellato
    app.add_handler(MessageHandler(filters.ALL, cleanup_other))

    # Error handler globale
    app.add_error_handler(error_handler)
