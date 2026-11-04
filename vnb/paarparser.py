"""Parser für Tabellen, in denen jede Ebene aus zwei Zeilen besteht ("< 2.500 | LP | AP" und "> 2.500 | LP | AP"), die Ebenenbezeichnung
aber auf einer der beiden Zeilen oder zwischen ihnen steht, auch auf beide verteilt ("Umspannung" / "zur Mittelspannung"; Deggendorf, Weiler,
Neuwied, Schwäbisch Hall). Die Ebene wird aus dem Text der beiden Zeilen und der Zeilen dazwischen bestimmt.
Liefert {ebene: [LP<, AP<, LP>=, AP>=]} oder {}."""
import re

KLEIN = re.compile(r"(?:<|≤|bis(?:\s+zu)?|unter)\s*2[.,]?500", re.I)
GROSS = re.compile(r"(?:>=|>|≥|ab|über|ueber|mehr\s+als)\s*2[.,]?500", re.I)
ZAHL = re.compile(r"(?<![\d.,])\d{1,3}(?:\.\d{3})*,\d{1,4}(?![\d])")

def _zahlen(z):
    z = re.sub(r"2[.,]?500", " ", z)
    return [float(m.group().replace(".", "").replace(",", ".")) for m in ZAHL.finditer(z)]

def _text(z):
    z = re.sub(r"(?:<|≤|>=|>|≥|bis(?:\s+zu)?|unter|ab|über|mehr\s+als)\s*2[.,]?500\s*h?(?:/a)?", " ", z, flags=re.I)
    return re.sub(r"[\d.,€/*()%≤≥<>=-]+|\b[hH]\b", " ", z)

def klassifiziere(t):
    t = re.sub(r"\s+", " ", t.lower())
    if re.search(r"hoch|hs\s*/?\s*ms|hsp|zur mittelspannung|auf mittelspannung", t): return "hsms"
    if re.search(r"umspann|ms/ns|msp\s*/\s*nsp|mittel.{0,3}/\s*nieder|zur niederspannung", t): return "msns"
    if "mittelspannung" in t or re.search(r"\bms\b|\bmsp\b", t): return "ms"
    if "niederspannung" in t or re.search(r"\bns\b|\bnsp\b", t): return "ns"
    return None

def paarparser(zeilen):
    klein = [(i, _zahlen(z)) for i, z in enumerate(zeilen) if KLEIN.search(z) and len(_zahlen(z)) == 2]
    gross = [(i, _zahlen(z)) for i, z in enumerate(zeilen) if GROSS.search(z) and len(_zahlen(z)) == 2]
    if len(klein) < 2 or len(gross) < 2:
        return {}
    paare = []
    for k_i, k_w in klein:
        g = next(((gi, gw) for gi, gw in gross if k_i < gi <= k_i + 4), None)
        if g:
            paare.append((k_i, g[0], k_w, g[1]))
    if len(paare) < 2:
        return {}
    out = {}
    for n, (k_i, g_i, k_w, g_w) in enumerate(paare):
        ende = paare[n + 1][0] if n + 1 < len(paare) else g_i + 1
        # Textzeilen zwischen den Zeilen und die Zeile direkt vor der kleinen Zeile (Name steht ggf. davor)
        vorher = zeilen[k_i - 1] if k_i > 0 and not _zahlen(zeilen[k_i - 1]) else ""
        text = " ".join([_text(zeilen[j]) for j in range(k_i, g_i + 1)] + [vorher])
        e = klassifiziere(text)
        w = [k_w[0], k_w[1], g_w[0], g_w[1]]
        if e and e not in out and w[1] >= w[3] * 0.95 and w[2] >= 20 and w[2] > w[0]:
            out[e] = w
    return out
