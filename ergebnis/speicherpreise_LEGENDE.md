# Speicherpreise: Funde (`ergebnis/speicherpreise_funde.csv`)

Gesammelt von `vnb/speicherpreise.py` (Workflow „Speicherpreise sammeln“). Jede Zeile ist **eine Preisangabe in €/kWh auf einer Webseite**, kein geprüfter Wert.

| Spalte | Bedeutung |
|---|---|
| id | Kurzkennung (Hash aus Adresse, Preis, Kontext) |
| abruf_datum | Tag des Abrufs |
| url, domain, titel | Fundstelle |
| art_quelle | Fachmagazin, Studie/Verband, Händler/Anbieter, Ratgeber oder unklar (aus Domain und Seitentext) |
| preis_von/bis_eur_kwh | Preis oder Spanne, wie angegeben |
| netto_brutto | nur wenn im Umfeld „netto“ oder „brutto“ bzw. „zzgl./inkl. MwSt.“ steht, sonst unklar |
| kapazitaet_kwh | nächstgenannte Kapazität im Umfeld, sonst leer |
| umfang | nur Hardware, schlüsselfertig oder unklar |
| segment | Heim, Gewerbe/Industrie oder unklar |
| veroeffentlicht | Datum aus den Metadaten der Seite, sonst leer |
| kontext | Textauszug um die Angabe (etwa 340 Zeichen) |
| status | **ungeprüft** bis jemand die Angabe am Original gelesen hat, dann **geprüft** oder **verworfen** |
| pruefnotiz | Anmerkung der Prüfung |

Regeln: nichts wird geschätzt; Preise unter 80 oder über 1.800 €/kWh werden ausgeschlossen (Strompreise, Ausreißer); robots.txt wird beachtet, höchstens 1 Anfrage pro Sekunde je Domain. In den Rechner gehen nur Funde mit Status **geprüft**.

---

# Produkttabelle (`ergebnis/speicherprodukte.csv`)

Eine Zeile je Speichersystem, nach dem Muster der pv-magazine-Marktübersicht. Erzeugt mit `python -m vnb.speicherprodukte <datei>` aus eingefügten Tabellenzeilen (Tabulator-getrennt: Hersteller, Produkt, Zellchemie, kWh, kW, Wirkungsgrad, Zyklen, Preis, Fläche, Volumen). Was die Quelle nicht angibt, bleibt leer.

| Spalte | Bedeutung |
|---|---|
| id | Kurzkennung (Hersteller, Produkt, Kapazität, Quelle) |
| hersteller, produkt, zellchemie | wie in der Quelle (LFP, NMC …) |
| kapazitaet_kwh, leistung_kw | Nennkapazität und Leistung |
| wirkungsgrad_prozent, zyklen | Herstellerangabe |
| preis_eur_kwh | Preis so, wie die Quelle ihn nennt |
| preis_netto_brutto, preis_umfang | **unklar**, bis die Kopfzeile der Quelle oder das Original es sagt (nur Hardware oder schlüsselfertig) |
| flaeche_m2, volumen_m3 | Platzbedarf |
| datenblatt_url | Hinweis auf das Datenblatt, sobald die Quelle eines verlinkt |
| quelle, quelle_url, abruf_datum | Herkunft der Zeile |
| status | ungeprüft, geprüft, verworfen |
| pruefnotiz | Anmerkung der Prüfung |

Die Funde-Tabelle (`speicherpreise_funde.csv`) hält Preis-Aussagen von Webseiten fest. Die Produkttabelle hält Systeme mit technischen Daten fest. Beide ergänzen sich: Der Rechner soll später aus der Produkttabelle wählen können (Kapazität, Leistung, Zyklen, Wirkungsgrad), mit Preis und Quelle daneben.
