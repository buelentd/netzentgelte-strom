# Aufgabe: 44 Netzbetreiber ohne Dokument

Datei `aufgabe_44_ohne_dokument.csv`. Für jeden Netzbetreiber zwei Dokumente suchen und die Dateien liefern.

1. **Preisblatt Netzentgelte Strom 2026** (Spalte `suche_preisblatt`): endgültiges Blatt vor vorläufigem. Nicht 2027, nicht Gas, Wärme, Wasser, nicht nur Einspeisung. Datei speichern als `dateiname_preisblatt`.
2. **Hochlastzeitfenster 2026** (Spalte `suche_hochlastzeitfenster`): Datei speichern als `dateiname_hochlastzeitfenster`. Steht es im Preisblatt selbst, ist keine zweite Datei nötig (kurz vermerken).
3. Seiten können HTML sein (Tabelle in der Webseite): dann die Seite als PDF speichern oder die Werte als Text liefern.
4. Status `blockiert` und `robots`: im Browser öffnen und speichern. Keine Umgehung von Sperren, kein Web-Reader eines Dritten (kein Jina).
5. Nichts schätzen. Findest du nichts: in `bemerkung` notieren (z. B. "kein Preisblatt auf der Website", "nur 2025").
6. Ergebnis in `eingang/pdfs_neu/` ablegen, Commit und Push. Zusätzlich eine kurze Liste: nr; gefunden ja/nein; URL; Bemerkung.
