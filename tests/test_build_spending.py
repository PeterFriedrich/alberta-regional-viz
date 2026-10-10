"""build_spending: Phase 2b gross operating cost per capita by function, and the
same net of user charges (SPEC_phase1.md §"Phase 2b basis", decided 2026-10-02).
The real-data tests read the committed data/processed/spending_per_capita.csv
and recompute from the committed fir_long.csv and population.csv without
calling the module."""
import csv
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
import build_spending as bs  # noqa: E402

OUT = list(csv.DictReader((REPO / "data/processed/spending_per_capita.csv").open()))
ROW = {(r["region"], r["level"], r["unit"], r["function"], int(r["year"])): r for r in OUT}
FIR = list(csv.DictReader((REPO / "data/processed/fir_long.csv").open()))
POP = list(csv.DictReader((REPO / "data/processed/population.csv").open()))
CODES = {"police": ("01210", "02250"), "transit": ("01310", "02350"),
         "fcss": ("01400", "02440"), "housing": ("01480", "02520")}


def recompute():
    """{(muni, year, function): (gross, user charges)} straight from fir_long."""
    v = defaultdict(float)
    for r in FIR:
        v[(r["muni_id"], int(r["fir_year"]), r["schedule"], r["line_code"])] += float(r["value"] or 0)
    out = {}
    for m, y in {(m, y) for m, y, _, _ in v}:
        for fn, (c, e) in CODES.items():
            g = v[(m, y, "C_OP", c)] if y <= 2008 else v[(m, y, "C", c)] - v[(m, y, "E_AMORT", e)]
            out[(m, y, fn)] = (g, v[(m, y, "E_UC", e)])
    return out


def test_police_exclusions_pinned():
    assert bs.POLICE_EXCLUDED == {"foothills", "parkland", "rocky_view", "sturgeon"}
    assert bs.POLICE_ZERO_YEARS == {(2022, "cochrane"), (2021, "devon")}


def test_classification_unstable_series_are_not_built():
    """docs/FINDINGS_spending_jumps_2026-10-10.md, option A (Peter, 2026-10-10)."""
    assert bs.NOT_COMPARABLE == {("fcss", "calgary"): None, ("housing", "calgary"): None,
                                 ("fcss", "edmonton"): 2007}
    built = {(r["region"], r["unit"], r["function"]): set() for r in OUT}
    for r in OUT:
        built[(r["region"], r["unit"], r["function"])].add(int(r["year"]))
    for unit in ("calgary", "core"):
        assert ("calgary", unit, "fcss") not in built and ("calgary", unit, "housing") not in built
        assert min(built[("edmonton", "edmonton" if unit == "calgary" else "core", "fcss")]) == 2007
    # The ring and the other functions keep every year.
    assert min(built[("calgary", "ring", "fcss")]) == min(built[("edmonton", "ring", "fcss")]) == 2001
    assert min(built[("calgary", "ring", "housing")]) == 2009
    assert min(built[("calgary", "core", "police")]) == 2001
    # The Homeward Trust transfer is captioned where Edmonton is counted, and only there.
    noted = {(r["unit"], int(r["year"])) for r in OUT if "Homeward Trust" in r["basis_note"]}
    assert noted == {("edmonton", 2022), ("core", 2022)}


def test_values_pinned_against_the_spec_table():
    """SPEC_phase1.md §"Phase 2b basis": Edmonton police 243.4M (2008 operating),
    249.9M (2009 expense - amortization)."""
    assert ROW[("edmonton", "member", "edmonton", "police", 2008)]["gross"] == "243442000"
    assert ROW[("edmonton", "member", "edmonton", "police", 2009)]["gross"] == "249897000"


def test_every_row_matches_an_independent_recompute():
    v = recompute()
    p = {(r["muni_id"], int(r["year"])): int(r["population_asof"]) for r in POP}
    side = defaultdict(set)
    for r in POP:
        side[(r["region"], r["role"])].add(r["muni_id"])
    for r in OUT:
        y, fn = int(r["year"]), r["function"]
        munis = {r["unit"]} if r["level"] == "member" else side[(r["region"], r["unit"])]
        out = {m for m in munis if fn == "police" and (m in bs.POLICE_EXCLUDED
                                                      or (y, m) in bs.POLICE_ZERO_YEARS)}
        kept = munis - out
        g = sum(v[(m, y, fn)][0] for m in kept)
        uc = sum(v[(m, y, fn)][1] for m in kept)
        pp = sum(p[(m, y)] for m in kept)
        assert set(filter(None, r["excluded"].split("|"))) == out, r
        assert (int(r["gross"]), int(r["user_charges"]), int(r["net"])) == (round(g), round(uc), round(g - uc)), r
        assert int(r["population"]) == pp, r
        if pp:
            assert float(r["gross_per_capita"]) == round(g / pp, 2), r
            assert float(r["net_per_capita"]) == round((g - uc) / pp, 2), r
        else:
            assert r["gross_per_capita"] == r["net_per_capita"] == "", r


def test_shape_and_basis():
    members = {r["muni_id"] for r in csv.DictReader((REPO / "data/regions.csv").open())}
    years = {int(r["year"]) for r in OUT}
    assert years == set(range(2001, max(years) + 1)) and max(years) >= 2025
    assert {r["unit"] for r in OUT if r["level"] == "member"} == members
    # Less the NOT_COMPARABLE series, each on its member row and its core row.
    dropped = 2 * (len(years) + len([y for y in years if y >= 2009]) + (2007 - 2001))
    assert len(OUT) == (len(members) + 4) * (3 * len(years) + len([y for y in years if y >= 2009])) - dropped
    assert min(int(r["year"]) for r in OUT if r["function"] == "housing") == 2009
    assert all(r["basis_note"].startswith("nominal dollars; gross operating cost") for r in OUT)
    assert ROW[("edmonton", "side", "ring", "police", 2015)]["excluded"] == "parkland|sturgeon"


