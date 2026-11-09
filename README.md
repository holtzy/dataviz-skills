# AI skills for data visualization

This repo provides a set of AI skills that improve the quality of the charts you build with AI. They cover both the **technical** side (clean, idiomatic code) and the **aesthetic** side (chart choice, color, polish) of the work. You can stay up to date with my skills by [signing up to the newsletter](https://www.yan-holtz.com/subscribe).

The skills follow the open Agent Skills standard (`SKILL.md`). Each one is a Markdown file that your favorite AI tool reads to produce better results.

## Available skills

- **[d3](./d3/)** - Improve the quality of the code of a d3.js chart inside a React environment.
- **[ggplot2](./ggplot2/)** - Publication-ready charts in R with ggplot2 (co-authored with Cédric Scherer)
- **[matplotlib](./matplotlib/)** - Publication-ready charts in Python with Matplotlib and Seaborn (co-authored with Joseph Barbier)

- **[roast-my-chart](./roast-my-chart/)** - Review a finished chart against the 61 [Data to Viz caveat flashcards](https://github.com/holtzy/dataviz-caveat-flashcards) and get a prioritized list of fixes
- **[inspiration](./inspiration/)** - Before drawing, find 3–5 published charts to borrow ideas from, searched across [dataviz-inspiration.com](https://www.dataviz-inspiration.com) and [Dataviz Index](https://datavizindex.fr) (co-authored with Joël Gombin)

## How to use

Once a skill is installed, just describe your task. Your AI loads the relevant skills automatically.

### Copy the skill folders

No install needed. Get the skills with git, or with **Code → Download ZIP** on this page:

```bash
git clone https://github.com/holtzy/dataviz-skills.git
```

Then copy the skill folders you want into your tool's skills folder:

| Tool | Project folder | Global folder |
|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Cursor | `.cursor/skills/` | `~/.cursor/skills/` |
| GitHub Copilot | `.github/skills/` | — |
| OpenAI Codex | `.agents/skills/` | `~/.agents/skills/` |

For example: `cp -r dataviz-skills/roast-my-chart ~/.claude/skills/`

**Claude.ai**: download a skill zip from the [latest release](https://github.com/holtzy/dataviz-skills/releases/latest) and upload it in your settings ([guide](https://support.claude.com/en/articles/12512198-creating-custom-skills)).

**ChatGPT, Gemini and other chat apps**: paste the content of a `SKILL.md` into your project or Gem instructions.

### Claude Code marketplace

In Claude Code, add this repo as a marketplace and install the skills:

```
/plugin marketplace add holtzy/dataviz-skills
/plugin install dataviz-skills@dataviz-skills
```

The marketplace also offers `dataviz-nudge`, a hook that makes the agent load the inspiration skill before it writes chart code.

### With Node.js: npx

If you have Node.js installed, one command installs the skills into any coding agent (Claude Code, Cursor, Codex, Copilot, Gemini CLI…):

```bash
npx skills add holtzy/dataviz-skills
```

Add `--skill roast-my-chart` to install a single skill, and `--global` to install it for all your projects.

## License

This repository is licensed under the MIT License. See [LICENSE](./LICENSE).
