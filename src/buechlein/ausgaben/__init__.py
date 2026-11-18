"""Ausgabeformate. Jedes Format ist eine Funktion mit derselben Signatur.

Ein neues Format (z. B. das Druck-PDF) braucht ein eigenes Modul mit einer Funktion
``erzeugen(buch, texte, ordner)`` und einen Eintrag in ``AUSGABEN``.
"""

from collections.abc import Callable
from pathlib import Path

from buechlein.ausgaben import epub, website
from buechlein.buch import Buch
from buechlein.konvertieren import Text

Ausgabe = Callable[[Buch, list[Text], Path], Path]
"""Schreibt ein Format in den Build-Ordner und gibt den Pfad des Ergebnisses zurück.

Die Texte kommen in der Reihenfolge des Buchs. Ihre Bilder liegen in ``ordner/bilder/``.
"""

# Die Reihenfolge zählt: Die Website bietet das EPUB zum Download an.
AUSGABEN: dict[str, Ausgabe] = {
    "epub": epub.erzeugen,
    "website": website.erzeugen,
}
