"""Crawl der Netzbetreiber-Websites nach Hochlastzeitfenster-Dokumenten (PDF, XLSX, HTML-Seiten).
Regeln (CLAUDE.md): robots.txt beachten (gesperrt oder 403 auf robots.txt -> nicht umgehen, Status robots/blockiert), max. 1 Anfrage/s je Domain, max. 40 Seiten je Website, Timeout 30 s, HTML wie PDF.
Eingabe: ergebnis/HLZF_FEHLENDE_ZUM_SUCHEN.csv (mastr_nr, domain_ohne_www). Ausgabe: lauf/hlzf_crawl_ergebnis.csv (mastr_nr zuerst).
Aufruf: PYTHONPATH=. python daten/hlzf_crawl.py [anzahl_threads]"""
import csv, re, sys, time, urllib.request, urllib.parse, urllib.robotparser, concurrent.futures as cf
UA = "Mozilla/5.0 (compatible; netzentgelte-datenerhebung)"
HIT = re.compile(r"hochlast|hlzf|atypisch|19[-_ ]?abs|sonderform", re.I)
FOLLOW = re.compile(r"netz|veroeff|veröff|pflicht|marktpartner|zugang|entgelt|strom|download|service|sonderform|nutzung", re.I)
SKIP = re.compile(r"\.(jpg|jpeg|png|gif|svg|css|js|zip|mp4|ico)(\?|$)", re.I)
def get(u):
    r = urllib.request.Request(u, headers={"User-Agent": UA})
    with urllib.request.urlopen(r, timeout=30) as f:
        return f.status, f.headers.get("content-type", ""), f.read(1_500_000)
def crawl(k, d):
    res = {"status": "", "seiten": 0, "treffer": [], "anfrage": ""}
    base = None; rp = urllib.robotparser.RobotFileParser()
    for pre in ("https://www.", "https://"):
        try:
            _, _, b = get(pre + d + "/robots.txt"); rp.parse(b.decode("utf-8", "ignore").splitlines()); base = pre + d; break
        except urllib.error.HTTPError as e:
            if e.code in (403, 401): res["status"] = "robots/blockiert (HTTP %d)" % e.code; return res
            if e.code == 404: base = pre + d; rp.parse([]); break
        except Exception: pass
        time.sleep(1)
    if not base: res["status"] = "nicht erreichbar"; return res
    seen, q = set(), [base + "/"]
    while q and res["seiten"] < 40:
        u = q.pop(0)
        if u in seen or not rp.can_fetch("*", u): continue
        seen.add(u); time.sleep(1)
        try: s, c, b = get(u)
        except Exception: continue
        res["seiten"] += 1
        if "html" not in c: continue
        t = b.decode("utf-8", "ignore")
        if re.search(r"hochlast", t, re.I) and re.search(r"anfrag|auf anfrage", t, re.I): res["anfrage"] = u
        for m in re.finditer(r"href=[\"']([^\"']+)[\"'][^>]*>([^<]{0,100})", t):
            h = urllib.parse.urljoin(u, m.group(1).replace("&amp;", "&")).split("#")[0]; tx = m.group(2).strip()
            if SKIP.search(h) or urllib.parse.urlparse(h).netloc.replace("www.", "") != d: continue
            if HIT.search(h + " " + tx) or (re.search(r"\.(pdf|xlsx?)(\?|$)", h, re.I) and re.search(r"2026|2027", h + tx)):
                if h not in [x[0] for x in res["treffer"]]: res["treffer"].append((h, tx[:60]))
            elif h not in seen and h not in q and len(q) < 60 and FOLLOW.search(h + " " + tx): q.append(h)
    res["status"] = "treffer" if res["treffer"] else ("auf Anfrage (Text nennt Hochlast und Anfrage)" if res["anfrage"] else "keine Treffer")
    return res
def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    rows = [r for r in csv.DictReader(open("ergebnis/HLZF_FEHLENDE_ZUM_SUCHEN.csv", encoding="utf-8-sig"), delimiter=";") if r["domain_ohne_www"] and not r["domain_ohne_www"].startswith("(")]
    out = []
    with cf.ThreadPoolExecutor(n) as ex:
        fut = {ex.submit(crawl, r["mastr_nr"], r["domain_ohne_www"]): r for r in rows}
        for f in cf.as_completed(fut):
            r = fut[f]
            try: res = f.result()
            except Exception as e: res = {"status": "Fehler " + str(e)[:50], "seiten": 0, "treffer": [], "anfrage": ""}
            out.append([r["mastr_nr"], r["netzbetreiber"], r["domain_ohne_www"], res["status"], res["seiten"], " | ".join(f"{h} [{t}]" for h, t in res["treffer"][:8]), res["anfrage"]])
            print(r["mastr_nr"], r["domain_ohne_www"], res["status"], len(res["treffer"]), flush=True)
    out.sort()
    w = csv.writer(open("lauf/hlzf_crawl_ergebnis.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";")
    w.writerow(["mastr_nr", "netzbetreiber", "domain", "status", "seiten", "treffer", "anfrage_seite"]); w.writerows(out)
main()
