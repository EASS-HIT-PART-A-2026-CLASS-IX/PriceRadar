# EX3 Notes

## Architecture

PriceRadar keeps the same domain from EX1 and EX2: shoppers track products and target prices until a URL refresh cycle tells them a deal is ready.

The EX3 stack now contains:

1. `FastAPI` backend in `app/main.py`
2. SQLite persistence with SQLModel models plus SQL migrations in `migrations/`
3. `Typer` interface in `app/cli.py`
4. Background refresh worker in `app/worker.py`
5. Redis for idempotent refresh runs
6. Deterministic URL import adapters in `app/imports.py`

## Async refresher

The worker and `scripts/refresh.py` run bounded concurrent refresh jobs with retries and Redis-backed idempotency keys of the form `refresh:YYYY-MM-DD:<product_id>`.

For supported stores, the refresh uses the same adapter path as `POST /imports/url-preview`, so preview and refresh agree about product name, store, currency, image, and current price. If a refresh crosses from above target to at-or-below target, PriceRadar stores a local row in `price_alert_events` and a local sent email record in `email_outbox_messages`.

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
4. If demo credentials were shared, rotate `DEMO_ADMIN_PASSWORD` and `DEMO_ANALYST_PASSWORD`, then rerun `uv run python scripts/seed_products.py` on a fresh database.

## Enhancement

The EX3 enhancement is URL-based product import with preview and track confirmation.

Supported demo URLs:

- `https://demo.ksp.local/products/sony-wh1000xm5`
- `https://demo.ivory.local/products/steam-deck-oled`
- `https://demo.bug.local/products/pixel-8-pro`

Flow:

1. The user pastes a supported product URL in `/app` or `uv run python -m app.cli preview-url`.
2. The API selects the adapter by host.
3. The adapter parses deterministic local HTML fixtures.
4. The API returns `name`, `store`, `current_price`, `currency`, `product_url`, and `image_url`.
5. The user confirms a target price.
6. The product is saved to tracked products.
7. The worker refreshes the same URL later and stores an alert event when the price reaches the target.
8. PriceRadar stores a local `Email Sent` outbox record so graders can inspect the notification without requiring SMTP.

The protected weekly markdown digest remains as a small reporting feature, while URL import is the main EX3 product enhancement.

## Demo recording

The repository includes a local walkthrough recording named `video1974253171.mp4`.
It shows the PriceRadar browser dashboard and the main EX3 flow end to end.
