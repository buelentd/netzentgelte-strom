"""Eigener Parser nur für SLP (Entnahme ohne Leistungsmessung, Niederspannung): Standard-Grundpreis (€/a) und Arbeitspreis (ct/kWh).
Unabhängig von den RLM-Parsern. Liefert (gp, ap, beleg) oder None."""
import re

ZAHL = re.compile(r"(?<![\d.,])-?\d{1,3}(?:\.\d{3})*,\d{1,4}(?![\d])|(?<![\d.,])-?\d+[.,]\d{1,4}(?![\d])")
AUSSCHLUSS = re.compile(r"speicher|w[äa]rmepumpe|elektromobil|ladestation|steuerbar|(?<!nicht )(?<!nicht\s)unterbrech|14\s*a|modul|heiz|pauschal|reduz|nachtstrom|zweitarif|ht\b|nt\b|hochtarif|niedertarif|beleucht|kommunal|rabatt|lastg|leistungsmessung\s*\(?rlm", re.I)
STANDARD = re.compile(r"niederspannung|\bns\b|kleinkunde|haushalt|gewerbe|standard|allgemein|eintarif|ohne\s+(?:registrierende\s+)?(?:leistungsmessung|lastgang)|slp|sonstige", re.I)

def zahl(s):
    return float(s.replace(".", "").replace(",", ".")) if "," in s else float(s)

def _paar(zeile):
    """Erste zwei Preiszahlen (ohne kV-Angaben) einer Zeile."""
    z = re.sub(r"\d+(?:[.,]\d+)?\s*kV\b", " ", zeile)
    z = re.sub(r"\b(?:20\d\d|\d{1,2}\.\d{1,2}\.(?:20\d\d)?)\b", " ", z)
    return [zahl(m.group()) for m in ZAHL.finditer(z) if m.group()][:4]

def slp_parser(zeilen):
    n = len(zeilen)
    for i, kopf in enumerate(zeilen):
        k = kopf.lower()
        k3 = " ".join(zeilen[i:i + 3]).lower()
        if ("grundpreis" in k or "grundentgelt" in k) and ("arbeitspreis" in k3 or "arbeitsentgelt" in k3):
            gp_zuerst = k3.find("grund") < min(x for x in (k3.find("arbeitsp"), k3.find("arbeitse")) if x >= 0)
        elif re.search(r"(?:€|eur)\s*/\s*(?:a|jahr)", k) and re.search(r"ct\s*/\s*kwh|cent\s*/\s*kwh", k):   # Kopf nur mit Einheiten ("EUR/a  Ct/kWh")
            gp_zuerst = re.search(r"(?:€|eur)\s*/\s*(?:a|jahr)", k).start() < re.search(r"ct\s*/\s*kwh|cent\s*/\s*kwh", k).start()
        else:
            continue
        for j in range(i + 1, min(n, i + 14)):
            l = zeilen[j]
            if not l.strip(): continue
            lab = re.sub(r"[\d.,€/*()%-]+", " ", l).strip()
            ctx = " ".join(zeilen[max(i - 2, j - 2):j + 1])
            if re.search(r"leistungsmessung|lastgang", ctx, re.I) and not re.search(r"ohne", ctx, re.I) and j - i > 6:
                continue
            if AUSSCHLUSS.search(lab) and not STANDARD.search(lab.split("14")[0]):
                continue
            if AUSSCHLUSS.search(lab): continue
            zahlen = _paar(l)
            if len(zahlen) < 2: continue
            kopf_text = " ".join(zeilen[i:i + 4]).lower()
            mwst = len(zahlen) >= 4 and zahlen[0] > 0 and abs(zahlen[1] / zahlen[0] - 1.19) < 0.012
            if len(zahlen) >= 4 and ("brutto" in kopf_text or mwst):      # netto | brutto | netto | brutto
                gp, ap = (zahlen[0], zahlen[2]) if gp_zuerst else (zahlen[2], zahlen[0])
            else:
                gp, ap = (zahlen[0], zahlen[1]) if gp_zuerst else (zahlen[1], zahlen[0])
            if 0 <= gp <= 300 and 2 <= ap <= 25 and (STANDARD.search(lab) or STANDARD.search(ctx) or j == i + 1 or j == i + 2 or j == i + 3):
                return gp, ap, f"{lab[:40]} | {l.strip()[:60]}"
    return slp_untereinander(zeilen) or slp_bdew(zeilen)


