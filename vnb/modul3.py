"""Modul 3 (§ 14a EnWG, zeitvariable Netzentgelte): HT-/ST-/NT-Zeiten und Quartale aus dem Layout-Text eines Preisblatts (0 Tokens).
Nur eindeutige Fälle werden gelesen: (A) Zeile mit Tarifname und Zeit, (B) Kopfzeile mit Tarifnamen und Zeiten darunter in derselben Spalte.
Alles andere: Ergebnis None und Ausschnitt für die Prüfliste. Nichts wird geraten. Preise kommen nicht von hier (daten/modul_messentgelte.py)."""
import re

ZEIT = re.compile(r"(?<!\d)(\d{1,2})[:.](\d{2})\s*(?:uhr)?\s*(?:[-–−]|bis)\s*(\d{1,2})[:.](\d{2})\s*(?:uhr)?(?!\d)", re.I)
HT = re.compile(r"hochlast(?:tarif)?|hochtarif|hoch-?tarif|\bHT\b", re.I)
NT = re.compile(r"niedriglast(?:tarif)?|niedertarif|niedrigtarif|\bNT\b", re.I)
ST = re.compile(r"standardlast(?:tarif)?|standardtarif|\bST\b", re.I)
REST = re.compile(r"restliche|restzeit|übrige|uebrige|alle anderen|sonstige zeit", re.I)
JAHRESZEIT = re.compile(r"frühling|fruehling|sommer|herbst|winter", re.I)
MODUL = re.compile(r"modul\s*(?:1\s*(?:\+|i\.?v\.?m\.?|und|u\.)\s*)?3|zeitvariabl", re.I)


def norm(m):
    a, b, c, d = (int(x) for x in m.groups())
    if a > 24 or c > 24 or b > 59 or d > 59 or (a == 24 and b):
        return None
    return f"{a:02d}:{b:02d}-{c:02d}:{d:02d}"


def quartale(text):
    """Quartals-Angabe in einer Zeile -> sortierte Menge 1..4 oder None."""
    t = text.lower()
    if re.search(r"quartale?\s*(?:i\s*,\s*ii\s*,\s*iii\s*(?:und|,)\s*iv|1\s*[-–bis]+\s*4|1\s*,\s*2\s*,\s*3\s*(?:und|,)\s*4)", t) or "ganzjähr" in t or "ganzjaehr" in t:
        return (1, 2, 3, 4)
    m = re.search(r"quartale?\s*([1-4](?:\s*(?:,|und|\+|/)\s*[1-4])*)", t) or re.search(r"([1-4](?:\s*(?:,|und|\+|/)\s*[1-4])*)\s*\.?\s*quartale?", t)
    if m:
        return tuple(sorted({int(x) for x in re.findall(r"[1-4]", m.group(1))}))
    m = re.search(r"\bq\s*([1-4])\s*(?:[-–]\s*q?\s*([1-4])|((?:\s*(?:\+|,|und|/)\s*q?\s*[1-4])+))", t)
    if m:
        if m.group(2):
            return (1, 2, 3, 4) if (m.group(1), m.group(2)) == ("1", "4") else None
        return tuple(sorted({int(x) for x in re.findall(r"[1-4]", m.group(1) + m.group(3))}))
    r = {"i": 1, "ii": 2, "iii": 3, "iv": 4}
    m = re.search(r"quartale?\s*((?:i{1,3}|iv)(?:\s*(?:,|und|\+)\s*(?:i{1,3}|iv))*)\b", t)
    if m:
        return tuple(sorted({r[x] for x in re.findall(r"iv|iii|ii|i", m.group(1))}))
    return None


def blocks(L):
    """Zeilenbereiche, die zu Modul 3 gehören (ab Treffer 14 Zeilen), Jahreszeit-Tabellen (§ 19) ausgeschlossen."""
    idx = [i for i, l in enumerate(L) if MODUL.search(l)]
    keep = set()
    for i in idx:
        keep.update(range(max(0, i - 2), min(len(L), i + 16)))
    return sorted(keep)


