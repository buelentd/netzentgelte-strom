# Legende: ergebnis/netzentgelte_2026.csv

Trennzeichen `;`, Dezimalkomma, UTF-8. Alle Preise **netto**, ohne Umlagen, Konzessionsabgabe,
Messstellenbetrieb und Umsatzsteuer. Eine Zeile pro Netzbetreiber bzw. Netzgebiet.
Die Einheit steht im Spaltennamen.

## Stammdaten

| Spalte | Inhalt |
|---|---|
| `nr` | laufende Nummer (1–50 = Pilot in der Reihenfolge von `pilot_50_vnb_2026.csv`, danach alphabetisch) |
| `netzbetreiber` | Firmenname laut Marktstammdatenregister (MaStR), bei Pilotfällen ohne MaStR-Treffer der Pilotname |
| `mastr_nr` | MaStR-Nummer des Marktakteurs (SNB…), leer wenn kein MaStR-Treffer |
| `website` | Website laut MaStR (Webseite, sonst Webportal des Netzbetreibers, sonst aus der E-Mail-Domain abgeleitet, dann im `hinweis` vermerkt) |
| `bundesland` | Bundesland bzw. Bundesländer des Netzgebiets, mehrere mit ` / ` getrennt (Anteil ≥ 5 %) |
| `region` | Stadtnetz: Gemeinde(n); sonst die bis zu 3 größten Landkreise des Netzgebiets (`u. a.` = weitere) |
| `netztyp` | `Stadtnetz` / `Regionalnetz` / `Flächennetz`, regelbasiert (siehe unten), leer wenn keine Gebietsdaten |
| `status` | Bearbeitungsstand, siehe unten |

**Herkunft von bundesland/region/netztyp:** Das Netzgebiet wird aus dem MaStR abgeleitet. Die
Solareinheiten mit Standort (PLZ, Gemeinde, Landkreis, Bundesland) sind über ihren
Netzanschlusspunkt genau einem Netzbetreiber zugeordnet und decken praktisch jede Gemeinde ab. Gibt
es dazu keine Daten, wird das Bundesland der Netze laut MaStR genommen, sonst der Sitz des
Netzbetreibers. Der Sitz wird im `hinweis` als „Bundesland/Region laut Sitz (MaStR)“ vermerkt.

**Netztyp-Regel** (bezogen auf die Gemeinden/Landkreise, in denen 95 % der Einheiten liegen):
Stadtnetz ≤ 2 Gemeinden · Regionalnetz ≤ 25 Gemeinden und ≤ 2 Landkreise · sonst Flächennetz.
Unter 10 Einheiten bleibt der Netztyp leer.

## SLP Niederspannung (ohne Leistungsmessung, bis 100.000 kWh/Jahr)

| Spalte | Einheit | Inhalt |
|---|---|---|
| `slp_ap_ct_kwh` | ct/kWh | Standard-Arbeitspreis Niederspannung (Eintarif). Nicht Wärmepumpe, Speicherheizung, unterbrechbare Verbrauchseinrichtungen, § 14a Module, HT/NT |
| `slp_grundpreis_eur_jahr` | €/Jahr | Grundpreis je Zählpunkt; €/Tag × 365 bzw. €/Monat × 12 umgerechnet (im `hinweis` vermerkt) |

## RLM Jahresleistungspreissystem (mit Leistungsmessung, ab 100.000 kWh/Jahr)

| Spalte | Einheit | Inhalt |
|---|---|---|
| `ns_lp_unter_2500h_eur_kw_jahr` | €/kW/a | Leistungspreis Niederspannung, Benutzungsdauer unter 2.500 h |
| `ns_ap_unter_2500h_ct_kwh` | ct/kWh | Arbeitspreis Niederspannung, unter 2.500 h |
| `ns_lp_ueber_2500h_eur_kw_jahr` | €/kW/a | Leistungspreis Niederspannung, ab 2.500 h |
| `ns_ap_ueber_2500h_ct_kwh` | ct/kWh | Arbeitspreis Niederspannung, ab 2.500 h |
| `msns_lp_unter_2500h_eur_kw_jahr` | €/kW/a | Leistungspreis Umspannung MS/NS, unter 2.500 h |
| `msns_ap_unter_2500h_ct_kwh` | ct/kWh | Arbeitspreis Umspannung MS/NS, unter 2.500 h |
| `msns_lp_ueber_2500h_eur_kw_jahr` | €/kW/a | Leistungspreis Umspannung MS/NS, ab 2.500 h |
| `msns_ap_ueber_2500h_ct_kwh` | ct/kWh | Arbeitspreis Umspannung MS/NS, ab 2.500 h |

