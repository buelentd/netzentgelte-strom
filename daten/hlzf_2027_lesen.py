"""HLZF-Dokumente für 2027 (eingang/2027_vorlaeufig/SNB…_hlzf_2027.pdf) offline lesen (0 Tokens) und als Overlay-Zeilen mit Status
gelesen_aus_2027 nach lauf/hlzf_2027_gelesen.csv schreiben (Festlegung 12.11.2026: 2027-Fund zählt für 2026 und 2027).
Nur Dokumente mit Jahr 2027, die der Leser eindeutig liest und die keine Prüfmeldung haben. Rest: lauf/hlzf_2027_offen.csv mit Grund.
Aufruf: PYTHONPATH=. python daten/hlzf_2027_lesen.py ; danach die Zeilen in lauf/hlzf_kollege_verifiziert.csv übernehmen (nur wenn Status nicht nutzer/unser, macht hlzf_zusammenfuehren)."""
import csv, glob, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, ".")
from vnb.hlzf import hlzf_lesen, JAHRESZEITEN
from daten.hlzf_regeln import stufe

def zeit_ok(z):
    m = re.fullmatch(r"(\d\d):(\d\d)-(\d\d):(\d\d)", z.strip())
    if not m: return False
    a, b = int(m[1]) * 60 + int(m[2]), int(m[3]) * 60 + int(m[4])
    return 5 * 60 <= a < b <= 23 * 60 + 59 and b - a <= 11 * 60

def main():
    T = {r["mastr_nr"]: r for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
    H = ["mastr_nr", "hlzf_ns_fruehling", "hlzf_ns_sommer", "hlzf_ns_herbst", "hlzf_ns_winter", "hlzf_msns_fruehling", "hlzf_msns_sommer", "hlzf_msns_herbst", "hlzf_msns_winter",
         "hlzf_schwelle_prozent", "hlzf_mindestleistung_kw", "hlzf_quelle_url", "hlzf_status"]
    ok, offen = [], []
    for f in sorted(glob.glob("eingang/2027_vorlaeufig/SNB*_hlzf_2027.pdf")):
        mn = Path(f).name[:15]
        nr = str(int(T[mn]["nr"])) if mn in T else ""
        try:
            t = subprocess.run(["pdftotext", "-layout", f, "-"], capture_output=True, text=True, timeout=60).stdout
        except Exception as e:
            offen.append([mn, Path(f).name, "Datei nicht lesbar"]); continue
        e = hlzf_lesen(t, f)
        stf = stufe(nr, t, e) if e.gelesen else None
        if not stf or not e.gelesen:
            offen.append([mn, Path(f).name, len(t.strip()) < 100 and "kein Text (Scan?)" or (e.grund or "Zeitfenster nicht lesbar")]); continue
        if e.jahr not in (2027,):
            offen.append([mn, Path(f).name, f"Jahr im Dokument: {e.jahr}"]); continue
        d = dict.fromkeys(H, ""); d["mastr_nr"] = mn
        pr = []
        for eb in ("NS", "MSNS"):
            for s in JAHRESZEITEN:
                v = e.fenster.get(eb, {}).get(s)
                d[f"hlzf_{eb.lower()}_{s}"] = ", ".join(v) if v else ("keins" if eb in e.fenster else "")
                if v and not all(zeit_ok(x) for x in v): pr.append(f"{eb} {s}")
        if pr:
            offen.append([mn, Path(f).name, "Zeit unplausibel: " + "; ".join(pr)]); continue
        if stf == "ungeprueft":
            offen.append([mn, Path(f).name, "ungeprüfte Form: " + str(e.form)]); continue
        sc = e.schwelle.get("NS") or e.schwelle.get("MSNS")
        d["hlzf_schwelle_prozent"] = sc if sc is not None else ""
        d["hlzf_mindestleistung_kw"] = e.mindest_kw.get("NS", "") or e.mindest_kw.get("MSNS", "")
        d["hlzf_quelle_url"] = "eingang/2027_vorlaeufig/" + Path(f).name
        d["hlzf_status"] = "gelesen_aus_2027"
        ok.append(d)
    csv.DictWriter(open("lauf/hlzf_2027_gelesen.csv", "w", encoding="utf-8-sig", newline=""), fieldnames=H, delimiter=";").writeheader()
    w = csv.DictWriter(open("lauf/hlzf_2027_gelesen.csv", "w", encoding="utf-8-sig", newline=""), fieldnames=H, delimiter=";"); w.writeheader(); w.writerows(ok)
    w = csv.writer(open("lauf/hlzf_2027_offen.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";"); w.writerow(["mastr_nr", "datei", "grund"]); w.writerows(offen)
    print("gelesen", len(ok), "| offen", len(offen))

main()
