"""End-to-End-Test des Crawlers gegen eine lokale Test-Website (kein Internet nötig)."""
import asyncio
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from tests.fixtures import KOPF_STANDARD, pdf

ANFRAGEN = []

SEITEN = {
    "robots.txt": "User-agent: *\nDisallow: /intern/\n",
    "index.html": """<html><head><title>Musternetz</title></head><body>
        <a href="/karriere/">Karriere</a> <a href="/gas/">Gasnetz</a>
        <a href="/netz/">Netz &amp; Marktpartner</a></body></html>""",
    "gas/index.html": '<a href="/dl/gas_preisblatt_2026.pdf">Preisblatt Gas 2026</a>',
    "karriere/index.html": "Jobs",
    "netz/index.html": '<a href="/netz/netzentgelte/">Netzentgelte Strom</a>',
    "netz/netzentgelte/index.html": """<html><body><ul>
        <li><a href="/dl/preisblatt_strom_2026_vorlaeufig.pdf">Preisblatt Strom 2026 (vorläufig)</a></li>
        <li><a href="/dl/preisblatt_strom_2027_vorlaeufig.pdf">Preisblatt Strom 2027 (vorläufig)</a></li>
        <li><a href="/intern/preisblatt_strom_2026_final.pdf">Preisblatt Strom 2026 final (intern)</a></li>
        <li><a href="/dl/Preise_Standardlastprofil-Kunden_2026_endgueltig.pdf">Standardlastprofil-Kunden 2026</a></li>
        <li id="spaeter"></li></ul>
        <script>setTimeout(() => { document.getElementById('spaeter').innerHTML =
          '<evd-link link="/dl/NNE_Strom_2026_endgueltig.pdf">Preisblatt Netzentgelte Strom 2026 endgültig</evd-link>';
        }, 300);</script></body></html>""",
}


def _site(root: Path):
    for name, inhalt in SEITEN.items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(inhalt, encoding="utf-8")
    (root / "dl").mkdir(exist_ok=True)
    (root / "intern").mkdir(exist_ok=True)
    zeile_ns = "Niederspannung                {}            {}                 {}           {}"
    endg = KOPF_STANDARD + [zeile_ns.format("18,64", "7,49", "171,87", "1,36")]
    vorl = [z.replace("(endgültig)", "(vorläufig)") for z in KOPF_STANDARD] + [
        zeile_ns.format("19,00", "7,60", "175,00", "1,40")]
    pdf(root / "dl" / "NNE_Strom_2026_endgueltig.pdf", endg)
    pdf(root / "dl" / "preisblatt_strom_2026_vorlaeufig.pdf", vorl)
    pdf(root / "dl" / "preisblatt_strom_2027_vorlaeufig.pdf", [z.replace("2026", "2027") for z in vorl])
    pdf(root / "intern" / "preisblatt_strom_2026_final.pdf", endg)
    pdf(root / "dl" / "gas_preisblatt_2026.pdf", ["Gas"])
    pdf(root / "dl" / "Preise_Standardlastprofil-Kunden_2026_endgueltig.pdf", [
        "Musternetz GmbH - Preise für Standardlastprofilkunden, gültig ab 01.01.2026, endgültig",
        "Entnahme ohne Leistungsmessung (Standardlastprofil)",
        "Netzebene                 Grundpreis       Arbeitspreis",
        "                          €/a              ct/kWh",
        "Niederspannung            54,00            7,95",
        "Steuerbare Verbrauchseinrichtungen nach § 14a EnWG",
        "Modul 2                                    3,18",
    ] + ["Fußnote: Alle Preise netto zuzüglich Umsatzsteuer."] * 5)


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        ANFRAGEN.append((time.monotonic(), self.path))


@pytest.fixture(scope="module")
def server(tmp_path_factory):
    root = tmp_path_factory.mktemp("site")
    _site(root)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(root)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()


async def _lauf(url, cache, **kw):
    from playwright.async_api import async_playwright

    from vnb.crawl import Auftrag, Crawler
    from vnb.netz import Drossel, Robots
    async with async_playwright() as pw:
        try:
            browser = await pw.chromium.launch()
        except Exception:
            browser = await pw.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        req = await pw.request.new_context()
        drossel = Drossel(1.0)
        c = Crawler(browser, Robots(req, drossel), drossel, cache, 2026, log=lambda *a: None)
        fund = await c.bearbeiten(Auftrag(key="t", nr=1, name="Musternetz GmbH", mastr_nr="", website=url, **kw))
        await req.dispose()
        await browser.close()
        return fund


def test_crawler_findet_endgueltiges_preisblatt(server, tmp_path):
    ANFRAGEN.clear()
    fund = asyncio.run(_lauf(server, tmp_path))
    assert fund.status == "ok", fund.grund
    k = fund.kandidat
    assert k.url.endswith("NNE_Strom_2026_endgueltig.pdf")      # per JavaScript nachgeladener Link
    assert k.preisstand == "endgültig"
    assert k.ns["lp_ueber_2500"] == pytest.approx(171.87)
    s = fund.slp_kandidat                                          # SLP aus separatem Preisblatt
    assert s.url.endswith("Standardlastprofil-Kunden_2026_endgueltig.pdf")
    assert s.slp == {"ap": 7.95, "gp": 54.0}
    pfade = [p for _, p in ANFRAGEN]
    assert not any(p.startswith("/intern/") for p in pfade)       # robots.txt beachtet
    assert not any("gas" in p for p in pfade)                     # Gas ausgeschlossen
    assert not any("karriere" in p for p in pfade)
    # höchstens 1 Anfrage pro Sekunde (Seiten, Dokumente, robots.txt)
    zeiten = [t for t, p in ANFRAGEN if not p.startswith("/favicon")]
    abstaende = [b - a for a, b in zip(zeiten, zeiten[1:])]
    assert min(abstaende) >= 0.95, abstaende


def test_crawler_robots_komplett_gesperrt(tmp_path):
    root = tmp_path / "site"
    root.mkdir()
    (root / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(root)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        fund = asyncio.run(_lauf(f"http://127.0.0.1:{httpd.server_address[1]}", tmp_path / "c"))
    finally:
        httpd.shutdown()
    assert fund.status == "robots"


def test_crawler_nicht_erreichbar(tmp_path):
    fund = asyncio.run(_lauf("http://127.0.0.1:9", tmp_path))
    assert fund.status == "blockiert"


def test_cache_liefert_dokument_nicht_url_datei(tmp_path):
    """Zweiter Abruf derselben URL muss das PDF aus dem Cache liefern, nicht <hash>.url."""
    import hashlib

    from vnb.crawl import Auftrag, Crawler
    url = "https://x.de/preisblatt.pdf"
    h = hashlib.sha1(url.encode()).hexdigest()[:12]
    ordner = tmp_path / "k"
    ordner.mkdir()
    (ordner / f"{h}.url").write_text(url)
    (ordner / f"{h}.pdf").write_bytes(b"%PDF-1.4")
    c = Crawler(None, None, None, tmp_path, 2026)
    pfad, fehler = asyncio.run(c.herunterladen(None, url, Auftrag(key="k", nr=1, name="X", mastr_nr="", website="")))
    assert pfad.suffix == ".pdf" and not fehler