Tagesleistungspreise (€/kW/Tag) sind × 365 umgerechnet, Arbeitspreise in €/kWh × 100.
Grenze: Standard ist „< 2.500 h / ≥ 2.500 h“. Steht im `hinweis` „Grenze ≤ 2.500 / > 2.500 h“,
gehören genau 2.500 h zur Gruppe „unter“. MS/NS bleibt leer, wenn die Zeile im Preisblatt fehlt
oder unplausibel ist.

## Berechnet: Netzentgelt RLM Niederspannung in ct/kWh

| Spalte | Benutzungsstunden |
|---|---|
| `ns_ct_kwh_bei_1500h` | 1.500 h (Tarif unter 2.500 h) |
| `ns_ct_kwh_bei_2500h` | 2.500 h (Tarif ab 2.500 h; bei „≤ 2.500“-Grenze Tarif unter 2.500 h) |
| `ns_ct_kwh_bei_4000h` | 4.000 h (Tarif ab 2.500 h) |
| `ns_ct_kwh_bei_6000h` | 6.000 h (Tarif ab 2.500 h) |

Formel: `AP + LP × 100 / Benutzungsstunden` mit LP und AP der zu den Benutzungsstunden
passenden Gruppe laut Preisblatt. Es wird nicht automatisch der günstigere Tarif gewählt.
Nur gefüllt, wenn die RLM-Werte unauffällig sind (Plausibilität bestanden, Name passt).

## Abschluss

| Spalte | Inhalt |
|---|---|
| `preisstand` | `endgültig` / `vorläufig` / `unklar`, aus Titel bzw. Kopf des Preisblatts, sonst aus dem Dateinamen |
| `stand_datum` | „Stand“-Datum aus dem Dokument, sonst aus dem Dateinamen (TT.MM.JJJJ) |
| `hinweis` | Besonderheiten: Pilot, Umrechnungen, Grenzregel, Prüfgründe, Herkunft der Website/Region |
| `quelle_url` | URL des Preisblatts. Stammen RLM und SLP aus verschiedenen Dokumenten: `RLM: <url> \| SLP: <url>` |

## status

| Wert | Bedeutung |
|---|---|
| `ok` | RLM- und SLP-Werte gelesen, plausibel, Netzbetreibername im Dokument |
| `pruefen` | Werte (teilweise) gelesen, aber auffällig oder unvollständig: Plausibilität, Name fehlt, SLP oder RLM fehlt, mehrere abweichende Preisblätter, mehrere Netzbetreiber auf einer Website. Werte nur nach Prüfung verwenden |
| `kein_preisblatt` | Website erreichbar, aber kein passendes Preisblatt des Jahres gefunden bzw. nicht auslesbar |
| `blockiert` | Website nicht erreichbar, Sperrseite oder Zeitüberschreitung |
| `robots` | Startseite oder Preisblatt-Pfade per robots.txt gesperrt |
| `keine_website` | keine Website im MaStR und nicht ableitbar |

Plausibilitätsregeln: NS LP ab 2.500 h 40–260 €/kW/a, LP unter < LP ab, AP unter > AP ab
(gilt auch für MS/NS), SLP-AP 3–15 ct/kWh, SLP-Grundpreis 0–200 €/Jahr.

# Weitere Dateien in ergebnis/

| Datei | Inhalt |
|---|---|
| `restliste.csv` | alle Zeilen mit status ≠ ok: `nr; netzbetreiber; mastr_nr; website; status; grund; kandidaten; quelle_url` (`kandidaten` = geprüfte Dokumente mit Ergebnis) |
| `zusammenfassung.md` | Anzahl je Status, Spannen SLP-AP, NS ct/kWh bei 4.000 h und NS LP, Datenherkunft, Restfälle |
| `netzbetreiber.csv` | Liste aus dem MaStR inkl. Website-Quelle, Sitz, Netzgebiet |
| `plz_netzbetreiber.csv` | PLZ → Netzbetreiber für den Rechner: `plz; mastr_nr; netzbetreiber; anteil_prozent; einheiten`. Mehrere Zeilen je PLZ, wenn sie in mehreren Netzgebieten liegt; `anteil_prozent` = Anteil der MaStR-Einheiten dieser PLZ beim Netzbetreiber (unter 2 % ausgelassen) |
| `mastr_rollen.txt` | Marktrollen und -funktionen im MaStR mit Anzahl, zur Kontrolle des Filters |
| `fortschritt.jsonl` | Bearbeitungsstand je Netzbetreiber (für den Neustart) |
| `pdf/` | verwendete Preisblätter `<nr>_<name>.pdf`, separates SLP-Blatt als `<nr>_<name>_slp.pdf` |
