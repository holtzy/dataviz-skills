---
name: roast-my-chart
description: Review a finished chart, plot, map or dashboard against the 61 Data to Viz caveat flashcards, and report what to fix. Use when the user asks to roast, review, critique, audit or give feedback on a chart, asks "what's wrong with my chart" or "is this chart misleading", or wants a check before publishing. Works on an image, on plotting code (ggplot2, Matplotlib, D3, Plotly, Vega…), or both.
---

# Roast my chart

Review a chart against every caveat in [references/caveats.md](references/caveats.md): 61 common dataviz mistakes from the [Data to Viz flashcards](https://github.com/holtzy/dataviz-caveat-flashcards), in 8 sections. Each caveat has four fields:

- **Look for:** what the mistake looks like, in the rendered chart and in code.
- **Why it matters**
- **Fix**
- **Fine when:** the exception. If it applies, the caveat is not a problem here.

The value of this review is that it is **complete and specific**: every caveat is checked, and every remark points at something visible in this chart.

## 1. Get the chart

- **Image** (screenshot, PNG, PDF, URL of a page): look at it carefully.
- **Code**: if you can run it, render the chart to an image and look at the result. Many caveats only show once rendered (overplotting, contrast, overlapping labels, font size). Use the code to confirm what the image suggests (axis limits, sort order, palette).
- **Code you can't run**: review the code, and say which caveats need the rendered chart to be checked.

If the chart is unclear (cropped screenshot, missing data, unknown audience), ask before reviewing.

## 2. Describe the chart

Before judging, write down in a few lines what is actually there:

- chart type and what each visual channel encodes (position, length, color, size…)
- number of groups, series and points
- single chart, small multiples or dashboard; map or not
- the message the chart seems to carry, from its title or emphasis

This grounds every remark in the chart, not in generic advice.

## 3. Check every caveat

Read the whole of [references/caveats.md](references/caveats.md). Then go through the 8 sections in order, and through every caveat in each section:

- **Flag** a caveat only when the chart shows what **Look for** describes, and the **Fine when** exception does not apply.
- **Skip a whole section** only when it cannot apply, and say why ("Maps: not a map", "Dashboards and data stories: single chart").
- **Can't tell?** If checking needs something you don't have (the raw data, the sample size, the audience), don't flag it: list it under "Couldn't check".
- Don't add mistakes that aren't in the cards to the list. If something outside the cards is seriously wrong, mention it in one line at the end.

## 4. Write the roast

Use this structure:

```markdown
## 🔥 Roast

<One cheeky line about the chart, never about its author.>

**Verdict:** <one sentence: the single most important thing to fix>.
Checked 61 caveats: <n> flagged, <n> not applicable, <n> couldn't check.

## What to fix

### 🔴 <Caveat title>
**What I see:** <the specific evidence in this chart: which axis, which bars, which colors>
**Fix:** <the card's fix, applied to this chart, with code if the user shared code>
[Flashcard](<image link from the card>) · [Read more](<read more link>)

### 🟠 <Caveat title>
...

## What works well

- <2 or 3 things the chart already does right, tied to caveats it passes>

## Couldn't check

- <caveat>: <what would be needed>
```

- **Order by severity:** 🔴 misleading (the reader can draw a wrong conclusion: mostly the "Misleading charts" section), 🟠 hard to read (wrong chart type, color, labels, overplotting), 🟡 polish (alignment, fonts, boxes, decluttering).
- Keep "What I see" concrete: name the element, quote the value or the label. "The y-axis starts at 50, so the 52 vs 58 bars look like a 4× difference" beats "The axis is truncated".
- The roast line is the only joke. Everything after it is straight, useful feedback.
- No flagged caveat? Say so plainly, and keep "What works well" and "Couldn't check".

## 5. Offer to fix it

End by offering to apply the fixes. When the user shared code, fix it in place, following the library skill if one is available (ggplot2, matplotlib, d3), then render the chart again and check that the flagged caveats are gone.
