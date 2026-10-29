"""Übernahme der 50 geprüften Pilot-Netzbetreiber und Abgleich mit der MaStR-Liste."""
from __future__ import annotations

import csv
import re
from pathlib import Path

from .extract import de_zahl, norm
from .netz import basis_domain

# Namen im MaStR, die vom Pilot-Kurznamen abweichen (Umbenennungen, Langformen)
ALIASE = {
    "DONETZ (Dortmund)": ["Dortmunder Netz", "DONETZ"],
    "EVH Netz (Halle)": ["Energieversorgung Halle Netz", "EVH Netz"],
    "MITNETZ Strom": ["Mitteldeutsche Netzgesellschaft Strom", "MITNETZ STROM"],
    "ThügaNETZE": ["Thüga Energienetze", "ThügaNETZE"],
    "E-Werk Netze (Mittelbaden)": ["E-Werk Netze", "Netze Mittelbaden"],
    "MVV Netze (ehem. Netrion, Mannheim)": ["MVV Netze", "Netrion"],
    "naturenergie netze (ehem. ED Netze)": ["naturenergie netze", "ED Netze"],
    "SachsenNetze (Dresden)": ["SachsenNetze"],
    "SWM Infrastruktur (München)": ["SWM Infrastruktur"],
    "Stadtwerke Karlsruhe Netzservice": ["Netzservice SWKA", "Stadtwerke Karlsruhe Netzservice"],
    "TEN Thüringer Energienetze": ["TEN Thüringer Energienetze", "Thüringer Energienetze"],
    "N-ERGIE Netz (Nürnberg)": ["N-ERGIE Netz"],
    "BS|NETZ (Braunschweig)": ["BS|NETZ", "BS Netz"],
}
# Website, wenn die Quelle auf einem CDN liegt bzw. kein MaStR-Treffer existiert
WEBSITES = {
    "Netze BW": "https://www.netze-bw.de",
    "Netzgesellschaft Düsseldorf": "https://www.netz-duesseldorf.de",
    "Hamburger Energienetze": "https://www.hamburger-energienetze.de",
    "Netz Leipzig": "https://www.netz-leipzig.de",
}
CDN = ("ctfassets.net", "storyblok.com", "admiralcloud.com", "l.de")


def _kompakt(s: str) -> str:
    s = re.sub(r"\b(gmbh|ag|kg|mbh|co|ug|se|eg)\b", " ", norm(s))
    return re.sub(r"[^a-z0-9]", "", s)


def lesen(pfad: Path) -> list[dict]:
    with open(pfad, newline="", encoding="utf-8-sig") as f:
        zeilen = list(csv.DictReader(f, delimiter=";"))
    for z in zeilen:
        for k in ("ns_lp_unter_2500", "ns_ap_unter_2500", "ns_lp_ueber_2500", "ns_ap_ueber_2500"):
            z[k] = de_zahl(z[k]) if z.get(k) else None
    return zeilen


def zuordnen(pilot: dict, liste: list[dict]) -> dict | None:
    """Sucht den MaStR-Eintrag zum Pilot-Netzbetreiber (Name, sonst Domain der Quelle)."""
    name = pilot["netzbetreiber"]
    ohne_klammer = re.sub(r"\(.*?\)", " ", name)
    klammer = re.findall(r"\(([^)]*)\)", name)
    versuche = []
    if klammer:
        versuche.append(_kompakt(ohne_klammer + " " + klammer[0].split(",")[-1]))
    versuche.append(_kompakt(ohne_klammer))
    versuche += [_kompakt(a) for a in ALIASE.get(name, [])]
    for v in versuche:
        if len(v) < 4:
            continue
        treffer = [e for e in liste if v in _kompakt(e["netzbetreiber"])]
        if treffer:
            return min(treffer, key=lambda e: len(_kompakt(e["netzbetreiber"])))
    dom = basis_domain(pilot["quelle"])
    if dom not in CDN:
        treffer = [e for e in liste if e.get("website") and basis_domain(
            e["website"] if "://" in e["website"] else "https://" + e["website"]) == dom]
        if len(treffer) == 1:
            return treffer[0]
    return None


def website(pilot: dict, eintrag: dict | None) -> str:
    if eintrag and eintrag.get("website"):
        return eintrag["website"]
    name = pilot["netzbetreiber"]
    if name in WEBSITES:
        return WEBSITES[name]
    dom = basis_domain(pilot["quelle"])
    return "" if dom in CDN else "https://www." + dom
