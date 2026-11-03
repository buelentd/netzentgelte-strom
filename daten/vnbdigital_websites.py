"""Prüft die Websites der 222 Problemfälle (Status kein_preisblatt, blockiert) gegen die Website in vnbdigital.de.
Je Netzbetreiber: Namenssuche, nur eindeutiger Treffer (gleicher Name nach Normalisierung), dann get_operator.
Eine Abfrage alle 2,5 Sekunden (läuft parallel zum großen Lauf, zusammen unter einer Abfrage je Sekunde).
Ergebnis: daten/vnbdigital_websites.json. Ändert die Ergebnisdatei nicht."""
import csv, json, re, time
from pathlib import Path
from urllib.parse import urlparse
from vnbdigital_client import VNBDigitalClient

HIER = Path(__file__).parent
CSV = HIER.parent / "ergebnis" / "netzentgelte_2026.csv"
AUS = HIER / "vnbdigital_websites.json"


def norm(s):
    s = (s or "").lower().replace("&", "und")
    return re.sub(r"[^a-z0-9äöüß]+", "", s)


def domain(u):
    if not u:
        return ""
    if "//" not in u:
        u = "//" + u
    h = (urlparse(u).hostname or "").lower()
    return h[4:] if h.startswith("www.") else h


def main():
    zeilen = [r for r in csv.DictReader(open(CSV, encoding="utf-8"), delimiter=";") if r["status"] in ("kein_preisblatt", "blockiert")]
    print(len(zeilen), "Fälle")
    erg = json.loads(AUS.read_text()) if AUS.exists() else {}
    c = VNBDigitalClient()
    for z in zeilen:
        nr = z["nr"]
        if nr in erg:
            continue
        e = {"netzbetreiber": z["netzbetreiber"], "unsere_website": z["website"], "status": z["status"]}
        try:
            t = c.search(z["netzbetreiber"])
            time.sleep(2.5)
            tr = [r for r in t if norm(r.title) == norm(z["netzbetreiber"])]
            e["treffertypen"] = sorted({r.type for r in t})
            if len(tr) == 1:
                o = c.get_operator(tr[0].id)
                time.sleep(2.5)
                e["vnb_id"] = tr[0].id
                e["vnb_website"] = o.website
                e["gleich"] = domain(o.website) == domain(z["website"])
            else:
                e["ergebnis"] = "kein eindeutiger Treffer" if not tr else "mehrere Treffer"
        except Exception as ex:
            e["fehler"] = f"{type(ex).__name__}: {str(ex)[:150]}"
            time.sleep(2.5)
        erg[nr] = e
        print(nr, json.dumps(e, ensure_ascii=False)[:300], flush=True)
        AUS.write_text(json.dumps(erg, ensure_ascii=False, indent=1))


main()
