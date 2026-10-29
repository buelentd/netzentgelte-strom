"""Netzentgelt-Rechner für Gewerbe (netto, ohne Umlagen, Konzessionsabgabe, Messstellenbetrieb, USt).

Zwei Eingabewege, eine Berechnung:
  A. manuell:     berechnen(tarif, kwh, kw=None, branche=...)
  B. Lastprofil:  profil = lastprofil_lesen(datei); berechnen_aus_profil(tarif, profil)

Tarifwahl:
  - Jahresverbrauch < 100.000 kWh und keine Leistungsmessung: SLP = Grundpreis + AP × kWh
  - sonst RLM (Jahresleistungspreissystem), Ebene NS (Standard) oder MS/NS:
    Benutzungsstunden h = kWh / kW; h < 2.500 → Tarif "unter 2.500 h", sonst "ab 2.500 h"
    (bei Preisblättern mit "≤ 2.500 / > 2.500" gehört genau 2.500 h zu "unter").
    Netzentgelt € = LP × kW + AP × kWh / 100

Das Modul hat keine Abhängigkeiten außer der Standardbibliothek (openpyxl nur für xlsx).
"""
from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

GRENZE_H = 2500
SLP_GRENZE_KWH = 100_000
TYPISCHE_STUNDEN = (1500, 2500, 4000, 6000)
TZ = ZoneInfo("Europe/Berlin")

# Branchen-Standardwerte für Benutzungsstunden (Annahme, wenn keine Spitzenleistung bekannt ist)
BRANCHEN_STUNDEN = {
    "buero": 1500, "handwerk": 1500, "werkstatt": 1500, "schule": 1500,
    "imbiss": 2500, "baeckerei": 2500, "gastronomie": 2500, "restaurant": 2500, "einzelhandel": 2500,
    "hotel": 4000, "systemgastronomie": 4000, "fitnessstudio": 4000, "produktion_einschichtig": 2500,
    "produktion_zweischichtig": 4000, "supermarkt": 6000, "kuehlhaus": 6000, "rechenzentrum": 6000,
    "produktion_dreischichtig": 6000,
}

RLM_FELDER = ("lp_unter_2500", "ap_unter_2500", "lp_ueber_2500", "ap_ueber_2500")


def _de(v) -> float | None:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if not s:
        return None
    return float(s.replace(".", "").replace(",", ".")) if "," in s else float(s)


@dataclass
class Tarif:
    netzbetreiber: str = ""
    ns: dict = field(default_factory=dict)       # RLM_FELDER, LP €/kW/a, AP ct/kWh
    msns: dict = field(default_factory=dict)
    slp_ap: float | None = None                  # ct/kWh
    slp_gp: float | None = None                  # €/a
    grenze_le: bool = False                      # "≤ 2.500 / > 2.500" statt "< / ≥"
    preisstand: str = ""
    stand_datum: str = ""
    quelle_url: str = ""

    @classmethod
    def aus_zeile(cls, z: dict) -> "Tarif":
        """Aus einer Zeile von netzentgelte_2026.csv (Strings mit Dezimalkomma)."""
        def ebene(prefix):
            w = {}
            for f in RLM_FELDER:
                art, grenze = f.split("_", 1)
                einheit = "eur_kw_jahr" if art == "lp" else "ct_kwh"
                w[f] = _de(z.get(f"{prefix}_{art}_{grenze}h_{einheit}"))
            return w if all(v is not None for v in w.values()) else {}
        return cls(netzbetreiber=z.get("netzbetreiber", ""), ns=ebene("ns"), msns=ebene("msns"),
                   slp_ap=_de(z.get("slp_ap_ct_kwh")), slp_gp=_de(z.get("slp_grundpreis_eur_jahr")),
                   grenze_le="≤ 2.500" in (z.get("hinweis") or ""), preisstand=z.get("preisstand", ""),
                   stand_datum=z.get("stand_datum", ""), quelle_url=z.get("quelle_url", ""))


def gruppe(stunden: float, grenze_le: bool = False) -> str:
    """"unter" oder "ueber" laut Preisblatt-Regel."""
    if grenze_le:
        return "unter" if stunden <= GRENZE_H else "ueber"
    return "unter" if stunden < GRENZE_H else "ueber"


