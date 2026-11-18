"""Website: schreibt ein Zensical-Projekt und baut es."""

import html
import json
import shutil
import subprocess
import sys
from pathlib import Path

from buechlein.ausgaben import epub
from buechlein.buch import Buch
from buechlein.konvertieren import BILDER, Text

_CSS = Path(__file__).with_name("website.css")
SITE_URL = "https://stayingclean.github.io/seelenhaepli/"


def erzeugen(buch: Buch, texte: list[Text], ordner: Path) -> Path:
    projekt = ordner / "website"
    docs = projekt / "docs"
    shutil.rmtree(projekt, ignore_errors=True)
    (docs / "texte").mkdir(parents=True)

    for text in texte:
        (docs / "texte" / f"{text.slug}.md").write_text(text.als_markdown(), encoding="utf-8")
    if (ordner / BILDER).exists():
        # Die Bildpfade im Markdown sind relativ zur Textseite.
        shutil.copytree(ordner / BILDER, docs / "texte" / BILDER)

    platzhalter = {
        "{{titel}}": buch.titel,
        "{{untertitel}}": buch.untertitel,
        "{{beschreibung}}": buch.beschreibung,
        "{{herausgeber}}": buch.herausgeber,
        "{{max_zeichen}}": str(buch.max_zeichen),
        "{{anzahl_texte}}": str(len(texte)),
        "{{epub}}": f"downloads/{epub.dateiname(buch)}",
    }
    for seite in sorted((buch.ordner / "seiten").glob("*.md")):
        inhalt = seite.read_text(encoding="utf-8")
        for schluessel, wert in platzhalter.items():
            inhalt = inhalt.replace(schluessel, wert)
        (docs / seite.name).write_text(inhalt, encoding="utf-8")
    (docs / "inhalt.md").write_text(_inhaltsverzeichnis(texte), encoding="utf-8")

    shutil.copytree(buch.ordner / "vorlage", docs / "vorlage")
    fertiges_epub = ordner / epub.dateiname(buch)
    if fertiges_epub.exists():
        (docs / "downloads").mkdir()
        shutil.copy(fertiges_epub, docs / "downloads")
    (docs / "stylesheets").mkdir()
    shutil.copy(_CSS, docs / "stylesheets" / "extra.css")

    (projekt / "zensical.toml").write_text(_konfiguration(buch, texte), encoding="utf-8")
    subprocess.run([sys.executable, "-m", "zensical", "build", "--clean"], cwd=projekt, check=True)
    return projekt / "site"


def _inhaltsverzeichnis(texte: list[Text]) -> str:
    zeilen = ["# Inhalt", ""]
    for text in texte:
        autor = f' <span class="autor">{html.escape(text.autor)}</span>' if text.autor else ""
        zeilen.append(f"1. [{text.titel or text.name}](texte/{text.slug}.md){autor}")
    return "\n".join(zeilen) + "\n"


def _konfiguration(buch: Buch, texte: list[Text]) -> str:
    """Schreibt zensical.toml. JSON-Zeichenketten sind auch gültige TOML-Zeichenketten."""
    q = json.dumps
    textseiten = "\n".join(
        f"    {{ {q(text.titel or text.name)} = {q(f'texte/{text.slug}.md')} }}," for text in texte
    )
    return f"""\
[project]
site_name = {q(buch.titel)}
site_description = {q(buch.beschreibung)}
site_author = {q(buch.herausgeber)}
site_url = {q(SITE_URL)}
docs_dir = "docs"
site_dir = "site"
extra_css = ["stylesheets/extra.css"]
nav = [
  {{ "Start" = "index.md" }},
  {{ "Inhalt" = "inhalt.md" }},
  {{ "Texte" = [
{textseiten}
  ] }},
  {{ "Mitmachen" = "mitmachen.md" }},
]

[project.theme]
language = "de"
font = false
features = [
  "content.footnote.tooltips",
  "navigation.footer",
  "navigation.sections",
  "navigation.top",
]

[[project.theme.palette]]
media = "(prefers-color-scheme: light)"
scheme = "default"
primary = "brown"
toggle.icon = "lucide/sun"
toggle.name = "Dunkles Design"

[[project.theme.palette]]
media = "(prefers-color-scheme: dark)"
scheme = "slate"
primary = "brown"
toggle.icon = "lucide/moon"
toggle.name = "Helles Design"

[project.markdown_extensions]
attr_list = {{}}
footnotes = {{}}
md_in_html = {{}}
"""
