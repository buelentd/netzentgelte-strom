"""Plausibilitätsprüfung der maschinell gelesenen Modul- und Messwerte (0 Tokens). Eingabe: ergebnis/modul_messentgelt_2026.csv und netzentgelte_2026.csv.
Regeln: Modul 1 Pauschale 40-250 €/a; Modul 2 AP 0,3-9 ct und 15-85 % des SLP-Arbeitspreises; Modul 3: Niedrig < Standard < Hoch, Standard höchstens 40 % neben dem SLP-AP;
Eintarifzähler 5-80 €/a; Werte gleich einem Konzessionsabgaben-Satz (0,11/0,61/1,32/1,59/1,99/2,39) gelten als verdächtig.
Ausgabe: ergebnis/modul_messentgelt_2026_geprueft.csv (nur plausible Werte, mastr_nr zuerst) und Spalte plausibilitaet. Aufruf: PYTHONPATH=. python daten/modul_pruefen.py"""
import csv
F = lambda s: float(s.replace(",", ".")) if s else None
KA = {0.11, 0.61, 1.32, 1.59, 1.99, 2.39}
def main():
    N = {r["mastr_nr"]: r for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
    R = list(csv.DictReader(open("ergebnis/modul_messentgelt_2026.csv", encoding="utf-8-sig"), delimiter=";"))
    cols = ["mastr_nr", "nr", "netzbetreiber", "modul1_pauschale_eur_jahr_netto", "modul2_ap_ct_kwh", "modul3_standard_ap_ct_kwh", "modul3_hoch_ap_ct_kwh", "modul3_nieder_ap_ct_kwh", "messung_eintarifzaehler_eur_jahr", "plausibilitaet", "fundstellen_zeilen", "status"]
    out, z = [], {"ok": 0, "teilweise": 0, "verdaechtig": 0}
    k = {"m1": 0, "m2": 0, "st": 0, "ht": 0, "nt": 0, "ez": 0}
    for r in R:
        n = N.get(r["mastr_nr"], {}); ap = F(n.get("slp_ap_ct_kwh", ""))
        v = {"m1": F(r["modul1_pauschale_eur_jahr_netto"]), "m2": F(r["modul2_ap_ct_kwh"]), "st": F(r["modul3_standard_ap_ct_kwh"]), "ht": F(r["modul3_hoch_ap_ct_kwh"]), "nt": F(r["modul3_nieder_ap_ct_kwh"]), "ez": F(r["messung_eintarifzaehler_eur_jahr"])}
        bad = {}
        if v["m1"] is not None and not 40 <= v["m1"] <= 250: bad["m1"] = "Modul 1 außerhalb 40-250 €"
        if v["m2"] is not None:
            if not 0.3 <= v["m2"] <= 9 or v["m2"] in KA: bad["m2"] = "Modul 2 unplausibel"
            elif ap and not 0.15 <= v["m2"] / ap <= 0.85: bad["m2"] = f"Modul 2 / SLP-AP = {v['m2']/ap:.2f}"
        if v["st"] is not None and ap and abs(v["st"] - ap) / ap > 0.4: bad["st"] = "Standard weicht über 40 % vom SLP-AP ab"
        if v["nt"] is not None and (v["nt"] in KA or (v["st"] and v["nt"] >= v["st"])): bad["nt"] = "Niedrig nicht unter Standard oder Konzessionsabgabe"
        if v["ht"] is not None and (v["ht"] in KA or (v["st"] and v["ht"] <= v["st"])): bad["ht"] = "Hoch nicht über Standard"
        if v["ez"] is not None and not 5 <= v["ez"] <= 80: bad["ez"] = "Eintarifzähler außerhalb 5-80 €"
        gesamt = [x for x in v if v[x] is not None]
        if not gesamt: continue
        for x in bad:
            v[x] = None
        for x in gesamt:
            if x not in bad: k[x] += 1
        status = "ok" if not bad else ("verdaechtig" if len(bad) == len(gesamt) else "teilweise")
        z[status] += 1
        fmt = lambda x: "" if x is None else str(x).replace(".", ",")
        out.append([r["mastr_nr"], r["nr"], r["netzbetreiber"]] + [fmt(v[x]) for x in ("m1", "m2", "st", "ht", "nt", "ez")] + ["; ".join(bad.values()), r["fundstellen_zeilen"], "maschinell gelesen, Plausibilität geprüft, nicht am Dokument bestätigt"])
    w = csv.writer(open("ergebnis/modul_messentgelt_2026_geprueft.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";")
    w.writerow(cols); w.writerows(out)
    print(len(out), "Netzbetreiber:", z, "| plausible Werte:", k)
main()
