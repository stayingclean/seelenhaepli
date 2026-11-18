"""Wandelt eine Word-Datei mit Pandoc in einen Text (Markdown und Angaben) um."""

import html
import json
import re
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree

from buechlein.zaehlen import als_text, zeichen_zaehlen

MARKDOWN = "markdown_strict+footnotes"
"""Markdown-Dialekt, den sowohl Zensical als auch Pandoc (für das EPUB) lesen."""

BILDER = "bilder"
"""Unterordner des Zielordners, in den die Bilder aller Texte extrahiert werden."""

_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
_UMLAUTE = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})


@dataclass(frozen=True)
class Text:
    name: str
    """Dateiname ohne «.docx», so wie er in buch.yaml steht."""
    slug: str
    titel: str
    untertitel: str
    autor: str
    inhalt: str
    """Fliesstext als Markdown. Zwischenüberschriften beginnen bei Ebene 2."""
    zeichen: int
    leere_absaetze: int
    hat_aenderungen: bool
    """Die Word-Datei enthält nachverfolgte Änderungen."""

    def als_markdown(self) -> str:
        """Ganzer Text: Titel als H1, darunter Untertitel und Autor, dann der Inhalt."""
        teile = [f"# {self.titel or self.name}"]
        if self.untertitel:
            teile.append(f'<p class="untertitel">{html.escape(self.untertitel)}</p>')
        if self.autor:
            teile.append(f'<p class="autor">{html.escape(self.autor)}</p>')
        teile.append(self.inhalt)
        return "\n\n".join(teile) + "\n"


def slug(name: str) -> str:
    """Macht aus einem Datei- oder Buchnamen einen URL-tauglichen Namen."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower().translate(_UMLAUTE)).strip("-")


def pandoc(*argumente: str, eingabe: str | None = None, ordner: Path | None = None) -> str:
    ergebnis = subprocess.run(
        ["pandoc", *argumente],
        input=eingabe,
        cwd=ordner,
        capture_output=True,
        encoding="utf-8",
        check=False,
    )
    if ergebnis.returncode != 0:
        raise RuntimeError(f"pandoc {' '.join(argumente)}\n{ergebnis.stderr}")
    return ergebnis.stdout


def konvertieren(docx: Path, ziel: Path) -> Text:
    """Konvertiert eine Word-Datei. Bilder landen in ``ziel/bilder/<slug>/``.

    Kommentare und nachverfolgte Änderungen ignoriert Pandoc von sich aus
    (Änderungen gelten als angenommen).
    """
    name = docx.stem
    bilder = f"{BILDER}/{slug(name)}"
    ziel.mkdir(parents=True, exist_ok=True)
    roh = pandoc(str(docx.resolve()), "-t", "json", f"--extract-media={bilder}", ordner=ziel)
    dokument = json.loads(roh)
    meta = dokument["meta"]
    inhalt = pandoc(
        "-f", "json", "-t", MARKDOWN, "--wrap=none", "--shift-heading-level-by=1", eingabe=roh
    )
    kopf = [meta.get(feld, []) for feld in ("title", "subtitle", "author")]
    leere_absaetze, hat_aenderungen = _word_pruefen(docx)
    return Text(
        name=name,
        slug=slug(name),
        titel=als_text(kopf[0]).strip(),
        untertitel=als_text(kopf[1]).strip(),
        autor=_autoren(kopf[2]),
        inhalt=inhalt.strip(),
        zeichen=zeichen_zaehlen(kopf) + zeichen_zaehlen(dokument["blocks"]),
        leere_absaetze=leere_absaetze,
        hat_aenderungen=hat_aenderungen,
    )


def _autoren(meta: dict | list) -> str:
    """Mehrere Absätze mit der Formatvorlage «Author» ergeben eine Liste."""
    if isinstance(meta, dict) and meta.get("t") == "MetaList":
        return ", ".join(als_text(eintrag).strip() for eintrag in meta["c"])
    return als_text(meta).strip()


def _word_pruefen(docx: Path) -> tuple[int, bool]:
    """Zählt leere Absätze und erkennt nachverfolgte Änderungen.

    Beides sieht man nur in der Word-Datei selbst: Pandoc lässt leere Absätze weg.
    """
    with zipfile.ZipFile(docx) as archiv:
        wurzel = ElementTree.fromstring(archiv.read("word/document.xml"))
    leer = 0
    for absatz in wurzel.iter(f"{_W}p"):
        hat_inhalt = "".join(t.text or "" for t in absatz.iter(f"{_W}t")).strip() or any(
            absatz.iter(f"{_W}drawing")
        )
        ist_abschnittsende = absatz.find(f"{_W}pPr/{_W}sectPr") is not None
        if not hat_inhalt and not ist_abschnittsende:
            leer += 1
    hat_aenderungen = any(wurzel.iter(f"{_W}ins")) or any(wurzel.iter(f"{_W}del"))
    return leer, hat_aenderungen
