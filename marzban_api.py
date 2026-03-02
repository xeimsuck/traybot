import logging
from datetime import datetime, timedelta, UTC
import httpx
from config import config

class MarzbanAPI:
    def __init__(self):
        self.base_url = config.marzban_url.get_secret_value()
        self.admin_username = config.marzban_admin_username.get_secret_value()
        self.admin_password = config.marzban_admin_password.get_secret_value()
        self.token = None

    async def get_token(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/admin/token",
                data={"username": self.admin_username, "password": self.admin_password}
            )
            self.token = response.json()['access_token']


    async def create_user(self, username: str, proxied_days: int | None, data_limit: int):
        if not self.token: await self.get_token()

        expire_value = int((datetime.now(UTC) + timedelta(days=proxied_days)).timestamp()) if proxied_days else 0

        headers = {"Authorization": f"Bearer {self.token}"}
        user_data = {
            "username": username,
            "inbounds": {
                "vless": [
                    "VLESS TCP REALITY",
                ]
            },
            "proxies": {"vless": {}},
            "expire": expire_value,
            "data_limit": data_limit * 1024 * 1024 * 1024,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/api/user", json=user_data, headers=headers)
            return response.json()


    async def get_user(self, username: str):
        if not self.token:
            await self.get_token()

        headers = {"Authorization": f"Bearer {self.token}"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/user/{username}",
                    headers=headers
                )

                if response.status_code == 200:
                    return response.json()

                elif response.status_code == 401:
                    await self.get_token()
                    headers["Authorization"] = f"Bearer {self.token}"
                    response = await client.get(f"{self.base_url}/api/user/{username}", headers=headers)
                    return response.json() if response.status_code == 200 else None

                else:
                    logging.error(f"Ошибка Marzban API: Статус {response.status_code} для пользователя {username}")
                    return None

            except Exception as e:
                logging.error(f"Ошибка при запросе к Marzban API: {e}")
                return None

    async def remove_user(self, username: str):
        if not self.token:
            await self.get_token()

        headers = {"Authorization": f"Bearer {self.token}"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                url = f"{self.base_url}/api/user/{username}"
                response = await client.delete(url, headers=headers)

                # 1. Если всё успешно
                if response.status_code == 200:
                    return True

                # 2. Если токен протух (401)
                elif response.status_code == 401:
                    logging.info("Токен истек, обновляю для удаления...")
                    await self.get_token()
                    headers["Authorization"] = f"Bearer {self.token}"
                    # Повторная попытка
                    response = await client.delete(url, headers=headers)
                    return response.status_code == 200

                # 3. Если пользователя уже нет (404)
                elif response.status_code == 404:
                    logging.warning(f"Пользователь {username} не найден в Marzban (уже удален).")
                    return True

                else:
                    logging.error(f"Ошибка Marzban API при удалении: {response.status_code}")
                    return False

            except Exception as e:
                logging.error(f"Исключение при удалении из Marzban API: {e}")
                return False

    # Меняет статус юзера. status: 'active' или 'disabled'
    async def set_user_status(self, username: str, status: str):
        if not self.token:
            await self.get_token()

        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Для смены статуса в Marzban отправляется PUT запрос
            response = await client.put(
                f"{self.base_url}/api/user/{username}",
                json={"status": status},
                headers=headers
            )
            if response.status_code != 200:
                logging.error(f"Ошибка смены статуса {username}: {response.status_code}")
            return response.status_code == 200

marzban_api = MarzbanAPI()