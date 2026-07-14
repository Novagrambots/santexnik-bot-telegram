from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import crud
from db.models import User
from i18n import kind_label, t
from keyboards.common import cancel_btn, confirm_request_kb
from services.notify import notify_admins, notify_masters

router = Router()

# код заявки -> (тип в БД, ключ текста «отправлено», ключ уведомления админам)
REQUESTS = {
    "master": ("вызов", "master_request_sent", "n_master"),
    "emergency": ("авария", "emergency_sent", "n_emergency"),
}


# ---------- Вызов мастера (выбор по виду оборудования) ----------

@router.message(F.text.in_({t("btn_call_master", "ru"), t("btn_call_master", "uz")}))
async def call_master(message: Message, state: FSMContext, user: User | None):
    await state.clear()
    if not user:
        await message.answer(t("not_registered"))
        return
    masters = await crud.list_masters()
    if not masters:
        # мастеров нет — обычный общий вызов с подтверждением
        await message.answer(
            t("confirm_master", user.lang), reply_markup=confirm_request_kb(user.lang, "master")
        )
        return
    # один пункт на вид оборудования, без имён мастеров и без дублей
    kinds_seen: dict[str, int] = {}
    for m in masters:
        kinds_seen.setdefault(m.kind, m.id)
    b = InlineKeyboardBuilder()
    for kind, master_id in kinds_seen.items():
        b.button(text=kind_label(kind, user.lang), callback_data=f"req_kind:{master_id}")
    b.button(text=t("btn_any_master", user.lang), callback_data="req_kind:0")
    b.adjust(1)
    b.row(cancel_btn(user.lang))
    await message.answer(t("choose_master", user.lang), reply_markup=b.as_markup())


@router.callback_query(F.data.startswith("req_kind:"))
async def req_kind_chosen(cb: CallbackQuery, user: User | None, lang: str):
    if not user:
        await cb.answer()
        return
    master_id = int(cb.data.split(":", 1)[1])
    master = await crud.get_master(master_id) if master_id else None
    with suppress(TelegramBadRequest):
        await cb.message.edit_reply_markup(reply_markup=None)
    if master:
        # алерт всем мастерам этого вида + супер-админам (всегда)
        await crud.create_request(user.telegram_id, "вызов", comment=f"вид: {master.kind}")
        await cb.message.answer(t("master_request_sent", user.lang))
        await notify_masters(
            cb.bot, "n_master_kind", master.kind,
            name=user.full_name, phone=user.phone or "—", id=user.telegram_id,
        )
    else:
        # «Любой мастер» (или мастера уже удалили) — общий вызов всем админам
        await crud.create_request(user.telegram_id, "вызов")
        await cb.message.answer(t("master_request_sent", user.lang))
        await notify_admins(
            cb.bot, "n_master",
            name=user.full_name, phone=user.phone or "—", id=user.telegram_id,
        )
    await cb.answer()


# ---------- Аварийная заявка (с подтверждением) ----------

@router.message(F.text.in_({t("btn_emergency", "ru"), t("btn_emergency", "uz")}))
async def emergency(message: Message, state: FSMContext, user: User | None):
    await state.clear()
    if not user:
        await message.answer(t("not_registered"))
        return
    await message.answer(
        t("confirm_emergency", user.lang), reply_markup=confirm_request_kb(user.lang, "emergency")
    )


@router.callback_query(F.data == "req_cancel")
async def req_cancel(cb: CallbackQuery, lang: str):
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(t("cancelled", lang))
    await cb.answer()


@router.callback_query(F.data.startswith("req_ok:"))
async def req_confirm(cb: CallbackQuery, user: User | None):
    if not user:
        await cb.answer()
        return
    code = cb.data.split(":", 1)[1]
    meta = REQUESTS.get(code)
    if not meta:
        await cb.answer()
        return
    type_, sent_key, notify_key = meta
    await crud.create_request(user.telegram_id, type_)
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(t(sent_key, user.lang))
    await notify_admins(
        cb.bot, notify_key,
        name=user.full_name, phone=user.phone or "—", id=user.telegram_id,
    )
    await cb.answer()


# ---------- Контакты ----------

@router.message(F.text.in_({t("btn_contacts", "ru"), t("btn_contacts", "uz")}))
async def contacts(message: Message, state: FSMContext):
    await state.clear()
    cfg = await crud.get_settings()
    await message.answer(cfg.contacts)
