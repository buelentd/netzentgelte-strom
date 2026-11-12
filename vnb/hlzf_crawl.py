"""Suche der Hochlastzeitfenster (HLZF, § 19 Abs. 2 Satz 1 StromNEV) je Netzbetreiber mit Playwright (Chromium).

Jeder Netzbetreiber muss seine Fenster veröffentlichen. Das Dokument ist also da (PDF, Excel oder Tabelle in einer Webseite),
der Crawler muss es nur finden und am Inhalt erkennen. Wiederverwendet: Drossel (1 Anfrage/s je Host), Robots (robots.txt;
ein 4xx auf robots.txt gilt nach RFC 9309 als "keine Einschränkung"), USER_AGENT, Dokumenterkennung aus vnb/crawl.py.

Ablauf je Netzbetreiber
1. Startseite und Sitemap (XML und sichtbar) lesen, Links nach HLZF-Hinweisen bewerten (Text, Adresse, Jahr).
2. Seiten nach Bewertung abarbeiten (höchstens 40 Seiten, Tiefe 3). Auch Links in data-Attributen (data-pdf-url) und Dateien auf Fremdhosts (CDN).
3. Jeder Dokumentkandidat wird geladen und am INHALT geprüft: "Hochlast", Uhrzeiten, Jahreszeiten, Jahr. Eine Webseite zählt wie ein Dokument.
4. Ergebnis: Status gefunden_2026 | nur_2027 | nur_aelter | anfrage | kein_treffer | blockiert | robots | nicht_erreichbar.
Funde werden nach eingang/pdfs_neu/<MaStR-Nr.>_hlzf_<Name> gelegt (Webseiten als Text nach ergebnis/hlzf_crawl_texte/).
Aufruf: python -m vnb.hlzf_crawl [--liste CSV] [--max N] [--parallel N] [--nur SNB…]"""
from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import heapq
import itertools
import os
import re
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

from .crawl import SPERRE, ist_dokument, start_urls, website_domain
from .extract import norm
from .netz import TIMEOUT_MS, Drossel, Robots, basis_domain

# Neutrale, ehrliche Kennung: ein Crawler, ohne Firmennamen (Festlegung Nutzer 11.11.2026). Keine Tarnung als normaler Browser, keine Umgehung von Sperren.
USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36 "
              "(compatible; netzentgelte-datenerhebung/1.0; Crawler)")

MAX_SEITEN = 40
MAX_TIEFE = 3
MAX_DOKUMENTE = 14
MAX_GROESSE = 30 * 1024 * 1024
ZIEL_DOKUMENTE = Path(os.environ.get("HLZF_ZIEL", "eingang/pdfs_neu"))
ZIEL_TEXTE = Path(os.environ.get("HLZF_TEXTE", "ergebnis/hlzf_crawl_texte"))
DEBUG = bool(os.environ.get("HLZF_DEBUG"))
IGNORIEREN = re.compile(r"\.(jpe?g|png|gif|svg|webp|ico|mp4|mp3|zip|docx?|pptx?|css|js|json|ics|vcf)(?:$|[?#])", re.I)

# Hinweise in Linktext und Adresse (nach norm: ä→ae usw.)
PLUS = [("hochlast", 10), ("hlzf", 10), ("atypisch", 6), ("individuelle netzentgelt", 5), ("individuelles netzentgelt", 5),
        ("19 abs", 4), ("19-abs", 4), ("19_abs", 4), ("stromnev", 3), ("sonderform", 3), ("zeitfenster", 3),
        ("pflichtangaben", 3), ("veroeffentlichung", 3), ("marktpartner", 2), ("netzzugang", 2), ("netzentgelt", 2),
        ("netznutzung", 2), ("download", 2), ("elektrizitaet", 3), ("elektrizitat", 3), ("stromnetz", 3), ("netze", 2),
        ("formular", 3), ("dokument", 2), ("service", 1), ("kunden", 1), ("energie", 1), ("strom", 1), ("netz", 1)]
MINUS = re.compile(r"\bgas\b|waerme|wasser|einspeis|datenschutz|impressum|karriere|kontakt|presse|newsletter|ladestation|"
                   r"wallbox|pv-anlage|solar|tarif", re.I)
