"""Baut die Testseite (Nachbau der geführten Abschätzung von conplot.de) aus vorlage.html und den Ergebnissen.

Aufruf: python abschaetzung_testseite/bauen.py  →  abschaetzung_testseite/netzentgelt_abschaetzung.html
Veröffentlicht als Artifact: https://claude.ai/artifact/J8UnVGkS6kvUFdF2WFZMiL (mit dieser URL aktualisieren).
"""
import collections
import csv
import json
from pathlib import Path

HIER = Path(__file__).parent
ERG = HIER.parent / "ergebnis"


def de(v):
    v = (v or "").strip()
    return float(v.replace(".", "").replace(",", ".")) if v else None


import sys
sys.path.insert(0, str(HIER.parent))
from vnb.db import Db                                           # alle Werte kommen über die Zugriffsschicht (heute CSV)
db = Db()
nb = []
for d in db.alle():
    e = {"n": d["nr"], "bl": (d["bundesland"].split(" / ")[0] or "Bayern"), "name": d["name"], "ps": d["preisstand"],
         "sd": d["stand_datum"], "le": d["grenze_le"], "fehlt": d["fehlt"]}
    for k in ("slp", "ns", "msns", "ms", "hsms"):
        if d[k]:
            e[k] = d[k]                                         # fehlt ein Wert, fehlt der Schlüssel: Seite zeigt "Werte nicht vorhanden"
    if d["slp"] and d["ns"]:                                    # nutzbar für Gewerbe an der Niederspannung: SLP und NS reichen (MS, MS/NS nur zusätzlich)
        e["voll"] = 1
    if not d["geprueft"]:
        e["ug"] = 1                                             # Status nicht "ok": noch nicht am Dokument bestätigt
    if "teurer als" in d["hinweis"]:
        e["bad"] = 1
    if d["quelle_url"]:
        e["q"] = d["quelle_url"]
    nb.append(e)
plz = {p: [list(x) for x in v] for p, v in db.plz().items() if len(p) == 5 and p.isdigit()}    # ungültige Einträge aus VNBdigital (z. B. 7651NK) auslassen
hlzf = {}
for d in db.alle():
    h = d["hlzf"]
    if h:
        hlzf[d["nr"]] = {"f": {j.capitalize().replace("Fruehling", "Frühling"): v for j, v in h["fenster"].items()},
                         "s": h["schwelle"] or 30, "sh": "Dokument" if h["schwelle"] else "Standard (fachlich zu bestätigen)",
                         "m": h["mindestleistung"], "q": h["quelle_url"]}
# Börsenpreise (Viertelstunden → Stundenmittel, ct/kWh), Solarertrag je Bundesland, Lastprofilformen (Stunden, Anteil am Tag)
DATEN = HIER.parent / "daten"
aktuell = DATEN / "boerse_aktuell.json"                                      # vom täglichen Lauf (Energy-Charts, bis morgen)
if aktuell.exists():
    quelle = ec_datei = aktuell
else:
    quelle = next(DATEN.glob("boerse_entsoe_*.json"), None) or next(DATEN.glob("boerse_20*.json"))      # ENTSO-E, sonst Energy-Charts
    ec_datei = next(DATEN.glob("boerse_20*.json"))
b = json.load(open(quelle))
ec = json.load(open(ec_datei))                                                 # Energy-Charts füllt Lücken der Hauptquelle
import datetime as _dt
_ende = _dt.datetime.fromtimestamp(b["start"] + len(b["ct_kwh"]) * b["schritt_s"] - 1, _dt.timezone.utc).astimezone(_dt.timezone(_dt.timedelta(hours=1)))
stand_boerse = _ende.strftime("%d.%m.%Y")
q = []
for i, x in enumerate(b["ct_kwh"]):
    if x is None:
        j = (b["start"] + i * b["schritt_s"] - ec["start"]) // ec["schritt_s"]
        x = ec["ct_kwh"][j] if 0 <= j < len(ec["ct_kwh"]) and ec["ct_kwh"][j] is not None else 0
    q.append(x)
boerse = [round(sum(q[i:i + 4]) / 4, 2) for i in range(0, len(q) - 3, 4)]
solar = json.load(open(DATEN / "solar_je_land.json"))["land"]
profile = {}
rows = list(csv.reader(open(DATEN / "lastprofile" / "selp_series.csv", encoding="utf-8")))
kopf = rows[0]
for col in ("g0", "g1", "g2", "g3", "g4", "g5", "g6", "h0"):
    i = kopf.index(col)
    summe = {1: [0.0] * 24, 6: [0.0] * 24, 7: [0.0] * 24}
    for r in rows[1:]:
        tag = int(r[2])
        tag = 1 if tag <= 5 else tag
        summe[tag][int(r[0][11:13])] += float(r[i])
    for k, n in ((1, 15), (6, 3), (7, 3)):        # 3 Zeiträume (Sommer, Winter, Übergang) × 5 Werktage bzw. je 1 Samstag/Sonntag
        summe[k] = [x / n for x in summe[k]]
    gesamt = 261 * sum(summe[1]) + 52 * sum(summe[6]) + 52 * sum(summe[7])        # Jahresenergie in diesen Einheiten
    profile[col] = {k: [round(x / gesamt, 7) for x in v] for k, v in zip(("werktag", "samstag", "sonntag"), (summe[1], summe[6], summe[7]))}
daten = json.dumps({"stand": "31.10.2026", "boerse_stand": stand_boerse, "nb": nb, "plz": plz, "hlzf": hlzf, "boerse": boerse, "solar": solar, "profile": profile}, ensure_ascii=False, separators=(",", ":"))
seite = (HIER / "vorlage.html").read_text(encoding="utf-8").replace("__DATEN__", daten.replace("</", "<\\/"))
(HIER / "netzentgelt_abschaetzung.html").write_text(seite, encoding="utf-8")
print(f"{len(nb)} Netzbetreiber, {len(plz)} Postleitzahlen, {len(hlzf)} mit Hochlastzeitfenstern")
