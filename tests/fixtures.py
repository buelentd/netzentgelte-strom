"""Erzeugt synthetische Preisblätter (PDF/xlsx) für die Tests.

Die Layouts bilden typische Varianten echter Preisblätter nach (Standard, vertauschte
Spalten, Tagesleistungspreis, getrennte Tabellen, Zeilen je Benutzungsdauer, Umbrüche).
Die Zahlen sind frei erfunden und nur Testdaten.
"""
from pathlib import Path

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


def pdf(pfad: Path, zeilen: list[str], quer=True):
    """Schreibt Zeilen in Festbreitenschrift; Spalten bleiben für pdftotext -layout erhalten."""
    groesse = landscape(A4) if quer else A4
    c = canvas.Canvas(str(pfad), pagesize=groesse)
    y = groesse[1] - 40
    for z in zeilen:
        if z == "<SEITE>":
            c.showPage()
            y = groesse[1] - 40
            continue
        c.setFont("Courier", 8)
        c.drawString(30, y, z)
        y -= 11
    c.save()


KOPF_STANDARD = [
    "Musternetz GmbH",
    "Preisblatt Netzentgelte Strom gültig ab 01.01.2026 (endgültig)   Stand: 12.12.2025",
    "",
    "Entnahme mit Leistungsmessung - Jahresleistungspreissystem",
    "                              Jahresbenutzungsdauer < 2.500 h/a      Jahresbenutzungsdauer ≥ 2.500 h/a",
    "Netz- bzw. Umspannebene       Leistungspreis   Arbeitspreis         Leistungspreis   Arbeitspreis",
    "                              €/kW/a           ct/kWh               €/kW/a           ct/kWh",
]


def standard(pfad):
    pdf(pfad, KOPF_STANDARD + [
        "Hochspannung                  10,11            4,22                 99,10            0,52",
        "Umspannung HS/MS              11,20            4,30                 105,00           0,61",
        "Mittelspannung                12,50            5,10                 110,40           1,20",
        "Umspannung MS/NS              14,80            5,90                 130,20           1,05",
        "Niederspannung                18,64            7,49                 171,87           1,36",
        "",
        "Monatsleistungspreissystem",
        "Niederspannung                         14,32            1,36",
        "",
        "Entnahme ohne Leistungsmessung",
        "Niederspannung   Grundpreis 60,00 €/a   Arbeitspreis 8,12 ct/kWh",
    ])


def vertauscht(pfad):
    """Arbeitspreis vor Leistungspreis, Grenzen in umgekehrter Reihenfolge."""
    pdf(pfad, [
        "WEMUSTER Netz GmbH  Preisblatt 2026, gültig ab 01.01.2026, endgültig",
        "Jahresleistungspreissystem",
        "                              Benutzungsdauer ≥ 2.500 h/a            Benutzungsdauer < 2.500 h/a",
        "Ebene                         Arbeitspreis     Leistungspreis       Arbeitspreis     Leistungspreis",
        "                              ct/kWh           €/kW/a               ct/kWh           €/kW/a",
        "Umspannung MS/NS              1,40             150,10               6,10             20,00",
        "Niederspannung                1,55             187,82               7,77             32,37",
    ])


def tag(pfad):
    pdf(pfad, [
        "Tagnetz GmbH   Preisblatt Netznutzung Strom 2026 vorläufig",
        "Gültig ab 01.01.2026",
        "Entnahme mit Leistungsmessung (Tagesleistungspreis)",
        "                         Jahresbenutzungsdauer < 2.500 h      Jahresbenutzungsdauer ≥ 2.500 h",
        "                         Leistungspreis  Arbeitspreis         Leistungspreis  Arbeitspreis",
        "                         €/kW/Tag        ct/kWh               €/kW/Tag        ct/kWh",
        "Niederspannung           0,056164        8,12                 0,281370        4,83",
    ])


