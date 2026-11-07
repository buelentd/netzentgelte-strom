"""Legt Texte aller gelieferten PDFs (eingang/**/<nr>_preis_*.pdf, ergebnis/pdf/<nnnn>_*.pdf) neben die bestehenden Dokumenttexte,
damit der Beleg-Leser auch gegen die gelieferten Preisblätter prüfen kann: ergebnis/texte_layout/<MaStR>_<nr4>_lieferung_<name>.txt"""
import csv, glob, re, subprocess, os
N = {r["nr"]: r for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
n = 0
pdfs = [(m.group(1), p) for p in glob.glob("eingang/**/*.pdf", recursive=True) if (m := re.search(r"(?:^|-)(\d{1,3})_preis_", os.path.basename(p))) and "2027" not in p]
pdfs += [(str(int(m.group(1))), p) for p in glob.glob("ergebnis/pdf/*.pdf") if (m := re.match(r"(\d{4})_", os.path.basename(p)))]
for nr, p in pdfs:
    r = N.get(nr)
    if not r:
        continue
    name = re.sub(r"[^A-Za-z0-9]+", "_", os.path.splitext(os.path.basename(p))[0])[-40:]
    ziel = f"ergebnis/texte_layout/{r['mastr_nr']}_{int(nr):04d}_lieferung_{name}.txt"
    try:
        t = subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True, text=True, timeout=60).stdout
    except Exception:
        continue
    if len(t.strip()) > 200:
        open(ziel, "w", encoding="utf-8").write(t); n += 1
print(n, "Texte aus gelieferten PDFs angelegt")
