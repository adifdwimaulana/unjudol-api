from typing import Literal

from pydantic import computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True
    )

    HOST: str = "localhost"
    ENVIRONMENT: Literal["local", "production"] = "local"
    JWT_SECRET_KEY: str

    @computed_field
    def SERVER_HOST(self) -> str:
        if self.ENVIRONMENT == "local":
            return f"http://{self.HOST}"

        return f"https://{self.HOST}"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    @computed_field
    def DATABASE_URI(self) -> str:
        return str(MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            path=self.POSTGRES_DB
        ))

config = Config()