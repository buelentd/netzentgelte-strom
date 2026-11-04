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
        "nr;preisstand;stand_datum;ms_lp_unter_2500h_eur_kw_jahr;ms_ap_unter_2500h_ct_kwh;ms_lp_ab_2500h_eur_kw_jahr;ms_ap_ab_2500h_ct_kwh;"
        "msns_lp_unter_2500h_eur_kw_jahr;msns_ap_unter_2500h_ct_kwh;msns_lp_ab_2500h_eur_kw_jahr;msns_ap_ab_2500h_ct_kwh;"
        "ns_lp_unter_2500h_eur_kw_jahr;ns_ap_unter_2500h_ct_kwh;ns_lp_ab_2500h_eur_kw_jahr;ns_ap_ab_2500h_ct_kwh;slp_ap;slp_gp;quelle_url;geprueft\n"
        "5;endgültig;01.01.2026;12;4,5;150;0,9;15;5,2;130;1,4;21,5;6,1;118,4;2,35;7,3;45;https://x.de;ja\n"
        "6;endgültig;01.01.2026;12;4,5;150;0,9;15;5,2;130;1,4;21,5;6,1;118,4;2,35;70;45;https://x.de;ja\n", encoding="utf-8")
    sp = Speicher(tmp_path / "ergebnis")
    sp.daten = {"k1": {"key": "k1", "nr": 5, "status": "kein_preisblatt", "netzbetreiber": "A"},
                "k2": {"key": "k2", "nr": 6, "status": "robots", "netzbetreiber": "B"}}
    z = {d["nr"]: d for d in sp.zeilen()}
    assert z[5]["status"] == "ok" and z[5]["ns"]["lp_ueber_2500"] == 118.4 and z[5]["slp"]["gp"] == 45.0 and z[5]["ms"]["lp_ueber_2500"] == 150.0
    assert z[6]["status"] == "pruefen" and "SLP" in z[6]["hinweis"]


def test_status_v2_verlangt_alle_ebenen(tmp_path):
    (tmp_path / "ergebnis").mkdir()
    sp = Speicher(tmp_path / "ergebnis")
    w = {"lp_unter_2500": 10, "ap_unter_2500": 6, "lp_ueber_2500": 100, "ap_ueber_2500": 2}
    voll = {"key": "a", "nr": 1, "status": "ok", "v2": True, "ns": w, "msns": w, "ms": w, "slp": {"ap": 7, "gp": 50}}
    ohne_ms = {"key": "b", "nr": 2, "status": "ok", "v2": True, "ns": w, "msns": w, "ms": {}, "slp": {"ap": 7, "gp": 50}}
    gross = dict(voll, key="c", nr=3, hs_erwaehnt=True)
    sp.daten = {d["key"]: d for d in (voll, ohne_ms, gross)}
    z = {d["nr"]: d for d in sp.zeilen()}
    assert z[1]["status"] == "ok" and z[1]["hsms_status"] == "nicht ausgewiesen"
    assert z[2]["status"] == "pruefen" and "Mittelspannung" in z[2]["hinweis"]
    assert z[3]["status"] == "pruefen" and z[3]["hsms_status"] == "fehlt"


def test_sperrliste_leert_werte():
    """Nummern in lauf/zuordnung_unbelegt.csv geben keine Werte aus und stehen auf 'pruefen'."""
    from vnb.ergebnis import Speicher as Ergebnisse
    d = {"nr": "186", "status": "ok", "ns": {"x": 1}, "ms": {}, "msns": {}, "hsms": {}, "slp": {"ap": 1, "gp": 2}}
    out = Ergebnisse._gesperrt(d, {"186": "grund"})
    assert out["status"] == "pruefen" and out["ns"] == {} and out["slp"] == {} and out["hinweis"] == "grund"
    assert Ergebnisse._gesperrt(d, {})["status"] == "ok"
