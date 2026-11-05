"""Elektronische Preisblätter (Excel) aus eingang/ lesen (vnb/xlsx_preisblatt.py) und nach lauf/preise_manuell.csv übernehmen.
Stimmen die Excel-Werte mit der Tabelle überein, gilt die Zeile als bestätigt (zwei unabhängige Lesungen). Weichen sie ab oder fehlen sie in der Tabelle,
gewinnt das Excel (Hinweis beginnt mit "Korrigiert"). Aufruf: PYTHONPATH=. python daten/xlsx_uebernehmen.py [--schreiben]"""
import csv, glob, io, os, sys
sys.path.insert(0, ".")
from vnb.xlsx_preisblatt import preisblatt_lesen
exec(open("daten/eingang_verarbeiten.py", encoding="utf-8").read().split("def main(")[0])
F = ("lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh")
de = lambda v: float(v.replace(".", "").replace(",", ".")) if v else None
def fmt(v):
    t = f"{v:.4f}".rstrip("0")
    if len(t.split(".")[1]) < 2:
        t = f"{v:.2f}"
    return t.replace(".", ",")

def main(schreiben):
    n2m, unser = zuordnung()
    tab = {r["nr"]: r for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
    plan = []
    dateien = sorted(set(glob.glob("eingang/**/pb_*.xlsx", recursive=True) + glob.glob("eingang/**/pb_*.xls", recursive=True)
                         + glob.glob("eingang/**/pb_*.xlsm", recursive=True)))
    for f in dateien:
        z = ziel(f, n2m, unser)
        if not z:
            continue
        nr = str(int(z[1]))
        try:
            r = preisblatt_lesen(f)
        except Exception as e:
            print(os.path.basename(f), "nicht lesbar:", type(e).__name__); continue
        x = tab[nr]
        felder, gleich, korr = {}, [], []
        for eb in ("ns", "msns", "ms", "hsms"):
            if eb not in r:
                continue
            alt = [de(x[f"{eb}_{k}"]) for k in F]
            for k, v in zip(F, r[eb]):
                felder[f"{eb}_{k}"] = fmt(v)
            if None in alt:
                korr.append(f"{eb} neu")
            elif all(abs(a - b) < 0.02 for a, b in zip(alt, r[eb])):
                gleich.append(eb)
            else:
                korr.append(f"{eb} abweichend")
        if "slp" in r:
            alt = (de(x["slp_grundpreis_eur_jahr"]), de(x["slp_ap_ct_kwh"]))
            felder["slp_grundpreis_eur_jahr"], felder["slp_ap_ct_kwh"] = fmt(r["slp"][0]), fmt(r["slp"][1])
            if None in alt:
                korr.append("slp neu")
            elif abs(alt[0] - r["slp"][0]) < 0.02 and abs(alt[1] - r["slp"][1]) < 0.02:
                gleich.append("slp")
            else:
                korr.append("slp abweichend")
        if felder:
            plan.append((nr, x["netzbetreiber"], os.path.basename(f), felder, gleich, korr))
    for nr, name, datei, felder, gleich, korr in plan:
        print(f"{nr:>4} {name[:30]:30} {datei:16} bestätigt: {','.join(gleich) or '-':26} übernommen: {', '.join(korr) or '-'}")
    if not schreiben:
        return
    p = "lauf/preise_manuell.csv"
    raw = open(p, encoding="utf-8", newline="").read()
    bom = raw.startswith("﻿"); nl = "\r\n" if "\r\n" in raw else "\n"
    rows = list(csv.reader(io.StringIO(raw.lstrip("﻿")), delimiter=";"))
    H = rows[0]; I = {h: i for i, h in enumerate(H)}
    byn = {x[0]: x for x in rows[1:]}
    for nr, name, datei, felder, gleich, korr in plan:
        x = byn.get(nr)
        if x is None:
            x = [""] * len(H); x[I["nr"]] = nr; x[I["netzbetreiber"]] = name; x[I["stand_datum"]] = "2026"
            x[I["quelle_url"]] = tab[nr]["quelle_url"]; rows.append(x); byn[nr] = x
        for k, v in felder.items():
            if k in I:
                x[I[k]] = v
        alt = x[I["hinweis"]]
        if korr:
            neu = "Korrigiert: aus elektronischem Preisblatt (Excel, " + datei + ") gelesen: " + ", ".join(korr)
            x[I["hinweis"]] = neu + ("; " + alt if alt else "")
        elif gleich and not alt:
            x[I["hinweis"]] = "bestätigt durch elektronisches Preisblatt (Excel, " + datei + ")"
        if gleich and not korr and "geprueft" in I:
            x[I["geprueft"]] = "ja"                      # zwei unabhängige Lesungen stimmen überein
    out = io.StringIO(); w = csv.writer(out, delimiter=";", lineterminator=nl); w.writerows(rows)
    open(p, "w", encoding="utf-8", newline="").write(("﻿" if bom else "") + out.getvalue())
    print("preise_manuell.csv geschrieben")

main("--schreiben" in sys.argv)
