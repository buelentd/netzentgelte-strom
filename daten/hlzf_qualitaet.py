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
for r in rows:
    nr = r[0]
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
