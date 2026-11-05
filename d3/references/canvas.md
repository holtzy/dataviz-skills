# Canvas

## When to switch

SVG creates one DOM node per mark, drawn by the CPU. Fine for hundreds of marks, sluggish for tens of thousands, especially when a hover effect re-renders all of them. Canvas is a single `<canvas>` node that paints pixels on a bitmap: no layout, no per-node cost.

Switch the **marks** to canvas when you hit performance issues: thousands of points (large scatterplots, dense heatmaps, big networks or maps), dashboards with many charts, or interactions that update every mark. Stay in SVG otherwise: canvas code is imperative, more verbose, has no per-shape events, and no CSS.

## Drawing

D3 still does the math. Canvas only replaces the JSX: draw in a `useEffect` on a ref, and redraw when the data, scales or size change.

```jsx
const canvasRef = useRef(null);

useEffect(() => {
  const ctx = canvasRef.current.getContext("2d");
  ctx.clearRect(0, 0, boundsWidth, boundsHeight);

  ctx.globalAlpha = 0.7;
  for (const d of data) {
    ctx.beginPath();
    ctx.arc(xScale(d.x), yScale(d.y), 4, 0, 2 * Math.PI);
    ctx.fillStyle = colorScale(d.group);
    ctx.fill();
  }
}, [data, xScale, yScale, boundsWidth, boundsHeight]);

return <canvas ref={canvasRef} width={boundsWidth} height={boundsHeight} />;
```

- Draw order is stacking order: later shapes paint on top. Sort the data before drawing if needed (for bubbles, biggest first).
- Same-style marks are fastest in one path: `beginPath()`, `moveTo` + `arc` for each point, a single `fill()`.
- D3 shape generators draw straight into the canvas: `d3.line().x(...).y(...).context(ctx)(data)` then `ctx.stroke()`. An existing SVG path string works too: `ctx.fill(new Path2D(pathString))`.
- Memoize scales with `useMemo`, otherwise they're new objects every render and the effect redraws each time.

## Sharp on retina screens

A canvas sized in CSS pixels looks blurry on high-density screens. Size the bitmap by `devicePixelRatio`, keep the CSS size, and scale the context:

```jsx
useEffect(() => {
  const canvas = canvasRef.current;
  const dpr = window.devicePixelRatio || 1;
  canvas.width = boundsWidth * dpr;
  canvas.height = boundsHeight * dpr;
  canvas.style.width = `${boundsWidth}px`;
  canvas.style.height = `${boundsHeight}px`;

  const ctx = canvas.getContext("2d");
  ctx.scale(dpr, dpr);
  // ...draw in CSS-pixel coordinates as usual
}, [/* ... */]);
```

When you set `width`/`height` this way, don't also pass them as props on `<canvas>`.

## Layering canvas with SVG and HTML

Keep axes, labels, annotations and tooltips in SVG/HTML. Stack the layers in a bounds div translated by the margins: the canvas stays in the normal flow and gives the div its size, the SVG sits on top with `position: absolute`:

```jsx
<div style={{ position: "relative" }}>
  <div
    style={{
      transform: `translate(${MARGIN.left}px, ${MARGIN.top}px)`,
      width: boundsWidth,
      height: boundsHeight,
    }}
  >
    {/* SVG layer: the axes */}
    <svg
      width={boundsWidth}
      height={boundsHeight}
      style={{ position: "absolute", top: 0, left: 0, overflow: "visible" }}
    >
      <AxisLeft yScale={yScale} pixelsPerTick={40} width={boundsWidth} />
      <g transform={`translate(0, ${boundsHeight})`}>
        <AxisBottom xScale={xScale} pixelsPerTick={40} />
      </g>
    </svg>

    {/* Canvas layer: the marks */}
    <canvas ref={canvasRef} style={{ position: "relative" }} width={boundsWidth} height={boundsHeight} />
  </div>
</div>
```

Absolutely positioned layers are placed relative to the nearest positioned ancestor, so keep `position: relative` on the parent.

**Think in layers:** most charts have a large static part (all the marks) and a tiny dynamic part (the hovered point). Put the dynamic part on its own canvas (or SVG) on top, and redraw only that layer on interaction.

## Hover and interaction

Shapes have no DOM nodes, so no `onMouseOver` per mark. Instead:

1. Listen to `onMouseMove` on the canvas (or on a transparent layer on top).
2. Convert the mouse to chart coordinates: `e.clientX - rect.left` with `rect = e.currentTarget.getBoundingClientRect()`.
3. Find the closest mark. A linear scan is fine up to ~100k points; for more, or many lookups, build a `d3.Delaunay` (`.find(x, y)`) or `d3.quadtree` once with `useMemo`.
4. Store the hovered id in state and redraw the hover layer, then show an HTML tooltip.

**Throttle** `mousemove`, `scroll` and `resize` handlers (for example with `requestAnimationFrame`) so a redraw doesn't run on every event.
