import html

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import config
import keyboards
from database.requests import get_user_by_tg_id, get_device_by_id, rename_custom_device_name, create_new_device, \
    delete_device_by_id, update_user_balance
from keyboards import get_top_up_list_keyboard
from marzban_api import marzban_api
from states import RenameDevice

router = Router()

install_link = {
    "android": "https://play.google.com/store/apps/details?id=app.hiddify.com",
    "ios": "https://apps.apple.com/us/app/hiddify-proxy-vpn/id6596777532",
    "macos": "https://apps.apple.com/us/app/hiddify-proxy-vpn/id6596777532",
    "windows": "https://github.com/hiddify/hiddify-next/releases/latest/download/Hiddify-Windows-Setup-x64.exe",
    "linux": "https://github.com/Happ-proxy/happ-desktop/releases/latest/download/Happ.linux.x64.deb",
}




# --- 1. ГЛАВНОЕ МЕНЮ УСТРОЙСТВ ---
@router.callback_query(F.data == "devices")
async def show_devices(callback: types.CallbackQuery):
    user = await get_user_by_tg_id(callback.from_user.id)
    if not user:
        return await callback.answer("Ошибка пользователя")

    devices = user.devices
    total_devices = len(devices)
    active_devices = sum(1 for d in devices if d.is_active)

    one_day_price = config.one_day_price
    additional_device_price = config.additional_device_price

    # Математика списаний
    if total_devices == 0:
        daily_cost = 0.0
    elif total_devices <= 3:
        daily_cost = one_day_price / 30.0
    else:
        daily_cost = (one_day_price + (total_devices - 3) * additional_device_price) / 30.0

    text = (
        f"💰 Баланс: `{round(user.balance, 2)}₽`\n"
        f"📈 Ежедневный расход: `~{round(daily_cost, 2)}₽/день`\n"
        f"🔑 Активно устройств: {active_devices} из {max(total_devices, 3)}\n\n"
        f"ℹ️ Первые 3 устройства стоят 149₽/мес. Каждое следующее +100₽/мес.\n\n"
    )

    new_media = InputMediaPhoto(
        media=f"{config.assets_url}/img/menu_connect.png?v=070326",
        caption=text,
        parse_mode="HTML"
    )

    await callback.message.edit_media(
        media=new_media,
        reply_markup=keyboards.get_devices_keyboard(devices),
    )


# --- 2. ИНФОРМАЦИЯ ОБ УСТРОЙСТВЕ (КЛЮЧ) ---
@router.callback_query(F.data.startswith("dev_info_"))
async def show_device_details(callback: types.CallbackQuery):
    dev_id = int(callback.data.split("_")[-1])
    device = await get_device_by_id(dev_id)

    if not device or device.user.tg_id != callback.from_user.id:
        return await callback.answer("😢 Устройство не найдено.", show_alert=True)

    # Получаем данные из Marzban
    try:
        marzban_data = await marzban_api.get_user(device.marzban_username)
        status = "Активно 🟢" if marzban_data['status'] == 'active' else "Заблокировано 🔴"
        used_gb = round(marzban_data['used_traffic'] / (1024 ** 3), 2)
        sub_url = marzban_data.get('subscription_url')
        if sub_url and not sub_url.startswith('http'):
            sub_url = f"{config.marzban_url.get_secret_value()}{sub_url}#TrayVPN"

    except Exception:
        status = "Ошибка связи с сервером, попробуйте Обновить ⚠️"
        used_gb = 0
        sub_url = "Недоступно"

    safe_device_name = html.escape(device.custom_name)
    safe_sub_url = html.escape(sub_url)
    safe_install_link = html.escape(install_link[device.os_type.lower()])

    text = (
        f"<b>Управление устройством: {safe_device_name}</b>\n\n"
        f"📄 Статус: {status}\n"
        f"💻 ОС: {device.os_type.capitalize()}\n"
        f"📊 Трафик: {used_gb} GB (безлимит)\n\n"
        f"🔑 Скопируй ключ для подключения:\n<code>{safe_sub_url}</code>\n\n"
        f"📱 <a href='{safe_install_link}'>Скачать Happ</a>"
    )

    new_media = InputMediaPhoto(
        media=f"{config.assets_url}/img/menu_{device.os_type.lower()}-install.png?v=070326",
        caption=text,
        parse_mode="HTML"
    )

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="✏️ Переименовать", callback_data=f"rename_{dev_id}"))
    builder.row(types.InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"confirm_delete_{dev_id}"))
    builder.row(types.InlineKeyboardButton(text="🔄 Обновить", callback_data=f"dev_info_{dev_id}"))
    builder.row(types.InlineKeyboardButton(text="⬅️ К списку устройств", callback_data="devices"))

    await callback.answer()
    await callback.message.edit_media(media=new_media, reply_markup=builder.as_markup())


