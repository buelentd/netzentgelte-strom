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
| `rlm.ms` | Entnahme in der **Mittelspannung** (Großspeicher, Ladehubs mit eigener Mittelspannungsanbindung), soweit das Preisblatt sie ausweist |
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

## Stand 12.11.2026 (neu erzeugt aus der aktuellen Tabelle mit `PYTHONPATH=. python daten/conplot_export.py`)

**Schlüssel ist die MaStR-Nummer** (`mastr_nr`, SNB…), nicht `nr`. Die PLZ-Datei verweist auf `mastr_nr`:
`"08393": [{"mastr_nr": "SNB…", "anteil_prozent": 78.4}]`.

| | Anzahl von 831 |
|---|---|
| RLM Niederspannung (Jahresleistungspreise) | 781 |
| SLP (Arbeitspreis, Grundpreis) | 778 |
| **Hochlastzeitfenster** (nur geprüft: `hlzf.status` gelesen_nutzer, gelesen_unser, gelesen_kollege_verifiziert, gelesen_aus_2027) | **555** |
| **Modul 3** (zeitvariable Netzentgelte nach § 14a, `modul3`) | 25 (wird ergänzt) |
| **Netzentgelte 2027 vorläufig** (`preise_2027_vorlaeufig`, gleiche Struktur wie `rlm`/`slp`) | 32 (wird ergänzt) |

### Neue Felder
- `hlzf.status`: Herkunft. `gelesen_aus_2027` heißt: Das Dokument gilt für 2027 und wird für 2026 und 2027 genutzt (Festlegung).
  Die Zeitfenster gelten **nur an Werktagen**, die Uhrzeiten sind laut Dokument von–bis.
- `hlzf.ns` und `hlzf.msns`: Fehlt eine Jahreszeit in `zeitfenster`, nennt das Dokument sie nicht. Leere Liste = "keins".
  `herkunft_schwelle` ist `laut Netzbetreiber` oder `Standard (fachlich zu bestätigen)` (30 % für NS und MS/NS).
- `modul3`: Liste je Jahr. `hochtarif`, `standardtarif`, `niedertarif` mit `zeiten` (Text, mehrere Fenster) und `ct_kwh` (netto), `quartale`
  (in welchen Quartalen gilt Modul 3, zum Beispiel `Q1+Q4`), `preisstand`, `quelle`, `hinweis`. **Modul 3 gibt es nur zusammen mit Modul 1 und einem
  intelligenten Messsystem, nicht für RLM-Kunden.** Preise stehen netto im Preisblatt, die Zeiten gelten täglich (Mo–So), nicht nur Werktage.
- `preise_2027_vorlaeufig`: vorläufige Netzentgelte 2027, wo das Preisblatt gelesen ist.

### Hinweis zu den Zeitfenstern (zwei Arten, nicht verwechseln)
1. **Hochlastzeitfenster nach § 19 Abs. 2 StromNEV:** für die atypische Netznutzung (Peak Shaving mit individuellem Netzentgelt).
2. **Modul 3 (§ 14a EnWG):** zeitvariabler Arbeitspreis. Das ist keine atypische Netznutzung.

Die übrigen Netzbetreiber werden ergänzt.

## Zeitreihe der Hochlastzeitfenster (Datenprodukt für Optimierungsmodelle)

`PYTHONPATH=. python daten/hlzf_zeitreihe.py <MaStR-Nr.> <ns|msns> <Jahr> [datei.csv]` erzeugt je Netzbetreiber, Ebene und Jahr einen Vektor mit
einem Eintrag je Viertelstunde (35.040 im Jahr 2026 und 2027, lokale Zeit ohne Sommerzeit-Verschiebung, Zeitzone legt der Nutzer fest):
`is_hlzf = 1`, wenn die Viertelstunde in einem Hochlastzeitfenster liegt. Damit lässt sich jedes Lastprofil und jedes Erzeugungsprofil per einfachem
Join gegen das Fenster des jeweiligen Netzbetreibers rechnen.

Regeln, laut Dokumenten der Netzbetreiber (Standard; Abweichungen im Einzelfall möglich, deshalb im Datensatz `hlzf.quelle` prüfen):
- Nur **Werktage Mo bis Fr**, ohne gesetzliche **Feiertage des Bundeslands** des Netzbetreibers und ohne 24.12. bis 01.01. (Weihnachten bis Neujahr).
- **Brückentage:** Die Dokumente sagen "maximal ein Brückentag" oder "Brückentage" und sind nicht einheitlich (Arneburg: "alle Brückentage sind Werktage").
  Die Zeitreihe zieht sie standardmäßig **nicht** ab (Parameter `brueckentage=True` zieht Tage zwischen Feiertag und Wochenende ab).
- Jahreszeiten: Frühling März bis Mai, Sommer Juni bis August, Herbst September bis November, Winter Dezember bis Februar.
- Ein Fenster `16:45-19:45` gilt von 16:45 (einschließlich) bis 19:45 (ausschließlich). Einzelne Netzbetreiber geben das Ende als Zeitstempel einer Messperiode an
  (Aalen, Netze ODR, Düsseldorf); die Schreibweise steht im Dokument.
- Bekannte Ausnahme: Covestro Brunsbüttel (Werksnetz) nennt Fenster ohne Beschränkung auf Werktage.
- Eine einzelne Überschreitung im Fenster ändert die höchste Leistung im Fenster und damit das individuelle Netzentgelt (Rechenweg oben, Prüfung vereinfacht, fachlich zu bestätigen).
