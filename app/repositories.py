from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, select

from app.models import (
    AppUser,
    EmailOutboxMessage,
    PriceAlertEvent,
    TrackedProduct,
    TrackedProductCreate,
    TrackedProductUpdate,
)


class ProductRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(
        self, *, offset: int = 0, limit: int = 100, user_email: str | None = None
    ) -> list[TrackedProduct]:
        statement = select(TrackedProduct).order_by(TrackedProduct.id)
        if user_email is not None:
            statement = statement.where(TrackedProduct.user_email == user_email.lower().strip())
        return list(self.session.exec(statement.offset(offset).limit(limit)))

    def list_active(self) -> list[TrackedProduct]:
        statement = (
            select(TrackedProduct)
            .where(TrackedProduct.is_active.is_(True))
            .order_by(TrackedProduct.id)
        )
        return list(self.session.exec(statement))

    def get(self, product_id: int) -> TrackedProduct | None:
        return self.session.get(TrackedProduct, product_id)

    def create(self, product_in: TrackedProductCreate) -> TrackedProduct:
        product = TrackedProduct.model_validate(product_in)
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def update(self, product: TrackedProduct, product_in: TrackedProductUpdate) -> TrackedProduct:
        update_data = product_in.model_dump(exclude_unset=True, exclude_none=True)
        product.sqlmodel_update(update_data)
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def delete(self, product: TrackedProduct) -> None:
        self.session.delete(product)
        self.session.commit()

    def summary(self) -> dict[str, float | int]:
        products = self.list(limit=500)
        total = len(products)
        active = sum(1 for product in products if product.is_active)
        below_target = sum(1 for product in products if product.current_price <= product.target_price)
        average_target = (
            round(sum(product.target_price for product in products) / total, 2) if total else 0.0
        )
        return {
            "total": total,
            "active": active,
            "below_target": below_target,
            "average_target_price": average_target,
        }


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_email(self, email: str) -> AppUser | None:
        statement = select(AppUser).where(AppUser.email == email.lower().strip())
        return self.session.exec(statement).first()

    def create(self, user: AppUser) -> AppUser:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def list(self) -> list[AppUser]:
        return list(self.session.exec(select(AppUser).order_by(AppUser.id)))


class AlertRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_for_product(
        self,
        *,
        product: TrackedProduct,
        refreshed_price: float,
        checked_at: datetime,
    ) -> PriceAlertEvent:
        alert = PriceAlertEvent(
            product_id=product.id or 0,
            product_name=product.name,
            store=product.store,
            product_url=product.product_url,
            current_price=refreshed_price,
            target_price=product.target_price,
            currency=product.currency,
            message=(
                f"{product.name} is now {refreshed_price:.2f} {product.currency}, "
                f"below target {product.target_price:.2f} {product.currency}."
            ),
            created_at=checked_at,
        )
        self.session.add(alert)
        self.session.commit()
        self.session.refresh(alert)
        return alert

    def list(self, *, limit: int = 100) -> list[PriceAlertEvent]:
        statement = select(PriceAlertEvent).order_by(PriceAlertEvent.id.desc()).limit(limit)
        return list(self.session.exec(statement))


class EmailOutboxRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_for_product(
        self,
        *,
        product: TrackedProduct,
        refreshed_price: float,
        checked_at: datetime,
        alert_event: PriceAlertEvent | None = None,
    ) -> EmailOutboxMessage:
        recipient = product.user_email or "user@priceradar.local"
        subject = f"PriceRadar alert: {product.name} dropped below your target"
        message = EmailOutboxMessage(
            alert_event_id=alert_event.id if alert_event else None,
            product_id=product.id or 0,
            recipient_email=recipient,
            subject=subject,
            product_name=product.name,
            store=product.store,
            product_url=product.product_url,
            current_price=refreshed_price,
            target_price=product.target_price,
            currency=product.currency,
            status="sent",
            created_at=checked_at,
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message

    def list(self, *, limit: int = 100) -> list[EmailOutboxMessage]:
        statement = select(EmailOutboxMessage).order_by(EmailOutboxMessage.id.desc()).limit(limit)
        return list(self.session.exec(statement))

    def clear(self) -> int:
        messages = self.list(limit=500)
        for message in messages:
            self.session.delete(message)
        self.session.commit()
        return len(messages)
