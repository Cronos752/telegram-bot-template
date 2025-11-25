"""Gestione della vista a singolo messaggio (dashboard) per ogni chat.

Regole:
- Qualsiasi messaggio dell'utente (comandi, testo, upload, ecc.) viene cancellato.
- In ogni chat esiste al massimo UN solo messaggio del bot ("dashboard").
- Ad ogni nuovo comando, la dashboard viene EDITATA (edit_message_text)
  per mostrare solo l'output corrente.
- Se il comando e l'output sono IDENTICI all'ultima volta, non viene
  fatto alcun update (nessuna trasformazione visibile).
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
        # Non blocchiamo il bot se non riusciamo a cancellare
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

    La dashboard è un singolo messaggio del bot che contiene SOLO il body_text.
    Se command_label + body_text sono identici all'ultima invocazione,
    la dashboard non viene modificata (si cancella solo il messaggio utente).
    """
    if not update.effective_chat:
        return

    chat_id = update.effective_chat.id

    # 1) Cancella SEMPRE il messaggio dell'utente
    await _delete_user_message(update)

    chat_data = context.chat_data

    # Leggiamo l'ultimo comando/output usati per questa chat
    last_label = chat_data.get("last_command_label")
    last_body = chat_data.get("last_body_text")

    # Se comando e output sono identici a prima, non aggiorniamo la dashboard
    if last_label == command_label and last_body == body_text:
        logger.debug(
            "Same command (%s) and body as last time; not updating dashboard.",
            command_label,
        )
        return

    dashboard_id = chat_data.get("dashboard_message_id")

    text = body_text

    # 2) Crea o edita la dashboard
    if dashboard_id is None:
        # Non esiste ancora: creiamo un nuovo messaggio
        sent = await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
        )
        chat_data["dashboard_message_id"] = sent.message_id
    else:
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

    # 3) Aggiorniamo lo stato logico per la prossima volta
    chat_data["last_command_label"] = command_label
    chat_data["last_body_text"] = body_text
