from __future__ import annotations

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    """Esempio di modello utente collegato a un account Telegram."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(32), nullable=True)
