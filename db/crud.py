from datetime import date

from sqlalchemy import delete, func, select
from sqlalchemy.orm import selectinload

from config import settings as app_config
from db.base import async_session
from db.models import Admin, Broadcast, Equipment, ReminderLog, ServiceRequest, Settings, User


# ---------- Настройки бота ----------

async def get_settings() -> Settings:
    """Возвращает строку настроек, создавая её из .env-дефолтов при первом обращении."""
    async with async_session() as s:
        cfg = await s.get(Settings, 1)
        if cfg is None:
            cfg = Settings(
                id=1,
                reminder_hour=app_config.reminder_hour,
                reminder_minute=app_config.reminder_minute,
                reminder_stages=app_config.reminder_stages_days,
            )
            s.add(cfg)
            await s.commit()
            await s.refresh(cfg)
        return cfg


async def update_settings(
    reminder_hour: int | None = None,
    reminder_minute: int | None = None,
    reminder_stages: str | None = None,
    contacts: str | None = None,
) -> None:
    await get_settings()  # гарантирует наличие строки
    async with async_session() as s:
        cfg = await s.get(Settings, 1)
        if reminder_hour is not None:
            cfg.reminder_hour = reminder_hour
        if reminder_minute is not None:
            cfg.reminder_minute = reminder_minute
        if reminder_stages is not None:
            cfg.reminder_stages = reminder_stages
        if contacts is not None:
            cfg.contacts = contacts
        await s.commit()


# ---------- Админы ----------

async def is_db_admin(telegram_id: int) -> bool:
    async with async_session() as s:
        return await s.get(Admin, telegram_id) is not None


async def add_admin(telegram_id: int, added_by: int) -> None:
    async with async_session() as s:
        if await s.get(Admin, telegram_id) is None:
            s.add(Admin(telegram_id=telegram_id, added_by=added_by))
            await s.commit()


async def remove_admin(telegram_id: int) -> None:
    async with async_session() as s:
        admin = await s.get(Admin, telegram_id)
        if admin:
            await s.delete(admin)
            await s.commit()


async def list_admins() -> list[Admin]:
    async with async_session() as s:
        res = await s.scalars(select(Admin).order_by(Admin.created_at))
        return list(res)


# ---------- Пользователи ----------

async def get_user(telegram_id: int) -> User | None:
    async with async_session() as s:
        return await s.get(User, telegram_id)


async def create_user(telegram_id: int, full_name: str, phone: str | None, lang: str) -> User:
    async with async_session() as s:
        user = User(telegram_id=telegram_id, full_name=full_name, phone=phone, lang=lang)
        s.add(user)
        await s.commit()
        await s.refresh(user)
        return user


async def set_user_active(telegram_id: int, active: bool) -> None:
    async with async_session() as s:
        user = await s.get(User, telegram_id)
        if user:
            user.is_active = active
            await s.commit()


async def set_user_lang(telegram_id: int, lang: str) -> None:
    async with async_session() as s:
        user = await s.get(User, telegram_id)
        if user:
            user.lang = lang
            await s.commit()


async def count_users() -> int:
    async with async_session() as s:
        return await s.scalar(select(func.count()).select_from(User)) or 0


async def list_users(limit: int, offset: int) -> list[User]:
    async with async_session() as s:
        res = await s.scalars(
            select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
        )
        return list(res)


async def get_recipients(segment: str, kind: str | None = None) -> list[User]:
    """Получатели рассылки по сегменту: all / overdue / lang:ru / lang:uz / kind:<вид>."""
    async with async_session() as s:
        stmt = select(User).where(User.is_active.is_(True))
        if segment == "overdue":
            today = date.today()
            sub = select(Equipment.user_id).where(Equipment.next_service_date < today)
            stmt = stmt.where(User.telegram_id.in_(sub))
        elif segment.startswith("lang:"):
            stmt = stmt.where(User.lang == segment.split(":", 1)[1])
        elif segment.startswith("kind:"):
            k = segment.split(":", 1)[1]
            sub = select(Equipment.user_id).where(Equipment.kind == k)
            stmt = stmt.where(User.telegram_id.in_(sub))
        res = await s.scalars(stmt)
        return list(res)