DOK_HINWEIS = re.compile(r"hochlast|hlzf|atypisch|19[ _.-]*abs|stromnev|individuell|zeitfenster|sonderform|hlz[ _-]", re.I)
# Häufige Einstiegspfade deutscher Netzbetreiber (werden nur abgerufen, wenn robots.txt es erlaubt; 404 kostet nur eine Anfrage)
SEED_PFADE = ["/formularcenter", "/formulare", "/service/downloads", "/dokumente", "/netz", "/netznutzung", "/netznutzung/strom", "/veroeffentlichungspflichten", "/veroeffentlichungen", "/pflichtangaben",
              "/netzentgelte", "/netzdaten", "/downloads", "/stromnetz", "/strom/netz", "/netz/strom", "/netz/veroeffentlichungen"]
# Bereiche, die nie HLZF enthalten: nicht crawlen (Zeit sparen)
HART_IGNORIEREN = re.compile(r"/(karriere|jobs?|stellen|presse|news|aktuelles|neuigkeiten|veranstaltung\w*|baeder|bad|freibad|schwimmbad|"
                             r"glasfaser|wasser|trinkwasser|gas|erdgas|waerme|fernwaerme|impressum|datenschutz|shop|kundenportal|"
                             r"ladestation\w*|e-mobilitaet|photovoltaik|ausbildung|unternehmen/geschichte)(/|$|-|\\.)", re.I)


PORTAL_HOSTEN = {"enwg-veroeffentlichungen.de", "gipsprojekt.de"}


def verwandte_domain(href: str, start_domain: str) -> bool:
    """Zielhost ist dieselbe Basisdomain oder eine Netz-Schwesterdomain mit demselben Namensstamm (stadtwerke-x.de → netze-x.de, netz.stadtwerke-x.de)."""
    h = urlparse(href).netloc.lower().split(":")[0].removeprefix("www.")
    if basis_domain(h) in PORTAL_HOSTEN:      # Veröffentlichungsportale, die viele Stadtwerke einbinden (GIPS / EnWG-Tool)
        return True
    if basis_domain(h) == basis_domain(start_domain):
        return True
    stamm = [t for t in re.split(r"[.\-]", basis_domain(start_domain).rsplit(".", 1)[0]) if len(t) >= 5 and t not in ("stadtwerke", "gemeindewerke", "energie", "netze", "netz")]
    return bool(re.search(r"netz|infrastruktur|energienetze", h)) and any(t in h for t in stamm)


HOCHLAST = re.compile(r"hochlast[- ]?(?:zeit|fenster)|hlzf", re.I)   # nicht "Hochlasttarifstufe" (HT/NT)
UHRZEIT = re.compile(r"(?<!\d)([01]?\d|2[0-3])[:.][0-5]\d(?!\d)")
JAHRESZEIT = re.compile(r"fr[üu]hling|fr[üu]hjahr|sommer|herbst|winter", re.I)
MODUL3 = re.compile(r"§\s*14a|modul\s*3|steuerbare\s+verbrauchseinrichtung|hochtarif|niedertarif|\bHT\b.{0,20}\bNT\b", re.I)
PARA19 = re.compile(r"stromnev|atypisch|§\s*19|individuelle[sn]?\s+netzentgelt", re.I)
ANFRAGE = re.compile(r"auf\s+anfrage|anfragen|bitte\s+(?:kontaktieren|wenden)", re.I)

HTML_JS = """() => { const t = [];
    document.querySelectorAll('table').forEach(tb => { tb.querySelectorAll('tr').forEach(r =>
      t.push([...r.children].map(c => c.innerText.replace(/\\s+/g, ' ').trim()).join('   '))); t.push(''); });
    const tc = document.body ? document.body.textContent.replace(/\\s+/g, ' ') : '';
    const vers = (/hochlast/i.test(tc)) ? '\\n\\n' + tc.slice(0, 300000) : '';
    return (document.body ? document.body.innerText : '').replace(/\\t/g, '   ') + '\\n\\n' + t.join('\\n') + vers; }"""
