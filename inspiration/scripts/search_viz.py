#!/usr/bin/env python3
"""Search curated dataviz galleries from the command line, as one catalog.

Sources, read live from their public endpoints and cached locally (24 h by default;
a stale cache is used when offline). Nothing is redistributed.

- dataviz-inspiration.com by Yan Holtz (English): catalog data under CC BY 4.0.
- Dataviz Index by WeDoData (French): editorial selection from the
  Buena Vista Data Club newsletter; descriptions are fetched on demand.

Images belong to their authors: look at them, never reuse them.
Standard library only, Python 3.9+.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path
from typing import Any, Iterable, Optional

DEFAULT_CACHE_DIR = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "dataviz-inspiration"

SOURCES: dict[str, dict[str, str]] = {
    "dataviz-inspiration": {
        "name": "dataviz-inspiration.com",
        "home": "https://www.dataviz-inspiration.com",
        "url": "https://www.dataviz-inspiration.com/viz-list.json",
        "credit": "by Yan Holtz — catalog data licensed under CC BY 4.0",
    },
    "datavizindex": {
        "name": "Dataviz Index",
        "home": "https://datavizindex.fr",
        "url": "https://datavizindex.fr/api/blocks",
        "credit": "by WeDoData — selection and descriptions © WeDoData; link, do not republish",
    },
}
YAN_SITE = SOURCES["dataviz-inspiration"]["home"]
DVI_SITE = SOURCES["datavizindex"]["home"]
DVI_PAGE = DVI_SITE + "/inspiration-infographie-datavisualisation/"
YAN_UNKNOWN_DATE = "1000"  # dataviz-inspiration's sentinel for "date unknown"

# Chart families, as defined in dataviz-inspiration's source (util/sectionDescription.tsx, MIT).
FAMILIES: dict[str, list[str]] = {
    "distribution": ["violin", "density", "histogram", "boxplot", "ridgeline"],
    "correlation": ["scatter", "heatmap", "correlogram", "bubble", "connectedScatter", "density2d"],
    "ranking": ["barplot", "radar", "wordcloud", "parallel", "lollipop", "circularBarplot"],
    "partOfAWhole": ["treemap", "venn", "donut", "pie", "dendrogram", "circularPacking"],
    "evolution": ["line", "area", "stackedArea", "stream"],
    "map": ["map", "choropleth", "hexbin", "cartogram", "connection", "bubbleMap"],
    "flow": ["chordDiagram", "network", "sankey", "arc", "edgeBundling"],
}
# Dataviz Index chart types mapped onto those families (our mapping; unlisted types have no family).
DVI_FAMILIES: dict[str, str] = {
    "cartographies": "map",
    "histogrammes-et-barres": "ranking",
    "classements": "ranking",
    "radars": "ranking",
    "courbes-et-series": "evolution",
    "bulles-et-points": "correlation",
    "heatmaps": "correlation",
    "treemaps-et-diagrammes-de-voronoi": "partOfAWhole",
    "pie-charts-et-donuts": "partOfAWhole",
    "dendrogrammes": "partOfAWhole",
    "reseaux-et-graphes-relationnels": "flow",
    "diagrammes-de-flux-et-sankey": "flow",
}
YAN_TYPE_PAGES = {t for types in FAMILIES.values() for t in types}  # types with a page on the site
TYPE_TO_FAMILY = {t: fam for fam, types in FAMILIES.items() for t in types} | DVI_FAMILIES

# Field weights for free-text ranking.
WEIGHTS = {"title": 3, "chartTypes": 2, "labels": 2, "themes": 2, "description": 2, "author": 1, "context": 1}
STOPWORDS = {
    "a", "an", "and", "of", "the", "in", "on", "for", "to", "with", "by",
    "de", "des", "du", "la", "le", "les", "un", "une", "et", "en", "au", "aux", "par", "pour", "sur",
}


# --- network & cache -------------------------------------------------------

def _download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "dataviz-skills/inspiration (+https://github.com/holtzy/dataviz-skills)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def _write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)


def load_source(name: str, cache_dir: Path = DEFAULT_CACHE_DIR, ttl_hours: float = 24) -> Any:
    """Return a source's raw payload, from a fresh cache, the network, or a stale cache."""
    cache = Path(cache_dir) / f"{name}.json"
    if cache.exists() and time.time() - cache.stat().st_mtime < ttl_hours * 3600:
        return json.loads(cache.read_text(encoding="utf-8"))
    url = SOURCES[name]["url"]
    try:
        raw = _download(url)
        data = json.loads(raw)
        _write_atomic(cache, raw)
        return data
    except (OSError, ValueError) as exc:
        if cache.exists():
            print(f"warning: could not refresh {name} ({exc}); using cached copy", file=sys.stderr)
            return json.loads(cache.read_text(encoding="utf-8"))
        raise RuntimeError(f"cannot fetch {url} and no cached copy at {cache}: {exc}") from exc


