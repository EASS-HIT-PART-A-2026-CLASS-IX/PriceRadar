from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlmodel import Session, select

from app.bootstrap import ensure_demo_users
from app.config import get_settings
from app.database import create_db_and_tables, engine
from app.models import TrackedProduct


def build_seed_products() -> list[TrackedProduct]:
    settings = get_settings()
    return [
        TrackedProduct(
            name="Sony WH-1000XM5",
            store="KSP Demo",
            product_url="https://demo.ksp.local/products/sony-wh1000xm5",
            image_url="https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6505/6505727_rd.jpg%3BmaxHeight%3D1920%3BmaxWidth%3D900?format=webp",
            current_price=1299.9,
            target_price=999.9,
            user_email=settings.demo_analyst_email,
            currency="ILS",
            is_active=True,
        ),
        TrackedProduct(
            name="Steam Deck OLED",
            store="Ivory Demo",
            product_url="https://demo.ivory.local/products/steam-deck-oled",
            image_url="https://cdn.fastly.steamstatic.com/steamdeck/images/oled/oled_deck_top.png",
            current_price=2599.0,
            target_price=2499.0,
            user_email=settings.demo_admin_email,
            currency="ILS",
            is_active=True,
        ),
        TrackedProduct(
            name="Google Pixel 8 Pro",
            store="Bug Demo",
            product_url="https://demo.bug.local/products/pixel-8-pro",
            image_url="https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6559/6559251_sd.jpg%3BmaxHeight%3D1920%3BmaxWidth%3D900?format=webp",
            current_price=4290.0,
            target_price=3790.0,
            user_email=settings.demo_admin_email,
            currency="ILS",
            is_active=True,
        ),
    ]


def main() -> None:
    create_db_and_tables()
    with Session(engine) as session:
        ensure_demo_users(session)
        existing = session.exec(select(TrackedProduct)).first()
        if existing is not None:
            print("Seed skipped: products already exist.")
            return

        session.add_all(build_seed_products())
        session.commit()
        print("Seeded demo users and tracked products.")


if __name__ == "__main__":
    main()
