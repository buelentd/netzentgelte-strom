"""Fortschrittsspeicher (jsonl) und Ausgabe der Ergebnis-CSV, Restliste und Zusammenfassung."""
from __future__ import annotations

import csv
import json
import os
import statistics
from collections import Counter
from datetime import datetime
from pathlib import Path

from .extract import plausibel, plausibel_reihenfolge, plausibel_slp
from .rechner import TYPISCHE_STUNDEN, ct_kwh_bei

RLM = ("lp_unter_2500", "ap_unter_2500", "lp_ueber_2500", "ap_ueber_2500")
RLM_NAMEN = ("lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr",
             "ap_ab_2500h_ct_kwh")
HLZF_JAHRESZEITEN = ("fruehling", "sommer", "herbst", "winter")
HLZF_COLS = ([f"hlzf_ns_{x}" for x in HLZF_JAHRESZEITEN] + [f"hlzf_msns_{x}" for x in HLZF_JAHRESZEITEN]
             + ["hlzf_schwelle_prozent", "hlzf_mindestleistung_kw", "hlzf_quelle_url"])
SPALTEN = (["mastr_nr", "nr", "netzbetreiber", "website", "bundesland", "region", "netztyp", "status",
            "slp_ap_ct_kwh", "slp_grundpreis_eur_jahr"]
           + [f"ms_{n}" for n in RLM_NAMEN] + [f"msns_{n}" for n in RLM_NAMEN]
           + [f"ns_{n}" for n in RLM_NAMEN] + [f"hsms_{n}" for n in RLM_NAMEN]
           + ["hsms_status", "grenze_2500h"]
           + [f"ms_ct_kwh_bei_{h}h" for h in TYPISCHE_STUNDEN] + ["msns_ct_kwh_bei_4000h"]
           + [f"ns_ct_kwh_bei_{h}h" for h in TYPISCHE_STUNDEN]
           + HLZF_COLS + ["hlzf_status"]
           + ["preisstand", "stand_datum", "hinweis", "quelle_url"])
