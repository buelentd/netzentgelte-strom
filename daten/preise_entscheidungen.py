"""Am Dokumenttext von Hand geprüfte Entscheidungen zu Preisblöcken (05.11.2026): korrigieren oder entfernen.
KORRIGIEREN: (nr, ebene) -> [LP unter, AP unter, LP ab, AP ab] laut Dokumentzeile; ENTFERNEN: (nr, ebene) -> Grund.
Aufruf: PYTHONPATH=. python daten/preise_entscheidungen.py"""
import csv, io
KORRIGIEREN = {
    ("553", "ms"): [16.58, 5.79, 130.93, 1.21],           # Lippe-Weser: drei Ebenen waren verschoben gelesen
    ("553", "msns"): [18.41, 6.41, 145.04, 1.34],
    ("553", "ns"): [20.76, 8.00, 171.13, 1.98],
    ("662", "ms"): [25.77, 6.33, 154.60, 1.18],           # Sondershausen: Nettospalten statt Brutto
    ("662", "msns"): [30.56, 7.13, 186.01, 0.91],
    ("662", "ns"): [27.48, 8.99, 196.30, 2.24],
    ("508", "ns"): [32.14, 7.71, 186.50, 1.54],           # Haltern: NS-Werte standen als MS, AP unter fehlte
    ("617", "ms"): [12.53, 2.51, 58.19, 0.68],            # Pritzwalk: Brutto statt Netto gelesen, Nettospalten verwendet
    ("617", "msns"): [21.60, 3.89, 85.18, 1.34],
    ("617", "ns"): [40.99, 5.74, 104.29, 3.21],
    ("21", "ms"): [11.26, 5.58, 121.00, 1.19],            # Bielefelder Netz: stand HS/MS-Zeile (6,47 …) als MS
    ("25", "hsms"): [28.15, 1.92, 31.77, 1.78],           # Hamburger Energienetze: zwei Tabellen (unter und ab 2.500 h), Zeile Umspannung Hoch-/Mittelspannung
}
ENTFERNEN = {
    ("508", "ms"): "Werte waren NS-Preise (32,14 / 186,50), im Jahresleistungspreissystem keine MS-Preise im Dokument",
    ("52", "hsms"): "Werte sind SLP-Preise (98,00 / 5,69), keine HS/MS-Ebene im Dokument",
    ("194", "hsms"): "Werte im Dokument nicht belegt (von Hand am Text geprüft)",
    ("283", "ns"): "Werte im Dokument nicht belegt (von Hand am Text geprüft)",
    ("370", "msns"): "Werte im Dokument nicht belegt (von Hand am Text geprüft)",
}
F = ("lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh")
fmt = lambda v: f"{v:.2f}".replace(".", ",")

def main():
    tab = {r["nr"]: r for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
    p = "lauf/preise_manuell.csv"
    raw = open(p, encoding="utf-8", newline="").read()
    bom = raw.startswith("﻿"); nl = "\r\n" if "\r\n" in raw else "\n"
    rows = list(csv.reader(io.StringIO(raw.lstrip("﻿")), delimiter=";"))
    H = rows[0]; I = {h: i for i, h in enumerate(H)}
    byn = {r[0]: r for r in rows[1:]}
    for (nr, eb), v in KORRIGIEREN.items():
        r = byn.get(nr)
        if r is None:
            r = [""] * len(H); r[I["nr"]] = nr; r[I["netzbetreiber"]] = tab[nr]["netzbetreiber"]; r[I["stand_datum"]] = "2026"
            r[I["quelle_url"]] = tab[nr]["quelle_url"]; rows.append(r); byn[nr] = r
        for k, x in zip(F, v):
            r[I[f"{eb}_{k}"]] = fmt(x)
        note = f"Korrigiert: {eb.upper()} von Hand am Dokument geprüft und korrigiert"
        if note not in r[I["hinweis"]]:
            r[I["hinweis"]] = note + ("; " + r[I["hinweis"]] if r[I["hinweis"]] else "")
        r[I["geprueft"]] = ""
    out = io.StringIO(); w = csv.writer(out, delimiter=";", lineterminator=nl); w.writerows(rows)
    open(p, "w", encoding="utf-8", newline="").write(("﻿" if bom else "") + out.getvalue())
    # Entfernen: lauf/werte_entfernt.csv ergänzen
    pe = "lauf/werte_entfernt.csv"
    alt = {(r["nr"], r["ebene"]): r["grund"] for r in csv.DictReader(open(pe, encoding="utf-8-sig"), delimiter=";")}
    alt.update(ENTFERNEN)
    with open(pe, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(["nr", "ebene", "grund"])
        for (nr, eb), g in sorted(alt.items(), key=lambda kv: (int(kv[0][0]), kv[0][1])):
            w.writerow([nr, eb, g])
    print(len(KORRIGIEREN), "korrigiert,", len(ENTFERNEN), "entfernt")

main()
