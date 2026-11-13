import pandas as pd

from run import geschwister
from vnb import pilot as pilot_mod
from vnb.liste import filtern, website_bestimmen


def test_filtern(tmp_path):
    akteure = pd.DataFrame([
        {"MastrNummer": "A1", "Firmenname": "Stadtwerke Musterstadt Netz GmbH", "Webseite": "www.swm-netz.de",
         "Marktfunktion": "Stromnetzbetreiber", "Email": "", "Taetigkeitsende": None},
        {"MastrNummer": "A2", "Firmenname": "Gasnetz Muster GmbH", "Webseite": "gas.de",
         "Marktfunktion": "Gasnetzbetreiber", "Email": "", "Taetigkeitsende": None},
        {"MastrNummer": "A3", "Firmenname": "TenneT TSO GmbH", "Webseite": "tennet.eu",
         "Marktfunktion": "Stromnetzbetreiber", "Email": "", "Taetigkeitsende": None},
        {"MastrNummer": "A4", "Firmenname": "Alt Netz GmbH", "Webseite": "alt.de",
         "Marktfunktion": "Stromnetzbetreiber", "Email": "", "Taetigkeitsende": "2019-12-31"},
        {"MastrNummer": "A5", "Firmenname": "Dorfnetz eG", "Webseite": None,
         "Marktfunktion": "Stromnetzbetreiber", "Email": "netz@dorfnetz-eg.de", "Taetigkeitsende": None},
    ])
    rollen = pd.DataFrame([
        {"MarktakteurMastrNummer": "A1", "Marktrolle": "Netzbetreiber", "Marktpartneridentifikationsnummer": "990"},
        {"MarktakteurMastrNummer": "A2", "Marktrolle": "Netzbetreiber Gas", "Marktpartneridentifikationsnummer": ""},
        {"MarktakteurMastrNummer": "A3", "Marktrolle": "Übertragungsnetzbetreiber", "Marktpartneridentifikationsnummer": ""},
        {"MarktakteurMastrNummer": "A4", "Marktrolle": "Netzbetreiber", "Marktpartneridentifikationsnummer": ""},
        {"MarktakteurMastrNummer": "A5", "Marktrolle": "Netzbetreiber", "Marktpartneridentifikationsnummer": ""},
    ])
    out = filtern(akteure, rollen, tmp_path / "netzbetreiber.csv")
    assert [e["mastr_nr"] for e in out] == ["A1", "A5"]
    assert out[1]["website"] == "https://www.dorfnetz-eg.de"
    assert (tmp_path / "mastr_rollen.txt").exists()


def test_website_freemail():
    assert website_bestimmen("", "", "x@gmail.com") == ("", "")


def test_pilot_zuordnung():
    liste = [{"netzbetreiber": "wesernetz Bremerhaven GmbH", "mastr_nr": "1", "website": "wesernetz.de"},
             {"netzbetreiber": "wesernetz Bremen GmbH", "mastr_nr": "2", "website": "wesernetz.de"},
             {"netzbetreiber": "SachsenNetze HS.HD GmbH", "mastr_nr": "3", "website": "sachsen-netze.de"},
             {"netzbetreiber": "SachsenNetze GmbH", "mastr_nr": "4", "website": "sachsen-netze.de"},
             {"netzbetreiber": "Dortmunder Netz GmbH", "mastr_nr": "5", "website": "do-netz.de"}]
    def p(name, quelle="https://x.de/a.pdf"):
        return {"netzbetreiber": name, "quelle": quelle}
    assert pilot_mod.zuordnen(p("wesernetz (Bremen)"), liste)["mastr_nr"] == "2"
    assert pilot_mod.zuordnen(p("SachsenNetze (Dresden)"), liste)["mastr_nr"] == "4"
    assert pilot_mod.zuordnen(p("DONETZ (Dortmund)"), liste)["mastr_nr"] == "5"
    assert pilot_mod.zuordnen(p("Unbekannt Netz"), liste) is None


def test_geschwister():
    eintraege = [{"nr": 1, "netzbetreiber": "wesernetz Bremen GmbH", "website": "https://www.wesernetz.de"},
                 {"nr": 2, "netzbetreiber": "wesernetz Bremerhaven GmbH", "website": "https://www.wesernetz.de"},
                 {"nr": 3, "netzbetreiber": "Einzel Netz GmbH", "website": "https://einzel.de"}]
    g = geschwister(eintraege)
    assert "3" not in g
    pflicht, ausschluss, unklar = g["2"]
    assert "bremerhaven" in pflicht and not unklar
    assert "bremerhaven" in g["1"][1]


