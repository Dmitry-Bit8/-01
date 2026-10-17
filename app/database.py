"""Схема БД SQLite + подключение."""
import sqlite3
from contextlib import contextmanager
from typing import Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS contacts (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT DEFAULT '',
    note  TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_contacts_name  ON contacts(name);
CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone);
"""


def init_db(path: str) -> None:
    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()


@contextmanager
def connection(path: str) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
