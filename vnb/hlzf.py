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

import os
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
                if not ZEIT.search(z) and len(KEIN.findall(re.sub(r"^\s*\S.*?\s{3,}", "", z.strip() + "   ", count=1))) >= 3:
                    out.setdefault(eb, {})              # Ebene mit "kein/-" in allen Spalten: keine Hochlastzeitfenster
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


UHR = re.compile(r"(?<![\d:.])([0-2]?\d):([0-5]\d)(?::00)?(?:\s*uhr)?(?![\d:])(?!\s*h\b)", re.I)     # "02:30 h" ist die Dauer, kein Zeitpunkt


def _paare(z: str):
    """[(pos, "07:45-10:15")] aus Zeiten, die paarweise (von, bis) in einer Zeile stehen, auch ohne Strich dazwischen."""
    ts = [(m.start(), f"{int(m.group(1)):02d}:{m.group(2)}") for m in UHR.finditer(z)]
    if len(ts) < 2 or len(ts) % 2:
        return []
    out = []
    for k in range(0, len(ts), 2):
        if ts[k][1] >= ts[k + 1][1]:
            return []
        out.append(((ts[k][0] + ts[k + 1][0]) / 2, f"{ts[k][1]}-{ts[k + 1][1]}"))
    return out


def _form_e(zeilen):
    """Zeile je Fenster mit Jahreszeit am Zeilenanfang ("Winter 07:45 Uhr 10:15 Uhr", "Herbst 1 06:15 10:15"); Ebene steht als Überschrift darüber."""
    out, eb, jz_alt = {}, None, None
    for z in zeilen:
        st = z.strip()
        if not st:
            continue
        m = JZ_WORT.match(st)
        if not m:
            if jz_alt and _paare(z) and re.match(r"^\s*(?:\d\.?\s{2,}|\d+\s)?\s*[0-2]?\d[:.]", st):
                out.setdefault(eb, {}).setdefault(jz_alt, []).extend(f for _, f in _paare(z))   # Fortsetzungszeile derselben Jahreszeit
                continue
            if EBENE_WORT.search(st) and not UHR.search(st) and len(st) < 90:
                nxt = _ebene_text(EBENE_WORT.search(st).group()) or _ebene_text(st)
                eb, jz_alt = (nxt if nxt in ("NS", "MSNS") else "andere"), None
            continue
        jz = _jz(m.group())
        rest = st[m.end():]
        if eb in (None, "andere"):
            _IGN[0] += len(_paare(rest))
            continue
        zeit = _paare(rest)
        if zeit:
            out.setdefault(eb, {}).setdefault(jz, []).extend(f for _, f in zeit)
            jz_alt = jz
        elif len(KEIN.findall(rest)) >= 1 and not UHR.search(rest):
            out.setdefault(eb, {}).setdefault(jz, [])
            jz_alt = jz
        elif UHR.search(rest):
            return {}                                       # Zeiten in der Zeile, aber nicht als Paar lesbar: lieber nichts als falsch
    _IGN[0] += sum(len(v) for e in out if e not in ("NS", "MSNS") for v in out[e].values())
    return {e: {j: out[e].get(j, []) for j in JAHRESZEITEN} for e in out if e in ("NS", "MSNS")}


def _von_spalten(zeilen, i, spalten):
    """Positionen der vier "von"-Unterspalten unter dem Jahreszeiten-Kopf (genauer als die Mitte des Jahreszeitenworts); sonst None."""
    for k in (i + 1, i + 2):
        if k < len(zeilen):
            v = [m.start() for m in re.finditer(r"\bvon\b", zeilen[k], re.I)]
            if len(v) == 4:
                return [(p, jz) for p, (_, jz) in zip(v, sorted(spalten))]
    return None


def _ordne(z, spalten, von):
    """[(Jahreszeit, "07:45-10:15")] einer Zeile: Beginn der Zeit zählt gegen die "von"-Spalten, sonst Mitte gegen die Jahreszeiten."""
    out = []
    ts = [(m.start(), f"{int(m.group(1)):02d}:{m.group(2)}") for m in UHR.finditer(z)]
    if len(ts) < 2 or len(ts) % 2:
        return out
    for k in range(0, len(ts), 2):
        if ts[k][1] >= ts[k + 1][1]:
            return []
        pos = ts[k][0] if von else (ts[k][0] + ts[k + 1][0]) / 2
        out.append((_naechste(pos, von or spalten)[1], f"{ts[k][1]}-{ts[k + 1][1]}"))
    return out


