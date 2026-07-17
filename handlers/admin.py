import io
from datetime import date

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import settings
from db import crud
from i18n import kind_label, t
from keyboards.common import NOT_MENU, cancel_kb, kinds_kb
from services.access import IsAdmin, is_super_admin
from services.loyalty import format_money, parse_money
from services.notify import notify_admins
from services.reminders import add_months, fmt_date, parse_date, parse_stages
from services.scheduler import reschedule

router = Router()

PAGE = 8

# доступ ко всему роутеру только у админов (супер + из БД); прочие апдейты проходят мимо
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


class AdmState(StatesGroup):
    set_date = State()
    set_time = State()
    set_stages = State()
    set_contacts = State()
    set_workhours = State()
    add_admin = State()
    add_master_id = State()
    add_master_name = State()
    add_master_kind = State()
    pay_amount = State()
    spend_amount = State()
    req_amount = State()
    set_bonus_thr = State()
    set_bonus_amt = State()


def admin_menu_kb(lang: str, is_super: bool = False) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t("a_btn_clients", lang), callback_data="adm_users:0")
    b.button(text=t("a_btn_stats", lang), callback_data="adm_stats")
    b.button(text=t("a_btn_requests", lang), callback_data="adm_reqs")
    b.button(text=t("a_btn_broadcast", lang), callback_data="adm_bc")
    b.button(text=t("a_btn_export", lang), callback_data="adm_export")
    b.button(text=t("a_btn_settings", lang), callback_data="adm_cfg")
    b.button(text=t("a_btn_masters", lang), callback_data="adm_masters")
    layout = [2, 2, 2, 1]
    if is_super:
        b.button(text=t("a_btn_admins", lang), callback_data="adm_admins")
        layout.append(1)
    b.adjust(*layout)
    return b.as_markup()


async def _open_panel(message: Message, lang: str, user_id: int) -> None:
    await message.answer(t("a_panel_title", lang), reply_markup=admin_menu_kb(lang, is_super_admin(user_id)))


@router.message(Command("admin"))
async def admin_cmd(message: Message, state: FSMContext, lang: str):
    await state.clear()
    await _open_panel(message, lang, message.from_user.id)


# вход в панель по кнопке главного меню (видна только админам)
@router.message(F.text.in_({t("btn_admin_panel", "ru"), t("btn_admin_panel", "uz")}))
async def admin_panel_button(message: Message, state: FSMContext, lang: str):
    await state.clear()
    await _open_panel(message, lang, message.from_user.id)


@router.message(Command("test_reminders"))
async def admin_test_reminders(message: Message, lang: str):
    from services.scheduler import run_reminders

    sent = await run_reminders(message.bot)
    await message.answer(t("a_test_done", lang, n=sent))


@router.callback_query(F.data == "adm_home")
async def admin_home(cb: CallbackQuery, state: FSMContext, lang: str):
    await state.clear()
    await cb.message.edit_text(
        t("a_panel_title", lang), reply_markup=admin_menu_kb(lang, is_super_admin(cb.from_user.id))
    )
    await cb.answer()


# ---------- Статистика ----------

@router.callback_query(F.data == "adm_stats")
async def admin_stats(cb: CallbackQuery, lang: str):
    today = date.today()
    total = await crud.count_users()
    overdue = await crud.count_overdue(today)
    month_end = add_months(today.replace(day=1), 1)
    due_month = await crud.equipment_due_between(today, month_end)
    text = t("a_stats", lang, total=total, month=len(due_month), overdue=overdue)
    b = InlineKeyboardBuilder()
    b.button(text=t("a_btn_back", lang), callback_data="adm_home")
    await cb.message.edit_text(text, reply_markup=b.as_markup())
    await cb.answer()


# ---------- Клиенты ----------

