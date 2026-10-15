# Method references

The **chart-type**, **maps** and **color** skills of this collection cover the core method; the
references below go further.

The galleries show *what good looks like*. These references help decide *what to draw* and
*how to draw it right*. Read the relevant page (WebFetch) when the choice of form is not obvious,
when the audience is the public sector or the general public, or when the chart risks misleading.

## Choosing the form

- **From Data to Viz** — https://www.data-to-viz.com (Yan Holtz & Conor Healy)
  Decision tree from the *shape of the data* (one numeric variable, several categorical, time
  series, maps, networks…) to candidate chart types, with each type's pitfalls.
  - One page per chart type: `https://www.data-to-viz.com/graph/<type>.html`
    (e.g. `barplot`, `lollipop`, `ridgeline`, `choropleth`, `sankey`, `streamgraph`).
  - **Caveats**, a catalogue of classic mistakes (spaghetti charts, dual axes, pie abuse,
    cut y-axis…): https://www.data-to-viz.com/caveats.html — check it before shipping.
- **The Data Visualisation Catalogue** — https://datavizcatalogue.com (Severino Ribecca)
  ~60 chart types searchable *by function* (comparisons, proportions, relationships,
  distribution, location, part-to-whole…), each with anatomy and limits. Good for less common
  forms (Marimekko, parallel sets, spiral plots…).

## Doing it right (French public statistics school)

- **Insee, « Comment présenter nos données pour mieux communiquer ? »** — Courrier des
  statistiques n° 10, 2023: https://www.insee.fr/fr/information/7722079
  Graphic semiology vs. design, synthesis and simplicity, metadata and rigour in the figures,
  maps and tables as first-class forms. The reference for official-statistics style in France.
- **Éric Mauvière (icem7), « La dataviz pour donner du sens aux données et communiquer un
  message »**, talk for the public-statistics data-science network, Feb. 2024:
  https://minio.lab.sspcloud.fr/lgaliana/ssphub/replay/20240229-dataviz-mauviere/conf_ssphub_icem7.pdf
  Slide-by-slide redesigns of real Insee charts: legend order matching the stacking, grey as a
  neutral that lets colours stand out, hue to group related categories, removing visual
  interference. Good model for *iterating* on a chart.

## Reproducing it (code)

- **R Graph Gallery** — https://r-graph-gallery.com and **Python Graph Gallery** —
  https://python-graph-gallery.com (Yan Holtz): hundreds of charts *with their code*, from basic
  to publication-grade (many dataviz-inspiration entries link to them).
- **ggplot2: Elegant Graphics for Data Analysis** (3rd ed.) — https://ggplot2-book.org :
  the grammar of graphics in practice, for layered R charts.
