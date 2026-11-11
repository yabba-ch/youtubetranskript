# -*- coding: utf-8 -*-
"""
neue-seite.py - Generator fuer eine Feldbuch-Transkriptseite (Standard-Familie).

Der Agent schreibt nur eine kleine JSON-Inhaltsdatei; dieses Skript erledigt den Rest:
Thumbnail herunterladen+skalieren, HTML aus _vorlage/seite.html fuellen, Karte in
index.html einfuegen (Zaehler automatisch). So muss keine grosse HTML-Datei gelesen werden.

Aufruf (aus YouTube-VideoTranskripte/):
    python _vorlage/neue-seite.py inhalt.json
    python _vorlage/neue-seite.py inhalt.json --dry-run --out ..\\scratch\\test.html

JSON-Schema (Pflicht: slug, video_id, title, channel, duration_min, date, category):
{
  "slug": "claude-20-neue-funktionen",
  "video_id": "WUse7fDq2VQ",
  "title": "Claude 2.0 ist da: Alle neuen Funktionen einfach erklaert",
  "channel": "Julian Ivanov | KI-Automatisierung",
  "duration_min": 18,
  "date": "2026-11-02",          // Ablagedatum (heute), nicht Video-Datum
  "time": "18:00",               // optional, fuer die Sortierung; Default 12:00
  "category": "Workflow & Produktivitaet",
  "sr_summary": "Screenreader-Kurzbeschreibung ...",
  "lede": "Ein bis zwei Saetze Einleitung (darf Inline-HTML enthalten).",
  "kontext_intro": {"strong": "Roter Faden:", "text": "..."},   // optional
  "beschreibung": {                                              // optional, Block nach dem Roter Faden
    "summary": "Zusammenfassung der YouTube-Beschreibung, max. 8 Saetze (Inline-HTML erlaubt).",
    "links": [{"title": "Projekt/Tool/Quelle", "url": "https://..."}]  // nur relevante Links,
  },                                                             // KEINE Eigenwerbung/Social-Media/Affiliate
  "clusters": [
    {"title": "Die neue Struktur", "range": "01-05", "tricks": [
      {"title": "Zwei Bereiche", "time": "1:23", "body": "Fliesstext, Inline-HTML erlaubt."}
    ]}
  ],
  "kontext_outro": {"strong": "Fazit:", "text": "..."}          // optional
}
Hinweise: trick.time ist "M:SS"/"H:MM:SS"; "sec" wird daraus berechnet (oder explizit angeben).
Texte sind rohe HTML-Fragmente - '&' als '&amp;' schreiben, wie in den Bestandsseiten.
"""
import argparse, json, os, re, sys, io, base64, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # YouTube-VideoTranskripte/
TEMPLATE = os.path.join(HERE, "seite.html")
INDEX = os.path.join(ROOT, "index.html")
THUMBS = os.path.join(ROOT, "assets", "thumbs")


def parse_time(s):
    parts = [int(p) for p in str(s).split(":")]
    sec = 0
    for p in parts:
        sec = sec * 60 + p
    return sec


def dmy(date):
    y, m, d = date.split("-")
    return f"{d}.{m}.{y}"


def kontextbox(k):
    if not k:
        return ""
    strong = k.get("strong", "")
    text = k.get("text", "")
    inner = (f"<strong>{strong}</strong> " if strong else "") + text
    return f'<div class="kontextbox">\n    {inner}\n  </div>'


def beschreibung(b):
    """Block aus der YouTube-Beschreibung: Zusammenfassung (max. 8 Saetze) + relevante Links.
    Eigenwerbung/Social-Media/Affiliate-Links gehoeren nicht hierher (vom Agenten vorab gefiltert).
    """
    if not b:
        return ""
    summary = b.get("summary", "")
    links = b.get("links") or []
    link_items = "\n".join(
        f'      <li><a href="{l["url"]}" target="_blank" rel="noopener">{l["title"]}</a></li>'
        for l in links if l.get("url") and l.get("title")
    )
    links_html = (f'\n    <p class="desc-links-title">Links aus Beschreibung</p>\n'
                  f'    <ul class="desc-links">\n{link_items}\n    </ul>' if link_items else "")
    summary_html = f'\n    <p>{summary}</p>' if summary else ""
    return (f'<section class="beschreibung">\n'
            f'    <h2>Aus der Videobeschreibung</h2>{summary_html}{links_html}\n  </section>')


