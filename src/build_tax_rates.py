"""Core-vs-ring municipal property tax rates (Phase 2c): each member's own mill
rate by class, and pooled rates for the core, the ring and the whole region.

Rates are FIR Schedule MR's municipal general rates (education excluded,
DECISIONS 2026-11-26). A pooled rate is sum(rate x base) / sum(base), the single
rate that raises the same levy on the combined base. The base is FIR's equalized
assessment for the same taxation year (report year T + 1, docs/SPEC_phase1.md
§"Year semantics") through taxation 2024, the last FIR EA year; from 2025 it is
MR's taxable assessment for that year, and `weight_basis` says which. Where both
exist (2024) the two agree within WEIGHT_SWITCH_TOL mills (measured 2026-11-26),
so the switch can step a pooled rate by up to about 0.13 mills.

A municipality absorbed into a member (decision 8) is pooled with its own rate
and base for the years it reported; the member row is the member's own code. An
absorbed code's all-zero rate row is a placeholder and is skipped. An absorbed
code with a rate but no base in the next report (its base is already reported
under the member, e.g. Entwistle 2000) is pooled at the member's rate and logged.
FIR has no Schedule MR for 2001, so 2001 is absent and logged. A rate with no
base row fails the build.

Usage:
    python src/build_tax_rates.py [--fir data/processed/fir_long.csv] [--regions data/regions.csv]
                                  [--out data/processed/tax_rates.csv]
"""
import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jsonlog import event, get_logger  # noqa: E402

log = get_logger("build_tax_rates")

REPO = Path(__file__).resolve().parent.parent
FIRST, LAST = 1998, 2026
MISSING = {2001}            # FIR has no Schedule MR for 2001 (data/DATA.md §"Schedule MR")
EQ_LAST = 2024              # last taxation year with an FIR equalized base (report 2025)
OLD_LAST = 2008             # 1998-2008: MR_NR / MR_RES item 05800
# Equalized vs taxable pooled rate in 2024, the one clean overlap year (FIR's 2023
# MR(2) gives Strathcona a zero base): max 0.126 mills, Edmonton region NR.
WEIGHT_SWITCH_TOL = 0.15

# FIR EA cells that don't add up to their own GRAND TOTAL (docs/DATA_ISSUES.md
# 2026-10-02; tests/test_parse_fir.py::test_fir_ea_rows_add_up_except_calgary_2001).
# The base is taken as the total minus the row's other components: Calgary's 2001
# NR prints 1.62B, the residual is 16.23B, and the 2001 PDF report prints 16,560M.
EA_RESIDUAL = {("0046", 2001, "08275")}
EA_PARTS = ("08265", "08270", "08275", "08280", "08285", "08290", "08295")

# FIR MR rates that its own Schedule K(1) (property taxes actually levied) contradicts
# (docs/DATA_ISSUES.md 2026-11-26; Peter's decision 2026-11-27). Foothills 2024: MR's
# levy is 1.56x (NR) and 1.99x (residential) K(1)'s, while 2023 and 2025 agree within
# 0.5%. NR takes the Regional Dashboard's rate (it equals MR's in every other
# member-year); residential takes K(1) levy / MR assessment (no second rate source;
# that ratio is within 0.1% of MR's rate in 2023 and 2025).
K1_FOOTHILLS_2024_RES = 32291692       # FIR 2024 K(1) Residential Land and Improvements
RATE_FIX = {
    ("0111", 2024, "nr"): (8.85966, "Regional Dashboard rate"),
    ("0111", 2024, "residential"): (None, "FIR K(1) levy / MR assessment"),
}
FIX_NOTE = "; Foothills 2024 rate replaced ({}): FIR Schedule MR overstates it"

# class -> (old rate (schedule, line), new rate line, equalized base lines, taxable base line)
CLASSES = {
    "nr": (("MR_NR", "05800"), "10034", ("08275", "08265", "08290"), "10034"),
    "residential": (("MR_RES", "05800"), "10030", ("08280",), "10030"),
}
# No M&E class: MR's M&E rate is blank for every member 2009-2022, and from 2023
# Calgary prints an M&E rate on a zero taxable M&E base (DECISIONS 2026-11-26).
BASIS_NOTE = ("municipal general rate only (education excluded); mills; levy at bylaw time; "
              "2025 board membership applied to all years")
FIELDS = ["region", "level", "unit", "role", "taxation_year", "class", "mill_rate", "weight",
          "weight_basis", "n_codes", "basis_note"]


class BuildError(Exception):
    pass


def index(fir_rows):
    """{(fir_code, year, schedule, line): value} and {fir_code: muni_id}."""
    val, muni = {}, {}
    for r in fir_rows:
        muni[r["fir_code"]] = r["muni_id"]
        if r["value"] != "":
            val[(r["fir_code"], int(r["fir_year"]), r["schedule"], r["line_code"])] = float(r["value"])
    return val, muni


