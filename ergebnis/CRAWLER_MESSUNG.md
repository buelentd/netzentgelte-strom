# Crawler-Messung (Hochlastzeitfenster 2026): wird er besser?

Damit es nachprüfbar bleibt, werden alle Versionen an denselben Mengen gemessen. Stand 12.11.2026.

## Menge A: 9 Netzbetreiber, deren Dokument wir kennen (Mainzer, Bad Honnef, Arneburg, e-netz Südhessen, Lingen, Burgdorf, Bielefeld, Avacon, Westnetz)
Gesperrt (nicht umgangen): Avacon, Westnetz. Messgröße: gefundene von 7 erreichbaren.

| Version | Fund 2026 von 7 |
|---|---|
| v1 (Links ab Schwelle 3, alle PDFs laden, Download ohne Proxy) | 1 |
| v2 (Schwelle 1, Dokumente nur mit HLZF-Hinweis, Proxy) | 7 |
| v3 (+ eingeklappte HTML-Bereiche, Umfeldtext der Links, Seitensuche, Einstiegspfade, Schwesterdomains) | 7 (Regressionstest) |

## Menge B: 41 Netzbetreiber, bei denen der einfache Crawler nichts fand (`ergebnis/HLZF_KEIN_TREFFER.md`)
| Version | Fund 2026 |
|---|---|
| einfacher Crawler (urllib, ohne Browser) | 0 |
| v2 | 3 |
| v3 (läuft, 35 von 38 durch) | bisher 1 weiterer |

Die Menge B ist die Messlatte. Wird v3 nicht deutlich besser, fehlen echte Beispieladressen von den Netzbetreibern, bei denen der Crawler scheitert.

## Regel
Jede Änderung am Crawler wird erst an Menge A (Regression) und dann an Menge B gemessen und hier eingetragen.
