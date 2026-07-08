import asyncio
import logging

from sqlalchemy.exc import InterfaceError, OperationalError

from alembic import command
from alembic.config import Config
from config import settings
from db.base import _ensure_sqlite_dir

logger = logging.getLogger(__name__)


def _run_upgrade() -> None:
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")


async def run_migrations(retries: int = 10, delay: float = 2.0) -> None:
    """Накатывает все миграции до head. Ждёт готовности БД (важно для PostgreSQL в Docker).

    Alembic запускается в отдельном потоке — внутри env.py используется asyncio.run,
    что несовместимо с уже работающим event loop основного процесса."""
    _ensure_sqlite_dir(settings.db_url)
    for attempt in range(1, retries + 1):
        try:
            await asyncio.to_thread(_run_upgrade)
            logger.info("Миграции применены (alembic upgrade head)")
            return
        except (OperationalError, InterfaceError, ConnectionError, OSError) as e:
            if attempt == retries:
                raise
            logger.warning("БД недоступна (попытка %s/%s): %s. Жду %.0f c…", attempt, retries, e, delay)
            await asyncio.sleep(delay)
