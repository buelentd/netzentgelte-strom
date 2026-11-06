"""Hochlastzeitfenster-Dateien aus eingang/ (beliebiger Unterordner, z. B. pdfs_neu oder neue listen; SNB…_NNNN_hlzf.pdf/.xls/.xlsx) offline lesen und in ergebnis/hlzf_ergebnis.csv eintragen.
Text je Datei: ergebnis/hlzf_texte/<nr>.txt (Nachprüfung). Eine vorhandene gelesene Zeile wird nur ersetzt, wenn die neue Datei mehr Fenster liefert.
Aufruf: PYTHONPATH=. python daten/hlzf_eingang.py"""
import csv, glob, re, shutil, subprocess, sys, os
from pathlib import Path
sys.path.insert(0, ".")
from vnb.hlzf import hlzf_lesen, JAHRESZEITEN
from daten.hlzf_regeln import stufe

def zeit_ok(z):
    m = re.fullmatch(r"(\d\d):(\d\d)-(\d\d):(\d\d)", z.strip())
    if not m: return False
    a, b = int(m[1]) * 60 + int(m[2]), int(m[3]) * 60 + int(m[4])
    return 5 * 60 <= a < b <= 23 * 60 + 59 and b - a <= 11 * 60

from html.parser import HTMLParser


class _Tab(HTMLParser):
    """HTML -> Text; Tabellen spaltentreu (jede Zelle auf feste Breite), damit die Leser die Spalten über die Position zuordnen können."""
    BLOCK = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "br", "section", "ul", "ol", "article", "header", "footer", "nav"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.zeilen, self.tab, self.zeile, self.zelle, self.skip = [], None, None, None, 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"): self.skip += 1
        elif tag == "table": self.tab = []
        elif tag == "tr" and self.tab is not None: self.zeile = []
        elif tag in ("td", "th") and self.zeile is not None: self.zelle = []
        elif tag in self.BLOCK and self.tab is None: self.zeilen.append("")

    def handle_endtag(self, tag):
        if tag in ("script", "style"): self.skip = max(0, self.skip - 1)
        elif tag in ("td", "th") and self.zelle is not None and self.zeile is not None:
            self.zeile.append(re.sub(r"\s+", " ", "".join(self.zelle)).strip()); self.zelle = None
        elif tag == "tr" and self.zeile is not None and self.tab is not None:
            if any(self.zeile): self.tab.append(self.zeile)
            self.zeile = None
        elif tag == "table" and self.tab is not None:
            n = max((len(r) for r in self.tab), default=0)
            w = [max((len(r[k]) for r in self.tab if k < len(r)), default=0) + 3 for k in range(n)]
            for r in self.tab:
                self.zeilen.append("".join((c if c else "-").ljust(w[k]) for k, c in enumerate(r)).rstrip())
            self.tab = None; self.zeilen.append("")
        elif tag in self.BLOCK and self.tab is None: self.zeilen.append("")

    def handle_data(self, d):
        if self.skip: return
        if self.zelle is not None: self.zelle.append(d)
        elif self.tab is None:
            if not self.zeilen: self.zeilen.append("")
            self.zeilen[-1] += d


def html_text(h):
    t = _Tab(); t.feed(h)
    return "\n".join(re.sub(r"[ \t]+", " ", z).strip() if "   " not in z else z for z in t.zeilen if z.strip())


def nur_2026(text):
    """Webseiten zeigen oft mehrere Jahre untereinander: nur die Abschnitte mit Jahr 2026 behalten (Marker: Zeile mit Jahr und Hochlast/HLZF/Angaben in MEZ)."""
    z = text.splitlines()
    marker = [(i, int(m.group(1))) for i, l in enumerate(z) if len(l) < 140 and re.search(r"hochlast|hlzf|angaben in mez|f[üu]r:", l, re.I)
              for m in [re.search(r"(?<!\d)(20[2-3]\d)(?!\d)", l)] if m]
    if len({j for _, j in marker}) < 2:
        return text
    ende = len(z); teile = []
    for k, (i, j) in enumerate(marker):
        nxt = marker[k + 1][0] if k + 1 < len(marker) else ende
        if j == 2026:
            teile.append("\n".join(z[i:nxt]))
    return "\n".join(teile) if teile else text


def text_aus(pfad):
    ext = Path(pfad).suffix.lower()
    if ext == ".pdf":
        return subprocess.run(["pdftotext", "-layout", pfad, "-"], capture_output=True, timeout=120).stdout.decode("utf-8", "replace")
    if ext == ".xlsx":
        import openpyxl
        wb = openpyxl.load_workbook(pfad, data_only=True)
        return "\n".join(f"## {ws.title}\n" + "\n".join("   ".join(str(c) for c in r if c is not None) for r in ws.iter_rows(values_only=True)) for ws in wb)
    if ext == ".xls":
        import xlrd
        wb = xlrd.open_workbook(pfad)
        return "\n".join(f"## {ws.name}\n" + "\n".join("   ".join(str(c) for c in ws.row_values(i) if c != "") for i in range(ws.nrows)) for ws in wb.sheets())
    if ext in (".html", ".htm"):
        return nur_2026(html_text(Path(pfad).read_text(encoding="utf-8", errors="replace")))
    return ""

