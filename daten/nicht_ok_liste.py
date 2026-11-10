"""Liste aller Netzbetreiber mit Status != ok: MaStR-Nr. zuerst, Website, bekannte Quelle, Google-Suchlinks mit site: OHNE www.
Aufruf: PYTHONPATH=. python daten/nicht_ok_liste.py  ->  ergebnis/nicht_ok_suchliste.csv"""
import csv, re, urllib.parse
BEGRIFFE = ["Netzentgelte Strom 2026 Preisblatt", "Netznutzung Preisblatt 2026 Leistungspreis Arbeitspreis", "Preisblatt Netzentgelte Strom 2026 pdf"]
def domain(w):
    w = re.sub(r"^https?://", "", (w or "").strip().lower()).split("/")[0]
    return re.sub(r"^www\.", "", w)
def link(q):
    return "https://www.google.com/search?q=" + urllib.parse.quote(q)
T = list(csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";"))
K = {r["nr"]: r["website"] for r in csv.DictReader(open("lauf/website_korrektur.csv", encoding="utf-8-sig"), delimiter=";")}   # Korrektur vor MaStR
rows = []
for t in T:
    if t["status"] == "ok":
        continue
    web = K.get(t["nr"]) or t["website"]
    dom = domain(web)
    s = [link(f"site:{dom} {b}") if dom else link(f"{t['netzbetreiber']} {b}") for b in BEGRIFFE]
    rows.append([t["mastr_nr"], t["nr"], t["netzbetreiber"], t["status"], dom, t["quelle_url"] or (web if web.startswith("http") else ""), (t["hinweis"] or "")[:150], *s])
rows.sort(key=lambda r: (r[3], int(r[1])))
H = ["mastr_nr", "nr", "netzbetreiber", "status", "domain_ohne_www", "bekannte_quelle_url", "hinweis", "suche_1", "suche_2", "suche_3"]
w = csv.writer(open("ergebnis/nicht_ok_suchliste.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";"); w.writerow(H); w.writerows(rows)
import collections; print(len(rows), collections.Counter(r[3] for r in rows))
