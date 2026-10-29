"""robots.txt-Prüfung und Drosselung (max. 1 Anfrage pro Sekunde je Domain)."""
from __future__ import annotations

import asyncio
import time
from urllib.parse import urlparse

from protego import Protego

UA_TOKEN = "intersignum-netzentgelte"
USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/130.0 Safari/537.36 (compatible; intersignum-netzentgelte/1.0; +https://intersignum.de)")
TIMEOUT_MS = 30_000


def host(url: str) -> str:
    return urlparse(url).netloc.lower()


def basis_domain(url_oder_host: str) -> str:
    h = host(url_oder_host) if "://" in url_oder_host else url_oder_host.lower()
    h = h.split(":")[0].removeprefix("www.")
    teile = h.split(".")
    return ".".join(teile[-2:]) if len(teile) >= 2 else h


class Drossel:
    """Mindestabstand zwischen zwei Anfragen an denselben Host, über alle Worker hinweg."""

    def __init__(self, abstand: float = 1.0):
        self.abstand = abstand
        self._letzte: dict[str, float] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self.anfragen: dict[str, int] = {}

    async def warten(self, url: str):
        h = host(url)
        lock = self._locks.setdefault(h, asyncio.Lock())
        async with lock:
            jetzt = time.monotonic()
            frei = self._letzte.get(h, 0) + self.abstand
            if frei > jetzt:
                await asyncio.sleep(frei - jetzt)
            self._letzte[h] = time.monotonic()
            self.anfragen[h] = self.anfragen.get(h, 0) + 1


class Robots:
    """Lädt robots.txt je Host einmal und beantwortet can_fetch."""

    def __init__(self, request_context, drossel: Drossel):
        self.req = request_context
        self.drossel = drossel
        self._cache: dict[str, Protego | None | str] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    async def _laden(self, url: str):
        p = urlparse(url)
        key = f"{p.scheme}://{p.netloc}"
        lock = self._locks.setdefault(key, asyncio.Lock())
        async with lock:
            if key in self._cache:
                return self._cache[key]
            await self.drossel.warten(key)
            regel = None
            try:
                r = await self.req.get(key + "/robots.txt", timeout=TIMEOUT_MS, max_redirects=5,
                                       headers={"User-Agent": USER_AGENT})
                if r.status == 200:
                    txt = (await r.body()).decode("utf-8", "replace")
                    # HTML-Fehlerseiten mit Status 200 nicht als robots.txt deuten
                    regel = None if "<html" in txt[:500].lower() else Protego.parse(txt)
                elif r.status in (401, 403):
                    regel = "alles_gesperrt"
                elif r.status >= 500:
                    regel = "nicht_erreichbar"
                # 404 usw.: keine Einschränkungen
            except Exception:
                regel = "nicht_erreichbar"
            self._cache[key] = regel
            return regel

    async def erlaubt(self, url: str) -> bool | None:
        """True/False; None wenn robots.txt nicht erreichbar war (Server down)."""
        regel = await self._laden(url)
        if regel is None:
            return True
        if regel == "alles_gesperrt":
            return False
        if regel == "nicht_erreichbar":
            return None
        return regel.can_fetch(url, UA_TOKEN)

    async def sitemaps(self, url: str) -> list[str]:
        regel = await self._laden(url)
        if isinstance(regel, Protego):
            return list(regel.sitemaps)[:3]
        return []
