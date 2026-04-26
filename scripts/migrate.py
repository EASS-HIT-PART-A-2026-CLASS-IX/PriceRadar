from __future__ import annotations

from app.database import create_db_and_tables


def main() -> None:
    applied = create_db_and_tables()
    if applied:
        print(f"Applied migrations: {', '.join(applied)}")
    else:
        print("No pending migrations.")


if __name__ == "__main__":
    main()