def _form_f(zeilen):
    """Je Ebene ein Kopf mit vier Jahreszeiten-Spalten (jede "von / bis"), darunter Zeilen mit Zeitpaaren nach Spalte."""
    out = {}
    koepfe = [i for i, z in enumerate(zeilen) if not UHR.search(z) and len(JZ_WORT.findall(z)) == 4]
    for n, i in enumerate(koepfe):
        ende = koepfe[n + 1] if n + 1 < len(koepfe) else min(i + 25, len(zeilen))
        label = re.split(r"\s{3,}", zeilen[i].strip())[0]
        if JZ_WORT.search(label):
            continue
        eb = _ebene_text(label)
        if eb not in ("NS", "MSNS"):
            _IGN[0] += sum(len(_paare(z)) for z in zeilen[i + 1:ende])
            continue
        spalten = [(m.start() + len(m.group()) / 2, _jz(m.group())) for m in JZ_WORT.finditer(zeilen[i])]
        out.setdefault(eb, {j: [] for j in JAHRESZEITEN})
        von = _von_spalten(zeilen, i, spalten)
        for z in zeilen[i + 1:ende]:
            for jz, f in _ordne(z, spalten, von):
                out[eb][jz].append(f)
    return out if any(v for e in out.values() for v in e.values()) or out else {}


def _form_g(zeilen):
    """Ein Kopf mit vier Jahreszeiten-Spalten (von / bis); links die Ebene, Folgezeilen ohne Ebene gehören zur selben Ebene."""
    out = {}
    koepfe = [i for i, z in enumerate(zeilen) if not UHR.search(z) and len(JZ_WORT.findall(z)) == 4]
    for n, i in enumerate(koepfe):
        ende = koepfe[n + 1] if n + 1 < len(koepfe) else min(i + 40, len(zeilen))
        spalten = [(m.start() + len(m.group()) / 2, _jz(m.group())) for m in JZ_WORT.finditer(zeilen[i])]
        eb, leer, zeit_gesehen = None, 0, False
        von = _von_spalten(zeilen, i, spalten)
        for z in zeilen[i + 1:ende]:
            if not z.strip():
                leer += 1
                if leer > 3:
                    break
                continue
            leer = 0
            label = re.split(r"\s{3,}", z.strip())[0]
            if label and not UHR.search(z) and not KEIN.search(z[len(label):]) and eb is not None and zeit_gesehen:
                return {}                                       # Ebenenname allein in einer Zeile zwischen Datenzeilen (mittig gesetzt): Zuordnung unsicher
            zeit_gesehen = zeit_gesehen or bool(UHR.search(z))
            if re.match(r"(?:zu|auf|in|nach)\b", label, re.I):
                label = ""                                      # Fortsetzung der Ebenenbezeichnung ("Umspannung MS" / "zu Niederspannung")
            if label and not UHR.match(label) and not KEIN.fullmatch(label) and EBENE_WORT.search(label) and len(label) < 40:
                tl = _ebene_text(label)
                if re.fullmatch(r"umspann\w*", label.strip(), re.I) and re.search(r"hoch(?:spannung|spannungs)|\bHS\b", "\n".join(zeilen[max(0, i - 6):ende]), re.I):
                    tl = None                                   # "Umspannung" neben Hochspannung: HS/MS oder MS/NS unklar
                eb = tl if tl in ("NS", "MSNS") else "andere"
            elif label and not UHR.match(label) and not KEIN.fullmatch(label) and not re.search(r"\d", label) and len(label) < 40 and eb is None:
                continue
            if eb in (None, "andere"):
                _IGN[0] += len(_paare(z))
                continue
            paare = _paare(z)
            if UHR.search(z) and not paare:
                return {}                                       # Zeiten nicht als von/bis-Paare lesbar: lieber nichts als falsch
            out.setdefault(eb, {j: [] for j in JAHRESZEITEN})
            for jz, f in _ordne(z, spalten, von):
                out[eb][jz].append(f)
    return out


