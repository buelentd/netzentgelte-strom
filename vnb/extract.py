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
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

FELDER = ["lp_unter_2500", "ap_unter_2500", "lp_ueber_2500", "ap_ueber_2500"]

ZAHL = re.compile(r"(?<![\d.,])-?\d{1,3}(?:\.\d{3})*,\d{1,6}(?![\d,])")
LP_EINHEIT = re.compile(r"(?:€|eur(?:o)?|euro)\s*/\s*kw(?!h)(?:\s*(?:/|\s|pro|je|und|x)\s*(a|jahr|tag|d|monat|mon))?", re.I)
AP_EINHEIT = re.compile(r"(ct|cent|€|eur(?:o)?)\s*/\s*kwh", re.I)
GRENZE_UNTER = re.compile(r"(<|≤|<=|unter|bis|kleiner)\s*(?:als\s*)?2[.\s]?500", re.I)
GRENZE_UEBER = re.compile(r"(≥|>=|>|über|ueber|ab|größer|groesser|mindestens)\s*(?:als\s*)?2[.\s]?500", re.I)

START = re.compile(r"jahresleistungspreis|jahresbenutzungsdauer|benutzungsdauer|2[.]?500\s*(h|std|stunden)", re.I)
STOP = re.compile(
    r"monatsleistungspreis|ohne\s+leistungsmessung|ohne\s+registrierende|standardlastprofil|"
    r"§\s*14\s*a|modul\s*[123]|blindarbeit|blindstrom|messstellenbetrieb|messstellenentgelt|"
    r"singul[äa]r|§\s*19|reservekapazit|reserveleistung|einspeis|konzessionsabgabe|"
    r"kwkg|offshore|stromsteuer|sonderformen|pauschal", re.I)
BRUTTO = re.compile(r"\bbrutto\b|inkl(?:usive|\.)?\s*(?:der\s*)?(?:gesetzl(?:ichen|\.)?\s*)?(?:umsatzsteuer|ust|mwst)", re.I)
AUSSCHLUSS_LABEL = re.compile(r"14\s*a|steuerbar|wärmepumpe|waermepumpe|speicher|ladeeinricht|ladepunkt|"
                              r"nachtstrom|schwachlast|ohne|monat|grundpreis|blind", re.I)


@dataclass
class Ergebnis:
    ns: dict = field(default_factory=dict)        # FELDER -> float
    msns: dict = field(default_factory=dict)
    hinweise: list = field(default_factory=list)
    unklar: list = field(default_factory=list)    # Gründe, die eine Prüfung erfordern
    preisstand: str = "unklar"
    stand_datum: str = ""
    jahre: set = field(default_factory=set)
    gueltig_jahre: set = field(default_factory=set)
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


def zahlen_mit_pos(zeile: str):
    return [(m.start() + len(m.group()) / 2, de_zahl(m.group()), m.start()) for m in ZAHL.finditer(zeile)]


def label_von(zeile: str) -> str:
    m = ZAHL.search(zeile)
    return (zeile[: m.start()] if m else zeile).strip()


def ebene(label: str) -> str | None:
    """Ordnet ein Zeilenlabel der Ebene NS bzw. MSNS zu (sonst None)."""
    lab = norm(label)
    lab = re.sub(r"^[\d.)\s\-–•]+", "", lab)
    lab = re.sub(r"\s*/\s*", "/", lab)
    lab = re.sub(r"\s*-\s*/", "/", lab)
    lab = lab.replace("-/", "/").replace("- ", "")
    if not lab or AUSSCHLUSS_LABEL.search(lab):
        return None
    if len(lab) > 70:
        return None
    if re.search(r"ms/ns|mittel/nieder|mittelspannung/niederspannung|mittel(spannung)?\s*(und|zu|auf)\s*nieder|"
                 r"umspann\w*\s*(ms|mittel)\w*\s*/?\s*(ns|nieder)|umspann\w*\s*(zur\s*)?nieder|"
                 r"umspann\w*.*\bns\b", lab):
        return "MSNS"
    if re.search(r"hoch|hs/|mittelspannung(?!.*nieder)|\bms\b(?!/)", lab):
        return None
    if re.search(r"^(netzebene\s*7\s*)?niederspannung\b|^\(?ns\)?$|^ne\s*7\b|^netzebene\s*7\b|niederspannungsnetz|"
                 r"^entnahme\s+(aus\s+der\s+|in\s+der\s+)?niederspannung", lab):
        return "NS"
    return None


@dataclass
class Kopf:
    einheiten: list = field(default_factory=list)   # (pos, "LP"/"AP", faktor)
    worte: list = field(default_factory=list)       # (pos, "LP"/"AP")
    grenzen: list = field(default_factory=list)     # (pos, "unter"/"ueber", zeile_idx)
    brutto: bool = False


