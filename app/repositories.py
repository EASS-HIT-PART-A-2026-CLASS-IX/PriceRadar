from sqlmodel import Session, select

from app.models import TrackedProduct, TrackedProductCreate, TrackedProductUpdate


class ProductRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(self, *, offset: int = 0, limit: int = 100) -> list[TrackedProduct]:
        statement = select(TrackedProduct).order_by(TrackedProduct.id).offset(offset).limit(limit)
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
        update_data = product_in.model_dump(exclude_unset=True)
        product.sqlmodel_update(update_data)
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def delete(self, product: TrackedProduct) -> None:
        self.session.delete(product)
        self.session.commit()
