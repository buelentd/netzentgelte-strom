"""Von Hand am Dokumenttext abgelesene Hochlastzeitfenster (05.11.2026): überschreibt die Zeile in ergebnis/hlzf_ergebnis.csv mit Status 'gelesen'.
Eintrag: nr -> (NS, MSNS, Bemerkung); NS/MSNS = 'F|S|H|W' je Jahreszeit (Frühling|Sommer|Herbst|Winter), Fenster mit Komma, 'k' = keins, '' = nicht ausgewiesen.
Aufruf: PYTHONPATH=. python daten/hlzf_handlesung.py"""
import csv, sys
sys.path.insert(0, ".")
K = "k"
HAND = {
    "660": ("13:00-16:00|k|k|k", "k|k|16:30-19:30|16:30-19:30", "Spalten Mittelspannung, USP MS/NS, Niederspannung; Zeilen je Jahreszeit"),
    "622": ("k|11:00-14:30|k|k", "k|07:00-08:00, 11:00-14:30|k|k", "Spalten Winter, Frühling, Sommer, Herbst; Zeilen MS, Umspannung MS/NS, NS"),
    "639": ("k|k|k|07:30-11:30", "06:00-07:15|10:45-12:45, 14:00-15:30|k|07:30-09:30, 18:30-19:45", "Spalten Winter, Frühling, Sommer, Herbst je 1. und 2. Zeit; Zeilen MS, MN (Umspannung MS/NS), NS"),
    "652": ("k|k|17:00-18:45|10:45-13:00, 16:15-19:15", "k|k|17:00-18:45|11:00-12:00, 16:15-19:15", "Spalten Mittelspannung, Umspannung MS/NS, Niederspannung; Jahreszeit in der ersten Spalte"),
    "590": ("k|k|09:15-12:15|09:15-12:45, 17:00-19:15", "k|k|10:45-13:15, 17:00-18:30|08:00-13:15, 17:00-19:15", "Spalten Mittelspannung, Umspannung MS/NS, Niederspannung; zwei Zeilen je Jahreszeit"),
    "553": ("12:00-15:15|k|k|11:45-12:15, 13:00-13:15", "k|k|16:45-19:45|17:00-19:15", "Tabellen Mittelspannung, Umspannebene MS/NS, Niederspannung mit HLZF-1 bis -5; Spalten Herbst, Winter, Frühjahr, Sommer"),
    "556": ("k|k|k|12:30-13:15, 17:30-19:45", "k|k|k|12:30-13:00, 17:30-19:45", "Aufzählung je Jahreszeit und Ebene; Herbst: nur Umspannung zur Mittelspannung genannt"),
    "560": ("k|k|16:00-19:00|14:00-19:45", "k|k|16:45-18:45|16:45-19:45", "Spalten Mittelspannung, Umspannung MS/NS, Niederspannung; Zeilen je Jahreszeit"),
    "606": ("11:30-14:30|k|k|16:45-19:45", "k|k|k|16:30-19:30", "Spalten Mittelspannung, Umspannung MS/NS, Niederspannung; Jahreszeit in der ersten Spalte"),
    "532": ("k|k|16:45-19:15|11:45-13:15, 16:30-19:15", "k|k|16:45-19:15|12:00-13:00, 16:30-19:00", "Tabellen Mittelspannung, Umspannung MS/NS, Niederspannung; im Dokument steht bei Herbst 19-15 (Tippfehler für 19:15)"),
    "536": ("11:00-14:00|k|12:15-15:15|k", "k|k|10:15-13:15|09:00-12:00", "Spalten Winter, Frühling, Sommer, Herbst; Zeilen Mittelspannungsebene, Umspannung MS/NS, Niederspannungsebene"),
    "493": ("k|k|17:45-18:15|17:00-19:30", "k|k|17:00-19:00|17:00-19:30", "Tabellen Mittelspannung, Umspannung MS/NS, Niederspannung mit Datumszeilen 2026"),
    "499": ("k|k|07:45-18:00|08:00-09:00, 11:30-12:15", "k|k|k|08:00-09:00, 17:15-18:00", "Spalten Frühling, Sommer, Herbst, Winter und zweite Winter-Spalte (Zeitfenster 2)"),
    "432": ("k|k|k|16:45-19:15", "k|k|k|09:30-10:00, 16:00-19:30", "Tabellen Mittelspannung, Umspannung MS/NS, Niederspannung; Winter Januar/Februar und Dezember"),
    "449": ("k|k|k|11:45-15:00, 16:30-19:15", "k|k|k|12:15-14:00, 16:45-19:15", "Spalten Frühling-Winter je von/bis; Zeilen Umspannung HS/MS, MS, Umspannung MS/NS, NS"),
    "382": ("k|k|k|17:00-19:30", "k|k|k|17:00-19:30", "Spalten Winter, Frühling, Sommer, Herbst; Zeilen Mittelspannungsebene, Umspannung MS/NS, Niederspannungsebene"),
    "388": ("k|k|16:15-19:15|12:30-13:15, 17:00-19:15", "k|k|16:00-19:00|12:00-13:15, 17:15-19:00", "Spalten Frühling-Winter je von/bis; Zeilen Mittelspannung, Umspannung, Niederspannung"),
    "400": ("k|k|17:00-19:00|16:45-19:00", "k|k|16:45-19:15|16:45-19:00", "Spalten Mittelspannung, Umspannung MS/NS, Niederspannung; Zeilen je Jahreszeit"),
    "369": ("k|k|k|11:30-13:45, 16:30-19:15", "k|k|k|11:30-13:45, 16:30-19:15", "Tabelle Mittelspannung, Umspg. MS/NS, Niederspannung; nur Winter"),
    "372": ("12:45-13:45|k|k|k", "12:00-13:30|12:15-13:15, 13:30-13:45, 14:00-14:30|k|k", "Tabelle mit Spaltenposition: Frühling, Sommer"),
    "315": ("k|k|k|16:30-19:30", "k|k|k|16:30-19:30", "Netzebene 6 und 7 mit Spalten Winter, Frühling, Sommer, Herbst; Ende :59 = nächste Viertelstunde"),
    "300": ("k|k|k|11:15-11:45, 18:00-18:15", "k|k|k|11:15-11:45, 17:30-18:15", "Titel Hochlastzeitfenster 2026, Datumszeilen im Dokument 2025 (Vorlage); Tabellen MS, Umspannung MS/NS, NS"),
    "246": ("k|k|k|10:15-12:15, 17:30-19:30", "k|k|k|17:30-19:00", "Tabelle Mittelspannung, Umspg. MS/NS, Niederspannung; Spalten Frühling-Winter"),
    "274": ("k|k|16:45-19:00|11:00-12:15, 16:45-19:45", "k|k|k|17:15-19:30", "Netzebene 4-7 mit Spalten Herbst, Winter, Frühling, Sommer (Position der Zeiten)"),
    "194": ("k|k|17:00-18:30|11:15-14:00, 16:15-19:00", "k|k|17:00-18:30|11:15-14:00, 16:15-19:00", "Spalten Frühling-Winter, Zeilen MS, MS/NS, NS; Ende :59 als nächste Viertelstunde (Ende 18:29:59 = 18:30)"),
    "174": ("k|k|08:45-09:15, 09:45-10:00, 11:15-11:30|k", "", "Tabellen MS und NS; nur MS und NS ausgewiesen"),
    "172": ("k|k|16:45-19:45|17:00-20:00", "k|k|k|17:00-20:00", "Spalten Frühling-Winter je von/bis; Zeilen Mittelspannung, Umspannung, Niederspannung"),
    "128": ("k|k|17:15-19:15|16:45-19:15", "k|k|17:15-19:15|16:45-19:15", "Tabelle Mittelspannung, Umspg. MS/NS, Niederspannung mit Spalten Frühling-Winter"),
    "163": ("k|k|15:30-18:30|15:30-18:30", "k|k|16:00-19:00|09:30-12:30, 16:00-19:00", "Tabelle Mittelspannung, Umspg. MS/NS, Niederspannung; Fenster je Zeile über/unter dem Ebenennamen"),
    "741": ("k|k|k|18:45-20:00", "k|k|17:30-18:15|17:00-19:15", "Blöcke Mittelspannung, Umspannung MS/NS, Niederspannung; Ebenenname mittig"),
    "785": ("11:30-13:15|k|17:15-19:00, 21:15-22:00|09:30-15:45, 16:45-19:30, 21:00-22:30", "k|10:15-13:00|11:15-12:45, 13:30-14:15, 14:45-15:45|k", "Blöcke mit Zeilen Winter, Frühling, Sommer, Herbst; Ebene HS, HS/MS, MS, MS/NS, NS; Ebenenname mittig"),
    "646": ("k|k|k|17:30-19:15", "k|k|18:00-18:15|08:30-08:45, 11:15-13:15, 17:15-19:00", "Blöcke Mittelspannung, Umspannung MS/NS, Niederspannung; Ebenenname mittig"),
    "492": ("09:30-09:45, 12:15-12:30|k|k|k", "09:15-09:45, 12:00-12:30|k|k|11:30-11:45, 17:00-19:15", "Blöcke Mittelspannung, Umspannungsebene MS/NS, Niederspannungsebene; leere Zeilen = keine Fenster"),
    "275": ("k|k|k|18:15-20:00", "k|k|09:30-10:15, 10:45-11:00|k", "Blöcke Netzebene 5, 6 (Umspannung), 7 (Niederspannung)"),
    "365": ("k|k|17:00-18:00|11:30-12:30, 17:15-20:30", "k|k|k|16:45-20:30", "Blöcke Mittelspannung, Umspannung M/N, Niederspannung"),
    "804": ("11:00-14:00|11:00-14:00|17:00-20:00|11:00-14:00, 17:00-19:15", "k|k|17:00-20:00|17:00-20:00", "Netzebene 6 = Umspannung MS/NS, Netzebene 7 = Niederspannung (gleiches Layout wie 217)"),
    "744": ("k|k|10:15-12:00, 16:45-17:00|11:00-11:15, 16:15-18:15", "k|k|16:00-17:45|15:30-18:30", "Blöcke je Netzebene mit Jahreszeit-Zeilen; Dokument liegt auf netzplusservice.de (eigene Website des Netzbetreibers)"),
    "795": ("17:00-20:00|k|k|16:45-19:45", "17:00-20:00|k|k|16:45-19:45", "Spalten Winter, Frühling, Sommer, Herbst; Zeilen MS, Umspannung MS/NS, NS"),
    "799": ("k|k|k|17:45-18:45", "k|k|k|10:15-12:45, 18:00-18:30", "Blöcke MS, Umspannebene MS/NS, NS"),
    "662": ("k|k|17:15-18:30|11:30-12:15, 16:45-19:30", "k|k|17:15-18:30|11:30-12:15, 16:45-19:30", "Blöcke MS-Ebene, US-Ebene (von MS in NS), NS-Ebene"),
    "709": ("k|k|k|08:45-09:45, 18:30-20:00", "k|k|16:30-18:30|16:30-19:30", "Spalten Winter, Frühling, Sommer, Herbst; Zeilen MS, MS/NS, NS"),
    "737": ("k|k|k|10:00-13:00", "k|k|10:30-12:30|10:00-13:15, 17:00-18:00", "drei Tabellen Mittelspannung, Umspannung zur Niederspannung, Niederspannung"),
    "635": ("10:00-10:14, 17:15-19:59|k|16:30-19:29|16:30-19:59", "k|k|16:45-19:44|16:45-19:59", "Blöcke HS, HS/MS, MS, MS/NS, NS mit Kopfzeile je Block; Zeiten wie im Dokument (Ende :59)"),
    "613": ("k|k|10:45-13:00, 16:45-19:00|09:45-12:45, 13:00-13:15, 16:30-19:15", "k|k|11:30-12:30, 16:45-19:00|11:45-12:00, 16:45-19:15", "Blöcke Mittelspannebene, Umspannebene 20/0,4 kV, Niederspannungsebene"),
    "581": ("k|k|17:30-18:30|17:15-19:45", "k|k|17:30-17:45, 18:00-18:30|17:15-19:45", "Spalten Winter, Frühling, Sommer, Herbst; Zeilen MS, US-Ebene (MS-NS), NS"),
    "526": ("k|k|09:30-14:45, 16:30-18:45|k", "11:00-12:00|k|k|k", "Blöcke MSP, USP, NSP je Jahreszeit"),
    "535": ("k|k|17:30-18:45|16:45-19:15", "k|k|17:30-18:45|16:45-19:15", "Zeile 'NS inkl. MS/NS'"),
    "538": ("k|k|17:00-19:00|17:00-20:15", "||17:00-19:00|17:00-20:15", "Aufzählung je Jahreszeit; Umspannung MS/NS nur Herbst und Winter genannt"),
    "522": ("k|k|16:30-19:30|17:00-20:00", "k|k|16:45-19:15|17:00-19:30", "Zeilen Mittelspannungsebene, Umspannungsebene MS/NS, Niederspannungsebene; Spalten Herbst, Winter, Frühling, Sommer"),
    "512": ("k|k|k|10:00-12:00", "k|k|k|k", "Spalten Winter, Frühling, Sommer, Herbst; Umspannung MS/NS: keine"),
    "498": ("12:00-12:45|k|k|k", "k|k|k|17:30-19:15", "Blöcke Mittelspannung, Umspannung MS/NS, Niederspannung; Jahreszeit mittig in den Zeilen"),
    "443": ("k|k|16:45-19:00|12:00-13:00, 16:30-19:30", "k|k|16:45-19:00|12:00-12:45, 16:30-19:30", "Liste je Spannungsebene, Jahreszeit Herbst/Winter"),
    "441": ("k|k|k|17:00-18:30", "k|k|k|17:15-18:30", "Spalten Umspannung HS/MS, MS, Umspannung MS/NS, NS"),
    "455": ("k|k|k|17:00-19:15", "k|k|k|k", "Zeile MS/NS leer, NS nur Winter"),
    "481": ("k|k|k|17:15-19:15", "10:30-10:45, 18:00-18:15|10:30-11:00, 12:00-12:30, 13:30-13:45|k|k", "Tabellen je Ebene mit HLZF 1-3 je Jahreszeitspalte"),
    "386": ("k|k|09:30-10:00, 15:00-17:30|09:15-10:15, 15:15-17:15", "k|k|09:30-10:00, 15:00-17:30|09:15-10:30, 15:15-17:15", "Blöcke Mittelspannung, Umspannung MS/NS, Niederspannung; Jahreszeit mittig in den Zeilen"),
    "395": ("k|k|k|17:00-19:30, 20:00-22:30", "k|k|k|17:00-19:30, 21:00-22:15", "nummerierte Blöcke 1 MS, 2 Umspannung MS/NS, 3 NS"),
    "335": ("k|k|10:15-12:45, 17:30-18:30|10:00-13:00, 17:00-18:45", "k|k|10:30-13:15, 17:15-18:15|10:00-13:00, 16:00-18:45", "Blöcke Mittelspannung, Umspannung Mittel-/Niederspannung, Niederspannung"),
    "356": ("k|k|k|10:45-12:15, 16:30-19:15", "k|k|k|11:15-12:15", "Tabellen Niederspannung, Mittelspannung/Niederspannung, Mittelspannung"),
    "366": ("k|k|k|09:00-12:00, 17:00-18:30", "k|k|k|09:30-12:45, 17:15-19:30", "fünf Tabellen HS, HS/MS, MS, MS/NS, NS"),
    "311": ("k|k|18:00-18:15|10:15-10:30, 10:45-12:15, 16:45-19:15", "k|k|18:00-18:15|11:15-12:00, 16:45-19:15", "Tabellen MS, Umspannung zur NS, NS; Ebenenname mittig in den Zeilen"),
    "322": ("13:45-14:45|k|10:45-13:45|k", "k|k|17:15-18:15|16:45-18:45", "Tabelle HLZF 1 je Jahreszeit; Zeilen MS, Umspg. MS/NS, NS"),
    "330": ("k|k|17:45-19:15|16:30-20:00", "k|k|17:45-19:15|16:30-20:00", "Blöcke HS, HS/MS, MS, MS/NS, NS"),
    "331": ("k|k|09:30-11:00|09:00-12:00", "k|k|08:15-13:15|08:30-12:45", "Spalten Niederspannung, Umspannung MS/NS, Mittelspannung"),
    "291": ("11:15-15:00|12:00-15:30|k|k", "10:30-15:45|11:30-15:30|k|k", "Tabellen MS, MS/NS, NS je Jahreszeit mit von/bis; leere Zeilen = keine Fenster"),
    "226": ("09:00-10:00|k|k|k", "k|k|k|17:00-19:30", "drei Tabellen MS, NS, Umspannung MS/NS; Spalte laut Position unter Jahreszeit-Kopf"),
    "192": ("k|k|k|17:15-20:15", "k|k|k|17:15-20:15", "Spalten U HS/MS, MS, U MS/NS, NS; Winter 2026 (Jan-Feb und Dez)"),
    "211": ("k|k|17:15-18:15|16:30-19:45", "k|k|17:15-18:15|16:45-19:30", "Tabellen Mittelspannung, Umspannung MS/NS, Niederspannung"),
    "217": ("11:00-14:00|11:00-14:00|17:00-20:00|11:00-14:00, 17:00-19:15", "k|k|17:00-20:00|17:00-20:00", "Netzebene 6 = Umspannung MS/NS, Netzebene 7 = Niederspannung"),
    "81": ("k|k|16:45-19:00|15:15-20:00", "k|k|16:45-19:00|16:00-16:15, 16:30-20:00", "Blöcke Mittelspannung, Umspannung MS/NS, Niederspannung; Spalten von/bis je Jahreszeit"),
    "109": ("k|k|k|16:45-19:45", "k|k|k|16:45-19:45", "Blöcke Mittelspannung, Umspannung Mittel- auf Niederspannung, Niederspannung"),
    "157": ("k|k|k|17:30-19:30", "k|k|k|17:45-19:30", "Blöcke MS, MS/NS, NS"),
    "166": ("k|k|k|16:45-20:00, 21:30-22:15", "k|k|k|16:45-20:00, 21:30-22:15", "Zeilenpaare je Ebene: Mittelspannung, Umspannung MS/NS, Niederspannung"),
    "13": ("k|k|k|10:45-12:30", "k|k|k|11:00-12:30", "Blöcke Hochspannung, HS in MS, Mittelspannung, MS in NS, Niederspannung"),
    "23": ("k|k|k|12:00-14:45, 17:30-19:00", "k|k|k|16:45-19:30", "Spalten HS/MS, Mittelspannung, Umspannung MS/NS, Niederspannung; Monate Dez-Feb = Winter"),
    "39": ("k|k|17:30-19:15|16:30-19:45", "k|k|17:15-19:15|16:30-19:30", "vier Blöcke Umspannung zur MS, MS, Umspannung zur NS, NS"),
    "24": ("k|k|17:00-20:00|17:00-20:00", "k|k|17:00-20:00|17:00-20:00", "je Ebene zwei Zeilen; Frühling/Sommer ohne Fenster (Strich)"),
    "56": ("k|k|18:00-21:00|12:30-13:15, 16:45-19:30", "k|k|k|09:45-12:30", "drei Blöcke MSP, MSP/NSP, NSP"),
    "59": ("k|k|16:15-19:15|17:00-19:15", "k|k|16:15-19:15|17:00-19:15", "vier Zeilen-Blöcke, MS/NS und NS gleich"),
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
LEER = {"377": "Dokument ist textgleich mit dem von Energieversorgung Rüsselsheim (166, liegt auf deren Website); kein Netzbetreibername im Dokument",
        "277": "Dokument (netzplusservice.de) gehört zu Städtische Werke Netz+Service (744), nicht zu inetz"}
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
    for nr, grund in LEER.items():
        r = rows.get(nr) or [""] * len(H); r[0] = nr
        for c in H:
            if c.startswith("hlzf_ns_") or c.startswith("hlzf_msns_") or c in ("hlzf_schwelle_prozent", "hlzf_mindestleistung_kw", "hlzf_jahr"):
                r[ix[c]] = ""
        r[ix["hlzf_status"]] = "fehlt: Dokument gehört einem anderen Netzbetreiber"; r[ix["hlzf_pruefung"]] = grund
        rows[nr] = r
    csv.writer(open("ergebnis/hlzf_ergebnis.csv", "w", encoding="utf-8-sig", newline=""), delimiter=";").writerows([H] + sorted(rows.values(), key=lambda r: int(r[0])))
    print(len(HAND), "von Hand abgelesen")

main()
