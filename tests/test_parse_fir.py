"""parse_fir: the reader on synthetic rows, and the findings its committed output
(data/processed/fir_long.csv) supports: the year mapping to the equalized
reports, FIR's own row arithmetic, the four kept-as-printed anomalies, and the
transfers total across the 2023 reclassification."""
import csv
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
import parse_fir as pf  # noqa: E402

EA_PARTS = ("08265", "08270", "08275", "08280", "08285", "08290", "08295")


def load_fir():
    """{(year, muni_id, line): value}, an absorbed municipality's rows summed
    into its member (decision 8)."""
    out = {}
    for r in csv.DictReader(open(REPO / "data/processed/fir_long.csv", newline="")):
        if r["value"]:
            k = (int(r["fir_year"]), r["muni_id"], r["line_code"])
            out[k] = out.get(k, 0) + float(r["value"])
    return out


FIR = load_fir()
REGIONS = list(csv.DictReader(open(REPO / "data/regions.csv", newline="")))


# --- reader -----------------------------------------------------------------

def test_read_sheet_finds_columns_by_code_not_position():
    rows = [("Schedule D", "Financial Activities by Type/Object - Total"),
            ("YEAR", "STATUS", "CODE", "MUNICIPALITY", "Other", "Prov. Conditional", "Prov. Unconditional"),
            (None, None, None, "(* Includes AB & SK)", "01970", "01920", "01910"),
            ("2005", "City", "0003", "AIRDRIE", 5, 20, 10)]
    (year, code, name, cols), = pf.read_sheet(rows, 2005, "D")
    assert (year, code, name) == ("2005", "0003", "AIRDRIE")
    assert cols == {"01920": ("Prov. Conditional", 20.0), "01910": ("Prov. Unconditional", 10.0)}


def test_read_sheet_maps_2001_headers_by_name_and_keeps_blanks_blank():
    rows = [("YEAR", "STATUS", "CODE", "MUNICIPALITY", "GRAND TOTAL", "Non Residential Subtotal"),
            (2001.0, "City", "0046", "CALGARY", 9.0, None)]
    (_, _, _, cols), = pf.read_sheet(rows, 2001, "EA")
    assert cols == {"08260": ("GRAND TOTAL", 9.0), "08275": ("Non Residential Subtotal", None)}


def test_schedule_titles_and_supplements():
    assert pf.SCHEDULES["D"].search("<< Index | Schedule D | Financial Activities by Type/Object - TOTAL")
    assert not pf.SCHEDULES["D"].search("Schedule DE | Financial Activities by Type/Object - Total")
    assert not pf.SCHEDULES["POPL"].search("Schedule POPL | Population of Alberta - Total Dwell Units")
    assert pf.SUPPLEMENT.search("2004/2004-D-Total-G.xlsx")
    assert not pf.SUPPLEMENT.search("2004/2004-D-Total.xlsx")


def test_fir_name_variants_match_aliases():
    assert pf.norm("FOOTHILLS NO. 31, M.D. OF") == pf.norm("FOOTHILLS NO. 31 M.D. OF")


# --- committed output -------------------------------------------------------

def test_every_member_has_every_required_line():
    rows = csv.DictReader(open(REPO / "data/processed/fir_long.csv", newline=""))
    pf.check_complete({(int(r["fir_year"]), r["fir_code"], r["schedule"], r["line_code"]): r
                       for r in rows}, REGIONS)


def test_fir_year_is_the_equalized_report_year():
    """FIR financial year Y carries the equalized assessment of REPORT year Y
    (taxation year Y-1). Checked on whole-region nr_all totals against the
    committed Phase 1 output: median gap 0.5% on that mapping, >= 3.6% one
    year either side."""
    members = defaultdict(list)
    for r in REGIONS:
        members[r["region"]].append(r["muni_id"])
    rows = [r for r in csv.DictReader(open(REPO / "data/processed/core_ring_share.csv"))
            if r["basis"] == "nr_all"]

    def gaps(offset):
        out = []
        for r in rows:
            y = int(r["report_year"]) + offset
            if (y, members[r["region"]][0], "08275") not in FIR:
                continue
            fir = sum(FIR.get((y, m, c), 0) for m in members[r["region"]]
                      for c in ("08265", "08270", "08275", "08290", "08295"))
            out.append(abs(fir / (float(r["core_value"]) + float(r["ring_value"])) - 1))
        return statistics.median(out)

    assert gaps(0) < 0.01
    assert gaps(-1) > 0.03 and gaps(1) > 0.03


