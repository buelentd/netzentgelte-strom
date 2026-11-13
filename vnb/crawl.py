"""Suche des Preisblatts je Netzbetreiber mit Playwright (Chromium)."""
from __future__ import annotations

import asyncio
import hashlib
import heapq
import itertools
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

from .bewerten import PREISSTAND_RANG, Kandidat, bewerten
from .extract import norm
from .netz import TIMEOUT_MS, USER_AGENT, Drossel, Robots, basis_domain

MAX_SEITEN = 40
MAX_TIEFE = 3
MAX_DOKUMENTE = 15
MAX_GROESSE = 40 * 1024 * 1024
DOK_ENDUNG = re.compile(r"\.(pdf|pdfx|xlsx|xlsm|xls)(?:$|[?#])", re.I)
DOK_MUSTER = re.compile(r"deliverfile|/filer/sharing/|media\.php|/download(?:s)?/file|getfile|/blob/|"
                        r"[?&](?:download|file)=", re.I)
IGNORIEREN = re.compile(r"\.(jpe?g|png|gif|svg|webp|ico|mp4|mp3|zip|docx?|pptx?|css|js|xml|json|ics|vcf)(?:$|[?#])", re.I)
SPERRE = re.compile(r"just a moment|attention required|access denied|zugriff verweigert|captcha|"
                    r"request rejected|forbidden", re.I)

SEITE_PLUS = [("netzentgelt", 6), ("netznutzung", 5), ("preisblatt", 5), ("preisblaett", 5), ("entgelt", 2),
              ("netzzugang", 4), ("marktpartner", 3), ("veroeffentlichung", 4), ("netzinformation", 3),
              ("netzbetreiber", 2), ("lieferant", 2), ("stromnetz", 3), ("strom", 2), ("netz", 1),
              ("download", 1), ("energiewirtschaft", 1), ("enwg", 2), ("2026", 3), ("unternehmen", 1)]
SEITE_MINUS = re.compile(r"karriere|jobs|stellen|presse|news|aktuelles|blog|impressum|datenschutz|cookie|"
                         r"kontakt|shop|tarif|ladesaeule|e-?mobil|glasfaser|breitband|internet|telefon|"
                         r"baeder|bad\b|parken|veranstaltung|login|anmelden|warenkorb|faq|stoerung", re.I)
SPARTE_FREMD = re.compile(r"(?<![a-z])gas(?!se|t)|erdgas|waerme|fernwaerme|wasser|abwasser|einspeis|biogas|wasserstoff", re.I)

DOK_PLUS = [("preisblatt", 5), ("preisblaett", 5), ("netzentgelt", 5), ("netznutzung", 4), ("nne", 3),
            ("entgelt", 2), ("strom", 2), ("endgueltig", 3), ("final", 3), ("netzzugang", 1),
            ("standardlastprofil", 3), ("slp", 2), ("ohne leistungsmessung", 3)]
DOK_MINUS = [("14a", 4), ("sonderform", 4), ("atypisch", 4), ("singul", 4), ("fiktiv", 0),
             ("messstell", 4), ("msb", 3), ("konzession", 4), ("kwk", 3), ("umlage", 2), ("verlust", 4),
             ("erloesobergrenze", 6), ("strukturdaten", 5), ("blindarbeit", 2), ("mehrerloes", 5),
             ("netzverlust", 4), ("kapazitaet", 1), ("einspeis", 20), ("redispatch", 5), ("bilanz", 3),
             ("vermiedene", 20), ("referenzpreis", 20)]

