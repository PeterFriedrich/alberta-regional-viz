"""Core-vs-ring share of non-residential equalized assessment, per region and year.

Joins the parsed long table to data/regions.csv (fixed 2025 board membership,
decision 8) and writes one row per (region, report_year, basis). Every member
must be found in every year, exactly once, or the build fails.

Usage:
    python src/build_share_series.py [--long ...] [--regions ...] [--out-dir data/processed]
"""
import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jsonlog import event, get_logger  # noqa: E402

log = get_logger("build_share_series")

REPO = Path(__file__).resolve().parent.parent

# docs/SPEC_phase1.md §"Phase 1 goal". nr_railway is 0 from the 2020 report on
# (the column no longer exists); linear and railway are both regulated property.
BASES = {
    "nr": ["nr"],
    "nr_linear": ["nr", "nr_linear", "nr_railway"],
    "nr_all": ["nr", "nr_linear", "nr_railway", "nr_cogen_me", "me"],
}
BASIS_NOTE = "equalized assessment; 2025 board membership applied to all years"


class BuildError(Exception):
    pass


def norm(name: str) -> str:
    return re.sub(r"\s+", " ", name.replace(",", " ")).strip().upper()


def load_regions(path: Path) -> list[dict]:
    with path.open() as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["aliases"] = {norm(a) for a in r["eq_aliases"].split("|")}
    seen = {}
    for r in rows:
        for a in r["aliases"]:
            if a in seen:
                raise BuildError(f"alias {a!r} used by both {seen[a]} and {r['muni_id']}")
            seen[a] = r["muni_id"]
    return rows


def member_values(long_rows, regions):
    """{(report_year, muni_id): {class: value}}, failing on a missing member or
    an alias that matches two report rows in one year."""
    alias_to = {a: r["muni_id"] for r in regions for a in r["aliases"]}
    found = defaultdict(dict)
    source = {}
    for row in long_rows:
        mid = alias_to.get(norm(row["muni_name_raw"]))
        if mid is None:
            continue
        year = int(row["report_year"])
        key = (year, mid)
        where = (row["muni_name_raw"], row["page"])
        if source.setdefault((key, row["class"]), where) != where:
            raise BuildError(f"{mid} matched twice in report {year}: "
                             f"{source[(key, row['class'])]} and {where}")
        found[key][row["class"]] = int(row["value"])
    years = sorted({int(r["report_year"]) for r in long_rows})
    missing = [(y, r["muni_id"]) for y in years for r in regions if (y, r["muni_id"]) not in found]
    if missing:
        raise BuildError(f"members not found: {missing}")
    return found, years


def shares(found, years, regions):
    out = []
    for region in sorted({r["region"] for r in regions}):
        members = [r for r in regions if r["region"] == region]
        core = [r["muni_id"] for r in members if r["role"] == "core"]
        if len(core) != 1:
            raise BuildError(f"region {region} needs exactly one core, has {core}")
        for y in years:
            for basis, classes in BASES.items():
                val = {r["muni_id"]: sum(found[(y, r["muni_id"])].get(c, 0) for c in classes)
                       for r in members}
                core_v = val[core[0]]
                ring_v = sum(v for m, v in val.items() if m != core[0])
                out.append({"region": region, "report_year": y, "taxation_year": y - 1,
                            "basis": basis, "core_value": core_v, "ring_value": ring_v,
                            "core_share": round(core_v / (core_v + ring_v), 6),
                            "n_members_found": len(val), "n_members_expected": len(members),
                            "basis_note": BASIS_NOTE})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--long", type=Path, default=REPO / "data/processed/equalized_long.csv")
    ap.add_argument("--regions", type=Path, default=REPO / "data/regions.csv")
    ap.add_argument("--out-dir", type=Path, default=REPO / "data/processed")
    args = ap.parse_args(argv)

    regions = load_regions(args.regions)
    with args.long.open() as f:
        long_rows = list(csv.DictReader(f))
    found, years = member_values(long_rows, regions)
    series = shares(found, years, regions)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    with (args.out_dir / "core_ring_share.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(series[0]))
        w.writeheader()
        w.writerows(series)
    region_of = {r["muni_id"]: r for r in regions}
    with (args.out_dir / "member_assessment.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["region", "muni_id", "role", "report_year", "taxation_year", "class", "value"])
        for (y, mid), vals in sorted(found.items()):
            r = region_of[mid]
            for c, v in sorted(vals.items()):
                w.writerow([r["region"], mid, r["role"], y, y - 1, c, v])
    event(log, "wrote series", rows=len(series), years=years)
    return 0


if __name__ == "__main__":
    sys.exit(main())
