"""§ 14a Modul 1 bis 3 und Messentgelte aus den gespeicherten Preisblatt-Texten (0 Tokens), Fassung 2 (09.11.2026).
Je Wert werden alle Kandidaten aus passenden Zeilen gesammelt; nur wenn alle Kandidaten gleich sind, wird der Wert übernommen, sonst 'mehrdeutig' und leer.
Netto/Brutto-Paare (zweite Zahl = erste x 1,19): die erste. Ausgabe: ergebnis/modul_messentgelt_2026.csv (mastr_nr zuerst), Status 'maschinell, ungeprüft'.
Aufruf: PYTHONPATH=. python daten/modul_messentgelte.py"""
import csv, glob, re
ZAHL = re.compile(r"(?<![\d,.])[-−–]?\d{1,3}(?:\.\d{3})*,\d+(?![\d])")
def f(s): return float(s.replace("−", "-").replace("–", "-").replace(".", "").replace(",", "."))
def nums(l): return [f(x) for x in ZAHL.findall(l)]
def ohne_paar(z):
    """Netto/Brutto-Paare zusammenfassen: [a, a*1,19, b, b*1,19] -> [a, b]"""
    out, i = [], 0
    while i < len(z):
        out.append(z[i])
        if i + 1 < len(z) and z[i] and abs(z[i + 1] - z[i] * 1.19) < 0.02 * max(1, abs(z[i])) + 0.011: i += 2
        else: i += 1
    return out
SCHLECHT = re.compile(r"speicherheiz|wärmepump|waermepump|schwachlast|konzession|elektromob|straßenbeleucht|reservekap|zählpunkt.*monat", re.I)
def kandidaten(L, muster, bereich, art):
    out = []
    for i, l in enumerate(L):
        if not re.search(muster, l, re.I) or SCHLECHT.search(l): continue
        zl = ohne_paar(nums(re.sub(r"\d+ ?%|bis \d+|\d{1,2}\.\d{2} ?uhr", " ", l)))
        if not zl and i + 1 < len(L) and not SCHLECHT.search(L[i + 1]): zl = ohne_paar(nums(L[i + 1]))
        if art == "neg":
            c = [abs(x) for x in zl if x <= -20]
            if not c: c = [x for x in zl if 30 <= x <= 300]
        else:
            c = [x for x in zl if bereich[0] <= x <= bereich[1]]
            c = c[-1:] if art == "letzte" else c[:1]
        if c: out.append((c[0], l[:100]))
    return out
def wert(L, muster, bereich, art):
    k = kandidaten(L, muster, bereich, art)
    if not k: return None, "", ""
    v = {x for x, _ in k}
    if len(v) == 1: return k[0][0], "", k[0][1]
    return None, "mehrdeutig " + "/".join(str(x).replace(".", ",") for x in sorted(v)), k[0][1]
def main():
    N = list(csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";"))
    out = []; z = {k: [0, 0] for k in ("m1", "m2", "st", "ht", "nt", "ez")}
    for r in N:
        fs = glob.glob(f"ergebnis/texte_layout/{r['mastr_nr']}_*.txt") + glob.glob(f"ergebnis/texte/{int(r['nr']):04d}.txt")
        if not fs: continue
        L = [re.sub(r"\s{2,}", "  ", x.strip()) for x in open(fs[0], encoding="utf8", errors="replace").read().split("\n") if x.strip()]
        spec = {"m1": (r"modul ?1(?!\s*\+|.*modul ?3)|pauschale (netzentgelt)?reduk|pauschale netzentgeltreduzierung", (20, 300), "neg"),
                "m2": (r"modul ?2", (0.3, 9), "letzte"),
                "st": (r"(standard(last)?tarif(stufe)?|\bST\b)\s*(\(|[-–]|\s)\s*[\d(]|standardlasttarif", (2, 25), "letzte"),
                "ht": (r"hoch(last)?tarif(stufe)?\s*[\d(–-]|\bHT\b\s+[\d]", (3, 40), "letzte"),
                "nt": (r"nieder(last)?tarif(stufe)?\s*[\d(–-]|niedriglasttarif|\bNT\b\s+[\d]", (0.1, 12), "letzte"),
                "ez": (r"ein-?tarifz", (5, 80), "erste")}
        res, flags, zeilen = {}, [], []
        for k, (m, b, a) in spec.items():
            v, fl, zl = wert(L, m, b, a); res[k] = v
            if fl: flags.append(k + ":" + fl)
            if zl: zeilen.append(zl)
            z[k][0] += v is not None; z[k][1] += bool(fl)
        if not any(v is not None for v in res.values()) and not flags: continue
        fmt = lambda x: "" if x is None else str(x).replace(".", ",")
        out.append([r["mastr_nr"], r["nr"], r["netzbetreiber"]] + [fmt(res[k]) for k in ("m1", "m2", "st", "ht", "nt", "ez")] + ["; ".join(flags), " | ".join(zeilen)[:300], "maschinell, ungeprüft"])
    w = csv.writer(open("ergebnis/modul_messentgelt_2026.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";")
    w.writerow(["mastr_nr", "nr", "netzbetreiber", "modul1_pauschale_eur_jahr_netto", "modul2_ap_ct_kwh", "modul3_standard_ap_ct_kwh", "modul3_hoch_ap_ct_kwh", "modul3_nieder_ap_ct_kwh", "messung_eintarifzaehler_eur_jahr", "hinweis", "fundstellen_zeilen", "status"]); w.writerows(out)
    print(len(out), "Netzbetreiber;", {k: f"{a} eindeutig / {b} mehrdeutig" for k, (a, b) in z.items()})
main()
