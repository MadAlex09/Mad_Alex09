import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

from config import DATABASE_PATH
from translations import DEFAULT_LANGUAGE, normalize_language

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
USE_POSTGRES = DATABASE_URL.startswith(("postgres://", "postgresql://"))


@contextmanager
def connection():
    if USE_POSTGRES:
        import psycopg
        from psycopg.rows import dict_row
        database = psycopg.connect(DATABASE_URL, connect_timeout=10, row_factory=dict_row)
    else:
        database = sqlite3.connect(DATABASE_PATH, timeout=15)
        database.row_factory = sqlite3.Row
        database.execute("PRAGMA foreign_keys = ON")
        database.execute("PRAGMA journal_mode = WAL")
    try:
        yield database
    finally:
        database.close()


def sql(query: str) -> str:
    return query.replace("?", "%s") if USE_POSTGRES else query


def create_db() -> None:
    booking_id = "BIGSERIAL PRIMARY KEY" if USE_POSTGRES else "INTEGER PRIMARY KEY AUTOINCREMENT"
    statements = (
        """
        CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS user_languages (
            telegram_id BIGINT PRIMARY KEY,
            language TEXT NOT NULL DEFAULT 'en',
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS bookings (
            id {booking_id}, user_id BIGINT NOT NULL, name TEXT NOT NULL,
            place TEXT NOT NULL, hours INTEGER NOT NULL, booking_date TEXT NOT NULL,
            start_time TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
        "CREATE INDEX IF NOT EXISTS idx_bookings_slot ON bookings(place, booking_date, start_time)",
        "CREATE INDEX IF NOT EXISTS idx_bookings_user ON bookings(user_id, booking_date)",
    )
    with connection() as database:
        for statement in statements:
            database.execute(statement)
        database.commit()


def user_exists(telegram_id: int) -> bool:
    return get_user(telegram_id) is not None


def get_user(telegram_id: int):
    with connection() as database:
        return database.execute(sql("SELECT telegram_id, name, phone FROM users WHERE telegram_id = ?"), (telegram_id,)).fetchone()


def save_user(telegram_id: int, name: str, phone: str) -> None:
    with connection() as database:
        database.execute(sql("""
            INSERT INTO users (telegram_id, name, phone) VALUES (?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET name = excluded.name, phone = excluded.phone
        """), (telegram_id, name, phone))
        database.commit()


def delete_user(telegram_id: int) -> None:
    with connection() as database:
        database.execute(sql("DELETE FROM users WHERE telegram_id = ?"), (telegram_id,))
        database.execute(sql("DELETE FROM user_languages WHERE telegram_id = ?"), (telegram_id,))
        database.commit()


def get_user_language(telegram_id: int) -> str:
    with connection() as database:
        row = database.execute(sql("SELECT language FROM user_languages WHERE telegram_id = ?"), (telegram_id,)).fetchone()
    return normalize_language(row["language"] if row else DEFAULT_LANGUAGE)


def has_language_choice(telegram_id: int) -> bool:
    with connection() as database:
        row = database.execute(sql("SELECT 1 FROM user_languages WHERE telegram_id = ?"), (telegram_id,)).fetchone()
    return row is not None


def set_user_language(telegram_id: int, language: str) -> None:
    language = normalize_language(language)
    with connection() as database:
        database.execute(sql("""
            INSERT INTO user_languages (telegram_id, language, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(telegram_id) DO UPDATE SET
                language = excluded.language,
                updated_at = CURRENT_TIMESTAMP
        """), (telegram_id, language))
        database.commit()


def _minutes(value: str) -> int:
    parsed = datetime.strptime(value, "%H:%M")
    return parsed.hour * 60 + parsed.minute


def create_booking_if_available(user_id, name, place, hours, booking_date, start_time):
    requested_start = _minutes(start_time)
    requested_end = requested_start + hours * 60
    with connection() as database:
        if USE_POSTGRES:
            database.execute(sql("SELECT pg_advisory_xact_lock(hashtext(?)::bigint)"), (f"{place}|{booking_date}",))
        else:
            database.execute("BEGIN IMMEDIATE")
        rows = database.execute(sql("SELECT start_time, hours FROM bookings WHERE place = ? AND booking_date = ?"), (place, booking_date)).fetchall()
        for row in rows:
            existing_start = _minutes(row["start_time"])
            existing_end = existing_start + int(row["hours"]) * 60
            if requested_start < existing_end and existing_start < requested_end:
                database.rollback()
                return None
        if USE_POSTGRES:
            cursor = database.execute(sql("""
                INSERT INTO bookings (user_id, name, place, hours, booking_date, start_time)
                VALUES (?, ?, ?, ?, ?, ?) RETURNING id
            """), (user_id, name, place, hours, booking_date, start_time))
            booking_id = int(cursor.fetchone()["id"])
        else:
            cursor = database.execute("""
                INSERT INTO bookings (user_id, name, place, hours, booking_date, start_time)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, name, place, hours, booking_date, start_time))
            booking_id = int(cursor.lastrowid)
        database.commit()
        return booking_id


def get_user_bookings(user_id: int, limit: int = 5):
    with connection() as database:
        return database.execute(sql("""
            SELECT id, place, hours, booking_date, start_time FROM bookings
            WHERE user_id = ? ORDER BY booking_date ASC, start_time ASC LIMIT ?
        """), (user_id, limit)).fetchall()


def get_all_bookings(limit: int = 50):
    with connection() as database:
        return database.execute(sql("""
            SELECT id, user_id, name, place, hours, booking_date, start_time FROM bookings
            ORDER BY booking_date ASC, start_time ASC LIMIT ?
        """), (limit,)).fetchall()


def delete_booking(booking_id: int) -> bool:
    with connection() as database:
        cursor = database.execute(sql("DELETE FROM bookings WHERE id = ?"), (booking_id,))
        database.commit()
        return cursor.rowcount > 0
