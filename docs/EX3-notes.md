# EX3 Notes

## Architecture

PriceRadar keeps the same domain from EX1 and EX2: shoppers track products and target prices until a weekly digest or refresh cycle tells them a deal is ready.

The EX3 stack now contains:

1. `FastAPI` backend in `app/main.py`
2. SQLite persistence with SQLModel models plus SQL migrations in `migrations/`
3. `Typer` interface in `app/cli.py`
4. Background refresh worker in `app/worker.py`
5. Redis for idempotent refresh runs

## Async refresher

The worker and `scripts/refresh.py` run bounded concurrent refresh jobs with retries and Redis-backed idempotency keys of the form `refresh:YYYY-MM-DD:<product_id>`.

Example trace excerpt:

```text
worker-cycle processed=2 skipped=0 retries=1
refresh completed processed=0 skipped=2 retries=0
redis key refresh:2026-04-14:1 claimed
redis key refresh:2026-04-14:2 claimed
```

## Security baseline

- Passwords are hashed with PBKDF2-SHA256 in `app/auth.py`
- JWT access tokens are issued by `POST /auth/login`
- `GET /reports/weekly-digest` requires both `reports:read` scope and `admin` role
- `POST /refresh/run` requires both `refresh:run` scope and `admin` role

### Secret rotation steps

1. Change `JWT_SECRET` in `.env` or compose environment.
2. Restart `api` and `worker`.
3. Log in again so graders receive freshly signed tokens.
4. If demo credentials were shared, rotate `DEMO_ADMIN_PASSWORD` and `DEMO_ANALYST_PASSWORD`, then rerun `python scripts/seed_products.py` on a fresh database.

## Enhancement

The EX3 enhancement is the protected weekly markdown digest. It stays small, uses the same tracked product data, and adds value without turning the project into a larger platform.
