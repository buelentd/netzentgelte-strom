"""Fälle aus dem Abgleich mit dem Leser des Nutzers (Layout-Texte aus ergebnis/texte_layout)."""
import glob
from pathlib import Path
import pytest
from vnb.extract import auswerten

FAELLE = {   # MaStR-Nr: {Ebene: (LP<, AP<, LP>=, AP>=)}
    "SNB938624241519": {"ms": (12.42, 8.04, 188.31, 1.0), "msns": (12.56, 8.88, 216.79, 0.71), "ns": (14.84, 9.0, 138.01, 4.07)},   # Trossingen: Label nach den Zahlen, §14a-Tabelle
}
SUCHE = {   # nach Name im Text, falls MaStR-Datei fehlt
    "garmisch": ("Garmisch", {"ns": (15.67, 9.94, 244.61, 0.79)}),   # Zeile "Kommunalrabatt" darf nicht gelten
    "dreieich": ("Dreieich", {"ns": (9.5, 8.44, 182.23, 1.53)}),     # Beispieltabelle "Jahresverbrauch von" darf nicht gelten
}
K = ["lp_unter_2500", "ap_unter_2500", "lp_ueber_2500", "ap_ueber_2500"]

def _lesen(pfad, tmp_path):
    p = tmp_path / "a.html"; p.write_text(Path(pfad).read_text(encoding="utf8", errors="replace"), encoding="utf8")
    return auswerten(p, "https://x.de/a.pdf", 2026)

@pytest.mark.parametrize("mastr,erwartet", list(FAELLE.items()))
def test_trossingen(mastr, erwartet, tmp_path):
    f = glob.glob(f"ergebnis/texte_layout/{mastr}_*.txt")
    if not f: pytest.skip("Layout-Text fehlt")
    e = _lesen(f[0], tmp_path)
    for eb, w in erwartet.items():
        assert tuple(round(getattr(e, eb)[k], 2) for k in K) == w

@pytest.mark.parametrize("key", list(SUCHE))
def test_garmisch_dreieich(key, tmp_path):
    name, erwartet = SUCHE[key]
    treffer = [f for f in glob.glob("ergebnis/texte_layout/SNB*.txt") if name in Path(f).read_text(encoding="utf8", errors="replace")[:600]]
    if not treffer: pytest.skip("Layout-Text fehlt")
    e = _lesen(treffer[0], tmp_path)
    for eb, w in erwartet.items():
        assert tuple(round(getattr(e, eb)[k], 2) for k in K) == w
