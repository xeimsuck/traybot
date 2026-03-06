import datetime
import uuid
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from config import config
from marzban_api import marzban_api
from .models import async_session, User, Device

async def create_user(tg_id, username, referred_by):
    async with async_session() as session:
        # Исправлено: правильный поиск по tg_id, а не по первичному ключу
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            return False

        new_user = User(tg_id=tg_id, username=username, balance=15, referred_by=referred_by)
        session.add(new_user)
        try:
            await session.commit()
            return True
        except Exception as e:
            # Лучше принтить ошибку, чтобы в будущем понимать, если база упадет по другой причине
            print(f"Error creating user: {e}")
            await session.rollback()
            return False

async def get_user_balance_by_tg_id(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            return user.balance
        return 0

async def update_user_balance(tg_id: int, amount: float): # Изменил на float, так как баланс у тебя Float
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.balance += amount
            await session.commit()

async def get_user_by_tg_id(tg_id: int) -> User | None:
    async with async_session() as session:
        query = select(User).where(User.tg_id == tg_id).options(selectinload(User.devices))
        result = await session.execute(query)
        return result.scalar_one_or_none()

async def get_device_by_id(device_id: int) -> Device | None:
    async with async_session() as session:
        query = select(Device).where(Device.id == device_id).options(selectinload(Device.user))
        result = await session.execute(query)
        return result.scalar_one_or_none()

async def delete_device_by_id(device_id: int) -> bool:
    async with async_session() as session:
        device = await session.get(Device, device_id) # Здесь .get() использовать правильно, так как device_id это Primary Key

        if not device:
            return False

        username_to_delete = device.marzban_username

        await session.delete(device)
        await session.commit()

        return await marzban_api.remove_user(username_to_delete)

async def rename_custom_device_name(device_id: int, new_name: str):
    async with async_session() as session:
        device = await session.get(Device, device_id)
        if device:
            device.custom_name = new_name
            await session.commit()

async def create_new_device(tg_id: int, os_type: str) -> Device | None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return None

        short_uuid = str(uuid.uuid4())[:6]
        marzban_username = f"usr_{tg_id}_{short_uuid}"

        os_names = {
            "windows": "💻 Мой Windows",
            "ios": "🍏 Мой iPhone",
            "android": "🤖 Мой Android",
            "macos": "🍎 Мой Mac",
            "linux": "🐧 Мой Linux"
        }
        custom_name = os_names.get(os_type, "📱 Новое устройство")

        new_device = Device(
            user_id=user.id,
            marzban_username=marzban_username,
            os_type=os_type,
            custom_name=custom_name
        )

        session.add(new_device)
        await session.commit()

        await session.refresh(new_device)
        return new_device

def calculate_daily_cost(device_count: int) -> float:
    if device_count == 0:
        return 0.0
    if device_count <= 3:
        return config.one_day_price / 30.0
    return (config.one_day_price + (device_count - 3) * config.additional_device_price) / 30.0

async def add_referral_bonus(user_tg_id: int, referred_id: int) -> bool:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == user_tg_id))
        referred = await session.scalar(select(User).where(User.tg_id == referred_id))

        if user and referred:
            user.balance += 35.0
            user.invited_count += 1
            referred.balance += 15.0
            await session.commit()
            return True
    return False