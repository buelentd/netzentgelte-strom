"""Zuordnung Ihre Nummer (queue.json) -> MaStR-Nummer (Primärschlüssel).
Aufruf: python daten/zuordnung_mastr.py <queue.json> [<abgleich_referenz_ergebnis.csv>]
Ausgabe: ergebnis/zuordnung_nutzer_mastr.csv (sicher: Namen gleich oder Abgleichsdatei; zweifel: Kandidaten zur Prüfung)"""
import csv, json, re, sys
from difflib import SequenceMatcher

def norm(s):
    s = s.lower()
    for a, b in (("ä","ae"),("ö","oe"),("ü","ue"),("ß","ss"),("＆","&")): s = s.replace(a, b)
    s = re.sub(r"\b(gmbh|ag|kg|mbh|co|ohg|eg|e\.?g\.?|e\.?k\.?|und|&)\b", " ", s)
    return re.sub(r"[^a-z0-9]", "", s)

def main():
    queue = json.load(open(sys.argv[1], encoding="utf8"))
    unser = list(csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";"))
    nr2m = {r["nr"]: r for r in unser}
    fest = {}
    if len(sys.argv) > 2:      # Abgleichsdatei: refnr = unsere Nummer, unser_nr = Nummer des Nutzers
        for r in csv.DictReader(open(sys.argv[2], encoding="utf-8-sig"), delimiter=";"):
            if r["unser_nr"] and r["refnr"] in nr2m: fest[r["unser_nr"]] = nr2m[r["refnr"]]
    byname = {}
    for r in unser: byname.setdefault(norm(r["netzbetreiber"]), []).append(r)
    out, sicher, zweifel, keine = [], 0, 0, 0
    for q in queue:
        n = str(q["nr"]); name = q.get("nb", "")
        if n in fest: t = fest[n]; art = "sicher (Abgleichsdatei)"
        elif len(byname.get(norm(name), [])) == 1: t = byname[norm(name)][0]; art = "sicher (Name gleich)"
        else:
            c = sorted(unser, key=lambda r: -SequenceMatcher(None, norm(name), norm(r["netzbetreiber"])).ratio())[:2]
            best = SequenceMatcher(None, norm(name), norm(c[0]["netzbetreiber"])).ratio()
            if best >= 0.8: t, art = c[0], f"zweifel (Ähnlichkeit {best:.2f}, Nr. {c[0]['nr']}: {c[0]['netzbetreiber']})"
            else: t, art = None, "keine"
        if t is None: keine += 1; out.append([n, name, "", "", "", art]); continue
        if art.startswith("sicher"): sicher += 1
        else: zweifel += 1
        out.append([n, name, t["mastr_nr"], t["nr"], t["netzbetreiber"], art])
    belegt = {o[2] for o in out if o[5].startswith("sicher")}
    for o in out:        # Zweifelsfall, dessen MaStR-Nummer schon sicher vergeben ist, ist ein Fehltreffer
        if o[5].startswith("zweifel") and o[2] in belegt:
            o[2:5] = ["", "", ""]; o[5] = "keine (Fehltreffer: MaStR-Nummer schon vergeben)"; zweifel -= 1; keine += 1
    with open("ergebnis/zuordnung_nutzer_mastr.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(["nutzer_nr", "nutzer_name", "mastr_nr", "unsere_nr", "unser_name", "sicherheit"]); w.writerows(out)
    print(f"{len(queue)} Einträge: sicher {sicher}, zweifel {zweifel}, keine {keine}")
main()
