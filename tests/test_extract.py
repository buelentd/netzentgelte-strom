from pathlib import Path

import pytest

from tests.fixtures import erzeugen
from vnb.bewerten import bewerten
from vnb.ergebnis import zahl
from vnb.extract import auswerten, ebene, name_im_text, plausibel


@pytest.fixture(scope="module")
def fx(tmp_path_factory) -> Path:
    return erzeugen(tmp_path_factory.mktemp("fx"))


def ns(e):
    return tuple(round(e.ns[k], 2) for k in ("lp_unter_2500", "ap_unter_2500", "lp_ueber_2500", "ap_ueber_2500"))


def msns(e):
    return tuple(round(e.msns[k], 2) for k in ("lp_unter_2500", "ap_unter_2500", "lp_ueber_2500", "ap_ueber_2500"))


def test_standard_ignoriert_monats_und_slp_tabellen(fx):
    e = auswerten(fx / "standard.pdf", "https://x.de/standard.pdf")
    assert ns(e) == (18.64, 7.49, 171.87, 1.36)
    assert msns(e) == (14.80, 5.90, 130.20, 1.05)
    assert e.preisstand == "endgültig" and e.stand_datum == "12.12.2025"
    assert not e.unklar
    assert e.slp == {"ap": 8.12, "gp": 60.0} and not e.slp_unklar


def test_spalten_vertauscht_ueber_kopfzeile(fx):
    e = auswerten(fx / "vertauscht.pdf")
    assert ns(e) == (32.37, 7.77, 187.82, 1.55)
    assert msns(e) == (20.00, 6.10, 150.10, 1.40)


def test_tagesleistungspreis_mal_365(fx):
    e = auswerten(fx / "tag.pdf")
    assert ns(e) == (20.50, 8.12, 102.70, 4.83)
    assert e.preisstand == "vorläufig"
    assert "Tagesleistungspreis × 365 umgerechnet" in e.hinweise


def test_getrennte_tabellen_und_umbrochenes_label(fx):
    e = auswerten(fx / "getrennt.pdf")
    assert ns(e) == (26.76, 8.28, 148.97, 3.39)
    assert msns(e) == (15.10, 6.00, 120.00, 2.10)


def test_zeilen_je_benutzungsdauer(fx):
    assert ns(auswerten(fx / "zeilen.pdf")) == (22.04, 6.68, 138.62, 2.01)


def test_xlsx_mit_tageswerten(fx):
    e = auswerten(fx / "excel.xlsx")
    assert ns(e) == (41.86, 6.36, 117.23, 3.35)
    assert e.preisstand == "endgültig"
    assert e.slp["ap"] == 7.71 and round(e.slp["gp"], 2) == 60.0     # Tagesgrundpreis × 365, ohne Wärmepumpe
    assert "Tagesgrundpreis × 365 umgerechnet" in e.slp_hinweise


@pytest.mark.parametrize("text,erwartet,unklar", [
    ("Entnahme ohne Leistungsmessung\nNetzebene   Grundpreis   Arbeitspreis\n            €/a          ct/kWh\n"
     "Niederspannung   54,00   7,95\nSteuerbare Verbrauchseinrichtungen § 14a\nModul 2       3,18\n", {"ap": 7.95, "gp": 54.0}, False),
    ("Standardlastprofilkunden\nArbeitspreis    8,41 ct/kWh\nGrundpreis   0,1644 €/Tag\n"
     "Speicherheizung\nArbeitspreis   3,10 ct/kWh\n", {"ap": 8.41, "gp": 60.006}, False),
    ("Entnahme ohne Leistungsmessung\nGrundpreis bis 10.000 kWh   30,00 €/a\nGrundpreis über 10.000 kWh   50,00 €/a\n"
     "Arbeitspreis   8,00 ct/kWh\n", {"ap": 8.0}, True),
    ("Entnahme ohne Leistungsmessung\nNiederspannung   Grundpreis 5,00   Arbeitspreis 7,10\n", {}, True),
])
def test_slp_varianten(text, erwartet, unklar):
    from vnb.extract import tabellen_lesen
    e = tabellen_lesen([text])
    assert e.slp == erwartet
    assert bool(e.slp_unklar) == unklar


def test_plausibel_slp():
    from vnb.extract import plausibel_slp
    assert plausibel_slp({"ap": 8.0, "gp": 60.0}) == []
    assert plausibel_slp({"ap": 18.0, "gp": 60.0}) and plausibel_slp({"ap": 8.0, "gp": 250.0})
    assert plausibel_slp({"ap": 8.0}) == ["SLP-Grundpreis fehlt"]


