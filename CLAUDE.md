# CLAUDE.md – youtubetranskript

Dieses Repo enthält zwei Dinge: die `/watch`-Skill-Implementierung (`.claude/skills/watch/`) und die gesammelten HTML-Transkripte (`YouTube-VideoTranskripte/`).

## Ablaufverfahren pro Video

> **Schritt 0 – Repo synchronisieren (zuerst!):** Vor dem Bauen immer `git fetch` und `git merge --ff-only origin/main`. Nie auf einem veralteten lokalen Stand bauen oder pushen – sonst kollidiert es mit Commits aus Cloud-/Worktree-Sessions. Beim Committen nur die **zum Video gehörenden Dateien** stagen (`<slug>.html`, `index.html`, `assets/thumbs/<slug>.jpg`, ggf. `assets/img/...`), nie Fremd-Dateien aus dem Arbeitsverzeichnis.

Pro transkribiertem Video entstehen **zwei Ausgaben**:

> **Videobeschreibung auswerten:** `/watch` gibt die YouTube-Beschreibung seit 2026-11 als Abschnitt `## Description` im Report aus. Daraus in **beide Ausgaben** – direkt **nach dem Roter Faden** (`kontext_intro`) – ein Block `Aus der Videobeschreibung`: (1) eine Zusammenfassung der Beschreibung (**max. 8 Sätze**) und (2) eine Aufzählung der **relevanten** Links (`Titel – URL`: genannte Projekte, Tools, Quellen). **Eigenwerbung** (eigene Community/Masterclass), **Social-Media-Profile** und **Affiliate-/Sponsor-Links** rausfiltern.

### 1. Vault-Notiz (Markdown)
Wird im Obsidian-Vault unter `03 Bereiche/YouTube Transkripte/` abgelegt. Nach der `## Zusammenfassung` folgt der Abschnitt `## Aus der Videobeschreibung` (Zusammenfassung + Links-Liste), dann `## Einordnung`.

**Dateiname:** Titel des Videos in normaler Schreibweise, z. B. `Zwanzig Claude-Code-Tricks.md`

**Frontmatter-Vorlage:**
```yaml
---
tags: [transkript, youtube]
quelle: https://youtu.be/VIDEO-ID
kanal:
datum: YYYY-MM-DD
status: aktiv
---
```

### 2. HTML-Seite (dieses Repo) – via Vorlage + Generator
Seit dem Umbau (2026-11): **keine Base64-Bilder und kein Inline-`<style>` mehr.** Bilder liegen als Dateien unter `assets/`, CSS zentral in `assets/feldbuch.css` (Detailseiten) bzw. `assets/index.css` (Startseite). Vorlage und Generator liegen in `YouTube-VideoTranskripte/_vorlage/` (Ordner beginnt mit `_` → von GitHub Pages nicht publiziert).

Ablauf:
1. **Slug** wählen (Kebab-Case, beschreibend, z. B. `zwanzig-claude-code-tricks`).
2. Claude schreibt eine kleine **JSON-Inhaltsdatei** `<slug>.json` (Schema steht im Kopf von `_vorlage/neue-seite.py`: `slug, video_id, title, channel, duration_min, date` = Ablagedatum, `category, sr_summary, lede, kontext_intro?, beschreibung?{summary, links[]{title,url}}, clusters[]→tricks{title,time,body}, kontext_outro?`). `beschreibung` ist der Block aus der Videobeschreibung (Zusammenfassung max. 8 Sätze + nur relevante Links). Das ist die eigentliche Zusammenfassung; `body`/`lede`/`text` dürfen Inline-HTML enthalten (`<strong>`, `<span class="inline-code">`), `&` als `&amp;` schreiben.
3. Aus `YouTube-VideoTranskripte/` aufrufen:
   ```bash
   python _vorlage/neue-seite.py <slug>.json
   ```
   Der Generator: lädt+skaliert das Thumbnail (`hqdefault.jpg` → 480×360 JPEG nach `assets/thumbs/<slug>.jpg`), füllt `_vorlage/seite.html` (externes CSS, `source-thumb`, TOC + Cluster mit `?t=`-Deeplinks, «Selbststudium» verlinkt `index.html`) und fügt die `entry-card` in `index.html` ein (passende Kategorie, `data-date` = **Ablagedatum** = Tag der Transkription, Zähler automatisch, idempotent).
