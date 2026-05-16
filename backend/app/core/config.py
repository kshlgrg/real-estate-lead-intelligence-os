from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Editorial Intelligence Platform"
    environment: str = "development"
    ai_provider: str = "rules-local"
    confidence_review_threshold: float = 0.5
    high_priority_threshold: float = 8.0
    hot_lead_threshold: float = 8.0
    warm_lead_threshold: float = 5.5

    model_config = SettingsConfigDict(env_file=".env", env_prefix="CI_OS_")


@lru_cache
def get_settings() -> Settings:
    return Settings()
