"""RLM-Parser (vnb/rlm_parser.py) für Ebenen, die in der Tabelle fehlen, obwohl ein Dokument vorliegt: nach lauf/preise_manuell.csv,
ungeprüft (geprueft wird geleert -> Status prüfen, Hinweis nennt die Zeile). Aufruf: PYTHONPATH=. python daten/rlm_uebernehmen.py [--schreiben]"""
import csv, glob, io, sys
from pathlib import Path
from vnb.rlm_parser import rlm_parser

SP = ["lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh"]

def text(r):
    f = glob.glob(f"ergebnis/texte_layout/{r['mastr_nr']}_*.txt") or glob.glob(f"ergebnis/texte/{int(r['nr']):04d}.txt")
    return Path(f[0]).read_text(encoding="utf8", errors="replace").split("\n") if f else None

def main(schreiben):
    sperre = {r["nr"] for r in csv.DictReader(open("lauf/zuordnung_unbelegt.csv", encoding="utf-8-sig"), delimiter=";")}
    plan = {}
    for r in csv.DictReader(open("ergebnis/ebenen_erwartung.csv", encoding="utf-8-sig"), delimiter=";"):
        if r["nr"] in sperre: continue
        L = text(r)
        if not L: continue
        for eb in ("ms", "msns", "ns", "hsms"):
            if r[eb] in ("im_dokument_nicht_gelesen", "nicht_ausgewiesen"):
                res = rlm_parser(L, eb)
                if res: plan.setdefault(r["nr"], {})[eb] = res
    n = sum(len(v) for v in plan.values())
    print(n, "Ebenen bei", len(plan), "Netzbetreibern aus dem RLM-Parser (ungeprüft)")
    if not schreiben: return
    p = "lauf/preise_manuell.csv"
    raw = open(p, encoding="utf-8", newline="").read()
    bom = raw.startswith("﻿"); nl = "\r\n" if "\r\n" in raw else "\n"
    rows = list(csv.reader(io.StringIO(raw.lstrip("﻿")), delimiter=";"))
    H = rows[0]; I = {h: i for i, h in enumerate(H)}
    byn = {x[0]: x for x in rows[1:]}
    O = {r["nr"]: r for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
    for nr, ebs in plan.items():
        x = byn.get(nr)
        if x is None:
            x = [""] * len(H); x[I["nr"]] = nr; x[I["netzbetreiber"]] = O[nr]["netzbetreiber"]; x[I["stand_datum"]] = "2026"
            x[I["quelle_url"]] = O[nr]["quelle_url"]; rows.append(x); byn[nr] = x
        for eb, (w, beleg) in ebs.items():
            for s, v in zip(SP, w): x[I[f"{eb}_{s}"]] = f"{v:.2f}".replace(".", ",")
        x[I["geprueft"]] = ""
        alt = x[I["hinweis"]]
        x[I["hinweis"]] = (alt + "; " if alt else "") + "Ebene(n) " + ", ".join(ebs) + " vom RLM-Parser gelesen, nicht gegen das Dokument bestätigt: " + " ".join(list(ebs.values())[0][1].split())[:80]
    out = io.StringIO(); w = csv.writer(out, delimiter=";", lineterminator=nl); w.writerows(rows)
    open(p, "w", encoding="utf-8", newline="").write(("﻿" if bom else "") + out.getvalue())
    print("preise_manuell.csv geschrieben")
main("--schreiben" in sys.argv)
