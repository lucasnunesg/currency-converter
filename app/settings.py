from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Defines settings used by the engine"""
    model_config = SettingsConfigDict(
        env_file=".env.dev", env_file_encoding="utf-8"
    )

    DATABASE_URL: str
