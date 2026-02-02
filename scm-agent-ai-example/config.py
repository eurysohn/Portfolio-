from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "SCM Agent API"
    APP_VERSION: str = "0.1.0"
    ENV: str = "local"
    PORT: int = 8080
    
    OPENAI_API_KEY: Optional[str] = None
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
