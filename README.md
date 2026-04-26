# PriceRadar

PriceRadar keeps one domain through all three exercises: shoppers track real product URLs, set a target price, and later consume summaries or refresh jobs without changing the product storyline.

## Stack

- `FastAPI` backend
- `SQLModel` + `SQLite`
- SQL migrations in `migrations/`
- `Typer` interface for EX2 and EX3
- `Redis` + async refresh worker for EX3
- `pytest` and `FastAPI TestClient`

## What maps to each exercise

### EX1

- CRUD for the main resource: tracked products
- Validation for URLs, email, and price rules
- Repository and service layers
- SQLite persistence
- `pytest` coverage for list/create/update/delete and error cases
- README + `requests.http` + seed script

### EX2

- Same backend reused as-is
- Friendly `Typer` interface that lists products and adds a new one in under a minute
- Extra feature: summary metrics and CSV export
- Optional browser dashboard still available at `/app`
- Automated CLI workflow test included

### EX3

- JWT login with hashed credentials and role checks
- Protected weekly digest enhancement
- `compose.yaml` for API + Redis + worker
- `scripts/refresh.py` with bounded concurrency, retries, and Redis-backed idempotency
- Demo script at `python -m app.demo`
- Runbooks in `docs/runbooks/compose.md`
- Design notes in `docs/EX3-notes.md`

## Quick start

1. Create and activate the environment:

```bash
uv venv
.venv\Scripts\activate
```

2. Install dependencies:

```bash
uv sync
```

3. Optional: copy values from `.env.example`.

4. Apply migrations and seed demo data:

```bash
python -m scripts.migrate
python scripts/seed_products.py
```

5. Run the API locally:

```bash
python -m uvicorn app.main:app --reload
```

API URLs:

- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Optional dashboard: `http://127.0.0.1:8000/app#/`

## EX1 walkthrough

Core endpoints:

- `GET /health`
- `GET /products`
- `GET /products/{product_id}`
- `POST /products`
- `PUT /products/{product_id}`
- `DELETE /products/{product_id}`

Manual playground:

- `requests.http`

Run tests:

```bash
python -m pytest
```

## EX2 interface

The graded interface is the Typer CLI so the project now matches the lecturer's `Streamlit or Typer` requirement.

List existing entries:

```bash
python -m app.cli list-products
```

Add a new entry:

```bash
python -m app.cli add-product --name "Steam Deck OLED" --store "Valve" --product-url "https://example.com/steam-deck-oled" --current-price 2599 --target-price 2499 --user-email analyst@priceradar.local
```

Small extra feature:

```bash
python -m app.cli summary
python -m app.cli export-csv
```

## EX3 local stack

Start the microservice stack:

```bash
docker compose up --build
```

The compose stack includes:

- `api`
- `redis`
- `worker`

Useful EX3 commands:

```bash
python -m app.cli weekly-digest
python -m scripts.refresh
python -m app.demo
```

Protected routes:

- `POST /auth/login`
- `GET /auth/me`
- `GET /reports/weekly-digest`
- `POST /refresh/run`

Demo users:

- Admin: `admin@priceradar.local` / `ChangeMe123!`
- Analyst: `analyst@priceradar.local` / `Analyst123!`

## Files that matter most

- `app/main.py`: FastAPI routes, rate-limit headers, auth endpoints
- `app/cli.py`: EX2 and EX3 interface
- `app/auth.py`: password hashing and JWT
- `app/refresh.py`: async refresh coordinator
- `app/worker.py`: background worker loop
- `migrations/`: SQL migration history
- `docs/runbooks/compose.md`: compose verification guide
- `docs/EX3-notes.md`: EX3 architecture and security notes

## Notes

- The database lives under `data/` by default and `*.db` is ignored by git.
- The project uses SQL migrations instead of committing SQLite artifacts.
- The optional browser dashboard is still present, but the official interface for grading is the Typer CLI.

## AI Assistance

AI assistance was used for planning, review, refactoring ideas, and documentation drafting. Every generated change was then verified locally by running tests and checking the API behavior.
