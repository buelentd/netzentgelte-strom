"""Suchliste Hochlastzeitfenster 2026: Netzbetreiber ohne Fenster in der Tabelle (Status nicht fertig), die der Kollege nicht gefunden hat.
Regel (Festlegung Nutzer 06.11.2026): Google-Suchlinks mit mehreren Begriffen und site: OHNE www. MaStR-Nr. zuerst (Festlegung 09.11.2026).
Eingabe: lauf/hlzf_zusammen.csv, ergebnis/netzentgelte_2026.csv, optional lauf/hlzf_kollege_bemerkung.csv (mastr_nr;bemerkung).
Ausgabe: ergebnis/hlzf_suchliste_offen.csv und .md.   Aufruf: PYTHONPATH=. python daten/hlzf_suchliste.py"""
import csv, re, urllib.parse, os
FERTIG = ("gelesen_nutzer", "gelesen_unser", "gelesen_kollege_verifiziert")
BEGRIFFE = ["Hochlastzeitfenster 2026", "Hochlastzeitfenster 2026 § 19 StromNEV atypische Netznutzung", "Hochlastzeitfenster Netznutzung Strom pdf"]
def domain(w):
    w = re.sub(r"^https?://", "", (w or "").strip().lower()).split("/")[0]
    return re.sub(r"^www\.", "", w)
def link(dom, b): return "https://www.google.com/search?q=" + urllib.parse.quote(f"site:{dom} {b}")
T = {r["mastr_nr"]: r for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
bem = {}
if os.path.exists("lauf/hlzf_kollege_bemerkung.csv"):
    bem = {r["mastr_nr"]: r["bemerkung"] for r in csv.DictReader(open("lauf/hlzf_kollege_bemerkung.csv", encoding="utf-8-sig"), delimiter=";")}
rows = []
for z in csv.DictReader(open("lauf/hlzf_zusammen.csv", encoding="utf-8-sig"), delimiter=";"):
    if z["hlzf_status"] in FERTIG or z["hlzf_status"] == "gelesen_kollege_ungeprueft": continue
    t = T[z["mastr_nr"]]; dom = domain(t["website"])
    rows.append([z["mastr_nr"], t["nr"], t["netzbetreiber"], z["hlzf_status"], dom or "(keine Website)", z["hlzf_quelle_url"], "ja" if z["mastr_nr"] in bem else "nein", bem.get(z["mastr_nr"], ""),
                 *([link(dom, b) for b in BEGRIFFE] if dom else ["", "", ""])])
H = ["mastr_nr", "nr", "netzbetreiber", "status", "domain_ohne_www", "bisherige_url", "kollege_ohne_werte", "bemerkung_kollege", *[f"suche_{i+1}" for i in range(len(BEGRIFFE))]]
w = csv.writer(open("ergebnis/hlzf_suchliste_offen.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";"); w.writerow(H); w.writerows(rows)
md = [f"# Hochlastzeitfenster 2026: {len(rows)} Netzbetreiber ohne fertiges Fenster", "",
      "Im Browser das HLZF-Dokument 2026 holen (PDF, Excel oder Webseite mit Tabelle). Als `<MaStR-Nr>_hlzf_<Originalname>.pdf` speichern. 2026 vor 2027. Suchlinks: `site:` ohne www.", "",
      "| MaStR-Nr. | Netzbetreiber | Status | Domain | bisherige URL | Kollege ohne Werte | Suche 1 | Suche 2 | Suche 3 |", "|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    md.append(f"| {r[0]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | " + " | ".join(f"[{i+1}]({u})" if u else "" for i, u in enumerate(r[8:])) + " |")
open("ergebnis/hlzf_suchliste_offen.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
print(len(rows), "Zeilen")
