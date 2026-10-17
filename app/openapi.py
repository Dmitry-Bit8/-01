"""OpenAPI 3.0 спецификация — отдаётся по /openapi.json."""
CONTACT_SCHEMA = {
    "type": "object",
    "properties": {
        "id":    {"type": "integer", "readOnly": True, "example": 1},
        "name":  {"type": "string",  "example": "Иван Петров"},
        "phone": {"type": "string",  "example": "+7 900 123-45-67"},
        "email": {"type": "string",  "example": "ivan@example.com"},
        "note":  {"type": "string",  "example": "друг"},
    },
    "required": ["name", "phone"],
}

ERROR_SCHEMA = {
    "type": "object",
    "properties": {"error": {"type": "string", "example": "Некорректный номер телефона"}},
}

_CONTACT_REF = {"$ref": "#/components/schemas/Contact"}
_ERROR_REF   = {"$ref": "#/components/schemas/Error"}
_INPUT_REF   = {"$ref": "#/components/schemas/ContactInput"}

OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "PhoneBook API",
        "description": "Справочник контактов — интеграция с RequestSystem и GUI.",
        "version": "1.0.0",
    },
    "servers": [{"url": "/", "description": "текущий хост"}],
    "tags": [{"name": "contacts", "description": "Работа с контактами"}],
    "paths": {
        "/api/health": {
            "get": {
                "tags": ["contacts"], "summary": "Health-check",
                "responses": {"200": {"description": "OK"}},
            }
        },
        "/api/contacts": {
            "get": {
                "tags": ["contacts"], "summary": "Список контактов с поиском",
                "parameters": [{
                    "name": "q", "in": "query", "required": False,
                    "schema": {"type": "string"}, "description": "Поиск по имени/телефону",
                }],
                "responses": {"200": {
                    "description": "Массив контактов",
                    "content": {"application/json": {"schema": {"type": "array", "items": _CONTACT_REF}}},
                }},
            },
            "post": {
                "tags": ["contacts"], "summary": "Создать контакт",
                "requestBody": {"required": True, "content": {"application/json": {"schema": _INPUT_REF}}},
                "responses": {
                    "201": {"description": "Создан", "content": {"application/json": {"schema": _CONTACT_REF}}},
                    "400": {"description": "Ошибка валидации", "content": {"application/json": {"schema": _ERROR_REF}}},
                },
            },
        },
        "/api/contacts/{id}": {
            "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer", "example": 1}}],
            "get": {
                "tags": ["contacts"], "summary": "Получить контакт",
                "responses": {
                    "200": {"description": "OK", "content": {"application/json": {"schema": _CONTACT_REF}}},
                    "404": {"description": "Не найден"},
                },
            },
            "put": {
                "tags": ["contacts"], "summary": "Обновить контакт",
                "requestBody": {"required": True, "content": {"application/json": {"schema": _INPUT_REF}}},
                "responses": {
                    "200": {"description": "Обновлён", "content": {"application/json": {"schema": _CONTACT_REF}}},
                    "400": {"description": "Ошибка валидации"},
                },
            },
            "delete": {
                "tags": ["contacts"], "summary": "Удалить контакт",
                "responses": {"204": {"description": "Удалён"}},
            },
        },
    },
    "components": {
        "schemas": {
            "Contact": CONTACT_SCHEMA,
            "ContactInput": {
                "type": "object",
                "properties": {k: v for k, v in CONTACT_SCHEMA["properties"].items() if k != "id"},
                "required": ["name", "phone"],
            },
            "Error": ERROR_SCHEMA,
        }
    },
}
