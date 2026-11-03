"""Eine einzige Abfrage (Postleitzahl 08393 und Name 'Stadtwerke Meerane'): rohe Antwort von vnbdigital.de im Protokoll zeigen,
um zu sehen, welche Felder und Links zu einem Netzbetreiber geliefert werden (zum Beispiel Website, Dokumente, Preisblatt-Links).
Nichts wird gespeichert."""
import dataclasses
import json
import time

from vnbdigital_client import VNBDigitalClient


def roh(x, grenze=5000):
    try:
        if dataclasses.is_dataclass(x):
            x = dataclasses.asdict(x)
        elif hasattr(x, "__dict__") and not isinstance(x, (dict, list)):
            x = vars(x)
        return json.dumps(x, ensure_ascii=False, default=str)[:grenze]
    except Exception as e:
        return f"{type(x).__name__}: {x!r}"[:grenze] + f" ({e})"


c = VNBDigitalClient()
treffer = c.search("08393")
time.sleep(2)
print("Suche 08393:", [roh(t, 400) for t in treffer][:5])
pc = next((r for r in treffer if r.type == "POSTCODE"), None)
if pc:
    d = c.search_by_postcode(pc.id)
    time.sleep(2)
    print("search_by_postcode (Ausschnitt):", roh(d, 6000))
    vn = d.get("vnbs", [])
    print("Felder eines Netzbetreibers:", sorted(vn[0].keys()) if vn else None)
    for v in vn[:2]:
        for schluessel in ("id", "bdewId", "bdewCode", "code", "operatorId"):
            if v.get(schluessel) is not None:
                try:
                    op = c.get_operator(str(v[schluessel])); time.sleep(2)
                    print("get_operator", v.get("name"), roh(op, 3000))
                    de = c.get_operator_details(str(v[schluessel])); time.sleep(2)
                    print("get_operator_details", v.get("name"), roh(de, 5000))
                except Exception as e:
                    print("Detail Fehler", v.get("name"), type(e).__name__, str(e)[:200])
                break
r2 = c.search("Stadtwerke Meerane")
print("Suche Name:", [roh(t, 500) for t in r2][:4])
