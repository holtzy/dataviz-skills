# Dataviz Skills

A collection of AI skills for data visualization, by [Yan Holtz](https://www.yan-holtz.com).

Skills give your AI assistant specialized knowledge and workflows. They are activated automatically when your task matches, so your agent picks the right chart, the right colors, and writes better D3, ggplot2 or Matplotlib code, without you having to ask.

These skills follow the open [Agent Skills](https://agentskills.io) standard (`SKILL.md`). They work in **Claude Code, Claude.ai, OpenAI Codex, GitHub Copilot, Gemini CLI, Cursor, Windsurf** and [many more](https://github.com/vercel-labs/skills). They're plain Markdown, so you can also paste them into any chat app.

> 🚧 **Work in progress.** The structure is in place, and the skills are being written.


## Available Skills

### Dataviz Design

Tool-agnostic skills: the principles behind a good chart. Useful whatever you build it with, from D3 to Excel.

- **[chart-type](./dataviz-design/chart-type/)** - Pick the right chart for your data and your question, following the [data-to-viz.com](https://www.data-to-viz.com) decision tree
- **[color](./dataviz-design/color/)** - Choose a purposeful, colorblind-safe palette (categorical, sequential, diverging) and use color to highlight what matters
- **[maps](./dataviz-design/maps/)** - Visualize geographic data: choropleth, bubble map, hexbin, cartogram or connection map, and when to use which
- **[inspiration](./dataviz-design/inspiration/)** - Before drawing, find 3–5 published charts to borrow ideas from, searched across [dataviz-inspiration.com](https://www.dataviz-inspiration.com) and [Dataviz Index](https://datavizindex.fr), and cite them with links back to each source (co-authored with [Joël Gombin](https://github.com/joelgombin))

### Dataviz Tech

Library-specific skills: build and polish charts with your tool of choice.

- **[d3](./dataviz-tech/d3/)** - Build charts with D3.js inside React / Next.js: D3 for the math, React for the rendering, with responsiveness, axes, tooltips and transitions
- **[ggplot2](./dataviz-tech/ggplot2/)** - Create publication-ready charts in R with ggplot2: themes, fonts, annotations, direct labels and export
- **[matplotlib](./dataviz-tech/matplotlib/)** - Create publication-ready charts in Python with Matplotlib and Seaborn: clean styling, annotations, direct labels and export

## Installation

### Using `npx skills add` (Any Agent)

Install skills into any supported coding agent (Claude Code, Codex, Cursor, Copilot, Gemini CLI, and [many more](https://github.com/vercel-labs/skills)):

```bash
# List available skills without installing
npx skills add holtzy/dataviz-skills --list

# Install skills via an interactive menu
npx skills add holtzy/dataviz-skills

# Install specific skills
npx skills add holtzy/dataviz-skills --skill chart-type --skill ggplot2

# Install globally (all your projects)
npx skills add holtzy/dataviz-skills --global
```

### Claude Code

#### Method 1: Add Marketplace

Add this repository as a plugin marketplace in Claude Code:

```
/plugin marketplace add holtzy/dataviz-skills
```

Then browse and install the skill categories you need through the Claude Code UI.

#### Method 2: Direct Installation

Install a whole category directly:

```
/plugin install dataviz-design@dataviz-skills
/plugin install dataviz-tech@dataviz-skills
/plugin install dataviz-nudge@dataviz-skills
```

`dataviz-nudge` is not a skill but a Claude Code hook, see [Making sure the skills are used](#making-sure-the-skills-are-used-claude-code).

#### Method 3: Manual Installation

```bash
git clone https://github.com/holtzy/dataviz-skills.git
cp -r dataviz-skills/dataviz-tech/ggplot2 ~/.claude/skills/
```

### Other agents (manual)

Copy the skill folders into your tool's skills directory:

| Tool | Project folder | Global folder |
|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Cursor | `.cursor/skills/` | `~/.cursor/skills/` |
| GitHub Copilot | `.github/skills/` | — |
| OpenAI Codex | `.agents/skills/` | `~/.agents/skills/` |

No skill support in your tool? Point it at [`AGENTS.md`](./AGENTS.md), which indexes every skill.

### Claude.ai

Download a skill zip from the [latest release](https://github.com/holtzy/dataviz-skills/releases/latest) and upload it following the [Creating Custom Skills guide](https://support.claude.com/en/articles/12512198-creating-custom-skills).

### ChatGPT, Gemini and other chat apps

Create a project (or a Gem) and paste the content of the `SKILL.md` you need into its instructions.

## Using Skills

Once installed, your agent activates relevant skills automatically based on your task. You don't need to invoke them.

For example, with the `chart-type` and `ggplot2` skills installed:

```
You: I have salaries for 5 departments, ~200 employees each. Plot them with ggplot2.

Claude: Since you want to compare distributions across groups, a boxplot with
jittered points will show both the summary and the individual salaries...
```

### Making sure the skills are used (Claude Code)

Agents pick skills from their description at the start of a task. Once busy fetching and cleaning
data, they often jump straight to plotting code without loading any. The optional
**[dataviz-nudge](./hooks/dataviz-nudge/)** plugin fixes that: when the agent is about to write
chart or map code (Matplotlib, ggplot2, D3, plotly, Vega, Leaflet…) and no design skill has been
loaded in the session, the call is denied **once**, with a reason naming the skills to load
(`inspiration`, `chart-type`, `maps`, `color`, and the matching library skill). A retry goes
through, so it never locks anyone out. Opt out with `DATAVIZ_NUDGE=off`.

## Skill Categories

| Category | Description |
| --- | --- |
| **dataviz-design** | Tool-agnostic dataviz principles (chart type, color, maps) and published references (inspiration) |
| **dataviz-tech** | Library-specific skills (D3 + React, ggplot2, Matplotlib) |

## Want to go deeper?

Each tech skill is the condensed version of a full course:

| Skill | Gallery | Course |
| --- | --- | --- |
| **d3** | [React Graph Gallery](https://www.react-graph-gallery.com) | [D3 Loves React](https://www.d3-loves-react.com) |
| **ggplot2** | [R Graph Gallery](https://r-graph-gallery.com) | [ggplot2 Uncharted](https://www.ggplot2-uncharted.com) |
| **matplotlib** | [Python Graph Gallery](https://python-graph-gallery.com) | [Matplotlib Journey](https://www.matplotlib-journey.com) |

The design skills build on [data-to-viz.com](https://www.data-to-viz.com).

## Contributing

Issues and PRs are welcome! Skills are grouped by category: each skill is a folder containing a `SKILL.md` whose `name` matches the folder name.

While editing skills, symlink them into your global skills folder so every project picks up your changes:

```bash
./scripts/link-skills.sh                    # → ~/.claude/skills
./scripts/link-skills.sh ~/.cursor/skills   # or any other tool's folder
```

Skills that ship scripts (`inspiration`) and the `dataviz-nudge` hook have tests:

```bash
pip install pytest && pytest
```

## License

This repository is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

The `inspiration` skill reads its galleries live from their public endpoints and never copies them
into this repository:

- [dataviz-inspiration.com](https://www.dataviz-inspiration.com): catalog data licensed under
  [CC BY 4.0](https://github.com/holtzy/dataviz-inspiration/blob/main/LICENSE);
- [Dataviz Index](https://datavizindex.fr) by [WeDoData](https://wedodata.fr), from the
  [*Buena Vista Data Club*](https://wedodata.beehiiv.com) newsletter: selection and editorial
  comments © WeDoData. The agent reads them like a visitor would, paraphrases and links to them;
  it does not republish them.

Images in both galleries are screenshots of work by their respective authors: the agent may look
at them, never reuse them.

## Resources

- [Agent Skills standard](https://agentskills.io)
- [`npx skills` CLI](https://github.com/vercel-labs/skills)
- [Using Skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
- [Anthropic's Official Skills Repository](https://github.com/anthropics/skills)
- [Posit Skills](https://github.com/posit-dev/skills), which inspired this repo's structure

---

**Built with ❤️ + ☕ + 📊 by [Yan Holtz](https://www.yan-holtz.com)**
