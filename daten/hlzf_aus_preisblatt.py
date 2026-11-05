"""Hochlastzeitfenster, die im Text des Preisblatts selbst stehen (kein eigenes Dokument), lesen und in ergebnis/hlzf_ergebnis.csv eintragen.
Nur Netzbetreiber, die dort noch keine gelesene Zeile haben. Aufruf: PYTHONPATH=. python daten/hlzf_aus_preisblatt.py"""
import csv, glob, re, sys
sys.path.insert(0, ".")
from vnb.hlzf import hlzf_lesen, JAHRESZEITEN
tab = list(csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";"))
zeilen = list(csv.reader(open("ergebnis/hlzf_ergebnis.csv", encoding="utf-8-sig"), delimiter=";"))
H, rows = zeilen[0], {r[0]: r for r in zeilen[1:]}
neu = []
for x in tab:
    if x["hlzf_status"] != "kein_dokument_oder_adresse":
        continue
    fs = glob.glob(f"ergebnis/texte_layout/{x['mastr_nr']}_*.txt") + glob.glob(f"ergebnis/texte/{int(x['nr']):04d}.txt")
    t = "\n".join(open(f, errors="ignore").read() for f in fs)
    e = hlzf_lesen(t, x["quelle_url"]) if t else None
    if not e or not e.gelesen or e.jahr != 2026:
        continue
    d = dict.fromkeys(H, ""); d["nr"] = x["nr"]
    for eb in ("NS", "MSNS"):
        for s in JAHRESZEITEN:
            v = e.fenster.get(eb, {}).get(s)
            d[f"hlzf_{eb.lower()}_{s}"] = ", ".join(v) if v else ("keins" if eb in e.fenster else "")
    d["hlzf_quelle_url"] = x["quelle_url"]; d["hlzf_jahr"] = e.jahr; d["hlzf_status"] = "gelesen, Prüfung offen"
    d["hlzf_pruefung"] = "aus dem Preisblatt-Text gelesen"
    rows[x["nr"]] = [d[h] for h in H]; neu.append(x["nr"])
csv.writer(open("ergebnis/hlzf_ergebnis.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";").writerows([H] + sorted(rows.values(), key=lambda r: int(r[0])))
print("neu aus Preisblatt:", neu)
