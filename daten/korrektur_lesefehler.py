"""Findet Lesefehler in der Tabelle und korrigiert sie aus der Zeile im Dokument (lauf/preise_manuell.csv, Hinweis "Korrigiert: …", ungeprüft).
Regel A (Müllwerte): mindestens 3 der 4 Werte einer Ebene sind ganze Zahlen, oder es steht 365 / 1095 / 28–31 als Preis dort (Tage statt Preise gelesen).
Regel B (Arbeitspreis ab): Die ersten drei Werte stimmen mit der Dokumentzeile überein, der vierte nicht (z. B. 1,00 statt 1,24).
Die Dokumentzeile: Zeile mit dem Ebenennamen und genau vier Dezimalzahlen mit Komma (netto; bei "netto (brutto)" und "netto / brutto" gilt netto), plausibel.
Aufruf: PYTHONPATH=. python daten/korrektur_lesefehler.py [--schreiben]"""
import csv, glob, io, re, sys
K = ("lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh")
LAB = {"ms": r"^\s*(?:mittelspannung(?:snetz)?\b(?!.*nieder)|ms\b(?!\s*/))", "msns": r"umspann|mittel.{0,12}nieder|ms\s*/\s*ns",
       "ns": r"^\s*niederspannung", "hsms": r"hoch.{0,20}mittel|hs\s*/\s*ms"}
ZAHL = r"(\d{1,3}(?:\.\d{3})*,\d{1,4})"
de = lambda v: float(v.replace(".", "").replace(",", ".")) if v else None
fmt = lambda v: f"{v:.4f}".rstrip("0").replace(".", ",") if abs(v * 100 - round(v * 100)) > 1e-6 else f"{v:.2f}".replace(".", ",")

def zeilenwerte(l):
    """vier Nettozahlen aus einer Zeile oder None."""
    m = re.search(ZAHL + r"\s*(?:\(\s*" + ZAHL + r"\s*\)|/\s*" + ZAHL + r")?" + "".join(r"\s+" + ZAHL + r"\s*(?:\(\s*" + ZAHL + r"\s*\)|/\s*" + ZAHL + r")?" for _ in range(3)), l)
    if not m:
        return None
    g = m.groups()
    netto = [g[0], g[3], g[6], g[9]]
    brutto = [g[1] or g[2], g[4] or g[5], g[7] or g[8], g[10] or g[11]]
    if any(brutto) and not all(brutto):
        return None
    if all(brutto) and not all(abs(de(b) / de(n) - 1.19) < 0.02 for n, b in zip(netto, brutto) if de(n)):
        return None
    zeilenwerte.brutto = [de(b) for b in brutto] if all(brutto) else []
    return [de(x) for x in netto]

def plausibel(v, eb):
    lpu, apu, lpo, apo = v
    return 0 < lpo < 700 and 0 < lpu < 700 and 1 <= apu < 30 and 0 <= apo < 30 and lpu < lpo * 1.5 and lpo > 5

def muell(v):
    ganz = sum(1 for x in v if abs(x - round(x)) < 1e-9)
    return ganz >= 3 or any(x in (365, 366, 1095, 28, 29, 30, 31) for x in v)

def main(schreiben):
    tab = {r["nr"]: r for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
    plan = []
    for nr, x in tab.items():
        fs = glob.glob(f"ergebnis/texte_layout/{x['mastr_nr']}_{int(nr):04d}.txt")
        if not fs:
            continue
        zeilen = open(fs[0], errors="ignore").read().splitlines()
        for eb in ("ms", "msns", "ns", "hsms"):
            alt = [de(x[f"{eb}_{k}"]) for k in K]
            if None in alt:
                continue
            cand = []
            for l in zeilen:
                if re.search(LAB[eb], l, re.I):
                    zeilenwerte.brutto = []
                    v = zeilenwerte(l)
                    if v and plausibel(v, eb) and v not in cand:
                        cand.append(v); brutto = list(zeilenwerte.brutto)
            if len(cand) != 1:
                continue
            neu = cand[0]
            if all(abs(a - b) < 0.011 for a, b in zip(alt, neu)):
                continue
            regel = "A" if muell(alt) else ("B" if all(abs(a - b) < 0.011 for a, b in zip(alt[:3], neu[:3])) else None)
            if regel is None and brutto and any(abs(a - b) < 0.011 for a in alt for b in brutto) and not any(abs(a - b) < 0.011 for a in alt for b in neu[:1]):
                regel = "C"                              # Bruttozahlen als Preise gelesen
            if regel:
                plan.append((nr, x["netzbetreiber"], eb, regel, alt, neu))
    for nr, name, eb, regel, alt, neu in plan:
        print(f"{nr:>4} {name[:28]:28} {eb:5} Regel {regel}: {alt} -> {neu}")
    print(len(plan), "Korrekturen")
    if not schreiben:
        return
    p = "lauf/preise_manuell.csv"
    raw = open(p, encoding="utf-8", newline="").read()
    bom = raw.startswith("﻿"); nl = "\r\n" if "\r\n" in raw else "\n"
    rows = list(csv.reader(io.StringIO(raw.lstrip("﻿")), delimiter=";"))
    H = rows[0]; I = {h: i for i, h in enumerate(H)}
    byn = {r[0]: r for r in rows[1:]}
    for nr, name, eb, regel, alt, neu in plan:
        r = byn.get(nr)
        if r is None:
            r = [""] * len(H); r[I["nr"]] = nr; r[I["netzbetreiber"]] = name; r[I["stand_datum"]] = "2026"
            r[I["quelle_url"]] = tab[nr]["quelle_url"]; rows.append(r); byn[nr] = r
        for k, v in zip(K, neu):
            r[I[f"{eb}_{k}"]] = fmt(v)
        note = f"Korrigiert: {eb.upper()} aus der Dokumentzeile gelesen (vorher {', '.join(fmt(a) for a in alt)}), Lesefehler Regel {regel}"
        r[I["hinweis"]] = note + ("; " + r[I["hinweis"]] if r[I["hinweis"]] else "")
        if "geprueft" in I:
            r[I["geprueft"]] = ""
    out = io.StringIO(); w = csv.writer(out, delimiter=";", lineterminator=nl); w.writerows(rows)
    open(p, "w", encoding="utf-8", newline="").write(("﻿" if bom else "") + out.getvalue())
    print("preise_manuell.csv geschrieben")

main("--schreiben" in sys.argv)