def ct_kwh_bei(werte: dict, stunden: float, grenze_le: bool = False) -> float | None:
    """Netzentgelt in ct/kWh bei gegebenen Benutzungsstunden: AP + LP × 100 / h (Tarif der passenden Gruppe)."""
    if not werte or stunden <= 0:
        return None
    g = gruppe(stunden, grenze_le)
    lp, ap = werte.get(f"lp_{g}_2500"), werte.get(f"ap_{g}_2500")
    if lp is None or ap is None:
        return None
    return ap + lp * 100 / stunden


def _rlm(werte: dict, kwh: float, kw: float, grenze_le: bool) -> dict:
    h = kwh / kw
    g = gruppe(h, grenze_le)
    lp, ap = werte[f"lp_{g}_2500"], werte[f"ap_{g}_2500"]
    leistung = lp * kw
    arbeit = ap * kwh / 100
    return {"gruppe": g, "stunden": h, "lp": lp, "ap": ap, "leistungsanteil_eur": leistung,
            "arbeitsanteil_eur": arbeit, "netzentgelt_eur": leistung + arbeit}


def _grenztext(grenze_le: bool, g: str) -> str:
    if grenze_le:
        return "bis 2.500 h" if g == "unter" else "über 2.500 h"
    return "unter 2.500 h" if g == "unter" else "ab 2.500 h"


def berechnen(tarif: Tarif, kwh: float, kw: float | None = None, *, leistungsmessung: bool | None = None,
              ebene: str = "NS", branche: str | None = None, stunden: float | None = None) -> dict:
    """Netzentgelt für einen Jahresverbrauch (kWh) und ggf. eine Jahreshöchstleistung (kW)."""
    if kwh is None or kwh <= 0:
        raise ValueError("Jahresverbrauch muss größer als 0 sein")
    annahmen, hinweise = [], []
    basis = {"netzbetreiber": tarif.netzbetreiber, "preisstand": tarif.preisstand,
             "stand_datum": tarif.stand_datum, "quelle_url": tarif.quelle_url, "kwh": kwh}
    if tarif.preisstand and tarif.preisstand != "endgültig":
        hinweise.append(f"Preisstand des Preisblatts: {tarif.preisstand}")

    rlm = bool(leistungsmessung) or kwh >= SLP_GRENZE_KWH
    if not rlm:
        if tarif.slp_ap is None or tarif.slp_gp is None:
            raise ValueError("SLP-Preise für diesen Netzbetreiber nicht verfügbar")
        arbeit = tarif.slp_ap * kwh / 100
        gesamt = tarif.slp_gp + arbeit
        return {**basis, "tarif": "SLP Niederspannung (ohne Leistungsmessung)",
                "begruendung": f"Jahresverbrauch {kwh:,.0f} kWh unter {SLP_GRENZE_KWH:,} kWh und keine "
                               f"Leistungsmessung".replace(",", "."),
                "netzentgelt_eur": gesamt, "ct_kwh": gesamt / kwh * 100, "grundpreis_eur": tarif.slp_gp,
                "arbeitsanteil_eur": arbeit, "leistungsanteil_eur": 0.0, "kw": kw, "benutzungsstunden": None,
                "ersparnis_je_kw_eur": 0.0, "tarifwechsel": None, "annahmen": annahmen, "hinweise": hinweise}

    werte = tarif.msns if ebene.upper().replace("/", "") == "MSNS" else tarif.ns
    ebene_name = "Umspannung MS/NS" if werte is tarif.msns else "Niederspannung"
    if not werte:
        raise ValueError(f"RLM-Preise {ebene_name} für diesen Netzbetreiber nicht verfügbar")
    if kw is None or kw <= 0:
        if stunden is None:
            if not branche or branche not in BRANCHEN_STUNDEN:
                raise ValueError("Spitzenleistung (kW) oder Branche/Benutzungsstunden angeben")
            stunden = BRANCHEN_STUNDEN[branche]
            annahmen.append(f"Benutzungsstunden {stunden:,} h als Branchen-Standardwert ({branche}) angenommen"
                            .replace(",", "."))
        else:
            annahmen.append(f"Benutzungsstunden {stunden:,.0f} h vorgegeben".replace(",", "."))
        kw = kwh / stunden
        annahmen.append(f"Jahreshöchstleistung daraus abgeleitet: {kw:,.1f} kW".replace(",", "X")
                        .replace(".", ",").replace("X", "."))
    r = _rlm(werte, kwh, kw, tarif.grenze_le)
    grund = (f"Benutzungsstunden {r['stunden']:,.0f} h → Tarif {_grenztext(tarif.grenze_le, r['gruppe'])}"
             .replace(",", "."))
    if kwh >= SLP_GRENZE_KWH:
        grund = f"Jahresverbrauch ab {SLP_GRENZE_KWH:,} kWh → RLM; ".replace(",", ".") + grund
    else:
        grund = "Leistungsmessung vorhanden → RLM; " + grund
    if abs(r["stunden"] - GRENZE_H) < 1:
        hinweise.append("Benutzungsstunden genau an der Grenze 2.500 h: Zuordnung laut Preisblatt-Regel "
                        + ("(≤ 2.500 h → unter)" if tarif.grenze_le else "(ab 2.500 h → über)"))
    return {**basis, "tarif": f"RLM {ebene_name}, Jahresleistungspreis {_grenztext(tarif.grenze_le, r['gruppe'])}",
            "begruendung": grund, "netzentgelt_eur": r["netzentgelt_eur"],
            "ct_kwh": r["netzentgelt_eur"] / kwh * 100, "grundpreis_eur": 0.0,
            "leistungsanteil_eur": r["leistungsanteil_eur"], "arbeitsanteil_eur": r["arbeitsanteil_eur"],
            "lp_eur_kw_jahr": r["lp"], "ap_ct_kwh": r["ap"], "kw": kw, "benutzungsstunden": r["stunden"],
            "ersparnis_je_kw_eur": r["lp"], "tarifwechsel": _tarifwechsel(werte, kwh, kw, tarif.grenze_le, r),
            "annahmen": annahmen, "hinweise": hinweise, "ebene": ebene_name}


