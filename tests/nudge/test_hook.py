import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[2] / "hooks/dataviz-nudge/hooks/nudge.py"

MPL_CODE = "import geopandas as gpd\nimport matplotlib.pyplot as plt\ngdf.plot(column='abst', ax=ax)\nplt.savefig('carte.png')\n"


def run(payload, data_dir, env_extra=None):
    env = dict(os.environ, CLAUDE_PLUGIN_DATA=str(data_dir))
    env.pop("DATAVIZ_NUDGE", None)
    env.update(env_extra or {})
    proc = subprocess.run(
        [sys.executable, str(HOOK)], input=json.dumps(payload), capture_output=True, text=True, env=env, timeout=10
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout) if proc.stdout.strip() else None


def payload(tool_name, tool_input, transcript, session="s1"):
    return {
        "session_id": session,
        "transcript_path": str(transcript),
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input,
    }


def write_mpl(transcript, session="s1"):
    return payload("Write", {"file_path": "/x/carte.py", "content": MPL_CODE}, transcript, session)


@pytest.fixture
def transcript(tmp_path):
    t = tmp_path / "t.jsonl"
    t.write_text(json.dumps({"message": {"role": "user", "content": "fais-moi une carte"}}) + "\n")
    return t


def add_skill_call(transcript, skill):
    with transcript.open("a") as f:
        f.write(json.dumps({"message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "Skill", "input": {"skill": skill}}]}}) + "\n")


def reason(out):
    assert out is not None and out["hookSpecificOutput"]["permissionDecision"] == "deny"
    return out["hookSpecificOutput"]["permissionDecisionReason"]


def test_denies_chart_code_when_no_dataviz_skill_loaded(tmp_path, transcript):
    r = reason(run(write_mpl(transcript), tmp_path / "data"))
    assert "inspiration" in r and "chart-type" in r and "Skill" in r


def test_reason_names_the_library_skill_detected(tmp_path, transcript):
    data = tmp_path / "data"
    assert "matplotlib" in reason(run(write_mpl(transcript, "a"), data))
    gg = payload("Write", {"file_path": "/x/a.R", "content": "ggplot(df, aes(x, y)) + geom_line()"}, transcript, "b")
    assert "ggplot2" in reason(run(gg, data))
    d3 = payload("Write", {"file_path": "/x/C.tsx", "content": "const y = d3.scaleLinear()"}, transcript, "c")
    assert "d3" in reason(run(d3, data))


def test_reason_mentions_maps_for_map_code(tmp_path, transcript):
    assert "maps" in reason(run(write_mpl(transcript), tmp_path / "data"))


def test_denies_only_once_per_session(tmp_path, transcript):
    data = tmp_path / "data"
    reason(run(write_mpl(transcript), data))
    assert run(write_mpl(transcript), data) is None
    reason(run(write_mpl(transcript, session="s2"), data))


@pytest.mark.parametrize("skill", [
    "inspiration", "chart-type", "maps", "color",
    "dataviz-design:inspiration", "dataviz-design:chart-type",
])
def test_allows_once_a_design_skill_is_loaded(tmp_path, transcript, skill):
    add_skill_call(transcript, skill)
    assert run(write_mpl(transcript), tmp_path / "data") is None


def test_a_library_skill_alone_is_not_enough(tmp_path, transcript):
    add_skill_call(transcript, "dataviz-tech:matplotlib")
    reason(run(write_mpl(transcript), tmp_path / "data"))


def test_unrelated_skill_with_same_suffix_does_not_count(tmp_path, transcript):
    add_skill_call(transcript, "other-plugin:sitemaps")
    reason(run(write_mpl(transcript), tmp_path / "data"))


def test_allows_when_skill_typed_as_slash_command(tmp_path, transcript):
    with transcript.open("a") as f:
        f.write(json.dumps({"message": {"role": "user", "content": [
            {"type": "text", "text": "Base directory for this skill: /Users/x/.claude/plugins/cache/dataviz-skills/dataviz-design/inspiration\n\n# Inspiration"}]}}) + "\n")
    assert run(write_mpl(transcript), tmp_path / "data") is None


def test_ignores_code_without_plotting(tmp_path, transcript):
    code = "import pandas as pd\ndf = pd.read_csv('x.csv')\nprint(df.describe())\n"
    assert run(payload("Write", {"file_path": "/x/a.py", "content": code}, transcript), tmp_path / "data") is None


def test_detects_plotting_in_edit_bash_and_notebook(tmp_path, transcript):
    data = tmp_path / "data"
    reason(run(payload("Edit", {"file_path": "/x/a.py", "old_string": "x", "new_string": "fig = px.choropleth(df)"}, transcript, "e"), data))
    reason(run(payload("Bash", {"command": "python3 - <<'EOF'\nimport matplotlib.pyplot as plt\nEOF"}, transcript, "b"), data))
    reason(run(payload("NotebookEdit", {"notebook_path": "/x/n.ipynb", "new_source": "ggplot(df, aes(x, y)) + geom_line()"}, transcript, "n"), data))
    reason(run(payload("Write", {"file_path": "/x/index.html", "content": "<script>d3.select('#map').append('svg')</script>"}, transcript, "w"), data))


def test_bash_running_an_existing_script_is_not_blocked(tmp_path, transcript):
    assert run(payload("Bash", {"command": "python3 carte.py"}, transcript), tmp_path / "data") is None


def test_opt_out_env_var(tmp_path, transcript):
    assert run(write_mpl(transcript), tmp_path / "data", {"DATAVIZ_NUDGE": "off"}) is None


def test_missing_transcript_still_works(tmp_path):
    reason(run(write_mpl(tmp_path / "nope.jsonl"), tmp_path / "data"))


def test_garbage_stdin_never_blocks(tmp_path):
    proc = subprocess.run([sys.executable, str(HOOK)], input="not json", capture_output=True, text=True,
                          env=dict(os.environ, CLAUDE_PLUGIN_DATA=str(tmp_path)), timeout=10)
    assert proc.returncode == 0 and proc.stdout.strip() == ""
