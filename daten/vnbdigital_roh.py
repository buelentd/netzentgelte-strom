"""Zwei Abfragen: Details zum Netzbetreiber mit Kennung 960 (Stadtwerke Meerane) von vnbdigital.de, roh im Protokoll. Nichts wird gespeichert."""
import dataclasses
import json
import time

from vnbdigital_client import VNBDigitalClient


def roh(x, grenze=3500):
    if dataclasses.is_dataclass(x):
        x = dataclasses.asdict(x)
    elif hasattr(x, "__dict__") and not isinstance(x, (dict, list)):
        x = vars(x)
    return json.dumps(x, ensure_ascii=False, default=str)[:grenze]


c = VNBDigitalClient()
for name, f in (("get_operator", c.get_operator), ("get_operator_details", c.get_operator_details)):
    try:
        print(name, roh(f("960")))
    except Exception as e:
        print(name, "Fehler", type(e).__name__, str(e)[:200])
    time.sleep(2)
