"""Übernimmt Preisblätter aus eingang/neue preise (SNB…_NNNN.pdf, auch _SLP/_RLM/_LM-Suffix) als Dokumenttext.
Je Datei Dokumentprüfung (daten/dokument_pruefen.py): OK oder PRUEFEN nur wegen Form-Hinweisen (Titel, Einheit) wird übernommen; Name fehlt/kein Text/FALSCH nie, mehrere Dateien je Netzbetreiber werden zusammengefügt
(Datei-Trennzeile). Der alte Text bleibt als .alt erhalten. Bericht: ergebnis/neue_preise_bericht.csv.
Aufruf: PYTHONPATH=. python daten/neue_preise_uebernehmen.py [Ordner]"""
import csv, glob, os, re, sys, shutil
sys.path.insert(0, ".")
src = open("daten/eingang_verarbeiten.py", encoding="utf-8").read().split("def main(")[0]
exec(src)
from daten.dokument_pruefen import pruefen
ordner = sys.argv[1] if len(sys.argv) > 1 else "eingang/neue preise"
n2m, unser = zuordnung()
name_von = {r["nr"]: r["netzbetreiber"] for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
gruppen = {}
for f in sorted(glob.glob(f"{ordner}/*")):
    if f.endswith(".txt") or os.path.isdir(f):
        continue
    z = ziel(f, n2m, unser)
    if z:
        gruppen.setdefault(z, []).append(f)
bericht = []
for (mastr, nr), fs in gruppen.items():
    teile, ok = [], []
    for f in fs:
        st, gr = pruefen("preis", f, name_von.get(nr, ""))
        tmp = "/tmp/pb_neu.txt"
        if os.path.exists(tmp): os.remove(tmp)
        fehler = datei_text(f, tmp)
        akzept = st == "OK" or (st == "PRUEFEN" and all(g.startswith(("Titel/Anfang", "Preisblatt unvollständig")) for g in gr))   # Name im Dokument, nur Form-Hinweise
        if akzept and not fehler and os.path.exists(tmp) and os.path.getsize(tmp) >= 200:
            teile.append((f, open(tmp, errors="ignore").read())); ok.append(os.path.basename(f))
        bericht.append([nr, name_von.get(nr, ""), os.path.basename(f), st, "; ".join(gr)[:200] + (f"; Umwandlung: {fehler}" if fehler else "")])
    if not teile:
        continue
    txt = f"ergebnis/texte_layout/{mastr}_{int(nr):04d}.txt"
    if os.path.exists(txt) and not os.path.exists(txt + ".alt"):
        shutil.copy(txt, txt + ".alt")
    inhalt = "\n\n".join((f"=== Datei {os.path.basename(f)} ===\n" if len(teile) > 1 else "") + t for f, t in teile)
    open(txt, "w", encoding="utf-8").write(inhalt)
with open("ergebnis/neue_preise_bericht.csv", "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.writer(fh, delimiter=";"); w.writerow(["nr", "netzbetreiber", "datei", "pruefung", "gruende"]); w.writerows(bericht)
import collections
print(collections.Counter(b[3] for b in bericht), "| Netzbetreiber übernommen:", sum(1 for b in bericht if b[3] == "OK" and True) and len({b[0] for b in bericht if b[3] == "OK"}))
