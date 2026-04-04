# PriceRadar - Shopping Price Tracking and Alert System

`PriceRadar` is a small `FastAPI` backend for tracking products and saving a target price for future alerts. The current version focuses on the core CRUD flow for tracked products and is structured so it can grow into later exercises without replacing the API foundation.

## Stack

- `FastAPI`
- `SQLModel`
- `SQLite`
- `pytest`
- Repository and service layers

## Features

- Create, view, update, and delete tracked products
- Persist data in a local `SQLite` database
- Filterable list endpoint with `offset` and `limit`
- Auto-generated API docs with Swagger and ReDoc
- Sample seed script for demo data
- Input validation for URLs, prices, and required fields

## Product Model

Tracked products contain:

- `id`
- `name`
- `store`
- `product_url`
- `current_price`
- `target_price`
- `currency`
- `is_active`
- `created_at`

## Quick Start

1. Create a virtual environment:

```bash
uv venv
```

2. Activate it on Windows PowerShell:

```bash
.venv\Scripts\activate
```

3. Install dependencies:

```bash
uv sync
```

4. Optional: set a custom database path.

PowerShell:

```powershell
$env:DATABASE_URL="sqlite:///./priceradar.db"
```

Bash:

```bash
export DATABASE_URL="sqlite:///./priceradar.db"
```

An example is also available in `.env.example`.

5. Optional: seed sample products:

```bash
uv run python scripts/seed_products.py
```

## Run the API

```bash
uv run uvicorn app.main:app --reload
```

The API starts on `http://127.0.0.1:8000`.

Interactive docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Main Endpoints

- `GET /`
- `GET /health`
- `GET /products`
- `GET /products/{product_id}`
- `POST /products`
- `PUT /products/{product_id}`
- `DELETE /products/{product_id}`

Example create request:

```json
{
  "name": "Sony WH-1000XM5",
  "store": "KSP",
  "product_url": "https://example.com/products/sony-wh1000xm5",
  "current_price": 1299.9,
  "target_price": 999.9,
  "currency": "ILS",
  "is_active": true
}
```

## Tests

Run the test suite with:

```bash
uv run pytest
```

If `uv` is not installed, use:

```bash
python -m pytest
```

Current automated coverage includes:

- Empty-state listing
- Create, update, delete flows
- Missing-resource `404` handling
- Pagination behavior
- Validation failures for invalid URL and invalid target price

## Project Structure

- `app/main.py`: FastAPI app, routes, and startup lifecycle
- `app/models.py`: SQLModel entities and request/response schemas
- `app/database.py`: engine, session dependency, and table creation
- `app/repositories.py`: data access layer
- `app/services.py`: business logic layer
- `scripts/seed_products.py`: inserts demo products into the database
- `tests/test_main.py`: API test coverage
- `requests.http`: manual request collection for local testing

## Notes

- The default database file `priceradar.db` is intentionally ignored by `git`.
- The app reads `DATABASE_URL` directly from the environment; `.env.example` is documentation only unless you load it yourself.
- `requests.http` can be used from editors that support HTTP request files.
- The layered structure keeps route handlers thin and makes later features easier to add.

## EX1 Submission Checklist

- REST API implemented with `FastAPI`
- Persistent storage implemented with `SQLite` and `SQLModel`
- Full CRUD for the main resource `tracked products`
- Separation between routes, service logic, and repository access
- Automated tests included and passing
- `README` includes setup, run, and test instructions
- Manual request file included for quick demo during grading

## Suggested Demo Flow

If the lecturer opens the project for a quick review, this order is the clearest:

1. Open Swagger at `http://127.0.0.1:8000/docs`
2. Call `GET /health`
3. Create a product with `POST /products`
4. Show `GET /products` and `GET /products/{id}`
5. Update the price with `PUT /products/{id}`
6. Delete it with `DELETE /products/{id}`
7. Mention that tests pass with `python -m pytest`

## AI Assistance

This project was developed with AI assistance for planning, scaffolding, and review. The code and documentation should still be verified locally by running the API and tests.
