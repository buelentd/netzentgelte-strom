"""Lieferpaket: MaStR-Nummer zuerst, keine lokalen Dateinamen als Quelle, Zahlen im Text aus den Daten."""
import csv, io, sys, zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "daten"))
import partnerpaket


def test_paket(tmp_path):
    ziel = tmp_path / "p.zip"
    partnerpaket.bauen(ziel)
    z = zipfile.ZipFile(ziel)
    assert set(z.namelist()) == {"netzentgelte_2026.csv", "plz_netzbetreiber.csv", "LEGENDE.md", "LIES_MICH.md", "AENDERUNGEN.md"}
    for name in ("netzentgelte_2026.csv", "plz_netzbetreiber.csv"):
        rows = list(csv.DictReader(io.StringIO(z.read(name).decode("utf-8-sig")), delimiter=";"))
        assert list(rows[0].keys())[0] == "mastr_nr", name
        assert all(r["mastr_nr"].startswith("SNB") for r in rows)
    tab = list(csv.DictReader(io.StringIO(z.read("netzentgelte_2026.csv").decode("utf-8-sig")), delimiter=";"))
    assert len(tab) == 831 and len({r["mastr_nr"] for r in tab}) == 831
    assert all(not r["hlzf_quelle_url"] or r["hlzf_quelle_url"].startswith("http") for r in tab)
    lies = z.read("LIES_MICH.md").decode("utf-8")
    ok = sum(1 for r in tab if r["status"] == "ok")
    assert f"Status `ok`: {ok} Netzbetreiber" in lies
    assert "40–500" in z.read("LEGENDE.md").decode("utf-8") and "Weitere Dateien in ergebnis/" not in z.read("LEGENDE.md").decode("utf-8")
