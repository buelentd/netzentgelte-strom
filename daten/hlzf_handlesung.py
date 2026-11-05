"""Von Hand am Dokumenttext abgelesene Hochlastzeitfenster (05.11.2026): überschreibt die Zeile in ergebnis/hlzf_ergebnis.csv mit Status 'gelesen'.
Eintrag: nr -> (NS, MSNS, Bemerkung); NS/MSNS = 'F|S|H|W' je Jahreszeit (Frühling|Sommer|Herbst|Winter), Fenster mit Komma, 'k' = keins, '' = nicht ausgewiesen.
Aufruf: PYTHONPATH=. python daten/hlzf_handlesung.py"""
import csv, sys
sys.path.insert(0, ".")
K = "k"
HAND = {
    "791": ("k|k|16:30-19:00|10:00-13:00, 16:30-19:30", "k|k|16:30-19:00|10:00-13:00, 16:30-19:30", "drei Blöcke Mittelspannung, Mittelspannung/Niederspannung, Niederspannung"),
    "794": ("k|k|17:00-19:00|17:00-19:30", "k|k|k|k", "Blöcke NS, MS/NS (leer), MS, HS/MS"),
    "614": ("k|k|10:15-11:45|16:30-17:30", "k|k|k|k", "drei Blöcke Mittelspannung, Umspannung zur Niederspannung (leer), Niederspannung"),
    "712": ("k|k|17:00-18:45|17:00-19:00", "k|k|17:15-18:45|17:00-19:00", "drei Blöcke Mittelspannung, Umspannung MS/NS, Niederspannung"),
    "508": ("k|k|16:15-19:30|14:00-14:45, 17:00-19:30", "k|k|16:15-19:30|14:00-14:45, 17:00-19:30", "drei Blöcke Mittelspannung, Umspannung MS/NS, Niederspannung; MS/NS und NS gleich"),
    "569": ("k|k|k|16:30-19:30", "k|k|k|16:30-19:30", "drei Blöcke Mittelspannung, Mittelspannung/Niederspannung, Niederspannung"),
    "17": ("k|k|16:00-17:30|15:45-17:30", "k|k|16:00-17:30|15:45-17:30", "vier Blöcke HS/MS, MS, MS/NS, NS laut Fußnote; letzte zwei für MS/NS und NS"),
    "150": ("k|k|13:00-13:30, 18:00-18:15|10:30-14:00, 14:15-14:30, 16:30-18:30", "", "Dokument nennt nur Niederspannung"),
    "380": ("k|k|k|12:00-14:15, 17:45-20:00", "k|k|k|17:30-19:00", "Ebenenname steht vor den Zeilen (Mittelspannung, Umspannung M/N, Niederspannung)"),
    "319": ("k|k|11:30-14:30|09:00-14:15, 18:15-19:15", "k|k|k|16:15-19:15", "Spalten Mittel- | Umspannung | Nieder-"),
    "473": ("13:00-13:30|k|k|k", "k|k|k|16:30-18:45", "drei Blöcke Mittelspannung, Umspannung MSP/NSP, Niederspannung"),
    "173": ("k|k|k|12:15-15:30, 17:15-19:45", "k|k|k|12:30-12:45, 13:30-15:30, 17:00-20:00", "Segmenttabelle, Ebenenname steht in der Sommer-Zeile des 4-Zeilen-Blocks"),
}
J = ["fruehling", "sommer", "herbst", "winter"]

def main():
    z = list(csv.reader(open("ergebnis/hlzf_ergebnis.csv", encoding="utf-8-sig"), delimiter=";"))
    H = z[0]; ix = {h: i for i, h in enumerate(H)}; rows = {r[0]: r for r in z[1:]}
    for nr, (ns, ms, bem) in HAND.items():
        r = rows.get(nr) or [""] * len(H); r[0] = nr
        for eb, s in (("ns", ns), ("msns", ms)):
            teile = s.split("|")
            for j, t in zip(J, teile):
                r[ix[f"hlzf_{eb}_{j}"]] = "keins" if t.strip() == K else t.strip()
        r[ix["hlzf_status"]] = "gelesen"; r[ix["hlzf_jahr"]] = "2026"
        r[ix["hlzf_pruefung"]] = "von Hand am Dokumenttext abgelesen: " + bem
        rows[nr] = r
    csv.writer(open("ergebnis/hlzf_ergebnis.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";").writerows([H] + sorted(rows.values(), key=lambda r: int(r[0])))
    print(len(HAND), "von Hand abgelesen")

main()
