import pytest

from app.api import create_app
from app import service


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test.db")


@pytest.fixture
def app(db_path):
    app = create_app(db_path)
    app.testing = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()