# --- 3. ПЕРЕИМЕНОВАНИЕ УСТРОЙСТВА ---
@router.callback_query(F.data.startswith("rename_"))
async def rename_dev_start(callback: types.CallbackQuery, state: FSMContext):
    dev_id = int(callback.data.split("_")[-1])
    await state.update_data(dev_to_rename=dev_id)
    await state.set_state(RenameDevice.waiting_for_name)
    await callback.message.answer("📝 Отправьте новое имя для устройства (например: Мамин планшет):")


@router.message(RenameDevice.waiting_for_name)
async def rename_dev_finish(message: types.Message, state: FSMContext):
    new_name = message.text.strip()
    if not (3 <= len(new_name) <= 25):
        return await message.answer("❌ Имя должно быть от 3 до 25 символов. Попробуйте еще раз:")

    data = await state.get_data()
    await rename_custom_device_name(data.get("dev_to_rename"), new_name)
    await state.clear()
    await message.answer(f"✅ Готово! Устройство переименовано в: <b>{html.escape(new_name)}</b>", parse_mode="HTML")


# --- 4. МЕНЮ ДОБАВЛЕНИЯ НОВОГО УСТРОЙСТВА ---
@router.callback_query(F.data == "add_device")
async def add_device_menu(callback: types.CallbackQuery):
    user = await get_user_by_tg_id(callback.from_user.id)

    # Если баланс нулевой или минус, не даем создать устройство
    if user.balance <= 0:
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="💸 Пополнить баланс",
                                               callback_data="topup_menu"))  # Сделай обработчик topup_menu
        builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="devices"))

        return await callback.message.edit_caption(
            caption="❌ **Недостаточно средств**\n\nДля добавления новых устройств ваш баланс должен быть больше 0₽.",
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )

    text = (
        f"➕ **Добавление нового устройства**\n\n"
        f"Выберите операционную систему вашего устройства. Мы сгенерируем ключ и выдадим правильную инструкцию."
    )

    new_media = InputMediaPhoto(
        media=f"{config.assets_url}/img/menu_connect.png?v=070326",
        caption=text,
        parse_mode="Markdown"
    )

    await callback.message.edit_media(
        media=new_media,
        reply_markup=keyboards.get_os_selection_keyboard(),
    )