def test_ohne_kopf_wird_nicht_geraten(fx):
    e = auswerten(fx / "ohne_kopf.pdf")
    assert not e.ns_vollstaendig
    assert any("Spaltenreihenfolge" in u for u in e.unklar)


def test_bewerten_2027_nachrangig(fx):
    # nur ein Preisblatt 2027: wird verwendet (mit Hinweis), aber jedes Blatt 2026 geht vor
    k = bewerten(fx / "jahr2027.pdf", "https://x.de/a.pdf", "Musternetz GmbH")
    assert k.folgejahr and any("2027" in h for h in k.hinweise)
    k26 = bewerten(fx / "standard.pdf", "https://musternetz.de/p.pdf", "Musternetz GmbH")
    assert k26.rang() > k.rang()


def test_bewerten_ohne_name_pruefen(fx):
    k = bewerten(fx / "ohne_name.pdf", "https://a.storyblok.com/f/1/x/abc/p.pdf", "Andere Netz GmbH")
    assert k.verwendbar and "Netzbetreibername nicht im Dokument" in k.pruefen


def test_bewerten_ok(fx):
    k = bewerten(fx / "standard.pdf", "https://musternetz.de/p.pdf", "Musternetz GmbH")
    assert k.verwendbar and not k.pruefen


def test_bewerten_netzgebiet(fx):
    k = bewerten(fx / "standard.pdf", "https://musternetz.de/hb/p.pdf", "Musternetz Bremerhaven GmbH",
                 pflicht=("bremerhaven",))
    assert not k.verwendbar and "Netzgebiet" in k.grund


@pytest.mark.parametrize("label,erwartet", [
    ("Niederspannung", "NS"), ("NS", "NS"), ("7 Niederspannung", "NS"),
    ("Umspannung MS/NS", "MSNS"), ("Umspannung Mittel-/Niederspannung", "MSNS"),
    ("Umspannung MS / NS", "MSNS"), ("Mittelspannung", None), ("Umspannung HS/MS", None),
    ("Niederspannung steuerbare Verbrauchseinrichtung § 14a", None), ("Hochspannung", None),
])
def test_ebene(label, erwartet):
    assert ebene(label) == erwartet


def test_plausibel():
    assert plausibel({"lp_unter_2500": 18, "ap_unter_2500": 7, "lp_ueber_2500": 171, "ap_ueber_2500": 1.3}) == []
    assert plausibel({"lp_unter_2500": 18, "ap_unter_2500": 7, "lp_ueber_2500": 600, "ap_ueber_2500": 1.3})
    assert plausibel({"lp_unter_2500": 180, "ap_unter_2500": 1, "lp_ueber_2500": 171, "ap_ueber_2500": 1.3})


def test_name_im_text():
    assert name_im_text("Stadtwerke Bochum Netz GmbH", "STADTWERKE BOCHUM NETZ GMBH Preisblatt")
    assert name_im_text("Netze BW GmbH", "Netze BW GmbH, Stuttgart")
    assert not name_im_text("Netzgesellschaft Düsseldorf mbH", "Preisblatt Netzentgelte 2026")
    assert name_im_text("MVV Netze GmbH", "Netrion GmbH Preisblatt", aliase=["Netrion"])


def test_zahlformat():
    assert zahl(171.87) == "171,87" and zahl(0.28) == "0,28" and zahl(1.2345) == "1,2345" and zahl(None) == ""


@pytest.mark.parametrize("text,url,ok", [
    ("Netze BW GmbH\nPreisblatt Netzentgelte Strom 2026\n" + "x\n" * 40 + "Seit dem 01.01.2024 gilt ...", "", True),
    ("Preisblatt Netzentgelte Strom\ngültig ab 1. Januar 2026\n", "", True),
    ("Preisblatt Netzentgelte Strom\ngültig ab 01.01.2027\nVorjahr 2026 zum Vergleich", "", False),
    ("Preisblatt Aktuell\ngültig ab 01.01.2024\n" + "x\n" * 40 + "Ausblick 2026", "https://x.de/Aktuell.pdf", False),
    ("Preisblatt\nStand 2025\n" + "x\n" * 40 + "Werte 2026", "https://x.de/preisblatt_2026.pdf", True),
])
def test_jahr_pruefen(text, url, ok):
    from vnb.extract import jahr_pruefen, metadaten, tabellen_lesen
    e = tabellen_lesen([text])
    metadaten(e, url)
    assert (jahr_pruefen(e, 2026, url) is None) == ok
