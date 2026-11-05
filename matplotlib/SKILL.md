---
name: matplotlib
description: Create, improve, or reproduce Matplotlib charts with deliberate styling, typography, annotations, custom layouts, and maps. Use when producing Python visualizations or refining existing Matplotlib, Seaborn, or GeoPandas figures.
---

- Rank categories by a meaningful measure; preserve chronological, ordinal, or domain order when it matters. Prefer horizontal bars or dots to crowded category labels.
- For distributions, examine bin width or KDE bandwidth; a change in smoothing can change the apparent story. Show individual observations when a summary hides meaningful structure.
- For many groups, use small multiples or highlight a few groups over muted context. Twenty distinguishable colors rarely solve a crowded chart.
- Let the message justify unusual forms. Matplotlib can combine primitives: a dumbbell is `ax.hlines()` plus two `ax.scatter()` calls; a confidence band is `ax.fill_between()`. A bespoke chart does not always need a bespoke library.

Use [Data to Viz](https://www.data-to-viz.com/) when chart choice is uncertain, [Python Graph Gallery](https://python-graph-gallery.com/) for implementation patterns, and [Dataviz Inspiration](https://www.dataviz-inspiration.com/) for composition ideas. Borrow visual structure while preserving the meaning of the actual data.

## Construct the figure deliberately

Use explicit Figure and Axes objects throughout: `fig, ax = plt.subplots(...)`, `ax.plot(...)`, `fig.savefig(...)`. Pass `ax=ax` to compatible third-party plotting functions. This makes layering and multi-panel work predictable. Keep data preparation separate from presentation; reusable plotting functions should accept an Axes or return the figure and axes they create.

Choose figure dimensions for the final reading size. Increasing export DPI does not fix text that becomes too small when the image is embedded in a report or webpage.

Choose one layout strategy:

- For ordinary grids, use `layout="tight"`; `layout="constrained"` is useful for layouts involving shared colorbars or panels spanning rows and columns.
- For an editorial figure with a manually positioned header, footer, or closely packed marginal plots, use `layout=None` and `fig.subplots_adjust(...)`. Reserve space for text explicitly.
- Avoid mixing automatic layout with manual `subplots_adjust()` calls. Automatic layout also does not guarantee that arbitrary `fig.text()` annotations receive enough space.

See the [layout guide](https://matplotlib.org/stable/users/explain/axes/constrainedlayout_guide.html) when a layout engine interferes with positioning.

## Style for the reading task

Remove visual competition around the data. Usually hide the top and right spines; for a labeled bar chart, removing all spines can work better. Remove tick marks while retaining useful tick labels. Put subtle gridlines behind the marks, along the quantitative axis: vertical gridlines for horizontal bars, horizontal gridlines for vertical bars.

```python
ax.spines[["top", "right"]].set_visible(False)
ax.tick_params(length=0, pad=8)
ax.set_axisbelow(True)
ax.grid(axis="x", color="#dddddd", linewidth=0.6)  # horizontal bars
```

Use a zero baseline for bars and area encodings of magnitude. For line and scatter charts, choose limits that reveal the relevant variation without silently hiding observations. Format units and percentages explicitly. Reduce tick density, wrap labels, or change orientation before rotating every label.

Apply a theme before creating artists, then make chart-specific adjustments. Keep figure and axes backgrounds consistent unless their difference serves a purpose. Use `plt.rc_context({...})` or `plt.style.context(...)` to scope reusable styles; a property cycle provides defaults, but an explicit mapping is better when group identities must remain stable across charts.

**morethemes** supplies coherent themes such as `ft`, `urban`, and `economist`. Use one as a starting point, then adjust hierarchy and spacing for the actual chart. `mt.set_theme("ft")` applies a theme globally and resets defaults first; for scoped use:

```python
import matplotlib.pyplot as plt
import morethemes as mt

with plt.rc_context(mt.get_rcparams("ft")):
    fig, ax = plt.subplots(figsize=(8, 4), layout="constrained")
    ax.plot(x, y)
```

[morethemes documentation](https://y-sunflower.github.io/morethemes/guide/reference/). Native [style sheets and rcParams](https://matplotlib.org/stable/users/explain/customizing.html) are sufficient when only a few settings need changing.

## Make visual mappings explicit

Choose color for a specific job: distinguish categories, encode quantities, or highlight a finding. Use a qualitative palette for groups, a perceptually ordered sequential palette for magnitudes, and a diverging palette around a meaningful reference value. A continuous colormap made from categorical colors does not become a meaningful quantitative scale merely because it is interpolated.

For explanation, start with muted context and one or two accent colors. Avoid a different color for every bar when position already identifies the categories. Check contrast against the actual background; use labels, marker shapes, line styles, or hatching when color alone is insufficient.

Preserve category-to-color mappings across sorting, filtering, panels, and separate figures:

```python
palette = {"North": "#335c67", "South": "#ae2f2f"}
ax.scatter(df["x"], df["y"], color=df["region"].map(palette))

# Highlight a condition without removing the rest of the data.
colors = df["region"].eq("North").map({True: "#335c67", False: "#d3d3d3"})
```

For numeric color, pass the values to `c`, the colormap to `cmap`, and retain the returned mappable for `fig.colorbar(mappable, ax=ax, label=...)`. Set shared `norm` or `vmin`/`vmax` across comparable panels. Use `TwoSlopeNorm(vmin=..., vcenter=0, vmax=...)` for a diverging scale centered on zero when values span both sides. Do not rescale each panel independently without communicating it.

**pypalettes** provides curated palettes and Matplotlib colormaps. Prefer a named palette chosen for the data over inventing a multicolor scheme. Use the discrete palette's `.colors` for categorical mappings and a continuous colormap for numeric values:

```python
from pypalettes import load_cmap

palette = load_cmap("Acadia").colors
cmap = load_cmap("BluGrn", cmap_type="continuous")
points = ax.scatter(df["x"], df["y"], c=df["value"], cmap=cmap)
```

[pypalettes API](https://y-sunflower.github.io/pypalettes/reference/load_cmap/) and [palette finder](https://python-graph-gallery.com/color-palette-finder/). Select a fixed name for reproducible output; avoid a random palette.

For bubble charts, `scatter(s=...)` encodes marker area in points squared. If bubble area represents magnitude, use `s = scale * values`, not a radius proportional to values. A min/max size remapping changes proportional relationships; if needed, communicate that mapping and use it consistently in the size legend. Draw large bubbles first and small bubbles last; use opacity to expose overlap.

## Compose text as part of the chart

Prefer `fig.text()` and `ax.text()` for custom titles, subtitles, direct labels, and notes because their placement is flexible. Use a takeaway title supported by the data, a quieter subtitle for scope and units, and a small source note. Align these blocks with the plotting area or a consistent figure margin. Use a clear size/weight hierarchy rather than many font families.

Choose coordinates according to what the annotation belongs to:

| Placement | API / transform | Useful for |
| --- | --- | --- |
| Data coordinates | `ax.text(x, y, ...)` | End-of-line labels, outliers, extrema |
| Relative to the panel, 0–1 | `ax.text(..., transform=ax.transAxes)` | Panel names, stable corner notes |
| Relative to the figure, 0–1 | `fig.text(x, y, ...)` | Shared title, subtitle, caption |

Set `ha` and `va` deliberately. For a label attached to a point, `ax.annotate(..., xytext=(6, 0), textcoords="offset points")` gives a stable physical offset. Use `clip_on=False` when an artist should extend beyond its Axes, and leave enough room in the figure. See the [transforms tutorial](https://matplotlib.org/stable/users/explain/artists/transforms_tutorial.html) for mixed coordinate systems.

Directly label a manageable number of lines, bars, or groups near their marks, matching label colors to the data. Reserve space for endpoint labels instead of placing them against the figure edge. Keep a legend when direct labels would crowd the data or when readers need a numeric color or size key. A continuous color scale normally needs a labeled colorbar. Build a manual legend only when its custom layout materially helps.

**highlight_text** handles several colors, weights, or fonts inside one annotation. Use it to turn a title or sentence into a compact color key rather than positioning separate text fragments by eye:

```python
from highlight_text import fig_text

fig_text(
    x=0.12, y=0.94, s="<North> grows while <South> declines",
    highlight_textprops=[{"color": "#335c67"}, {"color": "#ae2f2f"}],
    fig=fig, fontsize=18, ha="left", va="top",
)
```

Provide one properties dictionary per `<highlighted substring>`. `ax_text(..., ax=ax)` uses data coordinates; `fig_text(..., fig=fig)` uses figure coordinates. [highlight_text documentation](https://github.com/znstrider/highlight_text#use).

**pyfonts** loads fonts reproducibly as `FontProperties` objects. Prefer the named Google/Bunny loaders over searching repositories for font-file URLs. Load the actual weights and styles required by the design; setting `weight="bold"` on text referencing a specific regular font file does not select a different file.

```python
from pyfonts import load_google_font

regular = load_google_font("Roboto")
bold = load_google_font("Roboto", weight="bold")
fig.text(0.12, 0.94, "The supported takeaway", font=bold, fontsize=20)
ax.text(0.02, 0.95, "Panel A", transform=ax.transAxes, font=regular, va="top")
```

Use `load_font(local_path_or_url)` for an existing font asset; `set_default_font(regular)` applies it to future ticks, labels, and other text. Load fonts before final layout and inspection because font metrics affect spacing. [pyfonts documentation](https://y-sunflower.github.io/pyfonts/).

**drawarrow** simplifies curved annotation arrows without juggling Matplotlib's several arrow APIs. Use it when a curved connector helps connect a note to a finding; keep its visual weight subordinate to the data:

```python
from drawarrow import ax_arrow

ax_arrow(
    tail_position=(2, 8), head_position=(4, 5),
    radius=0.25, color="#555555", ax=ax,
)
```

`ax_arrow` uses data coordinates; `fig_arrow` is useful for figure-relative connectors. [drawarrow documentation](https://y-sunflower.github.io/drawarrow/). For a simple native callout, `ax.annotate()` may already suffice.

For contextual bands and reference lines, use `ax.axvspan()`, `ax.axhspan()`, `ax.axvline()`, or `ax.axhline()` with subdued styling. For other shapes, add patches with an explicit transform and `zorder`. A decorative arrow or shaded region should explain something specific.

## Use statistical extensions where they reduce work

**Seaborn** supplies grouping and statistical calculations for KDEs, violins, swarms, regression fits, and more. Let it construct the data layer, then finish the composition through Matplotlib. Use axes-level functions when integrating into an existing figure:

```python
import seaborn as sns

sns.scatterplot(
    data=df, x="x", y="y", hue="region", style="region",
    palette={"North": "#335c67", "South": "#ae2f2f"}, ax=ax,
)
# A separate distribution example:
# sns.kdeplot(data=df, x="value", hue="region", fill=True, ax=ax)
```

Check statistical defaults before accepting the result: `sns.lineplot()` aggregates repeated x-values and adds confidence intervals by default. Use `estimator=None, errorbar=None` for an already prepared series, and `units=` when distinct trajectories must remain separate. For categorical totals already computed, `ax.barh()` avoids accidental re-aggregation.

`pairplot`, `jointplot`, `relplot`, `displot`, and `catplot` manage their own figures/grids; do not treat them as axes-level functions accepting `ax=`. They are useful for exploration, while a manual layout gives more control over a finished explanatory figure. [Seaborn API](https://seaborn.pydata.org/api.html), [function overview](https://seaborn.pydata.org/tutorial/function_overview.html), and [lineplot defaults](https://seaborn.pydata.org/generated/seaborn.lineplot.html).

## Build layouts around comparisons

Use `plt.subplots()` for regular grids and `plt.subplot_mosaic()` for asymmetric layouts with named panels. Repeated mosaic labels make one Axes span cells; `"."` leaves a gap. Prefer these readable layouts before reaching for low-level positioning.

```python
fig, axs = plt.subplot_mosaic(
    [["main", "detail"], ["main", "distribution"]],
    figsize=(10, 6), width_ratios=[2, 1], layout="constrained",
)
axs["main"].plot(x, y)
inset = axs["main"].inset_axes([0.6, 0.12, 0.32, 0.28])
```

For small multiples, iterate over groups and axes (`zip(groups, axs.flat)`); `squeeze=False` gives a consistent two-dimensional array even for a single panel. Rank panels intentionally, share axis limits and visual mappings when comparing magnitudes, label each panel inside the Axes, and hide unused panels. Optionally show all other groups as faint background traces in each panel. If scales differ, make that difference conspicuous.

An inset's bounds are `[left, bottom, width, height]` relative to its parent Axes by default. Use it for a secondary distribution, map detail, compact visual key, or relevant image. For logos/images, call `inset.imshow(image)` and `inset.set_axis_off()`; keep the image from competing with the marks. [Mosaic guide](https://matplotlib.org/stable/users/explain/axes/mosaic.html) and [inset API](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.inset_axes.html).

## Treat maps as layered charts with a CRS

**GeoPandas** reads geographic files, joins attributes to geometries, reprojects them, and draws boundaries or choropleths onto a Matplotlib Axes. Start with the geometry table on the left of the join to preserve its geospatial behavior. For one metric per region, validate the join cardinality and inspect unmatched identifiers; show missing values distinctly from zero.

```python
import geopandas as gpd

regions = gpd.read_file("regions.geojson")
mapped = regions.merge(metrics, on="region_id", how="left", validate="one_to_one")
mapped.plot(
    column="rate", cmap="viridis", legend=True, ax=ax,
    edgecolor="white", linewidth=0.4,
    missing_kwds={"color": "#eeeeee", "label": "No data"},
)
ax.set_axis_off()
```

[GeoPandas mapping guide](https://geopandas.org/en/stable/docs/user_guide/mapping.html).

- Choropleths generally need a rate, proportion, or density; absolute totals often mostly reflect population. When totals are the message, consider proportional symbols instead. Large geographic regions can dominate perception even when few people live there.
- Use the same color normalization or classification boundaries for maps that readers should compare. Explain the units and any bins; keep missing regions visible.
- Use `to_crs(...)` to transform coordinates. `set_crs(...)` declares what existing coordinates mean and does not transform them. Choose projections for the task; Mercator is unsuitable for comparing world region areas.
- For bubble maps, convert longitude/latitude to point geometries with `gpd.points_from_xy(...)`, assign their known source CRS, and reproject to the map CRS before plotting. Changing the basemap projection alone does not move raw scatter coordinates.
- For region labels, use projected coordinates for centroid calculations; `representative_point()` is often better when a label must lie inside its region.

**Cartopy** is useful for projection-aware Matplotlib GeoAxes, coastlines, graticules, and global maps. The Axes `projection=` describes the display; each data layer's `transform=` describes its source coordinates. For example, longitude/latitude points on a Robinson GeoAxes need `ax.scatter(lon, lat, transform=ccrs.PlateCarree(), ...)`. Import projections with `import cartopy.crs as ccrs`. [Cartopy CRS documentation](https://cartopy.readthedocs.io/stable/reference/crs.html). GeoPandas with an appropriate `to_crs()` can suffice when a projected polygon map is all that is needed.

## Reach for specialized tools selectively

**PyWaffle** draws waffle and pictogram charts into an existing Axes. It handles block allocation, spacing, and icons; specify the scale and remember that fitting values into a fixed grid can introduce rounding.

```python
from pywaffle import Waffle

Waffle.make_waffle(ax=ax, rows=5, columns=10, values=[30, 16, 4])
ax.set_aspect("equal")
ax.set_axis_off()
```

[PyWaffle documentation](https://pywaffle.readthedocs.io/en/latest/quickstart.html). In small multiples, keep the meaning of one block consistent if readers should compare absolute quantities.

**plotnine** offers a grammar-of-graphics interface for layered charts and faceting. Use it when mappings and facets express the chart more clearly than manual Axes loops; `fig = p.draw()` returns a Matplotlib Figure for final annotations or insets. [plotnine documentation](https://plotnine.org/) and [the draw bridge](https://plotnine.org/reference/ggplot.html#draw).

**ninejs** adds hover tooltips, linked highlighting, and click interactions to plotnine charts and exports standalone HTML. Use it when browser interaction is part of the requested deliverable. It works with plotnine objects rather than arbitrary Matplotlib Figures. Consult its [documentation](https://y-sunflower.github.io/ninejs/) for the interaction API supported by the installed version.

For truly custom curves, use native `matplotlib.path.Path` and `PathPatch`: quadratic Bézier segments use two `CURVE3` entries (control point, endpoint); cubic segments use three `CURVE4` entries (two control points, endpoint). Prefer a dedicated chart library for standard flow diagrams; build paths when the visual design needs custom geometry. See the [Path tutorial](https://matplotlib.org/stable/users/explain/artists/paths.html). Do not smooth observed time series merely to make them more attractive if the curve would imply unsupported intermediate behavior.

## Inspect the artifact, then refine it

Render and open the exported chart at its intended display size. Check text collisions, clipping, title/subtitle spacing, label contrast, line endpoints, legend interpretation, and whether the main comparison is obvious. Refine the actual figure rather than relying on code inspection or successful execution.

Save through `fig.savefig(...)`: PNG for raster delivery, SVG/PDF when vector output is useful. Set DPI for raster output and preserve the intended background with `facecolor=fig.get_facecolor()`. `bbox_inches="tight"` helps include outside annotations but changes the exported bounding dimensions; omit it when exact canvas dimensions are required and fit everything inside the canvas instead.

For reusable chart pipelines, inspect meaningful artist properties as needed: `fig.axes`, `ax.lines`, `ax.collections`, `ax.patches`, or `ax.get_children()`. Test the intended data and visual contract rather than every styling detail. Colorbars can add Axes, so an Axes count is not automatically a panel count. Artist checks complement visual inspection.

When an undocumented-looking keyword is needed, inspect the underlying artist's documentation: `ax.plot()` creates `Line2D` artists, `ax.scatter()` returns a `PathCollection`, and shapes are patches. Their supported properties explain many `**kwargs` in the high-level API. Use the [Axes reference](https://matplotlib.org/stable/api/axes_api.html) to find the plotting method, then follow its returned artist type for precise styling options.