def _tarifwechsel(werte, kwh, kw, grenze_le, r) -> dict | None:
    """Spitzenkappung, ab der die Benutzungsstunden in die Gruppe ab 2.500 h wechseln."""
    if r["gruppe"] != "unter":
        return None
    kw_grenze = kwh / GRENZE_H
    if grenze_le:
        kw_grenze *= 0.9999      # muss über 2.500 h liegen
    nachher = _rlm(werte, kwh, kw_grenze, grenze_le)
    return {"kappung_kw": kw - kw_grenze, "spitze_danach_kw": kw_grenze,
            "netzentgelt_danach_eur": nachher["netzentgelt_eur"],
            "ersparnis_eur": r["netzentgelt_eur"] - nachher["netzentgelt_eur"],
            "hinweis": f"Eine Spitzenkappung um {kw - kw_grenze:,.1f} kW hebt die Benutzungsstunden über "
                       f"2.500 h; dann gilt der Tarif ab 2.500 h (neu gerechnet)."
                       .replace(",", "X").replace(".", ",").replace("X", ".")}


def kappung(tarif: Tarif, kwh: float, kw: float, minus_kw: float, ebene: str = "NS") -> dict:
    """Ergebnis nach Senkung der Jahreshöchstleistung um minus_kw (Speicher, Lastmanagement)."""
    vorher = berechnen(tarif, kwh, kw, leistungsmessung=True, ebene=ebene)
    nachher = berechnen(tarif, kwh, kw - minus_kw, leistungsmessung=True, ebene=ebene)
    erg = {"vorher": vorher, "nachher": nachher, "ersparnis_eur": vorher["netzentgelt_eur"] - nachher["netzentgelt_eur"]}
    if vorher["tarif"] != nachher["tarif"]:
        erg["hinweis"] = (f"Tarifwechsel durch die Kappung: {vorher['tarif']} → {nachher['tarif']} "
                          f"(Benutzungsstunden {vorher['benutzungsstunden']:.0f} → {nachher['benutzungsstunden']:.0f} h)")
    return erg


