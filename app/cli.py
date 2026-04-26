from __future__ import annotations

import csv
from pathlib import Path

import httpx
import typer

from app.config import get_settings

cli = typer.Typer(add_completion=False, help="PriceRadar Typer interface for EX2 and EX3.")


def build_client(base_url: str | None = None) -> httpx.Client:
    target = base_url or get_settings().api_base_url
    return httpx.Client(base_url=target, timeout=10.0)


def _raise_for_error(response: httpx.Response) -> None:
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        detail = ""
        try:
            payload = response.json()
            if isinstance(payload, dict):
                detail = str(payload.get("detail", ""))
        except ValueError:
            detail = response.text
        message = detail or str(exc)
        typer.echo(message, err=True)
        raise typer.Exit(code=1) from exc


def _login_headers(client: httpx.Client, email: str, password: str) -> dict[str, str]:
    response = client.post("/auth/login", json={"email": email, "password": password})
    _raise_for_error(response)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@cli.command("list-products")
def list_products(
    user_email: str | None = typer.Option(default=None, help="Filter by alert email."),
) -> None:
    with build_client() as client:
        response = client.get("/products", params={"user_email": user_email} if user_email else None)
        _raise_for_error(response)
        products = response.json()
    if not products:
        typer.echo("No tracked products yet.")
        return
    for product in products:
        typer.echo(
            f"[{product['id']}] {product['name']} | {product['store']} | "
            f"current={product['current_price']} {product['currency']} | "
            f"target={product['target_price']} | active={product['is_active']}"
        )


@cli.command("add-product")
def add_product(
    name: str = typer.Option(..., prompt=True),
    store: str = typer.Option(..., prompt=True),
    product_url: str = typer.Option(..., prompt=True),
    current_price: float = typer.Option(..., prompt=True),
    target_price: float = typer.Option(..., prompt=True),
    user_email: str | None = typer.Option(default=None),
    currency: str = typer.Option(default="ILS"),
) -> None:
    payload = {
        "name": name,
        "store": store,
        "product_url": product_url,
        "current_price": current_price,
        "target_price": target_price,
        "user_email": user_email,
        "currency": currency,
        "is_active": True,
    }
    with build_client() as client:
        response = client.post("/products", json=payload)
        _raise_for_error(response)
        product = response.json()
    typer.echo(f"Tracked product #{product['id']}: {product['name']}")


@cli.command("summary")
def summary() -> None:
    with build_client() as client:
        response = client.get("/products/summary")
        _raise_for_error(response)
        data = response.json()
    typer.echo(f"Total tracked: {data['total']}")
    typer.echo(f"Active items: {data['active']}")
    typer.echo(f"Below target: {data['below_target']}")
    typer.echo(f"Average target price: {data['average_target_price']}")


@cli.command("export-csv")
def export_csv(
    output: Path = typer.Option(default=Path("exports/tracked-products.csv")),
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with build_client() as client:
        response = client.get("/products")
        _raise_for_error(response)
        products = response.json()
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "id",
                "name",
                "store",
                "product_url",
                "current_price",
                "target_price",
                "currency",
                "is_active",
                "user_email",
            ],
        )
        writer.writeheader()
        writer.writerows(products)
    typer.echo(f"Exported {len(products)} products to {output}")


@cli.command("weekly-digest")
def weekly_digest(
    email: str = typer.Option(default_factory=lambda: get_settings().demo_admin_email),
    password: str = typer.Option(default_factory=lambda: get_settings().demo_admin_password, hide_input=True),
) -> None:
    with build_client() as client:
        headers = _login_headers(client, email, password)
        response = client.get("/reports/weekly-digest", headers=headers)
        _raise_for_error(response)
        typer.echo(response.text)


if __name__ == "__main__":
    cli()
