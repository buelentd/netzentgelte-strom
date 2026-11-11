"""Schutz gegen verrutschte Nummern: Listen, die nur über `nr` zugeordnet sind, müssen zum Netzbetreiber der Tabelle passen.
Anlass: Die Nutzerliste hatte eine eigene Nummerierung, Hochlastzeitfenster standen bei rund 120 Netzbetreibern falsch (11.11.2026).
Prüft Name bzw. MaStR-Nr. je `nr` in den Listen, die einen Namen oder eine MaStR-Nr. führen."""
import csv, re, unicodedata
from pathlib import Path

W = Path(__file__).parent.parent


def norm(s):
    s = unicodedata.normalize("NFKC", s).lower().replace("ß", "ss").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("＆", "&")
    s = re.sub(r"\b(gmbh|ag|kg|mbh|ohg|e\.?k\.?|e\.?v\.?|aör|ku|co|und|&|der|die|des)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", "", s)


def tabelle():
    return {r["nr"]: r for r in csv.DictReader(open(W / "ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}


def pruefen(pfad, name_spalte="netzbetreiber", mastr_spalte=None):
    T, fehler = tabelle(), []
    for r in csv.DictReader(open(W / pfad, encoding="utf-8-sig"), delimiter=";"):
        t = T.get(r["nr"])
        if t is None:
            fehler.append((r["nr"], "nr nicht in der Tabelle")); continue
        if mastr_spalte and r.get(mastr_spalte) and r[mastr_spalte] != t["mastr_nr"]:
            fehler.append((r["nr"], r[mastr_spalte], t["mastr_nr"]))
        elif r.get(name_spalte) and norm(r[name_spalte])[:10] != norm(t["netzbetreiber"])[:10]:
            fehler.append((r["nr"], r[name_spalte], t["netzbetreiber"]))
    return fehler


def test_preise_manuell_passt_zur_tabelle():
    assert pruefen("lauf/preise_manuell.csv") == []


def test_freigaben_passen_zur_tabelle():
    assert pruefen("lauf/ok_freigabe_nutzer.csv", mastr_spalte="mastr_nr") == []


def test_sonderfaelle_passen_zur_tabelle():
    assert pruefen("lauf/sonderfall_nutzer.csv", mastr_spalte="mastr_nr") == []


def test_nur_nr_listen_verweisen_auf_vorhandene_netzbetreiber():
    T = tabelle()
    for f in ("lauf/beleg_manuell.csv", "lauf/werte_entfernt.csv", "lauf/zuordnung_unbelegt.csv", "lauf/beleg_offen.csv", "lauf/hlzf_urls.csv"):
        for r in csv.DictReader(open(W / f, encoding="utf-8-sig"), delimiter=";"):
            assert r["nr"] in T, f"{f}: nr {r['nr']} nicht in der Tabelle"


def test_hlzf_nutzerliste_ist_ueber_mastr_zugeordnet():
    """Nutzerliste (eigene alphabetische Nummerierung): die Zuordnung darf nicht über nr laufen. Bei Zeilen mit MaStR-Nr. muss der Name zur Tabelle passen."""
    T = {r["mastr_nr"]: r for r in tabelle().values()}
    for r in csv.DictReader(open(W / "ergebnis/FORMAT_NEU_netzentgelte_final_alle_3_ergaenzt.csv", encoding="utf-8-sig"), delimiter=";"):
        m = (r.get("mastr_nr") or "").strip()
        if m in T:
            assert norm(r["netzbetreiber"])[:8] == norm(T[m]["netzbetreiber"])[:8], (r["nr"], r["netzbetreiber"], T[m]["netzbetreiber"])
