---
name: matplotlib
description: Generate, review, or refactor Python Matplotlib code following an opinionated set of best practices. Use whenever the user writes Matplotlib code, asks for Matplotlib help, customizes a theme, styles axes, adds annotations, lays out multiple axes, or exports a plot. Python-specific.
---

# Matplotlib Coding Skill

You are an expert Python and Matplotlib assistant. Follow these rules strictly when generating or reviewing Matplotlib code. This skill covers the coding side only. For chart design principles, pair it with a dedicated dataviz design skill.

## Coding Conventions

- Prefer the explicit object-oriented API: `fig, ax = plt.subplots()`.
- Avoid the stateful pyplot interface for chart construction except for imports and `plt.show()`.
- Use clear variable names: `fig`, `ax`, `axs`, `df`, `colors`, `palette`.
- Keep data preparation separate from chart styling.
- Use `pandas` for tabular data manipulation when useful.
- Use `layout="tight"` in `plt.subplots(...)` or call `fig.tight_layout()` before export when appropriate.
- For multiple panels, use `plt.subplots()` or `plt.subplot_mosaic()` and name axes clearly.
- Do not silently depend on global state. Return `fig, ax` from reusable plotting functions.

## Basic Chart Patterns

- Horizontal bars: `ax.barh(labels, values)`, especially when category labels are long.
- Lines: `ax.plot(x, y, linewidth=...)` for trends over time.
- Scatter: `ax.scatter(x, y, s=..., c=...)` for relationships.
- Histograms: `ax.hist(values, bins=...)`; explain bin choices when relevant.
- Use `ax.stem(..., orientation="horizontal")` for lollipop-style charts when a lighter alternative to bars is useful.

## Theme and Styling

- Remove unnecessary spines by default: `ax.spines[["top", "right"]].set_visible(False)`.
- Remove tick marks when they add clutter: `ax.tick_params(length=0)`.
- Use grid lines only when they improve value reading. Prefer subtle horizontal grid lines for horizontal bar charts.
- Style grid lines lightly: thin, low-contrast, behind data.
- Set labels, ticks, and text colors deliberately. Avoid pure black for every secondary element.
- Use `rcParams` for reusable themes. Useful keys include:
  - `axes.spines.top`, `axes.spines.right`
  - `axes.facecolor`, `figure.facecolor`
  - `axes.prop_cycle`
  - `xtick.major.size`, `ytick.major.size`
  - `grid.color`, `grid.linewidth`
- For custom default color cycles, use `cycler`: `plt.rcParams["axes.prop_cycle"] = cycler("color", palette)`.

## Text, Titles, and Annotation

- Use `fig.text()` for figure-level title, subtitle, captions, and source notes.
- Use `ax.text()` for labels tied to data coordinates.
- Prefer narrative titles that state the insight.
- Use subtitles for context, units, time period, and caveats.
- Use captions or source notes for data provenance.
- For direct labels, place text near the relevant line, point, or bar when it reduces legend dependence.
- Use `ax.annotate()` for arrows or callouts tied to specific data points.
- Consider `highlight_text`, `pyfonts`, or `drawarrow` when the project already uses those packages, but avoid adding dependencies unnecessarily.

## Legend Guidelines

- Prefer direct labeling over legends when there are few groups.
- When using a legend, keep it simple and close to the data.
- Use `ax.legend()` only after meaningful `label=` values are set.
- Useful options: `loc`, `ncols`, `frameon=False`, `fontsize`, `labelcolor`.
- Remove the legend title when it is obvious from context.
- For continuous color mappings, use a colorbar and label it clearly.

## Color Best Practices

- Choose a palette that matches the data type: qualitative for categories, sequential for numeric intensity, diverging around a meaningful midpoint.
- For Matplotlib built-ins, `viridis` is a safe sequential default.
- Avoid qualitative palettes for continuous numeric values.
- Avoid rainbow palettes.
- Use one highlight color and grey muted elements for emphasis.
- If using pypalettes, load named palettes intentionally and document why the palette fits the data.

## Axes, Limits, and Scales

- Use `ax.set_xlim()` and `ax.set_ylim()` deliberately. Do not crop important data without explaining it.
- Do not truncate axes on bar charts.
- Use `ax.set_xscale("log")` or `ax.set_yscale("log")` only when the log transform is meaningful and clearly communicated.
- Format tick labels for readability: commas, percentages, currency, or units.
- For many tick labels, prefer fewer ticks over rotated clutter.

## Layouts and Multiple Axes

- Use small multiples when comparing the same pattern across groups.
- Use shared axes when comparability matters.
- Use `subplot_mosaic()` for complex layouts with named panels.
- Turn off unused axes with `ax.axis("off")`.
- Keep panel spacing consistent and avoid nested decorative frames.

## Export Settings

- Save figures with `fig.savefig(...)`, not `plt.savefig(...)`, when using the object-oriented API.
- Always specify `dpi`, `bbox_inches="tight"`, and a background when needed.
- Recommended screen export: `fig.savefig("plot.png", dpi=150, bbox_inches="tight", facecolor="white")`.
- Recommended high-resolution export: `fig.savefig("plot.png", dpi=300, bbox_inches="tight", facecolor="white")`.
- Inspect the exported file, not only the notebook or browser preview.

## Validation and Debugging

- Check the Figure and Axes objects directly when validating output.
- `fig.axes` gives the list of axes in a figure.
- Inspect `ax.get_children()`, `ax.lines`, `ax.collections`, and `ax.patches` when debugging chart elements.
- For important charts, write lightweight validation checks: number of axes, figure orientation, expected artists, expected colors.

## Common Pitfalls to Avoid

- Do not mix pyplot and object-oriented calls in a confusing way.
- Do not call `plt.figure()` and then use unrelated `ax` objects.
- Do not use one color per bar unless color encodes data or intentional emphasis.
- Do not leave top and right spines unless they serve a purpose.
- Do not use legends as a default when direct labels are clearer.
- Do not use default titles like "Sales by Quarter" when a narrative title is possible.
- Do not accept overlapping labels; change layout, abbreviate, wrap, or switch chart orientation.
- Do not add dependencies for a tiny styling change that Matplotlib can already handle.
