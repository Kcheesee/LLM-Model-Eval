"""
Configuration management for Model Eval Studio backend.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/model_eval_db"

    # LLM Provider API Keys
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""

    # Application
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-change-in-production"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    # API Settings
    MAX_CONCURRENT_REQUESTS: int = 5
    REQUEST_TIMEOUT: int = 120

    # Model Defaults
    DEFAULT_MAX_TOKENS: int = 1000
    DEFAULT_TEMPERATURE: float = 0.7

    # Cost per 1M tokens (approximate, update as pricing changes)
    CLAUDE_SONNET_INPUT_COST: float = 3.0
    CLAUDE_SONNET_OUTPUT_COST: float = 15.0
    GPT4_TURBO_INPUT_COST: float = 10.0
    GPT4_TURBO_OUTPUT_COST: float = 30.0
    GEMINI_PRO_INPUT_COST: float = 0.5
    GEMINI_PRO_OUTPUT_COST: float = 1.5

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
