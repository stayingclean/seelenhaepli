"""Zählt Zeichen wie Words «Zeichen (mit Leerzeichen)».

Gezählt wird auf Pandocs Dokumentstruktur (JSON), nicht auf dem Markdown: So zählen
weder Markdown-Zeichen noch Absatzumbrüche mit, Fussnoten aber schon.
"""

from typing import Any

_LEERZEICHEN = {"Space", "SoftBreak"}
_MIT_TEXT_AM_ENDE = {"Code", "Math", "CodeBlock"}


def zeichen_zaehlen(knoten: Any) -> int:  # noqa: ANN401 – beliebiges JSON
    """Zählt die sichtbaren Zeichen in einem Teil des Pandoc-JSON."""
    if isinstance(knoten, list):
        return sum(zeichen_zaehlen(kind) for kind in knoten)
    if not isinstance(knoten, dict):
        return 0
    typ = knoten.get("t")
    if typ == "Str":
        return len(knoten["c"])
    if typ in _LEERZEICHEN:
        return 1
    if typ in _MIT_TEXT_AM_ENDE:
        return len(knoten["c"][-1])
    return sum(zeichen_zaehlen(wert) for wert in knoten.values())


def als_text(knoten: Any) -> str:  # noqa: ANN401 – beliebiges JSON
    """Gibt den reinen Text eines Teils des Pandoc-JSON zurück (für Titel und Autor)."""
    if isinstance(knoten, list):
        return "".join(als_text(kind) for kind in knoten)
    if not isinstance(knoten, dict):
        return ""
    typ = knoten.get("t")
    if typ == "Str":
        return knoten["c"]
    if typ in _LEERZEICHEN or typ == "LineBreak":
        return " "
    if typ == "Note":
        return ""
    return "".join(als_text(wert) for wert in knoten.values())
