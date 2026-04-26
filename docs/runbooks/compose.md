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
python -m scripts.migrate
python scripts/seed_products.py
```

## Run the Typer interface

```bash
python -m app.cli list-products
python -m app.cli summary
python -m app.cli weekly-digest
```

## Run checks

```bash
python -m pytest
python -m schemathesis run http://127.0.0.1:8000/openapi.json --checks all
```

The Schemathesis command is the CI-friendly smoke test for the contract. `pytest` covers API, CLI, auth, and the async refresh worker.