@router.callback_query(F.data.startswith("adm_users:"))
async def admin_users(cb: CallbackQuery, lang: str):
    offset = int(cb.data.split(":", 1)[1])
    users = await crud.list_users(PAGE, offset)
    total = await crud.count_users()
    b = InlineKeyboardBuilder()
    for u in users:
        b.button(text=f"{u.full_name} ({u.phone or '—'})", callback_data=f"adm_user:{u.telegram_id}")
    b.adjust(1)
    nav = []
    if offset > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"adm_users:{max(0, offset - PAGE)}"))
    if offset + PAGE < total:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"adm_users:{offset + PAGE}"))
    if nav:
        b.row(*nav)
    b.row(InlineKeyboardButton(text=t("a_btn_menu", lang), callback_data="adm_home"))
    await cb.message.edit_text(t("a_clients_title", lang, n=total), reply_markup=b.as_markup())
    await cb.answer()


@router.callback_query(F.data.startswith("adm_user:"))
async def admin_user_card(cb: CallbackQuery, lang: str):
    uid = int(cb.data.split(":", 1)[1])
    user = await crud.get_user(uid)
    if not user:
        await cb.answer(t("a_not_found", lang), show_alert=True)
        return
    items = await crud.list_user_equipment(uid)
    lines = [
        f"👤 {user.full_name}", f"📱 {user.phone or '—'}", f"🌐 {user.lang}", f"id: {uid}",
        t("a_card_money", lang, paid=format_money(user.total_paid), balance=format_money(user.bonus_balance)),
        "",
    ]
    b = InlineKeyboardBuilder()
    if items:
        for eq in items:
            model = f" ({eq.model})" if eq.model else ""
            name = kind_label(eq.kind, lang)
            lines.append(t("a_card_equip", lang, name=name, model=model, date=fmt_date(eq.next_service_date)))
            b.button(text=t("a_btn_setdate", lang, name=name), callback_data=f"adm_setdate:{eq.id}")
    else:
        lines.append(t("a_card_no_equip", lang))
    b.adjust(1)
    b.row(
        InlineKeyboardButton(text=t("a_btn_pay", lang), callback_data=f"adm_pay:{uid}"),
        InlineKeyboardButton(text=t("a_btn_spend", lang), callback_data=f"adm_spend:{uid}"),
    )
    b.row(InlineKeyboardButton(text=t("a_btn_to_list", lang), callback_data="adm_users:0"))
    await cb.message.edit_text("\n".join(lines), reply_markup=b.as_markup())
    await cb.answer()


@router.callback_query(F.data.startswith("adm_setdate:"))
async def admin_set_date_start(cb: CallbackQuery, state: FSMContext, lang: str):
    eq_id = int(cb.data.split(":", 1)[1])
    await state.set_state(AdmState.set_date)
    await state.update_data(eq_id=eq_id)
    await cb.message.answer(t("a_ask_date", lang), reply_markup=cancel_kb(lang))
    await cb.answer()


@router.message(AdmState.set_date, NOT_MENU)
async def admin_set_date_apply(message: Message, state: FSMContext, lang: str):
    d = parse_date(message.text)
    if not d:
        await message.answer(t("a_bad_date", lang), reply_markup=cancel_kb(lang))
        return
    data = await state.get_data()
    await crud.set_next_service_date(data["eq_id"], d)
    await state.clear()
    await message.answer(
        t("a_date_updated", lang, date=fmt_date(d)),
        reply_markup=admin_menu_kb(lang, is_super_admin(message.from_user.id)),
    )


# ---------- Заявки ----------

