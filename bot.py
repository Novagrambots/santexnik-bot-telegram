import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import settings
from db import crud
from db.migrate import run_migrations
from handlers import admin, broadcast, equipment, requests, start
from middlewares.user import UserMiddleware
from services.scheduler import setup_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    await run_migrations()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # middleware: подгрузка пользователя и языка
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())

    # роутеры: админские первыми (фильтруются по id админа), затем пользовательские
    dp.include_router(admin.router)
    dp.include_router(broadcast.router)
    dp.include_router(start.router)
    dp.include_router(equipment.router)
    dp.include_router(requests.router)

    scheduler = await setup_scheduler(bot)
    scheduler.start()

    cfg = await crud.get_settings()
    logger.info("Бот запущен. Напоминания в %02d:%02d", cfg.reminder_hour, cfg.reminder_minute)
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
