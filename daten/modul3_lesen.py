"""Modul 3 (HT/ST/NT-Zeiten) aus den Preisblatt-Texten lesen (0 Tokens), mit vnb/modul3.py.
Bereits geprüfte Zeilen in ergebnis/modul3_zeiten.csv bleiben unverändert. Neue Zeilen: 'maschinell gelesen, Zeiten geprüft auf Überlappung und 24 h, nicht am Dokument bestätigt'.
Preise aus ergebnis/modul_messentgelt_2026_geprueft.csv. Nicht eindeutige Fälle: ergebnis/modul3_offen.csv (mastr_nr zuerst, mit Ausschnitt).
Aufruf: PYTHONPATH=. python daten/modul3_lesen.py"""
import csv, glob, re
from vnb.modul3 import lesen, formatieren, blocks, HT, NT

def lies(p):
    return list(csv.DictReader(open(p, encoding="utf-8-sig"), delimiter=";"))

def main():
    N = {r["mastr_nr"]: r for r in lies("ergebnis/netzentgelte_2026.csv")}
    P = {r["mastr_nr"]: r for r in lies("ergebnis/modul_messentgelt_2026_geprueft.csv")}
    alt = [r for r in lies("ergebnis/modul3_zeiten.csv") if not r["hinweis"].startswith("maschinell gelesen")]
    cols = list(alt[0].keys())
    fertig = {r["mastr_nr"] for r in alt}
    neu, offen = [], []
    for f in sorted(glob.glob("ergebnis/texte_layout/SNB*.txt")):
        m = re.search(r"(SNB\d+)", f)
        mn = m.group(1)
        if mn in fertig or mn not in N:
            continue
        t = open(f, encoding="utf8", errors="replace").read()
        if not (re.search(r"modul\s*3|zeitvariabl", t, re.I) and (HT.search(t) or NT.search(t))):
            continue
        e, grund = lesen(t)
        n, p = N[mn], P.get(mn, {})
        if e:
            ht, st, nt, q = formatieren(e)
            fmt = lambda x: x or ""
            neu.append({"mastr_nr": mn, "netzbetreiber": n["netzbetreiber"], "jahr": "2026", "ht_zeiten": ht, "st_zeiten": st, "nt_zeiten": nt, "quartale": q,
                        "ht_ct_kwh": fmt(p.get("modul3_hoch_ap_ct_kwh")), "st_ct_kwh": fmt(p.get("modul3_standard_ap_ct_kwh")), "nt_ct_kwh": fmt(p.get("modul3_nieder_ap_ct_kwh")),
                        "preisstand": n.get("preisstand", ""), "quelle_url": n.get("quelle_url", ""),
                        "hinweis": f"maschinell gelesen ({grund}), Zeiten geprüft auf Überlappung und 24 h, nicht am Dokument bestätigt; Preise maschinell"})
        else:
            L = t.split("\n")
            B = blocks(L)
            ausz = " / ".join(re.sub(r"\s{2,}", " ", L[i].strip()) for i in B[:14] if L[i].strip())[:900]
            offen.append({"mastr_nr": mn, "netzbetreiber": n["netzbetreiber"], "grund": grund, "quelle_url": n.get("quelle_url", ""), "ausschnitt": ausz})
    w = csv.DictWriter(open("ergebnis/modul3_zeiten.csv", "w", encoding="utf-8-sig", newline=""), fieldnames=cols, delimiter=";")
    w.writeheader(); w.writerows(alt + neu)
    w = csv.DictWriter(open("ergebnis/modul3_offen.csv", "w", encoding="utf-8-sig", newline=""), fieldnames=["mastr_nr", "netzbetreiber", "grund", "quelle_url", "ausschnitt"], delimiter=";")
    w.writeheader(); w.writerows(offen)
    print("geprüft vorhanden", len(alt), "| neu maschinell", len(neu), "| offen", len(offen))

main()
