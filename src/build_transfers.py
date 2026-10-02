"""Total provincial transfers per capita, per member and for each region's core
and ring, 2001 onward.

Decision 9 as amended 2026-10-01: transfers = FIR 01910+01920 through 2022 and
01912+01922 from 2023, summed into one total, in nominal dollars. Population =
StatCan 17-10-0155 (decision 2026-10-02), which starts in 2001. Absorbed
municipalities' FIR rows are already filed under their member (decision 8).
The ring's per-capita value is its total transfers over its total population,
not a mean of members' rates. The 5-year value is five years' transfers over
five years' population, so it weights each year by its population.

A member-year with population but no transfer lines fails the run.

Usage:
    python src/build_transfers.py [--fir ...] [--population ...] [--out data/processed/transfers_per_capita.csv]
"""
import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jsonlog import event, get_logger  # noqa: E402
from parse_fir import TRANSFERS_NEW, TRANSFERS_OLD  # noqa: E402

log = get_logger("build_transfers")

REPO = Path(__file__).resolve().parent.parent
WINDOW = 5
BASIS_NOTE = ("nominal dollars; total provincial transfers (FIR 01910+01920 to 2022, "
              "01912+01922 from 2023); population StatCan 17-10-0155 July 1 estimates, "
              "2021 boundaries; 2025 board membership applied to all years")
FIELDS = ["region", "level", "unit", "role", "year", "transfers", "population", "per_capita",
          "per_capita_5yr", "basis_note"]


class BuildError(Exception):
    pass


def member_transfers(fir_rows) -> tuple[dict, dict]:
    """{(year, muni_id): total} over the year's transfer lines, and
    {(year, muni_id): [line notes]} for negative lines, kept as printed."""
    total, negative = defaultdict(float), defaultdict(list)
    for r in fir_rows:
        year = int(r["fir_year"])
        if r["line_code"] in (TRANSFERS_NEW if year >= 2023 else TRANSFERS_OLD) and r["value"]:
            v = float(r["value"])
            total[(year, r["muni_id"])] += v
            if v < 0:
                negative[(year, r["muni_id"])].append(f"{r['fir_name'].strip()} {r['line_code']} {v:,.0f}")
    return total, negative


def build(fir_rows, pop_rows) -> list[dict]:
    transfers, negative = member_transfers(fir_rows)
    pop = {(int(r["year"]), r["muni_id"]): int(r["population"]) for r in pop_rows}
    info = {r["muni_id"]: (r["region"], r["role"]) for r in pop_rows}
    missing = sorted(k for k in pop if k not in transfers)
    if missing:
        raise BuildError(f"{len(missing)} member-years have population but no transfers, e.g. {missing[:5]}")
    years = sorted({y for y, _ in pop})

    units = {(region, "member", m, role): [m] for m, (region, role) in info.items()}
    for region in sorted({reg for reg, _ in info.values()}):
        for side in ("core", "ring"):
            units[(region, "side", side, side)] = sorted(
                m for m, (reg, role) in info.items() if reg == region and role == side)

    out = []
    for (region, level, unit, role), munis in sorted(units.items()):
        t = {y: sum(transfers[(y, m)] for m in munis) for y in years}
        p = {y: sum(pop[(y, m)] for m in munis) for y in years}
        for y in years:
            span = [y - i for i in range(WINDOW)]
            five = (round(sum(t[s] for s in span) / sum(p[s] for s in span), 2)
                    if all(s in t for s in span) else "")
            neg = [n for m in munis for n in negative.get((y, m), [])]
            out.append({"region": region, "level": level, "unit": unit, "role": role, "year": y,
                        "transfers": round(t[y]), "population": p[y],
                        "per_capita": round(t[y] / p[y], 2), "per_capita_5yr": five,
                        "basis_note": BASIS_NOTE + (f"; negative line kept as printed: {', '.join(neg)}"
                                                    if neg else "")})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fir", type=Path, default=REPO / "data/processed/fir_long.csv")
    ap.add_argument("--population", type=Path, default=REPO / "data/processed/population.csv")
    ap.add_argument("--out", type=Path, default=REPO / "data/processed/transfers_per_capita.csv")
    args = ap.parse_args(argv)
    with args.fir.open(newline="") as f, args.population.open(newline="") as g:
        rows = build(list(csv.DictReader(f)), list(csv.DictReader(g)))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    event(log, "wrote transfers per capita", path=str(args.out), rows=len(rows),
          years=[rows[0]["year"], rows[-1]["year"]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