def test_fir_ea_rows_add_up_except_calgary_2001():
    """FIR's 2001 file (the legacy EQASSMT layout) prints Calgary's NR as 1.62B
    against ~16B either side; its components fall 14.6B short of its own total.
    Every other member-year's components sum to the printed total."""
    bad = set()
    for (y, m, line), total in FIR.items():
        if line == "08260":
            parts = sum(FIR.get((y, m, c), 0) for c in EA_PARTS)
            if abs(parts - total) > 1000:
                bad.add((y, m))
    assert bad == {(2001, "calgary")}


def test_fir_resolves_the_four_kept_as_printed_anomalies():
    """DECISIONS 2026-09-28: each printed value is checked against FIR. The
    printed values (report years) were re-read from the PDF text 2026-10-02.
    FIR's value sits within 25% of the midpoint of its neighbours and its row
    adds up; the printed value is >= 40% off that midpoint."""
    printed = {(2017, "airdrie", "08275"): 0,
               (2001, "sturgeon", "08275"): 647_603_090,
               (1999, "devon", "08275"): 99_815_242,
               (2003, "calgary", "08265"): 1_860_234_990}
    for (y, m, line), value in printed.items():
        mid = (FIR[(y - 1, m, line)] + FIR[(y + 1, m, line)]) / 2
        assert abs(FIR[(y, m, line)] / mid - 1) < 0.25, (y, m)
        assert abs(value / mid - 1) >= 0.4, (y, m)
        assert abs(sum(FIR.get((y, m, c), 0) for c in EA_PARTS) - FIR[(y, m, "08260")]) <= 1000


def test_transfers_total_shows_no_common_step_at_the_2023_reclassification():
    """Decision 9 as amended 2026-10-01: total provincial transfers = 01910+01920
    through 2022, 01912+01922 from 2023. Single members are too lumpy to test one
    by one (Leduc City's capital transfers go 8.6M -> 45.9M in 2023, then 54.8M,
    25.7M: real grants, not a relabelling), so the test is common-mode: the
    median member's log change into 2023, and the all-member total's, must sit
    inside the middle three quarters of the other years' absolute changes.
    Resolution, measured 2026-10-02: scaling every 2023+ total by 1.3 fails it,
    by 0.75 does not — a smaller common shift is inside year-to-year noise."""
    totals = defaultdict(float)
    for (y, m, line), v in FIR.items():
        if line in pf.TRANSFERS_OLD | pf.TRANSFERS_NEW:
            totals[(y, m)] += v
    munis = sorted({r["muni_id"] for r in REGIONS})

    def steps(y):
        each = [math.log(totals[(y, m)] / totals[(y - 1, m)]) for m in munis
                if totals[(y, m)] > 0 and totals[(y - 1, m)] > 0]
        agg = math.log(sum(totals[(y, m)] for m in munis) / sum(totals[(y - 1, m)] for m in munis))
        return abs(statistics.median(each)), abs(agg)

    others = [steps(y) for y in range(1995, 2026) if y != 2023]
    med_p75 = sorted(s[0] for s in others)[int(0.75 * len(others))]
    agg_p75 = sorted(s[1] for s in others)[int(0.75 * len(others))]
    med23, agg23 = steps(2023)
    assert med23 <= med_p75 and agg23 <= agg_p75


def test_absorbed_municipalities_are_read_under_their_member():
    """Decision 8: the four villages are summed into the member that absorbed
    them. Their transfers (Schedule D) run to the last year they filed."""
    last_d = defaultdict(int)
    for r in csv.DictReader(open(REPO / "data/processed/fir_long.csv", newline="")):
        if r["schedule"] == "D" and r["fir_code"] in pf.absorbed(REGIONS):
            last_d[(r["fir_code"], r["muni_id"])] = max(last_d[(r["fir_code"], r["muni_id"])],
                                                        int(r["fir_year"]))
    assert dict(last_d) == {("0032", "foothills"): 1997, ("0104", "parkland"): 2000,
                            ("0234", "leduc_county"): 2009, ("0364", "parkland"): 2020}


def test_an_absorbed_municipality_with_a_gap_fails():
    regions = [{"muni_id": "m", "fir_code": "0001", "absorbed_fir_codes": "0002"}]
    out = {}
    for y in range(pf.FIRST, pf.TAX_RATES_YEAR + 1):  # Schedule MR runs a year past LAST
        for sch in pf.SCHEDULES:
            if y > pf.LAST and sch not in pf.MR_SCHEDULES:
                continue
            for line in pf.wanted(sch, y):
                out[(y, "0001", sch, line)] = {"value": 1.0}
                if y <= 2000:
                    out[(y, "0002", sch, line)] = {"value": 1.0}
    pf.check_complete(out, regions)
    del out[(1996, "0002", "D", "01910")]
    with pytest.raises(pf.ParseError, match=r"m<0002>"):
        pf.check_complete(out, regions)


# --- Schedule MR (Phase 2c) ---------------------------------------------------

