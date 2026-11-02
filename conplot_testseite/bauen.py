"""Baut die Testseite (Nachbau der geführten Abschätzung von conplot.de) aus vorlage.html und den Ergebnissen.

Aufruf: python conplot_testseite/bauen.py  →  conplot_testseite/netzentgelt_abschaetzung.html
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
FELDER = ("lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ueber_2500h_eur_kw_jahr", "ap_ueber_2500h_ct_kwh")
nb, mastr2nr = [], {}
for nr, r in z.items():
    mastr2nr.setdefault(r["mastr_nr"], nr)
    gr = g.get(nr, {})
    e = {"n": int(nr), "name": r["netzbetreiber"], "ps": r["preisstand"], "sd": r["stand_datum"], "le": "≤ 2.500" in r["hinweis"]}
    if gr.get("slp") == "ok":
        e["slp"] = [de(r["slp_ap_ct_kwh"]), de(r["slp_grundpreis_eur_jahr"])]
    if gr.get("rlm_ns") == "ok":
        e["ns"] = [de(r[f"ns_{k}"]) for k in FELDER]
        m = [de(r[f"msns_{k}"]) for k in FELDER]
        if gr.get("rlm_msns") == "ok" and all(x is not None for x in m):
            e["msns"] = m
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
daten = json.dumps({"stand": "31.10.2026", "nb": nb, "plz": plz, "hlzf": hlzf}, ensure_ascii=False, separators=(",", ":"))
seite = (HIER / "vorlage.html").read_text(encoding="utf-8").replace("__DATEN__", daten.replace("</", "<\\/"))
(HIER / "netzentgelt_abschaetzung.html").write_text(seite, encoding="utf-8")
print(f"{len(nb)} Netzbetreiber, {len(plz)} Postleitzahlen, {len(hlzf)} mit Hochlastzeitfenstern")
