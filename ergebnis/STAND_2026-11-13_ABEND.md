# Stand 13.11.2026, Abend (Fortsetzung morgen)

## Zahlen 2027 (vorläufige Preise), beide Quellen zusammen (Crawler + eigene Tabelle), 831 Netzbetreiber
| Was | Anzahl |
|---|---:|
| Niederspannung RLM komplett (4 Preise) | 611 |
| SLP (Arbeitspreis + Grundpreis) | 500 |
| Umspannung MS/NS komplett | 497 |
| Mindestens SLP oder Niederspannung | 643 |
| Status ok bzw. gelesen | 480 |

Crawler (`ergebnis_2027/netzentgelte_2027.csv`): ok 423, pruefen 210, kein_preisblatt 162, blockiert 25, robots 10, keine_website 1.
Eigene Tabelle (`ergebnis/netzentgelte_2027_vorlaeufig.csv`): gelesen 145, teilweise 60, pruefen 3, Rest ohne Blatt.

Hochlastzeitfenster: fertig 637 von 831, davon nur 35 mit einem 2027-Dokument (602 beruhen auf 2026). Modul 3: 231 Zeilen für 215 Netzbetreiber gelesen, 541 Zeilen für 504 offen. Zahlen für 2026 unverändert: 788 ok.

## Heute gebaut (alles auf main)
- **Paralleler Lauf:** `.github/workflows/netzentgelte_parallel.yml`, 8 Teilläufe (`run.py --shard K/8`, Aufteilung nach Website-Domain), einmalige Suche, Zusammenführen und Commit. Start über `lauf/parallel.env`. Läuft für ~200 Netzbetreiber in 10–15 Minuten. Zwischenstände während des Laufs: `.github/zwischenstand.sh`.
- **Crawler (Preisblätter 2027):** Start-URLs aus der 2026-Quelle (Host, Verzeichnis); `<base href>` wird beachtet (ovag); Adressen mit nur älteren Jahren werden nicht geladen; erfundene Upload-Ordner des Zieljahres entfernt; Brave-Suchtreffer auch für 2027; XML-Sitemaps inkl. Sitemap-Index; harter Prozess-Abschluss (`os._exit`, Lauf hing sonst); Referenzpreisblätter (§ 18) werden übergangen.
- **Nutzerhinweise:** `lauf/nutzer_hinweise.csv` und `lauf/hinweis_urls_2027.csv` (SachsenNetze, ovag, EWR Remscheid, Max Peissker, Ludwigsfelde). Regel in CLAUDE.md und Playbook: Hinweise sofort speichern.
- **Fallback Butzbach <- ovag:** `ergebnis/hlzf_fallback.csv` (getrennt von den Primärdaten, Herkunft und Konfidenz).
- **Quellenregister:** `ergebnis/quellenregister.csv` (1.777 Zeilen, 597 nur mit lokalem Pfad).
- **Listen für den Kollegen:** `ergebnis/kollege_hlzf_2027_suchen_400.csv` (400 mit HLZF 2026, 2027 wird gesucht), `ergebnis/kollege_hlzf_offen_aktuell.csv` (194 offene HLZF), Modul 3: `ergebnis/modul3_offen_kollege_sortiert.csv`.
- **API und Server:** REST-API v1 mit Swagger (`/docs`), `ergebnis/conplot/openapi.json`; `Dockerfile`, `deploy/docker-compose.plesk.yml` und README für den Plesk-Server.
- **Quellenkunde:** Namensfalle SWN (`swneustadt.de` = Weinstraße, `swn-netze.de` = Coburg), Referenzpreisblätter als falsche Dokumente, Vilsbiburg-Link mit Leerzeichen.

## Läuft noch
Diagnose-Lauf für die 214 `pruefen` (Workflow „Netzentgelte Strom“, gestartet 18:04, fertig ca. 18:32). Er schreibt die Textauszüge der geladenen Dokumente auf den Branch `diagnose`. Der erste Lauf hatte keine Texte geliefert, weil der Diagnose-Schritt ohne `--jahr` den leeren 2026-Cache las. Behoben in `b7f5a101`.

## Morgen
1. **Die 210 `pruefen` abarbeiten:** Texte auf `diagnose` lesen, nach Ursache gruppieren (falsches Dokument, SLP-Blatt fehlt, Staffelpreise, Layout, Zuordnung), je Ursache beheben, offline neu auslesen, `ok` vergleichen.
   - Befund an 46 lokalen Dokumenten: 41 haben gar keinen SLP-Abschnitt (falsches oder anderes Preisblatt: Preisblatt 1 nur RLM, Hochlastzeitfenster, Reservekapazität, Zuschuss Übertragungsnetz); 5 haben Staffelpreise nach Jahresverbrauch (MEGA Monheim).
   - Crawler-Regel: Hat ein Netzbetreiber RLM, aber kein SLP, gezielt nach „ohne Leistungsmessung“, „Standardlastprofil“, „Preisblatt 2“ suchen. Dokumente für Hochlastzeitfenster, Reserve und Zuschuss nicht als Preisblatt zählen.
2. **Entscheidung (Nutzer):** Staffelpreise (SLP nach Jahresverbrauch) in eigene Datei `slp_staffeln_2027.csv`, Hauptspalten leer, Kennzeichen „Staffel“. Der Rechner muss später darauf umgestellt werden.
3. **Kollege:** ZIP `hlzf_quellen_etappe_7.zip` (22 Dateien) fehlt bei uns, 39 Zeilen warten darauf (nach Ablage unter `eingang/` übernehmen). Liste der 400 für das 2027-Dokument. Modul 3: 504 Netzbetreiber offen.
4. **Browser (Nutzer):** 162 `kein_preisblatt`, 25 `blockiert`, 10 `robots` (Namenssuche, die größten zuerst); ovag-PDF hochladen (Reader-Fehler dort); Auftrag 8 (571 Preisblätter).
5. **Server (Nutzer):** Auf `82.165.123.132` (Plesk, Ubuntu 20.04) ist Docker 28.1.1 installiert. Noch zu tun: Repo klonen (öffentlich, ohne Token), `deploy/docker-compose.plesk.yml` starten, in Plesk `api.intersignum.de` mit Reverse Proxy auf Port 8000 und Let's-Encrypt, DNS-Eintrag auf diese IP prüfen (stand zuerst auf 76.76.21.21). Der Dienst `openvpn@client` fragt dauernd nach Zugangsdaten; nur anfassen, wenn der Admin zustimmt.
6. **Offen aus früheren Tagen:** Zeitstempel = Ende Messperiode (15 Minuten verschieben?); Conplot-Importer ohne Modul 3, 2027 und Konzessionsabgabe; Fallback Butzbach noch nicht in der API; 38 `pruefen` und zwei Ausreißer bei 2026.

## Regeln und Lerneffekte (bleiben)
- Sperren (403, robots.txt, Cloudflare) werden nicht umgangen, auch nicht mit Referer oder angepasstem User-Agent. Gesperrtes kommt in die Browser-Liste.
- Nichts schätzen: Staffelpreise, unklare Zuordnung und fremde Dokumente nicht raten.
- Suchlinks nach Name, nicht nach `site:Domain`.
- Das Repo ist öffentlich: Actions kostenlos, Artefakte und Logs sichtbar, nur veröffentlichte Daten committen.