def _mr_own():
    """{(muni_id, year, schedule, line): value} for each member's OWN fir_code, and
    {(muni_id, year): [nr rates of every code read under the member]}."""
    own_code = {r["muni_id"]: r["fir_code"] for r in REGIONS}
    own, nr_all = {}, defaultdict(list)
    for r in csv.DictReader(open(REPO / "data/processed/fir_long.csv", newline="")):
        if not r["schedule"].startswith("MR") or r["value"] == "":
            continue
        y, v = int(r["fir_year"]), float(r["value"])
        if r["fir_code"] == own_code[r["muni_id"]]:
            own[(r["muni_id"], y, r["schedule"], r["line_code"])] = v
        if (r["schedule"], r["line_code"]) in (("MR_NR", "05800"), ("MR_RATE", "10034")):
            nr_all[(r["muni_id"], y)].append(v)
    return own, nr_all


def _nr_rate(own, muni, y):
    return own.get((muni, y, "MR_NR", "05800"), own.get((muni, y, "MR_RATE", "10034")))


def test_mr_schedule_titles_and_years():
    assert pf.SCHEDULES["MR_NR"].search("Schedule MR | Schedule MR | Tax Rate Data - Non-Residential")
    assert pf.SCHEDULES["MR_RES"].search("MR Residential or Farmland | Schedule MR | Tax Rate Data - Residential or Farmland")
    assert pf.SCHEDULES["MR_RATE"].search("<< Index | Schedule MR | Tax Rate Data - MILL RATE")
    # 2001's folder holds 2002's rows in per-dollar units under another title: never read.
    assert not any(p.search("Mr_col2 | Schedule Mr | Tax Rate Information - Non-Residential")
                   for s, p in pf.SCHEDULES.items() if s in pf.MR_SCHEDULES)
    years = defaultdict(set)
    for r in csv.DictReader(open(REPO / "data/processed/fir_long.csv", newline="")):
        if r["schedule"].startswith("MR"):
            years[r["schedule"]].add(int(r["fir_year"]))
    old = set(range(1998, 2009)) - {2001}
    assert years == {"MR_NR": old, "MR_RES": old, "MR_RATE": set(range(2009, 2027)),
                     "MR_LEVY": set(range(2017, 2027)), "MR_ASSESS": set(range(2023, 2027))}


def test_mr_levy_is_rate_times_assessment():
    """MR(1) = MR(2) x MR(3) / 1000 for every member, year and class with an
    assessment, 2023 on (edmonton-tax-viz found the same for Edmonton)."""
    own, _ = _mr_own()
    checked = 0
    for (muni, y, sch, line), assess in own.items():
        if sch != "MR_ASSESS" or assess <= 0 or line not in ("10030", "10034", "10038"):
            continue
        levy, rate = own.get((muni, y, "MR_LEVY", line)), own.get((muni, y, "MR_RATE", line))
        assert levy is not None and rate is not None, (muni, y, line)
        assert abs(levy - assess * rate / 1000) <= 1e-4 * levy + 1, (muni, y, line, levy, assess, rate)
        checked += 1
    assert checked >= 21 * 4 * 2


# Dashboard rows for a CSD that absorbed municipalities are the SUM of their mill
# rates (data/DATA.md §"Regional Dashboard"). Measured 2026-11-26.
ABSORBED_SUM = {("leduc_county", y) for y in range(1998, 2011) if y != 2001} | \
               {("parkland", y) for y in range(1998, 2021) if y != 2001}
# FIR's levy/assessment reproduce 13.74, but the residential levy doubles that year
# and falls back in 2025; the dashboard's 8.86 fits the trend. Needs the 2024 bylaw.
UNRESOLVED = {("foothills", 2024)}


def test_fir_nr_rate_matches_the_regional_dashboard():
    """The independent check on Schedule MR: every member-year agrees with the
    Regional Dashboard, except the explained and the logged sets, which must still
    disagree (a fix upstream should be noticed)."""
    own, nr_all = _mr_own()
    dash = {(r["muni_id"], int(r["year"])): float(r["nr_mill_rate"])
            for r in csv.DictReader(open(REPO / "data/processed/dashboard_nr_rates.csv", newline=""))}
    summed, unresolved, fir_missing = set(), set(), set()
    for (muni, y), d in dash.items():
        fir = _nr_rate(own, muni, y)
        if fir is None:
            fir_missing.add(y)
        elif abs(fir - d) > 5e-4:
            if len(nr_all[(muni, y)]) > 1 and abs(sum(nr_all[(muni, y)]) - d) <= 5e-4:
                summed.add((muni, y))
            else:
                unresolved.add((muni, y))
    assert fir_missing == {2001}
    assert summed == ABSORBED_SUM
    assert unresolved == UNRESOLVED
