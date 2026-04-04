from datetime import datetime, UTC
from typing import Optional

from pydantic import field_validator
from sqlmodel import Field, SQLModel


class TrackedProductBase(SQLModel):
    name: str = Field(index=True, min_length=1, max_length=120)
    store: str = Field(min_length=1, max_length=80)
    product_url: str = Field(min_length=1, max_length=500)
    current_price: float = Field(ge=0)
    target_price: float = Field(ge=0)
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


class TrackedProduct(TrackedProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TrackedProductCreate(TrackedProductBase):
    pass


class TrackedProductUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    store: Optional[str] = Field(default=None, min_length=1, max_length=80)
    product_url: Optional[str] = Field(default=None, min_length=1, max_length=500)
    current_price: Optional[float] = Field(default=None, ge=0)
    target_price: Optional[float] = Field(default=None, ge=0)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    is_active: Optional[bool] = None

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


class TrackedProductRead(TrackedProductBase):
    id: int
    created_at: datetime
