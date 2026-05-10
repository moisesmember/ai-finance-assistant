from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Assistente Inteligente de Analise Financeira Pessoal"
    environment: str = "local"
    database_url: str = Field(
        default="postgresql+asyncpg://finance:finance@localhost:5432/finance_assistant"
    )
    default_user_id: str = "default-user"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
