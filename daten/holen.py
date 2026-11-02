"""Holt Börsenpreise (Energy-Charts) und Solarertrag (PVGIS) für den Rechner. Läuft über GitHub (Internet nötig).

Ausgabe:
  daten/boerse_<von>_<bis>.json   stündliche Day-Ahead-Preise DE-LU in ct/kWh: {"start": "...", "ct_kwh": [...]}
  daten/solar_je_land.json        je Bundesland und Monat ein mittlerer Tagesverlauf (24 Werte) in kWh je kWp und Stunde
"""
import json
import os
import statistics
import sys
import time
import xml.etree.ElementTree as ET
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


def boerse_entsoe(bis: date):
    """Day-Ahead-Preise DE-LU von der ENTSO-E Transparenzplattform (Originalquelle), Abgleich mit Energy-Charts.
    Schlüssel: Umgebungsvariable ENTSOE_TOKEN; ohne Schlüssel wird übersprungen."""
    token = os.environ.get("ENTSOE_TOKEN", "")
    if not token:
        print("ENTSO-E übersprungen: ENTSOE_TOKEN nicht gesetzt")
        return
    von = bis - timedelta(days=364)
    url = ("https://web-api.tp.entsoe.eu/api?documentType=A44&in_Domain=10Y1001A1001A82H&out_Domain=10Y1001A1001A82H"
           f"&periodStart={von:%Y%m%d}0000&periodEnd={bis + timedelta(days=1):%Y%m%d}0000&securityToken={token}")
    for i in range(3):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                xml = r.read()
            break
        except Exception as e:
            print(f"  ENTSO-E Fehler {type(e).__name__} (Versuch {i + 1})")
            time.sleep(2 ** (i + 1))
    else:
        print("ENTSO-E nicht erreichbar")
        return
    punkte = {}                                                    # Unix-Sekunden (UTC) → ct/kWh
    kuerzel = lambda t: t.rsplit("}", 1)[-1]
    for ts in ET.fromstring(xml).iter():
        if kuerzel(ts.tag) != "TimeSeries":
            continue
        for per in [x for x in ts.iter() if kuerzel(x.tag) == "Period"]:
            start = res = None
            for x in per.iter():
                if kuerzel(x.tag) == "start" and start is None:
                    start = x.text
                if kuerzel(x.tag) == "resolution":
                    res = x.text
            from datetime import datetime, timezone
            t0 = datetime.strptime(start, "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc).timestamp()
            schritt = {"PT15M": 900, "PT30M": 1800, "PT60M": 3600}[res]
            for pt in [x for x in per if kuerzel(x.tag) == "Point"]:
                pos = int([c.text for c in pt if kuerzel(c.tag) == "position"][0])
                pr = float([c.text for c in pt if kuerzel(c.tag) == "price.amount"][0])
                for k in range(schritt // 900):                    # auf Viertelstunden ausdehnen
                    punkte[int(t0 + (pos - 1) * schritt + k * 900)] = round(pr / 10, 3)
    ec = next(HIER.glob("boerse_20*.json"), None)
    if ec and punkte:
        d = json.loads(ec.read_text())
        diffs = [abs(punkte[d["start"] + i * d["schritt_s"]] - v) for i, v in enumerate(d["ct_kwh"])
                 if v is not None and (d["start"] + i * d["schritt_s"]) in punkte]
        print(f"ENTSO-E: {len(punkte)} Werte; Abgleich mit Energy-Charts auf {len(diffs)} Zeitpunkten: "
              f"mittlere Abweichung {statistics.mean(diffs):.4f} ct/kWh, größte {max(diffs):.3f}")
    ziel = HIER / f"boerse_entsoe_{von}_{bis}.json"
    zeiten = sorted(punkte)
    ziel.write_text(json.dumps({"start": zeiten[0], "schritt_s": 900, "quelle": "ENTSO-E Transparenzplattform, Day-Ahead DE-LU",
                                "ct_kwh": [punkte.get(t) for t in range(zeiten[0], zeiten[-1] + 900, 900)]}, separators=(",", ":")))
    print(f"ENTSO-E gespeichert: {ziel.name}")


def regelenergie(bis: date):
    """Preise für Regelenergie-Vorhaltung (Leistungspreis) von ENTSO-E: FCR (A95), aFRR (A96). Nur Diagnose und Mittelwerte:
    welche Elemente zurückkommen, wie viele Punkte, Mittelwert je Punkt. Schlüssel: ENTSOE_TOKEN."""
    token = os.environ.get("ENTSOE_TOKEN", "")
    if not token:
        print("Regelenergie übersprungen: ENTSOE_TOKEN nicht gesetzt")
        return
    von = bis - timedelta(days=364)
    erg = {"quelle": "ENTSO-E Transparenzplattform, Prices of procured balancing capacity (A89), Regelzone DE-LU",
           "zeitraum": f"{von}..{bis}"}
    kuerzel = lambda t: t.rsplit("}", 1)[-1]
    for name, typ in (("FCR", "A95"), ("aFRR", "A96")):
        for richtung in ([None] if name == "FCR" else ["A01", "A02"]):
            url = ("https://web-api.tp.entsoe.eu/api?documentType=A89&businessType=" + typ + "&controlArea_Domain=10Y1001A1001A82H"
                   "&type_MarketAgreement.Type=A01" + (f"&flowDirection.direction={richtung}" if richtung else "")
                   + f"&periodStart={von:%Y%m%d}0000&periodEnd={bis + timedelta(days=1):%Y%m%d}0000&securityToken={token}")
            marke = name + (f" {richtung}" if richtung else "")
            try:
                with urllib.request.urlopen(url, timeout=120) as r:
                    xml = r.read()
            except Exception as e:
                detail = ""
                try:
                    detail = e.read().decode("utf-8", "ignore")[:300]
                except Exception:
                    pass
                print(f"{marke}: Fehler {type(e).__name__} {detail}")
                continue
            wurzel = ET.fromstring(xml)
            tags = sorted({kuerzel(x.tag) for x in wurzel.iter()})
            preise = [float(x.text) for x in wurzel.iter() if kuerzel(x.tag) in ("procurement_Price.amount", "price.amount") and x.text]
            aufl = sorted({x.text for x in wurzel.iter() if kuerzel(x.tag) == "resolution"})
            print(f"{marke}: {len(preise)} Preise, Auflösung {aufl}, Elemente {tags[:40]}")
            if preise:
                print(f"  Mittel {statistics.mean(preise):.2f}, min {min(preise):.2f}, max {max(preise):.2f} (Einheit laut Dokument, vermutlich EUR je MW und Block)")
                erg[marke] = {"punkte": len(preise), "mittel": round(statistics.mean(preise), 3), "min": min(preise), "max": max(preise),
                              "aufloesung": aufl}
            else:
                print("  Antwort ohne Preise:", xml[:400].decode("utf-8", "ignore"))
    (HIER / "regelenergie.json").write_text(json.dumps(erg, ensure_ascii=False, indent=1))


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
    heute = date.today() - timedelta(days=2)
    boerse(heute)
    boerse_entsoe(heute)
    regelenergie(heute)
    solar()
