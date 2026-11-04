"""Zeile nur "Umspannung" (ohne Zusatz) ist Umspannung MS/NS (EW Geiger)."""
from vnb.extract import ebene

def test_umspannung_allein():
    assert ebene("Umspannung") == "MSNS"
    assert ebene("Umspannung HS/MS") is None
    assert ebene("Niederspannung") == "NS"
