---
name: gribouille
description: Generate, review, or refactor Gribouille plots in Typst following an opinionated set of best practices. Use whenever the user writes a #plot() call with the @preview/gribouille package, maps aesthetics, picks a theme, tweaks scales, sets up facets, or exports a figure. Typst-specific.
---

# Gribouille Coding Skill

You are an expert Typst and Gribouille assistant. Follow these rules strictly when generating or reviewing Gribouille code. Gribouille is a ggplot2-like grammar-of-graphics package for Typst. This skill covers the coding side only. For chart design principles, pair it with a dedicated dataviz skill. Use the [Gribouille gallery](https://m.canouil.dev/gribouille/gallery/) for implementation patterns and [Data to Viz](https://www.data-to-viz.com/) when chart choice is uncertain.

## Call Shape

```typst
#import "@preview/gribouille:0.8.0": *

#plot(
  data: penguins,
  mapping: aes(x: "flipper-len", y: "body-mass", colour: "species"),
  layers: (
    geom-point(size: 2pt),
    geom-smooth(method: "lm"),
  ),
  scales: scales(y: scale-continuous(labels: format-comma())),
  labels: labels(title: "Penguins", x: "Flipper length (mm)", y: "Body mass (g)"),
  theme: theme-minimal(),
  width: 12cm,
  height: 8cm,
)
```

- The API is pre-1.0: pin the version, and check [Typst Universe](https://typst.app/universe/package/gribouille) for the latest one.
- `data` is an array of row dictionaries, a dictionary of column arrays, or a built-in dataset (`penguins`, `mpg`, `economics`). Load a CSV with `#let rows = csv("data.csv", row-type: dictionary)` and pass `data: rows`.
- `mapping: aes(...)` links column names (strings) to aesthetics. `layers` is a tuple of `geom-*` calls, so a single layer needs a trailing comma: `(geom-point(),)`.
- Optional arguments: `scales`, `coord`, `facet`, `labels`, `guides`, `theme`, `alt`, `width` (default `10cm`), `height` (default `7cm`).
- Scale constructors take no aesthetic. The key of `scales()` sets it: `scales(colour: scale-viridis-d())`, not `scale-colour-viridis-d()`; `scales(x: scale-log10())`, not `scale-x-log10()`.

## Coding Conventions

- Use `kebab-case` for column names and variables, as in the built-in datasets: `"flipper-len"`.
- Put each layer, scale, and argument on its own line.
- Map variables inside `aes()`; set constants as layer arguments: `geom-point(colour: red)`, not `aes(colour: "red")`.
- Use `geom-col()` when you have explicit y values, `geom-bar()` only when counting.
- Use native Typst (`.map()`, `.filter()`, `.sorted()`) to prepare rows. Use `summarise`, `count`, `pivot-longer`, and `left-join` to wrangle columns.
- Never build one layer for each group with `.map()`. Map the variable in `aes()` (`colour:`, `fill:`, `shape:`, `linetype:`, or `group:`) and Gribouille splits the data, applies the palette, and draws the legend. `colour` and `fill` apply a palette and draw a legend; `shape` and `linetype` draw a legend with their own glyph; `group` only splits the data.

```typst
// Wrong: one layer for each species, with hand-made colors (rows is an array of dictionaries).
layers: species.map(s => geom-point(data: rows.filter(r => r.species == s), colour: palette.at(s))),

// Right: one layer, and the grouping lives in the mapping.
mapping: aes(x: "flipper-len", y: "body-mass", colour: "species"),
layers: (geom-point(),),
```

- Wide data (one column for each series) goes through `pivot-longer`, then the new key column is mapped:

```typst
#plot(
  data: pivot-longer(mpg, ("cty", "hwy"), names-to: "metric", values-to: "mpg"),
  mapping: aes(x: "displ", y: "mpg", colour: "metric"),
  layers: (geom-point(),),
)
```

- Use the grammar before raw Typst. Reach for `grid`, `place`, `geom-rect`, `geom-segment`, or `geom-typst` only when no geom, scale, or theme setting can do the job:

| You want | Use | Not |
| --- | --- | --- |
| Plots side by side, a shared title | `compose(defer(plot, ...), labels: labels(title: ...))` | `grid` of plots with `text()` titles |
| Filled or stacked bars | `geom-col(position: "fill")` or `"stack"` | `geom-rect` with hand-computed heights |
| Axis ticks, labels, gridlines | scale `breaks` and `labels`, theme `panel-grid-major-x` | `geom-segment` grids, `geom-typst` tick labels |
| A log axis | `scale-log10()` | `calc.log` applied to the data |
| Number formats | `format-comma()`, `format-percent()`, `format-currency()` | hand-written formatting functions |
| Styled labels | `geom-text(font:, size:, colour:)` | `geom-typst` with `text(...)[...]` |
| Labels that do not overlap | `geom-text(repel: true, segment: true)` | hand-made offsets for each label |

## Theme & Styling

- Start from `theme-minimal()` and override elements with `theme()`: `theme-minimal() + theme(plot-title: element-text(weight: "bold"))`. Other base themes include `theme-grey()`, `theme-classic()`, `theme-bw()`, `theme-light()`, `theme-dark()`, `theme-linedraw()`, and `theme-void()`.
- Use `element-blank()` to remove an element: `theme(panel-grid-minor: element-blank())`.
- Style text through `element-text(size:, weight:, colour:, font:)`, and lines through `element-line()`.
- Set the font for a whole `compose()` once with `compose(theme:)`; the panels do not need a theme of their own.

## Scale & Axis Best Practices

- Use `coord-cartesian(x-limits: ..., y-limits: ...)` for zooming (preserves data). Use `scale-continuous(limits: ...)` only to filter data.
- Format axis labels with `format-comma()`, `format-percent()`, etc.: `scale-continuous(labels: format-percent())`.
- Set ticks with `breaks:`, or with `breaks-width(1000)`. To hide them, write `breaks: ()`, not `breaks: none`.
- Control padding with `expand:`, for example `scale-continuous(expand: (0%, 0%))`.
- Pick palettes with `scale-viridis-d()`, `scale-okabe-ito()`, `scale-brewer()`, or `scale-manual(values: ...)`.

## Legend Guidelines

- Position all legends with `theme(legend-position: "bottom")` (or `"top"`, `"left"`, `"none"`).
- Hide every legend with `guides(default: none)`, one legend with `guides(colour: none)`.
- Remove a legend title with `labels(colour: none)`, or rename it with `labels(colour: "Species")`.
- Use `guide-legend(nrow: 1)` through `guides(colour: guide-legend(nrow: 1))` for compact horizontal legends.
- Add direct labels with `geom-text()` or `geom-label()`.

## Faceting

- Use `facet-wrap("species", ncolumn: 3)` for a single variable, `facet-grid(rows: "sex", columns: "species")` for cross-breakdowns.
- `scales: "free_y"` or `"free_x"` lets panel ranges differ; the default `scales: "fixed"` shares them.

## Export Settings

- Compile with `typst compile plot.typ plot.png --ppi 150` (screen), `plot.svg`, or `plot.pdf` (print, vector).
- For a standalone figure, start the file with `#set page(width: auto, height: auto, margin: 5mm)` so the page fits the plot.
- Set `width` and `height` on `plot()` for the final reading size; `--ppi` does not fix text that is too small.
- Give `height` a fixed length unless the container has a set height.
- Set `alt:` on `plot()` for tagged PDF output.

## Common Pitfalls to Avoid

- Don't write `color`: aesthetics use `colour`, and Gribouille rejects `color`, with the valid channels listed in the error.
- Don't forget `as-numeric(rows, "col")` for each numeric column of CSV data: string numbers stay discrete, so the axis spaces values evenly instead of using a continuous scale.
- Don't pass constants as columns: `aes(x: 0)` fails. Add a constant column, or use a layer argument.
- Don't use `hjust` on text geoms: place a label with `anchor: "west"`.
- Don't read `geom-point(size:)` as a diameter: it is a radius, as in `circle(radius:)`.
- Don't give a layer its own `data` without `x` and `y` columns: it draws nothing, with no error. Map them in the layer, or set `inherit-aes: false` with a full mapping.
- Don't pass a discrete `y` to `geom-col()`: it draws nothing. Use a discrete `x` and `coord-flip()`.
- Don't expect `annotate()` or `geom-blank()` to leave the axes alone: they train the scales, so set `limits` to keep the range.
- Don't rely on the default fill of `geom-area()` or `geom-ribbon()` for overlapping groups: it is opaque, so pass `alpha:`.
- Don't pass `expand:` to `scale-log10()`: use `scale-continuous(transform: "log10", expand: ...)`.
- Don't draw maps with points and `coord-fixed()`: Gribouille has no geo geoms.
- Don't use `.map()` to loop over groups: see Coding Conventions.

## Check the API

Never recall a geom, stat, scale, or argument from memory: the names and arguments change between releases. Read the index at <https://m.canouil.dev/gribouille/llms.txt>, then fetch the `.llms.md` page of the symbol (for example `.../reference/geoms/geom-smooth.llms.md`) and use only the arguments documented there. Compile with `typst compile` before claiming success, and read the error hint if it fails.
