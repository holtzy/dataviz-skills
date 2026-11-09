---
name: new-dataviz-project
description: Scaffold a new web dataviz project with Yan Holtz's preferred stack - Vite, React, TypeScript, D3 (latest, typed), shadcn/ui + Tailwind, Lucide icons, Bitter / Roboto / Fira Mono fonts, a narrow reading column, a responsive default barplot, and GitHub Pages deployment. Use when the user asks to create, start, scaffold, bootstrap or set up a new dataviz, chart, D3 or React visualization project or website.
---

# New dataviz project

Create a ready-to-deploy project where the user only has to replace the default barplot with their own charts. Work through the steps in order, and check that the project builds at the end.

If the user didn't give a project name, ask for it. It becomes the folder name, the `package.json` name and the GitHub repo name (it is part of the GitHub Pages URL).

## The stack

| Need | Choice |
|---|---|
| Build tool | **Vite**, React + TypeScript template. A static site, so it deploys to GitHub Pages with no server. |
| Language | **TypeScript**, strict mode (the template default). |
| Charts | **D3**, latest version (`npm install d3`), types from DefinitelyTyped (`npm install -D @types/d3`). |
| UI | **shadcn/ui** on **Tailwind CSS** v4. |
| Icons | **Lucide** (`lucide-react`), the icon set shadcn/ui uses. No other icon library. |
| Fonts | **Bitter** for titles, **Roboto** for text, **Fira Mono** for code, self-hosted with Fontsource. |
| Deploy | **GitHub Pages**, through a GitHub Actions workflow. |

Always install the latest versions. Don't pin versions from memory: run the install commands and let npm resolve them.

## 1. Create the project

```bash
npm create vite@latest <project-name> -- --template react-ts
cd <project-name>
npm install
npm install d3 lucide-react @fontsource-variable/bitter @fontsource/roboto @fontsource/fira-mono
npm install -D @types/d3 @types/node
```

Then set up Tailwind and shadcn/ui following the current [shadcn/ui Vite guide](https://ui.shadcn.com/docs/installation/vite): the `@tailwindcss/vite` plugin, the `@/*` path alias in `tsconfig.json`, `tsconfig.app.json` and `vite.config.ts`, then `npx shadcn@latest init`. If the guide and these notes disagree, follow the guide for the setup commands and keep the preferences below.

Add the shadcn components the page needs, and no more: `npx shadcn@latest add button card` is enough for the default page.

## 2. Load the d3 skill

Every chart in this project follows the **d3** skill from the same repo: D3 for math, React for rendering, margins and bounds, axes as components, the `useDimensions` hook and `Responsive*` wrappers, Motion for animation.

- Read it now, before writing chart code: `../d3/SKILL.md` next to this skill, or [github.com/holtzy/dataviz-skills/tree/main/d3](https://github.com/holtzy/dataviz-skills/tree/main/d3) if it isn't installed.
- Copy the whole `d3` folder (with its `references/`) into the new project's skills folder (`.claude/skills/d3/`, or `.cursor/skills/`, `.agents/skills/`… for the tool in use), so every future session in the project follows it too.

## 3. Fonts and typography

Load the fonts once, in `src/main.tsx`:

```ts
import "@fontsource-variable/bitter";
import "@fontsource/roboto/300.css";
import "@fontsource/roboto/400.css";
import "@fontsource/roboto/500.css";
import "@fontsource/roboto/700.css";
import "@fontsource/fira-mono/400.css";
```

Fontsource bundles the font files with the site, so visitors never call Google Fonts.

In `src/index.css`, after the shadcn variables, register the fonts as Tailwind theme tokens and style the base elements. These values match the [React Graph Gallery](https://www.react-graph-gallery.com):

```css
@theme inline {
  --font-title: "Bitter Variable", serif;
  --font-sans: "Roboto", sans-serif;
  --font-mono: "Fira Mono", monospace;
}

@layer base {
  body {
    @apply bg-background text-foreground font-sans text-[19px];
  }

  p {
    @apply leading-7 [&:not(:first-child)]:mt-6;
  }

  h1, h2, h3 {
    font-family: var(--font-title);
    font-weight: bold;
    letter-spacing: 0.03em;
  }

  h1 {
    font-size: 28px;
    line-height: 36px;
  }
  @media (min-width: 640px) {
    h1 {
      font-size: 42px;
      line-height: 54px;
    }
  }

  /* Lots of space above each section title */
  h2 {
    font-size: 32px;
    line-height: 44px;
    margin-top: 100px;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
    scroll-margin-top: 100px;
  }

  h3 {
    font-size: 22px;
    line-height: 34px;
    margin-top: 40px;
  }
  h3 + p {
    margin-top: 8px;
  }

  code {
    font-family: var(--font-mono);
    font-size: 92%;
  }
}
```

Keep the big `margin-top` on `h2`: it is what separates the sections of a long dataviz page.

## 4. Narrow content column

Text reads best in a narrow column, while some charts need more room. Use a three-column grid ([full-bleed layout](https://www.joshwcomeau.com/css/full-bleed/)): everything sits in the 700px middle column, and an element with `full-bleed` spans the whole width.

```css
@layer components {
  .wrapper {
    display: grid;
    grid-template-columns: 1fr min(700px, 100%) 1fr;
    padding-left: 15px;
    padding-right: 15px;
  }
  .wrapper > * {
    grid-column: 2;
  }
  .full-bleed {
    grid-column: 1 / 4;
    width: 100%;
  }
}
```

The page is `<main className="wrapper">…</main>`. Don't use a wider `max-w-*` container for text.

## 5. Default barplot

Create a working, responsive barplot that follows the d3 skill, so the user starts from a correct pattern:

```
src/
  hook/use-dimensions.ts        shared hook, contract in the d3 skill
  components/barplot/
    Barplot.tsx                 takes width, height, data
    ResponsiveBarplot.tsx       wrapper, does nothing else
    AxisBottom.tsx
  data/barplot-data.ts          8 to 10 { name, value } rows of example data
```

- Horizontal bars sorted by value, names as labels on the left of the bars, a bottom axis.
- Colors from the shadcn theme variables (`var(--primary)`, `var(--muted-foreground)`), so the chart matches the page.
- All types explicit: `type DataItem = { name: string; value: number }`, props types, `d3.ScaleBand<string>`, `d3.ScaleLinear<number, number>`.

`App.tsx` renders a short page that shows the conventions: an `h1`, an intro paragraph, an `h2` section with the barplot in a container with an explicit height (`<div className="h-[400px]">`), and a shadcn `Button` with a Lucide icon (for example a link to the source code with `<Github />`).

## 6. GitHub Pages

The site is served from `https://<user>.github.io/<project-name>/`, so Vite needs the base path. In `vite.config.ts`:

```ts
export default defineConfig({
  base: "/<project-name>/",
  // plugins, resolve.alias…
});
```

Reference assets in `public/` through `import.meta.env.BASE_URL`, never with a leading `/`.

Add `.github/workflows/deploy.yml`, which builds and deploys on every push to `main`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: lts/*
          cache: npm
      - run: npm ci
      - run: npm run build
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: dist
      - id: deployment
        uses: actions/deploy-pages@v4
```

## 7. Check and hand over

1. `npm run build` passes with no TypeScript error.
2. `npm run dev`, open the page, and check the barplot renders, resizes with the window, and uses the fonts (Bitter titles, Roboto text).
3. `git init` and make a first commit. Don't create the GitHub repo or push unless the user asks.

Tell the user the last manual step: on GitHub, **Settings → Pages → Source: GitHub Actions**. After the next push, the site is live at `https://<user>.github.io/<project-name>/`.