@router.callback_query(F.data == "adm_reqs")
async def admin_requests(cb: CallbackQuery, lang: str):
    reqs = await crud.list_new_requests()
    if not reqs:
        b = InlineKeyboardBuilder()
        b.button(text=t("a_btn_menu", lang), callback_data="adm_home")
        await cb.message.edit_text(t("a_no_requests", lang), reply_markup=b.as_markup())
        await cb.answer()
        return
    b = InlineKeyboardBuilder()
    lines = [t("a_requests_title", lang)]
    for r in reqs:
        u = await crud.get_user(r.user_id)
        who = f"{u.full_name} ({u.phone})" if u else str(r.user_id)
        rtype = t(f"rtype_{r.type}", lang)
        lines.append(f"#{r.id} · {rtype} · {who}")
        b.button(text=t("a_btn_req_done", lang, id=r.id), callback_data=f"adm_reqdone:{r.id}")
    b.adjust(1)
    b.row(InlineKeyboardButton(text=t("a_btn_menu", lang), callback_data="adm_home"))
    await cb.message.edit_text("\n".join(lines), reply_markup=b.as_markup())
    await cb.answer()


async def _apply_payment(
    bot: Bot, user_id: int, amount: int, admin_id: int, request_id: int | None = None
) -> tuple[int, int]:
    """Учитывает оплату, начисляет бонус и рассылает уведомления. -> (delta, balance)."""
    delta, balance = await crud.add_payment(user_id, amount, admin_id, request_id=request_id)
    if delta > 0:
        user = await crud.get_user(user_id)
        ulang = user.lang if user else "ru"
        try:
            await bot.send_message(
                user_id,
                t("bonus_earned", ulang, delta=format_money(delta), balance=format_money(balance)),
            )
        except TelegramAPIError:
            pass
        await notify_admins(
            bot, "n_bonus_earned",
            name=user.full_name if user else str(user_id),
            delta=format_money(delta), amount=format_money(amount), balance=format_money(balance),
        )
    return delta, balance


@router.callback_query(F.data.startswith("adm_reqdone:"))
async def admin_request_done(cb: CallbackQuery, state: FSMContext, lang: str):
    req_id = int(cb.data.split(":", 1)[1])
    req = await crud.get_request(req_id)
    if not req:
        await admin_requests(cb, lang)
        await cb.answer()
        return
    await state.set_state(AdmState.req_amount)
    await state.update_data(req_id=req_id, req_user_id=req.user_id)
    b = InlineKeyboardBuilder()
    b.button(text=t("a_btn_no_pay", lang), callback_data="adm_req_nopay")
    b.button(text=t("btn_cancel", lang), callback_data="fsm_cancel")
    b.adjust(1)
    await cb.message.answer(t("a_ask_req_amount", lang), reply_markup=b.as_markup())
    await cb.answer()


async def _finish_request(message: Message, state: FSMContext, lang: str, amount: int | None):
    data = await state.get_data()
    await state.clear()
    await crud.mark_request_done(data["req_id"])
    if amount:
        delta, balance = await _apply_payment(
            message.bot, data["req_user_id"], amount, message.from_user.id, request_id=data["req_id"]
        )
        await message.answer(
            t("a_pay_done", lang, amount=format_money(amount),
              delta=format_money(delta), balance=format_money(balance)),
            reply_markup=admin_menu_kb(lang, is_super_admin(message.from_user.id)),
        )
    else:
        await message.answer(
            t("a_req_done_toast", lang),
            reply_markup=admin_menu_kb(lang, is_super_admin(message.from_user.id)),
        )


@router.callback_query(AdmState.req_amount, F.data == "adm_req_nopay")
async def admin_req_nopay(cb: CallbackQuery, state: FSMContext, lang: str):
    await cb.message.edit_reply_markup(reply_markup=None)
    await _finish_request(cb.message, state, lang, None)
    await cb.answer()


@router.message(AdmState.req_amount, NOT_MENU)
async def admin_req_amount(message: Message, state: FSMContext, lang: str):
    amount = parse_money(message.text)
    if amount is None:
        await message.answer(t("a_bad_amount", lang), reply_markup=cancel_kb(lang))
        return
    await _finish_request(message, state, lang, amount)


# ---------- Оплаты и списание бонусов (из карточки клиента) ----------

