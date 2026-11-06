"""Liste der Dokumente, die im Browser geholt werden müssen (Arbeitsliste, Zeilen mit preise_wer = Nutzer (Browser)).
Regel (Festlegung Nutzer, 06.11.2026): Google-Suchlinks mit Suchbegriffen und site: OHNE www. (z. B. site:eks.ch, nicht site:www.eks.ch).
Ausgabe: ergebnis/browser_downloads_33.csv und BROWSER_DOWNLOADS_33.md.
Aufruf: PYTHONPATH=. python daten/browser_liste.py"""
import csv, re, urllib.parse
BEGRIFFE = ["Netzentgelte Strom 2026 Preisblatt", "Netznutzung Preisblatt 2026 Leistungspreis Arbeitspreis", "Preisblatt Netzentgelte Strom 2026 pdf"]
a = list(csv.DictReader(open("ergebnis/arbeitsliste.csv", encoding="utf-8-sig"), delimiter=";"))
T = {r["nr"]: r for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
Q = {}
for r in csv.DictReader(open("lauf/quellen_recherche.csv", encoding="utf-8-sig"), delimiter=";"):
    Q.setdefault(r["nr"], []).append(r["url"])
def domain(w):
    w = re.sub(r"^https?://", "", (w or "").strip().lower()).split("/")[0]
    return re.sub(r"^www\.", "", w)
def link(dom, begriff):
    return "https://www.google.com/search?q=" + urllib.parse.quote(f"site:{dom} {begriff}")
rows = []
for r in a:
    if "Nutzer" not in (r["preise_wer"] or ""):
        continue
    n = r["nr"]; t = T[n]; dom = domain(t["website"])
    urls = [u for u in (t["quelle_url"], *Q.get(n, [])) if u and u.startswith("http")]
    rows.append([n, t["netzbetreiber"], t["mastr_nr"], f"{n}_preis_<Originalname>.pdf", dom, (urls[0] if urls else "https://" + (t["website"] or dom).replace("https://", "")),
                 *[link(dom, b) for b in BEGRIFFE]])
H = ["nr", "netzbetreiber", "mastr_nr", "speichern_als", "domain_ohne_www", "seite", *[f"suche_{i+1}" for i in range(len(BEGRIFFE))]]
w = csv.writer(open("ergebnis/browser_downloads_33.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";"); w.writerow(H); w.writerows(rows)
md = [f"# {len(rows)} Dokumente im Browser holen", "",
      "Diese Seiten sperren unseren Server (Cloudflare, Geo-Block, JavaScript-Portal). Im Browser das **Preisblatt Netzentgelte Strom 2026** (Netznutzung, Strom; endgültig vor vorläufig; nicht Gas/Wärme) als PDF speichern, unter dem angegebenen Namen (`<nr>_preis_<Originalname>.pdf`) nach `eingang/lieferung2` legen, committen und syncen.",
      "Suchlinks: `site:` immer ohne www.", "", "| Nr | Netzbetreiber | Speichern als | Seite | Suche 1 | Suche 2 | Suche 3 |", "|---|---|---|---|---|---|---|"]
for r in rows:
    md.append(f"| {r[0]} | {r[1]} | `{r[3]}` | {r[5]} | [1]({r[6]}) | [2]({r[7]}) | [3]({r[8]}) |")
open("ergebnis/BROWSER_DOWNLOADS_33.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
print(len(rows), "Zeilen")
