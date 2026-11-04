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


def test_manuelle_preise_machen_ok(tmp_path):
    (tmp_path / "ergebnis").mkdir()
    (tmp_path / "lauf").mkdir()
    (tmp_path / "lauf" / "preise_manuell.csv").write_text(
        "nr;preisstand;stand_datum;ns_lp_unter_2500h;ns_ap_unter_2500h;ns_lp_ab_2500h;ns_ap_ab_2500h;slp_ap;slp_gp;quelle_url\n"
        "5;endgültig;01.01.2026;21,5;6,1;118,4;2,35;7,3;45;https://x.de\n"
        "6;endgültig;01.01.2026;21,5;6,1;118,4;2,35;70;45;https://x.de\n", encoding="utf-8")
    sp = Speicher(tmp_path / "ergebnis")
    sp.daten = {"k1": {"key": "k1", "nr": 5, "status": "kein_preisblatt", "netzbetreiber": "A"},
                "k2": {"key": "k2", "nr": 6, "status": "robots", "netzbetreiber": "B"}}
    z = {d["nr"]: d for d in sp.zeilen()}
    assert z[5]["status"] == "ok" and z[5]["ns"]["lp_ueber_2500"] == 118.4 and z[5]["slp"]["gp"] == 45.0
    assert z[6]["status"] == "pruefen" and "SLP-Arbeitspreis" in z[6]["hinweis"]
