from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine

from app.bootstrap import ensure_demo_users
from app.database import get_session
from app.main import app
from app.migrations import apply_migrations


@pytest.fixture
def test_engine(tmp_path):
    database_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )
    apply_migrations(engine)
    with Session(engine) as session:
        ensure_demo_users(session)
    return engine


@pytest.fixture
def client(test_engine) -> Generator[TestClient, None, None]:
    def override_get_session() -> Generator[Session, None, None]:
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
