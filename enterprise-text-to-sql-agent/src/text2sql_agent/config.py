from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    db_url: str = "sqlite:///data/app.db"

    # LLM Configuration
    openai_api_key: Optional[str] = None
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.0
    llm_max_tokens: int = 500

    # Generator Mode: "rule_based", "llm", or "hybrid"
    generator_mode: str = "hybrid"

    # Agent Configuration
    max_rows: int = 200
    allow_union: bool = False


# Global settings instance
settings = Settings()
