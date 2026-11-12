"""Lieferung des Kollegen (ergebnis/hlzf/hlzf_2027_gelesen.csv, hlzf_auftrag7_gelesen.csv) prüfen und übernehmen. 0 Tokens.
Übernommen wird eine Zeile nur, wenn (1) die MaStR-Nr. bei uns noch nicht fertig ist, (2) die Quelldatei im Repo liegt und (3) JEDE Zeit der Zeile im PDF-Text wiederzufinden ist.
Alles andere kommt in lauf/hlzf_lieferung_zurueck.csv (mit Grund) und wird nicht übernommen. Status: Jahr 2027 -> gelesen_aus_2027, Jahr 2026 -> gelesen_kollege_verifiziert.
Aufruf: PYTHONPATH=. python daten/hlzf_lieferung_uebernehmen.py"""
import csv, glob, os, re, subprocess
from collections import Counter

J = ("fruehling", "sommer", "herbst", "winter")
FERTIG = ("gelesen_nutzer", "gelesen_unser", "gelesen_kollege_verifiziert", "gelesen_aus_2027")
_cache = {}


def lesen(p):
    return list(csv.DictReader(open(p, encoding="utf-8-sig"), delimiter=";"))


def datei(name):
    if name in _cache:
        return _cache[name]
    b = os.path.basename(name.split("|")[0].strip())
    t = [f for f in glob.glob(f"eingang/**/{b}", recursive=True) + glob.glob(f"dl_up/**/{b}", recursive=True) if os.path.isfile(f)]
    _cache[name] = t[0] if t else None
    return _cache[name]


def text(f):
    if f.lower().endswith(".pdf"):
        return re.sub(r"\s+", " ", subprocess.run(["pdftotext", "-layout", f, "-"], capture_output=True, text=True).stdout)
    if f.lower().endswith((".html", ".htm", ".txt", ".csv")):
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", open(f, encoding="utf8", errors="replace").read()))
    return ""


def zeit_im_text(z, t):
    a, b, c, d = z[:2], z[3:5], z[6:8], z[9:]
    a0, c0 = a.lstrip("0") or "0", c.lstrip("0") or "0"
    for x in (rf"(?<!\d)0?{a0}[:.]{b}\s*(?:uhr)?\s*(?:[-–]|bis)\s*0?{c0}[:.]{d}", rf"(?<!\d)0?{a0}[:.]{b}\D{{1,14}}0?{c0}[:.]{d}"):
        if re.search(x, t, re.I):
            return True
    return False


def main():
    Z = {r["mastr_nr"]: r["hlzf_status"] for r in lesen("lauf/hlzf_zusammen.csv")}
    ov = lesen("lauf/hlzf_kollege_verifiziert.csv")
    H = list(ov[0].keys())
    have = {r["mastr_nr"] for r in ov}
    add, zurueck, z = [], [], Counter()
    for fn in ("ergebnis/hlzf/hlzf_2027_gelesen.csv", "ergebnis/hlzf/hlzf_auftrag7_gelesen.csv"):
        for r in lesen(fn):
            mn = r["mastr_nr"]
            zeiten = [x for e in ("ns", "msns") for j in J for x in re.findall(r"\d\d:\d\d-\d\d:\d\d", r.get(f"{e}_{j}", ""))]
            if Z.get(mn) in FERTIG or mn in have:
                z["schon fertig"] += 1; continue
            if not zeiten:
                zurueck.append([mn, r["netzbetreiber"][:30], "keine Zeiten in der Zeile"]); continue
            f = datei(r.get("quelle_url", ""))
            if not f:
                zurueck.append([mn, r["netzbetreiber"][:30], "Quelldatei nicht im Repo: " + r.get("quelle_url", "")[:50]]); continue
            t = text(f)
            if len(t) < 100:
                zurueck.append([mn, r["netzbetreiber"][:30], "Datei ohne Text (Bild): am Bild zu bestätigen"]); continue
            fehlt = [x for x in zeiten if not zeit_im_text(x, t)]
            if fehlt:
                zurueck.append([mn, r["netzbetreiber"][:30], f"{len(fehlt)} von {len(zeiten)} Zeiten nicht im Text: " + ", ".join(fehlt[:3])]); continue
            status = "gelesen_aus_2027" if r.get("jahr") == "2027" else "gelesen_kollege_verifiziert"
            q = r["quelle_url"] if r["quelle_url"].startswith("http") else f
            add.append({"mastr_nr": mn, **{f"hlzf_{k}": r[k] for k in [f"{e}_{j}" for e in ("ns", "msns") for j in J]}, "hlzf_schwelle_prozent": r.get("schwelle_prozent", ""),
                        "hlzf_mindestleistung_kw": r.get("mindestleistung_kw", ""), "hlzf_quelle_url": q, "hlzf_status": status})
            have.add(mn)
    w = csv.DictWriter(open("lauf/hlzf_kollege_verifiziert.csv", "w", encoding="utf-8-sig", newline=""), fieldnames=H, delimiter=";")
    w.writeheader(); w.writerows(ov + [{k: a.get(k, "") for k in H} for a in add])
    w = csv.writer(open("lauf/hlzf_lieferung_zurueck.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";")
    w.writerow(["mastr_nr", "netzbetreiber", "grund"]); w.writerows(zurueck)
    print("übernommen", len(add), "| schon fertig", z["schon fertig"], "| zurückgestellt", len(zurueck))
    print(Counter(g[2].split(":")[0].split(" ")[0] + " " + g[2].split(":")[0].split(" ")[1] if " " in g[2] else g[2] for g in zurueck).most_common(5))


main()
