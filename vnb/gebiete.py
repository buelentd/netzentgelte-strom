"""Netzgebiet je Netzbetreiber aus dem MaStR: Bundesland, Region, Netztyp, PLZ-Zuordnung.

Das Netzgebiet wird aus den Standorten der Solareinheiten abgeleitet: Jede Einheit hängt über
ihren Netzanschlusspunkt (Lokation) an genau einem Netzbetreiber, und Solareinheiten gibt es in
praktisch jeder Gemeinde. Gezählt wird, in welchen Gemeinden/Landkreisen/Bundesländern/PLZ die
Einheiten eines Netzbetreibers liegen.

Netztyp (regelbasiert, Schwellen in LEGENDE.md):
  Stadtnetz     95 % der Einheiten liegen in höchstens 2 Gemeinden
  Regionalnetz  sonst, wenn 95 % in höchstens 25 Gemeinden und höchstens 2 Landkreisen liegen
  Flächennetz   sonst
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

MIN_EINHEITEN = 10
STADT_MAX_GEMEINDEN = 2
REGION_MAX_GEMEINDEN = 25
REGION_MAX_LANDKREISE = 2
BUNDESLAND_MIN_ANTEIL = 0.05
PLZ_MIN_ANTEIL = 0.02


def _abdeckung(zaehler: Counter, anteil=0.95) -> int:
    gesamt = sum(zaehler.values())
    summe = n = 0
    for _, v in zaehler.most_common():
        summe += v
        n += 1
        if summe >= anteil * gesamt:
            break
    return n


class Sammler:
    """Zählt Einheiten je Netzbetreiber und Ort (blockweise, für Millionen Zeilen geeignet)."""

    def __init__(self):
        self.gemeinden = defaultdict(Counter)
        self.landkreise = defaultdict(Counter)
        self.laender = defaultdict(Counter)
        self.plz = defaultdict(Counter)        # plz -> Counter(nb)
        self.plz_gemeinde = defaultdict(Counter)  # plz -> Counter((gemeindeschluessel, gemeinde))

    def add(self, nb: str, bundesland: str, landkreis: str, gemeinde: str, gemeindeschluessel: str, plz: str,
            anzahl: int = 1):
        if not nb:
            return
        g = gemeindeschluessel or f"{landkreis}|{gemeinde}"
        if gemeinde or gemeindeschluessel:
            self.gemeinden[nb][(g, gemeinde)] += anzahl
        if landkreis:
            self.landkreise[nb][landkreis] += anzahl
        if bundesland:
            self.laender[nb][bundesland] += anzahl
        if plz:
            self.plz[str(plz).zfill(5)][nb] += anzahl
            if gemeinde or gemeindeschluessel:
                self.plz_gemeinde[str(plz).zfill(5)][(str(gemeindeschluessel or ""), gemeinde or "")] += anzahl

    def gebiet(self, nb: str) -> dict:
        gem, lk, bl = self.gemeinden.get(nb, Counter()), self.landkreise.get(nb, Counter()), self.laender.get(nb, Counter())
        n = sum(bl.values()) or sum(gem.values())
        if n < MIN_EINHEITEN:
            return {}
        bl_n = sum(bl.values())
        laender = [k for k, v in bl.most_common() if v >= BUNDESLAND_MIN_ANTEIL * bl_n]
        n_gem, n_lk = _abdeckung(gem), _abdeckung(lk)
        if n_gem <= STADT_MAX_GEMEINDEN:
            typ = "Stadtnetz"
            namen = [name for (_, name), _ in gem.most_common(n_gem) if name]
            region = ", ".join(namen)
        else:
            typ = "Regionalnetz" if n_gem <= REGION_MAX_GEMEINDEN and n_lk <= REGION_MAX_LANDKREISE else "Flächennetz"
            namen = [k for k, _ in lk.most_common(min(n_lk, 3))]
            region = ", ".join(namen) + (" u. a." if n_lk > 3 else "")
        return {"bundesland": " / ".join(laender), "region": region, "netztyp": typ,
                "gebiet_einheiten": n, "gebiet_gemeinden": n_gem}

    def plz_zeilen(self, namen: dict[str, str]):
        for plz in sorted(self.plz):
            c = self.plz[plz]
            gesamt = sum(c.values())
            for nb, v in c.most_common():
                if nb in namen and v / gesamt >= PLZ_MIN_ANTEIL:
                    yield {"plz": plz, "mastr_nr": nb, "netzbetreiber": namen[nb],
                           "anteil_prozent": round(100 * v / gesamt, 1), "einheiten": v}


def plz_schreiben(sammler: Sammler, namen: dict[str, str], pfad: Path):
    with open(pfad, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["plz", "mastr_nr", "netzbetreiber", "anteil_prozent", "einheiten"],
                           delimiter=";")
        w.writeheader()
        for z in sammler.plz_zeilen(namen):
            z["anteil_prozent"] = str(z["anteil_prozent"]).replace(".", ",")
            w.writerow(z)


def plz_gemeinde_schreiben(sammler: Sammler, pfad: Path, min_anteil: float = 0.02):
    """Postleitzahl -> Gemeinde (n:m) aus den Standorten der Solareinheiten im MaStR: plz;gemeindeschluessel;gemeinde;einheiten;anteil_prozent.
    Gemeindeschluessel = AGS laut MaStR (8-stellig, wenn vorhanden). Gemeinden unter 2 % der Einheiten einer PLZ entfallen."""
    with open(pfad, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["plz", "gemeindeschluessel", "gemeinde", "einheiten", "anteil_prozent"])
        for plz in sorted(sammler.plz_gemeinde):
            c = sammler.plz_gemeinde[plz]
            gesamt = sum(c.values())
            for (ags, name), v in c.most_common():
                if v / gesamt >= min_anteil:
                    w.writerow([plz, ags, name, v, str(round(100 * v / gesamt, 1)).replace(".", ",")])
