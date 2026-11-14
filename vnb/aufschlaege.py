"""Strompreis-Aufschläge im Netz sammeln: Vertriebsmarge, Risikoaufschlag, Beschaffung und Vertrieb in ct/kWh.

Zweck: belegte Werte statt der Annahme "Aufschlag des Stromanbieters 2,5 ct" im Rechner. Jeder Fund trägt URL, Abrufdatum,
Textauszug, Wert von/bis in ct/kWh, Stichwort (Aufschlag, Marge, Beschaffung ...), Kundengruppe und Quellenart.
Nichts wird geschätzt. Regeln (robots.txt, 1 Anfrage/s je Domain, Timeout 30 s) wie bei den Speicherpreisen; die Funde sind
Kandidaten ("ungeprüft"), geprüft wird am Original.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import re
import time
import urllib.parse
from pathlib import Path

from .speicherpreise import Holer, art_der_quelle, seitentext

SPALTEN = ["id", "abruf_datum", "url", "domain", "titel", "art_quelle", "wert_von_ct_kwh", "wert_bis_ct_kwh", "stichwort",
           "kundengruppe", "netto_brutto", "veroeffentlicht", "kontext", "status", "pruefnotiz"]
WERT_MIN, WERT_MAX = 0.1, 40.0               # ct/kWh
ABFRAGEN = [
    "Vertriebsmarge Gewerbekunden Strom ct/kWh RLM Aufschlag",
    "Aufschlag Stromlieferant Gewerbe Marge ct/kWh Mittelstand Ausschreibung",
    "BDEW Strompreisanalyse 2026 Beschaffung und Vertrieb ct/kWh",
    "Risikoaufschlag Lastgang Strom Ausschreibung ct/kWh",
    "Strombeschaffung Gewerbe Vertriebskosten ct/kWh Spotmarkt Tranchen Aufschlag",
    "Stromliefervertrag Gewerbe Börsenpreis plus Aufschlag ct/kWh Spotprodukt",
    "dynamischer Stromtarif Gewerbe Aufschlag ct/kWh Beschaffungskosten Vertrieb",
    "Energy Brainpool Strompreis Gewerbe Vertriebsaufschlag",
    "Strompreis Zusammensetzung Gewerbe 2026 Energiebeschaffung Vertrieb Marge ct/kWh",
    "Direktvermarktung Aufschlag ct/kWh Marktwert Abzug Gebühr",
]
STICHWORT = re.compile(r"(vertriebs\w*|marge\w*|risikoaufschlag|risiko\w*|aufschlag|zuschlag|beschaffung\w*|handling\w*|servicegeb\w*|bilanzkreis\w*|"
                       r"abwicklung\w*|grundpreis|arbeitspreis)", re.I)
WERT = re.compile(r"(?P<a>\d{1,2}(?:[.,]\d{1,3})?)\s*(?:(?:–|-|—|bis)\s*(?P<b>\d{1,2}(?:[.,]\d{1,3})?)\s*)?(?:ct|cent)\s*(?:/|pro|je)\s*kwh", re.I)
GRUPPE = [("Haushalt", r"haushalt|privatkund"), ("RLM/Gewerbe", r"rlm|registrierend|gewerbe|mittelstand|industri|ausschreib|sonderverträg|sondervertrag"),
          ("SLP", r"\bslp\b|standardlastprofil")]


def _z(s: str) -> float:
    return float(s.replace(",", "."))


def funde_aus_text(text: str, url: str, titel: str = "", veroeffentlicht: str = "", abruf: str | None = None) -> list[dict]:
    domain = urllib.parse.urlparse(url).netloc.lower().removeprefix("www.")
    abruf = abruf or dt.date.today().isoformat()
    art = art_der_quelle(domain, text)
    out, gesehen = [], set()
    for m in WERT.finditer(text):
        a = _z(m.group("a"))
        b = _z(m.group("b")) if m.group("b") else a
        if a > b:
            a, b = b, a
        if not (WERT_MIN <= a <= WERT_MAX and WERT_MIN <= b <= WERT_MAX):
            continue
        davor = text[max(0, m.start() - 160):m.start()]
        kw = STICHWORT.findall(davor) or STICHWORT.findall(text[m.end():m.end() + 40])    # nächstes Stichwort vor dem Wert zählt zuerst
        if not kw:                                     # nur Angaben mit Bezug zu Aufschlag, Marge, Vertrieb, Beschaffung
            continue
        von, bis = max(0, m.start() - 170), min(len(text), m.end() + 170)
        ctx = re.sub(r"\s+", " ", text[von:bis]).strip()
        nah = ctx.lower()
        key = (round(a, 2), round(b, 2), ctx[:80])
        if key in gesehen:
            continue
        gesehen.add(key)
        grp = next((n for n, rx in GRUPPE if re.search(rx, nah)), "unklar")
        nb = "netto" if re.search(r"netto|zzgl\.?\s*(?:mwst|ust)|ohne\s*(?:mwst|ust)", nah) else "brutto" if re.search(
            r"brutto|inkl\.?\s*(?:mwst|ust)", nah) else "unklar"
        fid = hashlib.sha1(f"{url}|{a}|{b}|{ctx[:60]}".encode()).hexdigest()[:12]
        out.append({"id": fid, "abruf_datum": abruf, "url": url, "domain": domain, "titel": titel, "art_quelle": art,
                    "wert_von_ct_kwh": f"{a:g}".replace(".", ","), "wert_bis_ct_kwh": f"{b:g}".replace(".", ","),
                    "stichwort": kw[-1].lower(), "kundengruppe": grp, "netto_brutto": nb, "veroeffentlicht": veroeffentlicht,
                    "kontext": ctx, "status": "ungeprüft", "pruefnotiz": ""})
    return out


def laden(pfad: Path) -> dict[str, dict]:
    if not pfad.exists():
        return {}
    with open(pfad, encoding="utf-8-sig", newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f, delimiter=";")}


def speichern(pfad: Path, zeilen: dict[str, dict]):
    pfad.parent.mkdir(parents=True, exist_ok=True)
    with open(pfad, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SPALTEN, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in sorted(zeilen.values(), key=lambda r: (r["domain"], r["url"], r["wert_von_ct_kwh"])):
            w.writerow(r)


def lauf(ziel: Path, schluessel: str = "", max_abfragen: int = 10, max_seiten_gesamt: int = 120, holer: Holer | None = None,
         suche=None, log=print) -> dict:
    from .speicherpreise import websuche
    holer = holer or Holer(log=log)
    suche = suche or (lambda q: websuche(schluessel, q) if schluessel else [])
    vorhanden = laden(ziel)
    urls = []
    for q in ABFRAGEN[:max_abfragen]:
        urls += suche(q)
        time.sleep(1.1 if schluessel else 0)
    gesehen, neu, seiten = set(), 0, 0
    for u in urls:
        u = u.split("#")[0]
        if u in gesehen or seiten >= max_seiten_gesamt:
            continue
        gesehen.add(u)
        if re.search(r"\.pdf$", urllib.parse.urlparse(u).path, re.I):
            text = holer.holen_pdf(u)
            titel, datum = ((text or "").strip().splitlines() or [""])[0][:160], ""
        else:
            roh = holer.holen(u)
            text, titel, datum = seitentext(roh) if roh else (None, "", "")
        if not text:
            continue
        seiten += 1
        for f in funde_aus_text(text, u, titel, datum):
            if f["id"] not in vorhanden:
                vorhanden[f["id"]] = f
                neu += 1
    speichern(ziel, vorhanden)
    log(f"Aufschläge: {seiten} Seiten gelesen, {neu} neue Funde, {len(vorhanden)} insgesamt")
    return {"seiten": seiten, "neu": neu, "gesamt": len(vorhanden)}


if __name__ == "__main__":
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--ziel", default="ergebnis/strompreis_aufschlaege_funde.csv")
    ap.add_argument("--abfragen", type=int, default=10)
    ap.add_argument("--seiten", type=int, default=120)
    a = ap.parse_args()
    lauf(Path(a.ziel), os.environ.get("SUCHE_SCHLUESSEL", ""), a.abfragen, a.seiten)
