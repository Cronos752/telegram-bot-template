"""Registrazione centralizzata degli handler di telegram-telegram-bot."""

from telegram.ext import Application, CommandHandler

from .start import start


def setup_handlers(application: Application) -> None:
    """Registra tutti gli handler sull'istanza di Application."""

    application.add_handler(CommandHandler("start", start))
