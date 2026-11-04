"""Eigener Parser nur für SLP (Entnahme ohne Leistungsmessung, Niederspannung): Standard-Grundpreis (€/a) und Arbeitspreis (ct/kWh).
Unabhängig von den RLM-Parsern. Liefert (gp, ap, beleg) oder None."""
import re

ZAHL = re.compile(r"(?<![\d.,])-?\d{1,3}(?:\.\d{3})*,\d{1,4}(?![\d])|(?<![\d.,])-?\d+[.,]\d{1,4}(?![\d])")
AUSSCHLUSS = re.compile(r"speicher|w[äa]rmepumpe|elektromobil|ladestation|steuerbar|unterbrech|14\s*a|modul|heiz|pauschal|reduz|nachtstrom|zweitarif|ht\b|nt\b|hochtarif|niedertarif|beleucht|kommunal|rabatt|lastg|leistungsmessung\s*\(?rlm", re.I)
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
        if "grundpreis" not in k and "grundentgelt" not in k: continue
        k3 = " ".join(zeilen[i:i + 3]).lower()
        if "arbeitspreis" not in k3 and "arbeitsentgelt" not in k3: continue
        gp_zuerst = k3.find("grund") < min(x for x in (k3.find("arbeitsp"), k3.find("arbeitse")) if x >= 0)
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
    return None
