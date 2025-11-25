"""Gestione errori globali."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


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
