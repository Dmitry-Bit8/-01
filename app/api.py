"""Flask REST API + Swagger UI.

Запуск:
    python -m app.api            # порт 0 → свободный автоматически
    PORT=8001 python -m app.api  # задать явно
"""
import os
import socket
from dataclasses import asdict

from flask import Flask, request, jsonify, redirect
from flask_swagger_ui import get_swaggerui_blueprint

from . import service
from .config import DATABASE_PATH
from .database import init_db
from .models import Contact
from .openapi import OPENAPI_SPEC

SWAGGER_URL = "/docs"
OPENAPI_URL = "/openapi.json"


def create_app(db_path: str | None = None) -> Flask:
    app = Flask(__name__)
    db = db_path or str(DATABASE_PATH)
    service.set_db(db)
    init_db(db)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", db=service._path())

    @app.get("/api/contacts")
    def list_all():
        q = request.args.get("q", "")
        return jsonify([asdict(c) for c in service.list_contacts(q)])

    @app.get("/api/contacts/<int:cid>")
    def get_one(cid):
        c = service.get(cid)
        return (jsonify(asdict(c)), 200) if c else (jsonify(error="not found"), 404)

    @app.post("/api/contacts")
    def create_one():
        d = request.get_json(force=True) or {}
        try:
            c = service.create(Contact(None, d.get("name", ""), d.get("phone", ""),
                                       d.get("email", ""), d.get("note", "")))
            return jsonify(asdict(c)), 201
        except ValueError as e:
            return jsonify(error=str(e)), 400

    @app.put("/api/contacts/<int:cid>")
    def update_one(cid):
        d = request.get_json(force=True) or {}
        try:
            c = service.update(Contact(cid, d.get("name", ""), d.get("phone", ""),
                                       d.get("email", ""), d.get("note", "")))
            return jsonify(asdict(c))
        except ValueError as e:
            return jsonify(error=str(e)), 400

    @app.delete("/api/contacts/<int:cid>")
    def delete_one(cid):
        service.delete(cid)
        return "", 204

    @app.get(OPENAPI_URL)
    def spec():
        return jsonify(OPENAPI_SPEC)

    app.register_blueprint(
        get_swaggerui_blueprint(SWAGGER_URL, OPENAPI_URL, config={"app_name": "PhoneBook API"}),
        url_prefix=SWAGGER_URL,
    )

    @app.get("/")
    def root():
        return redirect(SWAGGER_URL)

    return app


def find_free_port() -> int:
    """Спросить у ОС свободный TCP-порт."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def run(port: int | None = None) -> None:
    port = port or int(os.environ.get("PORT", 0)) or find_free_port()
    app = create_app()
    url = f"http://localhost:{port}"
    print("=" * 60)
    print(f"  PhoneBook API запущен")
    print(f"  Swagger UI : {url}/docs/")
    print(f"  OpenAPI    : {url}/openapi.json")
    print(f"  API        : {url}/api/contacts")
    print("=" * 60)
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    run()
