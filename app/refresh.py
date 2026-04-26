from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Awaitable, Callable, Protocol

import anyio
from sqlmodel import Session

from app.models import TrackedProduct, TrackedProductUpdate
from app.repositories import ProductRepository
from app.services import ProductService


class SupportsNxSet(Protocol):
    async def set(self, key: str, value: str, *, ex: int, nx: bool) -> object: ...


PriceFetcher = Callable[[TrackedProduct], Awaitable[float]]
SessionFactory = Callable[[], Session]


@dataclass(slots=True)
class RefreshStats:
    processed: int = 0
    skipped: int = 0
    retries: int = 0


async def deterministic_price_fetcher(product: TrackedProduct) -> float:
    await anyio.sleep(0)
    factor = 1 - (((product.id or 1) % 4) + 1) * 0.01
    return round(max(product.target_price * 0.85, product.current_price * factor), 2)


class RefreshCoordinator:
    def __init__(
        self,
        *,
        session_factory: SessionFactory,
        redis_client: SupportsNxSet,
        fetch_price: PriceFetcher = deterministic_price_fetcher,
        concurrency_limit: int = 3,
        retry_attempts: int = 3,
    ) -> None:
        self.session_factory = session_factory
        self.redis_client = redis_client
        self.fetch_price = fetch_price
        self.concurrency_limit = concurrency_limit
        self.retry_attempts = retry_attempts

    def _load_active_products(self) -> list[TrackedProduct]:
        with self.session_factory() as session:
            return ProductRepository(session).list_active()

    def _save_price(self, product_id: int, refreshed_price: float, checked_at: datetime) -> None:
        with self.session_factory() as session:
            service = ProductService(ProductRepository(session))
            service.update_product(
                product_id,
                TrackedProductUpdate(
                    current_price=refreshed_price,
                    last_checked_at=checked_at,
                ),
            )

    async def run_for_day(self, *, run_date: date | None = None) -> RefreshStats:
        active_products = self._load_active_products()
        semaphore = anyio.Semaphore(self.concurrency_limit)
        stats = RefreshStats()
        effective_date = run_date or datetime.now(UTC).date()

        async def worker(product: TrackedProduct) -> None:
            async with semaphore:
                claimed = await self.redis_client.set(
                    f"refresh:{effective_date.isoformat()}:{product.id}",
                    "claimed",
                    ex=24 * 60 * 60,
                    nx=True,
                )
                if not claimed:
                    stats.skipped += 1
                    return

                attempt = 0
                while True:
                    attempt += 1
                    try:
                        refreshed_price = await self.fetch_price(product)
                        self._save_price(product.id or 0, refreshed_price, datetime.now(UTC))
                        stats.processed += 1
                        return
                    except Exception:
                        if attempt >= self.retry_attempts:
                            raise
                        stats.retries += 1
                        await anyio.sleep(0.05 * attempt)

        async with anyio.create_task_group() as task_group:
            for product in active_products:
                task_group.start_soon(worker, product)

        return stats
