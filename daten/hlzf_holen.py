"""Hochlastzeitfenster (HLZF) für alle Netzbetreiber mit Adresse in lauf/hlzf_urls.csv (nr;url;herkunft) laden und lesen.
Jede Adresse: PDF (pdftotext -layout) oder Webseite (Tabellen spaltentreu), dann vnb.hlzf.hlzf_lesen. Je Netzbetreiber das Dokument
mit den meisten gelesenen Fenstern. Prüfung: Zeiten plausibel (Beginn vor Ende, 05:00 bis 23:00, höchstens 6 Stunden), vier Jahreszeiten je Ebene.
Ergebnis: ergebnis/hlzf_ergebnis.csv (eine Zeile je Netzbetreiber, Zielformat) und ergebnis/hlzf_texte/<nr>.txt (Text zur Nachprüfung).
Regeln: robots.txt beachtet, höchstens eine Anfrage je Sekunde und Domain, Timeout 30 s."""
import csv, html as html_mod, re, subprocess, sys, tempfile, time, threading, urllib.robotparser
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse
import requests
W = Path(__file__).parent.parent
sys.path.insert(0, str(W))
from vnb.hlzf import hlzf_lesen, JAHRESZEITEN
UA = "netzentgelte-strom/1.0 (Datenerfassung Netzentgelte)"
LOCK = defaultdict(threading.Lock); LETZT = {}; ROB = {}


def warten(d):
    with LOCK[d]:
        w = 1.1 - (time.time() - LETZT.get(d, 0))
        if w > 0: time.sleep(w)
        LETZT[d] = time.time()


def robots_ok(url):
    u = urlparse(url); b = f"{u.scheme}://{u.netloc}"
    if b not in ROB:
        rp = urllib.robotparser.RobotFileParser()
        try:
            warten(u.netloc); r = requests.get(b + "/robots.txt", headers={"User-Agent": UA}, timeout=30)
            rp.parse(r.text.splitlines() if r.status_code == 200 else [])
        except Exception: rp.parse([])
        ROB[b] = rp
    return ROB[b].can_fetch(UA, url)


def text_von(url):
    """(text, fehler)"""
    if not robots_ok(url): return "", "robots.txt sperrt"
    try:
        warten(urlparse(url).netloc)
        r = requests.get(url, headers={"User-Agent": UA}, timeout=30, allow_redirects=True)
    except Exception as e:
        return "", f"nicht erreichbar ({type(e).__name__})"
    if r.status_code != 200: return "", f"HTTP {r.status_code}"
    if r.content[:4] == b"%PDF":
        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            f.write(r.content); f.flush()
            t = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, timeout=120).stdout.decode("utf-8", "replace")
        return t, "" if len(t.strip()) > 100 else "kein Text (Scan?)"
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", r.text)
    h = re.sub(r"(?i)</t[dh]\s*>", "\x01", h); h = re.sub(r"(?i)</(tr|p|div|li|h\d)\s*>|<br\s*/?>", "\n", h)
    h = html_mod.unescape(re.sub(r"<[^>]+>", " ", h))
    zl = []
    for l in h.splitlines():
        c = [re.sub(r"\s+", " ", x).strip() for x in l.split("\x01")]
        l2 = "   ".join(x for x in c if x)
        if l2: zl.append(l2)
    return "\n".join(zl), ""


def zeit_ok(z):
    m = re.fullmatch(r"(\d\d):(\d\d)-(\d\d):(\d\d)", z.strip())
    if not m: return False
    a, b = int(m[1]) * 60 + int(m[2]), int(m[3]) * 60 + int(m[4])
    return 5 * 60 <= a < b <= 23 * 60 + 59 and b - a <= 6 * 60


def einer(job):
    nr, urls = job
    best = None; fehler = []
    for u in urls:
        t, f = text_von(u)
        if f: fehler.append(f"{u[-50:]}: {f}"); continue
        e = hlzf_lesen(t, u)
        gew = sum(len(v) for eb in e.fenster.values() for v in eb.values()) + 100 * ("NS" in e.fenster) if e.gelesen else 0
        if best is None or gew > best[0]: best = (gew, u, t, e)
    return nr, urls, best, fehler


def main():
    jobs = defaultdict(list)
    for z in csv.DictReader(open(W / "lauf" / "hlzf_urls.csv", encoding="utf-8"), delimiter=";"):
        if z["url"].startswith("http") and z["url"] not in jobs[z["nr"]]: jobs[z["nr"]].append(z["url"])
    print(len(jobs), "Netzbetreiber mit Adresse", flush=True)
    (W / "ergebnis" / "hlzf_texte").mkdir(exist_ok=True)
    H = ["nr", "hlzf_status", *[f"hlzf_{e}_{s}" for e in ("ns", "msns") for s in JAHRESZEITEN], "hlzf_schwelle_prozent", "hlzf_mindestleistung_kw", "hlzf_quelle_url", "hlzf_jahr", "hlzf_pruefung"]
    rows = []
    with ThreadPoolExecutor(8) as ex:
        for nr, urls, best, fehler in ex.map(einer, list(jobs.items())):
            d = dict.fromkeys(H, ""); d["nr"] = nr
            if best is None or best[0] == 0:
                d["hlzf_status"] = "fehlt: " + ("; ".join(fehler)[:150] if fehler and best is None else (best[3].grund if best else "kein Dokument"))
                if best: (W / "ergebnis" / "hlzf_texte" / f"{nr}.txt").write_text(best[1] + "\n\n" + best[2][:40000], encoding="utf-8"); d["hlzf_quelle_url"] = best[1]
            else:
                _, u, t, e = best
                (W / "ergebnis" / "hlzf_texte" / f"{nr}.txt").write_text(u + "\n\n" + t[:40000], encoding="utf-8")
                pr = []
                for eb in ("NS", "MSNS"):
                    for s in JAHRESZEITEN:
                        v = e.fenster.get(eb, {}).get(s)
                        d[f"hlzf_{eb.lower()}_{s}"] = ", ".join(v) if v else ("keins" if eb in e.fenster else "")
                        if v and not all(zeit_ok(x) for x in v): pr.append(f"{eb} {s}: Zeit unplausibel")
                    if eb in e.fenster and len(e.fenster[eb]) < 4 and not all(s in e.fenster[eb] or True for s in JAHRESZEITEN): pr.append(f"{eb}: nicht alle Jahreszeiten")
                sc = e.schwelle.get("NS") or e.schwelle.get("MSNS")
                d["hlzf_schwelle_prozent"] = sc if sc is not None else ""
                d["hlzf_mindestleistung_kw"] = e.mindest_kw.get("NS", "") or e.mindest_kw.get("MSNS", "")
                d["hlzf_quelle_url"] = u; d["hlzf_jahr"] = e.jahr or ""
                d["hlzf_pruefung"] = "; ".join(pr)
                d["hlzf_status"] = "gelesen" if not pr and e.jahr in (2026, None) else ("gelesen, Jahr " + str(e.jahr) if e.jahr not in (2026, None) else "gelesen, Prüfung offen")
            rows.append([d[h] for h in H])
    rows.sort(key=lambda r: int(r[0]))
    csv.writer(open(W / "ergebnis" / "hlzf_ergebnis.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";").writerows([H] + rows)
    print("fertig:", sum(1 for r in rows if r[1].startswith("gelesen")), "gelesen von", len(rows))


main()
