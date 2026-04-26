from __future__ import annotations

import httpx

from app.config import get_settings


def main() -> None:
    settings = get_settings()
    print("PriceRadar local demo")
    print("====================")
    print("1. Start the API stack with: docker compose up --build")
    print("2. Open Swagger at: http://127.0.0.1:8000/docs")
    print("3. Use the Typer interface:")
    print("   python -m app.cli list-products")
    print("   python -m app.cli add-product --name \"Steam Deck OLED\" --store \"Valve\" --product-url \"https://example.com/steam-deck\" --current-price 2699 --target-price 2499")
    print("   python -m app.cli summary")
    print("4. Protected enhancement:")
    print("   python -m app.cli weekly-digest")
    print("")
    try:
        with httpx.Client(base_url=settings.api_base_url, timeout=5.0) as client:
            health = client.get("/health")
            print(f"Live health check: {health.json()}")
            headers = {
                key: value
                for key, value in health.headers.items()
                if key.lower().startswith("x-ratelimit")
            }
            print(f"Rate-limit headers: {headers}")
    except Exception as exc:
        print(f"API not reachable yet: {exc}")


if __name__ == "__main__":
    main()
