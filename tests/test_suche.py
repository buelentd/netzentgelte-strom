"""Suchschritt: Abfrage, Filter der Treffer, Fortsetzen nach Abbruch (ohne echte Schnittstelle)."""
import csv

from vnb.crawl import hinweise_laden
from vnb.suche import abfrage, kernname, suchen


def test_kernname_und_abfrage():
    assert kernname("Stadtwerk am See GmbH ＆ Co. KG") == "Stadtwerk am See"
    assert kernname("Elektrizitätsgenossenschaft Unterneukirchen eG") == "Elektrizitätsgenossenschaft Unterneukirchen"
    assert abfrage("Stadtwerke Elmshorn", 2026) == "Stadtwerke Elmshorn netzentgelte strom 2026 pdf"


def test_suchen_filtert_und_setzt_fort(tmp_path):
    ziel, erledigt = tmp_path / "suche_treffer.csv", tmp_path / "suche_erledigt.csv"
    zeilen = [{"nr": "1", "netzbetreiber": "A Netz GmbH", "website": "www.a.de", "status": "kein_preisblatt"},
              {"nr": "2", "netzbetreiber": "B Netz GmbH", "website": "www.b.de", "status": "pruefen"},
              {"nr": "3", "netzbetreiber": "C Netz GmbH", "website": "www.c.de", "status": "blockiert"}]
    antworten = {
        "A Netz": {"web": {"results": [{"url": "https://www.a.de/preisblatt_netzentgelte_2026.pdf"},
                                       {"url": "https://www.a.de/grundversorgung_2026.pdf"},
                                       {"url": "https://www.a.de/gas_preisblatt_2026.pdf"},
                                       {"url": "https://www.a.de/seite.html"}]}},
        "B Netz": {},
    }

    def abrufen(schluessel, q):
        if "C Netz" in q:
            raise RuntimeError("HTTP 429 Kontingent erschöpft")
        return antworten[" ".join(q.split()[:2])]

    assert suchen(zeilen, "s", ziel, erledigt, abrufen=abrufen, log=lambda *a: None, pause=0) == 2
    zeilen_csv = list(csv.DictReader(erledigt.read_text(encoding="utf-8").splitlines(), delimiter=";"))
    assert [(z["nr"], z["anzahl_treffer"]) for z in zeilen_csv] == [("1", "1"), ("2", "0")]  # C nicht vermerkt
    assert hinweise_laden(ziel) == {"a.de": ("https://www.a.de/preisblatt_netzentgelte_2026.pdf",)}
    # zweiter Aufruf: alle werden erneut abgefragt (kein Überspringen, Kosten begrenzt max_abfragen)
    gefragt = []
    suchen(zeilen, "s", ziel, erledigt, abrufen=lambda s, q: gefragt.append(q) or {}, log=lambda *a: None, pause=0)
    assert len(gefragt) == 3


def test_nur_eigene_treffer():
    from vnb.suche import eigener_treffer
    assert eigener_treffer("https://www.redinet.de/files/pb_2026.pdf", "www.redinet.de", "REDINET Burgenland GmbH")
    assert not eigener_treffer("https://qeo-netz.de/Entgelte-2026-QEO.pdf", "www.redinet.de", "REDINET Burgenland GmbH")
    # fremde Domain, aber Name im Link (Veröffentlichungsplattform)
    assert eigener_treffer("https://www.enwg-veroeffentlichungen.de/bigge/Netzentgelte-2026.pdf", "www.bigge-energie.de",
                           "BIGGE ENERGIE GmbH ＆ Co. KG")
