# An den Kollegen: Hochlastzeitfenster und Modul 3 ordentlich abarbeiten (12.11.2026)

Es fehlen **236 von 831** Netzbetreibern bei den Hochlastzeitfenstern (595 fertig) und bei Modul 3 noch 541. Das ist die größte Lücke im Projekt. Bis zum Jahreswechsel sind es 50 Tage. Bitte arbeite die Listen jetzt **vollständig, genau und in Stapeln** ab.

## Was fehlt
| Status | Anzahl | Was zu tun ist |
|---|---:|---|
| Dokument vorhanden, nicht lesbar | 106 | am Dokument ablesen (Auftrag 7, `ablesen`) |
| Kein Dokument gefunden | 89 | suchen (Auftrag 7, `suchen`) |
| Raster-Grafik | 11 | markierte Viertelstunden am Bild ablesen |
| Maschinell gelesen, nicht bestätigt | 10 | gegenprüfen |
| Dokument hat das falsche Jahr | 7 | neues Dokument suchen |
| Von dir gelesen, nicht bestätigt | 5 | Beleg nachliefern |
| "keine Hochlastzeitfenster" | 5 | Stelle im Dokument belegen |
| Zurückgehalten (unplausibel) | 3 | Gemünden, Fröndenberg-Wickede, Töging: Dokument liefern oder lesen |
| **Modul 3** | 426 mit Uhrzeiten | Auftrag 5 |

## Was ich von dir erwarte
1. **Reihenfolge einhalten:** erst `ablesen` (116, das Dokument liegt vor), dann `prüfen` (5), dann `suchen` (132). Danach Modul 3.
2. **Stapel liefern:** alle 10 bis 20 Netzbetreiber ein Push, nicht erst am Ende. Vor jedem Push `daten/hlzf_lieferung_pruefen.py` bzw. `daten/modul3_manuell_pruefen.py` laufen lassen. Rote Zeilen nicht liefern.
3. **Jede Zeile belegen:** Seite und Zelle im Dokument in `bemerkung`. Kann ich eine Zeit im Dokument nicht wiederfinden, ist die Zeile nicht fertig. Bei Bild-PDFs ausdrücklich schreiben "nur im Bild, Seite X, Zeile Y".
4. **Die bekannten Fehler nicht wiederholen:** Mittelspannung gehört nicht nach MS/NS. Fehlt eine Ebene im Dokument, Felder **leer** lassen, nicht `keins`. Spaltenreihenfolge aus der Kopfzeile lesen. Alle Fenster einer Zelle eintragen. Alle Zeilen rückwärts prüfen.
5. **Beide Jahre gelten:** Fehlt 2026, nimm 2027 und umgekehrt, was zuerst gefunden wird, reicht. **Ein Dokument nicht deshalb aussortieren, weil es 2026 statt 2027 heißt** (SWTE, Waging, Lünen waren 2026 und hätten gelesen werden müssen). Nur 2025 und älter fällt weg.
6. **Nichts raten.** Unklar: leer lassen und im `bemerkung` begründen. Aber: nach drei Minuten ohne Ergebnis weitergehen und zurückkommen, nicht festbeißen.
7. **Tempo:** Nutze `daten/hlzf_entwurf.py` (Entwurf mit Zeitzeilen und Seitenbildern). Gleiche Layouts hintereinander lesen. Siehe `2026-11-12_TEMPO_FUER_KOLLEGE.md`.
8. **Zahlen nur aus den Dateien:** In Meldungen nur Zahlen aus `lauf/hlzf_zusammen.csv` und den Export-Dateien nennen. "566 mit Hochlastzeitfenstern" war die Zahl der Netzbetreiber mit nutzbaren Preisen, nicht der mit Fenstern.
9. **Sperren nicht umgehen:** 403, Cloudflare, robots.txt werden nicht umgangen. Solche Dokumente meldest du als `blockiert` mit Adresse, der Nutzer holt sie im Browser.

## Rückmeldung
Nach jedem Stapel eine kurze Meldung in `eingang/kommunikation/`: gelesen, nicht gefunden, blockiert, unklar (mit Grund). Ich prüfe Stichproben und nehme die Zeilen nach `main`. Bei 6 deiner Zeilen aus der letzten Lieferung stand die Belegpflicht noch offen (Selb, Schwerin, Guben, MITNETZ, Remscheid, Villingen); ich habe deine Antwort noch nicht abschließend geprüft.

Gesamtplan mit Fristen: `ergebnis/PLAYBOOK_2027.md`, Aufgabenverteilung: `ergebnis/ARBEITSTEILUNG.md`.
