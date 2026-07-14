from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import crud
from i18n import kind_label, t
from keyboards.common import KIND_CODES, MENU_TEXTS, cancel_kb
from services.access import IsAdmin
from services.broadcast import run_broadcast

router = Router()

# доступ только у админов (супер + из БД)
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

SEGMENTS = [
    ("all", "bc_seg_all"),
    ("overdue", "bc_seg_overdue"),
    ("lang:ru", "bc_seg_lang_ru"),
    ("lang:uz", "bc_seg_lang_uz"),
]


class BC(StatesGroup):
    content = State()
    confirm = State()


def segments_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for code, key in SEGMENTS:
        b.button(text=t(key, lang), callback_data=f"bcseg:{code}")
    for kind in KIND_CODES:
        b.button(text=t("bc_kind_prefix", lang, kind=kind_label(kind, lang)), callback_data=f"bcseg:kind:{kind}")
    b.adjust(2)
    b.row()
    b.button(text=t("bc_cancel", lang), callback_data="adm_home")
    return b.as_markup()


@router.callback_query(F.data == "adm_bc")
async def bc_start(cb: CallbackQuery, state: FSMContext, lang: str):
    await state.clear()
    await cb.message.edit_text(t("bc_choose", lang), reply_markup=segments_kb(lang))
    await cb.answer()


@router.callback_query(F.data.startswith("bcseg:"))
async def bc_segment(cb: CallbackQuery, state: FSMContext, lang: str):
    segment = cb.data.split(":", 1)[1]  # all / overdue / lang:ru / kind:boiler
    recipients = await crud.get_recipients(segment)
    if not recipients:
        await cb.answer(t("bc_no_recipients", lang), show_alert=True)
        return
    await state.update_data(segment=segment, count=len(recipients))
    await state.set_state(BC.content)
    await cb.message.edit_text(
        t("bc_ask_content", lang, n=len(recipients)), reply_markup=cancel_kb(lang)
    )
    await cb.answer()


@router.message(BC.content, ~F.text.in_(MENU_TEXTS))
async def bc_content(message: Message, state: FSMContext, lang: str):
    await state.update_data(from_chat_id=message.chat.id, message_id=message.message_id)
    await state.set_state(BC.confirm)
    data = await state.get_data()
    b = InlineKeyboardBuilder()
    b.button(text=t("bc_send", lang), callback_data="bc_confirm")
    b.button(text=t("bc_cancel2", lang), callback_data="adm_home")
    b.adjust(2)
    await message.answer(t("bc_preview", lang, n=data["count"]), reply_markup=b.as_markup())


@router.callback_query(BC.confirm, F.data == "bc_confirm")
async def bc_confirm(cb: CallbackQuery, state: FSMContext, lang: str):
    data = await state.get_data()
    await state.clear()
    segment = data["segment"]
    recipients = await crud.get_recipients(segment)
    await cb.message.edit_text(t("bc_sending", lang, n=len(recipients)))
    sent, failed = await run_broadcast(
        cb.bot, [u.telegram_id for u in recipients], data["from_chat_id"], data["message_id"]
    )
    await crud.log_broadcast(cb.from_user.id, segment, sent, failed)
    await cb.message.answer(t("bc_done", lang, sent=sent, failed=failed))
    await cb.answer()
