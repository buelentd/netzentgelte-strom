"""Liefert den Ordner data_quellen/netzentgelte_<jahr>/ im Layout, das scripts/netzentgelte_import.py der Conplot-Web-App erwartet:
netzentgelte_<jahr>.csv, plz_netzbetreiber.csv, LEGENDE.md. Ausgabe: ergebnis/conplot/data_quellen/netzentgelte_2026/.
Der Importer übernimmt jedes befüllte hlzf-Feld ungeprüft; deshalb stehen Hochlastzeitfenster hier nur, wenn hlzf_status fertig ist.
Aufruf: PYTHONPATH=. python daten/conplot_data_quellen.py"""
import csv, re, shutil
from pathlib import Path

FERTIG = ("gelesen_nutzer", "gelesen_unser", "gelesen_kollege_verifiziert", "gelesen_aus_2027")
J = ("fruehling", "sommer", "herbst", "winter")
HL = [f"hlzf_{e}_{j}" for e in ("ns", "msns") for j in J] + ["hlzf_schwelle_prozent", "hlzf_mindestleistung_kw", "hlzf_quelle_url"]


def unplausibel(t):
    """Fenster mit Ende vor oder gleich Anfang, die keine Nachtfenster sind (Beginn ab 18:00, Ende bis 06:00), oder ungültige Minuten."""
    for e in ("ns", "msns"):
        for j in J:
            for teil in re.split(r"[,/]", t.get(f"hlzf_{e}_{j}", "") or ""):
                m = re.fullmatch(r"\s*(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})\s*", teil)
                if not m:
                    continue
                a, b, c, d = (int(x) for x in m.groups())
                if b > 59 or d > 59:
                    return True
                s_, e_ = a * 60 + b, c * 60 + d
                if e_ <= s_ and not (s_ >= 18 * 60 and e_ <= 6 * 60):
                    return True
    return False


def lesen(p):
    return list(csv.DictReader(open(p, encoding="utf-8-sig"), delimiter=";"))


def main():
    ziel = Path("ergebnis/conplot/data_quellen/netzentgelte_2026")
    ziel.mkdir(parents=True, exist_ok=True)
    T = lesen("ergebnis/netzentgelte_2026.csv")
    H = {r["mastr_nr"]: r for r in lesen("lauf/hlzf_zusammen.csv")}
    kopf = list(T[0].keys())
    ok = 0
    for t in T:
        h = H.get(t["mastr_nr"], {})
        fertig = h.get("hlzf_status") in FERTIG
        for c in HL:
            t[c] = h.get(c, "") if fertig else ""
        t["hlzf_status"] = h.get("hlzf_status", "") or t.get("hlzf_status", "")
        if fertig and unplausibel(t):
            for c in HL:
                t[c] = ""
            t["hlzf_status"] = "pruefung_offen"
            fertig = False
        ok += fertig
    w = csv.DictWriter(open(ziel / "netzentgelte_2026.csv", "w", encoding="utf-8-sig", newline=""), fieldnames=kopf, delimiter=";")
    w.writeheader()
    w.writerows(T)
    shutil.copy("ergebnis/plz_netzbetreiber.csv", ziel / "plz_netzbetreiber.csv")
    shutil.copy("LEGENDE.md", ziel / "LEGENDE.md")
    print(len(T), "Netzbetreiber,", ok, "mit Hochlastzeitfenstern; Ordner", ziel)


main()
