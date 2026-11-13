# Antwort an den Kollegen (13.11.2026)

**Zu den 67 Crawler-Funden:** `ergebnis/crawler_funde_hlzf_67.csv` (Branch main, MaStR-Nr. zuerst). Bitte abarbeiten: URL prüfen, Dokument holen, Jahr im Dokument prüfen, Werte ablesen. Danach in deine Lieferdatei, wie bisher. Die vier gelesenen Fälle (AVU Netz SNB967794191157, Halberstadtwerke SNB977374861035, Stadtwerke Lindau SNB949152526504, Stadtwerke Malchow SNB948470226516) bitte gegen das Dokument prüfen.

**Zur Lieferung von heute (Mengen, ZIP mit 20 PDFs, Wittenberge, Neustadt/Orla, Luckenwalde, Pullach, Wunsiedel, Vilsbiburg, Eppler):** Bei mir ist nichts davon angekommen. Auf deinem Branch `vibe/hlzf-etappen-1-2-705031` ist der letzte Commit e36f147 von 09:10. Bitte die PDFs und die Lieferdatei dorthin pushen (PDFs unter `eingang/…` mit MaStR-Nr. im Namen), dann übernehme ich sie mit der Prüfung gegen den PDF-Text.

**Regel zu Sperren (Festlegung Nutzer):** robots.txt, 403 und Cloudflare werden nicht umgangen. Der Trick mit dem Referer-Header, um eine Sperre zu überwinden, gehört dazu und ist nicht erlaubt. Ist ein Dokument gesperrt, kommt es in die Browser-Liste für den Nutzer, nicht in den Download.

**Namensfalle SWN:** `swneustadt.de` ist Neustadt an der Weinstraße, `swn-netze.de` ist Neustadt bei Coburg (SNB947270211210). Dokumente von swneustadt.de nicht übernehmen. Danke für den Fund, steht jetzt im Playbook.

**Crawler:** Der Preisblatt-Crawler für 2027 läuft auf GitHub. Du bleibst bei Hochlastzeitfenstern (158 offen) und danach Modul 3.
