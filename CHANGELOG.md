# Changelog

## Unreleased

- New skill `dataviz-design/inspiration`: searches curated galleries (dataviz-inspiration.com, Dataviz Index) as one catalog for published references to borrow from, with links back to each source. Standard-library Python script, cached live reads, 34 tests.
- New Claude Code plugin `dataviz-nudge`: a `PreToolUse` hook that asks the agent to load the design skills (and the matching library skill) before it writes chart or map code. Once per session, opt-out with `DATAVIZ_NUDGE=off`.
- Test workflow running `pytest` on Python 3.9 and 3.12.
- Repository structure with two categories: `dataviz-design` (chart-type, color, maps) and `dataviz-tech` (d3, ggplot2, matplotlib).
- Skills are placeholders for now.
- Claude Code plugin marketplace, `AGENTS.md` fallback index, release workflow publishing one zip per skill.
