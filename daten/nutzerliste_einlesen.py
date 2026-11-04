"""Liste des Nutzers (daten/format_neu_final_alle_nutzer_*.csv) in lauf/preise_manuell.csv übernehmen.
Zuordnung über den Namen (die Nummern der Liste sind nicht unsere). Regel: Lücken füllen, bereits gelesene und abweichende Werte
nicht überschreiben; Abweichungen stehen in ergebnis/abweichungen_nutzerliste.csv zur Prüfung."""
import csv, glob, re, collections, unicodedata
from pathlib import Path
W = Path(__file__).parent.parent
def n(s):
    s = unicodedata.normalize("NFKD", (s or "").lower()).encode("ascii", "ignore").decode().replace("&", " ").replace("oe", "o").replace("ae", "a").replace("ue", "u")
    s = re.sub(r"\b(gmbh|co|kg|ag|mbh|ku|aor|eg|e\.?g\.?|eigenbetrieb|stadtwerke|stadtwerk|netz|netze|strom|und|gas|der|stadt)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", "", s)
def f(x):
    try: return float((x or "").replace(",", "."))
    except ValueError: return None
K = ("lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh")
U = list(csv.DictReader(open(sorted(glob.glob(str(W / "daten" / "format_neu_final_alle_nutzer_*.csv")))[-1], encoding="utf-8-sig"), delimiter=";"))
O = list(csv.DictReader(open(W / "ergebnis" / "netzentgelte_2026.csv", encoding="utf-8"), delimiter=";"))
idx = collections.defaultdict(list)
for o in O: idx[n(o["netzbetreiber"])].append(o)
H = ["nr", "netzbetreiber", "preisstand", "stand_datum", *[f"{e}_{k}" for e in ("ms", "msns", "ns", "hsms") for k in K], "slp_ap_ct_kwh", "slp_grundpreis_eur_jahr", "grenze_2500h", "quelle_url", "hinweis"]
aus, abw, c = [], [], collections.Counter()
for r in U:
    m = idx.get(n(r["netzbetreiber"]))
    if not m or len(m) > 1: c["nicht eindeutig zugeordnet"] += 1; continue
    o = m[0]; row = dict.fromkeys(H, ""); row.update(nr=o["nr"], netzbetreiber=o["netzbetreiber"], stand_datum=r["stand_datum"], quelle_url=r["quelle_url"], hinweis="Quelle: Liste des Nutzers 04.11.2026")
    neu = 0
    for e in ("ms", "msns", "ns", "hsms"):
        u = [f(r[f"{e}_{k}"]) for k in K]; v = [f(o[f"{e}_{k}"]) for k in K]
        if None in u: continue
        if None in v:
            for k, x in zip(K, u): row[f"{e}_{k}"] = str(x).replace(".", ","); 
            neu += 1; c[f"{e} ergänzt"] += 1
        elif any(abs(a - b) > 0.011 for a, b in zip(u, v)):
            c[f"{e} Abweichung"] += 1; abw.append([o["nr"], o["netzbetreiber"], e, " | ".join(map(str, v)), " | ".join(map(str, u)), r["quelle_url"]])
    sa, sg = f(r["slp_ap_ct_kwh"]), f(r["slp_grundpreis_eur_jahr"])
    if sa is not None and sg is not None and not f(o["slp_ap_ct_kwh"]):
        row["slp_ap_ct_kwh"], row["slp_grundpreis_eur_jahr"] = str(sa).replace(".", ","), str(sg).replace(".", ","); neu += 1; c["SLP ergänzt"] += 1
    if neu: aus.append([row[h] for h in H])
csv.writer(open(W / "lauf" / "preise_manuell.csv", "w", encoding="utf-8", newline=""), delimiter=";").writerows([H] + aus)
csv.writer(open(W / "ergebnis" / "abweichungen_nutzerliste.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";").writerows([["nr", "netzbetreiber", "ebene", "unser_wert_lp_unter|ap_unter|lp_ab|ap_ab", "wert_nutzerliste", "quelle_url"]] + abw)
print(dict(c), "| Zeilen in preise_manuell.csv:", len(aus), "| Abweichungen:", len(abw))
