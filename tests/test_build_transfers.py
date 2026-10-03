"""build_transfers: total provincial transfers per capita (decision 9 as amended
2026-10-01; population decision 2026-10-02). The real-data tests read the
committed data/processed/transfers_per_capita.csv and recompute from the
committed fir_long.csv and population.csv without calling the module."""
import csv
import sys
from collections import defaultdict
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
import build_transfers as bt  # noqa: E402

OUT = list(csv.DictReader((REPO / "data/processed/transfers_per_capita.csv").open()))
ROW = {(r["region"], r["level"], r["unit"], int(r["year"])): r for r in OUT}
FIR = list(csv.DictReader((REPO / "data/processed/fir_long.csv").open()))
POP = list(csv.DictReader((REPO / "data/processed/population.csv").open()))


def recompute():
    lines = lambda y: ("01912", "01922") if y >= 2023 else ("01910", "01920")  # noqa: E731
    t = defaultdict(float)
    for r in FIR:
        y = int(r["fir_year"])
        if r["line_code"] in lines(y):
            t[(r["muni_id"], y)] += float(r["value"])
    p = {(r["muni_id"], int(r["year"])): int(r["population_asof"]) for r in POP}
    return t, p


def test_core_values_pinned():
    # 516.79 / 496.26 on 2021 boundaries; the 542 people annexed in 2019 come out (audit Q1).
    assert ROW[("edmonton", "side", "core", 2010)]["per_capita"] == "517.12"
    assert ROW[("calgary", "side", "core", 2023)]["per_capita"] == "317.0"
    assert ROW[("edmonton", "side", "core", 2010)]["per_capita_5yr"] == "496.6"


def test_every_row_matches_an_independent_recompute():
    t, p = recompute()
    side = defaultdict(set)
    for r in POP:
        side[(r["region"], r["role"])].add(r["muni_id"])
    for r in OUT:
        y = int(r["year"])
        munis = [r["unit"]] if r["level"] == "member" else side[(r["region"], r["unit"])]
        tt, pp = sum(t[(m, y)] for m in munis), sum(p[(m, y)] for m in munis)
        assert int(r["transfers"]) == round(tt) and int(r["population"]) == pp, r
        assert float(r["per_capita"]) == round(tt / pp, 2), r
        span = range(y - 4, y + 1)
        if y - 4 < 2001:
            assert r["per_capita_5yr"] == ""
        else:
            five = sum(t[(m, s)] for m in munis for s in span) / sum(p[(m, s)] for m in munis for s in span)
            assert float(r["per_capita_5yr"]) == round(five, 2), r


def test_shape_and_basis():
    members = {r["muni_id"] for r in csv.DictReader((REPO / "data/regions.csv").open())}
    years = {int(r["year"]) for r in OUT}
    assert years == set(range(2001, max(years) + 1)) and max(years) >= 2025
    assert {r["unit"] for r in OUT if r["level"] == "member"} == members
    assert len(OUT) == (len(members) + 4) * len(years)
    assert all(r["basis_note"].startswith("nominal dollars; total provincial transfers") for r in OUT)


def test_absorbed_village_transfers_are_in_their_member():
    own = sum(float(r["value"]) for r in FIR if r["fir_code"] == "0245" and r["fir_year"] == "2016"
              and r["line_code"] in ("01910", "01920"))
    assert int(ROW[("edmonton", "member", "parkland", 2016)]["transfers"]) > own  # + Wabamun


def test_negative_line_is_kept_and_named():
    r = ROW[("edmonton", "member", "spruce_grove", 2015)]
    assert int(r["transfers"]) == -1760210 and "negative line kept as printed" in r["basis_note"]
    assert "negative line kept" in ROW[("edmonton", "side", "ring", 2015)]["basis_note"]


def test_population_without_transfers_fails():
    pop = [{"year": "2001", "muni_id": "a", "region": "r", "role": "core", "population": "10", "population_asof": "10"}]
    with pytest.raises(bt.BuildError, match="no transfers"):
        bt.build([], pop)
