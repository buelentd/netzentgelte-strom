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
    # gemessen wird die Ankunft am Testserver; einzelne Anfragen kommen auf CI-Rechnern bis ~0,15 s
    # verspätet an (1,12 s, dann 0,88 s). Je zwei Abstände zusammen müssen daher ≥ 1,95 s sein.
    assert min(abstaende) >= 0.7, abstaende
    assert all(a + b >= 1.95 for a, b in zip(abstaende, abstaende[1:])), abstaende


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


class _Antwort:
    def __init__(self, status, text=""):
        self.status, self._text = status, text

    async def body(self):
        return self._text.encode()


class _Req:
    def __init__(self, antwort):
        self.antwort = antwort

    async def get(self, url, **kw):
        return self.antwort


@pytest.mark.parametrize("status,erwartet", [(403, True), (401, True), (404, True), (503, None)])
def test_robots_statuscodes_nach_rfc9309(status, erwartet):
    # 4xx: robots.txt "nicht verfügbar" -> keine Einschränkung; 5xx: "nicht erreichbar"
    from vnb.netz import Drossel, Robots
    r = Robots(_Req(_Antwort(status)), Drossel(0))
    assert asyncio.run(r.erlaubt("https://netz.example/preisblatt.pdf")) is erwartet


def test_robots_sperre_wird_mit_regel_protokolliert():
    from vnb.netz import Drossel, Robots, sperrregel
    meldungen = []
    txt = "User-agent: *\nDisallow: /content/dam/\nDisallow: /*.pdf$\n"
    r = Robots(_Req(_Antwort(200, txt)), Drossel(0), log=meldungen.append)
    assert asyncio.run(r.erlaubt("https://netz.example/content/dam/a.pdf")) is False
    assert asyncio.run(r.erlaubt("https://netz.example/seite.html")) is True
    assert len(meldungen) == 1 and "Disallow: /content/dam/" in meldungen[0]
    assert sperrregel(txt, "https://netz.example/x/y.pdf") == "Disallow: /*.pdf$"


def test_drossel_mindestabstand():
    from vnb.netz import Drossel
    # die Drossel selbst hält den Abstand exakt ein (Zeitpunkt der Freigabe, ohne Netzlaufzeit)
    async def lauf():
        d = Drossel(0.2)
        zeiten = []
        async def eins():
            await d.warten("https://x.de/a")
            zeiten.append(time.monotonic())
        await asyncio.gather(*(eins() for _ in range(5)))
        return sorted(zeiten)
    zeiten = asyncio.run(lauf())
    assert min(b - a for a, b in zip(zeiten, zeiten[1:])) >= 0.199


def test_hinweis_url_wird_geprueft(server, tmp_path):
    # Startseite ohne Links; das Preisblatt kennt der Crawler nur aus der Hinweis-Liste
    fund = asyncio.run(_lauf(server + "/karriere/", tmp_path,
                             hinweise=(server + "/dl/NNE_Strom_2026_endgueltig.pdf",)))
    assert fund.kandidat and fund.kandidat.ns["lp_ueber_2500"] == pytest.approx(171.87)


def test_hinweise_laden(tmp_path):
    from vnb.crawl import hinweise_laden, website_domain
    p = tmp_path / "h.csv"
    p.write_text("Netzbetreiber_Website,Preisblatt_URL,Status\n"
                 "www.evng.de,https://www.evng.de/x/netznutzungsentgelte_strom_2026_evng.pdf,Gefunden (PDF)\n"
                 "www.gemeinde-x.de,https://www.gemeinde-x.de,Gemeindeportal\n"
                 "https://www.blomberg-netz.de/,https://www.blomberg-netz.de/stromnetz/netzentgelte/,Gefunden\n",
                 encoding="utf-8")
    h = hinweise_laden(p)
    assert h["evng.de"] == ("https://www.evng.de/x/netznutzungsentgelte_strom_2026_evng.pdf",)
    assert "gemeinde-x.de" not in h                       # nur Startseite: nichts Neues
    assert h[website_domain("https://www.blomberg-netz.de/")] == ("https://www.blomberg-netz.de/stromnetz/netzentgelte/",)


