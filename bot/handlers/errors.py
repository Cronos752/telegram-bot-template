from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes


logger = logging.getLogger(__name__)


async def error_handler(update: object | Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler globale per gli errori non gestiti."""

    logger.exception("Unhandled exception while handling update %s", update, exc_info=context.error)
