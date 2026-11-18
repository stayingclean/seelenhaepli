import json

import pytest

from buechlein.konvertieren import pandoc
from buechlein.zaehlen import als_text, zeichen_zaehlen


def bloecke(markdown: str) -> list:
    return json.loads(pandoc("-f", "markdown", "-t", "json", eingabe=markdown))["blocks"]


@pytest.mark.parametrize(
    ("markdown", "erwartet"),
    [
        ("Hallo Welt", 10),
        ("Zwei  Leerzeichen\nund Umbruch", len("Zwei Leerzeichen und Umbruch")),
        ("Erster Absatz.\n\nZweiter Absatz.", 14 + 15),  # Absatzumbruch zählt nicht
        ("# Titel\n\nText", 5 + 4),
        ("Ein *betontes* und **fettes** Wort", len("Ein betontes und fettes Wort")),
        ("> Zitat hier", len("Zitat hier")),
        ("«Grüezi», sagte sie – leise.", len("«Grüezi», sagte sie – leise.")),
    ],
)
def test_zaehlt_sichtbare_zeichen(markdown, erwartet):
    assert zeichen_zaehlen(bloecke(markdown)) == erwartet


def test_fussnoten_zaehlen_mit():
    mit_fussnote = bloecke("Text.[^1]\n\n[^1]: Eine Quelle.")
    assert zeichen_zaehlen(mit_fussnote) == len("Text.") + len("Eine Quelle.")


def test_als_text_ohne_fussnote():
    assert als_text(bloecke("Ein *Titel*[^1] hier\n\n[^1]: Notiz")) == "Ein Titel hier"