LINKS_JS = r"""
() => {
  const out = [];
  const attrs = ['href','data-href','data-url','data-link','data-file','data-download','link','url',
                 'ng-reflect-href','ng-reflect-link','ng-reflect-url','download-url','src'];
  const kontext = el => {
    const c = el.closest('li,tr,p,dd,td,figure,article');
    return c ? (c.innerText || '').trim().slice(0, 250) : '';
  };
  const els = document.querySelectorAll('a,area,evd-link,[data-href],[data-url],[data-link],[data-file],' +
                                        '[data-download],[ng-reflect-href],[ng-reflect-link],iframe,embed,object');
  for (const el of els) {
    let u = null;
    for (const a of attrs) {
      const v = el.getAttribute && el.getAttribute(a);
      if (v && !/^(javascript:|mailto:|tel:|#)/i.test(v.trim())) { u = v.trim(); break; }
    }
    if (!u && el.tagName === 'OBJECT') u = el.getAttribute('data');
    if (!u) continue;
    const t = (el.innerText || el.getAttribute('title') || el.getAttribute('aria-label') ||
               el.getAttribute('download') || '').trim().slice(0, 250);
    let abs = u;                     // relative Links gegen <base href> auflösen (ovag: Seite setzt eine Basis-Adresse)
    try { abs = new URL(u, document.baseURI).href; } catch (e) {}
    out.push({u: abs, t, k: kontext(el)});
  }
  for (const el of document.querySelectorAll('[onclick]')) {
    const m = (el.getAttribute('onclick') || '').match(/(https?:\/\/[^'"\s)]+|\/[^'"\s)]+\.(pdf|xlsx?))/i);
    if (m) out.push({u: m[1], t: (el.innerText || '').trim().slice(0, 250), k: kontext(el)});
  }
  return out;
}
"""


@dataclass
class Auftrag:
    key: str
    nr: int
    name: str
    mastr_nr: str
    website: str
    aliase: tuple = ()
    pflicht: tuple = ()       # Netzgebiet-Kennungen, die im Dokument vorkommen müssen
    ausschluss: tuple = ()    # Kennungen anderer Netzgebiete derselben Website
    nur_endgueltig: bool = False
    nur_slp: bool = False     # nur ein SLP-Preisblatt gesucht (RLM bereits bekannt, z. B. Pilot)
    hinweise: tuple = ()      # zusätzliche Start-URLs (Unterseiten oder Dokumente), lauf/hinweis_urls.csv
    vorschlaege: tuple = ()   # abgeleitete Start-URLs (Host/Verzeichnis der Vorjahres-Quelle, umgeschriebene Jahres-URLs): werden geprüft, aber nicht als vertraut gewertet


@dataclass
class Fund:
    status: str
    kandidat: Kandidat | None = None
    slp_kandidat: Kandidat | None = None
    hinweise: list = field(default_factory=list)
    grund: str = ""
    kandidaten: list = field(default_factory=list)
    seiten: int = 0
    website: str = ""


def _score(text: str, plus, minus=None) -> int:
    s = sum(w for k, w in plus if k in text)
    if minus is not None and minus.search(text):
        s -= 4
    return s


def seiten_score(text: str) -> int:
    t = norm(unquote(text))
    if SPARTE_FREMD.search(t) and "strom" not in t:
        return -1
    return _score(t, SEITE_PLUS, SEITE_MINUS)


def dok_score(text: str, jahr: int) -> int:
    t = norm(unquote(text))
    if SPARTE_FREMD.search(t) and "strom" not in t:
        return -1
    s = _score(t, DOK_PLUS) - sum(w for k, w in DOK_MINUS if k in t)
    jahre = set(re.findall(r"(?<!\d)(20[2-3]\d)(?!\d)", t))
    if str(jahr) in jahre:
        s += 6
    elif jahre:
        s -= 6
    elif re.search(rf"(?<!\d){str(jahr)[2:]}(?!\d)|(?<!\d){str(jahr - 1)[2:]}1[0-2]\d\d(?!\d)", t):
        s += 1   # z. B. 251212_... (Datum im Dateinamen)
    if str(jahr + 1) in jahre and str(jahr) not in jahre:
        s -= 10
    if "vorl" in t:
        s += 1
    return s


def ist_dokument(url: str) -> bool:
    return bool(DOK_ENDUNG.search(url) or DOK_MUSTER.search(url))