def kopf_lesen(zeilen: list[str], von: int, bis: int, erg: Ergebnis) -> Kopf:
    """Sammelt Kopfinformationen aus den Zeilen [von, bis) eines Abschnitts."""
    k = Kopf()
    beste_einheiten = []
    for i in range(von, bis):
        z = zeilen[i]
        if ZAHL.search(z) and ebene(label_von(z)):
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
        if len(einh) >= 2:
            beste_einheiten = sorted(einh)
        wl = re.compile(r"leistungs-?\s*preis|\blp\b", re.I)
        wa = re.compile(r"arbeits-?\s*preis|\bap\b", re.I)
        worte = [(m.start() + len(m.group()) / 2, "LP") for m in wl.finditer(z)]
        worte += [(m.start() + len(m.group()) / 2, "AP") for m in wa.finditer(z)]
        if len(worte) >= 2:
            k.worte = sorted(worte)
        g = [(m.start() + len(m.group()) / 2, "unter", i) for m in GRENZE_UNTER.finditer(z)]
        g += [(m.start() + len(m.group()) / 2, "ueber", i) for m in GRENZE_UEBER.finditer(z)]
        if g:
            if re.search(r"≤|<=|bis\s*(einschl|zu)?\s*2[.\s]?500", z) and re.search(r"(?<![≥>])>(?!=)\s*2[.\s]?500|über", z):
                erg.grenze_le = True
            k.grenzen.extend(g)
        if BRUTTO.search(z):
            k.brutto = True
        if re.search(r"tagesleistungspreis|€\s*/\s*kw\s*/?\s*(tag|d)\b", z, re.I):
            erg.tageswerte = True
    k.einheiten = beste_einheiten
    return k


def _naechster(pos, liste):
    return min(liste, key=lambda t: abs(t[0] - pos))


def zuordnen(zahlen, kopf: Kopf, zeilen_grenze: str | None):
    """Ordnet die Zahlen einer Tabellenzeile den Feldern zu.

    Rückgabe: (dict feld->wert, grund_falls_unklar)
    """
    if not zahlen:
        return {}, "keine Zahlen"
    # Art (LP/AP) und Umrechnungsfaktor je Zahl
    art = []
    zahlen = sorted(zahlen)
    if len(kopf.einheiten) == len(zahlen):
        # gleich viele Einheiten wie Zahlen: Zuordnung über die Reihenfolge der Spalten
        for (pos, wert, _), (p, a, f) in zip(zahlen, kopf.einheiten):
            art.append((a, wert * f, pos))
    elif len(kopf.einheiten) > len(zahlen):
        for pos, wert, _ in zahlen:
            p, a, f = _naechster(pos, kopf.einheiten)
            art.append((a, wert * f, pos))
    elif len(kopf.worte) == len(zahlen) and not kopf.einheiten:
        for (pos, wert, _), (p, a) in zip(zahlen, kopf.worte):
            art.append((a, wert, pos))
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

    funde = {"NS": [], "MSNS": []}   # Liste von dicts je Tabelle
    im_abschnitt = False
    start = 0
    offen_label = ""                   # Label einer Zeile ohne Zahlen (Umbruch)
    offen_ebene = None                 # Ebene, deren Zahlen in Folgezeilen stehen
    for i, z in enumerate(zeilen):
        zl = z.strip()
        if not zl:
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
        label = label_von(z)
        eb = ebene(label)
        if not eb and offen_label and not offen_ebene and len(label) < 40:
            eb = ebene(offen_label + " " + label)
        if zahlen and eb:
            kopf = kopf_lesen(zeilen, start, i, erg)
            gr = "unter" if GRENZE_UNTER.search(label) else "ueber" if GRENZE_UEBER.search(label) else None
            werte, grund = zuordnen(zahlen, kopf, gr)
            funde[eb].append({"werte": werte, "grund": grund, "brutto": kopf.brutto, "zeile": i})
            offen_label, offen_ebene = "", None
        elif zahlen and offen_ebene:
            gr = "unter" if GRENZE_UNTER.search(label) else "ueber" if GRENZE_UEBER.search(label) else None
            if gr:
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
    slp_lesen(zeilen, erg)
    return erg


# ---------------------------------------------------------------- SLP

SLP_START = re.compile(r"ohne\s+(?:registrierende\s+)?leistungsmessung|standardlastprofil|\bslp\b|"
                       r"ohne\s+(?:viertelstunden|lastgang)", re.I)
SLP_STOP = re.compile(r"mit\s+(?:registrierender\s+)?leistungsmessung|jahresleistungspreis|jahresbenutzungsdauer|"
                      r"monatsleistungspreis|blindarbeit|blindstrom|messstellen|konzessionsabgabe|einspeis|"
                      r"reservekapazit|singul[äa]r|§\s*19|kwkg|offshore|umlage|stromsteuer", re.I)
