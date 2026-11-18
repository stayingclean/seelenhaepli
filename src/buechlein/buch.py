"""Liest buch.yaml und bestimmt die Reihenfolge der Texte."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Buch:
    titel: str
    herausgeber: str
    sprache: str = "de-CH"
    untertitel: str = ""
    beschreibung: str = ""
    max_zeichen: int = 4500
    reihenfolge: list[str] = field(default_factory=list)
    ordner: Path = Path(".")
    """Projektordner mit buch.yaml, texte/, vorlage/, seiten/ und optional cover.jpg."""


def buch_laden(pfad: Path) -> Buch:
    daten = yaml.safe_load(pfad.read_text(encoding="utf-8")) or {}
    daten["reihenfolge"] = [str(name) for name in daten.get("reihenfolge") or []]
    return Buch(**daten, ordner=pfad.parent)


@dataclass(frozen=True)
class Reihenfolge:
    namen: list[str]
    """Alle vorhandenen Texte in der Reihenfolge des Buchs."""
    nicht_aufgefuehrt: list[str]
    """Vorhanden, aber nicht in buch.yaml (alphabetisch ans Ende gehängt)."""
    ohne_datei: list[str]
    """In buch.yaml aufgeführt, aber keine Datei vorhanden."""


def ordnen(vorhanden: list[str], gewuenscht: list[str]) -> Reihenfolge:
    """Ordnet die vorhandenen Texte gemäss buch.yaml."""
    aufgefuehrt = [name for name in dict.fromkeys(gewuenscht) if name in vorhanden]
    rest = sorted(set(vorhanden) - set(aufgefuehrt), key=str.casefold)
    fehlend = [name for name in gewuenscht if name not in vorhanden]
    return Reihenfolge(aufgefuehrt + rest, rest, fehlend)
