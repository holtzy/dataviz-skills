import json
import os
import sys
import time
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "dataviz-design/inspiration/scripts"
sys.path.insert(0, str(SCRIPTS))

import search_viz as sv  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"
YAN_RAW = json.loads((FIXTURES / "yan.json").read_text())
DVI_RAW = json.loads((FIXTURES / "dvi_blocks.json").read_text())
DVI_ITEM_HTML = (FIXTURES / "dvi_item.html").read_bytes()

NYC = "dvi:heatmap-des-temps-de-trajet-a-nyc-1657c27b-e92c-4cbe-8bf6-362784b3b3e0"
MEADOWS = "dvi:le-rapport-meadows-revisite-c5818333-d36a-474b-bf5f-1983cd7b1798"


@pytest.fixture
def yan():
    return sv.normalize_yan(YAN_RAW)


@pytest.fixture
def dvi():
    return sv.normalize_dvi(DVI_RAW)


@pytest.fixture
def items(yan, dvi):
    return yan + dvi


def uids(results):
    return [r["uid"] for r in results]


@pytest.fixture
def offline(monkeypatch):
    def boom(url):
        raise OSError("offline")

    monkeypatch.setattr(sv, "_download", boom)


@pytest.fixture
def cache_dir(tmp_path):
    (tmp_path / "dataviz-inspiration.json").write_text(json.dumps(YAN_RAW))
    (tmp_path / "datavizindex.json").write_text(json.dumps(DVI_RAW))
    return tmp_path


# --- normalization ---------------------------------------------------------

def test_yan_items_are_normalized(yan):
    first = yan[0]
    assert first["uid"] == "yan:1"
    assert first["source"] == "dataviz-inspiration"
    assert first["lang"] == "en"
    assert first["families"] == ["evolution"]
    assert first["description"] == "A circular streamgraph that broke the internet."
    assert first["thumbnail"] == "https://example.org/omicron-zoom.webp"
    # no per-viz page on the site: link to the chart-type page where it is listed
    assert first["page"] == "https://www.dataviz-inspiration.com/stream"
    assert first["via"] == {"name": "dataviz-inspiration.com", "url": "https://www.dataviz-inspiration.com"}


def test_yan_page_falls_back_to_homepage_for_types_without_a_page():
    payload = {"items": [dict(YAN_RAW["items"][0], chartTypes=["waffle"])]}
    assert sv.normalize_yan(payload)[0]["page"] == "https://www.dataviz-inspiration.com"


def test_yan_unknown_date_becomes_empty(yan):
    assert yan[4]["date"] == ""


def test_dvi_keeps_only_inspiration_entries(dvi):
    assert uids(dvi) == [NYC, MEADOWS]


def test_dvi_items_are_normalized(dvi):
    nyc = dvi[0]
    assert nyc["source"] == "datavizindex"
    assert nyc["lang"] == "fr"
    assert nyc["title"] == "Heatmap des temps de trajet à NYC"
    assert nyc["author"] == "Anthony Castrio"
    assert nyc["url"].startswith("https://castrio.me/nyc")
    assert nyc["page"] == "https://datavizindex.fr/inspiration-infographie-datavisualisation/" + NYC[4:]
    assert nyc["via"] == {"name": "Dataviz Index", "url": "https://datavizindex.fr"}
    assert nyc["date"] == "2026-10"
    assert nyc["chartTypes"] == ["cartographies", "heatmaps"]
    assert nyc["families"] == ["map", "correlation"]
    assert nyc["labels"] == ["interactif et web"]
    assert nyc["themes"] == ["Société"]
    assert nyc["interactive"] is True
    assert nyc["description"] == ""  # fetched on demand from the entry page
    # stable site path, not the expiring S3 url
    assert nyc["thumbnail"].startswith("https://datavizindex.fr/files/1657c27b")


# --- filtering -------------------------------------------------------------

def test_family_filter_spans_both_sources(items):
    assert uids(sv.filter_items(items, family="map")) == ["yan:2", "yan:4", NYC]


