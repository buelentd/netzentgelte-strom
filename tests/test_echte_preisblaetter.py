"""Regressionstests an Textauszügen echter Preisblätter 2026 (pdftotext -layout bzw. xlsx-Text aus dem
Lauf vom 30.10.2026). Erwartete NS-Werte = geprüfte Pilotwerte; MS/NS und SLP von Hand am Text geprüft.

Abgedeckte Layouts (Fortsetzung unten im Dict): Spaltenköpfe über der Startzeile (RheinNetz, Münster),
"Entnahme aus …"-Labels (wesernetz), nur teilweise lesbare Einheiten (Pfalzwerke, E-Werk), fehlendes ≥
(Offenbach, MVV), Zeilenpaare je Benutzungsdauer (Magdeburg), SLP-Varianten nach Rechnungslegung (Halle),
Netto-dann-Brutto-Spalten (WSW, Duisburg). Weitere Layouts: BDEW-Artikel-IDs mit Netto/Brutto (Berlin), mit Tageswerten (SWM, EWE mit 8
Nachkommastellen, Netze BW xlsx), Tabellen mit Monatsleistungspreis-Spalten (ODR), fiktiver Zusatztabelle
(Netze BW), Einheiten in der Zeile und kV-Angaben (e-netz), EUR/(kW · d) und "> =" (enercity),
SLP mit Netto/Brutto, Beispielrechnung und Modul-3-Tabelle (MITNETZ), PRICAT-Spaltenversatz (WWN).
"""
from pathlib import Path

import pytest

from vnb.extract import FELDER, jahr_pruefen, metadaten, tabellen_lesen

ECHT = Path(__file__).parent / "echt"

