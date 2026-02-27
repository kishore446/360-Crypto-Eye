from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    env: str = "dev"
    log_level: str = "INFO"

    telegram_bot_token: str
    telegram_spot_chat_id: str
    telegram_futures_chat_id: str
    telegram_admin_user_id: int

    binance_base_url: str = "https://api.binance.com"
    binance_futures_url: str = "https://fapi.binance.com"

    database_url: str
    redis_url: str


settings = Settings()
