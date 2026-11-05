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

- Horizontal bars: `ax.barh(labels, values)`.
- Lines: `ax.plot(x, y, linewidth=...)`.
- Scatter: `ax.scatter(x, y, s=..., c=...)`.
- Histograms: `ax.hist(values, bins=...)`.
- Lollipops: `ax.stem(..., orientation="horizontal")`.

## Theme and Styling

- Hide spines with `ax.spines[["top", "right"]].set_visible(False)`.
- Remove tick marks with `ax.tick_params(length=0)`.
- Draw grid lines behind the data: `ax.grid(axis="x", linewidth=0.5, color="#dddddd")` and `ax.set_axisbelow(True)`.
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
- Use `ax.annotate()` for arrows or callouts tied to specific data points.
- Consider `highlight_text`, `pyfonts`, or `drawarrow` when the project already uses those packages, but avoid adding dependencies unnecessarily.

## Legends and Colorbars

- Use `ax.legend()` only after meaningful `label=` values are set.
- Useful options: `loc`, `ncols`, `frameon=False`, `fontsize`, `labelcolor`, `title=None`.
- For continuous color mappings, add a colorbar with `fig.colorbar(mappable, ax=ax, label=...)`.

## Colors

- Pass categorical colors with `color=` (a list or a dict lookup) and continuous ones with `c=` plus `cmap=`.
- If the project uses pypalettes, load palettes by name rather than hardcoding hex lists.

## Axes, Limits, and Scales

- Set limits with `ax.set_xlim()` and `ax.set_ylim()`.
- Set log scales with `ax.set_xscale("log")` or `ax.set_yscale("log")`.
- Format tick labels with `matplotlib.ticker`: `StrMethodFormatter("{x:,.0f}")` for commas, `PercentFormatter()` for percentages, `FuncFormatter` for anything custom.
- Control the number of ticks with `ticker.MaxNLocator(n)`.

## Layouts and Multiple Axes

- Use `sharex=True` / `sharey=True` in `plt.subplots()` to share axes across panels.
- Use `subplot_mosaic()` for complex layouts with named panels.
- Turn off unused axes with `ax.axis("off")`.

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
- Do not add dependencies for a tiny styling change that Matplotlib can already handle.
