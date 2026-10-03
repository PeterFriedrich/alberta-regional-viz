"""Population (decision 2026-10-02): StatCan 17-10-0155 July 1 estimates,
2021 boundaries, 2001-2025, one row per member per year; `population_asof`
moves them onto each year's boundaries with data/annexations.csv (audit Q1). The real-data tests
read the committed data/processed/population.csv (from src/fetch_population.py)."""
import csv
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
import fetch_population as fp  # noqa: E402

POP = list(csv.DictReader((REPO / "data/processed/population.csv").open()))
MEMBERS = {r["muni_id"] for r in csv.DictReader((REPO / "data/regions.csv").open())}
EVENTS = list(csv.DictReader((REPO / "data/annexations.csv").open()))
# 2021 Census counts, StatCan 98-10-0002 (checked 2026-10-02). The estimates
# correct for census undercoverage, so each sits a little above its count.
CENSUS_2021 = {
    "airdrie": 74100, "calgary": 1306784, "chestermere": 22163, "cochrane": 32199,
    "foothills": 23199, "high_river": 14324, "okotoks": 30405, "rocky_view": 41028,
    "beaumont": 20888, "devon": 6545, "edmonton": 1010899, "fort_saskatchewan": 27088,
    "leduc_city": 34094, "leduc_county": 14416, "morinville": 10385, "parkland": 32205,
    "spruce_grove": 37645, "st_albert": 68232, "stony_plain": 17993, "strathcona": 99225,
    "sturgeon": 20061}


def test_source_is_table_17_10_0155_from_2001():
    assert fp.PID == "17100155" and fp.FIRST_YEAR == 2001
    assert min(int(r["year"]) for r in POP) == 2001


def test_one_row_per_member_per_year():
    years = {int(r["year"]) for r in POP}
    assert years == set(range(2001, max(years) + 1)) and max(years) >= 2025
    assert sorted((r["muni_id"], int(r["year"])) for r in POP) == sorted(
        (m, y) for m in MEMBERS for y in years)


def test_pinned_values():
    got = {(r["muni_id"], int(r["year"])): int(r["population"]) for r in POP}
    assert got[("edmonton", 2016)] == 957435 and got[("edmonton", 2021)] == 1050945
    assert got[("airdrie", 2016)] == 63984 and got[("airdrie", 2021)] == 77079


def test_2021_estimates_sit_0_to_6_pct_above_the_census():
    est = {r["muni_id"]: int(r["population"]) for r in POP if r["year"] == "2021"}
    assert set(CENSUS_2021) == MEMBERS
    for m, c in CENSUS_2021.items():
        assert 1.0 <= est[m] / c <= 1.06, (m, est[m], c)


def test_every_row_states_its_estimate_status_and_release():
    assert all(r["estimate_status"] and r["release"] for r in POP)
    assert {r["estimate_status"] for r in POP if r["year"] == "2010"} == {"final intercensal"}


def test_year_status_parses_the_footnote_and_fails_without_it():
    note = ("Population estimates as of July 1 are final intercensal up to 2020, final "
            "postcensal for 2021, updated postcensal for 2022 to 2024, and preliminary "
            "postcensal for 2025.")
    s = fp.year_status(["unrelated", note])
    assert s[2001] == s[2020] == "final intercensal" and s[2023] == "updated postcensal"
    assert s[2025] == "preliminary postcensal"
    with pytest.raises(fp.FetchError):
        fp.year_status(["unrelated"])


def _row(uid, year, value):
    return {"DGUID": f"2021A0005{uid}", "REF_DATE": str(year), "VALUE": str(value), "STATUS": ""}


def test_extract_fails_on_a_missing_member_year_and_an_empty_value():
    by_uid = {"4800001": {"muni_id": "a", "region": "r", "role": "core"},
              "4800002": {"muni_id": "b", "region": "r", "role": "ring"}}
    status = {2001: "x", 2002: "x"}
    rows = [_row("4800001", 2001, 10), _row("4800001", 2002, 11), _row("4800002", 2001, 5),
            _row("4899999", 2002, 7), {**_row("4800001", 2002, 0), "DGUID": "2021A000248"}]
    with pytest.raises(fp.FetchError, match=r"\('b', 2002\)"):
        fp.extract(rows, by_uid, status, "d")
    assert len(fp.extract(rows + [_row("4800002", 2002, 6)], by_uid, status, "d")) == 4
    with pytest.raises(fp.FetchError, match="empty"):
        fp.extract(rows + [_row("4800002", 2002, "")], by_uid, status, "d")


