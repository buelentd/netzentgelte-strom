from vnb.produktseiten import produkt_aus_html, produktlinks

PIXII = '''<html><head><title>PIXII POWERSHAPER2 50 KW / 50 KWH, GEWERBESPEICHER</title>
<script type="application/ld+json">{"@type":"Product","offers":{"@type":"Offer","price":"31571.00","priceCurrency":"EUR"}}</script></head>
<body><h1>PIXII POWERSHAPER2 50 KW / 50 KWH</h1><p>0 % MwSt.</p><p>ZELLCHEMIE LFP 41,66 KWH NUTZBAR, 50 KW WR</p></body></html>'''


def test_pixii_preis_pro_kwh():
    p = produkt_aus_html(PIXII, "https://www.aceflex.de/produkt/x/")
    assert p["kapazitaet_kwh"] == "41,66" and p["eur_pro_kwh"] == "757,83"
    assert "0 % MwSt" in p["netto_brutto_hinweis"] and p["status"] == "ungeprüft"


def test_heimspeicher_wird_verworfen():
    h = '<title>Heimspeicher 10 kWh</title><script type="application/ld+json">{"offers":{"price":"4000"}}</script>'
    assert produkt_aus_html(h, "https://x.de/a") is None


def test_text_preis_ohne_json():
    h = "<title>Gewerbespeicher 215 kWh</title><body><p>Preis</p><p>41.999,00 €</p></body>"
    assert produkt_aus_html(h, "https://x.de/a")["eur_pro_kwh"] == "195,34"


def test_produktlinks():
    h = '<a href="/p/oasis-l215-215kwh">Oasis</a><a href="/impressum">I</a><a href="https://f.de/x-100kwh">x</a>'
    assert produktlinks(h, "https://s.de/k") == ["https://s.de/p/oasis-l215-215kwh"]
