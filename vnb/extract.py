"""Auslesen der RLM-Netzentgelte (Jahresleistungspreissystem) aus Preisblättern, ohne KI.

Eingabe ist ein PDF (Text über ``pdftotext -layout``, Fallback pdfplumber) oder eine
Excel-Datei (xlsx/xls). Excel wird in denselben spaltentreuen Textauszug übersetzt,
damit nur ein Parser nötig ist.

Prinzip:
  1. Text zeilenweise lesen, Abschnitte "Jahresleistungspreissystem" erkennen
     (Kopf mit 2.500 h bzw. Jahresbenutzungsdauer) und bei Monatsleistungspreis,
     "ohne Leistungsmessung", § 14a usw. wieder verlassen.
  2. In diesen Abschnitten die Zeilen Niederspannung und Umspannung MS/NS suchen.
  3. Die Zahlen einer Zeile über die Spaltenposition den Kopf-Einheiten
     (€/kW/a bzw. ct/kWh) und den Grenzen (< 2.500 / ≥ 2.500) zuordnen.
     Lässt sich die Reihenfolge nicht aus dem Kopf bestimmen, wird nicht geraten,
     sondern der Fall als unklar markiert.
"""
from __future__ import annotations

import re
from urllib.parse import unquote
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

FELDER = ["lp_unter_2500", "ap_unter_2500", "lp_ueber_2500", "ap_ueber_2500"]

ZAHL = re.compile(r"(?<![\d.,])-?\d{1,3}(?:\.\d{3})*,\d{1,12}(?![\d,])")
LP_EINHEIT = re.compile(r"(?:€|eur(?:o)?|euro)\s*(?:/|pro\b|je\b)\s*\(?\s*kw(?!h)(?:\s*(?:/|\*|·|\s|pro|je|und|x)\s*)*"
                        r"(a\b|jahr|tag|d\b|monat|mon\b)?\)?", re.I)
AP_EINHEIT = re.compile(r"(ct|cent|€|eur(?:o)?)\s*(?:/|pro\b|je\b)\s*kwh", re.I)
GRENZE_UNTER = re.compile(r"(<|≤|<=|unter|bis|kleiner|weniger)\s*(?:als\s*|zu\s*|einschlie(?:ß|ss)lich\s*|einschl\.\s*)?"
                          r"2[.\s]?500", re.I)
GRENZE_UEBER = re.compile(r"(≥|>\s*=|>|über|ueber|ab|größer|groesser|mindestens|oberhalb|mehr)\s*(?:als\s*)?2[.\s]?500", re.I)

FIKTIV = re.compile(r"fiktiv|ohne\s+(?:berücksichtigung\s+des\s+)?(?:\w+\s+)?zuschuss|informationszweck", re.I)
START = re.compile(r"jahresleistungspreis|jahresbenutzungsdauer|benutzungsdauer|benutzungsstunden|"
                   r"2[.]?500\s*(h|std|stunden|bh\b)", re.I)
STOP = re.compile(
    r"monatsleistungspreis|ohne\s+leistungsmessung|ohne\s+registrierende|standardlastprofil|"
    r"§\s*14\s*a|modul\s*[123]|blindarbeit|blindstrom|messstellenbetrieb|messstellenentgelt|"
    r"singul[äa]r|§\s*19|reservekapazit|reserveleistung|einspeis|konzessionsabgabe|"
    r"kwkg|offshore|stromsteuer|sonderformen|pauschal|fiktiv|ohne\s+(?:berücksichtigung\s+des\s+)?zuschuss|"
    r"informationszweck", re.I)
BRUTTO = re.compile(r"\bbrutto\b|inkl(?:usive|\.)?\s*(?:der\s*)?(?:gesetzl(?:ichen|\.)?\s*)?(?:umsatzsteuer|ust|mwst)", re.I)
AUSSCHLUSS_LABEL = re.compile(r"14\s*a|steuerbar|wärmepumpe|waermepumpe|speicher|ladeeinricht|ladepunkt|"
                              r"nachtstrom|schwachlast|ohne|monat|grundpreis|blind", re.I)


@dataclass
class Ergebnis:
    ns: dict = field(default_factory=dict)        # FELDER -> float
    msns: dict = field(default_factory=dict)
    ms: dict = field(default_factory=dict)       # Mittelspannung (Netzebene 5), nur aus Tabellenzeilen gelesen
    hsms: dict = field(default_factory=dict)     # Umspannung HS/MS (Netzebene 4), optional
    hinweise: list = field(default_factory=list)
    unklar: list = field(default_factory=list)    # Gründe, die eine Prüfung erfordern
    preisstand: str = "unklar"
    stand_datum: str = ""
    jahre: set = field(default_factory=set)
    gueltig_jahre: set = field(default_factory=set)
    kopf_jahre: set = field(default_factory=set)
    text: str = ""
    grenze_le: bool = False                        # "≤ 2.500 / > 2.500" statt "< / ≥"
    tageswerte: bool = False
    slp: dict = field(default_factory=dict)        # "ap" (ct/kWh), "gp" (€/a)
    slp_unklar: list = field(default_factory=list)
    slp_hinweise: list = field(default_factory=list)

    @property
    def ns_vollstaendig(self):
        return all(self.ns.get(k) is not None for k in FELDER)


# ---------------------------------------------------------------- Textauszug

def text_aus_datei(pfad: Path) -> list[str]:
    """Liefert eine Liste von Seiten (bzw. Tabellenblättern) als spaltentreuen Text."""
    if pfad.suffix.lower() == ".html":      # Preistabelle aus einer Webseite (vom Crawler als Text abgelegt)
        return [pfad.read_text(encoding="utf-8", errors="replace")]
    daten = pfad.read_bytes()[:8]
    if daten.startswith(b"%PDF"):
        return pdf_seiten(pfad)
    if daten.startswith(b"PK"):
        return xlsx_seiten(pfad)
    if daten.startswith(b"\xd0\xcf\x11\xe0"):
        return xls_seiten(pfad)
    raise ValueError("unbekanntes Dateiformat")


def pdf_seiten(pfad: Path) -> list[str]:
    if shutil.which("pdftotext"):
        try:
            out = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(pfad), "-"],
                                 capture_output=True, timeout=120, check=True).stdout.decode("utf-8", "replace")
            seiten = out.split("\f")
            if sum(len(s.strip()) for s in seiten) > 100:
                return seiten
        except Exception:
            pass
    import pdfplumber
    with pdfplumber.open(str(pfad)) as pdf:
        return [(p.extract_text(layout=True) or "") for p in pdf.pages[:40]]


SPALTE = 18


def _zelle(v) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, (int, float)):
        if float(v).is_integer() and abs(v) >= 1000:
            return f"{int(v)}"
        s = f"{float(v):.6f}".rstrip("0")
        if s.endswith("."):
            s += "0"
        return s.replace(".", ",")
    return " ".join(str(v).split())


def _zeilen_als_text(zeilen) -> str:
    out = []
    for zeile in zeilen:
        teile = ""
        for i, v in enumerate(zeile):
            s = _zelle(v)
            if not s:
                continue
            pos = i * SPALTE
            if len(teile) < pos:
                teile += " " * (pos - len(teile))
            elif teile:
                teile += "  "
            teile += s
        out.append(teile.rstrip())
    return "\n".join(out)


def xlsx_seiten(pfad: Path) -> list[str]:
    import openpyxl
    wb = openpyxl.load_workbook(str(pfad), data_only=True, read_only=True)
    seiten = []
    for ws in wb.worksheets:
        seiten.append(_zeilen_als_text(ws.iter_rows(values_only=True, max_row=3000, max_col=40)))
    wb.close()
    return seiten


def xls_seiten(pfad: Path) -> list[str]:
    import xlrd
    wb = xlrd.open_workbook(str(pfad))
    return [_zeilen_als_text([[c.value for c in r] for r in ws.get_rows()]) for ws in wb.sheets()]


# ---------------------------------------------------------------- Hilfen

def de_zahl(s: str) -> float:
    return float(s.replace(".", "").replace(",", "."))


def norm(s: str) -> str:
    s = s.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, b)
    return s


def einheit_nach(text: str):
    """("LP"|"AP", faktor), wenn text (direkt hinter einer Zahl) mit einer Preiseinheit beginnt."""
    t = text[:16]
    m = re.match(r"\s*" + LP_EINHEIT.pattern, t, re.I)
    if m:
        per = (m.group(1) or "a").lower()
        if per.startswith("mon"):
            return None
        return ("LP", 365.0 if per in ("tag", "d") else 1.0)
    m = re.match(r"\s*" + AP_EINHEIT.pattern, t, re.I)
    if m:
        return ("AP", 1.0 if m.group(1).lower() in ("ct", "cent") else 100.0)
    return None


def ohne_spannung(zeile: str) -> str:
    """Maskiert Spannungsangaben wie "0,4 kV", damit sie nicht als Preis gelten."""
    return re.sub(r"\d+,\d+(?=\s*kV(?![a-zA-Z]))", lambda m: "x" * len(m.group()), zeile)


def zahlen_mit_pos(zeile: str):
    """(mittlere Position, Wert, Start, Einheit direkt dahinter oder None) je Zahl der Zeile."""
    zeile = ohne_spannung(zeile)
    return [(m.start() + len(m.group()) / 2, de_zahl(m.group()), m.start(), einheit_nach(zeile[m.end():]))
            for m in ZAHL.finditer(zeile)]


MWST = 1.19


def ist_brutto(netto: float, brutto: float) -> bool:
    if netto < 0 and brutto < 0:                    # Reduzierungen (§ 14a Modul 1) netto/brutto
        netto, brutto = -netto, -brutto
    return netto > 0 and abs(brutto - round(netto * MWST, 2)) <= 0.011 + 0.0005 * brutto


def ohne_brutto(zahlen):
    """Entfernt Bruttowerte, wenn die Zeile aus Paaren (netto, netto × 1,19) besteht."""
    if len(zahlen) >= 2 and len(zahlen) % 2 == 0 and all(
            ist_brutto(zahlen[i][1], zahlen[i + 1][1]) for i in range(0, len(zahlen), 2)):
        return zahlen[0::2]
    return zahlen


def label_von(zeile: str) -> str:
    zeile = ohne_spannung(zeile)
    m = ZAHL.search(zeile)
    return (zeile[: m.start()] if m else zeile).strip()