LINKS_JS = """() => { const out = [];
    document.querySelectorAll('a[href]').forEach(a => {
      let t = (a.innerText || a.title || a.getAttribute('aria-label') || '').trim();
      if (t.length < 14) { const c = a.closest('li, tr, p, td, dd, div'); if (c) t = (t + ' ' + c.innerText).replace(/\\s+/g, ' ').trim(); }
      out.push([a.href, t.slice(0, 200)]); });
    document.querySelectorAll('[data-pdf-url],[data-href],[data-download],[data-file],[data-url]').forEach(e => {
      for (const k of ['data-pdf-url', 'data-href', 'data-download', 'data-file', 'data-url']) {
        const v = e.getAttribute(k); if (v) out.push([new URL(v, document.baseURI).href, (e.innerText || e.getAttribute('data-pdf-name') || '').trim().slice(0, 120)]); } });
    return out; }"""


DOK_PFAD = re.compile(r"/downloads?/\d+|/download/|[?&](?:download|file|dl)=|/media/\d+|/dokumente?/|/attachment|/getfile|/dateien?/", re.I)
DOK_TEXT = re.compile(r"\((?:pdf|xlsx?|xls)\b|\b(?:pdf|xlsx?)[,)]|\.(?:pdf|xlsx?)\b", re.I)


def dok_link(href: str, text: str) -> bool:
    """Link auf ein Dokument: Endung .pdf/.xlsx, Dokumentpfad (/downloads/17085/) oder Linktext "(pdf, 119 KB)". Ob es eines ist, zeigt erst der Inhalt."""
    return bool(ist_dokument(href) or DOK_PFAD.search(href) or DOK_TEXT.search(text or ""))


def score(text: str, jahr: int = 2026) -> int:
    t = norm(unquote(text))
    s = sum(w for k, w in PLUS if k in t)
    if MINUS.search(t):
        s -= 4
    jahre = set(re.findall(r"(?<!\d)(20[2-3]\d)(?!\d)", t))
    if str(jahr) in jahre:
        s += 5
    elif str(jahr + 1) in jahre:
        s += 3          # 2027 vorläufig ist auch gefragt
    elif jahre:
        s -= 4
    return s


def inhalt_pruefen(text: str) -> dict:
    """Sieht der Text nach einer HLZF-Tabelle aus? Rückgabe: ok, jahr, anfrage, zeiten, jahreszeiten."""
    zeiten = len(UHRZEIT.findall(text))
    jz = len({m.lower()[:4] for m in JAHRESZEIT.findall(text)})
    hl = bool(HOCHLAST.search(text))
    jahre = re.findall(r"(?<!\d)(20[2-3]\d)(?!\d)", text)
    haeufig = {}
    for j in jahre:
        haeufig[j] = haeufig.get(j, 0) + 1
    jahr = ""
    if "2026" in haeufig:
        jahr = "2026"
    elif "2027" in haeufig:
        jahr = "2027"
    elif haeufig:
        jahr = max(haeufig, key=lambda k: (k, haeufig[k]))
    raster = bool(re.search(r"viertelstund|1/4|0/1", text, re.I))
    ok = hl and ((zeiten >= 3 and jz >= 2) or (raster and zeiten >= 8))
    # Modul-3-Tarifzeiten (§ 14a EnWG, HT/NT) sind keine Hochlastzeitfenster nach § 19 StromNEV (EWR Remscheid)
    if ok and MODUL3.search(text) and not PARA19.search(text):
        ok = False
    return {"ok": ok, "jahr": jahr, "anfrage": bool(hl and ANFRAGE.search(text)), "zeiten": zeiten, "jz": jz}


def datei_text(pfad: Path) -> str:
    try:
        if pfad.suffix.lower() == ".pdf":
            return subprocess.run(["pdftotext", "-layout", str(pfad), "-"], capture_output=True, text=True, timeout=60).stdout
        import openpyxl
        wb = openpyxl.load_workbook(pfad, data_only=True, read_only=True)
        teile = []
        for ws in wb:
            for row in ws.iter_rows(values_only=True):
                z = " ".join(str(c) for c in row if c not in (None, ""))
                if z:
                    teile.append(z)
            if len(teile) > 6000:
                break
        return "\n".join(teile)
    except Exception:
        return ""


