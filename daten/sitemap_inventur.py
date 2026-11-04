"""Sitemap-Inventur für alle Netzbetreiber-Websites: robots.txt lesen, Sitemaps (auch verschachtelt, auch .gz) laden und alle Adressen
nach Netzentgelten, Jahr 2026/2027 und Hochlastzeitfenstern durchsuchen, egal ob PDF oder Seite.
Regeln: robots.txt beachtet, höchstens eine Anfrage je Sekunde und Domain, Timeout 30 s, höchstens 40 Sitemap-Dateien je Website.
Ergebnis: ergebnis/sitemap_inventur.csv (eine Zeile je Netzbetreiber) und ergebnis/sitemap_kandidaten.csv (eine Zeile je Fundstelle)."""
import csv, gzip, re, time, threading, urllib.robotparser
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse, unquote
import requests

W = Path(__file__).parent.parent
UA = "netzentgelte-strom/1.0 (Datenerfassung Netzentgelte)"
LOCKS = defaultdict(threading.Lock); LETZTE = {}
PREIS = re.compile(r"netzentgelt|netznutzung|preisblatt|preisblaetter|preisblätter|(?<![a-z])nne(?![a-z])|netzzugang|netzpreise|entgelte|nutzungsentgelt", re.I)
HLZF = re.compile(r"hochlast|hlzf|(?<![a-z])hlz(?![a-z])|zeitfenster", re.I)
FREMD = re.compile(r"erdgas|(?<![a-z])gas(?![a-z])|waerme|wärme|fernwaerme|wasser|abwasser|telekom|glasfaser", re.I)
DOK = re.compile(r"\.(pdf|xlsx?|docx?)(\?|$)|/download|media-download|deliverfile", re.I)


def get(url, rate_domain=None):
    d = urlparse(url).netloc
    with LOCKS[d]:
        w = 1.1 - (time.time() - LETZTE.get(d, 0))
        if w > 0: time.sleep(w)
        LETZTE[d] = time.time()
    return requests.get(url, headers={"User-Agent": UA}, timeout=30, allow_redirects=True)


def locs(r):
    b = r.content
    if b[:2] == b"\x1f\x8b" or r.url.endswith(".gz"):
        try: b = gzip.decompress(b)
        except Exception: pass
    t = b[:30_000_000].decode("utf-8", "replace")
    return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", t), "<sitemapindex" in t[:2000].lower()


def einer(z):
    nr, name, web = z
    w = web if web.startswith("http") else "https://" + web.lstrip("/")
    u = urlparse(w); basis = f"{u.scheme}://{u.netloc}"
    res = {"nr": nr, "netzbetreiber": name, "website": web, "robots": "", "sitemap": "nein", "sitemap_dateien": 0, "urls": 0, "fehler": ""}
    kand = []; sitemaps = []
    try:
        rp = urllib.robotparser.RobotFileParser()
        try:
            r = get(basis + "/robots.txt"); res["robots"] = f"HTTP {r.status_code}"
            if r.status_code == 200:
                rp.parse(r.text.splitlines()); sitemaps = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", r.text)
            else: rp.parse([])
        except Exception as e:
            res["robots"] = f"Fehler {type(e).__name__}"; rp.parse([])
        if not sitemaps: sitemaps = [basis + "/sitemap.xml", basis + "/wp-sitemap.xml", basis + "/sitemap_index.xml"]
        todo = list(dict.fromkeys(sitemaps)); gesehen = set(); urls = []
        while todo and len(gesehen) < 40:
            s = todo.pop(0)
            if s in gesehen or not rp.can_fetch(UA, s): continue
            gesehen.add(s)
            try: r = get(s)
            except Exception: continue
            if r.status_code != 200: continue
            l, idx = locs(r)
            if not l: continue
            res["sitemap"] = "ja"; res["sitemap_dateien"] += 1
            if idx: todo += [x for x in l if x not in gesehen]
            else: urls += l
        res["urls"] = len(urls)
        for x in dict.fromkeys(urls):
            t = unquote(x)
            if FREMD.search(t) and "strom" not in t.lower(): continue
            p, h = bool(PREIS.search(t)), bool(HLZF.search(t))
            if not (p or h): continue
            j = [y for y in ("2026", "2027") if y in t]
            if p and not j and not DOK.search(t) and not h: continue     # allgemeine Seite ohne Jahr nur als Dokument/HLZF behalten
            kand.append([nr, name, x, "hlzf" if h else "preis", ",".join(j), "Dokument" if DOK.search(t) else "Seite"])
    except Exception as e:
        res["fehler"] = f"{type(e).__name__}"
    res["kandidaten"] = len(kand)
    return res, kand[:400]


def main():
    korr = {}
    p = W / "lauf" / "website_korrektur.csv"
    if p.exists():
        for z in csv.DictReader(open(p, encoding="utf-8"), delimiter=";"): korr[z["nr"]] = z["website"]
    rows = [(r["nr"], r["netzbetreiber"], korr.get(r["nr"]) or r["website"]) for r in csv.DictReader(open(W / "ergebnis" / "netzentgelte_2026.csv", encoding="utf-8"), delimiter=";") if (korr.get(r["nr"]) or r["website"]).strip()]
    print(len(rows), "Websites", flush=True)
    with ThreadPoolExecutor(16) as ex: res = list(ex.map(einer, rows))
    k = ["nr", "netzbetreiber", "website", "robots", "sitemap", "sitemap_dateien", "urls", "kandidaten", "fehler"]
    with open(W / "ergebnis" / "sitemap_inventur.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(k); [w.writerow([r[0].get(c, "") for c in k]) for r in res]
    with open(W / "ergebnis" / "sitemap_kandidaten.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(["nr", "netzbetreiber", "url", "art", "jahr", "typ"]); [w.writerow(x) for r in res for x in r[1]]
    print("fertig; Sitemap vorhanden bei", sum(1 for r in res if r[0]["sitemap"] == "ja"), "von", len(res))


main()
