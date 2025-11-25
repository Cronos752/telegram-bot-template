"""Gestione della vista dei messaggi (header + body) per ogni chat.

- Cancella sempre il messaggio dell'utente che ha generato il comando.
- Mantiene esattamente due messaggi del bot per chat:
  - un header (es. '> /start')
  - un body (l'output del comando)
- Ad ogni nuovo comando, edita questi due messaggi invece di crearne di nuovi.
"""

from __future__ import annotations

import logging

from telegram import Update
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
        # Non blocchiamo il bot se non riusciamo a cancellare (es. diritti mancanti)
        logger.debug("Failed to delete user message: %s", exc)


async def update_view(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    command_label: str,
    body_text: str,
) -> None:
    """Aggiorna (o crea) header e body per la chat corrente.

    - command_label: testo breve del comando (es. '/start', '/myid', '/admin')
    - body_text: output da mostrare nel body
    """
    if not update.effective_chat:
        return

    chat_id = update.effective_chat.id

    # 1) Cancella il messaggio dell'utente
    await _delete_user_message(update)

    chat_data = context.chat_data

    header_id = chat_data.get("header_message_id")
    body_id = chat_data.get("body_message_id")

    header_text = f"> {command_label}"

    # 2) Header: crea o edita
    if header_id is None:
        # Non esiste ancora: creiamo un nuovo header
        sent_header = await context.bot.send_message(
            chat_id=chat_id,
            text=header_text,
        )
        chat_data["header_message_id"] = sent_header.message_id
    else:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=header_id,
                text=header_text,
            )
        except Exception as exc:  # noqa: BLE001
            logger.debug("Failed to edit header message, sending new one: %s", exc)
            sent_header = await context.bot.send_message(
                chat_id=chat_id,
                text=header_text,
            )
            chat_data["header_message_id"] = sent_header.message_id

    # 3) Body: crea o edita
    if body_id is None:
        sent_body = await context.bot.send_message(
            chat_id=chat_id,
            text=body_text,
        )
        chat_data["body_message_id"] = sent_body.message_id
    else:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=body_id,
                text=body_text,
            )
        except Exception as exc:  # noqa: BLE001
            logger.debug("Failed to edit body message, sending new one: %s", exc)
            sent_body = await context.bot.send_message(
                chat_id=chat_id,
                text=body_text,
            )
            chat_data["body_message_id"] = sent_body.message_id
