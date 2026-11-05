"""Neue Preisblätter aus eingang/ einlesen: prüfen (dokument_pruefen), mit dem vorhandenen Text vergleichen, besseren Text speichern.
Der Text eines Netzbetreibers wird nur ersetzt, wenn das neue Dokument nicht FALSCH ist und mehr Preismerkmale hat als der alte Text (oder es keinen gibt).
Aufruf: PYTHONPATH=. python daten/preisblatt_einlesen.py [Ordner]"""
import csv, glob, os, re, sys
sys.path.insert(0, ".")
sys.path.insert(0, "daten")
import warnings; warnings.filterwarnings("ignore")
exec(open("daten/eingang_verarbeiten.py", encoding="utf-8").read().split("def main(")[0])
from dokument_pruefen import pruefen, text_lesen

def score(t):
    return sum(bool(re.search(p, t)) for p in (r"(?i)niederspannung|umspann", r"(?i)ct\s*/\s*kwh|cent", r"(?i)€\s*/\s*kw|eur\s*/\s*kw|euro\s*/\s*kw",
                                                 r"(?i)jahresleistungspreis|leistungspreis|arbeitspreis", r"(?i)preisblatt|netzentgelt|netznutzung"))

def main(ordner):
    n2m, unser = zuordnung()
    nm = {r["nr"]: r["netzbetreiber"] for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
    bericht = []
    for f in sorted(glob.glob(ordner + "/*")):
        if not os.path.isfile(f):
            continue
        z = ziel(f, n2m, unser)
        if not z:
            bericht.append([os.path.basename(f), "", "", "keine Zuordnung"]); continue
        mastr, nr = z
        name = nm.get(str(int(nr)), "")
        ziel_txt = f"ergebnis/texte_layout/{mastr}_{int(nr):04d}.txt"
        tmp = "/tmp/pb_neu.txt"
        if os.path.exists(tmp):
            os.remove(tmp)
        if f.lower().endswith(".txt"):
            open(tmp, "w", encoding="utf-8").write(open(f, errors="replace").read())
        else:
            fehler = datei_text(f, tmp)
            if fehler or not os.path.exists(tmp):
                bericht.append([os.path.basename(f), nr, name, "nicht lesbar: " + (fehler or "kein Text")]); continue
        neu = open(tmp, errors="ignore").read()
        if len(neu.strip()) < 200:
            bericht.append([os.path.basename(f), nr, name, "kaum Text (Scan?)"]); continue
        st, gr = pruefen("preis", f if not f.lower().endswith(".txt") else tmp, name)
        alt = open(ziel_txt, errors="ignore").read() if os.path.exists(ziel_txt) else ""
        besser = (not alt) or score(neu) > score(alt) or (score(neu) == score(alt) and len(neu) > len(alt) * 1.3)
        if st == "FALSCH":
            bericht.append([os.path.basename(f), nr, name, "FALSCH: " + "; ".join(gr)[:90]])
        elif besser:
            os.replace(tmp, ziel_txt)
            bericht.append([os.path.basename(f), nr, name, f"{st}: Text ersetzt (Merkmale {score(alt)} -> {score(neu)})"])
        else:
            bericht.append([os.path.basename(f), nr, name, f"{st}: vorhandener Text bleibt (Merkmale {score(alt)} / neu {score(neu)})"])
    with open("ergebnis/preisblatt_einlesen_bericht.csv", "w", encoding="utf-8-sig", newline="") as o:
        w = csv.writer(o, delimiter=";"); w.writerow(["datei", "nr", "netzbetreiber", "ergebnis"]); w.writerows(bericht)
    import collections
    print(collections.Counter(b[3].split(":")[0].split(" (")[0][:28] for b in bericht))
    return bericht

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "eingang/NEUE PREISBLAETTER")
