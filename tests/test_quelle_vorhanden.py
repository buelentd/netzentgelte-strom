"""Hat ein Netzbetreiber einen recherchierten Link, darf der Status nicht „kein_preisblatt“ sein, sondern „pruefen“."""
from vnb.ergebnis import Speicher


def test_kein_preisblatt_mit_recherchiertem_link_wird_pruefen(tmp_path):
    (tmp_path / "ergebnis").mkdir()
    (tmp_path / "lauf").mkdir()
    (tmp_path / "lauf" / "quellen_recherche.csv").write_text(
        "nr;url;art;herkunft\n5;https://x.de/pb.pdf;Dokument;Test\n", encoding="utf-8")
    sp = Speicher(tmp_path / "ergebnis")
    sp.daten = {"k1": {"key": "k1", "nr": 5, "status": "kein_preisblatt", "netzbetreiber": "A"},
                "k2": {"key": "k2", "nr": 6, "status": "kein_preisblatt", "netzbetreiber": "B"}}
    z = {d["nr"]: d for d in sp.zeilen()}
    assert z[5]["status"] == "pruefen" and z[5]["quelle_url"] == "https://x.de/pb.pdf"
    assert "Recherche" in z[5]["hinweis"]
    assert z[6]["status"] == "kein_preisblatt"
    assert sp.daten["k1"]["status"] == "kein_preisblatt"     # Fortschritt bleibt unverändert
