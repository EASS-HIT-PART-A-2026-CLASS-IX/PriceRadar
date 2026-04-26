from fastapi.testclient import TestClient


def test_list_products_starts_empty(client: TestClient) -> None:
    response = client.get("/products")

    assert response.status_code == 200
    assert response.json() == []


def test_root_endpoint_exposes_basic_api_metadata(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["name"] == "PriceRadar API"
    assert response.json()["docs"] == "/docs"
    assert response.headers["X-RateLimit-Limit"] == "60"


def test_create_product(client: TestClient) -> None:
    payload = {
        "name": "Sony WH-1000XM5",
        "store": "KSP",
        "product_url": "https://example.com/products/sony-wh1000xm5",
        "current_price": 1299.9,
        "target_price": 999.9,
        "currency": "ILS",
        "is_active": True,
    }

    response = client.post("/products", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == payload["name"]
    assert data["target_price"] == payload["target_price"]


def test_update_product(client: TestClient) -> None:
    create_response = client.post(
        "/products",
        json={
            "name": "Ninja Air Fryer",
            "store": "Amazon",
            "product_url": "https://example.com/products/ninja-air-fryer",
            "current_price": 499.0,
            "target_price": 420.0,
            "currency": "ILS",
            "is_active": True,
        },
    )
    product_id = create_response.json()["id"]

    response = client.put(
        f"/products/{product_id}",
        json={"current_price": 450.0, "target_price": 399.0, "is_active": False},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["current_price"] == 450.0
    assert data["target_price"] == 399.0
    assert data["is_active"] is False


def test_update_current_price_persists_in_backend(client: TestClient) -> None:
    create_response = client.post(
        "/products",
        json={
            "name": "Steam Deck OLED",
            "store": "Valve",
            "product_url": "https://example.com/products/steam-deck-oled",
            "current_price": 2599.0,
            "target_price": 2499.0,
            "currency": "ILS",
            "is_active": True,
        },
    )
    product_id = create_response.json()["id"]

    update_response = client.put(
        f"/products/{product_id}",
        json={"current_price": 2399.0, "target_price": 2299.0},
    )
    get_response = client.get(f"/products/{product_id}")

    assert update_response.status_code == 200
    assert get_response.status_code == 200
    assert get_response.json()["current_price"] == 2399.0
    assert get_response.json()["target_price"] == 2299.0


def test_pause_and_resume_product_persist_in_backend(client: TestClient) -> None:
    create_response = client.post(
        "/products",
        json={
            "name": "Galaxy Tab S8",
            "store": "Samsung Store",
            "product_url": "https://example.com/products/galaxy-tab-s8",
            "current_price": 2790.0,
            "target_price": 2590.0,
            "currency": "ILS",
            "is_active": True,
        },
    )
    product_id = create_response.json()["id"]

    pause_response = client.put(f"/products/{product_id}", json={"is_active": False})
    paused_state = client.get(f"/products/{product_id}")
    resume_response = client.put(f"/products/{product_id}", json={"is_active": True})
    resumed_state = client.get(f"/products/{product_id}")

    assert pause_response.status_code == 200
    assert paused_state.status_code == 200
    assert paused_state.json()["is_active"] is False
    assert resume_response.status_code == 200
    assert resumed_state.status_code == 200
    assert resumed_state.json()["is_active"] is True


def test_list_products_supports_pagination(client: TestClient) -> None:
    payloads = [
        {
            "name": "Product A",
            "store": "Store A",
            "product_url": "https://example.com/products/a",
            "current_price": 100.0,
            "target_price": 80.0,
            "currency": "ILS",
            "is_active": True,
        },
        {
            "name": "Product B",
            "store": "Store B",
            "product_url": "https://example.com/products/b",
            "current_price": 200.0,
            "target_price": 150.0,
            "currency": "ILS",
            "is_active": True,
        },
    ]

    for payload in payloads:
        client.post("/products", json=payload)

    response = client.get("/products", params={"offset": 1, "limit": 1})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Product B"


def test_products_summary_tracks_extra_feature_metrics(client: TestClient) -> None:
    client.post(
        "/products",
        json={
            "name": "Steam Deck OLED",
            "store": "Valve",
            "product_url": "https://example.com/products/steam-deck-oled",
            "current_price": 2499.0,
            "target_price": 2499.0,
            "currency": "ILS",
            "is_active": True,
        },
    )
    client.post(
        "/products",
        json={
            "name": "Kindle Paperwhite",
            "store": "Amazon",
            "product_url": "https://example.com/products/kindle-paperwhite",
            "current_price": 599.0,
            "target_price": 549.0,
            "currency": "ILS",
            "is_active": False,
        },
    )

    response = client.get("/products/summary")

    assert response.status_code == 200
    assert response.json() == {
        "total": 2,
        "active": 1,
        "below_target": 1,
        "average_target_price": 1524.0,
    }


def test_delete_product(client: TestClient) -> None:
    create_response = client.post(
        "/products",
        json={
            "name": "Apple Watch SE",
            "store": "iDigital",
            "product_url": "https://example.com/products/apple-watch-se",
            "current_price": 1049.0,
            "target_price": 899.0,
            "currency": "ILS",
            "is_active": True,
        },
    )
    product_id = create_response.json()["id"]

    delete_response = client.delete(f"/products/{product_id}")
    get_response = client.get(f"/products/{product_id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_get_product_returns_404_when_missing(client: TestClient) -> None:
    response = client.get("/products/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


def test_create_product_rejects_invalid_url(client: TestClient) -> None:
    response = client.post(
        "/products",
        json={
            "name": "Bad URL Product",
            "store": "Store",
            "product_url": "example.com/product",
            "current_price": 100.0,
            "target_price": 90.0,
            "currency": "ILS",
            "is_active": True,
        },
    )

    assert response.status_code == 422


def test_create_product_rejects_target_price_above_current_price(client: TestClient) -> None:
    response = client.post(
        "/products",
        json={
            "name": "Price Rule Product",
            "store": "Store",
            "product_url": "https://example.com/product",
            "current_price": 100.0,
            "target_price": 120.0,
            "currency": "ILS",
            "is_active": True,
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "target_price must be less than or equal to current_price"
    }


def test_update_product_rejects_invalid_target_price_rule(client: TestClient) -> None:
    create_response = client.post(
        "/products",
        json={
            "name": "Rule Check Product",
            "store": "Store",
            "product_url": "https://example.com/rule-check",
            "current_price": 100.0,
            "target_price": 90.0,
            "currency": "ILS",
            "is_active": True,
        },
    )
    product_id = create_response.json()["id"]

    response = client.put(f"/products/{product_id}", json={"target_price": 150.0})

    assert response.status_code == 422
    assert response.json() == {
        "detail": "target_price must be less than or equal to current_price"
    }


def test_update_product_returns_404_when_missing(client: TestClient) -> None:
    response = client.put("/products/999", json={"current_price": 100.0})

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


def test_delete_product_returns_404_when_missing(client: TestClient) -> None:
    response = client.delete("/products/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}
