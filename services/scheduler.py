import logging
from datetime import date

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramAPIError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db import crud
from i18n import kind_label, t
from keyboards.common import reminder_kb
from services.reminders import due_stages, fmt_date, parse_stages, stage_name

logger = logging.getLogger(__name__)

JOB_ID = "daily_reminders"
_scheduler: AsyncIOScheduler | None = None


async def run_reminders(bot: Bot) -> int:
    """Обходит всё оборудование и рассылает напоминания по наступившим этапам.

    Этапы берутся из настроек в БД (редактируются в админке).
    Возвращает число отправленных напоминаний."""
    today = date.today()
    cfg = await crud.get_settings()
    stages = parse_stages(cfg.reminder_stages)
    sent = 0
    for eq in await crud.all_equipment():
        user = eq.user
        if not user or not user.is_active:
            continue
        for stage in due_stages(eq.next_service_date, today, stages):
            sname = stage_name(stage)
            if await crud.reminder_sent(eq.id, sname):
                continue
            model = f" ({eq.model})" if eq.model else ""
            kind = kind_label(eq.kind, user.lang)
            if stage == 0:
                text = t("reminder_today", user.lang, kind=kind, model=model)
            else:
                text = t(
                    "reminder_soon", user.lang,
                    days=stage, kind=kind, model=model, date=fmt_date(eq.next_service_date),
                )
            try:
                await bot.send_message(
                    user.telegram_id, text, reply_markup=reminder_kb(user.lang, eq.id)
                )
                await crud.log_reminder(eq.id, sname)
                sent += 1
            except TelegramForbiddenError:
                await crud.set_user_active(user.telegram_id, False)
            except TelegramAPIError as e:
                logger.warning("Напоминание %s не отправлено: %s", user.telegram_id, e)
    logger.info("Напоминаний отправлено: %s", sent)
    return sent


async def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    """Создаёт и настраивает планировщик по времени из БД."""
    global _scheduler
    cfg = await crud.get_settings()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_reminders,
        trigger="cron",
        hour=cfg.reminder_hour,
        minute=cfg.reminder_minute,
        args=[bot],
        id=JOB_ID,
        replace_existing=True,
    )
    _scheduler = scheduler
    return scheduler


def reschedule(hour: int, minute: int) -> None:
    """Переносит ежедневную задачу на новое время без перезапуска бота."""
    if _scheduler is None:
        return
    _scheduler.reschedule_job(JOB_ID, trigger="cron", hour=hour, minute=minute)
    logger.info("Напоминания перенесены на %02d:%02d", hour, minute)
