"""§ 14a Modul 1 bis 3 und Messentgelte aus den gespeicherten Preisblatt-Texten (0 Tokens). Erste Fassung, maschinell, mit Fundstelle (Textzeile), ungeprüft.
Ausgabe: ergebnis/modul_messentgelt_2026.csv (mastr_nr zuerst). Aufruf: PYTHONPATH=. python daten/modul_messentgelte.py"""
import csv, glob, re
ZAHL = re.compile(r"(?<![\d,.])-?[−–]?\d{1,3}(?:\.\d{3})*,\d+(?![\d])")
def f(s): return float(s.replace("−", "-").replace("–", "-").replace(".", "").replace(",", "."))
def nums(l): return [f(x) for x in ZAHL.findall(l)]
def erste(zeilen, muster, lo, hi, neg=False):
    for l in zeilen:
        if re.search(muster, l, re.I):
            z = nums(re.sub(muster, " ", l, flags=re.I)) if False else nums(l)
            for x in z:
                if (neg and -400 <= x <= -20) or (not neg and lo <= x <= hi): return x, l[:110]
    return None, ""
def main():
    N = list(csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";"))
    out = []; z = {k: 0 for k in ("m1", "m2", "st", "ht", "nt", "ez")}
    for r in N:
        fs = glob.glob(f"ergebnis/texte_layout/{r['mastr_nr']}_*.txt") + glob.glob(f"ergebnis/texte/{int(r['nr']):04d}.txt")
        L = []
        for fn in fs[:1]: L += [re.sub(r"\s{2,}", "  ", x.strip()) for x in open(fn, encoding="utf8", errors="replace").read().split("\n") if x.strip()]
        if not L: continue
        m1, l1 = erste(L, r"modul ?1", 0, 0, neg=True)
        m2, l2 = erste(L, r"modul ?2", 0.3, 9)
        st, ls = erste(L, r"standard(last)?tarif(stufe)?|\bST\b|standardtarif", 2, 25)
        ht, lh = erste(L, r"hoch(last)?tarif(stufe)?|\bHT\b|\bHAT\b", 3, 40)
        nt, ln = erste(L, r"nieder(last)?tarif(stufe)?|niedriglast|\bNT\b", 0.1, 12)
        ez, le = erste(L, r"ein-?tarifz", 5, 80)
        if not any(x is not None for x in (m1, m2, st, ht, nt, ez)): continue
        for k, v in zip(("m1", "m2", "st", "ht", "nt", "ez"), (m1, m2, st, ht, nt, ez)): z[k] += v is not None
        fmt = lambda x: "" if x is None else str(x).replace(".", ",")
        out.append([r["mastr_nr"], r["nr"], r["netzbetreiber"], fmt(m1), fmt(m2), fmt(st), fmt(ht), fmt(nt), fmt(ez), " | ".join(x for x in (l1, l2, ls, lh, ln, le) if x)[:300], "maschinell gelesen, ungeprüft"])
    w = csv.writer(open("ergebnis/modul_messentgelt_2026.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";")
    w.writerow(["mastr_nr", "nr", "netzbetreiber", "modul1_pauschale_eur_jahr_netto", "modul2_ap_ct_kwh", "modul3_standard_ap_ct_kwh", "modul3_hoch_ap_ct_kwh", "modul3_nieder_ap_ct_kwh", "messung_eintarifzaehler_eur_jahr", "fundstellen_zeilen", "status"]); w.writerows(out)
    print(len(out), "Netzbetreiber mit mindestens einem Wert;", z)
main()
