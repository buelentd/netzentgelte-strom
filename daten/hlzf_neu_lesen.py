"""Liest alle gespeicherten Hochlastzeitfenster-Texte (ergebnis/hlzf_texte) mit dem aktuellen Leser neu, aber nur für Netzbetreiber, die noch nicht als gelesen gelten.
Gelingt es (Leser liest, Sicherungsprüfung bestanden, Jahr 2026 oder unbekannt), wird die Zeile in ergebnis/hlzf_ergebnis.csv ersetzt.
Aufruf: PYTHONPATH=. python daten/hlzf_neu_lesen.py [--zeigen]"""
import csv, glob, re, sys
sys.path.insert(0, ".")
from vnb.hlzf import hlzf_lesen, JAHRESZEITEN, _vollstaendig, _IGN
z = list(csv.reader(open("ergebnis/hlzf_ergebnis.csv", encoding="utf-8-sig"), delimiter=";"))
H, rows = z[0], {r[0]: r for r in z[1:]}
ix = {h: i for i, h in enumerate(H)}
neu = []
for f in glob.glob("ergebnis/hlzf_texte/*.txt"):
    nr = re.search(r"(\d+)\.txt$", f)[1]
    r = rows.get(nr)
    if r is not None and r[ix["hlzf_status"]] == "gelesen":
        continue
    t = open(f, encoding="utf-8").read()
    e = hlzf_lesen(t, r[ix["hlzf_quelle_url"]] if r else "")
    if not e.gelesen or e.jahr not in (2026, None):
        continue
    if not _vollstaendig(t, e.fenster):
        continue                                   # Uhrzeiten im Text, die der Leser nicht untergebracht hat: nicht übernehmen
    d = dict.fromkeys(H, ""); d["nr"] = nr
    for eb in ("NS", "MSNS"):
        for j in JAHRESZEITEN:
            v = e.fenster.get(eb, {}).get(j)
            d[f"hlzf_{eb.lower()}_{j}"] = ", ".join(v) if v else ("keins" if eb in e.fenster else "")
    sc = e.schwelle.get("NS") or e.schwelle.get("MSNS")
    d["hlzf_schwelle_prozent"] = sc if sc is not None else ""
    d["hlzf_mindestleistung_kw"] = e.mindest_kw.get("NS", "") or e.mindest_kw.get("MSNS", "")
    d["hlzf_quelle_url"] = r[ix["hlzf_quelle_url"]] if r else ""
    d["hlzf_jahr"] = e.jahr or ""
    sicher = e.form in ("Block je Ebene (Netzebene / Jahreszeit / Zeiten)", "Ebenen als Spalten (von/bis)", "Ebene mit Jahreszeiten-Spalten (von/bis)",
                        "Ebenen-Zeilen unter Jahreszeiten-Kopf (von/bis)", "Tabelle nach Positionen")
    d["hlzf_status"] = "gelesen" if sicher else "gelesen, Prüfung offen"
    d["hlzf_pruefung"] = ("neu gelesen (Form: " + e.form + ")") if sicher else ("ungeprüft neu gelesen (Form: " + e.form + "), Zuordnung der Zeilen zu den Ebenen nicht am Dokument bestätigt")
    rows[nr] = [d[h] for h in H]
    neu.append((int(nr), e.form))
if "--zeigen" not in sys.argv:
    csv.writer(open("ergebnis/hlzf_ergebnis.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";").writerows([H] + sorted(rows.values(), key=lambda r: int(r[0])))
print(len(neu), "neu gelesen:", sorted(neu)[:80])
