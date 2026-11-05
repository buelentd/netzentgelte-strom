"""Konsens beider Leser: Werte, bei denen der Leser des Nutzers (Datei *_ausgefuellt.csv, Spalte wert_nutzerleser) denselben Wert gelesen hat
wie die Tabelle, gelten als sehr sicher. Eine Zeile in lauf/preise_manuell.csv bekommt geprueft=ja, wenn jede Ebene der Zeile durch Konsens
oder Zeilenanker am Dokument bestätigt ist (SLP nur durch Konsens). Schreibt außerdem ergebnis/konsens_beide_leser.csv.
Aufruf: PYTHONPATH=. python daten/konsens_uebernehmen.py <ausgefuellte_csv> [--schreiben]"""
import csv, glob, io, re, sys
from pathlib import Path
src = open("daten/referenzliste.py", encoding="utf8").read().replace("\nmain()\n", "\n")
ns = {}; exec(compile(src, "rl", "exec"), ns)
best, z, SP = ns["bestaetigt"], ns["z"], ns["SP"]

def zahlen(s):
    return [z(x) for x in re.split(r"[/ ]+", s.strip()) if x.strip()]

def main(datei, schreiben):
    O = {r["mastr_nr"]: r for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
    konsens = set()
    for r in csv.DictReader(open(datei, encoding="utf-8-sig"), delimiter=";"):
        t = O.get(r["mastr_nr"]); eb = r["ebene"]
        if not t or not r["wert_nutzerleser"].strip(): continue
        theirs = zahlen(r["wert_nutzerleser"])
        if eb == "slp":
            mine = [z(t["slp_grundpreis_eur_jahr"]), z(t["slp_ap_ct_kwh"])] if t["slp_ap_ct_kwh"] else None
        else:
            mine = [z(t[f"{eb}_{s}"]) for s in SP] if all(t[f"{eb}_{s}"] for s in SP) else None
        if mine and len(mine) == len(theirs) and all(a is not None and b is not None and abs(a - b) < 0.006 for a, b in zip(mine, theirs)):
            konsens.add((r["mastr_nr"], eb))
    with open("ergebnis/konsens_beide_leser.csv", "w", encoding="utf-8-sig", newline="") as o:
        w = csv.writer(o, delimiter=";"); w.writerow(["mastr_nr", "ebene"]); w.writerows(sorted(konsens))
    print(len(konsens), "Werte, bei denen beide Leser übereinstimmen")
    p = "lauf/preise_manuell.csv"
    raw = open(p, encoding="utf-8", newline="").read()
    bom = raw.startswith("﻿"); nl = "\r\n" if "\r\n" in raw else "\n"
    rows = list(csv.reader(io.StringIO(raw.lstrip("﻿")), delimiter=";"))
    H = rows[0]; I = {h: i for i, h in enumerate(H)}
    N = {r["nr"]: r for r in O.values()}
    hoch = 0
    for x in rows[1:]:
        if x[I["geprueft"]]: continue
        t = N.get(x[0])
        if not t: continue
        f = glob.glob(f"ergebnis/texte_layout/{t['mastr_nr']}_*.txt")
        zeilen = Path(f[0]).read_text(encoding="utf8", errors="replace").split("\n") if f else None
        ok = True; n = 0
        for eb in ("ms", "msns", "ns", "hsms"):
            w = [x[I[f"{eb}_{s}"]] for s in SP]
            if not all(w): continue
            n += 1
            if (t["mastr_nr"], eb) in konsens: continue
            if zeilen and best(zeilen, eb, [z(v) for v in w]): continue
            ok = False
        if x[I["slp_ap_ct_kwh"]] and (t["mastr_nr"], "slp") not in konsens: ok = False
        if ok and n:
            x[I["geprueft"]] = "ja"; hoch += 1
            x[I["hinweis"]] = (x[I["hinweis"]] + "; " if x[I["hinweis"]] else "") + "Konsens beider Leser bzw. Zeilenanker: alle Ebenen der Zeile bestätigt (05.11.2026)"
    print(hoch, "Zeilen auf geprüft gesetzt")
    if schreiben:
        out = io.StringIO(); w = csv.writer(out, delimiter=";", lineterminator=nl); w.writerows(rows)
        open(p, "w", encoding="utf-8", newline="").write(("﻿" if bom else "") + out.getvalue())
        print("preise_manuell.csv geschrieben")
main(sys.argv[1], "--schreiben" in sys.argv)
