"""Entwurf für Auftrag 7 (Aktion 'ablesen'): je Datei Text mit Zeitzeilen, Teillesung des Maschinenlesers und Seitenbilder (PNG) zum schnellen Abgleich.
Der Entwurf ist NICHT geprüft; er spart nur das Abtippen und das Suchen der Seite. Ausgabe: lauf/hlzf_entwurf_auftrag7.csv und lauf/seiten/<mastr_nr>_s<seite>.png
Aufruf: PYTHONPATH=. python daten/hlzf_entwurf.py [anzahl]"""
import csv, os, re, subprocess, sys
sys.path.insert(0, ".")
from vnb.hlzf import hlzf_lesen, JAHRESZEITEN
ZEIT = re.compile(r"\d{1,2}[:.]\d{2}\s*(?:uhr)?\s*(?:[-–]|bis)\s*\d{1,2}[:.]\d{2}", re.I)

def main(n):
    os.makedirs("lauf/seiten", exist_ok=True)
    R = [r for r in csv.DictReader(open("ergebnis/kollege_hlzf_253.csv", encoding="utf-8-sig"), delimiter=";") if r["aktion"].startswith("ablesen")][:n]
    H = ["mastr_nr", "netzbetreiber", "datei", "jahr_erkannt", "ns_fruehling", "ns_sommer", "ns_herbst", "ns_winter", "msns_fruehling", "msns_sommer", "msns_herbst", "msns_winter", "zeitzeilen_im_text", "seitenbilder", "status"]
    out = []
    for r in R:
        mn = r["mastr_nr"]
        f = r["dateien_im_repo"].split(" | ")[0]
        if not f.lower().endswith(".pdf") or not os.path.exists(f):
            out.append({"mastr_nr": mn, "netzbetreiber": r["netzbetreiber"], "datei": f, "status": "keine PDF-Datei: von Hand"}); continue
        t = subprocess.run(["pdftotext", "-layout", f, "-"], capture_output=True, text=True).stdout
        e = hlzf_lesen(t, f)
        d = {"mastr_nr": mn, "netzbetreiber": r["netzbetreiber"], "datei": f, "jahr_erkannt": e.jahr or "", "status": "ENTWURF ungeprüft (Maschine, Teillesung)"}
        for eb in ("NS", "MSNS"):
            for s in JAHRESZEITEN:
                v = e.fenster.get(eb, {}).get(s)
                d[f"{eb.lower()}_{s}"] = ", ".join(v) if v else ""
        d["zeitzeilen_im_text"] = " // ".join(re.sub(r"\s{2,}", " | ", l.strip()) for l in t.split("\n") if ZEIT.search(l))[:900]
        pre = f"lauf/seiten/{mn}_s"
        subprocess.run(["pdftoppm", "-r", "70", "-png", "-l", "3", f, pre], capture_output=True)
        d["seitenbilder"] = " ".join(sorted(x for x in os.listdir("lauf/seiten") if x.startswith(mn)))
        out.append(d)
    w = csv.DictWriter(open("lauf/hlzf_entwurf_auftrag7.csv", "w", encoding="utf-8-sig", newline=""), fieldnames=H, delimiter=";"); w.writeheader(); w.writerows([{k: o.get(k, "") for k in H} for o in out])
    print(len(out), "Entwürfe")

main(int(sys.argv[1]) if len(sys.argv) > 1 else 200)
