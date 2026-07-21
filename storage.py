import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
SQLITE_PATH = BASE_DIR / "requests.db"
USE_POSTGRES = DATABASE_URL.startswith(("postgres://", "postgresql://"))


@contextmanager
def connection():
    if USE_POSTGRES:
        import psycopg
        from psycopg.rows import dict_row

        database = psycopg.connect(
            DATABASE_URL,
            connect_timeout=10,
            row_factory=dict_row,
        )
    else:
        database = sqlite3.connect(SQLITE_PATH, timeout=15)
        database.row_factory = sqlite3.Row

    try:
        yield database
    finally:
        database.close()


def sql(query: str) -> str:
    return query.replace("?", "%s") if USE_POSTGRES else query


def create_database() -> None:
    id_column = "BIGSERIAL PRIMARY KEY" if USE_POSTGRES else "INTEGER PRIMARY KEY AUTOINCREMENT"

    with connection() as database:
        database.execute(
            f"""
            CREATE TABLE IF NOT EXISTS site_requests
            (
                id         {id_column},
                name       TEXT NOT NULL,
                contact    TEXT NOT NULL,
                service    TEXT,
                budget     TEXT,
                message    TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        database.commit()


def save_request(name, contact, service, budget, message) -> None:
    with connection() as database:
        database.execute(
            sql(
                """
                INSERT INTO site_requests (
                    name,
                    contact,
                    service,
                    budget,
                    message,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """
            ),
            (
                name,
                contact,
                service,
                budget,
                message,
                datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            ),
        )
        database.commit()