def _lesen_roh(text):
    """Rückgabe (ergebnis, grund). ergebnis = {'quartale': {gruppe: {'ht': [...], 'st': [...], 'nt': [...]}}} oder None."""
    L = text.split("\n")
    B = blocks(L)
    if not B:
        return None, "kein Modul-3-Abschnitt"
    erg, fehler = {}, 0

    def add(q, art, wert):
        g = erg.setdefault(q or (1, 2, 3, 4), {"ht": [], "st": [], "nt": []})
        if wert not in g[art]:
            g[art].append(wert)

    # (A) Zeilenmodus
    ctx = None
    for i in B:
        l = L[i]
        if JAHRESZEIT.search(l):
            continue
        q = quartale(l)
        if q:
            ctx = q
        zs = [z for z in (norm(m) for m in ZEIT.finditer(l)) if z]
        arten = [a for a, rx in (("ht", HT), ("nt", NT), ("st", ST)) if rx.search(l)]
        rest = REST.search(l)
        if len(arten) == 1 and zs:
            for z in zs:
                add(q or ctx, arten[0], z)
        elif len(arten) == 1 and rest and arten[0] == "st":
            add(q or ctx, "st", "Restzeit")
        elif not arten and rest and not zs and re.search(r"\d,\d", l):
            add(q or ctx, "st", "Restzeit")
        elif len(arten) > 1 and zs:
            fehler += 1
    if erg and not fehler and not pruefen({"quartale": erg}):
        return {"quartale": erg}, "zeilenweise"
    erg.clear()

    # (D) Zeilengruppe: Tarifname in einer Zeile, weitere Zeiten in den Folgezeilen darunter (nur Zeiten, nichts anderes)
    ctx, cur, fehler = None, None, 0
    for i in B:
        l = L[i]
        if JAHRESZEIT.search(l):
            cur = None
            continue
        q = quartale(l)
        if q:
            ctx = q
        zs = [z for z in (norm(m) for m in ZEIT.finditer(l)) if z]
        arten = [a for a, rx in (("ht", HT), ("nt", NT), ("st", ST)) if rx.search(l)]
        if len(arten) == 1:
            cur = arten[0]
            for z in zs:
                add(q or ctx, cur, z)
        elif len(arten) > 1:
            cur = None
            fehler += bool(zs)
        elif cur and zs and not re.search(r"[a-zA-Z]{4,}", ZEIT.sub("", l)) :
            for z in zs:
                add(q or ctx, cur, z)
        else:
            cur = None
        if REST.search(l) and not zs and cur is None:
            pass
    if erg and not fehler and not pruefen({"quartale": erg}):
        return {"quartale": erg}, "zeilengruppe"
    erg.clear()

    # (B) Spaltenmodus: Kopfzeile mit mindestens zwei Tarifnamen, Zeiten in den Zeilen darunter
    fehler = 0
    for i in B:
        l = L[i]
        pos = {}
        for a, rx in (("ht", HT), ("nt", NT), ("st", ST)):
            m = rx.search(l)
            if m:
                pos[a] = (m.start() + m.end()) // 2
        if len(pos) < 3:
            continue
        ctx = quartale(" ".join(L[max(0, i - 3): i + 1])) or None
        for j in range(i + 1, min(len(L), i + 7)):
            if not L[j].strip() and j > i + 2:
                break
            if JAHRESZEIT.search(L[j]):
                break
            q = quartale(L[j]) or ctx
            for m in ZEIT.finditer(L[j]):
                z = norm(m)
                c = (m.start() + m.end()) // 2
                a = min(pos, key=lambda k: abs(pos[k] - c))
                if not z or abs(pos[a] - c) > 30:
                    fehler += 1
                    continue
                add(q, a, z)
            if REST.search(L[j]):
                m = REST.search(L[j])
                a = min(pos, key=lambda k: abs(pos[k] - m.start()))
                add(q, a, "Restzeit") if a == "st" else None
        if erg and not fehler and not pruefen({"quartale": erg}):
            return {"quartale": erg}, "spaltenweise"
        erg.clear()
    return None, "Zuordnung zu HT/ST/NT nicht eindeutig"