# Each census reprints the previous count on the new boundaries. Adjusted minus
# original, per member, from the 2001-2021 census population tables (audit Q1,
# docs/FINDINGS_per_capita_boundaries_2026-10-03.md). Census boundaries are those
# of January 1 of the census year; each event's `change_list` names the 92F0009X
# list, and so the census window, that carries it.
CENSUS_ADJUSTMENT = {
    "2001-2006": {"stony_plain": 35, "parkland": -35, "calgary": 137, "airdrie": 25,
                  "chestermere": 442, "cochrane": 243, "foothills": -162, "high_river": 38,
                  "okotoks": 25, "rocky_view": -763},
    "2006-2011": {"st_albert": 45, "spruce_grove": 45, "leduc_county": -5, "parkland": -45,
                  "sturgeon": -55, "devon": 5, "calgary": 619, "chestermere": 359,
                  "foothills": -5, "okotoks": 5, "rocky_view": -998},
    "2011-2016": {"leduc_city": 25, "leduc_county": -47, "devon": 5, "airdrie": 707,
                  "foothills": -10, "high_river": 10, "rocky_view": -707},
    "2016-2021": {"edmonton": 542, "beaumont": 61, "fort_saskatchewan": 20, "spruce_grove": 42,
                  "strathcona": -20, "leduc_county": -603, "parkland": -42, "foothills": -150,
                  "high_river": 10, "okotoks": 135},
}
# Census adjustments that are StatCan corrections, not legal changes (92F0009X
# codes 8/9 and 10/11), so they are rightly absent from annexations.csv.
CORRECTIONS = {"2001-2006": {"chestermere": 442, "rocky_view": -442},
               "2011-2016": {"leduc_county": -17}}


def test_annexations_reproduce_the_census_adjusted_counts():
    for window, want in CENSUS_ADJUSTMENT.items():
        got = dict(CORRECTIONS.get(window, {}))
        for e in (e for e in EVENTS if e["change_list"] == window):
            for m, s in ((e["gainer"], 1), (e["loser"], -1)):
                if m in MEMBERS:
                    got[m] = got.get(m, 0) + s * int(e["people"])
        assert {m: v for m, v in got.items() if v} == want, window


def test_asof_differs_only_by_the_annexations():
    d = {(r["muni_id"], int(r["year"])): int(r["population_asof"]) - int(r["population"])
         for r in POP}
    assert d[("edmonton", 2018)] == -542 and d[("edmonton", 2019)] == 0
    assert d[("leduc_county", 2016)] == 603 and d[("leduc_county", 2017)] == 542
    assert d[("calgary", 2001)] == -756 and d[("calgary", 2007)] == 0
    assert all(v == 0 for (m, y), v in d.items() if y == 2021)
    assert d[("st_albert", 2022)] == 100 and d[("sturgeon", 2025)] == -100


def test_add_asof_moves_people_to_where_they_lived():
    rows = [{"muni_id": m, "year": y, "population": 1000}
            for m in ("a", "b") for y in (2019, 2020, 2022)]
    ev = [{"effective": "2020-07-01", "gainer": "a", "loser": "b", "people": "10"},
          {"effective": "2022-01-01", "gainer": "b", "loser": "outside", "people": "5"}]
    got = {(r["muni_id"], r["year"]): r["population_asof"] for r in fp.add_asof(rows, ev)}
    assert got == {("a", 2019): 990, ("a", 2020): 1000, ("a", 2022): 1000,
                   ("b", 2019): 1010, ("b", 2020): 1000, ("b", 2022): 1005}
    with pytest.raises(fp.FetchError, match="no member"):
        fp.add_asof(rows, [{"effective": "2010-01-01", "gainer": "x", "loser": "y",
                            "people": "1"}])
