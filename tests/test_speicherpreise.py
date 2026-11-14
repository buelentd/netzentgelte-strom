from vnb import speicherpreise as sp

HTML = """<html><head><title>Gewerbespeicher Preise 2026</title>
<meta property="article:published_time" content="2026-04-02T08:00:00+02:00"></head><body>
<h1>Was kostet ein Stromspeicher mit 100 kWh?</h1>
<p>Systeme ab 100 kWh kosten schlüsselfertig derzeit etwa 410–450 € pro kWh netto. Das Angebot gilt zzgl. MwSt.</p>
<p>Der Strompreis liegt bei 0,28 €/kWh und ist kein Speicherpreis.</p>
<p>Heimspeicher für das Einfamilienhaus: 900 €/kWh brutto.</p>
<script>var x = "999 €/kWh";</script>
</body></html>"""


def test_text_titel_datum():
    text, titel, datum = sp.seitentext(HTML)
    assert titel == "Gewerbespeicher Preise 2026" and datum == "2026-04-02"
    assert "999" not in text                       # Skript zählt nicht


def test_funde_spanne_netto_umfang():
    text, titel, datum = sp.seitentext(HTML)
    f = sp.funde_aus_text(text, "https://www.beispiel-anbieter.de/ratgeber", titel, datum, "2026-11-14")
    gew = [x for x in f if x["preis_von_eur_kwh"] == "410"]
    assert len(gew) == 1
    g = gew[0]
    assert g["preis_bis_eur_kwh"] == "450" and g["netto_brutto"] == "netto" and g["umfang"] == "schlüsselfertig"
    assert g["veroeffentlicht"] == "2026-04-02" and g["status"] == "ungeprüft" and g["domain"] == "beispiel-anbieter.de"
    assert "410" in g["kontext"]


def test_strompreis_und_heimspeicher():
    text, *_ = sp.seitentext(HTML)
    f = sp.funde_aus_text(text, "https://x.de/", "", "", "2026-11-14")
    assert not [x for x in f if x["preis_von_eur_kwh"].startswith("0")]      # 0,28 €/kWh ist ein Strompreis
    heim = [x for x in f if x["preis_von_eur_kwh"] == "900"]
    assert heim and heim[0]["segment"] == "Heim" and heim[0]["netto_brutto"] == "brutto"


def test_kapazitaet_und_mwh():
    f = sp.funde_aus_text("Das 1,5 MWh Containersystem kostet 320 €/kWh netto ohne Montage.", "https://x.de/a", "", "", "2026-11-14")
    assert f[0]["kapazitaet_kwh"] == "1500" and f[0]["umfang"] == "nur Hardware"


def test_art_der_quelle():
    assert sp.art_der_quelle("pv-magazine.de", "") == "Fachmagazin"
    assert sp.art_der_quelle("ise.fraunhofer.de", "") == "Studie/Verband"
    assert sp.art_der_quelle("shop.de", "in den Warenkorb legen") == "Händler/Anbieter"


def test_holer_robots_limit_und_nicht_html():
    aufrufe = []

    def fake(url):
        aufrufe.append(url)
        if url.endswith("/robots.txt"):
            return 200, "text/plain", "User-agent: *\nDisallow: /privat/\n"
        return 200, "text/html", "<html></html>"
    h = sp.Holer(pause=0, max_seiten=2, abrufen=fake, log=lambda *_: None)
    assert h.holen("https://a.de/privat/x") is None            # robots.txt sperrt
    assert h.holen("https://a.de/ok1") is not None and h.holen("https://a.de/ok2") is not None
    assert h.holen("https://a.de/ok3") is None                  # Seitenlimit je Domain
    assert h.holen("https://a.de/datei.pdf") is None
    assert not [u for u in aufrufe if "privat/x" in u]


def test_lauf_speichert_ohne_doppelte(tmp_path):
    seiten = {"https://a.de/1": HTML}

    def fake(url):
        if url.endswith("/robots.txt"):
            return 404, "", ""
        return (200, "text/html", seiten[url]) if url in seiten else (404, "", "")
    h = sp.Holer(pause=0, abrufen=fake, log=lambda *_: None)
    ziel = tmp_path / "funde.csv"
    old = sp.STARTSEITEN
    sp.STARTSEITEN = ["https://a.de/1"]
    try:
        r1 = sp.lauf(ziel, "", 0, 10, h, lambda q: [], log=lambda *_: None)
        r2 = sp.lauf(ziel, "", 0, 10, sp.Holer(pause=0, abrufen=fake, log=lambda *_: None), lambda q: [], log=lambda *_: None)
    finally:
        sp.STARTSEITEN = old
    assert r1["neu"] >= 2 and r2["neu"] == 0 and r2["gesamt"] == r1["gesamt"]


def test_auswertung_nur_geprueft():
    funde = {"1": {"status": "ungeprüft", "preis_von_eur_kwh": "100", "preis_bis_eur_kwh": "100", "umfang": "u", "netto_brutto": "n", "segment": "G"},
             "2": {"status": "geprüft", "preis_von_eur_kwh": "400", "preis_bis_eur_kwh": "450", "umfang": "u", "netto_brutto": "n", "segment": "G"}}
    a = sp.auswertung(funde)
    assert len(a) == 1 and a[0]["anzahl"] == 1 and a[0]["median"] == 425


def test_auszuege(tmp_path):
    seiten = {"https://a.de/1": HTML}

    def fake(url):
        if url.endswith("/robots.txt"):
            return 404, "", ""
        return (200, "text/html", seiten[url]) if url in seiten else (404, "", "")
    h = sp.Holer(pause=0, abrufen=fake, log=lambda *_: None)
    funde = tmp_path / "funde.csv"
    old = sp.STARTSEITEN
    sp.STARTSEITEN = ["https://a.de/1"]
    try:
        sp.lauf(funde, "", 0, 10, h, lambda q: [], log=lambda *_: None)
    finally:
        sp.STARTSEITEN = old
    ziel = tmp_path / "auszuege.csv"
    r = sp.auszuege(funde, ziel, sp.Holer(pause=0, abrufen=fake, log=lambda *_: None), fenster=200, log=lambda *_: None)
    assert r["neu"] >= 2
    zeilen = sp.bestehende_laden(ziel)
    assert any("410" in z["auszug"] and "netto" in z["auszug"] for z in zeilen.values())
    r2 = sp.auszuege(funde, ziel, sp.Holer(pause=0, abrufen=fake, log=lambda *_: None), fenster=200, log=lambda *_: None)
    assert r2["neu"] == 0


def test_umfang_hardware_vor_komplettsystem():
    t = "Komplettsysteme mit Wechselrichter 173 bis 434 €/kWh netto. Nur Hardware, ohne Montage."
    f = sp.funde_aus_text(t, "https://x.de/a", "", "", "2026-11-14")
    assert f[0]["umfang"] == "nur Hardware"
    g = sp.funde_aus_text("Preise netto inklusive Montage und Inbetriebnahme: 525 bis 750 € je kWh.", "https://x.de/b", "", "", "2026-11-14")
    assert g[0]["umfang"] == "schlüsselfertig"
    h = sp.funde_aus_text("Hardware ab 450 €/kWh, schlüsselfertig mit Installation mehr.", "https://x.de/c", "", "", "2026-11-14")
    assert h[0]["umfang"] == "unklar"
