---
name: inspiration
description: 'Use BEFORE writing any code that draws a chart, map, plot or dashboard (D3, ggplot2, Matplotlib, geopandas, plotly, Vega…), even for a one-line request like "make a map of X", "fais-moi une carte de X", "visualise Z", and even when the work starts with fetching data. Searches curated galleries of published dataviz as one catalog (dataviz-inspiration.com, Dataviz Index) for 3–5 real references to borrow ideas from — form, annotation, palette, layout — with links back to each source. Also use when asked for chart ideas, examples or references, or to improve a chart that looks generic. Triggers: carte, graphique, visualisation, dataviz, infographie, tableau de bord, chart, map, plot, graph, figure, dashboard, choropleth.'
---


# Inspiration

Agents draw correct but generic charts: they have no visual culture. This skill gives you one,
by searching curated galleries of published visualizations as a single catalog:

| Source | What it brings | Language |
|---|---|---|
| [dataviz-inspiration.com](https://www.dataviz-inspiration.com) — Yan Holtz | 450+ projects (NYT, Bloomberg, independent designers…), tagged by chart type and design technique, each with "what the chart does" + context. CC BY 4.0. | English |
| [Dataviz Index](https://datavizindex.fr) — WeDoData | 300 picks from the *Buena Vista Data Club* newsletter, tagged by type, theme and format (scrollytelling, data art, 3D, physical…), with an editorial comment. | French |

Both are read live from their public endpoints and cached for 24 h. Never copy them into a project.

## Workflow

### 1. Frame the question before searching

Work out what the reader must see. That decides the **family** (it works across both sources):

| The reader must see…                  | `--family`     |
|---------------------------------------|----------------|
| how values are spread                 | `distribution` |
| a relationship between variables      | `correlation`  |
| an order, a comparison of quantities  | `ranking`      |
| shares of a whole, hierarchy          | `partOfAWhole` |
| change over time                      | `evolution`    |
| where (geography)                     | `map`          |
| flows, connections, networks          | `flow`         |

If the chart type is not chosen yet, use the **chart-type** skill first; for geographic data, the
**maps** skill; for the palette, the **color** skill (all in this collection). For more method
references (From Data to Viz caveats, Data Viz Catalogue, Insee and icem7 for French
public-statistics style), read [references/method.md](references/method.md).

Also note the techniques you may need (annotation, small multiples, direct labeling, highlight,
bivariate coloring, uncertainty, scrollytelling…) and the medium (static or interactive).

### 2. Search

```bash
python3 scripts/search_viz.py "<keywords in English AND French>" --family <family> [options]
```

`scripts/` is relative to this skill's directory. Python 3.9+, standard library only.

| Option | Meaning |
|---|---|
| `"query"` | free text over title, descriptions, author, types, labels, themes (accents and case ignored). **Give keywords in both languages** (`"election élection turnout participation"`): one gallery is English, the other French. |
| `--family F` | chart family, across sources |
| `--type T` | exact chart type, repeatable (OR) — `--vocab` lists them (`choropleth`, `sankey`, `cartographies`…) |
| `--label L` | technique or format, repeatable (**AND**): `annotation`, `small multiples`, `scrollytelling`, `3d`, `data art`… |
| `--source S` | `dataviz-inspiration` or `datavizindex` only |
| `--tool T`, `--interactive` / `--no-interactive`, `--luminosity light\|dark`, `--since 2022` | narrow down |
| `--limit N` | default 8 |
| `--format json` | full records |
| `--thumbs DIR` | also download the results' thumbnails into `DIR`, to look at them |
| `--vocab` | list families, chart types, labels and themes with counts — run it when unsure of names |

Search tactics:
- Start broad (family + a few bilingual keywords), then add `--label` to target a technique.
- No hit on the topic? Drop the query and search by family + technique: the *form* matters more
  than the subject. A good migration chart can inspire an election chart.
- Without a query, results come favorites first, then most recent.
- If one source is unreachable the other still answers; the output says which one is missing.

### 3. Look before you borrow

Pick the 3–5 most relevant results. Download their thumbnails with `--thumbs <scratch dir>` and
**view them** (images you can read; some are animated GIFs — you see the first frame). The text
says what the designer did; the image shows how dense, how annotated, how colored it really is.

### 4. Present the references, then design

For each reference you keep, give the user:
- title and author;
- **two links, always**: the original work (`Original`) and the gallery page where it was found
  (`Found via …`). The galleries did the curation: sending readers back to them is the point;
- **the specific idea to borrow** (e.g. "annotations placed directly on the peaks instead of a
  legend", "bivariate palette with a 3×3 key", "small multiples sorted by slope");
- why it fits this data and this audience.

Then propose the design, saying which idea comes from which reference. Adapt the ideas — never
present a copy of someone else's chart as original work.

For example:

> **South Gaza's services and a doubling of population** — Bloomberg ·
> [original](https://www.bloomberg.com/graphics/2023-israel-gaza-evacuation-hospital-access/) ·
> found via [dataviz-inspiration.com](https://www.dataviz-inspiration.com/choropleth)
> → borrow: a bivariate palette with a 2D key to cross two variables on one map, plus a
> before/after toggle to show the shift.

End with a linked credit line for each gallery you used:

> References found via [dataviz-inspiration.com](https://www.dataviz-inspiration.com) (Yan Holtz,
> CC BY 4.0) and [Dataviz Index](https://datavizindex.fr) (WeDoData).

If the deliverable itself has a sources, notes or colophon area (report, notebook, web page,
slide notes), put the same references and credit line there too.

## Rules

- **Images are not reusable.** Thumbnails are screenshots of work by their authors. Look at them;
  never embed, ship or redistribute them.
- **Always cite and link back.** Every reference you mention carries its original link and its
  gallery link, and every answer that used the galleries ends with the linked credit line. No
  reference without its links, ever.
- Yan Holtz's catalog data is CC BY 4.0: credit it. Dataviz Index comments are WeDoData's
  editorial text: paraphrase them and link to the entry, do not republish them.
- If no source can be fetched and no cache exists, say so and carry on with your own judgment —
  do not invent references.
- Some entries have an empty description: rely on the context and the thumbnail.
