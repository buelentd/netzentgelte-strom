"""Prüft jeden gelesenen Preisblock (ns, msns, ms, hsms: je vier Werte) gegen die Dokumentzeilen und schreibt die nicht bestätigten nach ergebnis/preise_nicht_bestaetigt.csv.
Bestätigt = im Dokumenttext steht in einer Zeile (oder zwei aufeinanderfolgenden) mit dem Ebenennamen jeder der vier Werte.
Aufruf: PYTHONPATH=. python daten/preise_bestaetigung.py"""
import csv, glob, re, collections
t = list(csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";"))
de = lambda v: float(v.replace(".", "").replace(",", ".")) if v else None
K = ("lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh")
Z = re.compile(r"\d{1,3}(?:\.\d{3})*,\d{1,4}")
LAB = {"ms": r"mittelspannung|\bms\b", "msns": r"umspann|ms\s*/\s*ns|mittel.{0,12}nieder", "ns": r"niederspannung|\bns\b", "hsms": r"hoch.{0,15}mittel|hs\s*/\s*ms"}
NAME = {"ns": "Niederspannung", "msns": "MS/NS", "ms": "Mittelspannung", "hsms": "HS/MS"}
zahlen = lambda l: [de(m) for m in Z.findall(l)]
EBENE_ID = {"7": "ns", "6": "msns", "5": "ms", "4": "hsms"}

def artikel(L):
    """BDEW-Artikel-IDs: {(ebene, 1..4): [Zahlen der Zeile]} (eine Zeile je Wert: 1-01-7-001 ... 8,39 9,98 €/kW/a)."""
    d = {}
    for i, l in enumerate(L):
        m = re.search(r"(?<!\d)1-01-(\d)-0*(\d)(?!\d)", l)
        if m and m.group(1) in EBENE_ID and m.group(2) in "1234":
            zs = zahlen(l) or zahlen(L[i + 1] if i + 1 < len(L) else "")
            d.setdefault((EBENE_ID[m.group(1)], int(m.group(2))), zs)
    return d
zaehler = collections.Counter()
out = []
for x in t:
    fs = glob.glob(f"ergebnis/texte_layout/{x['mastr_nr']}_{int(x['nr']):04d}.txt")
    L = open(fs[0], errors="ignore").read().splitlines() if fs else None
    for eb in ("ns", "msns", "ms", "hsms"):
        v = [de(x[f"{eb}_{k}"]) for k in K]
        if None in v:
            continue
        if L is None:
            zaehler["kein Text"] += 1
            out.append([x["nr"], x["netzbetreiber"], NAME[eb], *[f"{a:.2f}".replace(".", ",") for a in v], x["status"], "kein Text zum Abgleich (Wert aus der Liste des Nutzers)", "", ""]); continue
        beste, treffer = "", -1
        bestaetigt = False
        art = artikel(L)
        if all((eb, n) in art for n in (1, 2, 3, 4)):
            bestaetigt = all(any(abs(a - b) < 0.011 for b in art[(eb, n)]) for n, a in enumerate(v, 1))
            if bestaetigt:
                zaehler["bestätigt"] += 1; continue
            beste, treffer = "Artikel-IDs: " + " | ".join(f"{n}: {art[(eb, n)][:3]}" for n in (1, 2, 3, 4)), 0
        for i, l in enumerate(L):
            if not re.search(LAB[eb], l, re.I):
                continue
            for text in (l, l + " " + (L[i + 1] if i + 1 < len(L) else "")):
                zs = zahlen(text)
                n = sum(1 for a in v if any(abs(a - b) < 0.011 for b in zs))
                if n > treffer:
                    beste, treffer = text, n
                if n == 4:
                    bestaetigt = True; break
            if bestaetigt:
                break
        if not bestaetigt:
            # LP-Tabelle und AP-Tabelle getrennt: (LP unter, LP ab) in einer Zeile mit dem Ebenennamen, (AP unter, AP ab) in einer anderen
            def paar(a1, a2):
                for i2, l2 in enumerate(L):
                    if re.search(LAB[eb], l2, re.I):
                        for text in (l2, l2 + " " + (L[i2 + 1] if i2 + 1 < len(L) else "")):
                            zs2 = zahlen(text)
                            if any(abs(a1 - b) < 0.011 for b in zs2) and any(abs(a2 - b) < 0.011 for b in zs2):
                                return True
                return False
            bestaetigt = (paar(v[0], v[2]) and paar(v[1], v[3])) or (paar(v[0], v[1]) and paar(v[2], v[3]))        # LP/AP getrennt oder unter/ab getrennt
        if bestaetigt:
            zaehler["bestätigt"] += 1; continue
        zaehler["nicht bestätigt"] += 1
        art = "Ebenenzeile im Dokument nicht gefunden" if treffer < 0 else f"nächste Zeile hat {treffer} von 4 Werten"
        out.append([x["nr"], x["netzbetreiber"], NAME[eb], *[f"{a:.2f}".replace(".", ",") for a in v], x["status"], art, " ".join(beste.split())[:170], fs[0].split("/")[-1]])
out.sort(key=lambda r: (r[8].startswith("kein Text"), int(r[0])))
with open("ergebnis/preise_nicht_bestaetigt.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["nr", "netzbetreiber", "ebene", "lp_unter", "ap_unter", "lp_ab", "ap_ab", "status", "grund", "naechste_dokumentzeile", "textdatei"])
    w.writerows(out)
print(dict(zaehler))
