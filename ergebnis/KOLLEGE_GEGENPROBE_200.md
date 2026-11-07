# Aufgabe für den anderen Leser: unabhängige Gegenprobe an 200 Netzbetreibern

Stand 07.11.2026. Die Aufgaben vergibt Claude (Projektleitung). Entscheidungen zu Definitionen, Recht und Geld bleiben beim Nutzer.

## Ziel
Wir prüfen, ob unsere Werte stimmen. Du liest die Preisblätter **unabhängig** von uns. Unsere Werte bekommst du absichtlich nicht (blinde Gegenprobe), sonst ist es keine Gegenprobe. Den Vergleich macht danach Claude.

## Datei
`ergebnis/gegenprobe_200_blind.csv`: 200 Netzbetreiber (Zufallsauswahl aus den Fällen mit Status ok, ohne die bereits geprüften). Spalten `nr`, `mastr_nr`, `netzbetreiber`, `quelle_url` sind gefüllt. Alle anderen Spalten füllst du.

## Vorgehen je Netzbetreiber
1. Original-Dokument von `quelle_url` laden. Ist die Adresse tot oder ein anderes Jahr, selbst das **Preisblatt 2026, endgültig** auf der Website des Netzbetreibers suchen (PDF, Excel **und HTML-Tabellen** beachten).
2. Datei als `eingang/gegenprobe/<nr>_preis_<Originaldateiname>.pdf` ablegen (HTML: als PDF oder `.html`).
3. Prüfen: Steht der Netzbetreibername im Dokument oder liegt es auf dessen eigener Website? Sonst nicht werten, in `bemerkung` schreiben.
4. Lesen, jeweils Zahl aus der Zeile mit passender Beschriftung:
   - SLP Niederspannung: Arbeitspreis (ct/kWh) und Grundpreis (€/Jahr). Standardpreis, nicht Wärmepumpe, Speicherheizung, § 14a.
   - RLM Jahresleistungspreissystem: je Ebene Mittelspannung (`ms`), Umspannung MS/NS (`msns`), Niederspannung (`ns`): Leistungspreis und Arbeitspreis unter 2.500 h und ab 2.500 h (4 Werte). Netto, nicht brutto.
   - Zeile steht nicht im Dokument: **leer lassen** und in `bemerkung` „nicht ausgewiesen“. Nichts schätzen, nichts umrechnen außer Tagespreise × 365 (dann vermerken).
5. In `fundstelle_seite_zeile` Seite und Beschriftung der Zeile nennen (z. B. „S. 2, Netzebene 6 Umspannung MS/NS“).
6. `jahr_im_dokument` und `preisstand_im_dokument` (endgültig/vorläufig) eintragen.

## Regeln
- Nur Originaldokumente der Netzbetreiber, keine Portale Dritter, keine Zusammenfassungen.
- robots.txt und Bot-Schutz beachten. Gesperrte Seiten nicht umgehen: in `bemerkung` „gesperrt“.
- Maximal 1 Anfrage pro Sekunde je Domain.
- Dezimalkomma, Preise netto, Einheit wie im Spaltennamen.
- Keine Platzhalter und keine runden Zahlen eintragen, die nicht im Dokument stehen.
- Nichts im Namen des Nutzers behaupten. Du hast die Werte gelesen, nicht der Nutzer.
- Bei Unsicherheit leer lassen.

## Abgabe
Ausgefüllte Datei als `eingang/gegenprobe/gegenprobe_200_ausgefuellt.csv`. Claude vergleicht und meldet Abweichungen je Fall. Übernommen wird nur, was am Dokument belegt ist.

## Danach (nur wenn Zeit bleibt)
2027 sammeln: vorläufige Preisblätter 2027 nach `eingang/2027_vorlaeufig/<nr>_preis_<Original>.pdf`, ohne Auswertung.
