# Datensatz Netzentgelte Strom 2026 für conplot.de

Zwei Dateien, erzeugt mit `python run.py export` aus den geprüften Ergebnissen:

| Datei | Inhalt |
|---|---|
| `netzbetreiber_2026.json` | alle 831 Stromverteilnetzbetreiber mit Netzentgelten, Hochlastzeitfenstern und Quellen |
| `plz_2026.json` | Postleitzahl → Netzbetreiber (Nummer und Anteil in Prozent) |

Alle Preise sind **netto**, ohne Strom, Messstellenbetrieb, Konzessionsabgabe, Umlagen und Umsatzsteuer.
Es stehen nur **geprüfte** Werte drin. Fehlt ein Teil oder ist er unplausibel, steht `null`, und das Feld
`fehlt` nennt, was fehlt.

## Netzbetreiber finden

```json
"08393": [{"nr": 565, "anteil_prozent": 78.4}, {"nr": 6, "anteil_prozent": 21.6}]
```

Eine Postleitzahl kann mehrere Netzbetreiber haben. Der Anteil beruht auf den Anlagen im
Marktstammdatenregister und ist nur ein Anhaltspunkt. Bei mehreren Einträgen den Nutzer wählen lassen
(sein Netzbetreiber steht auf der Netzrechnung) oder den mit dem größten Anteil vorschlagen.

## Datensatz eines Netzbetreibers

```json
{
 "nr": 565,
 "netzbetreiber": "Stadtwerke Meerane GmbH",
 "jahr": 2026,
 "preisstand": "unklar",
 "stand_datum": "19.12.2025",
 "grenze": "<2500",
 "rlm": {
  "ns":   {"lp_unter_eur_kw_jahr": 37.37, "ap_unter_ct_kwh": 6.59, "lp_ab_eur_kw_jahr": 133.45, "ap_ab_ct_kwh": 2.74},
  "msns": null
 },
 "slp": {"ap_ct_kwh": 5.28, "gp_eur_jahr": 66.0},
 "hlzf": null,
 "quelle": {"rlm": "https://…pdf", "slp": "https://…pdf"},
 "status": "ok",
 "fehlt": ["hlzf"]
}
```

| Feld | Bedeutung |
|---|---|
| `preisstand` | `endgültig`, `vorläufig` oder `unklar` (Preisblatt sagt es nicht). Bei vorläufig im Ergebnis einen Hinweis zeigen |
| `grenze` | `<2500`: unter 2.500 Benutzungsstunden gilt die Gruppe „unter“, ab 2.500 die Gruppe „ab“. `<=2500`: genau 2.500 Stunden gehören noch zu „unter“ |
| `rlm.ns` | Kunden mit Leistungsmessung, Entnahme in der **Niederspannung** |
| `rlm.msns` | Entnahme aus der **Umspannung Mittelspannung/Niederspannung** (eigener Trafo) |
| `lp_…_eur_kw_jahr` | Leistungspreis in Euro je kW **und Jahr** (Jahresleistungspreissystem), nicht je Monat |
| `ap_…_ct_kwh` | Arbeitspreis in Cent je kWh |
| `slp` | Kunden ohne Leistungsmessung (bis 100.000 kWh): Arbeitspreis und Grundpreis |
| `hlzf` | Hochlastzeitfenster für die atypische Netznutzung, siehe unten. `null` = noch nicht erfasst |
| `quelle` | Preisblatt, aus dem die Werte stammen |
| `fehlt` | `rlm_ns`, `slp`, `hlzf`: was für diesen Netzbetreiber noch nicht vorliegt |

## Netzentgelt berechnen (Kunden mit Leistungsmessung)

```
Benutzungsstunden h = Jahresverbrauch kWh ÷ Jahreshöchstleistung kW
Gruppe = "unter", wenn h < 2.500 (bei grenze "<=2500": h ≤ 2.500), sonst "ab"
Netzentgelt € = LP(Gruppe) × kW  +  AP(Gruppe) × kWh ÷ 100
```

