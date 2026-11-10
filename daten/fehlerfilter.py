"""Fehlerfilter und zweiter Leser über alle ok-Zeilen (0 Tokens). Ausgabe: ergebnis/fehlerfilter_2026.csv (mastr_nr zuerst).
Prüft je Ebene und SLP, ob unsere Zahlen im gespeicherten Dokumenttext (a) als Brutto-Wert neben einem Netto-Wert (x/1,19) stehen,
(b) in einer Zeile mit Stichwörtern für andere Tarife stehen (Speicherheizung, Wärmepumpe, Modul, 14a, Ermäßigung, Monat, Reserve ...),
(c) mehrdeutig sind (dieselbe Ebene hat im Dokument mehrere unterschiedliche 4er-Zeilen) oder (d) im Text nicht als Zeile vorkommen.
Aufruf: PYTHONPATH=. python daten/fehlerfilter.py"""
import csv, glob, re
K = ("lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh")
ZAHL = re.compile(r"(?<![\d,.])-?\d{1,3}(?:\.\d{3})*,\d+(?![\d])|(?<![\d,.])-?\d+,\d+(?![\d])")
F = lambda s: float(s.replace(".", "").replace(",", ".")) if s else None
FALSCH = re.compile(r"speicherheiz|wärmepump|waermepump|modul|14a|ermäßig|ermaessig|nachtspeicher|elektromob|reserve|monat|tarifstufe|hochlast|niedriglast", re.I)
EBENE = {"ms": re.compile(r"mittelspannung(?!.*(nieder|/ ?ns|ms/ns))|^\s*(ms|msp|ne ?5)\b", re.I),
         "msns": re.compile(r"umspann\w*.*(nieder|ns\b)|mittel.{0,6}nieder|ms ?/ ?ns|msp ?/ ?nsp|ne ?6", re.I),
         "ns": re.compile(r"^\s*(\d\s*[-–]\s*)?nieder\w*(?!.*umspann)|^\s*(ns|nsp|ne ?7)\b", re.I)}
def tuples(lines, eb):
    out = []
    for l in lines:
        if EBENE[eb].search(l) and not re.search(r"umspann\w*.*hoch|hs ?/ ?ms", l, re.I) or (eb == "msns" and EBENE[eb].search(l)):
            z = [F(x) for x in ZAHL.findall(l)]
            if len(z) >= 4: out.append((tuple(z[:4]), l))
    return out
def main():
    N = list(csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";"))
    erg = []
    for r in N:
        if r["status"] != "ok": continue
        fs = glob.glob(f"ergebnis/texte_layout/{r['mastr_nr']}_*.txt") + glob.glob(f"ergebnis/texte/{int(r['nr']):04d}.txt")
        L = []
        for f in fs: L += [re.sub(r"\s{2,}", "  ", x.strip()) for x in open(f, encoding="utf8", errors="replace").read().split("\n") if x.strip()]
        if not L: erg.append([r["mastr_nr"], r["nr"], r["netzbetreiber"], "alle", "kein_text", ""]); continue
        for eb in ("ms", "msns", "ns"):
            v = tuple(F(r[f"{eb}_{k}"]) for k in K)
            if None in v: continue
            zeilen = [l for l in L if all(any(abs(x - y) < 0.006 for y in [F(t) for t in ZAHL.findall(l)]) for x in v)]
            gr = []
            if not zeilen: gr.append("nicht_als_Zeile_im_Text")
            for l in zeilen[:1]:
                zz = [F(t) for t in ZAHL.findall(l)]
                for x in v:
                    if any(abs(x / 1.19 - y) < 0.011 and y > 0 for y in zz): gr.append(f"brutto?({x})")
                if FALSCH.search(l): gr.append("falsche_Zeile?(" + FALSCH.search(l).group(0) + ")")
            T = {t for t, _ in tuples(L, eb)}
            if v not in T and T and zeilen == []: pass
            if len(T) > 1 and v in T: gr.append(f"mehrdeutig({len(T)} Tupel)")
            if gr: erg.append([r["mastr_nr"], r["nr"], r["netzbetreiber"], eb, "; ".join(gr), (zeilen[0] if zeilen else "")[:110]])
        s = (F(r["slp_ap_ct_kwh"]), F(r["slp_grundpreis_eur_jahr"]))
        if None not in s:
            zl = [l for l in L if all(any(abs(x - y) < 0.006 for y in [F(t) for t in ZAHL.findall(l)]) for x in s)]
            gr = []
            if not zl:
                # AP und GP in benachbarten Zeilen?
                ok = any(any(abs(s[0] - F(t)) < .006 for t in ZAHL.findall(L[i])) and any(abs(s[1] - F(t)) < .006 for j in range(max(0, i - 3), min(len(L), i + 4)) for t in ZAHL.findall(L[j])) for i in range(len(L)))
                if not ok: gr.append("slp_nicht_im_Text")
            else:
                zz = [F(t) for t in ZAHL.findall(zl[0])]
                for x in s:
                    if any(abs(x / 1.19 - y) < 0.011 and y > 0 for y in zz): gr.append(f"brutto?({x})")
                if FALSCH.search(zl[0]): gr.append("falsche_Zeile?(" + FALSCH.search(zl[0]).group(0) + ")")
            if gr: erg.append([r["mastr_nr"], r["nr"], r["netzbetreiber"], "slp", "; ".join(gr), (zl[0] if zl else "")[:110]])
    w = csv.writer(open("ergebnis/fehlerfilter_2026.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";")
    w.writerow(["mastr_nr", "nr", "netzbetreiber", "ebene", "verdacht", "zeile"]); w.writerows(erg)
    from collections import Counter
    c = Counter(); n = set()
    for e in erg:
        n.add(e[1])
        for g in e[4].split("; "): c[g.split("(")[0]] += 1
    print(len(n), "Netzbetreiber mit Verdacht;", dict(c))
main()
