"""Funzioni di supporto per l'autenticazione/ruoli (admin ecc.)."""

from __future__ import annotations

from functools import lru_cache
from typing import Set

from .config import load_settings


@lru_cache(maxsize=1)
def _get_admin_ids() -> Set[int]:
    """Ritorna l'insieme degli admin ID configurati nello `.env`."""
    settings = load_settings()
    return set(settings.admin_ids)


def is_admin(user_id: int) -> bool:
    """True se l'utente è configurato come admin nello `.env`."""
    return user_id in _get_admin_ids()
