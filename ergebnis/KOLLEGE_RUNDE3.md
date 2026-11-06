# Anleitung für den Kollegen: Runde 3 (Stand 06.11.2026)

Danke für Runde 2. Ausgewertet: 13 Preisblätter direkt übernommen, weitere 47 habe ich einzeln am Text geprüft und von Hand eingetragen. 562 von 831 Netzbetreibern sind jetzt „ok“. Die Liste für Runde 3 steht in `ergebnis/kollege_runde3.csv` (69 Zeilen, Spalte `aufgabe` sagt je Zeile, was fehlt). Zeilen, die du in Runde 2 mit `nicht_veroeffentlicht`, `nicht_gefunden` oder `gesperrt` begründet hast, sind nicht mehr drin.

## Regeln (unverändert)
- Nur Strom, nur 2026, nur Preisblätter bzw. Hochlastzeitfenster des **eigenen** Netzbetreibers (Name muss im Dokument stehen oder das Dokument liegt auf der eigenen Website).
- Dateiname `<nr>_preis_<Originalname>.pdf` bzw. `<nr>_hlzf_<Originalname>.pdf`, alle flach in `eingang/lieferung3`. Mehrere Dateien je Nummer erlaubt (SLP und RLM getrennt).
- Jede Datei vorher mit `daten/dokument_pruefen.py` prüfen. FALSCH nicht ablegen.
- Nichts schätzen, nichts abtippen, außer bei Scans und Rastern (dann Abschrift als `<nr>_..._abschrift.txt`).
- Nicht 2027 und nicht „vorläufig 2027“ mischen. 2027-Dateien in einen Unterordner `2027_vorlaeufig`, nicht in die Lieferung.

## Aufgaben
1. **Preisblätter, die nur zur Hälfte da sind (Zeilen mit Hinweis „nur SLP geliefert“ u. ä., etwa 12):** Geliefert ist nur das Blatt „ohne Leistungsmessung“ (SLP). Es fehlt das Blatt „mit Leistungsmessung“ (Jahresleistungspreise unter und ab 2.500 h). Beispiele: Dießen 118, Zirndorf 736, Baiersdorf 413, Waldmünchen 706, Soltau 661, Peißker 123, EVB 181, SachsenNetze 39. Gibt es kein zweites Blatt, bitte `nicht_veroeffentlicht` mit Datum und Seite melden.
2. **Falsches Dokument geliefert:** LEW 36 (Anschlusspreisblatt statt Netznutzung), FASTR 197 (Blatt gehört EGC, Nr. 88), Landshut 544 (nur § 19), SachsenNetze HS.HD 366 (eigenes Blatt fehlt). Richtiges Blatt suchen.
3. **Nicht lesbar:** Borna 743 (Scan ohne Text) und Thüga 46 (Jahresleistungspreise stehen nicht im Text): Werte als Text abschreiben, wenn kein lesbares PDF existiert.
4. **Lücken im Dokument:** BASF Lausitz 63 und Deidesheim 445 (SLP-Grundpreis fehlt), Fellbach 476 (Arbeitspreis bei Umspannung leer): prüfen, ob es ein weiteres Blatt gibt.
5. **Übrige Preisblatt-Zeilen und alle 20 Hochlastzeitfenster-Zeilen:** laut Liste, siehe Spalte `aufgabe`. Hochlastzeitfenster nur liefern, wenn sie als eigenes Dokument oder klar abgrenzbare Tabelle im Preisblatt stehen; sonst `nicht_veroeffentlicht`.
6. **Österreich:** Vorarlberger Energienetze (818) bitte nicht liefern, kein deutsches Netzentgelt.

## Rückmeldung
- Status pro Zeile in `status_runde3.csv` (`nr;art;ergebnis;begruendung;datum`, ergebnis: ja | nicht_veroeffentlicht | nicht_gefunden | gesperrt).
- Dann Commit und Sync, danach meldet der Nutzer „synched“; ich lese ein und nenne die neuen Zahlen.
