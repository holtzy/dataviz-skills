## AI skills for data visualization

### What is this?

This repo provides a set of AI skills that improve the quality of the charts you build with AI. They cover both the technical side (clean, idiomatic code) and the aesthetic side (chart choice, color, polish) of the work.

The skills follow the open [Agent Skills](https://agentskills.io) standard (`SKILL.md`). Each one is a Markdown file that your favorite AI tool reads to produce better results.

> 🚧 **Work in progress.** The structure is in place, and the skills are being written.

### Available skills

- **[inspiration](./inspiration/)** - Before drawing, find 3–5 published charts to borrow ideas from, searched across [dataviz-inspiration.com](https://www.dataviz-inspiration.com) and [Dataviz Index](https://datavizindex.fr), and cite them (co-authored with [Joël Gombin](https://github.com/joelgombin))
- **[d3](./d3/)** - Build charts with D3.js inside React / Next.js
- **[ggplot2](./ggplot2/)** - Create publication-ready charts in R with ggplot2 (co-authored with [Cédric Scherer](https://www.cedricscherer.com))
- **[matplotlib](./matplotlib/)** - Create publication-ready charts in Python with Matplotlib and Seaborn (co-authored with [Joseph Barbier](https://github.com/JosephBARBIERDARNAL))
- **[roast-my-chart](./roast-my-chart/)** - Review a finished chart against the 61 [Data to Viz caveat flashcards](https://github.com/holtzy/dataviz-caveat-flashcards) and get a prioritized list of fixes

### How to use

**Coding agent** (Claude Code, Cursor, Codex, Copilot, Gemini CLI…):

```bash
npx skills add holtzy/dataviz-skills
```

In Claude Code, you can also use `/plugin marketplace add holtzy/dataviz-skills`. The marketplace also offers `dataviz-nudge`, a hook that makes the agent load the inspiration skill before it writes chart code.

**Claude.ai**: download a skill zip from the [latest release](https://github.com/holtzy/dataviz-skills/releases/latest) and upload it in your settings ([guide](https://support.claude.com/en/articles/12512198-creating-custom-skills)).

**ChatGPT, Gemini and other chat apps**: paste the content of a `SKILL.md` into your project or Gem instructions.

Once a skill is installed, just describe your task. Your AI loads the relevant skills automatically.

### License

This repository is licensed under the MIT License. See [LICENSE](./LICENSE).
