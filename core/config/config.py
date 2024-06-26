from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    firebird_host: str | None = None
    firebird_user: str | None = None
    firebird_password: str | None = None
    firebird_database: str | None = None

    secret: str | None = None
    host: str | None = None
    port: int | None = None


Config = Settings()