def test_lokales_preisblatt_statt_download(tmp_path):
    # von Hand heruntergeladenes Preisblatt (Bot-Schutz) wird statt des Downloads genommen, ohne Anfrage
    import asyncio as aio
    from vnb.crawl import Auftrag, Crawler, lokale_preisblaetter_laden
    from vnb.netz import Drossel
    (tmp_path / "pb").mkdir()
    pdf(tmp_path / "pb" / "x.pdf", KOPF_STANDARD + ["Niederspannung   18,64   7,49   171,87   1,36"])
    (tmp_path / "preisblaetter.csv").write_text("url;datei;netzbetreiber\nhttps://gesperrt.example/p.pdf;pb/x.pdf;X\n",
                                                encoding="utf-8")
    c = Crawler(None, None, Drossel(0), tmp_path / "cache")
    c.lokal = lokale_preisblaetter_laden(tmp_path / "preisblaetter.csv")
    a = Auftrag(key="k", nr=1, name="Musternetz GmbH", mastr_nr="", website="gesperrt.example")
    pfad, fehler = aio.run(c.herunterladen(None, "https://gesperrt.example/p.pdf", a))
    assert fehler == "" and pfad.read_bytes().startswith(b"%PDF")


def test_lokales_preisblatt_ohne_namen_mit_zuordnung(tmp_path):
    # Preisblatt ohne Netzbetreibernamen, von Hand diesem Netzbetreiber zugeordnet: kein Prüfgrund "Name fehlt"
    import asyncio as aio
    from vnb.crawl import Auftrag, Crawler, lokale_namen_laden, lokale_preisblaetter_laden
    from vnb.netz import Drossel
    (tmp_path / "pb").mkdir()
    pdf(tmp_path / "pb" / "x.pdf", KOPF_STANDARD[1:] + ["Niederspannung   18,64   7,49   171,87   1,36"])
    (tmp_path / "preisblaetter.csv").write_text(
        "url;datei;netzbetreiber\nhttps://gesperrt.example/p.pdf;pb/x.pdf;Musternetz GmbH\n", encoding="utf-8")
    c = Crawler(None, None, Drossel(0), tmp_path / "cache")
    c.lokal = lokale_preisblaetter_laden(tmp_path / "preisblaetter.csv")
    c.lokal_namen = lokale_namen_laden(tmp_path / "preisblaetter.csv")
    a = Auftrag(key="k", nr=1, name="Musternetz GmbH", mastr_nr="", website="gesperrt.example")
    k = aio.run(c.dokument_pruefen(None, "https://gesperrt.example/p.pdf", a))
    assert k.verwendbar and not k.name_fehlt and "Netzbetreibername nicht im Dokument" not in k.pruefen
    b = Auftrag(key="k", nr=2, name="Anderes Netz GmbH", mastr_nr="", website="gesperrt.example")
    assert aio.run(c.dokument_pruefen(None, "https://gesperrt.example/p.pdf", b)).name_fehlt


def test_neu_auslesen_ohne_netz(tmp_path):
    # Schritt "lauf --offline": nur die früher geladenen Dokumente im Zwischenspeicher neu auslesen
    import asyncio as aio
    import hashlib
    from vnb.crawl import Auftrag, Crawler
    url = "https://www.musternetz.example/preisblatt_strom_2026.pdf"
    d = tmp_path / "cache" / "k"
    d.mkdir(parents=True)
    h = hashlib.sha1(url.encode()).hexdigest()[:12]
    pdf(d / f"{h}.pdf", KOPF_STANDARD + ["Niederspannung   18,64   7,49   171,87   1,36"])
    (d / f"{h}.url").write_text(url)
    c = Crawler(None, None, None, tmp_path / "cache")
    c.offline = True
    a = Auftrag(key="k", nr=1, name="Musternetz GmbH", mastr_nr="", website="www.musternetz.example")
    fund = aio.run(c.bearbeiten(a))
    assert fund.kandidat and fund.kandidat.ns["lp_ueber_2500"] == 171.87
    # ohne Zwischenspeicher: kein Netzzugriff, nichts gefunden
    leer = Auftrag(key="leer", nr=2, name="Leer GmbH", mastr_nr="", website="www.leer.example")
    assert c.zwischenspeicher_urls(leer) == [] and aio.run(c.neu_auslesen(leer)) is None
    pfad, fehler = aio.run(c.herunterladen(None, "https://www.leer.example/x.pdf", leer))
    assert pfad is None and fehler == "nicht im Zwischenspeicher"
