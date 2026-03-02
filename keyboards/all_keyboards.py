from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types


TARIFFS = {
    1, 3, 6, 12
}


def get_main_keyboard():
    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(text="👤 Профиль", callback_data="profile"))

    builder.row(types.InlineKeyboardButton(text="💳 Пополнить баланс", callback_data="top_up"))

    builder.row(types.InlineKeyboardButton(text="⛓️ Подключиться", callback_data="devices"))

    builder.row(
        types.InlineKeyboardButton(text="🛡 Поддержка", url="https://t.me/trayvpn_help"),
        types.InlineKeyboardButton(text="📢 Новости", url="https://t.me/tray_vpn")
    )

    return builder.as_markup()


def get_top_up_list_keyboard(month_price: int):
    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(text=f"{1*month_price}₽ - 1 месяц", callback_data=f"top_up_{1*month_price}"))
    builder.row(types.InlineKeyboardButton(text=f"{3*month_price}₽ - 3 месяца", callback_data=f"top_up_{3*month_price}"))
    builder.row(types.InlineKeyboardButton(text=f"{6*month_price}₽ - 6 месяцев", callback_data=f"top_up_{6*month_price}"))
    builder.row(types.InlineKeyboardButton(text=f"{12*month_price}₽ - 12 месяцев", callback_data=f"top_up_{12*month_price}"))

    builder.row(types.InlineKeyboardButton(text="⚙️ Поддержка", url="https://t.me/trayvpn_help"))
    builder.row(types.InlineKeyboardButton(text="↩️ Вернуться назад", callback_data="to_main"))
    return builder.as_markup()


def get_devices_keyboard(devices):
    builder = InlineKeyboardBuilder()

    for dev in devices:
        status_emoji = "🟢" if dev.is_active else "🔴"
        builder.row(types.InlineKeyboardButton(
            text=f"{dev.custom_name} {status_emoji}",
            callback_data=f"dev_info_{dev.id}"
        ))

    # Кнопка добавления нового устройства
    builder.row(types.InlineKeyboardButton(text="➕ Добавить устройство", callback_data="add_device"))
    builder.row(types.InlineKeyboardButton(text="↩️ Вернуться назад", callback_data="to_main"))
    return builder.as_markup()


def get_os_selection_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🍏 iOS", callback_data="new_device_ios"),
                types.InlineKeyboardButton(text="🤖 Android", callback_data="new_device_android"))
    builder.row(types.InlineKeyboardButton(text="💻 Windows", callback_data="new_device_windows"),
                types.InlineKeyboardButton(text="🍎 macOS", callback_data="new_device_macos"))
    builder.row(types.InlineKeyboardButton(text="🐧 Linux", callback_data="new_device_linux"))
    builder.row(types.InlineKeyboardButton(text="↩️ Назад", callback_data="devices"))
    return builder.as_markup()


def get_profile_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="💳 Пополнить баланс", callback_data="top_up_profile"))
    builder.row(types.InlineKeyboardButton(text="🎁 Реферальная программа", callback_data="bonus_system"))
    builder.row(types.InlineKeyboardButton(text="↩️ Назад", callback_data="to_main"))
    return builder.as_markup()


def get_bonus_system_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="💰 Вывести (от 500р)", url="https://t.me/trayvpn_help"))
    builder.row(types.InlineKeyboardButton(text="↩️ Назад", callback_data="profile"))
    return builder.as_markup()


def get_back_to_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="↩️ Назад", callback_data="to_main"))
    return builder.as_markup()

def get_back_to_devices_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔑 Мои устройства", callback_data="devices"))
    return builder.as_markup()

def get_back_to_profile_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="↩️ Назад", callback_data="profile"))
    return builder.as_markup()