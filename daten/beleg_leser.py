"""Beleg-Leser: liest die Ebenentabellen eines gespeicherten Dokumenttexts und merkt sich je Wert Zeile und Beschriftung.

Ziel: Ein Wert gilt nur als belegt, wenn er in einer Zeile steht, deren Beschriftung zur Ebene passt (HS/MS, MS, MS/NS, NS).
Der Leser ist unabhängig von den bisherigen Parsern. Ergebnis je Netzbetreiber: Liste von Belegen
(ebene, vier Werte, Zeilennummer, Beschriftung, Hinweise wie 'Tagespreis x 365', 'netto aus Netto/Brutto').

Prüfung des Lesers: an den von Hand geprüften Netzbetreibern (hinweis 'von Hand am Dokument geprüft') muss er die Handwerte reproduzieren.
Aufruf: PYTHONPATH=. python daten/beleg_leser.py pruefen     (Test an den Handwerten)
        PYTHONPATH=. python daten/beleg_leser.py alle        (schreibt ergebnis/beleg_je_wert.csv und ergebnis/beleg_zusammenfassung.csv)
"""
import csv, glob, re, sys
from pathlib import Path

K = ("lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh")
ZAHL = re.compile(r"(?<![\w.,])-?\d{1,3}(?:\.\d{3})*,\d+|(?<![\w.,])-?\d+\.\d{4,}|(?<![\w.,])-?\d+,\d+")
EBENEN = ("hsms", "ms", "msns", "ns")


def zahl(s):
    s = s.strip()
    if re.fullmatch(r"-?\d+\.\d{4,}", s):
        return float(s)
    return float(s.replace(".", "").replace(",", "."))


def ebene_von(label):
    """Strenge Zuordnung einer Beschriftung. Gibt hs | hsms | ms | msns | ns | None zurück."""
    t = re.sub(r"\s+", " ", label.lower())
    t = re.sub(r"[\*¹²³]", " ", t)
    if re.search(r"höchst|hös", t) and not re.search(r"hoch\s*-?\s*/?\s*mittel|mittelspannung", t):
        return None
    msns = re.search(r"mittel\s*-?\s*/?\s*(?:und\s*)?(?:auf\s*)?nieder|\bms\s*/\s*ns\b|\bmsp\s*/\s*nsp\b|\bms\s*-\s*ns\b|20\s*kv\s*/\s*0,?4|umspann\w*\s*(?:zur|in|auf)?\s*niederspannung|netzstation", t)
    hsms = re.search(r"hoch\s*-?\s*/?\s*(?:und\s*)?(?:auf\s*)?mittel|\bhs\s*/\s*msp?\b|\bhsp\s*/\s*msp\b|110\s*(?:kv)?\s*/\s*(?:10|20)|umspann\w*\s*(?:zur|in|auf)?\s*mittelspannung|hochspannung\s*(?:mit|einschl)|umspannstation|usp\.?\s*hs", t)
    if msns:
        return "msns"
    if hsms:
        return "hsms"
    if re.search(r"umspann", t):
        return None
    if re.search(r"hochspannung|\bhs\b|hsp\b", t) and not re.search(r"mittel|nieder", t):
        return "hs"
    if re.search(r"niederspannung|\bnsp?\b|\bnetzebene\s*7\b|netzebene\s*7", t) and not re.search(r"mittel", t):
        return "ns"
    if re.search(r"mittelspannung|\bmsp?\b", t) and not re.search(r"nieder|hoch", t):
        return "ms"
    return None


def zeilen(pfad):
    return [re.sub(r"[ \t]{2,}", "  ", x.strip()) for x in Path(pfad).read_text(encoding="utf8", errors="replace").split("\n")]


def paare_netto(nums):
    """Netto/Brutto-Paare erkennen: aufeinanderfolgende Zahlen mit Verhältnis ~1,19 -> nur Netto behalten."""
    if len(nums) >= 4 and len(nums) % 2 == 0:
        paare = [(nums[i], nums[i + 1]) for i in range(0, len(nums), 2)]
        if all(a > 0 and abs(b / a - 1.19) < 0.02 for a, b in paare):
            return [a for a, _ in paare], True
    # Brutto in Klammern oder nach Schrägstrich: "58,22 / 69,28"
    return nums, False


