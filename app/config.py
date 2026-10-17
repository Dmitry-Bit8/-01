"""Конфигурация модуля: путь к НОВОЙ изолированной базе."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "phonebook_api.db"

DEFAULT_PORT = 0
