"""Konvertierung, geprüft an der Word-Vorlage: Sie enthält Titel, Untertitel, Autor,
eine Zwischenüberschrift, ein Zitat, eine Fussnote und Kommentare."""

from pathlib import Path

import pytest

from buechlein.buch import Buch, ordnen
from buechlein.konvertieren import Text, konvertieren, pandoc, slug
from buechlein.pruefen import bericht, pruefen

VORLAGE = Path(__file__).parent.parent / "vorlage" / "Vorlage_Buechlein.docx"


@pytest.fixture(scope="module")
def text(tmp_path_factory) -> Text:
    return konvertieren(VORLAGE, tmp_path_factory.mktemp("build"))


def test_titel_untertitel_autor(text):
    assert text.titel == "Titel des Textes"
    assert text.untertitel.startswith("Untertitel (optional")
    assert text.autor == "Vorname Nachname"


def test_titel_wird_h1_mit_untertitel_und_autor_darunter(text):
    zeilen = [zeile for zeile in text.als_markdown().splitlines() if zeile]
    assert zeilen[0] == "# Titel des Textes"
    assert zeilen[1].startswith('<p class="untertitel">Untertitel')
    assert zeilen[2] == '<p class="autor">Vorname Nachname</p>'


def test_zwischenueberschrift_rutscht_eine_ebene_tiefer(text):
    ueberschriften = [zeile for zeile in text.inhalt.splitlines() if zeile.startswith("#")]
    assert ueberschriften == ["## Zwischenüberschrift (optional)"]


def test_zitat_und_fussnote(text):
    assert "\n> Längere Zitate setzen Sie" in text.inhalt
    assert "gehören in eine Fussnote.[^1]" in text.inhalt
    assert "[^1]: Beispiel einer Fussnote" in text.inhalt


def test_kommentare_werden_ignoriert(text):
    assert "Willkommen" not in text.inhalt
    assert "Guillemets" not in text.inhalt


def test_zeichenzahl_wie_word(text):
    """Vergleich mit dem reinen Text: alle Absätze inkl. Fussnote, ohne Umbrüche."""
    rein = pandoc(str(VORLAGE), "-t", "plain", "--wrap=none")
    absaetze = [zeile.removeprefix("[1] ").strip() for zeile in rein.splitlines()]
    kopf = len(text.titel) + len(text.untertitel) + len(text.autor)
    # «[1]» im Fliesstext ist nur Pandocs Darstellung des Fussnotenzeichens.
    erwartet = kopf + sum(len(absatz) for absatz in absaetze) - len("[1]")
    assert text.zeichen == erwartet


def test_keine_leeren_absaetze_und_aenderungen(text):
    assert text.leere_absaetze == 0
    assert not text.hat_aenderungen


def test_slug():
    assert slug("Müller_Über-die Brücke") == "mueller-ueber-die-bruecke"
    assert slug("Seelenhäppli") == "seelenhaeppli"


def test_pruefbericht_warnt_bei_ueberlaenge_und_fehlendem_eintrag(text):
    buch = Buch(titel="Probe", herausgeber="Jemand", max_zeichen=100)
    befund = pruefen(text, buch, ordnen([text.name], []))
    assert any("zu lang" in warnung for warnung in befund.warnungen)
    assert "steht nicht in buch.yaml" in befund.warnungen
    tabelle = bericht([befund], [], buch)
    assert "| Text | Autor | Zeichen | Status |" in tabelle
    assert f"| Titel des Textes | Vorname Nachname | {text.zeichen} | ⚠️ zu lang" in tabelle


def test_pruefbericht_ohne_warnung(text):
    buch = Buch(titel="Probe", herausgeber="Jemand")
    befund = pruefen(text, buch, ordnen([text.name], [text.name]))
    assert befund.warnungen == []
    assert "✅" in bericht([befund], [], buch)
