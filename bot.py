import asyncio
import logging
from config import config
from aiogram import Bot, Dispatcher
from database.models import async_main
from handlers import start, user_menu, devices, top_up
from utils.billing import setup_billing

logging.basicConfig(level=logging.INFO)

# Конфигурация
BOT_TOKEN = config.bot_token.get_secret_value()
MARZBAN_URL = config.marzban_url.get_secret_value()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def main():
    await async_main()
    dp.include_router(start.router)
    dp.include_router(user_menu.router)
    dp.include_router(devices.router)
    dp.include_router(top_up.router)
    setup_billing()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())