from aiogram import F
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from i18n import t

# коды видов оборудования; названия берутся из i18n (kind_<код>)
KIND_CODES = ["boiler", "water_heater", "water_filter", "pump", "radiators"]
PERIODS = [(6, "period_6"), (12, "period_12")]

# тексты кнопок главного меню (оба языка) — FSM-шаги не должны съедать их как ввод
_MENU_BUTTON_KEYS = [
    "btn_my_equipment", "btn_add_equipment", "btn_call_master",
    "btn_emergency", "btn_contacts", "btn_my_bonuses", "btn_change_lang", "btn_admin_panel",
]
MENU_TEXTS = {t(key, lng) for key in _MENU_BUTTON_KEYS for lng in ("ru", "uz")}

# фильтр для текстовых шагов FSM: любой текст, кроме кнопок главного меню
NOT_MENU = F.text & ~F.text.in_(MENU_TEXTS)


def cancel_btn(lang: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="fsm_cancel")


def cancel_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[cancel_btn(lang)]])


def lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
            InlineKeyboardButton(text="🇺🇿 O‘zbek", callback_data="lang:uz"),
        ]]
    )


def phone_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("btn_share_phone", lang), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def main_menu_kb(lang: str, admin: bool = False) -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.button(text=t("btn_my_equipment", lang))
    b.button(text=t("btn_add_equipment", lang))
    b.button(text=t("btn_call_master", lang))
    b.button(text=t("btn_emergency", lang))
    b.button(text=t("btn_contacts", lang))
    b.button(text=t("btn_my_bonuses", lang))
    b.button(text=t("btn_change_lang", lang))
    layout = [2, 2, 2, 1]
    if admin:
        b.button(text=t("btn_admin_panel", lang))
        layout.append(1)
    b.adjust(*layout)
    return b.as_markup(resize_keyboard=True)


def kinds_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for code in KIND_CODES:
        b.button(text=t(f"kind_{code}", lang), callback_data=f"kind:{code}")
    b.adjust(2)
    # отдельной строкой — вариант «нет в списке, напишу сам»
    b.row(InlineKeyboardButton(text=t("btn_kind_other", lang), callback_data="kind_other"))
    b.row(cancel_btn(lang))
    return b.as_markup()


def confirm_request_kb(lang: str, type_: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text=t("btn_confirm_yes", lang), callback_data=f"req_ok:{type_}"),
            InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="req_cancel"),
        ]]
    )


def skip_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_skip", lang), callback_data="skip_model")],
            [cancel_btn(lang)],
        ]
    )


def period_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for months, key in PERIODS:
        b.button(text=t(key, lang), callback_data=f"period:{months}")
    b.adjust(1)
    b.row(cancel_btn(lang))
    return b.as_markup()


def equipment_item_kb(lang: str, equipment_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text=t("btn_delete", lang), callback_data=f"eqdel:{equipment_id}")
        ]]
    )


def reminder_kb(lang: str, equipment_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t("btn_book", lang), callback_data=f"rem_book:{equipment_id}")
    b.button(text=t("btn_done", lang), callback_data=f"rem_done:{equipment_id}")
    b.button(text=t("btn_postpone", lang), callback_data=f"rem_postpone:{equipment_id}")
    b.adjust(1)
    return b.as_markup()


def postpone_kb(lang: str, equipment_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t("postpone_7", lang), callback_data=f"pp:{equipment_id}:7")
    b.button(text=t("postpone_30", lang), callback_data=f"pp:{equipment_id}:30")
    b.adjust(2)
    b.row(cancel_btn(lang))
    return b.as_markup()
