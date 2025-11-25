"""Gestione della vista a singolo messaggio (dashboard) per ogni chat.

Regole:
- Qualsiasi messaggio dell'utente (comandi, testo, upload, ecc.) viene cancellato.
- In ogni chat esiste al massimo UN solo messaggio del bot ("dashboard").
- Ad ogni nuovo comando, la dashboard viene EDITATA (edit_message_text)
  per mostrare:
    - l'ultimo comando eseguito
    - l'ultimo output prodotto
"""

from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def _delete_user_message(update: Update) -> None:
    """Cancella il messaggio dell'utente (se possibile)."""
    message = update.effective_message
    if not message:
        return

    try:
        await message.delete()
    except Exception as exc:  # noqa: BLE001
        # Non blocchiamo il bot se non riusciamo a cancellare (es. diritti mancanti, ecc.)
        logger.debug("Failed to delete user message: %s", exc)


async def update_dashboard(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    command_label: str,
    body_text: str,
) -> None:
    """Aggiorna (o crea) la dashboard per la chat corrente.

    - command_label: nome del comando (es. '/start', '/myid', '/admin', 'ERROR')
    - body_text: testo dell'output da mostrare

    La dashboard è un singolo messaggio del bot che contiene:
      *Last command*: `<command_label>`
      <body_text>
    """
    if not update.effective_chat:
        return

    chat_id = update.effective_chat.id

    # 1) Cancella SEMPRE il messaggio dell'utente
    await _delete_user_message(update)

    chat_data = context.chat_data

    dashboard_id = chat_data.get("dashboard_message_id")

    text = (
        f"*Last command*: `{command_label}`\n\n"
        f"{body_text}"
    )

    # 2) Crea o edita la dashboard
    if dashboard_id is None:
        # Non esiste ancora: creiamo un nuovo messaggio
        sent = await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
        )
        chat_data["dashboard_message_id"] = sent.message_id
        return

    # Esiste già: proviamo a editarla
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=dashboard_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("Failed to edit dashboard message, sending new one: %s", exc)
        sent = await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
        )
        chat_data["dashboard_message_id"] = sent.message_id