4. Committen und nach `main` pushen.

Hinweise:
- **Kategorie muss existieren:** Fehlt die Zielkategorie in `index.html`, bricht der Generator ab → Kategorie-Sektion einmalig von Hand anlegen, dann erneut laufen lassen.
- Zähler, Minuten, Sortierung (neueste zuerst), Suche und «Nur die letzten 3» berechnet das Seiten-Skript in `index.html` selbst.
- **Altseiten mit Inline-CSS:** Ein paar ältere Seiten mit eigenen Layout-Systemen behalten ihren Inline-`<style>` (siehe Migration). Für neue Transkripte immer den Generator nutzen.

**Git-Commit-Format** (Autor: **Pascal Junker** via `--author="Pascal Junker <pascal.junker@gmail.com>"`, Co-Author = aktuelles Claude-Modell):
```
Add transcript: <Videotitel>

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

**Am Ende jeder Transkription den Live-Link anzeigen:**
```
https://yabba-ch.github.io/youtubetranskript/YouTube-VideoTranskripte/<datei>.html
```
(Link auf die GitHub-Pages-Seite, nicht auf das Repo.)

## `/watch` Skill nutzen

```bash
/watch https://youtu.be/VIDEO-ID
```

Nützliche Flags:
- `--detail transcript` – nur Transkript, keine Frames (schnell, günstig)
- `--detail balanced` – Standard, szenenbasierte Frames
- `--start`/`--end` – auf einen Abschnitt fokussieren (z. B. `--start 2:15 --end 2:45`)

**Wichtig:** Immer **lokal** ausführen (eigener Rechner oder Claude Code im Web). Nie über einen VPS – YouTube blockiert Rechenzentrums-IPs.

## Sprachregeln

- **Deutsches Original:** läuft ohne Rückfrage durch.
- **Nicht-deutsches Original:** vor der Transkription nach der gewünschten Ausgabesprache fragen – Deutsch (übersetzt von Claude) / Originalsprache belassen / beides.
- Das `/watch`-Skript liefert das Rohtranskript immer in der Originalsprache. Die Übersetzung übernimmt Claude beim Erstellen von Notiz und HTML-Seite.

## HTML-Seitenstruktur

Neue Detailseiten entstehen aus `_vorlage/seite.html` (via Generator), nicht von Hand:
- Semantisches HTML5, **externes CSS** (`assets/feldbuch.css`, Light/Dark-Theme via CSS Custom Properties), Viewport-Meta
- `<title>`, `source-card` mit Quellenlink + `source-thumb`, `lede`, Kontextboxen, `toc`, Cluster mit nummerierten `trick`-Blöcken, `footer`
- Zusatzkomponenten in `feldbuch.css`: `.trick-shot` (Inhaltsbild), `.promptquote`, `.tbl`
- Responsives Layout (≤480px)

## Fallstricke (gelernt)

- **Repo-Sync zuerst** (Schritt 0). Grösster Zeitfresser war ein lokaler Stand hinter `origin/main`.
- **Nur die zum Video gehörenden Dateien committen** (`<slug>.html`, `index.html`, `assets/thumbs/<slug>.jpg`, ggf. `assets/img/...`). Fremde Projekte, Archive (`.tar.gz`), `.docx` usw. gehören nicht ins Repo → per `.gitignore` draussen halten, nie stagen.
- **Windows:** `/watch` mit `PYTHONUTF8=1` starten, sonst stürzt die Ausgabe an der Konsolen-Kodierung (cp1252) ab.
- **Datum überall = Ablagedatum** (Tag der Transkription): Vault-Frontmatter `datum`, Vault-Index-Eintrag und Feldbuch-`data-date` nutzen dasselbe Datum.
- **Thumbnail & Seite baut der Generator** (`_vorlage/neue-seite.py`): Thumb `hqdefault.jpg` → 480×360 JPEG als **Datei** in `assets/thumbs/`, Seite aus `_vorlage/seite.html`. **Nicht mehr** von Hand nach dem Muster einer Bestandsseite bauen und **kein Base64** mehr einbetten.
- **CSS zentral:** Design-Änderungen an Detailseiten nur in `assets/feldbuch.css` (gilt für alle Standard-Seiten), Startseite in `assets/index.css`.
