from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from contextlib import suppress

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from db import crud
from db.models import User
from i18n import t
from keyboards.common import NOT_MENU, lang_kb, main_menu_kb, phone_kb
from services.access import is_admin, is_super_admin

router = Router()


def _back_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t("a_btn_back", lang), callback_data="reg_restart")]]
    )


async def send_main_menu(message: Message, lang: str, admin: bool) -> None:
    await message.answer(t("main_menu", lang), reply_markup=main_menu_kb(lang, admin))


class Reg(StatesGroup):
    lang = State()
    name = State()
    phone = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, user: User | None):
    await state.clear()
    admin = await is_admin(message.from_user.id)
    if user:
        # уже зарегистрирован — сразу в меню, заодно снимаем флаг блокировки
        await crud.set_user_active(user.telegram_id, True)
        await send_main_menu(message, user.lang, admin)
        return
    if admin:
        # админа не гоняем через анкету — заводим тихо и сразу в меню + вход в панель
        await crud.create_user(message.from_user.id, message.from_user.full_name, None, "ru")
        await send_main_menu(message, "ru", True)
        return
    await state.set_state(Reg.lang)
    await message.answer(t("choose_lang"), reply_markup=lang_kb())


@router.callback_query(Reg.lang, F.data.startswith("lang:"))
async def reg_lang(cb: CallbackQuery, state: FSMContext):
    lang = cb.data.split(":", 1)[1]
    await state.update_data(lang=lang)
    await state.set_state(Reg.name)
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(t("ask_name", lang), reply_markup=_back_kb(lang))
    await cb.answer()


@router.callback_query(F.data == "reg_restart")
async def reg_restart(cb: CallbackQuery, state: FSMContext):
    # «Назад» в регистрации — возврат к выбору языка
    await state.clear()
    await state.set_state(Reg.lang)
    with suppress(TelegramBadRequest):
        await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(t("choose_lang"), reply_markup=lang_kb())
    await cb.answer()


@router.message(Reg.name, NOT_MENU)
async def reg_name(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    await state.update_data(name=message.text.strip())
    await state.set_state(Reg.phone)
    await message.answer(t("ask_phone", lang), reply_markup=phone_kb(lang))


@router.message(Reg.phone, F.contact)
async def reg_phone_contact(message: Message, state: FSMContext):
    await _finish_registration(message, state, message.contact.phone_number)


@router.message(Reg.phone, NOT_MENU)
async def reg_phone_text(message: Message, state: FSMContext):
    # разрешаем ввести номер вручную, если не нажали кнопку
    await _finish_registration(message, state, message.text.strip())


async def _finish_registration(message: Message, state: FSMContext, phone: str):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    name = data.get("name", message.from_user.full_name)
    await crud.create_user(message.from_user.id, name, phone, lang)
    await state.clear()
    await message.answer(t("registered", lang, name=name), reply_markup=ReplyKeyboardRemove())
    await send_main_menu(message, lang, await is_admin(message.from_user.id))


# --- Смена языка из меню ---

@router.message(F.text.in_({t("btn_change_lang", "ru"), t("btn_change_lang", "uz")}))
async def change_lang(message: Message, state: FSMContext, user: User | None):
    await state.clear()
    if not user:
        await message.answer(t("not_registered"))
        return
    await message.answer(t("choose_lang"), reply_markup=lang_kb())


@router.callback_query(F.data == "fsm_cancel")
async def fsm_cancel(cb: CallbackQuery, state: FSMContext, lang: str):
    """Универсальная отмена любого FSM-потока (кнопка «❌ Отмена»)."""
    current = await state.get_state()
    await state.clear()
    with suppress(TelegramBadRequest):
        await cb.message.edit_reply_markup(reply_markup=None)
    admin = await is_admin(cb.from_user.id)
    if admin and current and (current.startswith("AdmState") or current.startswith("BC")):
        # отменили админский поток — возвращаем в админ-панель
        from handlers.admin import admin_menu_kb

        await cb.message.answer(
            t("a_panel_title", lang), reply_markup=admin_menu_kb(lang, is_super_admin(cb.from_user.id))
        )
    else:
        await cb.message.answer(t("cancelled", lang))
        await send_main_menu(cb.message, lang, admin)
    await cb.answer()


@router.callback_query(F.data.startswith("lang:"))
async def switch_lang(cb: CallbackQuery, user: User | None):
    # смена языка уже зарегистрированным пользователем (вне FSM регистрации)
    if not user:
        await cb.answer()
        return
    lang = cb.data.split(":", 1)[1]
    await crud.set_user_lang(user.telegram_id, lang)
    await cb.message.edit_reply_markup(reply_markup=None)
    await send_main_menu(cb.message, lang, await is_admin(cb.from_user.id))
    await cb.answer()
