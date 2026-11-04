"""SLP-Parser (vnb/slp_parser.py) für Netzbetreiber mit Dokument, aber ohne SLP-Wert in der Tabelle:
Werte nach lauf/preise_manuell.csv, ungeprüft (geprueft leer -> Status prüfen, Hinweis nennt die Zeile).
Aufruf: PYTHONPATH=. python daten/slp_uebernehmen.py [--schreiben]"""
import csv, glob, io, sys
from pathlib import Path
from vnb.slp_parser import slp_parser

def text(r):
    f = glob.glob(f"ergebnis/texte_layout/{r['mastr_nr']}_*.txt") or glob.glob(f"ergebnis/texte/{int(r['nr']):04d}.txt")
    return Path(f[0]).read_text(encoding="utf8", errors="replace").split("\n") if f else None

def main(schreiben):
    sperre = {r["nr"] for r in csv.DictReader(open("lauf/zuordnung_unbelegt.csv", encoding="utf-8-sig"), delimiter=";")}
    plan = []
    for r in csv.DictReader(open("ergebnis/ebenen_erwartung.csv", encoding="utf-8-sig"), delimiter=";"):
        if r["slp"] != "fehlt" or r["nr"] in sperre: continue
        L = text(r)
        res = slp_parser(L) if L else None
        if res and 3 <= res[1] <= 15 and 0 < res[0] <= 200:
            plan.append((r, res))
    print(len(plan), "SLP-Werte aus dem SLP-Parser (ungeprüft)")
    if not schreiben: return
    p = "lauf/preise_manuell.csv"
    raw = open(p, encoding="utf-8", newline="").read()
    bom = raw.startswith("﻿"); nl = "\r\n" if "\r\n" in raw else "\n"
    rows = list(csv.reader(io.StringIO(raw.lstrip("﻿")), delimiter=";"))
    H = rows[0]; I = {h: i for i, h in enumerate(H)}
    byn = {x[0]: x for x in rows[1:]}
    O = {r["nr"]: r for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
    for r, (gp, ap, beleg) in plan:
        x = byn.get(r["nr"])
        if x is None:
            x = [""] * len(H); x[I["nr"]] = r["nr"]; x[I["netzbetreiber"]] = r["netzbetreiber"]; x[I["stand_datum"]] = "2026"
            x[I["quelle_url"]] = O[r["nr"]]["quelle_url"]; rows.append(x); byn[r["nr"]] = x
        x[I["slp_grundpreis_eur_jahr"]] = f"{gp:.2f}".replace(".", ","); x[I["slp_ap_ct_kwh"]] = f"{ap:.2f}".replace(".", ",")
        alt = x[I["hinweis"]]
        x[I["hinweis"]] = (alt + "; " if alt else "") + "SLP vom SLP-Parser gelesen, nicht gegen das Dokument bestätigt: " + " ".join(beleg.split())[:90]
    out = io.StringIO(); w = csv.writer(out, delimiter=";", lineterminator=nl); w.writerows(rows)
    open(p, "w", encoding="utf-8", newline="").write(("﻿" if bom else "") + out.getvalue())
    print("preise_manuell.csv geschrieben")
main("--schreiben" in sys.argv)
