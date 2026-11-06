"""Liste der Dokumente, die uns fehlen (Preisblatt / Hochlastzeitfenster), mit MaStR-Nummer als Schlüssel.
Preisblatt fehlt: kein Dokument, Scan ohne Text, Zugriff gesperrt (blockiert/robots), kein Preisblatt gefunden, falsches Dokument (keine Preise belegt), SLP/NS fehlt trotz Dokument ohne Treffer.
Hochlastzeitfenster fehlt: kein Dokument/Adresse, Jahr nicht 2026, Scan/Raster/kein Hochlastzeitfenster im Dokument/falsches Dokument.
Suchlinks: site: ohne www. (Festlegung Nutzer 06.11.2026).
Ausgabe: ergebnis/fehlende_dokumente_mastr.csv  (Aufruf: PYTHONPATH=. python daten/fehlende_dokumente.py)"""
import csv, os, re, urllib.parse
BEGRIFFE = ["Netzentgelte Strom 2026 Preisblatt", "Netznutzung Preisblatt 2026 Leistungspreis Arbeitspreis", "Hochlastzeitfenster 2026 Netznutzung"]
R = list(csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";"))
E = {r["nr"]: r for r in csv.DictReader(open("ergebnis/ebenen_erwartung.csv", encoding="utf-8-sig"), delimiter=";")}
Z = {r["mastr_nr"]: r for r in csv.DictReader(open("lauf/hlzf_zusammen.csv", encoding="utf-8-sig"), delimiter=";")}
TR = {r["nr"]: r for r in csv.DictReader(open("ergebnis/hlzf_nicht_lesbar_triage.csv", encoding="utf-8-sig"), delimiter=";")}
ohne = set(open("ergebnis/preise_ohne_beleg.txt").read().split())
Q = {}
for r in csv.DictReader(open("lauf/quellen_recherche.csv", encoding="utf-8-sig"), delimiter=";"):
    Q.setdefault(r["nr"], []).append(r["url"])
def domain(w):
    w = re.sub(r"^https?://", "", (w or "").strip().lower()).split("/")[0]
    return re.sub(r"^www\.", "", w)
link = lambda d, b: "https://www.google.com/search?q=" + urllib.parse.quote(f"site:{d} {b}") if d else ""
out = []
for r in R:
    nr, m = r["nr"], r["mastr_nr"]
    e = E.get(nr, {}); txt = f"ergebnis/texte_layout/{m}_{int(nr):04d}.txt"
    grund_p = []
    if r["status"] in ("blockiert", "robots", "kein_preisblatt", "keine_website"): grund_p.append(r["status"])
    if e.get("ns") == "kein_dokument" or e.get("slp") == "kein_dokument": grund_p.append("kein Dokument")
    if os.path.exists(txt) and os.path.getsize(txt) < 200: grund_p.append("Scan ohne Text")
    elif not os.path.exists(txt) and not [g for g in grund_p if "Dokument" in g]: grund_p.append("kein Dokumenttext bei uns (Werte nur aus Liste des Nutzers)")
    if nr in ohne: grund_p.append("Dokument belegt die Preise nicht (falsches Preisblatt?)")
    sperre = {x["nr"] for x in csv.DictReader(open("lauf/zuordnung_unbelegt.csv", encoding="utf-8-sig"), delimiter=";")}
    if e.get("slp") == "fehlt" and nr not in sperre and not [g for g in grund_p if "Dokument" in g or g in ("blockiert", "robots")] and os.path.exists(txt):
        grund_p.append("SLP-Preis (Grund- und Arbeitspreis) steht nicht vollständig im Dokument: separates SLP-Preisblatt liefern")
    if e.get("ns") in ("nicht_ausgewiesen", "im_dokument_nicht_gelesen") and nr not in sperre and not [g for g in grund_p if "Dokument" in g or g in ("blockiert", "robots")] and os.path.exists(txt):
        grund_p.append("Niederspannung (Leistungsmessung) nicht im Dokument: Preisblatt mit Leistungspreisen liefern")
    z = Z.get(m, {}); st = z.get("hlzf_status", "")
    grund_h = ""
    if st == "kein_dokument_oder_adresse": grund_h = "kein Dokument/keine Adresse"
    elif st == "jahr_nicht_2026": grund_h = "Dokument nicht 2026"
    elif st == "raster_grafik": grund_h = "Raster/Grafik (Markierung nicht im Text)"
    elif st == "zeitfenster_nicht_lesbar" and nr in TR and TR[nr]["wer"] == "Kollege": grund_h = TR[nr]["art"]
    if not grund_p and not grund_h: continue
    d = domain(r["website"]); urls = [u for u in (r["quelle_url"], *Q.get(nr, [])) if u and u.startswith("http")]
    out.append([m, nr, r["netzbetreiber"], r["bundesland"], d, "; ".join(grund_p), grund_h, f"SNB…_{int(nr):04d}.pdf" if grund_p else "", f"{m[:0]}{m}_{int(nr):04d}_hlzf.pdf" if grund_h else "",
                urls[0] if urls else "", link(d, BEGRIFFE[0]), link(d, BEGRIFFE[1]), link(d, BEGRIFFE[2])])
for o in out:                                 # richtige Dateinamen mit MaStR-Nr
    if o[7]: o[7] = f"{o[0]}_{int(o[1]):04d}.pdf"
H = ["mastr_nr", "nr", "netzbetreiber", "bundesland", "domain_ohne_www", "preisblatt_fehlt_grund", "hlzf_fehlt_grund", "dateiname_preisblatt", "dateiname_hlzf", "bekannte_url", "suche_preisblatt", "suche_preisblatt_2", "suche_hlzf"]
csv.writer(open("ergebnis/fehlende_dokumente_mastr.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";").writerows([H] + out)
p = sum(1 for o in out if o[5]); h = sum(1 for o in out if o[6])
print(len(out), "Netzbetreiber:", p, "ohne Preisblatt,", h, "ohne Hochlastzeitfenster,", sum(1 for o in out if o[5] and o[6]), "beides")
