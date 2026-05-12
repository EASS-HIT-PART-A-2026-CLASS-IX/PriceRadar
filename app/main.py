from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from html import escape

from fastapi import Depends, FastAPI, Query, Request, Response, status
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from redis import asyncio as redis_asyncio
from sqlmodel import Session

from app.auth import AuthenticatedUser, get_current_user, require_role, require_scope
from app.bootstrap import ensure_demo_users
from app.config import get_settings
from app.database import create_db_and_tables, engine, get_session
from app.imports import preview_product_url, supported_store_hosts
from app.models import (
    EmailOutboxMessage,
    EmailOutboxMessageRead,
    PriceAlertEvent,
    PriceAlertEventRead,
    ProductUrlPreviewRead,
    ProductUrlPreviewRequest,
    TokenResponse,
    TrackedProduct,
    TrackedProductCreate,
    TrackedProductRead,
    TrackedProductUpdate,
    UserLogin,
    UserRead,
    UserRole,
)
from app.refresh import RefreshCoordinator
from app.repositories import AlertRepository, EmailOutboxRepository, ProductRepository, UserRepository
from app.services import AuthService, ProductService, ReportService


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    create_db_and_tables()
    with Session(engine) as session:
        ensure_demo_users(session)
    yield


app = FastAPI(title="PriceRadar API", version="0.3.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

UNAUTHORIZED_RESPONSE = {401: {"description": "Missing, invalid, or expired credentials"}}
FORBIDDEN_RESPONSE = {403: {"description": "Authenticated user is not allowed to use this route"}}
NOT_FOUND_RESPONSE = {404: {"description": "Requested resource was not found"}}
PROTECTED_ROUTE_RESPONSES = {
    **UNAUTHORIZED_RESPONSE,
    **FORBIDDEN_RESPONSE,
}
VALIDATION_OR_MESSAGE_RESPONSE = {
    422: {
        "description": "Validation error or business rule violation",
        "content": {
            "application/json": {
                "schema": {
                    "anyOf": [
                        {"$ref": "#/components/schemas/HTTPValidationError"},
                        {
                            "type": "object",
                            "properties": {"detail": {"type": "string"}},
                            "required": ["detail"],
                        },
                    ]
                }
            }
        },
    }
}


@app.middleware("http")
async def add_rate_limit_headers(request: Request, call_next):
    response = await call_next(request)
    settings = get_settings()
    response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_limit)
    response.headers["X-RateLimit-Remaining"] = str(max(settings.rate_limit_limit - 1, 0))
    response.headers["X-RateLimit-Reset"] = str(settings.rate_limit_window_seconds)
    return response


def get_product_service(session: Session = Depends(get_session)) -> ProductService:
    return ProductService(
        ProductRepository(session),
        AlertRepository(session),
        EmailOutboxRepository(session),
    )


def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    return AuthService(UserRepository(session))


def get_report_service(session: Session = Depends(get_session)) -> ReportService:
    return ReportService(ProductRepository(session))


def get_alert_repository(session: Session = Depends(get_session)) -> AlertRepository:
    return AlertRepository(session)


def get_email_outbox_repository(session: Session = Depends(get_session)) -> EmailOutboxRepository:
    return EmailOutboxRepository(session)


@app.get("/", tags=["Meta"], summary="Get API summary")
def root() -> dict[str, str]:
    return {
        "name": "PriceRadar API",
        "version": "0.3.0",
        "docs": "/docs",
        "health": "/health",
        "interface": "Typer CLI via python -m app.cli and browser dashboard at /app",
    }


