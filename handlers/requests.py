from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from db import crud
from db.models import User
from i18n import t
from keyboards.common import confirm_request_kb
from services.notify import notify_admins

router = Router()

# код заявки -> (тип в БД, ключ текста «отправлено», ключ уведомления админам)
REQUESTS = {
    "master": ("вызов", "master_request_sent", "n_master"),
    "emergency": ("авария", "emergency_sent", "n_emergency"),
}


@router.message(F.text.in_({t("btn_call_master", "ru"), t("btn_call_master", "uz")}))
async def call_master(message: Message, user: User | None):
    if not user:
        await message.answer(t("not_registered"))
        return
    await message.answer(t("confirm_master", user.lang), reply_markup=confirm_request_kb(user.lang, "master"))


@router.message(F.text.in_({t("btn_emergency", "ru"), t("btn_emergency", "uz")}))
async def emergency(message: Message, user: User | None):
    if not user:
        await message.answer(t("not_registered"))
        return
    await message.answer(t("confirm_emergency", user.lang), reply_markup=confirm_request_kb(user.lang, "emergency"))


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


@router.message(F.text.in_({t("btn_contacts", "ru"), t("btn_contacts", "uz")}))
async def contacts(message: Message):
    cfg = await crud.get_settings()
    await message.answer(cfg.contacts)