@router.callback_query(F.data.startswith("adm_pay:"))
async def admin_pay_start(cb: CallbackQuery, state: FSMContext, lang: str):
    uid = int(cb.data.split(":", 1)[1])
    await state.set_state(AdmState.pay_amount)
    await state.update_data(target_uid=uid)
    await cb.message.answer(t("a_ask_pay", lang), reply_markup=cancel_kb(lang))
    await cb.answer()


@router.message(AdmState.pay_amount, NOT_MENU)
async def admin_pay_apply(message: Message, state: FSMContext, lang: str):
    amount = parse_money(message.text)
    if amount is None or amount <= 0:
        await message.answer(t("a_bad_amount", lang), reply_markup=cancel_kb(lang))
        return
    data = await state.get_data()
    await state.clear()
    delta, balance = await _apply_payment(message.bot, data["target_uid"], amount, message.from_user.id)
    await message.answer(
        t("a_pay_done", lang, amount=format_money(amount),
          delta=format_money(delta), balance=format_money(balance)),
        reply_markup=admin_menu_kb(lang, is_super_admin(message.from_user.id)),
    )


@router.callback_query(F.data.startswith("adm_spend:"))
async def admin_spend_start(cb: CallbackQuery, state: FSMContext, lang: str):
    uid = int(cb.data.split(":", 1)[1])
    user = await crud.get_user(uid)
    balance = user.bonus_balance if user else 0
    await state.set_state(AdmState.spend_amount)
    await state.update_data(target_uid=uid)
    await cb.message.answer(t("a_ask_spend", lang, balance=format_money(balance)), reply_markup=cancel_kb(lang))
    await cb.answer()


@router.message(AdmState.spend_amount, NOT_MENU)
async def admin_spend_apply(message: Message, state: FSMContext, lang: str):
    amount = parse_money(message.text)
    if amount is None or amount <= 0:
        await message.answer(t("a_bad_amount", lang), reply_markup=cancel_kb(lang))
        return
    data = await state.get_data()
    await state.clear()
    uid = data["target_uid"]
    spent, balance = await crud.spend_bonus(uid, amount, message.from_user.id)
    if spent > 0:
        user = await crud.get_user(uid)
        ulang = user.lang if user else "ru"
        try:
            await message.bot.send_message(
                uid, t("bonus_spent", ulang, spent=format_money(spent), balance=format_money(balance))
            )
        except TelegramAPIError:
            pass
    await message.answer(
        t("a_spend_done", lang, spent=format_money(spent), balance=format_money(balance)),
        reply_markup=admin_menu_kb(lang, is_super_admin(message.from_user.id)),
    )


# ---------- Настройки ----------

def _cfg_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t("a_btn_time", lang), callback_data="adm_cfg_time")
    b.button(text=t("a_btn_stages", lang), callback_data="adm_cfg_stages")
    b.button(text=t("a_btn_contacts_cfg", lang), callback_data="adm_cfg_contacts")
    b.button(text=t("a_btn_workhours_cfg", lang), callback_data="adm_cfg_workhours")
    b.button(text=t("a_btn_bonus_cfg", lang), callback_data="adm_cfg_bonus")
    b.button(text=t("a_btn_menu", lang), callback_data="adm_home")
    b.adjust(1)
    return b.as_markup()


@router.callback_query(F.data == "adm_cfg")
async def admin_cfg(cb: CallbackQuery, state: FSMContext, lang: str):
    await state.clear()
    cfg = await crud.get_settings()
    text = t(
        "a_settings", lang,
        time=f"{cfg.reminder_hour:02d}:{cfg.reminder_minute:02d}",
        stages=cfg.reminder_stages,
        work_hours=cfg.work_hours,
        threshold=format_money(cfg.bonus_threshold),
        bonus=format_money(cfg.bonus_amount),
        contacts=cfg.contacts,
    )
    await cb.message.edit_text(text, reply_markup=_cfg_kb(lang))
    await cb.answer()


