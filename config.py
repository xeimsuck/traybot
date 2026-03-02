from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    marzban_url: SecretStr
    marzban_admin_username: SecretStr
    marzban_admin_password: SecretStr
    assets_url: str
    one_day_price: int
    additional_device_price: int
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

config = Settings()