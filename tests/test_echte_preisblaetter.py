"""Regressionstests an Textauszügen echter Preisblätter 2026 (pdftotext -layout bzw. xlsx-Text aus dem
Lauf vom 30.10.2026). Erwartete NS-Werte = geprüfte Pilotwerte; MS/NS und SLP von Hand am Text geprüft.

Abgedeckte Layouts: BDEW-Artikel-IDs mit Netto/Brutto (Berlin), mit Tageswerten (SWM, EWE mit 8
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
