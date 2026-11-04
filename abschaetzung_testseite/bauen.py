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


z = {r["nr"]: r for r in csv.DictReader(open(ERG / "netzentgelte_2026.csv", encoding="utf-8"), delimiter=";")}
g = {r["nr"]: r for r in csv.DictReader(open(ERG / "gefunden.csv", encoding="utf-8"), delimiter=";")}
FELDER = ("lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh")
nb, mastr2nr = [], {}
for nr, r in z.items():
    mastr2nr.setdefault(r["mastr_nr"], nr)
    e = {"n": int(nr), "bl": (r["bundesland"].split(" / ")[0] or "Bayern"), "name": r["netzbetreiber"], "ps": r["preisstand"], "sd": r["stand_datum"],
         "le": r.get("grenze_2500h", "").startswith("≤") or "≤ 2.500" in r["hinweis"]}
    if r["slp_ap_ct_kwh"] and r["slp_grundpreis_eur_jahr"]:
        e["slp"] = [de(r["slp_ap_ct_kwh"]), de(r["slp_grundpreis_eur_jahr"])]
    for eb in ("ns", "msns", "ms", "hsms"):                       # Ebenen, wenn alle vier Werte da sind
        w = [de(r.get(f"{eb}_{k}", "")) for k in FELDER]
        if all(x is not None for x in w):
            e[eb] = w
    if "noch nicht gegen das Dokument" in r["hinweis"]:
        e["ug"] = 1                                                # Werte aus Liste, noch nicht gegen das Dokument geprüft
        e.pop("ms", None); e.pop("hsms", None)                     # ungeprüfte Ebenen nicht rechnen
    if r["quelle_url"]:
        e["q"] = r["quelle_url"]
    nb.append(e)
plz = collections.defaultdict(list)
for r in csv.DictReader(open(ERG / "plz_netzbetreiber.csv", encoding="utf-8"), delimiter=";"):
    nr = mastr2nr.get(r["mastr_nr"])
    if nr and int(nr) not in [x[0] for x in plz[r["plz"]]]:
        plz[r["plz"]].append([int(nr), de(r["anteil_prozent"])])
hlzf = {}
for r in csv.DictReader(open(ERG / "hochlastzeitfenster_2026.csv", encoding="utf-8"), delimiter=";"):
    if r["ebene"] != "Niederspannung":
        continue
    e = hlzf.setdefault(int(r["nr"]), {"f": {}, "s": int(r["schwelle_prozent"]), "sh": r["herkunft_schwelle"],
                                       "m": int(r["mindestleistung_kw"]) if r["mindestleistung_kw"] else None,
                                       "q": r["quelle_url"]})
    e["f"][r["jahreszeit"].split(" ")[0]] = [] if r["zeitfenster"] == "keins" else r["zeitfenster"].split(", ")
# Börsenpreise (Viertelstunden → Stundenmittel, ct/kWh), Solarertrag je Bundesland, Lastprofilformen (Stunden, Anteil am Tag)
DATEN = HIER.parent / "daten"
quelle = next(DATEN.glob("boerse_entsoe_*.json"), None) or next(DATEN.glob("boerse_20*.json"))      # ENTSO-E, sonst Energy-Charts
b = json.load(open(quelle))
ec = json.load(open(next(DATEN.glob("boerse_20*.json"))))                      # Energy-Charts füllt Lücken der Hauptquelle
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
daten = json.dumps({"stand": "31.10.2026", "nb": nb, "plz": plz, "hlzf": hlzf, "boerse": boerse, "solar": solar, "profile": profile}, ensure_ascii=False, separators=(",", ":"))
seite = (HIER / "vorlage.html").read_text(encoding="utf-8").replace("__DATEN__", daten.replace("</", "<\\/"))
(HIER / "netzentgelt_abschaetzung.html").write_text(seite, encoding="utf-8")
print(f"{len(nb)} Netzbetreiber, {len(plz)} Postleitzahlen, {len(hlzf)} mit Hochlastzeitfenstern")
