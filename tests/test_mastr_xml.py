"""MaStR-Export direkt aus dem ZIP lesen: nachgebauter Export im Originalformat (UTF-16, Katalog-IDs,
Listenfelder wie "712 812", mehrere Teildateien)."""
import zipfile
from datetime import date

from vnb import mastr_xml
from vnb.liste import filtern, gebiet_ergaenzen


def _xml(wurzel, satz, zeilen):
    teile = [f'<?xml version="1.0" encoding="utf-16"?>\n<{wurzel}>']
    for z in zeilen:
        teile.append(f"<{satz}>" + "".join(f"<{k}>{v}</{k}>" for k, v in z.items()) + f"</{satz}>")
    teile.append(f"</{wurzel}>")
    return "".join(teile).encode("utf-16")


def export(ordner):
    ordner.mkdir(parents=True, exist_ok=True)
    pfad = ordner / f"Gesamtdatenexport_{date.today():%Y%m%d}.zip"
    with zipfile.ZipFile(pfad, "w") as z:
        z.writestr("Katalogwerte.xml", _xml("Katalogwerte", "Katalogwert", [
            {"Id": "1", "Wert": "Anschlussnetzbetreiber"}, {"Id": "2", "Wert": "Anlagenbetreiber"},
            {"Id": "3", "Wert": "andere Gase"}, {"Id": "8", "Wert": "Kernenergie"},
            {"Id": "1400", "Wert": "Bayern"}, {"Id": "1401", "Wert": "Baden-Württemberg"},
            {"Id": "50", "Wert": "Strom"}, {"Id": "712", "Wert": "Haushalt"}, {"Id": "812", "Wert": "Gewerbe"}]))
        z.writestr("MarktakteureUndRollen.xml", _xml("MarktakteureUndRollen", "MarktakteurUndRolle", [
            {"MarktakteurMastrNummer": "SNB1", "Marktrolle": "1", "Marktpartneridentifikationsnummer": "9900001"},
            {"MarktakteurMastrNummer": "SNB2", "Marktrolle": "1"},
            {"MarktakteurMastrNummer": "SNB3", "Marktrolle": "1"},
            {"MarktakteurMastrNummer": "ABR1", "Marktrolle": "2"}]))
        z.writestr("Marktakteure_1.xml", _xml("Marktakteure", "Marktakteur", [
            {"MastrNummer": "ABR1", "Firmenname": "Privat", "Marktfunktion": "2"}]))
        z.writestr("Marktakteure_2.xml", _xml("Marktakteure", "Marktakteur", [
            {"MastrNummer": "SNB1", "Firmenname": "Stadtwerke Musterstadt Netz GmbH", "Webseite": "www.swm-netz.de",
             "Marktfunktion": "1", "Bundesland": "1400", "Ort": "Musterstadt", "Unbekannt": "x"},
            {"MastrNummer": "SNB2", "Firmenname": "Geschlossen Netz GmbH", "Webseite": "gn.de", "Marktfunktion": "1"},
            {"MastrNummer": "SNB3", "Firmenname": "Gasnetz GmbH", "Webseite": "gas.de", "Marktfunktion": "8"}]))
        z.writestr("Netze.xml", _xml("Netze", "Netz", [
            {"MastrNummer": "N1", "Bundesland": "1400 1401", "Sparte": "50", "GeschlossenesVerteilnetz": "0"},
            {"MastrNummer": "N2", "Bundesland": "1401", "Sparte": "50", "GeschlossenesVerteilnetz": "1"}]))
        z.writestr("Netzanschlusspunkte_1.xml", _xml("Netzanschlusspunkte", "Netzanschlusspunkt", [
            {"LokationMaStRNummer": f"L{i}", "NetzbetreiberMaStRNummer": "SNB1", "NetzMaStRNummer": "N1"}
            for i in range(30)] + [
            {"LokationMaStRNummer": "LX", "NetzbetreiberMaStRNummer": "SNB2", "NetzMaStRNummer": "N2"}]))
        for teil in (1, 2):
            z.writestr(f"EinheitenSolar_{teil}.xml", _xml("EinheitenSolar", "EinheitSolar", [
                {"LokationMaStRNummer": f"L{i}", "Bundesland": "1400", "Landkreis": "Musterkreis",
                 "Gemeinde": "Musterstadt", "Gemeindeschluessel": "09999000", "Postleitzahl": "86150",
                 "Nutzungsbereich": "712 812"} for i in range(teil * 15 - 15, teil * 15)]))
    return pfad


def test_export_lesen_und_filtern(tmp_path):
    pfad = export(tmp_path / "xml")
    assert mastr_xml.herunterladen(tmp_path / "xml", log=lambda *a: None) == pfad   # vorhandener Export
    akteure, rollen, sammler, netzinfo, zaehler = mastr_xml.lesen(pfad, log=lambda *a: None)
    assert set(akteure["MastrNummer"]) == {"SNB1", "SNB2", "SNB3"}                  # nur Netzbetreiber
    assert set(akteure["Marktfunktion"]) == {"Stromnetzbetreiber", "Gasnetzbetreiber"}  # Systemcodes
    assert zaehler["Anlagenbetreiber"] == 1
    assert netzinfo["SNB2"]["geschlossen"] and not netzinfo["SNB1"]["geschlossen"]
    assert netzinfo["SNB1"]["laender"] == {"Bayern", "Baden-Württemberg"}
    out = filtern(akteure, rollen, tmp_path / "netzbetreiber.csv", "", zaehler)
    assert {e["mastr_nr"] for e in out} == {"SNB1", "SNB2"}                         # ohne Gasnetz
    e = next(e for e in out if e["mastr_nr"] == "SNB1")
    assert e["sitz_bundesland"] == "Bayern" and e["marktpartner_id"] == "9900001"
    gebiet_ergaenzen(out, sammler, netzinfo)
    assert e["netztyp"] == "Stadtnetz" and e["bundesland"] == "Bayern" and e["region"] == "Musterstadt"
    assert list(sammler.plz_zeilen({"SNB1": "SW"}))[0]["einheiten"] == 30
