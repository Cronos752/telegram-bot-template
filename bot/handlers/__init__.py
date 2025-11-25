"""Registrazione degli handler del bot."""

from __future__ import annotations

from telegram.ext import Application, CommandHandler

from .start import start
from .errors import error_handler


def register_handlers(app: Application) -> None:
    app.add_handler(CommandHandler("start", start))

    # Error handler globale
    app.add_error_handler(error_handler)
