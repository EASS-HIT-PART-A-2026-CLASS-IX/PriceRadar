from __future__ import annotations

import asyncio

from redis import asyncio as redis_asyncio
from sqlmodel import Session

from app.config import get_settings
from app.database import create_db_and_tables, engine
from app.refresh import RefreshCoordinator


async def main() -> None:
    settings = get_settings()
    create_db_and_tables()
    redis = redis_asyncio.from_url(settings.redis_url, decode_responses=True)
    coordinator = RefreshCoordinator(
        session_factory=lambda: Session(engine),
        redis_client=redis,
        concurrency_limit=settings.refresh_concurrency,
        retry_attempts=settings.refresh_retry_attempts,
    )
    try:
        while True:
            stats = await coordinator.run_for_day()
            print(
                f"worker-cycle processed={stats.processed} skipped={stats.skipped} retries={stats.retries}"
            )
            await asyncio.sleep(settings.refresh_interval_seconds)
    finally:
        await redis.close()


if __name__ == "__main__":
    asyncio.run(main())
