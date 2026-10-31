"""Bewertung eines heruntergeladenen Dokuments als Preisblatt-Kandidat.

RLM (Jahresleistungspreissystem) und SLP (ohne Leistungsmessung) werden getrennt bewertet,
weil sie teils in verschiedenen Preisblättern stehen (z. B. SachsenNetze).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .extract import FELDER, auswerten, jahr_pruefen, name_im_text, norm, plausibel, plausibel_slp

PREISSTAND_RANG = {"endgültig": 2, "unklar": 1, "vorläufig": 0}


@dataclass
class Kandidat:
    url: str
    datei: Path | None = None
    verwendbar: bool = False                      # RLM-NS-Werte vollständig gelesen
    ns: dict = field(default_factory=dict)
    msns: dict = field(default_factory=dict)
    slp: dict = field(default_factory=dict)       # "ap" ct/kWh, "gp" €/a
    preisstand: str = "unklar"
    stand_datum: str = ""
    grenze_le: bool = False
    hinweise: list = field(default_factory=list)
    pruefen: list = field(default_factory=list)   # Gründe für status pruefen (RLM und allgemein)
    slp_pruefen: list = field(default_factory=list)
    slp_hinweise: list = field(default_factory=list)
    name_fehlt: bool = False
    folgejahr: bool = False                       # Preisblatt des Folgejahres (kein Blatt für das gesuchte Jahr)
    grund: str = ""                               # warum gar nicht verwendbar

    @property
    def slp_verwendbar(self) -> bool:
        return bool(self.slp)

    @property
    def slp_ok(self) -> bool:
        return self.slp_verwendbar and not self.slp_pruefen and not self.name_fehlt

    def _datum(self):
        d = self.stand_datum
        return d[6:10] + d[3:5] + d[0:2] if len(d) == 10 else ""

    def rang(self):
        return (self.verwendbar, not self.folgejahr, not self.pruefen, PREISSTAND_RANG.get(self.preisstand, 1), self.slp_ok,
                self._datum())

    def slp_rang(self):
        return (self.slp_verwendbar, not self.folgejahr, self.slp_ok, PREISSTAND_RANG.get(self.preisstand, 1), self._datum())

    def werte_tupel(self):
        return tuple(round(self.ns.get(k, -1), 4) for k in FELDER)


def bewerten(pfad: Path, url: str, name: str, aliase=(), website: str = "", jahr: int = 2026,
             pflicht=(), ausschluss=(), kontext: str = "") -> Kandidat:
    k = Kandidat(url=url, datei=pfad)
    try:
        erg = auswerten(pfad, url, jahr)
    except Exception as e:  # defekte Datei, Passwortschutz usw.
        k.grund = f"nicht lesbar ({type(e).__name__})"
        return k
    if len(erg.text.strip()) < 200:
        k.grund = "kein Text im Dokument (Scan?)"
        return k
    j = jahr_pruefen(erg, jahr, url)
    if j and jahr_pruefen(erg, jahr + 1, url) is None:
        # nur das Blatt des Folgejahres: verwenden, aber nachrangig (jedes Blatt des Jahres geht vor)
        k.folgejahr = True
        k.hinweise.append(f"Preisblatt {jahr + 1} (kein Preisblatt {jahr} gefunden)")
        k.slp_hinweise.append(f"Standardlastprofil aus Preisblatt {jahr + 1}")
    elif j:
        k.grund = j
        return k
    if not erg.ns_vollstaendig and not erg.slp:
        k.grund = "weder RLM- (NS) noch SLP-Werte gefunden"
        unklar = list(dict.fromkeys(erg.unklar + erg.slp_unklar))
        if unklar:
            k.grund += " (" + "; ".join(unklar) + ")"
        return k

    # Netzgebiet (mehrere Netzbetreiber/Gebiete auf derselben Website)
    such = norm(url + " " + kontext + " " + erg.text[:3000])
    if pflicht and not any(t in such for t in pflicht):
        k.grund = f"Netzgebiet passt nicht (erwartet: {', '.join(pflicht)})"
        return k
    if ausschluss and any(t in norm(url + " " + kontext) for t in ausschluss):
        k.grund = "Preisblatt eines anderen Netzgebiets"
        return k

    k.preisstand, k.stand_datum, k.grenze_le = erg.preisstand, erg.stand_datum, erg.grenze_le
    k.name_fehlt = not name_im_text(name, erg.text, aliase, website)

    if erg.ns_vollstaendig:
        k.verwendbar = True
        k.ns, k.msns = dict(erg.ns), dict(erg.msns)
        k.hinweise.extend(erg.hinweise)
        k.pruefen.extend(plausibel(k.ns, "NS"))
        if k.msns:
            k.pruefen.extend(plausibel(k.msns, "MS/NS"))
        else:
            k.hinweise.append("Umspannung MS/NS nicht gefunden")
        k.pruefen.extend(dict.fromkeys(erg.unklar))
        if k.name_fehlt:
            k.pruefen.append("Netzbetreibername nicht im Dokument")
    else:
        k.grund = "keine NS-Werte im Jahresleistungspreissystem (nur SLP)"

    if erg.slp:
        k.slp = dict(erg.slp)
        k.slp_pruefen.extend(plausibel_slp(k.slp))
        k.slp_hinweise.extend(erg.slp_hinweise)
    k.slp_pruefen.extend(dict.fromkeys(erg.slp_unklar))
    if re.search(r"§\s*14\s*a", erg.text[:1500]) and not re.search(r"jahresleistungspreis", norm(erg.text[:1500])):
        k.hinweise.append("Dokument beginnt mit § 14a")
    return k
