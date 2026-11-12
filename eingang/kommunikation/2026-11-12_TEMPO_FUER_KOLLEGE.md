# So wirst du schneller (Auftrag 7, die 116 "ablesen")

Dein Tempo ist das Problem, nicht die Sorgfalt. Du musst weniger tippen und weniger suchen. Neu in `main`:

```bash
git pull origin main
PYTHONPATH=. python daten/hlzf_entwurf.py     # erzeugt lauf/hlzf_entwurf_auftrag7.csv und lauf/seiten/*.png
```

Pro Fall liegt dann bereit:
1. **Entwurf** der Maschine (Spalten `ns_…`, `msns_…`, wo sie etwas lesen konnte; 50 von 116 haben eine Teillesung). **Ungeprüft.** Du vergleichst nur mit dem Bild und korrigierst.
2. **Die Zeilen mit Zeiten aus dem Text** (`zeitzeilen_im_text`): du musst die Seite nicht suchen.
3. **Seitenbilder** (`lauf/seiten/<mastr_nr>_s-1.png` …): das Bild direkt öffnen, nicht das PDF.

Arbeitsweise:
- **Stapel von 10:** erst alle 10 Bilder öffnen und abtippen, dann einmal prüfen (`daten/hlzf_lieferung_pruefen.py`), dann pushen. Nicht jede Zeile einzeln committen.
- **Gleiche Layouts zusammen:** Dokumente desselben Software-Anbieters (GIPS-Portal, "Zeile je Fenster", Raster) sehen gleich aus. Wer eines gelesen hat, liest die nächsten in zwei Minuten.
- **Zuerst die leichten:** Fälle mit Teillesung, dann die mit Zeitzeilen, zuletzt Raster-Bilder.
- **Nicht lesbar nach 3 Minuten:** leer lassen, `bemerkung = unklar: <Grund>`, weiter. Zurückkommen kostet weniger als Festbeißen.
- **Suchen (132):** Reihenfolge: erst der Suchlink, dann `<Domain>/netzentgelte`, dann das GIPS- und enwg-Portal. Nach 5 Minuten ohne Treffer: `nicht_gefunden` mit den geprüften Adressen. Findest du ein 2027- **oder** 2026-Dokument, reicht es.
- **Nichts doppelt:** Die 20 schon gelieferten Zeilen und die 10 von uns verifizierten nicht erneut lesen. Offen sind 6 deiner Zeilen: Selb-Marktredwitz, Schwerin, Guben, MITNETZ, Remscheid, Villingen-Schwenningen (Zeiten stehen nicht im PDF-Text). Bitte pro Zeile die Stelle im Dokument nennen (Seite, Zelle).
