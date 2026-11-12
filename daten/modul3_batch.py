"""Hilfsskript: gibt Modul-3-Ausschnitte der offenen Fälle kompakt zum Lesen aus. Aufruf: PYTHONPATH=. python daten/modul3_batch.py <von> <bis>"""
import csv, glob, re, sys
from vnb.modul3 import blocks, ZEIT
o = [r for r in csv.DictReader(open("ergebnis/modul3_offen.csv", encoding="utf-8-sig"), delimiter=";")]
fertig = set()
try:
    fertig = {r["mastr_nr"] for r in csv.DictReader(open("ergebnis/modul3_manuell.csv", encoding="utf-8-sig"), delimiter=";")}
except FileNotFoundError:
    pass
liste = []
for r in o:
    if r["mastr_nr"] in fertig:
        continue
    f = glob.glob(f"ergebnis/texte_layout/{r['mastr_nr']}_*.txt")[0]
    L = open(f, encoding="utf8", errors="replace").read().split("\n")
    B = blocks(L)
    if any(ZEIT.search(L[i]) for i in B):
        liste.append((r, L, B))
a, b = int(sys.argv[1]), int(sys.argv[2])
print(len(liste), "offen mit Zeiten")
for r, L, B in liste[a:b]:
    t = [i for i in B if ZEIT.search(L[i])]
    lo, hi = max(0, t[0] - 4), min(len(L), t[-1] + 4)
    print("=====", r["mastr_nr"], r["netzbetreiber"][:34])
    print("\n".join(re.sub(r"\s{3,}", " | ", L[k].strip())[:150] for k in range(lo, min(hi, lo + 26)) if L[k].strip()))
