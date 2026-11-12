"""Hochlastzeitfenster als Viertelstunden-Zeitreihe (Datenprodukt für conplot und andere Optimierungsmodelle).

Je Netzbetreiber (MaStR-Nr.), Ebene (ns, msns) und Jahr ein Vektor mit einem Eintrag je Viertelstunde (lokale Zeit, 96 je Tag, Sommerzeit
nicht eingerechnet: der Nutzer legt die Zeitzone beim Einlesen fest). Wert 1 = Viertelstunde liegt in einem Hochlastzeitfenster.
Regeln (Standard laut den Dokumenten, Abweichungen siehe ergebnis/conplot/FORMAT.md):
- nur Werktage (Mo bis Fr), keine gesetzlichen Feiertage des Bundeslands des Netzbetreibers, nicht 24.12. bis 01.01. (Weihnachten bis Neujahr)
- Brückentage: Dokumente sagen "maximal ein Brückentag" (nicht eindeutig) und werden NICHT abgezogen (Parameter brueckentage=True zieht die Tage zwischen Feiertag und Wochenende ab)
- Jahreszeiten: Frühling März bis Mai, Sommer Juni bis August, Herbst September bis November, Winter Dezember bis Februar
- Zeitfenster "von-bis" gelten von der Startzeit (einschließlich) bis zur Endzeit (ausschließlich); "24:00" oder "00:00" als Ende = Tagesende
Aufruf: PYTHONPATH=. python daten/hlzf_zeitreihe.py SNB948311994307 ns 2027 [ausgabe.csv]"""
import csv, datetime as dt, sys
from pathlib import Path

import holidays

ROOT = Path(__file__).resolve().parent.parent
LAND = {"Baden-Württemberg": "BW", "Bayern": "BY", "Berlin": "BE", "Brandenburg": "BB", "Bremen": "HB", "Hamburg": "HH", "Hessen": "HE",
        "Mecklenburg-Vorpommern": "MV", "Niedersachsen": "NI", "Nordrhein-Westfalen": "NW", "Rheinland-Pfalz": "RP", "Saarland": "SL",
        "Sachsen": "SN", "Sachsen-Anhalt": "ST", "Schleswig-Holstein": "SH", "Thüringen": "TH"}
JZ_MONAT = {3: "fruehling", 4: "fruehling", 5: "fruehling", 6: "sommer", 7: "sommer", 8: "sommer", 9: "herbst", 10: "herbst", 11: "herbst",
            12: "winter", 1: "winter", 2: "winter"}


def _minuten(s: str) -> int:
    h, m = s.strip().split(":")
    return int(h) * 60 + int(m)


def _fenster(text: str) -> list:
    out = []
    for t in (text or "").split(","):
        t = t.strip()
        if not t or t == "keins" or "-" not in t:
            continue
        a, b = t.split("-")
        von, bis = _minuten(a), _minuten(b)
        out.append((von, 1440 if bis == 0 else bis))
    return out


def vektor(zeile: dict, ebene: str, jahr: int, brueckentage: bool = False) -> list:
    land = LAND.get(zeile.get("bundesland", ""), "BY")
    feiertage = holidays.Germany(subdiv=land, years=[jahr - 1, jahr, jahr + 1])
    fen = {j: _fenster(zeile.get(f"hlzf_{ebene}_{j}", "")) for j in ("fruehling", "sommer", "herbst", "winter")}
    v = []
    tag = dt.date(jahr, 1, 1)
    while tag.year == jahr:
        werktag = tag.weekday() < 5 and tag not in feiertage and not ((tag.month == 12 and tag.day >= 24) or (tag.month == 1 and tag.day == 1))
        if werktag and brueckentage:
            vor, nach = tag - dt.timedelta(days=1), tag + dt.timedelta(days=1)
            if (tag.weekday() == 4 and nach in feiertage) or (tag.weekday() == 0 and vor in feiertage) or \
               (tag.weekday() == 3 and nach in feiertage) or (tag.weekday() == 1 and vor in feiertage):
                werktag = False
        f = fen[JZ_MONAT[tag.month]] if werktag else []
        for q in range(96):
            m = q * 15
            v.append(1 if any(a <= m < b for a, b in f) else 0)
        tag += dt.timedelta(days=1)
    return v


def main():
    mastr, ebene, jahr = sys.argv[1], sys.argv[2], int(sys.argv[3])
    z = next(r for r in csv.DictReader(open(ROOT / "ergebnis" / "netzentgelte_2026.csv", encoding="utf-8-sig"), delimiter=";") if r["mastr_nr"] == mastr)
    v = vektor(z, ebene, jahr)
    if len(sys.argv) > 4:
        with open(sys.argv[4], "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter=";"); w.writerow(["mastr_nr", "ebene", "viertelstunde_start_lokal", "is_hlzf"])
            t0 = dt.datetime(jahr, 1, 1)
            for i, x in enumerate(v):
                w.writerow([mastr, ebene, (t0 + dt.timedelta(minutes=15 * i)).strftime("%Y-%m-%dT%H:%M"), x])
    print(z["netzbetreiber"], ebene, jahr, "Viertelstunden:", len(v), "in Fenstern:", sum(v), f"= {sum(v)/4:.0f} Stunden", f"Land {z['bundesland']}")


if __name__ == "__main__":
    main()
