import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "daten"))
import hlzf_zeitreihe as z


def _tag(v, jahr, monat, tag):
    import datetime as dt
    i = (dt.date(jahr, monat, tag) - dt.date(jahr, 1, 1)).days * 96
    return sum(v[i:i + 96])


def test_vektor_laenge_und_regeln():
    zeile = {"bundesland": "Bayern", "hlzf_ns_winter": "08:00-09:00, 16:45-20:00", "hlzf_ns_sommer": "keins"}
    v = z.vektor(zeile, "ns", 2026)
    assert len(v) == 35040
    assert _tag(v, 2026, 1, 5) == 4 + 13          # Montag: 1 h + 3,25 h
    assert _tag(v, 2026, 1, 6) == 0               # Heilige Drei Könige (Bayern)
    assert _tag(v, 2026, 1, 3) == 0               # Samstag
    assert _tag(v, 2026, 12, 28) == 0             # zwischen Weihnachten und Neujahr
    assert _tag(v, 2026, 7, 15) == 0              # Sommer "keins"
    assert _tag(z.vektor(dict(zeile, bundesland="Berlin"), "ns", 2026), 2026, 1, 6) == 17   # in Berlin Werktag
