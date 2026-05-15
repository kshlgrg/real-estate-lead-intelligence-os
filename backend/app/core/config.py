from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Lead Intelligence OS"
    environment: str = "development"
    ai_provider: str = "rules-local"
    confidence_review_threshold: float = 0.5
    hot_lead_threshold: float = 8.0
    warm_lead_threshold: float = 5.0

    model_config = SettingsConfigDict(env_file=".env", env_prefix="LEAD_OS_")


@lru_cache
def get_settings() -> Settings:
    return Settings()
