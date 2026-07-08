from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TgUser

from db import crud
from i18n import DEFAULT_LANG


class UserMiddleware(BaseMiddleware):
    """Подгружает пользователя из БД и кладёт в data: user, lang."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user: TgUser | None = data.get("event_from_user")
        db_user = None
        if tg_user and not tg_user.is_bot:
            db_user = await crud.get_user(tg_user.id)
        data["user"] = db_user
        data["lang"] = db_user.lang if db_user else DEFAULT_LANG
        return await handler(event, data)