def render(data):
    tpl = open(TEMPLATE, encoding="utf-8").read()
    url = f"https://youtu.be/{data['video_id']}"
    duration = f"{data['duration_min']} Min"

    # Tricks fortlaufend nummerieren, TOC + Cluster bauen
    toc_lines, cluster_blocks, n = [], [], 0
    for cl in data["clusters"]:
        tricks_html = []
        for tr in cl["tricks"]:
            n += 1
            toc_lines.append(
                f'      <a href="#t{n}"><span class="n">{n:02d}</span>{tr["title"]}</a>')
            if tr.get("time") or tr.get("sec"):
                sec = tr.get("sec", parse_time(tr["time"]))
                time_html = (f'<a class="trick-time" href="{url}?t={sec}" '
                             f'target="_blank" rel="noopener">ab {tr["time"]}</a>')
            else:
                time_html = ""
            tricks_html.append(
                f'''    <div class="trick" id="t{n}">
      <span class="trick-num">{n:02d}</span>
      <div>
        <div class="trick-title-row"><p class="trick-title">{tr["title"]}</p>{time_html}</div>
        <p>{tr["body"]}</p>
      </div>
    </div>''')
        rng = f'<span class="cluster-range">{cl["range"]}</span>' if cl.get("range") else ""
        cluster_blocks.append(
            f'''  <section class="cluster">
    <div class="cluster-head"><h2>{cl["title"]}</h2>{rng}</div>
''' + "\n".join(tricks_html) + '''
  </section>''')

    repl = {
        "{{TITLE}}": data["title"],
        "{{SLUG}}": data["slug"],
        "{{VIDEO_URL}}": url,
        "{{CHANNEL}}": data["channel"],
        "{{DURATION}}": duration,
        "{{SR_SUMMARY}}": data.get("sr_summary", data["title"]),
        "{{LEDE}}": data.get("lede", ""),
        "{{KONTEXT_INTRO}}": kontextbox(data.get("kontext_intro")),
        "{{BESCHREIBUNG}}": beschreibung(data.get("beschreibung")),
        "{{TOC}}": "\n".join(toc_lines),
        "{{CLUSTERS}}": "\n\n".join(cluster_blocks),
        "{{KONTEXT_OUTRO}}": kontextbox(data.get("kontext_outro")),
    }
    for k, v in repl.items():
        tpl = tpl.replace(k, v)
    left = [m for m in re.findall(r"\{\{[A-Z_]+\}\}", tpl)]
    if left:
        print("WARN: nicht ersetzte Platzhalter:", left, file=sys.stderr)
    return tpl


def save_thumb(video_id, slug, force=False):
    os.makedirs(THUMBS, exist_ok=True)
    out = os.path.join(THUMBS, slug + ".jpg")
    if os.path.exists(out) and not force:
        print(f"  Thumb existiert, uebersprungen: {out}")
        return out
    url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=30).read()
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(raw)).convert("RGB").resize((480, 360), Image.LANCZOS)
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=82); raw = buf.getvalue()
    except Exception as e:
        print(f"  PIL nicht verfuegbar ({e}); hqdefault.jpg unveraendert gespeichert.", file=sys.stderr)
    open(out, "wb").write(raw)
    print(f"  Thumb gespeichert: {out} ({len(raw)} B)")
    return out


