"""Baut lauf/werte_entfernt.csv neu: Preisblöcke der Tabelle, die erkennbar Müll sind (ganze Zahlen, 365/1095, 2,50 aus "2.500 h/a") und für die keine Dokumentzeile gefunden wurde.
Aufruf: PYTHONPATH=. python daten/werte_entfernen.py"""
import csv
t = list(csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";"))
de = lambda v: float(v.replace(".", "").replace(",", ".")) if v else None
K = ("lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh")
alt = {}
try:
    for r_ in csv.DictReader(open("lauf/werte_entfernt.csv", encoding="utf-8-sig"), delimiter=";"):
        alt[(r_["nr"], r_["ebene"])] = r_["grund"]
except FileNotFoundError:
    pass
neu = {}
for x in t:
    for eb in ("ms", "msns", "ns", "hsms"):
        v = [de(x[f"{eb}_{k}"]) for k in K]
        if None in v:
            continue
        ganz = sum(1 for q in v if abs(q - round(q)) < 1e-9)
        if ganz >= 3 or any(q in (365, 366, 1095) for q in v) or abs(v[1] - 2.5) < 1e-9 or abs(v[0] - 2.5) < 1e-9:
            neu[(x["nr"], eb)] = "Müllwerte: ganze Zahlen, 365/1095 oder 2,50 (aus 2.500 h/a) als Preis gelesen; keine passende Dokumentzeile"
alt.update(neu)
rows = [(k[0], k[1], g) for k, g in sorted(alt.items(), key=lambda kv: (int(kv[0][0]), kv[0][1]))]
with open("lauf/werte_entfernt.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";"); w.writerow(["nr", "ebene", "grund"]); w.writerows(rows)
print(len(rows), "Werte entfernt,", len(neu), "neu")
