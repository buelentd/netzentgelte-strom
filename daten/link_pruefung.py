"""Prüft alle Links aus ergebnis/quellen_164_geprueft.csv (2026 und 2027) mit Internet.
Je Link: HTTP-Status, Dateityp, bei PDF die ersten Seiten per pdftotext (Jahre, Netzbetreibername, Preiswörter, fiktiv/vorläufig/endgültig),
bei HTML-Seiten Text ohne JavaScript, Preiswörter und die PDF-Links auf der Seite. Höchstens eine Anfrage je Sekunde und Domain,
robots.txt beachtet, Timeout 30 s. Ergebnis: ergebnis/link_pruefung.csv (Erster Eindruck, keine Auswertung der Preise)."""
import csv, re, subprocess, tempfile, time, threading, urllib.robotparser
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse, urljoin
import requests, sys, html as html_mod
sys.path.insert(0, str(Path(__file__).parent.parent))
from vnb.extract import auswerten

W = Path(__file__).parent.parent
UA = "netzentgelte-strom/1.0 (Datenerfassung Netzentgelte; Prüfung bereits veröffentlichter Preisblätter)"
LOCKS = defaultdict(threading.Lock); LETZTE = {}; ROBOTS = {}


def warten(domain):
    with LOCKS[domain]:
        d = 1.1 - (time.time() - LETZTE.get(domain, 0))
        if d > 0: time.sleep(d)
        LETZTE[domain] = time.time()


def robots_ok(url):
    u = urlparse(url); basis = f"{u.scheme}://{u.netloc}"
    if basis not in ROBOTS:
        rp = urllib.robotparser.RobotFileParser()
        try:
            warten(u.netloc); r = requests.get(basis + "/robots.txt", headers={"User-Agent": UA}, timeout=30)
            rp.parse(r.text.splitlines()) if r.status_code == 200 else rp.parse([])
        except Exception:
            rp.parse([])
        ROBOTS[basis] = rp
    return ROBOTS[basis].can_fetch(UA, url)


def kern(name):
    w = [x for x in re.split(r"[^A-Za-zÄÖÜäöüß]+", name) if len(x) > 3 and x.lower() not in ("gmbh", "stadtwerke", "stadtwerk", "netz", "netze", "energie", "versorgung", "gemeindewerke", "elektrizitaets", "elektrizitäts")]
    return (w[0].lower() if w else "")


MARK = re.compile(r"leistungspreis|arbeitspreis|grundpreis|jahresleistungspreis|netznutzungsentgelt", re.I)


def werte(pfad, url):
    e = auswerten(pfad, url, 2026)
    ns = e.ns or {}; ms = e.msns or {}; slp = e.slp or {}
    if not (ns or slp or ms): return [""] * 14
    return [ns.get("lp_ueber_2500", ""), ns.get("ap_ueber_2500", ""), ns.get("lp_unter_2500", ""), ns.get("ap_unter_2500", ""),
            ms.get("lp_unter_2500", ""), ms.get("ap_unter_2500", ""), ms.get("lp_ueber_2500", ""), ms.get("ap_ueber_2500", ""),
            slp.get("ap", ""), slp.get("gp", ""), f"{e.preisstand} {e.stand_datum or ''}".strip(), "ja" if e.grenze_le else "", url]


