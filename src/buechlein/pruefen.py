"""Prüft die Texte und schreibt den Bericht als Markdown-Tabelle."""

from dataclasses import dataclass

from buechlein.buch import Buch, Reihenfolge
from buechlein.konvertieren import Text


@dataclass(frozen=True)
class Befund:
    text: Text
    warnungen: list[str]


def pruefen(text: Text, buch: Buch, reihenfolge: Reihenfolge) -> Befund:
    warnungen = []
    if text.zeichen > buch.max_zeichen:
        warnungen.append(f"zu lang ({text.zeichen} statt höchstens {buch.max_zeichen} Zeichen)")
    if not text.titel:
        warnungen.append("Titel fehlt")
    if not text.autor:
        warnungen.append("Autor fehlt")
    if text.leere_absaetze:
        warnungen.append(f"{text.leere_absaetze} leere Absätze")
    if text.hat_aenderungen:
        warnungen.append("enthält nachverfolgte Änderungen (in Word annehmen und neu speichern)")
    if text.name in reihenfolge.nicht_aufgefuehrt:
        warnungen.append("steht nicht in buch.yaml")
    return Befund(text, warnungen)


def allgemeine_warnungen(reihenfolge: Reihenfolge) -> list[str]:
    return [
        f"buch.yaml nennt «{name}», aber texte/{name}.docx fehlt" for name in reihenfolge.ohne_datei
    ]


def bericht(befunde: list[Befund], allgemein: list[str], buch: Buch) -> str:
    zeilen = [
        "## Prüfbericht",
        "",
        f"Höchstlänge: {buch.max_zeichen} Zeichen (mit Leerzeichen, inkl. Titel, Untertitel, "
        "Autor und Fussnoten).",
        "",
        "| Text | Autor | Zeichen | Status |",
        "| --- | --- | ---: | --- |",
    ]
    for befund in befunde:
        text = befund.text
        status = "⚠️ " + "; ".join(befund.warnungen) if befund.warnungen else "✅ in Ordnung"
        zeilen.append(
            f"| {text.titel or text.name} | {text.autor or '–'} | {text.zeichen} | {status} |"
        )
    if allgemein:
        zeilen += ["", *(f"- ⚠️ {warnung}" for warnung in allgemein)]
    anzahl = sum(bool(befund.warnungen) for befund in befunde)
    zeilen += ["", f"{len(befunde)} Texte, davon {anzahl} mit Warnungen."]
    return "\n".join(zeilen) + "\n"
