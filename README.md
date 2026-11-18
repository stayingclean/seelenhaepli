# Seelenhäppli

Kurztexte verschiedener Autorinnen und Autoren. Sie schreiben in Word, daraus entstehen
automatisch eine Website und ein E-Book.

- **Website:** <https://stayingclean.github.io/seelenhaepli/>
- **E-Book (EPUB):** <https://stayingclean.github.io/seelenhaepli/downloads/seelenhaeppli.epub>
  (auch über die Startseite der Website)
- **Prüfbericht:** im Tab [Actions](https://github.com/stayingclean/seelenhaepli/actions),
  beim jeweiligen Lauf unter «Summary»

## Einen neuen Text hinzufügen

1. Die Word-Datei nach `texte/` legen. Dateiname: `Nachname_Kurztitel.docx`.
2. In `buch.yaml` unter `reihenfolge` den Dateinamen ohne `.docx` an der gewünschten
   Stelle eintragen.
3. Committen und auf `main` pushen (oder die Dateien direkt auf GitHub hochladen).

Nach ein paar Minuten sind Website und E-Book aktualisiert. Der Prüfbericht zeigt für jeden
Text die Zeichenzahl und allfällige Warnungen:

- mehr als 4500 Zeichen (mit Leerzeichen, inkl. Titel, Untertitel, Autor und Fussnoten)
- Titel oder Autor fehlt
- leere Absätze
- nachverfolgte Änderungen in der Word-Datei
- der Text steht nicht in `buch.yaml` (er kommt dann alphabetisch ans Ende)

Auf `main` sind das nur Warnungen: Ein einzelner Text blockiert die Website nicht.
Bei Pull Requests schlägt die Prüfung fehl, bis alles in Ordnung ist.

Die Dateien `texte/Beispiel_*.docx` sind fiktive Beispieltexte. Zum Entfernen die Dateien
löschen und ihre Einträge in `buch.yaml` streichen.

## Aufbau

| Ort | Inhalt |
| --- | --- |
| `texte/` | Word-Dateien der Autoren, die einzige Quelle der Wahrheit |
| `vorlage/` | Word-Vorlagen, auf der Website zum Download |
| `buch.yaml` | Titel, Herausgeber, Sprache, Beschreibung, Reihenfolge |
| `seiten/` | Startseite und «Mitmachen» als Markdown |
| `cover.jpg` | optional: Titelbild für das E-Book |
| `src/buechlein/` | die Pipeline (Python) |
| `build/` | alles Generierte, wird nicht committet |

Die Pipeline hat drei Schritte, je ein Modul:

1. `konvertieren.py`: Word → Markdown mit Pandoc. Der Titel wird zur Überschrift 1,
   Zwischenüberschriften rutschen eine Ebene tiefer. Kommentare werden ignoriert.
2. `pruefen.py`: Zeichenzählung (`zaehlen.py`) und Warnungen, Bericht als Tabelle.
3. `ausgaben/`: ein Modul pro Ausgabeformat (`epub.py`, `website.py`). Alle haben dieselbe
   Signatur `erzeugen(buch, texte, ordner)` und sind in `ausgaben/__init__.py` eingetragen.
   Ein weiteres Format, etwa ein Druck-PDF, kommt als neues Modul mit einem Eintrag dazu.

## Lokal arbeiten (Arch Linux)

Abhängigkeiten installieren:

```bash
sudo pacman -S --needed uv pandoc-cli epubcheck
```

Alles bauen (Prüfbericht, E-Book, Website):

```bash
uv run buechlein build
```

Das Ergebnis liegt in `build/`: das E-Book als `build/seelenhaeppli.epub`, die Website in
`build/website/site/`, der Bericht in `build/pruefbericht.md`.

Vorschau der Website im Browser (<http://localhost:8000>), nach einem Build:

```bash
uv run zensical serve -f build/website/zensical.toml
```

Nur prüfen, ohne Ausgaben zu erzeugen:

```bash
uv run buechlein check
```

Tests und Stilprüfung:

```bash
uv run pytest
```

```bash
uv run ruff check && uv run ruff format --check
```

Ohne `epubcheck` läuft der Build trotzdem, das E-Book wird dann nicht validiert.
