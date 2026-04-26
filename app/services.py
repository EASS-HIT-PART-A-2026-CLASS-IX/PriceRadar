from __future__ import annotations

from datetime import timedelta

from fastapi import HTTPException, status

from app.auth import create_access_token, verify_password
from app.config import get_settings
from app.models import (
    AppUser,
    TokenResponse,
    TrackedProduct,
    TrackedProductCreate,
    TrackedProductUpdate,
    UserLogin,
)
from app.repositories import ProductRepository, UserRepository


class ProductService:
    def __init__(self, repository: ProductRepository) -> None:
        self.repository = repository

    def list_products(
        self, *, offset: int = 0, limit: int = 100, user_email: str | None = None
    ) -> list[TrackedProduct]:
        return self.repository.list(offset=offset, limit=limit, user_email=user_email)

    def get_product(self, product_id: int) -> TrackedProduct:
        product = self.repository.get(product_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product

    def create_product(self, product_in: TrackedProductCreate) -> TrackedProduct:
        self._validate_price_target(
            current_price=product_in.current_price,
            target_price=product_in.target_price,
        )
        return self.repository.create(product_in)

    def update_product(self, product_id: int, product_in: TrackedProductUpdate) -> TrackedProduct:
        product = self.get_product(product_id)
        next_current_price = (
            product.current_price if product_in.current_price is None else product_in.current_price
        )
        next_target_price = (
            product.target_price if product_in.target_price is None else product_in.target_price
        )
        if product_in.target_price is not None:
            self._validate_price_target(
                current_price=next_current_price,
                target_price=next_target_price,
            )
        return self.repository.update(product, product_in)

    def delete_product(self, product_id: int) -> None:
        product = self.get_product(product_id)
        self.repository.delete(product)

    def get_summary(self) -> dict[str, float | int]:
        return self.repository.summary()

    @staticmethod
    def _validate_price_target(*, current_price: float, target_price: float) -> None:
        if target_price > current_price:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="target_price must be less than or equal to current_price",
            )


class AuthService:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    def login(self, login_request: UserLogin) -> TokenResponse:
        user = self.users.get_by_email(login_request.email)
        if user is None or not verify_password(login_request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive",
            )

        scopes = self._scopes_for_role(user)
        settings = get_settings()
        token = create_access_token(
            subject=user.email,
            role=user.role,
            scopes=scopes,
            expires_delta=timedelta(minutes=settings.access_token_minutes),
        )
        return TokenResponse(
            access_token=token,
            expires_in_seconds=settings.access_token_minutes * 60,
            scopes=scopes,
            role=user.role,
        )

    @staticmethod
    def _scopes_for_role(user: AppUser) -> list[str]:
        if user.role.value == "admin":
            return ["reports:read", "refresh:run"]
        return ["reports:read"]


class ReportService:
    def __init__(self, products: ProductRepository) -> None:
        self.products = products

    def weekly_digest_markdown(self) -> str:
        summary = self.products.summary()
        tracked = self.products.list(limit=20)
        lines = [
            "# PriceRadar Weekly Digest",
            "",
            f"- Total tracked products: {summary['total']}",
            f"- Active products: {summary['active']}",
            f"- Products already below target: {summary['below_target']}",
            f"- Average target price: {summary['average_target_price']}",
            "",
            "## Closest Deals",
        ]
        if not tracked:
            lines.append("- No products tracked yet.")
            return "\n".join(lines)

        ranked = sorted(
            tracked,
            key=lambda product: abs(product.current_price - product.target_price),
        )[:5]
        for product in ranked:
            difference = round(product.current_price - product.target_price, 2)
            lines.append(
                f"- {product.name} at {product.store}: current {product.current_price:.2f} {product.currency}, "
                f"target {product.target_price:.2f} {product.currency}, gap {difference:.2f}"
            )
        return "\n".join(lines)
