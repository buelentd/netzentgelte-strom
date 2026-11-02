"""Holt Börsenpreise (Energy-Charts) und Solarertrag (PVGIS) für den Rechner. Läuft über GitHub (Internet nötig).

Ausgabe:
  daten/boerse_<von>_<bis>.json   stündliche Day-Ahead-Preise DE-LU in ct/kWh: {"start": "...", "ct_kwh": [...]}
  daten/solar_je_land.json        je Bundesland und Monat ein mittlerer Tagesverlauf (24 Werte) in kWh je kWp und Stunde
"""
import json
import statistics
import sys
import time
import urllib.request
from datetime import date, timedelta
from pathlib import Path

HIER = Path(__file__).parent
LAND = {  # Landeshauptstadt als Stützpunkt
    "Baden-Württemberg": (48.78, 9.18), "Bayern": (48.14, 11.58), "Berlin": (52.52, 13.40), "Brandenburg": (52.40, 13.07),
    "Bremen": (53.08, 8.80), "Hamburg": (53.55, 10.00), "Hessen": (50.08, 8.24), "Mecklenburg-Vorpommern": (53.63, 11.41),
    "Niedersachsen": (52.37, 9.74), "Nordrhein-Westfalen": (51.23, 6.78), "Rheinland-Pfalz": (49.99, 8.27),
    "Saarland": (49.24, 7.00), "Sachsen": (51.05, 13.74), "Sachsen-Anhalt": (52.13, 11.63),
    "Schleswig-Holstein": (54.32, 10.14), "Thüringen": (50.98, 11.03),
}


def abrufen(url, versuche=4):
    for i in range(versuche):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "netzentgelte-strom"}), timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            print(f"  Fehler {type(e).__name__}: {str(e)[:80]} (Versuch {i + 1})")
            time.sleep(2 ** (i + 1))
    raise SystemExit(f"nicht erreichbar: {url}")


def boerse(bis: date):
    von = bis - timedelta(days=364)
    d = abrufen(f"https://api.energy-charts.info/price?bzn=DE-LU&start={von}&end={bis}")
    preise = [None if p is None else round(p / 10, 3) for p in d["price"]]      # €/MWh → ct/kWh
    ziel = HIER / f"boerse_{von}_{bis}.json"
    ziel.write_text(json.dumps({"start": d["unix_seconds"][0], "schritt_s": d["unix_seconds"][1] - d["unix_seconds"][0],
                                "quelle": "Energy-Charts (Fraunhofer ISE), Day-Ahead DE-LU", "ct_kwh": preise}, separators=(",", ":")))
    ok = [p for p in preise if p is not None]
    print(f"Börse {von}..{bis}: {len(ok)} Werte, Mittel {statistics.mean(ok):.2f} ct/kWh, min {min(ok):.2f}, max {max(ok):.2f}")


def solar():
    out = {}
    for land, (lat, lon) in LAND.items():
        d = abrufen(f"https://re.jrc.ec.europa.eu/api/v5_3/seriescalc?lat={lat}&lon={lon}&pvcalculation=1&peakpower=1&loss=14&angle=35&aspect=0"
                    f"&startyear=2020&endyear=2020&outputformat=json")
        monat = {m: [[] for _ in range(24)] for m in range(1, 13)}
        for z in d["outputs"]["hourly"]:
            t = z["time"]                                  # 20200115:1210
            monat[int(t[4:6])][int(t[9:11])].append(z["P"] / 1000)      # W je kWp → kWh je kWp und Stunde
        out[land] = {m: [round(statistics.mean(h) if h else 0, 4) for h in monat[m]] for m in monat}
        jahr = sum(sum(out[land][m]) * 30.4 for m in out[land])
        print(f"Solar {land}: etwa {jahr:.0f} kWh je kWp und Jahr")
        time.sleep(1)
    (HIER / "solar_je_land.json").write_text(json.dumps({"quelle": "PVGIS 5.3 (Europäische Kommission), Jahr 2020, 35 Grad Süd, 14 % Verluste",
                                                         "land": out}, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    boerse(date.today() - timedelta(days=2))
    solar()
