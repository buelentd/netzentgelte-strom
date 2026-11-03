"""FCR-Leistungspreise (Regelleistungsmarkt, Ergebnisse je Tag) von regelleistung.net.

Schnittstelle: https://www.regelleistung.net/apps/crds/api/v2/tenders/results/aggregated?productType=FCR&market=CAPACITY
               &exportFormat=xlsx&deliveryDate=JJJJ-MM-TT
Modus test: drei Tage, Tabelle im Protokoll zeigen (Aufbau prüfen). Modus jahr: 365 Tage (höchstens 1 Abruf je Sekunde),
Ergebnis daten/fcr_je_tag.json: {Datum: {Block: Grenzpreis}} und Jahresmittel.
"""
import io
import json
import statistics
import sys
import time
import urllib.request
from datetime import date, timedelta
from pathlib import Path

import openpyxl

HIER = Path(__file__).parent
URL = ("https://www.regelleistung.net/apps/crds/api/v2/tenders/results/aggregated?&productType=%s&market=CAPACITY"
       "&exportFormat=xlsx&deliveryDate=%s")


def tag(d, produkt="FCR"):
    with urllib.request.urlopen(urllib.request.Request(URL % (produkt, d), headers={"User-Agent": "netzentgelte-strom"}), timeout=60) as r:
        return openpyxl.load_workbook(io.BytesIO(r.read()), data_only=True)


def zeilen(wb):
    out = []
    for ws in wb.worksheets:
        out.append((ws.title, [[c for c in row] for row in ws.iter_rows(values_only=True)]))
    return out


def test():
    for d in ("2026-11-02", "2026-10-02", "2026-06-15"):
        try:
            wb = tag(d)
        except Exception as e:
            print(d, "Fehler", type(e).__name__, str(e)[:150])
            continue
        for name, rows in zeilen(wb):
            print(f"--- {d} Blatt {name!r}, {len(rows)} Zeilen")
            for r in rows[:14]:
                print("   ", r)
        time.sleep(1.1)


def jahr():
    bis = date.today() - timedelta(days=1)
    ergebnis, luecken = {}, []
    for i in range(365):
        d = bis - timedelta(days=i)
        try:
            ergebnis[str(d)] = [r for _, r in zeilen(tag(d))][0]
        except Exception as e:
            luecken.append(str(d))
        time.sleep(1.1)
    (HIER / "fcr_roh.json").write_text(json.dumps({"tage": ergebnis, "luecken": luecken}, ensure_ascii=False, default=str))
    print(len(ergebnis), "Tage geladen,", len(luecken), "Lücken")


def afrr():
    """aFRR-Kapazitätsergebnisse (Leistungspreis) für 365 Tage, Rohzeilen nach daten/afrr_roh.json.
    Zeigt zuerst Aufbau (Kopfzeile, erste Zeilen) im Protokoll; schlägt der erste Abruf fehl, bricht der Lauf ab."""
    bis = date.today() - timedelta(days=1)
    wb = tag(bis, "aFRR")
    for name, rows in zeilen(wb):
        print(f"--- {bis} Blatt {name!r}, {len(rows)} Zeilen")
        for r in rows[:14]:
            print("   ", r)
    ergebnis, luecken = {}, []
    for i in range(365):
        d = bis - timedelta(days=i)
        try:
            ergebnis[str(d)] = [r for _, r in zeilen(tag(d, "aFRR"))][0]
        except Exception as e:
            luecken.append(str(d))
        time.sleep(1.1)
    (HIER / "afrr_roh.json").write_text(json.dumps({"tage": ergebnis, "luecken": luecken}, ensure_ascii=False, default=str))
    print(len(ergebnis), "Tage geladen,", len(luecken), "Lücken")


if __name__ == "__main__":
    {"test": test, "jahr": jahr, "afrr": afrr}[sys.argv[1] if len(sys.argv) > 1 else "test"]()
