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
