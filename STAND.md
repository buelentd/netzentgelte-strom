# Stand Netzentgelte Strom 2026 (31.10.2026, 19:15 Uhr)

## Ergebnis

**566 von 831 Netzbetreibern sind nutzbar** (mindestens ein Teil der Preise geprüft und plausibel).

| | Anzahl |
|---|---:|
| Vollständig: Standardlastprofil und registrierende Leistungsmessung | 375 |
| Nur registrierende Leistungsmessung | 117 |
| Nur Standardlastprofil | 74 |
| **Nutzbar zusammen** | **566** |
| Preisblatt vorhanden, Werte aber auffällig oder unvollständig | 19 |
| Kein Preisblatt gefunden | 184 |
| Website blockiert automatische Abrufe | 38 |
| robots.txt verbietet den Abruf | 23 |
| Keine Website | 1 |

Spannen (nur geprüfte Werte):

- Standardlastprofil, Arbeitspreis Niederspannung: 3,17 bis 14,98 Cent pro Kilowattstunde, Median 7,28 (449 Netzbetreiber)
- Registrierende Leistungsmessung Niederspannung bei 4.000 Benutzungsstunden: 2,80 bis 14,46 Cent pro Kilowattstunde, Median 6,34 (492 Netzbetreiber)

Preisstand der vollständigen: unklar 215, endgültig 132, vorläufig 28.

Dateien:

- `ergebnis/netzentgelte_2026.csv`: alle 831, Spalten erklärt in `LEGENDE.md`
- `ergebnis/gefunden.csv`: die nutzbaren, mit Quelle je Preisart
- `ergebnis/nicht_gefunden.csv`: die übrigen, mit Grund
- `ergebnis/zusammenfassung.md`: Zahlen je Status und Spannen

## Verlauf heute

| Schritt | Nutzbar |
|---|---:|
| Morgens (Lauf 18) | 467 |
| Hochgeladene Preisblätter (Westnetz, Bayernwerk, E.DIS, Schleswig-Holstein Netz, Syna, Stuttgart, Avacon) und Verbesserungen beim Auslesen | 491 |
| Brave-Suche, erster Suchbegriff (Lauf 30) | 504 |
| Korrektur „vermiedene Netzentgelte“ und Suchbegriff mit Jahr (Lauf 32) | 509 |
| Auslesen verbessert (Nordhausen, Borken, Schwäbisch Hall, ÜZ Mainfranken, e.wa riss, Ratingen und andere), neu ausgelesen (Lauf 33) | 517 |
| Bekannte Preisblätter direkt neu geladen (Lauf 34), 22 weitere vollständig | 522 |
| Unklare Umspannung macht Niederspannung nicht mehr unbrauchbar (Lauf 35) | 526 |
| Grenze „bis zu / mehr als 2.500“ und über mehrere Kopfzeilen verteilte Grenzen (Lauf 36), 18 weitere vollständig | 527 |
| Preisblatt ohne Namen von der eigenen Website gilt als zugeordnet (Lauf 37) | 566 |

## Was die Brave-Suche gebracht hat

- Suchbegriff jetzt: `<Name ohne Rechtsform> netzentgelte strom 2026 pdf`, nur PDFs von der eigenen Website.
- Lauf 30: 141 Netzbetreiber mit Treffern, 432 PDFs, daraus 13 neu nutzbar.
- Lauf 32: 96 Netzbetreiber mit Treffern, 278 PDFs, daraus 5 neu nutzbar.
- Der Großteil der Treffer sind **ältere Preisblätter** (2025 und früher), auch mit „2026“ im Suchbegriff:
  151 von 278 PDFs in Lauf 32. Dazu kommen Stromtarife für Endkunden, Hausanschluss- und
  Messstellenpreisblätter und tote Links.
- Brave-Guthaben: etwa 4,98 von 5,00 US-Dollar verbraucht. Der Abrechnungszeitraum endet am 01.11.2026.
  9 Netzbetreiber ohne Preisblatt wurden wegen der Höchstzahl von 185 Abfragen nicht mehr gesucht.

## Offene Punkte, nach Nutzen geordnet

