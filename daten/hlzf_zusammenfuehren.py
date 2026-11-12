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
    if s == "gelesen, Jahr 2027" and not pruefung: return "gelesen_aus_2027"   # Festlegung 12.11.2026: 2027-Fund zählt für 2026 und 2027
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
    # Liste des Nutzers: ihre laufende Nummer ist eine andere als unsere (alphabetisch, 473 Zeilen); Zuordnung über MaStR-Nr., sonst über den Namen (Fehler vom 11.11.2026: vorher über `nr`, dadurch standen die Fenster beim falschen Netzbetreiber)
    import re, unicodedata
    def norm(s):
        s = unicodedata.normalize("NFKC", s).lower().replace("ß", "ss").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("＆", "&")
        s = re.sub(r"\b(gmbh|ag|kg|mbh|ohg|e\.?k\.?|e\.?v\.?|aör|ku|co|und|&|der|die|des)\b", " ", s)
        return re.sub(r"[^a-z0-9]+", "", s)
    tab = list(csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";"))
    nach_name = {}
    for t_ in tab: nach_name.setdefault(norm(t_["netzbetreiber"]), []).append(t_["mastr_nr"])
    gueltig = {t_["mastr_nr"] for t_ in tab}
    nutzer = {}
    for r in csv.DictReader(open("ergebnis/FORMAT_NEU_netzentgelte_final_alle_3_ergaenzt.csv", encoding="utf-8-sig"), delimiter=";"):
        m_ = (r.get("mastr_nr") or "").strip()
        if m_ not in gueltig:
            c_ = nach_name.get(norm(r["netzbetreiber"]), [])
            m_ = c_[0] if len(c_) == 1 else ""
        if m_ and (m_ not in nutzer or any(r.get(f"hlzf_{e}_{j}") for e in ("ns", "msns") for j in J) and not any(nutzer[m_].get(f"hlzf_{e}_{j}") for e in ("ns", "msns") for j in J)):
            nutzer[m_] = r
    import os
    kol = {r["mastr_nr"]: r for r in csv.DictReader(open("lauf/hlzf_kollege_verifiziert.csv", encoding="utf-8-sig"), delimiter=";")} if os.path.exists("lauf/hlzf_kollege_verifiziert.csv") else {}
    out, z = [], Counter()
    KONFLIKT = []
    for nr, mastr in T.items():
        n, u = nutzer.get(mastr), unser.get(nr)
        werte, st = {c: "" for c in COLS}, None
        st_u = status_unser(u["hlzf_status"], u["hlzf_jahr"], u.get("hlzf_pruefung", "")) if u else None
        n_hat = bool(n and any(n.get(f"hlzf_ns_{x}") or n.get(f"hlzf_msns_{x}") for x in J))
        if n_hat and st_u == "gelesen_unser":
            # Beide haben das 2026-Dokument gelesen: gleiche Werte -> Liste des Nutzers; verschieden -> unser Leser (am Dokumenttext geprüft, Stichprobe Abita/Regionetz 11.11.2026: Nutzerliste dort falsch) und Eintrag in die Konfliktliste
            gleich = all((n.get(c, "") or "") == (u.get(c, "") or "") for c in COLS if c.startswith(("hlzf_ns_", "hlzf_msns_")))
            if not gleich: KONFLIKT.append([mastr, nr, u.get("hlzf_quelle_url", ""), n.get("hlzf_quelle_url", "")] + [n.get(c, "") for c in COLS[:8]] + [u.get(c, "") for c in COLS[:8]])
            n_hat = gleich
        if n_hat:
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
        if mastr in kol and st not in ("gelesen_nutzer", "gelesen_unser"):
            for c in COLS: werte[c] = kol[mastr].get(c, "")
            st = kol[mastr].get("hlzf_status") or "gelesen_kollege_verifiziert"   # Kollege am Original-PDF gelesen, von uns am Dokumenttext geprüft (09.11.2026)
        z[st] += 1
        out.append([mastr, st] + [werte[c] for c in COLS])
    with open("lauf/hlzf_zusammen.csv", "w", encoding="utf-8-sig", newline="") as o:
        w = csv.writer(o, delimiter=";"); w.writerow(["mastr_nr", "hlzf_status"] + COLS); w.writerows(out)
    with open("ergebnis/hlzf_konflikt_nutzerliste_leser.csv", "w", encoding="utf-8-sig", newline="") as o:
        w = csv.writer(o, delimiter=";"); w.writerow(["mastr_nr", "nr", "quelle_unser", "quelle_nutzerliste"] + ["nutzer_" + c[5:] for c in COLS[:8]] + ["unser_" + c[5:] for c in COLS[:8]]); w.writerows(KONFLIKT)
    print(dict(z), "Konflikte:", len(KONFLIKT))
main()
