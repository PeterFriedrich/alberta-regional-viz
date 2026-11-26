"""Fetch the Alberta Regional Dashboard's non-residential mill rates and write one
row per member per year: the independent check on FIR Schedule MR (Phase 2c).

open.alberta.ca "Non-residential mill rates by municipality"
(c8a1e097-0081-4249-babb-164d3e709c0b); its CKAN resource dates say 2017 but the
data runs to the current year. Municipal rate only, non-residential only, keyed
by StatCan CSDUID. Members are joined through data/csd_crosswalk.csv (2021
rows); a member missing in any year fails the run.

A CSD that absorbed municipalities carries the SUM of their mill rates in the
years before the merger (Leduc County + New Sarepta, Parkland + Entwistle +
Wabamun): data/DATA.md §"Regional Dashboard". FIR's own row is the rate.

Usage:
    python src/fetch_dashboard_rates.py [--raw data/raw/dashboard] [--out data/processed/dashboard_nr_rates.csv]
"""
import argparse
import csv
import hashlib
import io
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jsonlog import event, get_logger  # noqa: E402

log = get_logger("fetch_dashboard_rates")

REPO = Path(__file__).resolve().parent.parent
URL = "https://regionaldashboard.alberta.ca/export/opendata/Municipal%20Tax%20Rates/csvs"
FIRST_YEAR = 1998
INDICATOR = "Non-res. Mill Rate"
FIELDS = ["muni_id", "csd_uid", "csd_name", "year", "nr_mill_rate"]


class FetchError(Exception):
    pass


def members(crosswalk: Path) -> dict[str, str]:
    """{csd_uid: muni_id} for the 2021 member rows."""
    with crosswalk.open() as f:
        return {r["csd_uid"]: r["muni_id"] for r in csv.DictReader(f)
                if r["census_year"] == "2021" and r["relation"] == "member"}


def extract(text: str, by_csd: dict[str, str]) -> list[dict]:
    rows = list(csv.DictReader(io.StringIO(text)))
    other = {r["IndicatorSummaryDescription"] for r in rows} - {INDICATOR}
    if other:
        raise FetchError(f"unexpected indicators {sorted(other)}: the file is no longer NR-only")
    out = {}
    for r in rows:
        muni = by_csd.get(r["CSDUID"])
        if muni is None:
            continue
        key = (muni, int(r["Period"]))
        if key in out:
            raise FetchError(f"{key} appears twice")
        out[key] = {"muni_id": muni, "csd_uid": r["CSDUID"], "csd_name": r["CSD"],
                    "year": key[1], "nr_mill_rate": float(r["OriginalValue"])}
    last = max(y for _, y in out)
    missing = [(m, y) for m in sorted(set(by_csd.values())) for y in range(FIRST_YEAR, last + 1)
               if (m, y) not in out]
    if missing:
        raise FetchError(f"{len(missing)} member-years missing, e.g. {missing[:8]}")
    return [out[k] for k in sorted(out)]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--raw", type=Path, default=REPO / "data/raw/dashboard")
    ap.add_argument("--crosswalk", type=Path, default=REPO / "data/csd_crosswalk.csv")
    ap.add_argument("--out", type=Path, default=REPO / "data/processed/dashboard_nr_rates.csv")
    args = ap.parse_args(argv)

    req = urllib.request.Request(URL, headers={"User-Agent": "alberta-regional-viz"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        body = resp.read()
    args.raw.mkdir(parents=True, exist_ok=True)
    (args.raw / "municipal_tax_rates.csv").write_bytes(body)
    (args.raw / "manifest.json").write_text(json.dumps({
        "url": URL, "sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body),
        "retrieved": datetime.now(timezone.utc).isoformat(timespec="seconds")}, indent=2) + "\n")

    rows = extract(body.decode("utf-8-sig"), members(args.crosswalk))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    event(log, "written", path=str(args.out), rows=len(rows),
          years=f"{rows[0]['year']}-{max(r['year'] for r in rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
