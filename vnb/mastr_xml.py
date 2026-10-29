"""MaStR-Gesamtdatenexport direkt aus dem ZIP lesen (ohne open-mastr-Datenbank).

open-mastr wird nur zum Herunterladen benutzt. Die Datenbank-Erzeugung von open-mastr scheitert
an Listenfeldern der aktuellen MaStR-Version (z. B. "712 812" in EinheitenSolar und Netze) und
braucht für Marktakteure und Solareinheiten viel Zeit und Speicher. Hier werden die XML-Dateien
gestreamt (lxml.iterparse), nur die benötigten Felder gelesen und nur Datensätze der
Netzbetreiber behalten.
"""
from __future__ import annotations

import re
import time
import zipfile
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

from lxml import etree

# Tabellen des Exports, die gebraucht werden (Präfix der XML-Dateinamen, kleingeschrieben)
TABELLEN = ["katalogwerte", "marktakteure", "marktakteureundrollen", "netze", "netzanschlusspunkte",
            "einheitensolar"]


def herunterladen(ordner: Path, gebiete: bool = True, log=print) -> Path:
    """Lädt die benötigten Dateien des Exports (robust, fortsetzbar) oder nutzt einen vorhandenen.

    Vorhanden heißt: vollständiger Download (Ordner) oder ZIP, höchstens 14 Tage alt.
    """
    import shutil

    from . import mastr_download

    ordner.mkdir(parents=True, exist_ok=True)
    benoetigt = set(TABELLEN if gebiete else ["katalogwerte", "marktakteure", "marktakteureundrollen"])
    for alt in sorted(ordner.glob("Gesamtdatenexport_*"), reverse=True):
        m = re.search(r"(\d{8})", alt.name)
        alter = (date.today() - datetime.strptime(m.group(1), "%Y%m%d").date()).days if m else 999
        if alter > 14:
            continue
        if alt.is_dir() and mastr_download.vollstaendig(alt) and benoetigt <= vorhandene_tabellen(alt):
            log(f"  vorhandener MaStR-Export wird verwendet: {alt.name} ({alter} Tage alt)")
            return alt
        if alt.suffix == ".zip" and benoetigt <= vorhandene_tabellen(alt):
            log(f"  vorhandener MaStR-Export wird verwendet: {alt.name} ({alter} Tage alt)")
            return alt
    ziel = mastr_download.herunterladen(ordner, benoetigt, log)
    # unvollständige Downloads anderer Tage verwerfen (deren URL gibt es nicht mehr)
    for alt in ordner.glob("Gesamtdatenexport_*"):
        if alt.is_dir() and alt != ziel and not mastr_download.vollstaendig(alt):
            shutil.rmtree(alt, ignore_errors=True)
    return ziel


def _quelle(pfad: Path):
    from .mastr_download import Teile
    return Teile(pfad) if Path(pfad).is_dir() else zipfile.ZipFile(pfad)


def vorhandene_tabellen(pfad: Path) -> set[str]:
    try:
        with _quelle(pfad) as z:
            return {n.lower().split("_")[0].split(".")[0] for n in z.namelist()}
    except (zipfile.BadZipFile, FileNotFoundError, ValueError):
        return set()


def _dateien(z: zipfile.ZipFile, tabelle: str) -> list[str]:
    def nr(n):
        m = re.search(r"_(\d+)\.xml$", n)
        return int(m.group(1)) if m else 0
    return sorted((n for n in z.namelist() if n.lower().split("_")[0].split(".")[0] == tabelle), key=nr)


def datensaetze(z: zipfile.ZipFile, tabelle: str, satz_tag: str, felder: set[str], log=None):
    """Liefert je Datensatz ein dict {feld: text} mit den gewünschten Feldern."""
    dateien = _dateien(z, tabelle)
    t0 = time.time()
    for i, name in enumerate(dateien, 1):
        if log and i > 1 and i % 10 == 1:
            log(f"    {tabelle}: {i - 1}/{len(dateien)} Dateien gelesen ({(time.time() - t0) / 60:.1f} min)")
        with z.open(name) as f:
            for _, el in etree.iterparse(f, events=("end",), tag=satz_tag, recover=True, huge_tree=True):
                d = {}
                for kind in el:
                    if kind.tag in felder and kind.text is not None:
                        d[kind.tag] = kind.text.strip()
                yield d
                el.clear()
                while el.getprevious() is not None:
                    del el.getparent()[0]


def katalog(z) -> dict[str, str]:
    return {d["Id"]: d.get("Wert", "") for d in datensaetze(z, "katalogwerte", "Katalogwert", {"Id", "Wert"})
            if "Id" in d}


# Systemkataloge: Codes, die nicht in Katalogwerte.xml stehen (Doku Gesamtdatenexport, wie open-mastr)
MARKTFUNKTION = {"1": "Stromnetzbetreiber", "2": "Anlagenbetreiber", "3": "Akteur im Strommarkt",
                 "4": "Organisierter Marktplatz", "5": "Behörde, Verband, Institution",
                 "6": "Sonstiger Marktakteur", "7": "Bundesnetzagentur", "8": "Gasnetzbetreiber",
                 "9": "Akteur im Gasmarkt", "10": "Supportpartner"}


def werte(roh: str, kat: dict) -> str:
    """Katalog-ID(s) ("712" oder "712 812") in Klartext; Text bleibt Text."""
    if not roh:
        return ""
    teile = roh.split()
    if all(t.isdigit() for t in teile):
        return " | ".join(kat.get(t, t) for t in teile)
    return roh


