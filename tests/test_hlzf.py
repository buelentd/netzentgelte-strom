"""Hochlastzeitfenster und Erheblichkeitsschwellen aus Textauszügen echter Dokumente 2026."""
from pathlib import Path

import pytest

from vnb.hlzf import hlzf_lesen

ORDNER = Path(__file__).parent / "hlzf"


def lesen(name):
    roh = (ORDNER / f"{name}.txt").read_text(encoding="utf-8")
    return hlzf_lesen(roh.partition("\n\n")[2], roh.split("\n", 1)[0][5:].strip())


@pytest.mark.parametrize("name, ns, msns", [
    # Jahreszeiten als Spalten, "Winter" eine Zeile höher, Ebenen-Bezeichnung um die Zeiten umbrochen (Bonn)
    ("bonn", {"winter": ["17:15-19:45"], "herbst": ["18:00-19:00"]}, {"winter": ["17:15-19:45"], "herbst": ["17:45-19:00"]}),
    # je Ebene eine eigene Tabelle mit Zeilen "HLZF-1" / "HLZF-2" (Singen)
    ("singen", {"winter": ["10:45-13:45", "16:45-19:15"]}, {"fruehling": ["18:00-19:00"], "winter": ["11:30-12:45", "16:45-19:15"]}),
    # Ebenen als Spalten, "ja / kein HLF" mit Zeiten darunter (EVKR)
    ("evkr", {"sommer": ["11:15-12:15"]}, {"herbst": ["17:15-18:15"], "winter": ["17:00-19:45"]}),
    # eine Zeile je Ebene und Jahreszeit (EWF)
    ("ewf", {"herbst": ["09:00-12:00"], "winter": ["11:00-14:00"]}, {"winter": ["15:30-19:15"]}),
    # Ebenen als Spalten, Jahreszeit mittig zwischen ihren Zeiten (Bitterfeld-Wolfen)
    ("bitterfeld", {"herbst": ["11:00-12:30"], "winter": ["10:45-12:15", "17:00-18:30"]}, None),
])
def test_hochlastzeitfenster(name, ns, msns):
    e = lesen(name)
    assert e.jahr == 2026
    gelesen = {k: v for k, v in e.fenster["NS"].items() if v}
    assert gelesen == ns
    if msns is not None:
        assert {k: v for k, v in e.fenster["MSNS"].items() if v} == msns


def test_schwellen_aus_tabelle():
    e = lesen("evkr")
    assert e.schwelle == {"MSNS": 30, "NS": 30} and e.mindest_kw == {"MSNS": 100, "NS": 100}


def test_modul3_ist_kein_hochlastzeitfenster():
    # "Hochlastzeitfenster" der zeitvariablen Netzentgelte (§ 14a Modul 3) nicht als HLZF lesen (Halberstadt)
    assert not lesen("halberstadt_modul3").gelesen


def test_mehrere_netzgebiete_nicht_raten():
    e = lesen("gw_zwei_gebiete")
    assert not e.gelesen and "mehrere Netzgebiete" in e.grund
