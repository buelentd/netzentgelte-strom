from vnb import speicherprodukte as pr

ZEILEN = (
    "SCU\tBRES-2400-1250\tLFP\t2400\t1250\t93\t6000\t—\t29.72\t86.08\tBearbeiten✕\n"
    "SCU Sicon Chat Union\tGRES 225 kWh Hybrid\tLFP\t225\t150\t95\t4000\t332.4\t5.12\t8.71\tPDFBearbeiten✕\n"
    "Tesla\tMegapack 2 XL\tLFP\t3916\t979\t92\t6000\t280\t—\t—\tBearbeiten✕\n"
)


def test_zeilen_lesen():
    z = [pr.zeile_lesen(x) for x in ZEILEN.splitlines()]
    assert all(z)
    a, b, c = z
    assert a["preis_eur_kwh"] == "" and a["kapazitaet_kwh"] == "2400" and a["flaeche_m2"] == "29,72"
    assert b["hersteller"] == "SCU Sicon Chat Union" and b["preis_eur_kwh"] == "332,4" and "Datenblatt" in b["datenblatt_url"]
    assert c["leistung_kw"] == "979" and c["preis_eur_kwh"] == "280" and c["flaeche_m2"] == "" and c["datenblatt_url"] == ""
    assert b["status"] == "ungeprüft" and b["preis_netto_brutto"] == "unklar" and b["preis_umfang"] == "unklar"


def test_import_ohne_doppelte(tmp_path):
    p = tmp_path / "p.csv"
    r1 = pr.importieren(ZEILEN + "Kopfzeile ohne Daten\n", p)
    r2 = pr.importieren(ZEILEN, p)
    assert r1 == {"neu": 3, "uebersprungen": 1, "gesamt": 3} and r2["neu"] == 0 and r2["gesamt"] == 3
