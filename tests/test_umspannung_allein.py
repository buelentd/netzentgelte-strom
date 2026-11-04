"""Zeile nur "Umspannung" (ohne Zusatz) ist Umspannung MS/NS (EW Geiger)."""
from vnb.extract import ebene

def test_umspannung_allein():
    assert ebene("Umspannung") == "MSNS"
    assert ebene("Umspannung HS/MS") is None
    assert ebene("Niederspannung") == "NS"


def test_artikel_id_mittelspannung():
    """BDEW-Artikel-IDs 1-01-5-xxx = Mittelspannung (Peine, Tagesleistungspreis x 365)."""
    from vnb.extract import ARTIKEL_FELD
    assert ARTIKEL_FELD[("1", "5", "003")] == ("MS", "lp_ueber_2500")
    assert ARTIKEL_FELD[("1", "4", "001")] == ("HSMS", "lp_unter_2500")
