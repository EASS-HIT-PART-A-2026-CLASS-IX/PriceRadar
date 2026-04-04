from fastapi import HTTPException, status

from app.models import TrackedProduct, TrackedProductCreate, TrackedProductUpdate
from app.repositories import ProductRepository


class ProductService:
    def __init__(self, repository: ProductRepository) -> None:
        self.repository = repository

    def list_products(self, *, offset: int = 0, limit: int = 100) -> list[TrackedProduct]:
        return self.repository.list(offset=offset, limit=limit)

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
        self._validate_price_target(
            current_price=next_current_price,
            target_price=next_target_price,
        )
        return self.repository.update(product, product_in)

    def delete_product(self, product_id: int) -> None:
        product = self.get_product(product_id)
        self.repository.delete(product)

    @staticmethod
    def _validate_price_target(*, current_price: float, target_price: float) -> None:
        if target_price > current_price:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="target_price must be less than or equal to current_price",
            )
