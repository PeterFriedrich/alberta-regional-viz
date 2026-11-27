"""Guards for src/project_tax_rates.py (Phase 2c base-shift scenario)."""
import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
import project_tax_rates as ptr  # noqa: E402

RATES = list(csv.DictReader(open(REPO / "data/processed/tax_rates.csv", newline="")))
OUT = list(csv.DictReader(open(REPO / "data/processed/tax_rate_scenario.csv", newline="")))


def test_committed_output_reproduces_from_tax_rates():
    assert [{k: str(v) for k, v in r.items()} for r in ptr.build(RATES)] == OUT


def test_two_block_formula_reproduces_every_built_region_rate():
    # The scenario rests on region = s*core + (1-s)*ring; check it on every built
    # region-year-class, both weight bases, before trusting it forward.
    n = 0
    for cls in ("nr", "residential"):
        for (region, year), d in ptr.sides(RATES, cls).items():
            (c, cw, _), (r, rw, _), (g, _, _) = d["core"], d["ring"], d["region"]
            assert abs(ptr.two_block(cw / (cw + rw), c, r) - g) < 1e-3, (region, year, cls)
            n += 1
    assert n == 2 * 2 * 28


def test_fit_uses_equalized_years_only():
    side = ptr.sides(RATES)
    for region in ("edmonton", "calgary"):
        s = ptr.share_series(side, region)
        assert max(s) == ptr.EQ_LAST == 2024 and 2001 not in s
    fits = {(r["region"], r["fit_window"]) for r in OUT}
    assert fits == {(g, f"{w}-2024") for g in ("edmonton", "calgary") for w in ptr.WINDOWS}


def test_scenario_stays_between_the_sides_and_starts_near_the_actual_2026_rate():
    actual = {r["region"]: float(r["mill_rate"]) for r in RATES
              if r["level"] == "region" and r["class"] == "nr" and r["taxation_year"] == "2026"}
    for r in OUT:
        rate, lo, hi = (float(r[k]) for k in ("region_rate", "ring_rate", "core_rate"))
        assert lo < rate < hi
        if r["year"] == "2026":
            # Fitted equalized share vs 2026's taxable weights: 0.16 mills max, measured 2026-11-27.
            assert abs(rate - actual[r["region"]]) < 0.2, r
