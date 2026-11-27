"""Guards for src/build_tax_rates.py (Phase 2c, DECISIONS 2026-11-26)."""
import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
import build_tax_rates as btr  # noqa: E402

FIR_ROWS = list(csv.DictReader(open(REPO / "data/processed/fir_long.csv", newline="")))
REGIONS = list(csv.DictReader(open(REPO / "data/regions.csv", newline="")))
OUT = list(csv.DictReader(open(REPO / "data/processed/tax_rates.csv", newline="")))
YEARS = [y for y in range(btr.FIRST, btr.LAST + 1) if y not in btr.MISSING]


def test_committed_output_reproduces_from_fir_long():
    rows, folded = btr.build(FIR_ROWS, REGIONS)
    assert [{k: str(v) for k, v in r.items()} for r in rows] == OUT
    # The one absorbed code pooled at its member's rate (Entwistle, dissolved into Parkland).
    assert {(m, c, y) for m, c, y, _ in folded} == {("parkland", "0104", 2000)}


def test_every_member_side_and_region_has_every_year_and_class():
    have = {(r["level"], r["unit"], int(r["taxation_year"]), r["class"]) for r in OUT}
    units = [("member", r["muni_id"]) for r in REGIONS] + \
            [("side", "core"), ("side", "ring"), ("region", "region")]
    want = {(lvl, u, y, c) for lvl, u in units for y in YEARS for c in btr.CLASSES}
    assert {k for k in want if k[0] == "member"} <= have
    sides = {(r["region"], r["level"], r["unit"], int(r["taxation_year"]), r["class"])
             for r in OUT if r["level"] != "member"}
    assert len(sides) == 2 * 3 * len(YEARS) * len(btr.CLASSES)
    assert 2001 not in {int(r["taxation_year"]) for r in OUT}


def _pooled(val, region, unit, year, cls, basis):
    num = den = 0.0
    for r in REGIONS:
        if r["region"] != region or (unit != "region" and r["role"] != unit):
            continue
        old, new, eq_lines, tax_line = btr.CLASSES[cls]
        rate = val[(r["fir_code"], year, "MR_RATE", new)]
        base = (sum(btr.ea(val, r["fir_code"], year + 1, ln) or 0 for ln in eq_lines) if basis == "equalized"
                else val[(r["fir_code"], year, "MR_ASSESS", tax_line)])
        num, den = num + rate * base, den + base
    return num / den


def test_equalized_and_taxable_weights_agree_where_they_overlap():
    """The base switches from equalized (to 2024) to taxable (2025 on). In 2024, the
    one clean year where both exist, the two pooled rates agree within
    WEIGHT_SWITCH_TOL mills (max 0.126, Edmonton region NR). 2023 is not usable:
    FIR's 2023 MR(2) gives Strathcona a zero base in every class (DATA_ISSUES)."""
    val, _ = btr.index(FIR_ROWS)
    worst = 0.0
    for year in (2024,):
        for region in ("edmonton", "calgary"):
            for unit in ("core", "ring", "region"):
                for cls in btr.CLASSES:
                    gap = abs(_pooled(val, region, unit, year, cls, "equalized")
                              - _pooled(val, region, unit, year, cls, "taxable"))
                    worst = max(worst, gap)
    assert worst <= btr.WEIGHT_SWITCH_TOL, worst


def test_calgary_2001_ea_uses_the_residual_not_the_dropped_digit():
    """FIR's 2001 Calgary NR prints 1.62B (docs/DATA_ISSUES.md 2026-10-02). The
    taxation-2000 base must be on the PDF's scale: within 3% of the share series'
    Calgary nr_linear value for report 2001, which comes from the PDF."""
    pdf = next(float(r["core_value"]) for r in csv.DictReader(open(REPO / "data/processed/core_ring_share.csv"))
               if (r["region"], r["report_year"], r["basis"]) == ("calgary", "2001", "nr_linear"))
    w = next(float(r["weight"]) for r in OUT if (r["level"], r["unit"], r["taxation_year"], r["class"])
             == ("member", "calgary", "2000", "nr"))
    assert abs(w / pdf - 1) < 0.03, (w, pdf)


def test_weight_basis_switches_after_the_last_fir_ea_year():
    basis = {int(r["taxation_year"]): r["weight_basis"] for r in OUT}
    assert {y for y, b in basis.items() if b == "taxable"} == {2025, 2026}
    assert btr.EQ_LAST == 2024


def test_foothills_2024_uses_the_replacement_rates_not_schedule_mr():
    # FIR MR's 2024 Foothills rates imply a levy 1.6x (NR) / 2.0x (residential) what
    # K(1) says was levied (docs/DATA_ISSUES.md 2026-11-26).
    got = {r["class"]: float(r["mill_rate"]) for r in OUT
           if r["unit"] == "foothills" and r["taxation_year"] == "2024"}
    dash = next(float(r["nr_mill_rate"]) for r in csv.DictReader(
        open(REPO / "data/processed/dashboard_nr_rates.csv", newline=""))
        if r["muni_id"] == "foothills" and r["year"] == "2024")
    assert abs(got["nr"] - dash) < 5e-4
    mr = {(int(r["fir_year"]), r["line_code"]): float(r["value"]) for r in FIR_ROWS
          if r["fir_code"] == "0111" and r["schedule"] == "MR_RATE" and r["value"]}
    # Residential sits with its neighbours, not at MR's doubled 7.23 mills.
    lo, hi = sorted((mr[(2023, "10030")], mr[(2025, "10030")]))
    assert lo * 0.9 < got["residential"] < hi * 1.1, (got, lo, hi)
    assert mr[(2024, "10030")] > 2 * hi * 0.9  # MR still wrong upstream; drop the fix if not
    notes = [r for r in OUT if "Foothills 2024 rate replaced" in r["basis_note"]]
    assert {(r["unit"], r["class"]) for r in notes} == {
        (u, c) for u in ("foothills", "ring", "region") for c in btr.CLASSES}
    assert all(r["region"] == "calgary" and r["taxation_year"] == "2024" for r in notes)
