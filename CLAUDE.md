# CLAUDE.md – youtubetranskript

Dieses Repo enthält zwei Dinge: die `/watch`-Skill-Implementierung (`.claude/skills/watch/`) und die gesammelten HTML-Transkripte (`YouTube-VideoTranskripte/`).

## Ablaufverfahren pro Video

> **Schritt 0 – Repo synchronisieren (zuerst!):** Vor dem Bauen immer `git fetch` und `git merge --ff-only origin/main`. Nie auf einem veralteten lokalen Stand bauen oder pushen – sonst kollidiert es mit Commits aus Cloud-/Worktree-Sessions. Beim Committen nur die **zwei Video-Dateien** stagen (neue HTML-Seite + `index.html`), nie Fremd-Dateien aus dem Arbeitsverzeichnis.

Pro transkribiertem Video entstehen **zwei Ausgaben**:

### 1. Vault-Notiz (Markdown)
Wird im Obsidian-Vault unter `03 Bereiche/YouTube Transkripte/` abgelegt.

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

### 2. HTML-Seite (dieses Repo)
- Neue HTML-Datei in `YouTube-VideoTranskripte/`
- **Dateiname:** Kebab-Case, beschreibend, z. B. `zwanzig-claude-code-tricks.html`
- Eintrag in `YouTube-VideoTranskripte/index.html` hinzufügen: neue `entry-card` in der passenden Kategorie (oder neue Kategorie), **mit Vorschaubild** (YouTube `hqdefault.jpg`, auf **480×360 JPEG** gebracht und als Base64-Data-URI eingebettet, gleiches Format wie die anderen Karten) und `data-date="YYYY-MM-DDTHH:MM"` (= **Ablagedatum**: Tag der Transkription, *nicht* das Video-Datum) auf dem `<a class="entry-card">`; Meta-Zeile: Kanal · Dauer · Datum (TT.MM.JJJJ). Zähler, Kategorien, Minuten, Sortierung (neueste zuerst), Suche und «Nur die letzten 3» berechnet das Skript in der Seite selbst.
- Auf der Detailseite oben ebenfalls das Vorschaubild (`source-thumb`) einbetten; das Wort «Selbststudium» im `eyebrow` ist ein Link auf `index.html`
- Committen und nach `main` pushen

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

Jede HTML-Seite folgt dem Stil der bestehenden Dateien in `YouTube-VideoTranskripte/`:
- Semantisches HTML5 mit eingebettetem CSS (Light/Dark-Theme via CSS Custom Properties)
- Metadaten im `<head>`: Titel, Kanal, Datum, Quellenlink
- Inhaltsverzeichnis falls sinnvoll
- Responsives Layout (≤480px)

## Fallstricke (gelernt)

- **Repo-Sync zuerst** (Schritt 0). Grösster Zeitfresser war ein lokaler Stand hinter `origin/main`.
- **Nur die 2 Video-Dateien committen.** Fremde Projekte, Archive (`.tar.gz`), `.docx` usw. gehören nicht ins Repo → per `.gitignore` draussen halten, nie stagen.
- **Windows:** `/watch` mit `PYTHONUTF8=1` starten, sonst stürzt die Ausgabe an der Konsolen-Kodierung (cp1252) ab.
- **Datum überall = Ablagedatum** (Tag der Transkription): Vault-Frontmatter `datum`, Vault-Index-Eintrag und Feldbuch-`data-date` nutzen dasselbe Datum.
- **Thumbnail:** `hqdefault.jpg` → 480×360 JPEG (q≈82), als Base64 einbetten (Detailseite als `source-thumb`, Karte als `entry-thumb`).
- **Detailseite** immer nach dem Muster einer bestehenden Seite bauen (gleicher `<style>`-Kopf, «Selbststudium» verlinkt `index.html`, Schritte mit `?t=`-Deeplinks).
