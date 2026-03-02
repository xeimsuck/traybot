from datetime import UTC, datetime

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import config
from database.requests import get_user_by_tg_id
from utils.math import get_daily_cost

router = Router()

@router.callback_query(F.data.startswith("top_up"))
async def top_up(callback: types.CallbackQuery):
    splited = callback.data.split("_")
    back_callback_data = "profile" if splited[-1]=="profile" else "to_main"

    user = await get_user_by_tg_id(callback.from_user.id)
    if not user:
        return await callback.answer("Ошибка пользователя")

    devices = user.devices
    total_devices = len(devices)
    active_devices = sum(1 for d in devices if d.is_active)

    daily_cost = get_daily_cost(total_devices)

    builder = InlineKeyboardBuilder()

    text = (
        f"💰 Баланс: `{round(user.balance, 2)}₽`\n"
        f"📈 Ежедневный расход: `~{round(daily_cost, 2)}₽/день`\n"
        f"🔑 Активно устройств: {active_devices} из {max(total_devices, 3)}\n\n"
        f"✅ Пополните баланс ниже"
    )

    new_media = InputMediaPhoto(
        media=f"{config.assets_url}/img/menu_top-up.png",
        caption=text,
        parse_mode="Markdown"
    )

    builder.row(types.InlineKeyboardButton(text="💸 Пополнить баланс", url="https://t.me/trayvpn_help"))
    builder.row(types.InlineKeyboardButton(text="↩️ Вернуться назад", callback_data=back_callback_data))

    await callback.message.edit_media(
        media=new_media,
        reply_markup=builder.as_markup(),
    )




@router.callback_query(F.data.startswith("pay_cardlink_"))
async def top_up_cardlink(callback: types.CallbackQuery, state: FSMContext):
    return