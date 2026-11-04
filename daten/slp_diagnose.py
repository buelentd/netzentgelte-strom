"""Diagnose ohne Internet: für Netzbetreiber mit RLM-Werten, aber ohne SLP-Preise, alle schon geladenen Dokumente
(ergebnis/cache/<key>/) durchsehen. Je Dokument: Quelle, Jahre im Kopf und im Text (2026 und 2027!), Preisstand,
Zahl der SLP-Wörter und die ersten Textzeilen dazu. Ergebnis: ergebnis/slp_diagnose.csv. Nur maschinelles Auslesen."""
import csv, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from vnb.extract import auswerten

W = Path(__file__).parent.parent
SLP = re.compile(r"standardlast|ohne\s+leistungsmessung|nicht\s+leistungsgemessen|\bSLP\b|Haushalt|Grundpreis|Arbeitspreis|Messstellenbetrieb", re.I)


def main():
    liste = W / "lauf" / "slp_diagnose.liste"      # Nummern, durch Komma getrennt; sonst Filter
    nrs = set(liste.read_text().strip().split(",")) if liste.exists() and liste.read_text().strip() else None
    z = [r for r in csv.DictReader(open(W / "ergebnis" / "netzentgelte_2026.csv", encoding="utf-8"), delimiter=";")
         if (r["nr"] in nrs if nrs else r["status"] == "pruefen" and r["ns_lp_ueber_2500h_eur_kw_jahr"] and not r["slp_ap_ct_kwh"])]
    (W / "ergebnis" / "slp_diagnose").mkdir(exist_ok=True)
    key = {}
    for l in open(W / "ergebnis" / "fortschritt.jsonl", encoding="utf-8"):
        try:
            o = json.loads(l)
            key[str(o["nr"])] = o["key"]
        except Exception:
            pass
    aus = csv.writer(open(W / "ergebnis" / "slp_diagnose.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";")
    aus.writerow(["nr", "netzbetreiber", "url", "kopf_jahre", "text_jahre", "gueltig_jahre", "preisstand",
                  "slp_ap", "slp_gp", "ns_lp_ueber", "slp_woerter", "slp_zeilen"])
    n = 0
    for r in z:
        d = W / "ergebnis" / "cache" / key.get(r["nr"], "?")
        if not d.is_dir():
            aus.writerow([r["nr"], r["netzbetreiber"], "kein Zwischenspeicher"] + [""] * 9)
            continue
        for u in sorted(d.glob("*.url")):
            datei = next((p for p in d.glob(u.stem + ".*") if p.suffix != ".url"), None)
            url = u.read_text().strip()
            if not datei:
                continue
            try:
                e = auswerten(datei, url, 2026)
            except Exception as ex:
                aus.writerow([r["nr"], r["netzbetreiber"], url, f"nicht lesbar: {type(ex).__name__}"] + [""] * 8)
                continue
            alle = e.text.splitlines()
            zeilen = [re.sub(r"\s+", " ", t).strip()[:110] for t in alle if SLP.search(t)]
            treffer = [i for i, t in enumerate(alle) if SLP.search(t)]
            keep = sorted({j for i in treffer for j in range(max(0, i - 2), min(len(alle), i + 3))})[:80]
            with open(W / "ergebnis" / "slp_diagnose" / f"{r['nr']}.txt", "a", encoding="utf-8") as f:
                f.write(f"### {r['netzbetreiber']} | {url}\n" + "\n".join(re.sub(r"\s+", " ", alle[j]).strip()[:140] for j in keep) + "\n\n")
            slp = e.slp or {}
            aus.writerow([r["nr"], r["netzbetreiber"], url, sorted(e.kopf_jahre), sorted(e.jahre), sorted(e.gueltig_jahre),
                          e.preisstand, slp.get("ap", ""), slp.get("gp", ""), (e.ns or {}).get("lp_ueber_2500", ""),
                          len(zeilen), " | ".join(zeilen[:6])])
            n += 1
    print(len(z), "Netzbetreiber,", n, "Dokumente")


main()