1. **Weitere Lücken beim Auslesen.** 210 Netzbetreiber haben ein Preisblatt, bei dem ein Teil fehlt oder
   auffällig ist (Liste: `ergebnis/nicht_gefunden.csv`, Status `pruefen`). Arbeit an den Textauszügen, danach
   `AUSLESEN=true` (Minuten, ohne Internet). Jede Änderung gegen alle Textauszüge abgleichen (keine Verluste).
2. **Ramstein:** Drei Netzbetreiber mit derselben Website (Ramstein, Bruchmühlbach-Miesau, Weilerbach); die Regel
   „Zuordnung unklar“ hat Ramstein den Standardlastprofil-Teil genommen. Künftig verliert ein Netzbetreiber beim
   Neu-Laden oder Neu-Auslesen keinen nutzbaren Teil mehr.
3. **Netzgesellschaft mit eigener Adresse.** Beispiel Aschaffenburg: Im Marktstammdatenregister steht
   `www.stwab.de`, die Preisblätter liegen auf `www.netze-stwab.de`. Vorschlag: Als eigene Website gilt auch
   eine Adresse, die den Kern der bekannten Adresse enthält (mindestens 5 Zeichen). Für Aschaffenburg liegen
   die Links vor:
   - https://www.netze-stwab.de/Stromnetz/Netzzugang-Entgelte/AVG-Preisblatt-2026-Netznutzung-mit-Leistungsmessung.pdf
   - https://www.netze-stwab.de/Stromnetz/Netzzugang-Entgelte.html
4. **184 ohne Preisblatt.** Die Suche liefert hier meist alte Jahre. Weiter nur von Hand: Link in
   `lauf/hinweis_urls.csv` eintragen oder PDF in `lauf/preisblaetter/` ablegen und in `lauf/preisblaetter.csv`
   zuordnen (Beispiele dort).
5. **38 blockiert und 23 robots.txt:** nur von Hand (PDF herunterladen und ablegen wie in Punkt 4).
6. **Preisblätter 2027.** Ist für ein Netzbetreiber kein Blatt 2026 auffindbar, wird jetzt das Blatt 2027 mit
   Hinweis genommen. Für eine eigene Tabelle 2027 braucht es noch einen eigenen Ergebnisordner je Jahr
   (sonst vermischen sich die Fortschrittsdateien) und den Ausschluss der Pilotwerte 2026.

## Bedienung (Kurzfassung, Einzelheiten in README.md)

Ein Lauf startet bei jeder gepushten Änderung an `lauf/anstoss.env`. Wichtige Einstellungen:

| Einstellung | Wirkung |
|---|---|
| `WIEDERHOLEN=kein_preisblatt` | welche Status erneut bearbeitet werden |
| `NUR_SUCHTREFFER=true` | nur Brave-Treffer und Hinweis-Links prüfen, Websites nicht durchsuchen (etwa 20 Minuten) |
| `AUSLESEN=true` | nur die schon geladenen Preisblätter neu auslesen, ohne Internet (Minuten) |
| `SUCHE_MAX=185` | Höchstzahl Brave-Abfragen je Lauf (Kosten: 5 US-Dollar je 1.000) |
| `NEU_PRUEFEN=` | Nummern, die unabhängig vom Status neu bearbeitet werden; nach Gebrauch leeren |

Ein Ergebnis wird in den Modi `NUR_SUCHTREFFER` und `AUSLESEN` nur übernommen, wenn es besser ist als das
bisherige. Der Fortschritt im Repository hat Vorrang vor dem Zwischenspeicher des Laufs.

## Bekannte Fehler von heute (behoben)

- Ein älterer Zwischenspeicher hat den gespeicherten Fortschritt überschrieben (Lauf 29): Ergebnisse der Läufe
  25 und 28 gingen verloren und wurden zusammengeführt.
- Die Liste „schon gesucht“ hat einen Lauf mit neuem Suchbegriff komplett übersprungen (Lauf 31). Entfernt.
- Eine Anmerkung zu vermiedenen Netzentgelten im Kopf hat echte Preisblätter verworfen (Butzbach, OVAG).
- Suchtreffer fremder Netzbetreiber wurden geprüft (REDINET). Jetzt nur eigene Website.
