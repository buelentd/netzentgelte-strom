"""Preise als Tabelle in einer Webseite (kein PDF): der Crawler legt den Seitentext als <hash>.html ab, die Auswertung liest ihn."""
from pathlib import Path

from vnb.extract import auswerten

HIER = Path(__file__).parent


def test_html_preisseite_wird_gelesen():
    e = auswerten(HIER / "daten" / "preisseite_beispiel.html", "https://beispiel.de/netzentgelte", 2026)
    assert e.ns == {"lp_unter_2500": 21.5, "ap_unter_2500": 6.1, "lp_ueber_2500": 118.4, "ap_ueber_2500": 2.35}
    assert e.msns["lp_ueber_2500"] == 96.3
    assert e.slp == {"ap": 7.3, "gp": 45.0}
    assert e.preisstand == "endgültig"
