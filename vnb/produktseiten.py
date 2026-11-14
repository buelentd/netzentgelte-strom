"""Speicherpreise Runde 7: Produktseiten von Händlern (Gesamtpreis + Kapazität -> €/kWh).

Die Runden 1-6 suchen Preise, die schon "€/kWh" im Text haben. Shops nennen aber Gesamtpreis und Kapazität getrennt
(z. B. 31.571 € und 41,66 kWh). Hier wird beides aus der Produktseite gelesen und gerechnet. Alles ist "ungeprüft",
Netto/Brutto und Lieferumfang werden nur als Hinweis aus dem Text übernommen, nie angenommen.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import re
import time
import urllib.parse
from pathlib import Path

from .speicherpreise import Holer, PREIS_MIN, PREIS_MAX, seitentext, websuche

SPALTEN = ["id", "abruf_datum", "url", "domain", "titel", "preis_eur", "kapazitaet_kwh", "eur_pro_kwh", "netto_brutto_hinweis",
           "umfang_hinweis", "quelle_preis", "status", "pruefnotiz"]
KAP_MIN, KAP_MAX = 30.0, 6000.0          # Gewerbe: ab 30 kWh; darüber Großspeicher/Container
# Händler-Kategorieseiten für Gewerbespeicher (robots.txt wird im Holer geprüft)
KATEGORIEN = [
    "https://www.aceflex.de/shop/einzelkomponenten/gewerbespeicher/",
    "https://tela.at/shop/photovoltaik-gesamtubersicht/speichersysteme/gewerbespeicher/",
    "https://shop.krannich-solar.com/solarspeicher/gewerbespeicher",
    "https://www.solartraders.com/de/products/speicher/batterie-system",
    "https://shop.solar-kit.eu/en/products/energy-storage",
    "https://www.memodo.de/gewerbespeicher/",
]
HERSTELLER = ["Pixii", "Sigenergy", "Dyness", "Hithium", "Fox ESS", "Sunwoda", "Huawei LUNA2000", "BYD", "Sungrow", "Hoymiles", "Tesvolt",
              "Fenecon", "Kehua", "Growatt", "GoodWe", "Deye", "Victron", "Kostal", "SMA", "Intilion"]
# weitere Marken (idealo-Herstellerfilter Batteriespeicher sowie Heizungs-/Systemanbieter wie Daikin, Viessmann; Wärmespeicher bewusst nicht)
HERSTELLER_WEITER = ["PYTES", "SofarSolar", "Felicity Solar", "SolarEdge", "Pramac", "VARTA", "G2 Energy Systems", "Daikin", "Viessmann", "Vaillant",
                     "Stiebel Eltron", "Senec", "E3/DC", "sonnen", "Tesla Megapack", "Enphase", "Solax", "Anker Solix", "EcoFlow", "Zendure",
                     "LG Energy Solution", "Samsung SDI", "Schneider Electric", "ABB", "Siemens", "Wärtsilä", "CATL", "EVE Energy", "Jinko ESS", "Trina Storage",
                     "Alpha ESS", "Solarwatt", "Wattkraft", "Kyocera", "Panasonic", "Mitsubishi Electric"]
ABFRAGEN = ([f"{h} Gewerbespeicher {k} kWh kaufen Preis" for h in HERSTELLER for k in (100, 215)]
            + [f"{h} Gewerbespeicher Industriespeicher kWh Preis kaufen" for h in HERSTELLER_WEITER])
LINK_KAP = re.compile(r"\d{2,4}[-_ ,.]?\d*\s*[-_ ]?kwh", re.I)
EURO = re.compile(r"(\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?|\d{4,6}(?:,\d{1,2})?)\s*(?:€|eur\b)", re.I)
KAPAZ = re.compile(r"(\d{2,4}(?:[.,]\d{1,2})?)\s*kwh", re.I)
NUTZBAR = re.compile(r"(\d{2,4}(?:[.,]\d{1,2})?)\s*kwh\s*nutzbar|nutzbar\w*\D{0,20}(\d{2,4}(?:[.,]\d{1,2})?)\s*kwh", re.I)


def _z(s: str) -> float:
    s = s.strip()
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    return float(s)


def _json_preis(roh: str) -> float | None:
    """Preis aus JSON-LD (offers.price) oder Meta product:price:amount."""
    for m in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', roh, re.S | re.I):
        try:
            d = json.loads(m.group(1))
        except Exception:
            continue
        st = [d]
        while st:
            x = st.pop()
            if isinstance(x, list):
                st += x
            elif isinstance(x, dict):
                o = x.get("offers")
                for oo in (o if isinstance(o, list) else [o]):
                    if isinstance(oo, dict):
                        p = oo.get("price") or oo.get("lowPrice")
                        try:
                            if p and float(p) > 0:
                                return float(p)
                        except (TypeError, ValueError):
                            pass
                st += [v for v in x.values() if isinstance(v, (dict, list))]
    m = re.search(r'product:price:amount"[^>]*content="([\d.,]+)"|content="([\d.,]+)"[^>]*product:price:amount', roh)
    if m:
        try:
            return _z(m.group(1) or m.group(2))
        except ValueError:
            pass
    return None


def produkt_aus_html(roh: str, url: str, abruf: str | None = None) -> dict | None:
    text, titel, _ = seitentext(roh)
    kopf = (titel + " " + " ".join(text.splitlines()[:40]))
    n = NUTZBAR.search(kopf) or NUTZBAR.search(text[:6000])
    k = None
    if n:
        k = _z(n.group(1) or n.group(2))
    else:
        for m in KAPAZ.finditer(titel):
            k = _z(m.group(1))
            break
        if k is None:
            m = KAPAZ.search(kopf)
            k = _z(m.group(1)) if m else None
    if k is None or not (KAP_MIN <= k <= KAP_MAX):
        return None
    quelle = "json-ld"
    p = _json_preis(roh)
    if p is None:
        quelle = "text"
        werte = [_z(m.group(1)) for m in EURO.finditer("\n".join(text.splitlines()[:80]))]
        werte = [w for w in werte if w >= 3000]
        p = werte[0] if werte else None
    if p is None:
        return None
    ekwh = p / k
    if not (PREIS_MIN <= ekwh <= PREIS_MAX):
        return None
    t = text[:8000].lower()
    hinweis = []
    for muster, wort in ((r"0\s*%\s*mwst", "0 % MwSt. (Hinweis der Seite, nicht als netto belegt)"), (r"zzgl\.?\s*(?:gesetzl\.?\s*)?(?:mwst|ust)", "zzgl. MwSt."),
                         (r"inkl\.?\s*(?:gesetzl\.?\s*)?(?:mwst|ust)", "inkl. MwSt."), (r"\bnetto\b", "Text nennt netto"), (r"\bbrutto\b", "Text nennt brutto")):
        if re.search(muster, t):
            hinweis.append(wort)
    umfang = []
    for muster, wort in ((r"inkl\.?\s*(?:pcs|wechselrichter|elecod)|\d+\s*kw\s*wr\b", "PCS/Wechselrichter wohl enthalten"),
                         (r"ohne\s+(?:pcs|wechselrichter)|nur\s+batterie", "ohne PCS/Wechselrichter"), (r"ohne\s+montage", "ohne Montage"),
                         (r"inkl\.?\s*montage|schl[üu]sselfertig", "Montage/schlüsselfertig genannt"), (r"auf anfrage|preis anfragen", "Preis auf Anfrage")):
        if re.search(muster, t):
            umfang.append(wort)
    d = urllib.parse.urlparse(url).netloc.lower().removeprefix("www.")
    return {"id": hashlib.sha1(url.encode()).hexdigest()[:12], "abruf_datum": abruf or dt.date.today().isoformat(), "url": url, "domain": d,
            "titel": titel[:160], "preis_eur": f"{p:.2f}".replace(".", ","), "kapazitaet_kwh": f"{k:g}".replace(".", ","),
            "eur_pro_kwh": f"{ekwh:.2f}".replace(".", ","), "netto_brutto_hinweis": "; ".join(hinweis) or "unklar",
            "umfang_hinweis": "; ".join(umfang) or "unklar", "quelle_preis": quelle, "status": "ungeprüft",
            "pruefnotiz": "Kapazität aus Titel/Kopf der Seite; nutzbar vs. nominal nicht unterschieden, wenn nicht ausdrücklich genannt"}


def produktlinks(roh: str, url: str) -> list[str]:
    """Links einer Kategorieseite, die nach Produkt mit kWh-Angabe aussehen (nur gleiche Domain)."""
    eigen = urllib.parse.urlparse(url).netloc
    aus = []
    for m in re.finditer(r'<a\b[^>]*href="([^"#]+)"[^>]*>(.*?)</a>', roh, re.S | re.I):
        z = urllib.parse.urljoin(url, m.group(1))
        anker = re.sub(r"<[^>]+>|\s+", " ", m.group(2))
        if urllib.parse.urlparse(z).netloc == eigen and (LINK_KAP.search(z) or LINK_KAP.search(anker)) and z not in aus:
            aus.append(z)
    return aus


def laden(pfad: Path) -> dict[str, dict]:
    if not pfad.exists():
        return {}
    with open(pfad, encoding="utf-8-sig", newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f, delimiter=";")}


def speichern(pfad: Path, z: dict[str, dict]):
    pfad.parent.mkdir(parents=True, exist_ok=True)
    with open(pfad, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SPALTEN, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in sorted(z.values(), key=lambda r: (r["domain"], r["url"])):
            w.writerow(r)


def lauf(ziel: Path, schluessel: str = "", max_abfragen: int = 90, max_seiten: int = 300, holer: Holer | None = None, suche=None,
         kategorien: list[str] | None = None, abfragen: list[str] | None = None, log=print) -> dict:
    holer = holer or Holer(log=log)
    suche = suche or (lambda q: websuche(schluessel, q) if schluessel else [])
    vorhanden = laden(ziel)
    kandidaten: list[str] = []
    for k in (KATEGORIEN if kategorien is None else kategorien):
        roh = holer.holen(k)
        if roh:
            kandidaten += produktlinks(roh, k)
    for q in (ABFRAGEN if abfragen is None else abfragen)[:max_abfragen]:
        kandidaten += suche(q)
        time.sleep(1.1 if schluessel else 0)
    gesehen, neu, seiten = set(), 0, 0
    for u in kandidaten:
        u = u.split("#")[0]
        if u in gesehen or u.lower().endswith(".pdf") or seiten >= max_seiten:
            continue
        gesehen.add(u)
        roh = holer.holen(u)
        if roh is None:
            continue
        seiten += 1
        p = produkt_aus_html(roh, u)
        if p and p["id"] not in vorhanden:
            vorhanden[p["id"]] = p
            neu += 1
    speichern(ziel, vorhanden)
    from .speicherpreise import gesperrte_speichern
    gesperrte_speichern(ziel.parent / "speicherpreise_gesperrt.csv", holer)
    log(f"Produktseiten: {seiten} gelesen, {neu} neu, {len(vorhanden)} gesamt, {len(holer.gesperrt)} gesperrt")
    return {"seiten": seiten, "neu": neu, "gesamt": len(vorhanden)}


if __name__ == "__main__":
    import os
    lauf(Path("ergebnis/speicherpreise_produktfunde.csv"), os.environ.get("SUCHE_SCHLUESSEL", ""))