FAELLE = {
    "stromnetz_berlin_2026": ((8.39, 7.14, 93.87, 3.72), (6.14, 5.66, 84.20, 2.54), (7.46, 33.36)),
    "swm_2026": ((24.39, 6.19, 153.13, 1.04), (17.32, 5.40, 144.11, 0.33), (6.47, 63.27)),
    "netze_bw_2026": ((18.64, 7.49, 171.87, 1.36), (16.52, 6.26, 146.49, 1.06), None),
    "netze_bw_2026_xlsx": ((18.64, 7.49, 171.87, 1.36), (16.52, 6.26, 146.49, 1.06), (7.57, 84.00)),
    "ewe_2026": ((13.14, 4.85, 63.29, 2.85), (13.95, 3.67, 68.21, 1.50), (3.20, 102.00)),
    "mitnetz_2026": ((46.88, 4.99, 146.63, 1.00), (41.40, 4.37, 128.15, 0.90), (6.31, 73.00)),
    "enetz_suedhessen_2026": ((34.10, 8.33, 203.11, 1.57), (28.83, 7.65, 192.93, 1.09), (5.63, 92.00)),
    "wwn_2026": ((13.29, 7.44, 102.06, 3.89), (11.76, 6.47, 125.34, 1.93), (6.46, 120.45)),
    "enercity_2026_tag": ((20.50, 8.12, 102.70, 4.83), (15.30, 7.50, 153.82, 1.96), None),
    "enercity_2026_jahr": ((20.50, 8.12, 102.70, 4.83), None, (8.54, 53.00)),
    "netze_odr_2026": ((10.75, 6.26, 138.57, 1.14), (17.74, 7.43, 139.96, 2.54), (5.87, 65.70)),
    # Lauf vom 30.10.2026 (Pilot 50): Fälle, die vorher nicht gelesen wurden
    "rheinnetz_2026": ((33.36, 7.40, 172.43, 1.84), (23.09, 5.82, 143.67, 1.00), (3.78, 150.00)),
    "stadtnetze_muenster_2026": ((9.27, 7.52, 152.53, 1.79), (9.13, 7.33, 151.49, 1.63), None),
    "wesernetz_2026": ((13.17, 6.46, 84.94, 3.58), (11.31, 5.46, 114.52, 1.33), (5.46, 65.00)),
    "pfalzwerke_2026": ((25.89, 5.67, 96.88, 2.84), (23.38, 5.53, 113.77, 1.92), None),
    "netze_magdeburg_2026": ((3.55, 8.08, 110.77, 3.79), (3.26, 7.97, 162.65, 1.59), None),
    "offenbach_2026": ((22.95, 6.19, 97.04, 3.22), (22.04, 6.01, 143.27, 1.16), (5.87, 69.00)),
    "ewerk_netze_2026": ((19.28, 7.86, 161.92, 2.15), (16.17, 6.40, 129.10, 1.88), (7.01, 98.00)),
    "mvv_netze_2026": ((17.16, 6.28, 103.91, 2.81), (16.66, 4.52, 107.58, 0.89), (4.32, 90.00)),
    "naturenergie_2026": ((21.66, 6.76, 74.56, 4.64), (21.38, 6.72, 143.16, 1.85), (7.30, 90.00)),
    "evh_halle_2026": ((26.76, 8.28, 148.97, 3.39), (24.64, 7.54, 161.58, 2.06), (6.86, 88.00)),
    "netze_duisburg_2026": ((16.95, 7.73, 136.60, 2.94), (12.79, 6.76, 135.60, 1.85), (6.96, 101.00)),
    "wsw_2026": ((13.59, 6.52, 169.66, 0.28), None, (6.40, 64.90)),
    "swka_2026": ((22.21, 7.11, 102.31, 3.90), (22.78, 5.16, 136.68, 0.61), (7.14, 90.00)),
    # gedrehte Tabellen: Zeilen Arbeits-/Leistungspreis, Spalten < / ≥ 2.500 (Lauf 8)
    "netz_leipzig_2026": ((19.17, 5.96, 82.02, 3.44), (13.12, 5.42, 103.16, 1.82), (4.29, 75.00)),
    "sachsennetze_ns_2026": ((27.83, 8.58, 153.33, 3.56), None, None),
    # Lauf 9 (erste Nicht-Pilot-Netzbetreiber), von Hand am Text geprüft: Aufzählungszeichen "n "/"●",
    # "Umspannung (MSP/NSP)", Monatspreis-Spalten in derselben Tabelle, "Niederlasttarif"
    "abita_2026": ((46.16, 6.16, 126.42, 2.95), (36.96, 6.30, 187.66, 0.27), (7.07, 75.00)),
    "alliander_heinsberg_2026": ((20.50, 5.94, 134.31, 1.39), (14.65, 5.36, 124.39, 0.97), (6.64, 110.00)),
    "ascanetz_2026": ((31.69, 6.15, 133.03, 2.10), (25.93, 5.61, 128.87, 1.49), (7.18, 30.00)),
    "avu_netz_2026": ((19.79, 7.23, 167.82, 1.31), (12.27, 6.74, 154.82, 1.03), (6.71, 70.00)),
    # Messstellenbetrieb-Tabellen zwischen den Netzentgelten dürfen keine Grundpreise liefern
    "sw_oranienburg_2026": ((38.79, 6.78, 136.71, 2.87), (27.36, 5.53, 122.46, 1.73), (8.46, 50.00)),
    "sw_lippe_weser_2026": ((20.76, 8.00, 171.13, 1.98), (18.41, 6.41, 145.04, 1.34), (7.55, 79.00)),
    # Kopf [€/kW * Tag] [€/kWh]; Zeilen "(informatorisch) (15,07 €/kW*Jahr)" dürfen ihn nicht ersetzen
    "sw_greifswald_2026": ((15.07, 7.01, 115.77, 2.98), None, None),
    # Artikel-ID-Zeilen unter den Werten (Werte spaltenweise eine Zeile darüber)
    "esw_netz_2026": ((18.64, 8.87, 187.49, 2.12), (14.23, 7.78, 166.22, 1.70), None),
    # gedrehte Tabellen je Seite "Netzanschluss … / Messung …", dritte Seite Mittelspannung
    "freital_2026": ((104.39, 6.90, 203.39, 2.94), (72.86, 5.71, 180.86, 1.39), None),
    # "Spannungsebene NS"; Standardlastprofil-Abschnitt "Entnahme von bis zu 100.000 kWh"
    "syna_2026": ((23.99, 8.08, 156.65, 2.78), (14.35, 7.94, 183.27, 1.19), (8.67, 91.25)),
    # Spaltenkopf "Leistungspreissystem für:" schließt den Standardlastprofil-Preis nicht aus
    "stuttgart_netze_2026": ((34.42, 8.95, 164.89, 3.73), (29.14, 7.85, 160.17, 2.61), (10.16, 55.00)),
    # Einheiten "in € pro kW und Jahr" / "in ct pro kWh", zweite Zeile "(Netzbereich 7) >= 2.500 h/a"
    "emb_miltenberg_2026": ((19.53, 10.48, 244.13, 1.50), (19.39, 10.20, 235.16, 1.57), (8.01, 115.00)),
    # Kopf "Jahresbenutzungsstunden" / "< 2.500 Bh"
    "sw_elmshorn_2026": ((27.37, 7.51, 144.78, 2.81), None, None),
}


def lesen(name):
    roh = (ECHT / f"{name}.txt").read_text(encoding="utf-8")
    kopf, _, text = roh.partition("\n\n")
    url = kopf.splitlines()[0].removeprefix("URL: ")
    e = tabellen_lesen(text.split("\f\n"))
    metadaten(e, url)
    return e, url


@pytest.mark.parametrize("name", FAELLE)
def test_echtes_preisblatt(name):
    ns, msns, slp = FAELLE[name]
    e, url = lesen(name)
    assert jahr_pruefen(e, 2026, url) is None
    assert tuple(round(e.ns[f], 2) for f in FELDER) == ns
    assert not e.unklar, e.unklar
    if msns:
        assert tuple(round(e.msns[f], 2) for f in FELDER) == msns
    if slp:
        assert (round(e.slp["ap"], 2), round(e.slp["gp"], 2)) == slp
        assert not e.slp_unklar, e.slp_unklar


