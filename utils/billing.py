import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import pytz
from database.models import async_session, User
from marzban_api import marzban_api
from utils.math import get_daily_cost


async def daily_billing():
    logging.info("Начинаю процесс биллинга...")
    async with async_session() as session:
        # Загружаем сразу юзеров и их устройства (чтобы не было DetachedInstanceError)
        query = select(User).options(selectinload(User.devices))
        result = await session.execute(query)
        users = result.scalars().all()

        for user in users:
            devices = list(user.devices)
            total_devices = len(devices)

            if total_devices == 0:
                continue

            daily_cost = get_daily_cost(total_devices)

            if user.balance >= daily_cost:
                # Баланс позволяет -> списываем
                user.balance -= daily_cost

                # Если юзер был отключен (is_active=False), значит он пополнил баланс -> включаем
                if not user.is_active:
                    user.is_active = True
                    for device in devices:
                        await marzban_api.set_user_status(device.marzban_username, "active")
            else:
                # Баланс меньше стоимости -> замораживаем, но не удаляем
                if user.is_active:
                    user.is_active = False
                    for device in devices:
                        await marzban_api.set_user_status(device.marzban_username, "disabled")

        # Коммитим все изменения в БД одним разом
        await session.commit()
    logging.info("Биллинг завершен.")


def setup_billing():
    """Инициализация планировщика"""
    scheduler = AsyncIOScheduler(timezone=pytz.timezone('Europe/Moscow'))
    # Запуск каждый день строго в 00:00
    scheduler.add_job(daily_billing, trigger='cron', hour=0, minute=0)
    scheduler.start()