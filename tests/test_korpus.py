"""Prüfstand: Der Leser läuft über die gesicherten Dokumenttexte (ergebnis/link_text) und darf nicht schlechter werden.
Die Untergrenzen sind der Stand vom 04.11.2026; steigen sie, werden sie hier angehoben."""
import glob
from pathlib import Path

import pytest

from vnb.extract import auswerten, plausibel_reihenfolge

TEXTE = sorted(glob.glob(str(Path(__file__).parent.parent / "ergebnis" / "link_text" / "*.txt")))


def _lesen(tmp_path):
    erg = {}
    for f in TEXTE:
        url, _, body = Path(f).read_text(encoding="utf-8").partition("\n\n")
        if "Sorry, you have been blocked" in body or len(body.strip()) < 200:
            continue
        p = tmp_path / (Path(f).stem + ".html")
        p.write_text(body, encoding="utf-8")
        erg[Path(f).stem] = (url, body, auswerten(p, url, 2026))
    return erg


@pytest.mark.skipif(len(TEXTE) < 40, reason="Dokumenttexte fehlen")
def test_korpus_nicht_schlechter(tmp_path):
    erg = _lesen(tmp_path)
    mit_werten = [k for k, (_, _, e) in erg.items() if e.ns or e.msns or e.slp]
    ns_slp = [k for k, (_, _, e) in erg.items() if len(e.ns) == 4 and e.slp.get("ap") is not None]
    ms = [k for k, (_, _, e) in erg.items() if len(e.ms) == 4]
    assert len(mit_werten) >= 38
    assert len(ns_slp) >= 13
    assert len(ms) >= 18
    # Mittelspannung: Gesamtkosten bei 4.000 Stunden müssen MS <= MS/NS <= NS ergeben
    for k in ms:
        e = erg[k][2]
        assert not plausibel_reihenfolge(e.ms, e.msns, e.ns), (k, plausibel_reihenfolge(e.ms, e.msns, e.ns))


@pytest.mark.skipif(len(TEXTE) < 40, reason="Dokumenttexte fehlen")
def test_korpus_jeder_wert_steht_im_text(tmp_path):
    import re
    for k, (url, body, e) in _lesen(tmp_path).items():
        for name, d in (("NS", e.ns), ("MSNS", e.msns), ("MS", e.ms), ("HSMS", e.hsms), ("SLP", e.slp)):
            for feld, v in (d or {}).items():
                s = f"{v:.2f}".replace(".", ",")
                kurz = {s, s.rstrip("0").rstrip(","), f"{v:.1f}".replace(".", ",")}
                assert any(re.search(r"(?<![\d,])" + re.escape(x) + r"(?!\d)", body) for x in kurz), (k, name, feld, v)
