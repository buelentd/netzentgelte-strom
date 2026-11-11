"""Netzentgelte 2027 (vorläufig, § 20 Abs. 1 Satz 2 EnWG): erste Tabelle wie ergebnis/netzentgelte_2026.csv, MaStR-Nr. zuerst.
Quellen: eingang/2027_vorlaeufig/ (Dateien, Zuordnung über MaStR-Nr. im Namen oder führende nr) und lauf/quellen_2027.csv (Art „Dokument“, wird geladen und dort abgelegt).
Gelesen wird mit demselben Leser wie 2026 (vnb/extract.py). Nur Dokumente, in denen 2027 steht. Seiten/Startseiten ohne Dokument werden nur als Quelle vermerkt.
Status: gelesen (NS oder MS/NS vollständig, plausibel) | teilweise | pruefen (Plausibilität verletzt) | quelle_seite | kein_blatt_2027. Preisstand immer „vorläufig“.
Aufruf: PYTHONPATH=. python daten/netzentgelte_2027.py [--nur-lokal]"""
import csv, glob, os, re, sys, time, threading, warnings
from pathlib import Path
from urllib.parse import urlparse
warnings.filterwarnings("ignore")
sys.path.insert(0, ".")
from vnb.extract import text_aus_datei, tabellen_lesen, slp_lesen, FELDER

W = Path(".")
UA = {"User-Agent": "netzentgelte-strom/1.0 (Datenerfassung Netzentgelte)"}
DEZ = lambda v: f"{v:.2f}".replace(".", ",")
EBENEN = ("ms", "msns", "ns", "hsms")
SUFF = ("lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh")


def lesen_csv(p):
    return list(csv.DictReader(open(p, encoding="utf-8-sig"), delimiter=";"))


