"""PDFs aus eingang/ (auch Unterordner) automatisch verarbeiten:
 1. Dateiname -> Netzbetreiber (MaStR-Nr_unsere-Nr.pdf wie in liste_gesperrte_pdfs.csv, oder p_<Nutzer-Nr>.pdf)
 2. pdftotext -layout -> ergebnis/texte_layout/<MaStR>_<Nr>.txt (vorhandene nicht leere Texte werden übersprungen, --neu erzwingt)
 3. Leser, Parser, Tabelle, Ebenen-Erwartung, HS/MS-Grund neu rechnen
 4. verarbeitete PDFs nach eingang/verarbeitet/ verschieben, Bericht ergebnis/eingang_bericht.csv
Aufruf: PYTHONPATH=. python daten/eingang_verarbeiten.py [--neu] [--ohne-rechnen]"""
import csv, glob, os, re, shutil, subprocess, sys
from pathlib import Path

def zuordnung():
    n2m = {}
    for r in csv.DictReader(open("ergebnis/zuordnung_nutzer_mastr.csv", encoding="utf-8-sig"), delimiter=";"):
        if r["mastr_nr"]: n2m[r["nutzer_nr"]] = (r["mastr_nr"], r["unsere_nr"])
    unser = {r["nr"]: r["mastr_nr"] for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
    return n2m, unser

def ziel(datei, n2m, unser):
    stem = Path(datei).stem
    m = re.match(r"(SNB\d+)_(\d+)", stem)
    if m and m.group(2).lstrip("0") in unser:
        return m.group(1), m.group(2).lstrip("0")
    m = re.match(r"p_(\d+)$", stem)
    if m and m.group(1) in n2m:
        return n2m[m.group(1)]
    m = re.match(r"(\d+)", stem)             # nur die Nummer (unsere Nr.)
    if m and m.group(1).lstrip("0") in unser:
        return unser[m.group(1).lstrip("0")], m.group(1).lstrip("0")
    return None

def main(neu, rechnen):
    n2m, unser = zuordnung()
    os.makedirs("ergebnis/texte_layout", exist_ok=True); os.makedirs("eingang/verarbeitet", exist_ok=True)
    bericht = []
    for f in sorted(glob.glob("eingang/**/*.pdf", recursive=True)):
        if "verarbeitet" in f or "_hlzf" in f: continue   # HLZF-Dateien: daten/hlzf_eingang.py
        z = ziel(f, n2m, unser)
        if not z:
            bericht.append([f, "", "", "keine Zuordnung (Dateiname nicht erkannt)"]); continue
        mastr, nr = z
        txt = f"ergebnis/texte_layout/{mastr}_{int(nr):04d}.txt"
        if os.path.exists(txt) and os.path.getsize(txt) > 200 and not neu:
            bericht.append([f, mastr, nr, "Text liegt schon vor, übersprungen"]); continue
        try:
            subprocess.run(["pdftotext", "-layout", f, txt], capture_output=True, timeout=60)
        except subprocess.TimeoutExpired:
            bericht.append([f, mastr, nr, "Zeitüberschreitung bei pdftotext"]); continue
        groesse = os.path.getsize(txt) if os.path.exists(txt) else 0
        if groesse < 200:
            bericht.append([f, mastr, nr, f"kaum Text ({groesse} Byte): Bild-PDF oder leer"]); continue
        shutil.move(f, f"eingang/verarbeitet/{Path(f).name}")
        bericht.append([f, mastr, nr, f"umgewandelt ({groesse} Byte)"])
    with open("ergebnis/eingang_bericht.csv", "w", encoding="utf-8-sig", newline="") as o:
        w = csv.writer(o, delimiter=";"); w.writerow(["datei", "mastr_nr", "unsere_nr", "ergebnis"]); w.writerows(bericht)
    ok = sum(1 for b in bericht if b[3].startswith("umgewandelt"))
    print(len(bericht), "Dateien,", ok, "neu umgewandelt")
    for b in bericht:
        if not b[3].startswith("umgewandelt"): print("  ", b)
    if rechnen and ok:
        for cmd in (["daten/leser_alle_texte.py"], ["daten/leser_uebernehmen.py", "--schreiben"], ["run.py", "bericht"],
                    ["daten/ebenen_erwartung.py"], ["daten/rlm_uebernehmen.py", "--schreiben"], ["daten/slp_uebernehmen.py", "--schreiben"],
                    ["daten/paar_uebernehmen.py", "--schreiben"], ["run.py", "bericht"], ["daten/ebenen_erwartung.py"], ["daten/hsms_grund.py"], ["run.py", "bericht"]):
            subprocess.run([sys.executable] + cmd, env={**os.environ, "PYTHONPATH": "."}, stdout=subprocess.DEVNULL)
        print("Tabelle neu berechnet (ergebnis/netzentgelte_2026.csv)")
main("--neu" in sys.argv, "--ohne-rechnen" not in sys.argv)
