from aiogram import Router, types, F
from aiogram.types import InputMediaPhoto

from config import config
import keyboards
from database.requests import get_user_by_tg_id

router = Router()

@router.callback_query(F.data == "profile")
async def show_profile(callback: types.CallbackQuery):
    await callback.answer()

    user = await get_user_by_tg_id(callback.from_user.id)

    text = (
        f"**📃 Информация об аккаунте**\n"
        f"├ Уникальный ID: {user.tg_id}\n"
        f"├ Баланс: {user.balance}₽\n"
        f"└ Подключено устройств: {len(user.devices)}шт.\n"
        f"\n"
        f"**🎁 Ваша реферальная ссылка**\n"
        f"└ https://t.me/trayvpn\\_bot?start=invite\\_{user.tg_id}\n"
        f"\n"
        f"👆 Скопируй ее и поделись с друзьями для получения бонусов"
    )

    new_media = InputMediaPhoto(
        media=f"{config.assets_url}/img/menu_cabinet.png",
        caption=text,
        parse_mode="Markdown"
    )

    await callback.message.edit_media(
        media=new_media,
        reply_markup=keyboards.get_profile_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "bonus_system")
async def bonus_system(callback: types.CallbackQuery):
    await callback.answer()

    user = await get_user_by_tg_id(callback.from_user.id)

    text = (
        f"🤝 Реферальная система\n\n"
        f"💸 Приглашайте друзей и зарабатывайте:\n"
        f"├ За каждого приглашенного вы получаете 7 дней\n"
        f"├ 50% от пополнений рефералов\n"
        f"└ Другу 3 дня бесплатно\n"
        f"\n"
        f"🔗 Ваша реферальная ссылка\n"
        f"└ https://t.me/trayvpn\\_bot?start=invite\\_{user.tg_id}\n"
        f"\n"
        f"📊 Статистика:\n"
        f"└ Приглашено рефералов: {user.invited_count}\n"
        f"\n"
        f"К выводу доступы 50% от заработка с рефералов"
    )

    new_media = InputMediaPhoto(
        media=f"{config.assets_url}/img/menu_bonus-system.png",
        caption=text,
        parse_mode="Markdown"
    )

    await callback.message.edit_media(
        media=new_media,
        reply_markup=keyboards.get_back_to_profile_keyboard(),
        parse_mode="Markdown"
    )