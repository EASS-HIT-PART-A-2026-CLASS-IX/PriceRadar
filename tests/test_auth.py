from __future__ import annotations

from datetime import timedelta

from fastapi.testclient import TestClient

from app.auth import create_access_token
from app.config import get_settings
from app.models import UserRole


def test_login_returns_access_token(client: TestClient) -> None:
    settings = get_settings()
    response = client.post(
        "/auth/login",
        json={
            "email": settings.demo_admin_email,
            "password": settings.demo_admin_password,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert "refresh:run" in data["scopes"]


def test_protected_weekly_digest_requires_token(client: TestClient) -> None:
    response = client.get("/reports/weekly-digest")

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing bearer token"}


def test_protected_weekly_digest_rejects_missing_scope(client: TestClient) -> None:
    settings = get_settings()
    token = create_access_token(
        subject=settings.demo_analyst_email,
        role=UserRole.analyst,
        scopes=[],
        expires_delta=timedelta(minutes=5),
    )

    response = client.get(
        "/reports/weekly-digest",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Missing required scope: reports:read"}


def test_protected_weekly_digest_rejects_wrong_role(client: TestClient) -> None:
    settings = get_settings()
    token = create_access_token(
        subject=settings.demo_analyst_email,
        role=UserRole.analyst,
        scopes=["reports:read"],
        expires_delta=timedelta(minutes=5),
    )

    response = client.get(
        "/reports/weekly-digest",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Role admin is required"}


def test_protected_weekly_digest_rejects_expired_token(client: TestClient) -> None:
    settings = get_settings()
    token = create_access_token(
        subject=settings.demo_admin_email,
        role=UserRole.admin,
        scopes=["reports:read"],
        expires_delta=timedelta(seconds=-1),
    )

    response = client.get(
        "/reports/weekly-digest",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token"}


def test_admin_can_read_weekly_digest(client: TestClient) -> None:
    settings = get_settings()
    client.post(
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
    login_response = client.post(
        "/auth/login",
        json={
            "email": settings.demo_admin_email,
            "password": settings.demo_admin_password,
        },
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/reports/weekly-digest",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "# PriceRadar Weekly Digest" in response.text
    assert "Steam Deck OLED" in response.text
