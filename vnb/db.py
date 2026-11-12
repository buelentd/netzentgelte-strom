"""Zugriffsschicht auf die Netzentgelt-Daten ("fiktive Datenbank").

Der Rechner liest alle Werte nur hierüber. Heute steht dahinter eine CSV (`ergebnis/netzentgelte_2026.csv`,
eine Zeile je Netzbetreiber mit allen Werten); später kann dieselbe Schnittstelle auf eine echte Datenbank zeigen.
Ein Wert, der nicht vorliegt, ist immer `None`; der Rechner zeigt dann "Werte nicht vorhanden".
"""
import csv
from pathlib import Path

CSV = Path(__file__).resolve().parent.parent / "ergebnis" / "netzentgelte_2026.csv"
NICHT_VORHANDEN = "Werte nicht vorhanden"
RLM = ("lp_unter_2500h_eur_kw_jahr", "ap_unter_2500h_ct_kwh", "lp_ab_2500h_eur_kw_jahr", "ap_ab_2500h_ct_kwh")
EBENEN = ("ns", "msns", "ms", "hsms")
JAHRESZEITEN = ("fruehling", "sommer", "herbst", "winter")


def de(v):
    v = (v or "").strip()
    return float(v.replace(".", "").replace(",", ".")) if v else None


class Db:
    def __init__(self, pfad=CSV):
        with open(pfad, encoding="utf-8-sig") as f:
            self._zeilen = {r["nr"]: r for r in csv.DictReader(f, delimiter=";")}

    def alle(self):
        return [self.netzbetreiber(nr) for nr in self._zeilen]

    def roh(self, nr):
        return self._zeilen.get(str(nr))

    def netzbetreiber(self, nr) -> dict | None:
        """Alle Werte eines Netzbetreibers; Fehlendes ist None. `fehlt` nennt die Bereiche ohne Werte."""
        r = self.roh(nr)
        if r is None:
            return None
        d = {"nr": int(r["nr"]), "name": r["netzbetreiber"], "mastr_nr": r["mastr_nr"], "bundesland": r["bundesland"],
             "status": r["status"], "preisstand": r["preisstand"], "stand_datum": r["stand_datum"],
             "grenze_le": r.get("grenze_2500h", "").startswith("≤") or "≤ 2.500" in r["hinweis"],
             "quelle_url": r["quelle_url"], "hinweis": r["hinweis"]}
        slp = (de(r["slp_ap_ct_kwh"]), de(r["slp_grundpreis_eur_jahr"]))
        d["slp"] = list(slp) if None not in slp else None
        for eb in EBENEN:
            w = [de(r.get(f"{eb}_{k}")) for k in RLM]
            d[eb] = w if None not in w else None
        d["hlzf"] = self._hlzf(r)
        d["hlzf_msns"] = self._hlzf(r, "msns")      # Fenster der Ebene Umspannung MS/NS, falls gelesen
        d["fehlt"] = [n for n, v in (("SLP", d["slp"]), ("Niederspannung", d["ns"]), ("MS/NS", d["msns"]),
                                     ("Mittelspannung", d["ms"]), ("Hochlastzeitfenster", d["hlzf"])) if v is None]
        d["vollstaendig"] = all(d[k] for k in ("slp", "ns", "msns", "ms"))
        d["geprueft"] = r["status"] == "ok"
        return d

    @staticmethod
    def _hlzf(r, ebene="ns"):
        if r.get("hlzf_status") not in ("gelesen_nutzer", "gelesen_unser", "gelesen_kollege_verifiziert", "gelesen_aus_2027"):
            return None                          # ungeprüft gelesene Fenster (gelesen_ungeprueft) gehen nicht in den Rechner
        f = {}
        for j in JAHRESZEITEN:
            t = (r.get(f"hlzf_{ebene}_{j}") or "").strip()
            if not t:
                return None                      # nicht alle vier Jahreszeiten gelesen: Werte nicht vorhanden
            f[j] = [] if t == "keins" else [x.strip() for x in t.split(",")]
        s = r.get("hlzf_schwelle_prozent", "")
        m = r.get("hlzf_mindestleistung_kw", "")
        return {"fenster": f, "schwelle": int(de(s)) if s else None, "mindestleistung": int(de(m)) if m else None,
                "quelle_url": r.get("hlzf_quelle_url", "")}

    def plz(self, pfad=None):
        """PLZ -> [(nr, Anteil %)] aus ergebnis/plz_netzbetreiber.csv (nur Betreiber aus der Tabelle)."""
        pfad = pfad or CSV.parent / "plz_netzbetreiber.csv"
        nr_von_mastr = {}
        for nr, r in self._zeilen.items():
            nr_von_mastr.setdefault(r["mastr_nr"], int(nr))
        aus = {}
        with open(pfad, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f, delimiter=";"):
                nr = nr_von_mastr.get(r["mastr_nr"])
                if nr and nr not in [x[0] for x in aus.setdefault(r["plz"], [])]:
                    aus[r["plz"]].append((nr, de(r["anteil_prozent"])))
        return aus
