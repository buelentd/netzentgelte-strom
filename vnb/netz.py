"""robots.txt-Prüfung und Drosselung (max. 1 Anfrage pro Sekunde je Domain)."""
from __future__ import annotations

import asyncio
import re
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

    def __init__(self, request_context, drossel: Drossel, log=None):
        self.req = request_context
        self.drossel = drossel
        self.log = log
        self._cache: dict[str, Protego | None | str] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._texte: dict[str, str] = {}
        self._gemeldet: set[str] = set()

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
                    if "<html" not in txt[:500].lower():
                        regel = Protego.parse(txt)
                        self._texte[key] = txt
                elif r.status >= 500:
                    regel = "nicht_erreichbar"
                # 4xx (auch 401/403): robots.txt "nicht verfügbar", keine Einschränkungen (RFC 9309, 2.3.1.3);
                # sperrt der Server die Seiten selbst, wird das beim Abruf als "blockiert" erkannt
            except Exception:
                regel = "nicht_erreichbar"
            self._cache[key] = regel
            return regel

    async def erlaubt(self, url: str) -> bool | None:
        """True/False; None wenn robots.txt nicht erreichbar war (Server down)."""
        regel = await self._laden(url)
        if regel is None:
            return True
        if regel == "nicht_erreichbar":
            return None
        ok = regel.can_fetch(url, UA_TOKEN)
        if not ok and self.log:
            key = "{0.scheme}://{0.netloc}".format(urlparse(url))
            if key not in self._gemeldet:
                self._gemeldet.add(key)
                self.log(f"    robots.txt von {key} sperrt {url[:120]} ({sperrregel(self._texte.get(key, ''), url)})")
        return ok

    async def sitemaps(self, url: str) -> list[str]:
        regel = await self._laden(url)
        if isinstance(regel, Protego):
            return list(regel.sitemaps)[:3]
        return []


def sperrregel(txt: str, url: str) -> str:
    """Die Disallow-Zeile(n), die den Pfad treffen (nur für das Protokoll)."""
    p = urlparse(url)
    pfad = (p.path or "/") + ("?" + p.query if p.query else "")
    treffer = []
    for zeile in txt.splitlines():
        k, _, v = zeile.partition(":")
        v = v.split("#")[0].strip()
        if k.strip().lower() == "disallow" and v:
            muster = "^" + ".*".join(map(re.escape, v.rstrip("$").split("*")))
            if re.match(muster, pfad):
                treffer.append("Disallow: " + v)
    return ", ".join(dict.fromkeys(treffer)) or "Regel nicht einzeln bestimmbar"
