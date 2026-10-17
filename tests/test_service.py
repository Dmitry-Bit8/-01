import pytest

from app import service
from app.models import Contact


@pytest.fixture(autouse=True)
def _db(tmp_path):
    service.set_db(str(tmp_path / "svc.db"))


def test_create_and_get():
    c = service.create(Contact(None, "Иван", "+7 900 123-45-67"))
    assert c.id == 1
    found = service.get(1)
    assert found is not None          
    assert found.name == "Иван"


def test_validation_empty_name():
    with pytest.raises(ValueError):
        service.create(Contact(None, "", "+7 900 123-45-67"))


def test_validation_bad_phone():
    with pytest.raises(ValueError):
        service.create(Contact(None, "Иван", "abc"))


def test_list_and_search():
    service.create(Contact(None, "Мария", "+7 900 111-11-11"))
    service.create(Contact(None, "Иван",  "+7 900 222-22-22"))
    assert len(service.list_contacts()) == 2
    assert len(service.list_contacts("Иван")) == 1


def test_update_and_delete():
    c = service.create(Contact(None, "Сергей", "+7 900 333-33-33"))
    c.name = "Сергей К."
    service.update(c)

    assert c.id is not None
    cid: int = c.id

    found = service.get(cid)
    assert found is not None
    assert found.name == "Сергей К."

    service.delete(cid)
    assert service.get(cid) is None