def kandidaten(L):
    """Zeilen mit mindestens zwei Preiszahlen und ihre Beschriftung (inkl. Fortsetzungszeilen)."""
    out = []
    for i, l in enumerate(L):
        if not l:
            continue
        ms = list(ZAHL.finditer(l))
        if len(ms) < 2:
            continue
        label = l[:ms[0].start()].strip(" :.-•●")
        nums = [zahl(m.group()) for m in ms]
        prev = [x for x in L[max(0, i - 2):i] if x and not ZAHL.search(x)]
        nxt = [x for x in L[i + 1:i + 3] if x and not ZAHL.search(x)]
        if len(re.sub(r"[^a-zäöüß]", "", label.lower())) >= 6:
            ctxs = [label]
            if prev:
                ctxs.append(prev[-1] + " " + label)
            if nxt:
                ctxs.append(label + " " + nxt[0])
        else:
            ctxs = []
            if len(prev) > 1:
                ctxs.append(prev[-2] + " " + prev[-1] + " " + label)
            if prev:
                ctxs.append(prev[-1] + " " + label)
            if nxt:
                ctxs.append(label + " " + nxt[0])
                ctxs.append(label + " " + " ".join(nxt[:2]))
            ctxs.append(label)
        eb = None; wel = ""
        for c in ctxs:
            eb = ebene_von(c)
            if eb:
                wel = c.strip(); break
        out.append(dict(i=i, nums=nums, label=wel or label, ebene=eb, text=l))
    return out


def kopf_hinweise(L, i):
    """Kopfzeilen oberhalb: Tagespreise? Benutzungsdauer < oder >=?"""
    t = " ".join(L[max(0, i - 12):i]).lower()
    return dict(tag=bool(re.search(r"€\s*/\s*\(?kw\s*[*x·]\s*(?:tag|d)\b|kw\s*\*\s*tag|€/kw/tag|eur/kw\*tag|/kw\s*·\s*tag", t)),
                unter=bool(re.search(r"<\s*2\.?500|bis\s*(?:zu\s*)?2\.?500|≤\s*2\.?500|unter\s*2\.?500", t[-300:])),
                ab=bool(re.search(r"≥\s*2\.?500|>\s*2\.?500|über\s*2\.?500|mehr\s*als\s*2\.?500|ab\s*2\.?500", t[-300:])))


def belege(pfad):
    """Liefert Liste von Belegen: dict(ebene, werte(4), zeile, label, hinweis)."""
    L = zeilen(pfad)
    cand = kandidaten(L)
    res = []
    # Vierer-Zeilen
    for c in cand:
        if not c["ebene"]:
            continue
        nums, netto = paare_netto(c["nums"])
        kh = kopf_hinweise(L, c["i"])
        hint = []
        if len(nums) >= 4:
            v = nums[:4]
            if v[0] < 2 and v[2] < 2 and (kh["tag"] or v[0] < 1.6):
                v = [round(v[0] * 365, 2), round(v[1] * 100, 2) if v[1] < 1 else v[1], round(v[2] * 365, 2), round(v[3] * 100, 2) if v[3] < 1 else v[3]]
                hint.append("Tagespreis x 365")
            if netto:
                hint.append("netto aus Netto/Brutto")
            res.append(dict(ebene=c["ebene"], werte=v, zeile=c["i"] + 1, label=c["label"][:60], hinweis="; ".join(hint), art="vier"))
        elif len(nums) == 2:
            res.append(dict(ebene=c["ebene"], werte=nums, zeile=c["i"] + 1, label=c["label"][:60], hinweis="", art="zwei", unter=kh["unter"], ab=kh["ab"]))
    # Zweier-Blöcke zu Vierern zusammensetzen (Tabelle < 2.500 h und Tabelle >= 2.500 h getrennt)
    zw = [r for r in res if r["art"] == "zwei"]
    unter = {}; ab = {}
    for r in zw:
        if r.get("ab") and not r.get("unter"):
            ab.setdefault(r["ebene"], []).append(r)
        elif r.get("unter") and not r.get("ab"):
            unter.setdefault(r["ebene"], []).append(r)
    for eb in unter:
        if eb in ab:
            u, a = unter[eb][0], ab[eb][0]
            res.append(dict(ebene=eb, werte=[u["werte"][0], u["werte"][1], a["werte"][0], a["werte"][1]], zeile=u["zeile"], label=u["label"], hinweis=f"zwei Tabellen (Zeilen {u['zeile']} und {a['zeile']})", art="vier"))
    return [r for r in res if r["art"] == "vier"]


