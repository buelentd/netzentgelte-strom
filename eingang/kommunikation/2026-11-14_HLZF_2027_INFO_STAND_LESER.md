# HLZF-2027-Suche: Wie der Stand zu lesen ist (Antwort an Kollegen, 14.11.2026)

## Klarstellung zur Lieferungs-Nummerierung

Die HLZF-2027-Suche wird seit Lieferung 1 als EINE fortgeschriebene Meldungsdatei geführt:
- `eingang/kommunikation/2026-11-14_HLZF_2027_SUCHE_LIEFERUNG_1.md` enthaelt die Nachtraege "Lieferung 1" bis "Lieferung 26" als fortlaufende Abschnitte.
- Jede Lieferung ist zusaetzlich als eigener Commit mit "HLZF 2027 Suche Lieferung N" im Titel dokumentiert (z. B. Commit 6d185182 = Lieferung 26: Ramstein, EVA voll; Ottersberg, Gunzenhausen nicht zuordenbar; 4x kein Fund).

Es gibt also KEINE einzelnen Dateien "SUCHE_LIEFERUNG_2.md" usw. Bitte fuer den Stand nicht nach "Lieferung 26"-Dateien suchen, sondern:
1. `ergebnis/hlzf/hlzf_2027_gelesen.csv` lesen (der Datenstand),
2. die Commit-Liste des Branches nach "HLZF 2027 Suche" filtern,
3. die Nachtrags-Abschnitte in der einen Meldungsdatei.

## Aktueller Stand nach Lieferung 26 (gezaehlt aus hlzf_2027_gelesen.csv)

- Bestand gesamt: 368 Zeilen, davon 316 mit jahr=2027.
- Von den 400 Eintraegen der Arbeitsliste haben damit 316 eine 2027-Zeile (voll gelesen, Raster-/Layout-Vorbehalte oder ehrliche Negativ-/Blockiert-Befunde, siehe je Zeile quelle_art/bemerkung).
- Offen: 142 Eintraege, alle Kleinbetreiber unter ca. 9.000 Einwohnern (die Grossen sind abgearbeitet). Sortiert nach Einwohnern groessten zuerst, laufend in Lieferungen a 5-15 NBs.
- Such-Historie je geprueftem NB: `lauf/nutzer_hinweise.csv` (mastr_nr, gepruefte URL, Zweck, Datum, "Vibe (HLZF-2027-Suche)").

## Weiterarbeit

Lieferung 27 laeuft (naechste 10 offene NBs, Groesste zuerst: Ludwigslust-Grabow, Zerbst, Bad Endorf, Kahl, Duderstadt, Grevesmuehlen, Schwarzenbruck, Bad Sooden-Allendorf, Budenheim, Velten). Ergebnisse folgen als Nachtrag in der Meldungsdatei plus Commit "HLZF 2027 Suche Lieferung 27".