# ---------- Оборудование ----------

async def add_equipment(
    user_id: int,
    kind: str,
    model: str | None,
    install_date: date,
    period_months: int,
    next_service_date: date,
) -> Equipment:
    async with async_session() as s:
        eq = Equipment(
            user_id=user_id,
            kind=kind,
            model=model,
            install_date=install_date,
            period_months=period_months,
            next_service_date=next_service_date,
        )
        s.add(eq)
        await s.commit()
        await s.refresh(eq)
        return eq


async def get_equipment(equipment_id: int) -> Equipment | None:
    async with async_session() as s:
        return await s.get(Equipment, equipment_id)


async def list_user_equipment(user_id: int) -> list[Equipment]:
    async with async_session() as s:
        res = await s.scalars(
            select(Equipment).where(Equipment.user_id == user_id).order_by(Equipment.next_service_date)
        )
        return list(res)


async def delete_equipment(equipment_id: int) -> None:
    async with async_session() as s:
        await s.execute(delete(Equipment).where(Equipment.id == equipment_id))
        await s.commit()


async def set_next_service_date(
    equipment_id: int, next_date: date, last_service: date | None = None
) -> None:
    """Обновляет дату следующей профилактики и сбрасывает лог напоминаний."""
    async with async_session() as s:
        eq = await s.get(Equipment, equipment_id)
        if not eq:
            return
        eq.next_service_date = next_date
        if last_service is not None:
            eq.last_service_date = last_service
        await s.execute(delete(ReminderLog).where(ReminderLog.equipment_id == equipment_id))
        await s.commit()


async def all_equipment() -> list[Equipment]:
    """Всё оборудование с подгруженным пользователем — для планировщика."""
    async with async_session() as s:
        res = await s.scalars(select(Equipment).options(selectinload(Equipment.user)))
        return list(res)


async def equipment_due_between(start: date, end: date) -> list[Equipment]:
    async with async_session() as s:
        res = await s.scalars(
            select(Equipment)
            .options(selectinload(Equipment.user))
            .where(Equipment.next_service_date >= start, Equipment.next_service_date <= end)
            .order_by(Equipment.next_service_date)
        )
        return list(res)


async def count_overdue(today: date) -> int:
    async with async_session() as s:
        return await s.scalar(
            select(func.count()).select_from(Equipment).where(Equipment.next_service_date < today)
        ) or 0


# ---------- Лог напоминаний ----------

async def reminder_sent(equipment_id: int, stage: str) -> bool:
    async with async_session() as s:
        row = await s.scalar(
            select(ReminderLog.id).where(
                ReminderLog.equipment_id == equipment_id, ReminderLog.stage == stage
            )
        )
        return row is not None


async def log_reminder(equipment_id: int, stage: str) -> None:
    async with async_session() as s:
        s.add(ReminderLog(equipment_id=equipment_id, stage=stage))
        await s.commit()


# ---------- Заявки ----------

async def create_request(
    user_id: int, type_: str, equipment_id: int | None = None, comment: str | None = None
) -> ServiceRequest:
    async with async_session() as s:
        req = ServiceRequest(user_id=user_id, type=type_, equipment_id=equipment_id, comment=comment)
        s.add(req)
        await s.commit()
        await s.refresh(req)
        return req


async def list_new_requests(limit: int = 20) -> list[ServiceRequest]:
    async with async_session() as s:
        res = await s.scalars(
            select(ServiceRequest)
            .where(ServiceRequest.status == "new")
            .order_by(ServiceRequest.created_at.desc())
            .limit(limit)
        )
        return list(res)


async def mark_request_done(request_id: int) -> None:
    async with async_session() as s:
        req = await s.get(ServiceRequest, request_id)
        if req:
            req.status = "done"
            await s.commit()


# ---------- Рассылки ----------

async def log_broadcast(admin_id: int, segment: str, sent: int, failed: int) -> None:
    async with async_session() as s:
        s.add(Broadcast(admin_id=admin_id, segment=segment, sent_count=sent, failed_count=failed))
        await s.commit()
