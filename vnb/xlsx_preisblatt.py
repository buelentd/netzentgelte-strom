"""Leser für das elektronische Preisblatt (Excel, BDEW-Artikel-IDs) der Netzbetreiber.

Zeilen wie "1-01-7-001 ; … Leistungspreis (Einheit: €/kW*Tag) ; X ; X ; 0,0571 ; 20,86" oder "Artikel-ID [1-01-7-001] ; Leistungspreis ; 0,1196 ; €/kW*Tag".
Ebene aus der Artikel-ID: 1-01-7 Niederspannung, -6 Umspannung MS/NS, -5 Mittelspannung, -4 Umspannung HS/MS.
Je Ebene vier Werte: -001 Leistungspreis unter 2.500 h, -002 Arbeitspreis unter, -003 Leistungspreis ab, -004 Arbeitspreis ab.
SLP: 1-02-0-001 Grundpreis (€/Tag), 1-02-0-002 Arbeitspreis. Einheiten werden umgerechnet (€/kW*Tag × 365, €/kWh × 100). Nichts wird geschätzt:
fehlt oder ist unplausibel ein Wert, bleibt die Ebene leer."""
from __future__ import annotations

import re
import warnings

EBENEN = {"7": "ns", "6": "msns", "5": "ms", "4": "hsms"}
ID = re.compile(r"(?<!\d)1-0([12])-(\d)(?:-0*(\d{1,3}))?(?!\d)")


def _zahl(v):
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(" ", "")
    if re.fullmatch(r"-?\d+(?:[.,]\d+)?", s):
        return float(s.replace(",", "."))
    return None


def zeilen_lesen(pfad: str):
    warnings.filterwarnings("ignore")
    if pfad.lower().endswith(".xls"):
        import xlrd
        wb = xlrd.open_workbook(pfad)
        for ws in wb.sheets():
            for i in range(ws.nrows):
                yield ws.row_values(i)
    else:
        import openpyxl
        wb = openpyxl.load_workbook(pfad, data_only=True, read_only=True)
        for ws in wb:
            for r in ws.iter_rows(values_only=True):
                yield list(r)


def _umrechnen(art: str, wert: float, text: str):
    """art "lp" (€/kW und Jahr), "ap" (ct/kWh), "gp" (€ und Jahr)."""
    t = text.lower().replace("\n", " ")
    if art == "lp":
        if re.search(r"kw\s*\*?\s*/?\s*tag|€/kw/d|kw\*tag", t):
            return wert * 365
        if re.search(r"kw\s*\*?\s*/?\s*(jahr|a)\b|/kw/a|kw\*a", t):
            return wert
        return None
    if art == "ap":
        if re.search(r"ct\s*/\s*kwh", t):
            return wert
        if re.search(r"€\s*/\s*kwh|eur\s*/\s*kwh", t):
            return wert * 100
        return None
    if art == "gp":
        if re.search(r"€\s*/\s*tag|eur\s*/\s*tag", t):
            return wert * 365
        if re.search(r"€\s*/\s*(jahr|a)\b", t):
            return wert
        return None
    return None


def _wert(art: str, paare, text: str):
    """Bevorzugt eine Zahl, deren Einheit schon die Zieleinheit ist (€/kW und Jahr, ct/kWh, € je Jahr); sonst die erste Zahl mit Umrechnung."""
    ziel = {"lp": r"kw\s*\*?\s*(?:/|und)?\s*(?:jahr|a)\b|/\(kw und jahr\)|€/kw/a|kw\*a", "ap": r"ct\s*/\s*kwh", "gp": r"€\s*/\s*(?:jahr|a)\b"}[art]
    for v, e in paare:
        if e and re.search(ziel, e.lower()):
            return v
    v, e = paare[0]
    return _umrechnen(art, v, (e + " " + text) if e else text)


def preisblatt_lesen(pfad: str) -> dict:
    """{"ns": [lp_u, ap_u, lp_o, ap_o], "msns": …, "ms": …, "hsms": …, "slp": [grundpreis_eur_jahr, ap_ct_kwh], "hinweis": [...]} (nur vollständige Ebenen)."""
    ebene: dict[str, dict[int, float]] = {}
    slp: dict[int, float] = {}
    for z in zeilen_lesen(pfad):
        text = " ".join("" if c is None else str(c) for c in z)
        m = ID.search(text)
        if not m or m.group(3) is None:
            continue
        gruppe, eb, nr = m.group(1), m.group(2), int(m.group(3))
        if gruppe == "1" and eb == "0":
            continue
        paare = []                                    # (Zahl, Einheit aus der Nachbarzelle oder "")
        for k, c in enumerate(z):
            v = _zahl(c)
            if v is None:
                continue
            nxt = z[k + 1] if k + 1 < len(z) else None
            einheit = str(nxt) if isinstance(nxt, str) and _zahl(nxt) is None and re.search(r"€|ct|eur", nxt, re.I) and len(nxt) < 30 else ""
            paare.append((v, einheit))
        if not paare:
            continue
        if gruppe == "1" and eb in EBENEN and nr in (1, 2, 3, 4) and "monat" not in text.lower()[:200]:
            if "modul" in text.lower() or "reduzierung" in text.lower() or "§ 14a" in text:
                continue
            art = "lp" if nr in (1, 3) else "ap"
            w = _wert(art, paare, text)
            if w is not None:
                ebene.setdefault(EBENEN[eb], {})[nr] = w
        elif gruppe == "2" and eb == "0" and nr in (1, 2):
            w = _wert("gp" if nr == 1 else "ap", paare, text)
            if w is not None:
                slp[nr] = w
    out = {"hinweis": []}
    for name, v in ebene.items():
        if all(k in v for k in (1, 2, 3, 4)):
            lp_u, ap_u, lp_o, ap_o = v[1], v[2], v[3], v[4]
            if lp_u + lp_o + ap_u + ap_o == 0:
                continue                                          # alles 0: Ebene gibt es dort nicht
            if not (0 < lp_o < 700 and 0 <= lp_u < 700 and 1 <= ap_u < 30 and 0 <= ap_o < 30 and lp_u < lp_o * 1.5):
                out["hinweis"].append(f"{name}: Werte unplausibel, nicht übernommen")
                continue
            out[name] = [round(lp_u, 4), round(ap_u, 4), round(lp_o, 4), round(ap_o, 4)]
    if 1 in slp and 2 in slp and 0 < slp[1] <= 200 and 3 <= slp[2] <= 15:
        out["slp"] = [round(slp[1], 4), round(slp[2], 4)]
    return out
