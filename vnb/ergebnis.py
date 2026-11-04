"""Fortschrittsspeicher (jsonl) und Ausgabe der Ergebnis-CSV, Restliste und Zusammenfassung."""
from __future__ import annotations

import csv
import json
import os
import statistics
from collections import Counter
from datetime import datetime
from pathlib import Path

from .extract import plausibel, plausibel_slp
from .rechner import TYPISCHE_STUNDEN, ct_kwh_bei

RLM = ("lp_unter_2500", "ap_unter_2500", "lp_ueber_2500", "ap_ueber_2500")
RLM_NAMEN = ("lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ueber_2500h_eur_kw_jahr",
             "ap_ueber_2500h_ct_kwh")
SPALTEN = (["nr", "netzbetreiber", "mastr_nr", "website", "bundesland", "region", "netztyp", "status",
            "slp_ap_ct_kwh", "slp_grundpreis_eur_jahr"]
           + [f"ns_{n}" for n in RLM_NAMEN] + [f"msns_{n}" for n in RLM_NAMEN]
           + [f"ns_ct_kwh_bei_{h}h" for h in TYPISCHE_STUNDEN]
           + ["preisstand", "stand_datum", "hinweis", "quelle_url"])
REST_SPALTEN = ["nr", "netzbetreiber", "mastr_nr", "website", "status", "grund", "kandidaten", "quelle_url"]
GEFUNDEN_SPALTEN = ["nr", "netzbetreiber", "website", "status", "rlm_ns", "rlm_msns", "slp",
                    "ns_ct_kwh_bei_4000h", "rlm_quelle_url", "slp_ap_ct_kwh", "slp_grundpreis_eur_jahr", "slp_quelle_url",
                    "preisstand"]
NICHT_GEFUNDEN_SPALTEN = ["nr", "netzbetreiber", "website", "status", "fehlt", "vorhanden", "grund", "quelle_url"]
STATUS = ["ok", "pruefen", "kein_preisblatt", "blockiert", "robots", "keine_website"]


def zahl(v) -> str:
    if v is None or v == "":
        return ""
    s = f"{float(v):.4f}".rstrip("0")
    ganz, _, nach = s.partition(".")
    nach = (nach + "00")[: max(2, len(nach))]
    return f"{ganz},{nach}"


def quellen(d: dict) -> tuple[str, str]:
    """(RLM-Quelle, SLP-Quelle) aus quelle_url ("RLM: … | SLP: …" bei getrennten Dokumenten)."""
    q = d.get("quelle_url", "")
    if q.startswith("RLM: ") and " | SLP: " in q:
        rlm, slp = q[5:].split(" | SLP: ", 1)
        return rlm, slp
    return (q if d.get("ns") else ""), (q if d.get("slp") else "")


