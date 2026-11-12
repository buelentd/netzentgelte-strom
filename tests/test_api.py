import os

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from api.main import app  # noqa: E402

c = TestClient(app)
BERLIN = "SNB979269087643"


def test_health():
    r = c.get("/api/v1/health").json()
    assert r["status"] == "ok" and r["netzbetreiber"] == 831


def test_plz_und_netzbetreiber():
    r = c.get("/api/v1/plz/10115").json()
    assert r["netzbetreiber"][0]["mastr_nr"] == BERLIN
    assert r["konzessionsabgabe"]["ka_tarifkunden_hoechstsatz_ct_kwh"] == 2.39
    assert c.get("/api/v1/plz/1011").status_code == 422
    assert c.get("/api/v1/netzbetreiber", params={"plz": "10115"}).json()[0]["mastr_nr"] == BERLIN
    assert c.get("/api/v1/netzbetreiber/SNB000").status_code == 404


def test_netzentgelte_und_hlzf():
    r = c.get(f"/api/v1/netzentgelte/{BERLIN}", params={"ebene": "ns"}).json()
    assert r["rlm"]["ns"]
    h = c.get(f"/api/v1/hlzf/{BERLIN}/zeitreihe", params={"ebene": "ns", "jahr": 2026}).json()
    assert h["werte"] == 35040 and sum(h["is_hlzf"]) > 0


def test_berechnung():
    r = c.post("/api/v1/berechnung/netzentgelt", json={"plz": "10115", "kwh": 200000, "kw": 60}).json()
    assert r["mastr_nr"] == BERLIN and r["ergebnis"]
    assert c.post("/api/v1/berechnung/netzentgelt", json={"kwh": 1000}).status_code == 422


def test_umlagen_und_schluessel(monkeypatch):
    assert len(c.get("/api/v1/umlagen").json()) == 14
    monkeypatch.setenv("NETZENTGELTE_API_KEY", "geheim")
    assert c.get("/api/v1/umlagen").status_code == 401
    assert c.get("/api/v1/umlagen", headers={"X-API-Key": "geheim"}).status_code == 200
