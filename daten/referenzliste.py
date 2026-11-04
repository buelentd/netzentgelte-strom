"""Referenzliste: Ebenen unserer Tabelle, die am Dokumenttext (ergebnis/texte/NNNN.txt) bestätigt sind:
alle vier Werte (ab 2.500 h) in einer Zeile UND der Zeilenname (Zeile oder vorherige nichtleere Zeile) ergibt dieselbe Ebene.
Aufruf: PYTHONPATH=. python daten/referenzliste.py  ->  ergebnis/referenzliste_bestaetigt.csv"""
import csv, re
from pathlib import Path
from vnb.extract import ebene, ebene_mshs

SP = ["lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh"]
EB = ["ms", "msns", "ns", "hsms"]

def z(v):
    try: return float(v.replace(",", "."))
    except Exception: return None

def formen(v):
    return {f"{v:.2f}".replace(".", ","), f"{v:.1f}".replace(".", ","), f"{v:.0f}"}

def hat(l, v):
    return any(re.search(r"(?<![\d,.])" + re.escape(s) + r"(?![\d])", l) for s in formen(v))

def ebene_von(label):
    lab = ebene_mshs(label) or ebene(label)
    return {"MS": "ms", "MSNS": "msns", "NS": "ns", "HSMS": "hsms"}.get(lab)

def bestaetigt(L, eb, w):
    for i, l in enumerate(L):
        if all(hat(l, v) for v in w[2:]):
            lab = re.sub(r"[\d.,€/*()%-]+", " ", re.sub(r"\(\s*\d[\d.,]*\s*\)", " ", l)).strip()
            k = i
            while len(re.sub(r"\W", "", lab)) < 5 and k > 0:
                k -= 1; lab = L[k].strip()
            nah = any(all(hat(L[j], v) for v in w[:2]) for j in range(max(0, i - 1), min(len(L), i + 2))) or all(hat(l, v) for v in w[:2])
            if ebene_von(lab) == eb and nah: return True
    return False

def main():
    out = []
    for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";"):
        p = Path(f"ergebnis/texte/{int(r['nr']):04d}.txt")
        if not p.exists(): continue
        L = p.read_text(encoding="utf8").split("\n")
        ok, offen, werte = [], [], []
        for eb in EB:
            w = [z(r[f"{eb}_{s}"]) for s in SP]
            if any(x is None for x in w): continue
            (ok if bestaetigt(L, eb, w) else offen).append(eb)
            werte.append(f"{eb}=" + "/".join(r[f"{eb}_{s}"] for s in SP))
        if ok: out.append([r["nr"], r["netzbetreiber"], r["status"], ",".join(ok), ",".join(offen), " | ".join(werte)])
    with open("ergebnis/referenzliste_bestaetigt.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(["nr_bei_uns", "netzbetreiber", "status", "ebenen_bestaetigt", "ebenen_nicht_bestaetigt", "werte"]); w.writerows(out)
    voll = sum(1 for o in out if not o[4])
    print(len(out), "Netzbetreiber mit mind. einer bestätigten Ebene,", voll, "mit allen vorhandenen Ebenen bestätigt")
main()
