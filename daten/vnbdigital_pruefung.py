"""Vollständige Prüfung der 222 Problemfälle (Status kein_preisblatt, blockiert) gegen vnbdigital.de.
Je Netzbetreiber wird alles gesichert: alle Suchtreffer (Name, Typ, Titel, Untertitel, Link) und für jeden Treffer
außer Postleitzahlen die vollständige Antwort der Detailabfrage (Website, Dokumente, Dienste, alle Felder).
Eine Abfrage alle 2,5 Sekunden. Ergebnis: daten/vnbdigital_pruefung.json (öffentliche Angaben). Ändert die Ergebnisdatei nicht."""
import csv, json, re, time
from pathlib import Path
from urllib.parse import urlparse
from vnbdigital_client import VNBDigitalClient

HIER = Path(__file__).parent
CSV = HIER.parent / "ergebnis" / "netzentgelte_2026.csv"
AUS = HIER / "vnbdigital_pruefung.json"
PAUSE = 2.5
MAX_TREFFER = 5


def norm(s):
    return re.sub(r"[^a-z0-9äöüß]+", "", (s or "").lower().replace("&", "und"))


def domain(u):
    if not u:
        return ""
    h = (urlparse(u if "//" in u else "//" + u).hostname or "").lower()
    return h[4:] if h.startswith("www.") else h


def main():
    zeilen = [r for r in csv.DictReader(open(CSV, encoding="utf-8"), delimiter=";") if r["status"] in ("kein_preisblatt", "blockiert")]
    print(len(zeilen), "Fälle", flush=True)
    erg = json.loads(AUS.read_text()) if AUS.exists() else {}
    c = VNBDigitalClient()
    for z in zeilen:
        if z["nr"] in erg:
            continue
        e = {"netzbetreiber": z["netzbetreiber"], "unsere_website": z["website"], "status": z["status"], "treffer": []}
        try:
            treffer = c.search(z["netzbetreiber"])
        except Exception as ex:
            e["fehler"] = f"Suche: {type(ex).__name__}: {str(ex)[:150]}"
            treffer = []
        time.sleep(PAUSE)
        n = 0
        for r in treffer:
            t = {"id": r.id, "typ": r.type, "titel": r.title, "untertitel": r.subtitle, "url": r.url,
                 "name_gleich": norm(r.title) == norm(z["netzbetreiber"])}
            if r.type != "POSTCODE" and n < MAX_TREFFER:
                n += 1
                try:
                    d = c.get_operator_details(r.id)
                    t["details"] = d.raw if hasattr(d, "raw") else d
                    t["website_gleich"] = domain(d.website) == domain(z["website"])
                except Exception as ex:
                    t["details_fehler"] = f"{type(ex).__name__}: {str(ex)[:150]}"
                time.sleep(PAUSE)
            e["treffer"].append(t)
        erg[z["nr"]] = e
        print(z["nr"], z["netzbetreiber"][:40], len(e["treffer"]), "Treffer", flush=True)
        AUS.write_text(json.dumps(erg, ensure_ascii=False, indent=1))


main()
