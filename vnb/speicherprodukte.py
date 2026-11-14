"""Produkttabelle für Gewerbe- und Großspeicher (eine Zeile je System), nach dem Muster der pv-magazine-Marktübersicht.

Spalten wie in der Quelle: Hersteller, Produkt, Zellchemie, Kapazität, Leistung, Wirkungsgrad, Zyklen, Preis, Fläche, Volumen,
Datenblatt. Dazu die Herkunft jeder Zeile (Quelle, Abrufdatum) und der Prüfstatus. Was die Quelle nicht angibt, bleibt leer:
nichts wird geschätzt. Der Preis steht so, wie die Quelle ihn nennt; ob netto oder brutto und was er umfasst, ist eine eigene Spalte
und bleibt "unklar", bis es am Original oder an der Kopfzeile der Quelle geprüft ist.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import re
from pathlib import Path

SPALTEN = ["id", "hersteller", "produkt", "zellchemie", "kapazitaet_kwh", "leistung_kw", "wirkungsgrad_prozent", "zyklen",
           "preis_eur_kwh", "preis_netto_brutto", "preis_umfang", "flaeche_m2", "volumen_m3", "datenblatt_url",
           "quelle", "quelle_url", "abruf_datum", "status", "pruefnotiz"]
LEER = {"", "—", "-", "–", "n/a", "k.a.", "k. a."}
RUMPF = re.compile(r"\s*(?:PDF)?\s*(?:Bearbeiten)?\s*[✕xX×]?\s*$")


def _zahl(s: str) -> str:
    s = (s or "").strip()
    if s in LEER:
        return ""
    s = s.replace("\xa0", "").replace(" ", "")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        v = float(s)
    except ValueError:
        return ""
    return f"{v:g}".replace(".", ",")


def zeile_lesen(zeile: str, quelle: str = "pv magazine Marktübersicht", quelle_url: str = "", abruf: str | None = None,
                notiz: str = "") -> dict | None:
    """Eine eingefügte Tabellenzeile (Tabulator-getrennt): Hersteller, Produkt, Zellchemie, kWh, kW, Wirkungsgrad, Zyklen, Preis,
    Fläche, Volumen, [PDF] [Bearbeiten]. Die Hersteller-Spalte darf Zusätze enthalten ("SCU Sicon Chat Union")."""
    teile = [t.strip() for t in zeile.rstrip("\n").split("\t")]
    teile = [t for t in teile if not RUMPF.fullmatch(t) or t.strip() in ("—", "-")]       # Spalten "PDF", "Bearbeiten ✕" entfernen
    pdf = "PDF" in zeile
    if len(teile) < 8:
        return None
    # erste Spalte kann "SCU" (Hersteller) sein oder "SCU Sicon Chat Union" (Hersteller + Zusatz); Produkt steht in der zweiten
    hersteller, produkt, chemie = teile[0], teile[1], teile[2]
    if not re.fullmatch(r"[A-Za-z]{2,6}", chemie):         # Spalte 3 ist keine Zellchemie: Zeile passt nicht ins Muster
        return None
    werte = [_zahl(x) for x in teile[3:10]] + [""] * 7
    kwh, kw, wg, zyk, preis, flaeche, vol = werte[:7]
    if not kwh:
        return None
    fid = hashlib.sha1(f"{hersteller}|{produkt}|{kwh}|{quelle}".encode()).hexdigest()[:12]
    return {"id": fid, "hersteller": hersteller, "produkt": produkt, "zellchemie": chemie, "kapazitaet_kwh": kwh, "leistung_kw": kw,
            "wirkungsgrad_prozent": wg, "zyklen": zyk, "preis_eur_kwh": preis, "preis_netto_brutto": "unklar",
            "preis_umfang": "unklar", "flaeche_m2": flaeche, "volumen_m3": vol,
            "datenblatt_url": "Datenblatt-Link vorhanden (Quelle verlinkt PDF)" if pdf else "", "quelle": quelle,
            "quelle_url": quelle_url, "abruf_datum": abruf or dt.date.today().isoformat(), "status": "ungeprüft",
            "pruefnotiz": notiz}


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
        for r in sorted(zeilen.values(), key=lambda r: (r["hersteller"], r["produkt"])):
            w.writerow(r)


def importieren(text: str, pfad: Path, **kw) -> dict:
    """Eingefügte Tabellenzeilen übernehmen; bestehende Zeilen (gleiche Kennung) bleiben unverändert."""
    vorhanden = laden(pfad)
    neu = uebersprungen = 0
    for z in text.splitlines():
        if not z.strip():
            continue
        r = zeile_lesen(z, **kw)
        if r is None:
            uebersprungen += 1
            continue
        if r["id"] not in vorhanden:
            vorhanden[r["id"]] = r
            neu += 1
    speichern(pfad, vorhanden)
    return {"neu": neu, "uebersprungen": uebersprungen, "gesamt": len(vorhanden)}


if __name__ == "__main__":
    import argparse
    import sys
    ap = argparse.ArgumentParser(description="Tabellenzeilen (Tabulator-getrennt) aus Datei oder stdin in die Produkttabelle übernehmen")
    ap.add_argument("datei", nargs="?")
    ap.add_argument("--ziel", default="ergebnis/speicherprodukte.csv")
    ap.add_argument("--quelle", default="pv magazine Marktübersicht")
    ap.add_argument("--quelle-url", default="")
    ap.add_argument("--notiz", default="")
    a = ap.parse_args()
    text = Path(a.datei).read_text(encoding="utf-8") if a.datei else sys.stdin.read()
    print(importieren(text, Path(a.ziel), quelle=a.quelle, quelle_url=a.quelle_url, notiz=a.notiz))