def main():
    zeilen = list(csv.reader(open("ergebnis/hlzf_ergebnis.csv", encoding="utf-8-sig"), delimiter=";"))
    H, rows = zeilen[0], {r[0]: r for r in zeilen[1:]}
    os.makedirs("ergebnis/hlzf_texte", exist_ok=True); os.makedirs("eingang/verarbeitet_hlzf", exist_ok=True)
    bericht = []
    gruppen = {}
    dateien = {}
    for f in sorted(g for g in glob.glob("eingang/**/*_hlzf*.*", recursive=True) if "verarbeitet" not in g and "/NEUE PREISBLAETTER/" not in g and "/neue preise/" not in g):
        dateien[Path(f).name] = f                      # gleicher Dateiname in mehreren Ordnern: der spätere zählt
    for f in sorted(dateien.values()):
        m = re.match(r"SNB\d+_(\d+)_hlzf", Path(f).name)
        if not m: continue
        if Path(f).suffix.lower() in (".png", ".jpg", ".jpeg"):
            bericht.append([str(int(m[1])), Path(f).name, "Bilddatei: nicht lesbar (kein OCR)", ""]); continue
        gruppen.setdefault(str(int(m[1])), []).append(f)
    for nr, fs in gruppen.items():           # mehrere Dateien je Netzbetreiber (z. B. MS / NS / Umspannung): Texte zusammen lesen
        f = fs[0] if len(fs) == 1 else ";".join(fs)
        try: t = "\n\n".join((f"=== Datei {Path(x).name} ===\n" if len(fs) > 1 else "") + text_aus(x) for x in fs)
        except Exception as e:
            bericht.append([nr, Path(fs[0]).name, "Datei nicht lesbar: " + type(e).__name__, ""]); continue
        f = Path(fs[0])
        e = hlzf_lesen(t, str(f))
        stf = stufe(nr, t, e) if e.gelesen else None
        gew = sum(len(v) for eb in e.fenster.values() for v in eb.values()) + 100 * ("NS" in e.fenster) if stf else 0
        Path(f"ergebnis/hlzf_texte/{nr}.txt").write_text(" | ".join(Path(x).name for x in fs) + "\n\n" + t[:60000], encoding="utf-8")
        alt = rows.get(nr)
        alt_gew = 1 if alt and alt[1].startswith("gelesen") else 0
        d = dict.fromkeys(H, ""); d["nr"] = nr
        if gew == 0:
            grund = "kein Text (Scan?)" if len(t.strip()) < 100 else (e.grund or "Zeitfenster nicht lesbar")
            bericht.append([nr, Path(f).name, "nicht gelesen: " + grund, "alte Zeile bleibt" if alt_gew else ""])
            if not alt_gew:
                d["hlzf_status"] = "fehlt: " + grund; d["hlzf_quelle_url"] = Path(f).name; rows[nr] = [d[h] for h in H]
            continue
        pr = []
        for eb in ("NS", "MSNS"):
            for s in JAHRESZEITEN:
                v = e.fenster.get(eb, {}).get(s)
                d[f"hlzf_{eb.lower()}_{s}"] = ", ".join(v) if v else ("keins" if eb in e.fenster else "")
                if v and not all(zeit_ok(x) for x in v): pr.append(f"{eb} {s}: Zeit unplausibel")
        sc = e.schwelle.get("NS") or e.schwelle.get("MSNS")
        d["hlzf_schwelle_prozent"] = sc if sc is not None else ""
        d["hlzf_mindestleistung_kw"] = e.mindest_kw.get("NS", "") or e.mindest_kw.get("MSNS", "")
        d["hlzf_quelle_url"] = "eingang: " + Path(f).name; d["hlzf_jahr"] = e.jahr or ""; d["hlzf_pruefung"] = "; ".join(pr)
        d["hlzf_status"] = "gelesen" if not pr and e.jahr in (2026, None) else ("gelesen, Jahr " + str(e.jahr) if e.jahr not in (2026, None) else "gelesen, Prüfung offen")
        if d["hlzf_status"] == "gelesen" and stf == "ungeprueft":
            d["hlzf_status"] = "gelesen, Prüfung offen"
            d["hlzf_pruefung"] = ("; ".join(x for x in (d["hlzf_pruefung"],) if x) + "; " if d["hlzf_pruefung"] else "") + "ungeprüft neu gelesen (Form: " + e.form + "), Zuordnung der Zeilen zu den Ebenen nicht am Dokument bestätigt"
        if any(Path(x).suffix.lower() in (".html", ".htm") for x in fs) and not e.jahr:
            d["hlzf_status"] = "gelesen, Prüfung offen"; d["hlzf_pruefung"] = (d["hlzf_pruefung"] + "; " if d["hlzf_pruefung"] else "") + "Webseite: Jahr nicht belegt"
        rows[nr] = [d[h] for h in H]
        bericht.append([nr, Path(f).name, d["hlzf_status"], f"Jahr {e.jahr}"])
    out = sorted(rows.values(), key=lambda r: int(r[0]))
    csv.writer(open("ergebnis/hlzf_ergebnis.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";").writerows([H] + out)
    csv.writer(open("ergebnis/hlzf_eingang_bericht.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";").writerows([["nr", "datei", "ergebnis", "bemerkung"]] + bericht)
    from collections import Counter
    print(Counter(b[2].split(":")[0] if b[2].startswith("nicht") else b[2] for b in bericht))
main()