def start_urls(website: str) -> list[str]:
    w = website.strip()
    if not w:
        return []
    if not re.match(r"https?://", w, re.I):
        return ["https://" + w.lstrip("/"), "http://" + w.lstrip("/")]
    p = urlparse(w)
    if p.scheme == "http":
        return [w, "https://" + w[len("http://"):]]
    return [w]


def website_domain(website: str) -> str:
    """"https://www.blomberg-netz.de/" und "www.blomberg-netz.de" → "blomberg-netz.de"."""
    return basis_domain(re.sub(r"^https?://", "", website.strip().lower()).split("/")[0])


def eigene_website(url: str, website: str) -> bool:
    """Dokument liegt auf der Website des Netzbetreibers oder einer Adresse mit deren Kern ("netze-stwab.de")."""
    if not website:
        return False
    d_url, d_web = website_domain(url), website_domain(website)
    kern = d_web.rsplit(".", 1)[0]
    return d_url == d_web or (len(kern) >= 5 and kern in d_url.rsplit(".", 1)[0])


def lokale_namen_laden(pfad: Path) -> dict[str, str]:
    """URL → Netzbetreiber aus lauf/preisblaetter.csv (manuelle Zuordnung)."""
    import csv
    if not pfad.exists():
        return {}
    return {z["url"].strip(): z.get("netzbetreiber", "").strip()
            for z in csv.DictReader(pfad.read_text(encoding="utf-8-sig").splitlines(), delimiter=";") if z.get("url")}


def lokale_preisblaetter_laden(pfad: Path) -> dict[str, Path]:
    """Von Hand heruntergeladene Preisblätter (z. B. bei Bot-Schutz): Spalten url;datei;netzbetreiber.
    Die Datei liegt relativ zur CSV; der Crawler nimmt sie statt des Downloads dieser URL."""
    import csv
    if not pfad.exists():
        return {}
    out = {}
    for z in csv.DictReader(pfad.read_text(encoding="utf-8-sig").splitlines(), delimiter=";"):
        if z.get("url") and z.get("datei"):
            out[z["url"].strip()] = pfad.parent / z["datei"].strip()
    return out


def hinweise_laden(pfad: Path) -> dict[str, tuple]:
    """Hinweis-URLs je Website-Domain aus einer CSV (Spalten website;url, Trennzeichen ; oder ,).

    Startseiten selbst werden übergangen (die besucht der Crawler ohnehin)."""
    import csv
    if not pfad.exists():
        return {}
    text = pfad.read_text(encoding="utf-8-sig")
    trenner = ";" if text.splitlines()[0].count(";") >= 1 else ","
    out: dict[str, list] = {}
    for zeile in csv.reader(text.splitlines()[1:], delimiter=trenner):
        if len(zeile) < 2 or not zeile[0].strip() or not zeile[1].strip().lower().startswith("http"):
            continue
        website, url = zeile[0].strip(), zeile[1].strip()
        if urlparse(url).path.strip("/") == "" and not urlparse(url).query:
            continue
        out.setdefault(website_domain(website), []).append(url)
    return {k: tuple(dict.fromkeys(v)) for k, v in out.items()}