def test_type_filter_matches_native_types(items):
    assert uids(sv.filter_items(items, types=["sankey", "courbes-et-series"])) == ["yan:4", MEADOWS]


def test_unknown_family_raises(items):
    with pytest.raises(ValueError):
        sv.filter_items(items, family="nope")


def test_labels_are_combined_with_and(items):
    assert uids(sv.filter_items(items, labels=["annotation"])) == ["yan:1", "yan:2", "yan:4", "yan:5"]
    assert uids(sv.filter_items(items, labels=["annotation", "color palette"])) == ["yan:2"]


def test_filter_by_source(items):
    assert uids(sv.filter_items(items, source="datavizindex")) == [NYC, MEADOWS]


def test_filter_by_tool_is_case_insensitive(items):
    assert uids(sv.filter_items(items, tools=["r"])) == ["yan:3"]


def test_filter_interactive_and_luminosity(items):
    assert uids(sv.filter_items(items, interactive=True)) == ["yan:2", NYC, MEADOWS]
    assert uids(sv.filter_items(items, luminosity="dark")) == ["yan:3"]


def test_filter_since_drops_unknown_dates(items):
    assert uids(sv.filter_items(items, since="2022", source="dataviz-inspiration")) == ["yan:1", "yan:4"]


# --- free-text ranking -----------------------------------------------------

def test_query_is_accent_and_case_insensitive(items):
    assert uids(sv.rank(items, "ELECTIONS municipales"))[0] == "yan:2"


def test_query_matches_french_titles(items):
    assert uids(sv.rank(items, "temps de trajet"))[0] == NYC


def test_query_ranks_title_hits_above_description_hits(items):
    assert uids(sv.rank(items, "gas map"))[0] == "yan:4"


def test_query_drops_items_without_any_hit(items):
    assert uids(sv.rank(items, "lollipop")) == ["yan:3"]


def test_no_query_sorts_favorites_then_most_recent(items):
    assert uids(sv.rank(items, None))[:2] == ["yan:2", NYC] or uids(sv.rank(items, None))[:2] == ["yan:2", MEADOWS]
    assert uids(sv.rank(items, None))[-1] == "yan:5"


# --- loading & cache -------------------------------------------------------

def test_load_uses_fresh_cache_without_network(cache_dir, offline):
    assert sv.load_source("dataviz-inspiration", cache_dir=cache_dir, ttl_hours=24)["count"] == 5


def test_load_refreshes_stale_cache(tmp_path, monkeypatch):
    cache = tmp_path / "dataviz-inspiration.json"
    cache.write_text(json.dumps({"count": 0, "items": []}))
    old = time.time() - 48 * 3600
    os.utime(cache, (old, old))
    monkeypatch.setattr(sv, "_download", lambda url: json.dumps(YAN_RAW).encode())
    assert sv.load_source("dataviz-inspiration", cache_dir=tmp_path, ttl_hours=24)["count"] == 5
    assert json.loads(cache.read_text())["count"] == 5


def test_load_falls_back_to_stale_cache_when_offline(cache_dir, offline):
    old = time.time() - 48 * 3600
    os.utime(cache_dir / "datavizindex.json", (old, old))
    assert len(sv.load_source("datavizindex", cache_dir=cache_dir, ttl_hours=24)) == 3


def test_load_without_cache_and_offline_raises(tmp_path, offline):
    with pytest.raises(RuntimeError):
        sv.load_source("dataviz-inspiration", cache_dir=tmp_path, ttl_hours=24)


def test_load_all_survives_one_failing_source(tmp_path, offline):
    (tmp_path / "dataviz-inspiration.json").write_text(json.dumps(YAN_RAW))
    items, failed = sv.load_items(cache_dir=tmp_path, ttl_hours=24)
    assert len(items) == 5
    assert failed == ["datavizindex"]


# --- datavizindex descriptions on demand -----------------------------------

