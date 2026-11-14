# Modul 3: Korrektur Dubletten in modul3_manuell.csv (14.11.2026)

Bei der Lieferung 2 (unterbrochener Push) wurden 22 Zeilen des Lieferumfangs versehentlich ein zweites Mal angehängt, obwohl sie bereits enthalten waren. Dieser Commit bereinigt die Datei.

## Was wurde korrigiert

- 21 doppelte Zeilen entfernt (22 Netzbetreiber des Lieferungs-2-Umfangs, davon war eine Zeile mit dem Bestand identisch).
- Bei 5 Netzbetreibern wurde die jeweils vollständigere/aktuellere Fassung behalten:
  - Stadtwerke Herne AG (Zeiten übernommen statt leere Fassung)
  - SWT Stadtwerke Trier Versorgungs-GmbH (vollständige Fassung mit Quelle NNe_2026.pdf auf stadtwerke-tir.de statt blockiert-Leerfassung)
  - SWK Kaiserslautern (Quartalsangabe Q1+Q4 ergänzt)
  - Kreiswerke Main-Kinzig (Preise 14,98/7,49/1,08 und Q1+Q4 ergänzt)
  - SÜC Energie und H2O (vollständige Fassung mit Zeiten und Preisen statt Leerbefund)
- Bei allen übrigen Dubletten wurde die bereits gelieferte Fassung (MODUL3_LIEFERUNG_2.md ff.) beibehalten.
- 5 Zeilen mit verschobener Spaltenstruktur repariert (leeres Feld preisstand fehlte, Werte rutschten eine Spalte): Stadtwerke Mühlhausen Netz, Stadtwerke Annaberg-Buchholz Energie, Stadtwerke Werl, SWN Stadtwerke Northeim, Stadtwerke Herne AG.

## Stand nach Korrektur

- 404 Datenzeilen (1 Header + 404), alle mit korrekten 13 Spalten.
- 372 Zeilen mit Hinweis gelesen_kollege, 6 Zeilen gelesen_unser (Bestand), Rest ohne Lesevermerk (z. B. Hinweise auf blockierte Seiten oder Befunde ohne Lesung).
- Keine MaStR-Dubletten mehr.
- 24-h-Prüfung der expliziten Zeitfenster (ohne Q-Präfix-Zeilen und Restzeit-Zeilen): 233 Zeilen geprüft, 0 Fehler.
- Lieferungsmeldungen 1 bis 20 (MODUL3_LIEFERUNG_1.md bis _20.md) bleiben unveraendert gueltig; an ihren Zahlen aendert sich nichts, da es sich um eine Dublettenbereinigung handelt.
