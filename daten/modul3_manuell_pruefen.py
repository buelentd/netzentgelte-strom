"""Prüft ergebnis/modul3_manuell.csv: pro Quartalsgruppe HT/ST/NT ohne Überlappung, zusammen 24 Stunden (ST darf 'Restzeit' sein);
Gruppen ohne HT und NT ('keins') gelten als reine Standardtarif-Quartale. Aufruf: PYTHONPATH=. python daten/modul3_manuell_pruefen.py"""
import csv, re, sys
from vnb.modul3 import minuten

def gruppen(feld):
    """'Q1+Q4: 17:00-19:00; Q2+Q3: keins' oder '17:00-19:00' -> {gruppe: [zeiten]}"""
    if ":" in feld and re.match(r"\s*(Q\d|ganzj)", feld):
        out = {}
        for teil in feld.split(";"):
            k, _, v = teil.partition(": ")
            out[k.strip()] = [] if v.strip() in ("keins", "") else [x.strip() for x in v.split(",")]
        return out
    return {"alle": [x.strip() for x in feld.split(",") if x.strip()]}

def main():
    fehler = 0
    for r in csv.DictReader(open("ergebnis/modul3_manuell.csv", encoding="utf-8-sig"), delimiter=";"):
        if not (r["ht_zeiten"] or r["nt_zeiten"]):
            continue
        H, S, N = gruppen(r["ht_zeiten"]), gruppen(r["st_zeiten"]), gruppen(r["nt_zeiten"])
        for g in H:
            ht, st, nt = H.get(g, []), S.get(g, S.get("alle", [])), N.get(g, [])
            if not ht and not nt and st == ["00:00-24:00"]:
                continue
            m = {"ht": set(), "st": set(), "nt": set()}
            f = None
            for a, zs in (("ht", ht), ("st", st), ("nt", nt)):
                for z in zs:
                    if z == "Restzeit":
                        continue
                    zz = minuten(z)
                    if any(zz & m[b] for b in m):
                        f = f"{g}: Zeiten überlappen ({z})"
                    m[a] |= zz
            if "Restzeit" not in st and not f and len(m["ht"] | m["st"] | m["nt"]) != 1440:
                f = f"{g}: Zeiten ergeben nicht 24 Stunden"
            if f:
                fehler += 1
                print(r["mastr_nr"], r["netzbetreiber"][:30], "-", f)
    print("Fehler:", fehler)
    sys.exit(1 if fehler else 0)

main()
