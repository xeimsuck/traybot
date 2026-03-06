import asyncio
import sqlite3
from datetime import datetime, UTC
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Импортируем твои модели и URL базы из файла models.py
from models import Base, User, Device, DB_URL

# Путь к старому файлу SQLite
SQLITE_DB_PATH = '../db.sqlite3'


async def migrate_data():
    # 1. Подключение к PostgreSQL
    engine = create_async_engine(DB_URL)
    async_session = async_sessionmaker(engine)

    # 2. Создание таблиц в Postgres (если еще не созданы)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 3. Чтение данных из SQLite
    # Используем стандартный sqlite3, так как для разового переноса он проще
    sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()

    print("Начинаю миграцию...")

    async with async_session() as session:
        # --- ПЕРЕНОС ПОЛЬЗОВАТЕЛЕЙ ---
        cursor.execute("SELECT * FROM users")
        sqlite_users = cursor.fetchall()

        for row in sqlite_users:
            new_user = User(
                id=row['id'],
                tg_id=row['tg_id'],
                username=row['username'],
                balance=row['balance'],
                is_active=bool(row['is_active']),
                referred_by=row['referred_by'],
                invited_count=row['invited_count']
            )
            session.add(new_user)

        await session.flush()  # Отправляем данные в буфер Postgres
        print(f"Подготовлено пользователей: {len(sqlite_users)}")

        # --- ПЕРЕНОС УСТРОЙСТВ ---
        cursor.execute("SELECT * FROM devices")
        sqlite_devices = cursor.fetchall()

        for row in sqlite_devices:
            # Обработка даты: SQLite хранит их строками
            created_at_val = row['created_at']
            if isinstance(created_at_val, str):
                # Убираем лишние символы, если они есть
                dt = datetime.fromisoformat(created_at_val.replace('Z', '+00:00'))
            else:
                dt = datetime.now(UTC)

            new_device = Device(
                id=row['id'],
                user_id=row['user_id'],
                marzban_username=row['marzban_username'],
                os_type=row['os_type'],
                custom_name=row['custom_name'],
                created_at=dt,
                is_active=bool(row['is_active'])
            )
            session.add(new_device)

        print(f"Подготовлено устройств: {len(sqlite_devices)}")

        try:
            await session.commit()
            print("Успех: Все данные перенесены в PostgreSQL.")

            # ВАЖНО: Синхронизация счетчиков ID (Sequences)
            # Так как мы вставляли ID вручную, Postgres "не знает", что счетчик должен сдвинуться.
            # Без этого следующий новый юзер в боте вызовет ошибку "ID уже занят".
            async with engine.begin() as conn:
                await conn.execute(text("SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));"))
                await conn.execute(text("SELECT setval('devices_id_seq', (SELECT MAX(id) FROM devices));"))
            print("Счетчики ID синхронизированы.")

        except Exception as e:
            print(f"Ошибка при миграции: {e}")
            await session.rollback()
        finally:
            sqlite_conn.close()
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(migrate_data())