"""Bettet ergebnis/tarifformeln.csv als D.formeln in rechner_online/index.html ein (Liste je Netzbetreiber-Nr.).
Aufruf: python daten/tarifformeln_einbetten.py   (danach rechner_online/index.html committen)"""
import csv
import json
import re
from pathlib import Path

W = Path(__file__).resolve().parent.parent
rows = list(csv.DictReader(open(W / "ergebnis/tarifformeln.csv", encoding="utf-8-sig"), delimiter=";"))
fl = lambda v: float(v.replace(",", ".")) if v else None
hp = W / "rechner_online/index.html"
s = hp.read_text(encoding="utf-8")
m = re.search(r'(<script type="application/json" id="daten">)(.*?)(</script>)', s, re.S)
d = json.loads(m.group(2))
d["formeln"] = {}
for x in rows:
    d["formeln"].setdefault(x["nr"], []).append({
        "lieferant": x["lieferant_grundversorger"], "art": x["art"], "gruppe": x["kundengruppe"], "basis": x["energiepreis_basis"],
        "auf": fl(x["aufschlag_ct_kwh"]), "prozent": fl(x["aufschlag_prozent"]), "neben": fl(x["nebenkosten_ct_kwh"]),
        "dienst": fl(x["dienstleistungsentgelt_ct_kwh"]), "grund": fl(x["grundpreis_eur_jahr"]), "netto": x["netto"],
        "ab": x["gueltig_ab"], "q": x["quelle_url"], "hinweis": x.get("hinweis_kurz", "")})
hp.write_text(s[:m.start(2)] + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + s[m.end(2):], encoding="utf-8")
print(len(rows), "Formeln in", len(d["formeln"]), "Netzgebieten eingebettet")
