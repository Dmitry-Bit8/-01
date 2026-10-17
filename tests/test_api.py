def test_root_redirects_to_docs(client):
    r = client.get("/")
    assert r.status_code in (301, 302, 308)
    assert r.headers["Location"].endswith("/docs")


def test_openapi_spec(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    assert r.json["openapi"].startswith("3.")
    assert "/api/contacts" in r.json["paths"]


def test_swagger_ui_served(client):
    r = client.get("/docs/")
    assert r.status_code == 200
    assert b"swagger" in r.data.lower()


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json["status"] == "ok"


def test_create_list_update_delete(client):
    r = client.post("/api/contacts", json={"name": "Мария", "phone": "+7 900 555-66-77"})
    assert r.status_code == 201
    cid = r.json["id"]

    assert any(c["id"] == cid for c in client.get("/api/contacts").json)

    r = client.put(f"/api/contacts/{cid}",
                   json={"name": "Мария", "phone": "+7 900 555-66-99"})
    assert r.status_code == 200 and r.json["phone"].endswith("66-99")

    assert client.delete(f"/api/contacts/{cid}").status_code == 204
    assert client.get(f"/api/contacts/{cid}").status_code == 404


def test_validation_error(client):
    r = client.post("/api/contacts", json={"name": "", "phone": "12"})
    assert r.status_code == 400
