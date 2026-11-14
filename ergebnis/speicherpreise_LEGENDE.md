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
