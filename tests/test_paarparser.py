from vnb.paarparser import paarparser

DEGGENDORF = """Entnahmeebene          Jahres-benutzungsdauer     Leistungspreis    Arbeitspreis
                       < 2.500                  32,78                    5,34
Mittelspannung 5)
                       > 2.500                 151,92                    0,57
                       < 2.500                  34,62                    5,60
Umspannung MS/NS
                       > 2.500                 144,70                    1,20
                       < 2.500                  35,18                    6,93
Niederspannung
                       > 2.500                 153,32                    2,20""".split("\n")

def test_label_zwischen_den_zeilen():
    r = paarparser(DEGGENDORF)
    assert r["ms"] == [32.78, 5.34, 151.92, 0.57]
    assert r["msns"] == [34.62, 5.6, 144.7, 1.2]
    assert r["ns"] == [35.18, 6.93, 153.32, 2.2]

def test_hsms_auf_zwei_zeilen():
    z = ["Umspannung < 2.500 h 6,69 2,67", "HS/MS >= 2.500 h 72,29 0,04", "< 2.500 h 14,08 4,73", "Mittelspannung", ">= 2.500 h 113,83 0,74"]
    r = paarparser(z)
    assert r["hsms"] == [6.69, 2.67, 72.29, 0.04] and r["ms"] == [14.08, 4.73, 113.83, 0.74]