def test_dvi_description_is_read_from_entry_page(tmp_path, dvi, monkeypatch):
    calls = []

    def fake(url):
        calls.append(url)
        return DVI_ITEM_HTML

    monkeypatch.setattr(sv, "_download", fake)
    sv.enrich_descriptions(dvi[:1], cache_dir=tmp_path)
    assert dvi[0]["description"] == "C’est mouvant. Une UX originale pour visualiser le temps de trajet & la heatmap en live."
    # cached: a second item list does not hit the network again
    again = sv.normalize_dvi(DVI_RAW)[:1]
    sv.enrich_descriptions(again, cache_dir=tmp_path)
    assert again[0]["description"] == dvi[0]["description"]
    assert len(calls) == 1


def test_dvi_description_failure_is_silent(tmp_path, dvi, offline):
    sv.enrich_descriptions(dvi[:1], cache_dir=tmp_path)
    assert dvi[0]["description"] == ""


# --- rendering -------------------------------------------------------------

def test_markdown_credits_each_source_used(yan, dvi):
    out = sv.render_markdown([yan[0], dvi[0]], total=2)
    assert "Here’s When We Expect Omicron to Peak" in out
    assert "https://www.nytimes.com/omicron" in out
    assert "CC BY 4.0" in out
    assert "Dataviz Index" in out and "WeDoData" in out


def test_markdown_links_every_result_to_its_gallery(yan, dvi):
    out = sv.render_markdown([yan[0], dvi[0]], total=2)
    assert "- Found via dataviz-inspiration.com: https://www.dataviz-inspiration.com/stream" in out
    assert "- Found via Dataviz Index: https://datavizindex.fr/inspiration-infographie-datavisualisation/" in out
    # footer credits link to the galleries' home pages
    assert "[dataviz-inspiration.com](https://www.dataviz-inspiration.com)" in out
    assert "[Dataviz Index](https://datavizindex.fr)" in out


def test_markdown_credits_only_sources_present(yan):
    out = sv.render_markdown([yan[0]], total=1)
    assert "WeDoData" not in out


def test_unknown_date_and_empty_description(yan):
    item = dict(yan[4], description="")
    out = sv.render_markdown([item], total=1)
    assert "date unknown" in out
    assert "What the chart does" not in out


def test_download_thumbnails_writes_one_file_per_result(tmp_path, yan, monkeypatch):
    monkeypatch.setattr(sv, "_download", lambda url: b"img:" + url.encode())
    paths = sv.download_thumbnails(yan[:2], tmp_path)
    assert [p.name for p in paths] == ["yan-1-omicron-zoom.webp", "yan-2-mun-zoom.webp"]
    assert paths[0].read_bytes() == b"img:https://example.org/omicron-zoom.webp"


def test_download_thumbnails_skips_failures(tmp_path, yan, monkeypatch):
    def flaky(url):
        if "omicron" in url:
            raise OSError("404")
        return b"ok"

    monkeypatch.setattr(sv, "_download", flaky)
    assert [p.name for p in sv.download_thumbnails(yan[:2], tmp_path)] == ["yan-2-mun-zoom.webp"]


# --- CLI -------------------------------------------------------------------

def test_cli_json_output(cache_dir, offline, capsys):
    code = sv.main(["--cache-dir", str(cache_dir), "--family", "map", "--format", "json", "--limit", "2"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["total"] == 3
    assert len(payload["results"]) == 2
    assert any("CC BY 4.0" in c for c in payload["credits"])
    assert all(r["via"]["url"].startswith("https://") and r["page"] for r in payload["results"])


def test_cli_source_option(cache_dir, offline, capsys):
    assert sv.main(["--cache-dir", str(cache_dir), "--source", "datavizindex", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert {r["source"] for r in payload["results"]} == {"datavizindex"}


def test_cli_vocab_lists_families_types_and_labels(cache_dir, offline, capsys):
    assert sv.main(["--cache-dir", str(cache_dir), "--vocab"]) == 0
    out = capsys.readouterr().out
    assert "choropleth (2)" in out
    assert "cartographies (1)" in out
    assert "annotation (4)" in out
