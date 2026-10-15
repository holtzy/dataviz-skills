#!/usr/bin/env python3
"""PreToolUse hook: ask the agent to load the dataviz skills before writing chart code.

Skills are chosen from their description, and an agent busy fetching data tends to go straight to
plotting code without loading any of them. This hook spots chart/map-drawing code in Write, Edit,
NotebookEdit and Bash calls and, if no dataviz-design skill (inspiration, chart-type, maps, color)
has been loaded in the session, denies the call ONCE with a reason naming the skills to load,
including the library skill matching the code (matplotlib, ggplot2, d3). A retry goes through, so
the hook can never lock anyone out.

Opt out with DATAVIZ_NUDGE=off. Never fails closed: any error means "allow".
Standard library only.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

DESIGN_SKILLS = ("inspiration", "chart-type", "maps", "color")

# Chart/map-drawing code, across the usual languages and libraries.
PLOT_PATTERN = re.compile(
    r"""
    matplotlib | pyplot | \bplt\.\w+\( | \bsns\.\w+\( | seaborn
    | plotly | \bpx\.\w+\( | \bgo\.Figure | altair | \balt\.Chart | bokeh | folium | plotnine | pygal
    | \.plot\( | \.hist\( | \.choropleth\(
    | \bggplot\( | \bgeom_\w+\( | \btm_shape\( | \bleaflet\(
    | \bd3\.(select|scale|geo|axis|line|area|arc|pie|stack|forceSimulation)
    | \bvega | \bPlot\.plot\( | @observablehq/plot | new\s+Chart\( | echarts | recharts | @nivo/ | @visx/
    | maplibre | mapbox-gl | deck\.gl | kepler\.gl
    """,
    re.IGNORECASE | re.VERBOSE,
)
LIBRARY_SKILLS = [
    ("matplotlib", re.compile(r"matplotlib|pyplot|\bplt\.|seaborn|\bsns\.|\.plot\(", re.IGNORECASE)),
    ("ggplot2", re.compile(r"\bggplot\(|\bgeom_\w+\(", re.IGNORECASE)),
    ("d3", re.compile(r"\bd3\.", re.IGNORECASE)),
]
MAP_PATTERN = re.compile(
    r"geopandas|\bgpd\.|choropleth|folium|leaflet|maplibre|mapbox|geom_sf|tm_shape|d3\.geo|cartopy|\.to_crs\(",
    re.IGNORECASE,
)


def _text_of(tool_name: str, tool_input: dict[str, Any]) -> str:
    if tool_name == "Bash":
        return tool_input.get("command") or ""
    parts = [tool_input.get(k) or "" for k in ("content", "new_string", "new_source")]
    parts += [e.get("new_string") or "" for e in tool_input.get("edits") or [] if isinstance(e, dict)]
    return "\n".join(parts)


def _design_skill_loaded(transcript_path: str) -> bool:
    names = "|".join(re.escape(s) for s in DESIGN_SKILLS)
    by_tool = re.compile(r'"skill"\s*:\s*"(?:[\w.-]+:)?(?:' + names + r')"')  # invoked through the Skill tool
    by_slash = re.compile(r"Base directory for this skill: \S*/dataviz-design/(?:" + names + r")\b")  # typed by the user
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as f:
            for line in f:
                if by_tool.search(line) or by_slash.search(line):
                    return True
    except OSError:
        pass
    return False


def _reason(code: str) -> str:
    skills = ["inspiration (published references to borrow from)",
              "chart-type (if the chart type is not settled yet)"]
    if MAP_PATTERN.search(code):
        skills.append("maps (projection, choropleth vs bubble map…)")
    skills.append("color (palette)")
    skills += [f"{name} (library skill)" for name, pat in LIBRARY_SKILLS if pat.search(code)]
    return (
        "dataviz-nudge: this call writes chart/map-drawing code, and no dataviz design skill has been "
        "loaded in this session. Before writing it, load the relevant skills with the Skill tool: "
        + "; ".join(skills)
        + ". Then write the code applying them, and cite the references you borrow from with their links. "
        "If this call is not about designing a visualization (fixing a test, a small tweak to a chart "
        "the user already approved…), just retry the same call: this check fires only once per session."
    )


def _marker(session_id: str) -> Path:
    base = os.environ.get("CLAUDE_PLUGIN_DATA") or str(Path.home() / ".cache" / "dataviz-skills")
    safe = re.sub(r"[^\w.-]", "_", session_id) or "unknown"
    return Path(base) / "nudge-sessions" / safe


def main() -> int:
    if os.environ.get("DATAVIZ_NUDGE", "").lower() in {"off", "0", "false", "no"}:
        return 0
    try:
        event = json.load(sys.stdin)
        code = _text_of(event.get("tool_name") or "", event.get("tool_input") or {})
        if not PLOT_PATTERN.search(code):
            return 0
        if _design_skill_loaded(event.get("transcript_path") or ""):
            return 0
        marker = _marker(str(event.get("session_id") or ""))
        if marker.exists():
            return 0  # already nudged in this session: let the agent decide
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.touch()
        out = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": _reason(code),
            }
        }
    except Exception:  # never block because of a bug in this hook
        return 0
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