def getrennt(pfad):
    """Zwei Tabellen, je eine für < und ≥ 2.500 h, mit umgebrochenem MS/NS-Label."""
    pdf(pfad, [
        "Getrennt Netz AG - Netzentgelte 2026 - endgültig - gültig ab 01.01.2026",
        "Entgelte für Entnahme mit Leistungsmessung",
        "Jahresbenutzungsdauer bis 2.500 h/a",
        "Ebene                    Leistungspreis €/kW/a     Arbeitspreis ct/kWh",
        "Umspannung",
        "MS/NS                    15,10                     6,00",
        "Niederspannung           26,76                     8,28",
        "",
        "Jahresbenutzungsdauer über 2.500 h/a",
        "Ebene                    Leistungspreis €/kW/a     Arbeitspreis ct/kWh",
        "Umspannung",
        "MS/NS                    120,00                    2,10",
        "Niederspannung           148,97                    3,39",
    ])


def zeilen_je_grenze(pfad):
    pdf(pfad, [
        "Zeilennetz GmbH Netzentgelte Strom ab 01.01.2026 endgültig",
        "Jahresleistungspreissystem",
        "                                   Leistungspreis   Arbeitspreis",
        "                                   €/kW/a           ct/kWh",
        "Niederspannung",
        "   Jahresbenutzungsdauer < 2.500 h  22,04           6,68",
        "   Jahresbenutzungsdauer ≥ 2.500 h  138,62          2,01",
    ])


def jahr_2027(pfad):
    pdf(pfad, [z.replace("2026", "2027") for z in KOPF_STANDARD] + [
        "Niederspannung                18,64            7,49                 171,87           1,36",
    ])


def ohne_name(pfad):
    pdf(pfad, KOPF_STANDARD[1:] + [
        "Niederspannung                18,64            7,49                 171,87           1,36",
    ])


def ohne_kopf_einheiten(pfad):
    pdf(pfad, [
        "Kopflos Netz GmbH Netzentgelte 2026 endgültig",
        "Jahresbenutzungsdauer",
        "Niederspannung                18,64            7,49                 171,87           1,36",
    ])


def xlsx(pfad):
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Excelnetz GmbH - Preisblatt 1 Strom ab 01.01.2026 - final"])
    ws.append([])
    ws.append(["Jahresleistungspreissystem"])
    ws.append(["Netzebene", "Jahresbenutzungsdauer < 2.500 h/a", None, "Jahresbenutzungsdauer ≥ 2.500 h/a"])
    ws.append([None, "Leistungspreis", "Arbeitspreis", "Leistungspreis", "Arbeitspreis"])
    ws.append([None, "€/kW/Tag", "ct/kWh", "€/kW/Tag", "ct/kWh"])
    ws.append(["Umspannung MS/NS", 0.08, 5.2, 0.3, 2.9])
    ws.append(["Niederspannung", 0.114685, 6.36, 0.321178, 3.35])
    ws.append([])
    ws.append(["Entnahme ohne Leistungsmessung (Standardlastprofil)"])
    ws.append(["Netzebene", "Grundpreis", "Arbeitspreis"])
    ws.append([None, "€/Tag", "ct/kWh"])
    ws.append(["Niederspannung", 0.164384, 7.71])
    ws.append(["Wärmepumpe", 0.05, 4.1])
    wb.save(pfad)


ALLE = {
    "standard.pdf": standard, "vertauscht.pdf": vertauscht, "tag.pdf": tag,
    "getrennt.pdf": getrennt, "zeilen.pdf": zeilen_je_grenze, "jahr2027.pdf": jahr_2027,
    "ohne_name.pdf": ohne_name, "ohne_kopf.pdf": ohne_kopf_einheiten, "excel.xlsx": xlsx,
}


def erzeugen(ordner: Path):
    ordner.mkdir(parents=True, exist_ok=True)
    for name, f in ALLE.items():
        f(ordner / name)
    return ordner