def ebene_mshs(label: str) -> str | None:
    """Mittelspannung (MS) und Umspannung HS/MS (HSMS) für Tabellenzeilen. Getrennt von ebene(), damit die übrigen Leser
    (die Mittelspannung bewusst ausblenden) unverändert bleiben."""
    lab = norm(re.sub(r"^\s*[n▪■●◼]\s+(?=[A-ZÄÖÜ])", "", label))
    lab = re.sub(r"^[\d.)\s\-–•▪■●]+", "", lab)
    lab = re.sub(r"\s*/\s*", "/", lab)
    lab = re.sub(r"[()]", " ", lab).replace("-/", "/").replace("- ", "")
    lab = re.sub(r"\s+", " ", lab).strip()
    lab = re.sub(r"(?<=[a-zäöüß])\d{1,2}\*?$", "", lab)
    if not lab or len(lab) > 70 or AUSSCHLUSS_LABEL.search(lab):
        return None
    if re.search(r"hs/ms|hoch\w*/mittel|umspann\w*\s*(hs|hoch)|netz(ebene|bereich)\s*4\b|^ne\s*4\b", lab):
        return "HSMS"
    if re.search(r"nieder|\bns\b|ms/ns|umspann|hoch", lab):
        return None
    if re.search(r"^(netz(ebene|bereich)\s*5\s*)?mittelspannung(?:s?ebene)?\b|^\(?msp?\)?$|^ne\s*5\b|^netz(ebene|bereich)\s*5\b", lab):
        return "MS"
    return None


def ebene(label: str) -> str | None:
    """Ordnet ein Zeilenlabel der Ebene NS bzw. MSNS zu (sonst None)."""
    # Aufzählungszeichen aus Symbolschriften erscheinen im Textauszug als "n " (Abita, Alliander)
    label = re.sub(r"^\s*[n▪■●◼]\s+(?=[A-ZÄÖÜ])", "", label)
    lab = norm(label)
    lab = re.sub(r"^[\d.)\s\-–•▪■●]+", "", lab)
    lab = re.sub(r"\s*/\s*", "/", lab)
    lab = re.sub(r"\s*-\s*/", "/", lab)
    lab = lab.replace("-/", "/").replace("- ", "")
    lab = re.sub(r"\s+", " ", re.sub(r"[()]", " ", lab)).strip()     # "Umspannung (MSP/NSP)"
    lab = re.sub(r"(?<=[a-zäöüß])\d{1,2}\*?$", "", lab)                 # Fußnote "Niederspannung2)"
    if not lab or AUSSCHLUSS_LABEL.search(lab):
        return None
    if len(lab) > 70:
        return None
    m_bereich = re.match(r"netzbereich\s*([1-7])\b", lab)    # "(Netzbereich 7) >= 2.500 h/a" (Miltenberg)
    if m_bereich:
        return {"7": "NS", "6": "MSNS"}.get(m_bereich.group(1))
    if re.search(r"umspann\w*\s*\d+\s*(kv)?\s*/\s*(0[,x.]4|x{3})|ms/ns|mittel/nieder|mittelspannung/niederspannung|mittel(spannung)?\s*(und|zu|auf)\s*nieder|"
                 r"umspann\w*\s*(ms|mittel)\w*\s*/?\s*(ns|nieder)|umspann\w*\s*(zur\s*|in\s*(die\s*)?|auf\s*(die\s*)?)?nieder|"
                 r"umspann\w*.*\bns\b", lab):
        return "MSNS"
    if re.fullmatch(r"umspannung\*?", lab):         # nur "Umspannung" zwischen Mittel- und Niederspannung (EW Geiger)
        return "MSNS"
    if re.search(r"hoch|hs/|mittelspannung(?!.*nieder)|\bms\b(?!/)", lab):
        return None
    kern = re.sub(r"^(?:(?:anschluss|entnahme)(?:\s+und\s+(?:anschluss|entnahme))?\s+(?:direkt\s+)?"
                  r"(?:aus|in|an|im|am)?\s*(?:der|dem|die)?\s*|(?:netz|spannungs)ebene\s*:?\s*)", "", lab)
    if re.search(r"^(netzebene\s*7\s*)?niederspannung(?:s?ebene)?\b|^\(?nsp?\)?$|^ne\s*7\b|^netzebene\s*7\b|niederspannungsnetz|"
                 r"^(7\s*)?niederspannung(?:s?ebene)?\b", kern) or re.search(r"^(ne|netzebene)\s*7\b", lab):
        return "NS"
    return None


@dataclass
class Kopf:
    einheiten: list = field(default_factory=list)   # (pos, "LP"/"AP", faktor)
    worte: list = field(default_factory=list)       # (pos, "LP"/"AP")
    grenzen: list = field(default_factory=list)     # (pos, "unter"/"ueber", zeile_idx)
    brutto: bool = False
    monats_ab: float | None = None                  # Spalten ab hier gehören zum Monatsleistungspreissystem
    datenzeilen: list = field(default_factory=list) # Zeilenindizes mit Werten innerhalb des Kopfbereichs


def _ergaenzen(spalten: list, zeilen_einzel: list) -> list:
    """Spaltenköpfe über zwei Zeilen verteilt (Leistungspreis-Einheiten in einer, Arbeitspreis-Einheiten in der
    anderen Zeile): ergänzt 3 + 1 bzw. 2 + 2 Köpfe an freien Stellen zu vier Spalten."""
    if len(spalten) not in (2, 3):
        return spalten
    for gruppe in zeilen_einzel:
        if len(spalten) + len(gruppe) == 4 and all(abs(e[0] - s[0]) > 8 for e in gruppe for s in spalten):
            return sorted(spalten + gruppe)
    return spalten


def kopf_lesen(zeilen: list[str], von: int, bis: int, erg: Ergebnis) -> Kopf:
    """Sammelt Kopfinformationen aus den Zeilen [von, bis) eines Abschnitts."""
    k = Kopf()
    beste_einheiten = []
    einzel_einheiten, einzel_worte = [], []     # Kopf über zwei Zeilen: "Leistungspreis pro" / "Arbeitspreis  Leistungspreis  Arbeitspreis"
    # Spaltenköpfe (Einheiten, "Leistungspreis/Arbeitspreis") stehen teils über der Startzeile
    vor = von
    while vor > 0 and von - vor < 6:
        z = zeilen[vor - 1]
        if ZAHL.search(ohne_spannung(z)) or STOP.search(z) or FIKTIV.search(z):
            break
        vor -= 1
    for i in range(vor, bis):
        z = zeilen[i]
        if ZAHL.search(z) and ebene(label_von(z)):
            k.datenzeilen.append(i)
            continue
        einh = []
        for m in LP_EINHEIT.finditer(z):
            per = (m.group(1) or "a").lower()
            if per.startswith("mon"):
                continue
            faktor = 365.0 if per in ("tag", "d") else 1.0
            einh.append((m.start() + len(m.group()) / 2, "LP", faktor))
        for m in AP_EINHEIT.finditer(z):
            faktor = 1.0 if m.group(1).lower() in ("ct", "cent") else 100.0
            einh.append((m.start() + len(m.group()) / 2, "AP", faktor))
        # Einheiten aus Zeilen mit Zahlen ("(informatorisch) (15,07 €/kW*Jahr)") ersetzen keinen Spaltenkopf
        if len(einh) >= 2 and not (beste_einheiten and ZAHL.search(ohne_spannung(z))):
            beste_einheiten = sorted(einh)
        if len(einh) in (1, 2) and not ZAHL.search(ohne_spannung(z)):
            einzel_einheiten.append(sorted(einh))
        wl = re.compile(r"leistungs-?\s*preis|\blp\b", re.I)
        wa = re.compile(r"arbeits-?\s*preis|\bap\b", re.I)
        worte = [(m.start() + len(m.group()) / 2, "LP") for m in wl.finditer(z)]
        worte += [(m.start() + len(m.group()) / 2, "AP") for m in wa.finditer(z)]
        if len(worte) >= 2:
            k.worte = sorted(worte)
        if len(worte) in (1, 2) and not ZAHL.search(ohne_spannung(z)):
            einzel_worte.append(sorted(worte))
        g = [(m.start() + len(m.group()) / 2, "unter", i) for m in GRENZE_UNTER.finditer(z)]
        g += [(m.start() + len(m.group()) / 2, "ueber", i) for m in GRENZE_UEBER.finditer(z)]
        if [x[1] for x in g] == ["unter"]:
            # "< 2.500 h/a   2.500 h/a": das Zeichen ≥ fehlt im Textauszug (Sonderzeichen-Schrift)
            belegt = [m.span() for m in GRENZE_UNTER.finditer(z)]
            nackt = [m for m in re.finditer(r"(?<![\d.,])2[.]?500(?=\s*(?:h|std|stunden))", z, re.I)
                     if not any(a <= m.start() < b for a, b in belegt)]
            if len(nackt) == 1 and nackt[0].start() > belegt[0][1]:
                g.append((nackt[0].start() + len(nackt[0].group()) / 2, "ueber", i))
                if "Grenze ab 2.500 h ohne Zeichen ≥ im Textauszug" not in erg.hinweise:
                    erg.hinweise.append("Grenze ab 2.500 h ohne Zeichen ≥ im Textauszug")
        if g:
            if re.search(r"≤|<=|bis\s*(einschl\w*\.?|zu)?\s*2[.\s]?500", z) and re.search(r"(?<![≥>])>(?!=)\s*2[.\s]?500|über|oberhalb", z):
                erg.grenze_le = True
            k.grenzen.extend(g)
        if BRUTTO.search(z):
            k.brutto = True
        if re.search(r"tagesleistungspreis|(€|eur)\s*/\s*\(?\s*kw\s*(/|\*|·)?\s*(tag|d)\b", z, re.I):
            erg.tageswerte = True
    k.einheiten = _ergaenzen(beste_einheiten, einzel_einheiten)
    k.worte = _ergaenzen(k.worte, einzel_worte)
    for i in range(max(0, von - 6), bis):
        z = zeilen[i]
        m_mon = re.search(r"monats(?:leistungs)?preis", z, re.I)
        if m_mon and re.search(r"jahres(?:leistungs)?preis|benutzungsdauer|2[.]?500", z[:m_mon.start()], re.I):
            k.monats_ab = m_mon.start() - 2
    return k


def _naechster(pos, liste):
    return min(liste, key=lambda t: abs(t[0] - pos))


