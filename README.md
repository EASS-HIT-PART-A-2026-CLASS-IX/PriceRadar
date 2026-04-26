# PriceRadar

PriceRadar is a local price-tracking product for shoppers. Users can track product URLs, store the current price, set a target price, list their tracked products, view summary metrics, and export the catalog to CSV.

The project keeps the same domain across the course exercises: EX1 provides the FastAPI backend, EX2 adds a Typer interface that talks to that backend, and the repository already includes groundwork for the EX3 local microservice stack.

## Current Features

- Track products with name, store, URL, current price, target price, currency, and alert email.
- List, create, update, and delete tracked products through the FastAPI API.
- Use the Typer CLI to list products, add products, view summary metrics, and export CSV.
- Persist data with SQLModel, SQLite, and SQL migrations.
- Seed reproducible demo data without committing SQLite database files.
- Run automated tests for API, CLI, auth, and async refresh behavior.
- Open the optional browser dashboard at `/app`.

## Stack

- `FastAPI` backend
- `SQLModel` + `SQLite`
- SQL migrations in `migrations/`
- `Typer` CLI interface
- Optional static browser dashboard
- `pytest` and `FastAPI TestClient`
- `Redis` + async worker groundwork for EX3

## Quick Start

Create and activate the environment:

```bash
uv venv
.venv\Scripts\activate
```

Install dependencies:

```bash
uv sync
```

Optional: copy values from `.env.example`.

Apply migrations and seed demo data:

```bash
python -m scripts.migrate
python scripts/seed_products.py
```

Run the API locally:

```bash
python -m uvicorn app.main:app --reload
```

Useful API URLs:

- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Optional browser dashboard: `http://127.0.0.1:8000/app`

## CLI Interface

Run the API in one terminal, then run the Typer interface in another terminal.

List existing tracked products:

```bash
python -m app.cli list-products
```

Add a new tracked product:

```bash
python -m app.cli add-product --name "Steam Deck OLED" --store "Valve" --product-url "https://example.com/steam-deck-oled" --current-price 2599 --target-price 2499 --user-email analyst@priceradar.local
```

View summary metrics:

```bash
python -m app.cli summary
```

Export tracked products to CSV:

```bash
python -m app.cli export-csv
```

## Core API

- `GET /health`
- `GET /products`
- `GET /products/{product_id}`
- `POST /products`
- `PUT /products/{product_id}`
- `DELETE /products/{product_id}`
- `GET /products/summary`

Manual API playground:

- `requests.http`

## Tests

Run all tests:

```bash
python -m pytest
```

The test suite covers:

- API list/create/update/delete flows
- FastAPI `TestClient` behavior
- Validation and error cases
- Typer CLI list/add workflows with `CliRunner`
- Auth and async refresh groundwork used for EX3

## Exercise Mapping

### EX1 - FastAPI Foundations

- CRUD backend for the main resource: tracked products.
- Validation for URLs, email, and price rules.
- Repository and service layers.
- SQLModel + SQLite persistence.
- SQL migrations and seed script.
- `pytest` coverage for list/create/update/delete.
- README and `requests.http` playground.

### EX2 - Friendly Interface

- Reuses the EX1 API as-is for the core flows.
- Official graded interface: Typer CLI in `app/cli.py`.
- Lists existing entries with `list-products`.
- Adds new entries with `add-product`.
- Provides extras with `summary` and `export-csv`.
- Documents side-by-side API and CLI usage.
- Includes automated CLI workflow tests in `tests/test_cli.py`.

### EX3 Groundwork

- `compose.yaml` for API, Redis, and worker.
- `scripts/refresh.py` with bounded concurrency, retries, and Redis-backed idempotency.
- JWT auth, hashed demo credentials, protected routes, and role checks.
- `docs/runbooks/compose.md` and `docs/EX3-notes.md`.
- Demo script at `python -m app.demo`.

## Files That Matter Most

- `app/main.py`: FastAPI routes and API wiring.
- `app/cli.py`: Typer interface for EX2.
- `app/models.py`: SQLModel/Pydantic models and validation.
- `app/repositories.py`: persistence access.
- `app/services.py`: product, auth, and report logic.
- `migrations/`: SQL migration history.
- `scripts/seed_products.py`: reproducible demo data.
- `tests/`: API, CLI, auth, and refresh tests.

## Notes

- The database lives under `data/` by default.
- `*.db` files are ignored by git and should not be committed.
- The project uses migrations and seed scripts instead of committing SQLite artifacts.
- The browser dashboard is optional; the official EX2 interface is the Typer CLI.

## AI Assistance

AI assistance was used for planning, review, refactoring ideas, UI copy, and documentation drafting. Generated changes were verified locally with `python -m pytest` and manual API/interface checks.
