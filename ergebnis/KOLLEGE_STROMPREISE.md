# Aufgabe Strompreise: Grundversorgung Gewerbe bei den 100 größten Netzgebieten (Stand 06.11.2026)

Ziel: Für unseren Rechner den Strompreis (Energie, ohne Netzentgelt) je Region statt einer Modellannahme. Liste: `ergebnis/strompreise_liste_100.csv` (100 Netzgebiete nach Zahl der Anschlüsse, mit Suchlinks `site:` ohne www). Vorlage zum Ausfüllen: `ergebnis/strompreise_vorlage.csv`.

## Was je Netzgebiet zu suchen ist
Die Preise des **Grundversorgers** in diesem Netzgebiet (meist das Stadtwerk selbst; sonst der in der Region genannte Grundversorger). Das ist die Pflichtveröffentlichung nach § 36 EnWG. Gesucht, in dieser Reihenfolge:
1. Gewerbe-Grundversorgung (Arbeitspreis ct/kWh und Grundpreis €/Jahr), gültig 2026.
2. Falls vorhanden: Gewerbe-Festpreistarif mit Preisblatt (nur wenn ohne Anfrage veröffentlicht).
3. Falls vorhanden: dynamischer Stromtarif (Börsenpreis plus Aufschlag): Aufschlag in ct/kWh und Grundpreis.

## Regeln
- **Netto** erfassen. Steht nur Brutto da, durch 1,19 teilen und in `bemerkung` „brutto umgerechnet“ vermerken. Nicht schätzen, nichts aus Vergleichsportalen (Verivox, Check24): nur Seite oder PDF des Lieferanten.
- **Enthält der Preis das Netzentgelt?** Grundversorgungspreise sind meist Gesamtpreise mit Netzentgelt, Steuern und Umlagen. Bitte in `enthaelt_netzentgelt` ja oder nein eintragen und in `bemerkung` festhalten, welche Bestandteile im Preis stehen (Netz, Konzessionsabgabe, Stromsteuer, Umlagen). Ohne diese Angabe ist der Preis für uns nicht verwendbar.
- Das Preisblatt als PDF speichern: `<nr>_strom_<Originalname>.pdf` in `eingang/lieferung_strompreise`. Ist der Preis nur als HTML-Tabelle da, Seite als PDF drucken oder Link und Datum in `quelle_url` und `bemerkung`.
- Nur 2026. Nicht 2027, nicht „ab 1.1.2027“ mischen.
- Gibt es keinen veröffentlichten Gewerbepreis: Zeile mit `bemerkung` = „kein Gewerbepreis veröffentlicht“, Seite und Datum nennen.
- robots.txt beachten, höchstens 1 Aufruf pro Sekunde, 40 Seiten je Website.

## Rückmeldung
Eine Zeile je Preis in `strompreise_vorlage.csv` (mehrere Zeilen je Netzgebiet möglich), Commit und Sync, dann der Nutzer „synched“.
