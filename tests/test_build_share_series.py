"""build_share_series and fetch_equalized on synthetic inputs, plus the
UPE01548 reproduction check on the real processed file when it exists."""
import csv
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
import build_share_series as bss  # noqa: E402
import fetch_equalized as fe  # noqa: E402


def regions(tmp_path, rows):
    p = tmp_path / "regions.csv"
    with p.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["muni_id", "name", "region", "role", "eq_aliases",
                                          "member_basis", "notes"])
        w.writeheader()
        for r in rows:
            w.writerow({"name": r[0], "member_basis": "test", "notes": "",
                        "muni_id": r[0], "region": r[1], "role": r[2], "eq_aliases": r[3]})
    return bss.load_regions(p)


def long(year, name, **vals):
    return [{"report_year": str(year), "muni_name_raw": name, "class": c, "value": str(v),
             "page": "1"} for c, v in vals.items()]


REGION = [("core", "r", "core", "CORE CITY"),
          ("ring", "r", "ring", "RING COUNTY|RING NO. 31 M.D. OF")]


def test_shares_per_basis_and_old_alias(tmp_path):
    reg = regions(tmp_path, REGION)
    rows = (long(2014, "Core City", nr=60, nr_linear=10, nr_railway=0, me=0)
            + long(2014, "Ring No. 31, M.D. Of", nr=40, nr_linear=10, nr_railway=0, me=100))
    found, years = bss.member_values(rows, reg)
    s = {r["basis"]: r["core_share"] for r in bss.shares(found, years, reg)}
    assert s == {"nr": 0.6, "nr_linear": round(70 / 120, 6), "nr_all": round(70 / 220, 6)}


def test_old_class_set_uses_old_bases(tmp_path):
    reg = regions(tmp_path, REGION)
    rows = (long(2003, "Core City", nr_incl_railway=60, nr_linear=10, me=0, residential_incl_farmland=5)
            + long(2003, "Ring County", nr_incl_railway=40, nr_linear=10, me=100, residential_incl_farmland=5))
    found, years = bss.member_values(rows, reg)
    out = {r["basis"]: r for r in bss.shares(found, years, reg)}
    assert out["nr"]["core_share"] == 0.6 and "railway" in out["nr"]["basis_note"]
    assert out["nr_all"]["core_share"] == round(70 / 220, 6)
    assert "railway" not in out["nr_linear"]["basis_note"]


def test_mixed_class_sets_in_one_year_fail(tmp_path):
    reg = regions(tmp_path, REGION)
    rows = long(2003, "Core City", nr_incl_railway=1) + long(2003, "Ring County", nr=1)
    found, years = bss.member_values(rows, reg)
    with pytest.raises(bss.BuildError, match="mix"):
        bss.shares(found, years, reg)


def test_part_alias_is_summed_and_a_plain_duplicate_still_fails(tmp_path):
    reg = regions(tmp_path, [("core", "r", "core", "CORE CITY|+CORE CITY (PART II)"),
                             ("ring", "r", "ring", "RING COUNTY")])
    rows = (long(1998, "Core City", nr_incl_railway=60) + long(1998, "Core City (Part II)", nr_incl_railway=5)
            + long(1998, "Ring County", nr_incl_railway=35))
    found, _ = bss.member_values(rows, reg)
    assert found[(1998, "core")]["nr_incl_railway"] == 65
    twice = rows + [{**r, "page": "2"} for r in long(1998, "Core City (Part II)", nr_incl_railway=5)]
    with pytest.raises(bss.BuildError, match="matched twice"):
        bss.member_values(twice, reg)


def test_missing_member_fails(tmp_path):
    reg = regions(tmp_path, REGION)
    rows = long(2014, "Core City", nr=1) + long(2015, "Core City", nr=1) + long(2015, "Ring County", nr=1)
    with pytest.raises(bss.BuildError, match=r"\(2014, 'ring'\)"):
        bss.member_values(rows, reg)


def test_alias_matching_two_rows_fails(tmp_path):
    reg = regions(tmp_path, [("core", "r", "core", "CORE CITY"),
                             ("ring", "r", "ring", "RING COUNTY|RING")])
    rows = long(2014, "Core City", nr=1) + long(2014, "Ring County", nr=1) + long(2014, "Ring", nr=2)
    with pytest.raises(bss.BuildError, match="matched twice"):
        bss.member_values(rows, reg)


def test_alias_shared_by_two_members_fails(tmp_path):
    with pytest.raises(bss.BuildError, match="used by both"):
        regions(tmp_path, [("a", "r", "core", "X"), ("b", "r", "ring", "Y|X")])


def test_fetch_duplicate_year_and_vanished_year():
    pkg = {"resources": [{"name": "Provincial 2020 equalized assessment report "},
                         {"name": "Something else"},
                         {"name": "Provincial 2021 Equalized Assessment Report"}]}
    new = fe.PACKAGES["2368-657x"]
    assert sorted(fe.report_resources(pkg, new)) == [2020, 2021]
    old = {"resources": [{"name": "2008 equalized assessment report"}]}
    assert sorted(fe.report_resources(old, fe.PACKAGES["1844032"])) == [2008]
    with pytest.raises(fe.FetchError, match="2021"):
        fe.report_resources({"resources": [{"name": "2021 equalized assessment report"}]},
                            fe.PACKAGES["1844032"], fe.report_resources(pkg, new))
    with pytest.raises(fe.FetchError, match="two resources"):
        fe.report_resources({"resources": pkg["resources"] * 2}, new)
    with pytest.raises(fe.FetchError, match="no longer listed"):
        fe.check_no_year_vanished({2021: {}}, {"files": [{"report_year": 2020}, {"report_year": 2021}]})


SERIES = REPO / "data/processed/core_ring_share.csv"


def test_reproduces_upe01548():
    """City of Edmonton UPE01548 (2024-06-19, p. 5): Edmonton's share of the
    region's non-residential assessment fell from 72% (2008) to 60% (2022),
    13 EMRB members. Fits the NR + linear basis (docs/SCOPE_candidates.md §"Spike")."""
    with SERIES.open() as f:
        s = {(r["region"], int(r["taxation_year"]), r["basis"]): float(r["core_share"])
             for r in csv.DictReader(f)}
    assert abs(s[("edmonton", 2022, "nr_linear")] - 0.60) <= 0.01
    assert s[("edmonton", 2010, "nr_linear")] <= 0.72


def test_suspect_printed_values_are_kept_until_verified():
    """Airdrie NR = 0 (taxation 2016) and Sturgeon NR 648M (2000) stay as printed
    until FIR corroborates or refutes them (docs/DECISIONS.md, 2026-09-28). A
    correction is 1.9 / 2.4 pp; it must arrive with a DECISIONS row, not silently."""
    with SERIES.open() as f:
        s = {(r["region"], int(r["taxation_year"]), r["basis"]): float(r["core_share"])
             for r in csv.DictReader(f)}
    assert abs(s[("calgary", 2016, "nr")] - 0.9375) <= 0.0005
    assert abs(s[("edmonton", 2000, "nr")] - 0.7380) <= 0.0005
