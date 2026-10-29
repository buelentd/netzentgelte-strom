"""Netzbetreiber-Liste aus dem Marktstammdatenregister (open-mastr, Bulk-Download)."""
from __future__ import annotations

import csv
import re
from collections import Counter
from datetime import date
from pathlib import Path

from .extract import norm

UENB = re.compile(r"50\s*hertz|amprion|tennet|transnet\s*bw", re.I)
FREEMAIL = {"gmail.com", "gmx.de", "gmx.net", "web.de", "t-online.de", "outlook.com", "hotmail.com",
            "yahoo.de", "yahoo.com", "freenet.de", "arcor.de", "online.de", "icloud.com", "posteo.de",
            "mail.de", "aol.com", "googlemail.com", "live.de"}
SPALTEN = ["nr", "netzbetreiber", "mastr_nr", "website", "website_quelle", "bundesland", "region", "netztyp",
           "gebiet_quelle", "marktpartner_id", "ort", "sitz_bundesland", "rollen", "pilot_nr"]


def _spalte(df, *namen):
    low = {c.lower(): c for c in df.columns}
    for n in namen:
        if n.lower() in low:
            return low[n.lower()]
    for n in namen:
        for c in df.columns:
            if n.lower() in c.lower():
                return c
    return None


def _txt(v) -> str:
    if v is None:
        return ""
    s = str(v).strip()
    return "" if s.lower() in ("nan", "none", "nat") else s


def website_bestimmen(webseite: str, portal: str, email: str) -> tuple[str, str]:
    for wert, quelle in ((webseite, "MaStR Webseite"), (portal, "MaStR Webportal des Netzbetreibers")):
        w = _txt(wert)
        if w and "." in w and " " not in w:
            return w, quelle
    m = re.search(r"@([a-z0-9.-]+\.[a-z]{2,})", _txt(email).lower())
    if m and m.group(1) not in FREEMAIL:
        return "https://www." + m.group(1).removeprefix("www."), "aus E-Mail-Domain abgeleitet"
    return "", ""


def aus_mastr(ausgabe: Path, mastr_dir: Path, rolle_regex: str = "", gebiete: bool = True, log=print) -> list[dict]:
    from . import gebiete as gebiete_mod
    from . import mastr_xml

    zip_pfad = mastr_xml.herunterladen(mastr_dir / "xml_download", gebiete, log)
    akteure, rollen, sammler, netzinfo, rollen_zaehler = mastr_xml.lesen(zip_pfad, gebiete, log, rolle_regex)
    out = filtern(akteure, rollen, ausgabe, rolle_regex, rollen_zaehler)
    geschlossen = [e for e in out if netzinfo.get(e["mastr_nr"], {}).get("geschlossen")]
    if geschlossen:
        log(f"  {len(geschlossen)} Betreiber ausschließlich geschlossener Verteilnetze ausgeschlossen")
        out = [e for e in out if e not in geschlossen]
    gebiet_ergaenzen(out, sammler, netzinfo)
    gebiete_mod.plz_schreiben(sammler, {e["mastr_nr"]: e["netzbetreiber"] for e in out},
                              ausgabe.parent / "plz_netzbetreiber.csv")
    if not 300 <= len(out) <= 2000:
        raise SystemExit(f"Filter ergibt {len(out)} Netzbetreiber (erwartet ca. 850). Rollenwerte prüfen in "
                         f"{ausgabe.parent / 'mastr_rollen.txt'} und mit --rolle-regex angeben.")
    return out


