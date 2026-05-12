from fastapi.testclient import TestClient


def test_supported_url_preview_returns_product_details(client: TestClient) -> None:
    response = client.post(
        "/imports/url-preview",
        json={"product_url": "https://demo.ksp.local/products/sony-wh1000xm5"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Sony WH-1000XM5"
    assert data["store"] == "KSP Demo"
    assert data["current_price"] == 1199.9
    assert data["currency"] == "ILS"
    assert data["supported_store_key"] == "ksp-demo"
    assert "BestBuy_US/images/products/6505" in data["image_url"]


def test_url_preview_rejects_unsupported_store(client: TestClient) -> None:
    response = client.post(
        "/imports/url-preview",
        json={"product_url": "https://unsupported.example/products/sony-wh1000xm5"},
    )

    assert response.status_code == 422
    assert "Supported hosts" in response.json()["detail"]


def test_url_preview_to_track_confirmation_flow(client: TestClient) -> None:
    preview_response = client.post(
        "/imports/url-preview",
        json={"product_url": "https://demo.ivory.local/products/steam-deck-oled"},
    )
    preview = preview_response.json()

    create_response = client.post(
        "/products",
        json={
            "name": preview["name"],
            "store": preview["store"],
            "product_url": preview["product_url"],
            "image_url": preview["image_url"],
            "current_price": preview["current_price"],
            "target_price": 2299.0,
            "currency": preview["currency"],
            "is_active": True,
        },
    )

    assert preview_response.status_code == 200
    assert create_response.status_code == 201
    tracked = create_response.json()
    assert tracked["name"] == "Steam Deck OLED"
    assert "steamdeck/images/oled" in tracked["image_url"]
