---
name: new-dataviz-project
description: Scaffold a new web dataviz project with Yan Holtz's preferred stack - React, TypeScript, D3, shadcn/ui + Tailwind, Lucide icons, Bitter / Roboto / Fira Mono fonts, a narrow reading column, a default barplot, and GitHub Pages deployment. Use when the user asks to create, start, scaffold or set up a new dataviz, chart, D3 or React visualization project or website.
---

# New dataviz project

Create a project that is ready to deploy, where the user only has to replace the default barplot with their own charts. Ask for the project name if it wasn't given. Use the latest version of every tool.

## What the project must have

- **TypeScript** everywhere, in strict mode.
- **D3**, latest version, with types from DefinitelyTyped (`@types/d3`).
- **The d3 skill.** Read the d3 skill from this repo before writing any chart code, and copy its folder into the new project's skills folder so later sessions follow it too.
- **shadcn/ui + Tailwind** for the UI, and **Lucide** (`lucide-react`) for icons.
- **Fonts:** Bitter for titles, Roboto for body text (19px), Fira Mono for code. Self-host them, so visitors never call Google Fonts.
- **Big gaps above `h2` titles:** `margin-top: 100px`, with a thin bottom border.
- **A narrow column:** content is 700px wide at most, centered. Charts can break out to full width when they need it.
- **A default barplot:** responsive, following the d3 skill, with example data, shown on a short page with a title, an intro paragraph and one section.
- **GitHub Pages:** a GitHub Actions workflow that deploys on every push to `main`, with the base path set for `https://<user>.github.io/<project-name>/`.

## Before handing over

- The build passes, and the page renders the barplot with the right fonts.
- Make a first git commit. Don't create the GitHub repo or push unless asked.
- Tell the user the one manual step: on GitHub, **Settings → Pages → Source: GitHub Actions**.
