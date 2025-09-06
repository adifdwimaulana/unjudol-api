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

    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    @computed_field
    def DATABASE_URI(self) -> MultiHostUrl:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            host=self.DB_HOST,
            port=self.DB_PORT,
            username=self.DB_USERNAME,
            password=self.DB_PASSWORD,
            path=self.DB_NAME
        )

config = Config()