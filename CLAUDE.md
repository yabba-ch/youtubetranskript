# CLAUDE.md – youtubetranskript

Dieses Repo enthält zwei Dinge: die `/watch`-Skill-Implementierung (`.claude/skills/watch/`) und die gesammelten HTML-Transkripte (`YouTube-VideoTranskripte/`).

## Ablaufverfahren pro Video

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
- Eintrag in `index.html` hinzufügen
- Committen und nach `main` pushen

**Git-Commit-Format:**
```
Add transcript: <Videotitel>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
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
