# bot/handlers/start.py

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler semplice per /start, senza DB e senza rate limit."""
    if not update.effective_user or not update.effective_chat:
        return

    first_name = update.effective_user.first_name or "lì"
    await update.effective_chat.send_message(
        f"Ciao {first_name}! Il bot è attivo."
    )
