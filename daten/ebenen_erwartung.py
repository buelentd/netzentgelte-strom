"""Je Netzbetreiber und Ebene: gelesen | im_dokument_nicht_gelesen | nicht_ausgewiesen | kein_dokument.
'im_dokument_nicht_gelesen' = im Text steht eine Zeile mit dem Ebenennamen und mindestens drei Zahlen, der Leser hat aber keinen Wert (Leser-Lücke).
'nicht_ausgewiesen' = Dokument vorhanden und gelesen, aber keine solche Zeile (die Ebene wird dort nicht ausgewiesen).
Aufruf: PYTHONPATH=. python daten/ebenen_erwartung.py -> ergebnis/ebenen_erwartung.csv"""
import csv, glob, re
from pathlib import Path
from vnb.extract import ebene, ebene_mshs

SP = ["lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh"]
EB = ["ms", "msns", "ns", "hsms"]
ZAHL = re.compile(r"\d+[.,]\d+")
MAP = {"MS": "ms", "MSNS": "msns", "NS": "ns", "HSMS": "hsms"}

def text_zu(r):
    f = glob.glob(f"ergebnis/texte_layout/{r['mastr_nr']}_*.txt")
    if f: return Path(f[0]).read_text(encoding="utf8", errors="replace")
    f = glob.glob(f"ergebnis/texte/{int(r['nr']):04d}.txt")
    return Path(f[0]).read_text(encoding="utf8", errors="replace") if f else None

def ausgewiesen(zeilen):
    ebs = set()
    for i, l in enumerate(zeilen):
        if len(ZAHL.findall(l)) < 3: continue
        lab = re.sub(r"[\d.,€/*()%-]+", " ", l).strip()
        k = i
        while len(re.sub(r"\W", "", lab)) < 5 and k > 0:
            k -= 1; lab = zeilen[k].strip()
        e = ebene_mshs(lab) or ebene(lab)
        if e in MAP: ebs.add(MAP[e])
    return ebs

def main():
    out, zaehl = [], {}
    for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";"):
        t = text_zu(r)
        z = ausgewiesen(t.split("\n")) if t else None
        zeile = [r["mastr_nr"], r["nr"], r["netzbetreiber"], r["status"]]
        for eb in EB:
            hat = all(r[f"{eb}_{s}"] for s in SP)
            if hat: st = "gelesen"
            elif z is None: st = "kein_dokument"
            elif eb in z: st = "im_dokument_nicht_gelesen"
            else: st = "nicht_ausgewiesen"
            zeile.append(st); zaehl[(eb, st)] = zaehl.get((eb, st), 0) + 1
        slp = "gelesen" if r["slp_ap_ct_kwh"] and r["slp_grundpreis_eur_jahr"] else ("kein_dokument" if z is None else "fehlt")
        zeile.append(slp); zaehl[("slp", slp)] = zaehl.get(("slp", slp), 0) + 1
        out.append(zeile)
    with open("ergebnis/ebenen_erwartung.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(["mastr_nr", "nr", "netzbetreiber", "status", "ms", "msns", "ns", "hsms", "slp"]); w.writerows(out)
    for eb in EB + ["slp"]:
        print(eb, {k[1]: v for k, v in sorted(zaehl.items()) if k[0] == eb})
main()
