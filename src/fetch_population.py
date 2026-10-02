"""Fetch StatCan's July 1 population estimates by CSD (table 17-10-0155, 2021
boundaries) and write one row per member per year.

Decision 2026-10-02 (docs/SPEC_phase1.md §"Population basis"). Members are
joined through data/csd_crosswalk.csv (2021 rows); a member missing in any
year fails the run. The estimate status per year is parsed from the table's own
footnote, so a release that changes it fails until this parser is updated.

Usage:
    python src/fetch_population.py [--raw data/raw/population] [--out data/processed/population.csv]
"""
import argparse
import csv
import hashlib
import io
import json
import re
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jsonlog import event, get_logger  # noqa: E402

log = get_logger("fetch_population")

REPO = Path(__file__).resolve().parent.parent
PID = "17100155"
CSV_URL = f"https://www150.statcan.gc.ca/n1/tbl/csv/{PID}-eng.zip"
META_URL = "https://www150.statcan.gc.ca/t1/wds/rest/getCubeMetadata"
FIRST_YEAR = 2001
# 2021 CSD DGUIDs are "2021A0005" + the 7-digit SGC code.
CSD_DGUID = re.compile(r"^2021A0005(\d{7})$")
STATUS_NOTE = re.compile(
    r"final intercensal up to (\d{4}), final postcensal for (\d{4}), "
    r"updated postcensal for (\d{4}) to (\d{4}), and preliminary postcensal for (\d{4})")


class FetchError(Exception):
    pass


def _get(url: str, data: bytes | None = None) -> bytes:
    req = urllib.request.Request(url, data=data, headers={
        "User-Agent": "alberta-regional-viz", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        return resp.read()


def year_status(footnotes: list[str]) -> dict[int, str]:
    """{year: status} from the footnote that states it; fails if none does."""
    for f in footnotes:
        m = STATUS_NOTE.search(f)
        if m:
            final, post, upd_a, upd_b, prelim = map(int, m.groups())
            out = {y: "final intercensal" for y in range(FIRST_YEAR, final + 1)}
            out[post] = "final postcensal"
            out.update({y: "updated postcensal" for y in range(upd_a, upd_b + 1)})
            out[prelim] = "preliminary postcensal"
            return out
    raise FetchError("no footnote states the estimate status by year — read the release notes")


def members(xwalk: Path, regions: Path) -> dict[str, dict]:
    """{csd_uid: region row} for the 2021 member rows of the crosswalk."""
    reg = {r["muni_id"]: r for r in csv.DictReader(regions.open())}
    out = {}
    for r in csv.DictReader(xwalk.open()):
        if r["census_year"] == "2021" and r["relation"] == "member":
            out[r["csd_uid"]] = reg[r["muni_id"]]
    if len(out) != len(reg):
        raise FetchError(f"crosswalk has {len(out)} 2021 member rows, regions.csv {len(reg)}")
    return out


def extract(table_rows, by_uid: dict[str, dict], status: dict[int, str], release: str) -> list[dict]:
    out = []
    for r in table_rows:
        m = CSD_DGUID.match(r["DGUID"] or "")
        if not m or m.group(1) not in by_uid:
            continue
        reg, year = by_uid[m.group(1)], int(r["REF_DATE"])
        if not r["VALUE"]:
            raise FetchError(f"{reg['muni_id']} {year}: empty value (status {r['STATUS']!r})")
        out.append({"muni_id": reg["muni_id"], "region": reg["region"], "role": reg["role"],
                    "year": year, "population": int(r["VALUE"]),
                    "estimate_status": status.get(year, ""), "csd_uid": m.group(1),
                    "release": release})
    years = sorted({r["year"] for r in out})
    if not years or years[0] != FIRST_YEAR:
        raise FetchError(f"expected the series to start in {FIRST_YEAR}, got {years[:1]}")
    have = {(r["muni_id"], r["year"]) for r in out}
    missing = [(reg["muni_id"], y) for reg in by_uid.values() for y in years
               if (reg["muni_id"], y) not in have]
    if missing or len(have) != len(out):
        raise FetchError(f"missing member-years {missing[:10]} or duplicate rows")
    unstated = sorted({r["year"] for r in out if not r["estimate_status"]})
    if unstated:
        raise FetchError(f"no estimate status for years {unstated}")
    return sorted(out, key=lambda r: (r["region"], r["role"] != "core", r["muni_id"], r["year"]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--raw", type=Path, default=REPO / "data/raw/population")
    ap.add_argument("--out", type=Path, default=REPO / "data/processed/population.csv")
    ap.add_argument("--crosswalk", type=Path, default=REPO / "data/csd_crosswalk.csv")
    ap.add_argument("--regions", type=Path, default=REPO / "data/regions.csv")
    args = ap.parse_args(argv)
    args.raw.mkdir(parents=True, exist_ok=True)

    meta = json.loads(_get(META_URL, json.dumps([{"productId": int(PID)}]).encode()))[0]["object"]
    release = meta["releaseTime"][:10]
    status = year_status([f["footnotesEn"] for f in meta.get("footnote", [])])

    body = _get(CSV_URL)
    (args.raw / f"{PID}-eng.zip").write_bytes(body)
    (args.raw / "manifest.json").write_text(json.dumps({
        "table": PID, "url": CSV_URL, "title": meta["cubeTitleEn"], "release": release,
        "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
        "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}, indent=1) + "\n")

    with zipfile.ZipFile(io.BytesIO(body)) as z, z.open(f"{PID}.csv") as f:
        rows = extract(csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig")),
                       members(args.crosswalk, args.regions), status, release)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    event(log, "wrote population", path=str(args.out), rows=len(rows), release=release,
          years=[rows[0]["year"], max(r["year"] for r in rows)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
