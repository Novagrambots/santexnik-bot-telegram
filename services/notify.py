import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from db import crud
from i18n import kind_label, t

logger = logging.getLogger(__name__)


async def notify_admins(bot: Bot, key: str, *, kind_code: str | None = None, **params) -> None:
    """Шлёт уведомление всем админам (супер + из БД), каждому на его языке.

    key — ключ i18n; params подставляются в шаблон. Если задан kind_code,
    название вида оборудования переводится на язык конкретного админа."""
    from services.access import all_admin_ids

    for admin_id in await all_admin_ids():
        user = await crud.get_user(admin_id)
        lang = user.lang if user else "ru"
        p = dict(params)
        if kind_code is not None:
            p["kind"] = kind_label(kind_code, lang)
        try:
            await bot.send_message(admin_id, t(key, lang, **p))
        except TelegramAPIError as e:
            logger.warning("Не смог уведомить админа %s: %s", admin_id, e)
