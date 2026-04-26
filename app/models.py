from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import field_validator
from sqlmodel import Field, SQLModel


class UserRole(str, Enum):
    admin = "admin"
    analyst = "analyst"


class TrackedProductBase(SQLModel):
    name: str = Field(index=True, min_length=1, max_length=120)
    store: str = Field(min_length=1, max_length=80)
    product_url: str = Field(min_length=1, max_length=500)
    current_price: float = Field(ge=0)
    target_price: float = Field(ge=0)
    user_email: str | None = Field(default=None, min_length=5, max_length=254)
    currency: str = Field(default="ILS", min_length=3, max_length=3)
    is_active: bool = True

    @field_validator("name", "store", "product_url", "currency", mode="before")
    @classmethod
    def strip_string_values(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("product_url")
    @classmethod
    def validate_product_url(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            raise ValueError("product_url must start with http:// or https://")
        return value

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()

    @field_validator("user_email")
    @classmethod
    def validate_user_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("user_email must be a valid email address")
        return value.lower()


class TrackedProduct(TrackedProductBase, table=True):
    __tablename__ = "tracked_products"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_checked_at: datetime | None = None


class TrackedProductCreate(TrackedProductBase):
    pass


class TrackedProductUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    store: str | None = Field(default=None, min_length=1, max_length=80)
    product_url: str | None = Field(default=None, min_length=1, max_length=500)
    current_price: float | None = Field(default=None, ge=0)
    target_price: float | None = Field(default=None, ge=0)
    user_email: str | None = Field(default=None, min_length=5, max_length=254)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    is_active: bool | None = None
    last_checked_at: datetime | None = None

    @field_validator("name", "store", "product_url", "currency", mode="before")
    @classmethod
    def strip_optional_string_values(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("product_url")
    @classmethod
    def validate_optional_product_url(cls, value: str | None) -> str | None:
        if value is not None and not value.startswith(("http://", "https://")):
            raise ValueError("product_url must start with http:// or https://")
        return value

    @field_validator("currency")
    @classmethod
    def normalize_optional_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.upper()

    @field_validator("user_email")
    @classmethod
    def validate_optional_user_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("user_email must be a valid email address")
        return value.lower()


class TrackedProductRead(TrackedProductBase):
    id: int
    created_at: datetime
    last_checked_at: datetime | None = None


class AppUser(SQLModel, table=True):
    __tablename__ = "app_users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, min_length=5, max_length=254)
    full_name: str = Field(min_length=1, max_length=120)
    password_hash: str = Field(min_length=20, max_length=512)
    role: UserRole = Field(default=UserRole.analyst)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("full_name", mode="before")
    @classmethod
    def normalize_full_name(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class UserLogin(SQLModel):
    email: str
    password: str


class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    scopes: list[str]
    role: UserRole


class UserRead(SQLModel):
    email: str
    full_name: str
    role: UserRole
    is_active: bool
