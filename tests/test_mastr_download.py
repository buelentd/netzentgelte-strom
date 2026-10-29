"""Robuster Download aus dem MaStR-Export: lokaler Server mit Range-Anfragen, der Verbindungen
mitten in der Antwort abbricht (wie download.marktstammdatenregister.de)."""
import re
import threading
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from tests.test_mastr_xml import export
from vnb import mastr_download, mastr_xml

ZAEHLER = {"get": 0}


def _server(daten: bytes, abbruch_jede: int):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_HEAD(self):
            self.send_response(200)
            self.send_header("Content-Length", str(len(daten)))
            self.end_headers()

        def do_GET(self):
            ZAEHLER["get"] += 1
            m = re.match(r"bytes=(\d+)-(\d+)", self.headers.get("Range", ""))
            von, bis = int(m.group(1)), int(m.group(2)) + 1
            teil = daten[von:bis]
            self.send_response(206)
            self.send_header("Content-Length", str(len(teil)))
            self.end_headers()
            if abbruch_jede and ZAEHLER["get"] % abbruch_jede == 0:
                self.wfile.write(teil[: len(teil) // 2])          # halbe Antwort, dann Abbruch
                self.wfile.flush()
                self.connection.close()
                return
            self.wfile.write(teil)

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


@pytest.fixture
def schnell(monkeypatch):
    monkeypatch.setattr(mastr_download, "STUECK", 4096)       # viele kleine Stücke
    monkeypatch.setattr(mastr_download, "_warten", lambda v: 0.01)


def test_download_mit_abbruechen(tmp_path, schnell):
    zip_pfad = export(tmp_path / "quelle")
    # Solardaten groß genug für mehrere Stücke, schlecht komprimierbar
    import os
    with zipfile.ZipFile(zip_pfad, "a", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("Gross_1.xml", os.urandom(50_000))
    daten = zip_pfad.read_bytes()
    httpd = _server(daten, abbruch_jede=3)
    url = f"http://127.0.0.1:{httpd.server_address[1]}/Gesamtdatenexport_20261029_26.2.zip"
    try:
        ziel = mastr_download.herunterladen(tmp_path / "dl", set(mastr_xml.TABELLEN) | {"gross"},
                                            log=lambda *a: None, urls=[url])
    finally:
        httpd.shutdown()
    assert mastr_download.vollstaendig(ziel)
    teile = mastr_download.Teile(ziel)
    with zipfile.ZipFile(zip_pfad) as z:
        for name in z.namelist():
            assert teile.open(name).read() == z.read(name), name   # bytegenau trotz Abbrüchen
    akteure, *_ = mastr_xml.lesen(ziel, log=lambda *a: None)
    assert set(akteure["MastrNummer"]) == {"SNB1", "SNB2", "SNB3"}


def test_download_fortsetzen_nach_abbruch(tmp_path, schnell, monkeypatch):
    zip_pfad = export(tmp_path / "quelle")
    httpd = _server(zip_pfad.read_bytes(), abbruch_jede=0)
    url = f"http://127.0.0.1:{httpd.server_address[1]}/Gesamtdatenexport_20261029_26.2.zip"
    echt = mastr_download.Http.bereich
    aufrufe = {"n": 0}

    def stirbt(self, a, b):                                     # Lauf bricht nach 6 Anfragen ganz ab
        aufrufe["n"] += 1
        if aufrufe["n"] > 6:
            raise KeyboardInterrupt
        return echt(self, a, b)
    try:
        monkeypatch.setattr(mastr_download.Http, "bereich", stirbt)
        with pytest.raises(KeyboardInterrupt):
            mastr_download.herunterladen(tmp_path / "dl", set(mastr_xml.TABELLEN), log=lambda *a: None, urls=[url])
        ziel = tmp_path / "dl" / "Gesamtdatenexport_20261029_26.2"
        schon_fertig = {p.name for p in ziel.glob("*.deflate")}
        assert not mastr_download.vollstaendig(ziel)
        monkeypatch.setattr(mastr_download.Http, "bereich", echt)
        ZAEHLER["get"] = 0
        mastr_download.herunterladen(tmp_path / "dl", set(mastr_xml.TABELLEN), log=lambda *a: None, urls=[url])
    finally:
        httpd.shutdown()
    assert mastr_download.vollstaendig(ziel)
    assert schon_fertig <= {p.name for p in ziel.glob("*.deflate")}
    assert set(mastr_xml.lesen(ziel, log=lambda *a: None)[0]["MastrNummer"]) == {"SNB1", "SNB2", "SNB3"}