@router.callback_query(F.data == "adm_cfg_workhours")
async def admin_cfg_workhours(cb: CallbackQuery, state: FSMContext, lang: str):
    await state.set_state(AdmState.set_workhours)
    await cb.message.answer(t("a_ask_workhours", lang), reply_markup=cancel_kb(lang))
    await cb.answer()


@router.message(AdmState.set_workhours, NOT_MENU)
async def admin_cfg_workhours_apply(message: Message, state: FSMContext, lang: str):
    await crud.update_settings(work_hours=message.text.strip())
    await state.clear()
    await message.answer(
        t("a_workhours_set", lang),
        reply_markup=admin_menu_kb(lang, is_super_admin(message.from_user.id)),
    )


@router.callback_query(F.data == "adm_cfg_bonus")
async def admin_cfg_bonus(cb: CallbackQuery, state: FSMContext, lang: str):
    await state.set_state(AdmState.set_bonus_thr)
    await cb.message.answer(t("a_ask_bonus_thr", lang), reply_markup=cancel_kb(lang))
    await cb.answer()


@router.message(AdmState.set_bonus_thr, NOT_MENU)
async def admin_cfg_bonus_thr(message: Message, state: FSMContext, lang: str):
    thr = parse_money(message.text)
    if thr is None or thr <= 0:
        await message.answer(t("a_bad_amount", lang), reply_markup=cancel_kb(lang))
        return
    await state.update_data(bonus_thr=thr)
    await state.set_state(AdmState.set_bonus_amt)
    await message.answer(t("a_ask_bonus_amt", lang), reply_markup=cancel_kb(lang))


@router.message(AdmState.set_bonus_amt, NOT_MENU)
async def admin_cfg_bonus_amt(message: Message, state: FSMContext, lang: str):
    amt = parse_money(message.text)
    if amt is None or amt <= 0:
        await message.answer(t("a_bad_amount", lang), reply_markup=cancel_kb(lang))
        return
    data = await state.get_data()
    await state.clear()
    await crud.update_settings(bonus_threshold=data["bonus_thr"], bonus_amount=amt)
    await message.answer(
        t("a_bonus_cfg_set", lang, threshold=format_money(data["bonus_thr"]), bonus=format_money(amt)),
        reply_markup=admin_menu_kb(lang, is_super_admin(message.from_user.id)),
    )


@router.callback_query(F.data == "adm_cfg_time")
async def admin_cfg_time(cb: CallbackQuery, state: FSMContext, lang: str):
    await state.set_state(AdmState.set_time)
    await cb.message.answer(t("a_ask_time", lang), reply_markup=cancel_kb(lang))
    await cb.answer()


@router.message(AdmState.set_time, NOT_MENU)
async def admin_cfg_time_apply(message: Message, state: FSMContext, lang: str):
    raw = message.text.strip().replace(".", ":").replace("-", ":")
    parts = raw.split(":")
    try:
        hour, minute = int(parts[0]), int(parts[1])
        assert 0 <= hour <= 23 and 0 <= minute <= 59
    except (ValueError, IndexError, AssertionError):
        await message.answer(t("a_bad_time", lang))
        return
    await crud.update_settings(reminder_hour=hour, reminder_minute=minute)
    reschedule(hour, minute)
    await state.clear()
    await message.answer(
        t("a_time_set", lang, time=f"{hour:02d}:{minute:02d}"),
        reply_markup=admin_menu_kb(lang, is_super_admin(message.from_user.id)),
    )


@router.callback_query(F.data == "adm_cfg_stages")
async def admin_cfg_stages(cb: CallbackQuery, state: FSMContext, lang: str):
    await state.set_state(AdmState.set_stages)
    await cb.message.answer(t("a_ask_stages", lang), reply_markup=cancel_kb(lang))
    await cb.answer()


@router.message(AdmState.set_stages, NOT_MENU)
async def admin_cfg_stages_apply(message: Message, state: FSMContext, lang: str):
    stages = parse_stages(message.text)
    if not stages:
        await message.answer(t("a_bad_stages", lang))
        return
    normalized = ",".join(str(x) for x in stages)
    await crud.update_settings(reminder_stages=normalized)
    await state.clear()
    await message.answer(
        t("a_stages_set", lang, stages=normalized),
        reply_markup=admin_menu_kb(lang, is_super_admin(message.from_user.id)),
    )


