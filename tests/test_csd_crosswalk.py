"""data/csd_crosswalk.csv: StatCan CSD codes per member per census year,
hand-built from the SGC lists and concordances (sources in data/DATA.md)."""
import csv
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CENSUS_YEARS = {1996, 2001, 2006, 2011, 2016, 2021}
ROWS = list(csv.DictReader((REPO / "data/csd_crosswalk.csv").open()))
MEMBERS = {r["muni_id"] for r in csv.DictReader((REPO / "data/regions.csv").open())}

# Dissolved municipalities merged into a member (decision 8), with the last
# census they appear in as their own CSD.
ABSORBED = {("foothills", "4806004", "Blackie"): 1996,
            ("parkland", "4811036", "Entwistle"): 1996,
            ("leduc_county", "4811014", "New Sarepta"): 2006,
            ("parkland", "4811045", "Wabamun"): 2016}


def test_every_member_has_exactly_one_member_row_per_census():
    got = Counter((r["muni_id"], int(r["census_year"])) for r in ROWS if r["relation"] == "member")
    assert set(got) == {(m, y) for m in MEMBERS for y in CENSUS_YEARS}
    assert set(got.values()) == {1}


def test_member_codes_are_alberta_and_constant_1996_to_2021():
    codes = {}
    for r in ROWS:
        assert len(r["csd_uid"]) == 7 and r["csd_uid"].startswith("48"), r
        if r["relation"] == "member":
            codes.setdefault(r["muni_id"], set()).add(r["csd_uid"])
    assert all(len(c) == 1 for c in codes.values()), codes
    assert len({next(iter(c)) for c in codes.values()}) == len(MEMBERS)


def test_no_code_maps_to_two_members_in_a_census():
    seen = Counter((r["census_year"], r["csd_uid"]) for r in ROWS)
    assert max(seen.values()) == 1


def test_absorbed_rows_are_exactly_the_known_dissolutions_until_they_dissolve():
    got = {}
    for r in ROWS:
        if r["relation"] == "absorbed":
            got.setdefault((r["muni_id"], r["csd_uid"], r["csd_name"]), set()).add(int(r["census_year"]))
    assert got == {k: {y for y in CENSUS_YEARS if y <= last} for k, last in ABSORBED.items()}
    assert {r["relation"] for r in ROWS} == {"member", "absorbed"}


def test_name_changes_are_noted():
    by = {(r["muni_id"], int(r["census_year"])): r for r in ROWS if r["relation"] == "member"}
    for (m, y), r in by.items():
        prev = by.get((m, y - 5))
        if prev and prev["csd_name"] != r["csd_name"]:
            assert "renamed" in r["note"], r