def zuordnen(zahlen, kopf: Kopf, zeilen_grenze: str | None):
    """Ordnet die Zahlen einer Tabellenzeile den Feldern zu.

    Rückgabe: (dict feld->wert, grund_falls_unklar)
    """
    if kopf.monats_ab is not None:
        zahlen = [z for z in zahlen if z[0] < kopf.monats_ab]
        einheiten = [e for e in kopf.einheiten if e[0] < kopf.monats_ab]
    else:
        einheiten = kopf.einheiten
    zahlen = ohne_brutto(sorted(zahlen))
    if not zahlen:
        return {}, "keine Zahlen"
    # Art (LP/AP) und Umrechnungsfaktor je Zahl
    art = []
    inline = [z[3] for z in zahlen if len(z) > 3]
    if len(inline) == len(zahlen) and all(inline):
        # Einheit steht direkt hinter jeder Zahl ("34,10 €/kW  8,33 ct/kWh")
        for (pos, wert, *_), (a, f) in zip(zahlen, inline):
            art.append((a, wert * f, pos))
    elif len(einheiten) == len(zahlen) and not (
            len(kopf.worte) == len(zahlen) and len(zahlen) == 4
            and sorted(e[1] for e in einheiten) != ["AP", "AP", "LP", "LP"]
            and sorted(w[1] for w in kopf.worte) == ["AP", "AP", "LP", "LP"]):
        # gleich viele Einheiten wie Zahlen: Zuordnung über die Reihenfolge der Spalten
        # (nicht bei offensichtlichem Tippfehler in den Einheiten, z. B. "€/kWa" über der Arbeitspreis-Spalte)
        for (pos, wert, *_), (p, a, f) in zip(zahlen, einheiten):
            art.append((a, wert * f, pos))
    elif len(einheiten) > len(zahlen):
        for pos, wert, *_ in zahlen:
            p, a, f = _naechster(pos, einheiten)
            art.append((a, wert * f, pos))
    elif len(kopf.worte) == len(zahlen):
        # Art aus den Spaltenwörtern (Leistungspreis/Arbeitspreis); Faktor von der nächsten Einheit gleicher Art,
        # wenn nur ein Teil der Einheiten lesbar ist ("Leistungspreis€/" + "kWa" auf zwei Zeilen)
        for (pos, wert, *_), (p, a) in zip(zahlen, kopf.worte):
            gleiche = [e for e in einheiten if e[1] == a]
            art.append((a, wert * (_naechster(pos, gleiche)[2] if gleiche else 1.0), pos))
    else:
        return {}, "Spaltenreihenfolge nicht aus Kopfzeile bestimmbar"

    # Grenze je Zahl
    if zeilen_grenze:
        grenzen = [zeilen_grenze] * len(art)
    else:
        g = kopf.grenzen
        arten_g = {x[1] for x in g}
        if arten_g == {"unter", "ueber"}:
            # nur Grenzen aus der letzten Kopfzeile, die beide enthält, sonst alle
            zeilen_beide = [zi for zi in {x[2] for x in g} if {x[1] for x in g if x[2] == zi} == {"unter", "ueber"}]
            if zeilen_beide:
                g = [x for x in g if x[2] == max(zeilen_beide)]
                unter = min(x[0] for x in g if x[1] == "unter")
                ueber = min(x[0] for x in g if x[1] == "ueber")
                # Zahlen nach Position halbieren: linke Hälfte gehört zur links stehenden Grenze
                sortiert = sorted(art, key=lambda t: t[2])
                n = len(sortiert)
                if n % 2:
                    return {}, "ungerade Spaltenzahl"
                links = "unter" if unter < ueber else "ueber"
                rechts = "ueber" if links == "unter" else "unter"
                grenzen_map = {id(t): (links if i < n // 2 else rechts) for i, t in enumerate(sortiert)}
                grenzen = [grenzen_map[id(t)] for t in art]
            elif max(x[2] for x in g) - min(x[2] for x in g) <= 6 and not any(
                    min(x[2] for x in g) < d < max(x[2] for x in g) for d in kopf.datenzeilen):
                # ein Kopf über mehrere Zeilen verteilt ("Benutzungs-" / "dauer < 2500 h/a" / "≥ 2500 h/a"):
                # jede Zahl gehört zur Grenze, die in ihrer Spalte steht
                grenzen = [_naechster(pos, g)[1] for _, _, pos in art]
            else:
                # Grenzen in verschiedenen Kopfzeilen (getrennte Tabellen): die zuletzt genannte gilt
                letzte = max(g, key=lambda x: x[2])
                grenzen = [letzte[1]] * len(art)
        elif len(arten_g) == 1:
            grenzen = [next(iter(arten_g))] * len(art)
        else:
            return {}, "Benutzungsdauer-Grenze nicht im Kopf gefunden"

    out = {}
    for (a, wert, _), gr in zip(art, grenzen):
        feld = f"{a.lower()}_{gr}_2500"
        wert = runden(wert)
        if feld in out and abs(out[feld] - wert) > 1e-9:
            return {}, f"Feld {feld} mehrfach belegt"
        out[feld] = wert
    return out, None


# ---------------------------------------------------------------- Hauptparser

def tabellen_lesen(seiten: list[str]) -> Ergebnis:
    erg = Ergebnis()
    zeilen = []
    for s in seiten:
        zeilen.extend(s.splitlines())
        zeilen.append("")
    erg.text = "\n".join(zeilen)

    funde = {"NS": [], "MSNS": [], "MS": [], "HSMS": []}   # Liste von dicts je Tabelle
    im_abschnitt = False
    start = 0
    offen_label = ""                   # Label einer Zeile ohne Zahlen (Umbruch)
    offen_ebene = None                 # Ebene, deren Zahlen in Folgezeilen stehen
    fiktiv = False                     # Bereich mit fiktiven Entgelten (nur zur Information)
    bereich = []                       # Zeilen in Jahresleistungspreis-Abschnitten
    for i, z in enumerate(zeilen):
        zl = z.strip()
        if not zl:
            continue
        if FIKTIV.search(zl):
            fiktiv, im_abschnitt, offen_ebene = True, False, None
            continue
        if fiktiv:
            if re.match(r"(preisblatt|anlage|kapitel)\s*\d|\d+(\.\d+)*\s+[A-ZÄÖÜ]", zl, re.I):
                fiktiv = False
            else:
                continue
        hat_start = bool(START.search(zl))
        hat_stop = bool(STOP.search(zl)) and not hat_start
        zahlen = zahlen_mit_pos(z)
        if hat_stop and not (zahlen and ebene(label_von(z))):
            im_abschnitt = False
            offen_ebene = None
            continue
        if hat_start and not zahlen:
            if not im_abschnitt:
                start = i
            im_abschnitt = True
            offen_ebene = None
            continue
        if not im_abschnitt:
            continue
        bereich.append(i)
        label = label_von(z)
        eb = ebene(label) or ebene_mshs(label)
        if not eb and offen_label and not offen_ebene and len(label) < 40:
            eb = ebene(offen_label + " " + label) or ebene_mshs(offen_label + " " + label)
        if zahlen and eb:
            kopf = kopf_lesen(zeilen, start, i, erg)
            gr = "unter" if GRENZE_UNTER.search(label) else "ueber" if GRENZE_UEBER.search(label) else None
            werte, grund = zuordnen(zahlen, kopf, gr)
            funde[eb].append({"werte": werte, "grund": grund, "brutto": kopf.brutto, "zeile": i})
            offen_label, offen_ebene = "", None
        elif zahlen and offen_ebene and not label:
            # umbrochener Zeilenname ("Umspannung Mittel-/Niederspan-" / Zahlen / "nung")
            kopf = kopf_lesen(zeilen, start, i, erg)
            werte, grund = zuordnen(zahlen, kopf, None)
            funde[offen_ebene].append({"werte": werte, "grund": grund, "brutto": kopf.brutto, "zeile": i})
            offen_label, offen_ebene = "", None
        elif zahlen and offen_ebene:
            gr = "unter" if GRENZE_UNTER.search(label) else "ueber" if GRENZE_UEBER.search(label) else None
            rest = re.sub(r"(jahres)?benutzungs(dauer|stunden)|\b(bd|t|jbd)\b", " ", GRENZE_TEXT.sub(" ", label), flags=re.I)
            if gr and not rest.strip(" :-–()"):
                # nur reine Grenzzeilen ("≥ 2.500 h/a 110,77 ...") gehören zur offenen Ebene, keine neue Bezeichnung
                kopf = kopf_lesen(zeilen, start, i, erg)
                werte, grund = zuordnen(zahlen, kopf, gr)
                funde[offen_ebene].append({"werte": werte, "grund": grund, "brutto": kopf.brutto, "zeile": i})
            else:
                offen_ebene = None
            offen_label = ""
        elif not zahlen:
            offen_ebene = eb
            offen_label = label if len(label) < 40 else ""
        else:
            offen_label, offen_ebene = "", None

    for eb, ziel in (("NS", erg.ns), ("MSNS", erg.msns)):
        ziel.update(_zusammenfuehren(funde[eb], eb, erg))
        if not ziel:
            werte = bloecke_lesen(zeilen, bereich, eb) or quer_lesen(zeilen, eb) or ebenen_spalten_lesen(zeilen, eb)
            if werte:
                ziel.update(werte)
                erg.unklar = [u for u in erg.unklar if not u.startswith(f"{eb}:")]
                if "Werte aus Zeilenpaaren je Benutzungsdauer gelesen" not in erg.hinweise:
                    erg.hinweise.append("Werte aus Zeilenpaaren je Benutzungsdauer gelesen")
    for eb, ziel in (("MS", erg.ms), ("HSMS", erg.hsms)):          # nur aus Tabellenzeilen; Lücken machen den Fall nicht unsicher
        try:
            ziel.update(_zusammenfuehren(funde[eb], eb, Ergebnis()))
        except Exception:
            pass
    slp_lesen(zeilen, erg)

    # BDEW-Artikel-IDs (1-01-7-001 usw.) sind eindeutig und haben Vorrang vor der Tabellenerkennung
    artikel, gruende = artikel_lesen(zeilen)
    genutzt = False
    for eb, ziel, felder in (("NS", erg.ns, FELDER), ("MSNS", erg.msns, FELDER), ("SLP", erg.slp, ("ap", "gp")),
                             ("MS", erg.ms, FELDER), ("HSMS", erg.hsms, FELDER)):
        werte = artikel.get(eb, {})
        if werte and all(werte.get(f) is not None for f in felder):
            ziel.clear()
            ziel.update(werte)
            genutzt = True
            praefix = "SLP:" if eb == "SLP" else f"{eb}:"
            if eb == "SLP":
                erg.slp_unklar = [u for u in erg.slp_unklar if not u.startswith(praefix)]
            else:
                erg.unklar = [u for u in erg.unklar if not u.startswith(praefix)]
        elif werte:
            ziel_gruende = [g for g in gruende if (eb == "SLP") == g.startswith("1-02")]
            (erg.slp_unklar if eb == "SLP" else erg.unklar).extend(
                f"{eb} Artikel-ID: {g}" for g in ziel_gruende[:3])
    if genutzt:
        erg.hinweise.append("Werte über BDEW-Artikel-IDs gelesen")
    # getrennte Tabellen "bis zu 2.500" / "mehr als 2.500 Vollbenutzungsstunden": Grenze ≤ 2.500 / > 2.500
    if erg.ns and re.search(r"bis\s+zu\s+2[.\s]?500", erg.text, re.I) and re.search(r"mehr\s+als\s+2[.\s]?500", erg.text, re.I):
        erg.grenze_le = True
    return erg


# ---------------------------------------------------------------- BDEW-Artikel-IDs (PRICAT)

ARTIKEL = re.compile(r"(?<![\d-])1-0([12])-(\d)-(\d{3})(?![\d-])")
ARTIKEL_FELD = {
    ("1", "7", "001"): ("NS", "lp_unter_2500"), ("1", "7", "002"): ("NS", "ap_unter_2500"),
    ("1", "7", "003"): ("NS", "lp_ueber_2500"), ("1", "7", "004"): ("NS", "ap_ueber_2500"),
    ("1", "6", "001"): ("MSNS", "lp_unter_2500"), ("1", "6", "002"): ("MSNS", "ap_unter_2500"),
    ("1", "6", "003"): ("MSNS", "lp_ueber_2500"), ("1", "6", "004"): ("MSNS", "ap_ueber_2500"),
    ("1", "5", "001"): ("MS", "lp_unter_2500"), ("1", "5", "002"): ("MS", "ap_unter_2500"),
    ("1", "5", "003"): ("MS", "lp_ueber_2500"), ("1", "5", "004"): ("MS", "ap_ueber_2500"),
    ("1", "4", "001"): ("HSMS", "lp_unter_2500"), ("1", "4", "002"): ("HSMS", "ap_unter_2500"),
    ("1", "4", "003"): ("HSMS", "lp_ueber_2500"), ("1", "4", "004"): ("HSMS", "ap_ueber_2500"),
    ("2", "0", "001"): ("SLP", "gp"), ("2", "0", "002"): ("SLP", "ap"),
}
BEREICH = {"LP": (0.5, 400.0), "AP": (0.05, 30.0), "GP": (0.0, 500.0)}


def _einheiten_in(text: str):
    """Alle Preiseinheiten eines Textes: (start, ende, art, faktor)."""
    out = []
    for m in LP_EINHEIT.finditer(text):
        per = (m.group(1) or "a").lower()
        if not per.startswith("mon"):
            out.append((m.start(), m.end(), "LP", 365.0 if per in ("tag", "d") else 1.0))
    for m in AP_EINHEIT.finditer(text):
        out.append((m.start(), m.end(), "AP", 1.0 if m.group(1).lower() in ("ct", "cent") else 100.0))
    for m in GP_EINHEIT.finditer(text):
        out.append((m.start(), m.end(), "GP", GP_FAKTOR[m.group(1).lower()]))
    return sorted(out)


def runden(v: float) -> float:
    """Entfernt Umrechnungsrauschen (Tageswert × 365, €/kWh × 100), echte Nachkommastellen bleiben."""
    r2 = round(v, 2)
    return r2 if abs(v - r2) < 0.0005 else round(v, 4)


def _naehe(a: float, b: float) -> bool:
    return abs(a - b) <= max(0.011, 0.006 * max(abs(a), abs(b)))


def artikel_wert(zeile: str, rest: str, art: str):
    """Wert einer Artikel-ID-Zeile in Zieleinheit (LP €/kW/a, AP ct/kWh, GP €/a) oder (None, Grund).

    Alle Zahlen der Zeile werden über die Einheit direkt dahinter (sonst die Einheiten der Zeile)
    umgerechnet; Bruttowerte (× 1,19) und Werte außerhalb des plausiblen Bereichs fallen weg;
    die übrigen müssen übereinstimmen (z. B. 0,051068 €/kW*Tag und 18,64 €/kW/a).
    """
    einh = _einheiten_in(rest)
    faktoren_zeile = {f for _, _, a, f in einh if a == art}
    kandidaten = []
    zahlen = list(ZAHL.finditer(rest))
    for i, m in enumerate(zahlen):
        x = de_zahl(m.group())
        if x <= 0:
            continue
        ende = zahlen[i + 1].start() if i + 1 < len(zahlen) else len(rest)
        direkt = [e for e in einh if m.end() <= e[0] < min(ende, m.end() + 16)]
        start_vorher = zahlen[i - 1].end() if i else 0
        davor = [e for e in einh if max(start_vorher, m.start() - 16) <= e[1] <= m.start()]
        if direkt or davor:
            e = direkt[0] if direkt else davor[-1]
            if e[2] == art:
                kandidaten.append((x * e[3], x))
            continue
        for f in faktoren_zeile or ({1.0} if art != "LP" else set()):
            kandidaten.append((x * f, x))
    lo, hi = BEREICH[art]
    werte = [v for v, _ in kandidaten if lo <= v <= hi]
    werte = [v for v in werte if not any(ist_brutto(w, v) for w in werte if w < v)]
    if not werte:
        return None, "kein Wert"
    if all(_naehe(werte[0], v) for v in werte):
        # bevorzugt der Wert mit wenigen Nachkommastellen (veröffentlichter Preis)
        return runden(min(werte, key=lambda v: len(f"{v:.6f}".rstrip("0")))), None
    return None, "widersprüchliche Werte " + ", ".join(f"{v:.4f}" for v in werte[:4])


def _artikel_spalten(zeilen: list[str], i: int) -> list[str] | None:
    """Zeile nur aus Artikel-IDs ("Artikel-ID  1-01-5-001  1-01-6-001  1-01-7-001"): die Werte stehen
    spaltenweise in einer Zeile darüber, die Einheit ("in €/kW pro Jahr") in der Nähe. Rückgabe je ID
    "Wert Einheit" oder None."""
    z = zeilen[i]
    ids = list(ARTIKEL.finditer(z))
    if len(ids) < 2 or ZAHL.search(ARTIKEL.sub(" ", z)):
        return None
    for k in range(i - 1, max(-1, i - 5), -1):
        werte = list(ZAHL.finditer(zeilen[k]))
        if not werte:
            continue
        if len(werte) != len(ids) or ARTIKEL.search(zeilen[k]):
            return None
        umfeld = range(max(0, k - 2), i)
        if len({e[2] for n in umfeld for e in _einheiten_in(zeilen[n])}) != 1:
            return None                  # genau eine Einheitenart rund um die Wertzeile
        n = min((abs(n - k), n) for n in umfeld if _einheiten_in(zeilen[n]))[1]
        a, b, _, _ = _einheiten_in(zeilen[n])[0]
        return [f"{w.group()} {zeilen[n][a:b]}" for w in werte]
    return None


def artikel_lesen(zeilen: list[str]) -> tuple[dict, list]:
    """Liest NS, MS/NS und SLP über die BDEW-Artikel-IDs. Rückgabe ({ebene: {feld: wert}}, gruende)."""
    gefunden, gruende = {}, []
    for i, z in enumerate(zeilen):
        spalten = _artikel_spalten(zeilen, i)
        for j, m in enumerate(ARTIKEL.finditer(z)):
            key = ARTIKEL_FELD.get(m.groups())
            if not key:
                continue
            eb, feld = key
            art = "GP" if feld == "gp" else "AP" if feld.startswith("ap") else "LP"
            if eb == "SLP" and feld == "ap":
                art = "AP"
            if spalten:
                w, grund = artikel_wert(z, spalten[j], art)
            else:
                w, grund = artikel_wert(z, z[m.end():] + " " + z[:m.start()], art)
            if w is None:
                gruende.append(f"{m.group()}: {grund}")
                continue
            vorher = gefunden.setdefault(eb, {}).get(feld)
            if vorher is not None and not _naehe(vorher, w):
                gruende.append(f"{m.group()}: mehrfach mit abweichenden Werten ({vorher:.4f}, {w:.4f})")
                gefunden[eb][feld] = None
            elif vorher is None and feld not in gefunden[eb]:
                gefunden[eb][feld] = w
    return {eb: {k: v for k, v in d.items()} for eb, d in gefunden.items()}, gruende


# ---------------------------------------------------------------- SLP

SLP_START = re.compile(r"ohne\s+(?:\S{1,20}?[\s-])?(?:leistungsmessung|lastgang)|standardlastprofil|\bslp\b|"
                       r"ohne\s+viertelstunden|entnahme\s+mit\s+lastprofil|"
                       r"entnahme\s+von\s+bis\s+(?:zu\s+)?100\.000\s*kwh", re.I)
SLP_STOP = re.compile(r"mit\s+(?:registrierender\s+)?leistungsmessung|\bmsb\b|jahresleistungspreis|jahresbenutzungsdauer|"
                      r"monatsleistungspreis|blindarbeit|blindstrom|messstellen|messeinrichtung|z[äa]hlerart|konzessionsabgabe|einspeis|"
                      r"reservekapazit|singul[äa]r|§\s*19|kwkg|offshore|umlage|stromsteuer|beispiel|"
                      r"berechnung\s+des|fiktiv|informationszweck", re.I)
SLP_AUSSCHLUSS = re.compile(r"w[äa]rmepumpe|waermepumpe|speicher|14\s*a|modul\s*[123]|unterbrech|steuerbar|"
                            r"nacht|schwachlast|\bnt\b|\bht\b|hochtarif|niedertarif|zweitarif|doppeltarif|"
                            r"zweizeit|schwach|ladeeinricht|ladepunkt|e-?mobil|heizung|mittelspannung|"
                            r"hochspannung|umspann|pausch|reduzier|leistungspreis|kw/a|kw\s*/\s*a|beleuchtung|"
                            r"elektromobil|mobilit|bestand\s*\d?\)|verbrauchseinrichtung|zeitvariabel|tarifstufe|"
                            r"hochlast|niedriglast|niederlast|niedrigtarif|\bkav\b|kommunal|rabatt|mischpreis|"
                            r"=", re.I)
# Sammelzeile "Standardlastprofilkunden, Wärmespeicherheizungen, Wärmepumpen und E-Ladestationen": ein Preis für alle
SLP_SAMMEL = re.compile(r"^\s*(standardlastprofil\w*|slp(-kunden)?\b|haushalt\w*|allgemein\w*)", re.I)
SLP_SAMMEL_NEIN = re.compile(r"schwach|nacht|\bnt\b|\bht\b|tarif|14\s*a|modul|unterbrech|steuerbar|reduzier|pausch|"
                             r"zeitvariabel|spannung|umspann|leistungspreis|=", re.I)
SLP_NEUTRAL = re.compile(r"^\s*(niederspannung|eintarif|standard|allgemein|haushalt|gewerbe)", re.I)
GP_EINHEIT = re.compile(r"(?:€|eur(?:o)?)\s*(?:/|pro\b|je\b)\s*(?:(?:z[äa]hlpunkt|z[äa]hler|zp|messlokation|malo|marktlokation|anschluss|"
                        r"entnahmestelle)\s*(?:/|und|x|je|pro)?\s*)?(a|jahr|tag|d|monat|mon)\b", re.I)
GP_FAKTOR = {"a": 1.0, "jahr": 1.0, "tag": 365.0, "d": 365.0, "monat": 12.0, "mon": 12.0}


def _slp_einheit(text: str):
    """Einheit am Anfang von text: ("AP"|"GP", faktor) oder None."""
    m_ap = AP_EINHEIT.search(text)
    m_gp = GP_EINHEIT.search(text)
    kand = []
    if m_ap:
        kand.append((m_ap.start(), "AP", 1.0 if m_ap.group(1).lower() in ("ct", "cent") else 100.0))
    if m_gp:
        kand.append((m_gp.start(), "GP", GP_FAKTOR[m_gp.group(1).lower()]))
    return min(kand)[1:] if kand else None


def _slp_kopf(zeilen, von, bis):
    """Spalten-Einheiten (pos, art, faktor) aus der letzten Kopfzeile des SLP-Abschnitts."""
    beste, einzel = [], []
    for i in range(von, bis):
        z = zeilen[i]
        if ZAHL.search(z):
            continue
        einh = [(m.start() + len(m.group()) / 2, "AP", 1.0 if m.group(1).lower() in ("ct", "cent") else 100.0)
                for m in AP_EINHEIT.finditer(z)]
        einh += [(m.start() + len(m.group()) / 2, "GP", GP_FAKTOR[m.group(1).lower()]) for m in GP_EINHEIT.finditer(z)]
        if not einh:
            wl = [(m.start() + len(m.group()) / 2, "GP", None) for m in re.finditer(r"grund-?\s*preis", z, re.I)]
            wl += [(m.start() + len(m.group()) / 2, "AP", None) for m in re.finditer(r"arbeits-?\s*preis", z, re.I)]
            if len(wl) >= 2:
                einh = wl
        if len(einh) >= 2:
            beste = sorted(einh)
        elif einh and einh[0][2] is not None:
            einzel.extend(einh)
    # Spalte "pauschale Reduktion" ist kein Preis: deren Einheit entfernen, fehlende aus anderen Kopfzeilen ergänzen
    reduktion = [m.start() + len(m.group()) / 2 for i in range(von, bis)
                 for m in re.finditer(r"reduktion|pauschale", zeilen[i], re.I) if not ZAHL.search(zeilen[i])]
    if reduktion and beste:
        beste = [e for e in beste if all(abs(e[0] - r) > 10 for r in reduktion)]
        for e in einzel:
            if all(abs(e[0] - r) > 10 for r in reduktion) and all(abs(e[0] - b[0]) > 8 for b in beste):
                beste = sorted(beste + [e])
    # Spaltenwörter ohne Einheit: Einheit aus Einzelangaben darunter ("Grundpreis als" / "Tagespreis" / "in EUR/d")
    if beste and any(f is None for _, _, f in beste):
        neu = []
        for pos, art, f in beste:
            gleiche = [e for e in einzel if e[1] == art]
            if f is None and gleiche:
                f = min(gleiche, key=lambda e: abs(e[0] - pos))[2]
            neu.append((pos, art, f))
        beste = neu
    return beste


def slp_lesen(zeilen: list[str], erg: Ergebnis):
    """Standard-Arbeitspreis und Grundpreis Niederspannung für Entnahme ohne Leistungsmessung."""
    werte = {"AP": [], "GP": []}
    zeilen_label = {"AP": [], "GP": []}
    im, start, ausgeschlossen = False, 0, False
    msb_sperre = False                     # nach einer Messstellenbetrieb-Tabelle bis zur nächsten Netzentgelt-Überschrift
    kopf_ausschluss = False                # Ausschluss kam von einem eingerückten Spaltenkopf
    einheit_offen = None                   # Einheit in eigener Zeile ("in ct/kWh") für den Wert darunter
    for i, z in enumerate(zeilen):
        zl = z.strip()
        if not zl:
            continue
        if msb_sperre and re.search(r"netznutzung|netzentgelt|preisblatt", zl, re.I) and not re.search(
                r"messstellen|messeinrichtung|z[äa]hler", zl, re.I):
            msb_sperre = False
        if msb_sperre and not ZAHL.search(z) and re.search(r"grund-?\s*preis", zl, re.I) and re.search(
                r"arbeits-?\s*preis", zl, re.I):
            msb_sperre, im, start, ausgeschlossen = False, True, i, False   # Kopf einer Netzentgelt-Tabelle
            continue
        if (not ZAHL.search(z) and len(zl) < 70 and not zl.endswith((".", ",")) and not re.search(r"gesetz|§", zl)
                and re.search(r"messstellen|messeinrichtung|z[äa]hlerart|messentgelt|messung\s+und\s+abrechnung", zl, re.I)
                and not re.search(r"netznutzung\s+und\s+messstellen", zl, re.I)):   # Seitenkopf beider Preisblätter
            msb_sperre, im = True, False   # Überschrift einer Messstellenbetrieb-Tabelle
            continue
        zahlen = list(ZAHL.finditer(ohne_spannung(z)))   # "0,4 kV" ist kein Preis
        fliesstext = zl[:1].islower()      # umgebrochener Satz, keine Überschrift
        if FIKTIV.search(zl) and not zahlen:
            im = False                     # fiktive Entgelte (nur zur Information)
            continue
        kurz = re.sub(r"\s+", " ", zl)      # Spaltenabstände zählen nicht zur Länge der Überschrift
        if kurz.lower().endswith(" ohne") and i + 1 < len(zeilen):
            kurz += " " + re.split(r"\s{3,}", zeilen[i + 1].strip())[0]    # "1.2 Kunden ohne" / "Leistungsmessung"
        elif (not zahlen and i + 1 < len(zeilen) and re.split(r"\s{3,}", zl)[0].lower().endswith(" ohne")
              and not ZAHL.search(zeilen[i + 1])):
            # "1.2 Kunden ohne      Grundpreis   Arbeitspreis" / "Leistungsmessung3   netto   netto"
            kurz = re.split(r"\s{3,}", zl)[0] + " " + re.split(r"\s{3,}", zeilen[i + 1].strip())[0]
        # lange einspaltige Überschrift "Entnahme ohne registrierende Lastgangmessung - Haushaltsbedarf, …"
        lang_ok = len(re.sub(r"^(?:preisblatt|anlage|tabelle)\s*[\d.]+\s*", "", kurz, flags=re.I)) < 100 or (len(kurz) < 160 and not kurz.endswith(".") and SLP_START.search(kurz[:60])
                                      and len(re.split(r"\s{3,}", zl)) == 1)
        if SLP_START.search(kurz) and not zahlen and not fliesstext and lang_ok and not re.match(r"[•\-–*]", zl):
            if re.search(r"(?:je|pro)\s+z[äa]hler|messstellen|messung\s+inkl|messentgelt|einspeis|"
                         r"mit\s+(?:registrierender\s+)?leistungsmessung", zl, re.I) or msb_sperre:
                # zweispaltiger Kopf "ohne … | mit Leistungsmessung" oder Messstellenbetrieb-Tabelle
                im = False          # z. B. Messstellenbetrieb "ohne Lastgangmessung je Zähler"
                continue
            # nur kurze Überschriften schließen aus, nicht Fließtext ("… pauschalierten Netzentgelt …")
            # Spaltenköpfe in der Überschrift ("… ohne Leistungsmessung | Niedriglasttarif | Hochlasttarif") zählen mit
            im, start, kopf_ausschluss = True, i, False
            spalten = " ".join(re.split(r"\s{3,}", zl)[1:])
            # Überschrift (kein Satz) schließt aus: "Entgelte für unterbrechbare und steuerbare Entnahmestellen ohne …"
            lange_ueberschrift = 70 <= len(kurz) < 130 and not kurz.rstrip().endswith((".", ","))
            ausgeschlossen = (bool(SLP_AUSSCHLUSS.search(kurz)) and len(kurz) < 70
                              or lange_ueberschrift and bool(re.search(   # nur vor "ohne …", nicht "… und Kunden mit steuerbaren"
                                  r"steuerbar|unterbrech|w[äa]rmepumpe|speicher|14\s*a|modul\s*[123]|heizung",
                                  kurz[:SLP_START.search(kurz).start()], re.I))
                              or bool(SLP_AUSSCHLUSS.search(spalten)))
            continue
        if not im:
            continue
        if SLP_STOP.search(zl) and not SLP_START.search(zl):
            im = False
            continue
        if not zahlen:
            erste_spalte = re.split(r"\s{3,}", zl)[0]   # Spaltenköpfe dahinter machen keinen Fließtext
            if fliesstext and (len(erste_spalte) >= 70 or erste_spalte.endswith(".")):
                continue        # umbrochener Fließtext; kurze Zwischenzeilen ("bei unterbrechbaren …") zählen
            if re.match(r"artikel", zl, re.I):
                continue        # "Artikel-ID Elektromobilität   1-02-0-010": Kennung, keine Tarifzeile
            if len(zl) < 30 and _slp_einheit(zl):
                einheit_offen = (_slp_einheit(zl), i)
            # Spaltenkopf "Netz- oder Umspannebene" schließt nichts aus
            zl = re.sub(r"netz-?\s*(?:oder|und|/|bzw\.?|bwz\.?)\s*umspann\w*|^umspannebene\b|"
                        r"^leistungspreissystem\s+f[üu]r\s*:?", " ", zl, flags=re.I).strip()
            # "Entnahmestellen ohne steuerbare oder unterbrechbare Verbrauchseinrichtungen" ist der Standardfall
            naechste = " ".join(zeilen[i + 1:i + 3])
            if re.search(r"(?:bzw\.?|oder|und|/)\s*niederspannung", zl + " " + naechste, re.I):
                # "Umspannung in Niederspannung" / "bzw. Niederspannung": ein Preis für beide (ÜZ Mainfranken)
                zl = re.sub(r"umspann\w*\s+(?:in|zur|auf)\s+(?:die\s+)?niederspannung", " ", zl, flags=re.I).strip()
            if len(z) - len(z.lstrip()) >= 20 or re.search(r"grund-?\s*preis|arbeits-?\s*preis", zl, re.I):
                # Spalten "pauschale Reduktion" / "ohne Kommunalrabatt | mit Kommunalrabatt": kein Tarif
                zl = re.sub(r"pauschale\s*(?:reduktion)?|reduktion|(?:ohne|mit)\s+kommunalrabatt", " ", zl, flags=re.I).strip()
            zl = re.sub(r"ohne\s+(?:steuerbare|unterbrechbare)(?:\s*(?:oder|und|/|,)\s*(?:steuerbare|unterbrechbare))*",
                        " ", zl, flags=re.I).strip()
            if SLP_AUSSCHLUSS.search(zl):
                ausgeschlossen = True
                # weit eingerückter Spaltenkopf ("HT   NT"): betrifft nur Zeilen, die keine Standardzeile sind
                kopf_ausschluss = len(z) - len(z.lstrip()) >= 20 and bool(
                    re.fullmatch(r"(?:(?:ht|nt|hochtarif|niedertarif)\s*\d?\)?\s*)+", zl, re.I))
            elif SLP_NEUTRAL.search(zl) and not SLP_AUSSCHLUSS.search(zl):
                ausgeschlossen = False
            elif len(z) - len(z.lstrip()) < 5 and re.search(
                    r"(?:grundpreis|arbeitspreis|entgelt)\s+f[üu]r\s+(?:die\s+)?netznutzung", zl, re.I):
                ausgeschlossen = False      # neue Zwischenüberschrift "Jährlicher Grundpreis für Netznutzung"
            continue
        label = z[:zahlen[0].start()]
        if re.match(r"\s*brutto|\s*(?:preis\s+)?inkl(?:\.|usive)\s*(?:\d+\s*%\s*)?(?:ust|mwst|umsatzsteuer)", label, re.I):
            continue                        # Bruttozeile ("Bruttopreis   88,06   6,84")
        sammel = bool(SLP_SAMMEL.search(label)) and not SLP_SAMMEL_NEIN.search(label)
        standardzeile = bool(re.match(r"\s*(standardkunde|haushalt|allgemein|kleinkunde)", label, re.I)) and not (
            SLP_AUSSCHLUSS.search(label) or re.search(r"tarif", label, re.I))
        if (ausgeschlossen and not (kopf_ausschluss and standardzeile)) or (SLP_AUSSCHLUSS.search(zl) and not sammel):
            continue
        kopf = None
        if len(zahlen) >= 2 and len(zahlen) % 2 == 0 and all(
                ist_brutto(de_zahl(zahlen[k].group()), de_zahl(zahlen[k + 1].group())) for k in range(0, len(zahlen), 2)):
            zahlen = zahlen[0::2]          # Netto/Brutto-Paare: nur netto
        elif len(zahlen) >= 4 and len(zahlen) % 2 == 0 and all(
                ist_brutto(de_zahl(zahlen[k].group()), de_zahl(zahlen[k + len(zahlen) // 2].group()))
                for k in range(len(zahlen) // 2)):
            zahlen = zahlen[: len(zahlen) // 2]   # erst alle Nettowerte, dann alle Bruttowerte
        for j, m in enumerate(zahlen):
            ende = zahlen[j + 1].start() if j + 1 < len(zahlen) else len(z)
            danach = z[m.end():ende][:30]
            davor = z[(zahlen[j - 1].end() if j else 0):m.start()]
            art = _slp_einheit(danach)
            if art is None:
                worte = [(w.end(), "GP") for w in re.finditer(r"grund-?\s*preis", davor, re.I)]
                worte += [(w.end(), "AP") for w in re.finditer(r"arbeits-?\s*preis", davor, re.I)]
                if worte:
                    a = max(worte)[1]
                    einheit_davor = _slp_einheit(davor)
                    if einheit_davor and einheit_davor[0] == a:
                        art = einheit_davor
                    else:
                        if kopf is None:
                            kopf = _slp_kopf(zeilen, start, i)
                        faktoren = {f for _, k, f in kopf if k == a and f is not None}
                        art = (a, faktoren.pop() if len(faktoren) == 1 else None)
            if art is None:
                if kopf is None:
                    kopf = _slp_kopf(zeilen, start, i)
                if len(kopf) == len(zahlen):
                    _, a, f = sorted(kopf)[j]
                    art = (a, f)
                elif kopf:
                    pos = m.start() + len(m.group()) / 2
                    _, a, f = min(kopf, key=lambda t: abs(t[0] - pos))
                    art = (a, f)
            if (art is None or art[1] is None) and len(zahlen) == 1:
                # senkrechte Anordnung: "Grundpreis   60,00" / "in € pro Jahr" bzw. "in ct/kWh" / "7,60"
                darunter = next((x.strip() for x in zeilen[i + 1:i + 3] if x.strip()), "")
                # Einheit darunter nur zu einem Wert mit Wort davor ("Grundpreis   60,00" / "in € pro Jahr"),
                # Einheit darüber nur aus der unmittelbar vorangehenden Zeile ("in ct/kWh" / "7,60")
                oben = einheit_offen[0] if einheit_offen and i - einheit_offen[1] <= 2 else None
                for kand in ((_slp_einheit(darunter) if art and len(darunter) < 30 and not ZAHL.search(darunter) else None),
                             oben):
                    if kand and (art is None or art[0] == kand[0]):
                        art = kand
                        break
            if art is None or m.group().startswith("-"):
                continue                    # negative Werte sind Reduzierungen, keine Preise
            a, f = art
            if f is None:
                erg.slp_unklar.append("SLP: Einheit nicht bestimmbar")
                continue
            if a == "GP" and f == 365.0:
                erg.slp_hinweise.append("Tagesgrundpreis × 365 umgerechnet")
            elif a == "GP" and f == 12.0:
                erg.slp_hinweise.append("Monatsgrundpreis × 12 umgerechnet")
            einheit_offen = None
            werte[a].append(round(de_zahl(m.group()) * f, 4))
            zeilen_label[a].append((werte[a][-1], label_von(z)))
    for a, schluessel, name in (("AP", "ap", "Arbeitspreis"), ("GP", "gp", "Grundpreis")):
        v = list(dict.fromkeys(werte[a]))
        if len(v) > 1:
            # Varianten nach Abrechnungsturnus (Halle): jährliche Rechnungslegung ist der Standard
            jaehrlich = {w for w, lab in zeilen_label[a]
                         if re.search(r"(?<!halb)(?<!viertel)j[äa]hrlich|jahresabrechnung", lab, re.I)}
            turnus = all(re.search(r"j[äa]hrlich|monatlich|jahresabrechnung|rechnungslegung|abrechnung", lab, re.I)
                         for _, lab in zeilen_label[a])
            if len(jaehrlich) == 1 and turnus:
                v = list(jaehrlich)
                erg.slp_hinweise.append(f"{name} bei jährlicher Rechnungslegung")
        if len(v) == 1:
            erg.slp[schluessel] = v[0]
        elif len(v) > 1:
            erg.slp_unklar.append(f"SLP: mehrere {name}e ({', '.join(str(x) for x in v[:4])})")


GRENZE_TEXT = re.compile(r"(?:<=|>=|<|≤|≥|>|unter|bis|ab|über|ueber)?\s*2[.]?500\s*(?:h\s*/\s*a|h\b|std\.?|stunden)?",
                         re.I)


EBENEN_WORT = re.compile(r"(?:umspannung\s+(?:in\s+|zur\s+|auf\s+)?)?(?:hoch|mittel|nieder)spannung|umspannung\s+(?:in|zur|auf)?", re.I)


def ebenen_spalten_lesen(zeilen: list[str], eb: str) -> dict:
    """Spannungsebenen als Spalten, Zeilen "Leistungspreis" / "Arbeitspreis" je Benutzungsdauer (Nordhausen):

        Mittelspannung   Umspannung in   Niederspannung
                         Niederspannung
        Leistungspreis in €/kW*a        6,99     10,83     15,12
    Benutzungsdauer < 2.500 h/a
        Arbeitspreis in ct/kWh          4,20      5,49      6,93
        ...
    """
    for i, z in enumerate(zeilen):
        if ZAHL.search(z) or len(EBENEN_WORT.findall(z)) < 2:
            continue
        spalten = [[m.start(), m.group()] for m in re.finditer(r"\S+(?:\s\S+)*", z)]
        if len(spalten) < 2 or not all(EBENEN_WORT.search(t) for _, t in spalten):
            continue
        # Fortsetzung des Spaltenkopfs in der nächsten Zeile ("Umspannung in" / "Niederspannung")
        if i + 1 < len(zeilen) and zeilen[i + 1].strip() and not ZAHL.search(zeilen[i + 1]):
            for m in re.finditer(r"\S+(?:\s\S+)*", zeilen[i + 1]):
                naechste = min(spalten, key=lambda s: abs(s[0] - m.start()))
                if abs(naechste[0] - m.start()) <= 6:
                    naechste[1] += " " + m.group()
        ziel = [s[0] for s in spalten if ebene(s[1]) == eb]
        if len(ziel) != 1:
            continue
        pos_spalten = [s[0] for s in spalten]
        reihen, grenzen = [], []          # (zeilenindex, "LP"/"AP", wert) und (zeilenindex, "unter"/"ueber")
        for j in range(i + 1, min(i + 14, len(zeilen))):
            zj = zeilen[j]
            if GRENZE_UNTER.search(zj) and not GRENZE_UEBER.search(zj):
                grenzen.append((j, "unter"))
            elif GRENZE_UEBER.search(zj) and not GRENZE_UNTER.search(zj):
                grenzen.append((j, "ueber"))
            zahlen = zahlen_mit_pos(zj)
            art = "LP" if re.search(r"leistungs-?\s*preis", zj, re.I) else "AP" if re.search(r"arbeits-?\s*preis", zj, re.I) else None
            if not art or len(zahlen) != len(spalten):
                continue
            einheit = (LP_EINHEIT if art == "LP" else AP_EINHEIT).search(zj)
            if not einheit or (art == "LP" and (einheit.group(1) or "a").lower().startswith(("mon", "tag", "d"))):
                return {}
            faktor = 1.0 if art == "LP" or einheit.group(1).lower() in ("ct", "cent") else 100.0
            k = min(range(len(zahlen)), key=lambda n: abs(zahlen[n][0] - ziel[0]))
            reihen.append((j, art, zahlen[k][1] * faktor))
        if len(reihen) != 4 or len(grenzen) != 2 or [r[1] for r in reihen] not in (["LP", "AP"] * 2, ["AP", "LP"] * 2):
            continue
        werte = {}
        for paar in (reihen[:2], reihen[2:]):
            mitte = (paar[0][0] + paar[1][0]) / 2
            grenze = min(grenzen, key=lambda g: abs(g[0] - mitte))[1]
            for _, art, w in paar:
                werte[f"{art.lower()}_{grenze}_2500"] = w
        if len(werte) == 4:
            return werte
    return {}


def quer_lesen(zeilen: list[str], eb: str) -> dict:
    """Gedrehte Tabelle: Spalten < 2.500 / ≥ 2.500, Zeilen "Arbeitspreis" und "Leistungspreis".

    Die Ebene steht als Zwischenzeile darüber (Netz Leipzig) oder, bei einem Blatt nur für eine Ebene,
    im Dokumentkopf ("Entnahme aus der Netzebene Niederspannung", SachsenNetze).
    """
    kopf = norm(" ".join([z for z in zeilen if z.strip()][:6]))
    nur_ns = "niederspannung" in kopf and not re.search(r"mittelspannung|umspann|hochspannung", kopf)
    treffer, aktiv, spalten, aktuelle, fiktiv = [], False, None, None, False
    satz, seite_ebene, seite_kopf = {}, None, False
    for z in zeilen:
        zl = z.strip()
        if not zl:
            continue
        m_anschluss = re.match(r"netzanschluss\s+(.+?)\s*/\s*messung", zl, re.I)
        if m_anschluss:              # Seitenkopf "Netzanschluss Niederspannung / Messung Niederspannung" (Freital)
            seite_ebene, seite_kopf = ebene(m_anschluss.group(1)), True    # Mittelspannung → keine Ebene
            continue
        if FIKTIV.search(zl):
            fiktiv, aktiv = True, False
            continue
        u, o = list(GRENZE_UNTER.finditer(z)), list(GRENZE_UEBER.finditer(z))
        zahlen = zahlen_mit_pos(z)
        if len(u) == 1 and len(o) == 1 and not zahlen:
            if aktuelle and len(satz) == 4:
                treffer.append((aktuelle, satz))      # vorige Tabelle abschließen
            aktiv, fiktiv, satz = True, False, {}
            aktuelle = seite_ebene if seite_kopf else ("NS" if nur_ns else None)
            spalten = {"unter": u[0].start(), "ueber": o[0].start()}
            continue
        if not aktiv or fiktiv:
            continue
        if STOP.search(zl) and not START.search(zl):
            aktiv = False
            continue
        label = label_von(z)
        m = re.match(r"(jahres)?(leistungs|arbeits)-?\s*preis", label, re.I)
        if not zahlen:
            e = ebene(zl)
            if e or re.search(r"spannung|umspann", zl, re.I):
                if aktuelle and len(satz) == 4:
                    treffer.append((aktuelle, satz))
                aktuelle, satz = e, {}
            continue
        if not m:
            continue
        art = "LP" if m.group(2).lower() == "leistungs" else "AP"
        rest = label[m.end():]
        einheit = einheit_nach(rest.strip()) if rest.strip() else None
        werte = ohne_brutto(sorted(zahlen))
        if len(werte) != 2:
            aktiv = False
            continue
        eigene = {x[3] for x in werte if x[3]}
        faktor = None
        for e in eigene | ({einheit} if einheit else set()):
            if e[0] != art:
                faktor = None
                break
            faktor = e[1] if faktor in (None, e[1]) else -1
        if art == "LP" and faktor is None and re.search(r"monat", z, re.I) is None:
            faktor = 1.0 if re.search(r"(€|eur)\s*/\s*kw\b", z, re.I) else None
        if faktor in (None, -1) or re.search(r"monat", z, re.I):
            aktiv = False
            continue
        links, rechts = ("unter", "ueber") if spalten["unter"] < spalten["ueber"] else ("ueber", "unter")
        for (pos, wert, *_), gr in zip(werte, (links, rechts)):
            satz[f"{art.lower()}_{gr}_2500"] = runden(wert * faktor)
        if aktuelle and len(satz) == 4:
            treffer.append((aktuelle, dict(satz)))
    saetze = {tuple(s[f] for f in FELDER) for e, s in treffer if e == eb}
    return next(s for e, s in treffer if e == eb) if len(saetze) == 1 else {}


def _block_kopf(zeilen: list[str], i: int):
    """Spaltenkopf über einer Wertezeile: [(art, faktor), (art, faktor)] in Spaltenreihenfolge, sonst None."""
    for j in range(i - 1, max(-1, i - 14), -1):
        z = zeilen[j]
        if ZAHL.search(ohne_spannung(z)) and not (GRENZE_UNTER.search(z) or GRENZE_UEBER.search(z)):
            continue
        wl, wa = re.search(r"leistungs-?\s*preis", z, re.I), re.search(r"arbeits-?\s*preis", z, re.I)
        if not (wl and wa) or ZAHL.search(ohne_spannung(z)):
            continue
        bereich_kopf = " ".join(zeilen[j:i])
        if re.search(r"monat|/\s*tag|kw\s*/\s*d\b", bereich_kopf, re.I):
            return None
        ap = AP_EINHEIT.search(bereich_kopf)
        if not ap or not LP_EINHEIT.search(bereich_kopf):
            return None
        ap_f = 1.0 if ap.group(1).lower() in ("ct", "cent") else 100.0
        return [("LP", 1.0), ("AP", ap_f)] if wl.start() < wa.start() else [("AP", ap_f), ("LP", 1.0)]
    return None


def bloecke_lesen(zeilen: list[str], bereich: list[int], eb: str) -> dict:
    """Zeilenpaare je Ebene: "< 2.500 h/a  3,55 EUR/kW a  8,08 ct/kWh" und darunter "≥ 2.500 h/a ...".

    Das Label steht in der Zeile, zwischen den beiden Zeilen oder in der Zeile davor (Netze Magdeburg).
    Nur eindeutige Fälle: genau ein LP und ein AP mit Einheit direkt hinter der Zahl.
    """
    reihen = []
    for i in bereich:
        z = zeilen[i]
        u, o = GRENZE_UNTER.search(z), GRENZE_UEBER.search(z)
        if bool(u) == bool(o):
            continue
        zahlen = zahlen_mit_pos(z)
        if len(zahlen) == 2 and not any(x[3] for x in zahlen):
            # Einheiten nur im Spaltenkopf darüber ("Leistungspreis Arbeitspreis" / "[€/kW] [ct/kWh]", Schwäbisch Hall)
            kopf = _block_kopf(zeilen, i)
            if kopf:
                zahlen = [(x[0], x[1], x[2], e) for x, e in zip(zahlen, kopf)]
        if len(zahlen) != 2 or not all(x[3] for x in zahlen) or {x[3][0] for x in zahlen} != {"LP", "AP"}:
            continue
        werte = {x[3][0]: runden(x[1] * x[3][1]) for x in zahlen}
        reihen.append((i, "unter" if u else "ueber", werte))
    treffer, letzte = [], -10
    k = 0
    while k + 1 < len(reihen):
        (i1, g1, w1), (i2, g2, w2) = reihen[k], reihen[k + 1]
        if {g1, g2} != {"unter", "ueber"} or i2 - i1 > 3:
            k += 1
            continue
        teile = []
        vor = zeilen[i1 - 1].strip() if i1 > 0 else ""
        if vor and i1 - 1 > letzte + 1 and not ZAHL.search(ohne_spannung(vor)) and not START.search(vor) \
                and not re.search(r"preis", vor, re.I):
            teile.append(vor)
        for j in range(i1, i2 + 1):
            t = label_von(zeilen[j]) if j in (i1, i2) else zeilen[j].strip()
            teile.append(GRENZE_TEXT.sub(" ", t).strip())
        if ebene(" ".join(t for t in teile if t)) == eb:
            w = {"unter": w1, "ueber": w2} if g1 == "unter" else {"unter": w2, "ueber": w1}
            treffer.append({f"{a.lower()}_{g}_2500": w[g][a] for g in w for a in ("LP", "AP")})
        letzte = i2
        k += 2
    saetze = {tuple(t[f] for f in FELDER) for t in treffer}
    return treffer[0] if len(saetze) == 1 else {}


def _zusammenfuehren(funde, eb, erg: Ergebnis) -> dict:
    """Fasst Teilfunde (z. B. getrennte Tabellen für < und ≥ 2.500) zu Sätzen zusammen."""
    if not funde:
        return {}
    netto = [f for f in funde if not f["brutto"]] or funde
    saetze, aktuell, gruende = [], {}, []
    for f in netto:
        if f["grund"]:
            gruende.append(f"{eb}: {f['grund']}")
            continue
        if any(k in aktuell for k in f["werte"]):
            saetze.append(aktuell)
            aktuell = {}
        aktuell.update(f["werte"])
    if aktuell:
        saetze.append(aktuell)
    vollst = [s for s in saetze if all(k in s for k in FELDER)]
    if not vollst:
        erg.unklar.extend(dict.fromkeys(gruende))
        # einzelner Wert bei Umspannung (z. B. Straßenbeleuchtung als reiner Arbeitspreis) macht NS nicht unsicher
        if saetze and not (eb == "MSNS" and all(len(s) <= 1 for s in saetze)):
            erg.unklar.append(f"{eb}: Werte unvollständig")
        return {}
    gerundet = {tuple(round(s[k], 4) for k in FELDER) for s in vollst}
    if len(gerundet) > 1:
        erg.unklar.append(f"{eb}: mehrere Jahresleistungspreis-Tabellen mit abweichenden Werten "
                          f"(Netzgebiete oder Varianten?)")
    return vollst[0]


# ---------------------------------------------------------------- Metadaten

DATUM = re.compile(r"(\d{1,2})\.\s?(\d{1,2})\.\s?(20\d{2}|\d{2})(?!\d)")


def metadaten(erg: Ergebnis, url: str = ""):
    text = erg.text
    kopf = norm("\n".join(z for z in text[:4000].splitlines()
                           if not re.match(r"\s*\d{1,2}\.\d{1,2}\.\d{4}\s", z)))
    u = norm(url)
    erg.jahre = {int(j) for j in re.findall(r"(?<!\d)(202[3-9])(?!\d)", text)}
    # Gültigkeit nur aus dem Kopf des Dokuments (Titel, erste Absätze): im Fließtext stehen oft
    # Verweise wie "seit 01.01.2024 gilt ...", die nichts über das Preisblatt aussagen
    kopf_text = re.sub(r"(?<!\d)(20[2-3])\s(\d)(?!\d)", r"\1\2", KOPFZEILEN(text))
    erg.kopf_jahre = {int(j) for j in re.findall(r"(?<!\d)(202[3-9])(?!\d)", kopf_text)}
    erg.gueltig_jahre = {int(j) for j in re.findall(
        r"(?:g[üu]ltig|gueltig|ab|zum|vom|seit)\s*(?:dem\s*|den\s*)?(?:0?1\.\s?0?1\.|1\.\s*januar)\s?(20\d{2})",
        kopf_text, re.I)}
    erg.gueltig_jahre |= {int(j) for j in re.findall(r"01\.01\.\s?(20\d{2})\s*(?:-|–|bis)\s*31\.12\.", kopf_text)}

    def stand(s):
        e = bool(re.search(r"endg[uü]ltig|endgueltig|\bfinal|(?<![a-z])endg(?![a-z])", s))
        v = bool(re.search(r"vorl[aä]ufig|vorlaeufig|\bvorl\b|\bvorl\.|_vorl|vorl_", s))
        return e, v
    te, tv = stand(kopf)
    ue, uv = stand(u)
    if te and not tv:
        erg.preisstand = "endgültig"
    elif tv and not te:
        erg.preisstand = "vorläufig"
    elif ue and not uv:
        erg.preisstand = "endgültig"
    elif uv and not ue:
        erg.preisstand = "vorläufig"
    else:
        erg.preisstand = "unklar"

    m = re.search(r"stand\s*:?\s*(?:vom\s*)?(\d{1,2}\.\s?\d{1,2}\.\s?\d{2,4})", text, re.I)
    if m:
        d = DATUM.search(m.group(1))
        if d:
            j = d.group(3)
            j = "20" + j if len(j) == 2 else j
            erg.stand_datum = f"{int(d.group(1)):02d}.{int(d.group(2)):02d}.{j}"
    if not erg.stand_datum:
        dateiname = url.rsplit("/", 1)[-1]
        m = re.search(r"(?<!\d)(202[4-7])[-_.]?(0[1-9]|1[0-2])[-_.]?([0-2]\d|3[01])(?!\d)", dateiname)
        if m:
            erg.stand_datum = f"{m.group(3)}.{m.group(2)}.{m.group(1)}"
        else:
            m = re.search(r"(?<!\d)(2[4-7])(0[1-9]|1[0-2])([0-2]\d|3[01])(?!\d)", dateiname)
            if m:
                erg.stand_datum = f"{m.group(3)}.{m.group(2)}.20{m.group(1)}"


def KOPFZEILEN(text: str) -> str:
    """Titelbereich: die ersten 25 nichtleeren Zeilen."""
    return "\n".join([z for z in text.splitlines() if z.strip()][:25])


def jahr_pruefen(erg: Ergebnis, jahr: int, url: str = "", vertraut: bool = False) -> str | None:
    """None wenn das Dokument zum Jahr passt, sonst Grund.

    Abgelehnt wird nur, wenn das Jahr gar nicht vorkommt oder der Kopf ein anderes Jahr nennt und
    das gesuchte nicht (z. B. Preisblatt 2027 oder veraltete Datei "Aktuell" von 2024).
    """
    if jahr not in erg.jahre and str(jahr) not in url and not vertraut:   # vertraut: Link vom Nutzer, Jahr nicht als Ausschluss werten
        return f"Jahr {jahr} nicht im Dokument"
    if erg.gueltig_jahre:
        if jahr not in erg.gueltig_jahre:
            return f"gültig ab {sorted(erg.gueltig_jahre)}, nicht {jahr}"
    elif erg.kopf_jahre and jahr not in erg.kopf_jahre and str(jahr) not in url.rsplit("/", 1)[-1]:
        return f"Kopf nennt {sorted(erg.kopf_jahre)}, nicht {jahr}"
    folge = folgejahr_dokument(erg.text, url, jahr)
    if folge:
        return f"Preisblatt für {folge}, nicht {jahr}"
    if re.search(r"fiktiv", norm(KOPFZEILEN(erg.text))) and not vertraut:
        return "fiktive Entgelte"
    if vne_dokument(erg.text, url):
        return "Preisblatt für vermiedene Netzentgelte (§ 18 StromNEV)"
    if liefer_dokument(erg.text, url):
        return "Endkunden-Preisblatt (Lieferung), keine Netzentgelte"
    return None


ZIELJAHR = re.compile(r"(?:netz(?:nutzungs)?entgelte|netznutzung|preisbl(?:a|ae|ä)tt(?:er)?|preise|entgelte)"
                      r"[^0-9\n]{0,40}?(20\d\d)\b|\b0?1[.\s]\s*0?1[.\s]\s*(20\d\d)\b|1\.\s*januar\s+(20\d\d)\b", re.I)


def folgejahr_dokument(text: str, url: str, jahr: int) -> int | None:
    """Jahr, für das das Blatt laut Titel/Dateiname gilt, wenn es ein anderes als `jahr` ist
    ("vorläufige Netzentgelte 2027", "..._01.01.2027.pdf"), sonst None. Nur Kopf und Dateiname."""
    datei = unquote(url.rsplit("/", 1)[-1]).replace("_", " ").replace("-", " ")
    kopf = "\n".join([z for z in text.splitlines() if z.strip()][:25])
    jahre = {int(j) for m in ZIELJAHR.finditer(kopf + "\n" + datei) for j in m.groups() if j}
    if jahr in jahre or not jahre:
        return None
    spaeter = [j for j in jahre if j > jahr]
    return min(spaeter) if spaeter else None


LIEFERUNG = re.compile(r"grundversorgung|ersatzversorgung|stromlieferung|lieferbedingungen|sondervertrag|strompreis|"
                       r"allgemeine preise|oekostrom|naturstrom|heizstrom|waermestrom|autostrom|"
                       r"preise fuer die belieferung")
NETZENTGELT = re.compile(r"netzentgelt|netznutzung|netzzugang|nutzungsentgelt|entgelte fuer (die )?(netz|nutzung)")


def liefer_dokument(text: str, url: str = "") -> bool:
    """Preisblatt eines Lieferanten (Grund-/Ersatzversorgung, Tarife), ohne Bezug auf Netzentgelte im Kopf."""
    datei = norm(url.rsplit("/", 1)[-1].replace("%20", " "))
    kopf = norm(" ".join([z for z in text.splitlines() if z.strip()][:10]))
    return bool((LIEFERUNG.search(kopf) or LIEFERUNG.search(datei))
                and not NETZENTGELT.search(kopf) and not NETZENTGELT.search(datei))


def vne_dokument(text: str, url: str = "") -> bool:
    """Referenzpreisblatt bzw. Preisblatt zur Ermittlung vermiedener Netzentgelte (nicht für Netznutzung)."""
    datei = norm(url.rsplit("/", 1)[-1].replace("%20", " "))
    if re.search(r"vermiedene|referenzpreis|(^|[_\-\s])vne([_\-\s.]|$)", datei):
        return True
    kopf, klammer = [], False
    for z in [z.strip() for z in text.splitlines() if z.strip()][:8]:
        # Anmerkung in eckigen Klammern ("[Für vermiedene Netzentgelte nur verwendbar, wenn …]") ist kein Titel
        if z.startswith("[") and not re.match(r"\[\d+\]", z) or klammer:
            klammer = "]" not in z
            continue
        kopf.append(z)
    return bool(re.search(r"vermiedene[nr]?\s+netzentgelt|referenzpreisblatt", norm(" ".join(kopf))))


# ---------------------------------------------------------------- Plausibilität

def plausibel(werte: dict, ebene_name: str = "NS") -> list[str]:
    g = []
    lp_lo, ap_lo = werte.get("lp_unter_2500"), werte.get("ap_unter_2500")
    lp_hi, ap_hi = werte.get("lp_ueber_2500"), werte.get("ap_ueber_2500")
    if None in (lp_lo, ap_lo, lp_hi, ap_hi):
        return [f"{ebene_name}: Werte unvollständig"]
    if ebene_name == "NS" and not (40 <= lp_hi <= 260):
        g.append(f"NS LP über 2.500 h = {lp_hi:.2f} außerhalb 40–260 €/kW/a")
    if not lp_lo < lp_hi:
        g.append(f"{ebene_name}: LP unter 2.500 ({lp_lo:.2f}) nicht kleiner als LP über ({lp_hi:.2f})")
    if not ap_lo > ap_hi:
        g.append(f"{ebene_name}: AP unter 2.500 ({ap_lo:.2f}) nicht größer als AP über ({ap_hi:.2f})")
    if not (0 < ap_lo < 30 and 0 < ap_hi < 30):
        g.append(f"{ebene_name}: AP außerhalb 0–30 ct/kWh")
    elif ap_lo < 1.0:
        g.append(f"{ebene_name}: AP unter 2.500 h = {ap_lo:.2f} ct/kWh, Einheit €/kWh?")
    return g


def plausibel_reihenfolge(ms: dict, msns: dict, ns: dict) -> list[str]:
    """Gesamtkosten in ct/kWh bei 4.000 Stunden: Mittelspannung <= MS/NS <= Niederspannung (Leistungspreise allein dürfen anders liegen)."""
    def c(d):
        return d["ap_ueber_2500"] + d["lp_ueber_2500"] * 100 / 4000 if d and len(d) == 4 else None
    a, b, n = c(ms), c(msns), c(ns)
    g = []
    if a is not None and b is not None and a > b * 1.05:
        g.append(f"MS ({a:.2f} ct/kWh bei 4.000 h) teurer als MS/NS ({b:.2f})")
    if a is not None and n is not None and a > n * 1.05:
        g.append(f"MS ({a:.2f} ct/kWh bei 4.000 h) teurer als NS ({n:.2f})")
    if b is not None and n is not None and b > n * 1.25:
        g.append(f"MS/NS ({b:.2f} ct/kWh bei 4.000 h) deutlich teurer als NS ({n:.2f})")
    return g


def plausibel_slp(slp: dict) -> list[str]:
    g = []
    ap, gp = slp.get("ap"), slp.get("gp")
    if ap is None:
        g.append("SLP-Arbeitspreis fehlt")
    elif not 3 <= ap <= 15:
        g.append(f"SLP-Arbeitspreis {ap:.2f} ct/kWh außerhalb 3–15")
    if gp is None:
        g.append("SLP-Grundpreis fehlt")
    elif not 0 <= gp <= 200:
        g.append(f"SLP-Grundpreis {gp:.2f} €/a außerhalb 0–200")
    return g


STOPWORTE = set("""gmbh co kg ag mbh ug ohg eg gbr se kgaa und der die das fuer von zu in am an
netz netze netzes netzbetrieb netzbetreiber netzgesellschaft netzservice netzdienste verteilnetz verteilnetze
stromnetz stromnetze energienetz energienetze energie energien energieversorgung versorgung versorger
versorgungsbetriebe stadtwerke stadtwerk werke werk gemeindewerke elektrizitaetswerk elektrizitaetswerke
elektrizitaetsversorgung strom stromversorgung gesellschaft infrastruktur service services kommunale
regional regionale holding technische betriebe gruppe""".split())


def name_tokens(name: str) -> list[str]:
    n = re.sub(r"[^a-z0-9]+", " ", norm(name))
    return [t for t in n.split() if len(t) >= 3 and t not in STOPWORTE]


def name_im_text(name: str, text: str, aliase=(), domain: str = "") -> bool:
    t = norm(text)
    t_kompakt = re.sub(r"[^a-z0-9]", "", t)
    kandidaten = [name, *aliase]
    for n in kandidaten:
        toks = name_tokens(n)
        if toks and any(re.search(r"(?<![a-z])" + re.escape(x), t) for x in toks):
            return True
        kompakt = re.sub(r"[^a-z0-9]", "", norm(re.sub(r"\b(GmbH|AG|KG|mbH|Co\.?|&)\b", " ", n)))
        if len(kompakt) >= 5 and kompakt in t_kompakt:
            return True
    if domain:
        d = norm(domain).removeprefix("www.").split(".")[0]
        if len(d) >= 4 and re.sub(r"[^a-z0-9]", "", d) in t_kompakt:
            return True
    return False


def auswerten(pfad: Path, url: str = "", jahr: int = 2026) -> Ergebnis:
    seiten = text_aus_datei(pfad)
    erg = tabellen_lesen(seiten)
    metadaten(erg, url)
    if erg.tageswerte:
        erg.hinweise.append("Tagesleistungspreis × 365 umgerechnet")
    if erg.grenze_le:
        erg.hinweise.append("Grenze ≤ 2.500 / > 2.500 h")
    erg.slp_hinweise = list(dict.fromkeys(erg.slp_hinweise))
    return erg
