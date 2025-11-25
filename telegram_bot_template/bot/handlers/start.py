from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler per il comando /start."""

    user = update.effective_user
    first_name = user.first_name if user is not None else "there"

    if update.message is not None:
        await update.message.reply_text(f"Ciao {first_name}! Il bot è attivo.")
