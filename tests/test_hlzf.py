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


def test_export_conplot(tmp_path):
    # Export: nur geprüfte Werte, beide Tarifgruppen, Grenze, Hochlastzeitfenster, PLZ-Zuordnung
    import json
    import shutil
    from vnb.export import erzeugen
    for f in ("netzentgelte_2026.csv", "gefunden.csv", "plz_netzbetreiber.csv", "hochlastzeitfenster_2026.csv"):
        shutil.copy(Path(__file__).parent.parent / "ergebnis" / f, tmp_path / f)
    zahlen = erzeugen(tmp_path, 2026)
    assert zahlen["netzbetreiber"] >= 800 and zahlen["rlm_ns"] > 0
    d = json.loads((tmp_path / "conplot" / "netzbetreiber_2026.json").read_text(encoding="utf-8"))
    for e in d["netzbetreiber"]:
        if e["rlm"] and e["rlm"]["ns"]:
            ns = e["rlm"]["ns"]
            assert ns["lp_unter_eur_kw_jahr"] < ns["lp_ab_eur_kw_jahr"] and e["grenze"] in ("<2500", "<=2500")
        assert ("rlm_ns" in e["fehlt"]) == (not (e["rlm"] and e["rlm"]["ns"]))
    plz = json.loads((tmp_path / "conplot" / "plz_2026.json").read_text(encoding="utf-8"))
    assert all(isinstance(v, list) and v for v in plz.values())


def test_zeile_je_fenster_mit_dauer():
    from vnb.hlzf import hlzf_lesen
    t = """Hochlastzeitfenster 2026
Umspannung Mittelspannung/Niederspannung
 Jahreszeit  Beginn        Ende       Dauer
Frühjahr         -           -           -
Herbst      17:45 Uhr    18:15 Uhr    00:30 h
Winter      17:15 Uhr    19:15 Uhr    02:00 h
Niederspannungsnetz
 Jahreszeit   Beginn             Ende          Dauer
Frühjahr     10:15 Uhr         10:45 Uhr       00:30 h
Sommer           -                 -              -
"""
    e = hlzf_lesen(t)
    assert e.fenster["MSNS"]["winter"] == ["17:15-19:15"] and e.fenster["MSNS"]["herbst"] == ["17:45-18:15"]
    assert e.fenster["NS"]["fruehling"] == ["10:15-10:45"] and e.fenster["NS"]["sommer"] == []


def test_ebene_mit_von_bis_spalten():
    from vnb.hlzf import hlzf_lesen
    t = """Hochlastzeitfenster 2026
NS                             Frühling               Sommer                   Herbst                     Winter
                       von                bis   von            bis       von            bis         von            bis
                           -                -     -              -       16:45          19:45      16:30           19:30
"""
    e = hlzf_lesen(t)
    assert e.fenster["NS"] == {"fruehling": [], "sommer": [], "herbst": ["16:45-19:45"], "winter": ["16:30-19:30"]}


def test_neue_form_wird_abgelehnt_wenn_zeiten_uebersehen_werden():
    from vnb.hlzf import hlzf_lesen
    # Uhrzeiten im Format 08:30:00 und eine Ebene ohne lesbare Zeilen: nicht "keins" melden
    t = """Hochlastzeitfenster 2026
Entnahmeebene     Winter      Frühling      Sommer      Herbst
                  von  bis    von  bis      von bis     von bis
1. Mittelspannung   08:30:00 - 13:15:00
3. Niederspannung                          12:00:00 - 12:30:00     10:45:00 - 12:30:00
"""
    e = hlzf_lesen(t)
    assert not e.fenster or e.fenster.get("NS", {}).get("sommer") != []


def test_block_je_ebene_mit_mittigem_namen_und_zweitem_fenster():
    from vnb.hlzf import hlzf_lesen
    t = """Hochlastzeitfenster 2026
           Netzebene                     Jahreszeit                       Zeiten
                                            Winter                     09:30 – 13:00
                                           Frühling                         –
        Mittelspannung
                                           Sommer                           –
                                            Herbst                     11:15 – 12:30
           Netzebene                     Jahreszeit                       Zeiten
                                                                       10:15 – 12:30
                                            Winter
                                                                       17:30 – 18:15
                                           Frühling                         –
       Niederspannung
                                           Sommer                           –
                                            Herbst                          –
"""
    e = hlzf_lesen(t)
    assert e.fenster["NS"]["winter"] == ["10:15-12:30", "17:30-18:15"]
    assert e.fenster["NS"]["herbst"] == [] and e.fenster["NS"]["frühling" if False else "fruehling"] == []
