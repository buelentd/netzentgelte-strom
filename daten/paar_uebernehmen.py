"""Zeilenpaar-Tabellen (vnb/paarparser.py) in die Tabelle übernehmen, wo sie vom Tabellenwert abweichen oder die Ebene fehlt.
Pilot-Zeilen (nicht in der Arbeits-Queue) bleiben unangetastet. Aufruf: PYTHONPATH=. python daten/paar_uebernehmen.py [--schreiben]"""
import csv, glob, io, sys
from pathlib import Path
from vnb.paarparser import paarparser
SP = ["lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh"]
PILOT = {"30", "34", "40"}

def main(schreiben):
    O = {r["mastr_nr"]: r for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
    sperre = {r["nr"] for r in csv.DictReader(open("lauf/zuordnung_unbelegt.csv", encoding="utf-8-sig"), delimiter=";")}
    plan = {}
    for f in sorted(glob.glob("ergebnis/texte_layout/SNB*.txt")):
        m = Path(f).stem.split("_")[0]; t = O.get(m)
        if not t or t["nr"] in PILOT or t["nr"] in sperre: continue
        res = paarparser(Path(f).read_text(encoding="utf8", errors="replace").split("\n"))
        for eb, w in res.items():
            tab = [t[f"{eb}_{s}"] for s in SP]
            if all(tab) and all(abs(float(a.replace(",", ".")) - b) < 0.006 for a, b in zip(tab, w)): continue
            plan.setdefault(t["nr"], {})[eb] = w
    print(sum(len(v) for v in plan.values()), "Ebenen bei", len(plan), "Netzbetreibern:", {n: list(v) for n, v in plan.items()})
    if not schreiben: return
    p = "lauf/preise_manuell.csv"
    raw = open(p, encoding="utf-8", newline="").read()
    bom = raw.startswith("﻿"); nl = "\r\n" if "\r\n" in raw else "\n"
    rows = list(csv.reader(io.StringIO(raw.lstrip("﻿")), delimiter=";"))
    H = rows[0]; I = {h: i for i, h in enumerate(H)}
    byn = {x[0]: x for x in rows[1:]}
    N = {r["nr"]: r for r in O.values()}
    for nr, ebs in plan.items():
        x = byn.get(nr)
        if x is None:
            x = [""] * len(H); x[I["nr"]] = nr; x[I["netzbetreiber"]] = N[nr]["netzbetreiber"]; x[I["stand_datum"]] = "2026"
            x[I["quelle_url"]] = N[nr]["quelle_url"]; rows.append(x); byn[nr] = x
        for eb, w in ebs.items():
            for s, v in zip(SP, w): x[I[f"{eb}_{s}"]] = f"{v:.2f}".replace(".", ",")
        x[I["geprueft"]] = ""
        x[I["hinweis"]] = "Korrigiert 04.11.2026: Ebene(n) " + ", ".join(ebs) + " aus Zeilenpaar-Tabelle (< 2.500 h / >= 2.500 h) nach Ebenenname gelesen; Werte am Text geprüft"
    out = io.StringIO(); w = csv.writer(out, delimiter=";", lineterminator=nl); w.writerows(rows)
    open(p, "w", encoding="utf-8", newline="").write(("﻿" if bom else "") + out.getvalue())
    print("geschrieben")
main("--schreiben" in sys.argv)
