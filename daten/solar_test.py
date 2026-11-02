"""Testet die Google Solar API (Building Insights) mit einigen Adressen: Abdeckung und gelieferte Werte.

Adressen → Koordinaten über OpenStreetMap (Nominatim, höchstens eine Anfrage pro Sekunde), dann Dachdaten von Google.
Die Ergebnisse stehen nur im Protokoll des Laufs und werden nicht gespeichert (Nutzungsbedingungen von Google).
Schlüssel: Umgebungsvariable SOLAR_SCHLUESSEL (GitHub-Secret), nie im Code oder Chat.
"""
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HIER = Path(__file__).parent.parent
SCHLUESSEL = os.environ.get("SOLAR_SCHLUESSEL", "")


def holen(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "netzentgelte-strom-test"}), timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def koordinaten(adresse):
    d = holen("https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=de&q=" + urllib.parse.quote(adresse))
    time.sleep(1.1)
    return (float(d[0]["lat"]), float(d[0]["lon"])) if d else None


def dach(lat, lon):
    url = ("https://solar.googleapis.com/v1/buildingInsights:findClosest?location.latitude=%s&location.longitude=%s"
           "&requiredQuality=LOW&key=%s" % (lat, lon, SCHLUESSEL))
    try:
        return holen(url)
    except urllib.error.HTTPError as e:
        return {"fehler": f"HTTP {e.code}: {e.read().decode('utf-8', 'ignore')[:200]}"}


if not SCHLUESSEL:
    sys.exit("SOLAR_SCHLUESSEL ist leer (Repository-Secret anlegen)")
ok = 0
adressen = [z["adresse"] for z in csv.DictReader(open(HIER / "lauf" / "solar_test_adressen.csv", encoding="utf-8"))]
for a in adressen:
    k = koordinaten(a)
    if not k:
        print(f"{a}: Adresse nicht gefunden")
        continue
    d = dach(*k)
    if "fehler" in d:
        print(f"{a}: {d['fehler']}")
        continue
    sp = d.get("solarPotential", {})
    konf = sp.get("solarPanelConfigs", [])
    gross = konf[-1] if konf else {}
    ok += 1
    print(f"{a}: Qualität {d.get('imageryQuality')}, Bilddatum {d.get('imageryDate')}, Dachfläche gesamt "
          f"{sp.get('wholeRoofStats', {}).get('areaMeters2', 0):.0f} m², nutzbar für Module {sp.get('maxArrayAreaMeters2', 0):.0f} m², "
          f"bis {sp.get('maxArrayPanelsCount')} Module à {sp.get('panelCapacityWatts')} W, Ertrag größte Anlage "
          f"{gross.get('yearlyEnergyDcKwh', 0):.0f} kWh/Jahr")
    time.sleep(0.3)
print(f"{ok} von {len(adressen)} Adressen mit Dachdaten")
