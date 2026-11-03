"""Eine Abfrage: Details zum Netzbetreiber 960 (Stadtwerke Meerane) von vnbdigital.de. Im Protokoll: alle Felder und alle Dienste vollständig. Nichts wird gespeichert."""
import json
from vnbdigital_client import VNBDigitalClient

d = VNBDigitalClient().get_operator_details("960")
raw = d.raw if hasattr(d, "raw") else d["raw"]
print("Felder:", sorted(raw.keys()))
for s in raw.get("services", []):
    t = s.get("type", {})
    rest = {k: v for k, v in s.items() if k != "type"}
    print("DIENST", t.get("type"), "|", t.get("name"), "|", json.dumps(rest, ensure_ascii=False)[:400], "| Typfelder:", sorted(t.keys()))
