"""Hochlastzeitfenster (HLZF) und Erheblichkeitsschwellen für die atypische Netznutzung (§ 19 Abs. 2 Satz 1 StromNEV).

Aus dem Textauszug (pdftotext -layout) eines Dokuments des Netzbetreibers:
  - Zeitfenster je Spannungsebene (NS, MSNS) und Jahreszeit (fruehling, sommer, herbst, winter)
  - Erheblichkeitsschwelle in Prozent und Mindestleistung in kW, wo angegeben

Gelesen werden drei Formen:
  A. Jahreszeiten als Spalten, Ebenen als Zeilen (Glattbach)
  B. Ebenen als Spalten, Jahreszeiten als Zeilen, oft mit Zeilen "Erheblichkeitsschwelle" (Greding)
  C. ein Fenster für das ganze Jahr ohne Jahreszeiten (Kaiserslautern)
Raster mit markierten Viertelstunden (die Markierung fehlt im Textauszug) und reiner Fließtext werden nicht gelesen.
Nichts wird geschätzt: Was nicht eindeutig ist, bleibt leer und steht im Grund.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .extract import ebene

JAHRESZEITEN = ("fruehling", "sommer", "herbst", "winter")
JZ_WORT = re.compile(r"fr[üu]e?hling|fr[üu]hjahr|sommer|herbst|winter", re.I)
ZEIT = re.compile(r"(?<![\d:.])([0-2]?\d):([0-5]\d)\s*(?:uhr)?\s*(?:-|–|bis)\s*([0-2]?\d):([0-5]\d)(?![\d:])", re.I)
KEIN = re.compile(r"(?<![\w])(?:-|–|—|kein(?:e)?\s*(?:hlf|hlzf|hochlastzeit\w*)?|keine?)(?![\w:])", re.I)
EBENE_WORT = re.compile(r"(?:umspann\w*\s*(?:in\s*|zur\s*|auf\s*)?)?(?:hoch|mittel|nieder)spannung\w*|"
                        r"umspann\w*\s*(?:hs|ms)\s*/\s*(?:ms|ns)|\b(?:hs/ms|ms/ns|hs|ms|ns)\b", re.I)
# Standard laut BNetzA-Festlegung (fachlich zu bestätigen); nur genutzt, wenn das Dokument nichts nennt
STANDARD_SCHWELLE = {"NS": 30, "MSNS": 30}


@dataclass
class Hlzf:
    fenster: dict = field(default_factory=dict)       # {"NS": {"winter": ["17:00-19:00"], ...}, "MSNS": {...}}
    schwelle: dict = field(default_factory=dict)      # {"NS": 30} in Prozent, nur laut Dokument
    mindest_kw: dict = field(default_factory=dict)    # {"NS": 100}
    jahr: int | None = None
    form: str = ""
    grund: str = ""

    @property
    def gelesen(self) -> bool:
        return bool(self.fenster)


def _jz(wort: str) -> str:
    w = wort.lower().replace("ü", "u")
    return "fruehling" if w.startswith("fr") else w


def _ebene_text(t: str) -> str | None:
    """"Niederspannung" → NS, "Umspannung MS/NS" → MSNS, "Mittelspannung" → None (nicht gebraucht)."""
    t = t.strip()
    if re.fullmatch(r"ns", t, re.I):
        return "NS"
    if re.fullmatch(r"ms\s*/\s*ns|umspann\w*\s*ms\s*/\s*ns", t, re.I):
        return "MSNS"
    return ebene(t)


def _zeiten(text: str):
    """[(pos, "07:30-14:45")] einer Zeile; keine aus Erläuterungssätzen ("z. B. 11:45 - 13:00 Uhr entspricht …")."""
    rest = re.findall(r"[A-Za-zÄÖÜäöüß]{3,}", ZEIT.sub(" ", text))
    if len(rest) >= 6:
        return []
    return [(m.start() + len(m.group()) / 2, f"{int(m.group(1)):02d}:{m.group(2)}-{int(m.group(3)):02d}:{m.group(4)}")
            for m in ZEIT.finditer(text) if (m.group(1), m.group(2)) != (m.group(3), m.group(4))]   # "13:15-13:15" ist kein Fenster


def _naechste(pos, spalten):
    return min(spalten, key=lambda s: abs(s[0] - pos))


def jahr_lesen(text: str, url: str = "") -> int | None:
    """Jahr der Hochlastzeitfenster: aus Überschrift/Dateiname; das späteste genannte Gültigkeitsjahr."""
    kopf = " ".join([z for z in text.splitlines() if z.strip()][:30]) + " " + url.rsplit("/", 1)[-1]
    jahre = [int(j) for j in re.findall(r"(?<!\d)(20[2-3]\d)(?!\d)", kopf)]
    hlzf_jahre = [int(m.group(1)) for m in re.finditer(r"(?:hochlast\w*|hlzf|hlf)\D{0,40}(20[2-3]\d)", kopf, re.I)]
    if hlzf_jahre:
        return max(hlzf_jahre)
    return max(jahre) if jahre else None


def _jz_kopf(zeilen, i):
    """Jahreszeiten-Spalten aus Zeile i und den Nachbarzeilen ohne Uhrzeiten ("Winter" eine Zeile höher)."""
    spalten = {}
    for k in range(max(0, i - 2), min(len(zeilen), i + 3)):
        if ZEIT.search(zeilen[k]):
            continue
        for m in JZ_WORT.finditer(zeilen[k]):
            spalten.setdefault(_jz(m.group()), m.start() + len(m.group()) / 2)
    return [(p, jz) for jz, p in spalten.items()]


def _label(z: str) -> str:
    """Erste Spalte einer Zeile ohne Uhrzeiten und Striche."""
    erst = re.split(r"\s{3,}", z.strip())[0]
    return "" if ZEIT.match(erst) or KEIN.fullmatch(erst.strip()) else erst


def _form_a(zeilen):
    """Jahreszeiten als Spalten. Rückgabe {ebene: {jz: [fenster]}} oder {}."""
    out = {}
    koepfe = [i for i, z in enumerate(zeilen)
              if not ZEIT.search(z) and len(JZ_WORT.findall(z)) >= 3 and len(_jz_kopf(zeilen, i)) == 4]
    for n, i in enumerate(koepfe):
        if n and i - koepfe[n - 1] <= 2:
            continue                                    # derselbe Kopf über zwei Zeilen
        spalten = _jz_kopf(zeilen, i)
        # Ebene über der Tabelle ("Netzebene NS", "Umspannebene MS/NS")
        tab_ebene = None
        for k in range(max(0, i - 3), i):
            if zeilen[k].strip() and not ZEIT.search(zeilen[k]) and EBENE_WORT.search(zeilen[k]) and not JZ_WORT.search(zeilen[k]):
                tab_ebene = _ebene_text(re.sub(r"^\s*(?:netz|umspann)ebene\s*", "", zeilen[k].strip(), flags=re.I)) or "andere"
        ende = next((k for k in koepfe if k > i + 2), min(i + 45, len(zeilen)))
        for k in range(ende - 1, max(i, ende - 4), -1):   # Ebenen-Überschrift der nächsten Tabelle gehört nicht dazu
            if ende < len(zeilen) and zeilen[k].strip() and not ZEIT.search(zeilen[k]) and EBENE_WORT.search(zeilen[k]):
                ende = k
        # Blöcke: zusammenhängende Zeilen (eine Ebene, deren Bezeichnung um die Zeiten herum umbrochen sein kann)
        bloecke, block = [], []
        for j in range(i + 1, ende):
            if zeilen[j].strip():
                block.append(zeilen[j])
            elif block:
                bloecke.append(block)
                block = []
        if block:
            bloecke.append(block)
        for block in bloecke:
            labels = [_label(z) for z in block]
            mit_ebene = [l for l in labels if l and EBENE_WORT.search(l)]
            if len(mit_ebene) >= 2 and len({_ebene_text(l) for l in mit_ebene}) >= 2:
                zuordnung, aktuell = [], None   # mehrere Ebenen im Block: zeilenweise
                for z, l in zip(block, labels):
                    if l and EBENE_WORT.search(l):
                        aktuell = _ebene_text(l) or "andere"
                    zuordnung.append((z, aktuell))
            else:
                eb = _ebene_text(" ".join(l for l in labels if l)) if mit_ebene else None
                eb = eb or (tab_ebene if not mit_ebene else "andere")
                zuordnung = [(z, eb) for z in block]
            for z, eb in zuordnung:
                if eb in (None, "andere"):
                    continue
                for pos, f in _zeiten(z):
                    _, jz = _naechste(pos, spalten)
                    out.setdefault(eb, {}).setdefault(jz, []).append(f)
    for eb in out:
        for jz in JAHRESZEITEN:
            out[eb].setdefault(jz, [])
    return out


def _form_b(zeilen, erg: Hlzf):
    """Ebenen als Spalten, Jahreszeiten als Zeilen; Zeilen "Erheblichkeitsschwelle" / "Mindestverlagerung"."""
    for i, z in enumerate(zeilen):
        if ZEIT.search(z):
            continue
        teile = [(m.start(), m.group()) for m in re.finditer(r"\S+(?:\s\S+)*", z)]
        eb_teile = [(p, t) for p, t in teile if EBENE_WORT.search(t)]
        if len(eb_teile) < 2:
            continue
        # Fortsetzung des Spaltenkopfs in der nächsten Zeile ("Umspannung" / "MS/NS")
        if i + 1 < len(zeilen) and not ZEIT.search(zeilen[i + 1]) and not JZ_WORT.search(zeilen[i + 1]):
            for m in re.finditer(r"\S+(?:\s\S+)*", zeilen[i + 1]):
                k = min(range(len(eb_teile)), key=lambda n: abs(eb_teile[n][0] - m.start()))
                if abs(eb_teile[k][0] - m.start()) <= 8:
                    eb_teile[k] = (eb_teile[k][0], eb_teile[k][1] + " " + m.group())
        spalten = [(p + len(t) / 2, _ebene_text(t) or "andere") for p, t in eb_teile]
        if not any(s in ("NS", "MSNS") for _, s in spalten):
            continue
        out, jz = {}, None
        bloecke, block = [], []
        for j in range(i + 1, min(i + 40, len(zeilen))):
            if zeilen[j].strip():
                block.append(zeilen[j])
            elif block:
                bloecke.append(block)
                block = []
        if block:
            bloecke.append(block)
        for block in bloecke:
            # Jahreszeit steht teils mittig zwischen ihren Uhrzeiten: alle Zeiten des Blocks gehören zu ihr
            jz_im_block = [_jz(m.group()) for zj in block for m in [JZ_WORT.match(zj.strip())] if m]
            if len(jz_im_block) == 1:
                jz = jz_im_block[0]                     # eine Jahreszeit: gilt für den ganzen Block
            elif jz_im_block:
                jz = jz_im_block[0]                     # mehrere: Zeiten vor der ersten gehören zur ersten, dann zeilenweise
            for zj in block:
                if re.match(r"\s*erheblichkeit", zj, re.I):
                    for mm in re.finditer(r"(\d{1,2})\s*(?:%|prozent)", zj, re.I):
                        _, eb = _naechste(mm.start(), spalten)
                        if eb in ("NS", "MSNS"):
                            erg.schwelle[eb] = int(mm.group(1))
                    continue
                if re.match(r"\s*mindest", zj, re.I):
                    for mm in re.finditer(r"(\d{2,4})\s*kw", zj, re.I):
                        _, eb = _naechste(mm.start(), spalten)
                        if eb in ("NS", "MSNS"):
                            erg.mindest_kw[eb] = int(mm.group(1))
                    continue
                m = JZ_WORT.match(zj.strip())
                if m and len(jz_im_block) > 1:
                    jz = _jz(m.group())
                if jz is None:
                    continue
                for pos, f in _zeiten(zj):
                    _, eb = _naechste(pos, spalten)
                    if eb in ("NS", "MSNS"):
                        out.setdefault(eb, {}).setdefault(jz, []).append(f)
        if out or jz:
            for _, eb in spalten:
                if eb in ("NS", "MSNS"):
                    for s in JAHRESZEITEN:
                        out.setdefault(eb, {}).setdefault(s, [])
            if any(v for e in out.values() for v in e.values()):
                return out
    return {}


def _form_d(zeilen):
    """Eine Zeile je Ebene und Jahreszeit untereinander ("MS   Frühling   13:15 – 14:45").

    Steht die Ebene in derselben Zeile wie eine Jahreszeit, gilt sie bis zur nächsten Ebene (Filstal); steht sie
    allein, mittig zwischen ihren Jahreszeiten, gilt die nächstgelegene Ebene (Duderstadt)."""
    erste = next((i for i, z in enumerate(zeilen) if JZ_WORT.search(z) and ZEIT.search(z)), None)
    if erste is None:
        return {}
    # Kopfzeile "Netzebene  Jahreszeit  Zeitraum" kurz vor der ersten Zeile mit Jahreszeit und Uhrzeit, sonst 4 Zeilen davor
    kopf = next((i for i in range(erste - 1, max(-1, erste - 10), -1)
                 if re.search(r"jahreszeit|saison", zeilen[i], re.I)), max(0, erste - 4))
    bereich = list(range(kopf + 1, min(kopf + 80, len(zeilen))))
    marken = {}                                          # Zeilenindex → (ebene, allein?)
    for i in bereich:
        erst = _label(zeilen[i])
        teile = re.split(r"\s{2,}", zeilen[i].strip())
        if erst and EBENE_WORT.search(erst) and not JZ_WORT.match(erst):
            marken[i] = (_ebene_text(erst) or "andere", not JZ_WORT.search(" ".join(teile[1:2])))
    if not marken:
        return {}
    out, aktuell = {}, None
    for i in bereich:
        z = zeilen[i]
        if i in marken and not marken[i][1]:
            aktuell = marken[i][0]
        m = JZ_WORT.search(z)
        zeiten = _zeiten(z)
        if not m or not zeiten:
            if m and i in marken:
                aktuell = marken[i][0]
            continue
        allein = [k for k, (e, a) in marken.items() if a and abs(k - i) <= 3]
        eb = marken[i][0] if i in marken else (
            marken[min(allein, key=lambda k: (abs(k - i), k > i))][0] if allein else aktuell)
        if eb in (None, "andere"):
            continue
        out.setdefault(eb, {}).setdefault(_jz(m.group()), []).extend(f for _, f in zeiten)
    for eb in out:
        for jz in JAHRESZEITEN:
            out[eb].setdefault(jz, [])
    return out


def _form_c(zeilen):
    """Ein Fenster für das ganze Jahr: Zeile "Hochlastzeitfenster  10:00 - 15:30  …" und Fortsetzungszeilen."""
    for i, z in enumerate(zeilen):
        if not re.search(r"hochlastzeitfenster|hochlast-?zeit", z, re.I) or not ZEIT.search(z) or JZ_WORT.search(z):
            continue
        umfeld = " ".join(zeilen[max(0, i - 8):i + 10])
        if re.search(r"modul\s*3|standardlast\w*zeit|niedriglast\w*zeit|quartal|tarifstufe|§\s*14\s*a", umfeld, re.I):
            continue                                    # zeitvariable Netzentgelte (Modul 3), keine Hochlastzeitfenster
        fenster = [f for _, f in _zeiten(z)]
        for j in range(i + 1, min(i + 6, len(zeilen))):
            zj = zeilen[j]
            if re.search(r"[a-zäöü]{4,}", zj, re.I) and not ZEIT.match(zj.strip()):
                break
            fenster += [f for _, f in _zeiten(zj)]
        fenster = list(dict.fromkeys(fenster))
        if fenster:
            return {"NS": {s: fenster for s in JAHRESZEITEN}}
    return {}


def schwellen_text(text: str, erg: Hlzf):
    """Schwellen aus Fließtext: "MS 20 Prozent, MS/NS 30 Prozent, NS 30 Prozent und 100 kW überschreiten"."""
    for m in re.finditer(r"(ms\s*/\s*ns|umspannung\s+(?:mittel|ms)[^\d%]{0,30}?|niederspannung|\bns\b)\s*:?\s*(\d{1,2})\s*(?:%|prozent)",
                         text, re.I):
        eb = "MSNS" if re.match(r"ms\s*/|umspann", m.group(1), re.I) else "NS"
        erg.schwelle.setdefault(eb, int(m.group(2)))
    m = re.search(r"(\d{2,4})\s*kw\s+(?:überschreiten|übersteigen)", text, re.I)
    if m and "NS" in erg.schwelle:
        erg.mindest_kw.setdefault("NS", int(m.group(1)))


def hlzf_lesen(text: str, url: str = "") -> Hlzf:
    erg = Hlzf(jahr=jahr_lesen(text, url))
    if not re.search(r"hochlast", text, re.I):
        erg.grund = "keine Hochlastzeitfenster im Dokument"
        return erg
    zeilen = text.splitlines()
    gebiete = {m.group(1).strip() for m in re.finditer(r"hochlastzeitfenster[^\n]{0,20}?(?:netzgebiet|netzbereich)\s*:?\s*([^\n]{3,40})", text, re.I)}
    if len(gebiete) > 1:
        erg.grund = "mehrere Netzgebiete im Dokument: " + ", ".join(sorted(gebiete))[:150]
        return erg
    for name, f in (("Jahreszeiten als Spalten", lambda: _form_a(zeilen)),
                    ("Ebenen als Spalten", lambda: _form_b(zeilen, erg)),
                    ("Zeile je Ebene und Jahreszeit", lambda: _form_d(zeilen)),
                    ("ganzjährig", lambda: _form_c(zeilen))):
        out = f()
        if out:
            erg.fenster, erg.form = out, name
            break
    schwellen_text(text, erg)
    if not erg.fenster:
        erg.grund = ("Raster mit markierten Viertelstunden (Markierung nicht im Text)"
                     if re.search(r"1/4-?h-?intervall|viertelstunde", text, re.I) else "Zeitfenster nicht lesbar")
    return erg


SPALTEN = ["nr", "netzbetreiber", "ebene", "jahreszeit", "zeitfenster", "schwelle_prozent", "herkunft_schwelle",
           "mindestleistung_kw", "jahr", "quelle_url"]
EBENE_NAME = {"NS": "Niederspannung", "MSNS": "Umspannung MS/NS"}
JZ_NAME = {"fruehling": "Frühling (März–Mai)", "sommer": "Sommer (Juni–August)", "herbst": "Herbst (September–November)",
           "winter": "Winter (Dezember–Februar)"}


def zeilen(nr, netzbetreiber: str, erg: Hlzf, url: str) -> list[list]:
    """CSV-Zeilen je Ebene und Jahreszeit; leeres Zeitfenster = in dieser Jahreszeit kein Hochlastzeitfenster."""
    out = []
    for eb in ("NS", "MSNS"):
        if eb not in erg.fenster:
            continue
        if eb in erg.schwelle:
            schwelle, herkunft = erg.schwelle[eb], "laut Netzbetreiber"
        else:
            schwelle, herkunft = STANDARD_SCHWELLE[eb], "Standard (fachlich zu bestätigen)"
        for jz in JAHRESZEITEN:
            out.append([nr, netzbetreiber, EBENE_NAME[eb], JZ_NAME[jz], ", ".join(erg.fenster[eb].get(jz, [])) or "keins",
                        schwelle, herkunft, erg.mindest_kw.get(eb, ""), erg.jahr or "", url])
    return out