def lesen(zip_pfad: Path, gebiete: bool = True, log=print, rolle_regex: str = ""):
    """Liest den Export und liefert (akteure, rollen, sammler, netzinfo, rollen_zaehler).

    akteure/rollen sind pandas-DataFrames mit den MaStR-Spaltennamen, nur für Marktakteure mit einer
    Netzbetreiber-Rolle (Vorfilter, die eigentliche Auswahl macht liste.filtern).
    """
    import pandas as pd

    from .extract import norm
    from .gebiete import Sammler

    t0 = time.time()
    with _quelle(zip_pfad) as z:
        kat = katalog(z)
        log(f"  {len(kat)} Katalogwerte")
        rollen = []
        for d in datensaetze(z, "marktakteureundrollen", "MarktakteurUndRolle",
                             {"MarktakteurMastrNummer", "Marktrolle", "Marktpartneridentifikationsnummer"}):
            d["Marktrolle"] = werte(d.get("Marktrolle", ""), kat)
            rollen.append(d)
        rollen_zaehler = Counter(d["Marktrolle"] for d in rollen)

        def kandidat(r):
            if rolle_regex:
                return bool(re.search(rolle_regex, r, re.I))
            return "netzbetreiber" in norm(r) or "verteilnetz" in norm(r)
        nb_kandidaten = {d.get("MarktakteurMastrNummer") for d in rollen if kandidat(d["Marktrolle"])}
        log(f"  {len(rollen)} Rollen, {len(nb_kandidaten)} Marktakteure mit Netzbetreiber-Rolle")
        rollen = [d for d in rollen if d.get("MarktakteurMastrNummer") in nb_kandidaten]

        akteure = []
        felder = {"MastrNummer", "Firmenname", "Webseite", "WebportalDesNetzbetreibers", "Email", "Marktfunktion",
                  "Taetigkeitsende", "Ort", "Bundesland", "Personenart"}
        for d in datensaetze(z, "marktakteure", "Marktakteur", felder):
            if d.get("MastrNummer") in nb_kandidaten:
                d["Marktfunktion"] = MARKTFUNKTION.get(d.get("Marktfunktion", ""), d.get("Marktfunktion", ""))
                d["Bundesland"] = werte(d.get("Bundesland", ""), kat)
                akteure.append(d)
        log(f"  {len(akteure)} Marktakteure gelesen ({(time.time() - t0) / 60:.1f} min)")

        sammler, netzinfo = Sammler(), {}
        if gebiete:
            lok_nb, netz_nb = {}, defaultdict(set)
            for d in datensaetze(z, "netzanschlusspunkte", "Netzanschlusspunkt",
                                 {"LokationMaStRNummer", "NetzbetreiberMaStRNummer", "NetzMaStRNummer"}, log):
                nb = d.get("NetzbetreiberMaStRNummer")
                if nb in nb_kandidaten:
                    if d.get("LokationMaStRNummer"):
                        lok_nb.setdefault(d["LokationMaStRNummer"], nb)
                    if d.get("NetzMaStRNummer"):
                        netz_nb[d["NetzMaStRNummer"]].add(nb)
            log(f"  {len(lok_nb)} Lokationen mit Netzbetreiber ({(time.time() - t0) / 60:.1f} min)")

            for d in datensaetze(z, "netze", "Netz", {"MastrNummer", "Bundesland", "Sparte",
                                                      "GeschlossenesVerteilnetz"}):
                sparte = werte(d.get("Sparte", ""), kat)
                if sparte and "strom" not in norm(sparte):
                    continue
                gvn = d.get("GeschlossenesVerteilnetz", "").lower() in ("1", "true", "ja")
                laender = [x for x in werte(d.get("Bundesland", ""), kat).split(" | ") if x]
                for nb in netz_nb.get(d.get("MastrNummer"), ()):
                    info = netzinfo.setdefault(nb, {"geschlossen": [], "laender": set()})
                    info["geschlossen"].append(gvn)
                    info["laender"].update(laender)
            for info in netzinfo.values():
                info["geschlossen"] = bool(info["geschlossen"]) and all(info["geschlossen"])

            n = 0
            for d in datensaetze(z, "einheitensolar", "EinheitSolar",
                                 {"LokationMaStRNummer", "Bundesland", "Landkreis", "Gemeinde",
                                  "Gemeindeschluessel", "Postleitzahl"}, log):
                nb = lok_nb.get(d.get("LokationMaStRNummer"))
                if nb:
                    n += 1
                    sammler.add(nb, werte(d.get("Bundesland", ""), kat), d.get("Landkreis", ""), d.get("Gemeinde", ""),
                                d.get("Gemeindeschluessel", ""), d.get("Postleitzahl", ""))
            log(f"  {n} Solareinheiten {len(sammler.laender)} Netzbetreibern zugeordnet "
                f"({(time.time() - t0) / 60:.1f} min)")

    spalten_a = ["MastrNummer", "Firmenname", "Webseite", "WebportalDesNetzbetreibers", "Email", "Marktfunktion",
                 "Taetigkeitsende", "Ort", "Bundesland"]
    spalten_r = ["MarktakteurMastrNummer", "Marktrolle", "Marktpartneridentifikationsnummer"]
    return (pd.DataFrame(akteure, columns=spalten_a), pd.DataFrame(rollen, columns=spalten_r), sammler, netzinfo,
            rollen_zaehler)
