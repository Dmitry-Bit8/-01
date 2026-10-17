"""Бизнес-логика справочника (валидация + CRUD)."""
import re
from dataclasses import asdict
from typing import List, Optional

from .database import connection, init_db
from .models import Contact

_db_path: Optional[str] = None
PHONE_RE = re.compile(r"^\+?[0-9\s\-()]{6,20}$")


def set_db(path: str) -> None:
    global _db_path
    _db_path = path
    init_db(path)


def _path() -> str:
    if not _db_path:
        raise RuntimeError("service.set_db() не вызван")
    return _db_path


def _validate(c: Contact) -> None:
    if not c.name.strip():
        raise ValueError("Имя обязательно")
    if not PHONE_RE.match(c.phone.strip()):
        raise ValueError("Некорректный номер телефона")


def list_contacts(q: str = "") -> List[Contact]:
    sql = "SELECT * FROM contacts"
    args: tuple = ()
    if q:
        sql += " WHERE name LIKE ? OR phone LIKE ?"
        args = (f"%{q}%", f"%{q}%")
    sql += " ORDER BY id"
    with connection(_path()) as conn:
        rows = conn.execute(sql, args).fetchall()
    return [Contact(r["id"], r["name"], r["phone"], r["email"], r["note"]) for r in rows]


def get(cid: int) -> Optional[Contact]:
    with connection(_path()) as conn:
        r = conn.execute("SELECT * FROM contacts WHERE id=?", (cid,)).fetchone()
    return Contact(r["id"], r["name"], r["phone"], r["email"], r["note"]) if r else None


def create(c: Contact) -> Contact:
    _validate(c)
    with connection(_path()) as conn:
        cur = conn.execute(
            "INSERT INTO contacts(name, phone, email, note) VALUES (?,?,?,?)",
            (c.name.strip(), c.phone.strip(), c.email, c.note),
        )
        c.id = cur.lastrowid
    return c


def update(c: Contact) -> Contact:
    _validate(c)
    with connection(_path()) as conn:
        conn.execute(
            "UPDATE contacts SET name=?, phone=?, email=?, note=? WHERE id=?",
            (c.name.strip(), c.phone.strip(), c.email, c.note, c.id),
        )
    return c


def delete(cid: int) -> None:
    with connection(_path()) as conn:
        conn.execute("DELETE FROM contacts WHERE id=?", (cid,))
