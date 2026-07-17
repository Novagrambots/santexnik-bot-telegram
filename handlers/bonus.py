from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db import crud
from db.models import User
from i18n import t
from services.loyalty import format_money, progress_to_next

router = Router()


@router.message(F.text.in_({t("btn_my_bonuses", "ru"), t("btn_my_bonuses", "uz")}))
async def my_bonuses(message: Message, state: FSMContext, user: User | None):
    await state.clear()
    if not user:
        await message.answer(t("not_registered"))
        return
    cfg = await crud.get_settings()
    left = progress_to_next(user.total_paid, cfg.bonus_threshold)
    await message.answer(
        t(
            "bonus_screen", user.lang,
            balance=format_money(user.bonus_balance),
            paid=format_money(user.total_paid),
            bonus=format_money(cfg.bonus_amount),
            left=format_money(left),
        )
    )
