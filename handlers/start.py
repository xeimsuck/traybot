from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InputMediaPhoto

from config import config
import keyboards
from database.requests import create_user, add_referral_bonus

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    args = message.text.split()

    inviter_id = None
    if len(args) > 1 and args[1].startswith("invite_"):
        inviter_id = int(args[1][7:])
        inviter_id = None if inviter_id==message.from_user.id else inviter_id

    is_new = await create_user(message.from_user.id, message.from_user.username, inviter_id)

    text = (
        f"Приветствуем тебя, {message.from_user.first_name}! 👋\n\n"
        f"⚡️ TRAY VPN - ваше лучшее VPN-решение"
    )

    if is_new:
        text+="\n\n🎁 Вам начислена пробная подписка на 3 дня! Проверьте в разделе 'Подключиться'."
        if inviter_id:
            await add_referral_bonus(inviter_id, referred_id=message.from_user.id)
    else:
        text+=f"\n\n🎁 Для новых пользователей мы дарим 3 дня бесплатного доступа"


    await message.answer_photo(
        photo=f"{config.assets_url}/img/menu_tray-vpn.png?v=070326",
        caption=text,
        reply_markup = keyboards.get_main_keyboard()
    )


@router.callback_query(F.data == "to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.answer()

    text = (
        f"Приветствуем тебя, {callback.from_user.first_name}! 👋\n\n"
        f"⚡️ TRAY VPN - ваше лучшее VPN-решение\n\n"
        f"🎁 Для новых пользователей мы дарим 3 дня бесплатного доступа"
    )

    new_media = InputMediaPhoto(
        media=f"{config.assets_url}/img/menu_tray-vpn.png?v=070326",
        caption=text,
        parse_mode="HTML"
    )

    await callback.message.edit_media(
        media=new_media,
        reply_markup=keyboards.get_main_keyboard()
    )



@router.message(Command("policy"))
async def cmd_privacy(message: types.Message):
    await message.answer(
        "Политика конфиденциальности: https://docs.google.com/document/d/1BkSJG3-AAIQC74ATA71jHetT9cx4k8cBWMnUBqY0Y4g/edit?usp=sharing"
    )

@router.message(Command("terms"))
async def cmd_terms(message: types.Message):
    await message.answer(
        "Пользовательское соглашение: https://docs.google.com/document/d/1Sn7KRvFeaCg1J_eJLMnbCRk-qRYdvWsnJIevPuepUEE/edit?usp=sharing"
    )

@router.message(Command("support"))
async def cmd_terms(message: types.Message):
    await message.answer(
        "Возникли трудности? Свяжитесь с нашей тех.поддержкой @trayvpn_help"
    )