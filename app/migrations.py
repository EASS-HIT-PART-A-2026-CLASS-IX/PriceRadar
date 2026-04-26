from __future__ import annotations

from pathlib import Path

from sqlalchemy.engine import Engine


def get_migrations_dir() -> Path:
    candidates = [
        Path.cwd() / "migrations",
        Path(__file__).resolve().parents[1] / "migrations",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def iter_sql_statements(sql: str) -> list[str]:
    return [statement.strip() for statement in sql.split(";") if statement.strip()]


def apply_migrations(engine: Engine) -> list[str]:
    migrations_dir = get_migrations_dir()
    migrations_dir.mkdir(parents=True, exist_ok=True)
    applied_files: list[str] = []
    with engine.begin() as connection:
        connection.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        rows = connection.exec_driver_sql("SELECT version FROM schema_migrations").fetchall()
        applied = {row[0] for row in rows}
        for path in sorted(migrations_dir.glob("*.sql")):
            if path.name in applied:
                continue
            sql = path.read_text(encoding="utf-8").strip()
            if sql:
                for statement in iter_sql_statements(sql):
                    connection.exec_driver_sql(statement)
            connection.exec_driver_sql(
                "INSERT INTO schema_migrations(version) VALUES (:version)",
                {"version": path.name},
            )
            applied_files.append(path.name)
    return applied_files
