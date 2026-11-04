"""Unser Leser (vnb/extract.py) über alle Layout-Texte (ergebnis/texte_layout), offline. Ergebnis: ergebnis/leser_ergebnis_aus_texten.csv
Aufruf: PYTHONPATH=. python daten/leser_alle_texte.py"""
import csv, glob, tempfile
from pathlib import Path
from vnb.extract import auswerten
K = ["lp_unter_2500", "ap_unter_2500", "lp_ueber_2500", "ap_ueber_2500"]
def f(d): return "/".join(f"{d[k]:.2f}".replace(".", ",") for k in K) if d and all(k in d for k in K) else ""
rows = []
for fn in sorted(glob.glob("ergebnis/texte_layout/SNB*.txt")):
    m, nr = Path(fn).stem.split("_")[:2]
    p = Path(tempfile.mkdtemp()) / "a.html"; p.write_text(Path(fn).read_text(encoding="utf8", errors="replace"), encoding="utf8")
    try: e = auswerten(p, "https://x.de/a.pdf", 2026)
    except Exception: continue
    rows.append([m, nr, f(e.ms), f(e.msns), f(e.ns), f(e.hsms)])
with open("ergebnis/leser_ergebnis_aus_texten.csv", "w", encoding="utf-8-sig", newline="") as o:
    w = csv.writer(o, delimiter=";"); w.writerow(["mastr_nr", "unsere_nr", "ms", "msns", "ns", "hsms"]); w.writerows(rows)
print(len(rows), "Texte gelesen")