@router.callback_query(F.data == "adm_cfg_contacts")
async def admin_cfg_contacts(cb: CallbackQuery, state: FSMContext, lang: str):
    await state.set_state(AdmState.set_contacts)
    await cb.message.answer(t("a_ask_contacts", lang), reply_markup=cancel_kb(lang))
    await cb.answer()


@router.message(AdmState.set_contacts, NOT_MENU)
async def admin_cfg_contacts_apply(message: Message, state: FSMContext, lang: str):
    await crud.update_settings(contacts=message.text.strip())
    await state.clear()
    await message.answer(
        t("a_contacts_set", lang),
        reply_markup=admin_menu_kb(lang, is_super_admin(message.from_user.id)),
    )


# ---------- Экспорт ----------

@router.callback_query(F.data == "adm_export")
async def admin_export(cb: CallbackQuery, lang: str):
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = t("a_sheet_title", lang)
    ws.append([
        t("a_col_name", lang), t("a_col_phone", lang), t("a_col_lang", lang),
        t("a_col_equipment", lang), t("a_col_model", lang),
        t("a_col_install", lang), t("a_col_service", lang),
    ])
    users = await crud.list_users(10000, 0)
    for u in users:
        items = await crud.list_user_equipment(u.telegram_id)
        if not items:
            ws.append([u.full_name, u.phone, u.lang, "", "", "", ""])
        for eq in items:
            ws.append([
                u.full_name, u.phone, u.lang, kind_label(eq.kind, lang), eq.model or "",
                fmt_date(eq.install_date), fmt_date(eq.next_service_date),
            ])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    await cb.message.answer_document(
        BufferedInputFile(buf.read(), filename="clients.xlsx"),
        caption=t("a_export_caption", lang),
    )
    await cb.answer()


async def _display_name(bot: Bot, tid: int) -> str:
    """«Имя (id)» для показа в списках. Имя — из БД, иначе из Telegram, иначе голый id."""
    u = await crud.get_user(tid)
    if u:
        return f"{u.full_name} ({tid})"
    try:
        chat = await bot.get_chat(tid)
        if chat.full_name:
            return f"{chat.full_name} ({tid})"
    except TelegramAPIError:
        pass
    return str(tid)


# ---------- Управление админами (только супер-админ) ----------

async def _show_admins(cb: CallbackQuery, lang: str) -> None:
    supers = settings.admin_ids_list
    db_admins = await crud.list_admins()
    lines = [t("a_admins_title", lang), t("a_supers", lang)]
    for sid in supers:
        lines.append(f"  • {await _display_name(cb.bot, sid)}")
    if not supers:
        lines.append("  —")
    lines.append(t("a_added_admins", lang))
    b = InlineKeyboardBuilder()
    if db_admins:
        for a in db_admins:
            name = await _display_name(cb.bot, a.telegram_id)
            lines.append(f"  • {name}")
            b.button(text=t("a_btn_del_admin", lang, id=name), callback_data=f"adm_admin_del:{a.telegram_id}")
    else:
        lines.append("  —")
    b.adjust(1)
    b.row(InlineKeyboardButton(text=t("a_btn_add_admin", lang), callback_data="adm_admin_add"))
    b.row(InlineKeyboardButton(text=t("a_btn_menu", lang), callback_data="adm_home"))
    await cb.message.edit_text("\n".join(lines), reply_markup=b.as_markup())


@router.callback_query(F.data == "adm_admins")
async def admin_admins(cb: CallbackQuery, state: FSMContext, lang: str):
    if not is_super_admin(cb.from_user.id):
        await cb.answer(t("a_super_only", lang), show_alert=True)
        return
    await state.clear()
    await _show_admins(cb, lang)
    await cb.answer()