def test_preisstand_aenderungshistorie_ewe():
    # "15.10.2025 Vorläufige Netzentgelte" in der Änderungshistorie macht das Blatt nicht vorläufig
    e, _ = lesen("ewe_2026")
    assert e.preisstand != "vorläufig"


def test_enercity_tagesgrundpreis():
    # "Grundpreis als" / "Tagespreis" / "in EUR/d" über drei Kopfzeilen: 0,14520548 €/d × 365
    e, _ = lesen("enercity_2026_tag")
    assert (round(e.slp["ap"], 2), round(e.slp["gp"], 2)) == (8.54, 53.00)


def test_pfalzwerke_grundpreis_ohne_einheit_bleibt_offen():
    e, _ = lesen("pfalzwerke_2026")
    assert "gp" not in e.slp and e.slp_unklar


def test_vermiedene_netzentgelte_abgelehnt():
    from vnb.extract import vne_dokument
    assert vne_dokument("", "https://x.de/2026-10-08_vNE_Westnetz.pdf")
    assert vne_dokument("", "https://x.de/vorlaeufige-preisblaetter-vermiedene-netzentgelte-2026.pdfx")
    assert vne_dokument("Referenzpreisblatt zur Ermittlung vermiedener Netzentgelte\nnach § 18 Abs. 2 StromNEV", "")
    assert not vne_dokument("Preisblatt Netzentgelte Strom 2026", "https://x.de/preisblatt-nne-2026.pdf")


def test_altes_preisblatt_schwentinental_abgelehnt():
    # Dateiname und Kopf "gültig ab 01. Jan 2024": kein Blatt für 2026
    e, url = lesen("sw_schwentinental_2024")
    assert jahr_pruefen(e, 2026, url) is not None


def test_endkunden_preisblatt_abgelehnt():
    from vnb.extract import liefer_dokument
    assert liefer_dokument("Preisblatt Grundversorgung Strom 2026\nAllgemeine Preise", "")
    assert liefer_dokument("", "https://x.de/heizstrom-preise-2026.pdf")
    assert not liefer_dokument("Preisblatt Netzentgelte Strom 2026\nEntgelte für die Netznutzung", "")


def test_gas_nur_als_wort():
    from vnb.crawl import SPARTE_FREMD
    assert SPARTE_FREMD.search("preisblatt_gas_2026.pdf")
    assert SPARTE_FREMD.search("erdgas netzentgelte")
    assert SPARTE_FREMD.search("Gasnetz Preisblatt 2026")
    assert not SPARTE_FREMD.search("netzentgelte-strom-gasse-2026.pdf")


@pytest.mark.parametrize("name, slp", [
    ("donetz_2026", (5.30, 99.50)),                     # Überschrift mit weitem Spaltenabstand
    ("netze_magdeburg_lastprofil_2026", (4.18, 100.00)),  # "Entnahme mit Lastprofil"
    ("stwbo_netz_2026", (6.72, 80.00)),                 # "ohne 1/4-h-Leistungsmessung"
    ("bhag_2026", (10.04, 84.00)),                      # Sammelzeile mit Wärmepumpen; §-14a-Tabelle danach
    ("sw_neuburg_2026", (11.35, 80.00)),                # Modul-3-Kopf "ohne Leistungsmessung | Niedriglasttarif …"
    ("sw_waren_2026", (5.76, 50.00)),                   # "Kleinkunden … / SLP / Pauschalanlagen"
    ("albwerk_2026", (4.56, 96.00)),                    # Spaltenkopf "HT  NT" schließt "Standardkunden" nicht aus
    ("harz_energie_netz_2026", (6.53, 73.50)),          # "Netz- bwz." / "Umspannebene" über zwei Zeilen
    ("swa_netze_2026", (6.07, 66.20)),                  # "ohne steuerbare oder unterbrechbare Verbrauchseinrichtungen"
    ("n_ergie_kol_2026", (5.96, 95.00)),                # "ohne registrierende Lastgangmessung", "Grundbetrag"
    ("netz_duesseldorf_2026", (7.91, 12.00)),           # "Jährlicher Grundpreis für Netznutzung" nach Speicherheizung
])
def test_slp_abschnitt_erkannt(name, slp):
    e, _ = lesen(name)
    assert (round(e.slp["ap"], 2), round(e.slp["gp"], 2)) == slp
    assert not e.slp_unklar, e.slp_unklar


def test_slp_borken_pauschale_reduktion_nicht_vertauscht():
    # Kopf "Grundpreis | Arbeitspreis | pauschale Reduktion": lieber nichts als vertauschte Werte
    e, _ = lesen("sw_borken_2026")
    assert e.slp.get("ap") != 90.0 and e.slp.get("gp") != 9.66


def test_ewr_bis_einschliesslich_2500():
    # "bis einschließlich 2.500 h" / "oberhalb 2.500 h": Grenze ≤ 2.500 / > 2.500
    e, _ = lesen("ewr_netz_2026")
    assert tuple(round(e.ns[f], 2) for f in FELDER) == (63.46, 8.40, 187.56, 3.43)
    assert e.grenze_le