SLP_AUSSCHLUSS = re.compile(r"w[äa]rmepumpe|waermepumpe|speicher|14\s*a|modul\s*[123]|unterbrech|steuerbar|"
                            r"nacht|schwachlast|\bnt\b|\bht\b|hochtarif|niedertarif|zweitarif|doppeltarif|"
                            r"zweizeit|schwach|ladeeinricht|ladepunkt|e-?mobil|heizung|mittelspannung|"
                            r"hochspannung|umspann|pausch|reduzier|leistungspreis|kw/a|kw\s*/\s*a", re.I)
SLP_NEUTRAL = re.compile(r"^\s*(niederspannung|eintarif|standard|allgemein|haushalt|gewerbe|entnahme)", re.I)
GP_EINHEIT = re.compile(r"(?:€|eur(?:o)?)\s*/\s*(?:(?:z[äa]hlpunkt|zp|messlokation|malo|marktlokation|anschluss|"
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
    beste = []
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
    return beste


def slp_lesen(zeilen: list[str], erg: Ergebnis):
    """Standard-Arbeitspreis und Grundpreis Niederspannung für Entnahme ohne Leistungsmessung."""
    werte = {"AP": [], "GP": []}
    im, start, ausgeschlossen = False, 0, False
    for i, z in enumerate(zeilen):
        zl = z.strip()
        if not zl:
            continue
        zahlen = list(ZAHL.finditer(z))
        if SLP_START.search(zl) and not zahlen:
            im, start, ausgeschlossen = True, i, bool(SLP_AUSSCHLUSS.search(zl))
            continue
        if not im:
            continue
        if SLP_STOP.search(zl) and not SLP_START.search(zl):
            im = False
            continue
        if not zahlen:
            if SLP_AUSSCHLUSS.search(zl):
                ausgeschlossen = True
            elif SLP_NEUTRAL.search(zl):
                ausgeschlossen = False
            continue
        if ausgeschlossen or SLP_AUSSCHLUSS.search(zl):
            continue
        kopf = None
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
            if art is None:
                continue
            a, f = art
            if f is None:
                erg.slp_unklar.append("SLP: Einheit nicht bestimmbar")
                continue
            if a == "GP" and f == 365.0:
                erg.slp_hinweise.append("Tagesgrundpreis × 365 umgerechnet")
            elif a == "GP" and f == 12.0:
                erg.slp_hinweise.append("Monatsgrundpreis × 12 umgerechnet")
            werte[a].append(round(de_zahl(m.group()) * f, 4))
    for a, schluessel, name in (("AP", "ap", "Arbeitspreis"), ("GP", "gp", "Grundpreis")):
        v = list(dict.fromkeys(werte[a]))
        if len(v) == 1:
            erg.slp[schluessel] = v[0]
        elif len(v) > 1:
            erg.slp_unklar.append(f"SLP: mehrere {name}e ({', '.join(str(x) for x in v[:4])})")


def _zusammenfuehren(funde, eb, erg: Ergebnis) -> dict:
    """Fasst Teilfunde (z. B. getrennte Tabellen für < und ≥ 2.500) zu Sätzen zusammen."""
    if not funde:
        return {}
    netto = [f for f in funde if not f["brutto"]] or funde
    saetze, aktuell = [], {}
    for f in netto:
        if f["grund"]:
            erg.unklar.append(f"{eb}: {f['grund']}")
            continue
        if any(k in aktuell for k in f["werte"]):
            saetze.append(aktuell)
            aktuell = {}
        aktuell.update(f["werte"])
    if aktuell:
        saetze.append(aktuell)
    vollst = [s for s in saetze if all(k in s for k in FELDER)]
    if not vollst:
        if saetze:
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
    kopf = norm(text[:4000])
    u = norm(url)
    erg.jahre = {int(j) for j in re.findall(r"(?<!\d)(202[3-9])(?!\d)", text)}
    erg.gueltig_jahre = {int(j) for j in re.findall(
        r"(?:g[üu]ltig|gueltig|ab|zum|vom|seit)\s*(?:dem\s*|den\s*)?0?1\.\s?0?1\.\s?(20\d{2})", text, re.I)}
    erg.gueltig_jahre |= {int(j) for j in re.findall(r"01\.01\.\s?(20\d{2})\s*(?:-|–|bis)\s*31\.12\.", text)}

    def stand(s):
        e = bool(re.search(r"endg[uü]ltig|endgueltig|\bfinal", s))
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


def jahr_pruefen(erg: Ergebnis, jahr: int, url: str = "") -> str | None:
    """None wenn das Dokument zum Jahr passt, sonst Grund."""
    if jahr not in erg.jahre and str(jahr) not in url:
        return f"Jahr {jahr} nicht im Dokument"
    if erg.gueltig_jahre and jahr not in erg.gueltig_jahre:
        return f"gültig ab {sorted(erg.gueltig_jahre)}, nicht {jahr}"
    if re.search(r"fiktiv", norm(erg.text[:3000])):
        return "fiktive Entgelte"
    return None


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
