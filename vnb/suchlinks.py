"""Suchlinks für den Browser nach dem NAMEN des Netzbetreibers (Festlegung Nutzer 12.11.2026), nicht nach der Domain.
Die Domain aus dem MaStR ist oft falsch oder eine Weiterleitung (Putzbrunn .com/.de). Mehrere Schreibweisen: voller Name,
Kernname ohne Rechtsform (GmbH, AG, KG, eG, e.K. ...), Kernname mit "Netz"."""
import re
import urllib.parse

RECHTSFORM = re.compile(r"\b(GmbH\s*(?:[&＆]|und)\s*Co\.?\s*(?:KG|OHG)?|GmbH|mbH|AG|KG|OHG|UG|SE|e\.\s?G\.?|eG|e\.\s?K\.?|e\.\s?V\.?|"
                        r"Anstalt des öffentlichen Rechts|AöR|Co\.)(?=\W|$)", re.I)


def voller_name(name: str) -> str:
    return re.sub(r"\s+", " ", (name or "").replace("＆", "&").replace("´", "'")).strip()


def kernname(name: str) -> str:
    n = RECHTSFORM.sub(" ", voller_name(name))
    n = re.sub(r"\(.*?\)", " ", n)            # Klammerzusätze
    return re.sub(r"\s+", " ", n).strip(" ,.-&")


def suchbegriffe(name: str, thema: str = "Hochlastzeitfenster 2026") -> list[str]:
    voll, kern = voller_name(name), kernname(name)
    netz = kern if "netz" in kern.lower() else kern + " Netz"
    b = [f"{voll} {thema}", f"{kern} {thema} § 19 StromNEV atypische Netznutzung", f"{netz} {thema} pdf"]
    return list(dict.fromkeys(b))


def links(name: str, thema: str = "Hochlastzeitfenster 2026") -> list[str]:
    return ["https://www.google.com/search?q=" + urllib.parse.quote(b) for b in suchbegriffe(name, thema)]
