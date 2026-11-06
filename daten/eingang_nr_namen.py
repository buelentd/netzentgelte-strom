"""Neue Lieferung des Kollegen mit Dateinamen '<nr>_preis_<Original>.pdf' und '<nr>_hlzf_<Original>.pdf' (nr = unsere Nummer):
kopiert sie unter die Namen, die unsere Einleser erwarten (SNB…_NNNN.pdf bzw. SNB…_NNNN_hlzf.pdf) in temporäre Ordner
eingang/_tmp_preis und eingang/_tmp_hlzf (nicht ins Git). Mehrere Dateien je Nummer werden durchnummeriert.
Aufruf: PYTHONPATH=. python daten/eingang_nr_namen.py [Ordner]   danach: neue_preise_uebernehmen.py eingang/_tmp_preis und hlzf_eingang.py"""
import csv, os, re, shutil, sys
from pathlib import Path
ordner = Path(sys.argv[1] if len(sys.argv) > 1 else "eingang/überarbeitet")
m = {r["nr"]: r["mastr_nr"] for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
for d in ("eingang/_tmp_preis", "eingang/_tmp_hlzf"):
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
import hashlib
def md5(pfad):
    return hashlib.md5(open(pfad, "rb").read()).hexdigest()
bekannt = {}
for g in Path("eingang").rglob("*"):
    if g.is_file() and ordner not in g.parents and "_tmp_" not in str(g):
        try: bekannt.setdefault(md5(g), str(g))
        except OSError: pass
dubletten = []
zaehl, bericht = {}, []
for f in sorted(ordner.iterdir()):
    mm = re.match(r"^(\d+)_(preis|hlzf)_(.*)$", f.name)
    if not mm or f.is_dir():
        bericht.append((f.name, "Name nicht erkannt")); continue
    nr, art, rest = mm.group(1), mm.group(2), mm.group(3)
    if nr not in m:
        bericht.append((f.name, "Nummer unbekannt")); continue
    h = md5(f)
    if h in bekannt:
        dubletten.append((f.name, bekannt[h]))
    k = (nr, art); zaehl[k] = zaehl.get(k, 0) + 1
    suffix = f".{f.suffix.lstrip('.')}" if f.suffix else ".pdf"
    ext = f.suffix.lower() or ".pdf"
    ziel = f"{m[nr]}_{int(nr):04d}" + ("_hlzf" if art == "hlzf" else "") + (f"_{zaehl[k]}" if zaehl[k] > 1 else "") + ext
    shutil.copy(f, f"eingang/_tmp_{art}/{ziel}")
    bericht.append((f.name, f"-> _tmp_{art}/{ziel}"))
with open("ergebnis/eingang_dubletten.csv", "w", encoding="utf-8-sig", newline="") as fh:
    cw = csv.writer(fh, delimiter=";"); cw.writerow(["datei", "identisch_mit"]); cw.writerows(dubletten)
print(len(dubletten), "Dubletten (gleicher Inhalt wie bereits vorhandene Datei), Liste: ergebnis/eingang_dubletten.csv")
print(sum(1 for k in zaehl if k[1] == "preis"), "Netzbetreiber mit Preisblatt,", sum(1 for k in zaehl if k[1] == "hlzf"), "mit Hochlastzeitfenster;", sum(1 for b in bericht if "erkannt" in b[1] or "unbekannt" in b[1]), "nicht zugeordnet")
