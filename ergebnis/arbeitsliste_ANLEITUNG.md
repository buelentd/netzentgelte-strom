# Arbeitsliste: eine Datei für alle

Datei `arbeitsliste.csv` (Trennzeichen `;`, UTF-8). Eine Zeile je Netzbetreiber, bei dem noch etwas fehlt. Sortiert nach Dringlichkeit (Spalte `prioritaet`, höher = mehr fehlt).

## Spalten
- `es_fehlt`: was fehlt (SLP, NS, MS/NS, MS, Hochlastzeitfenster)
- `preise_wer` / `preise_aktion`: wer sich um die Preise kümmert und was zu tun ist
- `hlzf_wer` / `hlzf_aktion` / `hlzf_status`: dasselbe für das Hochlastzeitfenster
- `suche_preisblatt`, `suche_hochlastzeitfenster`: fertige Suchbegriffe (`site:domain` ohne www)
- `dateiname_preisblatt`, `dateiname_hochlastzeitfenster`: so speichern

## Wer macht was
| wer | Aufgabe |
|---|---|
| **Kollege** | Dokument suchen und herunterladen. Gleich nach dem Download mit `dokument_pruefen.py` prüfen. Nur OK oder PRUEFEN ablegen, FALSCH nicht. |
| **Nutzer (Browser)** | Seiten, die uns sperren (403, Cloudflare, robots), im Browser öffnen und die Datei speichern. Keine Umgehung, kein Web-Reader. |
| **Claude** | Dokument liegt vor, der Leser muss es lesen. Hier ist nichts zu liefern. |

## Regeln
- Nur das Dokument für **2026**, nur **Strom**. Endgültig vor vorläufig. Kein 2027.
- Nichts schätzen. Findet man nichts, kurz in einer Statusdatei notieren (nr; gefunden ja/nein; URL; Bemerkung).
- Jina nur bei verschlüsselten PDFs, die man selbst heruntergeladen hat, und in der Statusliste mit `geprueft_mit` vermerken.

## Ablage
- Alle Dateien **flach** in `eingang/pdfs_neu/` (keine Unterordner nötig).
- Hochlastzeitfenster: `SNB…_NNNN_hlzf.pdf` (auch `.xls`, `.xlsx`, `.html`). Mehrere Teile: `…_hlzf_MS.pdf`, `…_hlzf_NS.pdf`.
- Preisblätter: `SNB…_NNNN.pdf` (auch `.xlsx`, `.html`).
- Danach: Commit, Sync, „synched“ an Claude. Claude liest ein und meldet die neue Zahl.
- Geht der Push nicht: auf github.com im Ordner `eingang/pdfs_neu` über „Add file, Upload files“ (bis 100 Dateien je Upload).