EINHEIT_GP = re.compile(r"(?:€|eur|euro)\s*/\s*(?:a|jahr)", re.I)
EINHEIT_AP = re.compile(r"(?:ct|cent)\s*/\s*kwh", re.I)


def slp_untereinander(zeilen):
    """Grundpreis und Arbeitspreis in getrennten Zeilen ("Grundpreis  67,80 €/Jahr" / "Arbeitspreis  4,95 ct/kWh"), der Block mit Hinweis auf
    Niederspannung / ohne Leistungsmessung / Standardlastprofil und ohne 14a, Modul, Wärmepumpe, Heizung davor."""
    n = len(zeilen)
    for i, l in enumerate(zeilen):
        if not re.search(r"grundpreis|grundentgelt", l, re.I) or not EINHEIT_GP.search(l):
            continue
        for j in range(i + 1, min(n, i + 6)):
            m = zeilen[j]
            if re.search(r"arbeitspreis|arbeitsentgelt", m, re.I) and EINHEIT_AP.search(m):
                kopf = " ".join(zeilen[max(0, i - 8):i]).lower()
                if AUSSCHLUSS.search(kopf) or not (STANDARD.search(kopf) or STANDARD.search(l)):
                    break
                gz, az = _paar(re.sub(r"(?:€|eur|euro)\s*/\s*(?:a|jahr)", " ", l, flags=re.I)), _paar(re.sub(r"(?:ct|cent)\s*/\s*kwh", " ", m, flags=re.I))
                if not gz or not az:
                    break
                gp, ap = gz[0], az[0]
                if len(gz) >= 2 and gz[0] > 0 and abs(gz[1] / gz[0] - 1.19) < 0.012 and len(az) >= 2 and az[0] > 0 and abs(az[1] / az[0] - 1.19) < 0.012:
                    gp, ap = gz[0], az[0]                       # netto | brutto
                if 0 <= gp <= 300 and 2 <= ap <= 25:
                    return gp, ap, f"{l.strip()[:45]} | {m.strip()[:45]}"
                break
    return None


def _kleine(zeile):
    """Dezimalzahlen mit bis zu 8 Stellen (BDEW: Preise je Tag und je kWh in Euro)."""
    return [float(m.replace(",", ".")) for m in re.findall(r"(?<![\d.,])\d+,\d{3,8}(?!\d)", zeile)]


def slp_bdew(zeilen):
    """BDEW-Preisblattteil 2: "Marktlokation Grundpreis für Arbeitspreissystem 0,1986 (€/Tag)" und Arbeitspreis "sonstiger Verbrauch" in €/kWh."""
    gp = ap = None
    beleg = ""
    for l in zeilen:
        t = l.lower()
        if gp is None and "grundpreis für arbeitspreissystem" in t:
            z = _kleine(l)
            if z:
                gp = z[0] * 365 if z[0] < 2 else z[0]
                beleg = l.strip()[:60]
        elif ap is None and "sonstiger verbrauch" in t:
            idx = zeilen.index(l)
            for k in range(idx, min(len(zeilen), idx + 5)):
                z = [v for v in _kleine(zeilen[k]) if 0 < v < 1]
                if z:
                    ap = z[0] * 100
                    break
    if gp is not None and ap is not None and 0 <= gp <= 300 and 2 <= ap <= 25:
        return round(gp, 2), round(ap, 4), beleg
    return None
