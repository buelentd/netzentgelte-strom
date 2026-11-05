"""Eine gemeinsame Arbeitsliste für alle: je Netzbetreiber, was fehlt, warum, wer es tut (Kollege / Nutzer im Browser / Claude) und welche Datei wohin.
Quellen: ergebnis/netzentgelte_2026.csv, ergebnis/ebenen_erwartung.csv. Ausgabe: ergebnis/arbeitsliste.csv. Aufruf: PYTHONPATH=. python daten/arbeitsliste.py"""
import csv, re
from urllib.parse import urlparse

tab = list(csv.DictReader(open("ergebnis/netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";"))
erw = {r["nr"]: r for r in csv.DictReader(open("ergebnis/ebenen_erwartung.csv", encoding="utf-8-sig"), delimiter=";")}
K = ("lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh")

def hat(x, p):
    return all(x[f"{p}_{k}"] for k in K)

def domain(w):
    if not w:
        return ""
    h = urlparse(w if w.startswith("http") else "http://" + w).netloc or w
    return re.sub(r"^www\.", "", h).lower()

try:
    OHNE_BELEG = set(open("ergebnis/preise_ohne_beleg.txt").read().split())
except FileNotFoundError:
    OHNE_BELEG = set()
zeilen = []
for x in tab:
    nr = x["nr"]; e = erw.get(nr, {})
    fehlt = []
    if not x["slp_ap_ct_kwh"] or not x["slp_grundpreis_eur_jahr"]:
        fehlt.append("SLP")
    for k, n in (("ns", "NS"), ("msns", "MS/NS"), ("ms", "MS")):
        if not hat(x, k):
            code = e.get(k, "")
            if code == "nicht_ausgewiesen" and k != "ns":
                continue                                 # Stadtwerke haben MS und MS/NS nicht immer: nicht ausgewiesen ist kein Fehler
            fehlt.append(n)
    hl = x["hlzf_status"]
    hlzf_offen = hl not in ("gelesen_nutzer", "gelesen_unser")
    if hlzf_offen:
        fehlt.append("Hochlastzeitfenster")
    if not fehlt:
        continue
    st = x["status"]
    # Preise: wer?
    preis_wer, preis_aktion = "", ""
    pf = [f for f in fehlt if f != "Hochlastzeitfenster"]
    if pf:
        if st in ("blockiert", "robots"):
            preis_wer, preis_aktion = "Nutzer (Browser)", "Seite im Browser öffnen, Preisblatt Strom 2026 speichern"
        elif st in ("kein_preisblatt", "keine_website") or e.get("ns") == "kein_dokument" or e.get("slp") == "kein_dokument":
            preis_wer, preis_aktion = "Kollege", "Preisblatt Strom 2026 suchen und laden (Suche site:Domain Netzentgelte Strom 2026 Preisblatt)"
        elif e.get("ns") == "nicht_ausgewiesen":
            preis_wer, preis_aktion = "Kollege", "Dokument ist vermutlich das falsche (keine Niederspannung ausgewiesen): richtiges Preisblatt suchen"
        else:
            preis_wer, preis_aktion = "Claude", "Dokument liegt vor, Leser muss es lesen"
    if nr in OHNE_BELEG and not preis_wer.startswith("Nutzer"):
        if "Niederspannung/Preise ohne Beleg" not in fehlt:
            fehlt.append("Preise ohne Beleg im Dokument")
        preis_wer, preis_aktion = "Kollege", "Das vorliegende Dokument bestätigt die Preise nicht (falsches Dokument?): richtiges Preisblatt Strom 2026 liefern"
    # Hochlastzeitfenster: wer?
    hlzf_wer, hlzf_aktion = "", ""
    if hlzf_offen:
        if hl == "kein_dokument_oder_adresse":
            hlzf_wer, hlzf_aktion = "Kollege", "Hochlastzeitfenster 2026 suchen und laden (Suche site:Domain Hochlastzeitfenster 2026)"
        elif hl == "jahr_nicht_2026":
            hlzf_wer, hlzf_aktion = "Kollege", "Dokument ist nicht für 2026: Datei für 2026 suchen"
        elif hl == "nur_mittelspannung":
            hlzf_wer, hlzf_aktion = "Kollege", "Dokument gilt nur für Mittelspannung: Dokument für Umspannung MS/NS und Niederspannung suchen"
        elif hl == "gelesen_ungeprueft":
            hlzf_wer, hlzf_aktion = "Claude", "Werte gelesen, Zuordnung zu den Ebenen am Dokument prüfen"
        elif hl in ("raster_grafik",):
            hlzf_wer, hlzf_aktion = "Kollege", "Raster/Grafik: Zeiten als Text abschreiben (Ebene, Jahreszeit, von-bis)"
        else:
            hlzf_wer, hlzf_aktion = "Claude", "Dokument liegt vor, Leser muss es lesen (Scan: Kollege liefert Zeiten als Text)"
    d = domain(x["website"])
    n4 = f"{int(nr):04d}"
    prio = (len(pf) * 2 + (1 if hlzf_offen else 0))
    zeilen.append([nr, x["netzbetreiber"], x["mastr_nr"], d, x["status"], ", ".join(fehlt), preis_wer, preis_aktion, hlzf_wer, hlzf_aktion,
                   hl if hlzf_offen else "", x["quelle_url"][:200],
                   f"site:{d} Netzentgelte Strom 2026 Preisblatt" if d else "", f"site:{d} Hochlastzeitfenster 2026" if d else "",
                   f"{x['mastr_nr']}_{n4}.pdf", f"{x['mastr_nr']}_{n4}_hlzf.pdf", prio])
zeilen.sort(key=lambda z: (-z[-1], int(z[0])))
H = ["nr", "netzbetreiber", "mastr_nr", "domain", "status_preise", "es_fehlt", "preise_wer", "preise_aktion", "hlzf_wer", "hlzf_aktion", "hlzf_status",
     "bekannte_preisblatt_url", "suche_preisblatt", "suche_hochlastzeitfenster", "dateiname_preisblatt", "dateiname_hochlastzeitfenster", "prioritaet"]
with open("ergebnis/arbeitsliste.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";"); w.writerow(H); w.writerows(zeilen)
import collections
print(len(zeilen), "Netzbetreiber mit Lücken")
print("Preise:", dict(collections.Counter(z[6] for z in zeilen if z[6])))
print("Hochlastzeitfenster:", dict(collections.Counter(z[8] for z in zeilen if z[8])))

# Zwei fertige Teillisten für den Kollegen: MaStR-Nummer zuerst
def teil(wer_spalte, datei, felder):
    rows = [z for z in zeilen if z[wer_spalte] == "Kollege"]
    idx = {h: i for i, h in enumerate(H)}
    with open(datei, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(["mastr_nr", "nr", "netzbetreiber", "domain"] + felder)
        for z in rows:
            w.writerow([z[idx["mastr_nr"]], z[idx["nr"]], z[idx["netzbetreiber"]], z[idx["domain"]]] + [z[idx[c]] for c in felder])
    return len(rows)
n1 = teil(6, "ergebnis/kollege_preise.csv", ["status_preise", "es_fehlt", "preise_aktion", "bekannte_preisblatt_url", "suche_preisblatt", "dateiname_preisblatt"])
n2 = teil(8, "ergebnis/kollege_hochlastzeitfenster.csv", ["hlzf_status", "hlzf_aktion", "suche_hochlastzeitfenster", "dateiname_hochlastzeitfenster"])
print("Kollege Preise:", n1, "| Kollege Hochlastzeitfenster:", n2)
