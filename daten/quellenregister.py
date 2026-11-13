"""Quellenregister: je MaStR-Nr. und Art (preis_2026, preis_2027, hlzf) die Herkunft des Dokuments.
Spalten: mastr_nr; netzbetreiber; art; quelle (Web-Adresse oder lokale Datei); quelle_ist_web; wer (aus dem Status); stand.
Wo nur ein lokaler Pfad bekannt ist (Upload vom Nutzer/Kollegen), steht quelle_ist_web = nein: die Original-Adresse fehlt dort und wird nachgetragen."""
import csv
L = lambda p: list(csv.DictReader(open(p, encoding="utf-8-sig"), delimiter=";"))
N = L("ergebnis/netzentgelte_2026.csv"); M = {r["mastr_nr"]: r for r in L("ergebnis/netzentgelte_2027_vorlaeufig.csv")}
Z = {r["mastr_nr"]: r for r in L("lauf/hlzf_zusammen.csv")}
WER = {"gelesen_nutzer": "Nutzer", "gelesen_unser": "Crawler/Claude", "gelesen_kollege_verifiziert": "Kollege (verifiziert)", "gelesen_aus_2027": "2027-Dokument"}
out = []
def add(k, n, art, q, wer=""):
    if q:
        out.append({"mastr_nr": k, "netzbetreiber": n, "art": art, "quelle": q, "quelle_ist_web": "ja" if q.startswith("http") else "nein", "wer": wer})
for r in N:
    k = r["mastr_nr"]; n = r["netzbetreiber"]
    add(k, n, "preis_2026", r.get("quelle_url", ""), r.get("status", ""))
    add(k, n, "preis_2027", M.get(k, {}).get("quelle_url", ""), M.get(k, {}).get("status", ""))
    z = Z.get(k, {})
    add(k, n, "hlzf", z.get("hlzf_quelle_url", ""), WER.get(z.get("hlzf_status", ""), z.get("hlzf_status", "")))
w = csv.DictWriter(open("ergebnis/quellenregister.csv", "w", encoding="utf-8-sig", newline=""), fieldnames=list(out[0]), delimiter=";")
w.writeheader(); w.writerows(out)
from collections import Counter
print(len(out), Counter((o["art"], o["quelle_ist_web"]) for o in out))
