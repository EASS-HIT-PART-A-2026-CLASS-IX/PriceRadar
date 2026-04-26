from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Query, Request, Response, status
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from redis import asyncio as redis_asyncio
from sqlmodel import Session

from app.auth import AuthenticatedUser, get_current_user, require_role, require_scope
from app.bootstrap import ensure_demo_users
from app.config import get_settings
from app.database import create_db_and_tables, engine, get_session
from app.models import (
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
from app.repositories import ProductRepository, UserRepository
from app.services import AuthService, ProductService, ReportService


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    create_db_and_tables()
    with Session(engine) as session:
        ensure_demo_users(session)
    yield


app = FastAPI(title="PriceRadar API", version="0.3.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.middleware("http")
async def add_rate_limit_headers(request: Request, call_next):
    response = await call_next(request)
    settings = get_settings()
    response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_limit)
    response.headers["X-RateLimit-Remaining"] = str(max(settings.rate_limit_limit - 1, 0))
    response.headers["X-RateLimit-Reset"] = str(settings.rate_limit_window_seconds)
    return response


def get_product_service(session: Session = Depends(get_session)) -> ProductService:
    return ProductService(ProductRepository(session))


def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    return AuthService(UserRepository(session))


def get_report_service(session: Session = Depends(get_session)) -> ReportService:
    return ReportService(ProductRepository(session))


@app.get("/", tags=["Meta"], summary="Get API summary")
def root() -> dict[str, str]:
    return {
        "name": "PriceRadar API",
        "version": "0.3.0",
        "docs": "/docs",
        "health": "/health",
        "interface": "Typer CLI via python -m app.cli",
    }


@app.get("/health", tags=["Meta"], summary="Check API health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "service": "priceradar-api"}


@app.post("/auth/login", response_model=TokenResponse, tags=["Auth"])
def login(login_request: UserLogin, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    return service.login(login_request)


@app.get("/auth/me", response_model=UserRead, tags=["Auth"])
def read_current_user(current: AuthenticatedUser = Depends(get_current_user)) -> UserRead:
    return UserRead(
        email=current.user.email,
        full_name=current.user.full_name,
        role=current.user.role,
        is_active=current.user.is_active,
    )


@app.get("/app", tags=["Frontend"], summary="Open optional PriceRadar dashboard")
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
) -> HTMLResponse:
    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>PriceRadar Alert</title>
  </head>
  <body style="margin:0;padding:0;background:#020617;font-family:Inter,Arial,sans-serif;color:#e2e8f0;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#020617;padding:24px;">
      <tr>
        <td align="center">
          <table role="presentation" width="620" cellspacing="0" cellpadding="0" style="max-width:620px;background:#0f172a;border:1px solid #1e293b;border-radius:16px;overflow:hidden;">
            <tr>
              <td style="padding:24px 28px;background:linear-gradient(135deg,#0f172a,#0b1224);border-bottom:1px solid #1e293b;">
                <div style="font-size:24px;font-weight:700;color:#f8fafc;">PriceRadar</div>
                <div style="margin-top:6px;font-size:13px;color:#93c5fd;">Premium AI Price Tracking</div>
              </td>
            </tr>
            <tr>
              <td style="padding:28px;">
                <h1 style="margin:0 0 10px;font-size:22px;color:#f8fafc;">Price drop detected</h1>
                <p style="margin:0 0 20px;font-size:15px;line-height:1.6;color:#cbd5e1;">
                  Your radar for <strong>{product_name}</strong> is now below your target. Move fast before this deal disappears.
                </p>
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-bottom:20px;">
                  <tr>
                    <td style="padding:14px;background:#020617;border:1px solid #1e293b;border-radius:12px;">
                      <div style="font-size:13px;color:#94a3b8;">Store</div>
                      <div style="font-size:16px;color:#e2e8f0;font-weight:600;margin-top:4px;">{store}</div>
                      <div style="margin-top:12px;font-size:13px;color:#94a3b8;">Current price</div>
                      <div style="font-size:26px;color:#22c55e;font-weight:700;">{current_price:.2f} ILS</div>
                      <div style="margin-top:8px;font-size:13px;color:#94a3b8;">Your target</div>
                      <div style="font-size:16px;color:#60a5fa;font-weight:600;">{target_price:.2f} ILS</div>
                    </td>
                  </tr>
                </table>
                <a href="{deal_url}" style="display:inline-block;background:#2563eb;color:#ffffff;text-decoration:none;padding:12px 22px;border-radius:10px;font-size:14px;font-weight:600;">
                  View Deal
                </a>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""
    return HTMLResponse(content=html)


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
)
def delete_product(
    product_id: int, service: ProductService = Depends(get_product_service)
) -> Response:
    service.delete_product(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/reports/weekly-digest",
    tags=["Reports"],
    response_class=PlainTextResponse,
    summary="Read the protected weekly markdown digest",
)
def weekly_digest(
    _: AuthenticatedUser = Depends(require_scope("reports:read")),
    __: AuthenticatedUser = Depends(require_role(UserRole.admin)),
    service: ReportService = Depends(get_report_service),
) -> PlainTextResponse:
    return PlainTextResponse(service.weekly_digest_markdown(), media_type="text/markdown")


@app.post("/refresh/run", tags=["Refresh"], summary="Trigger one protected refresh cycle")
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
