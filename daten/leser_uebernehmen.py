"""Übernimmt Ebenen, die unser Leser aus den Layout-Texten liest UND die am Dokument bestätigt sind (alle vier Werte in einer Zeile
mit dem passenden Ebenennamen), nach lauf/preise_manuell.csv. Nur wenn die Tabelle die Ebene nicht hat oder ihr Wert nicht bestätigt ist.
Aufruf: PYTHONPATH=. python daten/leser_uebernehmen.py [--schreiben]   (ohne Argument nur zählen)"""
import csv, glob, io, sys
from pathlib import Path
src = open("daten/referenzliste.py", encoding="utf8").read().replace("\nmain()\n", "\n")
ns = {}; exec(compile(src, "rl", "exec"), ns)
best, z, SP = ns["bestaetigt"], ns["z"], ns["SP"]
EB = ["ms", "msns", "ns", "hsms"]

def main(schreiben):
    O = {r["mastr_nr"]: r for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
    L = {r["mastr_nr"]: r for r in csv.DictReader(open("ergebnis/leser_ergebnis_aus_texten.csv", encoding="utf-8-sig"), delimiter=";")}
    sperre = {r["nr"] for r in csv.DictReader(open("lauf/zuordnung_unbelegt.csv", encoding="utf-8-sig"), delimiter=";")}
    plan = {}; neu = korr = 0
    for m, l in L.items():
        t = O.get(m)
        if not t or t["nr"] in sperre: continue
        pfad = glob.glob(f"ergebnis/texte_layout/{m}_*.txt")
        if not pfad: continue
        zeilen = Path(pfad[0]).read_text(encoding="utf8", errors="replace").split("\n")
        ad = {}; alle = True
        for eb in EB:
            v = l[eb]; tab = "/".join(t[f"{eb}_{s}"] for s in SP) if all(t[f"{eb}_{s}"] for s in SP) else ""
            wv = [z(x) for x in v.split("/")] if v else None
            if v and best(zeilen, eb, wv):
                if not tab: ad[eb] = v; neu += 1
                elif tab != v:
                    if not best(zeilen, eb, [z(x) for x in tab.split("/")]): ad[eb] = v; korr += 1
                    else: pass
            if tab and eb not in ad and not best(zeilen, eb, [z(x) for x in tab.split("/")]): alle = False
        if ad: plan[t["nr"]] = (t, ad, alle)
    print(f"{len(plan)} Netzbetreiber, {neu} neue Ebenen, {korr} Korrekturen; alle Ebenen der Zeile bestätigt bei {sum(1 for p in plan.values() if p[2])}")
    if not schreiben: return
    p = "lauf/preise_manuell.csv"
    raw = open(p, encoding="utf-8", newline="").read()
    bom = raw.startswith("﻿"); nl = "\r\n" if "\r\n" in raw else "\n"
    rows = list(csv.reader(io.StringIO(raw.lstrip("﻿")), delimiter=";"))
    H = rows[0]; I = {h: i for i, h in enumerate(H)}
    byn = {r[0]: r for r in rows[1:]}
    for nr, (t, ad, alle) in plan.items():
        r = byn.get(nr)
        if r is None:
            r = [""] * len(H); r[I["nr"]] = nr; r[I["netzbetreiber"]] = t["netzbetreiber"]; r[I["stand_datum"]] = "2026"
            r[I["quelle_url"]] = t["quelle_url"]; rows.append(r); byn[nr] = r
        for eb, v in ad.items():
            for s, x in zip(SP, v.split("/")): r[I[f"{eb}_{s}"]] = x
        if alle: r[I["geprueft"]] = "ja"
        r[I["hinweis"]] = ("Korrigiert 04.11.2026: Ebene(n) " + ", ".join(ad) + " vom Leser aus dem Layout-Text gelesen und am Dokument bestätigt (alle vier Werte in einer Zeile mit dem Ebenennamen)")
    out = io.StringIO(); w = csv.writer(out, delimiter=";", lineterminator=nl); w.writerows(rows)
    open(p, "w", encoding="utf-8", newline="").write(("﻿" if bom else "") + out.getvalue())
    print("preise_manuell.csv geschrieben")
main("--schreiben" in sys.argv)
