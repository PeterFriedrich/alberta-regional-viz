"""Population (decision 2026-10-02): StatCan 17-10-0155 July 1 estimates,
2021 boundaries, 2001-2025, one row per member per year. The real-data tests
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
