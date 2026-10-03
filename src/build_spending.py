"""Gross operating cost per capita by function (police, transit, FCSS, public
housing), and the same net of the function's user charges, per member and for
each region's core and ring, 2001 onward.

Phase 2b basis (SPEC_phase1.md, decided 2026-10-02): gross = Schedule C
operating expenditure through 2008, and Schedule C accrual expense minus
Schedule E amortization from 2009. Net = gross minus Schedule E sales and user
charges for the same function. A blank FIR cell counts as 0. A negative gross
(amortization above expense, from 2009) is kept as printed and named in the
row's basis_note. Nominal dollars.

Public housing starts in 2009: the accrual restatement changed what the
housing line covers (2008 restated vs FIR cash: Edmonton +45%, Calgary social
housing about -25%; SPEC_phase1.md §"The 2009 accrual switch, measured"), so
there are no housing rows before 2009. Police, transit and FCSS move by at
most 3% at the switch and run through it.
Population = StatCan 17-10-0155. Absorbed municipalities' FIR rows are already
filed under their member (decision 8). A side's per-capita value is its total
over its total population, not a mean of members' rates.

Police leaves out the members that report no police spending because the
province polices them (RCMP): POLICE_EXCLUDED in every year, so the ring's
membership does not change mid-series, and the member-years in
POLICE_ZERO_YEARS, which are unexplained single-year zeros. Both drop out of
the numerator and the population, and the row's `excluded` names them. Any
other member-year with no police spending fails the run.

Usage:
    python src/build_spending.py [--fir ...] [--population ...] [--out data/processed/spending_per_capita.csv]
"""
import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jsonlog import event, get_logger  # noqa: E402
from parse_fir import ACCRUAL  # noqa: E402

log = get_logger("build_spending")

REPO = Path(__file__).resolve().parent.parent
# function: (Schedule C expense code, Schedule E code)
FUNCTIONS = {"police": ("01210", "02250"), "transit": ("01310", "02350"),
             "fcss": ("01400", "02440"), "housing": ("01480", "02520")}
# Parkland, Rocky View and Sturgeon report $0 police in every year 2017–2025, and
# Foothills through 2020 (SPEC_phase1.md §"Phase 2b basis").
POLICE_EXCLUDED = {"foothills", "parkland", "rocky_view", "sturgeon"}
# Single-year reclassifications (data/DATA.md §"Spending per capita"): Cochrane 2022
# booked police under bylaw enforcement, Devon 2021 all protective services as "other".
POLICE_ZERO_YEARS = {(2022, "cochrane"), (2021, "devon")}
FIRST_YEAR = {"housing": ACCRUAL}
BASIS_NOTE = ("nominal dollars; gross operating cost = FIR Schedule C operating expenditure "
              "to 2008, Schedule C expense - Schedule E amortization from 2009 (accrual "
              "switch); net = gross - Schedule E sales and user charges; population StatCan "
              "17-10-0155 July 1 estimates, 2021 boundaries; 2025 board membership applied "
              "to all years")
FIELDS = ["region", "level", "unit", "role", "function", "year", "gross", "user_charges", "net",
          "population", "gross_per_capita", "net_per_capita", "excluded", "basis_note"]


class BuildError(Exception):
    pass


def member_spending(fir_rows) -> tuple[dict, dict]:
    """{(year, muni_id, function): gross} and {(...): user charges}."""
    lines = defaultdict(float)
    for r in fir_rows:
        if r["schedule"] in ("C_OP", "C", "E_AMORT", "E_UC"):
            lines[(int(r["fir_year"]), r["muni_id"], r["schedule"], r["line_code"])] += float(r["value"] or 0)
    keys = {(y, m) for y, m, _, _ in lines}
    gross, charges = {}, {}
    for y, m in keys:
        for fn, (c, e) in FUNCTIONS.items():
            gross[(y, m, fn)] = (lines[(y, m, "C_OP", c)] if y < ACCRUAL
                                 else lines[(y, m, "C", c)] - lines[(y, m, "E_AMORT", e)])
            charges[(y, m, fn)] = lines[(y, m, "E_UC", e)]
    return gross, charges


def negative_note(year, munis, fn, gross) -> str:
    neg = [f"{m} {gross[(year, m, fn)]:,.0f}" for m in munis if gross[(year, m, fn)] < 0]
    return f"; negative gross kept as printed (amortization above expense): {', '.join(neg)}" if neg else ""


def police_excluded(year: int, muni: str) -> bool:
    return muni in POLICE_EXCLUDED or (year, muni) in POLICE_ZERO_YEARS


def build(fir_rows, pop_rows) -> list[dict]:
    gross, charges = member_spending(fir_rows)
    pop = {(int(r["year"]), r["muni_id"]): int(r["population"]) for r in pop_rows}
    info = {r["muni_id"]: (r["region"], r["role"]) for r in pop_rows}
    missing = sorted((y, m) for y, m in pop if (y, m, "police") not in gross)
    if missing:
        raise BuildError(f"{len(missing)} member-years have population but no spending, e.g. {missing[:5]}")
    zero = sorted((y, m) for y, m in pop if gross[(y, m, "police")] == 0 and not police_excluded(y, m))
    if zero:
        raise BuildError(f"{len(zero)} member-years report no police spending and are not "
                         f"excluded, e.g. {zero[:5]}")
    years = sorted({y for y, _ in pop})

    units = {(region, "member", m, role): [m] for m, (region, role) in info.items()}
    for region in sorted({reg for reg, _ in info.values()}):
        for side in ("core", "ring"):
            units[(region, "side", side, side)] = sorted(
                m for m, (reg, role) in info.items() if reg == region and role == side)

    out = []
    for (region, level, unit, role), munis in sorted(units.items()):
        for fn in FUNCTIONS:
            for y in (y for y in years if y >= FIRST_YEAR.get(fn, 0)):
                left_out = [m for m in munis if fn == "police" and police_excluded(y, m)]
                kept = [m for m in munis if m not in left_out]
                g = sum(gross[(y, m, fn)] for m in kept)
                uc = sum(charges[(y, m, fn)] for m in kept)
                p = sum(pop[(y, m)] for m in kept)
                out.append({"region": region, "level": level, "unit": unit, "role": role,
                            "function": fn, "year": y, "gross": round(g), "user_charges": round(uc),
                            "net": round(g - uc), "population": p,
                            "gross_per_capita": round(g / p, 2) if p else "",
                            "net_per_capita": round((g - uc) / p, 2) if p else "",
                            "excluded": "|".join(left_out),
                            "basis_note": BASIS_NOTE + negative_note(y, kept, fn, gross)})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fir", type=Path, default=REPO / "data/processed/fir_long.csv")
    ap.add_argument("--population", type=Path, default=REPO / "data/processed/population.csv")
    ap.add_argument("--out", type=Path, default=REPO / "data/processed/spending_per_capita.csv")
    args = ap.parse_args(argv)
    with args.fir.open(newline="") as f, args.population.open(newline="") as g:
        rows = build(list(csv.DictReader(f)), list(csv.DictReader(g)))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    event(log, "wrote spending per capita", path=str(args.out), rows=len(rows),
          years=[rows[0]["year"], rows[-1]["year"]],
          police_excluded_member_years=sum(1 for r in rows if r["level"] == "member" and r["excluded"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
