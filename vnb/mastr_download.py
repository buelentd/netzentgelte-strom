"""Robuster Download einzelner Dateien aus dem MaStR-Gesamtexport (ZIP auf dem Server).

Der MaStR-Server bricht Verbindungen bei langen Downloads häufig ab. open-mastr gibt dann nach
drei schnellen Versuchen auf und verwirft das bisher Geladene. Hier wird jede benötigte Datei
des Exports per HTTP-Range in Stücken geladen, jedes Stück mit Wiederholungen und wachsender
Wartezeit, und sofort auf die Platte geschrieben. Ein Abbruch verliert höchstens ein Stück; ein
neuer Start (auch im nächsten Workflow-Lauf, über den Cache) setzt an derselben Stelle fort.

Ablage in <ordner>/<exportname>/:
  manifest.json         URL, Dateiliste mit Größen und Kompressionsart
  <Datei>.xml.deflate   komprimierte Rohdaten der Datei (fertig)
  <Datei>.xml.part      unvollständig, wird fortgesetzt
"""
from __future__ import annotations

import io
import json
import struct
import time
import zipfile
import zlib
from datetime import date, datetime, timedelta
from pathlib import Path

import requests

UA = "netzentgelte-strom (https://github.com/buelentd/netzentgelte-strom)"
STUECK = 8 * 1024 * 1024
VERSUCHE = 10


def _warten(versuch: int) -> float:
    return min(300, 5 * 2 ** versuch)


class Http:
    def __init__(self, url: str, log=print):
        self.url = url
        self.log = log
        self.s = requests.Session()
        self.s.headers["User-Agent"] = UA

    def bereich(self, start: int, ende: int) -> bytes:
        """Bytes [start, ende) mit Wiederholungen; unvollständige Antworten werden fortgesetzt."""
        daten = bytearray()
        versuch = 0
        while start + len(daten) < ende:
            von = start + len(daten)
            try:
                r = self.s.get(self.url, headers={"Range": f"bytes={von}-{ende - 1}"}, timeout=(30, 120),
                               stream=True)
                if r.status_code != 206:
                    raise IOError(f"HTTP {r.status_code} (Range nicht unterstützt?)")
                for block in r.iter_content(256 * 1024):
                    daten += block
                versuch = 0
            except (requests.RequestException, IOError) as e:
                versuch += 1
                if versuch > VERSUCHE:
                    raise IOError(f"Download abgebrochen nach {VERSUCHE} Versuchen: {e}") from e
                w = _warten(versuch)
                self.log(f"    Verbindung abgebrochen ({type(e).__name__}), neuer Versuch {versuch}/{VERSUCHE} "
                         f"in {w:.0f} s")
                time.sleep(w)
        return bytes(daten[: ende - start])

    def groesse(self) -> int:
        for versuch in range(1, VERSUCHE + 1):
            try:
                r = self.s.head(self.url, timeout=(30, 60), allow_redirects=True)
                if r.status_code == 404:
                    return -1
                if r.ok and r.headers.get("Content-Length"):
                    return int(r.headers["Content-Length"])
                # Fallback: Größe aus Content-Range einer 1-Byte-Anfrage
                r = self.s.get(self.url, headers={"Range": "bytes=0-0"}, timeout=(30, 60))
                if r.status_code == 404:
                    return -1
                r.raise_for_status()
                return int(r.headers["Content-Range"].rsplit("/", 1)[1])
            except (requests.RequestException, KeyError) as e:
                if versuch == VERSUCHE:
                    raise IOError(f"Exportgröße nicht ermittelbar: {e}") from e
                time.sleep(_warten(versuch))
        return -1


class RangeDatei(io.RawIOBase):
    """Seekbare Datei über HTTP-Range, nur für das Lesen des ZIP-Inhaltsverzeichnisses."""

    def __init__(self, http: Http, groesse: int):
        self.http, self.groesse, self.pos = http, groesse, 0

    def seekable(self):
        return True

    def readable(self):
        return True

    def seek(self, pos, whence=0):
        self.pos = pos if whence == 0 else self.pos + pos if whence == 1 else self.groesse + pos
        return self.pos

    def tell(self):
        return self.pos

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.groesse - self.pos
        n = min(n, self.groesse - self.pos)
        if n <= 0:
            return b""
        d = self.http.bereich(self.pos, self.pos + n)
        self.pos += len(d)
        return d

    def readinto(self, b):
        d = self.read(len(b))
        b[: len(d)] = d
        return len(d)


def export_urls(tag: date) -> list[str]:
    """Mögliche URLs des Exports (Versionsnummer im Namen wechselt, daher mehrere Kandidaten)."""
    from open_mastr.xml_download.utils_download_bulk import gen_xml_download_url
    urls = []
    for t in (tag, tag - timedelta(days=1)):
        st = datetime(t.year, t.month, t.day).timetuple()
        for v in ("current", "before", "after"):
            u = gen_xml_download_url(st, use_version=v)
            if u not in urls:
                urls.append(u)
    return urls


