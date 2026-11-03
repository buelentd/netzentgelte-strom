"""Eine Abfrage: Feld documents zum Netzbetreiber 960 (Stadtwerke Meerane) von vnbdigital.de, vollständig im Protokoll. Nichts wird gespeichert."""
import json
from vnbdigital_client import VNBDigitalClient

d = VNBDigitalClient().get_operator_details("960")
raw = d.raw if hasattr(d, "raw") else d["raw"]
print("DOKUMENTE", json.dumps(raw.get("documents"), ensure_ascii=False)[:6000])
