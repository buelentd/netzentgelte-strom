"""Rechenwert-Fallback für Hochlastzeitfenster, getrennt von den Primärdaten.

Primärdaten (lauf/hlzf_zusammen.csv, Status, Export) bleiben unverändert: der Befund
"nicht gefunden" bleibt stehen. Diese Datei erzeugt ergebnis/hlzf_fallback.csv mit
eindeutiger Herkunft (UPSTREAM_OPERATOR_FALLBACK), nur für ausdrücklich freigegebene Paare.
Nutzerfestlegung 13.11.2026 (Butzbach <- ovag Netz)."""
import csv
FALLBACKS = [  # (mastr_nr Standort, mastr_nr Fallback-Netzbetreiber, Grund)
    ("SNB972511582064", "SNB969534177940", "Betriebsführung und vorgelagertes Netz durch ovag Netz GmbH"),
]
Z = list(csv.DictReader(open("lauf/hlzf_zusammen.csv", encoding="utf-8-sig"), delimiter=";"))
N = {r["mastr_nr"]: r for r in csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";")}
Zm = {r["mastr_nr"]: r for r in Z}
F = ["mastr_nr", "netzbetreiber", "primary_hlzf_found", "audit_status", "hlzf_source_type", "hlzf_fallback_dso_mastr_nr",
     "hlzf_fallback_dso_name", "hlzf_fallback_reason", "confidence"] + [c for c in Z[0] if c.startswith("hlzf_") and c != "hlzf_status"]
out = []
for ziel, quelle, grund in FALLBACKS:
    q = Zm[quelle]
    if not q["hlzf_status"].startswith("gelesen"):
        continue
    z = Zm[ziel]
    r = {"mastr_nr": ziel, "netzbetreiber": N[ziel]["netzbetreiber"], "primary_hlzf_found": "False",
         "audit_status": "hlzf_nicht_gefunden_rlm_vorhanden", "hlzf_source_type": "UPSTREAM_OPERATOR_FALLBACK",
         "hlzf_fallback_dso_mastr_nr": quelle, "hlzf_fallback_dso_name": N[quelle]["netzbetreiber"],
         "hlzf_fallback_reason": grund, "confidence": "MEDIUM / VERIFY_WITH_DSO"}
    for c in F[9:]:
        r[c] = q[c]
    out.append(r)
w = csv.DictWriter(open("ergebnis/hlzf_fallback.csv", "w", encoding="utf-8-sig", newline=""), fieldnames=F, delimiter=";")
w.writeheader(); w.writerows(out)
print(len(out), "Fallback-Zeilen")