def filtern(akteure, rollen, ausgabe: Path, rolle_regex: str = "", rollen_zaehler: Counter | None = None) -> list[dict]:
    a_nr = _spalte(akteure, "MastrNummer")
    a_name = _spalte(akteure, "Firmenname")
    a_web = _spalte(akteure, "Webseite")
    a_portal = _spalte(akteure, "WebportalDesNetzbetreibers")
    a_mail = _spalte(akteure, "Email")
    a_funktion = _spalte(akteure, "Marktfunktion")
    a_ende = _spalte(akteure, "Taetigkeitsende")
    a_ort = _spalte(akteure, "Ort")
    a_bl = _spalte(akteure, "Bundesland")
    r_akteur = _spalte(rollen, "MarktakteurMastrNummer")
    r_rolle = _spalte(rollen, "Marktrolle")
    r_mpid = _spalte(rollen, "Marktpartneridentifikationsnummer")

    rollen_zaehler = rollen_zaehler or Counter(_txt(v) for v in rollen[r_rolle])
    funktion_zaehler = Counter(_txt(v) for v in akteure[a_funktion]) if a_funktion else Counter()

    def rolle_ist_vnb(r: str) -> bool:
        n = norm(r)
        if rolle_regex:
            return bool(re.search(rolle_regex, r, re.I))
        if "gas" in n or "uebertragung" in n or "geschlossen" in n:
            return False
        return "netzbetreiber" in n or "verteilnetz" in n

    rollen_je_akteur: dict[str, list] = {}
    mpid_je_akteur: dict[str, str] = {}
    for _, row in rollen.iterrows():
        nr = _txt(row[r_akteur])
        rolle = _txt(row[r_rolle])
        rollen_je_akteur.setdefault(nr, []).append(rolle)
        if rolle_ist_vnb(rolle) and r_mpid and _txt(row[r_mpid]):
            mpid_je_akteur.setdefault(nr, _txt(row[r_mpid]))

    heute = date.today().isoformat()
    out = []
    for _, row in akteure.iterrows():
        nr = _txt(row[a_nr])
        rl = rollen_je_akteur.get(nr, [])
        funktion = norm(_txt(row[a_funktion])) if a_funktion else ""
        rolle_ok = any(rolle_ist_vnb(r) for r in rl)
        strom = bool(rolle_regex) or ("strom" in funktion and "netzbetreiber" in funktion) or any(
            "strom" in norm(r) and rolle_ist_vnb(r) for r in rl)
        if not (rolle_ok and strom):
            continue
        name = _txt(row[a_name])
        if UENB.search(name) or any("uebertragung" in norm(r) for r in rl):
            continue
        ende = _txt(row[a_ende]) if a_ende else ""
        if ende and ende[:10] < heute:
            continue
        web, quelle = website_bestimmen(row[a_web] if a_web else "", row[a_portal] if a_portal else "",
                                        row[a_mail] if a_mail else "")
        out.append({"netzbetreiber": name, "mastr_nr": nr, "website": web, "website_quelle": quelle,
                    "marktpartner_id": mpid_je_akteur.get(nr, ""), "ort": _txt(row[a_ort]) if a_ort else "",
                    "sitz_bundesland": _txt(row[a_bl]) if a_bl else "",
                    "rollen": " | ".join(sorted(set(rl)))})

    with open(ausgabe.parent / "mastr_rollen.txt", "w", encoding="utf-8") as f:
        f.write("Marktrollen im MaStR (Anzahl Einträge):\n")
        for k, v in rollen_zaehler.most_common():
            f.write(f"  {v:6d}  {k}{'   <- als Verteilnetzbetreiber gewertet' if rolle_ist_vnb(k) else ''}\n")
        f.write("\nMarktfunktionen:\n")
        for k, v in funktion_zaehler.most_common():
            f.write(f"  {v:6d}  {k}\n")
        f.write(f"\nAusgewählt: {len(out)} Verteilnetzbetreiber Strom\n")
    return out


def gebiet_ergaenzen(eintraege: list[dict], sammler, netzinfo: dict):
    """bundesland/region/netztyp: Netzgebiet aus MaStR-Einheiten, sonst MaStR-Netzdaten, sonst Sitz."""
    for e in eintraege:
        g = sammler.gebiet(e["mastr_nr"])
        laender = sorted(netzinfo.get(e["mastr_nr"], {}).get("laender", ()))
        if g:
            e.update(bundesland=g["bundesland"], region=g["region"], netztyp=g["netztyp"],
                     gebiet_quelle="Netzgebiet (MaStR-Einheiten)")
        elif laender:
            e.update(bundesland=" / ".join(laender), region="", netztyp="", gebiet_quelle="MaStR-Netzdaten")
        else:
            e.update(bundesland=e.get("sitz_bundesland", ""), region=e.get("ort", ""), netztyp="",
                     gebiet_quelle="Sitz laut MaStR" if e.get("sitz_bundesland") or e.get("ort") else "")


def aus_csv(pfad: Path) -> list[dict]:
    """Alternative: CSV-Export der MaStR-Weboberfläche (Marktakteure, Netzbetreiber Strom)."""
    with open(pfad, newline="", encoding="utf-8-sig") as f:
        probe = f.read(4096)
        f.seek(0)
        dialekt = csv.Sniffer().sniff(probe, delimiters=";,\t")
        zeilen = list(csv.DictReader(f, dialect=dialekt))
    kopf = list(zeilen[0].keys())

    def pick(*kand):
        for k in kand:
            for c in kopf:
                if k in c.lower():
                    return c
        return None
    c_name = pick("firmenname", "name des marktakteurs", "name")
    c_nr = pick("mastr-nr", "mastrnummer", "mastr-nummer", "mastr")
    c_web = pick("webseite", "website", "internet", "homepage")
    c_mail = pick("e-mail", "email")
    out = []
    for z in zeilen:
        name = (z.get(c_name) or "").strip()
        if not name or UENB.search(name):
            continue
        web, quelle = website_bestimmen(z.get(c_web) or "", "", z.get(c_mail) or "")
        out.append({"netzbetreiber": name, "mastr_nr": (z.get(c_nr) or "").strip(), "website": web,
                    "website_quelle": quelle, "marktpartner_id": "", "ort": "", "rollen": ""})
    return out


def schreiben(eintraege: list[dict], pfad: Path):
    with open(pfad, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SPALTEN, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for e in eintraege:
            w.writerow(e)


def lesen(pfad: Path) -> list[dict]:
    with open(pfad, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))
