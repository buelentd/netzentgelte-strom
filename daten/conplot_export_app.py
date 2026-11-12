"""Export im Layout von app/data/netzentgelte_2026.json (Conplot-Web-App): {"jahr","quelle","erzeugt_mit","betreiber":{MaStR-Nr: {...}}}.
Quelle: ergebnis/netzentgelte_2026.csv (Preise) und lauf/hlzf_zusammen.csv (Hochlastzeitfenster, aktueller Stand mit Status).
Ausgabe: ergebnis/conplot/netzentgelte_2026_app.json. Aufruf: PYTHONPATH=. python daten/conplot_export_app.py"""
import csv, json
from pathlib import Path

J = ("fruehling", "sommer", "herbst", "winter")
FERTIG = ("gelesen_nutzer", "gelesen_unser", "gelesen_kollege_verifiziert", "gelesen_aus_2027")


def lesen(p):
    return list(csv.DictReader(open(p, encoding="utf-8-sig"), delimiter=";"))


def zahl(s):
    s = (s or "").strip()
    if not s:
        return None
    try:
        return float(s.replace(".", "").replace(",", ".")) if "," in s else float(s)
    except ValueError:
        return None


def main():
    T = lesen("ergebnis/netzentgelte_2026.csv")
    H = {r["mastr_nr"]: r for r in lesen("lauf/hlzf_zusammen.csv")}
    out = {}
    for t in T:
        mn = t["mastr_nr"]
        eb = {}
        for e in ("hsms", "ms", "msns", "ns"):
            w = {k: zahl(t.get(f"{e}_{c}")) for k, c in (("lp_unter", "lp_unter_2500h_eur_kw_jahr"), ("ap_unter", "ap_unter_2500h_ct_kwh"), ("lp_ab", "lp_ab_2500h_eur_kw_jahr"), ("ap_ab", "ap_ab_2500h_ct_kwh"))}
            if all(v is not None for v in w.values()):
                eb[e] = w
        h = H.get(mn, {})
        hl = {}
        if h.get("hlzf_status") in FERTIG:
            for e in ("ns", "msns"):
                d = {s: h[f"hlzf_{e}_{s}"] for s in J if h.get(f"hlzf_{e}_{s}")}
                if d:
                    hl[e] = d
        out[mn] = {
            "name": t["netzbetreiber"], "status": t["status"], "bundesland": t.get("bundesland", ""), "netztyp": t.get("netztyp", ""),
            "grenze_inklusiv": "≤" in (t.get("grenze_2500h") or ""),
            "ebenen": eb, "hlzf": hl, "hlzf_status": h.get("hlzf_status") or None,
            "hlzf_schwelle_prozent": zahl(h.get("hlzf_schwelle_prozent")), "hlzf_mindestleistung_kw": zahl(h.get("hlzf_mindestleistung_kw")),
            "hlzf_quelle": h.get("hlzf_quelle_url") or None,
            "preisstand": t.get("preisstand") or None, "stand": t.get("stand_datum") or None, "quelle": t.get("quelle_url") or None,
        }
    doc = {"jahr": 2026, "quelle": "Preisblaetter der Netzbetreiber (Erhebung), MaStR", "erzeugt_mit": "daten/conplot_export_app.py (netzentgelte-strom)", "betreiber": out}
    Path("ergebnis/conplot/netzentgelte_2026_app.json").write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    n = len(out)
    print({"betreiber": n, "mit_ns": sum(1 for v in out.values() if "ns" in v["ebenen"]), "mit_hlzf": sum(1 for v in out.values() if v["hlzf"])})


main()
