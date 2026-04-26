from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlmodel import Session, create_engine

from app.config import get_database_url
from app.migrations import apply_migrations

DATABASE_URL = get_database_url()

if DATABASE_URL.startswith("sqlite:///./"):
    sqlite_relative_path = DATABASE_URL.removeprefix("sqlite:///./")
    Path(sqlite_relative_path).parent.mkdir(parents=True, exist_ok=True)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


def create_db_and_tables() -> list[str]:
    return apply_migrations(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