# ====================================================================== Lastprofil

class RueckfrageNoetig(Exception):
    """Die Datei ist nicht eindeutig. Die Frage soll im UI gestellt werden, statt zu raten."""

    def __init__(self, frage: str, optionen: list[str]):
        super().__init__(frage)
        self.frage = frage
        self.optionen = optionen


@dataclass
class Profil:
    zeit_utc: list            # Intervallbeginn, timezone-aware UTC
    energie_kwh: list         # Energie je Intervall
    intervall_min: int
    einheit: str              # Einheit der Datei: "kW" oder "kWh"
    hinweise: list = field(default_factory=list)


_ZEIT_FORMATE = ["%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M", "%d.%m.%y %H:%M", "%Y-%m-%d %H:%M:%S",
                 "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%d/%m/%Y %H:%M", "%Y/%m/%d %H:%M"]
_DATUM_FORMATE = ["%d.%m.%Y", "%d.%m.%y", "%Y-%m-%d", "%d/%m/%Y"]
_UHRZEIT_FORMATE = ["%H:%M:%S", "%H:%M"]


def _zeit(s) -> datetime | None:
    if isinstance(s, datetime):
        return s
    if s is None:
        return None
    s = str(s).strip()
    if not s or not re.search(r"\d", s):
        return None
    plus_tag = False
    if re.search(r"\b24:00(:00)?$", s):
        s = re.sub(r"\b24:00(:00)?$", "00:00", s)
        plus_tag = True
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return d + timedelta(days=1) if plus_tag else d
    except ValueError:
        pass
    for f in _ZEIT_FORMATE + _DATUM_FORMATE:
        try:
            d = datetime.strptime(s, f)
            return d + timedelta(days=1) if plus_tag else d
        except ValueError:
            continue
    return None


def _uhrzeit(s):
    if s is None:
        return None
    if hasattr(s, "hour") and not isinstance(s, datetime):
        return s
    s = str(s).strip()
    if s in ("24:00", "24:00:00"):
        return "24"
    for f in _UHRZEIT_FORMATE:
        try:
            return datetime.strptime(s, f).time()
        except ValueError:
            continue
    return None


def _zeilen_lesen(daten: bytes, dateiname: str) -> list[list]:
    if daten[:2] == b"PK" or dateiname.lower().endswith((".xlsx", ".xlsm")):
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(daten), data_only=True, read_only=True)
        ws = wb.worksheets[0]
        return [list(r) for r in ws.iter_rows(values_only=True)]
    for enc in ("utf-8-sig", "cp1252"):
        try:
            text = daten.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    probe = "\n".join(text.splitlines()[:50])
    trenner = max([";", "\t", ","], key=lambda t: sum(z.count(t) for z in probe.splitlines()))
    return [r for r in csv.reader(io.StringIO(text), delimiter=trenner)]


def _dezimal(werte: list[str]) -> str:
    komma = sum(1 for w in werte if re.fullmatch(r"-?[\d.]*\d,\d+", w))
    punkt = sum(1 for w in werte if re.fullmatch(r"-?[\d,]*\d\.\d+", w))
    return "," if komma >= punkt else "."


def _num(v, dezimal: str) -> float | None:
    if v is None or isinstance(v, datetime):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(" ", "").replace(" ", "")
    if not s:
        return None
    if dezimal == ",":
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def _einheit_aus_kopf(kopf: str):
    """(einheit, faktor) aus dem Spaltenkopf, None wenn nicht erkennbar."""
    k = kopf.lower()
    for muster, einheit, faktor in ((r"\bmwh\b", "kWh", 1000.0), (r"\bkwh\b", "kWh", 1.0), (r"\bwh\b", "kWh", 0.001),
                                    (r"\bmw\b", "kW", 1000.0), (r"\bkw\b", "kW", 1.0), (r"\bw\b", "kW", 0.001)):
        if re.search(muster, k):
            return einheit, faktor
    if re.search(r"leistung", k):
        return "kW", 1.0
    if re.search(r"energie|arbeit|energiemenge", k):
        return "kWh", 1.0
    return None


