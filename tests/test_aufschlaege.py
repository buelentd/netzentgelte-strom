from vnb import aufschlaege as au

T = ("Bei gewerblichen Sonderverträgen mit RLM kalkulieren Versorger den Vertriebsaufschlag mit 1,5 bis 3,5 ct/kWh netto auf den Beschaffungswert. "
     "Der Arbeitspreis liegt bei 28 ct/kWh. Ohne Lastspitze kommt ein Risikoaufschlag von bis zu 5 ct/kWh hinzu. Das Wetter ist 12 ct/kWh schön.")


def test_funde_mit_stichwort_und_gruppe():
    f = au.funde_aus_text(T, "https://www.beispiel.de/artikel", "Titel", "2026-05-01", "2026-11-14")
    spannen = {(x["wert_von_ct_kwh"], x["wert_bis_ct_kwh"]) for x in f}
    assert ("1,5", "3,5") in spannen and ("5", "5") in spannen
    v = [x for x in f if x["wert_von_ct_kwh"] == "1,5"][0]
    assert v["stichwort"].startswith("vertrieb") and v["kundengruppe"] == "RLM/Gewerbe" and v["netto_brutto"] == "netto"
    assert v["status"] == "ungeprüft"


def test_ohne_stichwort_kein_fund():
    f = au.funde_aus_text("Das Wetter ist 12 ct/kWh schön und die Zahl 99 ct/kWh ist auch nichts.", "https://x.de/a")
    assert f == []


def test_lauf_ohne_doppelte(tmp_path):
    from vnb import speicherpreise as sp
    html = "<html><body><p>" + T + "</p></body></html>"

    def fake(url):
        if url.endswith("/robots.txt"):
            return 404, "", ""
        return 200, "text/html", html
    ziel = tmp_path / "a.csv"
    r1 = au.lauf(ziel, "k", 2, 5, sp.Holer(pause=0, abrufen=fake, log=lambda *_: None), lambda q: ["https://a.de/x"], log=lambda *_: None)
    r2 = au.lauf(ziel, "k", 2, 5, sp.Holer(pause=0, abrufen=fake, log=lambda *_: None), lambda q: ["https://a.de/x"], log=lambda *_: None)
    assert r1["neu"] >= 2 and r2["neu"] == 0
