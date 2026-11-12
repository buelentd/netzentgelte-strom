"""Formatprüfung einer HLZF-Lieferung des Kollegen (z. B. ergebnis/hlzf/hlzf_auftrag7_gelesen.csv). 0 Tokens.
Prüft: MaStR-Nr. zuerst und bekannt, Jahr 2026/2027, Zeiten im Format HH:MM-HH:MM (mehrere mit ', '), Zeit plausibel (5:00 bis 23:59, höchstens 11 h je Fenster),
je Ebene mindestens eine Jahreszeit gefüllt (sonst leer lassen), 'keins' nur zusammen mit gefüllten Feldern derselben Ebene, Bemerkung bei leerer Ebene.
Aufruf: PYTHONPATH=. python daten/hlzf_lieferung_pruefen.py <datei.csv>"""
import csv, re, sys
J = ("fruehling", "sommer", "herbst", "winter")
def ok(z):
    m = re.fullmatch(r"(\d\d):(\d\d)-(\d\d):(\d\d)", z.strip())
    if not m: return False
    a, b = int(m[1]) * 60 + int(m[2]), int(m[3]) * 60 + int(m[4])
    return 5 * 60 <= a < b <= 23 * 60 + 59 and b - a <= 11 * 60
def main(p):
    T = {r["mastr_nr"] for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
    R = list(csv.DictReader(open(p, encoding="utf-8-sig"), delimiter=";"))
    if not R or list(R[0].keys())[0] != "mastr_nr":
        print("Erste Spalte muss mastr_nr sein"); sys.exit(1)
    fehler = 0
    for r in R:
        f = []
        if r["mastr_nr"] not in T: f.append("MaStR-Nr. unbekannt")
        if r.get("jahr") not in ("2026", "2027"): f.append("Jahr nicht 2026/2027")
        for eb in ("ns", "msns"):
            w = [r.get(f"{eb}_{j}", "").strip() for j in J]
            for j, v in zip(J, w):
                if v and v != "keins" and not all(ok(z) for z in v.split(",")): f.append(f"{eb} {j}: Zeit unplausibel oder falsches Format '{v}'")
            if any(v == "keins" for v in w) and not any(v and v != "keins" for v in w) and not r.get("bemerkung"):
                f.append(f"{eb}: nur 'keins' ohne Bemerkung (steht 'entfällt' im Dokument?)")
        if not any(r.get(f"{e}_{j}", "").strip() not in ("", "keins") for e in ("ns", "msns") for j in J) and not r.get("bemerkung"):
            f.append("keine Zeiten und keine Bemerkung")
        if f:
            fehler += 1; print(r["mastr_nr"], (r.get("netzbetreiber") or "")[:28], "-", "; ".join(f))
    print(len(R), "Zeilen,", fehler, "mit Fehlern")
    sys.exit(1 if fehler else 0)
main(sys.argv[1])
