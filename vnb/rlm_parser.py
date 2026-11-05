"""Eigener Parser je RLM-Ebene (MS, MS/NS, NS, HS/MS): sucht die Zeile mit dem Ebenennamen und liest dahinter (oder in den
nächsten Zeilen) vier Preise: LP unter 2.500 h, AP unter, LP ab, AP ab. Unabhängig von den anderen Lesern; dient als Ergänzung
bei Lücken. Liefert (werte, beleg) oder None."""
import re
from vnb.extract import ebene, ebene_mshs

ZAHL = re.compile(r"(?<![\d.,])\d{1,3}(?:\.\d{3})*,\d{1,6}(?![\d])|(?<![\d.,])\d+\.\d{1,2}(?![\d])")
MAP = {"MS": "ms", "MSNS": "msns", "NS": "ns", "HSMS": "hsms"}
AUS = re.compile(r"kommunal|rabatt|speicher|w[äa]rmepumpe|steuerbar|14\s*a|modul|messstellen|z[äa]hler|jahresverbrauch|beispiel|vergleich|reserve|monats|wandler|blind", re.I)

def zahlen(zeile):
    z = re.sub(r"\d+(?:[.,]\d+)?\s*kV\b", " ", zeile)
    z = re.sub(r"\b\d{1,2}\.\d{1,2}\.(?:20\d\d)?", " ", z)
    return [float(m.group().replace(".", "").replace(",", ".")) if "," in m.group() else float(m.group()) for m in ZAHL.finditer(z)]

def label_von(zeile):
    """Text vor dem ersten Preis (Zeilenname mit Bindestrichen und Ziffern, z. B. "NS - NE 7 - Niederspannung")."""
    m = re.search(r"\d+,\d", zeile)
    kopf = zeile[:m.start()] if m else zeile
    return re.sub(r"\s+", " ", kopf).strip(" .:|*") if m else re.sub(r"[\d.,€/*()%-]+", " ", zeile).strip()

def plausibel(w, tag):
    lp1, ap1, lp2, ap2 = w
    if tag:
        pass
    return 1 <= lp1 <= 450 and 20 <= lp2 <= 700 and 1.0 <= ap1 <= 25 and 0 <= ap2 <= 15 and ap1 >= ap2 * 0.95 and lp2 > lp1 * 0.4 and lp1 < lp2 * 1.5

def rlm_parser(zeilen, eb):
    # BDEW-Artikel-IDs (1-01-5-001 ... 004): eindeutig, Tages-/Jahres-/Bruttowerte werden dort aufgelöst (Saalfeld)
    try:
        from vnb.extract import artikel_lesen
        art, _ = artikel_lesen(zeilen)
        d = art.get({"ms": "MS", "msns": "MSNS", "ns": "NS", "hsms": "HSMS"}[eb])
        if d and all(d.get(k) is not None for k in ("lp_unter_2500", "ap_unter_2500", "lp_ueber_2500", "ap_ueber_2500")):
            return [round(d[k], 2) for k in ("lp_unter_2500", "ap_unter_2500", "lp_ueber_2500", "ap_ueber_2500")], "BDEW-Artikel-ID-Zeilen"
    except Exception:
        pass
    n = len(zeilen)
    for i, l in enumerate(zeilen):
        lab = label_von(l)
        e = ebene_mshs(lab) or ebene(lab)
        if MAP.get(e) != eb or AUS.search(lab):
            continue
        zs = zahlen(l)
        belegzeilen = [l]
        j = i + 1
        while len(zs) < 8 and j < min(n, i + 5):
            nxt = zeilen[j]
            if nxt.strip():
                lab2 = label_von(nxt)
                if len(re.sub(r"\W", "", lab2)) > 5 and (ebene_mshs(lab2) or ebene(lab2)) and zahlen(nxt):
                    break           # nächste Ebene beginnt
                zs += zahlen(nxt); belegzeilen.append(nxt)
            j += 1
        kopf = " ".join(zeilen[max(0, i - 8):i]).lower()
        tag = bool(re.search(r"kw\s*[*/]\s*tag|/\s*tag|je tag|täglich", kopf + l.lower()))
        kandidaten = []
        mwst = len(zs) >= 2 and zs[0] > 0 and abs(zs[1] / zs[0] - 1.19) < 0.012
        if len(zs) >= 8 and ("brutto" in kopf or mwst):
            kandidaten.append(zs[0:8:2])               # netto | brutto | netto | brutto ...
            kandidaten.append([zs[0], zs[4], zs[2], zs[6]])   # LP< | brutto | LP>= | brutto | AP< | brutto | AP>= | brutto (Rinteln)
        if len(zs) >= 4:
            kandidaten.append(zs[:4])
        for k in kandidaten:
            w = [v * 365 if (tag and ix in (0, 2) and v < 2) else v for ix, v in enumerate(k)]
            if plausibel(w, tag):
                return [round(v, 2) for v in w], " | ".join(x.strip()[:70] for x in belegzeilen[:2])
    return _zeilenpaar(zeilen, eb)


def _halb(zs):
    """(LP, AP) einer Zeile: zwei Zahlen oder vier mit 19 %-Aufschlag (netto, brutto, netto, brutto)."""
    if len(zs) >= 4 and zs[0] > 0 and zs[2] > 0 and abs(zs[1] / zs[0] - 1.19) < 0.012 and abs(zs[3] / zs[2] - 1.19) < 0.012:
        return zs[0], zs[2]
    if len(zs) == 2:
        return zs[0], zs[1]
    return None


def _zeilenpaar(zeilen, eb):
    """Ebenenname steht in zwei aufeinanderfolgenden Zeilen (unter 2.500 h, dann ab 2.500 h), Schifferstadt, Sulz am Neckar."""
    reihen = []
    for i, l in enumerate(zeilen):
        lab = label_von(l)
        e = ebene_mshs(lab) or ebene(lab)
        if MAP.get(e) != eb or AUS.search(lab):
            continue
        h = _halb(zahlen(l))
        if h:
            reihen.append((i, h))
    for (i1, h1), (i2, h2) in zip(reihen, reihen[1:]):
        if 0 < i2 - i1 <= 14:
            w = [h1[0], h1[1], h2[0], h2[1]]
            if plausibel(w, False):
                return [round(v, 2) for v in w], "zwei Zeilen mit Ebenenname: " + " ".join(zeilen[i1].split())[:50]
    return None
