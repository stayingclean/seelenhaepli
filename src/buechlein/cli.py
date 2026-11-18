"""Kommandozeile: ``buechlein build`` und ``buechlein check``."""

import argparse
import os
import sys
from pathlib import Path

from buechlein.ausgaben import AUSGABEN
from buechlein.buch import Buch, buch_laden, ordnen
from buechlein.konvertieren import Text, konvertieren
from buechlein.pruefen import Befund, allgemeine_warnungen, bericht, pruefen


def main() -> None:
    parser = argparse.ArgumentParser(prog="buechlein", description=__doc__)
    parser.add_argument(
        "befehl",
        choices=["build", "check"],
        help="build: prüfen und alle Ausgaben erzeugen; check: nur konvertieren und prüfen",
    )
    parser.add_argument(
        "--streng", action="store_true", help="bei Warnungen mit Fehler enden (für Pull Requests)"
    )
    parser.add_argument(
        "--projekt", type=Path, default=Path("."), help="Ordner mit buch.yaml (Standard: hier)"
    )
    optionen = parser.parse_args()
    for strom in (sys.stdout, sys.stderr):
        strom.reconfigure(encoding="utf-8")  # type: ignore[union-attr]

    buch = buch_laden(optionen.projekt.resolve() / "buch.yaml")
    ordner = buch.ordner / "build"
    texte, hat_warnungen = _konvertieren_und_pruefen(buch, ordner)

    if optionen.befehl == "build":
        for name, erzeugen in AUSGABEN.items():
            print(f"{name}: {erzeugen(buch, texte, ordner)}")

    if hat_warnungen and optionen.streng:
        sys.exit("Die Prüfung hat Warnungen ergeben (siehe Prüfbericht).")


def _konvertieren_und_pruefen(buch: Buch, ordner: Path) -> tuple[list[Text], bool]:
    dateien = {
        datei.stem: datei
        for datei in (buch.ordner / "texte").glob("*.docx")
        if not datei.name.startswith("~$")  # Sperrdateien von Word
    }
    reihenfolge = ordnen(list(dateien), buch.reihenfolge)
    texte = [konvertieren(dateien[name], ordner) for name in reihenfolge.namen]
    befunde = [pruefen(text, buch, reihenfolge) for text in texte]
    allgemein = allgemeine_warnungen(reihenfolge)
    _berichten(bericht(befunde, allgemein, buch), befunde, allgemein, ordner)
    return texte, bool(allgemein) or any(befund.warnungen for befund in befunde)


def _berichten(text: str, befunde: list[Befund], allgemein: list[str], ordner: Path) -> None:
    """Gibt den Bericht aus: Konsole, build/pruefbericht.md und GitHub Actions."""
    print(text)
    (ordner / "pruefbericht.md").write_text(text, encoding="utf-8")
    if zusammenfassung := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(zusammenfassung, "a", encoding="utf-8") as datei:
            datei.write(text)
    if os.environ.get("GITHUB_ACTIONS"):
        for befund in befunde:
            for warnung in befund.warnungen:
                print(f"::warning file=texte/{befund.text.name}.docx::{warnung}")
        for warnung in allgemein:
            print(f"::warning file=buch.yaml::{warnung}")
