from __future__ import annotations

from datetime import date

import pytest
from sqlmodel import Session

from app.models import TrackedProduct
from app.refresh import RefreshCoordinator


class FakeRedis:
    def __init__(self) -> None:
        self.keys: set[str] = set()

    async def set(self, key: str, value: str, *, ex: int, nx: bool) -> bool:
        if nx and key in self.keys:
            return False
        self.keys.add(key)
        return True


@pytest.mark.anyio
async def test_refresh_uses_retries_and_redis_backed_idempotency(test_engine) -> None:
    with Session(test_engine) as session:
        session.add(
            TrackedProduct(
                name="Steam Deck OLED",
                store="Valve",
                product_url="https://example.com/steam-deck-oled",
                current_price=2599.0,
                target_price=2499.0,
                currency="ILS",
                is_active=True,
            )
        )
        session.commit()

    fake_redis = FakeRedis()
    attempts = {"count": 0}

    async def flaky_fetcher(product: TrackedProduct) -> float:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise RuntimeError("temporary upstream failure")
        return 2490.0

    coordinator = RefreshCoordinator(
        session_factory=lambda: Session(test_engine),
        redis_client=fake_redis,
        fetch_price=flaky_fetcher,
        concurrency_limit=2,
        retry_attempts=3,
    )

    first = await coordinator.run_for_day(run_date=date(2026, 4, 14))
    second = await coordinator.run_for_day(run_date=date(2026, 4, 14))

    assert first.processed == 1
    assert first.retries == 1
    assert second.skipped == 1
    assert attempts["count"] == 2

    with Session(test_engine) as session:
        refreshed = session.get(TrackedProduct, 1)
        assert refreshed is not None
        assert refreshed.current_price == 2490.0
        assert refreshed.last_checked_at is not None
