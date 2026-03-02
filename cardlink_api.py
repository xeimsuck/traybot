import aiohttp
import asyncio
from aiogram.exceptions import TelegramBadRequest
from aiogram import Bot

CARDLINK_API_KEY = "ТВОЙ_API_КЛЮЧ_CARDLINK"
SHOP_ID = "ТВОЙ_SHOP_ID"


# 1. Создание счета
async def create_cardlink_bill(amount: int, tg_id: int):
    url = "https://cardlink.link/api/v1/bill/create"
    headers = {
        "Authorization": f"Bearer {CARDLINK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "shop_id": SHOP_ID,
        "amount": amount,
        "currency": "RUB",
        "custom": str(tg_id)
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as resp:
            if resp.status == 200:
                res = await resp.json()
                # Возвращаем ID счета и саму ссылку
                return res.get("id"), res.get("link")
            return None, None


# 2. Проверка статуса счета
async def check_cardlink_status(bill_id: str) -> bool:
    url = f"https://cardlink.link/api/v1/bill/status?id={bill_id}"
    headers = {"Authorization": f"Bearer {CARDLINK_API_KEY}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                res = await resp.json()
                # Предполагаем, что статус успешной оплаты это "SUCCESS" или "PAID"
                return res.get("status") == "SUCCESS"
            return False