_IGN = [0]          # Fenster anderer Ebenen (HS, HS/MS, MS), die die neuen Formen sehen, aber nicht ausgeben
NEUE_FORMEN = {"Zeile je Fenster", "Ebene mit Jahreszeiten-Spalten (von/bis)", "Ebenen-Zeilen unter Jahreszeiten-Kopf (von/bis)", "Ebenen als Spalten (von/bis)", "Tabelle nach Positionen"}
ZEIT_DOPPELPUNKT = re.compile(r"(?<![\d:.])[0-2]?\d:[0-5]\d(?::\d\d)?(?![\d:])(?!\s*h\b)")
ZEIT_PUNKT = re.compile(r"(?<![\d:.])[0-2]?\d\.([0-5]\d)(?![\d:.])(?!\s*h\b)")
ZEITLIKE = re.compile(r"(?<![\d:.])[0-2]?\d[:.][0-5]\d(?::\d\d)?(?![\d:])(?![.]?\d)(?!\.)(?!\s*h\b)")


def _vollstaendig(text: str, out: dict) -> bool:
    """Absicherung der neuen Formen: Gibt es im Text deutlich mehr Uhrzeiten (auch 9.15 / 08:30:00) als gelesene Fenster, ist etwas übersehen."""
    fenster = sum(len(v) for eb in out.values() for v in eb.values()) + _IGN[0]
    text = "\n".join(z for z in text.splitlines() if not re.search(r"bedeutet|beispiel|entspricht|z\.\s?b\.", z, re.I))   # Erläuterungszeilen mit Beispielzeiten
    alle = len(ZEIT_DOPPELPUNKT.findall(text)) + sum(1 for m in ZEIT_PUNKT.finditer(text) if m.group(1) == "00" or int(m.group(1)) > 12)   # "9.15" zählt, Datum "29.02" nicht
    return alle <= 2 * fenster + 4


def _spaltenname(t: str):
    """Ebene einer Spalte aus ihrem Kopftext: "Mittel-/ Niederspannung" = MSNS, "Niederspannung" = NS, "Mittelspannung" = MS, sonst None."""
    t = re.sub(r"umspann\w*|für entnahmen aus der netzebene|netzebene", " ", t, flags=re.I)
    t = re.sub(r"\s+", " ", t).strip().lower()
    if re.search(r"mittel-?\s*/\s*nieder|ms\s*/\s*ns|mittelspannung\s*/\s*niederspannung", t):
        return "MSNS"
    if re.fullmatch(r"nieder\w*|ns|nsp", t):
        return "NS"
    if re.fullmatch(r"mittelspannung\w*|ms|msp", t):
        return "MS"
    return None


def _form_h(zeilen):
    """Ebenen als Spalten, je Spalte von / bis; Zeilen je Jahreszeit (Folgezeilen ohne Jahreszeit = weitere Fenster derselben Jahreszeit)."""
    out = {}
    for i, z in enumerate(zeilen):
        if UHR.search(z):
            continue
        vb = [(m.start(), m.group().lower()) for m in re.finditer(r"\b(?:von|bis)\b", z, re.I)]
        if len(vb) != 6 or [w for _, w in vb] != ["von", "bis"] * 3:
            continue
        pos = [p for p, _ in vb]
        # Ebenen aus den Kopfzeilen darüber: Text, dessen Mitte über dem von/bis-Paar liegt
        namen = []
        for k in range(3):
            lo, hi = pos[2 * k] - 10, pos[2 * k + 1] + 14
            teile = []
            for j in range(max(0, i - 5), i):
                for m in re.finditer(r"\S+(?:[ ]\S+)*", zeilen[j]):
                    if lo <= (m.start() + m.end()) / 2 <= hi:
                        teile.append(m.group())
            namen.append(_spaltenname(" ".join(teile)))
        if None in namen:
            return {}
        jz, leer = None, 0
        for z2 in zeilen[i + 1:]:
            if not z2.strip():
                leer += 1
                if leer > 2:
                    break
                continue
            leer = 0
            m = JZ_WORT.match(z2.strip())
            if m:
                jz = _jz(m.group())
            elif jz is not None and re.search(r"[A-Za-zÄÖÜäöüß]{3,}", z2):
                break                                           # Textzeile: Tabelle zu Ende
            if jz is None:
                continue
            ts = [(mm.start(), f"{int(mm.group(1)):02d}:{mm.group(2)}") for mm in UHR.finditer(z2)]
            idx = {}
            for p_, t_ in ts:
                k = min(range(6), key=lambda n: abs(pos[n] - p_))
                if k in idx:
                    return {}                                   # zwei Zeiten in einer Spalte: unsicher
                idx[k] = t_
            for k in range(3):
                v, b = idx.get(2 * k), idx.get(2 * k + 1)
                if (v is None) != (b is None) or (v and v >= b):
                    return {}
                e = out.setdefault(namen[k], {})
                e.setdefault(jz, [])
                if v:
                    e[jz].append(f"{v}-{b}")
    _IGN[0] += sum(len(v) for e in out if e not in ("NS", "MSNS") for v in out[e].values())
    return {e: {j: out[e].get(j, []) for j in JAHRESZEITEN} for e in out if e in ("NS", "MSNS")}


