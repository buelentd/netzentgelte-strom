"""Kleiner Test: vnbdigital.de (inoffizielle GraphQL-Schnittstelle über das Paket vnbdigital-client) gegen unsere Zuordnung
Postleitzahl -> Netzbetreiber vergleichen. 20 Postleitzahlen, höchstens eine Abfrage pro Sekunde, vorher robots.txt lesen.
Ergebnis: daten/vnbdigital_test.json (nur Namen der Netzbetreiber, öffentliche Angaben)."""
import json
import random
import time
import urllib.request
from pathlib import Path

HIER = Path(__file__).parent
ERG = HIER.parent / "ergebnis" / "conplot"
PLZ_FEST = ["88400", "08393"]


def robots():
    try:
        with urllib.request.urlopen(urllib.request.Request("https://www.vnbdigital.de/robots.txt", headers={"User-Agent": "netzentgelte-strom"}), timeout=30) as r:
            t = r.read().decode("utf-8", "replace")
        print("robots.txt:\n" + t[:1500])
        return t
    except Exception as e:
        print("robots.txt nicht lesbar:", type(e).__name__, str(e)[:150])
        return ""


def main():
    t = robots()
    # Abbruch, wenn alles gesperrt ist
    if "Disallow: /" in [z.strip() for z in t.splitlines()] and "User-agent: *" in t:
        print("robots.txt sperrt alles: Abbruch"); return
    from vnbdigital_client import VNBDigitalClient
    plz = json.load(open(ERG / "plz_2026.json", encoding="utf-8"))
    nb = {e["nr"]: e["netzbetreiber"] for e in json.load(open(ERG / "netzbetreiber_2026.json", encoding="utf-8"))["netzbetreiber"]}
    zufall = random.Random(7)
    mehrere = [k for k, v in plz.items() if len(v) >= 2 and k not in PLZ_FEST]
    einzeln = [k for k, v in plz.items() if len(v) == 1 and k not in PLZ_FEST]
    wahl = PLZ_FEST + zufall.sample(mehrere, 9) + zufall.sample(einzeln, 9)
    c = VNBDigitalClient()
    ergebnis = {}
    for k in wahl:
        unsere = [(nb.get(e["nr"], "?"), e["anteil_prozent"]) for e in plz[k]]
        eintrag = {"unsere": unsere}
        try:
            treffer = c.search(k)
            time.sleep(1.1)
            pc = next((r for r in treffer if r.type == "POSTCODE"), None)
            if pc:
                d = c.search_by_postcode(pc.id)
                time.sleep(1.1)
                eintrag["vnbdigital"] = [v.get("name") for v in d.get("vnbs", [])]
            else:
                eintrag["vnbdigital"] = None
                eintrag["treffer_typen"] = [r.type for r in treffer][:5]
        except Exception as e:
            eintrag["fehler"] = f"{type(e).__name__}: {str(e)[:200]}"
            time.sleep(1.1)
        ergebnis[k] = eintrag
        print(k, json.dumps(eintrag, ensure_ascii=False)[:400])
    # Felder eines Netzbetreibers ansehen (nur Struktur)
    try:
        r = c.search("Stadtwerke Meerane")
        time.sleep(1.1)
        print("Suche Name, Typen:", [(x.type, x.title) for x in r][:5])
    except Exception as e:
        print("Namenssuche Fehler:", str(e)[:150])
    (HIER / "vnbdigital_test.json").write_text(json.dumps(ergebnis, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
