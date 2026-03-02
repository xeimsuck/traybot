from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import BigInteger, String, ForeignKey, DateTime, Boolean, Float
from datetime import datetime, UTC

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String(50), nullable=True)

    # Используем Float, так как ежедневные списания будут с копейками
    balance: Mapped[float] = mapped_column(Float, default=0.0)

    # Флаг для блокировки, если баланс ушел в минус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    referred_by: Mapped[int] = mapped_column(BigInteger, nullable=True)
    invited_count: Mapped[int] = mapped_column(BigInteger, default=0)

    devices: Mapped[list["Device"]] = relationship("Device", back_populates="user", cascade="all, delete-orphan")


class Device(Base):
    __tablename__ = 'devices'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    # Уникальное имя юзера в Marzban (генерируется ботом)
    marzban_username: Mapped[str] = mapped_column(String(100), unique=True)

    # Тип ОС: windows, ios, android, linux, macos
    os_type: Mapped[str] = mapped_column(String(20))

    # Имя устройства для отображения юзеру (например: "Мой iPhone")
    custom_name: Mapped[str] = mapped_column(String(100))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    # Флаг активности конкретного устройства (можно дать юзеру возможность ставить на паузу)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship("User", back_populates="devices")


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)