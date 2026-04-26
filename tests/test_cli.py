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
