"""Ergänzt die Datei des Nutzers (gleiche Zeilen, gleiche 48 Spalten) um Werte aus unserer Auswertung. Nur LEERE Felder werden gefüllt,
vorhandene Werte bleiben unverändert. Zuordnung über den Namen. Ergänzt: SLP, Ebenen (ms, msns, ns, hsms), Grenze, Preisstand, Stand,
abgeleitete ct/kWh-Spalten, Hochlastzeitfenster (aus ergebnis/hlzf_ergebnis.csv). Der Hinweis nennt, was ergänzt wurde."""
import csv, glob, re, collections, sys, unicodedata
from pathlib import Path
W = Path(__file__).parent.parent
sys.path.insert(0, str(W))
from vnb.ergebnis import Speicher, SPALTEN
def n(s):
    s = unicodedata.normalize("NFKD", (s or "").lower()).encode("ascii", "ignore").decode().replace("&", " ").replace("oe", "o").replace("ae", "a").replace("ue", "u")
    s = re.sub(r"\b(gmbh|co|kg|ag|mbh|ku|aor|eg|e\.?g\.?|eigenbetrieb|stadtwerke|stadtwerk|netz|netze|strom|und|gas|der|stadt)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", "", s)
def f(x):
    try: return float((x or "").replace(",", "."))
    except ValueError: return None
def de(v): return f"{v:.2f}".replace(".", ",")
K = ("lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh")
quelle = sorted(glob.glob(str(W / "daten" / "format_neu_final_alle_nutzer_*.csv")))[-1]
roh = open(quelle, encoding="utf-8-sig", newline="").read()
reader = csv.reader(roh.splitlines(), delimiter=";"); H = next(reader); R = [dict(zip(H, z)) for z in reader]
O = [dict(zip(SPALTEN, Speicher.zeile(d))) for d in Speicher(W / "ergebnis").daten.values()]
O = [{k: ("" if v is None else str(v)) for k, v in o.items()} for o in O]
idx = collections.defaultdict(list)
for o in O: idx[n(o["netzbetreiber"])].append(o)
HL = {x["nr"]: x for x in csv.DictReader(open(W / "ergebnis" / "hlzf_ergebnis.csv", encoding="utf-8-sig"), delimiter=";")
      if x["hlzf_status"] == "gelesen" and x["hlzf_jahr"] == "2026"}        # nur Dokumente, die ausdrücklich für 2026 gelten
def ct(w, h, le=False):
    if None in w: return None
    return w[3] + w[2] * 100 / h if (h >= 2500 if not le else h > 2500) else w[1] + w[0] * 100 / h
c = collections.Counter()
for r in R:
    m = idx.get(n(r["netzbetreiber"]))
    if not m or len(m) > 1: c["nicht eindeutig zugeordnet"] += 1; continue
    o = m[0]; neu = []
    for k in ("slp_ap_ct_kwh", "slp_grundpreis_eur_jahr"):
        if not r[k].strip() and o.get(k, "").strip(): r[k] = o[k]; neu.append("SLP") if k == "slp_ap_ct_kwh" else None
    for e in ("ms", "msns", "ns", "hsms"):
        if all(not r[f"{e}_{k}"].strip() for k in K) and all(o.get(f"{e}_{k}", "").strip() for k in K):
            for k in K: r[f"{e}_{k}"] = o[f"{e}_{k}"]
            neu.append(e.upper())
    for k in ("grenze_2500h", "preisstand", "stand_datum"):
        if not r[k].strip() and o.get(k, "").strip(): r[k] = o[k]
    le = r["grenze_2500h"].startswith("≤")
    for e, hs in (("ms", (1500, 2500, 4000, 6000)), ("msns", (4000,)), ("ns", (4000,))):
        w = [f(r[f"{e}_{k}"]) for k in K]
        for h in hs:
            col = f"{e}_ct_kwh_bei_{h}h"
            if not r[col].strip() and None not in w: r[col] = de(ct(w, h, le))
    hl = HL.get(o["nr"])
    if hl and all(not r[x].strip() for x in ("hlzf_ns_fruehling", "hlzf_ns_winter", "hlzf_msns_winter")):
        for x in [y for y in H if y.startswith("hlzf_") and y != "hlzf_quelle_url"] + ["hlzf_quelle_url"]:
            if not r[x].strip() and hl.get(x, "").strip(): r[x] = hl[x]
        neu.append("Hochlastzeitfenster")
    if neu:
        c["Zeilen ergänzt"] += 1
        for x in dict.fromkeys(neu): c[f"ergänzt: {x}"] += 1
        r["hinweis"] = (r["hinweis"] + "; " if r["hinweis"] else "") + "ergänzt aus unserer Auswertung: " + ", ".join(dict.fromkeys(neu))
ziel = W / "ergebnis" / "FORMAT_NEU_netzentgelte_final_alle_3_ergaenzt.csv"
with open(ziel, "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.writer(fh, delimiter=";", lineterminator="\r\n"); w.writerow(H); [w.writerow([r[h] for h in H]) for r in R]
print(len(R), "Zeilen;", dict(c))
voll = lambda r: all(r[f"{e}_lp_ab_2500h_eur_kw_jahr"].strip() for e in ("ms", "msns", "ns")) and r["slp_ap_ct_kwh"].strip()
print("Zeilen mit SLP, MS, MS/NS, NS:", sum(1 for r in R if voll(r)), "| mit Hochlastzeitfenster:", sum(1 for r in R if r["hlzf_ns_winter"].strip()))