# --- normalization ---------------------------------------------------------
# Common schema: uid, source, lang, title, author, date (YYYY-MM or ""), url (original work),
# page (where the gallery lists it), via (gallery name + home), chartTypes, families, labels, themes, tools,
# interactive (bool or None), luminosity, favorite, description, context, thumbnail.

def _families(types: Iterable[str]) -> list[str]:
    out: list[str] = []
    for t in types:
        fam = TYPE_TO_FAMILY.get(t)
        if fam and fam not in out:
            out.append(fam)
    return out


def _via(source: str) -> dict[str, str]:
    return {"name": SOURCES[source]["name"], "url": SOURCES[source]["home"]}


def normalize_yan(payload: dict[str, Any]) -> list[dict[str, Any]]:
    items = []
    for it in payload.get("items") or []:
        date = it.get("date") or ""
        types = it.get("chartTypes") or []
        items.append({
            "uid": f"yan:{it['id']}",
            "source": "dataviz-inspiration",
            "lang": "en",
            "title": it.get("title") or "",
            "author": it.get("author") or "",
            "date": "" if date.startswith(YAN_UNKNOWN_DATE) else date[:7],
            "url": it.get("url") or "",
            # no per-viz page on the site: the chart-type page that lists it
            "page": next((f"{YAN_SITE}/{t}" for t in types if t in YAN_TYPE_PAGES), YAN_SITE),
            "via": _via("dataviz-inspiration"),
            "chartTypes": types,
            "families": _families(types),
            "labels": it.get("labels") or [],
            "themes": [],
            "tools": [t["name"] if isinstance(t, dict) else t for t in it.get("tools") or []],
            "interactive": bool(it.get("interactive")),
            "luminosity": it.get("luminosity") or [],
            "favorite": bool(it.get("favorite")),
            "description": (it.get("chartDescription") or "").strip(),
            "context": (it.get("contextDescription") or "").strip(),
            "thumbnail": (it.get("images") or {}).get("thumbnail"),
        })
    return items


