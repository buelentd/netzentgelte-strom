"""Prüft unsere Werte gegen den Dokumenttext (ergebnis/texte/NNNN.txt): steht die Zeile mit LP/AP ab 2.500 h unter dem richtigen
Ebenennamen, stehen die Werte unter 2.500 h in derselben/benachbarten Zeile, stimmt die ct/kWh-Reihenfolge, und liefert
der aktuelle Leser dasselbe wie die Tabelle? Aufruf: python daten/ergebnis_pruefen.py 6,10,23"""
import csv, re, sys, tempfile
from pathlib import Path
from vnb.extract import auswerten

SP = ["lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh"]
KURZ = ["lp_unter_2500", "ap_unter_2500", "lp_ueber_2500", "ap_ueber_2500"]
NAME = {"ms": r"mittelspannung|\bms\b|msp", "msns": r"umspann|ms/ns|mittel.{0,12}nieder|msp.{0,4}nsp", "ns": r"nieder|\bns\b|nsp"}

def z(v):
    try: return float(v.replace(",", "."))
    except Exception: return None

def formen(v):
    return {f"{v:.2f}".replace(".", ","), f"{v:.1f}".replace(".", ","), f"{v:.0f}", f"{v/365:.6f}".replace(".", ",")[:8], f"{v:.2f}"}

def hat(l, v):
    return any(re.search(r"(?<![\d,.])" + re.escape(s) + r"(?![\d])", l) for s in formen(v))

def pruefen(nr, row):
    pfad = Path(f"ergebnis/texte/{nr:04d}.txt")
    if not pfad.exists(): return ["kein Text"]
    L = pfad.read_text(encoding="utf8").split("\n")
    out = []
    frisch = {}
    d = Path(tempfile.mkdtemp()); p = d / "a.html"; p.write_text("\n".join(L), encoding="utf8")
    try: e = auswerten(p, "https://x.de/a.pdf", 2026)
    except Exception as ex: e = None; out.append(f"Leser-Fehler {ex}")
    ct = {}
    for eb in ("ms", "msns", "ns"):
        w = [z(row[f"{eb}_{s}"]) for s in SP]
        if any(x is None for x in w):
            out.append(f"{eb}: leer"); continue
        ct[eb] = w[3] + w[2] * 100 / 4000
        idx = [i for i, l in enumerate(L) if hat(l, w[2]) and hat(l, w[3])]
        if not idx: out.append(f"{eb}: Zeile ab-Werte NICHT gefunden"); continue
        i = idx[0]
        lab = " ".join(L[max(0, i - 3): i + 1]).lower()
        passt = bool(re.search(NAME[eb], lab))
        fremd = eb != "msns" and bool(re.search(r"hoch|hs/|umspann", re.sub(r"umspannung mittel|umspannung ms|umspannung msp", "", lab)))
        unter = any(hat(L[j], w[0]) and hat(L[j], w[1]) for j in range(max(0, i - 4), min(len(L), i + 5)))
        out.append(f"{eb}: Ebenenname {'ok' if passt and not fremd else 'PRUEFEN'}, unter-Werte nah {'ok' if unter else 'NICHT gefunden'}")
        if e is not None:
            n = getattr(e, eb)
            if n:
                neu = [round(n[k], 2) for k in KURZ]
                if any(abs(a - b) > 0.006 for a, b in zip(neu, w)): out.append(f"   Leser jetzt anders: {neu} statt {w}")
    if len(ct) == 3 and not (ct["ms"] <= ct["msns"] * 1.05 and ct["msns"] <= ct["ns"] * 1.25): out.append("ct-Reihenfolge verletzt")
    return out

if __name__ == "__main__":
    nrn = [int(x) for x in sys.argv[1].split(",")]
    R = {int(r["nr"]): r for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
    for n in nrn:
        r = R[n]; print(f"{n} {r['netzbetreiber'][:28]} [{r['status']}]")
        for x in pruefen(n, r): print("   ", x)
