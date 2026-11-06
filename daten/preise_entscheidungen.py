"""Am Dokumenttext von Hand geprüfte Entscheidungen zu Preisblöcken (05.11.2026): korrigieren oder entfernen.
KORRIGIEREN: (nr, ebene) -> [LP unter, AP unter, LP ab, AP ab] laut Dokumentzeile; ENTFERNEN: (nr, ebene) -> Grund.
Aufruf: PYTHONPATH=. python daten/preise_entscheidungen.py"""
import csv, io
NOTIZ = {("393", "slp"): "Dokument nennt keinen Grundpreis, Tabelle nur mit Arbeitspreis", ("247", "slp"): "Dokument nennt keinen Grundpreis, Tabelle nur mit Arbeitspreis",
         ("322", "slp"): "Grundpreis-Zelle für Kleinkunden im Dokument leer"}
TEXTAUSZUG = {"603", "151"}      # Werte aus dem Textauszug des Kollegen (Original-PDF im Browser geladen, nicht bei uns gespeichert): geprueft bleibt leer
KORRIGIEREN = {
    ("361", "msns"): [30.55, 7.02, 166.31, 1.59],         # Remstalwerk: Umspannung Mittel- auf Niederspannungsnetz
    ("558", "ms"): [5.79, 3.87, 97.20, 0.21],             # Ludwigslust-Grabow: Jahresleistungspreissystem (Monatssystem ignoriert)
    ("558", "msns"): [6.15, 5.91, 153.79, 0.00],
    ("558", "ns"): [11.81, 6.71, 94.16, 3.42],
    ("802", "hsms"): [21.86, 4.07, 114.88, 0.35],         # ÜZ Mainfranken: Umspannung in Mittelspannung
    ("802", "msns"): [24.76, 4.90, 140.26, 0.28],
    ("802", "ns"): [30.08, 4.79, 129.53, 0.81],
    ("528", "ms"): [6.29, 5.19, 118.31, 0.71],            # Husum: Tabellen < / ≥ 2.500 h, netto
    ("528", "msns"): [8.31, 6.50, 152.46, 0.74],
    ("528", "ns"): [13.18, 7.13, 116.99, 2.98],
    ("616", "ms"): [18.04, 2.75, 65.95, 0.83],            # Prenzlau: Leistungspreise (1.1) und Arbeitspreise (2.) getrennt
    ("616", "msns"): [24.61, 3.87, 94.34, 1.08],
    ("616", "ns"): [31.90, 4.78, 113.98, 1.50],
    ("262", "msns"): [35.00, 7.50, 199.00, 3.75],         # GIG energy services: Jahresleistungspreissystem (Monatssystem ignoriert)
    ("262", "ns"): [41.10, 10.90, 255.00, 4.90],
    ("262", "slp"): [15.00, 35.00],                       # Entnahme ohne Leistungsmessung, Niederspannung: Grundpreis 35 €/a, 15 ct/kWh
    ("283", "ms"): [11.65, 12.59, 270.44, 2.23],          # Stengle: Tabellen 1.2 (< 2.500 h) und 1.1 (≥ 2.500 h), Spalte Leistungspreis dann Arbeitspreis
    ("283", "ns"): [17.62, 15.74, 340.82, 2.82],
    ("331", "hsms"): [2.74, 3.94, 86.86, 0.57],           # Schwerin: Spalten Arbeitspreis (ct/kWh) vor Leistungspreis (€/kW a) vertauscht
    ("331", "ms"): [2.80, 4.28, 97.89, 0.48],
    ("331", "msns"): [3.48, 5.14, 115.10, 0.67],
    ("331", "ns"): [7.47, 6.98, 105.33, 3.06],
    ("494", "ms"): [9.14, 6.67, 151.47, 0.98],            # Bad Kreuznach: Tabelle mit Leistungsmessung, Netto-Spalten, < / ≥ 2.500 h
    ("494", "msns"): [11.76, 7.54, 164.35, 1.44],
    ("494", "ns"): [14.16, 8.48, 147.55, 3.14],
    ("494", "slp"): [6.81, 93.00],                        # Haushalts-, landwirtschaftlicher, gewerblicher Bedarf in Niederspannung (netto: 93 €/a, 6,81 ct)
    ("762", "ms"): [16.47, 6.40, 174.43, 0.08],           # Sulz am Neckar: Tabellen 1.1.a und 1.1.b
    ("762", "msns"): [13.20, 7.50, 185.32, 0.62],
    ("762", "ns"): [16.35, 8.63, 169.02, 2.52],
    ("762", "slp"): [7.38, 80.00],                        # 2.1.a Kunden der Grundversorgung: Grundpreis 80 €/Jahr, Arbeitspreis 7,38 ct
    ("179", "slp"): [6.16, 39.60],                        # Erlangen: Niederspannung ohne Leistungsmessung, Nettopreis
    ("381", "slp"): [6.16, 55.00],                        # Amberg: Grundpreis 55 €/Jahr, Arbeitspreis 6,16 ct
    ("393", "slp"): [9.05, 0.00],                         # Bad Dürkheim: Entnahmestellen ohne Leistungsmessung, nur Arbeitspreis
    ("247", "slp"): [10.10, 0.00],                        # Steinhagen: Preisblatt 1, nur Arbeitspreis (Kleinkunden)
    ("322", "slp"): [6.66, 0.00],                         # Ahlen: Kleinkunden, Grundpreis-Zelle leer
    ("442", "slp"): [7.70, 0.00],                         # Crailsheim: Entnahmestelle ohne Leistungsmessung (€/a 0,00; ct/kWh 7,70)
    ("623", "slp"): [9.42, 60.00],                        # Rastatt: nicht unterbrechbare Entnahme ohne Lastgangmessung
    ("716", "slp"): [6.68, 78.00],                        # Weinheim: Niederspannung nicht unterbrechbare Anlagen
    ("270", "ms"): [21.63, 7.36, 201.20, 0.17],           # Havelstrom Zehdenick: Mittelspannung, Umspannung MS/NS
    ("270", "msns"): [22.45, 8.08, 224.54, 0.00],
    ("361", "ms"): [24.92, 6.30, 155.81, 1.07],           # Remstalwerk: Mittelspannungsnetz
    ("512", "ms"): [14.97, 4.71, 111.17, 0.87],           # Havelberg: netto-Spalten, Tabellen < / ≥ 2.500 h
    ("512", "msns"): [22.15, 8.86, 193.53, 2.01],
    ("783", "ms"): [12.64, 5.27, 130.08, 0.58],           # SWS Netze: Tagespreis x 365, Arbeitspreis EUR/kWh x 100
    ("783", "msns"): [16.82, 5.67, 125.94, 1.30],
    ("802", "ms"): [21.86, 4.52, 130.62, 0.17],           # ÜZ Mainfranken: Mittelspannung
    ("16", "ms"): [15.55, 4.52, 91.16, 1.50],             # Düsseldorf: Zeilen Mittelspannung (unter und ab 2.500 h)
    ("16", "hsms"): [13.32, 4.28, 105.66, 0.58],          # Umspannung Hoch-/Mittelspannung
    ("109", "ms"): [10.09, 4.54, 105.66, 0.71],           # Mittelspannungsnetz
    ("113", "ms"): [7.68, 3.96, 91.08, 0.62],             # Allgäu: Mittelspannungsnetz
    ("113", "msns"): [9.00, 5.31, 124.08, 0.65],
    ("264", "ms"): [9.32, 7.88, 182.24, 0.96],            # Greiz
    ("264", "msns"): [11.91, 13.13, 340.19, 0.00],
    ("603", "hsms"): [5.16, 1.82, 45.09, 0.22],           # Olching (Textauszug_2026): Jahresleistungspreis RLM
    ("603", "ms"): [6.27, 2.59, 63.53, 0.30],
    ("603", "msns"): [10.50, 2.97, 58.86, 1.04],
    ("603", "ns"): [12.18, 4.05, 61.51, 2.08],
    ("603", "slp"): [2.77, 73.00],
    ("151", "ms"): [2.98, 5.25, 121.18, 0.52],            # Energienetze Bayern (Textauszug_2026, OCR geprüft)
    ("151", "msns"): [3.30, 5.52, 117.21, 0.96],
    ("151", "ns"): [3.65, 6.20, 125.92, 1.31],
    ("151", "slp"): [4.25, 62.05],
    ("42", "slp"): [4.95, 67.80],                         # SWKiel: Netznutzungsentgelt netto Grundpreis €/Jahr, Arbeitspreis ct/kWh
    ("275", "slp"): [10.93, 72.00],                       # HEWA: Arbeitspreis HT- und NT-Mengen (ein Preis)
    ("434", "slp"): [7.55, 30.00],                        # Buchholz: Kleinkunden ohne Bedarfsartendifferenzierung / SLP netto
    ("495", "slp"): [13.03, 43.00],                       # Goch: Entnahme ohne registrierende Lastgangmessung, Kleinkunden
    ("770", "slp"): [5.30, 57.84],                        # SVO Netz
    ("787", "slp"): [8.94, 0.00],                         # Wunsiedel
    ("829", "slp"): [5.41, 60.00],                        # Kleinkunden ohne Bedarfsartendifferenzierung / SLP netto
    ("82", "slp"): [6.88, 50.00],                         # Meckenheim: Grundpreis für SLP NS 50 €/Jahr, Arbeitspreis 6,88 ct
    ("222", "slp"): [8.25, 108.00],                       # Grefrath: Grundpreis per anno 108 €, AP 8,25 ct (Niederspannung ohne Leistungsmessung)
    ("87", "slp"): [7.89, 90.00],                         # SLP: Kunde im Niederspannungsnetz ohne Lastgangzählung (Netto €/Jahr, ct/kWh)
    ("140", "slp"): [6.88, 80.00],
    ("289", "slp"): [5.48, 63.00],
    ("412", "slp"): [9.52, 60.00],                        # BDEW-Artikel 1-02-0-001 / -002
    ("468", "slp"): [8.85, 23.72],                        # Artikel 1-02-0-002 in EUR/kWh x 100
    ("512", "slp"): [7.19, 80.00],
    ("635", "slp"): [5.38, 75.00],
    ("737", "slp"): [9.54, 69.84],
    ("320", "ms"): [11.58, 6.12, 146.21, 0.73],           # Bad Langensalza: BDEW-Artikel-IDs, Preis je Jahr (nicht je Tag)
    ("320", "msns"): [12.06, 7.16, 179.96, 0.45],
    ("320", "ns"): [13.13, 9.48, 159.15, 3.63],
    ("468", "ms"): [16.50, 3.66, 85.12, 0.91],            # Emmerich: Artikel-IDs, Arbeitspreis in EUR/kWh x 100
    ("468", "msns"): [22.69, 4.90, 112.49, 1.31],
    ("468", "ns"): [33.80, 6.92, 154.27, 2.10],
    ("675", "ms"): [28.29, 4.84, 96.05, 2.13],            # Südholstein: Jahresleistungspreissystem NE 5/6/7
    ("675", "msns"): [32.61, 5.52, 108.56, 2.48],
    ("675", "ns"): [40.86, 6.18, 110.29, 3.40],
    ("801", "ms"): [7.79, 5.04, 124.94, 0.35],            # Wörth/Isar-Altheim: Tabellen je Ebene < / > 2.500 h
    ("801", "msns"): [8.59, 5.32, 129.61, 0.48],
    ("801", "ns"): [10.36, 5.52, 124.81, 0.94],
    ("75", "hsms"): [8.43, 4.37, 97.24, 0.81],            # CPM Netz: Netzebenen 3-7 (Preisblatt auf cpm-netz.evonik.de)
    ("75", "ms"): [40.35, 3.04, 82.08, 1.37],
    ("75", "msns"): [48.74, 3.61, 97.16, 1.67],
    ("75", "ns"): [59.96, 3.64, 91.67, 2.38],
    ("306", "ms"): [9.19, 3.67, 84.93, 0.64],             # Mainsite (vorläufiges Preisblatt): Entnahme aus MSP, MSP/NSP, NSP
    ("306", "msns"): [14.50, 6.10, 144.66, 0.90],
    ("306", "ns"): [17.97, 8.19, 181.05, 1.66],
    ("564", "slp"): [6.15, 70.00],                        # Marburg: Entnahme ohne Leistungsmessung, Niederspannung
    ("564", "hsms"): [9.49, 3.10, 58.57, 1.14],           # Marburg: Tabellen "< 2.500" und "≥ 2.500" je Entnahmestelle
    ("564", "ms"): [21.35, 4.70, 87.60, 2.05],
    ("564", "msns"): [24.85, 5.81, 105.54, 2.58],
    ("564", "ns"): [34.47, 7.38, 144.49, 2.98],
    ("88", "ms"): [24.13, 7.67, 188.56, 1.09],            # EGC: Tabellen "bis" und "über 2.500 h" mit Netto/Brutto-Spalten
    ("88", "msns"): [27.92, 9.01, 205.57, 1.90],
    ("88", "ns"): [31.62, 9.70, 173.04, 4.04],
    ("106", "ms"): [27.00, 8.05, 210.00, 0.75],           # Nordhalben: Zeilen mit €-Zeichen, bis/über 2.500 h
    ("106", "msns"): [27.00, 8.05, 210.00, 0.00],
    ("106", "ns"): [25.00, 9.00, 180.00, 3.50],
    ("240", "ms"): [24.21, 6.78, 174.33, 0.77],           # Nümbrecht: je Ebene zwei Zeilen < / > 2.500 h
    ("240", "msns"): [26.89, 7.96, 208.70, 0.69],
    ("240", "ns"): [40.55, 7.62, 161.49, 2.79],
    ("318", "ms"): [21.64, 10.31, 226.64, 0.85],          # Netz & Energie: zwei Tabellen bis/über 2.500 h
    ("318", "ns"): [32.61, 14.88, 237.32, 4.75],
    ("318", "slp"): [10.96, 70.00],                       # SLP: Grundpreis 70 EUR/Jahr, Arbeitspreis 10,96 ct (Spalten vertauscht gelesen)
    ("9", "ms"): [11.17, 7.00, 146.10, 1.60],             # enercity: Tagesleistungspreis (0,03060274 / 0,40027397) x 365, vorher gerundet
    ("9", "hsms"): [7.55, 5.51, 125.94, 0.77],            # enercity: 0,02068493 / 0,34504110 x 365
    ("638", "ms"): [15.24, 7.83, 173.54, 1.50],           # Schifferstadt: zwei Tabellen (< und > 2.500 h), Ebenen vermischt gelesen
    ("638", "msns"): [18.94, 8.84, 184.55, 2.22],
    ("638", "ns"): [21.51, 10.27, 217.43, 2.43],
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
    ("262", "ms"): "Im Jahresleistungspreissystem des Dokuments gibt es keine Mittelspannung (nur Monatssystem): gelesene Werte waren Müll",
    ("508", "ms"): "Werte waren NS-Preise (32,14 / 186,50), im Jahresleistungspreissystem keine MS-Preise im Dokument",
    ("52", "hsms"): "Werte sind SLP-Preise (98,00 / 5,69), keine HS/MS-Ebene im Dokument",
    ("194", "hsms"): "Werte im Dokument nicht belegt (von Hand am Text geprüft)",
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
        if eb == "slp":
            r[I["slp_ap_ct_kwh"]], r[I["slp_grundpreis_eur_jahr"]] = fmt(v[0]), fmt(v[1])
        else:
            for k, x in zip(F, v):
                r[I[f"{eb}_{k}"]] = fmt(x)
        note = f"Korrigiert: {eb.upper()} " + ("aus Textauszug des Kollegen (Original-PDF nicht bei uns, nicht am Dokument bestätigt)" if nr in TEXTAUSZUG else "von Hand am Dokument geprüft und korrigiert")
        if NOTIZ.get((nr, eb)): note += f" ({NOTIZ[(nr, eb)]})"
        if note not in r[I["hinweis"]]:
            r[I["hinweis"]] = note + ("; " + r[I["hinweis"]] if r[I["hinweis"]] else "")
        r[I["geprueft"]] = "" if nr in TEXTAUSZUG else "ja"     # am Dokumenttext von Hand geprüft; Textauszug des Kollegen: nicht am Dokument bestätigt
    for (nr, eb) in ENTFERNEN:                          # entfernte Ebenen auch in der Handtabelle leeren
        r = byn.get(nr)
        if r is not None and (nr, eb) not in KORRIGIEREN:
            for k in F:
                if f"{eb}_{k}" in I:
                    r[I[f"{eb}_{k}"]] = ""
    out = io.StringIO(); w = csv.writer(out, delimiter=";", lineterminator=nl); w.writerows(rows)
    open(p, "w", encoding="utf-8", newline="").write(("﻿" if bom else "") + out.getvalue())
    # Entfernen: lauf/werte_entfernt.csv ergänzen
    pe = "lauf/werte_entfernt.csv"
    alt = {(r["nr"], r["ebene"]): r["grund"] for r in csv.DictReader(open(pe, encoding="utf-8-sig"), delimiter=";")}
    alt.update(ENTFERNEN)
    for k in KORRIGIEREN:                               # eine Handkorrektur ersetzt eine frühere Entfernung derselben Ebene
        if k in alt and k not in ENTFERNEN:
            del alt[k]
    with open(pe, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(["nr", "ebene", "grund"])
        for (nr, eb), g in sorted(alt.items(), key=lambda kv: (int(kv[0][0]), kv[0][1])):
            w.writerow([nr, eb, g])
    print(len(KORRIGIEREN), "korrigiert,", len(ENTFERNEN), "entfernt")

main()
