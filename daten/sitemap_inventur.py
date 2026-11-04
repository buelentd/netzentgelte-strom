"""Sitemap-Inventur für alle Netzbetreiber-Websites: robots.txt lesen, Sitemaps (auch verschachtelt, auch .gz) laden und alle Adressen
nach Netzentgelten, Jahr 2026/2027 und Hochlastzeitfenstern durchsuchen, egal ob PDF oder Seite.
Regeln: robots.txt beachtet, höchstens eine Anfrage je Sekunde und Domain, Timeout 30 s, höchstens 40 Sitemap-Dateien je Website.
Ergebnis: ergebnis/sitemap_inventur.csv, eine Zeile je Netzbetreiber (Sitemap ja/nein, beste Fundstelle für Preise 2026/2027 und Hochlastzeitfenster)."""
import csv, gzip, re, time, threading, urllib.robotparser
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse, unquote, urljoin
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


def html_sitemap_seiten(basis, start, rp):
    """Mögliche sichtbare Sitemap-Seiten: Link „Sitemap/Seitenübersicht/Inhaltsverzeichnis“ auf der Startseite, sonst übliche Pfade."""
    kand = []
    try:
        r = get(start)
        if r.status_code == 200:
            for h, t in re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', r.text, re.I | re.S):
                if re.search(r"sitemap|seitenuebersicht|seitenübersicht|inhaltsverzeichnis|seitenindex|seiten.?karte", h + " " + re.sub(r"<[^>]+>", "", t), re.I):
                    kand.append(urljoin(r.url, h.split("#")[0]))
    except Exception:
        pass
    kand += [basis + p for p in ("/sitemap.html", "/sitemap", "/sitemap/", "/seitenuebersicht", "/seitenuebersicht.html", "/inhaltsverzeichnis", "/sitemap.htm")]
    return [x for x in dict.fromkeys(kand) if rp.can_fetch(UA, x)][:6]


def einer(z):
    nr, name, web = z
    w = web if web.startswith("http") else "https://" + web.lstrip("/")
    u = urlparse(w); basis = f"{u.scheme}://{u.netloc}"
    res = {"nr": nr, "netzbetreiber": name, "website": web, "robots": "", "sitemap": "nein", "sitemap_dateien": 0, "urls": 0, "fehler": "", "sitemap_adresse": "", "html_sitemap": ""}
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
            if not res["sitemap_adresse"]: res["sitemap_adresse"] = s
            if idx: todo += [x for x in l if x not in gesehen]
            else: urls += l
        if res["sitemap"] != "ja":                                   # sichtbare Sitemap-Seite (HTML), z. B. /sitemap.html oder Link im Seitenfuß
            for sp in html_sitemap_seiten(basis, w, rp):
                try:
                    r = get(sp)
                    if r.status_code != 200 or "html" not in (r.headers.get("content-type") or ""): continue
                    links = [urljoin(r.url, x) for x in re.findall(r'href=["\']([^"\'#]+)', r.text, re.I)]
                    links = [x for x in links if x.startswith("http")]
                    if len(links) >= 10:
                        res["sitemap"] = "html"; res["sitemap_adresse"] = sp; res["html_sitemap"] = sp; res["sitemap_dateien"] += 1; urls += links; break
                except Exception:
                    continue
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
    def beste(kand, art, jahr):
        c = [x for x in kand if x[3] == art and (jahr in x[4].split(",") if jahr else True)]
        def pk(x):
            t = unquote(x[2]).lower()
            return (x[5] == "Dokument", bool(re.search(r"preisblatt|nne|netznutzungsentgelt|netzentgelt", t)), not re.search(r"14a|fiktiv|gas|messstellen|msb", t), -len(t))
        c.sort(key=pk, reverse=True)
        return " | ".join(x[2] for x in c[:2])
    k = ["nr", "netzbetreiber", "website", "robots_txt", "sitemap", "sitemap_adresse", "sitemap_dateien", "adressen_in_sitemap", "fundstellen",
         "preis_2026", "preis_2027", "hochlastzeitfenster_2026", "hochlastzeitfenster_2027", "hochlastzeitfenster_ohne_jahr", "fehler"]
    with open(W / "ergebnis" / "sitemap_inventur.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(k)
        for r, kd in res:
            w.writerow([r["nr"], r["netzbetreiber"], r["website"], r["robots"], r["sitemap"], r["sitemap_adresse"], r["sitemap_dateien"], r["urls"], r["kandidaten"],
                        beste(kd, "preis", "2026"), beste(kd, "preis", "2027"), beste(kd, "hlzf", "2026"), beste(kd, "hlzf", "2027"),
                        beste([x for x in kd if not x[4]], "hlzf", ""), r["fehler"]])
    print("fertig; Sitemap vorhanden bei", sum(1 for r in res if r[0]["sitemap"] == "ja"), "von", len(res))


main()