**Wichtig für Peak Shaving:** Nach dem Kappen sinkt die Jahreshöchstleistung, die Benutzungsstunden
steigen. Dabei kann die Gruppe wechseln. Deshalb immer **vorher und nachher getrennt** mit der jeweils
richtigen Gruppe rechnen, nie mit einem einzigen Leistungspreis.

Beispiel Meerane, 500.000 kWh, Kappung 300 → 200 kW:

| | vorher | nachher |
|---|---:|---:|
| Benutzungsstunden | 1.667 → unter | 2.500 → ab |
| Leistungsanteil | 37,37 × 300 = 11.211 € | 133,45 × 200 = 26.690 € |
| Arbeitsanteil | 6,59 ct × 500.000 = 32.950 € | 2,74 ct × 500.000 = 13.700 € |
| Netzentgelt | 44.161 € | 40.390 € |

Ersparnis 3.771 € pro Jahr. Mit einem pauschalen Leistungspreis von 150 € je kW wären es 15.000 €.

Der Arbeitspreis des Netzbetreibers gehört zum Netzentgelt. Wird zusätzlich ein Strompreis angesetzt, sollte
er **ohne** Netzentgelt sein, sonst wird der Arbeitspreis doppelt gezählt und der Gruppenwechsel nicht erfasst.

## Hochlastzeitfenster und atypische Netznutzung

```json
"hlzf": {
 "quelle": "https://…Hochlastzeitfenster-fuer-2026….pdf",
 "ns": {
  "zeitfenster": {"fruehling": [], "sommer": [], "herbst": ["16:45-18:00"], "winter": ["12:00-13:30", "16:15-19:15"]},
  "schwelle_prozent": 30,
  "herkunft_schwelle": "laut Netzbetreiber",
  "mindestverlagerung_kw": 100
 },
 "msns": { … }
}
```

| Feld | Bedeutung |
|---|---|
| `zeitfenster` | Uhrzeiten an **Werktagen** je Jahreszeit (Frühling März–Mai, Sommer Juni–August, Herbst September–November, Winter Dezember–Februar). Leere Liste = in dieser Jahreszeit kein Hochlastzeitfenster. Wochenenden, Feiertage und die Zeit zwischen Weihnachten und Neujahr gelten in der Regel nicht |
| `schwelle_prozent` | Erheblichkeitsschwelle: Die höchste Leistung in den Zeitfenstern muss um mindestens so viel Prozent unter der Jahreshöchstleistung liegen |
| `herkunft_schwelle` | `laut Netzbetreiber` oder `Standard (fachlich zu bestätigen)` |
| `mindestverlagerung_kw` | Mindestabstand in kW zwischen Jahreshöchstleistung und Höchstleistung im Zeitfenster, wenn der Netzbetreiber ihn nennt, sonst `null` |

Prüfung (vereinfacht, fachlich zu bestätigen):

```
Abstand %   = (Jahreshöchstleistung − Höchstleistung im Zeitfenster) ÷ Jahreshöchstleistung × 100   ≥ schwelle_prozent
Abstand kW  = Jahreshöchstleistung − Höchstleistung im Zeitfenster                                    ≥ mindestverlagerung_kw
individuelles Netzentgelt = LP(Gruppe) × Höchstleistung im Zeitfenster + Arbeitsanteil,
                            mindestens 20 % des normalen Netzentgelts
Ersparnis ≥ 500 € pro Jahr (Bagatellgrenze)
```

Ein Speicher darf dabei **nur außerhalb** der Zeitfenster nachladen, sonst steigt die Leistung im Zeitfenster.

## Stand

Netzentgelte: 492 Netzbetreiber mit Werten für Kunden mit Leistungsmessung in der Niederspannung, 449 mit
Werten ohne Leistungsmessung. Hochlastzeitfenster: 125 Netzbetreiber (112 mit Niederspannung). Die übrigen
werden ergänzt.
