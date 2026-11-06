"""Prüft die Ergebnisdaten selbst (nicht den Lesecode): Plausibilität der geprüften Zeilen und Übereinstimmung der Testseite mit der CSV."""
import csv, json, re
from pathlib import Path

W = Path(__file__).resolve().parent.parent
F = lambda s: float(s.replace(",", ".")) if s else None
EB = ("hsms", "ms", "msns", "ns")
K = ("lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh")


def zeilen():
    with open(W / "ergebnis" / "netzentgelte_2026.csv", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def test_mastr_nummern_eindeutig():
    z = zeilen()
    m = [r["mastr_nr"] for r in z]
    assert len(m) == len(set(m))


def test_ok_zeilen_haben_slp_und_niederspannung_vollstaendig():
    for r in zeilen():
        if r["status"] != "ok":
            continue
        assert r["slp_ap_ct_kwh"] and r["slp_grundpreis_eur_jahr"], r["nr"]
        assert all(r[f"ns_{k}"] for k in K), r["nr"]


def test_werte_im_plausiblen_bereich():
    for r in zeilen():
        if r["status"] != "ok":
            continue
        ap, gp = F(r["slp_ap_ct_kwh"]), F(r["slp_grundpreis_eur_jahr"])
        assert 2 <= ap <= 15 and 0 <= gp <= 200, (r["nr"], ap, gp)       # unter 3 ct nur von Hand am Dokument bestätigt (z. B. Olching)
        for eb in EB:
            v = [F(r[f"{eb}_{k}"]) for k in K]
            if None in v:
                continue
            assert all(x >= 0 for x in v), (r["nr"], eb)
            assert v[2] <= 500 and v[0] <= 200 and v[1] <= 30 and v[3] <= 30, (r["nr"], eb, v)


def test_testseite_stimmt_mit_csv_ueberein():
    pfad = W / "abschaetzung_testseite" / "netzentgelt_abschaetzung.html"
    if not pfad.exists():
        return
    d = json.loads(re.search(r'id="daten">(.*?)</script>', pfad.read_text(encoding="utf-8"), re.S).group(1))
    R = {r["nr"]: r for r in zeilen()}
    for e in d["nb"]:
        r = R[str(e["n"])]
        ns = [F(r[f"ns_{k}"]) for k in K]
        slp = [F(r["slp_ap_ct_kwh"]), F(r["slp_grundpreis_eur_jahr"])]
        assert (e.get("ns") or None) == (ns if None not in ns else None), e["n"]
        assert (e.get("slp") or None) == (slp if None not in slp else None), e["n"]