def insert_card(data):
    html = open(INDEX, encoding="utf-8").read()
    slug, title, cat = data["slug"], data["title"], data["category"]
    if f'href="{slug}.html"' in html:
        print(f"  Karte fuer {slug} existiert bereits - index.html unveraendert.")
        return
    datedt = data["date"] + "T" + data.get("time", "12:00")
    card = (
        f'      <a class="entry-card" data-date="{datedt}" href="{slug}.html">\n'
        f'        <img class="entry-thumb" src="assets/thumbs/{slug}.jpg" alt="Vorschaubild: {title}">\n'
        f'        <div class="entry-info">\n'
        f'          <p class="entry-title">{title}</p>\n'
        f'          <div class="entry-meta">\n'
        f'            <span>{data["channel"]}</span><span class="sep">&middot;</span>'
        f'<span>{data["duration_min"]} Min</span><span class="sep">&middot;</span><span>{dmy(data["date"])}</span>\n'
        f'          </div>\n'
        f'        </div>\n'
        f'      </a>\n')

    # Sektion anhand des <h2> finden (& und &amp; tolerieren)
    sections = re.split(r'(?=<section class="category">)', html)
    cat_norm = cat.replace("&amp;", "&")
    hit = -1
    for i, sec in enumerate(sections):
        m = re.search(r'<div class="category-head"><h2>(.*?)</h2>', sec)
        if m and m.group(1).replace("&amp;", "&").strip() == cat_norm.strip():
            hit = i; break
    if hit < 0:
        raise SystemExit(f"FEHLER: Kategorie {cat!r} nicht in index.html gefunden. "
                         f"Vorhandene Kategorien pruefen oder neue Kategorie manuell anlegen.")
    sec = sections[hit]
    anchor = '<div class="entries">\n'
    if anchor not in sec:
        raise SystemExit("FEHLER: <div class=\"entries\"> in der Zielsektion nicht gefunden.")
    sec = sec.replace(anchor, anchor + card, 1)
    # Zaehler erhoehen
    def bump(mm):
        n = int(mm.group(1)) + 1
        return f'<span class="category-count">{n} {"Eintrag" if n == 1 else "Eintraege"}</span>'
    sec = re.sub(r'<span class="category-count">(\d+) Eintr\w+</span>', bump, sec, count=1)
    sections[hit] = sec
    open(INDEX, "w", encoding="utf-8").write("".join(sections))
    print(f"  Karte in Kategorie {cat!r} eingefuegt, Zaehler erhoeht.")


def main():
    ap = argparse.ArgumentParser(description="Feldbuch-Transkriptseite erzeugen.")
    ap.add_argument("json", help="Pfad zur JSON-Inhaltsdatei")
    ap.add_argument("--dry-run", action="store_true",
                    help="HTML nur nach --out schreiben; kein Thumb-Download, kein index.html-Edit")
    ap.add_argument("--out", help="Ausgabepfad (Default: <slug>.html im Transkriptordner)")
    ap.add_argument("--no-thumb", action="store_true", help="Thumbnail-Download ueberspringen")
    ap.add_argument("--force-thumb", action="store_true", help="Thumbnail neu laden, auch wenn vorhanden")
    ap.add_argument("--no-index", action="store_true", help="index.html nicht veraendern")
    args = ap.parse_args()

    data = json.load(open(args.json, encoding="utf-8"))
    for req in ("slug", "video_id", "title", "channel", "duration_min", "date", "category", "clusters"):
        if req not in data:
            raise SystemExit(f"FEHLER: Pflichtfeld '{req}' fehlt in der JSON.")

    html = render(data)
    out = args.out or os.path.join(ROOT, data["slug"] + ".html")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)
    print(f"HTML geschrieben: {out} ({len(html)} B)")

    if args.dry_run:
        print("--dry-run: Thumbnail und index.html unveraendert.")
        return
    if not args.no_thumb:
        save_thumb(data["video_id"], data["slug"], force=args.force_thumb)
    if not args.no_index:
        insert_card(data)
    print("Fertig. Live-Link:")
    print(f"https://yabba-ch.github.io/youtubetranskript/YouTube-VideoTranskripte/{data['slug']}.html")


if __name__ == "__main__":
    main()
