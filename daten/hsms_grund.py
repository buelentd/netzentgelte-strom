"""Warum fehlt HS/MS? Je Netzbetreiber ein Grund -> lauf/hsms_grund.csv (wird von vnb/ergebnis.py in die Spalte hsms_status übernommen).
Codes: gelesen | nicht_ausgewiesen | nur_hochspannung | hochspannung_nur_im_text | null_ausgewiesen | im_dokument_nicht_gelesen | kein_dokument
Aufruf: PYTHONPATH=. python daten/hsms_grund.py   (nach jeder Änderung der Werte neu erzeugen)"""
import csv, glob, re
from pathlib import Path

HS = re.compile(r"hoch\s*-?\s*/?\s*(?:und\s*)?mittel|hochspannung|\bHS\s*/\s*MS\b|\bHSP\s*/\s*MSP\b|110\s*/\s*(?:10|20)\s*kV|netzebene\s*4\b", re.I)
ZAHL = re.compile(r"\d+,\d+")
UMSP = re.compile(r"umspann\w*\s*(?:hoch|hs|hsp|hö)|hoch\w*\s*-?\s*/?\s*mittelspannung", re.I)

def text(r):
    f = glob.glob(f"ergebnis/texte_layout/{r['mastr_nr']}_*.txt") or glob.glob(f"ergebnis/texte/{int(r['nr']):04d}.txt")
    return Path(f[0]).read_text(encoding="utf8", errors="replace").split("\n") if f else None

def main():
    out = []
    for r in csv.DictReader(open("ergebnis/ebenen_erwartung.csv", encoding="utf-8-sig"), delimiter=";"):
        st = r["hsms"]
        if st == "gelesen": grund = "gelesen"
        elif st == "kein_dokument": grund = "kein_dokument"
        elif st == "im_dokument_nicht_gelesen":
            L = text(r) or []
            nullzeile = any(UMSP.search(l) and len(ZAHL.findall(l)) >= 2 and all(float(x.replace(",", ".")) == 0 for x in ZAHL.findall(l)) for l in L)
            grund = "null_ausgewiesen" if nullzeile else "im_dokument_nicht_gelesen"
        else:
            L = text(r) or []
            mit_zahlen = [l for l in L if HS.search(l) and len(ZAHL.findall(l)) >= 2]
            ohne = any(HS.search(l) for l in L)
            grund = "nur_hochspannung" if mit_zahlen else ("hochspannung_nur_im_text" if ohne else "nicht_ausgewiesen")
        out.append([r["mastr_nr"], grund])
    with open("lauf/hsms_grund.csv", "w", encoding="utf-8-sig", newline="") as o:
        w = csv.writer(o, delimiter=";"); w.writerow(["mastr_nr", "hsms_status"]); w.writerows(out)
    from collections import Counter
    print(dict(Counter(g for _, g in out)))
main()