# --- 5. ПРОЦЕСС СОЗДАНИЯ УСТРОЙСТВА В MARZBAN ---
@router.callback_query(F.data.startswith("new_device_"))
async def process_create_device(callback: types.CallbackQuery):
    os_type = callback.data.split("_")[-1]
    tg_id = callback.from_user.id

    user = await get_user_by_tg_id(tg_id)

    one_day_price = config.one_day_price
    additional_device_price = config.additional_device_price
    total_devices = len(user.devices)

    additional_device_month_price = config.one_day_price if total_devices<3 else config.additional_device_price

    if total_devices == 0:
        month_price = 0.0
    elif total_devices <= 3:
        month_price = one_day_price
    else:
        month_price = (one_day_price + (total_devices - 3) * additional_device_price)

    if user.balance <= additional_device_month_price/30.0:
        text = (
            f"❌ Недостаточно средств\n\n"
            f"💰 Текущий баланс: {user.balance}"
            f"🌐 Ваш текущий тариф\n"
            f"├ Количество устройств: {total_devices}\n"
            f"└ Стоймость в месяц: {month_price}\n\n"
            f"🔰 Мы гарантируем работу сервиса и в случае неполадок вернем вам деньги\n\n"
            f"⚙️ Если у вас возникнут проблемы с пополнением или вы хотите пополниться на другую сумму, свяжитесь с нашей поддержкой"
        )

        new_media = InputMediaPhoto(
            media=f"{config.assets_url}/img/menu_top-up.png?v=070326",
            caption=text,
            parse_mode="Markdown"
        )

        await callback.message.edit_media(
            media=new_media,
            reply_markup=get_top_up_list_keyboard(month_price)
        )

    await callback.answer("⏳ Создаем устройство...", show_alert=False)

    # 1. Creating Device in bd
    device = await create_new_device(tg_id, os_type)
    if not device:
        return await callback.answer("Ошибка БД. Попробуйте позже.", show_alert=True)
    else:
        await update_user_balance(tg_id, -additional_device_month_price/30.0)

    # 2. Creating Marzban User
    await marzban_api.create_user(
        username=device.marzban_username,
        proxied_days=None,  # Вечный профиль
        data_limit=0  # Безлимит по трафику
    )

    text = (
        f"✅ **Устройство успешно добавлено!**\n\n"
        f"💻 ОС: `{os_type.capitalize()}`\n"
        f"Оно появится в списке ваших устройств.\n\n"
        f"⚠️ *Не забудьте настроить его, нажав на кнопку ниже.*"
    )

    new_media = InputMediaPhoto(
        media=f"{config.assets_url}/img/menu_connect.png?v=070326",
        caption=text,
        parse_mode="Markdown"
    )

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔑 Получить ключ", callback_data=f"dev_info_{device.id}"))

    await callback.message.edit_media(
        media=new_media,
        reply_markup=builder.as_markup()
    )

# --- 6. УБЕДИТЬСЯ ЧТО ХОТИТЕ УДАЛИТЬ ---
@router.callback_query(F.data.startswith("confirm_delete_"))
async def rename_dev_start(callback: types.CallbackQuery, state: FSMContext):
    dev_id = int(callback.data.split("_")[-1])

    device = await get_device_by_id(dev_id)
    if not device:
        await callback.answer(text="❌ Устройство не найдено", show_alert=True)
        return

    text = (
        f"Вы уверены что хотите удалить устройство: <i>{html.escape(device.custom_name)}</i>?\n\n"
    )

    new_media = InputMediaPhoto(
        media=f"{config.assets_url}/img/menu_delete-device.png?v=070326",
        caption=text,
        parse_mode="HTML"
    )

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="✅ Да, удалите", callback_data=f"delete_{dev_id}"))
    builder.row(types.InlineKeyboardButton(text="↩️ Нет, вернуться назад", callback_data=f"dev_info_{dev_id}"))

    await callback.message.edit_media(
        media=new_media,
        reply_markup=builder.as_markup()
    )


# --- 6. УДАЛИТЬ УСТРОЙСТВО ---
@router.callback_query(F.data.startswith("delete_"))
async def rename_dev_start(callback: types.CallbackQuery, state: FSMContext):
    dev_id = int(callback.data.split("_")[-1])

    result = await delete_device_by_id(dev_id)

    text = (
        f"✅ Устройство удалено"
    )

    new_media = InputMediaPhoto(
        media=f"{config.assets_url}/img/menu_successful.png?v=070326",
        caption=text,
        parse_mode="Markdown"
    )

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔑 Мои устройства", callback_data=f"devices"))

    await callback.message.edit_media(
        media=new_media,
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )