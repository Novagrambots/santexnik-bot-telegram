from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import settings


def _ensure_sqlite_dir(url: str) -> None:
    """Создаёт папку для файла SQLite, если её ещё нет."""
    marker = ":///"
    if url.startswith("sqlite") and marker in url:
        path = url.split(marker, 1)[1]
        if path and path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_dir(settings.db_url)
engine = create_async_engine(settings.db_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
