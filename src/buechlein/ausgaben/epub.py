"""E-Book: EPUB 3 mit Pandoc, ein Kapitel pro Text."""

import shutil
import subprocess
from pathlib import Path

import yaml

from buechlein.buch import Buch
from buechlein.konvertieren import MARKDOWN, Text, pandoc, slug

_CSS = Path(__file__).with_name("epub.css")


def dateiname(buch: Buch) -> str:
    return f"{slug(buch.titel)}.epub"


def erzeugen(buch: Buch, texte: list[Text], ordner: Path) -> Path:
    arbeit = ordner / "epub"
    arbeit.mkdir(parents=True, exist_ok=True)
    kapitel = []
    for nummer, text in enumerate(texte, start=1):
        datei = arbeit / f"{nummer:02d}-{text.slug}.md"
        datei.write_text(text.als_markdown(), encoding="utf-8")
        kapitel.append(str(datei))

    metadaten = arbeit / "metadaten.yaml"
    metadaten.write_text(yaml.safe_dump(_metadaten(buch), allow_unicode=True), encoding="utf-8")

    ziel = ordner / dateiname(buch)
    argumente = [
        "-f", MARKDOWN,
        "-t", "epub3",
        "--file-scope",  # jede Datei für sich lesen, sonst kollidieren die Fussnoten
        "--split-level=1",
        "--toc",
        "--toc-depth=1",
        f"--metadata-file={metadaten}",
        f"--css={_CSS}",
        f"--resource-path={ordner}",
        "-o", str(ziel),
    ]  # fmt: skip
    titelbild = buch.ordner / "cover.jpg"
    if titelbild.exists():
        argumente.append(f"--epub-cover-image={titelbild}")
    pandoc(*argumente, *kapitel)
    _validieren(ziel)
    return ziel


def _metadaten(buch: Buch) -> dict:
    metadaten = {
        "title": buch.titel,
        "lang": buch.sprache,
        "creator": [{"role": "edt", "text": buch.herausgeber}],
    }
    if buch.untertitel:
        metadaten["subtitle"] = buch.untertitel
    if buch.beschreibung:
        metadaten["description"] = buch.beschreibung
    return metadaten


def _validieren(epub: Path) -> None:
    programm = shutil.which("epubcheck")
    if programm is None:
        print("Hinweis: epubcheck ist nicht installiert, das EPUB wurde nicht validiert.")
        return
    ergebnis = subprocess.run(
        [programm, str(epub)], capture_output=True, encoding="utf-8", check=False
    )
    if ergebnis.returncode != 0:
        raise RuntimeError(f"epubcheck meldet Fehler:\n{ergebnis.stdout}{ergebnis.stderr}")
    print("epubcheck: keine Fehler.")
