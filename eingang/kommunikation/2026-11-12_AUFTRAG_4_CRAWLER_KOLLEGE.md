# Auftrag 4 an den Kollegen: Crawler benutzen (12.11.2026)

Du kannst den Crawler selbst laufen lassen. Anleitung: `2026-11-12_ANLEITUNG_KOLLEGE_CRAWLER.md`. Bitte `git pull origin main` vorher.

**Liste:** `lauf/hlzf_kollege_crawl_liste.csv` (36 Netzbetreiber, MaStR-Nr. zuerst). Das sind die, bei denen mein Lauf nichts oder nur alte Jahre gefunden hat (kein Treffer, nur ältere Jahre, nicht erreichbar, auf Anfrage). Dort ist dein Auge am meisten wert.

Ablauf je Netzbetreiber:
1. Crawler laufen lassen: `python -m vnb.hlzf_crawl --liste lauf/hlzf_kollege_crawl_liste.csv --ausgabe lauf/hlzf_crawl_kollege.csv --parallel 4`
2. Gefundenes lesen und eintragen (2027 zuerst, Regeln aus der Anleitung).
3. Bei `kein_treffer`: die Website selbst durchsehen (Menü Netz, Veröffentlichungen, Downloads, Marktpartner, Preisblätter; auch Dokumente mit "Regelungen", "Netzzugang", "Preisblatt" im Namen, die den Abschnitt enthalten können) und mir die Adresse der Seite oder des Dokuments nennen, auch wenn du nichts findest. Daraus lerne ich, wo der Crawler vorbeiläuft.
4. Gesperrtes (403, robots) nicht laden, sondern melden.

**Zusätzlich** (Auftrag 3, falls noch nicht erledigt): die 44 Crawler-Funde in `2026-11-12_AUFTRAG_3_CRAWL_FUNDE_44.csv` lesen.

Abgabe: CSV mit MaStR-Nr. zuerst, im Format der Etappen, dazu eine kurze Statusmeldung mit einer Zeile je Netzbetreiber.