def tabelle(name: str) -> str:
    return name.lower().split("_")[0].split(".")[0]


def herunterladen(ordner: Path, tabellen: set[str], log=print, urls: list[str] | None = None) -> Path:
    """Lädt die Dateien der gewünschten Tabellen; liefert den Ordner mit den Teilen."""
    ordner.mkdir(parents=True, exist_ok=True)
    http = groesse = None
    for url in urls or export_urls(date.today()):
        h = Http(url, log)
        g = h.groesse()
        if g > 0:
            http, groesse = h, g
            break
    if not http:
        raise SystemExit("MaStR-Export nicht gefunden (heute und gestern)")
    name = http.url.rsplit("/", 1)[-1].removesuffix(".zip")
    ziel = ordner / name
    ziel.mkdir(exist_ok=True)
    manifest_pfad = ziel / "manifest.json"
    if manifest_pfad.exists():
        manifest = json.loads(manifest_pfad.read_text())
    else:
        log(f"  Inhaltsverzeichnis von {http.url} ({groesse / 1e9:.1f} GB)")
        with zipfile.ZipFile(RangeDatei(http, groesse)) as z:
            manifest = {"url": http.url, "dateien": [
                {"name": i.filename, "offset": i.header_offset, "groesse": i.compress_size,
                 "entpackt": i.file_size, "methode": i.compress_type, "crc": i.CRC}
                for i in z.infolist() if tabelle(i.filename) in tabellen]}
        manifest_pfad.write_text(json.dumps(manifest, indent=1))
    dateien = manifest["dateien"]
    gesamt = sum(d["groesse"] for d in dateien)
    fertig_bytes = sum(d["groesse"] for d in dateien if (ziel / (d["name"] + ".deflate")).exists())
    log(f"  {len(dateien)} Dateien, {gesamt / 1e9:.2f} GB komprimiert, bereits vorhanden {fertig_bytes / 1e9:.2f} GB")
    t0 = time.time()
    geladen = 0
    for n, d in enumerate(dateien, 1):
        fertig = ziel / (d["name"] + ".deflate")
        if fertig.exists():
            continue
        teil = ziel / (d["name"] + ".part")
        # lokaler Dateikopf: 30 Bytes + Name + Extra-Feld, danach beginnen die Daten
        kopf = http.bereich(d["offset"], d["offset"] + 30)
        name_len, extra_len = struct.unpack("<HH", kopf[26:30])
        start = d["offset"] + 30 + name_len + extra_len
        vorhanden = teil.stat().st_size if teil.exists() else 0
        with open(teil, "ab") as f:
            pos = vorhanden
            while pos < d["groesse"]:
                bis = min(pos + STUECK, d["groesse"])
                f.write(http.bereich(start + pos, start + bis))
                f.flush()
                geladen += bis - pos
                pos = bis
        teil.rename(fertig)
        dauer = time.time() - t0
        rate = geladen / dauer if dauer else 0
        rest = gesamt - fertig_bytes - geladen
        log(f"  [{n}/{len(dateien)}] {d['name']} ({d['groesse'] / 1e6:.0f} MB), "
            f"{rate / 1e6:.1f} MB/s, noch ca. {rest / rate / 60 if rate else 0:.0f} min")
    (ziel / "vollstaendig").write_text(datetime.now().isoformat())
    return ziel


class Teile:
    """Liest heruntergeladene Teile wie ein ZipFile (namelist/open), entpackt beim Lesen."""

    def __init__(self, ordner: Path):
        self.ordner = ordner
        self.manifest = json.loads((ordner / "manifest.json").read_text())
        self.info = {d["name"]: d for d in self.manifest["dateien"]}

    def namelist(self):
        return [n for n in self.info if (self.ordner / (n + ".deflate")).exists()]

    def open(self, name):
        d = self.info[name]
        roh = open(self.ordner / (name + ".deflate"), "rb")
        if d["methode"] == zipfile.ZIP_STORED:
            return roh
        if d["methode"] != zipfile.ZIP_DEFLATED:
            raise ValueError(f"Kompression {d['methode']} nicht unterstützt")
        return _Entpacker(roh)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _Entpacker(io.RawIOBase):
    def __init__(self, roh):
        self.roh = roh
        self.z = zlib.decompressobj(-15)
        self.puffer = b""

    def readable(self):
        return True

    def read(self, n=-1):
        if n is None or n < 0:
            n = 1 << 30
        while len(self.puffer) < n:
            block = self.roh.read(1024 * 1024)
            if not block:
                self.puffer += self.z.flush()
                break
            self.puffer += self.z.decompress(block)
        out, self.puffer = self.puffer[:n], self.puffer[n:]
        return out

    def readinto(self, b):
        d = self.read(len(b))
        b[: len(d)] = d
        return len(d)

    def close(self):
        self.roh.close()
        super().close()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()
        return False


def vollstaendig(ordner: Path) -> bool:
    return (ordner / "vollstaendig").exists()
