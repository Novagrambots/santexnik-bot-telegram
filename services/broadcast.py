import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter, TelegramAPIError

from db import crud

logger = logging.getLogger(__name__)

# ~25 сообщений в секунду — безопасный лимит Telegram для рассылок
SEND_DELAY = 0.04


async def run_broadcast(
    bot: Bot, recipients: list[int], from_chat_id: int, message_id: int
) -> tuple[int, int]:
    """Копирует сообщение всем получателям. Возвращает (доставлено, ошибок)."""
    sent, failed = 0, 0
    for uid in recipients:
        try:
            await bot.copy_message(chat_id=uid, from_chat_id=from_chat_id, message_id=message_id)
            sent += 1
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            try:
                await bot.copy_message(chat_id=uid, from_chat_id=from_chat_id, message_id=message_id)
                sent += 1
            except TelegramAPIError:
                failed += 1
        except TelegramForbiddenError:
            # пользователь заблокировал бота
            failed += 1
            await crud.set_user_active(uid, False)
        except TelegramAPIError as e:
            failed += 1
            logger.warning("Рассылка: ошибка для %s: %s", uid, e)
        await asyncio.sleep(SEND_DELAY)
    return sent, failed
