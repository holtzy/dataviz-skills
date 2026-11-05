---
name: d3
description: Use when building, fixing or animating a chart with D3.js inside a React or Next.js app (barplot, scatterplot, line chart, treemap, map…). Covers the D3-for-math / React-for-rendering split, margins and axes, responsiveness with a useDimensions hook, animation with Motion, and switching from SVG to canvas for large datasets. Not for vanilla D3 projects without React.
---

# D3 + React

Build charts where **D3 does the math and React does the rendering**. Every chart follows the same skeleton: compute with D3, render JSX.

## 1. D3 for math only

D3 modules split in two families:

- **Math** (use them): `d3-scale`, `d3-shape`, `d3-array`, `d3-hierarchy`, `d3-geo`, `d3-force`, `d3-interpolate`, `d3-format`, `d3-time-format`… Numbers in, numbers or path strings out.
- **Rendering** (don't use them): `d3-selection`, `d3-transition`. No `d3.select()`, `.append()`, `.attr()`, `.data().join()` or `.transition()`.

React renders every element in JSX and loops with `.map()`:

```jsx
const xScale = d3.scaleLinear().domain([0, d3.max(data, (d) => d.value)]).range([0, boundsWidth]);

return data.map((d) => (
  <rect key={d.id} x={0} y={yScale(d.name)} width={xScale(d.value)} height={yScale.bandwidth()} />
));
```

For a path, call the D3 generator and pass the string to `d`:

```jsx
const linePath = d3.line().x((d) => xScale(d.x)).y((d) => yScale(d.y))(data);
return <path d={linePath} fill="none" stroke="currentColor" />;
```

When adapting an online D3 example, keep its math and rewrite its `select/append/attr` chain as JSX. `import * as d3 from "d3"` is fine; importing single modules (`import { scaleLinear } from "d3-scale"`) only matters for strict bundle-size goals.

## 2. Margins and translation

Leave room for the axes with a `MARGIN` object, compute the **bounds** dimensions, and shift everything into the bounds with a single `translate`:

```jsx
const MARGIN = { top: 10, right: 30, bottom: 50, left: 30 };

const boundsWidth = width - MARGIN.right - MARGIN.left;
const boundsHeight = height - MARGIN.top - MARGIN.bottom;

return (
  <svg width={width} height={height}>
    <g transform={`translate(${MARGIN.left}, ${MARGIN.top})`}>
      {/* every shape and axis goes here, in bounds coordinates */}
    </g>
  </svg>
);
```

- Scales map to the bounds: `.range([0, boundsWidth])` and `.range([boundsHeight, 0])`.
- **Don't** bake margins into the scale range (`.range([MARGIN.left, width - MARGIN.right])`). It is common in D3 examples, but margin math then leaks into every scale, axis and shape.

## 3. Axes are React components

Draw axes in JSX with `scale.ticks()`, and size the tick count from the available pixels rather than a fixed number:

```jsx
const TICK_LENGTH = 6;

export const AxisBottom = ({ xScale, pixelsPerTick }) => {
  const range = xScale.range();
  const numberOfTicksTarget = Math.floor((range[1] - range[0]) / pixelsPerTick);

  return (
    <>
      <line x1={range[0]} x2={range[1]} stroke="currentColor" />
      {xScale.ticks(numberOfTicksTarget).map((value) => (
        <g key={value} transform={`translate(${xScale(value)}, 0)`}>
          <line y2={TICK_LENGTH} stroke="currentColor" />
          <text style={{ fontSize: "10px", textAnchor: "middle", transform: "translateY(20px)" }}>{value}</text>
        </g>
      ))}
    </>
  );
};

// Inside the bounds <g>: push the axis to the bottom
<g transform={`translate(0, ${boundsHeight})`}>
  <AxisBottom xScale={xScale} pixelsPerTick={60} />
</g>
```

`AxisLeft` is the same with `y` and `textAnchor: "end"`. `d3.axisBottom()` called inside a `useEffect` on a ref is an accepted fallback, and the only place D3 touches the DOM.

## 4. Responsiveness: useDimensions + wrapper

Never hardcode `width` and `height`. Every chart gets:

1. **One shared hook**, `useDimensions`, in the project's hook folder (`hook/use-dimensions.ts`, or the existing `hooks/` folder). It measures a div and updates on resize. Write it once, following the contract in [references/responsiveness.md](references/responsiveness.md), and import it in every chart.
2. **A non-responsive chart component** that takes `width` and `height` as props.
3. **A responsive wrapper** that measures its div and forwards the size plus all other props. The wrapper does nothing else:

```jsx
// Responsive component = wrapper that manages the dimensions and does nothing else
export const ResponsiveBarplot = (props) => {
  const chartRef = useRef(null);

  const chartSize = useDimensions(chartRef);

  return (
    <div ref={chartRef} style={{ width: '100%', height: '100%' }}>
      <Barplot
        height={chartSize.height}
        width={chartSize.width}
        {...props} // pass all the props
      />
    </div>
  );
};

// Non responsive component
const Barplot = ({ width, height, data }) => {
  //... dataviz code goes here
}
```

Parents render `<ResponsiveBarplot data={data} />` inside a container **with an explicit height**. The chart returns `null` while `width` or `height` is `0` (first render). Read [references/responsiveness.md](references/responsiveness.md) for the hook contract, the TypeScript wrapper, and the pitfalls (zero height, flex children, resize performance).

## 5. SVG by default, canvas for performance

Use **SVG** by default: declarative JSX, CSS, and event handlers on every shape.

Switch the marks to **canvas** when the DOM gets too heavy: thousands of marks (large scatterplots, dense heatmaps, big networks), many charts on one page, or hover effects that update every mark. Keep axes, labels and tooltips in SVG/HTML layered on top. Read [references/canvas.md](references/canvas.md) before writing canvas code (layering, sharp rendering on retina screens, hover detection).

## 6. Animation with Motion

Animate only change that matters: a dataset switch, or feedback on a user interaction. Don't animate the first render or anything that isn't changing. Keep it short: 80–150 ms for hover, 200–400 ms for transitions in tools, up to ~1 s in one-shot storytelling.

- Small effects (hover color, tooltip fade): a plain **CSS transition**.
- Marks moving, entering or leaving: **spring animations with [Motion](https://motion.dev)** (`npm install motion`, `import { motion, AnimatePresence } from "motion/react"`). Not `d3.transition`, which fights React for the DOM. `framer-motion` is the old name of the same library.

```jsx
<motion.rect
  key={d.id}                       // stable id from the data, never the array index
  animate={{ y: yScale(d.name), width: xScale(d.value) }}
  transition={{ type: "spring", stiffness: 100, damping: 18 }}
/>
```

Read [references/animation.md](references/animation.md) for enter/exit with `AnimatePresence`, path morphing, line drawing, and reduced motion.

## Checklist

- [ ] No `d3.select`, `.append`, `.attr` or `d3.transition`: D3 computes, JSX renders.
- [ ] `MARGIN` object, `boundsWidth` / `boundsHeight`, one `translate` on the bounds `<g>`.
- [ ] Axes as React components using `scale.ticks()` and `pixelsPerTick`.
- [ ] Chart takes `width` / `height` props, exported through a `Responsive*` wrapper using the shared `useDimensions` hook.
- [ ] Early `return null` when `width` or `height` is `0`.
- [ ] `key` is a stable id from the data, not the index.
- [ ] SVG unless the mark count calls for canvas.
- [ ] Animation only on data change or interaction, with Motion springs.

Want to go further? These conventions come from the [D3 Loves React](https://www.d3-loves-react.com) course, with hundreds of examples in the [React Graph Gallery](https://www.react-graph-gallery.com).