@router.callback_query(F.data == "adm_admin_add")
async def admin_admin_add(cb: CallbackQuery, state: FSMContext, lang: str):
    if not is_super_admin(cb.from_user.id):
        await cb.answer(t("a_super_only", lang), show_alert=True)
        return
    await state.set_state(AdmState.add_admin)
    await cb.message.answer(t("a_ask_admin_id", lang), reply_markup=cancel_kb(lang))
    await cb.answer()


@router.message(AdmState.add_admin, NOT_MENU)
async def admin_admin_add_apply(message: Message, state: FSMContext, lang: str):
    if not is_super_admin(message.from_user.id):
        await state.clear()
        return
    raw = message.text.strip()
    if not raw.lstrip("-").isdigit():
        await message.answer(t("a_bad_admin_id", lang), reply_markup=cancel_kb(lang))
        return
    new_id = int(raw)
    if is_super_admin(new_id):
        await message.answer(t("a_already_super", lang))
    else:
        await crud.add_admin(new_id, message.from_user.id)
        await message.answer(t("a_admin_added", lang, id=new_id))
    await state.clear()
    await message.answer(t("a_panel_title", lang), reply_markup=admin_menu_kb(lang, True))


@router.callback_query(F.data.startswith("adm_admin_del:"))
async def admin_admin_del(cb: CallbackQuery, lang: str):
    if not is_super_admin(cb.from_user.id):
        await cb.answer(t("a_super_only", lang), show_alert=True)
        return
    del_id = int(cb.data.split(":", 1)[1])
    await crud.remove_admin(del_id)
    await cb.answer(t("a_admin_removed", lang))
    await _show_admins(cb, lang)


# ---------- Мастера ----------

async def _show_masters(cb: CallbackQuery, lang: str) -> None:
    masters = await crud.list_masters()
    lines = [t("a_masters_title", lang)]
    b = InlineKeyboardBuilder()
    if masters:
        for m in masters:
            lines.append(f"  • {m.name} — {kind_label(m.kind, lang)} (id {m.telegram_id})")
            b.button(
                text=t("a_btn_del_master", lang, name=m.name),
                callback_data=f"adm_master_del:{m.id}",
            )
    else:
        lines.append("  —")
    b.adjust(1)
    b.row(InlineKeyboardButton(text=t("a_btn_add_master", lang), callback_data="adm_master_add"))
    b.row(InlineKeyboardButton(text=t("a_btn_menu", lang), callback_data="adm_home"))
    await cb.message.edit_text("\n".join(lines), reply_markup=b.as_markup())


@router.callback_query(F.data == "adm_masters")
async def admin_masters(cb: CallbackQuery, state: FSMContext, lang: str):
    await state.clear()
    await _show_masters(cb, lang)
    await cb.answer()


@router.callback_query(F.data == "adm_master_add")
async def admin_master_add(cb: CallbackQuery, state: FSMContext, lang: str):
    from services.access import all_admin_ids

    await state.set_state(AdmState.add_master_id)
    # кнопками — существующие админы, либо ввод произвольного ID текстом
    b = InlineKeyboardBuilder()
    for tid in await all_admin_ids():
        b.button(text=await _display_name(cb.bot, tid), callback_data=f"adm_master_pick:{tid}")
    b.adjust(1)
    b.row(InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="fsm_cancel"))
    await cb.message.answer(t("a_ask_master_id", lang), reply_markup=b.as_markup())
    await cb.answer()


