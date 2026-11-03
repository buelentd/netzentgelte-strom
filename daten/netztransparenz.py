"""Netztransparenz-Schnittstelle (Übertragungsnetzbetreiber): Zugang prüfen und Datensätze auflisten.

Modus pruefen: zeigt nur, welche Secret-Namen gesetzt sind (ja/nein, nie den Wert), meldet sich an und
listet die angebotenen Datensätze (Pfade der Schnittstellenbeschreibung) im Protokoll.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

ID_NAMEN = ["NETZ_TRANSPARENZ_ID", "NETZ_TRANSPARENZ_API", "NETZ_TRANSPARENZ_CLIENT_ID", "NETZ_TRANSPARENZ_CLIENTID",
            "NETZTRANSPARENZ_CLIENT_ID", "NTP_CLIENT_ID"]
SECRET_NAMEN = ["NETZ_TRANSPARENZ_SECRET", "NETZ_TRANSPARENZ_CLIENT_SECRET", "NETZ_TRANSPARENZ_KEY", "NETZ_TRANSPARENZ",
                "NETZTRANSPARENZ_CLIENT_SECRET", "NTP_CLIENT_SECRET", "NETZTRANSPARENZ"]
NAMEN = ID_NAMEN + SECRET_NAMEN
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


def anmelden():
    cid = next((os.environ[n] for n in ID_NAMEN if os.environ.get(n)), "")
    sec = next((os.environ[n] for n in SECRET_NAMEN if os.environ.get(n)), "")
    kopf = urllib.parse.urlencode({"grant_type": "client_credentials", "client_id": cid, "client_secret": sec}).encode()
    st, body = abruf(TOKEN_URLS[0], kopf, {"Content-Type": "application/x-www-form-urlencoded"})
    print("Anmeldung Status", st)
    if st != 200:
        raise SystemExit("Anmeldung fehlgeschlagen")
    return json.loads(body)["access_token"]


def holen():
    """Holt Marktdaten: negative Preise (stündlich), aktivierte aFRR, Versuche für Monatsmarktwerte (Solar).
    Ergebnis: daten/ntp_negative_preise.csv, daten/ntp_afrr_aktiviert.csv; Marktwert-Versuche nur im Protokoll."""
    import time
    from datetime import date, timedelta
    token = anmelden()
    kopf = {"Authorization": "Bearer " + token}
    basis = "https://ds.netztransparenz.de/api/v1/data/"
    hier = os.path.dirname(os.path.abspath(__file__))
    von = "2025-11-01T00:00:00"
    bis = (date.today() + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00")
    st, body = abruf(basis + f"NegativePreise/1/{von}/{bis}", None, kopf)
    print("NegativePreise Status", st, "Bytes", len(body))
    if st == 200:
        open(os.path.join(hier, "ntp_negative_preise.csv"), "wb").write(body)
    # aktivierte aFRR in 30-Tage-Abschnitten
    kopfzeile, zeilen, ende = None, [], date.fromisoformat(von[:10])
    heute = date.today()
    while ende < heute + timedelta(days=1):
        nxt = min(ende + timedelta(days=30), heute + timedelta(days=1))
        st, body = abruf(basis + f"nrvsaldo/AktivierteSRL/Betrieblich/{ende}T00:00:00/{nxt}T00:00:00", None, kopf)
        if st == 200:
            t = body.decode("utf-8", "replace").splitlines()
            if t:
                kopfzeile = kopfzeile or t[0]; zeilen += t[1:]
        else:
            print("aFRR Abschnitt", ende, "Status", st)
        ende = nxt; time.sleep(1)
    if kopfzeile:
        open(os.path.join(hier, "ntp_afrr_aktiviert.csv"), "w", encoding="utf-8").write(kopfzeile + "\n" + "\n".join(zeilen) + "\n")
        print("aFRR aktiviert:", len(zeilen), "Zeilen")
    # Marktwerte: mehrere Schreibweisen ausprobieren
    for pfad in ("marktpraemie/2026-01-01T00:00:00/2026-11-01T00:00:00", "Monatsmarktwerte/2026-01-01T00:00:00/2026-11-01T00:00:00",
                 "marktpraemie/n/e/2026-01-01T00:00:00/2026-11-01T00:00:00", "marktpraemie/2026/1/2026/10",
                 "Jahresmarktpraemie/2025", "Jahresmarktpraemie/n/e", "Jahresmarktpraemie/2025-01-01T00:00:00/2026-01-01T00:00:00",
                 "marktpraemie/2026-01-01/2026-10-31"):
        st, body = abruf(basis + pfad, None, kopf)
        print("Marktwerte", pfad, "Status", st, "|", body[:200].decode("utf-8", "replace").replace("\n", " "))
        time.sleep(1)


def pruefen():
    gesetzt = {n: bool(os.environ.get(n)) for n in NAMEN}
    print("Gesetzte Secret-Namen:", {n: ("ja" if v else "nein") for n, v in gesetzt.items()})
    cid = next((os.environ[n] for n in ID_NAMEN if os.environ.get(n)), "")
    sec = next((os.environ[n] for n in SECRET_NAMEN if os.environ.get(n)), "")
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
    if token:
        basis = "https://ds.netztransparenz.de/api/v1/data/"
        for pfad in ("Spotmarktpreise/2026-10-30T00:00:00/2026-11-01T00:00:00",
                     "nrvsaldo/AktivierteSRL/Betrieblich/2026-10-30T00:00:00/2026-11-01T00:00:00",
                     "marktpraemie/2026-09-01T00:00:00/2026-10-01T00:00:00",
                     "NegativePreise/1/2026-01-01T00:00:00/2026-11-01T00:00:00"):
            st, body = abruf(basis + pfad, None, {"Authorization": "Bearer " + token})
            print("Abruf", pfad, "Status", st, "Antwort (Anfang):", body[:260].decode("utf-8", "replace").replace("\n", " "))
        return
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
    {"pruefen": pruefen, "holen": holen}[sys.argv[1] if len(sys.argv) > 1 else "pruefen"]()
