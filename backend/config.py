from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Social Intent Miner"
    DEBUG: bool = False
    API_PREFIX: str = "/api"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "https://*.vercel.app"]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/social_intent_miner"

    # Auth
    JWT_SECRET: str  # No default — must be set in env
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Reddit
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    REDDIT_USER_AGENT: str = "SocialIntentMiner/1.0"

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_PRO_MONTHLY: str = ""
    STRIPE_PRICE_PRO_YEARLY: str = ""

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
