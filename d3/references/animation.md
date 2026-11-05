# Animation with Motion

## When to animate

Animation earns its place for three reasons, in order: **object constancy** (the eye tracks which mark became which when data changes), **directing attention** (a new value, a highlighted item), and polish (the weakest reason). It hurts when it distracts from the data or makes frequent users wait.

- ✅ The dataset changed → animate the transition.
- ✅ A user interaction needs feedback → animate it.
- ❌ First load with no previous state → render in place.
- ❌ Nothing is changing → nothing moves.

Durations: 80–150 ms for hover and micro-interactions, 200–400 ms for transitions in daily-use tools, 500 ms–1 s only for narrative moments in one-shot content. When in doubt, faster.

## Tween or spring

- **Tween** (CSS `transition`): fixed duration and easing, zero dependency, predictable, but mechanical, and it restarts from zero when interrupted. Use it for small effects: hover color, tooltip fade, icon rotation.

  ```jsx
  <rect fill={isHovered ? "#e0ac2b" : "#69b3a2"} style={{ transition: "fill 150ms" }} />
  ```

- **Spring** (Motion): driven by physics (`stiffness`, `damping`, `mass`) instead of a duration, so it feels natural and keeps its velocity when retargeted mid-flight. Use it for everything that moves: dataset transitions, marks entering and leaving, morphing shapes.

Don't use `d3.transition`: it's a JS tween that mutates the DOM behind React's back.

## Setup

```bash
npm install motion
```

```jsx
import { motion, AnimatePresence } from "motion/react";
```

Every HTML and SVG element has an animated twin: `motion.circle`, `motion.rect`, `motion.path`, `motion.g`, `motion.div`… `framer-motion` is the legacy name of the same package.

## One shape

Move the animated attributes from the static props into `animate`. When the value changes, Motion springs to it:

```jsx
<motion.circle
  cy={60}
  r={32}
  animate={{ cx: position }}
  transition={{ type: "spring", stiffness: 100, damping: 20, mass: 1 }}
/>
```

`stiffness` (default 100) sets how hard the spring pulls, `damping` how quickly it stops oscillating, `mass` how heavy the object feels.

`initial` sets a starting state when the element mounts. To scale an SVG shape from its own center, set `transformBox`:

```jsx
<motion.rect
  style={{ transformBox: "fill-box", transformOrigin: "center" }}
  initial={{ scale: 0 }}
  animate={{ scale: 1 }}
/>
```

## A whole chart

A chart is many shapes: map over the data and give each `motion.*` element its target. Each one runs its own spring.

- **`key` must be a stable id from the data.** React uses it to match each element with its previous version. With the array index, elements get re-mounted or mismatched and the chart teleports instead of animating.
- **The chart takes data as a prop.** State lives in the parent; the chart re-renders with the new data and the springs do the rest.
- **Push `motion.*` into a small leaf component.** When an item is several shapes (lollipop: line + circle; dumbbell: 2 circles + line), render one `<g key={d.id}>` per item holding an `Item` component that owns the `motion.*` elements. The chart component keeps scales, margins and the loop, and knows nothing about Motion.

## Enter, update, exit

Items that appear or disappear between datasets need `AnimatePresence`. It enables `initial` (state before entering) and `exit` (state to animate to before removal) on its direct children, and uses their `key` to tell entering, updating and leaving items apart:

```jsx
<AnimatePresence>
  {data.map((d) => (
    <motion.rect
      key={d.id}
      x={0}
      height={yScale.bandwidth()}
      initial={{ width: 0, y: yScale(d.name) }}
      animate={{ width: xScale(d.value), y: yScale(d.name) }}
      exit={{ width: 0 }}
      transition={{ type: "spring", stiffness: 100, damping: 18 }}
    />
  ))}
</AnimatePresence>
```

Bars grow in from 0, update their length and slide to their new rank, and shrink out. A **bar chart race** is the same code fed one dataset per time step by a timer.

**Scrollytelling** is the same chart with the data driven by scroll: give each text step a ref, use Motion's `useInView(ref, { root: scrollerRef, margin: "-50% 0px -50% 0px" })` to detect the step crossing the middle of the screen, and store its index in state to pick the dataset.

## Paths

Line, area and stream charts are a single `path`. Motion animates its `d` string directly:

```jsx
<motion.path animate={{ d: linePath }} fill="none" stroke="currentColor" />
```

Limits of this:

- **Same number of points only.** If the two paths have different point counts (missing values, a different number of series points) or contain curves and arcs, the morph breaks. Use [flubber](https://github.com/veltman/flubber) to interpolate arbitrary shapes, or keep the point count stable.
- **Arcs (pie, donut) cave inward.** `d` interpolates each point in a straight line, so slices leave the circle mid-transition. Animate the **angles** instead and rebuild the arc on every frame:

  ```jsx
  import { motion, useSpring, useTransform } from "motion/react";

  const arc = d3.arc().innerRadius(60).outerRadius(100);

  const DonutSlice = ({ startAngle, endAngle, color }) => {
    const start = useSpring(startAngle, { stiffness: 100, damping: 18 });
    const end = useSpring(endAngle, { stiffness: 100, damping: 18 });

    useEffect(() => {
      start.set(startAngle);
      end.set(endAngle);
    }, [startAngle, endAngle]);

    const d = useTransform([start, end], ([s, e]) => arc({ startAngle: s, endAngle: e }));
    return <motion.path d={d} fill={color} />;
  };
  ```

  In TypeScript, type the generator and the callback: `d3.arc<{ startAngle: number; endAngle: number }>()` and `([s, e]: number[]) => arc({ startAngle: s, endAngle: e }) ?? ""`.

**Drawing a line progressively** (pen effect) uses `pathLength`, from 0 (nothing drawn) to 1:

```jsx
<motion.path
  d={linePath}
  initial={{ pathLength: 0 }}
  animate={{ pathLength: 1 }}
  transition={{ duration: 1.5, ease: "easeInOut" }}
/>
```

## Reduced motion

Respect the user's OS setting. Motion's `useReducedMotion()` returns `true` when `prefers-reduced-motion` is on:

```jsx
const reduceMotion = useReducedMotion();
const transition = reduceMotion ? { duration: 0 } : { type: "spring", stiffness: 100, damping: 18 };
```

## Performance

Springs on a few hundred elements are fine. With thousands of marks, animating each one in SVG gets slow: render the marks on canvas (see [canvas.md](canvas.md)) and animate the canvas drawing instead.
