"""tools/data_map.py: the graphs are read from the repo, so these check they still
see what the pipeline actually does. Uses only committed files."""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "src"))
import build_spending as bs  # noqa: E402
import data_map as dm  # noqa: E402


def test_every_src_step_and_processed_file_is_in_the_pipeline():
    g = dm.pipeline_graph()
    steps = {n for n, a in g["nodes"].items() if a["kind"] == "step"}
    with_args = {f"src/{p.name}" for p in (REPO / "src").glob("*.py") if "add_argument" in p.read_text()}
    assert steps == with_args
    produced = {e["dst"] for e in g["edges"] if e["src"] in steps}
    processed = {f"data/processed/{p.name}" for p in (REPO / "data/processed").glob("*.csv")}
    assert processed <= produced, f"processed files no step writes: {processed - produced}"
    # a directory argument is resolved to the files written into it
    assert {"data/processed/core_ring_share.csv", "data/processed/member_assessment.csv"} <= produced
    for fetch in ("fetch_equalized", "fetch_fir", "fetch_population"):
        assert f"source:{fetch}" in g["nodes"]


def test_spending_exclusions_match_build_spending():
    """The dashed edges come from the output rows; they must name exactly the members
    build_spending leaves out, so the map can't show a series as whole when it isn't."""
    shown = set()
    for region in ("edmonton", "calgary"):
        for e in dm.region_graph(region)["edges"]:
            if e.get("style") == "excluded":
                shown.add((e["dst"].rsplit(":", 1)[1], e["src"]))
    expected = {("police", m) for m in bs.POLICE_EXCLUDED}
    expected |= {("police", m) for _, m in bs.POLICE_ZERO_YEARS}
    expected |= set(bs.NOT_COMPARABLE)
    assert shown == expected


def test_year_spans():
    assert dm.year_spans([1997, 1998, 1999, 2001, 2010, 2011]) == "1997–1999, 2001, 2010–2011"
    assert dm.year_spans([]) == "none"
