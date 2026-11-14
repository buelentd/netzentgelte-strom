# TODO (angelegt 14.11.2026, Besprechung 15.11.2026)

## Grundsatz (vom Nutzer, 14.11.2026)

Der Rechner soll so weit wie möglich alles automatisieren und berechnen. Jede Eingabe, die er selbst aus Daten bestimmen kann, wird vorbelegt und ist überschreibbar, mit Angabe der Quellenebene (Preisblatt, Gesetz, Händlerpreis, Annahme). Nur was wir nicht belegen können, bleibt Eingabefeld oder „nicht enthalten". Zu prüfen für jedes Feld: Gibt es eine Datenquelle, aus der der Rechner den Wert selbst holen kann?

Kandidaten zur weiteren Automatisierung: Messentgelt bei Leistungsmessung (steht in den Netzbetreiber-Preisblättern, noch nicht erfasst), Baukostenzuschuss und Netzanschlusskosten (stehen in vielen Preisblättern und ergänzenden Bedingungen der Netzbetreiber, noch nicht erfasst), Jahr 2027 und Umlagen 2027, Modul-3-Zeiten und -Preise je Netzbetreiber, Spitzenleistung aus Branche und Verbrauch, Stadtwerke-Preisformeln für mehr Netzgebiete.

## Vor der Freigabe zu besprechen

**Aufteilung der Speicher-Investition im Rechner** (Commit `7da483e9`, noch nicht abgenommen)

- Aktuell gebaut: drei getrennte Posten. Speicher-System (belegte Händlerpreise, netto), Montage und Elektroinstallation (Eingabefeld, leer = nicht enthalten), Netzanschluss mit Anmeldung, Netzverträglichkeitsprüfung, Messung und Zählerumbau (Eingabefeld, einmalig, leer = nicht enthalten). Hinweistext zu Kostentreibern, keine Pauschalen.
- Zu klären: Soll es so bleiben, oder nur ein Feld, oder mit Orientierungswerten? Eingefügt war ein Vorschlag mit Richtwerten (3.000 € bis über 25.000 €, Wandlermessung ab 44 A, 135 kW bei 4110), die nicht belegt sind. Sie wurden bewusst nicht übernommen.
- Falls nicht gewünscht: Commit `7da483e9` zurücknehmen (`git revert 7da483e9`).
- Wichtig: Der Auftrag dazu kam nicht eindeutig von dir (eingefügter Text), die Umsetzung war eigenmächtig.

## Weitere offene Punkte (aus dem Tagesabschluss 14.11.)

- Impressum, Datenschutz, „ohne Gewähr" auf der Rechner-Seite (fehlt komplett). Dafür nötig: Firmenname, Anschrift, Vertretungsberechtigte, E-Mail, Registernummer.
- Jahr 2027 als Umschalter (Netzentgelte 2027 vorläufig und Umlagen 2027 liegen vor, Jahreswechsel in 7 Wochen).
- Modul 3 (§ 14a) einbinden (Daten des Kollegen, 404 Zeilen).
- Abgleichtest JavaScript gegen Python.
- Suchkontingent (Brave-Schlüssel) erneuern, dann Dauerläufe wieder auf „an" (`lauf/dauerlauf.txt`, `lauf/dauerlauf_aufschlaege.txt`).
- Rechner auf dem Server automatisch aktualisieren (Zeitsteuerung mit `git pull` und Kopieren nach `/var/www/vhosts/intersignum.de/rechner.intersignum.de/`).
- API api.intersignum.de antwortet mit 404 (falls die API gebraucht wird).
- Hochlastzeitfenster beim Kollegen: 53 PDFs mit leeren Feldern (davon 3 Raster), danach Prüfung der Zeilen mit Vorbehalt. 180 ohne Dokument und 8 im Browser holen.
- Offen im Rechner: Messentgelt bei Leistungsmessung, Aufschlag bei Festpreisverträgen, Speicherpreis unter 200 kWh.