def ea(val, code, report_year, line):
    if (code, report_year, line) in EA_RESIDUAL:
        total = val[(code, report_year, "EA", "08260")]
        return total - sum(val.get((code, report_year, "EA", c), 0) for c in EA_PARTS if c != line)
    return val.get((code, report_year, "EA", line))


def rate_and_base(val, code, year, cls):
    """(rate, base, basis) for one FIR code, or None when the code has no rate row."""
    old, new, eq_lines, tax_line = CLASSES[cls]
    if year <= OLD_LAST:
        rate = val.get((code, year, *old)) if old else None
    else:
        rate = val.get((code, year, "MR_RATE", new))
    if (code, year, cls) in RATE_FIX:
        rate = RATE_FIX[(code, year, cls)][0]
        if rate is None:
            rate = K1_FOOTHILLS_2024_RES / val[(code, year, "MR_ASSESS", tax_line)] * 1000
    if rate is None:
        return None
    if year <= EQ_LAST:
        parts = [ea(val, code, year + 1, line) for line in eq_lines]
        base = None if all(p is None for p in parts) else sum(p or 0 for p in parts)
        basis = "equalized"
    else:
        base, basis = val.get((code, year, "MR_ASSESS", tax_line)), "taxable"
    return rate, base, basis


def fix_note(code, year, cls):
    fix = RATE_FIX.get((code, year, cls))
    return FIX_NOTE.format(fix[1]) if fix else ""


def build(fir_rows, regions):
    val, _ = index(fir_rows)
    codes_of = {r["muni_id"]: [r["fir_code"]] + [c for c in (r.get("absorbed_fir_codes") or "").split("|") if c]
                for r in regions}
    out, no_base, folded = [], [], []
    for year in range(FIRST, LAST + 1):
        if year in MISSING:
            continue
        for cls in CLASSES:
            pools = defaultdict(lambda: [0.0, 0.0, 0, set()])
            for r in regions:
                own = rate_and_base(val, r["fir_code"], year, cls)
                if own is None:
                    raise BuildError(f"{r['muni_id']} {year} {cls}: no rate row")
                rate, base, basis = own
                out.append({"region": r["region"], "level": "member", "unit": r["muni_id"],
                            "role": r["role"], "taxation_year": year, "class": cls,
                            "mill_rate": round(rate, 6), "weight": "" if base is None else round(base),
                            "weight_basis": basis, "n_codes": 1,
                            "basis_note": BASIS_NOTE + fix_note(r["fir_code"], year, cls)})
                for code in codes_of[r["muni_id"]]:
                    got = rate_and_base(val, code, year, cls)
                    if got is None:
                        continue  # an absorbed code after it stopped reporting
                    rate, base, basis = got
                    absorbed = code != r["fir_code"]
                    if absorbed and rate == 0:
                        continue
                    if base is None:
                        (folded if absorbed else no_base).append((r["muni_id"], code, year, cls))
                        continue
                    for key in ((r["region"], "side", r["role"]), (r["region"], "region", "region")):
                        p = pools[key]
                        p[0] += rate * base
                        p[1] += base
                        p[2] += 1
                        p[3].add(basis)
            for (region, level, unit), (num, den, n, bases) in sorted(pools.items()):
                if len(bases) != 1 or den <= 0:
                    raise BuildError(f"{region} {unit} {year} {cls}: bases {bases}, weight {den}")
                note = BASIS_NOTE + "; pooled = sum(rate x base) / sum(base)"
                if unit != "core":
                    note += "".join(fix_note(r["fir_code"], year, cls) for r in regions
                                    if r["region"] == region)
                if year > EQ_LAST:
                    note += "; base is taxable assessment, not equalized (up to ~0.13 mill step from 2024)"
                if cls == "nr" and year >= 2025 and region == "edmonton" and unit in ("ring", "region"):
                    note += "; Beaumont and Devon also levy a lower small-business NR rate, not included"
                out.append({"region": region, "level": level, "unit": unit,
                            "role": unit if level == "side" else "", "taxation_year": year,
                            "class": cls, "mill_rate": round(num / den, 6), "weight": round(den),
                            "weight_basis": bases.pop(), "n_codes": n, "basis_note": note})
    if no_base:
        raise BuildError(f"{len(no_base)} rates with no base row, e.g. {no_base[:6]}")
    for muni, code, year, cls in folded:
        event(log, "absorbed code has no base: pooled at the member's rate", level=30,
              muni_id=muni, fir_code=code, taxation_year=year, rate_class=cls)
    return out, folded


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fir", type=Path, default=REPO / "data/processed/fir_long.csv")
    ap.add_argument("--regions", type=Path, default=REPO / "data/regions.csv")
    ap.add_argument("--out", type=Path, default=REPO / "data/processed/tax_rates.csv")
    args = ap.parse_args(argv)
    with args.fir.open() as f:
        fir_rows = list(csv.DictReader(f))
    with args.regions.open() as f:
        regions = list(csv.DictReader(f))
    rows, _ = build(fir_rows, regions)
    for y in sorted(MISSING):
        event(log, "year absent: FIR has no Schedule MR", level=30, taxation_year=y)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    event(log, "written", path=str(args.out), rows=len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
