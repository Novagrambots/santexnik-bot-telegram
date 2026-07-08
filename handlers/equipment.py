from datetime import date

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from db import crud
from db.models import User
from i18n import kind_label, t
from keyboards.common import (
    equipment_item_kb,
    kinds_kb,
    main_menu_kb,
    period_kb,
    postpone_kb,
    skip_kb,
)
from services.access import is_admin
from services.notify import notify_admins
from services.reminders import (
    add_months,
    calc_next_service_date,
    fmt_date,
    parse_date,
    timedelta,
)

router = Router()


class AddEq(StatesGroup):
    kind = State()
    model = State()
    install_date = State()
    period = State()


def _require(user: User | None) -> bool:
    return user is not None


# ---------- Мой список оборудования ----------

@router.message(F.text.in_({t("btn_my_equipment", "ru"), t("btn_my_equipment", "uz")}))
async def my_equipment(message: Message, user: User | None):
    if not _require(user):
        await message.answer(t("not_registered"))
        return
    items = await crud.list_user_equipment(user.telegram_id)
    if not items:
        await message.answer(t("no_equipment", user.lang))
        return
    for eq in items:
        model = f" ({eq.model})" if eq.model else ""
        text = t(
            "equipment_item", user.lang,
            kind=kind_label(eq.kind, user.lang), model=model, date=fmt_date(eq.next_service_date),
        )
        await message.answer(text, reply_markup=equipment_item_kb(user.lang, eq.id))


@router.callback_query(F.data.startswith("eqdel:"))
async def delete_eq(cb: CallbackQuery, user: User | None):
    eq_id = int(cb.data.split(":", 1)[1])
    eq = await crud.get_equipment(eq_id)
    if eq and user and eq.user_id == user.telegram_id:
        await crud.delete_equipment(eq_id)
        await cb.message.edit_reply_markup(reply_markup=None)
        await cb.answer(t("equipment_deleted", user.lang))
    else:
        await cb.answer()


# ---------- Добавление оборудования ----------

@router.message(F.text.in_({t("btn_add_equipment", "ru"), t("btn_add_equipment", "uz")}))
async def add_start(message: Message, state: FSMContext, user: User | None):
    if not _require(user):
        await message.answer(t("not_registered"))
        return
    await state.set_state(AddEq.kind)
    await message.answer(t("ask_kind", user.lang), reply_markup=kinds_kb(user.lang))


@router.callback_query(AddEq.kind, F.data.startswith("kind:"))
async def add_kind_cb(cb: CallbackQuery, state: FSMContext, lang: str):
    kind = cb.data.split(":", 1)[1]
    await state.update_data(kind=kind)
    await state.set_state(AddEq.model)
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(t("ask_model", lang), reply_markup=skip_kb(lang))
    await cb.answer()


@router.callback_query(AddEq.kind, F.data == "kind_other")
async def add_kind_other(cb: CallbackQuery, lang: str):
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(t("ask_kind_custom", lang))
    await cb.answer()


@router.message(AddEq.kind, F.text)
async def add_kind_text(message: Message, state: FSMContext, lang: str):
    await state.update_data(kind=message.text.strip())
    await state.set_state(AddEq.model)
    await message.answer(t("ask_model", lang), reply_markup=skip_kb(lang))


@router.callback_query(AddEq.model, F.data == "skip_model")
async def add_model_skip(cb: CallbackQuery, state: FSMContext, lang: str):
    await state.update_data(model=None)
    await state.set_state(AddEq.install_date)
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(t("ask_install_date", lang))
    await cb.answer()


@router.message(AddEq.model, F.text)
async def add_model_text(message: Message, state: FSMContext, lang: str):
    await state.update_data(model=message.text.strip())
    await state.set_state(AddEq.install_date)
    await message.answer(t("ask_install_date", lang))


@router.message(AddEq.install_date, F.text)
async def add_install_date(message: Message, state: FSMContext, lang: str):
    d = parse_date(message.text)
    if not d:
        await message.answer(t("bad_date", lang))
        return
    await state.update_data(install_date=d.isoformat())
    await state.set_state(AddEq.period)
    await message.answer(t("ask_period", lang), reply_markup=period_kb(lang))


@router.callback_query(AddEq.period, F.data.startswith("period:"))
async def add_period(cb: CallbackQuery, state: FSMContext, user: User | None, lang: str):
    period = int(cb.data.split(":", 1)[1])
    data = await state.get_data()
    install = date.fromisoformat(data["install_date"])
    # следующая профилактика от даты установки; если она уже в прошлом — считаем от сегодня
    next_date = calc_next_service_date(install, period)
    if next_date < date.today():
        next_date = calc_next_service_date(date.today(), period)
    await crud.add_equipment(
        user_id=user.telegram_id,
        kind=data["kind"],
        model=data.get("model"),
        install_date=install,
        period_months=period,
        next_service_date=next_date,
    )
    await state.clear()
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(
        t("equipment_added", lang, kind=kind_label(data["kind"], lang), date=fmt_date(next_date)),
        reply_markup=main_menu_kb(lang, await is_admin(user.telegram_id)),
    )
    await cb.answer()


# ---------- Кнопки в напоминаниях ----------

@router.callback_query(F.data.startswith("rem_book:"))
async def reminder_book(cb: CallbackQuery, user: User | None, lang: str):
    eq_id = int(cb.data.split(":", 1)[1])
    eq = await crud.get_equipment(eq_id)
    if not eq or not user:
        await cb.answer()
        return
    await crud.create_request(user.telegram_id, "запись", equipment_id=eq_id)
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(t("booked", lang))
    await notify_admins(
        cb.bot, "n_booking", kind_code=eq.kind,
        name=user.full_name, phone=user.phone or "—", id=user.telegram_id,
    )
    await cb.answer()


@router.callback_query(F.data.startswith("rem_done:"))
async def reminder_done(cb: CallbackQuery, lang: str):
    eq_id = int(cb.data.split(":", 1)[1])
    eq = await crud.get_equipment(eq_id)
    if not eq:
        await cb.answer()
        return
    today = date.today()
    next_date = add_months(today, eq.period_months)
    await crud.set_next_service_date(eq_id, next_date, last_service=today)
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(t("marked_done", lang, date=fmt_date(next_date)))
    await cb.answer()


@router.callback_query(F.data.startswith("rem_postpone:"))
async def reminder_postpone(cb: CallbackQuery, lang: str):
    eq_id = int(cb.data.split(":", 1)[1])
    await cb.message.answer(t("postpone_ask", lang), reply_markup=postpone_kb(lang, eq_id))
    await cb.answer()


@router.callback_query(F.data.startswith("pp:"))
async def reminder_postpone_apply(cb: CallbackQuery, lang: str):
    _, eq_id_s, days_s = cb.data.split(":")
    eq_id, days = int(eq_id_s), int(days_s)
    eq = await crud.get_equipment(eq_id)
    if not eq:
        await cb.answer()
        return
    base = max(eq.next_service_date, date.today())
    next_date = base + timedelta(days=days)
    await crud.set_next_service_date(eq_id, next_date)
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(t("postponed", lang, date=fmt_date(next_date)))
    await cb.answer()
