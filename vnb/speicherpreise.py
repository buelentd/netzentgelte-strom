"""Speicherpreise im Netz sammeln: Preise in €/kWh aus Angeboten, Händlerseiten, Ratgebern und Fachmagazinen.

Zweck: belegte Richtwerte für den Rechner statt eines Werts ohne Quelle. Jeder Fund trägt URL, Abrufdatum,
Textauszug (Kontext), Preis von/bis, netto/brutto, Kapazität, Umfang (nur Hardware oder schlüsselfertig) und
Art der Quelle. Nichts wird geschätzt: was der Text nicht sagt, bleibt leer oder "unklar".

Regeln wie beim Netzentgelt-Crawler: robots.txt beachten, höchstens 1 Anfrage pro Sekunde je Domain, Timeout 30 s,
höchstens N Seiten je Domain. Suchtreffer (Brave) werden nicht dauerhaft gespeichert, nur die daraus gelesenen
Funde mit der Quelladresse. Die Funde sind Kandidaten ("ungeprüft"); in den Rechner geht nur, was am Original
geprüft und als "geprüft" markiert ist.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import html
import json
import re
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

from protego import Protego

UA = "NetzentgelteStromBot/1.0 (+https://github.com/buelentd/netzentgelte-strom; Marktrecherche Speicherpreise)"
SPALTEN = ["id", "abruf_datum", "url", "domain", "titel", "art_quelle", "preis_von_eur_kwh", "preis_bis_eur_kwh",
           "netto_brutto", "kapazitaet_kwh", "umfang", "segment", "veroeffentlicht", "kontext", "status", "pruefnotiz"]
PREIS_MIN, PREIS_MAX = 80.0, 1800.0          # €/kWh; darunter sind es Strompreise, darüber Ausreißer oder andere Größen

# Abfragen für die Websuche (Brave). Bewusst viele Formulierungen: Angebote, Ratgeber, Fachpresse.
ABFRAGEN = [
    "Gewerbespeicher Preis pro kWh netto Angebot",
    "Batteriespeicher Gewerbe Kosten pro kWh schlüsselfertig",
    "Industriespeicher Preis €/kWh 2026",
    "Stromspeicher 100 kWh Preis Gewerbe Industrie 2026",
    "Gewerbespeicher kaufen Preis 215 kWh",
    "Peak Shaving Batteriespeicher Kosten pro kWh",
    "Großspeicher Preise sinken €/kWh Marktübersicht",
    "BESS Container Preis pro kWh Gewerbe",
    "Gewerbespeicher Wirtschaftlichkeit Investitionskosten €/kWh",
    "Batteriespeicher Preisentwicklung Gewerbe 2026 Euro pro Kilowattstunde",
]
HERSTELLER = ["BYD", "Sungrow", "Tesvolt", "Huawei", "Pixii", "Intilion", "SMA", "GoodWe", "Fox ESS", "Sigenergy", "Kehua", "Hithium",
              "CATL", "Fenecon", "Senec", "E3/DC", "Kostal", "Varta", "sonnen", "Victron"]
# Runde 2: Hersteller, Angebote, Preislisten (auch PDF), Förderung, Ausschreibungen
ABFRAGEN2 = ([f"{h} Gewerbespeicher Preis pro kWh netto" for h in HERSTELLER]
              + ["Gewerbespeicher Preisliste pdf netto kWh", "Gewerbespeicher Angebot pdf Euro pro kWh", "Batteriespeicher Preisliste Großhandel B2B kWh pdf",
                 "Ausschreibung Batteriespeicher Gewerbe Zuschlag Euro pro kWh", "Förderung Batteriespeicher Unternehmen Investitionskosten Euro pro kWh Projekt",
                 "Stadtwerke Batteriespeicher Kosten Projekt Euro pro kWh Gewerbe", "Fraunhofer ISE Studie Batteriespeicher Gewerbe Systemkosten Euro pro kWh pdf",
                 "BSW Solar Marktdaten Batteriespeicher Preise Gewerbe", "vbw Leitfaden Stromspeicher für Unternehmen pdf", "intilion Industriespeicher Preis pro kWh",
                 "Industriespeicher 1 MWh Preis Euro pro kWh netto Container", "Gewerbespeicher 200 kWh Preis netto schlüsselfertig Angebot"])
# Runde 5: Hersteller aus der idealo-Herstellerliste (nur Batterien; Juratherm, Flamco, Alpha Thermotec sind Wärmespeicher)
HERSTELLER5 = ["Growatt", "GoodWe", "Fox ESS", "Dyness", "PYTES", "SofarSolar", "Felicity Solar", "SolarEdge", "VARTA", "Pramac", "G2 Energy Systems"]
ABFRAGEN5 = [f for h in HERSTELLER5 for f in (f"{h} Batteriespeicher Gewerbe Preis kWh netto",
                                              f"{h} Speicher Datenblatt Kapazität kWh Zyklen Wirkungsgrad Preis",
                                              f"{h} Gewerbespeicher Preisliste pdf")]
# Runde 3: Originale, die die Fundseiten selbst nennen (Fraunhofer ISE, vbw, pv magazine, Rödl & Partner, BSW, RWTH, intilion ...)
ABFRAGEN3 = [
    "Fraunhofer ISE Studie Juli 2024 Batteriespeicher Investition Speicher PV-Dach 30 kWp bis 1 MWp Euro je kWh Tabelle",
    "Fraunhofer ISE Wirtschaftlichkeit Batteriespeicher Gewerbe Studie pdf Investitionskosten Tabelle 1",
    "Rödl & Partner Studie Gewerbespeicher Wirtschaftlichkeit Investitionskosten",
    "vbw Leitfaden Stromspeicher für Unternehmen September 2025 pdf",
    "pv magazine Marktübersicht Groß- und Gewerbespeicher 2026 Durchschnittspreis Euro pro Kilowattstunde Auswertung",
    "ISEA RWTH Aachen Battery Charts Gewerbespeicher Systempreise",
    "intilion Industriespeicher scalestac Preis 1 MWh Euro pro kWh",
    "BSW Solar Preisindex Batteriespeicher Gewerbe Euro pro kWh",
    "BloombergNEF Battery Price Survey 2025 stationary storage turnkey",
    "Batteriespeicher-Report Großspeicher Preiserhebung 2025 Euro pro kWh Quellen",
    "Bundesnetzagentur Marktstammdatenregister Batteriespeicher Gewerbe Kosten Studie",
    "Deutsche Energie-Agentur dena Batteriespeicher Gewerbe Kosten Studie pdf",
]
VERWEIS = re.compile(r"studie|leitfaden|fraunhofer|marktübersicht|marktuebersicht|bsw|vbw|rwth|isea|intilion|bnef|bloomberg|verbraucherzentrale|"
                     r"battery.?chart|preisindex|preiserhebung|dena\b|bundesnetzagentur|r[öo]dl|pdf", re.I)
# feste Startseiten (robots.txt wird trotzdem geprüft)
STARTSEITEN = [
    "https://www.pv-magazine.de/marktuebersichten/grosse-batteriespeicher",
    "https://www.pv-magazine.de/2026/03/03/aktuelle-pv-magazine-marktuebersicht-fuer-gross-und-gewerbespeicher-mit-500-eintraegen/",
    "https://www.logicenergy.de/neuigkeiten/stromspeicher-100-kwh-preis-2026",
    "https://www.solarserver.de/2026/04/01/gewerbespeicher-acht-haeufige-fehler-bei-der-wirtschaftlichkeitsberechnung/",
]
MAGAZINE = ("pv-magazine", "solarserver", "photovoltaik.eu", "energie-und-management", "pv-magazine.de", "zfk.de", "topagrar",
            "photovoltaikbüro", "elektroniknet", "heise.de", "ingenieur.de", "energate")
STUDIEN = ("fraunhofer", "ise.fraunhofer", "dena.de", "agora", "bsw-solar", "bdew", "eupd", "bundesnetzagentur", "iea.org")

ZAHL = r"\d{1,4}(?:[.,]\d{1,2})?"
PREIS = re.compile(
    rf"(?P<a>{ZAHL})\s*(?:(?:–|-|—|bis|und)\s*(?P<b>{ZAHL})\s*)?(?:€|euro|eur)\s*(?:/|pro|je|per)\s*(?:kwh|kilowattstunde)", re.I)
PREIS_VORAN = re.compile(rf"(?:€|euro|eur)\s*(?P<a>{ZAHL})\s*(?:(?:–|-|—|bis)\s*(?P<b>{ZAHL})\s*)?(?:/|pro|je|per)\s*kwh", re.I)
KAP = re.compile(r"(\d{1,5}(?:[.,]\d+)?)\s*(?:–|-|bis)?\s*(\d{1,5}(?:[.,]\d+)?)?\s*(mwh|kwh)\b(?!\s*(?:/|pro|je))", re.I)
HEIM = re.compile(r"heimspeicher|hausspeicher|einfamilienhaus|privathaus|balkonkraftwerk|steckdosen", re.I)
GEWERBE = re.compile(r"gewerbe|industrie|gro(ß|ss)speicher|bess\b|container|peak.?shaving|unternehmen|betrieb", re.I)


class _Text(HTMLParser):
    """Sichtbarer Text einer Seite samt Titel und Veröffentlichungsdatum (meta/JSON-LD)."""
    SKIP = {"script", "style", "noscript", "svg", "head", "nav", "footer", "form", "iframe"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.teile: list[str] = []
        self.titel = ""
        self.datum = ""
        self._skip = 0
        self.links: list[tuple[str, str]] = []
        self._href = None
        self._anker: list[str] = []
        self._titel = False
        self._json = False
        self._buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self._href = a["href"]
            self._anker = []
        if tag == "title":
            self._titel = True
        if tag == "meta" and not self.datum:
            n = (a.get("property") or a.get("name") or a.get("itemprop") or "").lower()
            if n in ("article:published_time", "datepublished", "date", "dc.date", "og:updated_time", "article:modified_time"):
                self.datum = (a.get("content") or "")[:10]
        if tag == "script" and (a.get("type") or "").lower() == "application/ld+json":
            self._json = True
            self._buf = []
        if tag in self.SKIP and tag != "head":
            self._skip += 1
        if tag in ("p", "br", "li", "tr", "h1", "h2", "h3", "h4", "div", "td", "th"):
            self.teile.append("\n")

    def handle_endtag(self, tag):
        if tag == "a" and self._href:
            self.links.append((self._href, re.sub(r"\s+", " ", "".join(self._anker)).strip()))
            self._href = None
        if tag == "title":
            self._titel = False
        if tag == "script" and self._json:
            self._json = False
            m = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', "".join(self._buf))
            if m and not self.datum:
                self.datum = m.group(1)
        if tag in self.SKIP and tag != "head" and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._href is not None:
            self._anker.append(data)
        if self._json:
            self._buf.append(data)
        elif self._titel:
            self.titel += data.strip()
        elif not self._skip:
            self.teile.append(data)


def verweise_aus_html(rohhtml: str, url: str) -> list[tuple[str, str]]:
    """Ausgehende Links zu fremden Domains, deren Adresse oder Linktext auf Studien, Leitfäden, Marktübersichten u. ä. deutet."""
    p = _Text()
    try:
        p.feed(rohhtml)
    except Exception:
        pass
    eigen = urllib.parse.urlparse(url).netloc.lower().removeprefix("www.")
    out = []
    for href, anker in p.links:
        ziel = urllib.parse.urljoin(url, href).split("#")[0]
        d = urllib.parse.urlparse(ziel).netloc.lower().removeprefix("www.")
        if d and d != eigen and ziel.startswith("http") and VERWEIS.search(ziel + " " + anker):
            out.append((ziel, anker[:100]))
    return out


def seitentext(rohhtml: str) -> tuple[str, str, str]:
    p = _Text()
    try:
        p.feed(rohhtml)
    except Exception:
        pass
    text = re.sub(r"[ \t\xa0]+", " ", html.unescape("".join(p.teile)))
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip(), re.sub(r"\s+", " ", p.titel)[:160], p.datum


def _zahl(s: str) -> float:
    s = s.strip()
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}\.\d{3}", s):
        s = s.replace(".", "")
    return float(s)


def art_der_quelle(domain: str, text: str) -> str:
    d = domain.lower()
    if any(k in d for k in STUDIEN):
        return "Studie/Verband"
    if any(k in d for k in MAGAZINE):
        return "Fachmagazin"
    if re.search(r"angebot|jetzt anfragen|warenkorb|in den warenkorb|zzgl\. mwst|lieferzeit|kaufen", text[:6000], re.I):
        return "Händler/Anbieter"
    if re.search(r"ratgeber|so viel kostet|was kostet|kosten im überblick", text[:3000], re.I):
        return "Ratgeber"
    return "unklar"


def funde_aus_text(text: str, url: str, titel: str = "", veroeffentlicht: str = "", abruf: str | None = None) -> list[dict]:
    """Alle plausiblen €/kWh-Angaben einer Seite mit Kontext. Nichts wird ergänzt, was nicht dasteht."""
    domain = urllib.parse.urlparse(url).netloc.lower().removeprefix("www.")
    abruf = abruf or dt.date.today().isoformat()
    art = art_der_quelle(domain, text)
    out, gesehen = [], set()
    for rx in (PREIS, PREIS_VORAN):
        for m in rx.finditer(text):
            try:
                a = _zahl(m.group("a"))
                b = _zahl(m.group("b")) if m.group("b") else a
            except ValueError:
                continue
            if a > b:
                a, b = b, a
            if not (PREIS_MIN <= a <= PREIS_MAX and PREIS_MIN <= b <= PREIS_MAX):
                continue
            von, bis = max(0, m.start() - 170), min(len(text), m.end() + 170)
            ctx = re.sub(r"\s+", " ", text[von:bis]).strip()
            nah = text[max(0, m.start() - 90):m.end() + 90].lower()
            key = (round(a, 1), round(b, 1), ctx[:80])
            if key in gesehen:
                continue
            gesehen.add(key)
            nb = "netto" if re.search(r"netto|zzgl\.?\s*mwst|ohne\s*mwst|exkl", nah) else "brutto" if re.search(
                r"brutto|inkl\.?\s*mwst|inkl\.?\s*ust|einschließlich\s*mwst", nah) else "unklar"
            kap = KAP.search(nah)
            kapkwh = ""
            if kap:
                v = _zahl(kap.group(1)) * (1000 if kap.group(3).lower() == "mwh" else 1)
                kapkwh = f"{v:g}"
            hw = re.search(r"nur\s+hardware|ohne\s+(?:bauseitige\s+)?(?:montage|installation|wechselrichter)|hardwarepreis|hardware\s*(?:ab|kosten|preis)|reine\s+speicher|listenpreis", nah)
            tk = re.search(r"schl[üu]sselfertig|inkl\.?\s*(?:montage|installation|inbetriebnahme)|inklusive\s+montage|fertig\s+installiert|installiert|turnkey", nah)
            umfang = "nur Hardware" if hw and not tk else "schlüsselfertig" if tk and not hw else "unklar"   # beides im Umfeld: nicht entscheiden
            segment = "Heim" if HEIM.search(nah) and not GEWERBE.search(nah) else "Gewerbe/Industrie" if GEWERBE.search(nah) else "unklar"
            fid = hashlib.sha1(f"{url}|{a}|{b}|{ctx[:60]}".encode()).hexdigest()[:12]
            out.append({"id": fid, "abruf_datum": abruf, "url": url, "domain": domain, "titel": titel, "art_quelle": art,
                        "preis_von_eur_kwh": f"{a:g}".replace(".", ","), "preis_bis_eur_kwh": f"{b:g}".replace(".", ","),
                        "netto_brutto": nb, "kapazitaet_kwh": kapkwh.replace(".", ","), "umfang": umfang, "segment": segment,
                        "veroeffentlicht": veroeffentlicht, "kontext": ctx, "status": "ungeprüft", "pruefnotiz": ""})
    return out


class Holer:
    """HTTP mit robots.txt, Drosselung je Domain und Seitenlimit je Domain."""

    def __init__(self, pause: float = 1.0, max_seiten: int = 12, timeout: float = 30.0, log=print, abrufen=None):
        self.pause, self.max_seiten, self.timeout, self.log = pause, max_seiten, timeout, log
        self._letzte: dict[str, float] = {}
        self._anzahl: dict[str, int] = {}
        self._robots: dict[str, Protego | None] = {}
        self._abrufen = abrufen or self._http
        self.gesperrt: dict[str, str] = {}          # url -> Grund (403, 429, robots.txt): Liste für den Abruf von Hand im Browser

    def _http(self, url: str) -> tuple[int, str, str]:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            ctype = r.headers.get("Content-Type", "")
            data = r.read(3_000_000)
            enc = re.search(r"charset=([\w-]+)", ctype)
            return r.status, ctype, data.decode(enc.group(1) if enc else "utf-8", errors="replace")

    def _erlaubt(self, url: str) -> bool:
        p = urllib.parse.urlparse(url)
        basis = f"{p.scheme}://{p.netloc}"
        if basis not in self._robots:
            try:
                st, _, txt = self._abrufen(basis + "/robots.txt")
                self._robots[basis] = Protego.parse(txt) if st == 200 else None
            except Exception:
                self._robots[basis] = None            # keine robots.txt erreichbar: übliche Regel, Zugriff erlaubt
        r = self._robots[basis]
        return True if r is None else r.can_fetch(url, UA)

    def holen_pdf(self, url: str, max_seiten_pdf: int = 40, max_bytes: int = 40_000_000) -> str | None:
        """Text einer PDF-Datei (pdfplumber). Dieselben Regeln: robots.txt, Drosselung, Seitenlimit je Domain."""
        p = urllib.parse.urlparse(url)
        if p.scheme not in ("http", "https") or not re.search(r"\.pdf$", p.path, re.I) or not self._erlaubt(url):
            return None
        if self._anzahl.get(p.netloc, 0) >= self.max_seiten:
            return None
        warte = self.pause - (time.time() - self._letzte.get(p.netloc, 0))
        if warte > 0:
            time.sleep(warte)
        self._letzte[p.netloc] = time.time()
        self._anzahl[p.netloc] = self._anzahl.get(p.netloc, 0) + 1
        try:
            daten = self._bytes(url, max_bytes)
            if not daten.startswith(b"%PDF"):
                return None
            import io
            import pdfplumber
            with pdfplumber.open(io.BytesIO(daten)) as pdf:
                return "\n".join((pg.extract_text() or "") for pg in pdf.pages[:max_seiten_pdf])
        except Exception as e:
            self.log(f"PDF fehlgeschlagen {url}: {type(e).__name__}: {str(e)[:80]}")
            return None

    def _bytes(self, url: str, max_bytes: int) -> bytes:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/pdf"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return r.read(max_bytes)

    def holen(self, url: str) -> str | None:
        p = urllib.parse.urlparse(url)
        if p.scheme not in ("http", "https") or re.search(r"\.(pdf|jpe?g|png|gif|zip|xlsx?)$", p.path, re.I):
            return None
        if not self._erlaubt(url):
            self.log(f"robots.txt sperrt: {url}")
            self.gesperrt[url] = "robots.txt"
            return None
        if self._anzahl.get(p.netloc, 0) >= self.max_seiten:
            return None
        warte = self.pause - (time.time() - self._letzte.get(p.netloc, 0))
        if warte > 0:
            time.sleep(warte)
        self._letzte[p.netloc] = time.time()
        self._anzahl[p.netloc] = self._anzahl.get(p.netloc, 0) + 1
        try:
            st, ctype, txt = self._abrufen(url)
        except Exception as e:
            self.log(f"Abruf fehlgeschlagen {url}: {type(e).__name__}: {str(e)[:80]}")
            m = re.search(r"HTTP Error (403|429|401)", str(e))
            if m:
                self.gesperrt[url] = f"HTTP {m.group(1)}"
            return None
        if st != 200 or "html" not in ctype.lower():
            return None
        return txt


def bestehende_laden(pfad: Path) -> dict[str, dict]:
    if not pfad.exists():
        return {}
    with open(pfad, encoding="utf-8-sig", newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f, delimiter=";")}


def speichern(pfad: Path, zeilen: dict[str, dict]):
    pfad.parent.mkdir(parents=True, exist_ok=True)
    with open(pfad, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SPALTEN, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in sorted(zeilen.values(), key=lambda r: (r["domain"], r["url"], r["preis_von_eur_kwh"])):
            w.writerow(r)


def websuche(schluessel: str, abfrage: str, abrufen=None) -> list[str]:
    from .suche import _abrufen as brave, links
    try:
        return links((abrufen or brave)(schluessel, abfrage))
    except Exception:
        return []


def lauf(ziel: Path, schluessel: str = "", max_abfragen: int = 10, max_seiten_gesamt: int = 150, holer: Holer | None = None,
         suche=None, log=print, abfragen: list[str] | None = None, startseiten: list[str] | None = None,
         verweise: dict | None = None, zusatz_urls: list[str] | None = None) -> dict:
    holer = holer or Holer(log=log)
    suche = suche or (lambda q: websuche(schluessel, q) if schluessel else [])
    vorhanden = bestehende_laden(ziel)
    urls = list(STARTSEITEN if startseiten is None else startseiten) + list(zusatz_urls or [])
    for q in (ABFRAGEN if abfragen is None else abfragen)[:max_abfragen]:
        urls += suche(q)
        time.sleep(1.1 if schluessel else 0)
    gesehen, neu, seiten = set(), 0, 0
    for u in urls:
        u = u.split("#")[0]
        if u in gesehen:
            continue
        gesehen.add(u)
        if seiten >= max_seiten_gesamt:
            break
        if re.search(r"\.pdf$", urllib.parse.urlparse(u).path, re.I):
            text = holer.holen_pdf(u)
            if not text:
                continue
            titel, datum = (text.strip().splitlines() or [""])[0][:160], ""
        else:
            roh = holer.holen(u)
            if roh is None:
                continue
            text, titel, datum = seitentext(roh)
            if verweise is not None and funde_aus_text(text, u, titel, datum):
                for z, anker in verweise_aus_html(roh, u):
                    verweise.setdefault(z, {"url": z, "von": u, "anker": anker, "gelesen": ""})
        seiten += 1
        for f in funde_aus_text(text, u, titel, datum):
            if f["id"] not in vorhanden:
                vorhanden[f["id"]] = f
                neu += 1
    speichern(ziel, vorhanden)
    gesperrte_speichern(ziel.parent / "speicherpreise_gesperrt.csv", holer)
    log(f"Speicherpreise: {seiten} Seiten gelesen, {neu} neue Funde, {len(vorhanden)} insgesamt, {len(holer.gesperrt)} gesperrt")
    return {"seiten": seiten, "neu": neu, "gesamt": len(vorhanden)}


def gesperrte_speichern(pfad: Path, holer: "Holer"):
    """Gesperrte Adressen (403/429/robots.txt) in eine Liste für den Abruf von Hand im Browser; bestehende Einträge bleiben."""
    vorhanden = {}
    if pfad.exists():
        with open(pfad, encoding="utf-8-sig", newline="") as f:
            vorhanden = {r["url"]: r for r in csv.DictReader(f, delimiter=";")}
    for u, grund in holer.gesperrt.items():
        d = urllib.parse.urlparse(u).netloc.lower().removeprefix("www.")
        vorhanden.setdefault(u, {"url": u, "domain": d, "grund": grund, "abruf_datum": dt.date.today().isoformat(),
                                 "erledigt": "", "ablage": ""})
    pfad.parent.mkdir(parents=True, exist_ok=True)
    with open(pfad, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["url", "domain", "grund", "abruf_datum", "erledigt", "ablage"], delimiter=";")
        w.writeheader()
        for r in sorted(vorhanden.values(), key=lambda r: (r["domain"], r["url"])):
            w.writerow(r)


def verweise_laden(pfad: Path) -> dict[str, dict]:
    if not pfad.exists():
        return {}
    with open(pfad, encoding="utf-8-sig", newline="") as f:
        return {r["url"]: r for r in csv.DictReader(f, delimiter=";")}


def verweise_speichern(pfad: Path, v: dict[str, dict]):
    pfad.parent.mkdir(parents=True, exist_ok=True)
    with open(pfad, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["url", "von", "anker", "gelesen"], delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in sorted(v.values(), key=lambda r: r["url"]):
            w.writerow(r)


def pdf_tabellen(holer: "Holer", url: str, max_seiten: int = 60) -> tuple[list[list[str]], str]:
    """PDF laden und die Tabellen seitenweise auslesen (pdfplumber). Rückgabe: Zeilen [Seite, Zelle1, Zelle2 ...] und der Volltext
    für die Preissuche. Dieselben Regeln wie sonst: robots.txt, Drosselung, Seitenlimit je Domain; Sperren landen in der Liste."""
    pu = urllib.parse.urlparse(url)
    if not re.search(r"\.pdf$", pu.path, re.I) or not holer._erlaubt(url):
        if not holer._erlaubt(url):
            holer.gesperrt[url] = "robots.txt"
        return [], ""
    warte = holer.pause - (time.time() - holer._letzte.get(pu.netloc, 0))
    if warte > 0:
        time.sleep(warte)
    holer._letzte[pu.netloc] = time.time()
    try:
        daten = holer._bytes(url, 40_000_000)
        if not daten.startswith(b"%PDF"):
            return [], ""
        import io
        import pdfplumber
        zeilen, text = [], []
        with pdfplumber.open(io.BytesIO(daten)) as pdf:
            for nr, seite in enumerate(pdf.pages[:max_seiten], 1):
                text.append(seite.extract_text() or "")
                for tab in seite.extract_tables() or []:
                    for z in tab:
                        zellen = [re.sub(r"\s+", " ", (c or "")).strip() for c in z]
                        if any(zellen):
                            zeilen.append([str(nr)] + zellen)
        return zeilen, "\n".join(text)
    except Exception as e:
        holer.log(f"PDF-Tabellen fehlgeschlagen {url}: {type(e).__name__}: {str(e)[:80]}")
        m = re.search(r"HTTP Error (403|429|401)", str(e))
        if m:
            holer.gesperrt[url] = f"HTTP {m.group(1)}"
        return [], ""


def pdf_liste_lauf(urls: list[str], zielordner: Path, funde_pfad: Path, holer: "Holer | None" = None, log=print) -> dict:
    """Je Adresse: Tabellen als TSV ablegen (Datei nach Adresse benannt) und Preisangaben aus dem Text als Funde festhalten."""
    holer = holer or Holer(max_seiten=60, log=log)
    vorhanden = bestehende_laden(funde_pfad)
    zielordner.mkdir(parents=True, exist_ok=True)
    tabellen = neu = 0
    for u in urls:
        u = u.strip()
        if not u or u.startswith("#"):
            continue
        zeilen, text = pdf_tabellen(holer, u)
        if not zeilen and not text:
            log(f"nichts gelesen: {u}")
            continue
        name = re.sub(r"[^A-Za-z0-9._-]+", "_", urllib.parse.urlparse(u).netloc + urllib.parse.urlparse(u).path)[:120]
        with open(zielordner / (name + ".tsv"), "w", encoding="utf-8", newline="") as f:
            f.write(f"# Quelle: {u}\n# Abruf: {dt.date.today().isoformat()}\n# Spalte 1 = Seite des PDF, danach die Zellen der Tabellenzeile\n")
            for z in zeilen:
                f.write("\t".join(z) + "\n")
        tabellen += 1
        titel = (text.strip().splitlines() or [""])[0][:160]
        for fnd in funde_aus_text(text, u, titel, ""):
            if fnd["id"] not in vorhanden:
                vorhanden[fnd["id"]] = fnd
                neu += 1
        log(f"{u}: {len(zeilen)} Tabellenzeilen")
    speichern(funde_pfad, vorhanden)
    gesperrte_speichern(funde_pfad.parent / "speicherpreise_gesperrt.csv", holer)
    return {"tabellen": tabellen, "neue_funde": neu}


def auswertung(funde: dict[str, dict]) -> list[dict]:
    """Spannen nur aus geprüften Funden (netto, bekannter Umfang). Ungeprüfte erscheinen separat als Kandidaten."""
    import statistics
    gruppen: dict[tuple, list[float]] = {}
    for r in funde.values():
        if r.get("status") != "geprüft":
            continue
        v = (float(r["preis_von_eur_kwh"].replace(",", ".")) + float(r["preis_bis_eur_kwh"].replace(",", "."))) / 2
        gruppen.setdefault((r["umfang"], r["netto_brutto"], r["segment"]), []).append(v)
    return [{"umfang": k[0], "netto_brutto": k[1], "segment": k[2], "anzahl": len(v), "min": min(v), "median": statistics.median(v), "max": max(v)}
            for k, v in sorted(gruppen.items())]


AUSZUG_SPALTEN = ["id", "url", "abruf_datum", "titel", "veroeffentlicht", "preis_von_eur_kwh", "preis_bis_eur_kwh", "auszug"]


def auszuege(funde_pfad: Path, ziel: Path, holer: Holer | None = None, fenster: int = 700, log=print) -> dict:
    """Zu jedem Fund den Originaltext rund um die Preisangabe (je ca. 2 x fenster Zeichen) neu abrufen und ablegen.

    Zweck: Prüfung am Original, wenn die Seite von der Arbeitsumgebung nicht erreichbar ist. Es werden nur
    Auszüge gespeichert, nicht ganze Seiten."""
    holer = holer or Holer(max_seiten=40, log=log)
    funde = bestehende_laden(funde_pfad)
    je_url: dict[str, list[dict]] = {}
    for f in funde.values():
        je_url.setdefault(f["url"], []).append(f)
    erledigt = set(bestehende_laden(ziel))
    ausgabe = {k: v for k, v in bestehende_laden(ziel).items()}
    n = 0
    for url, liste in je_url.items():
        if all(f["id"] in erledigt for f in liste):
            continue
        roh = holer.holen(url)
        if roh is None:
            continue
        text, titel, datum = seitentext(roh)
        for f in liste:
            a = f["preis_von_eur_kwh"].replace(",", ".")
            b = f["preis_bis_eur_kwh"].replace(",", ".")
            treffer = None
            for rx in (PREIS, PREIS_VORAN):
                for m in rx.finditer(text):
                    try:
                        x, y = _zahl(m.group("a")), _zahl(m.group("b")) if m.group("b") else _zahl(m.group("a"))
                    except ValueError:
                        continue
                    if x > y:
                        x, y = y, x
                    if f"{x:g}" == f"{float(a):g}" and f"{y:g}" == f"{float(b):g}":
                        treffer = m
                        break
                if treffer:
                    break
            if not treffer:
                continue
            auszug = re.sub(r"\s+", " ", text[max(0, treffer.start() - fenster):treffer.end() + fenster]).strip()
            ausgabe[f["id"]] = {"id": f["id"], "url": url, "abruf_datum": dt.date.today().isoformat(), "titel": titel,
                                "veroeffentlicht": datum, "preis_von_eur_kwh": f["preis_von_eur_kwh"],
                                "preis_bis_eur_kwh": f["preis_bis_eur_kwh"], "auszug": auszug}
            n += 1
    ziel.parent.mkdir(parents=True, exist_ok=True)
    with open(ziel, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=AUSZUG_SPALTEN, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in sorted(ausgabe.values(), key=lambda r: (r["url"], r["preis_von_eur_kwh"])):
            w.writerow(r)
    log(f"Auszüge: {n} neu, {len(ausgabe)} insgesamt")
    return {"neu": n, "gesamt": len(ausgabe)}


if __name__ == "__main__":
    import argparse
    import os
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ziel", default="ergebnis/speicherpreise_funde.csv")
    ap.add_argument("--abfragen", type=int, default=10)
    ap.add_argument("--seiten", type=int, default=150)
    ap.add_argument("--auszuege", action="store_true", help="zu den vorhandenen Funden Originalauszüge ablegen")
    ap.add_argument("--runde", type=int, default=1, help="2 = Hersteller, Angebote, Preislisten, PDFs")
    a = ap.parse_args()
    if a.auszuege:
        auszuege(Path(a.ziel), Path("ergebnis/speicherpreise_auszuege.csv"))
    else:
        vp = Path(a.ziel).parent / "speicherpreise_verweise.csv"
        if a.runde == 3:
            v = verweise_laden(vp)
            lauf(Path(a.ziel), os.environ.get("SUCHE_SCHLUESSEL", ""), a.abfragen, a.seiten, abfragen=ABFRAGEN3, startseiten=[], verweise=v)
            verweise_speichern(vp, v)
        elif a.runde == 6:                     # Adressen aus lauf/speicherpreise_pdfs.txt: Tabellen auslesen
            urls = Path("lauf/speicherpreise_pdfs.txt").read_text(encoding="utf-8").splitlines()
            print(pdf_liste_lauf(urls, Path(a.ziel).parent / "speicherpreise_pdftabellen", Path(a.ziel)))
        elif a.runde == 5:
            lauf(Path(a.ziel), os.environ.get("SUCHE_SCHLUESSEL", ""), a.abfragen, a.seiten, abfragen=ABFRAGEN5, startseiten=[])
        elif a.runde == 4:                     # Verweise der Fundseiten abarbeiten (Tiefe 1)
            v = verweise_laden(vp)
            offen = [u for u, r in v.items() if not r.get("gelesen")]
            lauf(Path(a.ziel), "", 0, a.seiten, abfragen=[], startseiten=[], zusatz_urls=offen[: a.seiten])
            for u in offen[: a.seiten]:
                v[u]["gelesen"] = dt.date.today().isoformat()
            verweise_speichern(vp, v)
        elif a.runde == 2:
            lauf(Path(a.ziel), os.environ.get("SUCHE_SCHLUESSEL", ""), a.abfragen, a.seiten, abfragen=ABFRAGEN2, startseiten=[])
        else:
            lauf(Path(a.ziel), os.environ.get("SUCHE_SCHLUESSEL", ""), a.abfragen, a.seiten)
