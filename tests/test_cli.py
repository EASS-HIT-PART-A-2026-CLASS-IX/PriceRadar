from __future__ import annotations

import httpx
from typer.testing import CliRunner

from app.cli import cli

runner = CliRunner()


def test_cli_lists_products(monkeypatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/products"
        return httpx.Response(
            200,
            json=[
                {
                    "id": 1,
                    "name": "Steam Deck OLED",
                    "store": "Valve",
                    "product_url": "https://example.com/steam-deck-oled",
                    "current_price": 2599.0,
                    "target_price": 2499.0,
                    "currency": "ILS",
                    "is_active": True,
                    "user_email": "analyst@priceradar.local",
                }
            ],
        )

    monkeypatch.setattr(
        "app.cli.build_client",
        lambda base_url=None: httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url="http://testserver",
        ),
    )

    result = runner.invoke(cli, ["list-products"])

    assert result.exit_code == 0
    assert "Steam Deck OLED" in result.stdout


def test_cli_add_product_posts_to_api(monkeypatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/products"
        payload = request.read().decode("utf-8")
        assert "Steam Deck OLED" in payload
        return httpx.Response(
            201,
            json={
                "id": 2,
                "name": "Steam Deck OLED",
                "store": "Valve",
                "product_url": "https://example.com/steam-deck-oled",
                "current_price": 2599.0,
                "target_price": 2499.0,
                "currency": "ILS",
                "is_active": True,
                "user_email": "analyst@priceradar.local",
                "created_at": "2026-04-14T10:00:00Z",
                "last_checked_at": None,
            },
        )

    monkeypatch.setattr(
        "app.cli.build_client",
        lambda base_url=None: httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url="http://testserver",
        ),
    )

    result = runner.invoke(
        cli,
        [
            "add-product",
            "--name",
            "Steam Deck OLED",
            "--store",
            "Valve",
            "--product-url",
            "https://example.com/steam-deck-oled",
            "--current-price",
            "2599",
            "--target-price",
            "2499",
            "--user-email",
            "analyst@priceradar.local",
        ],
    )

    assert result.exit_code == 0
    assert "Tracked product #2" in result.stdout


def test_cli_track_url_previews_then_creates_product(monkeypatch) -> None:
    seen_paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_paths.append(request.url.path)
        if request.url.path == "/imports/url-preview":
            return httpx.Response(
                200,
                json={
                    "name": "Sony WH-1000XM5",
                    "store": "KSP Demo",
                    "product_url": "https://demo.ksp.local/products/sony-wh1000xm5",
                    "image_url": "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6505/6505727_rd.jpg%3BmaxHeight%3D1920%3BmaxWidth%3D900?format=webp",
                    "current_price": 1199.9,
                    "currency": "ILS",
                    "supported_store_key": "ksp-demo",
                },
            )
        assert request.url.path == "/products"
        payload = request.read().decode("utf-8")
        assert "Sony WH-1000XM5" in payload
        assert "999.0" in payload
        return httpx.Response(
            201,
            json={
                "id": 3,
                "name": "Sony WH-1000XM5",
                "store": "KSP Demo",
                "product_url": "https://demo.ksp.local/products/sony-wh1000xm5",
                "image_url": "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6505/6505727_rd.jpg%3BmaxHeight%3D1920%3BmaxWidth%3D900?format=webp",
                "current_price": 1199.9,
                "target_price": 999.0,
                "currency": "ILS",
                "is_active": True,
                "user_email": None,
                "created_at": "2026-04-14T10:00:00Z",
                "last_checked_at": None,
            },
        )

    monkeypatch.setattr(
        "app.cli.build_client",
        lambda base_url=None: httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url="http://testserver",
        ),
    )

    result = runner.invoke(
        cli,
        [
            "track-url",
            "--product-url",
            "https://demo.ksp.local/products/sony-wh1000xm5",
            "--target-price",
            "999",
        ],
    )

    assert result.exit_code == 0
    assert seen_paths == ["/imports/url-preview", "/products"]
    assert "Tracked product #3" in result.stdout