def lastprofil_lesen(quelle, dateiname: str = "", einheit: str | None = None,
                     jahresverbrauch_kwh: float | None = None) -> Profil:
    """Liest ein Lastprofil (CSV/xlsx, Viertelstunden- oder Stundenwerte).

    einheit: "kW" oder "kWh" erzwingen (Antwort auf eine Rückfrage).
    jahresverbrauch_kwh: optionaler Vergleichswert (z. B. Rechnung) zur Einheiten-Erkennung.
    """
    if isinstance(quelle, (str, Path)):
        dateiname = dateiname or str(quelle)
        daten = Path(quelle).read_bytes()
    else:
        daten = quelle
    zeilen = _zeilen_lesen(daten, dateiname)
    hinweise = []

    # Datenzeilen: Zeitstempel (eine Spalte oder Datum + Uhrzeit) und mindestens ein Zahlwert
    def zeit_in(z):
        if not z:
            return None, 0
        t = _zeit(z[0])
        if t is not None and len(z) > 1:
            u = _uhrzeit(z[1])
            if u is not None and t.hour == 0 and t.minute == 0 and not isinstance(z[0], datetime) \
                    and re.fullmatch(r"[\d./-]+", str(z[0]).strip()):
                if u == "24":
                    return t + timedelta(days=1), 2
                return datetime.combine(t.date(), u), 2
            if isinstance(z[0], datetime) and u is not None and z[0].hour == 0 and z[0].minute == 0 \
                    and not isinstance(z[1], (int, float)):
                return (t + timedelta(days=1)) if u == "24" else datetime.combine(t.date(), u), 2
        return t, 1

    erste = None
    for i, z in enumerate(zeilen):
        t, n = zeit_in(z)
        if t is not None and any(_num(v, ",") is not None or _num(v, ".") is not None for v in z[n:]):
            erste = i
            break
    if erste is None:
        raise ValueError("Keine Zeilen mit Zeitstempel und Wert gefunden")
    kopf = [str(v or "") for v in zeilen[erste - 1]] if erste > 0 else []
    daten_zeilen = [z for z in zeilen[erste:] if z and zeit_in(z)[0] is not None]
    _, n_zeit = zeit_in(daten_zeilen[0])

    # Wertspalte: Kopf mit Einheit/Stichwort bevorzugen, sonst erste Zahlenspalte
    breite = max(len(z) for z in daten_zeilen)
    kandidaten = []
    for c in range(n_zeit, breite):
        roh = [z[c] for z in daten_zeilen[:500] if c < len(z)]
        texte = [str(v).strip() for v in roh if v not in (None, "")]
        dez = _dezimal([t for t in texte if not isinstance(t, float)])
        zahlen = [_num(v, dez) for v in roh]
        if texte and sum(x is not None for x in zahlen) >= 0.9 * len(texte):
            kandidaten.append(c)
    if not kandidaten:
        raise ValueError("Keine Wertspalte gefunden")
    mit_einheit = [c for c in kandidaten if c < len(kopf) and _einheit_aus_kopf(kopf[c])]
    spalte = mit_einheit[0] if mit_einheit else kandidaten[0]
    if len(kandidaten) > 1:
        hinweise.append(f"Mehrere Zahlenspalten, verwendet: {kopf[spalte] if spalte < len(kopf) else spalte + 1}")
    kopf_text = kopf[spalte] if spalte < len(kopf) else ""
    if n_zeit == 1 and kopf and re.search(r"\bbis\b|ende", str(kopf[0]).lower()):
        zeit_ist_ende = True
    else:
        zeit_ist_ende = False

    texte = [str(z[spalte]).strip() for z in daten_zeilen if spalte < len(z) and not isinstance(z[spalte], (int, float))]
    dez = _dezimal(texte)
    lokal, werte = [], []
    for z in daten_zeilen:
        t, _ = zeit_in(z)
        v = _num(z[spalte], dez) if spalte < len(z) else None
        if v is None:
            continue
        lokal.append(t)
        werte.append(v)

    # Zeitzone: naive Zeitstempel sind Europe/Berlin; doppelte Stunde (Oktober) über fold auflösen
    utc, gesehen, nicht_existent = [], set(), 0
    for t in lokal:
        if t.tzinfo is not None:
            utc.append(t.astimezone(timezone.utc))
            continue
        fold = 1 if t in gesehen else 0
        gesehen.add(t)
        a = t.replace(tzinfo=TZ, fold=fold)
        u = a.astimezone(timezone.utc)
        if u.astimezone(TZ).replace(tzinfo=None) != t:
            nicht_existent += 1
        utc.append(u)
    if nicht_existent:
        hinweise.append(f"{nicht_existent} Zeitstempel in der bei der Umstellung auf Sommerzeit ausgelassenen "
                        f"Stunde; Werte mitgezählt")

    diffs = sorted((b - a).total_seconds() / 60 for a, b in zip(utc, utc[1:]) if b > a)
    if not diffs:
        raise ValueError("Zu wenige Werte")
    intervall = int(round(diffs[len(diffs) // 2]))
    if intervall not in (5, 10, 15, 30, 60):
        hinweise.append(f"Ungewöhnliches Intervall {intervall} min")
    if zeit_ist_ende:
        utc = [u - timedelta(minutes=intervall) for u in utc]
    dt_h = intervall / 60

    # Einheit: Kopf, sonst Vorgabe, sonst Vergleich mit Jahresverbrauch, sonst Rückfrage
    erkannt = _einheit_aus_kopf(kopf_text)
    faktor = 1.0
    if einheit:
        einheit = "kWh" if einheit.lower() == "kwh" else "kW"
        if erkannt:
            faktor = erkannt[1]
    elif erkannt:
        einheit, faktor = erkannt
    elif jahresverbrauch_kwh:
        abdeckung = len(werte) * dt_h / 8760
        als_kwh = sum(werte) / abdeckung
        als_kw = sum(werte) * dt_h / abdeckung
        nah = lambda x: abs(x - jahresverbrauch_kwh) / jahresverbrauch_kwh  # noqa: E731
        if min(nah(als_kwh), nah(als_kw)) < 0.25 and abs(nah(als_kwh) - nah(als_kw)) > 0.25:
            einheit = "kWh" if nah(als_kwh) < nah(als_kw) else "kW"
            hinweise.append(f"Einheit {einheit} über den angegebenen Jahresverbrauch erkannt")
    if not einheit:
        raise RueckfrageNoetig(
            f"Sind die Werte in Spalte \"{kopf_text or spalte + 1}\" Leistung (kW) oder Energie je "
            f"{intervall}-Minuten-Intervall (kWh)?", ["kW", "kWh"])
    werte = [v * faktor for v in werte]
    energie = [v * dt_h for v in werte] if einheit == "kW" else werte
    return Profil(zeit_utc=utc, energie_kwh=energie, intervall_min=intervall, einheit=einheit, hinweise=hinweise)


def kennzahlen(p: Profil) -> dict:
    """Jahresverbrauch, Jahreshöchstleistung (Viertelstundenmittel), Benutzungsstunden, Datenqualität."""
    hinweise = list(p.hinweise)
    paare = sorted(zip(p.zeit_utc, p.energie_kwh))
    # länger als ein Jahr: die letzten 12 Monate
    if paare and paare[-1][0] - paare[0][0] > timedelta(days=366):
        ab = paare[-1][0] - timedelta(days=365) + timedelta(minutes=p.intervall_min)
        paare = [x for x in paare if x[0] >= ab]
        hinweise.append("Profil länger als ein Jahr: die letzten 12 Monate verwendet")
    dt = timedelta(minutes=p.intervall_min)

    # Viertelstunden bilden (feinere Intervalle summieren)
    if p.intervall_min < 15:
        bins = {}
        for t, e in paare:
            b = t.replace(minute=t.minute - t.minute % 15, second=0, microsecond=0)
            bins[b] = bins.get(b, 0) + e
        leistung = [(t, e * 4) for t, e in sorted(bins.items())]
    else:
        leistung = [(t, e / (p.intervall_min / 60)) for t, e in paare]
    if p.intervall_min > 15:
        hinweise.append(f"{p.intervall_min}-Minuten-Werte: Die Viertelstundenspitze liegt meist höher, "
                        f"der Leistungspreis wird unterschätzt")

    gemessen = sum(e for _, e in paare)
    spitze_t, spitze = max(leistung, key=lambda x: x[1])
    eindeutig = sorted({t for t, _ in paare})
    spanne = (eindeutig[-1] - eindeutig[0]) + dt
    erwartet = int(round(spanne / dt))
    luecken = max(0, erwartet - len(eindeutig))
    abgedeckt_h = len(eindeutig) * p.intervall_min / 60
    groesste = max(((b - a - dt, a) for a, b in zip(eindeutig, eindeutig[1:])), default=(timedelta(0), None))
    if luecken:
        hinweise.append(f"{luecken} fehlende Intervalle"
                        + (f", größte Lücke {groesste[0]} ab {groesste[1].astimezone(TZ):%d.%m.%Y %H:%M}"
                           if groesste[1] is not None and groesste[0] > timedelta(0) else ""))
    if len(eindeutig) < len(paare):
        hinweise.append(f"{len(paare) - len(eindeutig)} doppelte Zeitstempel")

    werte = sorted(w for _, w in leistung)
    p99 = werte[int(0.99 * (len(werte) - 1))] if werte else 0
    negativ = sum(1 for w in werte if w < 0)
    ausreisser = [(t, w) for t, w in leistung if p99 > 0 and w > 5 * p99]
    if negativ:
        hinweise.append(f"{negativ} negative Werte (Einspeisung?)")
    if ausreisser:
        hinweise.append("Mögliche Ausreißer: " + ", ".join(
            f"{t.astimezone(TZ):%d.%m.%Y %H:%M} {w:.1f} kW" for t, w in ausreisser[:3]))

    jahr_h = 8760
    hochrechnung = abgedeckt_h < jahr_h * 0.99
    faktor = jahr_h / abgedeckt_h if hochrechnung else 1.0
    jahres_kwh = gemessen * faktor
    if hochrechnung:
        hinweise.append(f"HOCHRECHNUNG: Profil deckt {abgedeckt_h / 24:.0f} Tage ab, Verbrauch auf 12 Monate "
                        f"hochgerechnet (Faktor {faktor:.2f}); die Jahresspitze kann höher liegen")
    return {"jahresverbrauch_kwh": jahres_kwh, "gemessen_kwh": gemessen, "spitze_kw": spitze,
            "spitze_zeit": spitze_t.astimezone(TZ).strftime("%d.%m.%Y %H:%M"),
            "benutzungsstunden": jahres_kwh / spitze if spitze > 0 else None,
            "abgedeckte_tage": abgedeckt_h / 24, "hochrechnung": hochrechnung, "hochrechnung_faktor": faktor,
            "luecken": luecken, "intervall_min": p.intervall_min, "hinweise": hinweise}


def berechnen_aus_profil(tarif: Tarif, profil: Profil, *, ebene: str = "NS",
                         leistungsmessung: bool | None = True) -> dict:
    """Wie berechnen(), Kennzahlen aus dem Lastprofil. Ein Lastgang setzt meist RLM-Messung voraus."""
    k = kennzahlen(profil)
    erg = berechnen(tarif, k["jahresverbrauch_kwh"], k["spitze_kw"], leistungsmessung=leistungsmessung, ebene=ebene)
    erg["kennzahlen"] = k
    erg["spitze_zeit"] = k["spitze_zeit"]
    erg["hinweise"] = k["hinweise"] + erg["hinweise"]
    return erg


def tabelle_ct_kwh(werte: dict, grenze_le: bool = False, stunden=TYPISCHE_STUNDEN) -> dict:
    return {h: ct_kwh_bei(werte, h, grenze_le) for h in stunden}


__all__ = ["Tarif", "berechnen", "berechnen_aus_profil", "kappung", "lastprofil_lesen", "kennzahlen",
           "ct_kwh_bei", "gruppe", "RueckfrageNoetig", "BRANCHEN_STUNDEN", "TYPISCHE_STUNDEN"]
