from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    lang: Mapped[str] = mapped_column(String(2), default="ru")
    is_active: Mapped[bool] = mapped_column(default=True)  # False = заблокировал бота
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    equipment: Mapped[list["Equipment"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE")
    )
    kind: Mapped[str] = mapped_column(String(64))              # котёл / бойлер / фильтр / ...
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    install_date: Mapped[date] = mapped_column(Date)
    period_months: Mapped[int] = mapped_column(default=12)
    last_service_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_service_date: Mapped[date] = mapped_column(Date, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="equipment")
    reminders: Mapped[list["ReminderLog"]] = relationship(
        back_populates="equipment", cascade="all, delete-orphan"
    )


class ReminderLog(Base):
    """Отметка, что напоминание этапа `stage` для оборудования уже отправлено.

    Чистится при сдвиге next_service_date (после профилактики/переноса),
    чтобы к новому циклу напоминания слались заново.
    """

    __tablename__ = "reminder_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipment.id", ondelete="CASCADE"), index=True
    )
    stage: Mapped[str] = mapped_column(String(8))   # "14d" / "3d" / "0d"
    sent_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    equipment: Mapped["Equipment"] = relationship(back_populates="reminders")


class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"))
    equipment_id: Mapped[int | None] = mapped_column(
        ForeignKey("equipment.id", ondelete="SET NULL"), nullable=True
    )
    type: Mapped[str] = mapped_column(String(16))     # запись / вызов / авария
    status: Mapped[str] = mapped_column(String(8), default="new")  # new / done
    comment: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


DEFAULT_CONTACTS = "📞 Наши контакты:\nТелефон: +998 XX XXX-XX-XX\nВремя работы: 9:00–18:00"


class Settings(Base):
    """Настройки бота, редактируемые из админки (одна строка, id=1)."""

    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    reminder_hour: Mapped[int] = mapped_column(default=9)
    reminder_minute: Mapped[int] = mapped_column(default=0)
    reminder_stages: Mapped[str] = mapped_column(String(64), default="14,3,0")
    contacts: Mapped[str] = mapped_column(String(1024), default=DEFAULT_CONTACTS)


class Admin(Base):
    """Динамические админы (добавляются супер-админом). Супер-админы — в .env ADMIN_IDS."""

    __tablename__ = "admins"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    added_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Master(Base):
    """Мастер компании. Получает уведомления по своему виду оборудования."""

    __tablename__ = "masters"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(128))
    kind: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Broadcast(Base):
    __tablename__ = "broadcasts"

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id: Mapped[int] = mapped_column(BigInteger)
    segment: Mapped[str] = mapped_column(String(64))
    sent_count: Mapped[int] = mapped_column(default=0)
    failed_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
