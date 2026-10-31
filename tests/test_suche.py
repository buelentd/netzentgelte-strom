"""Suchschritt: Abfrage, Filter der Treffer, Fortsetzen nach Abbruch (ohne echte Schnittstelle)."""
import csv

from vnb.crawl import hinweise_laden
from vnb.suche import abfrage, kernname, suchen


def test_kernname_und_abfrage():
    assert kernname("Stadtwerk am See GmbH ＆ Co. KG") == "Stadtwerk am See"
    assert kernname("Elektrizitätsgenossenschaft Unterneukirchen eG") == "Elektrizitätsgenossenschaft Unterneukirchen"
    assert abfrage("Stadtwerke Elmshorn", 2026) == '"Stadtwerke Elmshorn" Netzentgelte Strom 2026 Preisblatt filetype:pdf'


def test_suchen_filtert_und_setzt_fort(tmp_path):
    ziel = tmp_path / "suche_treffer.csv"
    zeilen = [{"nr": "1", "netzbetreiber": "A Netz GmbH", "website": "www.a.de", "status": "kein_preisblatt"},
              {"nr": "2", "netzbetreiber": "B Netz GmbH", "website": "www.b.de", "status": "pruefen"},
              {"nr": "3", "netzbetreiber": "C Netz GmbH", "website": "www.c.de", "status": "blockiert"}]
    antworten = {
        "A Netz": {"items": [{"link": "https://www.a.de/preisblatt_netzentgelte_2026.pdf"},
                             {"link": "https://www.a.de/grundversorgung_2026.pdf"},
                             {"link": "https://www.a.de/gas_preisblatt_2026.pdf"},
                             {"link": "https://www.a.de/seite.html"}]},
        "B Netz": {},
    }

    def abrufen(schluessel, kennung, q):
        if "C Netz" in q:
            raise RuntimeError("HTTP 429 Kontingent erschöpft")
        return antworten[q.split('"')[1]]

    assert suchen(zeilen, "s", "k", ziel, abrufen=abrufen, log=lambda *a: None) == 2
    zeilen_csv = list(csv.DictReader(ziel.read_text(encoding="utf-8").splitlines(), delimiter=";"))
    assert [z["nr"] for z in zeilen_csv] == ["1", "2"]          # C nicht vermerkt: nächster Lauf macht weiter
    assert hinweise_laden(ziel) == {"a.de": ("https://www.a.de/preisblatt_netzentgelte_2026.pdf",)}
    # zweiter Aufruf: A und B übersprungen, nur C wird abgefragt
    gefragt = []
    suchen(zeilen, "s", "k", ziel, abrufen=lambda s, k, q: gefragt.append(q) or {}, log=lambda *a: None)
    assert len(gefragt) == 1 and "C Netz" in gefragt[0]
