"""HTTP-клиент для GUI (и для RequestSystem)."""
from typing import List, Optional
import requests

from .models import Contact


class PhoneBookClient:
    def __init__(self, base_url: str, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def health(self) -> bool:
        r = requests.get(f"{self.base_url}/api/health", timeout=self.timeout)
        return r.ok and r.json().get("status") == "ok"

    def list(self, q: str = "") -> List[Contact]:
        r = requests.get(f"{self.base_url}/api/contacts",
                         params={"q": q} if q else None, timeout=self.timeout)
        r.raise_for_status()
        return [Contact(**c) for c in r.json()]

    def create(self, c: Contact) -> Contact:
        r = requests.post(f"{self.base_url}/api/contacts", json=c.__dict__, timeout=self.timeout)
        r.raise_for_status()
        return Contact(**r.json())

    def update(self, c: Contact) -> Contact:
        r = requests.put(f"{self.base_url}/api/contacts/{c.id}", json=c.__dict__,
                         timeout=self.timeout)
        r.raise_for_status()
        return Contact(**r.json())

    def delete(self, cid: int) -> None:
        r = requests.delete(f"{self.base_url}/api/contacts/{cid}", timeout=self.timeout)
        r.raise_for_status()

    def get(self, cid: int) -> Optional[Contact]:
        r = requests.get(f"{self.base_url}/api/contacts/{cid}", timeout=self.timeout)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return Contact(**r.json())
