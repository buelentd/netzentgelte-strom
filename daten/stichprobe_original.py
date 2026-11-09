"""Unabhängige Gegenprobe: lädt für eine Zufallsstichprobe von ok-Netzbetreibern das Original-PDF frisch von der Quell-Adresse
(nur wenn robots.txt den Pfad nicht sperrt, 1 Abruf je Sekunde) und liest es mit pdftotext neu aus. Der Beleg-Leser (ohne manuelle Belege)
vergleicht die frischen Zeilen mit unseren Werten.
Ausgabe: ergebnis/stichprobe_original.csv (nr;netzbetreiber;url;abruf;ebene;befund;unser_wert;dokument)
Aufruf: PYTHONPATH=. python daten/stichprobe_original.py [Anzahl] [Startwert]"""
import csv, random, re, subprocess, sys, time, urllib.request, urllib.robotparser, urllib.parse, os, hashlib
sys.path.insert(0, "daten")
import beleg_leser as B

N = [r for r in B.lese_n() if r["status"] == "ok" and r["quelle_url"].lower().split("?")[0].endswith(".pdf")]
anz = int(sys.argv[1]) if len(sys.argv) > 1 else 60
random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 20261107)
auswahl = random.sample(N, min(anz, len(N)))
os.makedirs("/tmp/claude-0/stichprobe", exist_ok=True)
out = []; stat = {"geladen": 0, "robots": 0, "fehler": 0}
rp_cache = {}
for r in auswahl:
    url = r["quelle_url"]; host = urllib.parse.urlparse(url)
    base = f"{host.scheme}://{host.netloc}"
    if base not in rp_cache:
        rp = urllib.robotparser.RobotFileParser(); rp.set_url(base + "/robots.txt")
        try:
            rp.read()
        except Exception:
            rp = None
        rp_cache[base] = rp
    rp = rp_cache[base]
    if rp is not None and not rp.can_fetch("*", url):
        stat["robots"] += 1; out.append([r["nr"], r["netzbetreiber"], url, "robots_gesperrt", "", "", "", ""]); continue
    pfad = f"/tmp/claude-0/stichprobe/{r['nr']}.pdf"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Netzentgelte-Gegenprobe; einzelner Abruf)"})
        data = urllib.request.urlopen(req, timeout=40).read()
        open(pfad, "wb").write(data); time.sleep(1)
    except Exception as e:
        stat["fehler"] += 1; out.append([r["nr"], r["netzbetreiber"], url, "abruf_fehler:" + str(e)[:40], "", "", "", ""]); continue
    stat["geladen"] += 1
    txt = f"/tmp/claude-0/stichprobe/{r['nr']}.txt"
    t = subprocess.run(["pdftotext", "-layout", pfad, txt], capture_output=True, text=True)
    try:
        bl = B.belege(txt)
    except Exception:
        bl = []
    if not bl and len(open(txt, encoding="utf8", errors="replace").read().strip()) < 300:
        out.append([r["nr"], r["netzbetreiber"], url, "geladen", "alle", "pdf_ohne_text", "", ""]); continue
    for eb in B.EBENEN:
        ours = B.unsere(r, eb)
        if ours is None:
            continue
        mit = [b for b in bl if b["ebene"] == eb]
        gl = [b for b in mit if B.passt(b["werte"], ours)]
        if gl:
            out.append([r["nr"], r["netzbetreiber"], url, "geladen", eb, "bestaetigt", "/".join(map(str, ours)), f"Zeile {gl[0]['zeile']}: {gl[0]['label']}"])
        elif mit:
            out.append([r["nr"], r["netzbetreiber"], url, "geladen", eb, "abweichend", "/".join(map(str, ours)), "/".join(map(str, mit[0]["werte"])) + f" (Zeile {mit[0]['zeile']})"])
        else:
            out.append([r["nr"], r["netzbetreiber"], url, "geladen", eb, "nicht_erkannt", "/".join(map(str, ours)), ""])
with open("ergebnis/stichprobe_original.csv", "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.writer(fh, delimiter=";"); w.writerow(["nr", "netzbetreiber", "url", "abruf", "ebene", "befund", "unser_wert", "dokument"]); w.writerows(out)
from collections import Counter
print(stat, Counter(o[5] for o in out if o[3] == "geladen"))
