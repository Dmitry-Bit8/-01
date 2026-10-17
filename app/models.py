"""Dataclass-модель контакта."""
from dataclasses import dataclass


@dataclass
class Contact:
    id: int | None
    name: str
    phone: str
    email: str = ""
    note: str = ""
