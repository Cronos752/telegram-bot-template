"""Configurazione SQLAlchemy async."""

from __future__ import annotations

from typing import Final

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from bot.config import load_settings

_settings = load_settings()

DATABASE_URL: Final = (
    f"postgresql+asyncpg://{_settings.db.user}:{_settings.db.password}"
    f"@{_settings.db.host}:{_settings.db.port}/{_settings.db.name}"
)


class Base(DeclarativeBase):
    """Base declarativa per tutti i modelli SQLAlchemy."""
    pass


engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
)

async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
