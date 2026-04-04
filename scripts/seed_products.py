from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlmodel import Session, select

from app.database import create_db_and_tables, engine
from app.models import TrackedProduct


SEED_PRODUCTS = [
    TrackedProduct(
        name="Sony WH-1000XM5",
        store="KSP",
        product_url="https://example.com/products/sony-wh1000xm5",
        current_price=1299.9,
        target_price=999.9,
        currency="ILS",
        is_active=True,
    ),
    TrackedProduct(
        name="Ninja Air Fryer",
        store="Amazon",
        product_url="https://example.com/products/ninja-air-fryer",
        current_price=499.0,
        target_price=420.0,
        currency="ILS",
        is_active=True,
    ),
    TrackedProduct(
        name="Apple Watch SE",
        store="iDigital",
        product_url="https://example.com/products/apple-watch-se",
        current_price=1049.0,
        target_price=899.0,
        currency="ILS",
        is_active=True,
    ),
]


def main() -> None:
    create_db_and_tables()
    with Session(engine) as session:
        existing = session.exec(select(TrackedProduct)).first()
        if existing is not None:
            print("Seed skipped: products already exist.")
            return

        session.add_all(SEED_PRODUCTS)
        session.commit()
        print(f"Seeded {len(SEED_PRODUCTS)} tracked products.")


if __name__ == "__main__":
    main()