class Crawler:
    def __init__(self, browser, robots: Robots, drossel: Drossel, cache: Path, jahr: int = 2026,
                 max_seiten: int = MAX_SEITEN, log=print):
        self.browser = browser
        self.robots = robots
        self.drossel = drossel
        self.cache = cache
        self.jahr = jahr
        self.max_seiten = max_seiten
        self.log = log
        self.lokal: dict[str, Path] = {}       # URL → lokal abgelegtes Preisblatt
        self.lokal_namen: dict[str, str] = {}  # URL → Netzbetreiber laut lauf/preisblaetter.csv
        self.offline = False                   # nur Zwischenspeicher neu auslesen, kein Netzzugriff
        self.nur_hinweise = False              # nur Hinweis-Dokumente (Suchtreffer) prüfen, Website nicht durchsuchen

    async def _kontext(self):
        ctx = await self.browser.new_context(user_agent=USER_AGENT, locale="de-DE",
                                             extra_http_headers={"Accept-Language": "de-DE,de;q=0.9"})
        ctx.set_default_timeout(TIMEOUT_MS)

        async def route(r):
            if r.request.resource_type in ("image", "media", "font"):
                await r.abort()
            else:
                await r.continue_()
        await ctx.route("**/*", route)
        return ctx

    # ------------------------------------------------------------ Webseiten mit Preistabellen
    HTML_JS = """() => { const t = [];
        document.querySelectorAll('table').forEach(tb => { tb.querySelectorAll('tr').forEach(r =>
          t.push([...r.children].map(c => c.innerText.replace(/\\s+/g, ' ').trim()).join('   '))); t.push(''); });
        return (document.body ? document.body.innerText : '').replace(/\\t/g, '   ') + '\\n\\n' + t.join('\\n'); }"""
    HTML_MARKER = re.compile(r"leistungspreis|arbeitspreis|netznutzungsentgelt|netzentgelt", re.I)
    HTML_EINHEIT = re.compile(r"€\s*/\s*kw|ct\s*/\s*kwh|cent\s*/\s*kwh|euro\s*/\s*kw", re.I)

    async def html_speichern(self, page, url: str, a: Auftrag) -> bool:
        """Preise stehen manchmal als Tabelle direkt in der Webseite (kein PDF). Dann den Seitentext (Tabellen spaltentreu)
        wie ein Dokument im Zwischenspeicher ablegen: <hash>.html + <hash>.url. True, wenn die Seite nach Preisen aussieht."""
        try:
            text = await page.evaluate(self.HTML_JS)
        except Exception:
            return False
        if not text or len(text) < 300 or len(self.HTML_MARKER.findall(text)) < 2 or len(self.HTML_EINHEIT.findall(text)) < 3:
            return False
        if len(re.findall(r"\d+[.,]\d+", text)) < 8:
            return False
        ziel_dir = self.cache / a.key
        ziel_dir.mkdir(parents=True, exist_ok=True)
        h = hashlib.sha1(url.encode()).hexdigest()[:12]
        (ziel_dir / f"{h}.html").write_text(text[:400_000], encoding="utf-8")
        (ziel_dir / f"{h}.url").write_text(url)
        return True

    # ------------------------------------------------------------ Dokumente
    async def herunterladen(self, ctx_request, url: str, a: Auftrag, referer: str = "") -> tuple[Path | None, str]:
        ziel_dir = self.cache / a.key
        ziel_dir.mkdir(parents=True, exist_ok=True)
        h = hashlib.sha1(url.encode()).hexdigest()[:12]
        lokal = self.lokal.get(url)
        if lokal and lokal.exists():               # von Hand heruntergeladen (lauf/preisblaetter.csv)
            pfad = ziel_dir / f"{h}{lokal.suffix.lower()}"
            pfad.write_bytes(lokal.read_bytes())
            (ziel_dir / f"{h}.url").write_text(url)
            return pfad, ""
        for endung in ("pdf", "xlsx", "xls", "html"):  # nicht die Begleitdatei <hash>.url; html = Preistabelle aus einer Webseite
            vorhanden = ziel_dir / f"{h}.{endung}"
            if vorhanden.exists():
                return vorhanden, ""
        if self.offline:
            return None, "nicht im Zwischenspeicher"
        erlaubt = await self.robots.erlaubt(url)
        if erlaubt is False:
            return None, "robots"
        await self.drossel.warten(url)
        try:
            r = await ctx_request.get(url, timeout=TIMEOUT_MS, max_redirects=10,
                                      headers={"Referer": referer} if referer else None)
        except Exception as e:
            return None, f"Download-Fehler: {str(e).splitlines()[0][:100]}"
        if r.status != 200:
            return None, f"HTTP {r.status}"
        laenge = int(r.headers.get("content-length") or 0)
        if laenge > MAX_GROESSE:
            return None, "zu groß"
        body = await r.body()
        if body.startswith(b"%PDF"):
            ext = "pdf"
        elif body.startswith(b"PK"):
            ext = "xlsx"
        elif body.startswith(b"\xd0\xcf\x11\xe0"):
            ext = "xls"
        else:
            return None, "kein PDF/Excel"
        pfad = ziel_dir / f"{h}.{ext}"
        pfad.write_bytes(body)
        (ziel_dir / f"{h}.url").write_text(url)
        return pfad, ""

    async def dokument_pruefen(self, ctx_request, url, a: Auftrag, kontext="", referer=""):
        pfad, fehler = await self.herunterladen(ctx_request, url, a, referer)
        if not pfad:
            k = Kandidat(url=url, grund=fehler)
            return k
        k = await asyncio.to_thread(bewerten, pfad, url, a.name, a.aliase, a.website, self.jahr,
                                    a.pflicht, a.ausschluss, kontext, url in a.hinweise)
        if k.name_fehlt and eigene_website(url, a.website) and not (a.pflicht or a.ausschluss):
            # Vorlage ohne Netzbetreibernamen, aber von der eigenen Website (nicht bei geteilter Website)
            k.name_fehlt = False
            k.pruefen = [p for p in k.pruefen if p != "Netzbetreibername nicht im Dokument"]
            k.hinweise.append("Name nicht im Dokument, Preisblatt von der eigenen Website")
        elif k.name_fehlt and norm(self.lokal_namen.get(url, "")) == norm(a.name):
            # von Hand heruntergeladen und in lauf/preisblaetter.csv diesem Netzbetreiber zugeordnet
            k.name_fehlt = False
            k.pruefen = [p for p in k.pruefen if p != "Netzbetreibername nicht im Dokument"]
            k.hinweise.append("Netzbetreiber laut manueller Zuordnung (Name nicht im Dokument)")
        return k

    # ------------------------------------------------------------ Hauptablauf
    def zwischenspeicher_urls(self, a: Auftrag) -> list[str]:
        """URLs der früher geladenen Dokumente dieses Netzbetreibers (Begleitdateien <hash>.url)."""
        d = self.cache / a.key
        if not d.is_dir():
            return []
        urls = [f.read_text().strip() for f in sorted(d.glob("*.url"))]
        return [u for u in urls if u] + [u for u in a.hinweise if u in self.lokal and u not in urls]

    async def neu_auslesen(self, a: Auftrag) -> Fund | None:
        """Alle früher geladenen Dokumente ohne Netzzugriff neu auslesen; None, wenn keine vorhanden."""
        urls = self.zwischenspeicher_urls(a)
        if not urls:
            return None
        geprueft = {}
        for u in urls:
            k = await self.dokument_pruefen(None, u, a, "Zwischenspeicher")
            if k.grund != "nicht im Zwischenspeicher":
                geprueft[u] = k
        if not geprueft:
            return None
        return self._entscheiden(a, geprueft, [], [], 0, 1, a.website)

    async def bearbeiten(self, a: Auftrag) -> Fund:
        if self.offline:
            return await self.neu_auslesen(a) or Fund("kein_preisblatt", grund="keine Dokumente im Zwischenspeicher")
        if not a.website:
            return Fund("keine_website", grund="keine Website im MaStR")
        ctx = await self._kontext()
        try:
            return await asyncio.wait_for(self._crawl(ctx, a), timeout=20 * 60)
        except asyncio.TimeoutError:
            return Fund("blockiert", grund="Gesamtzeit je Website überschritten (20 min)")
        finally:
            await ctx.close()

    async def _crawl(self, ctx, a: Auftrag) -> Fund:
        page = await ctx.new_page()
        zaehler = itertools.count()
        queue: list = []
        besucht: set[str] = set()
        dokumente: dict[str, dict] = {}
        geprueft: dict[str, Kandidat] = {}
        robots_gesperrt: list[str] = []
        fehler: list[str] = []
        seiten = seiten_ok = 0
        domains: set[str] = set()

        # Startseite (https, sonst http)
        start = None
        for su in start_urls(a.website):
            erlaubt = await self.robots.erlaubt(su)
            if erlaubt is False:
                return Fund("robots", grund="Startseite per robots.txt gesperrt", website=su)
            start = su
            break
        heapq.heappush(queue, (-100, next(zaehler), start, 0))
        alternative = start_urls(a.website)[1:]
        for h in (*a.hinweise, *a.vorschlaege):   # Hinweis-URLs und Vorschläge: Dokumente sofort prüfen, Seiten direkt nach der Startseite
            if ist_dokument(h):
                dokumente[h] = {"score": 1000, "kontext": "Hinweis-URL", "ref": ""}
            else:
                heapq.heappush(queue, (-99, next(zaehler), h, 1))

        if self.nur_hinweise:
            # nur die Hinweis-Seiten selbst öffnen (z. B. Seite "Netzentgelte"), keine weiteren Seiten
            queue[:] = [q for q in queue if q[2] in a.hinweise]
            heapq.heapify(queue)
            seiten_ok = 1                  # keine Startseite besucht: nicht als "blockiert" werten
        def bester():
            gut = [k for k in geprueft.values() if k.verwendbar]
            return max(gut, key=lambda k: k.rang()) if gut else None

        def fertig():
            """Ziel erreicht: endgültiges, unauffälliges RLM-Blatt und unauffällige SLP-Werte."""
            slp_gut = any(k.slp_ok and k.preisstand == "endgültig" and not k.folgejahr for k in geprueft.values())
            if a.nur_slp:
                return slp_gut
            b = bester()
            return bool(b and not b.pruefen and not b.folgejahr and b.preisstand == "endgültig"
                        and (b.slp_ok or slp_gut))

        async def pruefe_offene(min_score):
            offen = sorted(((d["score"], u) for u, d in dokumente.items() if u not in geprueft
                            and d["score"] >= min_score), reverse=True)
            for _, u in offen:
                if len(geprueft) >= MAX_DOKUMENTE:
                    return
                k = await self.dokument_pruefen(ctx.request, u, a, dokumente[u]["kontext"], dokumente[u]["ref"])
                geprueft[u] = k
                if k.grund == "robots":
                    robots_gesperrt.append(u)
                self.log(f"    Dokument {u[:110]} -> {'verwendbar' if k.verwendbar else k.grund}"
                         f"{' ' + k.preisstand if k.verwendbar else ''}")

        def dok_merken(u, text, kontext, ref):
            sc = dok_score(u + " " + text + " " + kontext, self.jahr)
            if u not in dokumente or dokumente[u]["score"] < sc:
                dokumente[u] = {"score": sc, "kontext": (text + " " + kontext)[:400], "ref": ref}

        while queue and seiten < self.max_seiten:
            _, _, url, tiefe = heapq.heappop(queue)
            if url in besucht:
                continue
            besucht.add(url)
            erlaubt = await self.robots.erlaubt(url)
            if erlaubt is False:
                robots_gesperrt.append(url)
                continue
            if erlaubt is None and seiten_ok == 0:
                fehler.append(f"robots.txt nicht erreichbar ({url})")
                if alternative:
                    heapq.heappush(queue, (-100, next(zaehler), alternative.pop(0), 0))
                continue
            await self.drossel.warten(url)
            seiten += 1
            try:
                resp = await page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT_MS)
            except Exception as e:
                msg = str(e)
                if "Download is starting" in msg or "download" in msg.lower() and "abort" in msg.lower():
                    dok_merken(url, "", "", "")
                else:
                    fehler.append(f"{type(e).__name__}: {msg.splitlines()[0][:120]}")
                    if seiten_ok == 0 and alternative:
                        heapq.heappush(queue, (-100, next(zaehler), alternative.pop(0), 0))
                continue
            if resp is None:
                continue
            ct = (resp.headers.get("content-type") or "").lower()
            if "pdf" in ct or "spreadsheet" in ct or "excel" in ct:
                dok_merken(url, "", "", "")
                continue
            if resp.status >= 400:
                fehler.append(f"HTTP {resp.status} {url[:80]}")
                if seiten_ok == 0 and alternative:
                    heapq.heappush(queue, (-100, next(zaehler), alternative.pop(0), 0))
                continue
            try:
                await page.wait_for_load_state("networkidle", timeout=6000)
            except Exception:
                pass
            try:
                titel = await page.title()
                links = await page.evaluate(LINKS_JS)
                html = await page.content()
            except Exception as e:
                fehler.append(f"Seite nicht lesbar: {type(e).__name__}")
                continue
            if seiten_ok == 0 and SPERRE.search(titel or "") and len(links) < 5:
                fehler.append(f"Sperrseite: {titel[:60]}")
                continue
            seiten_ok += 1
            aktuell = page.url
            if not self.offline and await self.html_speichern(page, aktuell, a):
                dok_merken(aktuell, "Preisblatt Netzentgelte Strom Netznutzung", "Preise als Tabelle in der Webseite", aktuell)
            if tiefe == 0:
                domains.add(basis_domain(aktuell))
                domains.add(basis_domain(url))
                for sm in await self.robots.sitemaps(aktuell):
                    if seiten < self.max_seiten:
                        seiten += 1
                        for u in await self._sitemap(ctx.request, sm):
                            if ist_dokument(u):
                                dok_merken(u, "", "", "")
                            elif basis_domain(u) in domains:
                                sc = seiten_score(u)
                                if sc >= 6:
                                    heapq.heappush(queue, (-sc, next(zaehler), u, 1))
            for m in re.finditer(r"https?://[^\"'\s<>]+?(?:\.pdf|\.xlsx?|deliverFile/[^\"'\s<>]+)(?:\?[^\"'\s<>]*)?",
                                 html, re.I):
                links.append({"u": m.group(0).replace("&amp;", "&"), "t": "", "k": ""})
            for l in links:
                u = urljoin(aktuell, l["u"]).split("#")[0]
                if not u.startswith("http") or IGNORIEREN.search(u):
                    continue
                text, kontext = l.get("t") or "", l.get("k") or ""
                if ist_dokument(u):
                    dok_merken(u, text, kontext, aktuell)
                    continue
                if self.nur_hinweise or basis_domain(u) not in domains or u in besucht or tiefe + 1 > MAX_TIEFE:
                    continue
                sc = seiten_score(u + " " + text)
                if sc > 0:
                    heapq.heappush(queue, (-sc, next(zaehler), u, tiefe + 1))
            # vielversprechende Dokumente sofort prüfen; mit endgültigem Treffer aufhören
            await pruefe_offene(12)
            if fertig():
                break

        if not fertig():
            await pruefe_offene(4)
        return self._entscheiden(a, geprueft, robots_gesperrt, fehler, seiten, seiten_ok, start)

    async def _sitemap(self, req, url) -> list[str]:
        if await self.robots.erlaubt(url) is False:
            return []
        await self.drossel.warten(url)
        try:
            r = await req.get(url, timeout=TIMEOUT_MS)
            if r.status != 200:
                return []
            txt = (await r.body())[:5_000_000].decode("utf-8", "replace")
        except Exception:
            return []
        return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", txt)[:20000]

    def _entscheiden(self, a, geprueft, robots_gesperrt, fehler, seiten, seiten_ok, start) -> Fund:
        kandidaten = sorted(geprueft.values(), key=lambda k: k.rang(), reverse=True)
        def beschr(k):
            teile = []
            if k.verwendbar:
                teile.append("RLM")
            if k.slp_verwendbar:
                teile.append("SLP")
            return f"{k.url} ({'+'.join(teile) + ', ' + k.preisstand if teile else k.grund})"
        liste = [beschr(k) for k in kandidaten[:6]]
        gut = [k for k in kandidaten if k.verwendbar]
        slp_kand = sorted((k for k in kandidaten if k.slp_verwendbar), key=lambda k: k.slp_rang(), reverse=True)
        if a.nur_slp:
            if slp_kand:
                s = slp_kand[0]
                return Fund("ok" if s.slp_ok else "pruefen", slp_kandidat=s, kandidaten=liste, seiten=seiten,
                            website=start, grund="; ".join(s.slp_pruefen))
            return Fund("kein_preisblatt", grund="kein SLP-Preisblatt gefunden", kandidaten=liste,
                        seiten=seiten, website=start)
        if gut:
            b = gut[0]
            hinweise = list(b.hinweise)
            pruefen = list(b.pruefen)
            gleichrangig = [k for k in gut[1:] if not k.pruefen and k.preisstand == b.preisstand
                            and k.folgejahr == b.folgejahr
                            and k.werte_tupel() != b.werte_tupel()]
            if not b.pruefen and gleichrangig:
                pruefen.append("weitere Preisblätter mit abweichenden NS-Werten: "
                               + ", ".join(k.url for k in gleichrangig[:3]))
            if a.nur_endgueltig and b.preisstand != "endgültig":
                return Fund("kein_preisblatt", grund="kein endgültiges Preisblatt gefunden",
                            kandidaten=liste, seiten=seiten, website=start)
            k = Kandidat(**{**b.__dict__, "pruefen": pruefen, "hinweise": hinweise})
            # SLP: aus demselben Blatt, sonst aus dem besten SLP-Blatt mit mindestens gleichem Preisstand
            s = k if k.slp_ok else None
            if s is None:
                passend = [x for x in slp_kand if x.slp_ok and PREISSTAND_RANG.get(x.preisstand, 1)
                           >= PREISSTAND_RANG.get(k.preisstand, 1)]
                s = passend[0] if passend else (k if k.slp_verwendbar else (slp_kand[0] if slp_kand else None))
            alle = pruefen + ([] if s and s.slp_ok else
                              (s.slp_pruefen + (["Netzbetreibername nicht im SLP-Dokument"] if s.name_fehlt else []))
                              if s else ["SLP-Werte nicht gefunden"])
            return Fund("pruefen" if alle else "ok", kandidat=k, slp_kandidat=s, kandidaten=liste,
                        seiten=seiten, website=start, grund="; ".join(dict.fromkeys(alle)))
        if slp_kand:
            s = slp_kand[0]
            return Fund("pruefen", slp_kandidat=s, kandidaten=liste, seiten=seiten, website=start,
                        grund="; ".join(["keine RLM-Werte (Jahresleistungspreissystem) gefunden", *s.slp_pruefen]))
        if seiten_ok == 0:
            if robots_gesperrt:
                return Fund("robots", grund="Seiten per robots.txt gesperrt", seiten=seiten, website=start)
            return Fund("blockiert", grund="; ".join(dict.fromkeys(fehler))[:300] or "keine Seite erreichbar",
                        seiten=seiten, website=start)
        dok_robots = [u for u in robots_gesperrt if ist_dokument(u)]
        if dok_robots and not any(k.grund and k.grund != "robots" for k in kandidaten):
            return Fund("robots", grund="Preisblatt-Links per robots.txt gesperrt: " + ", ".join(dok_robots[:3]),
                        kandidaten=liste, seiten=seiten, website=start)
        relevante_sperren = [u for u in robots_gesperrt if seiten_score(u) >= 5]
        if relevante_sperren and not kandidaten:
            return Fund("robots", grund="relevante Seiten per robots.txt gesperrt: " + ", ".join(relevante_sperren[:3]),
                        seiten=seiten, website=start)
        gruende = "; ".join(dict.fromkeys(k.grund for k in kandidaten if k.grund))
        grund = (f"{len(kandidaten)} Dokument(e) geprüft: {gruende}" if kandidaten
                 else f"kein Preisblatt-Link gefunden ({seiten} Seiten durchsucht)")
        return Fund("kein_preisblatt", grund=grund[:500], kandidaten=liste, seiten=seiten, website=start)