def normalize_dvi(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items = []
    for b in blocks:
        if b.get("section_dataviz_index") != "S'inspirer":
            continue  # "Se former" entries are tutorials, not visualizations
        types = [t["slug"] for t in b.get("types") or []]
        formats = [t["label"].lower() for t in b.get("formats") or []]
        thumb = b.get("thumbnail") or {}
        path = thumb.get("path") or (f"/files/{b['file_local_path']}" if b.get("file_local_path") else None)
        items.append({
            "uid": f"dvi:{b['slug']}",
            "source": "datavizindex",
            "lang": "fr",
            "title": b.get("title") or "",
            "author": b.get("source") or "",
            "date": (b.get("publication_date") or b.get("created_time") or "")[:7],
            "url": b.get("source_url") or DVI_PAGE + b["slug"],
            "page": DVI_PAGE + b["slug"],
            "via": _via("datavizindex"),
            "chartTypes": types,
            "families": _families(types),
            "labels": formats,
            "themes": [t["label"] for t in b.get("themes") or []],
            "tools": [t if isinstance(t, str) else t.get("name", "") for t in b.get("tools") or []],
            "interactive": True if "interactif et web" in formats else None,
            "luminosity": [],
            "favorite": False,
            "description": "",
            "context": "",
            "thumbnail": DVI_SITE + path if path else None,
        })
    return items


NORMALIZERS = {"dataviz-inspiration": normalize_yan, "datavizindex": normalize_dvi}


def load_items(
    sources: Optional[list[str]] = None, cache_dir: Path = DEFAULT_CACHE_DIR, ttl_hours: float = 24
) -> tuple[list[dict[str, Any]], list[str]]:
    """Load and normalize every requested source; a failing source is reported, not fatal."""
    items: list[dict[str, Any]] = []
    failed: list[str] = []
    for name in sources or list(SOURCES):
        try:
            items.extend(NORMALIZERS[name](load_source(name, cache_dir=cache_dir, ttl_hours=ttl_hours)))
        except RuntimeError as exc:
            print(f"warning: source {name} unavailable: {exc}", file=sys.stderr)
            failed.append(name)
    return items, failed


# --- Dataviz Index descriptions, on demand ---------------------------------

def _dvi_description(page_html: str) -> str:
    m = re.search(r'<meta name="description" content="([^"]*)"', page_html)
    return re.sub(r"\s+", " ", html.unescape(m.group(1))).strip() if m else ""


def enrich_descriptions(items: list[dict[str, Any]], cache_dir: Path = DEFAULT_CACHE_DIR) -> None:
    """Fill the description of Dataviz Index items from their entry page (cached)."""
    todo = [it for it in items if it["source"] == "datavizindex" and not it["description"]]
    if not todo:
        return
    cache = Path(cache_dir) / "datavizindex-descriptions.json"
    known: dict[str, str] = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else {}
    changed = False
    for it in todo:
        if it["uid"] not in known:
            try:
                known[it["uid"]] = _dvi_description(_download(it["page"]).decode("utf-8", "replace"))
                changed = True
            except OSError as exc:
                print(f"warning: description of {it['uid']} unavailable ({exc})", file=sys.stderr)
                continue
        it["description"] = known[it["uid"]]
    if changed:
        _write_atomic(cache, json.dumps(known, ensure_ascii=False).encode("utf-8"))


# --- filtering -------------------------------------------------------------

def filter_items(
    items: Iterable[dict[str, Any]],
    types: Optional[list[str]] = None,
    family: Optional[str] = None,
    labels: Optional[list[str]] = None,
    tools: Optional[list[str]] = None,
    interactive: Optional[bool] = None,
    luminosity: Optional[str] = None,
    since: Optional[str] = None,
    source: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Types match ANY chart type; labels and tools must ALL be present."""
    if family and family not in FAMILIES:
        raise ValueError(f"unknown family {family!r}; choose from {', '.join(FAMILIES)}")
    wanted_types = set(types or [])
    wanted_labels = {lab.lower() for lab in labels or []}
    wanted_tools = {t.lower() for t in tools or []}

    out = []
    for it in items:
        if source and it["source"] != source:
            continue
        if family and family not in it["families"]:
            continue
        if wanted_types and not wanted_types & set(it["chartTypes"]):
            continue
        if wanted_labels and not wanted_labels <= {lab.lower() for lab in it["labels"]}:
            continue
        if wanted_tools and not wanted_tools <= {t.lower() for t in it["tools"]}:
            continue
        if interactive is not None and it["interactive"] is not interactive:
            continue
        if luminosity and luminosity not in it["luminosity"]:
            continue
        if since and (not it["date"] or it["date"] < since):
            continue
        out.append(it)
    return out


# --- ranking ---------------------------------------------------------------

def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.replace("’", "'"))
    return "".join(c for c in text if not unicodedata.combining(c)).lower()


def _tokens(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", _normalize(text))
    return [w.rstrip("s") if len(w) > 3 else w for w in words if w not in STOPWORDS]


def _field_text(item: dict[str, Any], field: str) -> str:
    value = item.get(field)
    if isinstance(value, list):
        return " ".join(v.replace("-", " ") for v in value)
    return value or ""


def score(item: dict[str, Any], query_tokens: list[str]) -> int:
    total = 0
    for field, weight in WEIGHTS.items():
        field_tokens = set(_tokens(_field_text(item, field)))
        total += weight * sum(1 for q in query_tokens if q in field_tokens)
    return total


def rank(items: Iterable[dict[str, Any]], query: Optional[str]) -> list[dict[str, Any]]:
    """Rank by query score; without a query, favorites first then most recent."""
    items = list(items)
    if not query:
        return sorted(items, key=lambda it: (it["favorite"], it["date"]), reverse=True)
    q = _tokens(query)
    scored = [(score(it, q), it) for it in items]
    scored = [(s, it) for s, it in scored if s > 0]
    scored.sort(key=lambda p: (p[0], p[1]["favorite"], p[1]["date"]), reverse=True)
    return [it for _, it in scored]


# --- thumbnails ------------------------------------------------------------

def download_thumbnails(results: list[dict[str, Any]], dest: Path) -> list[Path]:
    """Save each result's thumbnail into dest, for viewing only. Failures are skipped."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    paths = []
    for it in results:
        url = it.get("thumbnail")
        if not url:
            continue
        try:
            data = _download(url)
        except OSError as exc:
            print(f"warning: thumbnail of {it['uid']} unavailable ({exc})", file=sys.stderr)
            continue
        source, _, ident = it["uid"].partition(":")
        path = dest / f"{source}-{ident[:40]}-{url.rsplit('/', 1)[-1].split('?')[0]}"
        path.write_bytes(data)
        paths.append(path)
    return paths


# --- rendering -------------------------------------------------------------

def credits_for(results: list[dict[str, Any]]) -> list[str]:
    used = {it["source"] for it in results}
    return [f"[{SOURCES[n]['name']}]({SOURCES[n]['home']}) {SOURCES[n]['credit']}" for n in SOURCES if n in used]


def render_markdown(results: list[dict[str, Any]], total: int) -> str:
    lines = [f"{total} matching visualizations, showing {len(results)}.", ""]
    for it in results:
        lines.append(f"## [{it['uid']}] {it['title']} — {it['author'] or '?'} ({it['date'] or 'date unknown'})")
        lines.append(f"- Original: {it['url']}")
        lines.append(f"- Found via {it['via']['name']}: {it['page']}")
        meta = f"- Source: {it['source']} ({it['lang']}) | Types: {', '.join(it['chartTypes'])}"
        if it["families"]:
            meta += f" [{', '.join(it['families'])}]"
        if it["labels"]:
            meta += f" | Labels: {', '.join(it['labels'])}"
        if it["themes"]:
            meta += f" | Themes: {', '.join(it['themes'])}"
        if it["tools"]:
            meta += f" | Tools: {', '.join(it['tools'])}"
        lines.append(meta)
        if it["description"]:
            lines.append(f"- What the chart does: {it['description']}")
        if it["context"]:
            lines.append(f"- Context: {it['context']}")
        if it["thumbnail"]:
            lines.append(f"- Thumbnail (look only, do not reuse): {it['thumbnail']}")
        lines.append("")
    for credit in credits_for(results):
        lines.append(f"_Source: {credit}._")
    if results:
        lines.append("_Images © their respective authors. Cite every reference with both links: the original and the gallery page._")
    return "\n".join(lines)


def render_vocab(items: list[dict[str, Any]]) -> str:
    def counts(field: str) -> dict[str, int]:
        c: dict[str, int] = {}
        for it in items:
            for v in it[field]:
                c[v] = c.get(v, 0) + 1
        return c

    types = counts("chartTypes")
    lines = ["Families (--family) and their chart types (--type), across sources:"]
    for fam in FAMILIES:
        members = [t for t in types if TYPE_TO_FAMILY.get(t) == fam]
        lines.append(f"- {fam}: " + ", ".join(f"{t} ({types[t]})" for t in members))
    orphans = [t for t in types if t not in TYPE_TO_FAMILY]
    if orphans:
        lines.append("- (no family): " + ", ".join(f"{t} ({types[t]})" for t in orphans))
    for field, title in (("labels", "Labels (--label, combined with AND)"), ("themes", "Themes (free-text query)")):
        c = counts(field)
        if c:
            lines += ["", f"{title}:", ", ".join(f"{k} ({n})" for k, n in sorted(c.items(), key=lambda p: -p[1]))]
    return "\n".join(lines)


# --- CLI -------------------------------------------------------------------

def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Search curated dataviz galleries (dataviz-inspiration.com, Dataviz Index).")
    p.add_argument("query", nargs="?", help="free-text keywords; give them in English AND French, e.g. 'election élection vote'")
    p.add_argument("--family", choices=list(FAMILIES), help="chart family (works across sources)")
    p.add_argument("--type", action="append", dest="types", help="exact chart type, repeatable (OR); see --vocab")
    p.add_argument("--label", action="append", dest="labels", help="design technique or format, repeatable (AND)")
    p.add_argument("--tool", action="append", dest="tools", help="tool used (R, python, d3.js…), repeatable (AND)")
    p.add_argument("--source", choices=list(SOURCES), help="restrict to one gallery")
    p.add_argument("--interactive", action=argparse.BooleanOptionalAction, default=None)
    p.add_argument("--luminosity", choices=["light", "dark"])
    p.add_argument("--since", help="only entries from this date on (YYYY or YYYY-MM)")
    p.add_argument("--limit", type=int, default=8)
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p.add_argument("--no-details", action="store_true", help="do not fetch Dataviz Index descriptions")
    p.add_argument("--thumbs", type=Path, metavar="DIR", help="also download the results' thumbnails into DIR (to look at, never to reuse)")
    p.add_argument("--vocab", action="store_true", help="list families, chart types, labels and themes with counts, then exit")
    p.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    p.add_argument("--ttl-hours", type=float, default=24)
    args = p.parse_args(argv)

    items, failed = load_items([args.source] if args.source else None, cache_dir=args.cache_dir, ttl_hours=args.ttl_hours)
    if not items:
        print("error: no source could be loaded", file=sys.stderr)
        return 2

    if args.vocab:
        print(render_vocab(items))
        return 0

    try:
        filtered = filter_items(
            items, types=args.types, family=args.family, labels=args.labels, tools=args.tools,
            interactive=args.interactive, luminosity=args.luminosity, since=args.since, source=args.source,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    ranked = rank(filtered, args.query)
    results = ranked[: args.limit]
    if not args.no_details:
        enrich_descriptions(results, cache_dir=args.cache_dir)

    if args.format == "json":
        print(json.dumps({
            "total": len(ranked),
            "unavailableSources": failed,
            "credits": credits_for(results),
            "imagesNotice": "Images show work by their respective authors; do not reuse them.",
            "results": results,
        }, ensure_ascii=False, indent=2))
    else:
        if failed:
            print(f"(sources unavailable: {', '.join(failed)})\n")
        print(render_markdown(results, total=len(ranked)))
    if args.thumbs:
        for path in download_thumbnails(results, args.thumbs):
            print(f"thumbnail: {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