FUELL = re.compile(r"\b(?:bei|in|aus|der|die|das|dem|den|entnahme|entnahmen|netzebene|spannungsebene|ebene|entnahmestelle|netz|zur|zum|im|am|und)\b|[().:,*]", re.I)


def _ebene_wort(label: str):
    """Ebene aus einer Zeilenbezeichnung: NS, MSNS, MS, HSMS, HS; None, wenn nicht eindeutig oder unvollständig ("Umspannung in")."""
    t = FUELL.sub(" ", label.lower().replace("ö", "oe"))
    t = re.sub(r"\s+", " ", t).strip()
    if not t:
        return None
    umsp = re.search(r"umspann|\busp\b|ms\s*/\s*ns|msp\s*/\s*nsp|mittel-?\s*/\s*nieder|mittelspannung\s*/\s*niederspannung|\bmitt?el\b.*\bnieder", t)
    hoch = re.search(r"hoch|\bhs\b|\bhsp\b", t)
    nied = re.search(r"nieder|\bns\b|\bnsp\b", t)
    mitt = re.search(r"mittel|\bms\b|\bmsp\b", t)
    if umsp and nied and not hoch:
        return "MSNS"
    if umsp and hoch and mitt:
        return "HSMS"
    if umsp:
        return None                                              # "Umspannung" allein: HS/MS oder MS/NS unklar
    if hoch and mitt:
        return "HSMS"
    if hoch:
        return "HS"
    if nied and not mitt:
        return "NS"
    if mitt and not nied:
        return "MS"
    return None


