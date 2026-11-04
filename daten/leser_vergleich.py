"""Vergleich: Leser des Nutzers (parsed_verified.json) gegen unseren Leser (ergebnis/netzentgelte_2026.csv).
Aufruf: python daten/leser_vergleich.py <parsed_verified.json> [<queue.json>]
Zuordnung über den Namen. Ausgabe: ergebnis/vergleich_leser.csv
"""
import csv, json, re, sys
from pathlib import Path

def norm(s):
    s = s.lower()
    for a, b in (("ä","ae"),("ö","oe"),("ü","ue"),("ß","ss")): s = s.replace(a, b)
    s = re.sub(r"\b(gmbh|ag|kg|mbh|co|und|&|netz|netze|netzgesellschaft|verteilnetz|stadtwerke)\b", " ", s)
    return re.sub(r"[^a-z0-9]", "", s)

def zahl(v):
    try: return float(str(v).replace(",", "."))
    except ValueError: return None

EB = {"ms": "ms", "msns": "msns", "ns": "ns", "hsms": "hsms"}
SP = ["lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh"]

def main():
    pv = json.load(open(sys.argv[1], encoding="utf8"))
    unser = {}
    with open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f, delimiter=";"):
            unser.setdefault(norm(r["netzbetreiber"]), []).append(r)
    out, z = [], {"gleich": 0, "abweichend": 0, "nur_nutzer": 0, "nur_unser": 0, "kein_paar": 0}
    for rec in pv:
        zeilen = unser.get(norm(rec["nb"]))
        if not zeilen: z["kein_paar"] += 1; continue
        u = zeilen[0]
        for eb in EB:
            n = (rec.get("levels") or {}).get(eb)
            uw = [zahl(u.get(f"{eb}_{s}")) for s in SP]
            uh = all(x is not None for x in uw)
            if n and uh:
                gl = all(abs(a - b) < 0.006 for a, b in zip(n, uw)); k = "gleich" if gl else "abweichend"
            elif n: k = "nur_nutzer"
            elif uh: k = "nur_unser"
            else: continue
            z[k] += 1
            out.append([u["nr"], u["netzbetreiber"], eb, k, rec.get("conf"), u["status"],
                        ";".join(map(str, n or [])), ";".join(map(str, uw)) if uh else ""])
    with open("ergebnis/vergleich_leser.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(["nr","netzbetreiber","ebene","ergebnis","nutzer_conf","unser_status","werte_nutzer","werte_unser"]); w.writerows(out)
    print(z)
main()
