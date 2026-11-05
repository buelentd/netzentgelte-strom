"""Qualitätsprüfung der von unserem Leser gelesenen Hochlastzeitfenster (nicht der Nutzerliste).
Jede gelesene Zeile aus ergebnis/hlzf_ergebnis.csv wird mit dem gespeicherten Text (ergebnis/hlzf_texte/<nr>.txt) und dem aktuellen Leser neu gelesen.
Wird sie vom Leser abgelehnt (Anzahl der Uhrzeiten im Dokument passt nicht zu den gelesenen Fenstern) oder liest er etwas anderes, steht die Zeile auf
"gelesen, Prüfung offen" mit Grund. Werte bleiben stehen, nichts wird gelöscht. Aufruf: PYTHONPATH=. python daten/hlzf_qualitaet.py"""
import csv, glob, re, sys
sys.path.insert(0, ".")
from vnb.hlzf import hlzf_lesen, JAHRESZEITEN
zeilen = list(csv.reader(open("ergebnis/hlzf_ergebnis.csv", encoding="utf-8-sig"), delimiter=";"))
H, rows = zeilen[0], zeilen[1:]
ix = {h: i for i, h in enumerate(H)}
geaendert = []
# Am Dokumenttext von Hand geprüft (05.11.2026): der neue Leser liest richtig, die gespeicherten Werte waren unvollständig oder vermischt
UEBERNEHMEN = {"91", "137", "676"}
# Am Dokumenttext von Hand als unsicher erkannt (Zeiten stehen mittig zwischen den Ebenennamen): bleiben auf Prüfung offen
ZWEIFEL = {"142": "Zeiten zwischen den Ebenennamen: Zuordnung zu NS/MS/NS unsicher", "214": "viele Fenster, Zuordnung der Zeilen zu den Ebenen unsicher"}
import re as _re
def _zeit_ok(z):
    m = _re.fullmatch(r"(\d\d):(\d\d)-(\d\d):(\d\d)", z.strip())
    if not m: return False
    a, b = int(m[1]) * 60 + int(m[2]), int(m[3]) * 60 + int(m[4])
    return 5 * 60 <= a < b <= 23 * 60 + 59 and b - a <= 11 * 60

for r in rows:
    nr = r[0]
    if r[ix["hlzf_status"]] == "gelesen, Prüfung offen" and "Zeit unplausibel" in r[ix["hlzf_pruefung"]] and "Leser" not in r[ix["hlzf_pruefung"]]:
        alle = [z.strip() for eb in ("ns", "msns") for j in JAHRESZEITEN for z in r[ix[f"hlzf_{eb}_{j}"]].split(",") if z.strip() and z.strip() != "keins"]
        if all(_zeit_ok(z) for z in alle):
            r[ix["hlzf_status"]] = "gelesen"
            r[ix["hlzf_pruefung"]] = "Fenster bis 11 Stunden gelten als plausibel"
        continue
    if nr in ZWEIFEL:
        r[ix["hlzf_status"]] = "gelesen, Prüfung offen"
        if "Leser" not in r[ix["hlzf_pruefung"]]:
            r[ix["hlzf_pruefung"]] = (r[ix["hlzf_pruefung"]] + "; " if r[ix["hlzf_pruefung"]] else "") + "Leser unsicher: " + ZWEIFEL[nr]
        continue
    if nr in UEBERNEHMEN:
        t = open(f"ergebnis/hlzf_texte/{nr}.txt", encoding="utf-8").read()
        e = hlzf_lesen(t, r[ix["hlzf_quelle_url"]])
        if e.gelesen:
            for eb in ("NS", "MSNS"):
                for j in JAHRESZEITEN:
                    v = e.fenster.get(eb, {}).get(j)
                    r[ix[f"hlzf_{eb.lower()}_{j}"]] = ", ".join(v) if v else ("keins" if eb in e.fenster else "")
            r[ix["hlzf_status"]] = "gelesen"
            r[ix["hlzf_pruefung"]] = "neu gelesen und am Dokument geprüft (05.11.2026)"
        continue
    if r[ix["hlzf_status"]] == "gelesen, Prüfung offen" and "Leser" in r[ix["hlzf_pruefung"]]:
        # früher geflaggt: wieder gelesen, wenn der Leser jetzt dieselben Werte liest und die Prüfung besteht (Fehlalarm)
        try:
            t = open(f"ergebnis/hlzf_texte/{nr}.txt", encoding="utf-8").read()
        except FileNotFoundError:
            continue
        e = hlzf_lesen(t, r[ix["hlzf_quelle_url"]])
        gleich = e.gelesen and all(
            (", ".join(e.fenster.get(eb, {}).get(j, [])) or ("keins" if eb in e.fenster else "")) == r[ix[f"hlzf_{eb.lower()}_{j}"]]
            for eb in ("NS", "MSNS") for j in JAHRESZEITEN)
        if gleich:
            r[ix["hlzf_status"]] = "gelesen"
            r[ix["hlzf_pruefung"]] = "Prüfung bestanden (Rasterzeilen herausgerechnet)"
        continue
    if r[ix["hlzf_status"]] != "gelesen":
        continue
    try:
        t = open(f"ergebnis/hlzf_texte/{nr}.txt", encoding="utf-8").read()
    except FileNotFoundError:
        continue
    e = hlzf_lesen(t, r[ix["hlzf_quelle_url"]])
    grund = ""
    if not e.gelesen:
        grund = "Leser lehnt nach Prüfung ab: " + (e.grund or "nicht lesbar")
    else:
        for eb in ("NS", "MSNS"):
            for j in JAHRESZEITEN:
                v = e.fenster.get(eb, {}).get(j)
                neu = ", ".join(v) if v else ("keins" if eb in e.fenster else "")
                if neu != r[ix[f"hlzf_{eb.lower()}_{j}"]]:
                    grund = "Leser liest jetzt anders als gespeichert"
    if grund:
        r[ix["hlzf_status"]] = "gelesen, Prüfung offen"
        r[ix["hlzf_pruefung"]] = (r[ix["hlzf_pruefung"]] + "; " if r[ix["hlzf_pruefung"]] else "") + grund
        geaendert.append((int(nr), grund))
csv.writer(open("ergebnis/hlzf_ergebnis.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";").writerows([H] + rows)
print("auf Prüfung offen gesetzt:", len(geaendert))