class Fund:
    def __init__(self, mastr, name, domain):
        self.mastr, self.name, self.domain = mastr, name, domain
        self.status, self.seiten, self.jahr, self.url, self.quelle, self.datei, self.hinweis = "kein_treffer", 0, "", "", "", "", ""
        self.alle: list[tuple[str, str, str]] = []   # (jahr, url, datei)

    def zeile(self):
        return [self.mastr, self.name, self.domain, self.status, self.jahr, self.url, self.quelle, self.datei, self.seiten, self.hinweis,
                " | ".join(f"{j}:{u}" for j, u, _ in self.alle[:6])]


KOPF = ["mastr_nr", "netzbetreiber", "domain", "status", "jahr", "dokument_url", "quelle_seite", "datei", "seiten", "hinweis", "alle_funde"]


class HlzfCrawler:
    def __init__(self, browser, req, robots: Robots, drossel: Drossel, log=print):
        self.browser, self.req, self.robots, self.drossel, self.log = browser, req, robots, drossel, log

    async def _kontext(self):
        ctx = await self.browser.new_context(user_agent=USER_AGENT, locale="de-DE", accept_downloads=False,
                                             extra_http_headers={"Accept-Language": "de-DE,de;q=0.9"})
        ctx.set_default_timeout(TIMEOUT_MS)

        async def route(r):
            if r.request.resource_type in ("image", "media", "font"):
                await r.abort()
            else:
                await r.continue_()
        await ctx.route("**/*", route)
        return ctx

    async def _laden(self, url: str, referer: str = ""):
        """(Fehler, Bytes). robots.txt und Drossel eingehalten."""
        erlaubt = await self.robots.erlaubt(url)
        if erlaubt is False:
            return "robots", b""
        if erlaubt is None:
            return "nicht_erreichbar", b""
        await self.drossel.warten(url)
        try:
            r = await self.req.get(url, timeout=TIMEOUT_MS, max_redirects=10, headers={"Referer": referer} if referer else None)
        except Exception as e:
            return f"Fehler: {str(e).splitlines()[0][:80]}", b""
        if r.status != 200:
            return f"HTTP {r.status}", b""
        if int(r.headers.get("content-length") or 0) > MAX_GROESSE:
            return "zu groß", b""
        return "", await r.body()

    async def sitemap_urls(self, basis: str) -> list[str]:
        urls = []
        for sm in (await self.robots.sitemaps(basis + "/"))[:2] or [basis + "/sitemap.xml"]:
            fehler, body = await self._laden(sm)
            if fehler:
                continue
            txt = body.decode("utf-8", "replace")
            locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", txt)
            untermaps = [u for u in locs if u.lower().endswith(".xml")][:3]
            urls += [u for u in locs if not u.lower().endswith(".xml")]
            for u in untermaps:
                f2, b2 = await self._laden(u)
                if not f2:
                    urls += re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", b2.decode("utf-8", "replace"))
        return [u for u in urls if score(u) >= 8][:25]

    async def bearbeiten(self, mastr: str, name: str, website: str) -> Fund:
        domain = website_domain(website)
        f = Fund(mastr, name, domain)
        starts = start_urls(website)
        if not starts:
            f.status = "keine_website"
            return f
        ctx = await self._kontext()
        try:
            await self._crawl(ctx, f, starts)
        except Exception as e:
            f.hinweis = f"Fehler: {str(e).splitlines()[0][:100]}"
        finally:
            await ctx.close()
        return f

    async def _crawl(self, ctx, f: Fund, starts: list[str]):
        zaehler = itertools.count()
        heap: list = []
        gesehen: set[str] = set()
        dok_gesehen: set[str] = set()
        geprueft_docs = 0
        robots_gesperrt = blockiert = erreicht = 0

        def seite_ein(url, prio, tiefe, ref):
            u = url.split("#")[0]
            if u in gesehen or IGNORIEREN.search(u) or ist_dokument(u) or HART_IGNORIEREN.search(urlparse(u).path):
                return
            heapq.heappush(heap, (-prio, next(zaehler), u, tiefe, ref))

        for s in starts:
            seite_ein(s, 100, 0, "")
        basis = starts[0].rstrip("/")
        for pfad in SEED_PFADE:
            seite_ein(basis + pfad, 30, 1, "Seed")
        for u in await self.sitemap_urls(basis):
            if ist_dokument(u) and DOK_HINWEIS.search(norm(unquote(u))):
                dok_gesehen.add(u)
                geprueft_docs = await self._dokument(f, u, "Sitemap", geprueft_docs)
            else:
                seite_ein(u, 50 + score(u), 1, "Sitemap")

        page = await ctx.new_page()
        suche_getan = False
        while heap and f.seiten < MAX_SEITEN and geprueft_docs < MAX_DOKUMENTE:
            _, _, url, tiefe, ref = (e := heapq.heappop(heap))
            if url in gesehen:
                continue
            gesehen.add(url)
            erlaubt = await self.robots.erlaubt(url)
            if erlaubt is False:
                robots_gesperrt += 1
                continue
            await self.drossel.warten(url)
            try:
                resp = await page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT_MS)
                await page.wait_for_timeout(600)
            except Exception:
                continue
            if resp is None:
                continue
            if resp.status in (401, 403, 429):
                blockiert += 1
                continue
            if resp.status >= 400:
                continue
            f.seiten += 1
            erreicht += 1
            if DEBUG:
                print("  Seite", url[:110], "S=%d" % -e[0])
            try:
                text = await page.evaluate(HTML_JS)
            except Exception:
                text = ""
            frame_links = []
            for fr in page.frames[1:]:        # Portale (GIPS, EnWG-Tool) laden die Veröffentlichungen in einem iframe
                try:
                    if fr.url.startswith("http"):
                        await page.wait_for_timeout(300)
                        text += "\n\n" + await fr.evaluate(HTML_JS)
                        frame_links += await fr.evaluate(LINKS_JS)
                except Exception:
                    pass
            if SPERRE.search(text[:600] or "") and len(text) < 1500:
                blockiert += 1
                continue
            # Die Seite selbst kann die Tabelle enthalten (HTML wie PDF)
            pr = inhalt_pruefen(text)
            if pr["ok"] and pr["zeiten"] >= 6 and pr["jz"] >= 3:      # Webseite strenger prüfen (Menütexte, Öffnungszeiten)
                self._seite_merken(f, url, text, pr)
            elif pr["anfrage"] and not f.hinweis:
                f.hinweis = f"Seite nennt Hochlast und Anfrage: {url}"
            try:
                links = await page.evaluate(LINKS_JS)
            except Exception:
                links = []
            links = list(links) + frame_links
            for href, txt in links:
                href = href.split("#")[0]
                if not href.startswith("http"):
                    continue
                s = score(txt + " " + href)
                if dok_link(href, txt):
                    th = norm(unquote(href + " " + txt))
                    # Preisblätter 2026/2027 enthalten die Fenster oft als Abschnitt (swa Netze, Emmendingen): auch laden, der Inhalt entscheidet
                    if href in dok_gesehen or not (DOK_HINWEIS.search(th) or (re.search(r"preisbl|netzentgelt|entgelte|netznutzung", th) and re.search(r"2026|2027", th))):
                        continue
                    dok_gesehen.add(href)
                    geprueft_docs = await self._dokument(f, href, url, geprueft_docs, s)
                    if geprueft_docs >= MAX_DOKUMENTE:
                        break
                elif tiefe < MAX_TIEFE and s >= 1 and verwandte_domain(href, url):
                    seite_ein(href, s, tiefe + 1, url)
            if not suche_getan and tiefe == 0:
                suche_getan = True
                ziel = await self._seitensuche(page, url)
                if ziel:
                    seite_ein(ziel, 200, 1, "Seitensuche")
            if f.alle and any(j == "2026" for j, _, _ in f.alle) and (any(j == "2027" for j, _, _ in f.alle) or f.seiten >= 12):
                break
        await page.close()
        if any(j == "2026" for j, _, _ in f.alle):
            f.status = "gefunden_2026"
        elif any(j == "2027" for j, _, _ in f.alle):
            f.status = "nur_2027"
        elif f.alle:
            f.status = "nur_aelter"
        elif f.hinweis.startswith("Seite nennt Hochlast und Anfrage"):
            f.status = "anfrage"
        elif erreicht == 0 and blockiert:
            f.status = "blockiert"
        elif erreicht == 0 and robots_gesperrt:
            f.status = "robots"
        elif erreicht == 0:
            f.status = "nicht_erreichbar"
        best = sorted(f.alle, key=lambda x: (x[0] != "2026", x[0] != "2027", x[1]))
        if best:
            f.jahr, f.url, f.datei = best[0]

    SUCHFELD = ("input[type=search], input[name=q], input[name=s], input[name=search], input[name=suche], "
                "input[name=searchword], input[name=query], input[name=keywords], input[name=\"tx_indexedsearch_pi2[search][sword]\"]")

    async def _seitensuche(self, page, url: str) -> str:
        """Die eigene Suche der Website benutzen (wie ein Mensch): "Hochlastzeitfenster" eintippen, Adresse der Trefferseite zurückgeben."""
        try:
            el = await page.query_selector(self.SUCHFELD)
            if not el or not await el.is_visible():
                return ""
            await self.drossel.warten(url)
            await el.fill("Hochlastzeitfenster")
            await el.press("Enter")
            await page.wait_for_load_state("domcontentloaded", timeout=15000)
            ziel = page.url
            return ziel if ziel != url else ""
        except Exception:
            return ""

    def _seite_merken(self, f: Fund, url: str, text: str, pr: dict):
        ZIEL_TEXTE.mkdir(parents=True, exist_ok=True)
        h = hashlib.sha1(url.encode()).hexdigest()[:8]
        pfad = ZIEL_TEXTE / f"{f.mastr}_{h}.txt"
        pfad.write_text(f"URL: {url}\n\n{text[:300_000]}", encoding="utf-8")
        if url not in [u for _, u, _ in f.alle]:
            f.alle.append((pr["jahr"] or "?", url, str(pfad)))
            f.quelle = url

    async def _dokument(self, f: Fund, url: str, ref: str, n: int, s: int = 0) -> int:
        fehler, body = await self._laden(url, ref if ref.startswith("http") else "")
        n += 1
        if DEBUG:
            print("  Dok", url[:110], fehler or len(body))
        if fehler:
            return n
        if body.startswith(b"%PDF"):
            ext = ".pdf"
        elif body.startswith(b"PK"):
            ext = ".xlsx"
        elif body.startswith(b"\xd0\xcf\x11\xe0"):
            ext = ".xls"
        else:
            return n
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as t:
            t.write(body)
            tmp = Path(t.name)
        try:
            text = await asyncio.to_thread(datei_text, tmp)
            # Name der Datei hilft bei Bild-PDFs ohne Text nicht; nur Textdateien prüfen
            pr = inhalt_pruefen(text)
            if pr["ok"]:
                ZIEL_DOKUMENTE.mkdir(parents=True, exist_ok=True)
                name = re.sub(r"[^A-Za-z0-9._-]+", "_", unquote(Path(urlparse(url).path).name))[:80] or "dokument" + ext
                if not name.lower().endswith(ext):
                    name += ext
                ziel = ZIEL_DOKUMENTE / f"{f.mastr}_hlzf_{name}"
                ziel.write_bytes(body)
                if url not in [u for _, u, _ in f.alle]:
                    f.alle.append((pr["jahr"] or "?", url, str(ziel)))
                    f.quelle = ref
            elif len(text.strip()) < 40 and len(body) > 20_000 and re.search(r"hochlast|hlzf", unquote(url), re.I):
                if url not in [u for _, u, _ in f.alle]:      # Bild-PDF ohne Textlayer: Treffer am Namen, am Bild zu lesen
                    ZIEL_DOKUMENTE.mkdir(parents=True, exist_ok=True)
                    name = re.sub(r"[^A-Za-z0-9._-]+", "_", unquote(Path(urlparse(url).path).name))[:80] or "dokument" + ext
                    ziel = ZIEL_DOKUMENTE / f"{f.mastr}_hlzf_{name}"
                    ziel.write_bytes(body)
                    jahr = (re.findall(r"20[2-3]\d", url) or ["?"])[0]
                    f.alle.append((jahr, url, str(ziel)))
                    f.hinweis = (f.hinweis + "; " if f.hinweis else "") + "Bild-PDF ohne Text: am Bild lesen"
        finally:
            tmp.unlink(missing_ok=True)
        return n


