"""Schritt `liste` am Stück wie im Workflow: realistischer Export (Format wie der MaStR-Gesamtexport,
> 300 Stromnetzbetreiber, Gas-/Übertragungsnetzbetreiber, geschlossenes Netz, beendete Tätigkeit),
Download über einen lokalen Server, der Verbindungen abbricht, dann run.schritt_liste."""
import argparse
import csv

import pytest

import run
from tests.test_mastr_download import _server
from tests.test_mastr_xml import _xml
from vnb import mastr_download


def _export(pfad):
    import zipfile
    kat = [{"Id": "1", "Wert": "Anschlussnetzbetreiber"}, {"Id": "5", "Wert": "Übertragungsnetzbetreiber"},
           {"Id": "8", "Wert": "Kernenergie"}, {"Id": "1400", "Wert": "Bayern"}, {"Id": "50", "Wert": "Strom"}]
    akteure, rollen, netze, nap, solar = [], [], [], [], []

    def vnb(nr, name, web="", funktion="1", rolle="1", ende=None, gvn="0", mail=""):
        a = {"MastrNummer": nr, "Firmenname": name, "Marktfunktion": funktion, "Bundesland": "1400", "Ort": "Ort"}
        for k, v in (("Webseite", web), ("Taetigkeitsende", ende), ("Email", mail)):
            if v:
                a[k] = v
        akteure.append(a)
        rollen.append({"MarktakteurMastrNummer": nr, "Marktrolle": rolle})
        netze.append({"MastrNummer": "N" + nr, "Bundesland": "1400", "Sparte": "50", "GeschlossenesVerteilnetz": gvn})
        for i in range(12):
            nap.append({"LokationMaStRNummer": f"L{nr}{i}", "NetzbetreiberMaStRNummer": nr, "NetzMaStRNummer": "N" + nr})
            solar.append({"LokationMaStRNummer": f"L{nr}{i}", "Bundesland": "1400", "Landkreis": "LK " + nr,
                          "Gemeinde": "Stadt " + nr, "Gemeindeschluessel": "09" + nr[-6:], "Postleitzahl": "8" + nr[-4:]})
    vnb("SNB000000001", "Stromnetz Berlin GmbH", "www.stromnetz.berlin")
    vnb("SNB000000002", "Dortmunder Netz GmbH", "do-netz.de")
    vnb("SNB000000003", "Ohne Web Netz GmbH", mail="info@ohneweb-netz.de")
    for i in range(310):
        vnb(f"SNB1{i:08d}", f"Stadtwerke {i} Netz GmbH &amp; Co. KG", f"https://sw{i}.de")
    for i in range(50):
        vnb(f"SNB2{i:08d}", f"Gasnetz {i} GmbH", "gas.de", funktion="8")
    vnb("SNB300000001", "TenneT TSO GmbH", "tennet.eu", rolle="5")
    vnb("SNB300000002", "Alt Netz GmbH", "alt.de", ende="2019-12-31")
    vnb("SNB300000003", "Industriepark Netz GmbH", "ip.de", gvn="1")
    with zipfile.ZipFile(pfad, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("Katalogwerte.xml", _xml("Katalogwerte", "Katalogwert", kat))
        z.writestr("MarktakteureUndRollen.xml", _xml("MarktakteureUndRollen", "MarktakteurUndRolle", rollen))
        z.writestr("Marktakteure_1.xml", _xml("Marktakteure", "Marktakteur", akteure))
        z.writestr("Netze.xml", _xml("Netze", "Netz", netze))
        z.writestr("Netzanschlusspunkte_1.xml", _xml("Netzanschlusspunkte", "Netzanschlusspunkt", nap))
        z.writestr("EinheitenSolar_1.xml", _xml("EinheitenSolar", "EinheitSolar", solar))


def test_schritt_liste(tmp_path, monkeypatch):
    zip_pfad = tmp_path / "export.zip"
    _export(zip_pfad)
    httpd = _server(zip_pfad.read_bytes(), abbruch_jede=4)
    monkeypatch.setattr(mastr_download, "_warten", lambda v: 0.01)
    monkeypatch.setattr(run, "HIER", tmp_path)
    (tmp_path / "pilot_50_vnb_2026.csv").write_text(
        (run.Path(__file__).parent.parent / "pilot_50_vnb_2026.csv").read_text(encoding="utf-8"), encoding="utf-8")
    from datetime import date
    monkeypatch.setenv("MASTR_EXPORT_URL", f"http://127.0.0.1:{httpd.server_address[1]}/"
                                           f"Gesamtdatenexport_{date.today():%Y%m%d}_26.2.zip")
    args = argparse.Namespace(out=str(tmp_path / "ergebnis"), csv=None, rolle_regex=None, ohne_gebiete=False)
    meldungen = []
    try:
        run.schritt_liste(args, meldungen.append)
    finally:
        httpd.shutdown()
    with open(tmp_path / "ergebnis" / "netzbetreiber.csv", encoding="utf-8") as f:
        zeilen = list(csv.DictReader(f, delimiter=";"))
    namen = {z["netzbetreiber"] for z in zeilen}
    assert "Stadtwerke 7 Netz GmbH & Co. KG" in namen                         # &amp; korrekt gelesen
    assert not namen & {"Gasnetz 1 GmbH", "TenneT TSO GmbH", "Alt Netz GmbH", "Industriepark Netz GmbH"}
    berlin = next(z for z in zeilen if z["netzbetreiber"] == "Stromnetz Berlin GmbH")
    assert berlin["pilot_nr"] == "1" and berlin["nr"] == "1" and berlin["mastr_nr"] == "SNB000000001"
    assert berlin["bundesland"] == "Bayern" and berlin["netztyp"] == "Stadtnetz"
    ohne = next(z for z in zeilen if z["netzbetreiber"] == "Ohne Web Netz GmbH")
    assert ohne["website"] == "https://www.ohneweb-netz.de"
    assert sum(1 for z in zeilen if z["mastr_nr"]) == 313                      # 3 + 310 Stromnetzbetreiber
    assert (tmp_path / "ergebnis" / "plz_netzbetreiber.csv").read_text().count("\n") > 300
    # zweiter Aufruf nutzt den vorhandenen Export (kein neuer Download)
    meldungen.clear()
    run.schritt_liste(args, meldungen.append)
    assert any("vorhandener MaStR-Export" in m for m in meldungen)