@router.callback_query(AdmState.add_master_id, F.data.startswith("adm_master_pick:"))
async def admin_master_pick(cb: CallbackQuery, state: FSMContext, lang: str):
    tid = int(cb.data.split(":", 1)[1])
    await state.update_data(master_id=tid)
    await cb.message.edit_reply_markup(reply_markup=None)
    # имя — из БД или из Telegram; если нашли — сразу к выбору вида
    name = None
    u = await crud.get_user(tid)
    if u:
        name = u.full_name
    else:
        try:
            chat = await cb.bot.get_chat(tid)
            name = chat.full_name
        except TelegramAPIError:
            pass
    if name:
        await state.update_data(master_name=name)
        await state.set_state(AdmState.add_master_kind)
        await cb.message.answer(t("a_ask_master_kind", lang), reply_markup=kinds_kb(lang))
    else:
        await state.set_state(AdmState.add_master_name)
        await cb.message.answer(t("a_ask_master_name", lang), reply_markup=cancel_kb(lang))
    await cb.answer()


@router.message(AdmState.add_master_id, NOT_MENU)
async def admin_master_id(message: Message, state: FSMContext, lang: str):
    raw = message.text.strip()
    if not raw.lstrip("-").isdigit():
        await message.answer(t("a_bad_admin_id", lang), reply_markup=cancel_kb(lang))
        return
    await state.update_data(master_id=int(raw))
    await state.set_state(AdmState.add_master_name)
    await message.answer(t("a_ask_master_name", lang), reply_markup=cancel_kb(lang))


@router.message(AdmState.add_master_name, NOT_MENU)
async def admin_master_name(message: Message, state: FSMContext, lang: str):
    await state.update_data(master_name=message.text.strip())
    await state.set_state(AdmState.add_master_kind)
    await message.answer(t("a_ask_master_kind", lang), reply_markup=kinds_kb(lang))


async def _finish_master(message: Message, state: FSMContext, lang: str, kind: str, user_id: int):
    data = await state.get_data()
    added = await crud.add_master(data["master_id"], data["master_name"], kind)
    await state.clear()
    if added:
        await message.answer(t("a_master_added", lang, name=data["master_name"]))
    else:
        await message.answer(t("a_master_exists", lang))
    await message.answer(t("a_panel_title", lang), reply_markup=admin_menu_kb(lang, is_super_admin(user_id)))


@router.callback_query(AdmState.add_master_kind, F.data.startswith("kind:"))
async def admin_master_kind_cb(cb: CallbackQuery, state: FSMContext, lang: str):
    kind = cb.data.split(":", 1)[1]
    await cb.message.edit_reply_markup(reply_markup=None)
    await _finish_master(cb.message, state, lang, kind, cb.from_user.id)
    await cb.answer()


@router.callback_query(AdmState.add_master_kind, F.data == "kind_other")
async def admin_master_kind_other(cb: CallbackQuery, lang: str):
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(t("ask_kind_custom", lang), reply_markup=cancel_kb(lang))
    await cb.answer()


@router.message(AdmState.add_master_kind, NOT_MENU)
async def admin_master_kind_text(message: Message, state: FSMContext, lang: str):
    await _finish_master(message, state, lang, message.text.strip(), message.from_user.id)


@router.callback_query(F.data.startswith("adm_master_del:"))
async def admin_master_del(cb: CallbackQuery, lang: str):
    # первый тап — подтверждение, само удаление в adm_master_delok
    master_id = int(cb.data.split(":", 1)[1])
    m = await crud.get_master(master_id)
    if not m:
        await _show_masters(cb, lang)
        await cb.answer()
        return
    b = InlineKeyboardBuilder()
    b.button(text=t("btn_confirm_yes", lang), callback_data=f"adm_master_delok:{master_id}")
    b.button(text=t("btn_cancel", lang), callback_data="adm_masters")
    b.adjust(2)
    await cb.message.edit_text(
        t("a_confirm_del_master", lang, name=m.name), reply_markup=b.as_markup()
    )
    await cb.answer()


@router.callback_query(F.data.startswith("adm_master_delok:"))
async def admin_master_delok(cb: CallbackQuery, lang: str):
    master_id = int(cb.data.split(":", 1)[1])
    await crud.remove_master(master_id)
    await cb.answer(t("a_master_removed", lang))
    await _show_masters(cb, lang)
