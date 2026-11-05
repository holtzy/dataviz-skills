# Responsiveness

Every chart is responsive the same way: one shared `useDimensions` hook, a chart component that takes `width` / `height` props, and a `Responsive*` wrapper.

## The useDimensions hook

If the project doesn't have it yet, write it once and import it in every chart. Don't redefine it inside chart files. Its contract:

- **Location:** the project's hook folder, `hook/use-dimensions.ts` (or `.js`), or the existing `hooks/` folder.
- **Input:** a ref to the div to measure: `useDimensions(chartRef)`.
- **Output:** `{ width, height }` in pixels, `{ width: 0, height: 0 }` until the div is measured.
- **Timing:** it measures before the first paint (`useLayoutEffect`), then again whenever the div changes size. Prefer a `ResizeObserver` on the div over a window `resize` listener, so it also catches layout changes like a collapsing sidebar.

In the Next.js App Router, start the file with `"use client"`.

## The wrapper, in TypeScript

The responsive component takes the same props as the chart, minus `width` and `height`:

```tsx
import { useRef } from "react";
import { useDimensions } from "../hook/use-dimensions";

type BarplotProps = {
  width: number;
  height: number;
  data: { name: string; value: number }[];
};

// Responsive component = wrapper that manages the dimensions and does nothing else
export const ResponsiveBarplot = (props: Omit<BarplotProps, "width" | "height">) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartSize = useDimensions(chartRef);

  return (
    <div ref={chartRef} style={{ width: "100%", height: "100%" }}>
      <Barplot height={chartSize.height} width={chartSize.width} {...props} />
    </div>
  );
};

// Non responsive component
const Barplot = ({ width, height, data }: BarplotProps) => {
  if (width === 0 || height === 0) {
    return null;
  }
  // ... dataviz code goes here
};
```

Thanks to `{...props}`, the wrapper never needs to change when the chart gets new props (colors, margins, callbacks…).

## Pitfalls

1. **The container has no height.** A div's height comes from its content, and the SVG waits for a height, so the result is 0 and nothing renders, with no error. The parent of `Responsive*` must set a height (`style={{ height: 400 }}`, `h-96`, a grid row…). To debug, give the container a red background and fix its size before touching chart code.
2. **A parent constrains the width.** A hardcoded width anywhere up the tree caps the chart. Check the whole parent chain in DevTools.
3. **Zero on first render.** The ref isn't attached yet, so the hook returns `{ width: 0, height: 0 }`. Return `null` early in the chart, before building scales.
4. **Flex children that won't shrink.** Flex items default to `min-width: auto`, so the SVG's pixel width becomes a floor and the chart grows but never shrinks back. Set `minWidth: 0` on the flex child that holds the chart.
5. **Re-renders during resize.** The chart re-renders on every resize event. For heavy computations (force layouts, binning, hierarchies), wrap them in `useMemo` keyed on `data` and the dimensions they use.
6. **Design changes with size.** A chart doesn't just reflow. Use fewer ticks on narrow screens (`pixelsPerTick` does this), rotate or abbreviate labels, or switch layout (for example horizontal bars on mobile). Test at 375 px wide.
