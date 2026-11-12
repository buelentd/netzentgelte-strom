"""REST-API v1 für die Netzentgelt-Daten (Netzentgelte, Hochlastzeitfenster, Modul 3, PLZ, Umlagen).
Schlüssel ist die MaStR-Nr. Daten: ergebnis/conplot/*.json (erzeugt von daten/conplot_export.py) und ergebnis/netzentgelte_2026.csv.
Start: uvicorn api.main:app --port 8000   Doku: /docs (Swagger) und /openapi.json
Optionaler Zugriffsschutz: Umgebungsvariable NETZENTGELTE_API_KEY setzen, dann Header X-API-Key verlangen."""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from vnb import rechner  # noqa: E402

VERSION = "1.0.0"
JAHR = 2026
EBENEN = ("ns", "msns", "ms")


def _json(name: str):
    return json.loads((ROOT / "ergebnis" / "conplot" / name).read_text(encoding="utf-8"))


def _csv(pfad: str):
    return list(csv.DictReader(open(ROOT / pfad, encoding="utf-8-sig"), delimiter=";"))


@lru_cache(maxsize=1)
def daten() -> dict:
    nb = _json("netzbetreiber_2026.json")
    liste = nb["netzbetreiber"]
    return {
        "meta": {k: v for k, v in nb.items() if k != "netzbetreiber"},
        "nb": {e["mastr_nr"]: e for e in liste},
        "plz": _json("plz_2026.json"),
        "ka": _json("plz_konzessionsabgabe_2026.json"),
        "umlagen": _json("umlagen_steuern_2026.json"),
        "zeilen": {r["mastr_nr"]: r for r in _csv("ergebnis/netzentgelte_2026.csv")},
        "hlzf_zeilen": {r["mastr_nr"]: r for r in _csv("lauf/hlzf_zusammen.csv")},
    }


def schluessel(x_api_key: str | None = Header(default=None)):
    erwartet = os.environ.get("NETZENTGELTE_API_KEY")
    if erwartet and x_api_key != erwartet:
        raise HTTPException(401, "API-Schlüssel fehlt oder ist falsch (Header X-API-Key)")


router = APIRouter(prefix="/api/v1", dependencies=[Depends(schluessel)])


def _nb(mastr_nr: str) -> dict:
    e = daten()["nb"].get(mastr_nr.upper())
    if not e:
        raise HTTPException(404, f"Netzbetreiber {mastr_nr} unbekannt")
    return e


def _kurz(e: dict) -> dict:
    return {"mastr_nr": e["mastr_nr"], "netzbetreiber": e["netzbetreiber"], "bundesland": e.get("bundesland"), "status": e.get("status"), "website": e.get("website")}


@router.get("/health", tags=["Meta"])
def health():
    d = daten()
    return {"status": "ok", "version": VERSION, "jahr": JAHR, "netzbetreiber": len(d["nb"]), "plz": len(d["plz"])}


@router.get("/netzbetreiber", tags=["Netzbetreiber"], summary="Netzbetreiber suchen (Name oder PLZ)")
def netzbetreiber_suchen(q: str | None = Query(None, description="Teil des Namens"), plz: str | None = Query(None, min_length=5, max_length=5),
                         limit: int = Query(50, ge=1, le=500)):
    d = daten()
    if plz:
        return [dict(_kurz(_nb(x["mastr_nr"])), anteil_prozent=x["anteil_prozent"]) for x in d["plz"].get(plz, [])]
    treffer = [e for e in d["nb"].values() if not q or q.lower() in e["netzbetreiber"].lower()]
    return [_kurz(e) for e in treffer[:limit]]


@router.get("/netzbetreiber/{mastr_nr}", tags=["Netzbetreiber"], summary="Alle Daten eines Netzbetreibers")
def netzbetreiber(mastr_nr: str):
    return _nb(mastr_nr)


@router.get("/netzentgelte/{mastr_nr}", tags=["Netzentgelte"], summary="Preise je Netzebene (beide Preissysteme) und SLP")
def netzentgelte(mastr_nr: str, ebene: str | None = Query(None, description="ns, msns oder ms")):
    e = _nb(mastr_nr)
    rlm = e.get("rlm") or {}
    if ebene:
        if ebene.lower() not in EBENEN:
            raise HTTPException(422, "ebene muss ns, msns oder ms sein")
        rlm = {ebene.lower(): rlm.get(ebene.lower())}
    return {"mastr_nr": e["mastr_nr"], "netzbetreiber": e["netzbetreiber"], "jahr": e.get("jahr"), "preisstand": e.get("preisstand"),
            "stand_datum": e.get("stand_datum"), "grenze": e.get("grenze"), "einheiten": "LP in EUR/kW und Jahr, AP in ct/kWh, alles netto",
            "rlm": rlm, "slp": e.get("slp"), "preise_2027_vorlaeufig": e.get("preise_2027_vorlaeufig"), "quelle_url": e.get("quelle_url")}