@app.get("/health", tags=["Meta"], summary="Check API health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "service": "priceradar-api"}


@app.post(
    "/auth/login",
    response_model=TokenResponse,
    tags=["Auth"],
    responses=PROTECTED_ROUTE_RESPONSES,
)
def login(login_request: UserLogin, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    return service.login(login_request)


@app.get("/auth/me", response_model=UserRead, tags=["Auth"], responses=UNAUTHORIZED_RESPONSE)
def read_current_user(current: AuthenticatedUser = Depends(get_current_user)) -> UserRead:
    return UserRead(
        email=current.user.email,
        full_name=current.user.full_name,
        role=current.user.role,
        is_active=current.user.is_active,
    )


@app.get(
    "/app",
    tags=["Frontend"],
    summary="Open optional PriceRadar dashboard",
    response_class=HTMLResponse,
)
def dashboard() -> FileResponse:
    return FileResponse("app/static/index.html")


@app.get(
    "/alerts/email-preview",
    tags=["Alerts"],
    summary="Preview branded price-drop email HTML",
    response_class=HTMLResponse,
)
def preview_email_template(
    product_name: str = Query(default="Sony WH-1000XM5"),
    current_price: float = Query(default=899.90, ge=0),
    target_price: float = Query(default=999.90, ge=0),
    store: str = Query(default="KSP"),
    deal_url: str = Query(default="https://example.com/products/sony-wh1000xm5"),
    repository: EmailOutboxRepository = Depends(get_email_outbox_repository),
) -> HTMLResponse:
    messages = repository.list(limit=25)
    latest = messages[0] if messages else None
    if latest is not None:
        product_name = latest.product_name
        current_price = latest.current_price
        target_price = latest.target_price
        store = latest.store
        deal_url = latest.product_url
    recipient = latest.recipient_email if latest else "user@priceradar.local"
    created_at = latest.created_at.strftime("%Y-%m-%d %H:%M") if latest else "Preview mode"
    safe_product_name = escape(product_name)
    safe_store = escape(store)
    safe_deal_url = escape(deal_url, quote=True)
    safe_recipient = escape(recipient)
    safe_created_at = escape(created_at)
    savings = max(target_price - current_price, 0)
    outbox_rows = "".join(
        f"""
              <tr>
                <td style="padding:14px 16px;border-top:1px solid #e4e4e7;font-size:14px;color:#0f172a;font-weight:700;">{escape(message.product_name)}</td>
                <td style="padding:14px 16px;border-top:1px solid #e4e4e7;font-size:14px;color:#475569;">{escape(message.recipient_email)}</td>
                <td style="padding:14px 16px;border-top:1px solid #e4e4e7;font-size:14px;color:#059669;font-weight:800;">₪{message.current_price:,.2f}</td>
                <td style="padding:14px 16px;border-top:1px solid #e4e4e7;font-size:14px;color:#3b82f6;font-weight:800;">₪{message.target_price:,.2f}</td>
                <td style="padding:14px 16px;border-top:1px solid #e4e4e7;font-size:13px;color:#64748b;">{message.created_at.strftime("%Y-%m-%d %H:%M")}</td>
              </tr>
        """
        for message in messages
    )
    if not outbox_rows:
        outbox_rows = """
              <tr>
                <td colspan="5" style="padding:18px 16px;border-top:1px solid #e4e4e7;font-size:14px;color:#64748b;">No sent email records yet. Update a tracked product so its current price reaches the target, or run the refresh worker.</td>
              </tr>
        """
    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>PriceRadar Alert</title>
  </head>
  <body style="margin:0;padding:0;background:#f8fafc;font-family:Inter,Arial,sans-serif;color:#0f172a;">
    <div style="border-bottom:1px solid #e4e4e7;background:rgba(255,255,255,0.88);">
      <div style="max-width:1100px;margin:0 auto;padding:18px 24px;display:flex;align-items:center;justify-content:space-between;">
        <a href="/app" style="display:flex;align-items:center;gap:12px;text-decoration:none;color:#0f172a;">
          <span style="display:inline-flex;height:38px;width:38px;align-items:center;justify-content:center;border-radius:12px;background:#eff6ff;color:#3b82f6;font-weight:800;">PR</span>
          <span>
            <span style="display:block;font-size:18px;font-weight:800;letter-spacing:-0.01em;">PriceRadar</span>
            <span style="display:block;margin-top:2px;font-size:12px;color:#64748b;">Premium Price Tracking</span>
          </span>
        </a>
        <a href="/app#/tracked" style="border-radius:999px;background:#3b82f6;color:#ffffff;text-decoration:none;padding:10px 16px;font-size:14px;font-weight:700;">Back to App</a>
      </div>
    </div>

    <main style="max-width:1100px;margin:0 auto;padding:40px 24px 56px;">
      <section style="display:grid;grid-template-columns:minmax(0,1fr);gap:22px;">
        <div>
          <p style="margin:0 0 10px;font-size:12px;font-weight:800;letter-spacing:0.14em;text-transform:uppercase;color:#64748b;">Email alert preview</p>
          <h1 style="margin:0;font-size:40px;line-height:1.08;font-weight:800;letter-spacing:-0.03em;color:#020617;">Price drop email ready to send.</h1>
          <p style="margin:14px 0 0;max-width:680px;font-size:16px;line-height:1.7;color:#475569;">
            This is the message PriceRadar prepares when a tracked product drops below the user's target price.
          </p>
        </div>

        <div style="border:1px solid #e4e4e7;border-radius:28px;background:#ffffff;box-shadow:0 24px 80px -45px rgba(15,23,42,0.38);overflow:hidden;">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:14px;border-bottom:1px solid #e4e4e7;background:#f8fafc;padding:18px 22px;">
            <div>
              <div style="font-size:13px;color:#64748b;">To</div>
              <div style="margin-top:3px;font-size:15px;font-weight:700;color:#0f172a;">{safe_recipient}</div>
            </div>
            <span style="border-radius:999px;background:#ecfdf5;color:#059669;padding:7px 12px;font-size:12px;font-weight:800;">Email Sent</span>
          </div>

          <div style="padding:28px;">
            <div style="margin-bottom:20px;border:1px solid #dbeafe;border-radius:22px;background:linear-gradient(135deg,#eff6ff,#ffffff);padding:22px;">
              <div style="font-size:13px;font-weight:800;letter-spacing:0.12em;text-transform:uppercase;color:#3b82f6;">PriceRadar Alert</div>
              <h2 style="margin:10px 0 0;font-size:28px;line-height:1.2;font-weight:800;color:#020617;">{safe_product_name} dropped below your target.</h2>
              <p style="margin:12px 0 0;font-size:15px;line-height:1.65;color:#475569;">
                The latest refresh found a lower price at <strong>{safe_store}</strong>. The product is now below the price you asked us to watch.
              </p>
            </div>

            <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-bottom:22px;">
              <div style="border-radius:18px;background:#f8fafc;padding:16px;">
                <div style="font-size:12px;color:#64748b;">Current price</div>
                <div style="margin-top:6px;font-size:24px;font-weight:800;color:#059669;">₪{current_price:,.2f}</div>
              </div>
              <div style="border-radius:18px;background:#f8fafc;padding:16px;">
                <div style="font-size:12px;color:#64748b;">Your target</div>
                <div style="margin-top:6px;font-size:24px;font-weight:800;color:#3b82f6;">₪{target_price:,.2f}</div>
              </div>
              <div style="border-radius:18px;background:#f8fafc;padding:16px;">
                <div style="font-size:12px;color:#64748b;">Below target by</div>
                <div style="margin-top:6px;font-size:24px;font-weight:800;color:#0f172a;">₪{savings:,.2f}</div>
              </div>
            </div>

            <div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:14px;border-top:1px solid #e4e4e7;padding-top:20px;">
              <div>
                <div style="font-size:13px;color:#64748b;">Store</div>
                <div style="margin-top:4px;font-size:16px;font-weight:700;color:#0f172a;">{safe_store}</div>
                <div style="margin-top:8px;font-size:12px;color:#94a3b8;">Sent at {safe_created_at}</div>
              </div>
              <a href="{safe_deal_url}" style="display:inline-block;border-radius:14px;background:#3b82f6;color:#ffffff;text-decoration:none;padding:13px 20px;font-size:14px;font-weight:800;">View Deal</a>
            </div>
          </div>
        </div>

        <div style="border:1px solid #e4e4e7;border-radius:24px;background:#ffffff;overflow:hidden;">
          <div style="padding:20px 22px;border-bottom:1px solid #e4e4e7;background:#f8fafc;">
            <h2 style="margin:0;font-size:20px;font-weight:800;color:#0f172a;">Sent Email Outbox</h2>
            <p style="margin:6px 0 0;font-size:14px;color:#64748b;">Local records created when PriceRadar detects a price drop.</p>
          </div>
          <div style="overflow-x:auto;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;min-width:720px;">
              <thead>
                <tr>
                  <th align="left" style="padding:12px 16px;font-size:12px;text-transform:uppercase;letter-spacing:0.12em;color:#64748b;">Product</th>
                  <th align="left" style="padding:12px 16px;font-size:12px;text-transform:uppercase;letter-spacing:0.12em;color:#64748b;">Recipient</th>
                  <th align="left" style="padding:12px 16px;font-size:12px;text-transform:uppercase;letter-spacing:0.12em;color:#64748b;">New Price</th>
                  <th align="left" style="padding:12px 16px;font-size:12px;text-transform:uppercase;letter-spacing:0.12em;color:#64748b;">Target</th>
                  <th align="left" style="padding:12px 16px;font-size:12px;text-transform:uppercase;letter-spacing:0.12em;color:#64748b;">Sent</th>
                </tr>
              </thead>
              <tbody>
                {outbox_rows}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </main>
  </body>
</html>"""
    return HTMLResponse(content=html)


@app.post(
    "/imports/url-preview",
    response_model=ProductUrlPreviewRead,
    tags=["Imports"],
    summary="Preview a supported external product URL",
    responses={**NOT_FOUND_RESPONSE, **VALIDATION_OR_MESSAGE_RESPONSE},
)
def preview_url_import(request: ProductUrlPreviewRequest) -> ProductUrlPreviewRead:
    return preview_product_url(request.product_url)


@app.get("/imports/supported-stores", tags=["Imports"], summary="List supported import hosts")
def list_supported_import_hosts() -> dict[str, list[str]]:
    return {"supported_hosts": supported_store_hosts()}


@app.get("/products/summary", tags=["Products"], summary="Get tracked products summary")
def products_summary(service: ProductService = Depends(get_product_service)) -> dict[str, float | int]:
    return service.get_summary()


@app.get(
    "/products",
    response_model=list[TrackedProductRead],
    tags=["Products"],
    summary="List tracked products",
)
def list_products(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    user_email: str | None = Query(default=None),
    service: ProductService = Depends(get_product_service),
) -> list[TrackedProduct]:
    return service.list_products(offset=offset, limit=limit, user_email=user_email)


@app.get(
    "/products/{product_id}",
    response_model=TrackedProductRead,
    tags=["Products"],
    summary="Get a tracked product by id",
    responses=NOT_FOUND_RESPONSE,
)
def get_product(
    product_id: int, service: ProductService = Depends(get_product_service)
) -> TrackedProduct:
    return service.get_product(product_id)


@app.post(
    "/products",
    response_model=TrackedProductRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Products"],
    summary="Create a tracked product",
    responses=VALIDATION_OR_MESSAGE_RESPONSE,
)
def create_product(
    product_in: TrackedProductCreate, service: ProductService = Depends(get_product_service)
) -> TrackedProduct:
    return service.create_product(product_in)


@app.put(
    "/products/{product_id}",
    response_model=TrackedProductRead,
    tags=["Products"],
    summary="Update a tracked product",
    responses={**NOT_FOUND_RESPONSE, **VALIDATION_OR_MESSAGE_RESPONSE},
)
def update_product(
    product_id: int,
    product_in: TrackedProductUpdate,
    service: ProductService = Depends(get_product_service),
) -> TrackedProduct:
    return service.update_product(product_id, product_in)


@app.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Products"],
    summary="Delete a tracked product",
    responses=NOT_FOUND_RESPONSE,
)
def delete_product(
    product_id: int, service: ProductService = Depends(get_product_service)
) -> Response:
    service.delete_product(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/alerts/events",
    response_model=list[PriceAlertEventRead],
    tags=["Alerts"],
    summary="List local price-drop alert events",
)
def list_alert_events(
    repository: AlertRepository = Depends(get_alert_repository),
) -> list[PriceAlertEvent]:
    return repository.list()


@app.get(
    "/alerts/email-outbox",
    response_model=list[EmailOutboxMessageRead],
    tags=["Alerts"],
    summary="List local sent email records",
)
def list_email_outbox(
    repository: EmailOutboxRepository = Depends(get_email_outbox_repository),
) -> list[EmailOutboxMessage]:
    return repository.list()


@app.delete(
    "/alerts/email-outbox",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Alerts"],
    summary="Clear local sent email records",
)
def clear_email_outbox(
    repository: EmailOutboxRepository = Depends(get_email_outbox_repository),
) -> Response:
    repository.clear()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/reports/weekly-digest",
    tags=["Reports"],
    response_class=PlainTextResponse,
    summary="Read the protected weekly markdown digest",
    responses=PROTECTED_ROUTE_RESPONSES,
)
def weekly_digest(
    _: AuthenticatedUser = Depends(require_scope("reports:read")),
    __: AuthenticatedUser = Depends(require_role(UserRole.admin)),
    service: ReportService = Depends(get_report_service),
) -> PlainTextResponse:
    return PlainTextResponse(service.weekly_digest_markdown(), media_type="text/markdown")


@app.post(
    "/refresh/run",
    tags=["Refresh"],
    summary="Trigger one protected refresh cycle",
    responses=PROTECTED_ROUTE_RESPONSES,
)
async def run_refresh(
    _: AuthenticatedUser = Depends(require_scope("refresh:run")),
    __: AuthenticatedUser = Depends(require_role(UserRole.admin)),
) -> dict[str, int]:
    settings = get_settings()
    redis = redis_asyncio.from_url(settings.redis_url, decode_responses=True)
    coordinator = RefreshCoordinator(
        session_factory=lambda: Session(engine),
        redis_client=redis,
        concurrency_limit=settings.refresh_concurrency,
        retry_attempts=settings.refresh_retry_attempts,
    )
    try:
        stats = await coordinator.run_for_day()
    finally:
        await redis.close()
    return {
        "processed": stats.processed,
        "skipped": stats.skipped,
        "retries": stats.retries,
    }
