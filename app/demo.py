from __future__ import annotations

import httpx

from app.config import get_settings


def main() -> None:
    settings = get_settings()
    print("PriceRadar local demo")
    print("====================")
    print("1. Install dependencies: uv sync")
    print("2. Prepare local data:")
    print("   uv run python -m scripts.migrate")
    print("   uv run python scripts/seed_products.py")
    print("3. Start the API locally:")
    print("   uv run python -m uvicorn app.main:app --reload")
    print("   Or start the EX3 stack with: docker compose up --build")
    print("4. Open Swagger at: http://127.0.0.1:8000/docs")
    print("5. Open the browser dashboard at: http://127.0.0.1:8000/app")
    print("6. Paste a supported product URL:")
    print("   https://demo.ksp.local/products/sony-wh1000xm5")
    print("   https://demo.ivory.local/products/steam-deck-oled")
    print("   https://demo.bug.local/products/pixel-8-pro")
    print("7. Use the Typer interface:")
    print("   uv run python -m app.cli list-products")
    print("   uv run python -m app.cli preview-url --product-url \"https://demo.ksp.local/products/sony-wh1000xm5\"")
    print("   uv run python -m app.cli track-url --product-url \"https://demo.ksp.local/products/sony-wh1000xm5\" --target-price 999")
    print("   uv run python -m app.cli summary")
    print("8. Refresh worker and protected enhancement:")
    print("   uv run python -m scripts.refresh")
    print("   uv run python -m app.cli weekly-digest")
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