def minuten(z):
    a, b = z.split("-")
    f = lambda x: int(x[:2]) * 60 + int(x[3:])
    s, e = f(a), f(b)
    return set(range(s, e)) if e > s else set(range(s, 1440)) | set(range(0, e))


def pruefen(erg):
    """Plausibilität: Quartalsgruppen überschneiden sich nicht und decken Q1-4 ab; je Gruppe keine Überlappung HT/ST/NT,
    HT und NT nicht leer; mit ausdrücklichen ST-Zeiten (ohne 'Restzeit') decken die drei genau 24 Stunden ab. -> Fehlertext oder None."""
    q = erg["quartale"]
    alle = [x for g in q for x in g]
    if sorted(alle) != [1, 2, 3, 4]:
        return "Quartale lückenhaft oder überlappend"
    for g, v in q.items():
        if not v["ht"] or not v["nt"]:
            return "HT oder NT ohne Zeit"
        m = {a: set() for a in v}
        for a in v:
            for z in v[a]:
                if z == "Restzeit":
                    continue
                zz = minuten(z)
                if zz & set().union(*[m[b] for b in v if b != a]) or zz & m[a]:
                    return "Zeiten überlappen"
                m[a] |= zz
        if "Restzeit" not in v["st"]:
            if len(m["ht"] | m["st"] | m["nt"]) != 1440:
                return "Zeiten decken nicht 24 Stunden"
        elif v["st"] != ["Restzeit"] and len(v["st"]) > 1:
            return "ST gemischt"
    return None


def formatieren(erg):
    """-> (ht, st, nt, quartale) als Text; bei je Quartal verschiedenen Zeiten 'Q1+Q4: …; Q2+Q3: …'."""
    q = erg["quartale"]
    name = lambda g: "+".join(f"Q{x}" for x in g) if g != (1, 2, 3, 4) else "ganzjährig"
    if len(q) == 1:
        g = next(iter(q.values()))
        return ", ".join(g["ht"]), ", ".join(g["st"]), ", ".join(g["nt"]), name(next(iter(q)))
    teile = {a: "; ".join(f"{name(k)}: {', '.join(v[a]) or 'keins'}" for k, v in sorted(q.items())) for a in ("ht", "st", "nt")}
    return teile["ht"], teile["st"], teile["nt"], "; ".join(name(k) for k in sorted(q))


def lesen(text):
    """Wie _lesen_roh, zusätzlich: Quartalsangaben im Abschnitt (z. B. 'AP gilt nur in Q1 + Q4') werden berücksichtigt;
    widersprüchliche Angaben -> nicht lesbar."""
    erg, grund = _lesen_roh(text)
    if not erg:
        return erg, grund
    L = text.split("\n")
    qs = set()
    for i in blocks(L):
        l = L[i]
        mehrfach = len(re.findall(r"quartal", l, re.I)) >= 2 or len(re.findall(r"\bq[1-4]\s*:", l, re.I)) >= 2
        if mehrfach and quartale(l) != (1, 2, 3, 4):
            return None, "Quartalstabelle im Abschnitt, nicht eindeutig"
        if not mehrfach:
            qs.add(quartale(l))
    qs -= {None}
    if len(erg["quartale"]) == 1 and next(iter(erg["quartale"])) == (1, 2, 3, 4):
        qs -= {(1, 2, 3, 4)}
        if len(qs) == 1:
            g = erg["quartale"].pop((1, 2, 3, 4))
            erg["quartale"][next(iter(qs))] = g
        elif len(qs) > 1:
            return None, "widersprüchliche Quartalsangaben"
    elif qs - set(erg["quartale"]) - {(1, 2, 3, 4)}:
        return None, "widersprüchliche Quartalsangaben"
    return erg, grund