REST_SPALTEN = ["mastr_nr", "nr", "netzbetreiber", "website", "status", "grund", "kandidaten", "quelle_url"]
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
        """lauf/preise_manuell.csv: von Hand oder aus der Liste des Nutzers eingetragene Werte (Dezimalkomma erlaubt).
        Je Ebene (ms_, msns_, ns_, hsms_) zählen nur vollständige Vierergruppen; SLP als slp_ap_ct_kwh und slp_grundpreis_eur_jahr."""
        pfad = self.ordner.parent / "lauf" / "preise_manuell.csv"
        out: dict = {}
        if not pfad.exists():
            return out
        def f(x):
            x = (x or "").strip().replace(" ", "")
            if "," in x:
                x = x.replace(".", "").replace(",", ".")
            try:
                return float(x) if x else None
            except ValueError:
                return None
        namen = (("lp_unter_2500", "lp_unter_2500h"), ("ap_unter_2500", "ap_unter_2500h"),
                 ("lp_ueber_2500", "lp_ab_2500h"), ("ap_ueber_2500", "ap_ab_2500h"))
        with open(pfad, encoding="utf-8-sig", newline="") as fh:
            for z in csv.DictReader(fh, delimiter=";"):
                nr = str(z.get("nr", "")).strip()
                if not nr:
                    continue
                m = {"ebenen": {}, "slp": {"ap": f(z.get("slp_ap_ct_kwh") or z.get("slp_ap")), "gp": f(z.get("slp_grundpreis_eur_jahr") or z.get("slp_gp"))},
                     "preisstand": (z.get("preisstand") or "").strip(), "stand_datum": (z.get("stand_datum") or "").strip(),
                     "le": (z.get("grenze") or z.get("grenze_2500h") or "").strip() in ("<=", "≤", "≤ / >", ">", "le"),
                     "url": (z.get("quelle_url") or "").strip(), "hinweis": (z.get("hinweis") or "").strip(),
                     "geprueft": (z.get("geprueft") or "").strip().lower() == "ja"}
                for eb in ("ms", "msns", "ns", "hsms"):
                    w = {k: f(z.get(f"{eb}_{n}_{'eur_kw_jahr' if k.startswith('lp') else 'ct_kwh'}")) for k, n in namen}
                    if all(v is not None for v in w.values()):
                        m["ebenen"][eb] = w
                if m["ebenen"] or any(v is not None for v in m["slp"].values()):
                    out[nr] = m
        return out

    def zeilen(self) -> list[dict]:
        if self.ordner.name != "ergebnis":      # Recherche und manuelle Preise gelten nur für 2026
            return sorted(self.daten.values(), key=lambda d: (int(d.get("nr") or 0), d["key"]))
        man = self._manuell()
        sperre = self._sperre()
        gruende = self._hsms_gruende()
        hlzf = self._hlzf()
        ent = self._entfernt()
        beleg_offen = self._beleg_offen_liste()
        freigabe = self._freigabe_liste()
        sonder = self._sonderfall_liste()
        zeilen = [self._sonderfall(self._freigabe(self._entfernt_hinweis(self._hsms_grund(self._beleg_offen(self._gesperrt(self._status_v2(self._entfernt_leeren(self._mit_manuell(d, man), ent)), sperre), beleg_offen), gruende), ent), freigabe), sonder)
                  for d in self._zeilen_recherche()]
        for d in zeilen:
            d["hlzf"] = hlzf.get(d.get("mastr_nr"), {})
        return zeilen

    def _entfernt(self) -> dict:
        """lauf/werte_entfernt.csv (nr;ebene;grund): erkannte Lesefehler (Tage oder Zeilennummern als Preise gelesen), die ohne Dokumentzeile bleiben; Wert wird leer ausgegeben."""
        pfad = self.ordner.parent / "lauf" / "werte_entfernt.csv"
        out: dict = {}
        if pfad.exists():
            with open(pfad, encoding="utf-8-sig") as f:
                for r in csv.DictReader(f, delimiter=";"):
                    out.setdefault(str(r["nr"]), {})[r["ebene"]] = r["grund"]
        return out

    @staticmethod
    def _entfernt_leeren(d: dict, ent: dict) -> dict:
        e = ent.get(str(d.get("nr")))
        if not e:
            return d
        d = dict(d)
        for eb in e:
            d[eb] = {}
        return d

    @staticmethod
    def _entfernt_hinweis(d: dict, ent: dict) -> dict:
        e = ent.get(str(d.get("nr")))
        if not e:
            return d
        d["hinweis"] = "Lesefehler entfernt: " + "; ".join(f"{eb.upper()} ({g})" for eb, g in e.items()) + ("; " + d["hinweis"] if d.get("hinweis") else "")
        if d.get("status") == "ok":
            d["status"] = "pruefen"
        return d

    def _hlzf(self) -> dict:
        """lauf/hlzf_zusammen.csv (Skript daten/hlzf_zusammenfuehren.py): Hochlastzeitfenster und Grund je Netzbetreiber, Schlüssel MaStR-Nr."""
        pfad = self.ordner.parent / "lauf" / "hlzf_zusammen.csv"
        if not pfad.exists():
            return {}
        with open(pfad, encoding="utf-8-sig", newline="") as f:
            return {r["mastr_nr"]: r for r in csv.DictReader(f, delimiter=";") if r.get("mastr_nr")}

    def _hsms_gruende(self) -> dict:
        """lauf/hsms_grund.csv (mastr_nr;hsms_status): warum HS/MS fehlt (Skript daten/hsms_grund.py)."""
        pfad = self.ordner.parent / "lauf" / "hsms_grund.csv"
        if not pfad.exists():
            return {}
        with open(pfad, encoding="utf-8-sig", newline="") as f:
            return {r["mastr_nr"]: r["hsms_status"] for r in csv.DictReader(f, delimiter=";") if r.get("mastr_nr")}

    @staticmethod
    def _hsms_grund(d: dict, gruende: dict) -> dict:
        g = gruende.get(d.get("mastr_nr"))
        if not g or len(d.get("hsms") or {}) == 4:
            return d
        d = dict(d)
        d["hsms_status"] = g
        return d

    def _sperre(self) -> dict:
        """lauf/zuordnung_unbelegt.csv (nr;grund): Netzbetreiber, deren Zuordnung zum gelesenen Preisblatt nicht belegt ist."""
        pfad = self.ordner.parent / "lauf" / "zuordnung_unbelegt.csv"
        if not pfad.exists():
            return {}
        with open(pfad, encoding="utf-8-sig", newline="") as f:
            return {r["nr"].strip(): r["grund"].strip() for r in csv.DictReader(f, delimiter=";") if r.get("nr")}

    def _beleg_offen_liste(self) -> dict:
        """lauf/beleg_offen.csv (nr;offene_ebenen): Werte, die der Beleg-Leser nicht zeilenweise belegen konnte (Regel 07.11.2026: 'ok' nur mit vollständigem Beleg)."""
        pfad = self.ordner.parent / "lauf" / "beleg_offen.csv"
        if not pfad.exists():
            return {}
        with open(pfad, encoding="utf-8-sig", newline="") as f:
            return {r["nr"].strip(): r["offene_ebenen"].strip() for r in csv.DictReader(f, delimiter=";") if r.get("nr")}

    def _freigabe_liste(self) -> set:
        """lauf/ok_freigabe_nutzer.csv (mastr_nr;nr;...): vom Nutzer freigegebene Netzbetreiber (09.11.2026), obwohl nicht zeilenweise am Dokument belegt."""
        pfad = self.ordner.parent / "lauf" / "ok_freigabe_nutzer.csv"
        if not pfad.exists():
            return set()
        with open(pfad, encoding="utf-8-sig", newline="") as f:
            return {r["nr"].strip() for r in csv.DictReader(f, delimiter=";") if r.get("nr")}

    def _sonderfall_liste(self) -> dict:
        """lauf/sonderfall_nutzer.csv (nr;status;hinweis): vom Nutzer geprüfte Sonderfälle (z. B. Werksnetz nur 110 kV), Status und Hinweis werden gesetzt."""
        pfad = self.ordner.parent / "lauf" / "sonderfall_nutzer.csv"
        if not pfad.exists():
            return {}
        with open(pfad, encoding="utf-8-sig", newline="") as f:
            return {r["nr"].strip(): r for r in csv.DictReader(f, delimiter=";") if r.get("nr")}

    @staticmethod
    def _sonderfall(d: dict, sonder: dict) -> dict:
        r = sonder.get(str(d.get("nr")))
        if not r:
            return d
        d = dict(d)
        d["status"] = r["status"].strip()
        d["hinweis"] = r["hinweis"].strip()
        return d

    @staticmethod
    def _freigabe(d: dict, frei: set) -> dict:
        if str(d.get("nr")) not in frei or d.get("status") != "pruefen" or not d.get("slp") or not d.get("ns"):
            return d
        d = dict(d)
        d["status"] = "ok"
        d["hinweis"] = "Freigegeben durch Nutzer 09.11.2026, nicht zeilenweise am Dokument belegt (Stichprobe 20 am Dokument: 3 Fehler, korrigiert)" + ("; " + d["hinweis"] if d.get("hinweis") else "")
        return d

    @staticmethod
    def _beleg_offen(d: dict, offen: dict) -> dict:
        grund = offen.get(str(d.get("nr")))
        if not grund or d.get("status") != "ok":
            return d
        d = dict(d)
        d["status"] = "pruefen"
        d["hinweis"] = "Nicht zeilenweise belegt (" + grund[:120] + ")" + ("; " + d["hinweis"] if d.get("hinweis") else "")
        return d

    @staticmethod
    def _gesperrt(d: dict, sperre: dict) -> dict:
        grund = sperre.get(str(d.get("nr")))
        if not grund:
            return d
        d = dict(d)
        for k in ("ms", "msns", "ns", "hsms", "slp"):
            d[k] = {}
        d["status"] = "pruefen"
        d["hinweis"] = grund
        return d

    @staticmethod
    def _status_v2(d: dict) -> dict:
        """Zielbild (Festlegung Nutzer 04.11.2026): ok nur mit Mittelspannung, MS/NS, Niederspannung und SLP.
        HS/MS: gelesen, 'nicht ausgewiesen' (Dokument nennt keine Hochspannung) oder 'fehlt' (erwartet, aber nicht gelesen)."""
        if not d.get("v2") or d.get("status") not in ("ok", "pruefen"):
            return d
        d = dict(d)
        fehlt = []
        if len(d.get("ns") or {}) < 4: fehlt.append("Niederspannung")
        if len(d.get("msns") or {}) < 4: fehlt.append("MS/NS")
        if len(d.get("ms") or {}) < 4: fehlt.append("Mittelspannung")
        slp = d.get("slp") or {}
        if slp.get("ap") is None or slp.get("gp") is None: fehlt.append("SLP")
        if len(d.get("hsms") or {}) == 4: d["hsms_status"] = "gelesen"
        elif d.get("hs_erwaehnt"):
            d["hsms_status"] = "fehlt"; fehlt.append("HS/MS")
        else: d["hsms_status"] = "nicht ausgewiesen"
        if fehlt and d["status"] == "ok":
            d["status"] = "pruefen"
            alt = d.get("hinweis", "")
            d["hinweis"] = "Fehlt: " + ", ".join(fehlt) + (f"; {alt}" if alt else "")
        return d

    def _mit_manuell(self, d: dict, man: dict) -> dict:
        """Eingetragene Werte ergänzen und überschreiben die gelesenen je Ebene; vollständige Gruppen werden geprüft."""
        m = man.get(str(d.get("nr")))
        if not m:
            return d
        d = dict(d)
        grund = []
        for eb, w in m["ebenen"].items():
            bad = [g for g in plausibel(w, "MS/NS" if eb == "msns" else {"ms": "Mittelspannung", "hsms": "HS/MS"}.get(eb, "NS"))
                   if eb == "ns" or "außerhalb 40–500" not in g]
            if str(m["hinweis"]).startswith("Korrigiert") and len(w) == 4 and w.get("lp_unter_2500") == w.get("lp_ueber_2500") and w.get("ap_unter_2500") == w.get("ap_ueber_2500"):
                bad = [g for g in bad if "nicht kleiner" not in g and "nicht größer" not in g]      # einstufiger Tarif: gleiche Werte für beide Benutzungsdauern, so im Preisblatt
            if str(m["hinweis"]).startswith("Korrigiert") and w.get("ap_ueber_2500") == 0.0:
                bad = [g for g in bad if "AP außerhalb 0–30" not in g]       # Arbeitspreis 0,00 ct steht so im Dokument (von Hand am Text geprüft)
            gel = d.get(eb) or {}
            abw = len(gel) == 4 and len(w) == 4 and any(abs(gel[k] - w[k]) > 0.006 for k in w) \
                and not str(m["hinweis"]).startswith("Korrigiert")
            if abw and not plausibel(gel, "MS/NS" if eb == "msns" else {"ms": "Mittelspannung", "hsms": "HS/MS"}.get(eb, "NS")):
                # Der Leser hat die Ebene am Dokument gelesen, die Liste weicht ab: gelesener Wert bleibt, Abweichung wird gemeldet
                grund.append(f"{eb}: Liste weicht vom gelesenen Wert ab ({'/'.join(str(w[k]) for k in w)}); gelesener Wert behalten")
            elif bad:
                grund.append(f"{eb}: {bad[0]}")
            else:
                d[eb] = w
        slp = {k: v for k, v in m["slp"].items() if v is not None}
        pl = plausibel_slp(slp) if len(slp) == 2 else ["unvollständig"]
        if str(m["hinweis"]).startswith("Korrigiert") and len(slp) == 2:
            pl = [g for g in pl if not ("Arbeitspreis" in g and 2 <= slp["ap"] < 3)]      # am Dokument von Hand geprüft: niedriger Arbeitspreis steht so im Preisblatt
        if len(slp) == 2 and not pl:
            d["slp"] = slp
        elif slp:
            grund.append("SLP: " + "; ".join(pl or ["unvollständig"]))
        red = plausibel_reihenfolge(d.get("ms") or {}, d.get("msns") or {}, d.get("ns") or {})
        grund += red
        d.update(v2=True, rlm_ok=len(d.get("ns") or {}) == 4, slp_ok=len(d.get("slp") or {}) == 2,
                 quelle_url=m["url"] or d.get("quelle_url", ""))
        if m["preisstand"]: d["preisstand"] = m["preisstand"]
        if m["stand_datum"]: d["stand_datum"] = m["stand_datum"]
        if m["le"]: d["grenze_le"] = True
        if not m["geprueft"]:                 # eingetragene Werte gelten erst als ok, wenn sie gegen das Dokument geprüft sind
            grund.append("noch nicht gegen das Dokument geprüft")
        d["status"] = "ok" if not grund else "pruefen"
        d["hinweis"] = "Werte aus Liste vom 04.11.2026 (Herkunft ungeklärt)" + (f" ({m['hinweis']})" if m["hinweis"] else "") + (("; Prüfung: " + "; ".join(grund)) if grund else "")
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
        ms, hsms = d.get("ms") or {}, d.get("hsms") or {}
        g = d.get("grenze_le", False)
        ct_ns = [ct_kwh_bei(ns, h, g) if d.get("rlm_ok") else None for h in TYPISCHE_STUNDEN]
        ct_ms = [ct_kwh_bei(ms, h, g) if len(ms) == 4 else None for h in TYPISCHE_STUNDEN]
        ct_mn = ct_kwh_bei(msns, 4000, g) if len(msns) == 4 else None
        hinweis = d.get("hinweis", "")
        return [d.get("mastr_nr", ""), d.get("nr", ""), d.get("netzbetreiber", ""), d.get("website", ""),
                d.get("bundesland", ""), d.get("region", ""), d.get("netztyp", ""), d.get("status", ""),
                zahl(slp.get("ap")), zahl(slp.get("gp")),
                *[zahl(ms.get(k)) for k in RLM], *[zahl(msns.get(k)) for k in RLM],
                *[zahl(ns.get(k)) for k in RLM], *[zahl(hsms.get(k)) for k in RLM],
                d.get("hsms_status", ""), ("≤ / >" if g else "< / ≥") if (ns or ms or msns) else "",
                *[zahl(round(c, 2)) if c is not None else "" for c in ct_ms],
                zahl(round(ct_mn, 2)) if ct_mn is not None else "",
                *[zahl(round(c, 2)) if c is not None else "" for c in ct_ns],
                *[(d.get("hlzf") or {}).get(c, "") for c in HLZF_COLS], (d.get("hlzf") or {}).get("hlzf_status", ""),
                d.get("preisstand", "") if (ns or slp or ms) else "", d.get("stand_datum", ""), hinweis,
                d.get("quelle_url", "")]

    @staticmethod
    def _stand_2026(d: dict, jahr: int) -> dict:
        """„vorläufig“ ist für 2026 überholt: Die Preise galten das ganze Jahr (Festlegung Nutzer 04.11.2026)."""
        if jahr == 2026 and d.get("preisstand") == "vorläufig":
            d = dict(d)
            d["preisstand"] = "endgültig"
            alt = d.get("hinweis", "")
            d["hinweis"] = "Dokument als vorläufig bezeichnet, Preise galten 2026 das ganze Jahr" + (f"; {alt}" if alt else "")
        elif jahr == 2026 and d.get("preisstand") == "unklar" and (d.get("ns") or d.get("slp")):
            d = dict(d)           # Blatt für 2026 gelesen, ohne Hinweis im Dokument: gilt als endgültig (Festlegung Nutzer 04.11.2026)
            d["preisstand"] = "endgültig"
        return d

    def ausgeben(self, jahr: int) -> str:
        zeilen = [self._stand_2026(d, jahr) for d in self.zeilen()]
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
                    w.writerow([d.get("mastr_nr", ""), d.get("nr", ""), d.get("netzbetreiber", ""),
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