def _form_t(zeilen):
    """Tabelle nach Positionen: Kopf mit vier Jahreszeiten, darunter Zeilen mit Ebenenbezeichnung (auch über mehrere Zeilen) und Zeitfenstern."""
    out = {}
    koepfe = []
    for i, z in enumerate(zeilen):
        if UHR.search(z):
            continue
        w = {_jz(m.group()) for m in JZ_WORT.finditer(z)}
        if len(w) == 4:
            koepfe.append(i)
    for n, i in enumerate(koepfe):
        ende = koepfe[n + 1] if n + 1 < len(koepfe) else min(i + 45, len(zeilen))
        spalten = [(m.start() + len(m.group()) / 2, _jz(m.group())) for m in JZ_WORT.finditer(zeilen[i])]
        links = min(p for p, _ in spalten) - 8
        eb, acc, offen, leer = None, "", [], 0
        titel = " ".join(zeilen[k] for k in range(max(0, i - 3), i) if zeilen[k].strip() and len(zeilen[k]) < 90)

        def abschluss():
            nonlocal offen
            if offen and eb is None:
                raise ValueError
            for jz, f in offen:
                if eb in ("NS", "MSNS"):
                    out.setdefault(eb, {j: [] for j in JAHRESZEITEN})[jz].append(f)
                elif eb:
                    out.setdefault("_andere", {j: [] for j in JAHRESZEITEN})[jz].append(f)
            offen = []
        try:
            for z in zeilen[i + 1:ende]:
                if not z.strip():
                    leer += 1
                    if leer > 3:
                        break
                    continue
                leer = 0
                st = z.strip()
                if not UHR.search(z) and re.search(r"\b(?:von|bis|uhrzeit|beginn|ende|anfang)\b", z, re.I) \
                        and not re.sub(r"\b(?:von|bis|uhrzeit|uhr|beginn|ende|anfang)\b|[-–:\s]", "", z, flags=re.I):
                    continue                                       # Unterkopf "von bis"
                fenster = [(m.start(), m.end(), f"{int(m.group(1)):02d}:{m.group(2)}-{int(m.group(3)):02d}:{m.group(4)}")
                           for m in ZEIT.finditer(z) if (m.group(1), m.group(2)) != (m.group(3), m.group(4))]
                if not fenster:
                    pr = _paare(z)
                    if pr:
                        ts = [m.start() for m in UHR.finditer(z)]
                        fenster = [(ts[2 * k], ts[2 * k + 1] + 5, f) for k, (_, f) in enumerate(pr)]
                    elif UHR.search(z):
                        raise ValueError                           # Zeiten, die sich nicht zu Fenstern ordnen lassen
                erstes = min([a for a, _, _ in fenster] + [len(z)])
                lab = re.split(r"\s{3,}", z[:erstes].strip())[0] if z[:erstes].strip() else ""
                kein = len(KEIN.findall(z[len(lab) + (len(z) - len(z.lstrip())):erstes if fenster else len(z)])) if True else 0
                daten = bool(fenster) or kein >= 2
                if lab and re.search(r"[A-Za-zÄÖÜäöüß]{2,}", lab) and len(lab.split()) <= 8 and (not daten or True) and lab.lower().split()[0] not in ("die", "das", "wenn", "für", "gemäß"):
                    if daten:
                        abschluss(); acc = lab; eb = _ebene_wort(acc)
                    elif eb is None:
                        acc += " " + lab; eb = _ebene_wort(acc)       # Bezeichnung läuft in der nächsten Zeile weiter
                    else:
                        raise ValueError                            # Bezeichnung nach den Daten, schon eindeutig: mittig gesetzt, unsicher
                    if daten and eb is None and offen is not None:
                        pass
                elif not daten and len(z.split()) >= 8:
                    break                                          # Fließtext: Tabelle zu Ende
                if not daten:
                    continue
                if eb is None and not offen and not acc:
                    eb = _ebene_wort(titel)
                for a, b, f in fenster:
                    jz = min(spalten, key=lambda s: abs(s[0] - (a + b) / 2))[1]
                    offen.append((jz, f))
                if eb:
                    abschluss()
                    out.setdefault(eb if eb in ("NS", "MSNS") else "_andere", {j: [] for j in JAHRESZEITEN})
                    if eb in ("NS", "MSNS") or True:
                        pass
            abschluss()
        except ValueError:
            if os.environ.get("HLZF_DEBUG"):
                raise
            return {}
    _IGN[0] += sum(len(v) for v in out.get("_andere", {}).values())
    return {e: out[e] for e in ("NS", "MSNS") if e in out}


def hlzf_lesen(text: str, url: str = "") -> Hlzf:
    erg = Hlzf(jahr=jahr_lesen(text, url))
    _IGN[0] = 0
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
                    ("ganzjährig", lambda: _form_c(zeilen)),
                    ("Ebenen als Spalten (von/bis)", lambda: _form_h(zeilen)),          # spezifischere Formen vor "Zeile je Fenster"
                    ("Ebene mit Jahreszeiten-Spalten (von/bis)", lambda: _form_f(zeilen)),
                    ("Ebenen-Zeilen unter Jahreszeiten-Kopf (von/bis)", lambda: _form_g(zeilen)),
                    ("Zeile je Fenster", lambda: _form_e(zeilen)),
                    ("Tabelle nach Positionen", lambda: _form_t(zeilen))):
        _IGN[0] = 0
        out = f()
        if out and name in NEUE_FORMEN and not _vollstaendig(text, out):
            erg.grund = "Zeiten im Dokument nicht vollständig gelesen"
            out = {}
        if out:
            erg.fenster, erg.form = out, name
            break
    schwellen_text(text, erg)
    if not erg.fenster and not erg.grund:
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
