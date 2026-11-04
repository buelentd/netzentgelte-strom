from datetime import datetime, timedelta, timezone

import pytest

from vnb.rechner import (TZ, RueckfrageNoetig, Tarif, berechnen, berechnen_aus_profil, ct_kwh_bei, gruppe,
                         kappung, kennzahlen, lastprofil_lesen)

NS = {"lp_unter_2500": 20.0, "ap_unter_2500": 7.0, "lp_ueber_2500": 150.0, "ap_ueber_2500": 1.5}
MSNS = {"lp_unter_2500": 15.0, "ap_unter_2500": 6.0, "lp_ueber_2500": 120.0, "ap_ueber_2500": 1.2}
T = Tarif(netzbetreiber="Musternetz", ns=NS, msns=MSNS, slp_ap=8.0, slp_gp=60.0, preisstand="endgültig",
          quelle_url="https://x.de/p.pdf")


# ---------------------------------------------------------------- manuelle Eingabe

def test_slp():
    r = berechnen(T, 20_000)
    assert r["tarif"].startswith("SLP")
    assert r["netzentgelt_eur"] == pytest.approx(60 + 1600)
    assert r["ct_kwh"] == pytest.approx(1660 / 20_000 * 100)


def test_slp_mit_leistungsmessung_ist_rlm():
    assert berechnen(T, 50_000, 40, leistungsmessung=True)["tarif"].startswith("RLM")


def test_rlm_unter_2500_mit_tarifwechsel():
    r = berechnen(T, 200_000, 100)
    assert r["benutzungsstunden"] == pytest.approx(2000)
    assert r["netzentgelt_eur"] == pytest.approx(20 * 100 + 7 * 200_000 / 100)
    assert r["leistungsanteil_eur"] == pytest.approx(2000) and r["arbeitsanteil_eur"] == pytest.approx(14000)
    assert r["ersparnis_je_kw_eur"] == 20
    tw = r["tarifwechsel"]
    assert tw["kappung_kw"] == pytest.approx(20)
    assert tw["netzentgelt_danach_eur"] == pytest.approx(150 * 80 + 1.5 * 2000)
    assert tw["ersparnis_eur"] == pytest.approx(16000 - 15000)


def test_rlm_branchenannahme():
    r = berechnen(T, 600_000, branche="supermarkt")
    assert r["benutzungsstunden"] == pytest.approx(6000)
    assert r["kw"] == pytest.approx(100)
    assert any("Branchen-Standardwert" in a for a in r["annahmen"])
    assert r["tarifwechsel"] is None


def test_rlm_ohne_kw_und_branche():
    with pytest.raises(ValueError):
        berechnen(T, 600_000)


def test_msns():
    r = berechnen(T, 600_000, 100, ebene="MS/NS")
    assert r["netzentgelt_eur"] == pytest.approx(120 * 100 + 1.2 * 6000)


def test_grenzfall_genau_2500():
    assert gruppe(2500) == "ueber" and gruppe(2499.9) == "unter"
    assert gruppe(2500, grenze_le=True) == "unter" and gruppe(2500.1, grenze_le=True) == "ueber"
    r = berechnen(T, 250_000, 100)
    assert "ab 2.500" in r["tarif"]
    t_le = Tarif(**{**T.__dict__, "grenze_le": True})
    r = berechnen(t_le, 250_000, 100)
    assert "bis 2.500" in r["tarif"]
    assert any("Grenze" in h for h in r["hinweise"])


def test_ct_kwh_bei():
    assert ct_kwh_bei(NS, 1500) == pytest.approx(7 + 20 * 100 / 1500)
    assert ct_kwh_bei(NS, 2500) == pytest.approx(1.5 + 150 * 100 / 2500)
    assert ct_kwh_bei(NS, 4000) == pytest.approx(1.5 + 150 * 100 / 4000)
    assert ct_kwh_bei({}, 4000) is None


def test_kappung_mit_tarifwechsel():
    k = kappung(T, 200_000, 100, 25)
    assert "Tarifwechsel" in k["hinweis"]
    assert k["ersparnis_eur"] == pytest.approx(16000 - (150 * 75 + 1.5 * 2000))


def test_tarif_aus_zeile():
    z = {"netzbetreiber": "X", "ns_lp_unter_2500h_eur_kw_jahr": "20,00", "ns_ap_unter_2500h_ct_kwh": "7,00",
         "ns_lp_ab_2500h_eur_kw_jahr": "150,00", "ns_ap_ab_2500h_ct_kwh": "1,50",
         "slp_ap_ct_kwh": "8,00", "slp_grundpreis_eur_jahr": "60,00", "hinweis": "Grenze ≤ 2.500 / > 2.500 h"}
    t = Tarif.aus_zeile(z)
    assert t.ns == NS and t.slp_gp == 60 and t.grenze_le and t.msns == {}


# ---------------------------------------------------------------- Lastprofil