def main(nur_lokal=False):
    T = lesen_csv("ergebnis/netzentgelte_2026.csv")
    nr2m = {r["nr"]: r["mastr_nr"] for r in T}
    ordner = W / "eingang" / "2027_vorlaeufig"
    ordner.mkdir(exist_ok=True)
    quellen = {}                    # mastr -> [(url, art)]
    for r in lesen_csv("lauf/quellen_2027.csv"):
        quellen.setdefault(r["mastr_nr"], []).append((r["url"].strip(), r["art_quelle"]))
    # Dokumente laden, die noch nicht liegen
    if not nur_lokal:
        import requests
        letzt, sperre = {}, threading.Lock()
        for m, lst in quellen.items():
            for u, art in lst:
                if art != "Dokument" or not re.search(r"\.(pdf|xlsx?|xlsm)(\?|$)", u, re.I):
                    continue
                nr = next((r["nr"] for r in T if r["mastr_nr"] == m), "0")
                ext = ".xlsx" if re.search(r"\.xls", u, re.I) else ".pdf"
                ziel = ordner / f"{m}_{int(nr):04d}_preis_2027_quelle{ext}"
                if ziel.exists() or glob.glob(str(ordner / f"{m}_*preis*2027*")):
                    continue
                d = urlparse(u).netloc
                w = 1.1 - (time.time() - letzt.get(d, 0))
                if w > 0: time.sleep(w)
                letzt[d] = time.time()
                try:
                    resp = requests.get(u, headers=UA, timeout=30)
                    if resp.status_code == 200 and len(resp.content) > 1000: ziel.write_bytes(resp.content)
                except Exception:
                    pass
    # Dateien je Netzbetreiber
    dateien = {}
    for f in sorted(glob.glob(str(ordner / "*"))):
        b = os.path.basename(f)
        if b.startswith("_") or f.endswith(".csv") or "hlzf" in b.lower() or "hochlast" in b.lower() or "dienstleist" in b.lower() or b.lower().endswith(".txt") and "Merck" not in b:
            continue
        m = re.search(r"SNB\d{12}", b)
        key = m.group(0) if m else nr2m.get((re.match(r"(\d{1,3})_", b) or [None, ""])[1])
        if key: dateien.setdefault(key, []).append(f)
    kopf = ["mastr_nr"] + [h for h in T[0] if h != "mastr_nr" and not h.startswith("hlzf_")]
    out, stat = [], {}
    for r in T:
        m = r["mastr_nr"]
        z = {h: r.get(h, "") for h in kopf}
        for h in kopf:
            if h.startswith(("slp_", "ms_", "msns_", "ns_", "hsms_")) or h in ("status", "preisstand", "stand_datum", "hinweis", "quelle_url", "grenze_2500h", "hsms_status"):
                z[h] = ""
        werte = {e: {} for e in EBENEN}; slp = {}; quelle = []; hinw = []; jahr_ok = False
        for f in dateien.get(m, []):
            try:
                sei = text_aus_datei(Path(f))
                text = "\n".join(sei)
                if "2027" not in text and "2027" not in os.path.basename(f): continue
                e = tabellen_lesen(sei)
                try: slp_lesen(text.splitlines(), e)
                except Exception: pass
            except Exception as ex:
                hinw.append(f"{os.path.basename(f)}: Lesefehler {type(ex).__name__}"); continue
            jahr_ok = True
            quelle.append(os.path.relpath(f))
            for eb, dct in (("ns", e.ns), ("msns", e.msns), ("ms", e.ms), ("hsms", e.hsms)):
                vals = [dct.get(k) for k in FELDER] if dct else []
                if len(vals) == 4 and None not in vals and not werte[eb]: werte[eb] = dict(zip(SUFF, vals))
            if e.slp.get("ap") is not None and not slp: slp = {"ap": e.slp["ap"], "gp": e.slp.get("gp")}
            if getattr(e, "grenze_le", False): z["grenze_2500h"] = "≤ / >"
        # Plausibilität (wie 2026)
        fehl = []
        for eb, d in werte.items():
            if not d: continue
            lu, au, la, aa = (d[s] for s in SUFF)
            if not (la >= lu and au >= aa): fehl.append(f"{eb}: Preise unter/ab 2.500 h unplausibel")
            if eb == "ns" and not (40 <= la <= 500): fehl.append("NS LP ab 2.500 h außerhalb 40–500")
            for s, v in d.items(): z[f"{eb}_{s}"] = DEZ(v)
        if slp:
            if slp["ap"] is not None: z["slp_ap_ct_kwh"] = DEZ(slp["ap"])
            if slp.get("gp") is not None: z["slp_grundpreis_eur_jahr"] = DEZ(slp["gp"])
            if slp["ap"] is not None and not (3 <= slp["ap"] <= 15): fehl.append("SLP-AP außerhalb 3–15")
        if not z["grenze_2500h"] and any(werte.values()): z["grenze_2500h"] = "< / ≥"
        # berechnete Spalten
        for h in kopf:
            mt = re.fullmatch(r"(ms|msns|ns|hsms)_ct_kwh_bei_(\d+)h", h)
            if mt and werte[mt.group(1)]:
                d, hh = werte[mt.group(1)], int(mt.group(2))
                lp, ap = (d[SUFF[0]], d[SUFF[1]]) if hh < 2500 else (d[SUFF[2]], d[SUFF[3]])
                z[h] = DEZ(ap + lp * 100 / hh)
        voll = bool(werte["ns"] or werte["msns"])
        quelleurl = " | ".join(quelle)
        seiten = [u for u, a in quellen.get(m, []) if a != "Dokument"]
        if jahr_ok and voll and not fehl: st = "gelesen"
        elif jahr_ok and fehl: st = "pruefen"
        elif jahr_ok: st = "teilweise"
        elif seiten: st = "quelle_seite"; quelleurl = seiten[0]
        elif quellen.get(m): st = "quelle_adresse"; quelleurl = quellen[m][0][0]
        else: st = "kein_blatt_2027"
        z["status"] = st; z["preisstand"] = "vorläufig" if jahr_ok else ""; z["stand_datum"] = "2027" if jahr_ok else ""
        z["quelle_url"] = quelleurl
        z["hinweis"] = "; ".join(hinw + fehl + (["Dokument 2027 im Repo: " + quelleurl] if jahr_ok else []))
        stat[st] = stat.get(st, 0) + 1
        out.append(z)
    with open("ergebnis/netzentgelte_2027_vorlaeufig.csv", "w", encoding="utf-8-sig", newline="") as o:
        w = csv.DictWriter(o, fieldnames=kopf, delimiter=";", lineterminator="\n"); w.writeheader(); w.writerows(out)
    print(len(out), "Zeilen", stat)


main("--nur-lokal" in sys.argv)
