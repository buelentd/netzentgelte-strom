"""Hochlastzeitfenster-Dateien aus eingang/pdfs_neu (SNB…_NNNN_hlzf.pdf/.xls/.xlsx) offline lesen und in ergebnis/hlzf_ergebnis.csv eintragen.
Text je Datei: ergebnis/hlzf_texte/<nr>.txt (Nachprüfung). Eine vorhandene gelesene Zeile wird nur ersetzt, wenn die neue Datei mehr Fenster liefert.
Aufruf: PYTHONPATH=. python daten/hlzf_eingang.py"""
import csv, glob, re, shutil, subprocess, sys, os
from pathlib import Path
sys.path.insert(0, ".")
from vnb.hlzf import hlzf_lesen, JAHRESZEITEN

def zeit_ok(z):
    m = re.fullmatch(r"(\d\d):(\d\d)-(\d\d):(\d\d)", z.strip())
    if not m: return False
    a, b = int(m[1]) * 60 + int(m[2]), int(m[3]) * 60 + int(m[4])
    return 5 * 60 <= a < b <= 23 * 60 + 59 and b - a <= 6 * 60

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
        import html as hm
        h = re.sub(r"(?is)<(script|style).*?</\1>", " ", Path(pfad).read_text(encoding="utf-8", errors="replace"))
        h = re.sub(r"(?i)</t[dh]\s*>", "   ", h); h = re.sub(r"(?i)</(tr|p|div|li|h\d)\s*>|<br\s*/?>", "\n", h)
        return "\n".join(l.strip() for l in hm.unescape(re.sub(r"<[^>]+>", " ", h)).splitlines() if l.strip())
    return ""

def main():
    zeilen = list(csv.reader(open("ergebnis/hlzf_ergebnis.csv", encoding="utf-8-sig"), delimiter=";"))
    H, rows = zeilen[0], {r[0]: r for r in zeilen[1:]}
    os.makedirs("ergebnis/hlzf_texte", exist_ok=True); os.makedirs("eingang/verarbeitet_hlzf", exist_ok=True)
    bericht = []
    gruppen = {}
    dateien = {}
    for f in sorted(glob.glob("eingang/pdfs_neu/**/*_hlzf*.*", recursive=True)):
        dateien[Path(f).name] = f                      # gleicher Dateiname in mehreren Ordnern: der spätere zählt
    for f in sorted(dateien.values()):
        m = re.match(r"SNB\d+_(\d+)_hlzf", Path(f).name)
        if not m: continue
        if Path(f).suffix.lower() in (".png", ".jpg", ".jpeg"):
            bericht.append([str(int(m[1])), Path(f).name, "Bilddatei: nicht lesbar (kein OCR)", ""]); continue
        gruppen.setdefault(str(int(m[1])), []).append(f)
    for nr, fs in gruppen.items():           # mehrere Dateien je Netzbetreiber (z. B. MS / NS / Umspannung): Texte zusammen lesen
        f = fs[0] if len(fs) == 1 else ";".join(fs)
        try: t = "\n\n".join(text_aus(x) for x in fs)
        except Exception as e:
            bericht.append([nr, Path(fs[0]).name, "Datei nicht lesbar: " + type(e).__name__, ""]); continue
        f = Path(fs[0])
        e = hlzf_lesen(t, str(f))
        gew = sum(len(v) for eb in e.fenster.values() for v in eb.values()) + 100 * ("NS" in e.fenster) if e.gelesen else 0
        Path(f"ergebnis/hlzf_texte/{nr}.txt").write_text(Path(f).name + "\n\n" + t[:40000], encoding="utf-8")
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
        rows[nr] = [d[h] for h in H]
        bericht.append([nr, Path(f).name, d["hlzf_status"], f"Jahr {e.jahr}"])
    out = sorted(rows.values(), key=lambda r: int(r[0]))
    csv.writer(open("ergebnis/hlzf_ergebnis.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";").writerows([H] + out)
    csv.writer(open("ergebnis/hlzf_eingang_bericht.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";").writerows([["nr", "datei", "ergebnis", "bemerkung"]] + bericht)
    from collections import Counter
    print(Counter(b[2].split(":")[0] if b[2].startswith("nicht") else b[2] for b in bericht))
main()