def test_netztyp_und_plz():
    from vnb.gebiete import Sammler
    from vnb.liste import gebiet_ergaenzen
    s = Sammler()
    for i in range(200):                                    # Stadtnetz: eine Gemeinde
        s.add("STADT", "Bayern", "Augsburg", "Augsburg", "09761000", "86150")
    for i in range(300):                                    # Flächennetz: 60 Gemeinden, 6 Landkreise
        s.add("FLAECHE", "Niedersachsen" if i % 10 else "Bremen", f"LK{i % 6}", f"G{i % 60}", f"03{i % 60:06d}",
              f"{26000 + i % 60}")
    for i in range(100):                                    # Regionalnetz: 10 Gemeinden, 1 Landkreis
        s.add("REGION", "Hessen", "Landkreis Fulda", f"Ort{i % 10}", f"06631{i % 10:03d}", "36037")
    s.add("REGION", "Hessen", "Landkreis Fulda", "Ort1", "06631001", "86150")   # Streuwert in fremder PLZ
    assert s.gebiet("STADT") == {"bundesland": "Bayern", "region": "Augsburg", "netztyp": "Stadtnetz",
                                 "gebiet_einheiten": 200, "gebiet_gemeinden": 1}
    assert s.gebiet("REGION")["netztyp"] == "Regionalnetz" and s.gebiet("REGION")["region"] == "Landkreis Fulda"
    g = s.gebiet("FLAECHE")
    assert g["netztyp"] == "Flächennetz" and g["bundesland"] == "Niedersachsen / Bremen"
    assert s.gebiet("UNBEKANNT") == {}
    plz = list(s.plz_zeilen({"STADT": "Stadtwerke", "REGION": "Regionalnetz"}))
    assert [z["mastr_nr"] for z in plz if z["plz"] == "86150"] == ["STADT"]   # 1 von 201 < 2 % → weggelassen

    e = [{"mastr_nr": "STADT"}, {"mastr_nr": "X", "sitz_bundesland": "Sachsen", "ort": "Dresden"}]
    gebiet_ergaenzen(e, s, {})
    assert e[0]["netztyp"] == "Stadtnetz" and e[0]["gebiet_quelle"] == "Netzgebiet (MaStR-Einheiten)"
    assert e[1]["bundesland"] == "Sachsen" and e[1]["gebiet_quelle"] == "Sitz laut MaStR"


def test_pilot_semikolon_im_hinweis(tmp_path):
    from vnb.pilot import lesen
    p = tmp_path / "pilot.csv"
    p.write_text("nr;netzbetreiber;status;ns_lp_unter_2500;ns_ap_unter_2500;ns_lp_ueber_2500;ns_ap_ueber_2500;"
                 "preisstand;hinweis;quelle\n"
                 "25;Hamburger Energienetze;ok;32,91;7,04;53,56;6,22;endgültig;Stand 12.12.2025; frühere Zuordnung "
                 "falsch;https://filehub.example/v5/deliverFile/abc?download=true\n", encoding="utf-8")
    z = lesen(p)[0]
    assert z["quelle"] == "https://filehub.example/v5/deliverFile/abc?download=true"
    assert z["hinweis"] == "Stand 12.12.2025; frühere Zuordnung falsch"
    assert z["ns_lp_ueber_2500"] == 53.56


def test_parallele_teile_decken_alles_genau_einmal_ab():
    from run import im_teil
    eintraege = [{"nr": i, "website": f"www.beispiel{i % 40}.de"} for i in range(500)]
    for e in eintraege:
        assert sum(im_teil(e, f"{k}/8") for k in range(8)) == 1
    # gleiche Website, gleicher Teil
    teile = {}
    for e in eintraege:
        t = next(k for k in range(8) if im_teil(e, f"{k}/8"))
        assert teile.setdefault(e["website"], t) == t
    assert all(im_teil(e, "") for e in eintraege)


def test_veraltete_adressen_werden_nicht_geladen():
    from vnb.crawl import veraltet_in_url
    assert veraltet_in_url("https://max-peissker.de/wp-content/uploads/2023/12/NNE-ab-01.01.2024.pdf", 2027)
    assert veraltet_in_url("https://x.de/uploads/2025/12/Preisblatt.pdf", 2027)
    assert not veraltet_in_url("https://x.de/uploads/2025/10/NNE_vorlaeufig_2027.pdf", 2027)
    assert not veraltet_in_url("https://x.de/uploads/2025/12/Preisblatt-2026.pdf", 2027)
    assert not veraltet_in_url("https://x.de/downloads/preisblatt.pdf", 2027)


def test_sitemap_index_wird_aufgeloest():
    import asyncio
    from vnb.crawl import Crawler

    class Antwort:
        def __init__(self, status, text): self.status, self._t = status, text
        async def body(self): return self._t.encode()

    seiten = {
        "https://x.de/sitemap_index.xml": "<sitemapindex><sitemap><loc>https://x.de/page-sitemap.xml</loc></sitemap><sitemap><loc>https://x.de/image-sitemap.xml</loc></sitemap></sitemapindex>",
        "https://x.de/page-sitemap.xml": "<urlset><url><loc>https://x.de/netzentgelte-strom/</loc></url><url><loc>https://x.de/kontakt/</loc></url></urlset>",
        "https://x.de/image-sitemap.xml": "<urlset><url><loc>https://x.de/bild.jpg</loc></url></urlset>",
    }

    class Req:
        async def get(self, url, timeout=0): return Antwort(200 if url in seiten else 404, seiten.get(url, ""))

    class Robots:
        async def erlaubt(self, u): return True

    class Drossel:
        async def warten(self, u): return None

    c = object.__new__(Crawler)
    c.robots, c.drossel = Robots(), Drossel()
    urls = asyncio.run(c._sitemap(Req(), "https://x.de/sitemap_index.xml"))
    assert "https://x.de/netzentgelte-strom/" in urls and "https://x.de/kontakt/" in urls and "https://x.de/bild.jpg" in urls
