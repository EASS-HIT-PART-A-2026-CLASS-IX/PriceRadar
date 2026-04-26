from __future__ import annotations

from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str
    redis_url: str
    jwt_secret: str
    jwt_algorithm: str
    access_token_minutes: int
    api_base_url: str
    rate_limit_limit: int
    rate_limit_window_seconds: int
    refresh_concurrency: int
    refresh_retry_attempts: int
    refresh_interval_seconds: int
    demo_admin_email: str
    demo_admin_password: str
    demo_admin_name: str
    demo_analyst_email: str
    demo_analyst_password: str
    demo_analyst_name: str


def _getenv_int(name: str, default: int) -> int:
    value = getenv(name)
    return default if value is None else int(value)


def get_settings() -> Settings:
    return Settings(
        database_url=getenv("DATABASE_URL", "sqlite:///./data/priceradar.db"),
        redis_url=getenv("REDIS_URL", "redis://127.0.0.1:6379/0"),
        jwt_secret=getenv("JWT_SECRET", "priceradar-dev-secret-change-me-2026"),
        jwt_algorithm=getenv("JWT_ALGORITHM", "HS256"),
        access_token_minutes=_getenv_int("ACCESS_TOKEN_MINUTES", 30),
        api_base_url=getenv("PRICERADAR_API_BASE_URL", "http://127.0.0.1:8000"),
        rate_limit_limit=_getenv_int("RATE_LIMIT_LIMIT", 60),
        rate_limit_window_seconds=_getenv_int("RATE_LIMIT_WINDOW_SECONDS", 60),
        refresh_concurrency=_getenv_int("REFRESH_CONCURRENCY", 3),
        refresh_retry_attempts=_getenv_int("REFRESH_RETRY_ATTEMPTS", 3),
        refresh_interval_seconds=_getenv_int("REFRESH_INTERVAL_SECONDS", 30),
        demo_admin_email=getenv("DEMO_ADMIN_EMAIL", "admin@priceradar.local"),
        demo_admin_password=getenv("DEMO_ADMIN_PASSWORD", "ChangeMe123!"),
        demo_admin_name=getenv("DEMO_ADMIN_NAME", "PriceRadar Admin"),
        demo_analyst_email=getenv("DEMO_ANALYST_EMAIL", "analyst@priceradar.local"),
        demo_analyst_password=getenv("DEMO_ANALYST_PASSWORD", "Analyst123!"),
        demo_analyst_name=getenv("DEMO_ANALYST_NAME", "PriceRadar Analyst"),
    )


def get_database_url() -> str:
    return get_settings().database_url