def _profil(tage=365, min_=15, start=datetime(2025, 1, 1, tzinfo=TZ), wert_kw=10.0, spitze=None,
            einheit="kW", kopf="Leistung [kW]", fmt="%d.%m.%Y %H:%M", dez=","):
    """Lokale Zeitstempel wie in echten Exporten: Oktober doppelte Stunde, März fehlende Stunde."""
    t = start.astimezone(timezone.utc)
    ende = t + timedelta(days=tage)
    zeilen = [f"Zeitstempel;{kopf}"]
    while t < ende:
        lokal = t.astimezone(TZ)
        kw = spitze[1] if spitze and lokal.replace(tzinfo=None) == spitze[0] else wert_kw
        v = kw * min_ / 60 if einheit == "kWh" else kw
        zeilen.append(f"{lokal.strftime(fmt)};{f'{v:.4f}'.replace('.', dez)}")
        t += timedelta(minutes=min_)
    return "\n".join(zeilen).encode()


SPITZE = (datetime(2025, 7, 3, 11, 15), 50.0)


def test_profil_kw_volles_jahr_mit_zeitumstellung():
    p = lastprofil_lesen(_profil(spitze=SPITZE), "p.csv")
    assert p.einheit == "kW" and p.intervall_min == 15
    assert len(p.zeit_utc) == 35040 and len(set(p.zeit_utc)) == 35040     # doppelte Oktoberstunde aufgelöst
    k = kennzahlen(p)
    assert k["luecken"] == 0 and not k["hochrechnung"]
    assert k["jahresverbrauch_kwh"] == pytest.approx(10 * 8760 + 40 * 0.25)
    assert k["spitze_kw"] == pytest.approx(50) and k["spitze_zeit"] == "03.07.2025 11:15"
    assert k["benutzungsstunden"] == pytest.approx(k["jahresverbrauch_kwh"] / 50)


def test_profil_kwh_je_viertelstunde():
    p = lastprofil_lesen(_profil(einheit="kWh", kopf="Verbrauch [kWh]", spitze=SPITZE), "p.csv")
    assert p.einheit == "kWh"
    k = kennzahlen(p)
    assert k["spitze_kw"] == pytest.approx(50)                              # kWh je 15 min × 4
    assert k["jahresverbrauch_kwh"] == pytest.approx(10 * 8760 + 40 * 0.25)


def test_profil_stundenwerte():
    p = lastprofil_lesen(_profil(min_=60, kopf="kW", dez="."), "p.csv")
    k = kennzahlen(p)
    assert p.intervall_min == 60 and k["jahresverbrauch_kwh"] == pytest.approx(87600)
    assert any("unterschätzt" in h for h in k["hinweise"])


def test_profil_teiljahr_hochrechnung():
    p = lastprofil_lesen(_profil(tage=90, spitze=(datetime(2025, 2, 1, 8, 0), 30.0)), "p.csv")
    k = kennzahlen(p)
    assert k["hochrechnung"] and k["hochrechnung_faktor"] == pytest.approx(8760 / (90 * 24), rel=1e-3)
    assert k["jahresverbrauch_kwh"] == pytest.approx((10 * 90 * 24 + 20 * 0.25) * 8760 / (90 * 24), rel=1e-6)
    assert any("HOCHRECHNUNG" in h for h in k["hinweise"])


def test_profil_luecke_gemeldet():
    daten = _profil(tage=30).decode().splitlines()
    del daten[100:200]
    k = kennzahlen(lastprofil_lesen("\n".join(daten).encode(), "p.csv"))
    assert k["luecken"] == 100 and any("fehlende Intervalle" in h for h in k["hinweise"])


def test_profil_einheit_unklar_rueckfrage():
    daten = _profil(kopf="Wert")
    with pytest.raises(RueckfrageNoetig) as e:
        lastprofil_lesen(daten, "p.csv")
    assert e.value.optionen == ["kW", "kWh"]
    assert lastprofil_lesen(daten, "p.csv", einheit="kW").einheit == "kW"
    assert lastprofil_lesen(daten, "p.csv", jahresverbrauch_kwh=87_600).einheit == "kW"


def test_profil_datum_uhrzeit_getrennt_und_xlsx(tmp_path):
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Lastgang Zählpunkt DE000"])
    ws.append(["Datum", "Uhrzeit", "Wirkleistung kW"])
    t = datetime(2025, 3, 1, tzinfo=TZ).astimezone(timezone.utc)
    for i in range(96 * 3):
        lokal = (t + timedelta(minutes=15 * i)).astimezone(TZ)
        ws.append([lokal.strftime("%d.%m.%Y"), lokal.strftime("%H:%M"), 12.5])
    pfad = tmp_path / "p.xlsx"
    wb.save(pfad)
    p = lastprofil_lesen(pfad)
    assert p.einheit == "kW" and p.intervall_min == 15 and len(p.zeit_utc) == 288
    assert kennzahlen(p)["spitze_kw"] == pytest.approx(12.5)


def test_berechnen_aus_profil():
    p = lastprofil_lesen(_profil(wert_kw=20, spitze=SPITZE), "p.csv")
    r = berechnen_aus_profil(T, p)
    kwh = 20 * 8760 + 30 * 0.25
    assert r["kwh"] == pytest.approx(kwh) and r["kw"] == pytest.approx(50)
    assert r["benutzungsstunden"] == pytest.approx(kwh / 50)          # > 2.500 h
    assert r["netzentgelt_eur"] == pytest.approx(150 * 50 + 1.5 * kwh / 100)
    assert r["spitze_zeit"] == "03.07.2025 11:15"
