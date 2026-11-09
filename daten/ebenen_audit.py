"""VERSION 1, NICHT ALS BEFUND VERWENDEN: viele Fehlalarme (Stichprobe: 5 von 5 „harten Konflikten“ waren richtige Werte). Die Zuordnung von Beschriftungen zu Ebenen ist noch zu unscharf (Zeilen wie „5 Mittelspannungsnetz“, mehrzeilige Beschriftungen, netto/brutto-Spalten).

Zeilenweiser Abgleich: Steht der Wert, den wir für eine Ebene führen, im Dokument in der Zeile mit der passenden Beschriftung?

Je Netzbetreiber wird der gespeicherte Dokumenttext in Zeilen zerlegt. Eine Beschriftung (auch über bis zu zwei Zeilen verteilt) wird einer Ebene zugeordnet:
  hs    Hochspannung (Netz)            -> nicht in unserer Tabelle
  hsms  Umspannung Hoch-/Mittelspannung, HS/MS, 110/20 kV, "Hochspannung mit Umspannung auf MS"
  ms    Mittelspannung (ohne Umspannung)
  msns  Umspannung Mittel-/Niederspannung, MS/NS
  ns    Niederspannung
Die vier Zahlen der Zeile (Leistungspreis unter, Arbeitspreis unter, Leistungspreis ab, Arbeitspreis ab) werden mit unserem Wert verglichen.
Ausgabe: ergebnis/ebenen_audit.csv (nr; ebene; unser_wert; wert_im_dokument_mit_passender_beschriftung; befund)
Befund: gleich | abweichend | ebene_im_dokument_nicht_gefunden | unser_wert_gehoert_zu_anderer_zeile
Aufruf: PYTHONPATH=. python daten/ebenen_audit.py
"""
import csv, glob, re
from pathlib import Path

K = ("lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh")
ZAHL = re.compile(r"-?\d{1,3}(?:\.\d{3})*,\d+|-?\d+,\d+")


def f(s):
    return float(s.replace(".", "").replace(",", ".")) if s else None


def ebene_von(label: str):
    t = label.lower()
    t = re.sub(r"\s+", " ", t)
    if re.search(r"höchstspannung|hös", t) and not re.search(r"mittel", t):
        return None
    hoch_mittel = re.search(r"hoch\s*-?\s*/?\s*(?:und\s*)?mittel|\bhs\s*/\s*ms\b|\bhsp\s*/\s*msp\b|110\s*(?:kv)?\s*/\s*(?:10|20)|umspann\w*\s*(?:zur|in|auf)?\s*mittelspannung|hochspannung\s*(?:mit|einschl)", t)
    mittel_nieder = re.search(r"mittel\s*-?\s*/?\s*(?:und\s*)?nieder|\bms\s*/\s*ns\b|\bmsp\s*/\s*nsp\b|20\s*kv\s*/\s*0,4|umspann\w*\s*(?:zur|in|auf)?\s*niederspannung|netzstation", t)
    if hoch_mittel and not mittel_nieder:
        return "hsms"
    if mittel_nieder:
        return "msns"
    if re.search(r"hochspannung|\bhs\b", t) and not re.search(r"umspann|mittel", t):
        return "hs"
    if re.search(r"niederspannung|\bnsp?\b|\bnetzebene\s*7\b", t) and not re.search(r"umspann|mittel", t):
        return "ns"
    if re.search(r"mittelspannung|\bmsp?\b|\bnetzebene\s*5\b", t) and not re.search(r"umspann", t):
        return "ms"
    if re.search(r"umspann", t):
        return "umspannung?"
    return None


def zeilen_des_dokuments(L):
    """Liefert [(ebene, (4 Zahlen), Beschriftung)] für Zeilen mit vier Preiszahlen; Beschriftung ggf. aus den beiden Zeilen davor/danach."""
    out = []
    for i, l in enumerate(L):
        nums = ZAHL.findall(l)
        if len(nums) < 4:
            continue
        vals = tuple(f(x) for x in nums[:4])
        label = re.split(r"\s{2,}|\d", l.strip(), 1)[0]
        for ctx in (label, " ".join(L[max(0, i - 1):i] + [label]), " ".join(L[max(0, i - 2):i] + [label]), " ".join([label] + L[i + 1:i + 2]), " ".join([label] + L[i + 1:i + 3])):
            eb = ebene_von(ctx)
            if eb:
                out.append((eb, vals, ctx.strip()))
                break
    return out


def main():
    N = list(csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";"))
    erg = []
    for r in N:
        fs = glob.glob(f"ergebnis/texte_layout/{r['mastr_nr']}_*.txt") + glob.glob(f"ergebnis/texte/{int(r['nr']):04d}.txt")
        if not fs:
            continue
        L = [re.sub(r"\s{2,}", "  ", x.strip()) for x in Path(fs[0]).read_text(encoding="utf8", errors="replace").split("\n") if x.strip()]
        doc = zeilen_des_dokuments(L)
        if not doc:
            continue
        for eb in ("hsms", "ms", "msns", "ns"):
            ours = tuple(f(r[f"{eb}_{k}"]) for k in K)
            if None in ours:
                continue
            gleiche = [d for d in doc if d[0] == eb and all(abs(a - b) < 0.006 for a, b in zip(d[1], ours))]
            if gleiche:
                befund, ref = "gleich", gleiche[0][1]
            else:
                passende = [d for d in doc if d[0] == eb]
                andere = [d for d in doc if all(abs(a - b) < 0.006 for a, b in zip(d[1], ours))]
                if andere:
                    befund, ref = "unser_wert_gehoert_zu_anderer_zeile:" + andere[0][0] + " (" + andere[0][2][:40] + ")", (passende[0][1] if passende else "")
                elif passende:
                    befund, ref = "abweichend", passende[0][1]
                else:
                    befund, ref = "ebene_im_dokument_nicht_gefunden", ""
            erg.append([r["nr"], r["netzbetreiber"][:30], r["status"], eb, "/".join(str(x) for x in ours), "/".join(str(x) for x in ref) if ref else "", befund])
    with open("ergebnis/ebenen_audit.csv", "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["nr", "netzbetreiber", "status", "ebene", "unser_wert", "wert_im_dokument_mit_passender_beschriftung", "befund"])
        w.writerows(erg)
    from collections import Counter
    c = Counter(e[6].split(":")[0] for e in erg)
    print(dict(c))
    return erg


if __name__ == "__main__":
    main()
