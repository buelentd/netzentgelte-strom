"""Schlüsseltabelle: MaStR-Nummer (Primärschlüssel) <-> unsere laufende Nr. <-> Nr. der Liste des Nutzers (Warteschlange) <-> Name, Domain, Dateinamen.
Ausgabe: ergebnis/schluessel.csv (eine Zeile je Netzbetreiber) und ergebnis/schluessel_offen.csv (Nutzer-Nummern ohne MaStR-Zuordnung, mit Vorschlägen).
Aufruf: PYTHONPATH=. python daten/schluessel.py"""
import csv, difflib, re
from collections import defaultdict
from urllib.parse import urlparse

tab = list(csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";"))
zu = list(csv.DictReader(open("ergebnis/zuordnung_nutzer_mastr.csv", encoding="utf-8-sig"), delimiter=";"))
nutz = defaultdict(list)
for r in zu:
    if r["unsere_nr"]:
        nutz[r["unsere_nr"]].append(r["nutzer_nr"])

def domain(w):
    if not w:
        return ""
    h = urlparse(w if w.startswith("http") else "http://" + w).netloc or w
    return re.sub(r"^www\.", "", h).lower()

with open("ergebnis/schluessel.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["mastr_nr", "nr", "nutzer_nr", "netzbetreiber", "domain", "dateiname_preisblatt", "dateiname_hochlastzeitfenster"])
    for x in tab:
        n4 = f"{int(x['nr']):04d}"
        w.writerow([x["mastr_nr"], x["nr"], ",".join(nutz.get(x["nr"], [])), x["netzbetreiber"], domain(x["website"]),
                    f"{x['mastr_nr']}_{n4}.pdf", f"{x['mastr_nr']}_{n4}_hlzf.pdf"])

def norm(s):
    s = s.lower().replace("ü", "ue").replace("ä", "ae").replace("ö", "oe")
    return re.sub(r"\b(gmbh|ag|kg|co|mbh|und|e\.?g\.?|netz|netze|stadtwerke|gemeindewerke)\b|[&＆]", "", s)

belegt = {r["unsere_nr"] for r in zu if r["unsere_nr"]}
with open("ergebnis/schluessel_offen.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["nutzer_nr", "nutzer_name", "mastr_nr_gefunden", "vorschlag_nr", "vorschlag_name", "vorschlag_mastr_nr", "vorschlag_schon_vergeben_an_nutzer_nr", "aehnlichkeit", "entscheidung"])
    for r in zu:
        if r["mastr_nr"]:
            continue
        sc = sorted(((difflib.SequenceMatcher(None, norm(r["nutzer_name"]), norm(x["netzbetreiber"])).ratio(), x) for x in tab), key=lambda a: -a[0])[:2]
        for s, x in sc:
            w.writerow([r["nutzer_nr"], r["nutzer_name"], "", x["nr"], x["netzbetreiber"], x["mastr_nr"], ",".join(nutz.get(x["nr"], [])), f"{s:.2f}", ""])
print(len(tab), "Zeilen Schlüssel;", sum(1 for r in zu if not r["mastr_nr"]), "Nutzer-Nummern offen")
