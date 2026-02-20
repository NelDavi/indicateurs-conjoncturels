from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "PGIC API"
    database_url: str = Field(
        default="postgresql+psycopg://pgic:pgic@localhost:5432/pgic",
        description="SQLAlchemy database URL",
    )


settings = Settings()