class Speicher:
    def __init__(self, ordner: Path):
        self.ordner = ordner
        self.pfad = ordner / "fortschritt.jsonl"
        self.daten: dict[str, dict] = {}
        if self.pfad.exists():
            with open(self.pfad, encoding="utf-8") as f:
                for zeile in f:
                    zeile = zeile.strip()
                    if not zeile:
                        continue
                    try:
                        d = json.loads(zeile)
                    except json.JSONDecodeError:
                        continue   # abgebrochene letzte Zeile
                    self.daten[d["key"]] = d

    def erledigt(self, key: str, wiederholen=()) -> bool:
        d = self.daten.get(key)
        return bool(d) and d.get("status") not in wiederholen

    def speichern(self, d: dict):
        d["zeit"] = datetime.now().isoformat(timespec="seconds")
        self.daten[d["key"]] = d
        with open(self.pfad, "a", encoding="utf-8") as f:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def _recherche(self) -> dict:
        """lauf/quellen_recherche.csv (nr;url;art): Links, die von Hand recherchiert wurden. Hat ein Netzbetreiber so einen
        Link, ist „kein_preisblatt“ falsch: Die Quelle gibt es, wir konnten sie nur (noch) nicht auslesen."""
        pfad = self.ordner.parent / "lauf" / "quellen_recherche.csv"
        out: dict = {}
        if pfad.exists():
            with open(pfad, encoding="utf-8-sig", newline="") as f:
                for z in csv.DictReader(f, delimiter=";"):
                    out.setdefault(str(z["nr"]).strip(), (z["url"].strip(), z.get("art", "").strip()))
        return out

    def _manuell(self) -> dict:
        """lauf/preise_manuell.csv: von Hand eingetragene Preise (Dezimalkomma erlaubt), siehe LEGENDE.md."""
        pfad = self.ordner.parent / "lauf" / "preise_manuell.csv"
        out: dict = {}
        if not pfad.exists():
            return out
        def f(x):
            x = (x or "").strip().replace(",", ".")
            try:
                return float(x) if x else None
            except ValueError:
                return None
        with open(pfad, encoding="utf-8-sig", newline="") as fh:
            for z in csv.DictReader(fh, delimiter=";"):
                nr = str(z.get("nr", "")).strip()
                if not nr:
                    continue
                ns = {"lp_unter_2500": f(z.get("ns_lp_unter_2500h")), "ap_unter_2500": f(z.get("ns_ap_unter_2500h")),
                      "lp_ueber_2500": f(z.get("ns_lp_ab_2500h")), "ap_ueber_2500": f(z.get("ns_ap_ab_2500h"))}
                ms = {"lp_unter_2500": f(z.get("msns_lp_unter_2500h")), "ap_unter_2500": f(z.get("msns_ap_unter_2500h")),
                      "lp_ueber_2500": f(z.get("msns_lp_ab_2500h")), "ap_ueber_2500": f(z.get("msns_ap_ab_2500h"))}
                if all(v is None for v in (*ns.values(), *ms.values(), f(z.get("slp_ap")), f(z.get("slp_gp")))):
                    continue
                out[nr] = {"ns": ns, "ms": ms, "slp": {"ap": f(z.get("slp_ap")), "gp": f(z.get("slp_gp"))},
                           "preisstand": (z.get("preisstand") or "").strip() or "unklar", "stand_datum": (z.get("stand_datum") or "").strip(),
                           "le": (z.get("grenze") or "").strip() in ("<=", "≤", ">", "le"), "url": (z.get("quelle_url") or "").strip(),
                           "hinweis": (z.get("hinweis") or "").strip()}
        return out

    def zeilen(self) -> list[dict]:
        man = self._manuell()
        return [self._mit_manuell(d, man) for d in self._zeilen_recherche()]

    def _mit_manuell(self, d: dict, man: dict) -> dict:
        m = man.get(str(d.get("nr")))
        if not m:
            return d
        d = dict(d)
        ns = {k: v for k, v in m["ns"].items() if v is not None}
        ms = {k: v for k, v in m["ms"].items() if v is not None}
        slp = {k: v for k, v in m["slp"].items() if v is not None}
        grund = []
        if ns:
            grund += plausibel(ns, "NS") if len(ns) == 4 else ["NS: Werte unvollständig"]
        else:
            grund.append("NS fehlt")
        if ms:
            grund += plausibel(ms, "MS/NS") if len(ms) == 4 else ["MS/NS: Werte unvollständig"]
        grund += plausibel_slp(slp) if slp else ["SLP fehlt"]
        d.update(ns=ns if len(ns) == 4 else {}, msns=ms if len(ms) == 4 else {}, slp=slp, rlm_ok=len(ns) == 4 and not any(g.startswith("NS") for g in grund),
                 slp_ok=bool(slp) and not plausibel_slp(slp), grenze_le=m["le"], preisstand=m["preisstand"], stand_datum=m["stand_datum"],
                 quelle_url=m["url"] or d.get("quelle_url", ""))
        d["status"] = "ok" if not grund else "pruefen"
        d["hinweis"] = "manuell eingetragen" + (f" ({m['hinweis']})" if m["hinweis"] else "") + (("; Prüfung: " + "; ".join(grund)) if grund else "")
        return d

    def _zeilen_recherche(self) -> list[dict]:
        ueber = self._recherche()
        erg = []
        for d in sorted(self.daten.values(), key=lambda d: (int(d.get("nr") or 0), d["key"])):
            if d.get("status") == "kein_preisblatt" and str(d.get("nr")) in ueber:
                url, art = ueber[str(d.get("nr"))]
                d = dict(d)
                d["status"] = "pruefen"
                d["quelle_url"] = d.get("quelle_url") or url
                alt = d.get("hinweis", "")
                d["hinweis"] = f"Quelle aus Recherche vorhanden ({art}), noch nicht ausgelesen: {url}" + (f"; {alt}" if alt else "")
            erg.append(d)
        return erg

    # ------------------------------------------------------------ Ausgabe
    @staticmethod
    def zeile(d: dict) -> list:
        ns, msns, slp = d.get("ns") or {}, d.get("msns") or {}, d.get("slp") or {}
        ct = [ct_kwh_bei(ns, h, d.get("grenze_le", False)) if d.get("rlm_ok") else None for h in TYPISCHE_STUNDEN]
        hinweis = d.get("hinweis", "")
        return [d.get("nr", ""), d.get("netzbetreiber", ""), d.get("mastr_nr", ""), d.get("website", ""),
                d.get("bundesland", ""), d.get("region", ""), d.get("netztyp", ""), d.get("status", ""),
                zahl(slp.get("ap")), zahl(slp.get("gp")),
                *[zahl(ns.get(k)) for k in RLM], *[zahl(msns.get(k)) for k in RLM],
                *[zahl(round(c, 2)) if c is not None else "" for c in ct],
                d.get("preisstand", "") if (ns or slp) else "", d.get("stand_datum", ""), hinweis,
                d.get("quelle_url", "")]

    def ausgeben(self, jahr: int) -> str:
        zeilen = self.zeilen()
        ziel = self.ordner / f"netzentgelte_{jahr}.csv"
        tmp = ziel.with_suffix(".tmp")
        with open(tmp, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(SPALTEN)
            for d in zeilen:
                w.writerow(self.zeile(d))
        tmp.replace(ziel)

        rest = self.ordner / "restliste.csv"
        with open(rest.with_suffix(".tmp"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(REST_SPALTEN)
            for d in zeilen:
                if d.get("status") != "ok":
                    w.writerow([d.get("nr", ""), d.get("netzbetreiber", ""), d.get("mastr_nr", ""),
                                d.get("website", ""), d.get("status", ""), d.get("grund", ""),
                                " | ".join(d.get("kandidaten") or []), d.get("quelle_url", "")])
        rest.with_suffix(".tmp").replace(rest)
        self.nicht_gefunden(zeilen)
        self.gefunden(zeilen)
        text = self.zusammenfassung(zeilen, jahr)
        (self.ordner / "zusammenfassung.md").write_text(text, encoding="utf-8")
        return text

    def nicht_gefunden(self, zeilen: list[dict]):
        """Zeilen, bei denen Preisblatt, SLP- oder RLM-Werte nicht gefunden wurden (zur separaten Nachbearbeitung)."""
        ziel = self.ordner / "nicht_gefunden.csv"
        with open(ziel.with_suffix(".tmp"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(NICHT_GEFUNDEN_SPALTEN)
            for d in zeilen:
                grund = d.get("grund", "")
                if d.get("status") == "kein_preisblatt":
                    fehlt = "Preisblatt"
                elif d.get("status") == "pruefen":
                    fehlt = " + ".join(t for t in ("SLP", "RLM") if f"{t}-Werte nicht gefunden" in grund)
                else:
                    fehlt = ""
                if not fehlt:
                    continue
                slp, ns = d.get("slp") or {}, d.get("ns") or {}
                vorhanden = ", ".join(t for t, ok in (("RLM NS", d.get("rlm_ok") and ns), ("SLP", d.get("slp_ok") and slp))
                                      if ok)
                w.writerow([d.get("nr", ""), d.get("netzbetreiber", ""), d.get("website", ""), d.get("status", ""),
                            fehlt, vorhanden, grund, d.get("quelle_url", "")])
        ziel.with_suffix(".tmp").replace(ziel)

    def gefunden(self, zeilen: list[dict]):
        """Zeilen, bei denen ein Preisblatt gefunden und mindestens ein Teil (RLM oder SLP) gelesen wurde."""
        def zustand(werte, ok):
            return "ok" if werte and ok else "auffällig" if werte else "fehlt"
        ziel = self.ordner / "gefunden.csv"
        with open(ziel.with_suffix(".tmp"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(GEFUNDEN_SPALTEN)
            for d in zeilen:
                ns, msns, slp = d.get("ns") or {}, d.get("msns") or {}, d.get("slp") or {}
                if d.get("status") not in ("ok", "pruefen") or not (ns or slp):
                    continue
                ct = ct_kwh_bei(ns, 4000, d.get("grenze_le", False)) if d.get("rlm_ok") else None
                rlm_url, slp_url = quellen(d)
                w.writerow([d.get("nr", ""), d.get("netzbetreiber", ""), d.get("website", ""), d.get("status", ""),
                            zustand(ns, d.get("rlm_ok")), zustand(msns, d.get("rlm_ok")),
                            zustand(slp, d.get("slp_ok")),
                            zahl(round(ct, 2)) if ct is not None else "", rlm_url,
                            zahl(slp.get("ap")) if d.get("slp_ok") else "", zahl(slp.get("gp")) if d.get("slp_ok") else "",
                            slp_url, d.get("preisstand", "")])
        ziel.with_suffix(".tmp").replace(ziel)

    @staticmethod
    def zusammenfassung(zeilen: list[dict], jahr: int) -> str:
        n = len(zeilen)
        c = Counter(d.get("status") for d in zeilen)
        z = [f"# Netzentgelte Strom {jahr} (SLP und RLM): Zusammenfassung", "",
             f"Stand {datetime.now():%d.%m.%Y %H:%M}, {n} Netzbetreiber bzw. Netzgebiete", "",
             "## Anzahl je Status", "", "| Status | Anzahl | Anteil |", "|---|---:|---:|"]
        for s in STATUS + sorted(set(c) - set(STATUS)):
            if c.get(s):
                z.append(f"| {s} | {c[s]} | {c[s] / n:.0%} |")
        ok = [d for d in zeilen if d.get("status") == "ok"]
        ps = Counter(d.get("preisstand") for d in ok)
        z += ["", "Preisstand (nur ok): " + ", ".join(f"{k} {v}" for k, v in ps.most_common()), ""]
        def spanne(titel, einheit, werte):
            werte = [(w, n) for w, n in werte if w is not None]
            if not werte:
                return []
            lo, hi = min(werte), max(werte)
            med = statistics.median(w for w, _ in werte)
            return [f"## {titel}", "", f"- Minimum: {zahl(round(lo[0], 2))} {einheit} ({lo[1]})",
                    f"- Maximum: {zahl(round(hi[0], 2))} {einheit} ({hi[1]})",
                    f"- Median: {zahl(round(med, 2))} {einheit} (n = {len(werte)})", ""]
        z += spanne("Spanne SLP-Arbeitspreis Niederspannung (SLP-Werte ok)", "ct/kWh",
                    [(d["slp"]["ap"], d["netzbetreiber"]) for d in zeilen if d.get("slp_ok") and d.get("slp")])
        z += spanne("Spanne NS-Netzentgelt RLM bei 4.000 h (RLM-Werte ok)", "ct/kWh",
                    [(ct_kwh_bei(d["ns"], 4000, d.get("grenze_le", False)), d["netzbetreiber"])
                     for d in zeilen if d.get("rlm_ok") and d.get("ns")])
        z += spanne("Spanne NS Leistungspreis ab 2.500 h (RLM-Werte ok)", "€/kW/a",
                    [(d["ns"]["lp_ueber_2500"], d["netzbetreiber"]) for d in zeilen
                     if d.get("rlm_ok") and (d.get("ns") or {}).get("lp_ueber_2500") is not None])
        mail = [d for d in zeilen if "Website aus E-Mail-Domain abgeleitet" in (d.get("hinweis") or "")]
        sitz = [d for d in zeilen if d.get("gebiet_quelle") == "Sitz laut MaStR"]
        typen = Counter(d.get("netztyp") or "unbekannt" for d in zeilen)
        z += ["## Datenherkunft", "",
              f"- Website aus E-Mail-Domain abgeleitet: {len(mail)}",
              f"- Bundesland/Region nur aus dem Sitz laut MaStR: {len(sitz)}",
              "- Netztyp: " + ", ".join(f"{k} {v}" for k, v in typen.most_common()), ""]
        pilot = [d for d in zeilen if d.get("pilot_abgleich")]
        if pilot:
            gl = [d for d in pilot if d["pilot_abgleich"] == "gleich"]
            ab = [d for d in pilot if d["pilot_abgleich"].startswith("abweichend")]
            ng = [d for d in pilot if d["pilot_abgleich"].startswith("nicht gelesen")]
            z += ["## Abgleich mit den geprüften Pilotwerten (Neuauslesung der Pilot-Quelle)", "",
                  f"- NS-Werte exakt gleich: {len(gl)} von {len(pilot)}",
                  f"- abweichend: {len(ab)}", f"- Quelle nicht lesbar: {len(ng)}", ""]
            z += [f"- {d.get('nr')}. {d.get('netzbetreiber')}: {d['pilot_abgleich']}" for d in ab + ng]
            z.append("")
        vorl = [d for d in ok if d.get("preisstand") != "endgültig"]
        if vorl:
            z += [f"## Status ok, aber Preisstand nicht endgültig ({len(vorl)})", ""]
            z += [f"- {d.get('nr')}. {d.get('netzbetreiber')}: {d.get('preisstand')}" for d in vorl]
            z.append("")
        rest = [d for d in zeilen if d.get("status") != "ok"]
        z += [f"## Restfälle ({len(rest)})", ""]
        for s in STATUS[1:] + sorted(set(c) - set(STATUS)):
            gruppe = [d for d in rest if d.get("status") == s]
            if not gruppe:
                continue
            z += [f"### {s} ({len(gruppe)})", ""]
            for d in gruppe:
                g = (d.get("grund") or "").replace("\n", " ")
                z.append(f"- {d.get('nr')}. {d.get('netzbetreiber')}: {g[:200]}")
            z.append("")
        return "\n".join(z)
