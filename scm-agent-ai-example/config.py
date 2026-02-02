from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "SCM Agent API"
    APP_VERSION: str = "0.1.0"
    ENV: Literal["local", "dev", "staging", "prod"] = "local"
    PORT: int = 8080
    LOG_LEVEL: str = "INFO"
    GIT_SHA: Optional[str] = None

    OPENAI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