async def main_async(args):
    from playwright.async_api import async_playwright
    liste = list(csv.DictReader(open(args.liste, encoding="utf-8-sig"), delimiter=";"))
    T = {r["mastr_nr"]: r for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
    korr = {}
    try:                       # lauf/website_korrektur.csv (nr;website): Website laut Nutzer/vnbdigital.de statt MaStR
        nr2m = {r["nr"]: k for k, r in T.items()}
        korr = {nr2m[r["nr"]]: r["website"] for r in csv.DictReader(open("lauf/website_korrektur.csv", encoding="utf-8-sig"), delimiter=";") if r["nr"] in nr2m}
    except Exception:
        pass
    auftraege = []
    for r in liste:
        k = r["mastr_nr"]
        if (args.nur and k not in args.nur) or k in args.ohne:
            continue
        w = (korr.get(k) or T.get(k, {}).get("website") or r.get("domain_ohne_www") or r.get("domain") or "").strip()
        auftraege.append((k, r.get("netzbetreiber") or T.get(k, {}).get("netzbetreiber", ""), w))
    if args.max:
        auftraege = auftraege[:args.max]
    drossel = Drossel(1.0)
    ergebnis = []
    async with async_playwright() as pw:
        exe = os.environ.get("CHROMIUM_PATH", "/opt/pw-browsers/chromium")
        proxy = None
        if os.environ.get("HTTPS_PROXY") and not args.ohne_proxy:
            proxy = {"server": os.environ["HTTPS_PROXY"], "bypass": "localhost,127.0.0.1"}
        try:
            browser = await pw.chromium.launch(proxy=proxy)
        except Exception:
            browser = await pw.chromium.launch(executable_path=exe, proxy=proxy)
        req = await pw.request.new_context(user_agent=USER_AGENT, proxy=proxy,
                                           extra_http_headers={"Accept": "text/html,application/pdf,application/xhtml+xml,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*;q=0.8",
                                                               "Accept-Language": "de-DE,de;q=0.9"})
        robots = Robots(req, drossel, log=print)
        crawler = HlzfCrawler(browser, req, robots, drossel)
        sem = asyncio.Semaphore(args.parallel)

        async def lauf(a):
            async with sem:
                f = await crawler.bearbeiten(*a)
                print(f.mastr, f.domain, f.status, f.jahr, f.seiten, flush=True)
                ergebnis.append(f)
                neu = not Path(args.ausgabe).exists()      # laufend sichern, damit ein Abbruch nichts kostet
                with open(args.ausgabe, "a", encoding="utf-8-sig", newline="") as o:
                    w = csv.writer(o, delimiter=";")
                    if neu:
                        w.writerow(KOPF)
                    w.writerow(f.zeile())
        await asyncio.gather(*(lauf(a) for a in auftraege))
        await browser.close()
        await req.dispose()
    from collections import Counter
    print(dict(Counter(f.status for f in ergebnis)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--liste", default="ergebnis/HLZF_FEHLENDE_ZUM_SUCHEN.csv")
    ap.add_argument("--ausgabe", default="lauf/hlzf_crawl2_ergebnis.csv")
    ap.add_argument("--max", type=int, default=0)
    ap.add_argument("--parallel", type=int, default=6)
    ap.add_argument("--nur", nargs="*", default=[])
    ap.add_argument("--ohne-proxy", action="store_true")
    ap.add_argument("--ohne", nargs="*", default=[], help="MaStR-Nummern, die schon erledigt sind")
    asyncio.run(main_async(ap.parse_args()))


if __name__ == "__main__":
    main()
