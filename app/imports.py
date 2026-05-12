from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from fastapi import HTTPException, status

from app.models import ProductUrlPreviewRead


@dataclass(frozen=True, slots=True)
class StoreAdapter:
    key: str
    host: str
    display_name: str


SUPPORTED_STORES: tuple[StoreAdapter, ...] = (
    StoreAdapter(key="ksp-demo", host="demo.ksp.local", display_name="KSP Demo"),
    StoreAdapter(key="ivory-demo", host="demo.ivory.local", display_name="Ivory Demo"),
    StoreAdapter(key="bug-demo", host="demo.bug.local", display_name="Bug Demo"),
)


class ProductMetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "meta":
            return
        attributes = {key.lower(): value for key, value in attrs if value is not None}
        name = attributes.get("name") or attributes.get("property")
        content = attributes.get("content")
        if name and content and name.startswith("priceradar:"):
            self.values[name.removeprefix("priceradar:")] = content.strip()


def supported_store_hosts() -> list[str]:
    return [store.host for store in SUPPORTED_STORES]


def _adapter_for_url(product_url: str) -> StoreAdapter:
    host = urlparse(product_url).hostname or ""
    host = host.lower().removeprefix("www.")
    for adapter in SUPPORTED_STORES:
        if host == adapter.host:
            return adapter
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=f"Unsupported store URL. Supported hosts: {', '.join(supported_store_hosts())}",
    )


def _fixture_slug(product_url: str) -> str:
    path = urlparse(product_url).path.strip("/")
    slug = path.rsplit("/", maxsplit=1)[-1]
    if not slug:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Product URL must include a product slug.",
        )
    return slug


def _fixture_path(adapter: StoreAdapter, product_url: str) -> Path:
    slug = _fixture_slug(product_url)
    return Path(__file__).resolve().parent / "store_fixtures" / adapter.key / f"{slug}.html"


def _load_fixture(adapter: StoreAdapter, product_url: str) -> str:
    path = _fixture_path(adapter, product_url)
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supported store, but no fixture exists for this product URL: {product_url}",
        )
    return path.read_text(encoding="utf-8")


def _parse_product_html(html: str, adapter: StoreAdapter, product_url: str) -> ProductUrlPreviewRead:
    parser = ProductMetaParser()
    parser.feed(html)
    values = parser.values
    missing = [
        key
        for key in ("name", "price", "currency", "image_url")
        if not values.get(key)
    ]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Product fixture is missing fields: {', '.join(missing)}",
        )
    try:
        current_price = float(values["price"])
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Product fixture price must be numeric.",
        ) from exc

    return ProductUrlPreviewRead(
        name=values["name"],
        store=values.get("store") or adapter.display_name,
        current_price=current_price,
        currency=values["currency"].upper(),
        product_url=product_url,
        image_url=values.get("image_url"),
        supported_store_key=adapter.key,
    )


def preview_product_url(product_url: str) -> ProductUrlPreviewRead:
    adapter = _adapter_for_url(product_url)
    html = _load_fixture(adapter, product_url)
    return _parse_product_html(html, adapter, product_url)
