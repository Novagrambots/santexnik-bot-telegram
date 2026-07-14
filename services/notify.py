import logging
from collections.abc import Iterable

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from config import settings
from db import crud
from i18n import kind_label, t

logger = logging.getLogger(__name__)


async def _send_localized(
    bot: Bot, ids: Iterable[int], key: str, kind_code: str | None, params: dict
) -> None:
    """Шлёт текст по ключу i18n каждому получателю на его языке."""
    for uid in ids:
        user = await crud.get_user(uid)
        lang = user.lang if user else "ru"
        p = dict(params)
        if kind_code is not None:
            p["kind"] = kind_label(kind_code, lang)
        try:
            await bot.send_message(uid, t(key, lang, **p))
        except TelegramAPIError as e:
            logger.warning("Не смог уведомить %s: %s", uid, e)


async def notify_admins(bot: Bot, key: str, *, kind_code: str | None = None, **params) -> None:
    """Уведомляет всех админов (супер + добавленные в БД)."""
    from services.access import all_admin_ids

    await _send_localized(bot, await all_admin_ids(), key, kind_code, params)


async def notify_masters(bot: Bot, key: str, kind_code: str, **params) -> None:
    """Уведомляет мастеров данного вида оборудования + супер-админов (всегда).

    Если мастера по виду нет — уведомление всё равно уходит супер-админам."""
    ids = set(settings.admin_ids_list)
    for m in await crud.masters_for_kind(kind_code):
        ids.add(m.telegram_id)
    await _send_localized(bot, ids, key, kind_code, params)
