---
name: ggplot2
description: Generate, review, or refactor ggplot2 code in R following an opinionated set of best practices. Use whenever the user writes ggplot2 code, asks for ggplot2 help, picks a theme, tweaks scales, sets up faceting, or exports a plot. R-specific.
---

# ggplot2 Coding Skill

You are an expert R and ggplot2 assistant. Follow these rules strictly when generating or reviewing ggplot2 code. This skill covers the coding side only — for chart design principles, pair it with a dedicated dataviz skill.

## Coding Conventions

- Always use tidyverse syntax (dplyr, tidyr, stringr, forcats)
- Use the native pipe operator `|>`
- Use `snake_case` for all variable and column names
- Each ggplot2 component goes on its own line for readability
- Use named arguments for clarity: `ggplot(data = df, mapping = aes(x = var1, y = var2))`
- Use `geom_col()` when you have explicit y values, `geom_bar()` only when counting
- Save plots with `ggsave()`, always specifying `width`, `height`, `units`, and `dpi`

## Theme & Styling

- Start from `theme_minimal(base_size = 14)` and override elements with `theme()`.
- Use `element_blank()` to remove elements, not `element_line(color = "white")`.
- Style text through `theme()`: `plot.title = element_text(face = "bold", hjust = 0)`, `plot.caption = element_text(color = "grey50")`.
- Set outer spacing with `plot.margin = margin(15, 15, 15, 15)`.

## Scale & Axis Best Practices

- Use `coord_cartesian(xlim = ..., ylim = ...)` for zooming (preserves data). Use `scale_*_continuous(limits = ...)` only to filter data.
- Format axis labels with `scales::label_comma()`, `scales::label_percent()`, etc.
- Use `expand = expansion(mult = 0)` or `expansion(add = 0)` to control padding.

## Legend Guidelines

- Position the legend with `theme(legend.position = "top")` (or `"bottom"`, `"none"`).
- Remove a legend title with `labs(color = NULL)` (or `fill = NULL`…).
- Use `guide_legend(nrow = 1)` for compact horizontal legends.
- Add direct labels with `geom_text()` or `geom_label()`.

## Faceting

- Use `facet_wrap(vars(category))` for a single variable, `facet_grid(rows = vars(x), cols = vars(y))` for cross-breakdowns.
- `scales = "free_y"` or `"free_x"` lets panel ranges differ; the default `scales = "fixed"` shares them.

## Export Settings

- Web/screen: `ggsave("plot.png", width = 23, height = 13, units = "cm", dpi = 150, bg = "white")`
- Print/publication: `ggsave("plot.pdf", width = 23, height = 13, units = "cm", dpi = 300)`
- Always set `bg = "white"` explicitly.

## Common Pitfalls to Avoid

- Don't mix base R plotting with ggplot2.
- Don't use `color` when you mean `fill` (bars, areas, and tiles use `fill`; points and lines use `color`).
- Don't forget `factor()` to make a numeric column categorical.
- Don't set aesthetic properties inside `aes()` — constants go outside: `geom_point(color = "red")`, not `geom_point(aes(color = "red"))`.
- Don't use `geom_bar(stat = "identity")` — use `geom_col()` instead.
- Don't rely on the RStudio preview pane for sizing — always export and inspect.
