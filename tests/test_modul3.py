from vnb.modul3 import lesen, formatieren

SPALTEN = """
Modul 3                                  Fenster NT                     Fenster ST                     Fenster HT
   Zeitfenster Ebene Niederspannung      Niedriglasttarif               Standardtarif                  Hochtarif
   Quartal 1 - 4: 01.01. - 31.12.          01:30-04:15                alle restlichen Zeiten              07:00-20:00
                                                                                                          und
                                                                                                          22:00-00:15
"""

GRUPPE = """
Modul 3
 Niedriglasttarif NT      00:00-01:00       12:30-17:00       2,54
                          22:30-00:00
 Standardlasttarif ST     01:00-07:45        10:00-12:30      6,36
                          17:00-19:30        21:45-22:30
 Hochlasttarif HT         07:45-10:00        19:30-21:45      10,85
"""

QUARTAL = """
Modul 3                    HT                NT                ST
                       11:00-13:00        23:00-07:00         Restzeit
                       17:00-19:00
AP gilt nur in   Q1 + Q4   30,00   13,89   3,10   9,26
"""


def test_spalten():
    e, g = lesen(SPALTEN)
    assert formatieren(e) == ("07:00-20:00, 22:00-00:15", "Restzeit", "01:30-04:15", "ganzjährig")


def test_zeilengruppe():
    e, g = lesen(GRUPPE)
    ht, st, nt, q = formatieren(e)
    assert ht == "07:45-10:00, 19:30-21:45" and nt == "00:00-01:00, 12:30-17:00, 22:30-00:00"


def test_quartale_aus_abschnitt():
    e, g = lesen(QUARTAL)
    assert formatieren(e)[3] == "Q1+Q4"


def test_nicht_eindeutig_bleibt_leer():
    assert lesen("Modul 3\n Hochtarif 17:00-19:00\n")[0] is None
