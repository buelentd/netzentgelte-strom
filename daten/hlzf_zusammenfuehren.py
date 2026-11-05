"""Hochlastzeitfenster (HLZF) aus der Liste des Nutzers und aus unserem Leser zusammenführen -> lauf/hlzf_zusammen.csv (Schlüssel MaStR-Nr).
Regel: die Werte des Nutzers gewinnen (Festlegung Nutzer 04.11.2026); unsere nur, wenn das Dokument 2026 ist und der Leser 'gelesen' meldet.
hlzf_status: gelesen_nutzer | gelesen_unser | zeitfenster_nicht_lesbar | raster_grafik | keine_im_dokument | jahr_nicht_2026 | pruefung_offen | kein_dokument_oder_adresse
Aufruf: PYTHONPATH=. python daten/hlzf_zusammenfuehren.py"""
import csv
from collections import Counter
J = ["fruehling", "sommer", "herbst", "winter"]
COLS = [f"hlzf_ns_{x}" for x in J] + [f"hlzf_msns_{x}" for x in J] + ["hlzf_schwelle_prozent", "hlzf_mindestleistung_kw", "hlzf_quelle_url"]

def status_unser(s, jahr, pruefung=""):
    if s == "gelesen" and jahr == "2026": return "gelesen_unser"
    if s == "gelesen, Prüfung offen" and pruefung.startswith("ungeprüft neu gelesen"): return "gelesen_ungeprueft"
    if s.startswith("gelesen, Jahr") or (s == "gelesen" and jahr not in ("2026", "")): return "jahr_nicht_2026"
    if s == "gelesen, Prüfung offen": return "pruefung_offen"
    if "Raster" in s: return "raster_grafik"
    if "keine Hochlastzeitfenster" in s: return "keine_im_dokument"
    if "nur für Mittelspannung" in s: return "nur_mittelspannung"
    if "nicht lesbar" in s or "nicht vollständig gelesen" in s or "Scan" in s: return "zeitfenster_nicht_lesbar"
    return "kein_dokument_oder_adresse"

def main():
    T = {r["nr"]: r["mastr_nr"] for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
    unser = {r["nr"]: r for r in csv.DictReader(open("ergebnis/hlzf_ergebnis.csv", encoding="utf-8-sig"), delimiter=";")}
    nutzer = {r["nr"]: r for r in csv.DictReader(open("ergebnis/FORMAT_NEU_netzentgelte_final_alle_3_ergaenzt.csv", encoding="utf-8-sig"), delimiter=";")}
    out, z = [], Counter()
    for nr, mastr in T.items():
        n, u = nutzer.get(nr), unser.get(nr)
        werte, st = {c: "" for c in COLS}, None
        if n and any(n.get(f"hlzf_ns_{x}") or n.get(f"hlzf_msns_{x}") for x in J):
            for c in COLS: werte[c] = n.get(c, "")
            st = "gelesen_nutzer"
        elif u:
            st = status_unser(u["hlzf_status"], u["hlzf_jahr"], u.get("hlzf_pruefung", ""))
            if st in ("gelesen_unser", "gelesen_ungeprueft"):
                for c in COLS: werte[c] = u.get(c, "")
            else:
                werte["hlzf_quelle_url"] = u.get("hlzf_quelle_url", "")
        else:
            st = "kein_dokument_oder_adresse"
        z[st] += 1
        out.append([mastr, st] + [werte[c] for c in COLS])
    with open("lauf/hlzf_zusammen.csv", "w", encoding="utf-8-sig", newline="") as o:
        w = csv.writer(o, delimiter=";"); w.writerow(["mastr_nr", "hlzf_status"] + COLS); w.writerows(out)
    print(dict(z))
main()
