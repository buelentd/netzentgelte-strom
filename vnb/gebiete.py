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


def _tabelle(namen, *kandidaten):
    low = {n.lower(): n for n in namen}
    for k in kandidaten:
        if k.lower() in low:
            return low[k.lower()]
    return None


def _spalte(spalten, *kandidaten):
    low = {c.lower(): c for c in spalten}
    for k in kandidaten:
        if k.lower() in low:
            return low[k.lower()]
    return None


def aus_mastr_db(engine, log=print) -> tuple[Sammler, dict]:
    """Liest Netzanschlusspunkte, Netze und Solareinheiten aus der open-mastr-Datenbank.

    Rückgabe: (Sammler, Netzinfo je Netzbetreiber {nb: {"geschlossen": bool, "laender": set}})
    """
    import pandas as pd
    from sqlalchemy import inspect, text

    insp = inspect(engine)
    tabellen = insp.get_table_names()
    t_nap = _tabelle(tabellen, "grid_connections", "netzanschlusspunkte")
    t_netze = _tabelle(tabellen, "grids", "netze")
    t_solar = _tabelle(tabellen, "units_solar", "solar_extended", "einheitensolar")
    sammler, netzinfo = Sammler(), {}
    if not t_nap:
        log("  Netzanschlusspunkte fehlen in der MaStR-Datenbank, Netzgebiete nicht ableitbar")
        return sammler, netzinfo

    sp = [c["name"] for c in insp.get_columns(t_nap)]
    c_lok = _spalte(sp, "LokationMaStRNummer", "LokationMastrNummer")
    c_nb = _spalte(sp, "NetzbetreiberMaStRNummer", "NetzbetreiberMastrNummer")
    c_netz = _spalte(sp, "NetzMaStRNummer", "NetzMastrNummer")
    lok_nb, netz_nb = {}, defaultdict(set)
    sql = f'SELECT "{c_lok}", "{c_nb}", "{c_netz}" FROM "{t_nap}"' if c_netz else \
        f'SELECT "{c_lok}", "{c_nb}", NULL FROM "{t_nap}"'
    with engine.connect() as con:
        for lok, nb, netz in con.execute(text(sql)):
            if lok and nb:
                lok_nb.setdefault(lok, nb)
            if netz and nb:
                netz_nb[netz].add(nb)
    log(f"  {len(lok_nb)} Lokationen mit Netzbetreiber")

    if t_netze:
        sp = [c["name"] for c in insp.get_columns(t_netze)]
        c_nr, c_bl = _spalte(sp, "MastrNummer"), _spalte(sp, "Bundesland")
        c_sparte, c_gvn = _spalte(sp, "Sparte"), _spalte(sp, "GeschlossenesVerteilnetz")
        netze = pd.read_sql_table(t_netze, engine, columns=[c for c in (c_nr, c_bl, c_sparte, c_gvn) if c])
        for _, r in netze.iterrows():
            if c_sparte and "strom" not in str(r[c_sparte]).lower():
                continue
            gvn = str(r[c_gvn]).strip().lower() in ("1", "true", "ja", "1.0") if c_gvn else False
            for nb in netz_nb.get(r[c_nr], ()):
                info = netzinfo.setdefault(nb, {"geschlossen": [], "laender": set()})
                info["geschlossen"].append(gvn)
                if c_bl and r[c_bl] and str(r[c_bl]) != "None":
                    info["laender"].add(str(r[c_bl]))
        for info in netzinfo.values():
            info["geschlossen"] = bool(info["geschlossen"]) and all(info["geschlossen"])

    if t_solar:
        sp = [c["name"] for c in insp.get_columns(t_solar)]
        spalten = [_spalte(sp, n) for n in ("LokationMaStRNummer", "Bundesland", "Landkreis", "Gemeinde",
                                            "Gemeindeschluessel", "Postleitzahl")]
        if spalten[0]:
            auswahl = ", ".join(f'"{c}"' if c else "NULL" for c in spalten)
            with engine.connect() as con:
                for lok, bl, lk, gem, gs, plz in con.execute(text(f'SELECT {auswahl} FROM "{t_solar}"')):
                    nb = lok_nb.get(lok)
                    if nb:
                        sammler.add(nb, str(bl or ""), str(lk or ""), str(gem or ""), str(gs or ""),
                                    str(plz or "").split(".")[0])
        log(f"  Solareinheiten {len(sammler.laender)} Netzbetreibern zugeordnet")
    else:
        log("  Solareinheiten fehlen in der MaStR-Datenbank, Region/Netztyp nur aus Sitz")
    return sammler, netzinfo


def plz_schreiben(sammler: Sammler, namen: dict[str, str], pfad: Path):
    with open(pfad, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["plz", "mastr_nr", "netzbetreiber", "anteil_prozent", "einheiten"],
                           delimiter=";")
        w.writeheader()
        for z in sammler.plz_zeilen(namen):
            z["anteil_prozent"] = str(z["anteil_prozent"]).replace(".", ",")
            w.writerow(z)
