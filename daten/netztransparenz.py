"""Netztransparenz-Schnittstelle (Übertragungsnetzbetreiber): Zugang prüfen und Datensätze auflisten.

Modus pruefen: zeigt nur, welche Secret-Namen gesetzt sind (ja/nein, nie den Wert), meldet sich an und
listet die angebotenen Datensätze (Pfade der Schnittstellenbeschreibung) im Protokoll.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

NAMEN = ["NETZTRANSPARENZ", "NETZ_TRANSPARENZ", "NETZTRANSPARENZ_SCHLUESSEL", "NETZTRANSPARENZ_TOKEN",
         "NETZTRANSPARENZ_CLIENT_ID", "NETZTRANSPARENZ_CLIENT_SECRET", "NTP_CLIENT_ID", "NTP_CLIENT_SECRET"]
TOKEN_URLS = ["https://identity.netztransparenz.de/users/connect/token"]
DOKU_URLS = ["https://ds.netztransparenz.de/swagger/v1/swagger.json", "https://ds.netztransparenz.de/api/swagger.json",
             "https://ds.netztransparenz.de/swagger/docs/v1"]


def abruf(url, daten=None, kopf=None):
    req = urllib.request.Request(url, data=daten, headers={"User-Agent": "netzentgelte-strom", **(kopf or {})})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:300]
    except Exception as e:
        return 0, str(e).encode()[:300]


def pruefen():
    gesetzt = {n: bool(os.environ.get(n)) for n in NAMEN}
    print("Gesetzte Secret-Namen:", {n: ("ja" if v else "nein") for n, v in gesetzt.items()})
    cid = next((os.environ[n] for n in ("NETZTRANSPARENZ_CLIENT_ID", "NTP_CLIENT_ID") if os.environ.get(n)), "")
    sec = next((os.environ[n] for n in ("NETZTRANSPARENZ_CLIENT_SECRET", "NTP_CLIENT_SECRET", "NETZTRANSPARENZ", "NETZ_TRANSPARENZ",
                                        "NETZTRANSPARENZ_SCHLUESSEL", "NETZTRANSPARENZ_TOKEN") if os.environ.get(n)), "")
    token = ""
    if cid and sec:
        for u in TOKEN_URLS:
            kopf = urllib.parse.urlencode({"grant_type": "client_credentials", "client_id": cid, "client_secret": sec}).encode()
            st, body = abruf(u, kopf, {"Content-Type": "application/x-www-form-urlencoded"})
            print("Anmeldung", u, "Status", st)
            if st == 200:
                token = json.loads(body).get("access_token", ""); break
    else:
        print("Client-ID und Client-Secret nicht beide gefunden; Anmeldung übersprungen")
    for u in DOKU_URLS:
        st, body = abruf(u, None, {"Authorization": "Bearer " + token} if token else {})
        print("Beschreibung", u, "Status", st)
        if st == 200:
            try:
                pfade = sorted(json.loads(body).get("paths", {}))
                print(len(pfade), "Pfade:"); [print("  ", p) for p in pfade]
            except Exception as e:
                print("keine auswertbare Beschreibung", str(e)[:100])
            break


if __name__ == "__main__":
    {"pruefen": pruefen}[sys.argv[1] if len(sys.argv) > 1 else "pruefen"]()
