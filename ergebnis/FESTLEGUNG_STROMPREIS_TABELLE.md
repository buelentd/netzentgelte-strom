# Festlegung: Block „Ihr Strompreis" im Rechner (Nutzer, 10.11.2026)

Noch nicht gebaut. Beschlossen:

- Tabelle mit allen Posten des Strompreises, Rechenweg aufklappbar, Mouseover nur für Begriffserklärung.
- Farben statt Statusspalte, Legende unten:
  - **grün** = belegt (Preisblatt oder Gesetz), auch die 162 vom Nutzer freigegebenen Netzentgelte
  - **Annahmefarbe** = Annahme, änderbar (z. B. Börsenniveau, Speicherpreis)
  - **grau mit „fehlt"** = nicht erfasst oder offen (z. B. Messstellenbetrieb, 59 offene Netzbetreiber); fließt als „fehlt" in die Summe, nichts wird geschätzt
- Posten: Netzentgelt (AP, Grundpreis/Leistungspreis), Messstellenbetrieb (fehlt), Konzessionsabgabe (KAV nach Einwohnern der Gemeinde, PLZ → `plz_gemeinde.csv` → `gemeinden_einwohner_2025.csv`), KWKG, Offshore, besondere Netznutzung, Stromsteuer, Energie (Börse Day-Ahead oder Festpreis), Aufschlag Stromanbieter (leeres Feld, zu verhandeln), Summe netto, Umsatzsteuer 19 % (gesetzt, § 12 Abs. 1 UStG), Summe brutto.
- Gilt auch für Großkunden (RLM) mit dynamischem Tarif: Börse je Stunde × Lastprofil + Aufschlag.
- Als Angebot nur mit Hinweis „Aufschlag und Messstellenbetrieb nicht enthalten".

## Ergänzung 10.11.2026: Ladezyklen und Lastprofile (Nutzer)

- Neue Tabelle „Ladezyklen" im Ergebnis: Kappung, Solarverschiebung, Handel, Summe, je pro Tag und pro Jahr, dazu entladene/eingespeiste Menge (kWh/Jahr). Rechenwert, nicht Messung.
- Zyklen pro Tag als **Eingabefeld** statt fester Konstante `ZYKLEN = 1.5` (`vorlage.html`), bis **2** einstellbar.
- Folgen, die mitgeändert werden müssen: Barwert-Laufzeit aus Zyklenzahl ableiten (6.000 Zyklen: 1,5/Tag ≈ 11 Jahre, 2/Tag ≈ 8 Jahre; heute fest 12 Jahre), Kapazitätsabbau mit den Zyklen koppeln (als Annahme kennzeichnen), Garantiehinweis (Herstellergrenzen), Wirkungsgrad 0,92 bleibt.
- Lastprofile: alle BDEW-Standardprofile aus `daten/lastprofile/` (H0, G0–G6, L0–L2, G25, H25) den Branchen zuordnen (Vorschlag: Bäckerei G5; Supermarkt/Büro/Handel G0 oder G4; Gastronomie G2 oder G3; Handwerk G1; nicht geprüft). Vorher mit dem Original auf bdew.de abgleichen (laut `HERKUNFT.md` noch offen).
- Börsenniveau und G5 sind keine Annahmen. Zinssatz, Anteil des Vermarkters, Verfügbarkeit Regelenergie, Direktvermarktergebühr gehören zur Speicher-/PV-Rechnung, nicht zum Block „Ihr Strompreis".

## Ergänzung 10.11.2026: Speicher-Annahmen wählbar und in der Annahmenliste (Nutzer)

| Feld | Vorbelegung | Art |
|---|---|---|
| Ladezyklen pro Tag (bis 2) | 1,5 | Annahme, wählbar |
| Zyklen bis Lebensende (Herstellerangabe) | 6.000 | Annahme, wählbar |
| Lebensdauer in Jahren | berechnet = Zyklen gesamt ÷ (Zyklen/Tag × 365); überschreibbar, dann wird die Zyklenzahl pro Tag angezeigt | Rechenwert |
| Kapazitätsabbau (% pro Jahr) | bisheriger Wert (conplot) | Annahme, mit Zyklen gekoppelt |
| Garantie / Zyklengrenze Hersteller | – | Hinweis im Ergebnis, kein Rechenwert |

Alle als Annahme gekennzeichnet in der Annahmenliste.

## Korrektur 10.11.2026 (Nutzer): Farben
Es wird **nur grün** (belegt, auch die 162 Freigaben) angezeigt, **sonst leer**. Keine Annahmefarbe, kein grau „fehlt" in der Tabelle; fehlende Werte bleiben leer. Annahmen stehen nur in der Annahmenliste. Legende unten erklärt nur grün.
Beschlossen zum Bau: Konzessionsabgabe nach Gemeindegröße (plz_gemeinde.csv + Einwohnerzahlen), Ladezyklen/Lebensdauer wählbar, BDEW-Profile, keine Vorbelegung Meerane.

## Umgesetzt 10.11.2026 (Commit siehe Git)
Block „Ihr Strompreis (netto, 2026)" im Rechner: Netzentgelt (SLP: Arbeits- und Grundpreis; RLM: Leistungs- und Arbeitspreis), Messentgelt Eintarifzähler (nur SLP, maschinell gelesen, nicht grün), Konzessionsabgabe nach Einwohnern der Gemeinde (SLP: Höchstsatz Tarifkunden; RLM: 0,11 Sondervertragskunden), KWKG, Offshore, besondere Netznutzung, Stromsteuer (Checkbox Entlastung), Energie und Aufschlag leer, Umsatzsteuer 19 %. Grün = belegt, sonst leer; Rechenweg aufklappbar und als Mouseover. Daten: `ergebnis/plz_gemeinde.csv` (je PLZ die Gemeinde mit größtem Anteil), `gemeinden_einwohner_2025.csv`, `modul_messentgelt_2026_geprueft.csv` (403 Netzbetreiber).
Offen: Messentgelt bei Leistungsmessung, Einstufung Tarif-/Sondervertragskunde ist vereinfacht (SLP = Tarifkunde, RLM = Sondervertrag), BDEW-Profile, Speicherpreis-Staffel.
