from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from ..config import BotConfig


class Base(DeclarativeBase):
    """Base declarativa per tutti i modelli SQLAlchemy."""


_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def init_engine(config: BotConfig):
    """Inizializza l'engine asincrono e il sessionmaker globale.

    Deve essere chiamata una sola volta all'avvio dell'applicazione.
    """

    global _sessionmaker

    engine = create_async_engine(config.database_url, echo=False)
    _sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    return engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Ritorna il sessionmaker globale.

    Solleva un RuntimeError se l'engine non è ancora stato inizializzato.
    """

    if _sessionmaker is None:
        raise RuntimeError("Database engine not initialized. Call init_engine() first.")
    return _sessionmaker


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Fornisce una sessione asincrona da usare con `async with`.

    Esempio:

    ```python
    async for session in get_session():
        ...
    ```
    """

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        yield session
