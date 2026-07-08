from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from config import settings
from db import crud


def is_super_admin(user_id: int) -> bool:
    """Супер-админы задаются в .env (ADMIN_IDS). Могут управлять другими админами."""
    return user_id in settings.admin_ids_list


async def is_admin(user_id: int) -> bool:
    """Админ = супер-админ из .env ИЛИ динамический админ из БД."""
    if is_super_admin(user_id):
        return True
    return await crud.is_db_admin(user_id)


async def all_admin_ids() -> list[int]:
    """Все админы: супер-админы из .env + добавленные в БД."""
    ids = set(settings.admin_ids_list)
    for a in await crud.list_admins():
        ids.add(a.telegram_id)
    return list(ids)


class IsAdmin(BaseFilter):
    """Фильтр роутера: пропускает только админов (супер + из БД)."""

    async def __call__(self, event: TelegramObject) -> bool:
        user = getattr(event, "from_user", None)
        if user is None:
            return False
        return await is_admin(user.id)
