"""Datensatz für conplot.de (und andere Rechner): Netzentgelte, Hochlastzeitfenster und PLZ-Zuordnung als JSON.

Nur geprüfte Werte: Preise einer Gruppe (RLM NS, RLM MS/NS, SLP) erscheinen nur, wenn sie plausibel sind
(gefunden.csv: "ok"); sonst steht null und der Grund in "fehlt". Beschreibung des Formats: ergebnis/conplot/FORMAT.md
"""
from __future__ import annotations

import csv
import json
from pathlib import Path


def _de(v):
    v = (v or "").strip()
    return float(v.replace(".", "").replace(",", ".")) if v else None


def _rlm(z: dict, prefix: str) -> dict | None:
    w = {
        "lp_unter_eur_kw_jahr": _de(z[f"{prefix}_lp_unter_2500h_eur_kw_jahr"]),
        "ap_unter_ct_kwh": _de(z[f"{prefix}_ap_unter_2500h_ct_kwh"]),
        "lp_ab_eur_kw_jahr": _de(z[f"{prefix}_lp_ab_2500h_eur_kw_jahr"]),
        "ap_ab_ct_kwh": _de(z[f"{prefix}_ap_ab_2500h_ct_kwh"]),
    }
    return w if all(v is not None for v in w.values()) else None


def _quellen(q: str) -> dict:
    """"RLM: url1 | SLP: url2" oder eine URL."""
    if q.startswith("RLM:"):
        teile = dict(t.strip().split(": ", 1) for t in q.split(" | ") if ": " in t)
        return {"rlm": teile.get("RLM"), "slp": teile.get("SLP")}
    return {"rlm": q or None, "slp": q or None}


def erzeugen(out: Path, jahr: int) -> dict:
    zeilen = {r["nr"]: r for r in csv.DictReader(open(out / f"netzentgelte_{jahr}.csv", encoding="utf-8"), delimiter=";")}
    gef = {r["nr"]: r for r in csv.DictReader(open(out / "gefunden.csv", encoding="utf-8"), delimiter=";")}
    hlzf: dict = {}
    pfad_h = out / f"hochlastzeitfenster_{jahr}.csv"
    if pfad_h.exists():
        jz_kurz = {"Frühling": "fruehling", "Sommer": "sommer", "Herbst": "herbst", "Winter": "winter"}
        eb_kurz = {"Niederspannung": "ns", "Umspannung MS/NS": "msns"}
        for r in csv.DictReader(open(pfad_h, encoding="utf-8"), delimiter=";"):
            h = hlzf.setdefault(r["nr"], {"quelle": r["quelle_url"]})
            eb = eb_kurz[r["ebene"]]
            e = h.setdefault(eb, {"zeitfenster": {}, "schwelle_prozent": int(r["schwelle_prozent"]),
                                  "herkunft_schwelle": r["herkunft_schwelle"],
                                  "mindestverlagerung_kw": int(r["mindestleistung_kw"]) if r["mindestleistung_kw"] else None})
            e["zeitfenster"][jz_kurz[r["jahreszeit"].split(" ")[0]]] = (
                [] if r["zeitfenster"] == "keins" else r["zeitfenster"].split(", "))

    netzbetreiber = []
    for nr, z in zeilen.items():
        g = gef.get(nr, {})
        ns = _rlm(z, "ns") if g.get("rlm_ns") == "ok" else None
        msns = _rlm(z, "msns") if g.get("rlm_msns") == "ok" else None
        slp = ({"ap_ct_kwh": _de(z["slp_ap_ct_kwh"]), "gp_eur_jahr": _de(z["slp_grundpreis_eur_jahr"])}
               if g.get("slp") == "ok" else None)
        fehlt = [t for t, v in (("rlm_ns", ns), ("slp", slp), ("hlzf", hlzf.get(nr))) if not v]
        netzbetreiber.append({
            "nr": int(nr), "netzbetreiber": z["netzbetreiber"], "mastr_nr": z["mastr_nr"], "website": z["website"],
            "jahr": jahr, "preisstand": z["preisstand"] or None, "stand_datum": z["stand_datum"] or None,
            "grenze": "<=2500" if "≤ 2.500" in z["hinweis"] else "<2500",
            "rlm": {"ns": ns, "msns": msns} if (ns or msns) else None,
            "slp": slp,
            "hlzf": hlzf.get(nr),
            "quelle": _quellen(z["quelle_url"]),
            "status": z["status"], "fehlt": fehlt,
        })
    mastr2nr = {z["mastr_nr"]: int(nr) for nr, z in sorted(zeilen.items(), key=lambda x: int(x[0]))}
    plz: dict = {}
    for r in csv.DictReader(open(out / "plz_netzbetreiber.csv", encoding="utf-8"), delimiter=";"):
        n = mastr2nr.get(r["mastr_nr"])
        if n is not None and all(e["nr"] != n for e in plz.get(r["plz"], [])):
            plz.setdefault(r["plz"], []).append({"nr": n, "anteil_prozent": _de(r["anteil_prozent"])})
    ziel = out / "conplot"
    ziel.mkdir(exist_ok=True)
    (ziel / f"netzbetreiber_{jahr}.json").write_text(json.dumps(
        {"jahr": jahr, "einheiten": {"lp": "EUR je kW und Jahr (Jahresleistungspreis, netto)", "ap": "Cent je kWh (netto)",
                                     "gp": "EUR je Jahr (netto)"},
         "netzbetreiber": netzbetreiber}, ensure_ascii=False, indent=1), encoding="utf-8")
    (ziel / f"plz_{jahr}.json").write_text(json.dumps(plz, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"netzbetreiber": len(netzbetreiber), "rlm_ns": sum(1 for e in netzbetreiber if e["rlm"] and e["rlm"]["ns"]),
            "slp": sum(1 for e in netzbetreiber if e["slp"]), "hlzf": sum(1 for e in netzbetreiber if e["hlzf"]),
            "plz": len(plz)}
