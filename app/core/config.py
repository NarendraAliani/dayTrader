from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DayTrader Market Intelligence Engine"
    app_env: str = "development"
    host: str = "127.0.0.1"
    port: int = 8000
    dhan_access_token: str = ""
    dhan_client_id: str = ""
    database_url: str = "postgresql+psycopg://daytrader:change_me@localhost:5432/daytrader"
    enable_live_orders: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
