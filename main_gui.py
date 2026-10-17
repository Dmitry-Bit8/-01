"""Запуск API на свободном порту + старт GUI."""
import threading
import time

from app.api import create_app, find_free_port
from app.client import PhoneBookClient


def start_api(port: int) -> threading.Thread:
    app = create_app()
    t = threading.Thread(
        target=lambda: app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False),
        daemon=True,
    )
    t.start()
    return t


def wait_api(url: str, tries: int = 30) -> None:
    client = PhoneBookClient(url)
    for _ in range(tries):
        try:
            if client.health():
                return
        except Exception:
            pass
        time.sleep(0.2)
    raise RuntimeError(f"API не поднялся на {url}")


def main() -> None:
    port = find_free_port()
    start_api(port)
    url = f"http://127.0.0.1:{port}"
    wait_api(url)
    print(f"API: {url}")
    print(f"Swagger UI: {url}/docs/")

    from gui.gui import PhoneBookGUI
    PhoneBookGUI(url).mainloop()


if __name__ == "__main__":
    main()