def pruefe(z, jahr, url, art):
    zeile = [z["nr"], z["netzbetreiber_liste"], jahr, url, art]
    u = urlparse(url)
    if not robots_ok(url):
        return zeile + ["robots.txt sperrt", "", "", "", "", "", "", "", "", ""]
    try:
        warten(u.netloc)
        r = requests.get(url, headers={"User-Agent": UA}, timeout=30, stream=True, allow_redirects=True)
        daten = r.raw.read(15_000_000, decode_content=True)
    except Exception as e:
        return zeile + [f"Fehler {type(e).__name__}", "", "", "", "", "", "", "", "", ""]
    ct = (r.headers.get("content-type") or "").split(";")[0].lower()
    zeile += [f"HTTP {r.status_code}", ct, len(daten)]
    text = ""; pdfs = ""
    if daten[:4] == b"%PDF":
        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            f.write(daten); f.flush()
            try:
                text = subprocess.run(["pdftotext", "-layout", "-l", "6", f.name, "-"], capture_output=True, timeout=60).stdout.decode("utf-8", "replace")
            except Exception:
                text = ""
        typ = "PDF"
    elif "html" in ct or daten[:200].lstrip().lower().startswith((b"<!doctype", b"<html")):
        h = daten.decode(r.encoding or "utf-8", "replace")
        links = re.findall(r'href=["\']([^"\']+)["\']', h, re.I)
        pd = [urljoin(r.url, l) for l in links if re.search(r"\.pdf|download|preisblatt|netzentgelt|nne", l, re.I)]
        pdfs = " | ".join(dict.fromkeys(pd))[:900]
        h2 = re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
        h2 = re.sub(r"(?i)</t[dh]\s*>", "\x01", h2); h2 = re.sub(r"(?i)</(tr|p|div|li|h\d)\s*>|<br\s*/?>", "\n", h2)
        h2 = html_mod.unescape(re.sub(r"<[^>]+>", " ", h2))
        zl = []
        for l in h2.splitlines():
            cells = [re.sub(r"\s+", " ", c).strip() for c in l.split("\x01")]
            l2 = "   ".join(c for c in cells if c)
            if l2: zl.append(l2)
        layout = "\n".join(zl)
        text = re.sub(r"\s+", " ", layout)
        typ = "HTML"
    else:
        typ = ct or "unbekannt"
    wert = [""] * 13
    try:
        if typ == "PDF":
            with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
                f.write(daten); f.flush(); wert = werte(Path(f.name), url)
        elif typ == "HTML":
            with tempfile.NamedTemporaryFile(suffix=".html", mode="w", encoding="utf-8") as f:
                f.write(layout); f.flush(); wert = werte(Path(f.name), url)
            if not wert[0] and pdfs:                       # Seite ohne Preise: PDF-Links auf der Seite prüfen (höchstens 6)
                kand = sorted(pdfs.split(" | "), key=lambda x: (not re.search(r"2026", x), bool(re.search(r"2027|vorl", x, re.I)), len(x)))
                for k2 in [x for x in kand if re.search(r"\.pdf|download", x, re.I)][:6]:
                    if not robots_ok(k2): continue
                    warten(urlparse(k2).netloc)
                    r2 = requests.get(k2, headers={"User-Agent": UA}, timeout=30)
                    if r2.content[:4] != b"%PDF": continue
                    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
                        f.write(r2.content); f.flush(); w2 = werte(Path(f.name), k2)
                    if w2[0]: wert = w2; break
    except Exception as e:
        wert = [""] * 12 + [f"Fehler beim Auslesen: {type(e).__name__}"]
    kopf = text[:3000]
    jahre = sorted(set(re.findall(r"(?<!\d)(202[5-8])(?!\d)", kopf)))
    k = kern(z["netzbetreiber_liste"])
    return zeile + [typ, ",".join(jahre), "ja" if k and k in text.lower() else ("nein" if text else ""),
                    len(MARK.findall(text)), len(re.findall(r"\d+[.,]\d+", text)),
                    "ja" if re.search(r"fiktiv", text, re.I) else "", "endgültig" if re.search(r"endg[uü]ltig", kopf, re.I) else ("vorläufig" if re.search(r"vorl[aä]ufig", kopf, re.I) else ""),
                    pdfs] + wert


def main():
    g = list(csv.DictReader(open(W / "ergebnis" / "quellen_164_geprueft.csv", encoding="utf-8-sig"), delimiter=";"))
    jobs = []
    for z in g:
        for jahr, q, a in (("2026", z["quelle_2026"], z["art_quelle_2026"]), ("2027", z["quelle_2027"], z["art_quelle_2027"])):
            if q.startswith("http"):
                jobs.append((z, jahr, q, a))
    print(len(jobs), "Links", flush=True)
    kopf = ["nr", "netzbetreiber", "jahr", "link", "art_laut_liste", "http", "inhaltstyp", "bytes", "typ_erkannt", "jahre_im_kopf",
            "name_im_text", "preiswoerter", "dezimalzahlen", "fiktiv", "preisstand_im_kopf", "pdf_links_auf_der_seite", "ns_lp_ab_2500h", "ns_ap_ab_2500h", "ns_lp_unter_2500h", "ns_ap_unter_2500h", "msns_lp_unter_2500h", "msns_ap_unter_2500h", "msns_lp_ab_2500h", "msns_ap_ab_2500h", "slp_ap", "slp_grundpreis", "preisstand_datum", "grenze_le", "werte_gefunden_in"]
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(lambda j: pruefe(*j), jobs))
    for r in res:
        r += [""] * (len(kopf) - len(r))
    with open(W / "ergebnis" / "link_pruefung.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(kopf); w.writerows(res)
    print("fertig", len(res))


main()
