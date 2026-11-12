# Status an den Kollegen — 12.11.2026 (Branch vibe/hlzf-etappen-1-2-705031, PR #1)

## Was geschafft ist

**2027-vorläufig Dokumente in `eingang/2027_vorlaeufig/`:** ca. 156 Preisblätter 2027-vorläufig + ca. 124 HLZF-2027, alle inhaltsgeprüft (2027 + Strom + Preisblatt/HLZF im Text; Gas/WVN/§14a/falsches Jahr verworfen).

Quellen der Dokumente:
- Mein Sitemap-/Domain-Crawler: 99 valide Dokumente
- Chromium-Crawler `vnb.hlzf_crawl` (main): Lauf über 508 offene MaStR-Nr. komplett — 38 gefunden_2026, 5 nur_2027, 116 blockiert (403, dokumentiert, nicht umgangen), 220 kein_treffer, 113 nicht_erreichbar; daraus 39 valide 2027-Dokumente abgelegt
- Kollegen-Crawl von `main` (`eingang/pdfs_neu/`): 54 Dokumente übernommen
- **Nutzer-Uploads: 20 Netzbetreiber, 30 PDFs** (manuell geprüft, robots/403 nicht umgangen — bei 403 nur als Upload, nie umgangen): Albwerk, ASCANETZ, Bad Honnef, Avacon, Bayernwerk, Creos, EKS Schaffhausen, ELE Verteilnetz, EVK Lohr-Karlstadt, ESTW Erlangen, EZV Untermain, EWR Netze Lichtenstein, Ebersdorf, Freiberger, Frammersbach, Garmisch-Partenkirchen, Steinhagen, Wendelstein, EG Wittmund, EWR Rheine, ENB Germering u. a.

**HLZF-2027-Zeilen gelesen:** `ergebnis/hlzf/hlzf_2027_gelesen.csv` — bisher 8 Zeilen (ESM Selb, NGS Schwerin, EnergieSüdwest, EV Alzenau, EV Guben, SW Wernigerode, SW Staßfurt, Halberstadtwerke), Text+Bild gegengeprüft, jahr=2027 + „vorläufig". Rest der 91 offenen Dokumente (lauf/hlzf_2027_offen.csv auf main) folgt in Stapeln.

**Listen für die manuelle Prüfung (Browser durch den Nutzer):**
- `2026-11-12_BLOCKIERT_40_TABELLE.md` (40× 403) und `2026-11-12_BLOCKIERT_MANUELL_PRUEFEN.csv` (92 Fälle inkl. nicht_erreichbar/robots/anfrage)

## Regeln (unverändert eingehalten)
Ehrlicher UA, robots.txt respektiert, max. 1 Req/s pro Domain, kein Headless-/WAF-Bypass — 403/robots werden als „blockiert“ dokumentiert. Nichts raten: unklare Dokumente bleiben leer mit Bemerkung.
