#!/usr/bin/env python3
"""Netzentgelte Strom (RLM, Jahresleistungspreissystem) aller Verteilnetzbetreiber erfassen.

  python run.py liste   [--csv mastr_export.csv]   Netzbetreiber-Liste (open-mastr) + Pilot-Abgleich
  python run.py lauf    [--worker 4] [--limit N]   Preisblätter suchen und auslesen (fortsetzbar)
  python run.py bericht                            CSV, Restliste und Zusammenfassung neu schreiben
  python run.py alles                              liste (falls nötig) + lauf + bericht

Details: CLAUDE.md und README.md.
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import os
import re
import shutil
import sys
import time
from collections import defaultdict
from pathlib import Path

from vnb import liste as liste_mod
from vnb import pilot as pilot_mod
from vnb.crawl import Auftrag, Crawler, Fund, hinweise_laden, lokale_preisblaetter_laden, website_domain
from vnb.ergebnis import Speicher
from vnb.extract import FELDER, name_tokens, norm, plausibel
from vnb.netz import USER_AGENT, Drossel, Robots, basis_domain

HIER = Path(__file__).resolve().parent
# Zusätzliche Kennungen von Netzgebieten (Pilot-Sonderfälle)
GEBIET_KENNUNG = {
    "bremerhaven": ("bremerhaven", "/bhv/", "_bhv_", "brhv"),
    "hs.hd": ("ostsachsen", "hs.hd", "hshd", "hs-hd"),
}


class Log:
    def __init__(self, pfad: Path):
        self.f = open(pfad, "a", encoding="utf-8")

    def __call__(self, *teile):
        s = " ".join(str(t) for t in teile)
        print(s, flush=True)
        self.f.write(s + "\n")
        self.f.flush()


# ---------------------------------------------------------------- Schritt 1: Liste

def schritt_liste(args, log):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if args.csv:
        eintraege = liste_mod.aus_csv(Path(args.csv))
        log(f"{len(eintraege)} Netzbetreiber aus {args.csv}")
    else:
        eintraege = liste_mod.aus_mastr(out / "netzbetreiber.csv", HIER / "mastr", args.rolle_regex or "",
                                        gebiete=not args.ohne_gebiete, log=log)
        log(f"{len(eintraege)} Verteilnetzbetreiber Strom aus dem MaStR (Details: {out / 'mastr_rollen.txt'})")
    pilot = pilot_mod.lesen(HIER / "pilot_50_vnb_2026.csv")
    benutzt = set()
    geordnet = []
    for p in pilot:
        e = pilot_mod.zuordnen(p, [x for x in eintraege if x["mastr_nr"] not in benutzt])
        if e:
            benutzt.add(e["mastr_nr"])
            zeile = dict(e)
        else:
            log(f"  Pilot {p['nr']} {p['netzbetreiber']}: kein MaStR-Treffer, wird ohne MaStR-Nr. geführt")
            zeile = {"netzbetreiber": p["netzbetreiber"], "mastr_nr": "", "website_quelle": "Pilot"}
        zeile["website"] = pilot_mod.website(p, e)
        zeile["pilot_nr"] = p["nr"]
        geordnet.append(zeile)
    rest = sorted((e for e in eintraege if e["mastr_nr"] not in benutzt), key=lambda e: norm(e["netzbetreiber"]))
    geordnet += rest
    for i, e in enumerate(geordnet, 1):
        e["nr"] = i
    liste_mod.schreiben(geordnet, out / "netzbetreiber.csv")
    ohne = sum(1 for e in geordnet if not e.get("website"))
    log(f"Liste geschrieben: {out / 'netzbetreiber.csv'} ({len(geordnet)} Einträge, {ohne} ohne Website)")


# ---------------------------------------------------------------- Schritt 2/3: Lauf

def geschwister(eintraege: list[dict]) -> dict[str, tuple[tuple, tuple, bool]]:
    """Netzbetreiber mit derselben Website: Kennungen, an denen ihr Preisblatt zu erkennen ist."""
    gruppen = defaultdict(list)
    for e in eintraege:
        if e.get("website"):
            w = e["website"] if "://" in e["website"] else "https://" + e["website"]
            gruppen[basis_domain(w)].append(e)
    out = {}
    for g in gruppen.values():
        if len(g) < 2:
            continue
        toks = {e["nr"]: set(name_tokens(e["netzbetreiber"])) for e in g}
        for e in g:
            andere = set().union(*(toks[x["nr"]] for x in g if x is not e))
            eigen = toks[e["nr"]] - andere
            pflicht = set(eigen)
            for kennung, varianten in GEBIET_KENNUNG.items():
                if kennung in norm(e["netzbetreiber"]):
                    pflicht |= set(varianten)
            ausschluss = set()
            for x in g:
                if x is e:
                    continue
                ausschluss |= toks[x["nr"]] - toks[e["nr"]]
                for kennung, varianten in GEBIET_KENNUNG.items():
                    if kennung in norm(x["netzbetreiber"]) and kennung not in norm(e["netzbetreiber"]):
                        ausschluss |= set(varianten)
            out[str(e["nr"])] = (tuple(sorted(pflicht)), tuple(sorted(ausschluss)), not pflicht)
    return out


def key_von(e: dict) -> str:
    return f"mastr:{e['mastr_nr']}" if e.get("mastr_nr") else f"nr:{e['nr']}"


def basis_satz(e: dict) -> dict:
    return {"key": key_von(e), "nr": int(e["nr"]), "netzbetreiber": e["netzbetreiber"],
            "mastr_nr": e.get("mastr_nr", ""), "website": e.get("website", ""),
            "bundesland": e.get("bundesland", ""), "region": e.get("region", ""), "netztyp": e.get("netztyp", ""),
            "gebiet_quelle": e.get("gebiet_quelle", ""), "status": "",
            "ns": {}, "msns": {}, "slp": {}, "rlm_ok": False, "slp_ok": False, "grenze_le": False,
            "preisstand": "", "stand_datum": "", "hinweis": "", "quelle_url": "",
            "grund": "", "kandidaten": [], "datei": ""}


def datei_ablegen(k, satz: dict, out: Path, zusatz: str = ""):
    if k is None or not k.datei or not Path(k.datei).exists():
        return
    slug = re.sub(r"[^a-z0-9]+", "_", norm(satz["netzbetreiber"]))[:50].strip("_")
    ziel = out / "pdf" / f"{satz['nr']:04d}_{slug}{zusatz}{Path(k.datei).suffix}"
    shutil.copyfile(k.datei, ziel)
    satz["datei"] = ", ".join(filter(None, [satz.get("datei", ""), str(ziel.relative_to(out))]))


def rlm_setzen(satz: dict, k, hinweise: list, out: Path):
    msns_ok = not plausibel(k.msns, "MS/NS")
    satz["ns"], satz["msns"] = k.ns, (k.msns if msns_ok else {})
    if k.msns and not msns_ok:
        hinweise.append("MS/NS-Werte unplausibel, nicht übernommen")
    satz["preisstand"], satz["stand_datum"], satz["grenze_le"] = k.preisstand, k.stand_datum, k.grenze_le
    satz["quelle_url"] = k.url
    satz["rlm_ok"] = not k.pruefen
    hinweise += k.hinweise + k.pruefen
    datei_ablegen(k, satz, out)


def slp_setzen(satz: dict, s, hinweise: list, out: Path):
    """SLP-Werte übernehmen; aus anderem Dokument → beide Quellen in quelle_url."""
    if s is None or not s.slp_verwendbar:
        return
    satz["slp"] = s.slp
    satz["slp_ok"] = s.slp_ok
    hinweise += s.slp_hinweise + s.slp_pruefen
    if s.name_fehlt:
        hinweise.append("Netzbetreibername nicht im SLP-Dokument")
    if not satz["quelle_url"]:
        satz["quelle_url"] = s.url
        satz["preisstand"], satz["stand_datum"] = s.preisstand, s.stand_datum
        datei_ablegen(s, satz, out)
    elif s.url != satz["quelle_url"] and not satz["quelle_url"].startswith("RLM:"):
        satz["quelle_url"] = f"RLM: {satz['quelle_url']} | SLP: {s.url}"
        if s.preisstand != satz["preisstand"]:
            hinweise.append(f"SLP-Preisblatt {s.preisstand}")
        datei_ablegen(s, satz, out, "_slp")


def fund_uebernehmen(satz: dict, fund: Fund, out: Path, extra_hinweise=()):
    satz["status"] = fund.status
    satz["grund"] = fund.grund
    satz["kandidaten"] = fund.kandidaten
    hinweise = list(extra_hinweise)
    if fund.kandidat:
        rlm_setzen(satz, fund.kandidat, hinweise, out)
    slp_setzen(satz, fund.slp_kandidat, hinweise, out)
    satz["hinweis"] = "; ".join(dict.fromkeys(h for h in hinweise if h))


def status_abschliessen(satz: dict):
    """ok nur, wenn RLM und SLP unauffällig sind; sonst pruefen (sofern Werte vorhanden)."""
    if satz["status"] not in ("ok", "pruefen"):
        return
    fehlt = []
    if not satz["rlm_ok"]:
        fehlt.append("RLM-Werte auffällig oder fehlend" if satz["ns"] else "RLM-Werte nicht gefunden")
    if not satz["slp_ok"]:
        fehlt.append("SLP-Werte auffällig" if satz["slp"] else "SLP-Werte nicht gefunden")
    if fehlt:
        satz["status"] = "pruefen"
        satz["grund"] = "; ".join(dict.fromkeys(filter(None, [satz["grund"], *fehlt])))
    else:
        satz["status"] = "ok"


def gleich(a: dict, b: dict) -> bool:
    return all(a.get(f) is not None and b.get(f) is not None and abs(a[f] - b[f]) < 0.006 for f in FELDER)


async def pilot_bearbeiten(crawler: Crawler, req, e: dict, p: dict, a: Auftrag, out: Path, log) -> dict:
    satz = basis_satz(e)
    ns_pilot = {f: p[f"ns_{f}"] for f in FELDER}
    satz.update(status="ok", ns=ns_pilot, rlm_ok=True, preisstand=p["preisstand"], quelle_url=p["quelle"])
    hinweise = ["Pilot (geprüft)"] + ([p["hinweis"]] if p.get("hinweis") else [])

    # Quelle erneut auslesen: MS/NS und SLP ergänzen, NS gegenprüfen
    k = await crawler.dokument_pruefen(req, p["quelle"], a)
    if k.verwendbar:
        abw = [f"{f} {k.ns.get(f, 0):.2f} statt {ns_pilot[f]:.2f}" for f in FELDER
               if k.ns.get(f) is None or abs(k.ns[f] - ns_pilot[f]) >= 0.006]
        satz["pilot_abgleich"] = "gleich" if not abw else "abweichend: " + ", ".join(abw)
    else:
        satz["pilot_abgleich"] = f"nicht gelesen ({k.grund[:80]})"
    if k.verwendbar and gleich(k.ns, ns_pilot):
        if k.msns and not plausibel(k.msns, "MS/NS"):
            satz["msns"] = k.msns
        else:
            hinweise.append("MS/NS in der Quelle nicht eindeutig gefunden")
        satz["stand_datum"], satz["grenze_le"] = k.stand_datum, k.grenze_le
        if p["preisstand"] == "unklar" and k.preisstand != "unklar":
            hinweise.append(f"Preisstand laut Dokument: {k.preisstand}")
        slp_setzen(satz, k, hinweise, out)
    elif k.verwendbar:
        hinweise.append("Neuauslesung der Quelle weicht vom Pilot ab, MS/NS und SLP nicht übernommen")
    elif k.slp_verwendbar:
        slp_setzen(satz, k, hinweise, out)
        hinweise.append(f"RLM in der Quelle nicht erneut auslesbar ({k.grund}), MS/NS fehlt")
    else:
        hinweise.append(f"Quelle nicht erneut auslesbar ({k.grund}), MS/NS und SLP fehlen")
    datei_ablegen(k, satz, out)

    if p["preisstand"] != "endgültig":
        fund = await crawler.bearbeiten(Auftrag(**{**a.__dict__, "nur_endgueltig": True}))
        nk = fund.kandidat
        if nk and nk.preisstand == "endgültig" and nk.url != p["quelle"] and not nk.pruefen:
            log(f"  [{e['nr']}] endgültiges Preisblatt gefunden: {nk.url}")
            alt = f"ersetzt vorläufigen Pilotwert (NS LP ab 2.500 h {p['ns_lp_ueber_2500']})"
            fund_uebernehmen(satz, fund, out, ["endgültiges Preisblatt gefunden", alt])
            status_abschliessen(satz)
            return satz
        if nk and nk.preisstand == "endgültig" and nk.url != p["quelle"]:
            satz["status"] = "pruefen"
            satz["grund"] = f"endgültiges Preisblatt gefunden, aber auffällig ({'; '.join(nk.pruefen)}): " \
                            f"{nk.url}; Werte noch aus dem vorläufigen Pilot"
            hinweise.append(satz["grund"])
        else:
            hinweise.append(f"kein endgültiges Preisblatt gefunden ({fund.status}: {fund.grund[:120]})")
        satz["kandidaten"] = fund.kandidaten
        if not satz["slp_ok"] and fund.slp_kandidat and fund.slp_kandidat.slp_ok:
            slp_setzen(satz, fund.slp_kandidat, hinweise, out)

    if not satz["slp_ok"]:
        fund = await crawler.bearbeiten(Auftrag(**{**a.__dict__, "nur_slp": True}))
        if fund.slp_kandidat and fund.slp_kandidat.slp_verwendbar:
            alt = (satz["slp"], satz["slp_ok"])
            slp_setzen(satz, fund.slp_kandidat, hinweise, out)
            if alt[1] and not satz["slp_ok"]:
                satz["slp"], satz["slp_ok"] = alt[0], True
        else:
            satz["kandidaten"] = satz["kandidaten"] or fund.kandidaten
    satz["hinweis"] = "; ".join(dict.fromkeys(h for h in hinweise if h))
    status_abschliessen(satz)
    return satz


async def schritt_lauf(args, log):
    from playwright.async_api import async_playwright

    out = Path(args.out)
    (out / "pdf").mkdir(parents=True, exist_ok=True)
    cache = out / "cache"
    liste_pfad = out / "netzbetreiber.csv"
    if not liste_pfad.exists():
        sys.exit(f"{liste_pfad} fehlt, zuerst: python run.py liste")
    eintraege = liste_mod.lesen(liste_pfad)
    pilot = {p["nr"]: p for p in pilot_mod.lesen(HIER / "pilot_50_vnb_2026.csv")}
    speicher = Speicher(out)
    wiederholen = tuple(s.strip() for s in (args.wiederholen or "").replace(";", ",").split(",") if s.strip())
    gesch = geschwister(eintraege)

    offen = [e for e in eintraege if not speicher.erledigt(key_von(e), wiederholen)]
    if args.nur:
        offen = [e for e in offen if norm(args.nur) in norm(e["netzbetreiber"])]
    alle_offen = len(offen)
    if args.limit:
        offen = offen[: args.limit]
    log(f"{len(eintraege)} Einträge, {len(eintraege) - alle_offen} bereits erledigt, {alle_offen} offen"
        + (f", davon {len(offen)} in diesem Lauf (--limit {args.limit})" if len(offen) < alle_offen else ""))
    if not offen:
        return

    proxy = None
    if os.environ.get("HTTPS_PROXY") and not args.ohne_proxy:
        proxy = {"server": os.environ["HTTPS_PROXY"], "bypass": "localhost,127.0.0.1"}
    async with async_playwright() as pw:
        try:
            browser = await pw.chromium.launch(proxy=proxy)
        except Exception:
            exe = os.environ.get("CHROMIUM_PATH", "/opt/pw-browsers/chromium")
            browser = await pw.chromium.launch(executable_path=exe, proxy=proxy)
        req = await pw.request.new_context(user_agent=USER_AGENT, proxy=proxy)
        drossel = Drossel(args.abstand)
        robots = Robots(req, drossel, log)
        crawler = Crawler(browser, robots, drossel, cache, args.jahr, args.max_seiten, log)
        sem = asyncio.Semaphore(args.worker)
        hinweise = hinweise_laden(HIER / "lauf" / "hinweis_urls.csv")
        for k, v in hinweise_laden(HIER / "lauf" / "suche_treffer.csv").items():
            hinweise[k] = tuple(dict.fromkeys(hinweise.get(k, ()) + v))
        crawler.lokal = lokale_preisblaetter_laden(HIER / "lauf" / "preisblaetter.csv")
        fertig = 0
        t0 = time.time()

        async def eins(e):
            nonlocal fertig
            async with sem:
                pflicht, ausschluss, unklar_gebiet = gesch.get(str(e["nr"]), ((), (), False))
                a = Auftrag(key=key_von(e), nr=int(e["nr"]), name=e["netzbetreiber"], mastr_nr=e.get("mastr_nr", ""),
                            website=e.get("website", ""), aliase=tuple(pilot_mod.ALIASE.get(
                                pilot[e["pilot_nr"]]["netzbetreiber"], [])) if e.get("pilot_nr") else (),
                            pflicht=pflicht, ausschluss=ausschluss,
                            hinweise=hinweise.get(website_domain(e.get("website", "")), ()))
                log(f"[{e['nr']}] {e['netzbetreiber']} ({a.website or 'ohne Website'})")
                try:
                    if e.get("pilot_nr"):
                        satz = await pilot_bearbeiten(crawler, req, e, pilot[e["pilot_nr"]], a, out, log)
                    else:
                        satz = basis_satz(e)
                        fund = await crawler.bearbeiten(a)
                        extra = []
                        if e.get("website_quelle") == "aus E-Mail-Domain abgeleitet":
                            extra.append("Website aus E-Mail-Domain abgeleitet")
                        fund_uebernehmen(satz, fund, out, extra)
                        status_abschliessen(satz)
                        if satz["status"] == "ok" and unklar_gebiet:
                            satz["status"], satz["rlm_ok"], satz["slp_ok"] = "pruefen", False, False
                            satz["grund"] = "mehrere Netzbetreiber mit derselben Website, Zuordnung unklar"
                            satz["hinweis"] = "; ".join(filter(None, [satz["hinweis"], satz["grund"]]))
                        if fund.website and not satz["website"]:
                            satz["website"] = fund.website
                except Exception as ex:
                    satz = basis_satz(e)
                    satz.update(status="blockiert", grund=f"Fehler: {type(ex).__name__}: {str(ex)[:200]}")
                if satz.get("gebiet_quelle") == "Sitz laut MaStR":
                    satz["hinweis"] = "; ".join(filter(None, [satz["hinweis"], "Bundesland/Region laut Sitz (MaStR)"]))
                speicher.speichern(satz)
                fertig += 1
                ns = satz["ns"].get("lp_ueber_2500")
                log(f"[{e['nr']}] -> {satz['status']}"
                    f"{f' NS LP>2500 {ns:.2f}' if ns else ''} {satz['grund'][:150]}")
                if fertig % 10 == 0:
                    speicher.ausgeben(args.jahr)
                    rate = (time.time() - t0) / fertig
                    log(f"--- {fertig}/{len(offen)} erledigt, ca. {rate * (len(offen) - fertig) / 60:.0f} min verbleibend")

        await asyncio.gather(*(eins(e) for e in offen))
        await req.dispose()
        await browser.close()
    speicher.ausgeben(args.jahr)


def schritt_diagnose(args, log):
    """Textauszüge aller geladenen Dokumente nach diagnose/ (zur Fehlersuche am Parser)."""
    from vnb.extract import text_aus_datei

    out = Path(args.out)
    ziel = HIER / "diagnose"
    shutil.rmtree(ziel, ignore_errors=True)
    ziel.mkdir()
    saetze = Speicher(out).daten
    index = ["# Diagnose: Textauszüge der geladenen Dokumente", "",
             "| nr | Netzbetreiber | Status | Datei | URL | Ergebnis |", "|---|---|---|---|---|---|"]
    for ordner in sorted((out / "cache").glob("*")):
        satz = saetze.get(ordner.name, {})
        nr = int(satz.get("nr") or 0)
        ergebnisse = {k.split(" (", 1)[0]: k.split(" (", 1)[-1].rstrip(")") for k in satz.get("kandidaten") or []}
        for datei in sorted(ordner.iterdir()):
            if datei.suffix not in (".pdf", ".xlsx", ".xls"):
                continue
            url_datei = datei.with_suffix(".url")
            url = url_datei.read_text() if url_datei.exists() else ""
            # ok-Fälle: nur die verwendeten Quellen (hält den Branch beim vollen Lauf klein)
            if satz.get("status") == "ok" and (not url or url not in (satz.get("quelle_url") or "")):
                continue
            try:
                text = "\f\n".join(text_aus_datei(datei))
            except Exception as e:
                text = f"FEHLER beim Textauszug: {type(e).__name__}: {e}"
            name = f"{nr:04d}_{datei.stem}.txt"
            (ziel / name).write_text(f"URL: {url}\nNetzbetreiber: {satz.get('netzbetreiber', '')}\n\n{text[:400_000]}",
                                     encoding="utf-8")
            index.append(f"| {nr} | {satz.get('netzbetreiber', '')} | {satz.get('status', '')} | {name} | {url} "
                         f"| {ergebnisse.get(url, satz.get('grund', ''))[:150]} |")
    (ziel / "README.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    log(f"Diagnose: {len(index) - 4} Textauszüge in {ziel}")


def schritt_suche(args, log):
    """Preisblatt-Kandidaten für alle noch nicht fertigen Netzbetreiber über die Such-Schnittstelle."""
    from vnb.suche import suchen
    schluessel, kennung = os.environ.get("SUCHE_SCHLUESSEL", ""), os.environ.get("SUCHE_KENNUNG", "")
    if not (schluessel and kennung):
        log("Suche übersprungen: SUCHE_SCHLUESSEL / SUCHE_KENNUNG nicht gesetzt")
        return
    tabelle = Path(args.out) / f"netzentgelte_{args.jahr}.csv"
    with open(tabelle, encoding="utf-8") as f:
        zeilen = [z for z in csv.DictReader(f, delimiter=";") if z["status"] not in ("ok", "robots", "keine_website")]
    n = suchen(zeilen, schluessel, kennung, HIER / "lauf" / "suche_treffer.csv", args.jahr, args.max_abfragen, log=log)
    log(f"Suche: {n} Abfragen für {len(zeilen)} offene Netzbetreiber")


def schritt_bericht(args, log):
    text = Speicher(Path(args.out)).ausgeben(args.jahr)
    log(text)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("schritt", choices=["liste", "suche", "lauf", "bericht", "alles", "diagnose"])
    ap.add_argument("--out", default=str(HIER / "ergebnis"))
    ap.add_argument("--jahr", type=int, default=2026)
    ap.add_argument("--csv", help="MaStR-Export (CSV) statt open-mastr-Download")
    ap.add_argument("--rolle-regex", help="Regex für die MaStR-Marktrolle der Verteilnetzbetreiber Strom "
                    "(Standard: automatisch, siehe ergebnis/mastr_rollen.txt)")
    ap.add_argument("--ohne-gebiete", action="store_true",
                    help="Netzgebiete (Solareinheiten/Netzanschlusspunkte) nicht laden; Bundesland/Region aus Sitz")
    ap.add_argument("--worker", type=int, default=4, help="parallel bearbeitete Websites")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--nur", help="nur Netzbetreiber, deren Name dies enthält")
    ap.add_argument("--wiederholen", help="Status erneut bearbeiten, z. B. blockiert,kein_preisblatt")
    ap.add_argument("--max-seiten", type=int, default=40)
    ap.add_argument("--abstand", type=float, default=1.0, help="Sekunden zwischen Anfragen je Domain (min. 1)")
    ap.add_argument("--ohne-proxy", action="store_true", help="HTTPS_PROXY nicht an Chromium durchreichen")
    ap.add_argument("--max-abfragen", type=int, default=1000, help="Höchstzahl Suchabfragen je Aufruf (Schritt suche)")
    args = ap.parse_args()
    args.abstand = max(1.0, args.abstand)
    args.max_seiten = min(40, args.max_seiten)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    log = Log(out / "lauf.log")
    if args.schritt in ("liste", "alles") and (args.schritt == "liste" or not (out / "netzbetreiber.csv").exists()):
        schritt_liste(args, log)
    if args.schritt == "suche":
        schritt_suche(args, log)
    if args.schritt in ("lauf", "alles"):
        asyncio.run(schritt_lauf(args, log))
    if args.schritt in ("bericht", "lauf", "alles"):
        schritt_bericht(args, log)
    if args.schritt == "diagnose":
        schritt_diagnose(args, log)


if __name__ == "__main__":
    main()
