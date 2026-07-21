import sqlite3
from contextlib import closing
from datetime import datetime

from config import DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH, timeout=15)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def create_db() -> None:
    with closing(get_connection()) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                place TEXT NOT NULL,
                hours INTEGER NOT NULL,
                booking_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_bookings_slot
            ON bookings(place, booking_date, start_time);

            CREATE INDEX IF NOT EXISTS idx_bookings_user
            ON bookings(user_id, booking_date);
            """
        )
        connection.commit()


def user_exists(telegram_id: int) -> bool:
    return get_user(telegram_id) is not None


def get_user(telegram_id: int):
    with closing(get_connection()) as connection:
        return connection.execute(
            "SELECT telegram_id, name, phone FROM users WHERE telegram_id = ?",
            (telegram_id,),
        ).fetchone()


def save_user(telegram_id: int, name: str, phone: str) -> None:
    with closing(get_connection()) as connection:
        connection.execute(
            """
            INSERT INTO users (telegram_id, name, phone)
            VALUES (?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                name = excluded.name,
                phone = excluded.phone
            """,
            (telegram_id, name, phone),
        )
        connection.commit()


def delete_user(telegram_id: int) -> None:
    with closing(get_connection()) as connection:
        connection.execute(
            "DELETE FROM users WHERE telegram_id = ?",
            (telegram_id,),
        )
        connection.commit()


def _minutes(value: str) -> int:
    parsed = datetime.strptime(value, "%H:%M")
    return parsed.hour * 60 + parsed.minute


def create_booking_if_available(
    user_id: int,
    name: str,
    place: str,
    hours: int,
    booking_date: str,
    start_time: str,
):
    requested_start = _minutes(start_time)
    requested_end = requested_start + hours * 60

    with closing(get_connection()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        rows = connection.execute(
            """
            SELECT start_time, hours
            FROM bookings
            WHERE place = ? AND booking_date = ?
            """,
            (place, booking_date),
        ).fetchall()

        for row in rows:
            existing_start = _minutes(row["start_time"])
            existing_end = existing_start + int(row["hours"]) * 60
            if requested_start < existing_end and existing_start < requested_end:
                connection.rollback()
                return None

        cursor = connection.execute(
            """
            INSERT INTO bookings
                (user_id, name, place, hours, booking_date, start_time)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, name, place, hours, booking_date, start_time),
        )
        connection.commit()
        return int(cursor.lastrowid)


def get_user_bookings(user_id: int, limit: int = 5):
    with closing(get_connection()) as connection:
        return connection.execute(
            """
            SELECT id, place, hours, booking_date, start_time
            FROM bookings
            WHERE user_id = ?
            ORDER BY booking_date ASC, start_time ASC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()


def get_all_bookings(limit: int = 50):
    with closing(get_connection()) as connection:
        return connection.execute(
            """
            SELECT id, user_id, name, place, hours, booking_date, start_time
            FROM bookings
            ORDER BY booking_date ASC, start_time ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()


def delete_booking(booking_id: int) -> bool:
    with closing(get_connection()) as connection:
        cursor = connection.execute(
            "DELETE FROM bookings WHERE id = ?",
            (booking_id,),
        )
        connection.commit()
        return cursor.rowcount > 0