# 2009 annual reports restate 2008 on the accrual basis: one year on both bases.
# (city, function): (2009 statement, 2008 restated), $K, both excluding amortization.
# Edmonton's statement includes amortization in each function, so its 2008 police
# figure is net of the 2009 FIR amortization as an estimate (2010's is within 0.5%).
# Sources: /home/opc/research/alberta-regional-viz/accrual_switch_overlap_2026-10-02.md
RESTATED = {("edmonton", "police"): (258_340 - 8_443, 245_938 - 8_443),
            ("calgary", "police"): (316_025, 285_936),
            ("calgary", "transit"): (295_252, 283_688),
            ("calgary", "fcss"): (49_535, 50_641),
            ("edmonton", "housing"): (33_829 - 669, 27_769 - 669),
            ("calgary", "housing"): (105_528, 75_153)}


def test_the_2009_accrual_switch_is_measured_on_restated_2008():
    """SPEC_phase1.md §"The 2009 accrual switch, measured": where a city's 2009
    statement line matches our 2009 gross (within 1%, so it is the same scope), its
    restated 2008 figure against our 2008 cash Operating figure is the basis step.
    Police, transit and FCSS step by at most 3% (largest: Edmonton police,
    cash 2.5% above accrual) and run through 2009. Housing does
    not match in scope (Calgary 2009: 105.5 vs 123.6 $M) or steps far more
    (Edmonton +45%), so it starts in 2009. A year-on-year statistical step test was
    tried first and rejected: 2009 sits in the 2007-09 boom (median police growth
    16% in 2008, 3% in 2010), so it fails police on real data and has no power for
    housing."""
    v = recompute()
    for (m, fn), (s09, s08) in RESTATED.items():
        g09, g08 = v[(m, 2009, fn)][0] / 1000, v[(m, 2008, fn)][0] / 1000
        same_scope = abs(g09 / s09 - 1) <= 0.01
        step = g08 / s08 - 1  # >0: the cash basis ran higher than accrual
        if fn == "housing":
            assert not same_scope or abs(step) > 0.25, (m, fn, g09, s09, step)
        else:
            assert same_scope and abs(step) <= 0.03, (m, fn, g09, s09, step)


def test_transit_and_fcss_show_no_common_step_at_2009():
    """Statistical backstop for the members the annual reports don't cover: per
    function, the median member's log change into 2009 less the mean of its 2008
    and 2010 changes (a level shift spikes it; the boom trend doesn't), and the
    same for the all-member total, must sit inside the middle three quarters of
    other years'. Resolution, measured 2026-10-02: a 2009+ shift of ±10% fails
    transit, ±5% fails FCSS. Police is not tested this way: it fails on real data
    (all-member total 3.8% under trend against a 3.0% bar), which the restated
    figures put down to the year, not the basis (Edmonton cash 2.5% above accrual, Calgary 1.3% below)."""
    v = recompute()
    munis = sorted({r["muni_id"] for r in POP})
    for fn in ("transit", "fcss"):
        g = {(m, y): v[(m, y, fn)][0] for m in munis for y in range(2001, 2026)}

        def s(m, y):
            return math.log(g[(m, y)] / g[(m, y - 1)])

        def total(y):
            return math.log(sum(g[(m, y)] for m in munis) / sum(g[(m, y - 1)] for m in munis))

        def kinks(y):
            each = [s(m, y) - (s(m, y - 1) + s(m, y + 1)) / 2 for m in munis
                    if all(g[(m, x)] > 0 for x in range(y - 2, y + 2))]
            return (abs(statistics.median(each)),
                    abs(total(y) - (total(y - 1) + total(y + 1)) / 2))
        others = [kinks(y) for y in range(2003, 2025) if y not in (2008, 2009, 2010)]
        med_p75 = sorted(k[0] for k in others)[int(0.75 * len(others))]
        agg_p75 = sorted(k[1] for k in others)[int(0.75 * len(others))]
        med09, agg09 = kinks(2009)
        assert med09 <= med_p75 and agg09 <= agg_p75, (fn, med09, med_p75, agg09, agg_p75)


def test_negative_gross_is_kept_and_named():
    r = ROW[("edmonton", "member", "morinville", "transit", 2021)]
    assert int(r["gross"]) == -11730 and "negative gross kept as printed" in r["basis_note"]
    assert "morinville -11,730" in ROW[("edmonton", "side", "ring", "transit", 2021)]["basis_note"]


def fir(y, m, sch, line, value):
    return {"fir_year": str(y), "muni_id": m, "schedule": sch, "line_code": line, "value": value}


def test_unexplained_zero_police_fails():
    pop = [{"year": "2005", "muni_id": "a", "region": "r", "role": "ring", "population": "10", "population_asof": "10"}]
    rows = [fir(2005, "a", "C_OP", "01310", "5")]
    with pytest.raises(bs.BuildError, match="no police spending"):
        bs.build(rows, pop)
    rows.append(fir(2005, "a", "C_OP", "01210", "20"))
    out = {r["function"]: r for r in bs.build(rows, pop) if r["level"] == "member"}
    assert out["police"]["gross_per_capita"] == 2.0 and out["transit"]["gross_per_capita"] == 0.5


def test_population_without_spending_fails():
    pop = [{"year": "2001", "muni_id": "a", "region": "r", "role": "core", "population": "10", "population_asof": "10"}]
    with pytest.raises(bs.BuildError, match="no spending"):
        bs.build([], pop)