@router.get("/plz/{plz}", tags=["PLZ"], summary="Netzbetreiber und Konzessionsabgabe einer PLZ")
def plz_info(plz: str):
    if not re.fullmatch(r"\d{5}", plz):
        raise HTTPException(422, "PLZ muss fünfstellig sein")
    d = daten()
    nbs = d["plz"].get(plz)
    if not nbs:
        raise HTTPException(404, f"PLZ {plz} unbekannt")
    return {"plz": plz, "netzbetreiber": [dict(_kurz(_nb(x["mastr_nr"])), anteil_prozent=x["anteil_prozent"]) for x in nbs],
            "konzessionsabgabe": d["ka"].get(plz)}


@router.get("/hlzf/{mastr_nr}", tags=["Hochlastzeitfenster"], summary="Hochlastzeitfenster nach § 19 Abs. 2 StromNEV")
def hlzf(mastr_nr: str):
    e = _nb(mastr_nr)
    return {"mastr_nr": e["mastr_nr"], "netzbetreiber": e["netzbetreiber"], "hlzf": e.get("hlzf"),
            "hinweis": "Zeitfenster gelten Mo-Fr ohne Feiertage; ‚keins' heißt: in dieser Jahreszeit kein Fenster. Leer = nicht erfasst."}


@router.get("/hlzf/{mastr_nr}/zeitreihe", tags=["Hochlastzeitfenster"], summary="Viertelstunden-Vektor (is_hlzf) für ein Jahr")
def hlzf_zeitreihe(mastr_nr: str, ebene: str = Query("ns", pattern="^(ns|msns)$"), jahr: int = Query(JAHR, ge=2024, le=2030),
                   brueckentage: bool = False):
    e = _nb(mastr_nr)
    d = daten()
    zeile = dict(d["hlzf_zeilen"].get(e["mastr_nr"], {}))
    zeile["bundesland"] = d["zeilen"].get(e["mastr_nr"], {}).get("bundesland", "")
    if not (e.get("hlzf") or {}).get(ebene):
        raise HTTPException(404, "Für diese Ebene sind keine Hochlastzeitfenster erfasst")
    from daten.hlzf_zeitreihe import vektor
    v = vektor(zeile, ebene, jahr, brueckentage)
    return {"mastr_nr": e["mastr_nr"], "ebene": ebene, "jahr": jahr, "intervall_minuten": 15, "werte": len(v), "zeitzone": "lokale Zeit, ohne Sommerzeit-Verschiebung",
            "is_hlzf": v}


@router.get("/modul3/{mastr_nr}", tags=["Modul 3 (§ 14a)"], summary="Zeitvariable Netzentgelte (HT/ST/NT)")
def modul3(mastr_nr: str):
    e = _nb(mastr_nr)
    if not e.get("modul3"):
        raise HTTPException(404, "Für diesen Netzbetreiber ist kein Modul 3 erfasst")
    return {"mastr_nr": e["mastr_nr"], "netzbetreiber": e["netzbetreiber"], "modul3": e["modul3"]}


@router.get("/umlagen", tags=["Umlagen und Steuern"], summary="Umlagen, Stromsteuer, Konzessionsabgabe, Umsatzsteuer")
def umlagen():
    return daten()["umlagen"]


class Anfrage(BaseModel):
    mastr_nr: str | None = Field(None, description="MaStR-Nr. des Netzbetreibers")
    plz: str | None = Field(None, min_length=5, max_length=5, description="Alternativ: PLZ, größter Netzbetreiber")
    kwh: float = Field(..., gt=0, description="Jahresverbrauch in kWh")
    kw: float | None = Field(None, gt=0, description="Jahreshöchstleistung in kW (optional)")
    ebene: str = Field("NS", pattern="^(NS|MS/NS)$")
    stunden: float | None = Field(None, gt=0, le=8760, description="Benutzungsstunden, falls kW unbekannt")


@router.post("/berechnung/netzentgelt", tags=["Berechnung"], summary="Netzentgelt für Verbrauch und Leistung")
def berechnung(a: Anfrage):
    d = daten()
    mastr = a.mastr_nr
    if not mastr and a.plz:
        nbs = d["plz"].get(a.plz)
        if not nbs:
            raise HTTPException(404, f"PLZ {a.plz} unbekannt")
        mastr = nbs[0]["mastr_nr"]
    if not mastr:
        raise HTTPException(422, "mastr_nr oder plz angeben")
    zeile = d["zeilen"].get(mastr.upper())
    if not zeile:
        raise HTTPException(404, f"Netzbetreiber {mastr} unbekannt")
    try:
        r = rechner.berechnen(rechner.Tarif.aus_zeile(zeile), a.kwh, a.kw, ebene=a.ebene, stunden=a.stunden)
    except ValueError as ex:
        raise HTTPException(422, str(ex))
    return {"mastr_nr": mastr.upper(), "ergebnis": r, "hinweis": "netto, ohne Umlagen, Konzessionsabgabe, Messstellenbetrieb und Umsatzsteuer"}


app = FastAPI(title="Netzentgelte Strom API", version=VERSION,
              description="Netzentgelte 2026 aller Stromverteilnetzbetreiber (Preisblätter), Hochlastzeitfenster, Modul 3, PLZ-Zuordnung und Umlagen. Schlüssel: MaStR-Nr. Stand der Daten siehe /api/v1/health.")
app.include_router(router)