def passt(w, ours, tol=0.011):
    return ours is not None and len(w) == 4 and all(abs(a - b) <= tol for a, b in zip(w, ours))


def unsere(r, eb):
    v = []
    for k in K:
        s = r[f"{eb}_{k}"]
        if not s:
            return None
        v.append(float(s.replace(".", "").replace(",", ".")))
    return v


def textdateien(r):
    fs = glob.glob(f"ergebnis/texte_layout/{r['mastr_nr']}_*.txt") + glob.glob(f"ergebnis/texte/{int(r['nr']):04d}.txt") + glob.glob(f"ergebnis/texte_layout/{r['mastr_nr']}_*_*.txt")
    return sorted({f for f in fs if not f.endswith(".alt")})


def textdatei(r):
    fs = textdateien(r)
    return fs[0] if fs else None


def bewerte(r):
    """Je Ebene: belegt (gleicher Wert in Zeile mit passender Beschriftung) | konflikt (Zeile mit passender Beschriftung, anderer Wert) | nicht_im_text | keine_ebene_im_text."""
    fs = textdateien(r)
    if not fs:
        return {eb: ("kein_text", "", "") for eb in EBENEN}
    B = []
    for f in fs:
        B += belege(f)
    out = {}
    for eb in EBENEN:
        ours = unsere(r, eb)
        mit = [b for b in B if b["ebene"] == eb]
        if ours is None:
            out[eb] = ("leer_im_dokument_ebene_gefunden" if mit else "leer", "", "")
            continue
        gl = [b for b in mit if passt(b["werte"], ours)]
        if gl:
            b = gl[0]; out[eb] = ("belegt", f"Zeile {b['zeile']}: {b['label']}", b["hinweis"])
        elif mit:
            b = mit[0]; out[eb] = ("konflikt", f"Zeile {b['zeile']}: {b['label']} = " + "/".join(str(x) for x in b["werte"]), b["hinweis"])
        else:
            out[eb] = ("keine_zeile_mit_passender_beschriftung", "", "")
    return out


def lese_n():
    return list(csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";"))


def pruefen():
    N = lese_n()
    hand = [r for r in N if r["status"] == "ok" and "von Hand am Dokument geprüft" in r["hinweis"]]
    from collections import Counter
    c = Counter(); schlecht = []
    for r in hand:
        res = bewerte(r)
        for eb, (st, bel, h) in res.items():
            if st in ("leer", "kein_text"):
                continue
            c[st] += 1
            if st != "belegt":
                schlecht.append((r["nr"], r["netzbetreiber"][:26], eb, st, bel[:90]))
    ges = sum(c.values())
    print("Test an", len(hand), "von Hand geprüften Netzbetreibern, Werte:", ges, dict(c))
    print("Trefferquote (Handwert wird im Dokument in passender Zeile gefunden):", round(100 * c["belegt"] / max(1, ges)), "%")
    for x in schlecht[:30]:
        print("  ", x)


def alle():
    N = lese_n()
    zeilen_out = []; summ = []
    for r in N:
        res = bewerte(r)
        stat = [st for eb, (st, _, _) in res.items() if st not in ("leer", "kein_text")]
        for eb, (st, bel, h) in res.items():
            zeilen_out.append([r["nr"], r["mastr_nr"], r["netzbetreiber"], r["status"], eb, st, bel, h])
        summ.append([r["nr"], r["mastr_nr"], r["netzbetreiber"], r["status"], "alle_belegt" if stat and all(s == "belegt" for s in stat) else ("kein_text" if all(st == "kein_text" for st, _, _ in res.values()) else "offen"), "; ".join(f"{eb}:{st}" for eb, (st, _, _) in res.items() if st not in ("belegt", "leer"))])
    with open("ergebnis/beleg_je_wert.csv", "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, delimiter=";"); w.writerow(["nr", "mastr_nr", "netzbetreiber", "status", "ebene", "beleg_status", "fundstelle", "hinweis"]); w.writerows(zeilen_out)
    with open("ergebnis/beleg_zusammenfassung.csv", "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, delimiter=";"); w.writerow(["nr", "mastr_nr", "netzbetreiber", "status", "beleg", "offene_ebenen"]); w.writerows(summ)
    from collections import Counter
    print(Counter(s[4] for s in summ))


if __name__ == "__main__":
    {"pruefen": pruefen, "alle": alle}[sys.argv[1] if len(sys.argv) > 1 else "pruefen"]()
