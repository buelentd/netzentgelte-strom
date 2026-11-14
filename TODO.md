# TODO (angelegt 14.11.2026, Besprechung 15.11.2026)

## Grundsatz (vom Nutzer, 14.11.2026)

Der Rechner soll so weit wie möglich alles automatisieren und berechnen. Jede Eingabe, die er selbst aus Daten bestimmen kann, wird vorbelegt und ist überschreibbar, mit Angabe der Quellenebene (Preisblatt, Gesetz, Händlerpreis, Annahme). Nur was wir nicht belegen können, bleibt Eingabefeld oder „nicht enthalten". Zu prüfen für jedes Feld: Gibt es eine Datenquelle, aus der der Rechner den Wert selbst holen kann?

Kandidaten zur weiteren Automatisierung: Messentgelt bei Leistungsmessung (steht in den Netzbetreiber-Preisblättern, noch nicht erfasst), Baukostenzuschuss und Netzanschlusskosten (stehen in vielen Preisblättern und ergänzenden Bedingungen der Netzbetreiber, noch nicht erfasst), Jahr 2027 und Umlagen 2027, Modul-3-Zeiten und -Preise je Netzbetreiber, Spitzenleistung aus Branche und Verbrauch, Stadtwerke-Preisformeln für mehr Netzgebiete.

Zur eingefügten „Vollautomatisierung" (CapEx aus kW-Klasse berechnen): Hardware, VNB-Kette und Tarifformel ja, aber Montage und Zähler-/Wandlerpaket nur, wenn belegte Daten dahinterstehen. Heute gibt es dafür keine. Möglich wäre: (1) Anschlusskosten aus den Netzbetreiber-Preisblättern erfassen (Baukostenzuschuss, Anschlussentgelte), (2) Montagezuschlag aus Händlerangeboten ableiten, die dasselbe System mit und ohne Montage nennen. Die im Text genannten Schwellen (30 kW, 135 kW, 44 A) sind nicht belegt und teils vermischt (135 kW ist die Schwelle in VDE-AR-N 4105, nicht der Wechsel zur Mittelspannung). Die Netzebene wählt der Rechner heute nach Jahresverbrauch (Richtwerte, ebenfalls nicht belegt), nicht nach Leistung.

## Vor der Freigabe zu besprechen

**Aufteilung der Speicher-Investition im Rechner** (Commit `7da483e9`, noch nicht abgenommen)

- Aktuell gebaut: drei getrennte Posten. Speicher-System (belegte Händlerpreise, netto), Montage und Elektroinstallation (Eingabefeld, leer = nicht enthalten), Netzanschluss mit Anmeldung, Netzverträglichkeitsprüfung, Messung und Zählerumbau (Eingabefeld, einmalig, leer = nicht enthalten). Hinweistext zu Kostentreibern, keine Pauschalen.
- Zu klären: Soll es so bleiben, oder nur ein Feld, oder mit Orientierungswerten? Eingefügt war ein Vorschlag mit Richtwerten (3.000 € bis über 25.000 €, Wandlermessung ab 44 A, 135 kW bei 4110), die nicht belegt sind. Sie wurden bewusst nicht übernommen.
- Falls nicht gewünscht: Commit `7da483e9` zurücknehmen (`git revert 7da483e9`).
- Wichtig: Der Auftrag dazu kam nicht eindeutig von dir (eingefügter Text), die Umsetzung war eigenmächtig.

## Baukostenzuschuss und Anschlussentgelte erfassen (Plan vom Nutzer, 14.11.2026)

Vorbefund (grobe Suche in den 2.357 Preisblatt-PDFs im Repo): Nur bei etwa einem Dutzend Netzbetreiber steht ein Baukostenzuschuss in €/kW in den Netzentgelt-Preisblättern (rund 34 bis 228 €/kW, z. B. swa Netze, Lohr-Karlstadt, Zellingen). Anschlusskosten stehen bei etwa 10 Quellen mit Betrag, sonst „nach Aufwand". Bei den meisten Netzbetreibern liegt der BKZ in anderen Dokumenten („Ergänzende Bedingungen", „Preisblatt Netzanschluss"), die wir noch nicht gesucht haben.

Plan:

1. **Parser** (pdfplumber oder PyMuPDF): Suchbegriffe „Baukostenzuschuss", „BKZ", „§ 11 NAV", „Netzanschlusskosten", „Pauschalbetrag". Regex für Euro-Beträge je kW (`€/kW`, `EUR/kW`) oder feste Pauschalen im Umkreis dieser Begriffe.
2. **Zuordnung mit Quellenangabe:** Jeder Wert wird mit der MaStR-Nummer als Schlüssel gespeichert, zusammen mit Dateiname, Fundstelle, Netzebene, netto/brutto und Stand (z. B. „BKZ Niederspannung 72,34 €/kW netto, Quelle: <Datei>"). Steht im Dokument „nach Aufwand" oder lässt sich keine Zahl lesen, bleibt der Status „Individuelles VNB-Angebot", kein Schätzwert.
3. **Suche** der separaten Dokumente über alle 831 Netzbetreiber (wie bei den Hochlastzeitfenstern), inklusive HTML-Seiten und Portalen.
4. **Vor der Integration klären:** Gilt der Baukostenzuschuss für einen Speicher überhaupt, und wie wendet ihn der jeweilige Netzbetreiber an (Leistungsbereitstellung nach § 11 NAV)? Erst danach darf der Rechner damit rechnen.
5. **Integration in den Rechner:** Bei Angabe der Speicherleistung (kW) den Baukostenzuschuss automatisch berechnen, mit Quellenangabe des Netzbetreiber-Dokuments. Fehlt der Wert, bleibt das Feld „nicht enthalten".

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
