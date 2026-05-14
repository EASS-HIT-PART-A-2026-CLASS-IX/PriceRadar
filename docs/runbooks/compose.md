# Compose Runbook

## Start the local EX3 stack

```bash
docker compose up --build
```

Services:

- `api` on `http://127.0.0.1:8000`
- `redis` on `redis://127.0.0.1:6379/0`
- `worker` running `python -m app.worker`

## Verify health and rate-limit headers

```bash
curl -i http://127.0.0.1:8000/health
```

Expected headers include:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

## Seed demo data

```bash
docker compose exec api python -m scripts.migrate
docker compose exec api python scripts/seed_products.py
```

## Run the Typer interface

```bash
docker compose exec api python -m app.cli list-products
docker compose exec api python -m app.cli preview-url --product-url "https://demo.ksp.local/products/sony-wh1000xm5"
docker compose exec api python -m app.cli track-url --product-url "https://demo.ksp.local/products/sony-wh1000xm5" --target-price 999
docker compose exec api python -m app.cli summary
docker compose exec api python -m app.cli weekly-digest
```

The browser dashboard is available at `http://127.0.0.1:8000/app`. Paste one of these supported URLs into the hero input:

- `https://demo.ksp.local/products/sony-wh1000xm5`
- `https://demo.ivory.local/products/steam-deck-oled`
- `https://demo.bug.local/products/pixel-8-pro`

## Verify refresh and alert events

```bash
docker compose exec api python -m scripts.refresh
curl http://127.0.0.1:8000/alerts/events
curl http://127.0.0.1:8000/alerts/email-outbox
```

When a refreshed price crosses below the product target, `/alerts/events` returns the stored local alert row and `/alerts/email-outbox` returns the local `Email Sent` record. The footer link `Email alert preview` opens the same outbox in a branded browser view.

## Run checks

```bash
uv run python -m pytest
uv run schemathesis run --checks not_a_server_error,status_code_conformance,content_type_conformance,response_schema_conformance -n 10 --request-timeout 5 http://localhost:8000/openapi.json
```

On Windows PowerShell, set UTF-8 output first if Schemathesis renders box-drawing characters:

```powershell
$env:PYTHONIOENCODING = "utf-8"
uv run schemathesis run --checks not_a_server_error,status_code_conformance,content_type_conformance,response_schema_conformance -n 10 --request-timeout 5 http://localhost:8000/openapi.json
```

The Schemathesis command is the CI-friendly smoke test for the contract. `pytest` covers API, CLI, auth, and the async refresh worker.
