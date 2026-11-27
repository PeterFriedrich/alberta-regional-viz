"""Base-shift scenario for the pooled non-residential tax rate (Phase 2c).

A scenario, not a forecast. The core's and the ring's 2026 pooled rates are held
fixed, and the core's share of the region's base moves along its own linear trend.
The region's pooled rate is a weighted mean of the two sides,

    region = s * core + (1 - s) * ring,

so it falls toward the ring's rate as the core's share s falls, with no member
cutting anything. Inflation cancels: the rate depends on shares only.

s is the core's share of equalized assessment (tax_rates.csv `weight`, taxation
years through EQ_LAST). Taxable weights (2025-2026) are not used in the fit, since
they don't compare across municipalities (DECISIONS 2026-11-26). The trend is an
OLS line over each window in WINDOWS, and the projection starts from the fitted
line, not from the last observed point. The ring's member mix is frozen at 2026.

Not projected: residential. Its core and ring rates are close (Edmonton 1.95
mills apart in 2026, Calgary 0.43), so every window moves the region's rate by
<= 0.05 mills to 2035 (measured 2026-11-27).

Usage:
    python src/project_tax_rates.py [--rates data/processed/tax_rates.csv]
                                    [--out data/processed/tax_rate_scenario.csv]
"""
import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_tax_rates import EQ_LAST  # noqa: E402
from jsonlog import event, get_logger  # noqa: E402

log = get_logger("project_tax_rates")

REPO = Path(__file__).resolve().parent.parent
CLASS = "nr"
RATE_YEAR = 2026            # rates held at this year's pooled core and ring rates
HORIZON = 2035
# 2015: after the 2005/2007 Calgary annexations, spans Edmonton's 2019 Leduc
# annexation (it adds base to the core, so it flattens the core's fall).
# 2020: after every core annexation in data/annexations.csv.
WINDOWS = (2015, 2020)
BASIS_NOTE = ("scenario, not forecast: core and ring pooled rates held at their 2026 values, "
              "ring mix frozen at 2026; core share of equalized nr assessment on its linear "
              "trend over fit_window; municipal general rate only (education excluded); mills; "
              "2025 board membership applied to all years")
FIELDS = ["region", "class", "fit_window", "year", "core_share", "core_rate", "ring_rate",
          "region_rate", "slope_pp_per_year", "basis_note"]


def two_block(s, core, ring):
    """The region's pooled rate from the core's base share and the two sides' rates."""
    return s * core + (1 - s) * ring


def sides(rows, cls=CLASS):
    """{(region, year): {"core": (rate, weight), "ring": ..., "region": ...}} for one class."""
    out = {}
    for r in rows:
        if r["level"] == "member" or r["class"] != cls:
            continue
        out.setdefault((r["region"], int(r["taxation_year"])), {})[r["unit"]] = (
            float(r["mill_rate"]), float(r["weight"]), r["weight_basis"])
    return out


def share_series(side, region):
    """Core share of the base, equalized years only: {year: s}."""
    s = {}
    for (reg, year), d in side.items():
        if reg != region or year > EQ_LAST:
            continue
        assert d["core"][2] == d["ring"][2] == "equalized", (region, year)
        s[year] = d["core"][1] / (d["core"][1] + d["ring"][1])
    return s


def ols(points):
    """Slope and intercept of the least-squares line through (x, y) points."""
    n = len(points)
    mx = sum(x for x, _ in points) / n
    my = sum(y for _, y in points) / n
    slope = (sum((x - mx) * (y - my) for x, y in points)
             / sum((x - mx) ** 2 for x, _ in points))
    return slope, my - slope * mx


def build(rows):
    side = sides(rows)
    regions = sorted({reg for reg, _ in side})
    out = []
    for region in regions:
        core, ring = side[(region, RATE_YEAR)]["core"][0], side[(region, RATE_YEAR)]["ring"][0]
        s = share_series(side, region)
        for start in WINDOWS:
            pts = [(y, v) for y, v in sorted(s.items()) if y >= start]
            slope, icept = ols(pts)
            for year in range(RATE_YEAR, HORIZON + 1):
                sy = icept + slope * year
                assert 0 < sy < 1, (region, start, year, sy)
                out.append({
                    "region": region, "class": CLASS, "fit_window": f"{start}-{EQ_LAST}",
                    "year": year, "core_share": round(sy, 4), "core_rate": core,
                    "ring_rate": ring, "region_rate": round(two_block(sy, core, ring), 4),
                    "slope_pp_per_year": round(slope * 100, 3), "basis_note": BASIS_NOTE,
                })
            event(log, "fitted", region=region, fit_window=f"{start}-{EQ_LAST}",
                  points=len(pts), slope_pp_per_year=round(slope * 100, 3))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rates", type=Path, default=REPO / "data/processed/tax_rates.csv")
    ap.add_argument("--out", type=Path, default=REPO / "data/processed/tax_rate_scenario.csv")
    args = ap.parse_args(argv)
    with args.rates.open() as f:
        rows = build(list(csv.DictReader(f)))
    with args.out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    event(log, "written", path=str(args.out), rows=len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
